#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one anchor in {path}, found {count}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    suffix = "" if text.endswith("\n") else "\n"
    path.write_text(text + suffix + block.rstrip() + "\n", encoding="utf-8")


index = ROOT / "WIREFRAME/index.html"
replace_once(
    index,
    "    .schedule-priority-badge.stayover { background:#67509a; box-shadow:0 4px 12px rgba(103,80,154,.18); }\n"
    "    .schedule-priority-badge .icon { flex:0 0 auto; width:14px; height:14px; }",
    "    .schedule-priority-badge.stayover { background:#67509a; box-shadow:0 4px 12px rgba(103,80,154,.18); }\n"
    "    .schedule-priority-badge.guests { background:#17314a; box-shadow:0 4px 12px rgba(23,49,74,.2); }\n"
    "    .schedule-priority-badge .icon { flex:0 0 auto; width:14px; height:14px; }",
)
replace_once(
    index,
    "        const scheduleBadges=[stayProgress?`<span class=\"schedule-priority-badge stayover\">${icon('calendar','icon-sm')}${esc(stayProgress.label)}</span>`:'',special.early?`<span class=\"schedule-priority-badge\">${icon('clock','icon-sm')}얼리 체크인 ${esc(earlyTime)} · ${esc(special.earlyOffset)} 빠름</span>`:'',special.late?`<span class=\"schedule-priority-badge late\">${icon('clock','icon-sm')}레이트 체크아웃 ${esc(lateTime)} · ${esc(special.lateOffset)} 늦음</span>`:''].filter(Boolean).join('');",
    "        const cardGuestCount=closestReservation?reservationGuestCount(closestReservation):null;\n"
    "        const scheduleBadges=[cardGuestCount?`<span class=\"schedule-priority-badge guests\" aria-label=\"숙박 인원 ${cardGuestCount}명\">${icon('user','icon-sm')}${cardGuestCount}명</span>`:'',stayProgress?`<span class=\"schedule-priority-badge stayover\">${icon('calendar','icon-sm')}${esc(stayProgress.label)}</span>`:'',special.early?`<span class=\"schedule-priority-badge\">${icon('clock','icon-sm')}얼리 체크인 ${esc(earlyTime)} · ${esc(special.earlyOffset)} 빠름</span>`:'',special.late?`<span class=\"schedule-priority-badge late\">${icon('clock','icon-sm')}레이트 체크아웃 ${esc(lateTime)} · ${esc(special.lateOffset)} 늦음</span>`:''].filter(Boolean).join('');",
)

room_policy = ROOT / "DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md"
replace_once(
    room_policy,
    "`얼리 체크인 · N시간`과 `레이트 체크아웃 · N시간`은 청소 진행 서브 배지보다 눈에 잘 띄는 일정 배지로 표시하고, 조정된 실제 예정 시각을 같이 보여준다. 얼리·레이트 자체는 카드 주 상태나 색을 바꾸지 않는다. 기본 시각이면 특수 배지를 표시하지 않는다.\n\n"
    "카드형 객실 목록에는 별도의 큰 예약 요약 행을 두지 않는다.",
    "`얼리 체크인 · N시간`과 `레이트 체크아웃 · N시간`은 청소 진행 서브 배지보다 눈에 잘 띄는 일정 배지로 표시하고, 조정된 실제 예정 시각을 같이 보여준다. 얼리·레이트 자체는 카드 주 상태나 색을 바꾸지 않는다. 기본 시각이면 특수 배지를 표시하지 않는다.\n\n"
    "카드가 표시하는 현재 또는 가장 가까운 유효 예약에는 예약에 저장된 총 숙박 인원을 `N명` 형식의 일정 강조 배지로 표시한다. 추가 인원만 따로 계산한 `+N명` 표기는 사용하지 않으며, 예약이 없는 카드에는 인원 배지를 표시하지 않는다.\n\n"
    "카드형 객실 목록에는 별도의 큰 예약 요약 행을 두지 않는다.",
)

readme = ROOT / "WIREFRAME/README.md"
append_once(
    readme,
    "## 객실 카드 숙박 인원 표시 (2026-08-23)",
    """## 객실 카드 숙박 인원 표시 (2026-08-23)\n\n- 예약이 있는 객실 카드는 카드가 현재 보여 주는 예약의 총 숙박 인원을 `N명` 배지로 먼저 표시한다.\n- 추가 인원 차이값을 `+N명`으로 계산하지 않고 예약에 저장된 총인원을 그대로 사용한다.\n- 예약 인원을 수정해 저장하면 같은 예약을 표시하는 객실 카드 배지도 즉시 다시 렌더링된다.\n""",
)

