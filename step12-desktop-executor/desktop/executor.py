import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from Xlib import X, XK
from Xlib.display import Display
from Xlib.ext import xtest


ARTIFACT_DIR = Path(
    os.environ.get("ARTIFACT_DIR", "/root/artifacts")
)

ACTIONS_FILE = ARTIFACT_DIR / "desktop-actions.json"
EXECUTION_LOG_FILE = ARTIFACT_DIR / "desktop-execution.json"

DEFAULT_ACTION_DELAY = 0.3
DEFAULT_KEY_DELAY = 0.03


# Shift入力が必要な文字
SHIFTED_CHARACTERS = {
    "!": "1",
    '"': "'",
    "#": "3",
    "$": "4",
    "%": "5",
    "&": "7",
    "(": "9",
    ")": "0",
    "=": "-",
    "~": "`",
    "|": "\\",
    "{": "[",
    "}": "]",
    "+": "=",
    "*": "8",
    "_": "-",
    ":": ";",
    "<": ",",
    ">": ".",
    "?": "/",
}


# よく使う特殊キー
SPECIAL_KEYS = {
    "enter": "Return",
    "return": "Return",
    "tab": "Tab",
    "escape": "Escape",
    "esc": "Escape",
    "space": "space",
    "backspace": "BackSpace",
    "delete": "Delete",
    "insert": "Insert",
    "home": "Home",
    "end": "End",
    "pageup": "Prior",
    "pagedown": "Next",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
    "shift": "Shift_L",
    "ctrl": "Control_L",
    "control": "Control_L",
    "alt": "Alt_L",
    "super": "Super_L",
    "meta": "Meta_L",
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
}


