import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .executor import DesktopExecutor
from .observer import observe
from .policy import validate_actions
from .claude_planner import ClaudePlanner


ARTIFACT_DIR = Path("/root/artifacts")

STATE_PATH = ARTIFACT_DIR / "desktop-state.json"
PLAN_PATH = ARTIFACT_DIR / "desktop-agent-plan.json"
ACTION_PATH = ARTIFACT_DIR / "desktop-actions.json"
RESULT_PATH = ARTIFACT_DIR / "desktop-agent-result.json"


class DesktopAgent:
    def __init__(self, artifact_dir: Optional[Path] = None) -> None:
        self.artifact_dir = artifact_dir or ARTIFACT_DIR
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

        self.state_path = self.artifact_dir / "desktop-state.json"
        self.plan_path = self.artifact_dir / "desktop-agent-plan.json"
        self.action_path = self.artifact_dir / "desktop-actions.json"
        self.result_path = self.artifact_dir / "desktop-agent-result.json"

    def observe(self) -> Dict[str, Any]:
        state = observe()

        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return state

    def create_plan(
        self,
        instruction: str,
        actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        valid, errors = validate_actions(actions)

        plan = {
            "instruction": instruction,
            "status": "awaiting_approval" if valid else "rejected",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "actions": actions,
            "policy": {
                "valid": valid,
                "errors": errors,
            },
        }

        self.plan_path.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return plan

    def approve(self) -> Dict[str, Any]:
        plan = json.loads(self.plan_path.read_text(encoding="utf-8"))

        if not plan.get("policy", {}).get("valid"):
            raise RuntimeError("The agent plan was rejected by policy.")

        actions = plan.get("actions", [])

        self.action_path.write_text(
            json.dumps(actions, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        plan["status"] = "approved"

        self.plan_path.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return plan

    def execute(self) -> List[Dict[str, Any]]:
        plan = json.loads(self.plan_path.read_text(encoding="utf-8"))

        if plan.get("status") != "approved":
            raise RuntimeError(
                "The agent plan is not approved. "
                "Run approve() before execute()."
            )

        actions = json.loads(self.action_path.read_text(encoding="utf-8"))

        valid, errors = validate_actions(actions)

        if not valid:
            raise RuntimeError(
                "Action validation failed: " + "; ".join(errors)
            )

        executor = DesktopExecutor()

        try:
            execution = executor.execute_queue(actions)
        finally:
            executor.close()

        return execution

    def run_approved_plan(self) -> Dict[str, Any]:
        before = self.observe()
        execution = self.execute()
        after = self.observe()

        result = {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "before": before,
            "execution": execution,
            "after": after,
        }

        self.result_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return result


    def create_plan_with_claude(
        self,
        instruction: str,
    ) -> Dict[str, Any]:
        self.observe()

        claude_planner = ClaudePlanner(
            artifact_dir=self.artifact_dir,
        )

        claude_result = claude_planner.request_plan(instruction)

        actions = claude_result.get("actions", [])

        plan = self.create_plan(
            instruction=instruction,
            actions=actions,
        )

        plan["planner"] = {
            "name": "claude-code",
            "reasoning_summary": claude_result.get(
                "reasoning_summary",
                "",
            ),
        }

        self.plan_path.write_text(
            json.dumps(
                plan,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return plan

def command_observe(agent: DesktopAgent) -> int:
    """Observe the current desktop and save its state."""
    state = agent.observe()

    state_path = agent.artifact_dir / "desktop-state.json"

    print("Desktop observation completed.")
    print()
    print(f"State      : {state_path}")

    screenshot_path = state.get("screenshot_path")
    if screenshot_path:
        print(f"Screenshot : {screenshot_path}")

    resolution = state.get("resolution", {})
    width = resolution.get("width")
    height = resolution.get("height")

    if width is not None and height is not None:
        print(f"Resolution : {width}x{height}")

    windows = state.get("windows", [])
    print(f"Windows    : {len(windows)}")

    return 0


def build_cli_parser():
    import argparse

    parser = argparse.ArgumentParser(
        prog="python3 -m desktop.agent",
        description="Desktop Agent command-line interface.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
    )

    subparsers.add_parser(
        "observe",
        help="Observe the current desktop.",
    )

    return parser

# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _artifact_path(agent: DesktopAgent, filename: str) -> Path:
    """Return a path inside the configured artifact directory."""
    return Path(agent.artifact_dir) / filename


def _read_json(path: Path) -> Dict[str, Any]:
    """Read a JSON object from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Artifact does not exist: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Artifact contains invalid JSON: {path}") from exc

    if not isinstance(value, dict):
        raise RuntimeError(f"Artifact must contain a JSON object: {path}")

    return value


def _format_action(action: Dict[str, Any]) -> str:
    """Convert an action object into a compact human-readable string."""
    action_name = str(action.get("action", "unknown"))

    if action_name in {"move_mouse", "click", "double_click"}:
        x = action.get("x", "?")
        y = action.get("y", "?")
        button = action.get("button")

        text = f"{action_name} ({x}, {y})"
        if button is not None:
            text += f" button={button}"
        return text

    if action_name == "wait":
        return f"wait {action.get('seconds', '?')} sec"

    if action_name == "scroll":
        return f"scroll amount={action.get('amount', '?')}"

    if action_name == "keypress":
        return f"keypress {action.get('key', '?')}"

    if action_name == "key_combination":
        keys = action.get("keys", [])
        if isinstance(keys, list):
            return "key_combination " + "+".join(str(key) for key in keys)
        return f"key_combination {keys}"

    if action_name == "type_text":
        text = str(action.get("text", ""))
        preview = text if len(text) <= 60 else text[:57] + "..."
        return f"type_text {preview!r}"

    return json.dumps(action, ensure_ascii=False)


def _print_plan(plan: Dict[str, Any]) -> None:
    """Print a desktop plan in a review-friendly form."""
    policy = plan.get("policy", {})
    planner = plan.get("planner", {})
    actions = plan.get("actions", [])

    if not isinstance(policy, dict):
        policy = {}

    if not isinstance(planner, dict):
        planner = {}

    if not isinstance(actions, list):
        actions = []

    print("Desktop Plan")
    print("=" * 60)
    print(f"Status      : {plan.get('status', 'unknown')}")
    print(f"Instruction : {plan.get('instruction', '')}")
    print(f"Planner     : {planner.get('name', 'unknown')}")
    print(f"Policy      : {'valid' if policy.get('valid') is True else 'invalid'}")
    print(f"Actions     : {len(actions)}")

    reasoning = planner.get("reasoning_summary")
    if reasoning:
        print(f"Summary     : {reasoning}")

    errors = policy.get("errors", [])
    if errors:
        print()
        print("Policy errors")
        print("-" * 60)

        if isinstance(errors, list):
            for error in errors:
                print(f"- {error}")
        else:
            print(f"- {errors}")

    print()
    print("Action list")
    print("-" * 60)

    if not actions:
        print("(no actions)")
        return

    for index, action in enumerate(actions, start=1):
        if isinstance(action, dict):
            print(f"{index:>2}. {_format_action(action)}")
        else:
            print(f"{index:>2}. {action!r}")


def command_observe(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Observe the current desktop."""
    state = agent.observe()

    state_path = _artifact_path(agent, "desktop-state.json")
    screenshot_path = _artifact_path(agent, "desktop.png")

    resolution = state.get("resolution", {})
    if not isinstance(resolution, dict):
        resolution = {}

    windows = state.get("windows", [])
    if not isinstance(windows, list):
        windows = []

    width = resolution.get("width")
    height = resolution.get("height")

    print("Desktop observation completed.")
    print()
    print(f"State      : {state_path}")

    if screenshot_path.exists():
        print(f"Screenshot : {screenshot_path}")

    if width is not None and height is not None:
        print(f"Resolution : {width}x{height}")

    print(f"Windows    : {len(windows)}")

    return 0


def command_plan(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Observe the desktop and create a plan using Claude Code."""
    plan = agent.create_plan_with_claude(args.instruction)

    print("Desktop plan created.")
    print()
    _print_plan(plan)

    if plan.get("policy", {}).get("valid") is not True:
        print()
        print("Plan was rejected by policy.")
        return 1

    print()
    print("Review the plan, then run:")
    print("  python3 -m desktop.agent approve")

    return 0


def command_show_plan(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Display the current plan."""
    plan_path = _artifact_path(agent, "desktop-agent-plan.json")
    plan = _read_json(plan_path)

    if args.json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        _print_plan(plan)

    return 0


def command_approve(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Approve the current plan."""
    plan_path = _artifact_path(agent, "desktop-agent-plan.json")
    plan_before = _read_json(plan_path)

    current_status = plan_before.get("status")

    if current_status == "approved":
        print("Plan is already approved.")
        print(f"Actions : {len(plan_before.get('actions', []))}")
        return 0

    if current_status != "awaiting_approval":
        print(
            "Cannot approve plan with status: "
            f"{current_status!r}",
            file=sys.stderr,
        )
        return 1

    policy = plan_before.get("policy", {})
    if not isinstance(policy, dict) or policy.get("valid") is not True:
        print(
            "Cannot approve a plan rejected by policy.",
            file=sys.stderr,
        )
        return 1

    plan = agent.approve()

    print("Desktop plan approved.")
    print()
    print(f"Status  : {plan.get('status', 'unknown')}")
    print(f"Actions : {len(plan.get('actions', []))}")
    print()
    print("Execute it with:")
    print("  python3 -m desktop.agent execute")

    return 0


def command_execute(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Execute the approved plan."""
    plan_path = _artifact_path(agent, "desktop-agent-plan.json")
    plan = _read_json(plan_path)

    status = plan.get("status")

    if status != "approved":
        print("Plan has not been approved.", file=sys.stderr)
        print(file=sys.stderr)
        print(
            f"Current status: {status!r}",
            file=sys.stderr,
        )
        print(file=sys.stderr)
        print("Run:", file=sys.stderr)
        print(
            "  python3 -m desktop.agent approve",
            file=sys.stderr,
        )
        return 1

    result = agent.run_approved_plan()

    execution = result.get("execution", [])
    if not isinstance(execution, list):
        execution = []

    completed = sum(
        1
        for item in execution
        if isinstance(item, dict)
        and item.get("status") == "completed"
    )

    failed = sum(
        1
        for item in execution
        if isinstance(item, dict)
        and item.get("status") != "completed"
    )

    print("Desktop plan execution finished.")
    print()
    print(f"Status    : {result.get('status', 'unknown')}")
    print(f"Completed : {completed}")
    print(f"Failed    : {failed}")
    print(
        "Result    : "
        f"{_artifact_path(agent, 'desktop-agent-result.json')}"
    )

    return 0 if result.get("status") == "completed" else 1


def command_status(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Display the current DesktopAgent workflow status."""
    artifact_dir = Path(agent.artifact_dir)

    state_path = artifact_dir / "desktop-state.json"
    plan_path = artifact_dir / "desktop-agent-plan.json"
    queue_path = artifact_dir / "desktop-actions.json"
    result_path = artifact_dir / "desktop-agent-result.json"
    response_path = artifact_dir / "claude-plan-response.txt"

    plan: Dict[str, Any] = {}
    result: Dict[str, Any] = {}

    if plan_path.exists():
        try:
            plan = _read_json(plan_path)
        except (RuntimeError, FileNotFoundError):
            plan = {}

    if result_path.exists():
        try:
            result = _read_json(result_path)
        except (RuntimeError, FileNotFoundError):
            result = {}

    policy = plan.get("policy", {})
    planner = plan.get("planner", {})
    actions = plan.get("actions", [])
    execution = result.get("execution", [])

    if not isinstance(policy, dict):
        policy = {}

    if not isinstance(planner, dict):
        planner = {}

    if not isinstance(actions, list):
        actions = []

    if not isinstance(execution, list):
        execution = []

    completed = sum(
        1
        for item in execution
        if isinstance(item, dict)
        and item.get("status") == "completed"
    )

    print("Desktop Agent Status")
    print("=" * 60)
    print(f"Artifact dir : {artifact_dir}")
    print(
        "Observation  : "
        f"{'available' if state_path.exists() else 'missing'}"
    )
    print(
        "Plan         : "
        f"{plan.get('status', 'missing') if plan else 'missing'}"
    )
    print(
        "Planner      : "
        f"{planner.get('name', 'unknown') if plan else 'unknown'}"
    )

    if plan:
        policy_status = (
            "valid"
            if policy.get("valid") is True
            else "invalid"
        )
    else:
        policy_status = "unknown"

    print(f"Policy       : {policy_status}")
    print(f"Actions      : {len(actions)}")
    print(
        "Action queue : "
        f"{'available' if queue_path.exists() else 'missing'}"
    )
    print(
        "Result       : "
        f"{result.get('status', 'missing') if result else 'missing'}"
    )
    print(f"Executed     : {completed}/{len(execution)}")
    print(
        "Claude raw   : "
        f"{'available' if response_path.exists() else 'missing'}"
    )

    return 0


def command_show_result(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Display the latest execution result."""
    result_path = _artifact_path(
        agent,
        "desktop-agent-result.json",
    )
    result = _read_json(result_path)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    execution = result.get("execution", [])
    if not isinstance(execution, list):
        execution = []

    before = result.get("before", {})
    after = result.get("after", {})

    if not isinstance(before, dict):
        before = {}

    if not isinstance(after, dict):
        after = {}

    before_windows = before.get("windows", [])
    after_windows = after.get("windows", [])

    if not isinstance(before_windows, list):
        before_windows = []

    if not isinstance(after_windows, list):
        after_windows = []

    print("Desktop Agent Result")
    print("=" * 60)
    print(f"Status         : {result.get('status', 'unknown')}")
    print(f"Actions        : {len(execution)}")
    print(f"Windows before : {len(before_windows)}")
    print(f"Windows after  : {len(after_windows)}")
    print()
    print("Execution")
    print("-" * 60)

    if not execution:
        print("(no execution records)")
        return 0

    for index, item in enumerate(execution, start=1):
        if not isinstance(item, dict):
            print(f"{index:>2}. {item!r}")
            continue

        action_text = _format_action(item)
        action_status = item.get("status", "unknown")

        print(
            f"{index:>2}. "
            f"[{action_status}] "
            f"{action_text}"
        )

    return 0


def command_clear(agent: DesktopAgent, args: argparse.Namespace) -> int:
    """Remove generated DesktopAgent artifacts."""
    filenames = [
        "desktop-state.json",
        "desktop.png",
        "desktop-agent-plan.json",
        "desktop-actions.json",
        "desktop-agent-result.json",
        "claude-plan-response.txt",
    ]

    removed: List[Path] = []

    for filename in filenames:
        path = _artifact_path(agent, filename)

        if path.exists():
            path.unlink()
            removed.append(path)

    if not removed:
        print("No DesktopAgent artifacts were found.")
        return 0

    print("Removed DesktopAgent artifacts.")
    print()

    for path in removed:
        print(f"- {path}")

    return 0


def build_cli_parser() -> argparse.ArgumentParser:
    """Build the DesktopAgent command-line parser."""
    parser = argparse.ArgumentParser(
        prog="python3 -m desktop.agent",
        description=(
            "Observe, plan, approve, and execute "
            "desktop automation tasks."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
    )

    subparsers.add_parser(
        "observe",
        help="Observe the current desktop.",
    )

    plan_parser = subparsers.add_parser(
        "plan",
        help="Create a Claude-generated desktop plan.",
    )
    plan_parser.add_argument(
        "instruction",
        help="Desktop task to plan.",
    )

    show_plan_parser = subparsers.add_parser(
        "show-plan",
        help="Show the current desktop plan.",
    )
    show_plan_parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON instead of the review view.",
    )

    subparsers.add_parser(
        "approve",
        help="Approve the current desktop plan.",
    )

    subparsers.add_parser(
        "execute",
        help="Execute the approved desktop plan.",
    )

    subparsers.add_parser(
        "status",
        help="Show DesktopAgent workflow status.",
    )

    show_result_parser = subparsers.add_parser(
        "show-result",
        help="Show the latest execution result.",
    )
    show_result_parser.add_argument(
        "--json",
        action="store_true",
        help="Print the complete result as JSON.",
    )

    subparsers.add_parser(
        "clear",
        help="Remove generated DesktopAgent artifacts.",
    )

    return parser


def main() -> int:
    """Run the DesktopAgent command-line interface."""
    parser = build_cli_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    agent = DesktopAgent()

    commands = {
        "observe": command_observe,
        "plan": command_plan,
        "show-plan": command_show_plan,
        "approve": command_approve,
        "execute": command_execute,
        "status": command_status,
        "show-result": command_show_result,
        "clear": command_clear,
    }

    command = commands.get(args.command)

    if command is None:
        parser.error(f"Unknown command: {args.command}")
        return 2

    try:
        return command(agent, args)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())