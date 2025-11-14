## Removed empty function definitions that caused IndentationError
import pytest
from src.interface_adapter.controller.telegram_controller import TelegramMessageController
from src.interface_adapter.controller.webchat_controller import WebchatMessageController
from src.entities.message import Message

class DummyUseCase:
    async def execute(self, chat_id, user_message, prompt=None):
        _ = prompt
        return Message(
            to=chat_id,
            body=f"Echo: {user_message.body if hasattr(user_message, 'body') else user_message}",
        )

class DummyPresenter:
    pass

@pytest.mark.asyncio
async def test_telegram_message_controller_handle_text():
    controller = TelegramMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    chat_id = "user1"
    user_message = "hola mundo"
    result = await controller.handle(chat_id, user_message)
    assert result[0] == chat_id
    assert "Echo: hola mundo" in result[1]

@pytest.mark.asyncio
async def test_telegram_message_controller_handle_message_obj():
    controller = TelegramMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    chat_id = "user2"
    msg = Message(to=chat_id, body="mensaje obj")
    result = await controller.handle(chat_id, msg)
    assert result[0] == chat_id
    assert "Echo: mensaje obj" in result[1]

@pytest.mark.asyncio
async def test_webchat_message_controller_handle_text():
    controller = WebchatMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    user_id = "web1"
    user_message = "hola webchat"
    result = await controller.handle(user_id, user_message)
    assert result[0] == user_id
    assert "Echo: hola webchat" in result[1]

@pytest.mark.asyncio
async def test_webchat_message_controller_handle_message_obj():
    controller = WebchatMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    user_id = "web2"
    msg = Message(to=user_id, body="msg obj")
    result = await controller.handle(user_id, msg)
    assert result[0] == user_id
    assert "Echo: msg obj" in result[1]

class DummyUseCaseEmpty:
    async def execute(self, _chat_id, _user_message, prompt=None):
        class DummyMsg:
            body = ""
        return DummyMsg()

@pytest.mark.asyncio
async def test_telegram_message_controller_handle_empty_response():
    controller = TelegramMessageController(
        use_case=DummyUseCaseEmpty(), presenter=DummyPresenter()
    )
    chat_id = "user3"
    user_message = "hola"
    result = await controller.handle(chat_id, user_message)
    assert result[1] == "No tengo una respuesta en este momento."

@pytest.mark.asyncio
async def test_telegram_message_controller_handle_with_entities():
    controller = TelegramMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    chat_id = "user4"
    user_message = "hola mundo"
    entities = [
        {"offset": 0, "length": 4, "type": "bold"},
        {"offset": 5, "length": 5, "type": "italic"},
    ]
    result = await controller.handle(chat_id, user_message, entities=entities)
    assert "**hola**" in result[1]
    assert "*mundo*" in result[1]

@pytest.mark.asyncio
async def test_telegram_message_controller_handle_no_entities():
    controller = TelegramMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    chat_id = "user5"
    user_message = "sin entidades"
    result = await controller.handle(chat_id, user_message)
    assert result[0] == chat_id
    assert "Echo: sin entidades" in result[1]

@pytest.mark.asyncio
async def test_telegram_message_controller_handle_unknown_entity_type():
    controller = TelegramMessageController(
        use_case=DummyUseCase(), presenter=DummyPresenter()
    )
    chat_id = "user6"
    user_message = "hola mundo"
    entities = [{"offset": 0, "length": 4, "type": "unknown"}]
    result = await controller.handle(chat_id, user_message, entities=entities)
    assert result[0] == chat_id
    assert "Echo: hola mundo" in result[1]
