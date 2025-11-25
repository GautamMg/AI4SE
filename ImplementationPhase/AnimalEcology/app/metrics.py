from threading import Lock
from typing import Dict

_counts: Dict[str, int] = {}
_lock = Lock()


def increment(name: str) -> None:
    """Increment a named counter in a threadsafe way."""
    with _lock:
        _counts[name] = _counts.get(name, 0) + 1


def snapshot() -> Dict[str, int]:
    """Return a shallow copy of current metric counts."""
    with _lock:
        return dict(_counts)
