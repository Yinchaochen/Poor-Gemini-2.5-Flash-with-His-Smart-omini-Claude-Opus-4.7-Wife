"""
Runner — the workflow execution engine.

Orchestration loop:
  1. Consultant plans → list of steps
  2. For each step:
       a. Resolve {{step_N}} placeholders with prior results
       b. Worker executes
       c. Consultant reviews — if rejected, worker revises (max MAX_REVISIONS times)
  3. Consultant synthesizes all results → final output
"""

import re
from .consultant import Consultant
from .worker import Worker


MAX_REVISIONS = 2  # how many times a worker can be asked to revise one step


class Runner:
    def __init__(self, agents: dict) -> None:
        """
        agents: {name: BaseAgent}  — populated by the Workflow
        """
        self._agents = agents
        self._consultant = Consultant()

    # ------------------------------------------------------------------
    def run(self, task: str, verbose: bool = True) -> str:
        agent_names = list(self._agents.keys())

        # ── 1. Plan ────────────────────────────────────────────────────
        if verbose:
            print(f"\n[Consultant] Planning task with agents: {agent_names}")
        steps = self._consultant.plan(task, agent_names)
        if verbose:
            for s in steps:
                print(f"  Step {s['id']} → [{s['agent']}]: {s['instructions'][:80]}…")

        # ── 2. Execute ─────────────────────────────────────────────────
        results: dict[int, str] = {}

        for step in steps:
            step_id: int = step["id"]
            agent_name: str = step["agent"]
            instructions: str = step["instructions"]

            if agent_name not in self._agents:
                raise ValueError(
                    f"Step {step_id} requests unknown agent '{agent_name}'. "
                    f"Available: {agent_names}"
                )

            agent = self._agents[agent_name]
            instructions = _resolve_placeholders(instructions, results)
            context = _build_context(results)

            if verbose:
                print(f"\n[Worker:{agent_name}] Executing step {step_id}…")

            result = ""
            for attempt in range(MAX_REVISIONS + 1):
                result = agent.run(instructions, context)

                if verbose:
                    preview = result[:120].replace("\n", " ")
                    print(f"  Result preview: {preview}…")

                review = self._consultant.review(instructions, result)

                if review["approved"]:
                    if verbose:
                        print(f"  [Consultant] ✓ Approved")
                    break

                if attempt < MAX_REVISIONS:
                    feedback = review["feedback"]
                    if verbose:
                        print(f"  [Consultant] ✗ Revision requested: {feedback}")
                    instructions = (
                        f"{instructions}\n\n"
                        f"[Revision request — attempt {attempt + 2}/{MAX_REVISIONS + 1}]:\n"
                        f"{feedback}"
                    )
                else:
                    if verbose:
                        print(f"  [Consultant] Max revisions reached — accepting result")

            results[step_id] = result

        # ── 3. Synthesize ──────────────────────────────────────────────
        if verbose:
            print("\n[Consultant] Synthesizing final output…")

        final = self._consultant.synthesize(task, list(results.values()))
        return final


# ── Helpers ───────────────────────────────────────────────────────────

def _resolve_placeholders(text: str, results: dict[int, str]) -> str:
    """Replace {{step_N}} with the actual result of step N."""
    def replacer(m: re.Match) -> str:
        step_id = int(m.group(1))
        return results.get(step_id, f"[step {step_id} not yet available]")

    return re.sub(r"\{\{step_(\d+)\}\}", replacer, text)


def _build_context(results: dict[int, str]) -> str:
    if not results:
        return ""
    parts = [f"Step {sid} result:\n{res}" for sid, res in sorted(results.items())]
    return "\n\n".join(parts)
