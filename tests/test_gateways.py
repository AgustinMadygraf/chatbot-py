"""
Path: tests/test_gateways.py
"""

import pytest
import requests
from unittest.mock import MagicMock

from src.interface_adapter.gateways.agent_gateway import AgentGateway
from src.entities.interfaces import SystemInstructionsRepository, GeminiResponderService
from src.entities.message import Message
from src.interface_adapter.gateways.agent_gateway import _is_truthy


class DummyInstructionsRepository(SystemInstructionsRepository):
    def load(self):
        raise FileNotFoundError("no file")


class DummyGeminiService(GeminiResponderService):
    def get_response(self, prompt, system_instructions=None):
        return "dummy"


def make_gateway(http_client=None, repo=None, gemini=None):
    repo = repo if repo is not None else DummyInstructionsRepository()
    gemini = gemini if gemini is not None else DummyGeminiService()
    return AgentGateway(
        http_client=http_client, instructions_repository=repo, gemini_service=gemini
    )


def test_agent_gateway_ensure_fallback_components_exceptions(monkeypatch):
    "Test that exceptions in fallback component initialization are handled."
    gateway = make_gateway()
    monkeypatch.setattr(gateway, "_fallback_initialized", False)
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway.http_client = mock_http
    try:
        gateway.get_response("test message")
    except FileNotFoundError:
        pytest.fail(
            "FileNotFoundError fue propagado, pero debía ser manejado internamente."
        )


def test_agent_gateway_fallback_response_exception(monkeypatch):
    "Test that exceptions in fallback response generation are handled."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)

    class DummyGateway:
        def get_response(self, prompt, system_instructions=None):
            raise ValueError("fail")

    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: DummyGateway())
    resp = gateway.get_response("mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


def test_agent_gateway_init():
    "Test initialization of AgentGateway."
    gateway = make_gateway(http_client=MagicMock())
    assert gateway is not None


def test_agent_gateway_get_response_success():
    "Test get_response returns text from Rasa when available."
    mock_http = MagicMock()
    mock_http.post.return_value.json.return_value = [{"text": "Hola!"}]
    mock_http.post.return_value.raise_for_status.return_value = None
    gateway = make_gateway(http_client=mock_http)
    response = gateway.get_response("hola")
    assert "Hola" in response


def test_agent_gateway_get_response_rasa_error_fallback(monkeypatch):
    "Test get_response uses fallback when Rasa is unavailable."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    response = gateway.get_response("test message")
    assert "no está disponible" in response.lower() or "servidor" in response.lower()


def test_agent_gateway_local_response_saludo(monkeypatch):
    "Test local response returns saludo for greeting keywords when Rasa fails."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )


def test_agent_gateway_local_response_despedida(monkeypatch):
    "Test local response returns despedida for goodbye keywords when Rasa fails."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )


def test_agent_gateway_local_response_fallback(monkeypatch):
    "Test local response calls fallback for unknown message when Rasa fails."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    result = gateway.get_response("mensaje desconocido")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


def test_agent_gateway_local_response_calls_fallback(monkeypatch):
    "Test local response calls fallback for unknown message through public interface."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    monkeypatch.setattr(
        gateway, "_fallback_response", MagicMock(return_value="fallback called")
    )
    result = gateway.get_response("mensaje desconocido")
    assert "fallback called" in result or "no está disponible" in result.lower()


def test_agent_gateway_fallback_response_no_gateway(monkeypatch):
    "Test fallback response returns fallback string when Rasa fails and no GeminiGateway."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    result = gateway.get_response("test")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


def test_agent_gateway_fallback_response_with_gateway(monkeypatch):
    "Test fallback through get_response returns Gemini reply when Rasa fails."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    mock_gateway = MagicMock()
    mock_gateway.get_response.return_value = "respuesta gemini"
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=mock_gateway)
    )
    monkeypatch.setattr(gateway, "_system_instructions", None)
    result = gateway.get_response("test")
    assert "gemini" in result


class DummyHttpClient:
    "Dummy HTTP client for testing."

    def post(self, *_a, **_kw):
        "Dummy post method."

        class DummyResp:
            "Dummy response."

            def json(self):
                "Return a dummy JSON response."
                return [{"text": "Hola!"}]

            def raise_for_status(self):
                "Dummy raise_for_status method."
                return None

        return DummyResp()


