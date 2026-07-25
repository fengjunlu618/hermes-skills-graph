#!/usr/bin/env python3
"""Build D3 force-directed knowledge graph HTML for Hermes skills."""
import json
from pathlib import Path

SKILLS_GRAPH_DIR = Path.home() / ".hermes" / "skills-graph"
DATA = SKILLS_GRAPH_DIR / "skills_graph.json"
OUTPUT = SKILLS_GRAPH_DIR / "skills_knowledge_graph.html"

data = json.loads(DATA.read_text())

# Build data structures
d3_nodes = []
d3_links = []
cat_list = sorted({n.get('category', '未分类') for n in data['nodes'] if n['type'] == 'skill'})
cat_size = {}
for n in data['nodes']:
    if n['type'] == 'skill':
        c = n.get('category', '未分类')
        cat_size[c] = cat_size.get(c, 0) + 1

cat_color_list = [
    "#8b5cf6", "#ec4899", "#f59e0b", "#10b981", "#3b82f6",
    "#ef4444", "#14b8a6", "#f97316", "#6366f1", "#84cc16",
    "#06b6d4", "#d946ef", "#eab308", "#22c55e", "#a855f7",
    "#f43f5e", "#0ea5e9", "#64748b", "#7c3aed", "#d97706",
    "#0891b2", "#059669", "#9333ea", "#0f766e", "#b45309",
    "#2563eb", "#be123c", "#4f46e5", "#65a30d", "#0d9488"
]
cat_color = {c: cat_color_list[i % len(cat_color_list)] for i, c in enumerate(cat_list)}

for cat in cat_list:
    d3_nodes.append({"id": "cat:" + cat, "name": cat, "type": "category", "count": cat_size.get(cat, 1), "color": cat_color[cat]})

skill_cats = {}
for n in data['nodes']:
    if n['type'] == 'skill':
        sid, cat = n['id'], n.get('category', '未分类')
        skill_cats[sid] = cat
        d3_nodes.append({"id": sid, "name": sid, "type": "skill", "category": cat, "color": cat_color.get(cat, "#64748b"), "desc": n.get('description', '')})
        d3_links.append({"source": sid, "target": "cat:" + cat, "type": "belongs_to"})

seen_pairs = set()
for e in data['edges']:
    if 'shared_tag' in e.get('relation', ''):
        pair = tuple(sorted([e['source'], e['target']]))
        if pair not in seen_pairs:
            seen_pairs.add(pair)
            d3_links.append({"source": pair[0], "target": pair[1], "type": "shared_tag"})

js_graph = json.dumps({"nodes": d3_nodes, "links": d3_links}, ensure_ascii=False)
skill_count = len([n for n in d3_nodes if n['type'] == 'skill'])
cat_count = len(cat_list)
link_count = len(d3_links)

