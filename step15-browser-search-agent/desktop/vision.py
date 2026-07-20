import json
import subprocess
from pathlib import Path
from typing import Any, Dict


DEFAULT_ARTIFACT_DIR = Path("/root/artifacts")
DEFAULT_PROMPT_PATH = Path("/root/workspace/prompts/vision-prompt.md")
DEFAULT_SCREENSHOT_PATH = DEFAULT_ARTIFACT_DIR / "desktop.png"


class VisionReaderError(RuntimeError):
    pass


class VisionReader:
    """Reads a desktop screenshot with Claude and returns a JSON result.

    Mirrors ClaudePlanner's subprocess-based approach (desktop/claude_planner.py),
    but instead of generating an action plan, it asks Claude to visually
    inspect a screenshot file and answer a specific question about it.
    """

    def __init__(
        self,
        prompt_path: Path = DEFAULT_PROMPT_PATH,
        artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    ) -> None:
        self.prompt_path = prompt_path
        self.artifact_dir = artifact_dir
        self.raw_response_path = artifact_dir / "claude-vision-response.txt"

    def build_prompt(
        self,
        instruction: str,
        screenshot_path: Path,
    ) -> str:
        if not self.prompt_path.exists():
            raise VisionReaderError(
                f"Prompt file does not exist: {self.prompt_path}"
            )

        if not screenshot_path.exists():
            raise VisionReaderError(
                f"Screenshot does not exist: {screenshot_path}"
            )

        system_prompt = self.prompt_path.read_text(encoding="utf-8")

        return f"""
{system_prompt}

# Instruction

{instruction}

# Screenshot

{screenshot_path}
""".strip()

    def read(
        self,
        instruction: str,
        screenshot_path: Path = DEFAULT_SCREENSHOT_PATH,
    ) -> Dict[str, Any]:
        prompt = self.build_prompt(instruction, screenshot_path)

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
            raise VisionReaderError(
                "Claude Code command was not found."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise VisionReaderError(
                "Claude Code vision read timed out."
            ) from exc

        raw_response = completed.stdout.strip()

        self.artifact_dir.mkdir(parents=True, exist_ok=True)

        self.raw_response_path.write_text(
            raw_response,
            encoding="utf-8",
        )

        if completed.returncode != 0:
            stderr = completed.stderr.strip()

            raise VisionReaderError(
                "Claude Code failed.\n"
                f"exit code: {completed.returncode}\n"
                f"stderr: {stderr}"
            )

        if not raw_response:
            raise VisionReaderError(
                "Claude Code returned an empty response."
            )

        cleaned_response = self._remove_markdown_fence(raw_response)

        try:
            result = json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise VisionReaderError(
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
            raise VisionReaderError(
                "Claude vision response must be a JSON object."
            )

        status = result.get("status")

        if status not in ("completed", "cannot_read"):
            raise VisionReaderError(
                "Claude vision response must contain a valid "
                "'status' field ('completed' or 'cannot_read')."
            )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Read the desktop screenshot with Claude vision."
    )
    parser.add_argument(
        "instruction",
        help="What to look for or read on screen.",
    )

    args = parser.parse_args()

    reader = VisionReader()
    result = reader.read(args.instruction)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
