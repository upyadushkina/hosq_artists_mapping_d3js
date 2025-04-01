import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from collections import defaultdict
import base64

# === Color Scheme ===
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

def get_google_drive_image_url(url):
    if "drive.google.com" in url and "/d/" in url:
        file_id = url.split("/d/")[1].split("/")[0]
        return f"https://drive.google.com/thumbnail?id={file_id}"
    return url

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

# Load and process CSV
df = pd.read_csv("Etudes Lab 1 artistis d3js.csv")
df.fillna('', inplace=True)

category_colors = {
    'artist': NODE_NAME_COLOR,
    'city': NODE_CITY_COLOR,
    'country': NODE_CITY_COLOR,
    'professional field': NODE_FIELD_COLOR,
    'role': NODE_ROLE_COLOR,
    'style': PAGE_TEXT_COLOR,
    'tool': PAGE_TEXT_COLOR,
    'level': PAGE_TEXT_COLOR,
    'seeking for': PAGE_TEXT_COLOR,
}

multi_fields = ['professional field', 'role', 'style', 'tool', 'level', 'seeking for']
nodes, links, artist_info = [], [], {}
node_ids, edge_ids = set(), set()
filter_options = defaultdict(set)

def add_node(id, label, group):
    if id not in node_ids:
        nodes.append({"id": id, "label": label, "group": group, "color": category_colors.get(group, '#888888')})
        node_ids.add(id)

def add_link(source, target):
    key = f"{source}___{target}"
    if key not in edge_ids:
        links.append({"source": source, "target": target})
        edge_ids.add(key)

for _, row in df.iterrows():
    artist_id = f"artist::{row['name']}"
    add_node(artist_id, row['name'], 'artist')

    photo_url = get_google_drive_image_url(row['photo url']) if row['photo url'] else DEFAULT_PHOTO

    artist_info[artist_id] = {
        "name": row['name'],
        "photo": photo_url,
        "telegram": row['telegram nickname'],
        "email": row['email']
    }

    for field in multi_fields:
        values = [v.strip() for v in row[field].split(',')] if row[field] else []
        for val in values:
            if val:
                node_id = f"{field}::{val}"
                add_node(node_id, val, field)
                add_link(artist_id, node_id)
                filter_options[field].add(val)

    if row['country and city']:
        parts = [p.strip() for p in row['country and city'].split(',')]
        if len(parts) == 2:
            country, city = parts
            country_id = f"country::{country}"
            city_id = f"city::{city}"
            add_node(country_id, country, 'country')
            add_node(city_id, city, 'city')
            add_link(artist_id, city_id)
            add_link(city_id, country_id)
            filter_options['country'].add(country)
            filter_options['city'].add(city)

# Sidebar filters
selected = {}
st.sidebar.header("Filters")
for category, options in filter_options.items():
    selected[category] = st.sidebar.multiselect(
        label=category.title(),
        options=sorted(options),
        default=[]
    )

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

d3_data = {
    "nodes": visible_nodes,
    "links": visible_links,
    "artists": artist_info
}

d3_json = json.dumps(d3_data)
b64_data = base64.b64encode(d3_json.encode("utf-8")).decode("utf-8")

html_template = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <script src='https://d3js.org/d3.v7.min.js'></script>
  <link href='https://fonts.googleapis.com/css2?family=Lexend&display=swap' rel='stylesheet'>
  <style>
    html, body {{
      margin: 0; padding: 0; height: 100%; background: {GRAPH_BG_COLOR};
      overflow: hidden;
    }}
    svg {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 1;
    }}
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
<div id='popup' class='popup' style='display:none;'></div>
<script>
const data = JSON.parse(atob('{b64_data}'));

const svg = d3.select("svg");
const width = window.innerWidth;
const height = window.innerHeight;

const simulation = d3.forceSimulation(data.nodes)
  .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2));

const drag = simulation => {
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
  return d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended);
};

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
  .call(drag(simulation))
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
  popup.style.left = (event.clientX + 20) + "px";
  popup.style.top = (event.clientY + 20) + "px";
  popup.style.display = "block";
}
</script>
</body>
</html>
"""

components.html(html_template, height=1000, scrolling=False)
