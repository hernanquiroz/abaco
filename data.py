"""
data.py — Estructura inicial del tablero (datos por defecto).
"""
from __future__ import annotations

DEFAULT_BOARD = [
    {
        "id": "col_backlog",
        "title": "📌 Por hacer",
        "color": "#6B7280",
        "cards": [
            {
                "id": "card_001",
                "title": "Diseñar la landing page",
                "description": "Boceto inicial en Figma con hero + features.",
                "color": "#FFFFFF",
            },
            {
                "id": "card_002",
                "title": "Definir métricas de éxito",
                "description": "KPIs: conversión, tiempo en página, rebote.",
                "color": "#FFFFFF",
            },
        ],
    },
    {
        "id": "col_progress",
        "title": "🚧 En progreso",
        "color": "#3B82F6",
        "cards": [
            {
                "id": "card_003",
                "title": "Implementar drag-and-drop",
                "description": "Usar SortableJS dentro del componente custom.",
                "color": "#FFFFFF",
            },
        ],
    },
    {
        "id": "col_review",
        "title": "👀 En revisión",
        "color": "#F59E0B",
        "cards": [
            {
                "id": "card_004",
                "title": "PR #42 — refactor de estado",
                "description": "Revisar antes del merge a main.",
                "color": "#FFFFFF",
            },
        ],
    },
    {
        "id": "col_done",
        "title": "✅ Hecho",
        "color": "#10B981",
        "cards": [
            {
                "id": "card_005",
                "title": "Configurar repo en GitHub",
                "description": "Estructura numerada lista.",
                "color": "#FFFFFF",
            },
            {
                "id": "card_006",
                "title": "Desplegar en Streamlit Cloud",
                "description": "Entry point: 01_app.py",
                "color": "#FFFFFF",
            },
        ],
    },
]
