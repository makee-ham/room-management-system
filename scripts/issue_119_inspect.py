#!/usr/bin/env python3
"""Create a compact code map for issue #119 without changing product code."""

from __future__ import annotations

from pathlib import Path

SOURCE = Path("WIREFRAME/index.html")
OUTPUT = Path(".issue119/CODEMAP.md")

TERMS: tuple[tuple[str, str, int], ...] = (
    ("관리자 청소 화면", "renderHousekeeping", 2),
    ("메이드 루트 화면", "function renderMaid", 2),
    ("메이드 근무 가능 화면", "renderMaidSchedule", 2),
    ("메이드 네비게이션", "maid-nav", 3),
    ("메이드 알림", "알림", 5),
    ("관리자 근무표", "메이드 근무표", 4),
    ("미배정 객실", "아직 순서가 없는 객실", 3),
    ("객실별 담당 수정", "객실별 담당 수정", 3),
    ("객실 정보 없음", "객실 정보 없음", 5),
    ("장기투숙", "장기", 8),
    ("예약 모달", "openReservation", 5),
    ("예약 렌더", "renderReservation", 5),
    ("객실 상세", "openRoom", 5),
    ("객실 목록", "renderRooms", 3),
    ("청소 대상", "cleaningCandidates", 5),
    ("청소 가능 여부", "isCleaning", 6),
    ("세션", "roomManagementMaidSession", 5),
    ("초기 렌더", "DOMContentLoaded", 3),
)


def fenced(text: str) -> str:
    return "```html\n" + text.replace("```", "` ` `") + "\n```\n"


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines()
    out: list[str] = [
        "# Issue #119 code map",
        "",
        f"- source: `{SOURCE}`",
        f"- bytes: {len(source.encode('utf-8')):,}",
        f"- lines: {len(lines):,}",
        "- generated from the issue branch for temporary implementation inspection",
        "",
    ]

    for label, term, limit in TERMS:
        matches = [index for index, line in enumerate(lines) if term in line]
        out.extend((f"## {label}: `{term}`", "", f"matches: {len(matches)}", ""))
        if not matches:
            continue
        for occurrence, index in enumerate(matches[:limit], start=1):
            start = max(0, index - 45)
            end = min(len(lines), index + 70)
            numbered = "\n".join(
                f"{line_no + 1:>6} | {lines[line_no]}" for line_no in range(start, end)
            )
            out.extend((f"### occurrence {occurrence} · line {index + 1}", "", fenced(numbered)))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
