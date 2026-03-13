from __future__ import annotations

import os
from dataclasses import dataclass, field

from module_agent.agents.examples import IntentAgent
from module_agent.agents.modules import SequenceExecutionAgent, TypeScriptServiceGeneratorAgent
from module_agent.core.orchestrator import AgentOrchestrator
from module_agent.core.sandbox import DirectorySandbox
from module_agent.io.voice import StubVoiceInput
from module_agent.llm.clients import LocalLLMClient


@dataclass(slots=True)
class SequenceConfig:
    name: str
    app_kind: str
    model_provider: str
    env_key: str


@dataclass(slots=True)
class ModuleSetupAssistant:
    """Setup mode: selection-driven sequence planner for modular app orchestration."""

    sandbox: DirectorySandbox
    llm: LocalLLMClient
    sequences: list[SequenceConfig] = field(default_factory=list)

    APP_OPTIONS: tuple[str, ...] = ("file-handling", "processing", "apis")
    MODEL_OPTIONS: tuple[str, ...] = ("local", "openai", "groq", "other")

    def interact(self, text: str) -> str:
        lowered = text.strip().lower()
        if lowered in {"help", "options"}:
            return self._selection_prompt()
        if lowered.startswith("select sequence"):
            return self._apply_selection(text)
        if lowered.startswith("set env "):
            assignment = text.replace("set env", "", 1).strip()
            key, value = assignment.split("=", 1)
            os.environ[key.strip()] = value.strip()
            return f"Environment variable stored: {key.strip()}"
        if lowered.startswith("link "):
            return "Data handoff preference stored. Run mode will pass sequence_output to next sequence."
        if lowered in {"status", "show"}:
            if not self.sequences:
                return self._selection_prompt()
            listed = ", ".join(sequence.name for sequence in self.sequences)
            return f"Configured sequences: {listed}"
        return self._selection_prompt()

    def _selection_prompt(self) -> str:
        return (
            "Select sequence config: select sequence <name> app <file-handling|processing|apis> "
            "model <local|openai|groq|other> env <ENV_KEY=VALUE>. "
            "Use 'set env ENV_KEY=VALUE' to update credentials. "
            "Only provide data-handoff details if sequence boundaries are unclear."
        )

    def _apply_selection(self, text: str) -> str:
        # select sequence ingest app file-handling model openai env OPENAI_API_KEY=sk-xxx
        tokens = text.split()
        try:
            name = tokens[2]
            app_kind = tokens[tokens.index("app") + 1].lower()
            model_provider = tokens[tokens.index("model") + 1].lower()
            env_assignment = tokens[tokens.index("env") + 1]
        except (ValueError, IndexError):
            return self._selection_prompt()

        if app_kind not in self.APP_OPTIONS:
            return f"Invalid app option. Choose one of: {', '.join(self.APP_OPTIONS)}"
        if model_provider not in self.MODEL_OPTIONS:
            return f"Invalid model option. Choose one of: {', '.join(self.MODEL_OPTIONS)}"

        env_key, env_value = env_assignment.split("=", 1)
        os.environ[env_key] = env_value

        self.sequences.append(
            SequenceConfig(
                name=name,
                app_kind=app_kind,
                model_provider=model_provider,
                env_key=env_key,
            )
        )
        return f"Sequence '{name}' selected with app={app_kind}, model={model_provider}."


def build_mvp(command_text: str = "analyze slides and summarize") -> AgentOrchestrator:
    sandbox = DirectorySandbox("./agent_workspaces")
    llm = LocalLLMClient(model_name="local-mvp-model")

    chain = [
        IntentAgent(name="intent-agent", sandbox=sandbox, llm=llm),
    ]
    voice = StubVoiceInput(command_text=command_text)
    return AgentOrchestrator(voice_provider=voice, chain=chain)


def build_setup_assistant() -> ModuleSetupAssistant:
    sandbox = DirectorySandbox("./agent_workspaces")
    llm = LocalLLMClient(model_name="local-mvp-model")
    return ModuleSetupAssistant(sandbox=sandbox, llm=llm)


def build_from_setup(
    sequences: list[SequenceConfig],
    command_text: str = "run configured modular app",
) -> AgentOrchestrator:
    """Run mode: execute configured sequences in order with output handoff."""

    sandbox = DirectorySandbox("./agent_workspaces")

    sequence_payload = [
        {
            "name": sequence.name,
            "app_kind": sequence.app_kind,
            "model_provider": sequence.model_provider,
            "env_key": sequence.env_key,
        }
        for sequence in sequences
    ]

    chain = [
        TypeScriptServiceGeneratorAgent(name="typescript-generator", sandbox=sandbox),
    ]
    for sequence in sequences:
        chain.append(
            SequenceExecutionAgent(
                name=f"{sequence.name}-runner",
                sandbox=sandbox,
                sequence_name=sequence.name,
                app_kind=sequence.app_kind,
            )
        )

    voice = StubVoiceInput(command_text=command_text)
    return AgentOrchestrator(
        voice_provider=voice,
        chain=chain,
        initial_payload={"sequences": sequence_payload},
    )


def main() -> None:
    assistant = build_setup_assistant()
    assistant.interact(
        "select sequence intake app file-handling model local env LOCAL_LLM_ENDPOINT=http://localhost:11434"
    )
    assistant.interact(
        "select sequence transform app processing model openai env OPENAI_API_KEY=demo-key"
    )
    assistant.interact("select sequence publish app apis model groq env GROQ_API_KEY=demo-key")

    orchestrator = build_from_setup(
        sequences=assistant.sequences,
        command_text="execute configured sequences",
    )
    result = orchestrator.run_once()

    print(result.payload)
    print([str(p) for p in result.artifacts])


if __name__ == "__main__":
    main()
