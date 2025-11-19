"""FastAPI webhook bootstrap with delayed dependency initialization."""

import asyncio
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from src.entities.message import Message
from src.infrastructure.google_generative_ai.gemini_service import GeminiService
from src.infrastructure.repositories.json_instructions_repository import (
    JsonInstructionsRepository,
)
from src.interface_adapter.controller.telegram_controller import (
    TelegramMessageController,
)
from src.interface_adapter.controller.webchat_controller import WebchatMessageController
from src.interface_adapter.gateways.agent_gateway import AgentGateway
from src.interface_adapter.presenters.telegram_presenter import TelegramMessagePresenter
from src.shared.config import get_config
from src.shared.logger_rasa_v0 import get_logger
from src.use_cases.generate_agent_response_use_case import GenerateAgentResponseUseCase

logger = logging.getLogger("fastapi-webhook")


class DependencyContainer:
    """Instancia y mantiene las dependencias compartidas de la aplicación."""

    def __init__(self, config: dict | None = None):
        self._initial_config = config
        self.config: dict | None = None
        self.http_client: httpx.AsyncClient | None = None
        self.telegram_client: httpx.AsyncClient | None = None
        self.instructions_repository: JsonInstructionsRepository | None = None
        self.gemini_service: GeminiService | None = None
        self.agent_gateway: AgentGateway | None = None
        self.telegram_presenter: TelegramMessagePresenter | None = None
        self.generate_agent_bot_use_case: GenerateAgentResponseUseCase | None = None
        self.telegram_controller: TelegramMessageController | None = None
        self.webchat_controller: WebchatMessageController | None = None
        self.telegram_api_url: str | None = None
        self.telegram_message_delay: float = 0.5

    async def startup(self) -> None:
        self.config = self._initial_config or get_config()
        telegram_token = self.config.get("TELEGRAM_API_KEY")
        self.telegram_api_url = (
            f"https://api.telegram.org/bot{telegram_token}/sendMessage" if telegram_token else None
        )
        self.telegram_message_delay = self.config.get("TELEGRAM_MESSAGE_DELAY", 0.5)

        instructions_path = str(
            self.config.get(
                "SYSTEM_INSTRUCTIONS_PATH",
                "src/infrastructure/google_generative_ai/system_instructions.json",
            )
        )
        self.instructions_repository = JsonInstructionsRepository(instructions_path)
        self.gemini_service = GeminiService()

        self.http_client = httpx.AsyncClient()
        self.telegram_client = httpx.AsyncClient()
        self.agent_gateway = AgentGateway(
            http_client=self.http_client,
            instructions_repository=self.instructions_repository,
            gemini_service=self.gemini_service,
            agent_bot_url=self.config.get("RASA_REST_URL"),
            remote_available=not self.config.get("DISABLE_RASA", False),
        )
        self.telegram_presenter = TelegramMessagePresenter()
        self.generate_agent_bot_use_case = GenerateAgentResponseUseCase(self.agent_gateway)
        self.telegram_controller = TelegramMessageController(
            self.generate_agent_bot_use_case, self.telegram_presenter
        )
        self.webchat_controller = WebchatMessageController(
            self.generate_agent_bot_use_case, self.telegram_presenter
        )

    async def shutdown(self) -> None:
        for client in (self.http_client, self.telegram_client):
            if client is not None:
                await client.aclose()


