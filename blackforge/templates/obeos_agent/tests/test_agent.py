import asyncio

from {{ package_name }} import Agent, AgentRequest


def test_agent_handles_task() -> None:
    result = asyncio.run(Agent().handle(AgentRequest(task="status")))
    assert result.ok is True
    assert "status" in result.output


def test_agent_rejects_empty_task() -> None:
    result = asyncio.run(Agent().handle(AgentRequest(task="   ")))
    assert result.ok is False
