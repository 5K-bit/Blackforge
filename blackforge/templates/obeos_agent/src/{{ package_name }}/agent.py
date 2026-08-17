from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentRequest:
    task: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentResult:
    ok: bool
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent:
    name = "{{ project_name }}"
    capabilities: tuple[str, ...] = ()

    async def handle(self, request: AgentRequest) -> AgentResult:
        """Handle one bounded OBEOS task. Replace this stub with agent logic."""
        if not request.task.strip():
            return AgentResult(ok=False, output="Task cannot be empty.")

        return AgentResult(
            ok=True,
            output=f"{self.name} received: {request.task}",
            metadata={"agent": self.name},
        )
