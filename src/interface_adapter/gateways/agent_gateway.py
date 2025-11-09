"""Gateway to communicate with the Rasa webhook."""

from src.shared.logger_rasa_v0 import get_logger

logger = get_logger("agent-gateway")


class AgentGateway:
    "Interfaz para comunicarse con un modelo Rasa."
    def __init__(self, agent_bot_url: str, http_client):
        self.agent_bot_url = agent_bot_url
        self.http_client = http_client
        logger.debug("Inicializando AgentGateway con endpoint %s", agent_bot_url)

    def get_response(self, message_or_text) -> str:
        "Envía un mensaje al bot Rasa y devuelve la respuesta."
        if isinstance(message_or_text, str):
            payload = {"sender": "user", "message": message_or_text}
        else:
            payload = {"sender": "user", "message": message_or_text.body}
            if hasattr(message_or_text, 'media_url') and message_or_text.media_url:
                payload["media_url"] = message_or_text.media_url
                payload["media_type"] = message_or_text.media_type

        try:
            logger.debug("Enviando payload a Rasa (%s)", self.agent_bot_url)
            response = self.http_client.post(self.agent_bot_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            logger.debug(
                "Respuesta de Rasa recibida desde %s con %d mensajes",
                self.agent_bot_url,
                len(data) if isinstance(data, list) else 0,
            )
            return " ".join([msg.get("text", "") for msg in data if "text" in msg])
        except (ValueError, AttributeError) as e:
            logger.error("Error procesando la respuesta de Rasa (%s): %s", self.agent_bot_url, e, exc_info=True)
            return f"[Error procesando la respuesta de Rasa: {e}]"
