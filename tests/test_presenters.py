"""
Tests for TelegramMessagePresenter and MarkdownConverter.
"""

from src.entities.message import Message
from src.interface_adapter.presenters.markdown_converter import MarkdownConverter
from src.interface_adapter.presenters.telegram_presenter import TelegramMessagePresenter


def test_markdown_converter_bold_and_italic():
    "Test conversion of bold and italic markdown."
    converter = MarkdownConverter()
    text = "**bold** and *italic*"
    result = converter.convert(text)
    # Should convert bold and italic to _bold_ and _italic_, and escape special chars
    assert "_bold_" in result
    assert "_italic_" in result
    # Should escape special chars
    for char in ["[", "]", "(", ")", "!", "."]:
        assert result.count("\\" + char) == text.count(char)


def test_telegram_message_presenter_markdown():
    "Test TelegramMessagePresenter with markdown input."
    presenter = TelegramMessagePresenter()
    msg = Message(to="user", body="**Hola** *mundo*!")
    result = presenter.present(msg)
    assert isinstance(result, list)
    assert result[0]["parse_mode"] == "MarkdownV2"
    assert "_Hola_" in result[0]["text"]
    assert "_mundo_" in result[0]["text"]
    assert "\\!" in result[0]["text"]


def test_telegram_message_presenter_invalid_markdown(monkeypatch):
    "Test TelegramMessagePresenter handles invalid markdown gracefully."
    presenter = TelegramMessagePresenter()
    msg = Message(to="user", body="*texto desbalanceado")
    # Forzar MarkdownValidator a lanzar ValueError
    monkeypatch.setattr(
        presenter.validator,
        "validate",
        lambda t: (_ for _ in ()).throw(ValueError("desbalanceado")),
    )
    result = presenter.present(msg)
    assert result[0]["parse_mode"] is None
    assert "texto desbalanceado" in result[0]["text"]


def test_telegram_message_presenter_long_message():
    "Test TelegramMessagePresenter splits long messages."
    presenter = TelegramMessagePresenter()
    long_text = "Hola " + ("mundo " * 1000)
    msg = Message(to="user", body=long_text)
    result = presenter.present(msg)
    assert isinstance(result, list)
    assert len(result) > 1  # Debe dividir el mensaje en partes
