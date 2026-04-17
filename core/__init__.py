from .consultant import Consultant
from .worker import Worker
from .gemini_worker import GeminiWorker
from .runner import Runner


def make_worker(engine: str):
    """Factory — returns the right worker for the chosen engine."""
    if engine == "gemini":
        return GeminiWorker()
    if engine == "claude":
        return Worker()
    raise ValueError(f"Unknown engine '{engine}'. Choose 'claude' or 'gemini'.")


__all__ = ["Consultant", "Worker", "GeminiWorker", "Runner", "make_worker"]
