from pathlib import Path
import json
import subprocess
from typing import List, Optional


HOME = Path("/root")

CONFIG_DIR = HOME / ".config" / "code-server"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

WORKSPACE_DIR = HOME / "workspace"

VSCODE_SETTINGS_DIR = HOME / ".local" / "share" / "code-server" / "User"
VSCODE_SETTINGS_FILE = VSCODE_SETTINGS_DIR / "settings.json"


def run(command: List[str], cwd: Optional[Path] = None) -> None:
    subprocess.run(command, cwd=cwd, check=False)

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
    }

    VSCODE_SETTINGS_FILE.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def initialize_workspace() -> None:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    (WORKSPACE_DIR / "README.md").write_text(
        "# Claude Code Workspace\n\n"
        "This workspace is running inside AWS Lambda MicroVM.\n\n"
        "## Check\n\n"
        "```bash\n"
        "node --version\n"
        "npm --version\n"
        "claude --version\n"
        "git status\n"
        "```\n",
        encoding="utf-8",
    )

    (WORKSPACE_DIR / "CLAUDE.md").write_text(
        "# Claude Instructions\n\n"
        "- Keep code simple.\n"
        "- Prefer small, incremental changes.\n"
        "- Explain important changes clearly.\n"
        "- Use this workspace as a disposable MicroVM development environment.\n",
        encoding="utf-8",
    )

    (WORKSPACE_DIR / ".gitignore").write_text(
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "node_modules/\n"
        ".DS_Store\n",
        encoding="utf-8",
    )

    hello = WORKSPACE_DIR / "hello.py"
    if not hello.exists():
        hello.write_text(
            'print("Hello from AWS Lambda MicroVM + Claude Code")\n',
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

    print("Claude Code workspace initialized.")
    print(f"code-server config: {CONFIG_FILE}")
    print(f"workspace: {WORKSPACE_DIR}")


if __name__ == "__main__":
    main()
