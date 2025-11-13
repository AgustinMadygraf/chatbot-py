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


# --- Nuevos tests para edge cases de GeminiGateway ---
def test_gemini_gateway_get_response_system_instructions_content_string():
    # Usar SystemInstructions real, que es lo que el gateway trata especialmente
    class DummyService:
        def get_response(self, prompt, system_instructions):
            return f"resp:{prompt}:{system_instructions}"

    gateway = GeminiGateway(DummyService())
    sys_inst = SystemInstructions("solo texto")
    result = gateway.get_response("hola", sys_inst)
    assert "solo texto" in result


def test_gemini_gateway_get_response_system_instructions_content_none():
    # Usar SystemInstructions real con None como contenido
    class DummyService:
        def get_response(self, prompt, system_instructions):
            return f"resp:{prompt}:{system_instructions}"

    gateway = GeminiGateway(DummyService())
    sys_inst = SystemInstructions(None)
    result = gateway.get_response("hola", sys_inst)
    # El resultado debe contener la cadena 'None' (str(None))
    assert "None" in result


def test_gemini_gateway_get_response_system_instructions_as_string():
    class DummyService:
        def get_response(self, prompt, system_instructions):
            return f"resp:{prompt}:{system_instructions}"

    gateway = GeminiGateway(DummyService())
    result = gateway.get_response("hola", "instruccion directa")
    assert "instruccion directa" in result


def test_gemini_gateway_get_response_service_exception():
    class DummyService:
        def get_response(self, prompt, system_instructions):
            raise RuntimeError("fallo")

    gateway = GeminiGateway(DummyService())
    try:
        gateway.get_response("hola", "inst")
    except RuntimeError as e:
        assert "fallo" in str(e)


def test_gemini_gateway_get_response_empty_prompt():
    class DummyService:
        def get_response(self, prompt, system_instructions):
            return f"resp:{prompt}:{system_instructions}"

    gateway = GeminiGateway(DummyService())
    result = gateway.get_response("", "inst")
    assert result.startswith("resp:")
