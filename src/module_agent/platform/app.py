from __future__ import annotations

from dataclasses import dataclass, field

from module_agent.agents.examples import IntentAgent, RoutingAgent
from module_agent.agents.modules import (
    DataProcessingModuleAgent,
    ExportModuleAgent,
    SandboxWindowAgent,
    UploadModuleAgent,
)
from module_agent.core.contracts import ModuleAgent
from module_agent.core.orchestrator import AgentOrchestrator
from module_agent.core.sandbox import DirectorySandbox
from module_agent.io.voice import StubVoiceInput
from module_agent.llm.clients import LocalLLMClient


@dataclass(slots=True)
class ModuleSetupAssistant:
    """Chat-like setup helper for composing a multi-module chain."""

    sandbox: DirectorySandbox
    llm: LocalLLMClient
    module_keys: list[str] = field(default_factory=list)

    SUPPORTED_MODULES: dict[str, str] = field(
        default_factory=lambda: {
            "upload": "Upload module (files/images intake)",
            "processing": "Data processing module",
            "export": "Output module (PDF/presentation)",
        }
    )

    def interact(self, text: str) -> str:
        lowered = text.strip().lower()
        if lowered in {"help", "list", "list modules"}:
            options = ", ".join(
                f"{key}: {desc}" for key, desc in self.SUPPORTED_MODULES.items()
            )
            return f"Available modules -> {options}. Say 'add <module>' to include one."
        if lowered.startswith("add "):
            key = lowered.replace("add", "", 1).strip()
            if key not in self.SUPPORTED_MODULES:
                return (
                    f"Unknown module '{key}'. Try one of: "
                    f"{', '.join(self.SUPPORTED_MODULES.keys())}."
                )
            if key not in self.module_keys:
                self.module_keys.append(key)
                return f"Added '{key}' module. Current chain: {', '.join(self.module_keys)}"
            return f"'{key}' already exists in chain: {', '.join(self.module_keys)}"
        if lowered in {"show chain", "show modules", "status"}:
            if not self.module_keys:
                return "No modules configured yet. Use 'add upload', 'add processing', 'add export'."
            return f"Configured modules: {', '.join(self.module_keys)}"
        if lowered in {"run", "run mode"}:
            return "Setup complete. Use build_from_setup(...) to execute in run mode."
        return (
            "I can help configure modules. Use: 'list modules', 'add <module>', "
            "'show chain', then 'run mode'."
        )


def build_mvp(command_text: str = "analyze slides and summarize") -> AgentOrchestrator:
    sandbox = DirectorySandbox("./agent_workspaces")
    llm = LocalLLMClient(model_name="local-mvp-model")

    chain = [
        IntentAgent(name="intent-agent", sandbox=sandbox, llm=llm),
        RoutingAgent(name="routing-agent", sandbox=sandbox),
    ]
    voice = StubVoiceInput(command_text=command_text)
    return AgentOrchestrator(voice_provider=voice, chain=chain)


def build_setup_assistant() -> ModuleSetupAssistant:
    sandbox = DirectorySandbox("./agent_workspaces")
    llm = LocalLLMClient(model_name="local-mvp-model")
    return ModuleSetupAssistant(sandbox=sandbox, llm=llm)


def build_from_setup(
    module_keys: list[str], command_text: str = "upload images, process data and export pdf"
) -> AgentOrchestrator:
    """Builds an orchestrator with any number of module agents in one app instance."""

    sandbox = DirectorySandbox("./agent_workspaces")
    llm = LocalLLMClient(model_name="local-mvp-model")

    registry: dict[str, ModuleAgent] = {
        "upload": UploadModuleAgent(name="upload-agent", sandbox=sandbox),
        "processing": DataProcessingModuleAgent(
            name="processing-agent", sandbox=sandbox
        ),
        "export": ExportModuleAgent(name="export-agent", sandbox=sandbox),
    }

    chain: list[ModuleAgent] = [
        IntentAgent(name="intent-agent", sandbox=sandbox, llm=llm),
    ]
    enabled_module_agent_names: list[str] = []
    for key in module_keys:
        agent = registry.get(key)
        if agent is not None:
            chain.append(agent)
            enabled_module_agent_names.append(agent.name)

    chain.append(
        SandboxWindowAgent(
            name="sandbox-window-agent",
            sandbox=sandbox,
            module_agent_names=enabled_module_agent_names,
        )
    )
    chain.append(RoutingAgent(name="routing-agent", sandbox=sandbox))

    voice = StubVoiceInput(command_text=command_text)
    return AgentOrchestrator(voice_provider=voice, chain=chain)


def main() -> None:
    assistant = build_setup_assistant()
    assistant.interact("add upload")
    assistant.interact("add processing")
    assistant.interact("add export")

    orchestrator = build_from_setup(
        module_keys=assistant.module_keys,
        command_text="upload images, analyze content, export presentation",
    )
    result = orchestrator.run_once()

    print(result.payload)
    print([str(p) for p in result.artifacts])


if __name__ == "__main__":
    main()
