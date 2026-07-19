"""Minimal orchestrator for the DesktopAgent CLI.

The orchestrator coordinates DesktopAgent through subprocess calls.
It intentionally does not import DesktopAgent directly.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import List, Sequence


class OrchestratorError(RuntimeError):
    """Raised when a DesktopAgent CLI command fails."""


class DesktopOrchestrator:
    """Coordinate the DesktopAgent command-line workflow."""

    def __init__(self, python_executable: str = sys.executable) -> None:
        self.python_executable = python_executable

    def _command(self, *arguments: str) -> List[str]:
        """Build a DesktopAgent CLI command."""
        return [
            self.python_executable,
            "-m",
            "desktop.agent",
            *arguments,
        ]

    def _run(
        self,
        *arguments: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        """Run one DesktopAgent CLI command."""
        command = self._command(*arguments)

        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )

        if check and result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            if not message:
                message = "DesktopAgent command failed."

            raise OrchestratorError(
                f"{message}\n"
                f"Command: {' '.join(command)}"
            )

        return result

    def request(self, instruction: str) -> None:
        """Observe the desktop and generate a plan."""
        instruction = instruction.strip()

        if not instruction:
            raise OrchestratorError(
                "Instruction must not be empty."
            )

        print("=== OBSERVE ===")
        observe_result = self._run("observe")
        self._print_output(observe_result)

        print()
        print("=== PLAN ===")
        plan_result = self._run(
            "plan",
            instruction,
        )
        self._print_output(plan_result)

        print()
        print("Approval is required.")
        print(
            "Run: python3 -m "
            "desktop.orchestrator approve"
        )

    def approve(self) -> None:
        """Approve the current DesktopAgent plan."""
        result = self._run("approve")
        self._print_output(result)

        print()
        print(
            "Run: python3 -m "
            "desktop.orchestrator execute"
        )

    def execute(self) -> None:
        """Execute the approved DesktopAgent plan."""
        result = self._run("execute")
        self._print_output(result)

        print()
        print(
            "Run: python3 -m "
            "desktop.orchestrator status"
        )

    def status(self) -> None:
        """Display the current DesktopAgent status."""
        result = self._run(
            "status",
            check=False,
        )

        self._print_output(result)

        if result.returncode != 0:
            raise OrchestratorError(
                "DesktopAgent status command failed."
            )

    @staticmethod
    def _print_output(
        result: subprocess.CompletedProcess[str],
    ) -> None:
        """Print captured stdout and stderr."""
        if result.stdout:
            print(result.stdout.rstrip())

        if result.stderr:
            print(
                result.stderr.rstrip(),
                file=sys.stderr,
            )


def build_parser() -> argparse.ArgumentParser:
    """Build the orchestrator CLI parser."""
    parser = argparse.ArgumentParser(
        prog="python3 -m desktop.orchestrator",
        description=(
            "Coordinate DesktopAgent through its CLI."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="COMMAND",
    )

    request_parser = subparsers.add_parser(
        "request",
        help="Observe the desktop and create a plan.",
    )
    request_parser.add_argument(
        "instruction",
        help="Natural-language desktop instruction.",
    )

    subparsers.add_parser(
        "approve",
        help="Approve the current plan.",
    )

    subparsers.add_parser(
        "execute",
        help="Execute the approved plan.",
    )

    subparsers.add_parser(
        "status",
        help="Show DesktopAgent status.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Desktop Orchestrator CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    orchestrator = DesktopOrchestrator()

    try:
        if args.command == "request":
            orchestrator.request(args.instruction)
        elif args.command == "approve":
            orchestrator.approve()
        elif args.command == "execute":
            orchestrator.execute()
        elif args.command == "status":
            orchestrator.status()
        else:
            parser.error(
                f"Unknown command: {args.command}"
            )

        return 0

    except OrchestratorError as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    except KeyboardInterrupt:
        print(
            "\nInterrupted.",
            file=sys.stderr,
        )
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
