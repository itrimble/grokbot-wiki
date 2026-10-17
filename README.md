# Grok Bot Wiki
Live wiki at https://wiki.remnantsecurity.com (GitHub Pages, gh-pages branch like product-diary).
Source of truth: `/workspace/grokbot-docs` on the box (58 md pages). `bin/sync-content.sh` rsyncs *.md into `content/` (gitignored, generated — never hand-edit), `build.mjs` sanitizes (tailnet IPs, tokens, .ts.net hosts redacted), renders with marked + client-side mermaid, uses preview PNGs on Architecture page.
Build/deploy: `bash deploy.sh` (builds dist/, force-publishes gh-pages, CNAME wiki.remnantsecurity.com).
Proposed routine: 'Grokbot wiki daily rebuild' — weekdays ~6:20 AM CT (after 6 AM docs refresh): sync, build, commit source changes if any, deploy, verify live.
