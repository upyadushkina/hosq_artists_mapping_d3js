import streamlit as st
import streamlit.components.v1 as components

# HTML + D3.js код
d3_html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    .node { fill: #69b3a2; cursor: pointer; }
    .link { stroke: #999; stroke-opacity: 0.6; }
  </style>
</head>
<body>
<svg width="600" height="400"></svg>

<script>
const nodes = [
  {id: "A"}, {id: "B"}, {id: "C"}
];

const links = [
  {source: "A", target: "B"},
  {source: "A", target: "C"}
];

const svg = d3.select("svg"),
      width = +svg.attr("width"),
      height = +svg.attr("height");

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
    .attr("stroke", "#aaa")
  .selectAll("line")
  .data(links)
  .enter().append("line")
    .attr("class", "link");

const node = svg.append("g")
  .selectAll("circle")
  .data(nodes)
  .enter().append("circle")
    .attr("r", 10)
    .attr("fill", "#69b3a2")
    .call(drag(simulation));

node.append("title")
    .text(d => d.id);

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
</script>
</body>
</html>
"""

components.html(d3_html, height=450)
