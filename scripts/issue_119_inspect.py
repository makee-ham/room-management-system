#!/usr/bin/env python3
"""Split the large single-file wireframe into temporary review chunks for issue #119."""

from __future__ import annotations

import shutil
from pathlib import Path

SOURCE = Path("WIREFRAME/index.html")
ROOT = Path(".issue119")
CHUNKS = ROOT / "chunks"
CHUNK_LINES = 800


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

    (ROOT / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"wrote {len(list(CHUNKS.glob('*.txt')))} chunks")


if __name__ == "__main__":
    main()
