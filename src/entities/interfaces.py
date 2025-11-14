"""
Path: src/entities/interfaces.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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


class HttpClient(ABC):
    "Interfaz para un cliente HTTP minimalista, desacoplado de librerías externas."

    @abstractmethod
    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        "Envía una solicitud POST y devuelve la respuesta (puede ser un objeto Response o dict)."
        pass  # pylint: disable=unnecessary-pass
