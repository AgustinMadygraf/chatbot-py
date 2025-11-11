"""
Path: src/use_cases/load_system_instructions.py
"""

from src.entities.system_instructions import SystemInstructions


class LoadSystemInstructionsUseCase:
    "Orquesta la carga de instrucciones de sistema desde un repositorio/gateway."

    def __init__(self, instructions_repository):
        self.instructions_repository = instructions_repository

    def execute(self):
        "Carga las instrucciones de sistema y las devuelve como una entidad SystemInstructions."
        content = self.instructions_repository.load()
        return SystemInstructions(content) if content else None
