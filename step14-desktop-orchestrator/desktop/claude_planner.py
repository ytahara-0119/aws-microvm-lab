import json
import subprocess
from pathlib import Path
from typing import Any, Dict


DEFAULT_ARTIFACT_DIR = Path("/root/artifacts")
DEFAULT_PROMPT_PATH = Path("/root/workspace/prompts/agent-prompt.md")


class ClaudePlannerError(RuntimeError):
    pass


class ClaudePlanner:
    def __init__(
        self,
        prompt_path: Path = DEFAULT_PROMPT_PATH,
        artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    ) -> None:
        self.prompt_path = prompt_path
        self.artifact_dir = artifact_dir
        self.state_path = artifact_dir / "desktop-state.json"
        self.raw_response_path = artifact_dir / "claude-plan-response.txt"

    def build_prompt(self, instruction: str) -> str:
        if not self.prompt_path.exists():
            raise ClaudePlannerError(
                f"Prompt file does not exist: {self.prompt_path}"
            )

        if not self.state_path.exists():
            raise ClaudePlannerError(
                f"Desktop state does not exist: {self.state_path}"
            )

        system_prompt = self.prompt_path.read_text(encoding="utf-8")
        desktop_state = self.state_path.read_text(encoding="utf-8")

        return f"""
{system_prompt}

# Current user instruction

{instruction}

# Current desktop state

{desktop_state}
""".strip()

    def request_plan(self, instruction: str) -> Dict[str, Any]:
        prompt = self.build_prompt(instruction)

        command = [
            "claude",
            "-p",
            prompt,
            "--no-session-persistence",
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
        except FileNotFoundError as exc:
            raise ClaudePlannerError(
                "Claude Code command was not found."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ClaudePlannerError(
                "Claude Code planning timed out."
            ) from exc

        raw_response = completed.stdout.strip()

        self.raw_response_path.write_text(
            raw_response,
            encoding="utf-8",
        )

        if completed.returncode != 0:
            stderr = completed.stderr.strip()

            raise ClaudePlannerError(
                "Claude Code failed.\n"
                f"exit code: {completed.returncode}\n"
                f"stderr: {stderr}"
            )

        if not raw_response:
            raise ClaudePlannerError(
                "Claude Code returned an empty response."
            )

        cleaned_response = self._remove_markdown_fence(raw_response)

        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ClaudePlannerError(
                "Claude Code did not return valid JSON. "
                f"Raw response saved to: {self.raw_response_path}"
            ) from exc

        self._validate_response(result)

        return result

    @staticmethod
    def _remove_markdown_fence(response: str) -> str:
        text = response.strip()

        if text.startswith("```json"):
            text = text[len("```json"):]

        elif text.startswith("```"):
            text = text[len("```"):]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    @staticmethod
    def _validate_response(result: Any) -> None:
        if not isinstance(result, dict):
            raise ClaudePlannerError(
                "Claude response must be a JSON object."
            )

        actions = result.get("actions")

        if not isinstance(actions, list):
            raise ClaudePlannerError(
                "Claude response must contain an actions array."
            )

        for index, action in enumerate(actions):
            if not isinstance(action, dict):
                raise ClaudePlannerError(
                    f"Action {index} must be a JSON object."
                )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate desktop actions with Claude Code."
    )
    parser.add_argument(
        "instruction",
        help="Desktop task for Claude Code to plan.",
    )

    args = parser.parse_args()

    planner = ClaudePlanner()
    result = planner.request_plan(args.instruction)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
