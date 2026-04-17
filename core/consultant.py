"""
Consultant — Opus 4.7 with adaptive thinking.

Called ON-DEMAND only when the worker escalates a complex task.
Single responsibility: advise(task, complexity_reason) → strategic guidance.
"""

import anthropic

_MODEL = "claude-opus-4-7"

_ADVISE_SYSTEM = """You are a senior expert consultant called in for difficult problems.
A junior worker has assessed a task as too complex to handle alone and needs your guidance.

Your job:
- Think deeply about the best approach to this task.
- Return a clear, actionable strategy the worker can follow to complete the task well.
- Be specific: outline the key steps, warn about pitfalls, and suggest the best approach.
- Do NOT do the task yourself — write guidance for the worker to execute.
- Keep your response focused and practical (not longer than needed).
"""


class Consultant:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic()

    def advise(self, task: str, complexity_reason: str) -> str:
        """Return strategic guidance for the worker to execute a complex task."""
        prompt = (
            f"Task the worker needs to complete:\n{task}\n\n"
            f"Why the worker flagged this as complex:\n{complexity_reason}\n\n"
            f"Provide strategic guidance so the worker can complete this task well."
        )
        resp = self._client.messages.create(
            model=_MODEL,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=_ADVISE_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return next(b.text for b in resp.content if b.type == "text")