def create_app(config: dict | None = None) -> FastAPI:
    container = DependencyContainer(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await container.startup()
        app.state.container = container
        global logger
        logger = get_logger("fastapi-webhook")
        try:
            yield
        finally:
            await container.shutdown()

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://chat.profebustos.com.ar", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


def _get_container(request: Request) -> DependencyContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise RuntimeError("Dependency container not initialized")
    return container


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    "Webhook para manejar mensajes entrantes de Telegram"
    container = _get_container(request)
    telegram_controller = container.telegram_controller
    telegram_presenter = container.telegram_presenter
    if (
        telegram_controller is None
        or telegram_presenter is None
        or container.telegram_client is None
        or not container.telegram_api_url
    ):
        raise RuntimeError("Telegram dependencies not initialized")
    logger.info("[Telegram] Webhook POST recibido")
    update = await request.json()
    message = update.get("message")
    if not message:
        logger.info("[Telegram] No es un mensaje válido. Ignorando.")
        return PlainTextResponse("OK", status_code=200)

    chat_id = message["chat"]["id"]

    # --- Manejo de mensajes de texto ---
    if "text" in message:
        text = message["text"]
        entities = message.get("entities", None)
        try:
            chat_id, response_text = await telegram_controller.handle(chat_id, text, entities)
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error("[Telegram] Error de conexión: %s", e, exc_info=True)
            response_text = (
                "Lo sentimos, el servidor no está disponible en este momento. "
                "Por favor, comuníquese con el área de mantenimiento."
            )
        except ValueError as e:
            logger.error("[Telegram] Error de datos: %s", e, exc_info=True)
            response_text = "Lo sentimos, hubo un error procesando su mensaje."
        except (TypeError, AttributeError, KeyError) as e:
            logger.error("[Telegram] Error inesperado: %s", e, exc_info=True)
            response_text = (
                "Lo sentimos, el servidor no está disponible en este momento. "
                "Por favor, comuníquese con el área de mantenimiento."
            )
        logger.info("[Telegram] Respuesta generada: %s", response_text)
        response_message = Message(to=chat_id, body=response_text)
        formatted_responses = telegram_presenter.present(response_message)
        if not isinstance(formatted_responses, list):
            formatted_responses = [formatted_responses]
        for resp in formatted_responses:
            payload = {"chat_id": chat_id, **resp}
            await container.telegram_client.post(container.telegram_api_url, json=payload)
            await asyncio.sleep(container.telegram_message_delay)
        return PlainTextResponse("OK", status_code=200)

    logger.info("[Telegram] No es un mensaje de texto. Ignorando.")
    return PlainTextResponse("OK", status_code=200)


@app.get("/")
async def index():
    "Página de inicio simple para verificar que el servidor está funcionando."
    return {"message": "Bienvenido al webhook de FastAPI"}


@app.post("/webchat/webhook")
async def webchat_webhook(request: Request):
    """
    Endpoint para recibir mensajes del chat web y responder con el mensaje del agente.
    Espera un JSON: { "user_id": "...", "text": "mensaje del usuario" }
    Responde: { "role": "assistant", "text": "respuesta del agente" }
    """
    logger.debug("[Webchat] Nueva request recibida en /webchat/webhook")
    logger.debug("[Webchat] Headers: %s", dict(request.headers))
    container = _get_container(request)
    webchat_controller = container.webchat_controller
    if webchat_controller is None:
        raise RuntimeError("Webchat controller not initialized")
    try:
        data = await request.json()
        logger.debug("[Webchat] Payload recibido: %s", data)
    except (ValueError, TypeError) as e:
        logger.error("[Webchat] Error al parsear JSON: %s", e, exc_info=True)
        return {"role": "assistant", "text": "Error en el formato de la solicitud."}

    user_id = data.get("user_id", None)
    user_text = data.get("text", "")
    logger.debug("[Webchat] user_id: %s, user_text: %s", user_id, user_text)

    if not user_id or not user_text:
        logger.warning(
            "[Webchat] Faltan datos en la solicitud: user_id=%s, text=%s",
            user_id,
            user_text,
        )
        return {"role": "assistant", "text": "Faltan datos en la solicitud."}

    try:
        user_id, response_text = await webchat_controller.handle(user_id, user_text)
        logger.debug("[Webchat] Respuesta generada: %s", response_text)
    except ConnectionRefusedError as e:
        logger.error("[Webchat] Error de conexión con Rasa: %s", e, exc_info=True)
        return {
            "role": "assistant",
            "text": (
                "Lo sentimos, el servidor no está disponible en este momento. "
                "Por favor, comuníquese con el área de mantenimiento."
            ),
        }
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        logger.error("[Webchat] Error inesperado: %s", e, exc_info=True)
        return {
            "role": "assistant",
            "text": "Lo sentimos, hubo un error procesando su mensaje.",
        }

    return {"role": "assistant", "text": response_text}

@app.get("/test")
async def test():
    "Página de inicio simple para verificar que el servidor está funcionando."
    return {"message": "El servidor está funcionando correctamente."}
