from __future__ import annotations

import hashlib
import json
from pathlib import Path

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")
old = "        const y=Math.max(0,Math.round(Number(value)||0)),restore=()=>window.scrollTo(0,y);"
new = "        const y=Math.max(0,Math.round(Number(value)||0)),restore=()=>{const root=document.documentElement,previous=root.style.scrollBehavior;root.style.scrollBehavior='auto';window.scrollTo(0,y);root.style.scrollBehavior=previous;};"
if html.count(old) != 1:
    raise SystemExit(f"instant scroll restoration mismatch: {html.count(old)}")
html_path.write_text(html.replace(old, new, 1), encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
marker = "  'modalScrollRestoreTimer=setTimeout(()=>{restore();modalScrollRestoreTimer=0;},90);',"
addition = "  \"root.style.scrollBehavior='auto';window.scrollTo(0,y);root.style.scrollBehavior=previous;\",\n" + marker
if checker.count(marker) != 1:
    raise SystemExit(f"instant scroll checker mismatch: {checker.count(marker)}")
checker_path.write_text(checker.replace(marker, addition, 1), encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
sums_path.write_text("\n".join(f"{digest}  WIREFRAME/index.html" if line.endswith("  WIREFRAME/index.html") else line for line in lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
