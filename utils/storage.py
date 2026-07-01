import json
from pathlib import Path
from typing import List, Any
from threading import Lock

DATA_DIR = Path("data")
HISTORY_FILE = DATA_DIR / "chat_history.json"
_lock = Lock()


def _ensure():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]")


def append_history(item: dict) -> None:
    """Append a record to the chat history JSON file."""
    _ensure()
    with _lock:
        try:
            data = json.loads(HISTORY_FILE.read_text())
        except Exception:
            data = []
        data.append(item)
        HISTORY_FILE.write_text(json.dumps(data, indent=2))


def read_history() -> List[Any]:
    """Read chat history (returns a list)."""
    _ensure()
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []
