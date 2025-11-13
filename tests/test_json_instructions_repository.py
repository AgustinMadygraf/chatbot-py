"""
Path: tests/test_json_instructions_repository.py
"""

import json

from src.infrastructure.repositories.json_instructions_repository import (
    JsonInstructionsRepository,
)


def test_load_success(tmp_path):
    """"""
    # Crea un archivo JSON válido
    data = {"instructions": ["haz esto", "haz lo otro"]}
    json_file = tmp_path / "test_instructions.json"
    json_file.write_text(json.dumps(data), encoding="utf-8")

    repo = JsonInstructionsRepository(str(json_file))
    result = repo.load()
    assert result == ["haz esto", "haz lo otro"]


def test_load_file_not_found():
    repo = JsonInstructionsRepository("archivo_inexistente.json")
    assert repo.load() is None


def test_load_json_decode_error(tmp_path):
    # Crea un archivo JSON inválido
    json_file = tmp_path / "malformado.json"
    json_file.write_text("{invalido: true", encoding="utf-8")

    repo = JsonInstructionsRepository(str(json_file))
    assert repo.load() is None


def test_load_custom_key(tmp_path):
    # Crea un archivo JSON con una clave personalizada
    data = {"custom": ["instrucción"]}
    json_file = tmp_path / "custom.json"
    json_file.write_text(json.dumps(data), encoding="utf-8")

    repo = JsonInstructionsRepository(str(json_file), key="custom")
    result = repo.load()
    assert result == ["instrucción"]


def test_resolve_json_path_absolute(tmp_path):
    # Verifica que _resolve_json_path retorna la ruta absoluta si existe el archivo
    json_file = tmp_path / "file.json"
    json_file.write_text("{}", encoding="utf-8")
    repo = JsonInstructionsRepository(str(json_file))
    resolved = repo._resolve_json_path()
    assert resolved == json_file


def test_resolve_json_path_not_found():
    repo = JsonInstructionsRepository("no_existe.json")
    assert repo._resolve_json_path() is None
