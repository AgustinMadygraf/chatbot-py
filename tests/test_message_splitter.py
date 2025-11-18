"""
Tests for MessageSplitter (src/interface_adapter/presenters/message_splitter.py)
"""

from src.interface_adapter.presenters.message_splitter import MessageSplitter


def test_splitter_empty_text():
    splitter = MessageSplitter()
    assert splitter.split("", 10) == []


def test_splitter_short_text():
    splitter = MessageSplitter()
    assert splitter.split("hola", 10) == ["hola"]


def test_splitter_exact_length():
    splitter = MessageSplitter()
    assert splitter.split("abcdefghij", 10) == ["abcdefghij"]


def test_splitter_long_text():
    splitter = MessageSplitter()
    text = "abcdefghij12345"
    # max_len=10, debe dividir en [abcdefghij, 12345]
    assert splitter.split(text, 10) == ["abcdefghij", "12345"]


def test_splitter_multiple_chunks():
    splitter = MessageSplitter()
    text = "a" * 25
    # max_len=8, debe dividir en 4 partes: 8+8+8+1
    assert splitter.split(text, 8) == ["a" * 8, "a" * 8, "a" * 8, "a"]
