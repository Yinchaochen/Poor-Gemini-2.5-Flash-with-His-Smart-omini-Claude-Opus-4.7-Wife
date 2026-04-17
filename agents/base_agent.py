"""
BaseAgent — extend this to create any new specialist agent.

Minimum to implement:
  - name         : unique snake_case identifier (used in workflow configs)
  - description  : one sentence — tells the Consultant what this agent does
  - system_prompt: the worker's role/persona

engine options: "claude" (Sonnet 4.6) | "gemini" (Gemini 2.5 Flash)
"""

from core import make_worker


class BaseAgent:
    name: str = "base"
    description: str = "A generic agent."
    system_prompt: str = "You are a helpful assistant."

    def __init__(self, engine: str = "claude") -> None:
        self._worker = make_worker(engine)

    def run(self, instructions: str, context: str = "") -> str:
        """Execute one step. Called by Runner."""
        return self._worker.execute(self.system_prompt, instructions, context)
