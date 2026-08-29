#!/usr/bin/env python3
"""Post-process legacy duplicate markup after the issue #119 v2 transform."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html_path = ROOT / "WIREFRAME/index.html"
html = html_path.read_text(encoding="utf-8")

old = "<button class=\"btn btn-outline\" type=\"button\" data-action=\"switch-role\" aria-label=\"${state.role==='admin'?'메이드 보기':'관리자 보기'}\">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button>"
new = "<button class=\"btn btn-outline\" type=\"button\" data-action=\"logout\" aria-label=\"로그아웃\">${icon('logout','icon-sm')}<span>로그아웃</span></button>"
count = html.count(old)
if count != 1:
    raise RuntimeError(f"legacy role switch: expected 1 remaining match, found {count}")
html = html.replace(old, new, 1)
html_path.write_text(html, encoding="utf-8")

sums_path = ROOT / "SHA256SUMS.txt"
refreshed = []
for raw in sums_path.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    _, rel = raw.split(None, 1)
    path = ROOT / rel
    if not path.exists():
        raise RuntimeError(f"SHA256 tracked path missing: {rel}")
    refreshed.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
sums_path.write_text("\n".join(refreshed) + "\n", encoding="utf-8")

print("Removed the stale legacy role switch markup.")
