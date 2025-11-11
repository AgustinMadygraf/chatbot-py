"""Gateway to communicate with the conversational agent."""

from __future__ import annotations

import os
import threading
from typing import Dict, List, Optional, Tuple

import requests

from src.entities.message import Message
from src.infrastructure.google_generative_ai.gemini_service import GeminiService
from src.infrastructure.repositories.json_instructions_repository import (
    JsonInstructionsRepository,
)
from src.interface_adapter.gateways.gemini_gateway import GeminiGateway
from src.shared.config import DEFAULT_SYSTEM_INSTRUCTIONS_PATH
from src.shared.logger_rasa_v0 import get_logger
from src.use_cases.load_system_instructions import LoadSystemInstructionsUseCase

logger = get_logger("agent-gateway")


class AgentGateway:
    """Interfaz para comunicarse con un modelo Rasa o un fallback local."""

    _SALUDO_KEYWORDS: Tuple[str, ...] = (
        "hola",
        "hola!",
        "holi",
        "buenas",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "saludos",
    )
    _DESPEDIDA_KEYWORDS: Tuple[str, ...] = (
        "adios",
        "adiós",
        "chau",
        "nos vemos",
        "hasta luego",
        "gracias",
    )
    _SALUDO_RESPONSE: str = (
        "¡Hola!  ¿en qué te puedo dar una mano hoy? ¿Necesitás ayuda con el diseño de tu NLU, "
        "armando unas stories o rules, desarrollando actions personalizadas, o quizás pensando en "
        "el despliegue de tu bot?"
    )
    _DESPEDIDA_RESPONSE: str = "Adiós"
    _FALLBACK_RESPONSE: str = (
        "Lo sentimos, el servidor no está disponible en este momento. Por favor, "
        "comuníquese con el área de mantenimiento."
    )

    def __init__(self, http_client):
        rasa_url = os.getenv(
            "RASA_REST_URL", "http://localhost:5005/webhooks/rest/webhook"
        )
        self.agent_bot_url = rasa_url
        self.http_client = http_client
        self._remote_available = not _is_truthy(os.getenv("DISABLE_RASA"))
        self._history: Dict[str, List[Tuple[str, str]]] = {}
        self._history_lock = threading.Lock()
        self._gemini_gateway: Optional[GeminiGateway] = None
        self._system_instructions = None
        self._fallback_initialized = False
        logger.debug("Inicializando AgentGateway con endpoint %s", self.agent_bot_url)

    def get_response(self, message_or_text) -> str:
        """Envía un mensaje al bot Rasa y devuelve la respuesta.

        Si el servidor Rasa no está disponible o produce un error de conexión, se
        utiliza un fallback local que implementa reglas básicas de saludo y
        despedida, además de un generador usando Gemini cuando es posible.
        """

        payload, conversation_id = self._build_payload(message_or_text)
        message_text = payload["message"]

        if self._remote_available:
            try:
                logger.debug("Enviando payload a Rasa (%s)", self.agent_bot_url)
                response = self.http_client.post(
                    self.agent_bot_url, json=payload, timeout=60
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(
                    "Respuesta de Rasa recibida desde %s con %d mensajes",
                    self.agent_bot_url,
                    len(data) if isinstance(data, list) else 0,
                )
                text = " ".join(
                    [msg.get("text", "") for msg in data if "text" in msg]
                ).strip()
                if conversation_id:
                    self._store_turn(conversation_id, "user", message_text)
                    if text:
                        self._store_turn(conversation_id, "bot", text)
                return text
            except requests.exceptions.RequestException as exc:
                logger.error(
                    "No se pudo contactar al servidor Rasa en %s: %s",
                    self.agent_bot_url,
                    exc,
                    exc_info=True,
                )
                self._remote_available = False
            except (ValueError, AttributeError) as exc:
                logger.error(
                    "Error procesando la respuesta de Rasa (%s): %s",
                    self.agent_bot_url,
                    exc,
                    exc_info=True,
                )
                return f"[Error procesando la respuesta de Rasa: {exc}]"

        return self._local_response(conversation_id, message_text)

    def _build_payload(self, message_or_text) -> Tuple[Dict[str, str], str]:
        if isinstance(message_or_text, str):
            payload = {"sender": "user", "message": message_or_text}
            conversation_id = ""
        else:
            message: Message = message_or_text
            payload = {"sender": "user", "message": message.body}
            if hasattr(message, "media_url") and message.media_url:
                payload["media_url"] = message.media_url
                payload["media_type"] = message.media_type
            conversation_id = message.to or ""
        return payload, conversation_id

    def _local_response(self, conversation_id: str, message_text: str) -> str:
        normalized = message_text.lower().strip()
        if conversation_id:
            self._store_turn(conversation_id, "user", message_text)

        if any(keyword in normalized for keyword in self._SALUDO_KEYWORDS):
            response = self._SALUDO_RESPONSE
        elif any(keyword in normalized for keyword in self._DESPEDIDA_KEYWORDS):
            response = self._DESPEDIDA_RESPONSE
        else:
            response = self._fallback_response(conversation_id, message_text)

        if conversation_id:
            self._store_turn(conversation_id, "bot", response)
        return response

    def _fallback_response(self, conversation_id: str, message_text: str) -> str:
        prompt = self._build_prompt(conversation_id, message_text)
        gateway = self._ensure_fallback_components()
        if gateway is None:
            return self._FALLBACK_RESPONSE

        try:
            reply = gateway.get_response(prompt, self._system_instructions)
            if isinstance(reply, str) and reply.strip():
                return reply.strip()
        except (
            requests.exceptions.RequestException,
            ValueError,
            AttributeError,
            TypeError,
        ) as exc:
            logger.error("Error en fallback Gemini: %s", exc, exc_info=True)
        return self._FALLBACK_RESPONSE

    def _ensure_fallback_components(self) -> Optional[GeminiGateway]:
        if self._fallback_initialized:
            return self._gemini_gateway

        self._fallback_initialized = True
        try:
            repository = JsonInstructionsRepository(
                str(DEFAULT_SYSTEM_INSTRUCTIONS_PATH)
            )
            use_case = LoadSystemInstructionsUseCase(repository)
            self._system_instructions = use_case.execute()
        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            ValueError,
            TypeError,
        ) as exc:
            logger.error(
                "No se pudieron cargar las instrucciones del sistema: %s",
                exc,
                exc_info=True,
            )
            self._system_instructions = None

        try:
            service = GeminiService()
            self._gemini_gateway = GeminiGateway(service)
        except (
            ValueError,
            TypeError,
            AttributeError,
            ImportError,
            RuntimeError,
        ) as exc:
            logger.error("Gemini fallback deshabilitado: %s", exc, exc_info=True)
            self._gemini_gateway = None

        return self._gemini_gateway

    def _store_turn(self, conversation_id: str, role: str, text: str) -> None:
        if not conversation_id or not text:
            return
        with self._history_lock:
            history = self._history.setdefault(conversation_id, [])
            history.append((role, text))
            if len(history) > 20:
                del history[:-20]

    def _build_prompt(self, conversation_id: str, message_text: str) -> str:
        lines: List[str] = []
        if conversation_id:
            with self._history_lock:
                history = list(self._history.get(conversation_id, []))
            for role, text in history[-10:]:
                prefix = "Usuario" if role == "user" else "Gemini"
                lines.append(f"{prefix}: {text}")
        lines.append(f"Usuario: {message_text}")
        lines.append("Gemini:")
        return "\n".join(lines)


def _is_truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}
