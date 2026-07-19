from typing import Any, Dict, List, Tuple


ALLOWED_ACTIONS = {
    "move_mouse",
    "click",
    "double_click",
    "scroll",
    "keypress",
    "key_combination",
    "type_text",
    "wait",
}


BLOCKED_KEY_COMBINATIONS = {
    ("alt", "f4"),
    ("ctrl", "alt", "delete"),
}


def validate_action(action: Dict[str, Any]) -> Tuple[bool, str]:
    action_name = action.get("action")

    if action_name not in ALLOWED_ACTIONS:
        return False, f"Unsupported action: {action_name}"

    if action_name == "type_text":
        text = str(action.get("text", ""))

        blocked_fragments = [
            "rm -rf /",
            "shutdown",
            "reboot",
            "poweroff",
            "mkfs.",
        ]

        lowered = text.lower()

        for fragment in blocked_fragments:
            if fragment in lowered:
                return False, f"Blocked text fragment: {fragment}"

    if action_name == "key_combination":
        keys = tuple(str(key).lower() for key in action.get("keys", []))

        if keys in BLOCKED_KEY_COMBINATIONS:
            return False, f"Blocked key combination: {keys}"

    return True, "allowed"


def validate_actions(
    actions: List[Dict[str, Any]],
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    for index, action in enumerate(actions):
        allowed, reason = validate_action(action)

        if not allowed:
            errors.append(f"Action {index}: {reason}")

    return len(errors) == 0, errors
