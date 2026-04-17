from .base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    name = "research"
    description = "Researches topics and returns structured findings with key facts and insights."

    def __init__(self, engine: str = "claude") -> None:
        super().__init__(engine=engine)

    system_prompt = """You are an expert research analyst.
When given a topic or question:
- Identify and explain the most important facts, trends, and insights.
- Structure your output clearly with sections if needed.
- Cite reasoning, not invented sources.
- Be thorough but concise — prioritise signal over filler.
"""
