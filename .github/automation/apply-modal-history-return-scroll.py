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
    "      let modalPageScrollY=null,modalScrollRestoreFrame=0;",
    "      let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null;",
    "modal return scroll state",
)
replace_once(
    "        if(isWireframeHistory(history.state)&&history.state.layer==='modal'&&historyIndex()>0){rawCloseModal({restoreFocus:true,restoreScroll:false});historyTraversalPending=true;history.back();return;}",
    "        if(isWireframeHistory(history.state)&&history.state.layer==='modal'&&historyIndex()>0){modalHistoryReturnScrollY=modalPageScrollY;rawCloseModal({restoreFocus:true,restoreScroll:false});historyTraversalPending=true;history.back();return;}",
    "modal dismiss return scroll capture",
)
replace_once(
    "        if(wasModal)historyReturnFocus=historyReturnFocus||historyFocusDescriptor(modalTrigger);\n        rawCloseModal({restoreScroll:false});\n        const override=historyTraversalOverride,route=override||completed?.route||entry.route;historyTraversalOverride=null;",
    "        if(wasModal){historyReturnFocus=historyReturnFocus||historyFocusDescriptor(modalTrigger);if(modalHistoryReturnScrollY==null)modalHistoryReturnScrollY=modalPageScrollY;}\n        rawCloseModal({restoreScroll:false});\n        const override=historyTraversalOverride,baseRoute=override||completed?.route||entry.route,route=modalHistoryReturnScrollY==null?baseRoute:{...baseRoute,scrollY:modalHistoryReturnScrollY};historyTraversalOverride=null;modalHistoryReturnScrollY=null;",
    "history navigation return scroll override",
)

html_path.write_text(html, encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
old_contract = "  'let modalPageScrollY=null,modalScrollRestoreFrame=0;',"
new_contract = "  'let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null;',\n  'modalHistoryReturnScrollY=modalPageScrollY;',\n  'route=modalHistoryReturnScrollY==null?baseRoute:{...baseRoute,scrollY:modalHistoryReturnScrollY}',"
if checker.count(old_contract) != 1:
    raise SystemExit(f"modal checker contract mismatch: {checker.count(old_contract)}")
checker_path.write_text(checker.replace(old_contract, new_contract, 1), encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
sums_path.write_text("\n".join(f"{digest}  WIREFRAME/index.html" if line.endswith("  WIREFRAME/index.html") else line for line in lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
