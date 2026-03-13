from __future__ import annotations

from dataclasses import dataclass

from module_agent.core.contracts import LLMClient


@dataclass(slots=True)
class LocalLLMClient(LLMClient):
    """Placeholder adapter for local model runtimes (llama.cpp, Ollama, etc.)."""

    model_name: str

    def complete(self, prompt: str) -> str:
        return f"[{self.model_name}] local completion for: {prompt}"


@dataclass(slots=True)
class SecureAPIClient(LLMClient):
    """Placeholder adapter for secure remote inference gateways."""

    endpoint: str
    api_key_env: str = "LLM_API_KEY"

    def complete(self, prompt: str) -> str:
        return f"[{self.endpoint}] secure API completion for: {prompt}"
