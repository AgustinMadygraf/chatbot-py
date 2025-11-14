"""
Path: src/infrastructure/http/http_client.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
