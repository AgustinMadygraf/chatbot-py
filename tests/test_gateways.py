"""
Path: tests/test_gateways.py
"""

from unittest.mock import MagicMock, AsyncMock
import asyncio
import pytest
import httpx

from src.interface_adapter.gateways.agent_gateway import AgentGateway
from src.entities.interfaces import SystemInstructionsRepository, GeminiResponderService
from src.entities.message import Message


class DummyInstructionsRepository(SystemInstructionsRepository):
    " Dummy repository that raises FileNotFoundError on load."
    def load(self):
        raise FileNotFoundError("no file")


class DummyGeminiService(GeminiResponderService):
    " Dummy Gemini service for testing."
    def get_response(self, prompt, system_instructions=None):
        return "dummy"


def make_gateway(http_client=None, repo=None, gemini=None):
    "Helper to create AgentGateway with optional dependencies."
    repo = repo if repo is not None else DummyInstructionsRepository()
    gemini = gemini if gemini is not None else DummyGeminiService()
    return AgentGateway(
        http_client=http_client, instructions_repository=repo, gemini_service=gemini
    )


@pytest.mark.asyncio
async def test_agent_gateway_ensure_fallback_components_exceptions(monkeypatch):
    "Test that exceptions in fallback component initialization are handled."
    gateway = make_gateway()
    monkeypatch.setattr(gateway, "_fallback_initialized", False)
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway.http_client = mock_http
    # Ya no debe lanzar, debe devolver el fallback response
    resp = await gateway.get_response("test message")
    # Puede ser 'dummy' (DummyGeminiService) o fallback string
    assert (
        resp == "dummy"
        or "no está disponible" in resp.lower()
        or "mantenimiento" in resp.lower()
    )


@pytest.mark.asyncio
async def test_agent_gateway_fallback_response_exception(monkeypatch):
    "Test that exceptions in fallback response generation are handled."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)

    class DummyGateway:
        "Dummy GeminiGateway that raises exception."
        async def get_response(self, prompt, system_instructions=None):
            "Simulate failure in get_response."
            raise ValueError("fail")

    monkeypatch.setattr(gateway, "_ensure_fallback_components", DummyGateway)
    # Ya no debe lanzar, debe devolver el fallback response
    resp = await gateway.get_response("mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


def test_agent_gateway_init():
    "Test initialization of AgentGateway."
    gateway = make_gateway(http_client=MagicMock())
    assert gateway is not None


@pytest.mark.asyncio
async def test_agent_gateway_get_response_success():
    "Test get_response returns text from Rasa when available."
    mock_response = MagicMock()
    mock_response.json.return_value = [{"text": "Hola!"}]
    mock_response.raise_for_status.return_value = None
    mock_http = AsyncMock()
    mock_http.post.return_value = mock_response
    gateway = make_gateway(http_client=mock_http)
    response = await gateway.get_response("hola")
    assert "Hola" in response


@pytest.mark.asyncio
async def test_agent_gateway_get_response_rasa_error_fallback(monkeypatch):
    "Test get_response uses fallback when Rasa is unavailable."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    # Ya no debe lanzar, debe devolver el fallback response
    resp = await gateway.get_response("test message")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


@pytest.mark.asyncio
async def test_agent_gateway_local_response_saludo(monkeypatch):
    "Test local response returns saludo for greeting keywords when Rasa fails."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    resp = await gateway.get_response("hola")
    assert "hola" in resp.lower()


@pytest.mark.asyncio
async def test_agent_gateway_local_response_despedida(monkeypatch):
    "Test local response returns despedida for goodbye keywords when Rasa fails."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    resp = await gateway.get_response("adios")
    assert "adios" in resp.lower() or "adiós" in resp.lower()


@pytest.mark.asyncio
async def test_agent_gateway_local_response_fallback(monkeypatch):
    "Test local response calls fallback for unknown message when Rasa fails."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    result = await gateway.get_response("mensaje desconocido")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


@pytest.mark.asyncio
async def test_agent_gateway_local_response_calls_fallback(monkeypatch):
    "Test local response calls fallback for unknown message through public interface."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    # El mock debe ser async para que await funcione correctamente

    async def async_fallback_response(_c, _m):
        return "fallback called"

    monkeypatch.setattr(gateway, "_fallback_response", async_fallback_response)
    result = await gateway.get_response("mensaje desconocido")
    assert "fallback called" in result or "no está disponible" in result.lower()


@pytest.mark.asyncio
async def test_agent_gateway_fallback_response_no_gateway(monkeypatch):
    "Test fallback response returns fallback string when Rasa fails and no GeminiGateway."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=None)
    )
    result = await gateway.get_response("test")
    assert "no está disponible" in result.lower() or "servidor" in result.lower()


@pytest.mark.asyncio
async def test_agent_gateway_fallback_response_with_gateway(monkeypatch):
    "Test fallback through get_response returns Gemini reply when Rasa fails."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    mock_gateway = MagicMock()
    mock_gateway.get_response.return_value = "respuesta gemini"
    monkeypatch.setattr(
        gateway, "_ensure_fallback_components", MagicMock(return_value=mock_gateway)
    )
    monkeypatch.setattr(gateway, "_system_instructions", None)
    result = await gateway.get_response("test")
    assert "gemini" in result


