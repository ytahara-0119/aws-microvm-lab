import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .controller import (
    clear_actions,
    click,
    focus_window,
    get_actions,
    keypress,
    move_mouse,
    type_text,
)
from .executor import (
    ACTIONS_FILE,
    EXECUTION_LOG_FILE,
    DesktopExecutor,
    load_actions,
    save_execution_results,
)
from .observer import observe
from .planner import DesktopPlanner


class DesktopTools:
    def __init__(self) -> None:
        self.planner = DesktopPlanner()

    def observe(self) -> Dict[str, Any]:
        return observe()

    def clear_actions(self) -> None:
        clear_actions()

    def get_actions(self) -> List[Dict[str, Any]]:
        return get_actions()

    def move_mouse(self, x: int, y: int) -> Dict[str, Any]:
        return move_mouse(x, y)

    def click(
        self,
        x: int,
        y: int,
        button: int = 1,
    ) -> Dict[str, Any]:
        return click(x, y, button)

    def type_text(self, text: str) -> Dict[str, Any]:
        return type_text(text)

    def keypress(self, key: str) -> Dict[str, Any]:
        return keypress(key)

    def focus_window(
        self,
        window_id: str,
    ) -> Dict[str, Any]:
        return focus_window(window_id)

    def plan(
        self,
        instruction: str,
    ) -> List[Dict[str, Any]]:
        actions = self.planner.plan(instruction)
        self.planner.save(actions)
        return actions

    def execute(
        self,
        actions: Optional[List[Dict[str, Any]]] = None,
        stop_on_error: bool = True,
    ) -> List[Dict[str, Any]]:
        queue = actions if actions is not None else load_actions()

        executor = DesktopExecutor()

        try:
            results = executor.execute_queue(
                queue,
                stop_on_error=stop_on_error,
            )
        finally:
            executor.close()

        save_execution_results(results)

        return results

    def execute_file(
        self,
        actions_file: Path = ACTIONS_FILE,
        stop_on_error: bool = True,
    ) -> List[Dict[str, Any]]:
        actions = load_actions(actions_file)

        return self.execute(
            actions=actions,
            stop_on_error=stop_on_error,
        )

    def observe_execute_observe(
        self,
        actions: Optional[List[Dict[str, Any]]] = None,
        stop_on_error: bool = True,
    ) -> Dict[str, Any]:
        before = self.observe()

        execution = self.execute(
            actions=actions,
            stop_on_error=stop_on_error,
        )

        after = self.observe()

        return {
            "before": before,
            "execution": execution,
            "after": after,
        }


def main() -> None:
    tools = DesktopTools()

    state = tools.observe()
    plan = tools.plan(
        "Describe the current desktop and prepare the next action."
    )
    actions = tools.get_actions()

    print("Desktop state:")
    print(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\nDesktop plan:")
    print(
        json.dumps(
            plan,
            ensure_ascii=False,
            indent=2,
        )
    )

    print("\nQueued actions:")
    print(
        json.dumps(
            actions,
            ensure_ascii=False,
            indent=2,
        )
    )

    print(f"\nAction queue: {ACTIONS_FILE}")
    print(f"Execution log: {EXECUTION_LOG_FILE}")
    print(
        "Run `tools.execute()` or "
        "`python3 -m desktop.executor` "
        "to execute the queued actions."
    )


if __name__ == "__main__":
    main()