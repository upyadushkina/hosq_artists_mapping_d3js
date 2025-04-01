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

POPUP_BG_COLOR = "#E8DED3"  # background color for popup
POPUP_TEXT_COLOR = "#262123"  # text color for popup


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
    'artist': "#4C4646",
    'city': "#B1D3AA",
    'country': "#B1D3AA",
    'professional field': "#B3A0EB",
    'role': "#F4C07C",
    'style': "#EEC0E7",
    'tool': "#E8DED3",
    'level': "#EC7F4D",
    'seeking for': "#D3DAE8",
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

with open("graph_template.html", "r", encoding="utf-8") as f:
    html_template = f.read()

html_filled = html_template.replace("{{ b64_data }}", b64_data)
html_filled = html_filled.replace("{{ popup_bg }}", POPUP_BG_COLOR)
html_filled = html_filled.replace("{{ popup_text }}", POPUP_TEXT_COLOR)

components.html(html_filled, height=1400, scrolling=False)
