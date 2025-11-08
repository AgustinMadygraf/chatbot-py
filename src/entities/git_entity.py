"""
Path: src/entities/git_entity.py
"""

class GitEntity:
    "Entidad que representa el estado de Git"
    def __init__(self, esta_instalado: bool = False):
        self.esta_instalado = esta_instalado

    def puede_clonar(self) -> bool:
        "Verifica si Git está instalado para poder clonar repositorios"
        return self.esta_instalado
