"""
01_app.py — Tablero Kanban interactivo (puro Python).
Sin componentes custom, sin HTML, sin JS. Funciona 100% en Streamlit Cloud.
Las fichas se mueven entre columnas con los botones ⬅ / ➡.
"""
from __future__ import annotations
import uuid
import json
from pathlib import Path
import streamlit as st


# ---------------------------------------------------------------------------
# Configuración de página (debe ser el primer comando de Streamlit)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Tablero Kanban",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Estado por defecto
# ---------------------------------------------------------------------------
DEFAULT_BOARD = [
    {
        "id": "col_backlog",
        "title": "📌 Por hacer",
        "color": "#6B7280",
        "cards": [
            {"id": "card_001", "title": "Diseñar landing", "description": "Boceto en Figma"},
            {"id": "card_002", "title": "Definir métricas", "description": "KPIs del proyecto"},
        ],
    },
    {
        "id": "col_progress",
        "title": "🚧 En progreso",
        "color": "#3B82F6",
        "cards": [
            {"id": "card_003", "title": "Implementar Kanban", "description": "Versión inicial"},
        ],
    },
    {
        "id": "col_review",
        "title": "👀 En revisión",
        "color": "#F59E0B",
        "cards": [],
    },
    {
        "id": "col_done",
        "title": "✅ Hecho",
        "color": "#10B981",
        "cards": [
            {"id": "card_004", "title": "Subir repo a GitHub", "description": ""},
        ],
    },
]

DATA_FILE = Path(__file__).parent / "kanban_data.json"


def load_state():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return [c.copy() for c in DEFAULT_BOARD]


def save_state(board):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as fh:
            json.dump(board, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Inicialización de sesión
# ---------------------------------------------------------------------------
if "board" not in st.session_state:
    st.session_state.board = load_state()


# ---------------------------------------------------------------------------
# Helpers de movimiento
# ---------------------------------------------------------------------------
def move_card(col_idx, card_idx, direction):
    """Mueve una ficha a la columna adyacente."""
    board = st.session_state.board
    if direction == "left" and col_idx > 0:
        card = board[col_idx]["cards"].pop(card_idx)
        board[col_idx - 1]["cards"].append(card)
    elif direction == "right" and col_idx < len(board) - 1:
        card = board[col_idx]["cards"].pop(card_idx)
        board[col_idx + 1]["cards"].append(card)
    save_state(board)
    st.rerun()


def delete_card(col_idx, card_idx):
    st.session_state.board[col_idx]["cards"].pop(card_idx)
    save_state(st.session_state.board)
    st.rerun()


# ---------------------------------------------------------------------------
# Cabecera y toolbar
# ---------------------------------------------------------------------------
st.title("📋 Tablero Kanban Interactivo")
st.caption("Mueve las fichas entre columnas con los botones ⬅ y ➡.")

toolbar = st.columns([1, 1, 1, 1, 4])

with toolbar[0]:
    if st.button("💾 Guardar", use_container_width=True):
        save_state(st.session_state.board)
        st.toast("Estado guardado.", icon="✅")

with toolbar[1]:
    if st.button("🔄 Reiniciar", use_container_width=True):
        st.session_state.board = [c.copy() for c in DEFAULT_BOARD]
        save_state(st.session_state.board)
        st.rerun()

with toolbar[2]:
    st.download_button(
        "⬇️ Exportar",
        data=json.dumps(st.session_state.board, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="kanban_backup.json",
        mime="application/json",
        use_container_width=True,
    )

with toolbar[3]:
    uploaded = st.file_uploader("⬆️ Importar", type=["json"], label_visibility="collapsed")
    if uploaded is not None:
        try:
            new_board = json.loads(uploaded.read())
            if isinstance(new_board, list):
                st.session_state.board = new_board
                save_state(new_board)
                st.rerun()
        except Exception as e:
            st.error(f"Error al importar: {e}")


# ---------------------------------------------------------------------------
# Render del tablero
# ---------------------------------------------------------------------------
board = st.session_state.board

if not board:
    st.info("No hay columnas. Crea una desde la barra lateral.")
else:
    cols = st.columns(len(board))
    for i, col_data in enumerate(board):
        with cols[i]:
            # Header coloreado
            st.markdown(
                f"<div style='background:{col_data.get('color', '#4F8DF7')};"
                f"color:white;padding:10px 14px;border-radius:8px 8px 0 0;"
                f"font-weight:700;font-size:14px;'>"
                f"{col_data['title']} "
                f"<span style='opacity:0.8;font-weight:400;'>({len(col_data['cards'])})</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Cuerpo de la columna
            with st.container(border=True):
                if not col_data["cards"]:
                    st.caption("_(sin fichas)_")
                for j, card in enumerate(col_data["cards"]):
                    with st.container(border=True):
                        st.markdown(f"**{card['title']}**")
                        if card.get("description"):
                            st.caption(card["description"])
                        bc = st.columns([1, 1, 1])
                        if bc[0].button("⬅", key=f"l_{i}_{j}", use_container_width=True):
                            move_card(i, j, "left")
                        if bc[1].button("🗑", key=f"d_{i}_{j}", use_container_width=True):
                            delete_card(i, j)
                        if bc[2].button("➡", key=f"r_{i}_{j}", use_container_width=True):
                            move_card(i, j, "right")


# ---------------------------------------------------------------------------
# Sidebar: gestión
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Gestión del tablero")

    with st.expander("➕ Nueva columna"):
        with st.form("add_col", clear_on_submit=True):
            title = st.text_input("Nombre de la columna")
            color = st.color_picker("Color", "#4F8DF7")
            if st.form_submit_button("Crear columna"):
                if title.strip():
                    st.session_state.board.append({
                        "id": f"col_{uuid.uuid4().hex[:8]}",
                        "title": title.strip(),
                        "color": color,
                        "cards": [],
                    })
                    save_state(st.session_state.board)
                    st.rerun()

    with st.expander("📝 Nueva ficha"):
        col_titles = [c["title"] for c in st.session_state.board]
        if col_titles:
            with st.form("add_card", clear_on_submit=True):
                ct = st.text_input("Título")
                cd = st.text_area("Descripción (opcional)")
                tgt = st.selectbox("Columna destino", col_titles)
                if st.form_submit_button("Agregar ficha"):
                    if ct.strip():
                        for c in st.session_state.board:
                            if c["title"] == tgt:
                                c["cards"].append({
                                    "id": f"card_{uuid.uuid4().hex[:8]}",
                                    "title": ct.strip(),
                                    "description": cd.strip(),
                                })
                                break
                        save_state(st.session_state.board)
                        st.rerun()
        else:
            st.info("Crea primero una columna.")

    with st.expander("🗑️ Eliminar columna"):
        col_titles = [c["title"] for c in st.session_state.board]
        if col_titles:
            del_col = st.selectbox("Columna a eliminar", col_titles, key="del_col_select")
            if st.button("Eliminar definitivamente", type="primary"):
                st.session_state.board = [
                    c for c in st.session_state.board if c["title"] != del_col
                ]
                save_state(st.session_state.board)
                st.rerun()
        else:
            st.info("No hay columnas.")

    st.divider()
    st.markdown(
        "**💡 Tip:** Cada ficha tiene botones ⬅ / ➡ para moverse entre columnas. "
        "La posición se guarda automáticamente."
    )
