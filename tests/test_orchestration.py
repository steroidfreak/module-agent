import os

from module_agent.platform.app import build_from_setup, build_mvp, build_setup_assistant


def test_chain_runs_and_produces_intent() -> None:
    orchestrator = build_mvp("prepare slide deck summary")
    result = orchestrator.run_once()

    assert "intent" in result.payload
    assert len(result.artifacts) == 1


def test_setup_assistant_builds_sequence_chain() -> None:
    assistant = build_setup_assistant()

    assert "Sequence 'intake' selected" in assistant.interact(
        "select sequence intake app file-handling model local env LOCAL_LLM_ENDPOINT=http://localhost:11434"
    )
    assert "Sequence 'transform' selected" in assistant.interact(
        "select sequence transform app processing model openai env OPENAI_API_KEY=sk-test"
    )
    assert "Sequence 'publish' selected" in assistant.interact(
        "select sequence publish app apis model groq env GROQ_API_KEY=gsk-test"
    )

    orchestrator = build_from_setup(
        assistant.sequences,
        command_text="run configured modular app",
    )
    result = orchestrator.run_once()

    assert os.environ["OPENAI_API_KEY"] == "sk-test"
    assert len(result.payload["services"]) == 3
    assert result.payload["sequence_output"]["sequence"] == "publish"
    assert len(result.artifacts) == 4
