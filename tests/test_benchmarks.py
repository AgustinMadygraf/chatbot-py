"""
tests/test_benchmarks.py
"""

import asyncio

import pytest

from src.interface_adapter.gateways.agent_gateway import AgentGateway


@pytest.mark.benchmark
def test_agent_gateway_local_response_benchmark(benchmark):
    "Benchmark for AgentGateway local response."
    gateway = AgentGateway(http_client=None)

    def run():
        return asyncio.run(gateway._local_response("conv1", "hola"))

    result = benchmark(run)
    assert "Hola" in result
