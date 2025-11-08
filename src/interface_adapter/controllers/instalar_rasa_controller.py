"""
Path: src/interface_adapter/controllers/instalar_rasa_controller.py
"""

from src.use_cases.validar_instalacion_rasa import ValidarInstalacionRasaUseCase
from src.interface_adapter.presenters.instalar_rasa_presenter import InstalarRasaPresenter

class InstalarRasaController:
    "Controlador para la funcionalidad de instalación de Rasa, agnóstico de infraestructura"
    def __init__(self, presenter=None):
        self.presenter = presenter or InstalarRasaPresenter()
        self.use_case = ValidarInstalacionRasaUseCase()

    def validar_proyecto_descargado(self, valor):
        "Valida el estado del proyecto y determina acciones a tomar"
        if not isinstance(valor, str):
            return {"valor_valido": False, "mensaje": self.presenter.mensaje_pregunta_proyecto_descargado()}

        val = valor.lower().strip()
        if val not in ["si", "sí", "no"]:
            return {"valor_valido": False, "mensaje": self.presenter.mensaje_pregunta_proyecto_descargado()}

        proyecto = self.use_case.validar_proyecto_descargado(val)
        return {
            "valor_valido": True,
            "valor_normalizado": "si" if proyecto.esta_descargado else "no",
            "proyecto": proyecto
        }

    def evaluar_instalacion(self, proyecto_descargado, git_instalado):
        "Evalúa el estado completo de instalación y determina mensajes"
        proyecto = self.use_case.validar_proyecto_descargado(proyecto_descargado)
        git = self.use_case.validar_git_instalado(git_instalado)
        resultado = self.use_case.necesita_descarga_y_git(proyecto, git)

        mensajes = []
        if resultado["necesita_descarga"]:
            if resultado["puede_clonar"]:
                mensajes.append(self.presenter.mensaje_guia_clonar_proyecto())
            else:
                mensajes.append(self.presenter.mensaje_git_requerido())

        return {
            "mensajes": mensajes,
            "proyecto_descargado": "si" if proyecto.esta_descargado else "no",
            "git_instalado": "si" if git.puede_clonar() else "no"
        }
