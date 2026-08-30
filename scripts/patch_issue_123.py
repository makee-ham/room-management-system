#!/usr/bin/env python3
"""Apply issue #123: simplify login and permit current-stay extensions from past weeks."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "WIREFRAME/index.html"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


html = INDEX.read_text(encoding="utf-8")

# Login: keep only the brand, form, error state, credentials hint, and submit action.
html = replace_once(
    html,
    """    .auth-role-card { display:flex; align-items:flex-start; gap:12px; padding:13px 14px; border:1px solid var(--line); border-radius:14px; background:var(--surface-soft); }
    .auth-role-card strong { display:block; color:var(--ink); }
    .auth-role-card span { display:block; margin-top:3px; color:var(--muted); font-size:.85rem; line-height:1.45; }
""",
    "",
    "remove obsolete login role-card styles",
)

old_login = r'''      function renderLogin() {
        const error=state.loginMode==='error';
        return `<main id="main-content" style="max-width:480px;padding-top:7vh"><section class="card card-pad" style="box-shadow:var(--shadow)"><div class="brand" style="padding:4px 0 22px"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리 로그인</div></div></div><div class="notice notice-info"><div><strong>아이디에 따라 화면이 분리됩니다.</strong><br>관리자는 관리자 화면만, 메이드는 본인 업무 화면만 이용합니다.</div></div>${error?'<div class="notice notice-danger auth-error" role="alert">아이디 또는 비밀번호가 일치하지 않습니다.</div>':''}<form id="login-form" style="display:grid;gap:12px;margin-top:16px"><div class="field"><label for="login-id">로그인 아이디</label><input id="login-id" class="input-control" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="admin 또는 maid1" required></div><div class="field"><label for="login-password">로그인 비밀번호</label><input id="login-password" class="input-control" type="password" autocomplete="current-password" required><small>와이어프레임: 관리자 admin / admin1234 · 메이드 maid1~maid9 / maid1234</small></div><button class="btn btn-primary btn-block" type="submit">로그인</button></form><div class="auth-role-card" style="margin-top:14px">${icon('shield')}<div><strong>역할 간 직접 전환 없음</strong><span>다른 역할은 로그아웃한 뒤 해당 아이디로 다시 로그인합니다.</span></div></div></section></main>`;
      }'''
new_login = r'''      function renderLogin() {
        const error=state.loginMode==='error';
        return `<main id="main-content" style="max-width:480px;padding-top:7vh"><section class="card card-pad" style="box-shadow:var(--shadow)"><div class="brand" style="padding:4px 0 22px"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리 로그인</div></div></div>${error?'<div class="notice notice-danger auth-error" role="alert">아이디 또는 비밀번호가 일치하지 않습니다.</div>':''}<form id="login-form" style="display:grid;gap:12px;margin-top:${error?'16px':'0'}"><div class="field"><label for="login-id">로그인 아이디</label><input id="login-id" class="input-control" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="admin 또는 maid1" required></div><div class="field"><label for="login-password">로그인 비밀번호</label><input id="login-password" class="input-control" type="password" autocomplete="current-password" required><small>와이어프레임: 관리자 admin / admin1234 · 메이드 maid1~maid9 / maid1234</small></div><button class="btn btn-primary btn-block" type="submit">로그인</button></form></section></main>`;
      }'''
html = replace_once(html, old_login, new_login, "simplify login renderer")

# Current-stay policy: an active reservation remains editable when the room is still
# occupied, even if its scheduled checkout or source week has already passed.
old_past = r'''      function reservationRecordIsPast(reservation) {
        if(!reservation)return false;
        if(reservation.status!=='active')return true;
        const room=ROOMS.find(item=>item.no===reservation.room);
        if(room?.occupancy==='occupied'&&currentOccupiedReservation(room)?.id===reservation.id)return false;
        return reservation.checkOutAt<=reservationCurrentMoment();
      }'''
new_past = r'''      function reservationCanEditCurrentStay(reservation,room=ROOMS.find(item=>item.no===reservation?.room)) {
        if(!reservation||reservation.status!=='active'||!room||room.occupancy!=='occupied')return false;
        const now=reservationCurrentMoment();
        if(reservation.checkInAt>now)return false;
        if(room.currentStayReservationId===reservation.id||room.reservationProjectionId===reservation.id)return true;
        if(currentOccupiedReservation(room)?.id===reservation.id)return true;
        const latestStarted=activeReservationsFor(state,room.no).filter(item=>item.checkInAt<=now).sort((left,right)=>right.checkInAt.localeCompare(left.checkInAt)||right.id.localeCompare(left.id))[0]||null;
        return latestStarted?.id===reservation.id;
      }
      function reservationRecordIsPast(reservation) {
        if(!reservation)return false;
        if(reservation.status!=='active')return true;
        const room=ROOMS.find(item=>item.no===reservation.room);
        if(reservationCanEditCurrentStay(reservation,room))return false;
        return reservation.checkOutAt<=reservationCurrentMoment();
      }'''
html = replace_once(html, old_past, new_past, "add editable current-stay policy")

# Past-week schedule rows remain clickable only for the currently occupied stay.
html = replace_once(
    html,
    "records=buckets.weekRecords,countLabel=",
    "records=buckets.weekRecords,editablePastStay=nextRegistration.weekPast&&records.some(reservation=>reservationCanEditCurrentStay(reservation,room)),countLabel=",
    "derive editable past-week stay",
)
html = replace_once(
    html,
    "const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=",
    "const readOnly=(nextRegistration.weekPast||reservationRecordIsPast(reservation))&&!reservationCanEditCurrentStay(reservation,room),assignment=",
    "keep current stay clickable in past week",
)
html = replace_once(
    html,
    "${nextRegistration.weekPast?`<p class=\"reservation-week-note\">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}",
    "${nextRegistration.weekPast?`<p class=\"reservation-week-note\">${icon(editablePastStay?'edit':'lock','icon-sm')}${editablePastStay?'투숙 중 예약은 수정 가능 · 종료된 기록은 조회만 가능':'지난 예약 기록 · 조회만 가능'}</p>`:''}",
    "explain past-week current-stay exception",
)

# Reservation modal: current-entry and current-stay edits are not locked merely
# because the selected week is in the past.
html = replace_once(
    html,
    "requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id",
    "requestedCurrentStay=!!requested&&reservationCanEditCurrentStay(requested,room)",
    "resolve current stay with extension policy",
)
html = replace_once(
    html,
    "weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),",
    "weekPast=reservationWeekIsPast(selectedWeek),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),editableCurrentStay=!!existing&&reservationCanEditCurrentStay(existing,room),readOnly=weekPast&&!currentEntry&&!editableCurrentStay||!!existing&&reservationRecordIsPast(existing)&&!editableCurrentStay,",
    "allow current stay modal in past week",
)
html = replace_once(
    html,
    "editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id",
    "editingCurrentStay=editableCurrentStay",
    "reuse editable current-stay state",
)

# Upsert must treat an overdue active stay in an occupied room as linked to the
# current guest, so its original past check-in may stay unchanged while checkout
# moves into the future.
html = replace_once(
    html,
    "linkedCurrentStay=!!before&&room.occupancy==='occupied'&&currentOccupiedReservation(room)?.id===before.id",
    "linkedCurrentStay=!!before&&reservationCanEditCurrentStay(before,room)",
    "link overdue occupied reservation",
)

# Save guard: past weeks remain locked for ordinary/history records, but not for
# current-stay entry or an active occupied reservation being extended.
html = replace_once(
    html,
    "const reservationId=document.getElementById('res-id')?.value||'',existing=reservationId?state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null:null,no=existing?.room||document.getElementById('res-room')?.value||'211',room=ROOMS.find(item=>item.no===no);",
    "const reservationId=document.getElementById('res-id')?.value||'',existing=reservationId?state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null:null,no=existing?.room||document.getElementById('res-room')?.value||'211',room=ROOMS.find(item=>item.no===no),currentStay=document.getElementById('res-current-stay')?.value==='1',editableCurrentStay=reservationCanEditCurrentStay(existing,room);",
    "read current-stay policy before save guard",
)
html = replace_once(
    html,
    "if(reservationWeekIsPast()||reservationRecordIsPast(existing)){closeModal();render();toast('지난 예약 기록은 조회만 가능하며 수정할 수 없습니다.','error');return;}",
    "if((reservationWeekIsPast()||reservationRecordIsPast(existing))&&!currentStay&&!editableCurrentStay){closeModal();render();toast('종료된 예약 기록은 조회만 가능하며 수정할 수 없습니다.','error');return;}",
    "permit current stay save from past week",
)
html = replace_once(
    html,
    "guestCount=document.getElementById('res-guests')?.value??'',currentStay=document.getElementById('res-current-stay')?.value==='1';",
    "guestCount=document.getElementById('res-guests')?.value??'';",
    "avoid duplicate current-stay declaration",
)

INDEX.write_text(html, encoding="utf-8")

# Permanent regression checker.
checker = r'''#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const html=readFileSync(resolve('WIREFRAME/index.html'),'utf8');

for(const removed of [
  '아이디에 따라 화면이 분리됩니다.',
  '관리자는 관리자 화면만, 메이드는 본인 업무 화면만 이용합니다.',
  '역할 간 직접 전환 없음',
  '다른 역할은 로그아웃한 뒤 해당 아이디로 다시 로그인합니다.',
  '.auth-role-card {',
]){
  if(html.includes(removed))throw new Error(`Issue #123 removed login copy remains: ${removed}`);
}

for(const required of [
  'id="login-form"',
  '와이어프레임: 관리자 admin / admin1234 · 메이드 maid1~maid9 / maid1234',
  'function reservationCanEditCurrentStay(reservation,room=',
  'latestStarted?.id===reservation.id',
  'if(reservationCanEditCurrentStay(reservation,room))return false',
  "requestedCurrentStay=!!requested&&reservationCanEditCurrentStay(requested,room)",
  'editableCurrentStay=!!existing&&reservationCanEditCurrentStay(existing,room)',
  'readOnly=weekPast&&!currentEntry&&!editableCurrentStay',
  "const readOnly=(nextRegistration.weekPast||reservationRecordIsPast(reservation))&&!reservationCanEditCurrentStay(reservation,room)",
  "linkedCurrentStay=!!before&&reservationCanEditCurrentStay(before,room)",
  "if((reservationWeekIsPast()||reservationRecordIsPast(existing))&&!currentStay&&!editableCurrentStay)",
  "checkInAt<=now&&(openEndedLongStay||checkOutAt>now)",
  '투숙 중 예약은 수정 가능 · 종료된 기록은 조회만 가능',
]){
  if(!html.includes(required))throw new Error(`Issue #123 contract missing: ${required}`);
}

const inlineScripts=[...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(match=>match[1]);
if(!inlineScripts.length)throw new Error('No inline application script found.');
for(const script of inlineScripts)new Function(script);
console.log('Issue #123 login and current-stay extension contracts verified.');
'''
(ROOT / "scripts/check-issue-123.mjs").write_text(checker, encoding="utf-8")

append_once(
    ROOT / "WIREFRAME/QA.md",
    "## Issue #123 · 로그인 간소화와 투숙 중 예약 연장",
    """
