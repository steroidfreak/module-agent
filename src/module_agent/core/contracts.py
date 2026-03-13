from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from .models import AgentMessage, VoiceCommand


class VoiceInputProvider(ABC):
    """Converts microphone input into text commands."""

    @abstractmethod
    def capture(self) -> VoiceCommand:
        raise NotImplementedError


class LLMClient(ABC):
    """Abstraction over local LLM runtime or secure remote API."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class ModuleAgent(ABC):
    """Unit agent with dedicated workspace and processing logic."""

    name: str

    @abstractmethod
    def process(self, message: AgentMessage) -> AgentMessage:
        raise NotImplementedError


class FileSandbox(ABC):
    """Filesystem boundary for each agent."""

    @abstractmethod
    def root_for(self, agent_name: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def validate_paths(self, agent_name: str, paths: Iterable[Path]) -> None:
        raise NotImplementedError
