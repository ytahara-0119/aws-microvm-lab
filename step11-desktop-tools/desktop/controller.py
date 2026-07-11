import json
from pathlib import Path
from typing import Any, Dict, List


ARTIFACT_DIR = Path("/root/artifacts")
ACTIONS_FILE = ARTIFACT_DIR / "desktop-actions.json"


def load_actions() -> List[Dict[str, Any]]:
    if not ACTIONS_FILE.exists():
        return []

    try:
        return json.loads(ACTIONS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_actions(actions: List[Dict[str, Any]]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    ACTIONS_FILE.write_text(
        json.dumps(actions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def enqueue_action(action: Dict[str, Any]) -> Dict[str, Any]:
    actions = load_actions()
    actions.append(action)
    save_actions(actions)
    return action


def clear_actions() -> None:
    save_actions([])


def move_mouse(x: int, y: int) -> Dict[str, Any]:
    return enqueue_action(
        {
            "action": "move_mouse",
            "x": x,
            "y": y,
            "status": "queued",
        }
    )


def click(x: int, y: int, button: int = 1) -> Dict[str, Any]:
    return enqueue_action(
        {
            "action": "click",
            "x": x,
            "y": y,
            "button": button,
            "status": "queued",
        }
    )


def type_text(text: str) -> Dict[str, Any]:
    return enqueue_action(
        {
            "action": "type_text",
            "text": text,
            "status": "queued",
        }
    )


def keypress(key: str) -> Dict[str, Any]:
    return enqueue_action(
        {
            "action": "keypress",
            "key": key,
            "status": "queued",
        }
    )


def focus_window(window_id: str) -> Dict[str, Any]:
    return enqueue_action(
        {
            "action": "focus_window",
            "window_id": window_id,
            "status": "queued",
        }
    )


def get_actions() -> List[Dict[str, Any]]:
    return load_actions()


def main() -> None:
    clear_actions()

    move_mouse(100, 100)
    click(100, 100)
    type_text("Hello from Desktop Tools")
    keypress("Enter")

    print(
        json.dumps(
            get_actions(),
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"Saved action queue: {ACTIONS_FILE}")


if __name__ == "__main__":
    main()
