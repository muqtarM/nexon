const envList = document.getElementById('env-list');
const pkgList = document.getElementById('pkg-list');
const reqInput = document.getElementById('req-input');
const graphBtn = document.getElementById('graph-btn');
const svg = d3.select('#graph-svg');
const width = +svg.attr('width') || svg.node().clientWidth;
const height = +svg.attr('height') || svg.node().clientHeight;

// Fetch & render environments
fetch('/api/envs/').then(r=>r.json()).then(data=>{
  envList.innerHTML = data.map(e=>`<li>${e.name} (${e.role})</li>`).join('');
});

// Fetch & render packages
fetch('/api/packages/').then(r=>r.json()).then(data=>{
  pkgList.innerHTML = data.map(p=>`<li>${p.name}: ${p.versions.join(', ')}</li>`).join('');
});

// Build & render dependency graph
graphBtn.addEventListener('click', async () => {
  const req = reqInput.value.trim();
  if (!req) return;
  const resp = await fetch('/api/graph/', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({requirements:[req]})
  });
  const graph = await resp.json();
  renderGraph(graph);
});

function renderGraph(graph) {
  // transform into D3-friendly nodes & links
  const nodes = Object.keys(graph).map(id=>({id}));
  const links = [];
  for (const [src, deps] of Object.entries(graph)) {
    deps.forEach(dst=>links.push({source: src, target: dst}));
  }

  svg.selectAll('*').remove();
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width/2, height/2));

  const link = svg.append('g')
      .attr('stroke', '#999')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke-width', 2);

  const node = svg.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
    .selectAll('circle')
    .data(nodes)
    .join('circle')
      .attr('r', 12)
      .attr('fill', '#4A90E2')
      .call(drag(simulation));

  const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('dy', 4)
      .text(d=>d.id)
      .style('font-size', '10px')
      .style('pointer-events', 'none');

  simulation.on('tick', () => {
    link
      .attr('x1', d=>d.source.x)
      .attr('y1', d=>d.source.y)
      .attr('x2', d=>d.target.x)
      .attr('y2', d=>d.target.y);
    node
      .attr('cx', d=>d.x)
      .attr('cy', d=>d.y);
    label
      .attr('x', d=>d.x)
      .attr('y', d=>d.y);
  });

  function drag(sim) {
    function started(event, d) {
      if (!event.active) sim.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    }
    function dragged(event, d) {
      d.fx = event.x; d.fy = event.y;
    }
    function ended(event, d) {
      if (!event.active) sim.alphaTarget(0);
      d.fx = null; d.fy = null;
    }
    return d3.drag()
      .on('start', started)
      .on('drag', dragged)
      .on('end', ended);
  }
}
