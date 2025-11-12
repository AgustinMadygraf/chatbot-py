"""
tests/test_benchmarks.py
"""

import pytest
from src.interface_adapter.gateways.agent_gateway import AgentGateway

@pytest.mark.benchmark
def test_agent_gateway_local_response_benchmark(benchmark):
    gateway = AgentGateway(http_client=None)
    result = benchmark(gateway._local_response, "conv1", "hola")
    assert "Hola" in result
