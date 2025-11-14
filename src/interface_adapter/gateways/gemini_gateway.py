"""
Path: src/interface_adapter/gateways/gemini_gateway.py
"""

from src.entities.gemini_responder import GeminiResponder
from src.entities.system_instructions import SystemInstructions


class GeminiGateway(GeminiResponder):
    "Puente entre el servicio Gemini y la interfaz del gateway."

    def __init__(self, service):
        "Inicializa el gateway con el servicio Gemini proporcionado."
        self.service = service

    def get_response(self, prompt, system_instructions: SystemInstructions = None):
        "Obtiene una respuesta del servicio Gemini utilizando el prompt y las instrucciones del sistema."
        if isinstance(system_instructions, SystemInstructions):
            # Usa 'content' o 'instructions' según el atributo real
            content = getattr(system_instructions, "content", None) or getattr(
                system_instructions, "instructions", None
            )
            if isinstance(content, list):
                instructions_content = ", ".join(map(str, content))
            else:
                instructions_content = str(content)
        else:
            instructions_content = system_instructions
        return self.service.get_response(prompt, instructions_content)
