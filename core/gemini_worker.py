"""
GeminiWorker — Google Gemini 2.5 Flash as the cheap executor.

Drop-in replacement for Worker: same execute() interface,
different model underneath.
"""

import os
from google import genai
from google.genai import types


_MODEL = "models/gemini-2.5-flash"


class GeminiWorker:
    def __init__(self) -> None:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY not set")
        self._client = genai.Client(api_key=api_key)

    def execute(
        self,
        system_prompt: str,
        instructions: str,
        context: str = "",
    ) -> str:
        """Run a single step and return the result as a string."""
        user_content = instructions
        if context:
            user_content = (
                f"Context from previous steps:\n{context}\n\n---\n\n{instructions}"
            )

        resp = self._client.models.generate_content(
            model=_MODEL,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return resp.text