# Write HTML without f-string (to avoid JS curly brace conflicts)
html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hermes Skills 知识图谱</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a1a;color:#e0e0e0;overflow:hidden;height:100vh}
#header{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(10,10,26,0.92);backdrop-filter:blur(12px);padding:12px 24px;border-bottom:1px solid #1e1e3a;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
#header h1{font-size:1.2rem;color:#8b5cf6;font-weight:600}
#header .stats{font-size:0.8rem;color:#666}
#search{flex:1;min-width:150px;max-width:300px;background:#1a1a2e;border:1px solid #2a2a4a;border-radius:6px;padding:6px 12px;color:#e0e0e0;font-size:0.85rem;outline:none}
#search:focus{border-color:#8b5cf6}
svg{width:100vw;height:100vh;display:block}
.link{stroke-opacity:0.15}
.link.belongs_to{stroke:#8b5cf6;stroke-dasharray:3,3;stroke-width:0.5}
.link.shared_tag{stroke:#ff6b9d;stroke-width:0.4}
.node text{font-size:8px;fill:#ccc;pointer-events:none;text-shadow:0 1px 2px rgba(0,0,0,0.8)}
.node.category text{font-size:11px;font-weight:bold;fill:#fff}
.node.skill{cursor:pointer}
.node.skill:hover circle{stroke:#fff;stroke-width:2}
#tooltip{position:fixed;display:none;background:#1a1a2e;border:1px solid #3a3a5a;border-radius:8px;padding:12px 16px;font-size:0.8rem;max-width:300px;z-index:200;box-shadow:0 8px 24px rgba(0,0,0,0.4);pointer-events:none}
#tooltip .name{color:#c4b5fd;font-weight:600;font-size:0.9rem;margin-bottom:4px}
#tooltip .detail{color:#888;font-size:0.75rem}
#tooltip .desc{color:#aaa;margin-top:4px;font-size:0.75rem}
#legend{position:fixed;bottom:20px;right:20px;background:rgba(26,26,46,0.9);backdrop-filter:blur(8px);border:1px solid #2a2a4a;border-radius:8px;padding:12px;max-height:60vh;overflow-y:auto;min-width:180px;z-index:100}
#legend h3{font-size:0.75rem;color:#8b5cf6;margin-bottom:6px}
.legend-item{display:flex;align-items:center;gap:6px;padding:2px 0;font-size:0.7rem;color:#888;cursor:pointer}
.legend-item .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.legend-item .count{color:#555;margin-left:auto;font-size:0.65rem}
.legend-item:hover{color:#fff}
.controls{position:fixed;bottom:20px;left:20px;z-index:100;display:flex;gap:6px}
.controls button{background:rgba(26,26,46,0.85);border:1px solid #3a3a5a;color:#ccc;padding:6px 12px;border-radius:6px;font-size:0.75rem;cursor:pointer}
.controls button:hover{background:#2a2a4a;color:#fff;border-color:#8b5cf6}
#detail-panel{position:fixed;top:60px;right:20px;z-index:100;background:rgba(26,26,46,0.92);border:1px solid #3a3a5a;border-radius:8px;padding:12px;max-width:280px;display:none}
#detail-panel .title{color:#c4b5fd;font-weight:600;margin-bottom:4px}
#detail-panel .body{color:#aaa;font-size:0.75rem}
</style>
</head>
<body>
<div id="header">
  <h1>Hermes Skills 知识图谱</h1>
  <span class="stats">__SKILL_COUNT__ skills __CAT_COUNT__ categories __LINK_COUNT__ relations</span>
  <input id="search" type="text" placeholder="搜索 skill 名称">
</div>
<div id="detail-panel"></div>
<div><svg id="main-svg"></svg></div>
<div id="tooltip"></div>
<div id="legend">
  <h3>Categories</h3>
  <div class="legend-item" onclick="resetFilter()" style="border-bottom:1px solid #2a2a4a;margin-bottom:4px;padding-bottom:4px;color:#8b5cf6;font-weight:bold">Show All</div>
</div>
<div class="controls">
  <button onclick="zoomToFit()">Zoom To Fit</button>
  <button onclick="resetSim()">Reset Layout</button>
</div>
<script>
const graph = __GRAPH_DATA__;
const width = window.innerWidth, height = window.innerHeight;
const svg = d3.select("#main-svg").attr("width", width).attr("height", height);
const g = svg.append("g");
const zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", function(e) { g.attr("transform", e.transform); });
svg.call(zoom);
const sim = d3.forceSimulation(graph.nodes)
  .force("link", d3.forceLink(graph.links).id(function(d) { return d.id; }).distance(function(d) { return d.type==='belongs_to' ? 80 : 120; }))
  .force("charge", d3.forceManyBody().strength(-200))
  .force("center", d3.forceCenter(width/2, height/2))
  .force("collision", d3.forceCollide(function(d) { return d.type==='category' ? Math.sqrt(d.count||10)*4+10 : 10; }));
const link = g.selectAll("line.link").data(graph.links).join("line")
  .attr("class", function(d) { return "link "+d.type; })
  .attr("stroke", function(d) { return d.type==='belongs_to' ? '#8b5cf6' : '#ff6b9d'; })
  .attr("stroke-opacity", 0.15).attr("stroke-width", 0.5);
const node = g.selectAll("g.node").data(graph.nodes).join("g").attr("class", function(d) { return "node "+d.type; })
  .call(d3.drag().on("start", function(e,d) { if(!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", function(e,d) { d.fx = e.x; d.fy = e.y; })
    .on("end", function(e,d) { if(!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));
node.append("circle")
  .attr("r", function(d) { return d.type==='category' ? Math.sqrt(d.count||10)*4+10 : 5; })
  .attr("fill", function(d) { return d.color||'#64748b'; })
  .attr("opacity", function(d) { return d.type==='category' ? 0.85 : 0.6; });
node.append("text")
  .text(function(d) { return d.name; })
  .attr("dx", function(d) { return d.type==='category' ? 0 : 7; })
  .attr("dy", function(d) { return d.type==='category' ? 4 : 3; })
  .attr("text-anchor", function(d) { return d.type==='category' ? 'middle' : 'start'; });
var tip = d3.select("#tooltip");
node.on("mouseover", function(e,d) {
  var h = '<div class="name">'+d.name+'</div>';
  if(d.type==='category') { h += '<div class="detail">Category - '+d.count+' skills</div>'; }
  else { h += '<div class="detail">'+d.category+'</div>'; if(d.desc) h += '<div class="desc">'+d.desc.substring(0,80)+'</div>'; }
  tip.html(h).style("display","block").style("left",(e.pageX+15)+"px").style("top",(e.pageY-10)+"px");
}).on("mouseout", function() { tip.style("display","none"); }).on("click", function(e,d) {
  if(d.type!=='skill') return;
  var panel = d3.select("#detail-panel");
  var friends = graph.links.filter(function(l) { return (l.source.id===d.id||l.target.id===d.id) && l.type==='shared_tag'; })
    .map(function(l) { return l.source.id===d.id ? l.target.id : l.source.id; });
  var h = '<div class="title">'+d.name+'</div>';
  h += '<div class="body">Category: '+d.category+'</div>';
  if(d.desc) h += '<div class="body">'+d.desc.substring(0,120)+'</div>';
  if(friends.length) { h += '<div class="body" style="margin-top:6px;color:#ff6b9d">Related ('+friends.length+'):</div>'; h += '<div class="body">'+friends.slice(0,10).join(', ')+(friends.length>10?'...':'')+'</div>'; }
  panel.html(h).style("display","block");
});
sim.on("tick", function() {
  link.attr("x1", function(d) { return d.source.x; }).attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; }).attr("y2", function(d) { return d.target.y; });
  node.attr("transform", function(d) { return "translate("+d.x+","+d.y+")"; });
});
function zoomToFit() { var b = g.node().getBBox(); var s = Math.min(width/b.width, height/b.height)*0.85; svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity.translate(width/2-b.x*s-b.width*s/2,height/2-b.y*s-b.height*s/2).scale(s)); }
function resetSim() { graph.nodes.forEach(function(n) { n.fx=null; n.fy=null; }); sim.alpha(1).restart(); }
document.getElementById("search").addEventListener("input", function() {
  var q = this.value.toLowerCase().trim();
  node.style("opacity", function(d) { if(!q||d.type==='category') return 1; return d.name.toLowerCase().includes(q)?1:0.05; });
  link.style("opacity", function(l) { if(!q) return 1; var s=typeof l.source==='object'?l.source.id:l.source, t=typeof l.target==='object'?l.target.id:l.target; return(s.includes(q)||t.includes(q))?0.3:0.02; });
});
function resetFilter() { node.style("opacity",1); link.style("opacity",1); }
var cats = graph.nodes.filter(function(n) { return n.type==='category'; }).sort(function(a,b) { return b.count-a.count; });
cats.forEach(function(c) {
  d3.select("#legend").append("div").attr("class","legend-item").html('<span class="dot" style="background:'+c.color+'"></span> '+c.name+' <span class="count">'+c.count+'</span>')
    .on("click", function() {
      var sks = graph.nodes.filter(function(n) { return n.type==='skill' && n.category===c.name; }).map(function(n) { return n.id; });
      node.style("opacity", function(d) { return (d.type==='category'&&d.id===c.id)||sks.includes(d.id)?1:0.08; });
      link.style("opacity", function(l) { var si=typeof l.source==='object'?l.source.id:l.source, ti=typeof l.target==='object'?l.target.id:l.target; return si===c.id||ti===c.id||(sks.includes(si)&&sks.includes(ti))?0.3:0.02; });
    });
});
setTimeout(zoomToFit, 800);
</script>
</body>
</html>
"""

# Replace placeholders
html = html_template.replace("__SKILL_COUNT__", str(skill_count))
html = html.replace("__CAT_COUNT__", str(cat_count))
html = html.replace("__LINK_COUNT__", str(link_count))
html = html.replace("__GRAPH_DATA__", js_graph)

OUTPUT.write_text(html, encoding='utf-8')
print(f"Written: {OUTPUT}")
print(f"Nodes: {skill_count} skills + {cat_count} categories")
print(f"Edges: {link_count}")
print(f"Size: {len(html):,} bytes")
