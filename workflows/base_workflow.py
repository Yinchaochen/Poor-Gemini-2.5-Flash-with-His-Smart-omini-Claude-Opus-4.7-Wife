"""
BaseWorkflow — extend this to create a new workflow.

Minimum to implement:
  - name    : human-readable identifier
  - _build_agents(engine) : return dict of {agent_name: AgentInstance}

engine options: "gemini" (Gemini 2.5 Flash, default) | "claude" (Sonnet 4.6)
Consultant (Opus 4.7) is only called when the worker escalates a complex task.
"""

from core.runner import Runner
from agents.base_agent import BaseAgent


class BaseWorkflow:
    name: str = "base_workflow"

    def _build_agents(self, engine: str) -> dict[str, BaseAgent]:
        """Override in subclasses to return {name: AgentInstance}."""
        raise NotImplementedError

    def run(self, task: str, engine: str = "gemini", verbose: bool = True) -> str:
        """Execute the worker-first, on-demand Opus escalation loop."""
        agents = self._build_agents(engine)
        if not agents:
            raise ValueError(f"Workflow '{self.name}' returned no agents.")
        if verbose:
            worker_label = "Gemini 2.5 Flash" if engine == "gemini" else "Sonnet 4.6"
            print(f"Engine   : {worker_label} (worker) + Opus 4.7 (on-demand consultant)")
        runner = Runner(agents, engine=engine)
        return runner.run(task, verbose=verbose)
