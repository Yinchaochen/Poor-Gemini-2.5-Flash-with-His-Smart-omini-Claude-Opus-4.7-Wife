"""
Runner — the workflow execution engine.

Orchestration logic (Gemini-first with on-demand Opus escalation):
  1. Worker receives the task and assesses complexity.
  2. Simple path  → worker completes the task alone (Opus never called).
  3. Complex path → worker asks Consultant (Opus) for guidance,
                    then executes the task using that guidance.
"""

from .consultant import Consultant
from .worker import Worker
from .gemini_worker import GeminiWorker


class Runner:
    def __init__(self, agents: dict, engine: str = "gemini") -> None:
        """
        agents: {name: BaseAgent}  — populated by the Workflow.
        engine: "gemini" | "claude" — which worker model to use.
        """
        self._agents = agents
        self._engine = engine
        self._consultant: Consultant | None = None  # lazy — only created if needed

    def _get_consultant(self) -> Consultant:
        if self._consultant is None:
            self._consultant = Consultant()
        return self._consultant

    def _make_worker(self) -> Worker | GeminiWorker:
        if self._engine == "gemini":
            return GeminiWorker()
        return Worker()

    # ------------------------------------------------------------------
    def run(self, task: str, verbose: bool = True) -> str:
        """
        Run a task through the worker, escalating to Opus only if complex.
        Uses the first agent's system_prompt as the worker's role context.
        """
        # Pick the first (or only) agent's system prompt as the role
        if not self._agents:
            raise ValueError("No agents registered in this workflow.")

        # For multi-agent workflows, concatenate all agent prompts as context
        agent_context = "\n\n".join(
            f"[{name} role]\n{agent.system_prompt}"
            for name, agent in self._agents.items()
        )

        worker = self._make_worker()

        # ── 1. Assess complexity ───────────────────────────────────────
        if verbose:
            print(f"\n[Worker:{self._engine}] Assessing task complexity…")

        assessment = worker.assess_complexity(task)
        is_complex: bool = assessment.get("is_complex", False)
        reason: str = assessment.get("reason", "")

        if verbose:
            label = "COMPLEX" if is_complex else "SIMPLE"
            print(f"  → {label}: {reason}")

        # ── 2a. Simple path — worker handles alone ─────────────────────
        if not is_complex:
            if verbose:
                print(f"\n[Worker:{self._engine}] Handling task independently…")
            result = worker.execute(
                system_prompt=agent_context,
                instructions=task,
            )
            if verbose:
                preview = result[:120].replace("\n", " ")
                print(f"  Result preview: {preview}…")
            return result

        # ── 2b. Complex path — consult Opus first ──────────────────────
        if verbose:
            print(f"\n[Consultant:Opus] Providing guidance for complex task…")

        guidance = self._get_consultant().advise(task, reason)

        if verbose:
            preview = guidance[:120].replace("\n", " ")
            print(f"  Guidance preview: {preview}…")
            print(f"\n[Worker:{self._engine}] Executing with expert guidance…")

        result = worker.execute(
            system_prompt=agent_context,
            instructions=task,
            guidance=guidance,
        )

        if verbose:
            preview = result[:120].replace("\n", " ")
            print(f"  Result preview: {preview}…")

        return result
