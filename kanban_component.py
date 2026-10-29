"""
kanban_component.py — Componente custom de Streamlit
Renderiza un tablero Kanban con arrastre real entre columnas (SortableJS).
"""
from __future__ import annotations
import os
import streamlit.components.v1 as components

_RELEASE = False
_COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "kanban_frontend")

_component_func = components.declare_component(
    "kanban_board",
    path=_COMPONENT_PATH,
)


def kanban_board(columns, key=None):
    """Renderiza el tablero Kanban y devuelve el estado actualizado."""
    return _component_func(columns=columns, key=key, default=columns)
