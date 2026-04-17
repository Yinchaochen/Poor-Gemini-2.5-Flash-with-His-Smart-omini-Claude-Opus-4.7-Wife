from .base_agent import BaseAgent


class WriterAgent(BaseAgent):
    name = "writer"
    description = "Writes polished, engaging prose — articles, reports, summaries, or any text content."

    def __init__(self, engine: str = "claude") -> None:
        super().__init__(engine=engine)

    system_prompt = """You are a professional writer and editor.
When given content or a brief:
- Write clear, engaging, well-structured prose.
- Match tone to the request (formal report, casual blog, concise summary, etc.).
- Do not pad with filler — every sentence should add value.
- Use markdown headings and lists only when they genuinely aid readability.
"""
