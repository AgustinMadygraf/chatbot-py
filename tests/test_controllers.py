"""
Tests for TelegramMessageController and WebchatMessageController.
"""
import asyncio
from src.interface_adapter.controller.telegram_controller import TelegramMessageController
from src.interface_adapter.controller.webchat_controller import WebchatMessageController
from src.entities.message import Message

class DummyUseCase:
    " a Dummy use case for testing. "
    def execute(self, chat_id, user_message, prompt=None):
        "Return a dummy Message echoing the input. "
        _ = prompt  # Acknowledge unused parameter
        return Message(to=chat_id, body=f"Echo: {user_message.body if hasattr(user_message, 'body') else user_message}")

class DummyPresenter:
    " a Dummy presenter for testing. "
    pass # pylint: disable=unnecessary-pass

def test_telegram_message_controller_handle_text():
    " Test handling text message in TelegramMessageController. "
    controller = TelegramMessageController(use_case=DummyUseCase(), presenter=DummyPresenter())
    chat_id = "user1"
    user_message = "hola mundo"
    result = asyncio.run(controller.handle(chat_id, user_message))
    assert result[0] == chat_id
    assert "Echo: hola mundo" in result[1]

def test_telegram_message_controller_handle_message_obj():
    " Test handling Message object in TelegramMessageController. "
    controller = TelegramMessageController(use_case=DummyUseCase(), presenter=DummyPresenter())
    chat_id = "user2"
    msg = Message(to=chat_id, body="mensaje obj")
    result = asyncio.run(controller.handle(chat_id, msg))
    assert result[0] == chat_id
    assert "Echo: mensaje obj" in result[1]

def test_webchat_message_controller_handle_text():
    " Test handling text message in WebchatMessageController. "
    controller = WebchatMessageController(use_case=DummyUseCase(), presenter=DummyPresenter())
    user_id = "web1"
    user_message = "hola webchat"
    result = asyncio.run(controller.handle(user_id, user_message))
    assert result[0] == user_id
    assert "Echo: hola webchat" in result[1]

def test_webchat_message_controller_handle_message_obj():
    " Test handling Message object in WebchatMessageController. "
    controller = WebchatMessageController(use_case=DummyUseCase(), presenter=DummyPresenter())
    user_id = "web2"
    msg = Message(to=user_id, body="msg obj")
    result = asyncio.run(controller.handle(user_id, msg))
    assert result[0] == user_id
    assert "Echo: msg obj" in result[1]
