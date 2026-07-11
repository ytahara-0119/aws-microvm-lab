from pathlib import Path
import json
import subprocess
from typing import List, Optional


HOME = Path("/root")

CONFIG_DIR = HOME / ".config" / "code-server"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

WORKSPACE_DIR = HOME / "workspace"
ARTIFACT_DIR = HOME / "artifacts"

VSCODE_SETTINGS_DIR = HOME / ".local" / "share" / "code-server" / "User"
VSCODE_SETTINGS_FILE = VSCODE_SETTINGS_DIR / "settings.json"


def run(command: List[str], cwd: Optional[Path] = None) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.returncode != 0:
        print(
            "Command failed:",
            " ".join(command),
            f"(exit={result.returncode})",
        )


def write_code_server_config() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    CONFIG_FILE.write_text(
        "\n".join(
            [
                "bind-addr: 127.0.0.1:8081",
                "auth: password",
                "password: microvm",
                "cert: false",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_vscode_settings() -> None:
    VSCODE_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    settings = {
        "workbench.startupEditor": "none",
        "terminal.integrated.defaultProfile.linux": "bash",
        "editor.fontSize": 14,
        "files.autoSave": "afterDelay",
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
        },
        "python.analysis.typeCheckingMode": "basic",
    }

    VSCODE_SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def initialize_workspace() -> None:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    readme = WORKSPACE_DIR / "README.md"
    readme.write_text(
        "# Desktop Tools Workspace\n\n"
        "This workspace runs inside AWS Lambda MicroVM.\n\n"
        "## STEP11 Goal\n\n"
        "Create reusable desktop tools for observing and planning desktop actions.\n\n"
        "## Components\n\n"
        "- `desktop.observer`: capture desktop state and screenshots\n"
        "- `desktop.controller`: enqueue desktop actions\n"
        "- `desktop.planner`: convert an instruction into an action plan\n"
        "- `desktop.tools`: unified API for Claude Code and future agents\n\n"
        "## Quick Check\n\n"
        "```bash\n"
        "cd /root/workspace\n"
        "python3 -m desktop.observer\n"
        "python3 -m desktop.controller\n"
        "python3 -m desktop.tools\n"
        "```\n\n"
        "## Generated Artifacts\n\n"
        "```text\n"
        "/root/artifacts/desktop-state.json\n"
        "/root/artifacts/desktop.png\n"
        "/root/artifacts/desktop-actions.json\n"
        "/root/artifacts/desktop-plan.json\n"
        "```\n",
        encoding="utf-8",
    )

    claude_md = WORKSPACE_DIR / "CLAUDE.md"
    claude_md.write_text(
        "# Claude Instructions\n\n"
        "This project provides desktop observation and action-planning tools.\n\n"
        "## Rules\n\n"
        "- Inspect the current desktop state before proposing actions.\n"
        "- Use `desktop.tools.DesktopTools` as the public API.\n"
        "- Do not call X11 commands directly unless debugging.\n"
        "- Treat queued actions as plans only. They are not executed yet.\n"
        "- Keep changes small and explain important design decisions.\n"
        "- Preserve Python 3.9 compatibility.\n\n"
        "## Current Scope\n\n"
        "- Observation is implemented.\n"
        "- Action queue generation is implemented.\n"
        "- Real mouse and keyboard execution is not implemented yet.\n",
        encoding="utf-8",
    )

    gitignore = WORKSPACE_DIR / ".gitignore"
    gitignore.write_text(
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "node_modules/\n"
        ".DS_Store\n"
        "*.log\n",
        encoding="utf-8",
    )

    example = WORKSPACE_DIR / "example_desktop_tools.py"
    example.write_text(
        "import json\n\n"
        "from desktop import DesktopTools\n\n\n"
        "def main():\n"
        "    tools = DesktopTools()\n\n"
        "    state = tools.observe()\n"
        "    plan = tools.plan(\n"
        '        "Describe the current desktop and prepare the next action."\n'
        "    )\n\n"
        '    print("Desktop state:")\n'
        "    print(json.dumps(state, ensure_ascii=False, indent=2))\n\n"
        '    print("\\nDesktop plan:")\n'
        "    print(json.dumps(plan, ensure_ascii=False, indent=2))\n\n\n"
        'if __name__ == "__main__":\n'
        "    main()\n",
        encoding="utf-8",
    )


def configure_git() -> None:
    run(["git", "config", "--global", "init.defaultBranch", "main"])
    run(["git", "config", "--global", "user.name", "MicroVM"])
    run(["git", "config", "--global", "user.email", "microvm@example.com"])

    if not (WORKSPACE_DIR / ".git").exists():
        run(["git", "init"], cwd=WORKSPACE_DIR)


def main() -> None:
    write_code_server_config()
    write_vscode_settings()
    initialize_workspace()
    configure_git()

    print("Desktop Tools workspace initialized.")
    print(f"code-server config: {CONFIG_FILE}")
    print(f"workspace: {WORKSPACE_DIR}")
    print(f"artifacts: {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()