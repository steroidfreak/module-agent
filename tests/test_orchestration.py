from module_agent.platform.app import build_from_setup, build_mvp, build_setup_assistant


def test_chain_runs_and_produces_route() -> None:
    orchestrator = build_mvp("prepare slide deck summary")
    result = orchestrator.run_once()

    assert "intent" in result.payload
    assert result.payload["route"] in {"slides-agent", "text-agent"}
    assert len(result.artifacts) == 2


def test_setup_assistant_builds_multi_module_chain() -> None:
    assistant = build_setup_assistant()

    assert "Added 'upload'" in assistant.interact("add upload")
    assert "Added 'processing'" in assistant.interact("add processing")
    assert "Added 'export'" in assistant.interact("add export")

    orchestrator = build_from_setup(
        assistant.module_keys,
        command_text="upload files and images, summarize and export pdf",
    )
    result = orchestrator.run_once()

    assert result.payload["upload"]["enabled"] is True
    assert result.payload["processing"]["enabled"] is True
    assert result.payload["export"]["format"] == "pdf"
    assert result.payload["sandbox_window"]["container"] == "big-sandbox-window"
    assert result.payload["sandbox_window"]["module_agents"] == [
        "upload-agent",
        "processing-agent",
        "export-agent",
    ]
    assert len(result.artifacts) == 6
