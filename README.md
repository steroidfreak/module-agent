# Module Agent

A modular app orchestrator + LLM deployment assistant.

## Behavior

### Setup mode
- Configure **sequences** one by one (file-handling, processing, APIs).
- For each sequence, select an LLM provider option:
  - local
  - OpenAI
  - Groq
  - other
- Store selected API key / endpoint in environment variables.
- Generate deployable TypeScript service scaffolds for each sequence:
  - `package.json`
  - `src/service.ts`
  - `Dockerfile`
- Ask for data handoff details **only** when sequence boundaries are unclear.

### Run mode
- No chat.
- Execute sequences in order.
- Pass output from one sequence into the next.

## Run

```bash
python -m module_agent.platform.app
```

## Test

```bash
pytest
```
