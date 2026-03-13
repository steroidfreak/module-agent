from __future__ import annotations

from module_agent.agents.examples import IntentAgent, RoutingAgent
from module_agent.core.orchestrator import AgentOrchestrator
from module_agent.core.sandbox import DirectorySandbox
from module_agent.io.voice import StubVoiceInput
from module_agent.llm.clients import LocalLLMClient


def build_mvp(command_text: str = "analyze slides and summarize") -> AgentOrchestrator:
    sandbox = DirectorySandbox("./agent_workspaces")
    llm = LocalLLMClient(model_name="local-mvp-model")

    chain = [
        IntentAgent(name="intent-agent", sandbox=sandbox, llm=llm),
        RoutingAgent(name="routing-agent", sandbox=sandbox),
    ]
    voice = StubVoiceInput(command_text=command_text)
    return AgentOrchestrator(voice_provider=voice, chain=chain)


def main() -> None:
    orchestrator = build_mvp()
    result = orchestrator.run_once()
    print(result.payload)
    print([str(p) for p in result.artifacts])


if __name__ == "__main__":
    main()