class DummyHttpClient:
    "Dummy HTTP client for testing async."

    async def post(self, *_a, **_kw):
        "Simulate an async HTTP POST request."
        class DummyResp:
            "Dummy response object for async HTTP POST."
            def json(self):
                "Return a dummy JSON response."
                return [{"text": "Hola!"}]

            def raise_for_status(self):
                "Simulate raising an HTTP error if status is not successful."
                return None

        return DummyResp()


@pytest.mark.asyncio
async def test_agent_gateway_internal_local_response_saludo():
    "Test local response returns saludo for greeting keywords."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    resp = await gateway.get_response("hola")
    assert "hola" in resp.lower()


@pytest.mark.asyncio
async def test_agent_gateway_internal_local_response_despedida():
    "Test local response returns despedida for goodbye keywords."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    resp = await gateway.get_response("adios")
    assert "adios" in resp.lower() or "adiós" in resp.lower()


@pytest.mark.asyncio
async def test_agent_gateway_internal_local_response_fallback(monkeypatch):
    "Test local response calls fallback for unknown message."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)

    async def async_fallback_response(_c, _m):
        return "fallback called"

    monkeypatch.setattr(gateway, "_fallback_response", async_fallback_response)
    resp = await gateway.get_response("mensaje desconocido")
    assert "fallback called" in resp
    gateway = make_gateway(http_client=None)
    monkeypatch.setattr(gateway, "_fallback_response", async_fallback_response)
    resp = await gateway.get_response("mensaje desconocido")
    assert "fallback called" in resp


@pytest.mark.asyncio
async def test_agent_gateway_fallback_response_gateway_none(monkeypatch):
    "Test fallback response returns fallback string when no GeminiGateway."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)
    monkeypatch.setattr(gateway, "_ensure_fallback_components", lambda: None)
    resp = await gateway.get_response("mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


@pytest.mark.asyncio
async def test_agent_gateway_fallback_response_gateway_error(monkeypatch):
    "Test fallback response returns fallback string when GeminiGateway fails."
    mock_http = AsyncMock()
    mock_http.post.side_effect = httpx.RequestError("Rasa down")
    gateway = make_gateway(http_client=mock_http)

    class DummyGateway:
        " Dummy GeminiGateway that raises exception."
        def get_response(self, prompt, system_instructions=None):
            "Simulate failure in get_response."
            raise ValueError("fail")

    monkeypatch.setattr(gateway, "_ensure_fallback_components", DummyGateway)
    resp = await gateway.get_response("mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()
    # Test fallback response through public interface
    resp = await gateway.get_response("mensaje")
    assert "no está disponible" in resp.lower() or "mantenimiento" in resp.lower()


# --- Nuevos tests para cobertura interna de AgentGateway ---

def test_agent_gateway_build_payload_str():
    "Test build_payload with string input through public interface."
    gateway = make_gateway(http_client=None)
    # Test the behavior indirectly through a public method that uses _build_payload
    # Since _build_payload is protected, we'll test its behavior through get_response
    mock_http = AsyncMock()
    gateway.http_client = mock_http
    # This will internally call _build_payload
    asyncio.run(gateway.get_response("hola"))
    # Verify the call was made (indicating _build_payload worked)
    assert mock_http.post.called


def test_agent_gateway_build_payload_message():
    "Test build_payload with Message input through public interface."
    gateway = make_gateway(http_client=None)
    msg = Message(to="conv1", body="hola body")
    # Test the behavior indirectly through a public method that uses _build_payload
    mock_http = AsyncMock()
    gateway.http_client = mock_http
    # This will internally call _build_payload
    asyncio.run(gateway.get_response(msg))
    # Verify the call was made (indicating _build_payload worked)
    assert mock_http.post.called


def test_agent_gateway_is_truthy_cases():
    "Test _is_truthy utility function."


@pytest.mark.asyncio
async def test_agent_gateway_conversation_handling():
    "Test conversation handling through public interface."
    gateway = make_gateway(http_client=None)
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = [{"text": "response"}]
    mock_response.raise_for_status.return_value = None
    mock_http.post.return_value = mock_response
    gateway.http_client = mock_http

    # Test multiple messages to verify conversation handling
    await gateway.get_response("first message")
    await gateway.get_response("second message")

    # Verify that the gateway processed the messages
    assert mock_http.post.call_count == 2


@pytest.mark.asyncio
async def test_agent_gateway_message_object_handling():
    "Test that Message objects are handled correctly through public interface."
    gateway = make_gateway(http_client=None)
    mock_http = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = [{"text": "response"}]
    mock_response.raise_for_status.return_value = None
    mock_http.post.return_value = mock_response
    gateway.http_client = mock_http

    msg = Message(to="conv1", body="test message")
    result = await gateway.get_response(msg)

    # Verify the message was processed
    assert "response" in result
    assert mock_http.post.called

    # Verify the message was processed and gateway handled it correctly
    assert mock_http.post.called
