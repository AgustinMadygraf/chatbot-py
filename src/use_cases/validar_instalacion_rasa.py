"""
Path: src/use_cases/validar_instalacion_rasa.py
"""

from src.entities.proyecto_entity import ProyectoEntity
from src.entities.git_entity import GitEntity

class ValidarInstalacionRasaUseCase:
    "Encapsula la lógica de validación de instalación de Rasa y Git"
    @staticmethod
    def validar_proyecto_descargado(slot_value: str) -> ProyectoEntity:
        "Valida si el proyecto está descargado basado en el valor del slot"
        val = slot_value.lower().strip()
        return ProyectoEntity(esta_descargado=(val in ["si", "sí"]))

    @staticmethod
    def validar_git_instalado(slot_value: str) -> GitEntity:
        "Valida si Git está instalado basado en el valor del slot"
        val = slot_value.lower().strip()
        return GitEntity(esta_instalado=(val == "si" or val == "sí"))

    @staticmethod
    def necesita_descarga_y_git(proyecto: ProyectoEntity, git: GitEntity) -> dict:
        "Devuelve dict con flags para side-effects (ej: mensajes)"
        return {
            "necesita_descarga": proyecto.necesita_descarga(),
            "puede_clonar": git.puede_clonar()
        }