## Issue #123 · 로그인 간소화와 투숙 중 예약 연장

- [ ] 로그인 화면에서 상단 역할 안내 블록과 하단 역할 전환 안내 카드가 보이지 않는다.
- [ ] 브랜드, 로그인 아이디·비밀번호, 데모 계정 안내, 로그인 버튼과 오류 메시지는 그대로 동작한다.
- [ ] 이전 날짜에 체크인한 현재 투숙 고객의 활성 예약은 지난 주차에서도 열리고 수정된다.
- [ ] 예정 체크아웃이 지났지만 객실이 계속 `투숙 중`이면 체크아웃을 미래로 연장할 수 있다.
- [ ] 예약 정보가 없던 투숙 중 객실은 과거 실제 체크인과 미래 체크아웃 또는 종료일 미정 장기 투숙으로 저장할 수 있다.
- [ ] 종료·취소된 과거 예약과 임의의 과거 신규 예약은 계속 읽기 전용 또는 저장 차단된다.
- [ ] 연장 일정이 다음 예약 또는 공개된 퇴실 청소와 충돌하면 기존 충돌 보호가 유지된다.
""",
)
append_once(
    ROOT / "WIREFRAME/README.md",
    "## 투숙 중 예약의 과거 일정 수정",
    """
## 투숙 중 예약의 과거 일정 수정

