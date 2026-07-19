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


def main() -> None:
    agent = DesktopAgent()

    print("Desktop Agent")
    print()
    print(f"State : {agent.state_path}")
    print(f"Plan  : {agent.plan_path}")
    print(f"Queue : {agent.action_path}")
    print(f"Result: {agent.result_path}")
    print()
    print("The agent will not execute an unapproved plan.")


if __name__ == "__main__":
    main()
