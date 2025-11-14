"""
Path: src/entities/interfaces.py
"""

from abc import ABC, abstractmethod
from typing import Any


class SystemInstructionsRepository(ABC):
    "Interfaz para repositorios de instrucciones de sistema."

    @abstractmethod
    def load(self) -> Any:
        "Carga instrucciones desde una fuente (por ejemplo, archivo JSON)."
        pass  # pylint: disable=unnecessary-pass


class GeminiResponderService(ABC):
    "Interfaz para servicios que generan respuestas tipo Gemini."

    @abstractmethod
    def get_response(self, prompt: str, system_instructions: Any = None) -> str:
        "Genera una respuesta usando el modelo Gemini o similar."
        pass  # pylint: disable=unnecessary-pass
