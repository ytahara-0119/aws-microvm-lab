from typing import Any, Dict, List, Optional, Tuple


ALLOWED_ACTIONS = {
    "move_mouse",
    "click",
    "double_click",
    "scroll",
    "keypress",
    "key_combination",
    "type_text",
    "wait",
    "browser_search",
    "vision_read",
}


BLOCKED_KEY_COMBINATIONS = {
    ("alt", "f4"),
    ("ctrl", "alt", "delete"),
}


BLOCKED_TEXT_FRAGMENTS = [
    "rm -rf /",
    "shutdown",
    "reboot",
    "poweroff",
    "mkfs.",
]


def _blocked_fragment(text: str) -> Optional[str]:
    """Return the first blocked fragment found in text, if any."""
    lowered = text.lower()

    for fragment in BLOCKED_TEXT_FRAGMENTS:
        if fragment in lowered:
            return fragment

    return None


def validate_action(action: Dict[str, Any]) -> Tuple[bool, str]:
    action_name = action.get("action")

    if action_name not in ALLOWED_ACTIONS:
        return False, f"Unsupported action: {action_name}"

    if action_name == "type_text":
        text = action.get("text")

        if not isinstance(text, str):
            return False, "type_text requires text (string)"

        if not text:
            return False, "type_text text must not be empty"

        if len(text) > 1000:
            return False, "type_text text is too long (max 1000 characters)"

        blocked = _blocked_fragment(text)

        if blocked:
            return False, f"Blocked text fragment: {blocked}"

    if action_name == "key_combination":
        keys = tuple(str(key).lower() for key in action.get("keys", []))

        if keys in BLOCKED_KEY_COMBINATIONS:
            return False, f"Blocked key combination: {keys}"

    if action_name == "browser_search":
        query = action.get("query")

        if not isinstance(query, str):
            return False, "browser_search requires query (string)"

        if not query:
            return False, "browser_search query must not be empty"

        if len(query) > 300:
            return False, "browser_search query is too long (max 300 characters)"

        blocked = _blocked_fragment(query)

        if blocked:
            return False, f"Blocked text fragment: {blocked}"

    if action_name == "vision_read":
        instruction = action.get("instruction")

        if not isinstance(instruction, str):
            return False, "vision_read requires instruction (string)"

        if not instruction:
            return False, "vision_read instruction must not be empty"

        if len(instruction) > 500:
            return False, (
                "vision_read instruction is too long "
                "(max 500 characters)"
            )

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