qa = ROOT / "WIREFRAME/QA.md"
append_once(
    qa,
    "## 2026-08-23 · 객실 카드 총 숙박 인원 배지",
    """## 2026-08-23 · 객실 카드 총 숙박 인원 배지\n\n### 변경\n\n- 객실 카드 상단 일정 강조 영역에 카드가 표시하는 예약의 총 숙박 인원을 `N명`으로 노출했다.\n- 인원 배지는 예약이 있을 때만 표시하며, 예약 상세의 인원 수정 저장 뒤 같은 카드에서 즉시 갱신된다.\n- `+N명`처럼 기본 인원과의 차이를 계산하지 않고 운영자가 준비해야 할 실제 총인원을 보여 준다.\n\n### 검증\n\n- `node scripts/check-workspace.mjs` 정적 계약 및 인라인 JavaScript 구문 검사를 통과했다.\n- Chrome headless에서 관리자 객실 목록을 360·390·768·1440px로 확인하고 가로 넘침이 없음을 검사했다.\n- 142호 예약 인원을 4명에서 5명으로 수정 저장한 뒤 카드 배지가 `5명`으로 갱신되는 상호작용을 확인했다.\n- 대표 화면: `WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png`, `WIREFRAME/QA/screenshots/admin-room-card-guest-count-1440.png`.\n\n### 한계\n\n- 데모 와이어프레임의 브라우저 메모리 상태를 검증한 결과이며 실제 OTA/PMS·백엔드 동기화를 구현한 것은 아니다.\n""",
)

checks = ROOT / "scripts/check-workspace.mjs"
replace_once(
    checks,
    "  'WIREFRAME/QA/screenshots/maid-reservation-guests-390.png',\n",
    "  'WIREFRAME/QA/screenshots/maid-reservation-guests-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-1440.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',\n",
)
replace_once(
    checks,
    "  'WIREFRAME/QA/screenshots/admin-reservation-cancel-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-cleaning-day-tabs-1440.png',",
    "  'WIREFRAME/QA/screenshots/admin-reservation-cancel-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-1440.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-cleaning-day-tabs-1440.png',",
)
room_card_contract = """for (const contract of [
  '.schedule-priority-badge.guests { background:#17314a;',
  'const cardGuestCount=closestReservation?reservationGuestCount(closestReservation):null;',
  'class="schedule-priority-badge guests" aria-label="숙박 인원 ${cardGuestCount}명"',
  "${icon('user','icon-sm')}${cardGuestCount}명",
]) {
  if (!html.includes(contract)) throw new Error(`Room-card guest-count contract missing: ${contract}`);
}
const roomCardPolicy = readFileSync(resolve(root, 'DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md'), 'utf8');
for (const contract of [
  '총 숙박 인원을 `N명` 형식의 일정 강조 배지로 표시한다.',
  '추가 인원만 따로 계산한 `+N명` 표기는 사용하지 않으며',
]) {
  if (!roomCardPolicy.includes(contract)) throw new Error(`Room-card guest-count policy missing: ${contract}`);
}
"""
replace_once(
    checks,
    "for (const contract of [\n  '체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',",
    room_card_contract + "for (const contract of [\n  '체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',",
)

index_hash = hashlib.sha256(index.read_bytes()).hexdigest()
final_audit = ROOT / "DOCS/FINAL_UX_AUDIT.md"
final_hash = hashlib.sha256(final_audit.read_bytes()).hexdigest()
(ROOT / "SHA256SUMS.txt").write_text(
    f"{final_hash}  DOCS/FINAL_UX_AUDIT.md\n{index_hash}  WIREFRAME/index.html\n",
    encoding="utf-8",
)
manifest_path = ROOT / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-23-room-card-guest-count"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).replace(microsecond=0).isoformat()
manifest.setdefault("sha256", {})["DOCS/FINAL_UX_AUDIT.md"] = final_hash
manifest["sha256"]["WIREFRAME/index.html"] = index_hash
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Patched room-card total guest count badge and updated QA metadata.")
