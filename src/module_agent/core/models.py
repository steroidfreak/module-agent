from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AgentMessage:
    """Data passed between agents in a chain."""

    sender: str
    payload: dict[str, Any]
    artifacts: list[Path] = field(default_factory=list)


@dataclass(slots=True)
class VoiceCommand:
    """Parsed voice command + metadata."""

    text: str
    confidence: float
    raw: dict[str, Any] = field(default_factory=dict)
