# Module Agent MVP

A modular scaffold for a **voice-controlled, chained multi-agent desktop platform** with per-agent sandboxed file access.

## Goals covered

- Voice-first command intake via pluggable input providers.
- Sequential/chain orchestration across multiple agents.
- Dedicated filesystem sandbox for each agent.
- Extensible adapters for **local LLM** or **secured API** inference.
- Clear module boundaries to support future platforms (desktop/web/edge).

## Proposed architecture

```text
module_agent/
  core/
    contracts.py      # protocol-style interfaces for agents, LLM, voice, sandbox
    models.py         # AgentMessage / VoiceCommand data contracts
    sandbox.py        # directory boundary enforcement
    orchestrator.py   # chain execution engine
  io/
    voice.py          # voice adapters (stub now, ASR integrations later)
  llm/
    clients.py        # LocalLLMClient + SecureAPIClient abstractions
  agents/
    base.py           # shared sandboxed agent behavior
    examples.py       # IntentAgent + RoutingAgent sample modules
  platform/
    app.py            # composition root / MVP bootstrap
```

## Security and sandbox model

- Each agent gets its own workspace under `agent_workspaces/<agent-name>/`.
- `DirectorySandbox.validate_paths(...)` rejects files outside agent scope.
- The pattern supports stronger isolation upgrades later (OS sandboxing, containers, ACLs).

## Extending with new agents

1. Create a class extending `SandboxedAgent`.
2. Implement `handle(message, workspace)`.
3. Register it in `platform/app.py` chain.
4. Keep payload keys namespaced or documented to avoid contract drift.

## Voice and inference extensibility

- Replace `StubVoiceInput` with microphone + ASR implementation (e.g., Vosk/Whisper).
- Use `LocalLLMClient` for fully local inference or `SecureAPIClient` for centrally managed, authenticated model access.
- Keep orchestration layer unchanged while swapping providers.


## Module agent layout (big sandbox window)

The runtime now models your requested layout explicitly:

- One **big sandbox window** (container)
- Multiple module agents inside it (e.g. `upload-agent`, `processing-agent`, `export-agent`)

```text
+------------------------------------------------------+
| BIG SANDBOX WINDOW                                   |
|  +---------------+   +---------------+               |
|  | module agent1 |   | module agent2 |               |
|  +---------------+   +---------------+               |
|         ...               +---------------+          |
|                           | module agentN |          |
|                           +---------------+          |
+------------------------------------------------------+
```

`build_from_setup(...)` adds a `SandboxWindowAgent` that stores this container + module list into the payload under `sandbox_window`.

## Run

```bash
python -m module_agent.platform.app
```

## Test

```bash
pytest
```
