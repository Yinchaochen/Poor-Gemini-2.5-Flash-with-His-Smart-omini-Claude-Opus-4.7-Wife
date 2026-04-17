from .base_agent import BaseAgent


class CodeAgent(BaseAgent):
    name = "code"
    description = "Writes, reviews, or refactors code in any language."

    def __init__(self, engine: str = "claude") -> None:
        super().__init__(engine=engine)

    system_prompt = """You are a senior software engineer.
When given a coding task:
- Write clean, readable, production-quality code.
- Include only necessary comments (explain WHY, not WHAT).
- If the language is not specified, infer from context or default to Python.
- Return code blocks with the correct language tag.
- Do not add unrequested features or abstractions.
"""