이미 입실한 고객의 활성 예약은 체크인 날짜나 예약 주차가 지났더라도 객실이 실제 `투숙 중`인 동안 열어 수정할 수 있습니다. 예정 체크아웃이 지난 고객도 새 종료 일시를 미래로 연장할 수 있고, 예약 정보가 없던 투숙 객실은 실제 과거 체크인 일시부터 등록할 수 있습니다. 다만 완료·취소된 예약 기록과 투숙 사실이 없는 임의의 과거 신규 예약은 계속 수정·등록할 수 없습니다.
""",
)

# Refresh canonical manifest and checksums.
index_hash = hashlib.sha256(INDEX.read_bytes()).hexdigest()
manifest_path = ROOT / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-30-issue-123-login-reservation-extension"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = index_hash
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sums_path = ROOT / "SHA256SUMS.txt"
refreshed: list[str] = []
for raw in sums_path.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    _, rel = raw.split(None, 1)
    tracked = ROOT / rel
    if not tracked.exists():
        raise RuntimeError(f"SHA256 tracked path missing: {rel}")
    refreshed.append(f"{hashlib.sha256(tracked.read_bytes()).hexdigest()}  {rel}")
sums_path.write_text("\n".join(refreshed) + "\n", encoding="utf-8")

print("Applied issue #123 login cleanup and current-stay extension policy.")
