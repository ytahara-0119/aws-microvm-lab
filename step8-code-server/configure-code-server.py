from pathlib import Path
import json


HOME = Path("/root")
CONFIG_DIR = HOME / ".config" / "code-server"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

WORKSPACE_DIR = HOME / "workspace"
VSCODE_SETTINGS_DIR = HOME / ".local" / "share" / "code-server" / "User"
VSCODE_SETTINGS_FILE = VSCODE_SETTINGS_DIR / "settings.json"


def main() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    VSCODE_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

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

    readme = WORKSPACE_DIR / "README.md"
    if not readme.exists():
        readme.write_text(
            "# MicroVM Workspace\n\n"
            "This workspace is running inside AWS Lambda MicroVM.\n\n",
            encoding="utf-8",
        )

    print("code-server configuration completed.")
    print(f"config: {CONFIG_FILE}")
    print(f"workspace: {WORKSPACE_DIR}")


if __name__ == "__main__":
    main()
