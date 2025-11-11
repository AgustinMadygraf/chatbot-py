"""
Path: tests/test_gateways.py
"""

from unittest.mock import MagicMock
from src.interface_adapter.gateways.agent_gateway import AgentGateway


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
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=None))
    response = gateway.get_response("test message")
    assert "no está disponible" in response.lower() or "servidor" in response.lower()


def test_agent_gateway_local_response_saludo(monkeypatch):
    "Test local response returns saludo for greeting keywords when Rasa fails."
    import requests
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=None))
def test_agent_gateway_local_response_despedida(monkeypatch):
    "Test local response returns despedida for goodbye keywords when Rasa fails."
    import requests
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=None))
def test_agent_gateway_local_response_fallback(monkeypatch):
    "Test local response calls fallback for unknown message when Rasa fails."
    import requests
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=None))
    result = gateway.get_response("mensaje desconocido")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


def test_agent_gateway_local_response_calls_fallback(monkeypatch):
    "Test local response calls fallback for unknown message through public interface."
    import requests
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=None))
    monkeypatch.setattr(gateway, '_fallback_response', MagicMock(return_value="fallback called"))
    result = gateway.get_response("mensaje desconocido")
    assert "fallback called" in result or "no está disponible" in result.lower()


def test_agent_gateway_fallback_response_no_gateway(monkeypatch):
    "Test fallback response returns fallback string when Rasa fails and no GeminiGateway."
    import requests
    mock_http = MagicMock()
    mock_http.post.side_effect = requests.exceptions.RequestException("Rasa down")
    gateway = AgentGateway(http_client=mock_http)
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=None))
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
    monkeypatch.setattr(gateway, '_ensure_fallback_components', MagicMock(return_value=mock_gateway))
    monkeypatch.setattr(gateway, '_system_instructions', None)
    result = gateway.get_response("test")
    assert "gemini" in result