class DesktopExecutor:
    def __init__(
        self,
        display_name: Optional[str] = None,
        action_delay: float = DEFAULT_ACTION_DELAY,
        key_delay: float = DEFAULT_KEY_DELAY,
    ) -> None:
        self.display_name = display_name or os.environ.get("DISPLAY", ":1")
        self.display = Display(self.display_name)
        self.action_delay = action_delay
        self.key_delay = key_delay

    def close(self) -> None:
        self.display.close()

    def sync(self) -> None:
        self.display.sync()

    def get_screen_size(self) -> Tuple[int, int]:
        screen = self.display.screen()
        return screen.width_in_pixels, screen.height_in_pixels

    def validate_coordinates(self, x: int, y: int) -> None:
        width, height = self.get_screen_size()

        if not 0 <= x < width:
            raise ValueError(
                "x coordinate is outside the screen: "
                f"x={x}, width={width}"
            )

        if not 0 <= y < height:
            raise ValueError(
                "y coordinate is outside the screen: "
                f"y={y}, height={height}"
            )

    def move_mouse(self, x: int, y: int) -> None:
        self.validate_coordinates(x, y)

        xtest.fake_input(
            self.display,
            X.MotionNotify,
            x=x,
            y=y,
        )

        self.sync()
        time.sleep(self.action_delay)

    def mouse_button(self, button: int, pressed: bool) -> None:
        if button not in (1, 2, 3, 4, 5):
            raise ValueError(
                f"Unsupported mouse button: {button}"
            )

        event_type = (
            X.ButtonPress if pressed else X.ButtonRelease
        )

        xtest.fake_input(
            self.display,
            event_type,
            detail=button,
        )

        self.sync()

    def click(
        self,
        x: int,
        y: int,
        button: int = 1,
        count: int = 1,
    ) -> None:
        self.move_mouse(x, y)

        for _ in range(count):
            self.mouse_button(button, True)
            time.sleep(0.05)
            self.mouse_button(button, False)
            time.sleep(0.1)

        time.sleep(self.action_delay)

    def double_click(
        self,
        x: int,
        y: int,
        button: int = 1,
    ) -> None:
        self.click(x, y, button=button, count=2)

    def scroll(self, amount: int) -> None:
        if amount == 0:
            return

        # X11ではホイール上がbutton 4、下がbutton 5
        button = 4 if amount > 0 else 5

        for _ in range(abs(amount)):
            self.mouse_button(button, True)
            self.mouse_button(button, False)
            time.sleep(0.05)

        time.sleep(self.action_delay)

    def resolve_keycode(self, key: str) -> int:
        normalized = key.strip()

        if not normalized:
            raise ValueError("Key must not be empty")

        keysym_name = SPECIAL_KEYS.get(
            normalized.lower(),
            normalized,
        )

        keysym = XK.string_to_keysym(keysym_name)

        if keysym == 0 and len(normalized) == 1:
            keysym = ord(normalized)

        if keysym == 0:
            raise ValueError(
                f"Unable to resolve keysym for key: {key}"
            )

        keycode = self.display.keysym_to_keycode(keysym)

        if keycode == 0:
            raise ValueError(
                f"Unable to resolve keycode for key: {key}"
            )

        return keycode

    def key_event(self, key: str, pressed: bool) -> None:
        keycode = self.resolve_keycode(key)

        event_type = (
            X.KeyPress if pressed else X.KeyRelease
        )

        xtest.fake_input(
            self.display,
            event_type,
            detail=keycode,
        )

        self.sync()

    def keypress(self, key: str) -> None:
        self.key_event(key, True)
        time.sleep(0.05)
        self.key_event(key, False)
        time.sleep(self.action_delay)

    def key_combination(self, keys: List[str]) -> None:
        if not keys:
            raise ValueError("keys must not be empty")

        for key in keys:
            self.key_event(key, True)
            time.sleep(0.03)

        for key in reversed(keys):
            self.key_event(key, False)
            time.sleep(0.03)

        time.sleep(self.action_delay)

    def type_character(self, character: str) -> None:
        if len(character) != 1:
            raise ValueError(
                "type_character accepts exactly one character"
            )

        if character == "\n":
            self.keypress("Enter")
            return

        if character == "\t":
            self.keypress("Tab")
            return

        if character == " ":
            self.keypress("space")
            return

        needs_shift = False
        base_character = character

        if character.isalpha() and character.isupper():
            needs_shift = True
            base_character = character.lower()
        elif character in SHIFTED_CHARACTERS:
            needs_shift = True
            base_character = SHIFTED_CHARACTERS[character]

        if needs_shift:
            self.key_event("Shift", True)

        try:
            self.key_event(base_character, True)
            time.sleep(self.key_delay)
            self.key_event(base_character, False)
        finally:
            if needs_shift:
                self.key_event("Shift", False)

        time.sleep(self.key_delay)

    def type_text(self, text: str) -> None:
        for character in text:
            self.type_character(character)

        time.sleep(self.action_delay)

    def execute_action(
        self,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        action_type = action.get("action")

        result = dict(action)
        result["status"] = "executing"

        try:
            if action_type == "move_mouse":
                self.move_mouse(
                    int(action["x"]),
                    int(action["y"]),
                )

            elif action_type == "click":
                self.click(
                    int(action["x"]),
                    int(action["y"]),
                    button=int(action.get("button", 1)),
                    count=int(action.get("count", 1)),
                )

            elif action_type == "double_click":
                self.double_click(
                    int(action["x"]),
                    int(action["y"]),
                    button=int(action.get("button", 1)),
                )

            elif action_type == "scroll":
                self.scroll(int(action["amount"]))

            elif action_type == "type_text":
                self.type_text(str(action["text"]))

            elif action_type == "keypress":
                self.keypress(str(action["key"]))

            elif action_type == "key_combination":
                keys = action.get("keys")

                if not isinstance(keys, list):
                    raise ValueError(
                        "key_combination requires a keys list"
                    )

                self.key_combination(
                    [str(key) for key in keys]
                )

            elif action_type == "wait":
                seconds = float(action.get("seconds", 1))
                time.sleep(seconds)

            elif action_type in ("observe", "note"):
                # Executorでは実行しない計画用アクション
                result["status"] = "skipped"
                result["note"] = (
                    "This action is informational and "
                    "was not executed."
                )
                return result

            else:
                raise ValueError(
                    f"Unsupported action: {action_type}"
                )

            result["status"] = "completed"

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

        return result

    def execute_queue(
        self,
        actions: List[Dict[str, Any]],
        stop_on_error: bool = True,
    ) -> List[Dict[str, Any]]:
        results = []

        for index, action in enumerate(actions):
            result = self.execute_action(action)
            result["index"] = index
            results.append(result)

            if (
                stop_on_error
                and result.get("status") == "failed"
            ):
                break

        return results


def load_actions(
    actions_file: Path = ACTIONS_FILE,
) -> List[Dict[str, Any]]:
    if not actions_file.exists():
        raise FileNotFoundError(
            f"Action queue not found: {actions_file}"
        )

    data = json.loads(
        actions_file.read_text(encoding="utf-8")
    )

    if not isinstance(data, list):
        raise ValueError(
            "Action queue must be a JSON array"
        )

    return data


def save_execution_results(
    results: List[Dict[str, Any]],
    output_file: Path = EXECUTION_LOG_FILE,
) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    output_file.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    print(f"DISPLAY: {os.environ.get('DISPLAY', '')}")
    print(f"Action queue: {ACTIONS_FILE}")

    actions = load_actions()
    executor = DesktopExecutor()

    try:
        results = executor.execute_queue(
            actions,
            stop_on_error=True,
        )
    finally:
        executor.close()

    save_execution_results(results)

    print(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        )
    )
    print(
        f"Saved execution results: "
        f"{EXECUTION_LOG_FILE}"
    )


if __name__ == "__main__":
    main()