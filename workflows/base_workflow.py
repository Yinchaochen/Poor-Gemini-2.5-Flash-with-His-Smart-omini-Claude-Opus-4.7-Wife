"""
BaseWorkflow — extend this to create a new workflow.

Minimum to implement:
  - name    : human-readable identifier
  - _build_agents(engine) : return dict of {agent_name: AgentInstance}

engine options: "claude" (Sonnet 4.6 workers) | "gemini" (Gemini 2.5 Flash workers)
Consultant is always Opus 4.7 regardless of engine.
"""

from core.runner import Runner
from agents.base_agent import BaseAgent


class BaseWorkflow:
    name: str = "base_workflow"

    def _build_agents(self, engine: str) -> dict[str, BaseAgent]:
        """Override in subclasses to return {name: AgentInstance}."""
        raise NotImplementedError

    def run(self, task: str, engine: str = "claude", verbose: bool = True) -> str:
        """Execute the full consultant → worker → synthesize loop."""
        agents = self._build_agents(engine)
        if not agents:
            raise ValueError(f"Workflow '{self.name}' returned no agents.")
        if verbose:
            worker_label = "Gemini 2.5 Flash" if engine == "gemini" else "Sonnet 4.6"
            print(f"Engine   : Opus 4.7 (consultant) + {worker_label} (workers)")
        runner = Runner(agents)
        return runner.run(task, verbose=verbose)
