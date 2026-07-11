import json
from typing import Any, Dict, List

from .controller import click, focus_window, keypress, move_mouse, type_text
from .observer import observe
from .planner import DesktopPlanner


class DesktopTools:
    def __init__(self) -> None:
        self.planner = DesktopPlanner()

    def observe(self) -> Dict[str, Any]:
        return observe()

    def move_mouse(self, x: int, y: int) -> Dict[str, Any]:
        return move_mouse(x, y)

    def click(self, x: int, y: int, button: int = 1) -> Dict[str, Any]:
        return click(x, y, button)

    def type_text(self, text: str) -> Dict[str, Any]:
        return type_text(text)

    def keypress(self, key: str) -> Dict[str, Any]:
        return keypress(key)

    def focus_window(self, window_id: str) -> Dict[str, Any]:
        return focus_window(window_id)

    def plan(self, instruction: str) -> List[Dict[str, Any]]:
        actions = self.planner.plan(instruction)
        self.planner.save(actions)
        return actions


def main() -> None:
    tools = DesktopTools()

    state = tools.observe()
    plan = tools.plan("Describe the current desktop and prepare the next action.")

    print("Desktop state:")
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print("\nDesktop plan:")
    print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
