from module_agent.platform.app import build_mvp


def test_chain_runs_and_produces_route() -> None:
    orchestrator = build_mvp("prepare slide deck summary")
    result = orchestrator.run_once()

    assert "intent" in result.payload
    assert result.payload["route"] in {"slides-agent", "text-agent"}
    assert len(result.artifacts) == 2
