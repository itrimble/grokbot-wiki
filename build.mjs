import { marked } from "marked";
import fs from "node:fs"; import path from "node:path";
const ROOT = path.dirname(new URL(import.meta.url).pathname);
const SRC = fs.existsSync(path.join(ROOT,"content")) ? path.join(ROOT,"content") : "/workspace/grokbot-docs";
const DIST = path.join(ROOT,"dist"); const DOMAIN="wiki.remnantsecurity.com";
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function sanitize(t){
  return t
    .replace(/\b100\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g,"[redacted tailnet IP]")
    .replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g,(m)=> m.startsWith("100.")?"[redacted tailnet IP]":m)
    .replace(/[a-z0-9\-]+\.ts\.net/gi,"[redacted tailnet host]")
    .replace(/phc_[A-Za-z0-9]{10,}/g,"[redacted token]")
    .replace(/gh[pousr]_[A-Za-z0-9]{10,}/g,"[redacted token]")
    .replace(/sk-[A-Za-z0-9\-_]{20,}/g,"[redacted token]");
}
function walk(dir,base=""){let out=[];for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(e.name.startsWith(".")||e.name==="node_modules")continue;const p=path.join(dir,e.name);const rel=base?base+"/"+e.name:e.name;if(e.isDirectory())out.push(...walk(p,rel));else if(e.name.endsWith(".md"))out.push(rel);}return out.sort();}
const files=walk(SRC);
const pages=files.map(rel=>{
  const raw=sanitize(fs.readFileSync(path.join(SRC,rel),"utf8"));
  const title=(raw.match(/^#\s+(.+)/m)||[])[1]||rel;
  let slug=rel.replace(/\.md$/,"").replace(/\/SKILL$/,"").toLowerCase();
  if(rel==="README.md") slug="index-readme";
  // mermaid -> placeholder div (client renders), keep source escaped
  let body=raw.replace(/```mermaid\n([\s\S]*?)```/g,(m,code)=>`\n<div class="mermaid">${esc(code)}</div>\n`);
  // Fix relative .md links to wiki routes
  body=body.replace(/\]\(([^)]+?)\.md(#[^)]*)?\)/g,(m,p,anchor)=>`](/${p.toLowerCase().replace(/\/skill$/,"")}/${anchor||""})`);
  let html=marked.parse(body);
  if(rel==="ARCHITECTURE.md"){
    html+=`<h2>Detailed diagrams (professional renders, verified 2026-10-17)</h2><p>Detailed local renders from <code>assets/diagrams-pro/</code> (2400px PNGs built by <code>src/build_diagrams.py</code> from wiki sources; no IPs, keys or secrets). They expand the mermaid diagrams below — where counts differ, the current mermaid renders are authoritative (pro renders are a 2026-10-17 snapshot saying 17 bots; current docs say 18). Diagram 4 is labelled DESIGN in the image and expands the approved Phase 0 orchestration mermaid (diagram 3 below).</p><p><img src="/assets/diagrams-pro/diagram-1-network-architecture.png" alt="Network architecture diagram"></p><p><img src="/assets/diagrams-pro/diagram-2-local-ai-flow.png" alt="Local AI flow diagram"></p><p><img src="/assets/diagrams-pro/diagram-3-bot-operating-model.png" alt="Bot operating model diagram"></p><p><img src="/assets/diagrams-pro/diagram-4-orchestration.png" alt="Orchestration control plane diagram (design)"></p><h2>Rendered diagrams (mermaid, current docs)</h2><p>Simple renders generated from the three mermaid blocks above with <code>npx @mermaid-js/mermaid-cli -b white -s 3</code>. Kept as the current-docs fallback to the detailed renders.</p><p><img src="/assets/diagrams/diagram-1-machines.png" alt="Machines diagram"></p><p><img src="/assets/diagrams/diagram-2-bot-handoffs.png" alt="Bot handoffs diagram"></p><p><img src="/assets/diagrams/diagram-3-orchestration.png" alt="Orchestration diagram"></p>`;
  }
  const section=rel.includes("/")?rel.split("/")[0]:"top";
  return {rel,slug,title,html,section};
});
fs.rmSync(DIST,{recursive:true,force:true}); fs.mkdirSync(DIST,{recursive:true});
fs.writeFileSync(path.join(DIST,"CNAME"),DOMAIN+"\n");
fs.cpSync(path.join(ROOT,"assets"),path.join(DIST,"assets"),{recursive:true});
fs.cpSync(path.join(ROOT,"styles.css"),path.join(DIST,"styles.css"));
const sections={}; for(const p of pages){(sections[p.section]??=[]).push(p);}
const nav=Object.entries(sections).map(([s,ps])=>`<details ${s==="bots"?"open":""}><summary>${esc(s)} (${ps.length})</summary><ul>${ps.map(p=>`<li><a href="/${p.slug}/">${esc(p.title)}</a></li>`).join("")}</ul></details>`).join("");
const layout=(title,main)=>`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} — Grok Bot Wiki</title><link rel="stylesheet" href="/styles.css"><script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';mermaid.initialize({startOnLoad:true,theme:'default'});</script></head><body><header><a class="brand" href="/">Grok Bot Wiki</a><span class="by">Remnant Security · source: grokbot-docs</span></header><div class="layout"><nav>${nav}</nav><main>${main}</main></div><footer>Built from <code>/workspace/grokbot-docs</code> — no secrets or tailnet IPs. <a href="https://blog.remnantsecurity.com/">Product Diary</a></footer></body></html>`;
for(const p of pages){const d=path.join(DIST,p.slug);fs.mkdirSync(d,{recursive:true});fs.writeFileSync(path.join(d,"index.html"),layout(p.title,`<article><p class="crumbs"><a href="/">Home</a> / ${esc(p.rel)}</p><h1>${esc(p.title)}</h1>${p.html}</article>`));}
// index (distinct from README page)
const counts=Object.entries(sections).map(([s,ps])=>`<li><strong>${esc(s)}</strong>: ${ps.length} pages</li>`).join("");
fs.writeFileSync(path.join(DIST,"index.html"),layout("Grok Bot Wiki",`<h1>Grok Bot Wiki</h1><p class="lede">Live wiki built from the grokbot-docs repo (${pages.length} pages). Source of truth stays in grokbot-docs; this site is regenerated, not hand-edited.</p><ul>${counts}</ul><h2>Start here</h2><ul><li><a href="/architecture/">Architecture</a></li><li><a href="/open-work/">Open work</a></li><li><a href="/routines/">Routines</a></li><li><a href="/index-readme/">Docs home (README)</a></li></ul>`));
console.log(`Built ${pages.length} pages from ${SRC}`);
