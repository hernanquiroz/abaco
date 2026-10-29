"""
01_app.py — Punto de entrada principal de la aplicación Streamlit
Tablero Kanban interactivo con drag-and-drop entre columnas ("mástiles").
"""

from __future__ import annotations

import uuid
import streamlit as st

from kanban_component import kanban_board
from state import init_state, save_state, reset_state, export_json, import_json


st.set_page_config(
    page_title="Tablero Kanban",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


if "board" not in st.session_state:
    st.session_state.board = init_state()

if "component_nonce" not in st.session_state:
    st.session_state.component_nonce = 0


st.title("📋 Tablero Kanban Interactivo")
st.caption("Arrastra las fichas entre las columnas — la posición se guarda automáticamente.")

toolbar_cols = st.columns([1, 1, 1, 1, 4])

with toolbar_cols[0]:
    if st.button("💾 Guardar", use_container_width=True):
        save_state(st.session_state.board)
        st.toast("Estado guardado en disco.", icon="✅")

with toolbar_cols[1]:
    if st.button("🗑️ Reiniciar", use_container_width=True):
        st.session_state.board = reset_state()
        st.session_state.component_nonce += 1
        st.rerun()

with toolbar_cols[2]:
    st.download_button(
        label="⬇️ Exportar JSON",
        data=export_json(st.session_state.board),
        file_name="kanban_backup.json",
        mime="application/json",
        use_container_width=True,
    )

with toolbar_cols[3]:
    uploaded = st.file_uploader("⬆️ Importar", type=["json"], label_visibility="collapsed")
    if uploaded is not None:
        try:
            new_board = import_json(uploaded)
            st.session_state.board = new_board
            st.session_state.component_nonce += 1
            st.toast("Tablero importado.", icon="✅")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo importar el archivo: {exc}")


new_state = kanban_board(
    columns=st.session_state.board,
    key=f"kanban_{st.session_state.component_nonce}",
)

if new_state is not None and new_state != st.session_state.board:
    st.session_state.board = new_state
    save_state(new_state)


with st.sidebar:
    st.header("⚙️ Gestión del tablero")

    with st.expander("➕ Nueva columna", expanded=False):
        with st.form("add_column", clear_on_submit=True):
            new_col_title = st.text_input("Nombre de la columna")
            new_col_color = st.color_picker("Color de acento", "#4F8DF7")
            if st.form_submit_button("Crear columna"):
                if new_col_title.strip():
                    st.session_state.board.append(
                        {
                            "id": f"col_{uuid.uuid4().hex[:8]}",
                            "title": new_col_title.strip(),
                            "color": new_col_color,
                            "cards": [],
                        }
                    )
                    st.session_state.component_nonce += 1
                    save_state(st.session_state.board)
                    st.rerun()

    with st.expander("📝 Nueva ficha", expanded=True):
        col_titles = [c["title"] for c in st.session_state.board]
        if not col_titles:
            st.info("Primero crea al menos una columna.")
        else:
            with st.form("add_card", clear_on_submit=True):
                card_title = st.text_input("Título de la ficha")
                card_desc = st.text_area("Descripción (opcional)", height=80)
                card_color = st.color_picker("Color de la ficha", "#FFFFFF")
                target_col = st.selectbox("Columna destino", col_titles)
                if st.form_submit_button("Agregar ficha"):
                    if card_title.strip():
                        new_card = {
                            "id": f"card_{uuid.uuid4().hex[:8]}",
                            "title": card_title.strip(),
                            "description": card_desc.strip(),
                            "color": card_color,
                        }
                        for col in st.session_state.board:
                            if col["title"] == target_col:
                                col["cards"].append(new_card)
                                break
                        st.session_state.component_nonce += 1
                        save_state(st.session_state.board)
                        st.rerun()

    with st.expander("🗑️ Eliminar columna", expanded=False):
        col_titles = [c["title"] for c in st.session_state.board]
        if col_titles:
            col_to_delete = st.selectbox("Columna a eliminar", col_titles)
            if st.button("Eliminar definitivamente", type="primary"):
                st.session_state.board = [
                    c for c in st.session_state.board if c["title"] != col_to_delete
                ]
                st.session_state.component_nonce += 1
                save_state(st.session_state.board)
                st.rerun()
        else:
            st.info("No hay columnas para eliminar.")

    st.divider()
    st.markdown(
        "**💡 Tip:** Arrastra cualquier ficha desde una columna hacia otra. "
        "El cambio se guarda automáticamente en `kanban_data.json`."
    )


st.divider()
st.caption(
    "Hecho con Streamlit + SortableJS · Despliegue en Streamlit Cloud · "
    "Estructura modular lista para GitHub."
)
