"""
Path: src/infrastructure/requests/requests_http_client.py
"""

import requests

class RequestsHttpClient:
    "Implementación de HttpClient usando la librería requests."
    def post(self, url: str, json: dict, timeout: int = 60):
        "Envía una solicitud POST usando requests."
        return requests.post(url, json=json, timeout=timeout)
