"""
Path: src/entities/proyecto_entity.py"""

class ProyectoEntity:
    "Entidad que representa el estado del proyecto"
    def __init__(self, esta_descargado: bool = False):
        self.esta_descargado = esta_descargado

    def necesita_descarga(self) -> bool:
        "Verifica si el proyecto necesita ser descargado"
        return not self.esta_descargado
