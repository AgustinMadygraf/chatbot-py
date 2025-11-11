"""
Path: tests/test_use_cases.py
"""

from src.use_cases.generate_agent_response_use_case import GenerateAgentResponseUseCase


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
