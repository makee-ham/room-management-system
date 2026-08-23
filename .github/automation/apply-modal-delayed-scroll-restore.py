from __future__ import annotations

import hashlib
import json
from pathlib import Path

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    html = html.replace(old, new, 1)


replace_once(
    "      let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null;\n      function scheduleWindowScrollRestore(value) {\n        const y=Math.max(0,Math.round(Number(value)||0));\n        cancelAnimationFrame(modalScrollRestoreFrame);\n        window.scrollTo(0,y);\n        modalScrollRestoreFrame=requestAnimationFrame(()=>{window.scrollTo(0,y);modalScrollRestoreFrame=0;});\n      }",
    "      let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null,modalScrollRestoreTimer=0;\n      function scheduleWindowScrollRestore(value) {\n        const y=Math.max(0,Math.round(Number(value)||0)),restore=()=>window.scrollTo(0,y);\n        cancelAnimationFrame(modalScrollRestoreFrame);clearTimeout(modalScrollRestoreTimer);\n        restore();\n        modalScrollRestoreFrame=requestAnimationFrame(()=>{restore();modalScrollRestoreFrame=requestAnimationFrame(()=>{restore();modalScrollRestoreFrame=0;});});\n        modalScrollRestoreTimer=setTimeout(()=>{restore();modalScrollRestoreTimer=0;},90);\n      }",
    "multi-stage modal scroll restore",
)
replace_once(
    "        cancelAnimationFrame(modalScrollRestoreFrame);modalScrollRestoreFrame=0;",
    "        cancelAnimationFrame(modalScrollRestoreFrame);clearTimeout(modalScrollRestoreTimer);modalScrollRestoreFrame=0;modalScrollRestoreTimer=0;",
    "cancel pending modal scroll restoration",
)
replace_once(
    "        requestAnimationFrame(()=>{window.scrollTo(0,Math.max(0,Number(route.scrollY)||0));if(entry.layer!=='modal'||override||completed)(findHistoryFocusTarget(focusDescriptor)||document.getElementById('main-content'))?.focus?.({preventScroll:true});});",
    "        requestAnimationFrame(()=>{scheduleWindowScrollRestore(Math.max(0,Number(route.scrollY)||0));if(entry.layer!=='modal'||override||completed)(findHistoryFocusTarget(focusDescriptor)||document.getElementById('main-content'))?.focus?.({preventScroll:true});});",
    "history navigation staged scroll restore",
)

html_path.write_text(html, encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
old_contract = "  'let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null;',"
new_contract = "  'let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null,modalScrollRestoreTimer=0;',\n  'modalScrollRestoreTimer=setTimeout(()=>{restore();modalScrollRestoreTimer=0;},90);',\n  'scheduleWindowScrollRestore(Math.max(0,Number(route.scrollY)||0))',"
if checker.count(old_contract) != 1:
    raise SystemExit(f"delayed restore checker mismatch: {checker.count(old_contract)}")
checker_path.write_text(checker.replace(old_contract, new_contract, 1), encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
sums_path.write_text("\n".join(f"{digest}  WIREFRAME/index.html" if line.endswith("  WIREFRAME/index.html") else line for line in lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
