"""
Consultant — Opus 4.7 with adaptive thinking.

Responsibilities:
  1. plan()      — break a task into ordered steps, assign each to an agent
  2. review()    — inspect a worker's result, approve or request revision
  3. synthesize() — merge all step results into the final deliverable
"""

import json
import re
import anthropic

_MODEL = "claude-opus-4-7"

_PLAN_SYSTEM = """You are a senior AI consultant who coordinates a team of specialist agents.
Given a task and the list of available agents, produce a concise execution plan.

Return ONLY valid JSON — no markdown fences, no explanation outside the JSON:
{
  "steps": [
    {
      "id": 1,
      "agent": "<agent_name>",
      "instructions": "<precise instructions for that agent>"
    }
  ]
}

Rules:
- Use only agent names from the provided list.
- Keep instructions specific and self-contained.
- Reference prior steps as {{step_<id>}} when needed (e.g. "Based on {{step_1}}, write...").
- Minimum 1 step, maximum 6 steps.
"""

_REVIEW_SYSTEM = """You are a quality-control consultant reviewing a worker's output.
Return ONLY valid JSON:
{
  "approved": true | false,
  "feedback": "<one concise sentence — empty string if approved>"
}

Approve if the result adequately fulfills the instructions.
Reject only for clear gaps or quality issues; be constructive.
"""

_SYNTHESIZE_SYSTEM = """You are a senior consultant writing the final deliverable.
Combine the provided step results into a polished, cohesive response to the original task.
Write naturally — do not mention steps, agents, or internal process.
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()
    return json.loads(text)


class Consultant:
    def __init__(self) -> None:
        self._client = anthropic.Anthropic()

    # ------------------------------------------------------------------
    def plan(self, task: str, available_agents: list[str]) -> list[dict]:
        """Return a list of step dicts: [{id, agent, instructions}, ...]."""
        agents_str = ", ".join(available_agents)
        prompt = f"Available agents: {agents_str}\n\nTask:\n{task}"

        resp = self._client.messages.create(
            model=_MODEL,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=_PLAN_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next(b.text for b in resp.content if b.type == "text")
        data = _extract_json(text)
        return data["steps"]

    # ------------------------------------------------------------------
    def review(self, instructions: str, result: str) -> dict:
        """Return {approved: bool, feedback: str}."""
        prompt = (
            f"Instructions given to the worker:\n{instructions}\n\n"
            f"Worker's result:\n{result}"
        )
        resp = self._client.messages.create(
            model=_MODEL,
            max_tokens=512,
            thinking={"type": "adaptive"},
            system=_REVIEW_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next(b.text for b in resp.content if b.type == "text")
        return _extract_json(text)

    # ------------------------------------------------------------------
    def synthesize(self, task: str, step_results: list[str]) -> str:
        """Merge step results into the final answer."""
        parts = "\n\n".join(
            f"[Step {i + 1}]\n{r}" for i, r in enumerate(step_results)
        )
        prompt = f"Original task:\n{task}\n\nStep results:\n{parts}"
        resp = self._client.messages.create(
            model=_MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=_SYNTHESIZE_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return next(b.text for b in resp.content if b.type == "text")
