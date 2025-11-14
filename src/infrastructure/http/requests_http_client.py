"""
Path: src/infrastructure/http/requests_http_client.py
"""

import requests
from typing import Any, Dict, Optional
from src.infrastructure.http.http_client import HttpClient


class RequestsHttpClient(HttpClient):
    "Implementación de HttpClient usando la librería requests."

    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        "Envía una solicitud POST y devuelve la respuesta (puede ser un objeto Response o dict)."
        response = requests.post(url, json=json, timeout=timeout)
        response.raise_for_status()
        return response
