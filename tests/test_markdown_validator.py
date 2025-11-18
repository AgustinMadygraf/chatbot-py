"""
Tests for MarkdownValidator (src/interface_adapter/presenters/markdown_validator.py)
"""

import pytest

from src.interface_adapter.presenters.markdown_validator import MarkdownValidator


def test_validator_balanced_asterisks_and_underscores():
    validator = MarkdownValidator()
    validator.validate("**bold** _italic_")  # No debe lanzar


def test_validator_unbalanced_asterisks():
    validator = MarkdownValidator()
    with pytest.raises(ValueError, match="asteriscos"):
        validator.validate("*bold** _italic_")


def test_validator_unbalanced_underscores():
    validator = MarkdownValidator()
    with pytest.raises(ValueError, match="guiones bajos"):
        validator.validate("**bold** _italic")


def test_validator_list_line_asterisk():
    validator = MarkdownValidator()
    # El asterisco de la lista no cuenta para el balanceo
    validator.validate("* item\n**bold**")


def test_validator_empty_text():
    validator = MarkdownValidator()
    validator.validate("")  # No debe lanzar
