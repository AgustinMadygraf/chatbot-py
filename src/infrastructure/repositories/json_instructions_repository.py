"""
Path: src/infrastructure/repositories/json_instructions_repository.py
"""

import json
from pathlib import Path

from src.shared.logger_rasa_v0 import get_logger

logger = get_logger("json-instructions-repository")


class JsonInstructionsRepository:
    "Repositorio para cargar instrucciones de sistema desde archivos JSON."

    def __init__(self, json_path, key="instructions"):
        self.json_path = json_path
        self.key = key
        logger.debug(
            "Repositorio inicializado | json_path=%s | absoluta=%s",
            json_path,
            Path(json_path).resolve(),
        )

    def _resolve_json_path(self):
        "Intenta resolver la ruta del JSON relativa a la raíz del proyecto."
        candidate = Path(self.json_path)
        logger.debug(
            "Intentando resolver ruta JSON | original=%s | absoluta=%s | existe=%s",
            candidate,
            candidate.is_absolute(),
            candidate.is_file(),
        )
        if candidate.is_file():
            logger.debug("Ruta JSON encontrada directamente | candidata=%s", candidate)
            return candidate

        if not candidate.is_absolute():
            project_root = Path(__file__).resolve().parents[3]
            project_candidate = (project_root / candidate).resolve()
            logger.debug(
                "Evaluando ruta relativa a la raíz | raiz=%s | candidata=%s | existe=%s",
                project_root,
                project_candidate,
                project_candidate.is_file(),
            )
            if project_candidate.is_file():
                logger.debug(
                    "Ruta JSON resuelta usando raíz del proyecto | candidata=%s",
                    project_candidate,
                )
                return project_candidate

        logger.debug(
            "No se pudo resolver la ruta JSON | json_path=%s | absoluta=%s",
            candidate,
            candidate.is_absolute(),
        )
        return None

    def load(self):
        "Carga instrucciones desde un archivo JSON."
        resolved_path = self._resolve_json_path()
        if not resolved_path:
            logger.debug("Resolución de ruta fallida | json_path=%s", self.json_path)
            logger.error("Archivo JSON no encontrado: %s", self.json_path)
            return None
        try:
            logger.debug(
                "Verificando instrucciones | absoluta=%s | existe=%s",
                resolved_path.resolve(),
                resolved_path.is_file(),
            )
            with open(resolved_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug("Contenido JSON leído: %s", data)
            return data.get(self.key)
        except FileNotFoundError:
            logger.debug(
                "FileNotFoundError tras resolución | resuelta=%s",
                resolved_path,
            )
            logger.error("Archivo JSON no encontrado: %s", resolved_path)
            return None
        except json.JSONDecodeError as e:
            logger.error("Error al decodificar JSON: %s", e)
            return None
