"""
Path: tests/test_gateways.py
"""

from unittest.mock import MagicMock
from src.interface_adapter.gateways.agent_gateway import AgentGateway

def test_agent_gateway_init():
    "Test initialization of AgentGateway."
    gateway = AgentGateway(http_client=MagicMock())
    assert gateway is not None
