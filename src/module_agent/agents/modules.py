from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from module_agent.agents.base import SandboxedAgent
from module_agent.core.models import AgentMessage


@dataclass(slots=True)
class UploadModuleAgent(SandboxedAgent):
    """Collects upload-related instructions (files/images) from command text."""

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        command = str(message.payload.get("command", ""))
        has_upload_intent = any(
            token in command.lower() for token in ("upload", "file", "image")
        )
        upload_summary = (
            "Detected upload intent for files/images."
            if has_upload_intent
            else "No explicit upload intent found; module ready for manual file selection."
        )
        output = workspace / "upload.txt"
        output.write_text(upload_summary)
        return AgentMessage(
            sender=self.name,
            payload={
                **message.payload,
                "upload": {
                    "enabled": True,
                    "summary": upload_summary,
                },
            },
            artifacts=[*message.artifacts, output],
        )


@dataclass(slots=True)
class DataProcessingModuleAgent(SandboxedAgent):
    """Builds a simple processing plan from current payload context."""

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        command = str(message.payload.get("command", ""))
        plan = (
            "Extract text, normalize metadata, and summarize content"
            if "summar" in command.lower() or "analy" in command.lower()
            else "Run standard cleanup and transformation pipeline"
        )
        output = workspace / "processing_plan.txt"
        output.write_text(plan)
        return AgentMessage(
            sender=self.name,
            payload={
                **message.payload,
                "processing": {
                    "enabled": True,
                    "plan": plan,
                },
            },
            artifacts=[*message.artifacts, output],
        )


@dataclass(slots=True)
class ExportModuleAgent(SandboxedAgent):
    """Chooses output channel (PDF/presentation) based on command text."""

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        command = str(message.payload.get("command", "")).lower()
        export_format = "presentation" if any(
            token in command for token in ("presentation", "slides", "ppt")
        ) else "pdf"
        output = workspace / "export.txt"
        output.write_text(export_format)
        return AgentMessage(
            sender=self.name,
            payload={
                **message.payload,
                "export": {
                    "enabled": True,
                    "format": export_format,
                },
            },
            artifacts=[*message.artifacts, output],
        )

