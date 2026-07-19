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

    (WORKSPACE_DIR / "README.md").write_text(
        "# Desktop Executor Workspace\n\n"
        "This workspace runs inside AWS Lambda MicroVM.\n\n"
        "## STEP12 Goal\n\n"
        "Execute queued desktop actions using Python Xlib and XTest.\n\n"
        "## Components\n\n"
        "- `desktop.observer`: capture desktop state and screenshot\n"
        "- `desktop.controller`: create the action queue\n"
        "- `desktop.planner`: create an action plan\n"
        "- `desktop.executor`: execute mouse and keyboard actions\n"
        "- `desktop.tools`: unified public API\n\n"
        "## Safe First Test\n\n"
        "Start with mouse movement only.\n\n"
        "```bash\n"
        "cat > /root/artifacts/desktop-actions.json <<'EOF'\n"
        "[\n"
        "  {\n"
        '    "action": "move_mouse",\n'
        '    "x": 400,\n'
        '    "y": 300,\n'
        '    "status": "queued"\n'
        "  },\n"
        "  {\n"
        '    "action": "wait",\n'
        '    "seconds": 2,\n'
        '    "status": "queued"\n'
        "  }\n"
        "]\n"
        "EOF\n\n"
        "python3 -m desktop.executor\n"
        "cat /root/artifacts/desktop-execution.json\n"
        "```\n\n"
        "## Observe Before and After\n\n"
        "```bash\n"
        "python3 -m desktop.observer\n"
        "cat /root/artifacts/desktop-state.json\n"
        "identify /root/artifacts/desktop.png\n"
        "```\n\n"
        "## Generated Artifacts\n\n"
        "```text\n"
        "/root/artifacts/desktop-state.json\n"
        "/root/artifacts/desktop.png\n"
        "/root/artifacts/desktop-actions.json\n"
        "/root/artifacts/desktop-plan.json\n"
        "/root/artifacts/desktop-execution.json\n"
        "```\n",
        encoding="utf-8",
    )

    (WORKSPACE_DIR / "CLAUDE.md").write_text(
        "# Claude Instructions\n\n"
        "This project provides desktop observation, planning, queueing, "
        "and execution tools.\n\n"
        "## Rules\n\n"
        "- Always observe the desktop before proposing an action.\n"
        "- Use `desktop.tools.DesktopTools` as the primary public API.\n"
        "- Explain the queued actions before executing them.\n"
        "- Start with non-destructive actions such as mouse movement.\n"
        "- Do not execute clicks or keyboard input unless explicitly requested.\n"
        "- Re-observe the desktop after execution.\n"
        "- Treat coordinates as untrusted until checked against the screen size.\n"
        "- Preserve Python 3.9 compatibility.\n\n"
        "## Current Scope\n\n"
        "- Observation is implemented.\n"
        "- Action queue generation is implemented.\n"
        "- Mouse and keyboard execution use Python Xlib and XTest.\n"
        "- Autonomous planning is not implemented yet.\n",
        encoding="utf-8",
    )

    (WORKSPACE_DIR / ".gitignore").write_text(
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "node_modules/\n"
        ".DS_Store\n"
        "*.log\n",
        encoding="utf-8",
    )

    (WORKSPACE_DIR / "example_desktop_executor.py").write_text(
        "import json\n\n"
        "from desktop import DesktopTools\n\n\n"
        "def main():\n"
        "    tools = DesktopTools()\n\n"
        "    tools.clear_actions()\n"
        "    before = tools.observe()\n"
        "    tools.move_mouse(400, 300)\n\n"
        '    print("Before:")\n'
        "    print(json.dumps(before, ensure_ascii=False, indent=2))\n\n"
        '    print("\\nQueued actions:")\n'
        "    print(\n"
        "        json.dumps(\n"
        "            tools.get_actions(),\n"
        "            ensure_ascii=False,\n"
        "            indent=2,\n"
        "        )\n"
        "    )\n\n"
        "    results = tools.execute()\n\n"
        '    print("\\nExecution results:")\n'
        "    print(json.dumps(results, ensure_ascii=False, indent=2))\n\n"
        "    after = tools.observe()\n\n"
        '    print("\\nAfter:")\n'
        "    print(json.dumps(after, ensure_ascii=False, indent=2))\n\n\n"
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

    print("Desktop Executor workspace initialized.")
    print(f"code-server config: {CONFIG_FILE}")
    print(f"workspace: {WORKSPACE_DIR}")
    print(f"artifacts: {ARTIFACT_DIR}")


if __name__ == "__main__":
    main()