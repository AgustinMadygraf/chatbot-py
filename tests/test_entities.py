"""
Path: tests/test_entities.py
"""

from src.entities.message import Message

def test_message_creation():
    "Crea una instancia de Message y verifica sus atributos."
    msg = Message(to="user", body="Hola")
    assert msg.to == "user"
    assert msg.body == "Hola"
