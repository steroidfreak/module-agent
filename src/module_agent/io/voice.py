from __future__ import annotations

from dataclasses import dataclass

from module_agent.core.contracts import VoiceInputProvider
from module_agent.core.models import VoiceCommand


@dataclass(slots=True)
class StubVoiceInput(VoiceInputProvider):
    """Simple provider useful for MVP demos and tests."""

    command_text: str
    confidence: float = 1.0

    def capture(self) -> VoiceCommand:
        return VoiceCommand(text=self.command_text, confidence=self.confidence)
