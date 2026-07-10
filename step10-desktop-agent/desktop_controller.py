import json
import subprocess
from pathlib import Path


ARTIFACT_DIR = Path("/root/artifacts")
ACTIONS_LOG = ARTIFACT_DIR / "desktop-actions.log"


def run(command):
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "output": result.stdout,
    }


def log_action(action):
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    with ACTIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(action, ensure_ascii=False) + "\n")


def move_mouse(x, y):
    action = {
        "type": "move_mouse",
        "x": x,
        "y": y,
        "status": "not_implemented",
        "note": "xdotool is not available on AL2023 default repositories.",
    }
    log_action(action)
    return action


def click(x, y, button=1):
    action = {
        "type": "click",
        "x": x,
        "y": y,
        "button": button,
        "status": "not_implemented",
        "note": "Click action will be implemented after selecting an input automation backend.",
    }
    log_action(action)
    return action


def type_text(text):
    action = {
        "type": "type_text",
        "text": text,
        "status": "not_implemented",
        "note": "Keyboard input will be implemented after selecting an input automation backend.",
    }
    log_action(action)
    return action


def keypress(key):
    action = {
        "type": "keypress",
        "key": key,
        "status": "not_implemented",
        "note": "Keypress action will be implemented after selecting an input automation backend.",
    }
    log_action(action)
    return action


def focus_window(window_id):
    action = {
        "type": "focus_window",
        "window_id": window_id,
        "status": "not_implemented",
        "note": "Window focus will be implemented after selecting a window control backend.",
    }
    log_action(action)
    return action


def main():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    demo_actions = [
        move_mouse(100, 100),
        click(100, 100),
        type_text("Hello from Desktop Controller"),
        keypress("Enter"),
    ]

    print(json.dumps(demo_actions, ensure_ascii=False, indent=2))
    print(f"Saved action log: {ACTIONS_LOG}")


if __name__ == "__main__":
    main()
