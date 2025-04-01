import streamlit as st
import streamlit.components.v1 as components

d3_html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      background-color: #262123;
      overflow: hidden;
    }
    svg {
      position: absolute;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 1;
      display: block;
      background-color: #262123;
    }
    .node {
      fill: #4C4646;
      cursor: pointer;
    }
    .link {
      stroke: #4C4646;
      stroke-opacity: 0.6;
    }
    .popup {
      position: absolute;
      background-color: #4C4646;
      color: #E8DED3;
      padding: 10px;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.5);
      font-family: sans-serif;
      z-index: 10;
      width: 200px;
      text-align: center;
    }
    .popup img {
      max-width: 100%;
      border-radius: 5px;
      margin-top: 8px;
    }
  </style>
</head>
<body>
<svg></svg>
<div id="popup" class="popup" style="display:none;"></div>

<script>
const nodes = [
  {id: "A"}, {id: "B"}, {id: "C"}
];

const links = [
  {source: "A", target: "B"},
  {source: "A", target: "C"}
];

// Устанавливаем размеры SVG как переменные
const screenWidth = window.innerWidth;
const screenHeight = window.innerHeight;

const svg = d3.select("svg")
  .attr("width", screenWidth)
  .attr("height", screenHeight);

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(screenWidth / 2, screenHeight / 2));

const link = svg.append("g")
  .selectAll("line")
  .data(links)
  .enter().append("line")
  .attr("class", "link");

const node = svg.append("g")
  .selectAll("circle")
  .data(nodes)
  .enter().append("circle")
  .attr("r", 10)
  .attr("class", "node")
  .call(drag(simulation))
  .on("click", onNodeClick);

node.append("title").text(d => d.id);

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

function drag(simulation) {
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
}

function onNodeClick(event, clickedNode) {
  // Reset node size
  node.transition().duration(200).attr("r", 10);
  link.style("stroke", "#4C4646");

  // Highlight clicked node and links
  d3.select(this).transition().duration(200).attr("r", 14);
  link.filter(d => d.source.id === clickedNode.id || d.target.id === clickedNode.id)
      .style("stroke", "#6A50FF");

  // Show popup near the node
  const popup = document.getElementById("popup");
  popup.innerHTML = `
    <strong>Имя художника</strong><br>
    <img src="https://drive.google.com/thumbnail?id=1nPGiD8aYWj-15cGEJXL0LDYGyMImK04b">
  `;
  popup.style.left = (event.pageX + 20) + "px";
  popup.style.top = (event.pageY - 20) + "px";
  popup.style.display = "block";
}
</script>
</body>
</html>
"""

components.html(d3_html, height=1000)
