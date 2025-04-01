import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

# === Цветовая схема ===
PAGE_BG_COLOR = "#262123"
PAGE_TEXT_COLOR = "#E8DED3"
SIDEBAR_BG_COLOR = "#262123"
SIDEBAR_LABEL_COLOR = "#E8DED3"
SIDEBAR_TAG_TEXT_COLOR = "#E8DED3"
SIDEBAR_TAG_BG_COLOR = "#6A50FF"
BUTTON_BG_COLOR = "#262123"
BUTTON_TEXT_COLOR = "#4C4646"
BUTTON_CLEAN_TEXT_COLOR = "#E8DED3"
SIDEBAR_HEADER_COLOR = "#E8DED3"
SIDEBAR_TOGGLE_ARROW_COLOR = "#E8DED3"
HEADER_MENU_COLOR = "#262123"
GRAPH_BG_COLOR = "#262123"
GRAPH_LABEL_COLOR = "#E8DED3"
NODE_NAME_COLOR = "#4C4646"
NODE_CITY_COLOR = "#D3DAE8"
NODE_FIELD_COLOR = "#EEC0E7"
NODE_ROLE_COLOR = "#F4C07C"
EDGE_COLOR = "#4C4646"
HIGHLIGHT_EDGE_COLOR = "#6A50FF"
TEXT_FONT = "Lexend"
DEFAULT_PHOTO = "https://static.tildacdn.com/tild3532-6664-4163-b538-663866613835/hosq-design-NEW.png"

# === Настройка страницы ===
st.set_page_config(page_title="HOSQ Artist Graph", layout="wide")
st.markdown(f"""
    <style>
    html, body, .stApp, main, section {{
        background-color: {PAGE_BG_COLOR} !important;
        color: {PAGE_TEXT_COLOR} !important;
        font-family: '{TEXT_FONT}', sans-serif;
    }}
    header, footer {{
        background-color: {PAGE_BG_COLOR} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# === Загрузка графа ===
with open("graph_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
links = data["links"]
artists = data["artists"]
filters = data["filters"]

# === Фильтры ===
selected = {}
st.sidebar.header("Фильтры")
for category, options in filters.items():
    selected[category] = st.sidebar.multiselect(
        label=category.title(),
        options=options,
        default=[]
    )

# === Фильтрация узлов ===
def node_passes_filter(node_id):
    if not node_id.startswith("artist::"):
        return True
    for cat, selected_vals in selected.items():
        if not selected_vals:
            continue
        artist_links = [l["target"] for l in links if l["source"] == node_id]
        relevant = [f"{cat}::{val}" for val in selected_vals]
        if not any(val in artist_links for val in relevant):
            return False
    return True

visible_nodes = [n for n in nodes if node_passes_filter(n["id"])]
visible_node_ids = set(n["id"] for n in visible_nodes)
visible_links = [l for l in links if l["source"] in visible_node_ids and l["target"] in visible_node_ids]

# === Подготовка данных для D3 ===
d3_data = {
    "nodes": visible_nodes,
    "links": visible_links,
    "artists": artists
}

# === Вставка графа ===
components.html(f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Lexend&display=swap" rel="stylesheet">
  <style>
    html, body {{ margin: 0; padding: 0; height: 100%; background: {GRAPH_BG_COLOR}; }}
    svg {{ width: 100vw; height: 100vh; }}
    .node {{ cursor: pointer; }}
    .popup {{
      position: absolute;
      background-color: {GRAPH_BG_COLOR};
      color: {PAGE_TEXT_COLOR};
      padding: 10px;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
      font-family: 'Lexend', sans-serif;
      z-index: 10;
      width: 220px;
      text-align: center;
    }}
    .popup img {{
      max-width: 100%;
      border-radius: 5px;
      margin-top: 8px;
    }}
  </style>
</head>
<body>
<svg></svg>
<div id="popup" class="popup" style="display:none;"></div>
<script>
const data = {json.dumps(d3_data)};
const svg = d3.select("svg");
const width = window.innerWidth;
const height = window.innerHeight;

const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
  .selectAll("line")
  .data(data.links)
  .enter().append("line")
  .attr("stroke", "{EDGE_COLOR}");

const node = svg.append("g")
  .selectAll("circle")
  .data(data.nodes)
  .enter().append("circle")
  .attr("r", 10)
  .attr("fill", d => d.color)
  .attr("class", "node")
  .on("click", onClick);

simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);
});

function onClick(event, d) {
  if (!d.id.startsWith("artist::")) return;
  const artist = data.artists[d.id];
  const popup = document.getElementById("popup");
  popup.innerHTML = `
    <strong>${artist.name}</strong><br>
    <img src="${artist.photo}" alt="photo"><br>
    ${artist.telegram ? `<div>📱 ${artist.telegram}</div>` : ''}
    ${artist.email ? `<div>✉️ ${artist.email}</div>` : ''}
  `;
  popup.style.left = (event.pageX + 20) + "px";
  popup.style.top = (event.pageY - 20) + "px";
  popup.style.display = "block";
}
</script>
</body>
</html>
""", height=1000, scrolling=False)
