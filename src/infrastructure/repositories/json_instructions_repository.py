"""
Path: src/infrastructure/repositories/json_instructions_repository.py
"""

import json
from pathlib import Path
from src.shared.logger_rasa_v0 import get_logger

logger = get_logger("json-instructions-repository")

class JsonInstructionsRepository:
    """Repositorio para cargar instrucciones de sistema desde archivos JSON."""

    def __init__(self, json_path, key="instructions"):
        self.json_path = json_path
        self.key = key
        logger.debug(
            "Repositorio inicializado | json_path=%s | absoluta=%s",
            json_path,
            Path(json_path).resolve(),
        )

    def load(self):
        """Carga instrucciones desde un archivo JSON."""
        try:
            json_path_obj = Path(self.json_path)
            logger.debug(
                "Verificando instrucciones | absoluta=%s | existe=%s",
                json_path_obj.resolve(),
                json_path_obj.is_file(),
            )
            with open(json_path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug("Contenido JSON leído: %s", data)
            return data.get(self.key)
        except FileNotFoundError:
            logger.error("Archivo JSON no encontrado: %s", self.json_path)
            return None
        except json.JSONDecodeError as e:
            logger.error("Error al decodificar JSON: %s", e)
            return None
