"""
Entidad para instrucciones de sistema de modelos LLM.
"""


class SystemInstructions:
    """
    Representa instrucciones de sistema para un modelo de lenguaje.
    """

    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content
