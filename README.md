# 🧠 Poor Gemini 2.5 Flash with His Smart Claude Opus 4.7 Wife

A multi-agent AI workflow where **Claude Opus 4.7** acts as the consultant (plans, reviews, synthesizes) and a cheaper model — **Gemini 2.5 Flash** or **Claude Sonnet 4.6** — does the actual work.

Inspired by Anthropic's pattern of using a high-capability model as an orchestrator to maximize quality while minimizing cost.

---

## Architecture

```
Your Task
    │
    ▼
┌─────────────────────────────────────┐
│   Consultant — Claude Opus 4.7      │  ← plans, reviews, synthesizes
│   (adaptive thinking enabled)       │    called sparingly
└──────────────┬──────────────────────┘
               │ step-by-step instructions
               ▼
┌─────────────────────────────────────┐
│   Workers  (your choice)            │
│                                     │
│   --engine gemini  → Gemini 2.5 Flash  (cheapest)
│   --engine claude  → Sonnet 4.6        (default)  │
└─────────────────────────────────────┘
               │
               ▼
         Final Output
```

The consultant uses **adaptive thinking** to reason about the task, break it into steps, assign each step to a specialist agent, review the output, and request revisions if needed — all automatically.

---

## Setup

```bash
git clone https://github.com/Yinchaochen/Poor-Gemini-2.5-Flash-with-His-Smart-omini-Claude-Opus-4.7-Wife.git
cd Poor-Gemini-2.5-Flash-with-His-Smart-omini-Claude-Opus-4.7-Wife

pip install -r requirements.txt

cp .env.example .env
# Edit .env and fill in your API keys
```

### Required API Keys

| Key | Used for | Get it from |
|-----|----------|-------------|
| `ANTHROPIC_API_KEY` | Consultant (Opus 4.7) — always required | [console.anthropic.com](https://console.anthropic.com) |
| `GOOGLE_API_KEY` | Workers when using `--engine gemini` | [aistudio.google.com](https://aistudio.google.com) |

---

## Usage

```bash
# Interactive mode
python main.py

# Gemini workers (cheapest combination)
python main.py -w research_and_write -t "Write an article about AI video summarization" --engine gemini

# Claude Sonnet workers (default)
python main.py -w research_and_write -t "Analyze the competitive landscape for short-video apps"

# List available workflows and engines
python main.py --list
```

---

## What Happens at Runtime

```
[Consultant] Planning task with agents: ['research', 'writer']
  Step 1 → [research]: Research the topic and return key findings…
  Step 2 → [writer]: Based on {{step_1}}, write a polished article…

[Worker:research] Executing step 1…
  Result preview: AI video summarization tools have grown rapidly…
  [Consultant] ✓ Approved

[Worker:writer] Executing step 2…
  Result preview: # The Rise of AI Video Summarization…
  [Consultant] ✓ Approved

[Consultant] Synthesizing final output…

══════════════════════════
FINAL OUTPUT
══════════════════════════
…
```

---

## Built-in Agents

| Agent | Role |
|-------|------|
| `research` | Researches topics and returns structured findings |
| `writer` | Writes polished articles, reports, and summaries |
| `code` | Writes, reviews, and refactors code |

---

## Adding a New Agent

Create a file in `agents/`:

```python
# agents/translator_agent.py
from .base_agent import BaseAgent

class TranslatorAgent(BaseAgent):
    name = "translator"
    description = "Translates text between languages while preserving tone."
    system_prompt = """You are a professional translator.
Preserve tone, formatting, and nuance. Output only the translated text."""

    def __init__(self, engine: str = "claude") -> None:
        super().__init__(engine=engine)
```

Then register it in `agents/__init__.py`:

```python
from .translator_agent import TranslatorAgent
```

---

## Adding a New Workflow

Create a file in `workflows/`:

```python
# workflows/translate_and_publish.py
from .base_workflow import BaseWorkflow
from agents.writer_agent import WriterAgent
from agents.translator_agent import TranslatorAgent

class TranslateAndPublishWorkflow(BaseWorkflow):
    name = "translate_and_publish"

    def _build_agents(self, engine: str) -> dict:
        return {
            "writer":     WriterAgent(engine=engine),
            "translator": TranslatorAgent(engine=engine),
        }
```

Register it in `main.py`:

```python
from workflows.translate_and_publish import TranslateAndPublishWorkflow

WORKFLOWS = {
    "research_and_write":    ResearchAndWriteWorkflow,
    "translate_and_publish": TranslateAndPublishWorkflow,  # ← add here
}
```

---

## Cost Comparison (per workflow run)

| Mode | Consultant | Workers | Estimated cost |
|------|-----------|---------|----------------|
| `--engine gemini` | Opus 4.7 | Gemini 2.5 Flash | ~$0.05–0.10 |
| `--engine claude` | Opus 4.7 | Sonnet 4.6 | ~$0.08–0.18 |

Opus 4.7 is called only 3–4 times per run (plan + reviews + synthesize). Workers handle the heavy lifting.

---

## Project Structure

```
.
├── main.py                  # CLI entry point
├── gemini_call.py           # Standalone Gemini helper (for direct shell use)
├── core/
│   ├── consultant.py        # Opus 4.7 orchestrator
│   ├── worker.py            # Sonnet 4.6 executor
│   ├── gemini_worker.py     # Gemini 2.5 Flash executor
│   └── runner.py            # Workflow execution engine
├── agents/
│   ├── base_agent.py        # Base class for all agents
│   ├── research_agent.py
│   ├── writer_agent.py
│   └── code_agent.py
└── workflows/
    ├── base_workflow.py     # Base class for all workflows
    └── research_and_write.py
```
