"""
ResearchAndWriteWorkflow

Opus 4.7 consultant coordinates: research → write

Workers configurable via engine:
  --engine claude   → Sonnet 4.6  (default)
  --engine gemini   → Gemini 2.5 Flash
"""

from .base_workflow import BaseWorkflow
from agents.research_agent import ResearchAgent
from agents.writer_agent import WriterAgent


class ResearchAndWriteWorkflow(BaseWorkflow):
    name = "research_and_write"

    def _build_agents(self, engine: str) -> dict:
        return {
            ResearchAgent.name: ResearchAgent(engine=engine),
            WriterAgent.name:   WriterAgent(engine=engine),
        }
