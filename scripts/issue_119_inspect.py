#!/usr/bin/env python3
"""Split the large wireframe and extract targeted review contexts for issue #119."""

from __future__ import annotations

import shutil
from pathlib import Path

SOURCE = Path("WIREFRAME/index.html")
ROOT = Path(".issue119")
CHUNKS = ROOT / "chunks"
CHUNK_LINES = 800
CONTEXT_BEFORE = 16
CONTEXT_AFTER = 34
TERMS: tuple[tuple[str, str, int], ...] = (
    ("state declaration", "let state =", 4),
    ("base state", "function baseState", 4),
    ("state normalization", "function normalize", 8),
    ("main render", "function render()", 8),
    ("main route", "function renderMain", 8),
    ("login", "function renderLogin", 8),
    ("topbar", "function renderTopbar", 8),
    ("admin navigation", "const adminNav", 4),
    ("maid navigation", "const maidNav", 4),
    ("maid route", "function renderMaid", 30),
    ("maid schedule", "function renderMaidSchedule", 8),
    ("maid availability", "근무 가능일", 20),
    ("maid alert route", "alerts", 30),
    ("logged in", "loggedIn", 30),
    ("logout action", "logout", 30),
    ("room presentation", "function roomPresentation", 8),
    ("room card", "function roomCard", 12),
    ("room table", "function renderRoomTable", 8),
    ("room detail", "function openRoom", 12),
    ("room detail action", "room-detail", 30),
    ("reservation modal", "function openReservation", 12),
    ("reservation config", "function reservationModalConfig", 12),
    ("reservation form", "reservation-form", 20),
    ("reservation save", "save-reservation", 20),
    ("reservation overlap", "reservationOverlaps", 20),
    ("reservation availability", "availableRooms", 20),
    ("assignment targets", "function assignmentTargets", 12),
    ("live assignment targets", "liveAssignmentTargetsForState", 20),
    ("filtered assignment targets", "filteredAssignmentTargets", 20),
    ("cleaning target rows", "객실별 담당 수정", 8),
    ("unassigned room cards", "아직 순서가 없는 객실", 8),
    ("click delegate", "document.addEventListener('click'", 30),
    ("data issue", "dataIssue", 30),
    ("initial occupied", "INITIAL_OCCUPIED_ROOMS", 16),
    ("long stay", "장기", 30),
)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines()

    if CHUNKS.exists():
        shutil.rmtree(CHUNKS)
    CHUNKS.mkdir(parents=True, exist_ok=True)

    index_lines = [
        "# Issue #119 temporary source chunks",
        "",
        f"- source: `{SOURCE}`",
        f"- bytes: {len(source.encode('utf-8')):,}",
        f"- lines: {len(lines):,}",
        f"- chunk size: {CHUNK_LINES} lines",
        "",
    ]

    for start in range(0, len(lines), CHUNK_LINES):
        end = min(len(lines), start + CHUNK_LINES)
        name = f"{start + 1:04d}-{end:04d}.txt"
        body = "\n".join(
            f"{line_no + 1:>6} | {lines[line_no]}" for line_no in range(start, end)
        ) + "\n"
        (CHUNKS / name).write_text(body, encoding="utf-8")
        index_lines.append(f"- `{name}` · lines {start + 1}-{end}")

    grep_lines = [
        "# Issue #119 targeted source contexts",
        "",
        "Generated only for implementation review; remove before the final PR commit.",
        "",
    ]
    occurrence_lines = ["# Issue #119 occurrence index", ""]
    for label, term, limit in TERMS:
        matches = [index for index, line in enumerate(lines) if term in line]
        occurrence_lines.append(f"- **{label}** `{term}`: {', '.join(str(index + 1) for index in matches) or 'none'}")
        grep_lines.extend((f"## {label}: `{term}`", "", f"matches: {len(matches)}", ""))
        for occurrence, index in enumerate(matches[:limit], start=1):
            start = max(0, index - CONTEXT_BEFORE)
            end = min(len(lines), index + CONTEXT_AFTER + 1)
            grep_lines.extend((f"### occurrence {occurrence} · line {index + 1}", "", "```html"))
            grep_lines.extend(f"{line_no + 1:>6} | {lines[line_no]}" for line_no in range(start, end))
            grep_lines.extend(("```", ""))

    (ROOT / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (ROOT / "GREP.md").write_text("\n".join(grep_lines) + "\n", encoding="utf-8")
    (ROOT / "OCCURRENCES.md").write_text("\n".join(occurrence_lines) + "\n", encoding="utf-8")
    print(f"wrote {len(list(CHUNKS.glob('*.txt')))} chunks and review indexes")


if __name__ == "__main__":
    main()
