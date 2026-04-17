# 🧠 Poor Gemini 2.5 Flash with His Smart Claude Opus 4.7 Wife

A multi-agent AI workflow where **Gemini 2.5 Flash** (or **Claude Sonnet 4.6**) handles tasks by default, and only escalates to **Claude Opus 4.7** when the task is genuinely complex.

The key insight: most tasks don't need the expensive model. Let the cheap worker decide when it needs help.

---

## Architecture

```
Your Task
    │
    ▼
┌─────────────────────────────────────┐
│   Worker  (cheap, fast)             │
│   Gemini 2.5 Flash / Sonnet 4.6    │
│                                     │
│   Step 1: Assess complexity         │
│     → Simple?  Handle alone ✓       │
│     → Complex? Ask Opus for help    │
└──────────────┬──────────────────────┘
               │ only if complex
               ▼
┌─────────────────────────────────────┐
│   Consultant — Claude Opus 4.7      │
│   (adaptive thinking)               │
│                                     │
│   Returns strategic guidance        │
│   Worker then executes with it      │
└─────────────────────────────────────┘
               │
               ▼
         Final Output
```

**Simple path** (Opus never called):
```
Task → Worker assesses → "I can handle this" → Worker completes → Done
```

**Complex path** (Opus called once):
```
Task → Worker assesses → "This is complex: [reason]"
     → Opus thinks deeply → Returns guidance
     → Worker executes with that guidance → Done
```

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
| `GOOGLE_API_KEY` | Gemini 2.5 Flash worker (default engine) | [aistudio.google.com](https://aistudio.google.com) |
| `ANTHROPIC_API_KEY` | Opus 4.7 consultant — **only needed for complex tasks** | [console.anthropic.com](https://console.anthropic.com) |

If you only use simple tasks with Gemini, `ANTHROPIC_API_KEY` is never called and not required.

---

## Usage

```bash
# Interactive mode
python main.py

# Gemini worker (default — cheapest)
python main.py -w research_and_write -t "Summarize the key ideas behind transformer models"

# Force Claude Sonnet workers instead
python main.py -w research_and_write -t "Write a blog post about AI agents" --engine claude

# List available workflows and engines
python main.py --list
```

---

## What Happens at Runtime

**Simple task:**
```
[Worker:gemini] Assessing task complexity…
  → SIMPLE: This is a well-defined factual summary task.

[Worker:gemini] Handling task independently…
  Result preview: Transformer models use self-attention mechanisms…

══════════════════════════
FINAL OUTPUT
══════════════════════════
…
```

**Complex task:**
```
[Worker:gemini] Assessing task complexity…
  → COMPLEX: This requires deep architectural decisions with many trade-offs.

[Consultant:Opus] Providing guidance for complex task…
  Guidance preview: Consider breaking this into three phases: first…

[Worker:gemini] Executing with expert guidance…
  Result preview: Based on the architectural guidance…

══════════════════════════
FINAL OUTPUT
══════════════════════════
…
```

---

## Cost Model

| Scenario | Models called | Estimated cost |
|----------|--------------|----------------|
| Simple task, Gemini engine | Gemini only (×2 — assess + execute) | ~$0.001–0.005 |
| Complex task, Gemini engine | Gemini (×2) + Opus (×1) | ~$0.05–0.10 |
| Simple task, Claude engine | Sonnet only (×2) | ~$0.01–0.03 |
| Complex task, Claude engine | Sonnet (×2) + Opus (×1) | ~$0.08–0.18 |

Opus is only called **once per complex task** — for guidance only, never for execution.

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

    def __init__(self, engine: str = "gemini") -> None:
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

## Project Structure

```
.
├── main.py                  # CLI entry point
├── gemini_call.py           # Standalone Gemini helper (for direct shell use)
├── core/
│   ├── consultant.py        # Opus 4.7 — on-demand advisor (advise() only)
│   ├── worker.py            # Sonnet 4.6 executor (assess_complexity + execute)
│   ├── gemini_worker.py     # Gemini 2.5 Flash executor (assess_complexity + execute)
│   └── runner.py            # Workflow execution engine (worker-first logic)
├── agents/
│   ├── base_agent.py        # Base class for all agents
│   ├── research_agent.py
│   ├── writer_agent.py
│   └── code_agent.py
└── workflows/
    ├── base_workflow.py     # Base class for all workflows
    └── research_and_write.py
```
