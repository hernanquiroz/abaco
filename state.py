"""
state.py — Persistencia del estado del tablero.
"""
from __future__ import annotations
import json
from pathlib import Path

from data import DEFAULT_BOARD

DATA_FILE = Path(__file__).parent / "kanban_data.json"


def init_state():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return [col.copy() for col in DEFAULT_BOARD]


def save_state(board):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as fh:
            json.dump(board, fh, ensure_ascii=False, indent=2)
    except OSError:
        pass


def reset_state():
    default = [col.copy() for col in DEFAULT_BOARD]
    save_state(default)
    return default


def export_json(board):
    return json.dumps(board, ensure_ascii=False, indent=2).encode("utf-8")


def import_json(uploaded_file):
    content = uploaded_file.read()
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("El JSON debe ser una lista de columnas.")
    for col in data:
        if not isinstance(col, dict) or "title" not in col or "cards" not in col:
            raise ValueError("Cada columna debe tener 'title' y 'cards'.")
    return data
