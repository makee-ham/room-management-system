#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: Path, old: str, new: str, expected: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(
            f"Expected {expected} anchor(s) in {path}, found {count}: {old[:160]!r}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8")


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    suffix = "" if text.endswith("\n") else "\n"
    path.write_text(text + suffix + block.rstrip() + "\n", encoding="utf-8")


index = ROOT / "WIREFRAME/index.html"

# Keep the threshold rule in one reusable helper so the card and filter cannot drift apart.
replace_exact(
    index,
    "      function guestCountLabel(value) { return Number.isInteger(Number(value))&&Number(value)>=1?`${Number(value)}명`:'인원 미기록'; }\n"
    "      const INITIAL_RESERVATIONS = Object.freeze([",
    "      function guestCountLabel(value) { return Number.isInteger(Number(value))&&Number(value)>=1?`${Number(value)}명`:'인원 미기록'; }\n"
    "      function reservationHasExtraGuests(reservation) {\n"
    "        return !!reservation&&reservationGuestCount(reservation)>guestPolicyForRoom(reservation.room).defaultGuestCount;\n"
    "      }\n"
    "      function roomHasExtraGuests(no) {\n"
    "        const reservation=activeReservationsFor(state,String(no)).find(item=>!reservationRecordIsPast(item))||null;\n"
    "        return reservationHasExtraGuests(reservation);\n"
    "      }\n"
    "      const INITIAL_RESERVATIONS = Object.freeze([",
)

replace_exact(
    index,
    "        const cardGuestCount=closestReservation?reservationGuestCount(closestReservation):null;",
    "        const cardGuestCount=closestReservation&&reservationHasExtraGuests(closestReservation)?reservationGuestCount(closestReservation):null;",
)

# Preserve the new filter through hash navigation and browser back/forward restoration.
replace_exact(
    index,
    "['all','vacant','available','blocked','cleaning','occupied','candle','issues','early','late'].includes(",
    "['all','vacant','available','blocked','cleaning','occupied','extra-guests','candle','issues','early','late'].includes(",
    expected=2,
)

replace_exact(
    index,
    "if(['available','blocked','cleaning','occupied'].includes(state.roomFilter))return p.key===state.roomFilter;if(state.roomFilter==='default'||state.roomFilter==='catalog'||state.roomFilter==='vacant')return r.occupancy==='vacant'&&!roomIsOnHold(r.no);",
    "if(['available','blocked','cleaning','occupied'].includes(state.roomFilter))return p.key===state.roomFilter;if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);if(state.roomFilter==='default'||state.roomFilter==='catalog'||state.roomFilter==='vacant')return r.occupancy==='vacant'&&!roomIsOnHold(r.no);",
)

replace_exact(
    index,
    "<optgroup label=\"상세 조건\"><option value=\"vacant\" ${state.roomFilter==='vacant'?'selected':''}>공실</option>",
    "<optgroup label=\"상세 조건\"><option value=\"extra-guests\" ${state.roomFilter==='extra-guests'?'selected':''}>인원 추가</option><option value=\"vacant\" ${state.roomFilter==='vacant'?'selected':''}>공실</option>",
)

# Current room-card policy: only over-base reservations receive a total-guest badge.
room_policy = ROOT / "DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md"
replace_exact(
    room_policy,
    "카드가 표시하는 현재 또는 가장 가까운 유효 예약에는 예약에 저장된 총 숙박 인원을 `N명` 형식의 일정 강조 배지로 표시한다. 추가 인원만 따로 계산한 `+N명` 표기는 사용하지 않으며, 예약이 없는 카드에는 인원 배지를 표시하지 않는다.",
    "카드가 표시하는 현재 또는 가장 가까운 유효 예약의 총 숙박 인원이 해당 객실 타입의 기준인원보다 많을 때만, 실제 총 숙박 인원을 `N명` 형식의 일정 강조 배지로 표시한다. `+N명`처럼 초과분만 표시하지 않으며, 기준인원 이하이거나 예약이 없는 카드에는 인원 배지를 표시하지 않는다. 객실 상태 필터의 `인원 추가`는 이 동일한 조건의 카드만 모아 보여 준다.",
)

readme = ROOT / "WIREFRAME/README.md"
replace_exact(
    readme,
    "## 객실 카드 숙박 인원 표시 (2026-08-23)\n\n"
    "- 예약이 있는 객실 카드는 카드가 현재 보여 주는 예약의 총 숙박 인원을 `N명` 배지로 먼저 표시한다.\n"
    "- 추가 인원 차이값을 `+N명`으로 계산하지 않고 예약에 저장된 총인원을 그대로 사용한다.\n"
    "- 예약 인원을 수정해 저장하면 같은 예약을 표시하는 객실 카드 배지도 즉시 다시 렌더링된다.",
    "## 객실 카드 숙박 인원 표시 (2026-08-23)\n\n"
    "- 카드가 현재 보여 주는 예약의 총 숙박 인원이 객실 타입별 기준인원보다 많을 때만 `N명` 배지를 표시한다.\n"
    "- 초과분을 `+N명`으로 쓰지 않고, 현장에서 준비해야 할 실제 총인원을 그대로 보여 준다.\n"
    "- 객실 상태 필터의 `인원 추가`는 같은 조건의 객실만 표시하며, 예약 인원 수정 저장 뒤 카드와 필터 결과가 함께 즉시 갱신된다.",
)

