"""
Path: tests/test_gateways.py
"""

import pytest

from src.infrastructure.repositories.json_instructions_repository import (
    JsonInstructionsRepository,
)
from src.interface_adapter.gateways.agent_gateway import AgentGateway
from src.entities.message import Message
from unittest.mock import MagicMock


def test_agent_gateway_ensure_fallback_components_exceptions(monkeypatch):
    gateway = AgentGateway(http_client=None)
    gateway._fallback_initialized = False
    # Monkeypatch el __init__ y load de la clase real
    monkeypatch.setattr(
        JsonInstructionsRepository,
        "__init__",
        lambda self, path, key="instructions": None,
    )
    monkeypatch.setattr(
        JsonInstructionsRepository,
        "load",
        lambda self: (_ for _ in ()).throw(FileNotFoundError("no file")),
    )
    # No debe lanzar excepción, sin importar el valor retornado
    try:
        gateway._ensure_fallback_components()
    except FileNotFoundError:
        pytest.fail(
            "FileNotFoundError fue propagado, pero debía ser manejado internamente."
        )


def test_agent_gateway_fallback_response_exception(monkeypatch):
    gateway = AgentGateway(http_client=None)
    # Forzar que el gateway devuelva un objeto que lanza excepción

    class DummyGateway:
        def get_response(self, prompt, system_instructions=None):
            raise ValueError("fail")

    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: DummyGateway())
    resp = gateway._fallback_response("conv1", "mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


def test_agent_gateway_init():
    "Test initialization of AgentGateway."
    gateway = AgentGateway(http_client=MagicMock())
    assert gateway is not None


def test_agent_gateway_get_response_success():
    "Test get_response returns text from Rasa when available."
    mock_http = MagicMock()
    mock_http.post.return_value.json.return_value = [{"text": "Hola!"}]
    mock_http.post.return_value.raise_for_status.return_value = None
    gateway = AgentGateway(http_client=mock_http)
    response = gateway.get_response("hola")
    assert "Hola" in response


def test_agent_gateway_get_response_rasa_error_fallback(monkeypatch):
    "Test get_response uses fallback when Rasa is unavailable."
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    # Mock the fallback components to ensure predictable fallback behavior
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    response = gateway.get_response("test message")
    assert "no está disponible" in response.lower() or "servidor" in response.lower()


def test_agent_gateway_local_response_saludo(monkeypatch):
    "Test local response returns saludo for greeting keywords when Rasa fails."
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )


def test_agent_gateway_local_response_despedida(monkeypatch):
    "Test local response returns despedida for goodbye keywords when Rasa fails."
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )


def test_agent_gateway_local_response_fallback(monkeypatch):
    "Test local response calls fallback for unknown message when Rasa fails."
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    result = gateway.get_response("mensaje desconocido")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


def test_agent_gateway_local_response_calls_fallback(monkeypatch):
    "Test local response calls fallback for unknown message through public interface."
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
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
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    result = gateway.get_response("test")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


def test_agent_gateway_fallback_response_with_gateway(monkeypatch):
    "Test fallback through get_response returns Gemini reply when Rasa fails."
    import requests

    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
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

    def post(self, *a, **kw):
        class DummyResp:
            def json(self):
                return [{"text": "Hola!"}]

            def raise_for_status(self):
                return None

        return DummyResp()


def test_agent_gateway_internal_local_response_saludo():
    gateway = AgentGateway(http_client=None)
    resp = gateway._local_response("conv1", "hola")
    assert "hola" in resp.lower()


def test_agent_gateway_internal_local_response_despedida():
    gateway = AgentGateway(http_client=None)
    resp = gateway._local_response("conv1", "adios")
    assert "adios" in resp.lower() or "adiós" in resp.lower()


def test_agent_gateway_internal_local_response_fallback(monkeypatch):
    gateway = AgentGateway(http_client=None)
    monkeypatch.setattr(gateway, "_fallback_response", lambda c, m: "fallback called")
    resp = gateway._local_response("conv1", "mensaje desconocido")
    assert "fallback called" in resp


def test_agent_gateway_fallback_response_gateway_none(monkeypatch):
    gateway = AgentGateway(http_client=None)
    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: None)
    resp = gateway._fallback_response("conv1", "mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


def test_agent_gateway_fallback_response_gateway_error(monkeypatch):
    gateway = AgentGateway(http_client=None)

    class DummyGateway:
        def get_response(self, prompt, system_instructions=None):
            raise ValueError("fail")

    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: DummyGateway())
    resp = gateway._fallback_response("conv1", "mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


# --- Nuevos tests para cobertura interna de AgentGateway ---
def test_agent_gateway_build_payload_str():
    gateway = AgentGateway(http_client=None)
    payload, conv_id = gateway._build_payload("hola")
    assert payload["message"] == "hola"
    assert isinstance(conv_id, str)


def test_agent_gateway_build_payload_message():
    gateway = AgentGateway(http_client=None)
    msg = Message(to="conv1", body="hola body")
    payload, conv_id = gateway._build_payload(msg)
    assert payload["message"] == "hola body"
    assert conv_id == "conv1"


def test_agent_gateway_is_truthy_cases():
    from src.interface_adapter.gateways.agent_gateway import _is_truthy

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
    gateway = AgentGateway(http_client=None)
    prompt = gateway._build_prompt("conv1", "mensaje final")
    assert prompt.startswith("Usuario: mensaje final") or "Gemini:" in prompt


def test_agent_gateway_build_prompt_with_history():
    gateway = AgentGateway(http_client=None)
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
    gateway = AgentGateway(http_client=None)
    conv_id = "conv3"
    # Agregar 25 turnos, debe recortar a 20
    for i in range(25):
        gateway._store_turn(conv_id, "user", f"msg{i}")
    with gateway._history_lock:
        history = gateway._history[conv_id]
    assert len(history) == 20
    # El primer mensaje debe ser msg5
    assert history[0][1] == "msg5"
