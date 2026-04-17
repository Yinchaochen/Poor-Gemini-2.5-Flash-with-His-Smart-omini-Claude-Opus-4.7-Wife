"""
AI Agent Workflow — CLI entry point.

Usage:
  python main.py                                              # interactive mode
  python main.py --workflow research_and_write --task "..."  # claude workers (default)
  python main.py --workflow research_and_write --task "..." --engine gemini
  python main.py --list
"""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from workflows.research_and_write import ResearchAndWriteWorkflow

WORKFLOWS: dict[str, type] = {
    "research_and_write": ResearchAndWriteWorkflow,
    # "my_new_workflow": MyNewWorkflow,  ← register new workflows here
}

ENGINES = ("claude", "gemini")


def list_workflows() -> None:
    print("\nAvailable workflows:")
    for name in WORKFLOWS:
        print(f"  {name}")
    print(f"\nAvailable engines: {', '.join(ENGINES)}")
    print()


def run(workflow_name: str, task: str, engine: str) -> None:
    if workflow_name not in WORKFLOWS:
        print(f"Unknown workflow '{workflow_name}'. Use --list to see options.")
        sys.exit(1)

    workflow = WORKFLOWS[workflow_name]()
    print(f"\n{'='*60}")
    print(f"Workflow : {workflow_name}")
    print(f"Task     : {task}")
    print(f"{'='*60}")

    result = workflow.run(task, engine=engine, verbose=True)

    print(f"\n{'='*60}")
    print("FINAL OUTPUT")
    print(f"{'='*60}\n")
    print(result)


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="AI Agent Workflow Runner")
    parser.add_argument("--workflow", "-w", help="Workflow name")
    parser.add_argument("--task", "-t", help="Task description")
    parser.add_argument(
        "--engine", "-e",
        choices=ENGINES,
        default="claude",
        help="Worker engine: 'claude' (Sonnet 4.6) or 'gemini' (Gemini 2.5 Flash). Default: claude",
    )
    parser.add_argument("--list", "-l", action="store_true", help="List options")
    args = parser.parse_args()

    if args.list:
        list_workflows()
        return

    # Validate Gemini key only when needed
    if args.engine == "gemini" and not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not set (required for --engine gemini).")
        sys.exit(1)

    # Interactive mode
    if not args.workflow and not args.task:
        list_workflows()
        wf = input("Select workflow: ").strip()
        task = input("Enter task: ").strip()
        engine = input(f"Engine [{'/'.join(ENGINES)}] (default: claude): ").strip() or "claude"
        run(wf, task, engine)
        return

    if not args.workflow or not args.task:
        parser.print_help()
        sys.exit(1)

    run(args.workflow, args.task, args.engine)


if __name__ == "__main__":
    main()