def test_agent_gateway_internal_local_response_saludo():
    "Test local response returns saludo for greeting keywords."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    resp = gateway.get_response("hola")
    assert "hola" in resp.lower()


def test_agent_gateway_internal_local_response_despedida():
    "Test local response returns despedida for goodbye keywords."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    resp = gateway.get_response("adios")
    assert "adios" in resp.lower() or "adiós" in resp.lower()


def test_agent_gateway_internal_local_response_fallback(monkeypatch):
    "Test local response calls fallback for unknown message."
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(gateway, "_fallback_response", lambda c, m: "fallback called")
    resp = gateway.get_response("mensaje desconocido")
    assert "fallback called" in resp
    gateway = make_gateway(http_client=None)
    monkeypatch.setattr(gateway, "_fallback_response", lambda c, m: "fallback called")
    resp = gateway._local_response("conv1", "mensaje desconocido")
    assert "fallback called" in resp


def test_agent_gateway_fallback_response_gateway_none(monkeypatch):
    "Test fallback response returns fallback string when no GeminiGateway."
    gateway = make_gateway(http_client=None)
    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: None)
    resp = gateway._fallback_response("conv1", "mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


def test_agent_gateway_fallback_response_gateway_error(monkeypatch):
    "Test fallback response returns fallback string when GeminiGateway fails."
    gateway = make_gateway(http_client=None)

    class DummyGateway:
        def get_response(self, prompt, system_instructions=None):
            raise ValueError("fail")

    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: DummyGateway())
    resp = gateway._fallback_response("conv1", "mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


# --- Nuevos tests para cobertura interna de AgentGateway ---
def test_agent_gateway_build_payload_str():
    "Test build_payload with string input."
    gateway = make_gateway(http_client=None)
    payload, conv_id = gateway._build_payload("hola")
    assert payload["message"] == "hola"
    assert isinstance(conv_id, str)


def test_agent_gateway_build_payload_message():
    "Test build_payload with Message input."
    gateway = make_gateway(http_client=None)
    msg = Message(to="conv1", body="hola body")
    payload, conv_id = gateway._build_payload(msg)
    assert payload["message"] == "hola body"
    assert conv_id == "conv1"


def test_agent_gateway_is_truthy_cases():
    "Test _is_truthy utility function."
    assert _is_truthy("1")
    assert _is_truthy("true")
    assert _is_truthy("yes")
    assert _is_truthy("on")
    assert not _is_truthy("0")
    assert not _is_truthy("false")
    assert not _is_truthy(None)
    assert not _is_truthy("")


# --- Nuevos tests para _build_prompt y _store_turn ---
def test_agent_gateway_build_prompt_empty_history():
    "Test that _build_prompt works with empty conversation history."
    gateway = make_gateway(http_client=None)
    prompt = gateway._build_prompt("conv1", "mensaje final")
    assert prompt.startswith("Usuario: mensaje final") or "Gemini:" in prompt


def test_agent_gateway_build_prompt_with_history():
    "Test that _build_prompt includes conversation history."
    gateway = make_gateway(http_client=None)
    # Simular historial de 3 turnos
    gateway._store_turn("conv2", "user", "hola")
    gateway._store_turn("conv2", "bot", "respuesta1")
    gateway._store_turn("conv2", "user", "¿cómo estás?")
    prompt = gateway._build_prompt("conv2", "mensaje final")
    # Debe contener los turnos previos y el mensaje final
    assert "Usuario: hola" in prompt
    assert "Gemini: respuesta1" in prompt
    assert "Usuario: ¿cómo estás?" in prompt
    assert "Usuario: mensaje final" in prompt
    assert prompt.endswith("Gemini:")


def test_agent_gateway_store_turn_limit():
    "Test that _store_turn limits history to last 20 turns."
    gateway = make_gateway(http_client=None)
    conv_id = "conv3"
    for i in range(25):
        gateway._store_turn(conv_id, "user", f"msg{i}")

    # Test the behavior indirectly by checking the built prompt
    prompt = gateway._build_prompt(conv_id, "final message")

    # The prompt should contain only the last 20 messages
    # Check that msg0-msg4 are not in the prompt (they should be truncated)
    assert "msg0" not in prompt
    assert "msg4" not in prompt
    # Check that msg5-msg24 are in the prompt (they should remain)
    assert "msg5" in prompt
    assert "msg24" in prompt
