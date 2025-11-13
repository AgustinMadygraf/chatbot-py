import pytest
from unittest.mock import MagicMock
from src.interface_adapter.gateways.gemini_gateway import GeminiGateway
from src.entities.system_instructions import SystemInstructions

class DummyService:
    def __init__(self):
        self.last_args = None
    def get_response(self, prompt, system_instructions):
        self.last_args = (prompt, system_instructions)
        return f"respuesta:{prompt}:{system_instructions}"

def test_gemini_gateway_get_response_with_system_instructions():
    service = DummyService()
    gateway = GeminiGateway(service)
    sys_inst = SystemInstructions(["haz esto"])
    result = gateway.get_response("hola", sys_inst)
    assert result.startswith("respuesta:hola:")
    # Debe pasar el string de system_instructions
    assert service.last_args[0] == "hola"
    assert isinstance(service.last_args[1], str)
    assert "haz esto" in service.last_args[1]

def test_gemini_gateway_get_response_without_system_instructions():
    service = DummyService()
    gateway = GeminiGateway(service)
    result = gateway.get_response("hola")
    assert result.startswith("respuesta:hola:")
    assert service.last_args[0] == "hola"
    assert service.last_args[1] is None