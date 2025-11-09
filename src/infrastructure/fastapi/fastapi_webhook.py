"""
Path: src/infrastructure/fastapi/fastapi_webhook.py
"""


import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from src.shared.logger import get_logger
from src.shared.config import get_config

from src.infrastructure.requests.requests_http_client import RequestsHttpClient
from src.interface_adapter.controller.telegram_controller import TelegramMessageController
from src.interface_adapter.gateways.agent_gateway import AgentGateway
from src.interface_adapter.presenters.telegram_presenter import TelegramMessagePresenter
from src.use_cases.generate_agent_response_use_case import GenerateAgentResponseUseCase
from src.entities.message import Message

logger = get_logger("fastapi-webhook")

config = get_config()
TELEGRAM_TOKEN = config.get("TELEGRAM_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
RASA_URL = config.get("RASA_API_URL")

logger.debug("Utilizando RASA_API_URL=%s", RASA_URL)

http_client = RequestsHttpClient()
agent_bot_service = AgentGateway(RASA_URL, http_client=http_client)
telegram_presenter = TelegramMessagePresenter()

# Inyectar el caso de uso de transcripción en GenerateAgentResponseUseCase
generate_agent_bot_use_case = GenerateAgentResponseUseCase(
    agent_bot_service
)

telegram_controller = TelegramMessageController(generate_agent_bot_use_case, telegram_presenter)

app = FastAPI()

# Agrega el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto a tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    "Webhook para manejar mensajes entrantes de Telegram "
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
        async with httpx.AsyncClient() as client:
            for resp in formatted_responses:
                payload = {
                    "chat_id": chat_id,
                    **resp
                }
                await client.post(TELEGRAM_API_URL, json=payload)
                await asyncio.sleep(3)  # <-- Delay de 3 segundos entre mensajes
        return PlainTextResponse("OK", status_code=200)

    logger.info("[Telegram] No es un mensaje de texto. Ignorando.")
    return PlainTextResponse("OK", status_code=200)

@app.get("/")
async def index():
    "Página de inicio simple para verificar que el servidor está funcionando."
    return {"message": "Bienvenido al webhook de FastAPI"}
