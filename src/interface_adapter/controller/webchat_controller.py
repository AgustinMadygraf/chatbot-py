"""
Path: src/interface_adapter/controller/webchat_controller.py
"""

from src.entities.message import Message

class WebchatMessageController:
    "Controlador para manejar mensajes entrantes del webchat usando Rasa."
    def __init__(self, use_case, presenter):
        self.use_case = use_case
        self.presenter = presenter

    async def handle(self, user_id, user_message_or_text):
        "Maneja un mensaje entrante del webchat y genera una respuesta usando el caso de uso."
        if isinstance(user_message_or_text, Message):
            user_message = user_message_or_text
        else:
            user_message = Message(to=user_id, body=user_message_or_text)

        response_message = self.use_case.execute(user_id, user_message)
        response_text = response_message.body.strip() if response_message.body else "No tengo una respuesta en este momento."
        return user_id, response_text
