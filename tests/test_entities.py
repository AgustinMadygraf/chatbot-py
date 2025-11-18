"""
Path: tests/test_entities.py
"""

import pytest

from src.entities.gemini_responder import GeminiResponder
from src.entities.message import Message


def test_message_creation():
    "Crea una instancia de Message y verifica sus atributos."
    msg = Message(to="user", body="Hola")
    assert msg.to == "user"
    assert msg.body == "Hola"


def test_gemini_responder_get_response_not_implemented():
    "Test para GeminiResponder: get_response debe lanzar NotImplementedError"
    responder = GeminiResponder()
    with pytest.raises(NotImplementedError):
        responder.get_response("prompt")
