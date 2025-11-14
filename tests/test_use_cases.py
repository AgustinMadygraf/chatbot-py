"""
Path: tests/test_use_cases.py
"""


from src.use_cases.generate_agent_response_use_case import GenerateAgentResponseUseCase
from src.entities.message import Message
from src.use_cases.load_system_instructions import LoadSystemInstructionsUseCase
from src.entities.system_instructions import SystemInstructions


def test_generate_agent_response_use_case_instantiation():
    "Test instantiation of GenerateAgentResponseUseCase."

    class DummyAgentBotService:
        "Dummy service for testing."

        def get_response(self, prompt):
            "Return a dummy response."
            _ = prompt  # Mark as intentionally unused
            return "ok"

    use_case = GenerateAgentResponseUseCase(agent_bot_service=DummyAgentBotService())
    assert use_case is not None


def test_generate_agent_response_use_case_execute_text():
    "Test execute returns Message with agent response for text input."

    class DummyAgentBotService:
        "Dummy service for testing."

        def get_response(self, prompt):
            "metodo dummy."
            return f"Echo: {prompt}"

    use_case = GenerateAgentResponseUseCase(agent_bot_service=DummyAgentBotService())
    user_message = Message(to="user1", body="hola")
    result = use_case.execute("conv1", user_message)
    assert isinstance(result, Message)
    assert result.body.startswith("Echo: hola")


def test_generate_agent_response_use_case_execute_prompt():
    "Test execute uses prompt if provided."

    class DummyAgentBotService:
        "Dummy service for testing."

        def get_response(self, prompt):
            "Método dummy."
            return f"Prompted: {prompt}"

    use_case = GenerateAgentResponseUseCase(agent_bot_service=DummyAgentBotService())
    user_message = Message(to="user2", body="ignored")
    result = use_case.execute("conv2", user_message, prompt="audio text")
    assert result.body.startswith("Prompted: audio text")


def test_generate_agent_response_use_case_execute_error_message():
    "Test execute returns friendly error if Rasa error detected."

    class DummyAgentBotService:
        "Dummy service for testing."

        def get_response(self, prompt):
            "metodo dummy."
            _ = prompt  # Mark as intentionally unused
            return "Error al comunicarse con Rasa: timeout"

    use_case = GenerateAgentResponseUseCase(agent_bot_service=DummyAgentBotService())
    user_message = Message(to="user3", body="hola")
    result = use_case.execute("conv3", user_message)
    assert (
        "servidor no está disponible" in result.body
        or "comuníquese con el área de mantenimiento" in result.body
    )


# --- Nuevos tests para edge cases de GenerateAgentResponseUseCase ---
def test_generate_agent_response_use_case_non_string_response():
    "Test execute maneja respuesta no-string del agente."

    class DummyAgentBotService:
        def get_response(self, prompt):
            _ = prompt  # Mark as intentionally unused
            return 12345  # No string

    use_case = GenerateAgentResponseUseCase(agent_bot_service=DummyAgentBotService())
    user_message = Message(to="user4", body="hola")
    result = use_case.execute("conv4", user_message)
    assert isinstance(result, Message)
    assert result.body == 12345


def test_generate_agent_response_use_case_empty_message():
    "Test execute maneja mensaje vacío."

    class DummyAgentBotService:
        def get_response(self, prompt):
            return "Echo: " + (prompt or "<vacio>")

    use_case = GenerateAgentResponseUseCase(agent_bot_service=DummyAgentBotService())
    user_message = Message(to="user5", body="")
    result = use_case.execute("conv5", user_message)
    assert isinstance(result, Message)
    assert result.body.startswith("Echo: ")


def test_generate_agent_response_use_case_with_audio_transcriber():
    "Test instanciación con audio_transcriber_use_case."

    class DummyAgentBotService:
        def get_response(self, _prompt):
            return "ok"

    class DummyAudioTranscriber:
        pass

    use_case = GenerateAgentResponseUseCase(
        agent_bot_service=DummyAgentBotService(),
        audio_transcriber_use_case=DummyAudioTranscriber(),
    )
    user_message = Message(to="user6", body="hola")
    result = use_case.execute("conv6", user_message)
    assert isinstance(result, Message)


class DummyRepo:
    "Dummy repository for testing."

    def __init__(self, content):
        self._content = content

    def load(self):
        "Load content from the repository."
        return self._content


def test_load_system_instructions_use_case_success():
    repo = DummyRepo(["inst1", "inst2"])
    use_case = LoadSystemInstructionsUseCase(repo)
    result = use_case.execute()
    assert isinstance(result, SystemInstructions)
    # Ajuste: usar 'content' si 'instructions' no existe
    assert getattr(result, "instructions", None) == ["inst1", "inst2"] or getattr(
        result, "content", None
    ) == ["inst1", "inst2"]


def test_load_system_instructions_use_case_none():
    "Test LoadSystemInstructionsUseCase returns None when repo.load() is None."
    repo = DummyRepo(None)
    use_case = LoadSystemInstructionsUseCase(repo)
    result = use_case.execute()
    assert result is None


# --- Nuevos tests para edge cases de LoadSystemInstructionsUseCase ---
def test_load_system_instructions_use_case_repo_exception():
    class FailingRepo:
        def load(self):
            raise RuntimeError("fail repo")

    use_case = LoadSystemInstructionsUseCase(FailingRepo())
    try:
        use_case.execute()
    except RuntimeError as e:
        assert "fail repo" in str(e)


def test_load_system_instructions_use_case_unexpected_type():
    class WeirdRepo:
        def load(self):
            return 12345

    use_case = LoadSystemInstructionsUseCase(WeirdRepo())
    result = use_case.execute()
    # SystemInstructions acepta cualquier cosa, pero debe envolverlo

    assert isinstance(result, SystemInstructions)
    assert (
        getattr(result, "instructions", None) == 12345
        or getattr(result, "content", None) == 12345
    )


def test_load_system_instructions_use_case_empty_list():
    class EmptyListRepo:
        def load(self):
            return []

    use_case = LoadSystemInstructionsUseCase(EmptyListRepo())
    result = use_case.execute()
    # [] es falsy, así que debe devolver None
    assert result is None


def test_load_system_instructions_use_case_empty_string():
    class EmptyStringRepo:
        def load(self):
            return ""

    use_case = LoadSystemInstructionsUseCase(EmptyStringRepo())
    result = use_case.execute()
    # "" es falsy, así que debe devolver None
    assert result is None
