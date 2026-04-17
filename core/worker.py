"""
Worker — Sonnet 4.6.

The cheap, fast executor.  Receives a system prompt (the agent's role),
precise instructions from the Consultant, and optional context (prior step
results).  Returns a plain-text result.
"""

import anthropic

_MODEL = "claude-sonnet-4-6"


class Worker:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic()

    def execute(
        self,
        system_prompt: str,
        instructions: str,
        context: str = "",
    ) -> str:
        """Run a single step and return the result as a string."""
        user_content = instructions
        if context:
            user_content = f"Context from previous steps:\n{context}\n\n---\n\n{instructions}"

        resp = self._client.messages.create(
            model=_MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        return next(b.text for b in resp.content if b.type == "text")
