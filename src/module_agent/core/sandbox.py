from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .contracts import FileSandbox


class DirectorySandbox(FileSandbox):
    """Restricts agent artifacts to an isolated per-agent directory."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def root_for(self, agent_name: str) -> Path:
        root = (self.base_dir / agent_name).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root

    def validate_paths(self, agent_name: str, paths: Iterable[Path]) -> None:
        root = self.root_for(agent_name)
        for path in paths:
            resolved = path.resolve()
            if root != resolved and root not in resolved.parents:
                raise PermissionError(
                    f"Path {resolved} escapes sandbox for agent '{agent_name}'."
                )
