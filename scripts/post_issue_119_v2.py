#!/usr/bin/env python3
"""Post-process duplicate legacy markup and update issue #119 validation policy."""
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

# Issue #119 intentionally replaces the old implicit occupancy-only model with an
# explicit long-stay reservation type. Keep rejecting deprecated fixed room lists,
# but require the new optional-end-date model instead of rejecting every mention of
# long stay.
check_path = ROOT / "scripts/check-workspace.mjs"
check = check_path.read_text(encoding="utf-8")
old_check = """if (/LONG_STAY_(?:ROOMS|ENDED_ROOMS)|long-?stay|장기투숙/i.test(html)) {
  throw new Error('Legacy long-stay UI or state contracts remain in WIREFRAME/index.html.');
}"""
new_check = """if (/LONG_STAY_(?:ROOMS|ENDED_ROOMS)/.test(html)) {
  throw new Error('Deprecated fixed long-stay room lists remain in WIREFRAME/index.html.');
}
for (const contract of [
  \"const LONG_STAY_OPEN_END_AT='9999-12-31T23:59'\",
  'function reservationIsLongStay(reservation)',
  'function reservationHasKnownEnd(reservation)',
  'function reservationLongStayEndLabel(reservation)',
  'data-control=\"reservation-long-stay\"',
  '종료일 미정',
]) {
  if (!html.includes(contract)) throw new Error(`Long-stay contract missing: ${contract}`);
}"""
if check.count(old_check) != 1:
    raise RuntimeError(f"workspace long-stay policy: expected 1 match, found {check.count(old_check)}")
check = check.replace(old_check, new_check, 1)

old_room_card_contract = "  \"reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`\","
new_room_card_contract = "  \"reservationActionLabel=room.longStay?'장기 투숙 관리':weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`\","
if check.count(old_room_card_contract) != 1:
    raise RuntimeError(f"room-card long-stay validation: expected 1 match, found {check.count(old_room_card_contract)}")
check = check.replace(old_room_card_contract, new_room_card_contract, 1)

old_checkout_label = "const reservationCheckoutLabel = '<label for=\"res-checkout\">2. 체크아웃 일시</label>';"
new_checkout_label = "const reservationCheckoutLabel = '<label for=\"res-checkout\" data-res-checkout-label>';"
if check.count(old_checkout_label) != 1:
    raise RuntimeError(f"reservation checkout label validation: expected 1 match, found {check.count(old_checkout_label)}")
check = check.replace(old_checkout_label, new_checkout_label, 1)

old_guest_fingerprint = "  'reservationGuestCount(reservation),reservation.status',"
new_guest_fingerprint = "  \"reservationGuestCount(reservation),reservationIsLongStay(reservation)?'long':'dated',reservation.status\","
if check.count(old_guest_fingerprint) != 1:
    raise RuntimeError(f"reservation fingerprint validation: expected 1 match, found {check.count(old_guest_fingerprint)}")
check = check.replace(old_guest_fingerprint, new_guest_fingerprint, 1)
check_path.write_text(check, encoding="utf-8")

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

print("Removed stale role-switch markup and updated issue #119 workspace validation.")
