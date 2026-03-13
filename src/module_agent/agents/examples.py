from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from module_agent.agents.base import SandboxedAgent
from module_agent.core.contracts import LLMClient
from module_agent.core.models import AgentMessage


@dataclass(slots=True)
class IntentAgent(SandboxedAgent):
    """Interprets voice command into normalized intent."""

    llm: LLMClient

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        command = str(message.payload.get("command", ""))
        intent = self.llm.complete(f"Normalize intent: {command}")
        output = workspace / "intent.txt"
        output.write_text(intent)
        return AgentMessage(
            sender=self.name,
            payload={**message.payload, "intent": intent},
            artifacts=[*message.artifacts, output],
        )


@dataclass(slots=True)
class RoutingAgent(SandboxedAgent):
    """Decides next action and stores route plan."""

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        intent = str(message.payload.get("intent", ""))
        route = "slides-agent" if "slide" in intent.lower() else "text-agent"
        output = workspace / "route.txt"
        output.write_text(route)
        return AgentMessage(
            sender=self.name,
            payload={**message.payload, "route": route},
            artifacts=[*message.artifacts, output],
        )
