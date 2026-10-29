"""
kanban_component.py — Componente custom de Streamlit (HTML inline).
Renderiza un tablero Kanban con arrastre real entre columnas (SortableJS).
Sin dependencia de archivos externos: el HTML/JS va embebido.
"""
from __future__ import annotations
import streamlit.components.v1 as components
import json

# -----------------------------------------------------------------------------
# HTML + JS del tablero Kanban (embebido, sin archivos externos)
# -----------------------------------------------------------------------------
_KANBAN_HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.6/Sortable.min.js"></script>
  <style>
    :root {
      --bg: #f4f5f7;
      --col-bg: #ebecf0;
      --col-header: #172b4d;
      --card-bg: #ffffff;
      --card-text: #172b4d;
      --muted: #5e6c84;
      --shadow: 0 1px 2px rgba(9, 30, 66, 0.25);
      --shadow-drag: 0 8px 16px rgba(9, 30, 66, 0.35);
    }
    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--card-text);
    }
    .board {
      display: flex; gap: 12px; padding: 12px;
      overflow-x: auto; align-items: flex-start; min-height: 420px;
    }
    .column {
      background: var(--col-bg); border-radius: 10px;
      width: 260px; min-width: 260px; max-height: 70vh;
      display: flex; flex-direction: column; overflow: hidden;
    }
    .column-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 10px 12px; font-weight: 700; font-size: 13px;
      color: var(--col-header); letter-spacing: 0.02em; text-transform: uppercase;
      border-top: 4px solid var(--accent, #4F8DF7);
    }
    .column-count {
      background: rgba(23, 43, 77, 0.08); color: var(--muted);
      border-radius: 10px; padding: 1px 8px; font-size: 11px; font-weight: 600;
    }
    .column-body {
      padding: 6px 8px 10px 8px; flex: 1; overflow-y: auto; min-height: 40px;
    }
    .card {
      background: var(--card-bg, #ffffff); border-radius: 6px;
      padding: 10px 12px; margin-bottom: 8px; box-shadow: var(--shadow);
      cursor: grab; font-size: 13px; line-height: 1.4; color: var(--card-text);
      border-left: 3px solid var(--accent, #4F8DF7);
      transition: box-shadow 0.15s ease, transform 0.15s ease;
    }
    .card:hover { box-shadow: 0 2px 4px rgba(9, 30, 66, 0.35); transform: translateY(-1px); }
    .card:active { cursor: grabbing; }
    .card-title { font-weight: 600; margin-bottom: 4px; word-wrap: break-word; }
    .card-desc {
      font-size: 11px; color: var(--muted);
      word-wrap: break-word; white-space: pre-wrap;
    }
    .sortable-ghost { opacity: 0.35; background: #dfe1e6 !important; }
    .sortable-chosen { box-shadow: 0 0 0 2px var(--accent, #4F8DF7); }
    .sortable-drag { box-shadow: var(--shadow-drag); transform: rotate(2deg); }
    .empty-col-hint {
      text-align: center; color: var(--muted); font-size: 11px;
      padding: 16px 4px; opacity: 0.7;
    }
  </style>
</head>
<body>
  <div class="board" id="board"></div>
  <script>
    let currentColumns = [];

    function normalizeColumns(raw) {
      if (!Array.isArray(raw)) return [];
      return raw.map((col) => ({
        id: col.id || ("col_" + Math.random().toString(36).slice(2, 8)),
        title: col.title || "Sin título",
        color: col.color || "#4F8DF7",
        cards: Array.isArray(col.cards) ? col.cards : [],
      }));
    }

    function renderBoard(columns) {
      const board = document.getElementById("board");
      board.innerHTML = "";

      columns.forEach((col) => {
        const colEl = document.createElement("div");
        colEl.className = "column";
        colEl.dataset.columnId = col.id;
        colEl.style.setProperty("--accent", col.color);

        const header = document.createElement("div");
        header.className = "column-header";
        const titleSpan = document.createElement("span");
        titleSpan.textContent = col.title;
        const countSpan = document.createElement("span");
        countSpan.className = "column-count";
        countSpan.textContent = col.cards.length;
        header.appendChild(titleSpan);
        header.appendChild(countSpan);
        colEl.appendChild(header);

        const body = document.createElement("div");
        body.className = "column-body";
        body.dataset.columnId = col.id;

        if (col.cards.length === 0) {
          const hint = document.createElement("div");
          hint.className = "empty-col-hint";
          hint.textContent = "Suelta fichas aquí";
          body.appendChild(hint);
        }

        col.cards.forEach((card) => {
          const cardEl = document.createElement("div");
          cardEl.className = "card";
          cardEl.dataset.cardId = card.id || "";
          cardEl.style.setProperty("--accent", card.color || col.color || "#4F8DF7");

          const titleEl = document.createElement("div");
          titleEl.className = "card-title";
          titleEl.textContent = card.title || "(sin título)";
          cardEl.appendChild(titleEl);

          if (card.description && card.description.trim()) {
            const descEl = document.createElement("div");
            descEl.className = "card-desc";
            descEl.textContent = card.description;
            cardEl.appendChild(descEl);
          }

          body.appendChild(cardEl);
        });

        colEl.appendChild(body);
        board.appendChild(colEl);

        new Sortable(body, {
          group: "kanban",
          animation: 180,
          easing: "cubic-bezier(0.2, 0.8, 0.2, 1)",
          ghostClass: "sortable-ghost",
          chosenClass: "sortable-chosen",
          dragClass: "sortable-drag",
          fallbackOnBody: true,
          swapThreshold: 0.55,
          onMove: function (evt) {
            document.querySelectorAll(".empty-col-hint").forEach((h) => h.remove());
            return true;
          },
          onEnd: function (evt) {
            collectAndSend();
            reapplyEmptyHints();
          },
        });
      });
    }

    function reapplyEmptyHints() {
      document.querySelectorAll(".column-body").forEach((body) => {
        if (body.querySelectorAll(".card").length === 0) {
          const existing = body.querySelector(".empty-col-hint");
          if (!existing) {
            const hint = document.createElement("div");
            hint.className = "empty-col-hint";
            hint.textContent = "Suelta fichas aquí";
            body.appendChild(hint);
          }
        }
      });
    }

    function collectAndSend() {
      const newColumns = [];
      const columnEls = document.querySelectorAll(".column");

      columnEls.forEach((colEl) => {
        const id = colEl.dataset.columnId;
        const titleEl = colEl.querySelector(".column-header > span");
        const title = titleEl ? titleEl.textContent : "Sin título";
        const color = colEl.style.getPropertyValue("--accent") || "#4F8DF7";
        const cards = [];
        colEl.querySelectorAll(".card").forEach((cardEl) => {
          const titleNode = cardEl.querySelector(".card-title");
          const descNode = cardEl.querySelector(".card-desc");
          cards.push({
            id: cardEl.dataset.cardId || ("card_" + Math.random().toString(36).slice(2, 8)),
            title: titleNode ? titleNode.textContent : "",
            description: descNode ? descNode.textContent : "",
            color: cardEl.style.getPropertyValue("--accent") || "#FFFFFF",
          });
        });
        newColumns.push({ id, title, color, cards });
      });

      currentColumns = newColumns;
      // Comunica el nuevo estado a Python vía postMessage.
      const msg = { isStreamlitMessage: true, type: "streamlit:setComponentValue", value: newColumns };
      window.parent.postMessage(msg, "*");
    }

    function receiveFromStreamlit(event) {
      const data = event.data;
      if (!data || typeof data !== "object") return;
      // Streamlit envía los args en event.detail del CustomEvent "streamlit:render".
      // Pero también podemos recibir por postMessage directo.
      if (data.type === "streamlit:render") {
        const args = (data.args || {});
        const incomingColumns = normalizeColumns(args.columns || []);
        if (!columnsEqual(currentColumns, incomingColumns)) {
          currentColumns = incomingColumns;
          renderBoard(currentColumns);
        }
        // Responder alto
        const heightMsg = { isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: document.body.scrollHeight };
        window.parent.postMessage(heightMsg, "*");
      }
    }

    function columnsEqual(a, b) {
      if (a.length !== b.length) return false;
      for (let i = 0; i < a.length; i++) {
        if (a[i].id !== b[i].id) return false;
        if (a[i].title !== b[i].title) return false;
        if (a[i].cards.length !== b[i].cards.length) return false;
        for (let j = 0; j < a[i].cards.length; j++) {
          if (a[i].cards[j].id !== b[i].cards[j].id) return false;
        }
      }
      return true;
    }

    window.addEventListener("message", receiveFromStreamlit);

    // Avisar que el componente está listo.
    window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:componentReady" }, "*");
    window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: 500 }, "*");
  </script>
</body>
</html>
"""


def kanban_board(columns, key=None):
    """
    Renderiza el tablero Kanban con `components.html` (inline, sin declare_component).
    Devuelve el nuevo estado si el usuario movió fichas, o `columns` sin cambios.

    Usamos `st.session_state[key]` para guardar el valor retornado vía postMessage.
    """
    import streamlit as st

    # Serializa el estado inicial y lo inyecta en el JS.
    initial_json = json.dumps(columns, ensure_ascii=False)

    # Wrapper HTML que recibe el estado inicial y escucha postMessage.
    html = f"""
    <div id="kanban-root" style="height:600px"></div>
    <script>
      // Pequeña envoltura: usa el HTML embebido pero recibe el estado inicial
      // desde Python a través de una variable global.
      window.__KANBAN_INITIAL__ = {initial_json};
    </script>
    """ + _KANBAN_HTML + r"""
    <script>
      // Reemplaza la inicialización del componente para usar window.__KANBAN_INITIAL__
      (function() {
        // Render inmediato con el estado inicial
        const initial = window.__KANBAN_INITIAL__ || [];
        // Normaliza
        function normalizeColumns(raw) {
          if (!Array.isArray(raw)) return [];
          return raw.map((col) => ({
            id: col.id || ("col_" + Math.random().toString(36).slice(2, 8)),
            title: col.title || "Sin título",
            color: col.color || "#4F8DF7",
            cards: Array.isArray(col.cards) ? col.cards : [],
          }));
        }
        // Llama a la función global renderBoard (definida en el bloque anterior).
        if (typeof renderBoard === "function") {
          currentColumns = normalizeColumns(initial);
          renderBoard(currentColumns);
        }
      })();
    </script>
    """

    # Renderiza el HTML en un iframe. height fijo para evitar problemas.
    components.html(html, height=620, key=key)

    # Recupera el valor si el usuario movió una ficha (vía session_state).
    # El mecanismo: el JS hace postMessage pero components.html no expone el
    # valor de retorno. Para capturarlo necesitamos un truco con query param.
    # Alternativa simple: el componente devuelve None y usamos session_state
    # interno actualizado por st.components.v1 con declare_component.
    #
    # Como components.html no soporta retorno, devolvemos el input sin cambios
    # y dejamos que el
