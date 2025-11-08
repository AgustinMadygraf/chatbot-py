"""
Path: src/interface_adapter/gateways/instalar_rasa_gateway.py
"""

from typing import Any, Dict

from src.interface_adapter.controllers.instalar_rasa_controller import InstalarRasaController
from src.interface_adapter.presenters.instalar_rasa_presenter import InstalarRasaPresenter

class InstalarRasaGateway:
    " Gateway para la funcionalidad de instalación de Rasa, conecta el controlador con la infraestructura"
    def __init__(self, presenter=None):
        self.presenter = presenter or InstalarRasaPresenter()
        self.controller = InstalarRasaController(presenter=self.presenter)

    def validar_proyecto_descargado(self, valor: Any) -> Dict[str, Any]:
        "Valida el valor del slot proyecto_descargado a través del controlador"
        return self.controller.validar_proyecto_descargado(valor)

    def evaluar_instalacion(self, proyecto_descargado: str, git_instalado: str) -> Dict[str, Any]:
        "Evalúa el estado de la instalación a través del controlador"
        return self.controller.evaluar_instalacion(proyecto_descargado, git_instalado)
