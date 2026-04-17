"""
GeminiWorker — Google Gemini 2.5 Flash as the primary executor.

Responsibilities:
  1. assess_complexity() — judge whether the task needs Opus guidance
  2. execute()           — complete the task (with optional guidance)
"""

import json
import os
import re

from google import genai
from google.genai import types

_MODEL = "models/gemini-2.5-flash"

_ASSESS_SYSTEM = """You are an expert at evaluating task complexity.
Given a task, decide whether you can handle it well on your own or need expert guidance.

Return ONLY valid JSON — no markdown fences, no extra text:
{
  "is_complex": true | false,
  "reason": "<one sentence explaining your assessment>"
}

Mark as complex (true) if the task requires:
- Deep domain expertise or specialized knowledge
- Multi-step reasoning with many interdependent parts
- High-stakes output where mistakes are costly
- Ambiguous requirements needing senior judgment

Mark as simple (false) if the task is:
- Clearly defined with a straightforward approach
- Within common knowledge and best practices
- Low-stakes or easily reversible
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()
    return json.loads(text)


class GeminiWorker:
    def __init__(self) -> None:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY not set")
        self._client = genai.Client(api_key=api_key)

    def assess_complexity(self, task: str) -> dict:
        """Return {is_complex: bool, reason: str}."""
        resp = self._client.models.generate_content(
            model=_MODEL,
            contents=task,
            config=types.GenerateContentConfig(
                system_instruction=_ASSESS_SYSTEM,
            ),
        )
        try:
            return _extract_json(resp.text)
        except (json.JSONDecodeError, KeyError):
            # If parsing fails, assume simple to avoid unnecessary Opus calls
            return {"is_complex": False, "reason": "Could not parse assessment — defaulting to simple."}

    def execute(
        self,
        system_prompt: str,
        instructions: str,
        context: str = "",
        guidance: str = "",
    ) -> str:
        """Run the task and return the result as a string."""
        user_content = instructions
        if context:
            user_content = f"Context from previous steps:\n{context}\n\n---\n\n{instructions}"
        if guidance:
            user_content = f"Expert guidance for this task:\n{guidance}\n\n---\n\n{user_content}"

        resp = self._client.models.generate_content(
            model=_MODEL,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return resp.text