qa = ROOT / "WIREFRAME/QA.md"
append_once(
    qa,
    "## 2026-08-23 · 기준인원 초과 배지와 인원 추가 필터",
    """## 2026-08-23 · 기준인원 초과 배지와 인원 추가 필터

### 변경

- 객실 카드의 숙박 인원 배지는 카드가 표시하는 예약의 총인원이 객실 타입별 기준인원보다 많을 때만 노출한다.
- 초과 인원 수가 아니라 현장 준비 기준이 되는 실제 총인원을 `N명`으로 표시한다.
- 객실 상태 필터에 `인원 추가`를 넣고 카드 배지와 동일한 판정 함수를 사용한다.
- 여러 유효 예약이 있는 객실은 카드와 마찬가지로 현재 또는 가장 가까운 예약 한 건만 판정한다.

### 검증

- `node scripts/check-workspace.mjs` 정적 계약 및 인라인 JavaScript 구문 검사를 통과했다.
- Chrome headless에서 기준 4명인 142호가 총 4명일 때 배지가 없고, 5명으로 수정하면 `5명` 배지가 생기는 것을 확인했다.
- `인원 추가` 필터에서 142호만 남고 기준인원 예약 객실은 제외되는 것을 확인했다.
- 142호를 다시 4명으로 수정하면 배지가 사라지고 `인원 추가` 필터 결과도 즉시 빈 상태로 바뀌는 것을 확인했다.
- 관리자 객실 목록을 360·390·768·1440px에서 확인해 가로 넘침과 브라우저 콘솔·런타임 오류가 없었다.
- 대표 화면: `WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-390.png`, `WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-1440.png`.

### 한계

- 데모 와이어프레임의 브라우저 메모리 상태를 검증한 결과이며 실제 OTA/PMS·백엔드 동기화를 구현한 것은 아니다.
""",
)

checks = ROOT / "scripts/check-workspace.mjs"
replace_exact(
    checks,
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-assignment-elevator-1440.png',",
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-1440.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-assignment-elevator-1440.png',",
)
replace_exact(
    checks,
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-cleaning-day-tabs-1440.png',",
    "  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-1440.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-390.png',\n"
    "  'WIREFRAME/QA/screenshots/admin-cleaning-day-tabs-1440.png',",
)

old_contract = """for (const contract of [
  '.schedule-priority-badge.guests { background:#17314a;',
  'const cardGuestCount=closestReservation?reservationGuestCount(closestReservation):null;',
  'class=\"schedule-priority-badge guests\" aria-label=\"숙박 인원 ${cardGuestCount}명\"',
  \"${icon('user','icon-sm')}${cardGuestCount}명\",
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
new_contract = """for (const contract of [
  '.schedule-priority-badge.guests { background:#17314a;',
  'function reservationHasExtraGuests(reservation)',
  'reservationGuestCount(reservation)>guestPolicyForRoom(reservation.room).defaultGuestCount',
  'function roomHasExtraGuests(no)',
  'const reservation=activeReservationsFor(state,String(no)).find(item=>!reservationRecordIsPast(item))||null;',
  'const cardGuestCount=closestReservation&&reservationHasExtraGuests(closestReservation)?reservationGuestCount(closestReservation):null;',
  \"if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);\",
  \"'occupied','extra-guests','candle'\",
  'value=\"extra-guests\"',
  '>인원 추가</option>',
  'class=\"schedule-priority-badge guests\" aria-label=\"숙박 인원 ${cardGuestCount}명\"',
  \"${icon('user','icon-sm')}${cardGuestCount}명\",
]) {
  if (!html.includes(contract)) throw new Error(`Room-card extra-guest/filter contract missing: ${contract}`);
}
const roomCardPolicy = readFileSync(resolve(root, 'DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md'), 'utf8');
for (const contract of [
  '기준인원보다 많을 때만',
  '`+N명`처럼 초과분만 표시하지 않으며',
  '객실 상태 필터의 `인원 추가`는 이 동일한 조건',
]) {
  if (!roomCardPolicy.includes(contract)) throw new Error(`Room-card extra-guest/filter policy missing: ${contract}`);
}
"""
replace_exact(checks, old_contract, new_contract)

index_hash = hashlib.sha256(index.read_bytes()).hexdigest()
final_audit = ROOT / "DOCS/FINAL_UX_AUDIT.md"
final_hash = hashlib.sha256(final_audit.read_bytes()).hexdigest()
(ROOT / "SHA256SUMS.txt").write_text(
    f"{final_hash}  DOCS/FINAL_UX_AUDIT.md\n{index_hash}  WIREFRAME/index.html\n",
    encoding="utf-8",
)
manifest_path = ROOT / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-23-room-extra-guest-filter"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).replace(microsecond=0).isoformat()
manifest.setdefault("sha256", {})["DOCS/FINAL_UX_AUDIT.md"] = final_hash
manifest["sha256"]["WIREFRAME/index.html"] = index_hash
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Patched over-base guest badge and the matching room status filter.")
