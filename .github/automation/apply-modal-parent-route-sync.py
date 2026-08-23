from __future__ import annotations

import hashlib
import json
from pathlib import Path

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")
old = "        const current=history.state,route=historyRouteSnapshot(),trigger=historyFocusDescriptor(modalTrigger);\n        if(isWireframeHistory(current)&&current.layer==='modal'&&!stack){"
new = "        const current=history.state,route=historyRouteSnapshot(),trigger=historyFocusDescriptor(modalTrigger);\n        if(isWireframeHistory(current)&&current.layer==='page')history.replaceState({...current,route},'',historyRouteUrl(route));\n        if(isWireframeHistory(current)&&current.layer==='modal'&&!stack){"
if html.count(old) != 1:
    raise SystemExit(f"modal parent route sync mismatch: {html.count(old)}")
html_path.write_text(html.replace(old, new, 1), encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
marker = "  \"else if(a==='close-modal'||a==='backdrop-close')dismissModal();\","
addition = "  \"if(isWireframeHistory(current)&&current.layer==='page')history.replaceState({...current,route},'',historyRouteUrl(route));\",\n" + marker
if checker.count(marker) != 1:
    raise SystemExit(f"modal parent route checker mismatch: {checker.count(marker)}")
checker_path.write_text(checker.replace(marker, addition, 1), encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
sums_path.write_text("\n".join(f"{digest}  WIREFRAME/index.html" if line.endswith("  WIREFRAME/index.html") else line for line in lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
