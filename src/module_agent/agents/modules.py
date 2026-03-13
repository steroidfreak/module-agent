from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from module_agent.agents.base import SandboxedAgent
from module_agent.core.models import AgentMessage


@dataclass(slots=True)
class TypeScriptServiceGeneratorAgent(SandboxedAgent):
    """Generates deployable TypeScript service scaffolds for configured sequences."""

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        sequences = message.payload.get("sequences", [])
        services: list[dict[str, str]] = []
        for index, sequence in enumerate(sequences, start=1):
            sequence_name = str(sequence["name"])
            app_kind = str(sequence["app_kind"])
            model_provider = str(sequence["model_provider"])
            service_dir = workspace / f"sequence_{index}_{sequence_name.replace(' ', '_')}"
            service_dir.mkdir(parents=True, exist_ok=True)

            package_json = """{
  \"name\": \"module-sequence-service\",
  \"version\": \"1.0.0\",
  \"private\": true,
  \"scripts\": {
    \"start\": \"ts-node src/service.ts\"
  },
  \"dependencies\": {
    \"dotenv\": \"^16.4.5\"
  },
  \"devDependencies\": {
    \"ts-node\": \"^10.9.2\",
    \"typescript\": \"^5.6.3\"
  }
}
"""
            service_ts = f"""import 'dotenv/config';

type SequencePayload = Record<string, unknown>;

const config = {{
  sequence: '{sequence_name}',
  appKind: '{app_kind}',
  modelProvider: '{model_provider}',
  modelEndpoint: process.env.{sequence['env_key']},
}};

export function runSequence(input: SequencePayload): SequencePayload {{
  return {{
    ...input,
    sequence: config.sequence,
    appKind: config.appKind,
    modelProvider: config.modelProvider,
    modelEndpointConfigured: Boolean(config.modelEndpoint),
  }};
}}

if (require.main === module) {{
  const result = runSequence({{ status: 'started' }});
  console.log(JSON.stringify(result, null, 2));
}}
"""
            dockerfile = """FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY src ./src
CMD ["npm", "run", "start"]
"""

            (service_dir / "package.json").write_text(package_json)
            src_dir = service_dir / "src"
            src_dir.mkdir(exist_ok=True)
            (src_dir / "service.ts").write_text(service_ts)
            (service_dir / "Dockerfile").write_text(dockerfile)

            services.append(
                {
                    "sequence": sequence_name,
                    "directory": str(service_dir),
                    "app_kind": app_kind,
                    "model_provider": model_provider,
                }
            )

        output = workspace / "typescript_services.txt"
        output.write_text("\n".join(service["directory"] for service in services))
        return AgentMessage(
            sender=self.name,
            payload={**message.payload, "services": services},
            artifacts=[*message.artifacts, output],
        )


@dataclass(slots=True)
class SequenceExecutionAgent(SandboxedAgent):
    """Executes a configured sequence in run mode and forwards output."""

    sequence_name: str
    app_kind: str

    def handle(self, message: AgentMessage, workspace: Path) -> AgentMessage:
        previous = message.payload.get("sequence_output", message.payload.get("command", ""))
        sequence_output = {
            "sequence": self.sequence_name,
            "app_kind": self.app_kind,
            "input": previous,
            "result": f"{self.sequence_name} completed",
        }
        output_file = workspace / f"{self.sequence_name.replace(' ', '_')}_run.json"
        output_file.write_text(str(sequence_output))
        return AgentMessage(
            sender=self.name,
            payload={**message.payload, "sequence_output": sequence_output},
            artifacts=[*message.artifacts, output_file],
        )
