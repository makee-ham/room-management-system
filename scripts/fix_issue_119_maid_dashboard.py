#!/usr/bin/env python3
"""Restore the latest maid work dashboard after the issue #119 schedule rewrite.

Also tightens optional long-stay end-date behavior:
- open-ended stays block future reservations;
- known-end stays allow reservations after the end;
- a new long-stay toggle starts with an empty optional end field;
- accessible reservation copy says 장기 instead of 0박.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "WIREFRAME/index.html"
CHECK_PATH = ROOT / "scripts/check-issue-119.mjs"
MANIFEST_PATH = ROOT / "manifest.json"
SUMS_PATH = ROOT / "SHA256SUMS.txt"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    require(count == 1, f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


html = HTML_PATH.read_text(encoding="utf-8")
schedule_index = html.rfind("      function renderMaidSchedule()")
alerts_marker = "      function renderMaidAlerts(){"
alerts_index = html.rfind(alerts_marker)
require(schedule_index >= 0 and alerts_index > schedule_index, "latest maid schedule/alerts range not found")
latest_range = html[schedule_index:alerts_index]
require("function renderMaidMy()" not in latest_range, "latest maid work dashboard is already restored")

maid_dashboard = r'''      function publicJobCard(no) {
        const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room?.type||'standard'];
        return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${esc(cleaningLabel(state.jobs[no]))}</h3><p>${esc(type.name)}</p></div>${statusBadge('관리자 배정','green')}</div><div class="schedule-line">${icon('clock','icon-sm')}<span>시작 가능 ${startTimeFor(no)} · 담당 ${esc(room?.assignee||'미정')}</span></div><div class="notice notice-info" style="margin:0">메이드는 관리자에게 통보받은 업무만 확인하고 수행할 수 있습니다.</div></article>`;
      }
      function renderMaidOpen() {
        return renderMaidSchedule();
      }
      function myJobCard(no) {
        const job=state.jobs[no], room=ROOMS.find(r=>r.no===no),attempt=state.cleaningAttempts?.[currentAttemptId(no)],access=attemptAccessStatus(no,attempt),start=access.start,reached=access.allowed,rollover=rolloverMetaForRoom(no);
        const guestCount=guestCountForAttempt(attempt),guestCountDisplay=guestCount?guestCountLabel(guestCount):'미기록',reclean=attempt?.kind==='재청소'?{reason:attempt.reason||'전체 반려 뒤 본인 재청소',previousMaid:currentSubmission(no)?.performerName||room?.assignee||'기존 메이드',originalKind:currentSubmission(no)?.kind||'퇴실 청소'}:null;
        const labels={scheduled:reached?'일 시작':'시작 시각 대기',claimed:reached?'일 시작':'시작 시각 대기',cleaning:'계속 청소',upload:taskState(no).uploads.some(u=>u.status==='failed')?'미전송 재시도':'청소 전체 제출',inspection:'제출 결과 보기',approved:'완료 결과 보기',reclean:reached?'재청소 시작':'시작 시각 대기'};
        const action='cleaning-detail';
        const bomb=bombRoomReport(no),bombMeta=bombRoomStatusMeta(bomb),tone=job==='approved'?'green':job==='cleaning'||job==='upload'?'amber':job==='inspection'?'blue':'neutral';
        return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${reclean?'재청소':cleaningLabel(job)}</h3><p>${esc(ROOM_TYPES[room?.type||'standard'].name)}</p></div><div class="badge-row">${statusBadge(statusLabel(job),tone)}${bomb?statusBadge(bombMeta.label,bombMeta.tone):''}</div></div>${rolloverBadgeMarkup(rollover,{compact:true})}<div class="schedule-line">${icon('clock','icon-sm')}<span>${job==='upload'?'현장 완료 · 사진 전송·전체 제출 필요':job==='cleaning'&&rollover?'계속 청소 가능':`시작 가능 ${start} · ${reached?'지금 시작 가능':esc(access.reason)}`}</span></div><div class="schedule-line">${icon('user','icon-sm')}<span>숙박 인원 ${guestCountDisplay}</span></div>${reclean?`<div class="job-meta"><div><span>재청소 요금</span><strong>0원 · 무급</strong></div><div><span>원 작업</span><strong>${no}호 ${esc(reclean.originalKind)}</strong></div></div><div class="notice notice-warning" style="margin:0"><div>처음 청소한 ${esc(reclean.previousMaid)} 본인에게 자동 배정 · 다른 메이드에게 넘길 수 없음 · ${esc(reclean.reason)}</div></div>`:''}<button class="btn ${job==='upload'&&taskState(no).uploads.some(u=>u.status==='failed')?'btn-danger':'btn-primary'} btn-block" type="button" data-action="${action}" data-id="${no}">${labels[job]||'상세 보기'}</button></article>`;
      }
      function renderMaidMy() {
        const maidId=signedInMaidId(),maidName=signedInMaidName(),activeCleaning=activeCleaningFor(maidId),own=Object.entries(state.jobs).filter(([no,v])=>['scheduled','claimed','cleaning','upload','inspection','approved','reclean'].includes(v)&&(ROOMS.find(r=>r.no===no)?.assignee===maidName||(['inspection','approved'].includes(v)&&currentSubmission(no)?.performerId===maidId))).map(([no])=>no);
        const upcoming=notifiedAssignmentEntriesForMaid(maidId);
        const upcomingNotice=upcoming.length?`<div class="assignment-notice">${icon('bell')}<div><p><strong>통보된 청소 일정 ${upcoming.length}건</strong><br>오늘·내일 날짜와 관리자가 확정한 순서입니다.</p><ol class="maid-assignment-route">${upcoming.map(({item,assignment})=>`<li><b>${assignment.order}</b><span>${esc(dateLabel(targetEffectiveDate(item)))} · ${item.room}호 · ${esc(item.kind)} · ${esc(assignmentScheduleText(item))}${assignment.activationBlockedBy?' · 관리자 확인 대기':''}</span></li>`).join('')}</ol></div></div>`:'';
        return renderCoach()+renderNetworkNotice()+`<div class="view-stack">${upcomingNotice}<section class="card work-hero"><span>${esc(maidName)} 현재 작업 상태</span><strong>${activeCleaning?`${activeCleaning}호 청소 중`:'청소 중 없음'}</strong><p>관리자에게 배정·통보된 업무만 표시합니다. 동시에 청소 중 한 건만 가능합니다.</p></section><div class="mobile-section-title"><div><h2>내 업무 ${own.length}건</h2><p>담당 확정부터 검수 결과까지 이어집니다.</p></div></div>${renderListState(own.length?`<div class="job-list">${own.map(myJobCard).join('')}</div>`:`<section class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 오늘·내일 배정을 통보하면 내 업무와 상단 알림에 표시됩니다.</p>${button('근무 가능일 확인','go-schedule','primary')}</section>`)}</div>`;
      }

'''
html = html[:alerts_index] + maid_dashboard + html[alerts_index:]

html = replace_once(
    html,
    "        if(roomHasActiveLongStay(room.no))return '장기 투숙 · 예약 불가';",
    "        if(roomHasOpenEndedLongStay(room.no))return '장기 투숙 · 종료일 미정 · 예약 불가';",
    "known-end long-stay future booking",
)
html = replace_once(
    html,
    """      function occupiedReservationEnd(room) {
        const current=currentOccupiedReservation(room);
        return room?.actualCheckoutAt||room?.plannedCheckoutAt||current?.checkOutAt||'';
      }""",
    """      function occupiedReservationEnd(room) {
        const current=currentOccupiedReservation(room);
        if(reservationIsLongStay(current)&&!reservationHasKnownEnd(current))return '';
        return room?.actualCheckoutAt||room?.plannedCheckoutAt||current?.checkOutAt||'';
      }""",
    "open-ended occupied stay end",
)
html = replace_once(
    html,
    "aria-label=\"${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}\"",
    "aria-label=\"${esc(`${quickRangeLabel(reservation)} ${reservationStayLengthLabel(reservation)} ${reservationGuestCount(reservation)}명 ${status}`)}\"",
    "long-stay accessible reservation label",
)
html = replace_once(
    html,
    "        if(c==='reservation-long-stay'){updateReservationTimePreview();return;}",
    "        if(c==='reservation-long-stay'){const checkout=document.getElementById('res-checkout'),existingId=document.getElementById('res-id')?.value||'';if(e.target.checked&&!existingId&&checkout)checkout.value='';updateReservationTimePreview();return;}",
    "new long-stay optional end default",
)
HTML_PATH.write_text(html, encoding="utf-8")

check = CHECK_PATH.read_text(encoding="utf-8")
check = replace_once(
    check,
    '  "reservationLongStayEndLabel(reservation)?",',
    "  'reservationLongStayEndLabel(reservation)',",
    "clean issue 119 long-stay check marker",
)
check = replace_once(
    check,
    "for(const contract of required){if(!html.includes(contract.replace('reservationLongStayEndLabel(reservation)?','reservationLongStayEndLabel(reservation)')))throw new Error(`Issue #119 contract missing: ${contract}`);}",
    "for(const contract of required){if(!html.includes(contract))throw new Error(`Issue #119 contract missing: ${contract}`);}",
    "simplify issue 119 contract loop",
)
order_check = r'''
const maidScheduleIndex=html.lastIndexOf('function renderMaidSchedule()');
const publicJobIndex=html.lastIndexOf('function publicJobCard(no)');
const maidOpenIndex=html.lastIndexOf('function renderMaidOpen()');
const myJobIndex=html.lastIndexOf('function myJobCard(no)');
const maidMyIndex=html.lastIndexOf('function renderMaidMy()');
const maidAlertsIndex=html.lastIndexOf('function renderMaidAlerts()');
if(!(maidScheduleIndex>=0&&maidScheduleIndex<publicJobIndex&&publicJobIndex<maidOpenIndex&&maidOpenIndex<myJobIndex&&myJobIndex<maidMyIndex&&maidMyIndex<maidAlertsIndex)){
  throw new Error('Latest maid schedule rewrite must retain the maid work dashboard functions before the alerts helper.');
}
if(!html.includes("if(roomHasOpenEndedLongStay(room.no))return '장기 투숙 · 종료일 미정 · 예약 불가';")){
  throw new Error('Only open-ended long stays may block all future reservation dates.');
}
'''
check = replace_once(
    check,
    "const inlineScripts=[...html.matchAll(/<script\\b(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)<\\/script>/gi)].map(match=>match[1]);",
    order_check + "\nconst inlineScripts=[...html.matchAll(/<script\\b(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)<\\/script>/gi)].map(match=>match[1]);",
    "maid dashboard regression check",
)
CHECK_PATH.write_text(check, encoding="utf-8")

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
manifest["generated_at_kst"] = "2026-08-30T02:35:00+09:00"
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = hashlib.sha256(HTML_PATH.read_bytes()).hexdigest()
MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

refreshed: list[str] = []
for raw in SUMS_PATH.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    _, rel = raw.split(None, 1)
    path = ROOT / rel
    require(path.exists(), f"SHA256 tracked path missing: {rel}")
    refreshed.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
SUMS_PATH.write_text("\n".join(refreshed) + "\n", encoding="utf-8")

print("Restored the latest maid dashboard and tightened optional long-stay end behavior.")
