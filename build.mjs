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
  // Architecture is pro-only: its mermaid blocks are linked as text below, not rendered inline
  let body=rel==="ARCHITECTURE.md" ? raw.replace(/```mermaid\n[\s\S]*?```/g,"\n*Mermaid source for this section is linked under \u201cMermaid source renders\u201d below \u2014 not rendered on this page.*\n") : raw.replace(/```mermaid\n([\s\S]*?)```/g,(m,code)=>`\n<div class="mermaid">${esc(code)}</div>\n`);
  // Fix relative .md links to wiki routes
  body=body.replace(/\]\(([^)]+?)\.md(#[^)]*)?\)/g,(m,p,anchor)=>`](/${p.toLowerCase().replace(/\/skill$/,"")}/${anchor||""})`);
  let html=marked.parse(body);
  if(rel==="ARCHITECTURE.md"){
    const pro=[
      ["Network Architecture","/assets/diagrams-pro/diagram-1-network-architecture.png","Network architecture diagram","Machines, tailnet and trust boundaries \u2014 how the fleet reaches each other. Platforms: macOS \u00b7 Mac mini / MacBook Pro / Neo; iOS apps built on Mac mini."],
      ["Local AI Flow","/assets/diagrams-pro/diagram-2-local-ai-flow.png","Local AI flow diagram","Who calls which model, and what falls back to what. Platform: macOS \u00b7 Mac mini (oMLX / Ollama host)."],
      ["Bot Operating Model","/assets/diagrams-pro/diagram-3-bot-operating-model.png","Bot operating model diagram","Lanes, handoffs and the Atlas gate. Platform: macOS \u00b7 AIMacMini ~/projects."],
      ["Orchestration (design)","/assets/diagrams-pro/diagram-4-orchestration.png","Orchestration control plane diagram (design)","Control plane, routing and failover \u2014 design, labelled DESIGN in the image; expands the approved Phase 0 orchestration mermaid. Platforms: macOS \u00b7 Mac mini / MacBook Pro."],
    ];
    html+=`<h2>Diagrams</h2><p class="quiet">Note: these detailed renders are an October 17, 2026 snapshot (they say 17 bots). Where counts differ, the mermaid sources and docs are authoritative \u2014 current docs say 18 bots. No IPs, keys or secrets are shown. Apple platform chips (macOS/iOS) in each diagram use the Simple Icons glyph from <code>assets/diagrams-pro/icons/</code> with a text label \u2014 see <code>assets/diagrams-pro/README.md</code> for source/license. iPadOS, tvOS and watchOS do not appear in the docs, so they are not shown.</p>`+
      pro.map(([cap,src,alt,desc])=>`<figure class="pro-diagram"><img src="${src}" alt="${alt}"><figcaption><strong>${cap}</strong> \u2014 ${desc}</figcaption></figure>`).join("")+
      `<h2>Mermaid source renders</h2><p>Text links only \u2014 the current-docs mermaid diagrams are not shown as images on this page:</p><ul>`+
      [["Machines","diagram-1-machines"],["Bot handoffs","diagram-2-bot-handoffs"],["Orchestration","diagram-3-orchestration"]].map(([name,f])=>`<li>${name}: <a href="/assets/diagrams/${f}.mmd">${f}.mmd (source)</a> \u00b7 <a href="/assets/diagrams/${f}.png">${f}.png (render)</a></li>`).join("")+
      `</ul>`;
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
