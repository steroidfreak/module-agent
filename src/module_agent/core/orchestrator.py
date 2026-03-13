from __future__ import annotations

from dataclasses import dataclass

from .contracts import ModuleAgent, VoiceInputProvider
from .models import AgentMessage


@dataclass(slots=True)
class AgentOrchestrator:
    """Coordinates voice command intake and sequential agent processing."""

    voice_provider: VoiceInputProvider
    chain: list[ModuleAgent]

    def run_once(self) -> AgentMessage:
        command = self.voice_provider.capture()
        message = AgentMessage(
            sender="voice",
            payload={
                "command": command.text,
                "confidence": command.confidence,
            },
        )
        for agent in self.chain:
            message = agent.process(message)
        return message
