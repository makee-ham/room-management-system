from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML_PATH = Path("WIREFRAME/index.html")
html = HTML_PATH.read_text(encoding="utf-8")

summary_before = '<strong>총 ${ROOMS.length}개 객실 · 상태 중복 집계</strong>'
summary_after = '<strong>총 ${ROOMS.length}개 객실</strong>'
if html.count(summary_before) != 1:
    raise SystemExit(f"room catalog summary title mismatch: {html.count(summary_before)} matches")
html = html.replace(summary_before, summary_after, 1)

# Only patch the final active roomCard implementation.
card_start = html.rfind("      function roomCard(no) {")
card_end = html.find("\n      function cleaningLabel(", card_start)
if card_start < 0 or card_end < 0:
    raise SystemExit("active roomCard block could not be isolated")
card_source = html[card_start:card_end]

substate_start = card_source.find("        const cleaningSubLabel=")
substate_end = card_source.find("\n", substate_start)
if substate_start < 0 or substate_end < 0:
    raise SystemExit("room-card secondary-status definition missing")
substate_line = card_source[substate_start:substate_end]
if ",statusIcon=" not in substate_line:
    raise SystemExit("room-card status icon expression could not be preserved")
status_icon_expression = substate_line.split(",statusIcon=", 1)[1]
card_source = card_source[:substate_start] + "        const statusIcon=" + status_icon_expression + card_source[substate_end:]

status_before = '<div class="concept-status-panel ${p.tone}"><span class="status-symbol">${icon(statusIcon)}</span><div class="concept-status-copy"><strong>${esc(p.status)}</strong><span>${esc(p.reason)}</span>${subBadges}</div></div>'
status_after = '<div class="concept-status-panel ${p.tone}"><span class="status-symbol">${icon(statusIcon)}</span><div class="concept-status-copy"><strong>${esc(p.status)}</strong></div></div>'
if card_source.count(status_before) != 1:
    raise SystemExit(f"room-card status markup mismatch: {card_source.count(status_before)} matches")
card_source = card_source.replace(status_before, status_after, 1)

for forbidden in ("const cleaningSubLabel=", "${subBadges}", '<span>${esc(p.reason)}</span>'):
    if forbidden in card_source:
        raise SystemExit(f"visible room-card secondary status remains: {forbidden}")
if "${scheduleBadges}${detailBadges}" not in card_source:
    raise SystemExit("upper-right schedule and detail badges were not preserved")
html = html[:card_start] + card_source + html[card_end:]
HTML_PATH.write_text(html, encoding="utf-8")

# Keep a permanent regression check near the rest of the workspace contracts.
check_path = Path("scripts/check-workspace.mjs")
check_source = check_path.read_text(encoding="utf-8")
check_marker = "const roomCardCopyStart = html.lastIndexOf('      function roomCard(no) {');"
if check_marker not in check_source:
    regression_contract = r'''

const roomCardCopyStart = html.lastIndexOf('      function roomCard(no) {');
const roomCardCopyEnd = html.indexOf('\n      function cleaningLabel(', roomCardCopyStart);
if (roomCardCopyStart < 0 || roomCardCopyEnd < 0) {
  throw new Error('Active roomCard source could not be resolved for copy cleanup checks.');
}
const roomCardCopySource = html.slice(roomCardCopyStart, roomCardCopyEnd);
if (!html.includes('<strong>총 ${ROOMS.length}개 객실</strong>')) {
  throw new Error('Room catalog total-only heading is missing.');
}
if (html.includes('총 ${ROOMS.length}개 객실 · 상태 중복 집계')) {
  throw new Error('Legacy duplicate-count wording remains in the room catalog heading.');
}
for (const forbidden of ['<span>${esc(p.reason)}</span>', '${subBadges}', 'const cleaningSubLabel=']) {
  if (roomCardCopySource.includes(forbidden)) {
    throw new Error(`Visible room-card secondary status remains: ${forbidden}`);
  }
}
for (const requiredContract of [
  '<div class="concept-status-copy"><strong>${esc(p.status)}</strong></div>',
  '${scheduleBadges}${detailBadges}',
  'class="badge-row room-schedule-badges"',
]) {
  if (!roomCardCopySource.includes(requiredContract)) {
    throw new Error(`Room-card primary-status or upper-badge contract missing: ${requiredContract}`);
  }
}
'''
    insert_at = check_source.rfind("\nconsole.log(`Required files:")
    if insert_at < 0:
        raise SystemExit("workspace check completion marker missing")
    check_source = check_source[:insert_at] + regression_contract + check_source[insert_at:]
    check_path.write_text(check_source, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme_marker = "## 객실 카드 주 상태 단순화 (2026-08-29)"
if readme_marker not in readme:
    readme += """

## 객실 카드 주 상태 단순화 (2026-08-29)

- 객실 목록 요약 제목은 전체 객실 수만 표시한다.
- 객실 카드의 상태 패널은 `투숙 중`, `청소 필요`, `배정 가능`, `배정 불가` 중 주 상태만 표시한다.
- 주 상태 아래의 이유 문장과 청소 보조 상태 칩은 카드에서 표시하지 않는다.
- 예약 일정·특이사항 등 우측 상단 배지, 체크인·체크아웃 시간대, 빠른 작업과 상세 화면은 유지한다.
"""
    readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa_marker = "## 2026-08-29 · 객실 목록 중복 상태 설명 제거"
if qa_marker not in qa:
    qa += """

## 2026-08-29 · 객실 목록 중복 상태 설명 제거

- 요약 제목이 `총 121개 객실`로만 표시되는지 확인한다.
- 카드형 목록의 모든 상태 패널이 주 상태 한 줄만 표시하는지 확인한다.
- `현재 투숙 중 · 체크아웃 11:00` 같은 이유 문장과 청소 보조 상태 칩이 카드에서 보이지 않는지 확인한다.
- 우측 상단 예약·특이사항 배지와 하단 빠른 작업이 유지되는지 확인한다.
- 390px·768px·1440px에서 가로 넘침, 콘솔 오류, 런타임 오류가 없는지 확인한다.
"""
    qa_path.write_text(qa + "\n", encoding="utf-8")

index_hash = hashlib.sha256(HTML_PATH.read_bytes()).hexdigest()
manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-29-room-card-status-cleanup"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).replace(microsecond=0).isoformat()
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = index_hash
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checksums_path = Path("SHA256SUMS.txt")
checksums = checksums_path.read_text(encoding="utf-8")
pattern = re.compile(r"^[a-f0-9]{64}(\s+\*?WIREFRAME/index\.html)$", re.MULTILINE)
checksums, replacements = pattern.subn(lambda match: index_hash + match.group(1), checksums, count=1)
if replacements != 1:
    raise SystemExit(f"WIREFRAME/index.html checksum entry mismatch: {replacements} matches")
checksums_path.write_text(checksums, encoding="utf-8")

print("Room catalog summary and card secondary-status cleanup applied.")
