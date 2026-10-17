#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf content; mkdir -p content
python3 - << 'PY'
import pathlib, shutil
src=pathlib.Path("/workspace/grokbot-docs"); dst=pathlib.Path("content")
for p in src.rglob("*.md"):
    if ".git" in p.parts: continue
    out=dst/p.relative_to(src); out.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p,out)
print(f"Synced {len(list(dst.rglob('*.md')))} md files")
PY
