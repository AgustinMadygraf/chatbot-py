"""
Tests for GeminiService (src/infrastructure/google_generative_ai/gemini_service.py)
"""
from unittest.mock import MagicMock, mock_open
import pytest
from src.infrastructure.google_generative_ai.gemini_service import GeminiService


def test_gemini_service_init_success(monkeypatch):
    "Mock get_config and genai.configure"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.get_config",
        lambda: {"GOOGLE_GEMINI_API_KEY": "key123"},
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.configure",
        lambda api_key: None,
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    service = GeminiService()
    assert service.api_key == "key123"


def test_gemini_service_init_no_api_key(monkeypatch):
    "Mock get_config and genai.configure with no API key"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.get_config", lambda: {}
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.configure",
        lambda api_key: None,
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    with pytest.raises(ValueError):
        GeminiService()


def test_gemini_service_init_with_instructions(monkeypatch):
    "Mock get_config, genai.configure, and load_system_instructions_from_json"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.get_config",
        lambda: {"GOOGLE_GEMINI_API_KEY": "key123"},
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.configure",
        lambda api_key: None,
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    monkeypatch.setattr(
        GeminiService, "load_system_instructions_from_json", lambda self, path: "INST"
    )
    service = GeminiService(instructions_json_path="dummy.json")
    assert service.system_instructions == "INST"


def test_load_system_instructions_from_json_success(monkeypatch):
    "Test successful loading of system instructions from JSON"
    m = mock_open(read_data='{"instructions": "test instructions"}')
    monkeypatch.setattr("builtins.open", m)
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    result = GeminiService.load_system_instructions_from_json("dummy.json")
    assert result == "test instructions"


def test_load_system_instructions_from_json_file_not_found(monkeypatch):
    "Test loading system instructions when file is not found"

    def raise_fnf(*a, **kw):
        raise FileNotFoundError("not found")

    monkeypatch.setattr("builtins.open", raise_fnf)
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    result = GeminiService.load_system_instructions_from_json("dummy.json")
    assert result is None


def test_load_system_instructions_from_json_json_decode(monkeypatch):
    "Test loading system instructions when JSON is invalid"
    import json as _json

    def raise_json(*a, **kw):
        raise _json.JSONDecodeError("decode error", doc="bad json", pos=0)

    monkeypatch.setattr("builtins.open", mock_open(read_data="bad json"))
    monkeypatch.setattr("json.load", raise_json)
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    result = GeminiService.load_system_instructions_from_json("dummy.json")
    assert result is None


def test_gemini_service_get_response(monkeypatch):
    "Test get_response with system instructions"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.get_config",
        lambda: {"GOOGLE_GEMINI_API_KEY": "key123"},
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.configure",
        lambda api_key: None,
    )
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "respuesta generada"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.GenerativeModel",
        lambda name: mock_model,
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    service = GeminiService()
    result = service.get_response("hola", system_instructions="INST")
    assert result == "respuesta generada"


def test_gemini_service_get_response_no_instructions(monkeypatch):
    "Test get_response without system instructions"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.get_config",
        lambda: {"GOOGLE_GEMINI_API_KEY": "key123"},
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.configure",
        lambda api_key: None,
    )
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "sin instrucciones"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.GenerativeModel",
        lambda name: mock_model,
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    service = GeminiService()
    result = service.get_response("hola")
    assert result == "sin instrucciones"


def test_gemini_service_get_response_value_error(monkeypatch):
    "Test get_response handles ValueError from model"
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.get_config",
        lambda: {"GOOGLE_GEMINI_API_KEY": "key123"},
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.configure",
        lambda api_key: None,
    )
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = ValueError("fail")
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.genai.GenerativeModel",
        lambda name: mock_model,
    )
    monkeypatch.setattr(
        "src.infrastructure.google_generative_ai.gemini_service.logger", MagicMock()
    )
    service = GeminiService()
    result = service.get_response("hola")
    assert "Error al generar respuesta" in result
