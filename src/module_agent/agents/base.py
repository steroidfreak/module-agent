from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from module_agent.core.contracts import FileSandbox, ModuleAgent
from module_agent.core.models import AgentMessage


@dataclass(slots=True)
class SandboxedAgent(ModuleAgent):
    """Base class for agents operating inside a dedicated directory."""

    name: str
    sandbox: FileSandbox

    def process(self, message: AgentMessage) -> AgentMessage:
        workspace = self.sandbox.root_for(self.name)
        self.sandbox.validate_paths(self.name, [workspace])
        return self.handle(message, workspace)

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        raise NotImplementedError
