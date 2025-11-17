"""
Path: rasa_project/actions/actions.py
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from src.shared.config import DEFAULT_SYSTEM_INSTRUCTIONS_PATH
from src.shared.logger_rasa_v0 import get_logger

from src.infrastructure.repositories.json_instructions_repository import (
    JsonInstructionsRepository,
)
from src.infrastructure.google_generative_ai.gemini_service import GeminiService
from src.interface_adapter.gateways.gemini_gateway import GeminiGateway
from src.use_cases.load_system_instructions import LoadSystemInstructionsUseCase

logger = get_logger("action-gemini-fallback")


def build_history_from_tracker(tracker: Tracker, max_turns: int = 10) -> str:
    "Construir el historial de conversación desde el tracker"
    events = tracker.events
    history = []
    for event in events:
        if event.get("event") == "user":
            text = event.get("text")
            if text:
                history.append(f"Usuario: {text}")
        elif event.get("event") == "bot":
            text = event.get("text")
            if text:
                history.append(f"Gemini: {text}")
    # Solo los últimos max_turns turnos
    return "\n".join(history[-max_turns:])


class ActionGeminiFallback(Action):
    "Fallback action for Gemini"

    def name(self) -> Text:
        return "action_gemini_fallback"

    def __init__(self) -> None:
        instructions_path = str(DEFAULT_SYSTEM_INSTRUCTIONS_PATH)
        self._instructions_repository = JsonInstructionsRepository(instructions_path)
        self._load_instructions = LoadSystemInstructionsUseCase(
            self._instructions_repository
        )
        self._system_instructions = self._load_instructions.execute()

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        "Fallback action for Gemini"
        # Construir historial
        history = build_history_from_tracker(tracker, max_turns=10)
        logger.debug(
            "Fallback activado | sender=%s | intent=%s | history_chars=%s",
            tracker.sender_id,
            tracker.get_intent_of_latest_message(),
            len(history),
        )
        prompt_with_history = f"{history[-2000:]}\nGemini:"

        # --- Reutilizar gateways, casos de uso y entidades ---
        try:
            gemini_service = GeminiService()
            gemini = GeminiGateway(gemini_service)

            respuesta = gemini.get_response(prompt_with_history, self._system_instructions)
            logger.debug("Respuesta Gemini recibida=%s", bool(respuesta))

            if not respuesta:
                raise ValueError("Gemini devolvió respuesta vacía")
            dispatcher.utter_message(text=respuesta)
        except (FileNotFoundError, KeyError, ValueError, RuntimeError) as e:
            logger.exception("Error en fallback Gemini: %s", e)
            dispatcher.utter_message(text="Me quedé sin datos. Te derivo con un humano por WhatsApp.")
        return []
