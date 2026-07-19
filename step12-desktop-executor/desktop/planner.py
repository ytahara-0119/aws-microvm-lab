import json
from pathlib import Path
from typing import Any, Dict, List


ARTIFACT_DIR = Path("/root/artifacts")
PLAN_FILE = ARTIFACT_DIR / "desktop-plan.json"


class DesktopPlanner:
    def plan(self, instruction: str) -> List[Dict[str, Any]]:
        instruction = instruction.strip()

        actions: List[Dict[str, Any]] = [
            {
                "action": "observe",
            },
            {
                "action": "note",
                "instruction": instruction,
                "status": "planning_required",
            },
        ]

        return actions

    def save(self, actions: List[Dict[str, Any]]) -> Path:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

        PLAN_FILE.write_text(
            json.dumps(actions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return PLAN_FILE
