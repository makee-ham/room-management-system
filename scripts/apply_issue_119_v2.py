#!/usr/bin/env python3
"""Apply issue #119 to the single-file wireframe.

The script is intentionally self-checking because WIREFRAME/index.html is a large,
framework-free HTML application. It edits the active (last) function definitions
and fails instead of silently producing a partial implementation.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "WIREFRAME/index.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    require(count == 1, f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


def replace_last(text: str, old: str, new: str, label: str) -> str:
    index = text.rfind(old)
    require(index >= 0, f"{label}: source marker not found")
    return text[:index] + new + text[index + len(old):]


def replace_last_block(text: str, start: str, end: str, new: str, label: str) -> str:
    begin = text.rfind(start)
    require(begin >= 0, f"{label}: start marker not found")
    finish = text.find(end, begin + len(start))
    require(finish >= 0, f"{label}: end marker not found")
    return text[:begin] + new.rstrip() + "\n\n" + text[finish:]


def regex_once(text: str, pattern: str, replacement: str, label: str, flags: int = re.S) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    require(count == 1, f"{label}: expected 1 regex match, found {count}")
    return updated


html = HTML_PATH.read_text(encoding="utf-8")
require("Issue #119 v2 role/session contract" not in html, "issue #119 v2 is already applied")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
css = r'''

    /* Issue #119 v2 role/session contract */
    .auth-role-card { display:flex; align-items:flex-start; gap:12px; padding:13px 14px; border:1px solid var(--line); border-radius:14px; background:var(--surface-soft); }
    .auth-role-card strong { display:block; color:var(--ink); }
    .auth-role-card span { display:block; margin-top:3px; color:var(--muted); font-size:.85rem; line-height:1.45; }
    .auth-error { margin-top:14px; }
    .demo-auth-role { min-width:180px; }
    .demo-auth-role strong { display:block; font-size:.9rem; }
    .assignment-availability-disclosure, .weekly-availability-disclosure { overflow:visible; }
    .assignment-availability-disclosure > summary, .weekly-availability-disclosure > summary { list-style:none; cursor:pointer; }
    .assignment-availability-disclosure > summary::-webkit-details-marker, .weekly-availability-disclosure > summary::-webkit-details-marker { display:none; }
    .assignment-availability-disclosure .disclosure-chevron, .weekly-availability-disclosure .disclosure-chevron { display:inline-flex; transition:transform .2s ease; }
    .assignment-availability-disclosure[open] .disclosure-chevron, .weekly-availability-disclosure[open] .disclosure-chevron { transform:rotate(180deg); }
    .assignment-disclosure-body, .weekly-availability-body { padding:0 20px 20px; }
    .assignment-room-type-link { display:inline; margin:0; padding:0; border:0; background:none; color:inherit; font:inherit; text-align:left; text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:3px; cursor:pointer; }
    .assignment-room-type-link:hover, .assignment-room-type-link:focus-visible { color:var(--blue); }
    button.maid-order-unassigned-chip { font:inherit; cursor:pointer; }
    button.maid-order-unassigned-chip:hover, button.maid-order-unassigned-chip:focus-visible { border-color:var(--blue); box-shadow:0 0 0 3px rgba(40,108,168,.14); }
    .assignment-table tr.is-focus-target > td { animation:issue119-row-focus 1.9s ease; }
    @keyframes issue119-row-focus { 0%,100%{background:transparent} 18%,72%{background:#fff3d9} }
    .reservation-long-stay-toggle { display:flex; align-items:flex-start; gap:11px; padding:14px; border:1px solid var(--line); border-radius:14px; background:var(--surface-soft); }
    .reservation-long-stay-toggle input { width:20px; height:20px; margin-top:2px; accent-color:var(--blue); }
    .reservation-long-stay-toggle strong, .reservation-long-stay-toggle span { display:block; }
    .reservation-long-stay-toggle span span { margin-top:3px; color:var(--muted); font-size:.86rem; line-height:1.45; }
    .long-stay-badge { background:#efe7ff; color:#5941a9; border-color:#d9ccff; }
    @media (max-width:720px) {
      .assignment-disclosure-body, .weekly-availability-body { padding:0 14px 14px; }
    }
'''
html = replace_once(html, "\n  </style>", css + "\n  </style>", "insert issue 119 CSS")

# ---------------------------------------------------------------------------
# Long-stay data model: optional end date
# ---------------------------------------------------------------------------
html = replace_once(
    html,
    "      const INITIAL_RESERVATIONS = Object.freeze([",
    """      const LONG_STAY_OPEN_END_AT='9999-12-31T23:59';
      const INITIAL_LONG_STAY_RESERVATIONS=Object.freeze(Object.entries(INITIAL_OCCUPIED_ROOMS).map(([room,stay])=>({
        id:`reservation-long-${room}`,room,checkInAt:`${stay.startedAt||'2026-01-01'}T00:00`,checkOutAt:LONG_STAY_OPEN_END_AT,
        guestCount:guestPolicyForRoom(room).defaultGuestCount,source:'long-stay',status:'active',isLongStay:true
      })));
      const INITIAL_RESERVATIONS = Object.freeze([
        ...INITIAL_LONG_STAY_RESERVATIONS,""",
    "seed existing long-stay rooms",
)
html = replace_once(
    html,
    "      function initialReservationDrafts(){return INITIAL_RESERVATIONS.map(reservation=>({id:`checkout-${reservation.id}`,room:reservation.room,kind:'퇴실 청소',created:'예약 연동',date:reservation.checkOutAt.slice(0,10),source:'reservation',reservationId:reservation.id,guestCount:reservationGuestCount(reservation),visibility:'private'}));}",
    "      function initialReservationDrafts(){return INITIAL_RESERVATIONS.filter(reservation=>!reservationIsLongStay(reservation)||reservationHasKnownEnd(reservation)).map(reservation=>({id:`checkout-${reservation.id}`,room:reservation.room,kind:'퇴실 청소',created:'예약 연동',date:reservation.checkOutAt.slice(0,10),source:'reservation',reservationId:reservation.id,guestCount:reservationGuestCount(reservation),visibility:'private'}));}",
    "long-stay initial cleaning drafts",
)
html = replace_once(
    html,
    "      function reservationCurrentMoment() { return `${state.selectedDate}T${state.time}`; }",
    """      function reservationIsLongStay(reservation){return reservation?.isLongStay===true;}
      function reservationHasKnownEnd(reservation){return reservationIsLongStay(reservation)&&!!reservation.checkOutAt&&reservation.checkOutAt!==LONG_STAY_OPEN_END_AT;}
      function reservationLongStayEndLabel(reservation){return reservationHasKnownEnd(reservation)?reservationMomentLabel(reservation.checkOutAt):'종료일 미정';}
      function reservationStayLengthLabel(reservation){return reservationIsLongStay(reservation)?'장기':`${reservationNights(reservation)}박`;}
      function roomHasOpenEndedLongStay(no,targetState=state){return activeReservationsFor(targetState,String(no)).some(item=>reservationIsLongStay(item)&&!reservationHasKnownEnd(item));}
      function roomHasActiveLongStay(no,targetState=state){const moment=operationalMoment(targetState);return activeReservationsFor(targetState,String(no)).some(item=>reservationIsLongStay(item)&&item.checkOutAt>moment);}
      function reservationCurrentMoment() { return `${state.selectedDate}T${state.time}`; }""",
    "insert long-stay helpers",
)
html = replace_once(
    html,
    """      function reservationNights(reservation) {
        if(!reservation)return 0;
        const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));
        return Math.max(1,Math.round((end-start)/86400000));
      }""",
    """      function reservationNights(reservation) {
        if(!reservation||reservationIsLongStay(reservation))return 0;
        const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));
        return Math.max(1,Math.round((end-start)/86400000));
      }""",
    "long-stay night count",
)
html = replace_once(
    html,
    """      function roomStayProgress(room,reservations=activeReservationsFor(state,room?.no||'')) {
        if(room?.occupancy!=='occupied')return null;
        const pivot=`${state.selectedDate}T${state.time}`,reservation=reservations.find(item=>item.checkInAt<=pivot&&pivot<item.checkOutAt),total=reservationNights(reservation);
        if(!reservation||total<2)return null;
        const day=Math.max(1,Math.min(total,Math.round((dateObject(state.selectedDate)-dateObject(reservation.checkInAt.slice(0,10)))/86400000)+1));
        return {day,total,reservationId:reservation.id,label:`연박 ${day}/${total}일차`};
      }""",
    """      function roomStayProgress(room,reservations=activeReservationsFor(state,room?.no||'')) {
        if(room?.occupancy!=='occupied')return null;
        const pivot=`${state.selectedDate}T${state.time}`,reservation=reservations.find(item=>item.checkInAt<=pivot&&pivot<item.checkOutAt);
        if(reservationIsLongStay(reservation))return {day:null,total:null,reservationId:reservation.id,label:'장기',longStay:true};
        const total=reservationNights(reservation);
        if(!reservation||total<2)return null;
        const day=Math.max(1,Math.min(total,Math.round((dateObject(state.selectedDate)-dateObject(reservation.checkInAt.slice(0,10)))/86400000)+1));
        return {day,total,reservationId:reservation.id,label:`연박 ${day}/${total}일차`};
      }""",
    "long-stay progress badge",
)
html = replace_once(
    html,
    "      function reservationFingerprint(reservation) {\n        return reservation?[reservation.id,reservation.room,reservation.checkInAt,reservation.checkOutAt,reservationGuestCount(reservation),reservation.status,reservation.updatedAt||''].join('|'):'';\n      }",
    "      function reservationFingerprint(reservation) {\n        return reservation?[reservation.id,reservation.room,reservation.checkInAt,reservation.checkOutAt,reservationGuestCount(reservation),reservationIsLongStay(reservation)?'long':'dated',reservation.status,reservation.updatedAt||''].join('|'):'';\n      }",
    "long-stay reservation fingerprint",
)

project_source = r'''      function projectReservationState(targetState,roomNos=null) {
        const selected=roomNos?new Set([].concat(roomNos).map(String)):null,moment=operationalMoment(targetState);
        ROOMS.forEach(room=>{
          if(selected&&!selected.has(room.no))return;
          const reservations=activeReservationsFor(targetState,room.no),current=reservations.find(item=>item.checkInAt<=moment&&moment<item.checkOutAt)||null,future=reservations.find(item=>item.checkInAt>moment)||null,completed=(targetState.reservations||[]).filter(item=>item.room===room.no&&item.status!=='cancelled'&&item.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null,projected=current||future||completed||null;
          if(projected){const projectedLong=reservationIsLongStay(projected);room.reservationCheckinAt=projected.checkInAt;room.reservationCheckoutAt=projected.checkOutAt;room.nextCheckinAt=projected.checkInAt;room.nextCheckoutAt=projected.checkOutAt;room.reservationProjectionId=projected.id;room.checkin=projected.checkInAt.slice(11,16);room.checkout=projectedLong?reservationLongStayEndLabel(projected):projected.checkOutAt.slice(11,16);room.longStay=projectedLong;room.longStayEndAt=reservationHasKnownEnd(projected)?projected.checkOutAt:null;}else if(room.reservationProjectionId){delete room.reservationCheckinAt;delete room.reservationCheckoutAt;delete room.nextCheckinAt;delete room.nextCheckoutAt;delete room.reservationProjectionId;delete room.longStay;delete room.longStayEndAt;room.checkin='정보 없음';room.checkout='정보 없음';}
          const override=room.occupancyOverride;
          if(override==='occupied'&&!current){room.occupancy='occupied';room.checkin=room.actualCheckinAt?.slice(11,16)||'투숙 중';room.checkout=room.longStay?(room.longStayEndAt?reservationMomentLabel(room.longStayEndAt):'종료일 미정'):(room.plannedCheckoutAt||room.reservationCheckoutAt||'예정 미입력').slice?.(11,16)||'예정 미입력';return;}
          if(override==='vacant'&&!current){room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;delete room.longStay;delete room.longStayEndAt;if(completed)room.actualCheckoutAt=completed.checkOutAt;return;}
          if(current){const currentLong=reservationIsLongStay(current);room.occupancy='occupied';room.actualCheckinAt=current.checkInAt;room.plannedCheckoutAt=current.checkOutAt;room.currentStayReservationId=current.id;room.longStay=currentLong;room.longStayEndAt=reservationHasKnownEnd(current)?current.checkOutAt:null;delete room.actualCheckoutAt;room.checkin=current.checkInAt.slice(11,16);room.checkout=currentLong?reservationLongStayEndLabel(current):current.checkOutAt.slice(11,16);return;}
          room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;delete room.longStay;delete room.longStayEndAt;if(completed)room.actualCheckoutAt=completed.checkOutAt;else delete room.actualCheckoutAt;
        });
      }'''
html = replace_last_block(html, "      function projectReservationState(", "      function roomDataIssue(", project_source, "replace reservation projection")

html = replace_once(
    html,
    """      function quickRangeLabel(reservation) {
        const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));
        return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${end.getMonth()+1}/${end.getDate()} ${reservation.checkOutAt.slice(11,16)}`;
      }""",
    """      function quickRangeLabel(reservation) {
        const start=dateObject(reservation.checkInAt.slice(0,10));
        if(reservationIsLongStay(reservation))return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${reservationLongStayEndLabel(reservation)}`;
        const end=dateObject(reservation.checkOutAt.slice(0,10));
        return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${end.getMonth()+1}/${end.getDate()} ${reservation.checkOutAt.slice(11,16)}`;
      }""",
    "long-stay quick range",
)
html = replace_once(
    html,
    "      function reservationMomentLabel(value) {\n        if(!/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$/.test(value||''))return '일정 없음';",
    "      function reservationMomentLabel(value) {\n        if(value===LONG_STAY_OPEN_END_AT)return '종료일 미정';\n        if(!/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$/.test(value||''))return '일정 없음';",
    "open-ended label",
)
html = replace_last_block(
    html,
    "      function plannedCheckoutLabel(",
    "      function roomMasterFingerprint(",
    r'''      function plannedCheckoutLabel(room) {
        if(!room)return '미입력';
        if(room.longStay)return room.longStayEndAt?reservationMomentLabel(room.longStayEndAt):'종료일 미정';
        const explicit=room.plannedCheckoutAt||room.reservationCheckoutAt||room.nextCheckoutAt;
        if(explicit)return explicit;
        return !room.actualCheckoutAt&&/^\d{1,2}:\d{2}(?:\s|$)/.test(room.checkout||'')?room.checkout:'미입력';
      }''',
    "long-stay planned checkout",
)

# Active room cards and status copy.
html = replace_last(
    html,
    "if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false",
    "if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:room.longStay?`장기 투숙 · ${room.longStayEndAt?`종료 ${reservationMomentLabel(room.longStayEndAt)}`:'종료일 미정'}`:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false",
    "long-stay room status",
)
html = replace_last(
    html,
    "checkinDisplay=closestReservation?reservationMomentLabel(closestReservation.checkInAt):'일정 없음',checkoutDisplay=closestReservation?reservationMomentLabel(closestReservation.checkOutAt):'일정 없음';",
    "checkinDisplay=closestReservation?reservationMomentLabel(closestReservation.checkInAt):'일정 없음',checkoutDisplay=reservationIsLongStay(closestReservation)?reservationLongStayEndLabel(closestReservation):closestReservation?reservationMomentLabel(closestReservation.checkOutAt):'일정 없음';",
    "room card long-stay end",
)
html = replace_last(
    html,
    "const detailBadges=[checkoutInspectionPending(no)?'<span class=\"room-detail-badge\">퇴실점검 대상</span>':'',",
    "const detailBadges=[room.longStay?'<span class=\"room-detail-badge long-stay-badge\">장기</span>':'',checkoutInspectionPending(no)?'<span class=\"room-detail-badge\">퇴실점검 대상</span>':'',",
    "long-stay badge",
)
html = replace_last(
    html,
    "reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`",
    "reservationActionLabel=room.longStay?'장기 투숙 관리':weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`",
    "long-stay reservation action label",
)
html = replace_once(
    html,
    "        if(roomIsOnHold(room.no))return '확인 필요 · 예약 불가';",
    "        if(roomIsOnHold(room.no))return '확인 필요 · 예약 불가';\n        if(roomHasActiveLongStay(room.no))return '장기 투숙 · 예약 불가';",
    "block active long-stay booking",
)

# Open-ended long stays do not create checkout cleaning; known-end long stays do.
checkout_target_marker = "      function reservationCheckoutTarget(reservation,date=reservation?.checkOutAt?.slice(0,10)||'',targetState=state,reservations=null) {\n"
html = replace_once(
    html,
    checkout_target_marker,
    checkout_target_marker + "        if(reservationIsLongStay(reservation)&&!reservationHasKnownEnd(reservation))return null;\n",
    "open-ended checkout target guard",
)
html = replace_once(
    html,
    "      function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {",
    """      function cleaningTargetVisible(item,targetState=state) {
        const room=ROOMS.find(entry=>entry.no===String(item?.room||''));if(!room)return false;
        if(roomDataIssue(room.no))return false;
        if(targetState?.roomStopped?.[room.no])return false;
        const linked=item?.reservationId?(targetState.reservations||[]).find(reservation=>reservation.id===item.reservationId):null;
        if(item?.kind==='퇴실 청소'&&(reservationIsLongStay(linked)&&!reservationHasKnownEnd(linked)||!linked&&roomHasOpenEndedLongStay(room.no,targetState)))return false;
        return true;
      }
      function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {""",
    "insert cleaning visibility policy",
)
html = replace_once(
    html,
    "        return [...carryovers,...live,...committedOrphans];\n      }\n      function assignmentTargets()",
    "        return [...carryovers,...live,...committedOrphans].filter(item=>cleaningTargetVisible(item,targetState));\n      }\n      function assignmentTargets()",
    "filter non-cleaning rooms",
)

# ---------------------------------------------------------------------------
# Authentication and role isolation
# ---------------------------------------------------------------------------
auth_source = r'''      const AUTH_SESSION_KEY='roomManagementAuthSessionV1';
      let volatileAuthSession=null;
      function authAccounts(){return [{id:'admin',password:'admin1234',role:'admin',name:'관리자',maidId:null},...MAIDS.map((maid,index)=>({id:`maid${index+1}`,password:'maid1234',role:'maid',name:maid.name,maidId:maid.id}))];}
      function safeAuthSession(value){if(!value||!['admin','maid'].includes(value.role))return null;const account=authAccounts().find(item=>item.id===value.id&&item.role===value.role&&(item.role==='admin'||item.maidId===value.maidId));return account?{id:account.id,role:account.role,name:account.name,maidId:account.maidId}:null;}
      function readAuthSession(){try{return safeAuthSession(JSON.parse(sessionStorage.getItem(AUTH_SESSION_KEY)||'null'))||safeAuthSession(volatileAuthSession);}catch{return safeAuthSession(volatileAuthSession);}}
      function writeAuthSession(account){const session=safeAuthSession(account);volatileAuthSession=session;try{if(session)sessionStorage.setItem(AUTH_SESSION_KEY,JSON.stringify(session));}catch{}return session;}
      function clearAuthSession(){volatileAuthSession=null;try{sessionStorage.removeItem(AUTH_SESSION_KEY);}catch{}}
      function syncAuthState(targetState=state){const session=readAuthSession();targetState.authSession=session;targetState.loggedIn=!!session;if(session){targetState.role=session.role;if(session.role==='maid'&&MAIDS.some(maid=>maid.id===session.maidId))targetState.currentMaidId=session.maidId;}return session;}

'''
html = replace_once(html, "      function baseState(scenario = 0) {", auth_source + "      function baseState(scenario = 0) {", "insert auth helpers")
html = replace_once(html, "loggedIn:true, loginMode:'normal',", "loggedIn:false, authSession:null, loginMode:'normal',", "default logged-out state")
html = replace_once(
    html,
    "        s.quickReservationAnchorDate=kstTodayIso();s.quickReservationFollowsToday=true;\n        syncAssignmentDateForCleaningTab(s);",
    "        s.quickReservationAnchorDate=kstTodayIso();s.quickReservationFollowsToday=true;\n        syncAuthState(s);\n        syncAssignmentDateForCleaningTab(s);",
    "restore auth in scenario",
)
html = replace_once(
    html,
    "      const maidNav = [\n        {id:'my',label:'내 업무',icon:'briefcase'}, {id:'schedule',label:'근무 일정',icon:'calendar'}, {id:'alerts',label:'알림',icon:'bell'}, {id:'pay',label:'주급',icon:'wallet'}, {id:'more',label:'더보기',icon:'more'}\n      ];",
    "      const maidNav = [\n        {id:'my',label:'내 업무',icon:'briefcase'}, {id:'schedule',label:'근무 일정',icon:'calendar'}, {id:'pay',label:'주급',icon:'wallet'}, {id:'more',label:'더보기',icon:'more'}\n      ];",
    "remove maid alert tab",
)
html = replace_once(
    html,
    "        const durableRenderSameState=durableRenderStateRef===state,durableBefore=durableLedgerFingerprint(state);\n        projectReservationState(state);",
    "        const durableRenderSameState=durableRenderStateRef===state,durableBefore=durableLedgerFingerprint(state);\n        syncAuthState(state);\n        projectReservationState(state);",
    "auth guard at render",
)
html = replace_once(html, "          ${renderDemoStrip()}\n          ${state.loggedIn ? `", "          ${state.loggedIn?renderDemoStrip():''}\n          ${state.loggedIn ? `", "hide demo strip while logged out")
html = replace_once(
    html,
    "        if(['admin','maid'].includes(route.role))state.role=route.role;\n        if(MAIDS.some(maid=>maid.id===route.currentMaidId)){state.currentMaidId=route.currentMaidId;syncSignedInMaidAvailability();}",
    "        const authSession=syncAuthState(state);\n        if(authSession?.role==='maid'&&MAIDS.some(maid=>maid.id===authSession.maidId)){state.currentMaidId=authSession.maidId;syncSignedInMaidAvailability();}",
    "block route role crossover",
)
html = replace_once(html, "        state.loggedIn=route.loggedIn!==false;", "        state.loggedIn=!!authSession;", "block route login restore")

render_demo = r'''      function renderDemoStrip() {
        const session=readAuthSession(),roleLabel=session?.role==='admin'?'관리자':`${signedInMaidName()} · 메이드`;
        return `<section class="demo-strip ${state.demoOpen?'open':''}" aria-label="데모 도구"><div class="demo-strip-inner"><div class="demo-label"><span class="signal"></span>데모 화면 · 실제 운영 데이터 아님</div><button class="icon-btn demo-toggle" type="button" data-action="toggle-demo" aria-expanded="${state.demoOpen}" aria-label="데모 도구 ${state.demoOpen?'접기':'펼치기'}">${icon('settings')}</button><div class="demo-controls"><div class="demo-field demo-auth-role"><span>로그인 역할</span><strong>${esc(roleLabel)}</strong><small>다른 역할은 로그아웃 후 로그인합니다.</small></div><div class="demo-field"><label for="demo-time">시간</label><select id="demo-time" data-control="time"><option ${state.time==='00:00'?'selected':''}>00:00</option><option ${state.time==='10:30'?'selected':''}>10:30</option><option ${state.time==='10:32'?'selected':''}>10:32</option><option ${state.time==='11:05'?'selected':''}>11:05</option><option ${state.time==='11:59'?'selected':''}>11:59</option><option ${state.time==='12:00'?'selected':''}>12:00</option><option ${state.time==='13:05'?'selected':''}>13:05</option><option ${state.time==='16:05'?'selected':''}>16:05</option><option ${state.time==='21:10'?'selected':''}>21:10</option><option ${state.time==='21:55'?'selected':''}>21:55</option><option ${state.time==='22:15'?'selected':''}>22:15</option><option ${state.time==='23:59'?'selected':''}>23:59</option></select></div><div class="demo-field"><label for="demo-network">네트워크</label><select id="demo-network" data-control="network"><option value="online" ${state.network==='online'?'selected':''}>정상</option><option value="offline" ${state.network==='offline'?'selected':''}>오프라인</option><option value="stale" ${state.network==='stale'?'selected':''}>오래된 데이터</option></select></div><div class="demo-field scenario"><label for="demo-scenario">시나리오</label><select id="demo-scenario" data-control="scenario">${Object.entries(SCENARIOS).map(([id,s])=>`<option value="${id}" ${state.scenario===Number(id)?'selected':''}>${id==='0'?'기본':id+'.'} ${esc(s.title)}</option>`).join('')}</select></div><button class="btn btn-ghost demo-reset" type="button" data-action="reset">${icon('refresh','icon-sm')}초기 상태로 재설정</button></div></div></section>`;
      }'''
html = replace_last_block(html, "      function renderDemoStrip()", "      function renderSidebar(", render_demo, "replace demo strip")
html = replace_once(html, "<div class=\"side-foot\">${button('로그인 상태 보기','logout','ghost')}</div>", "<div class=\"side-foot\">${button('로그아웃','logout','ghost')}</div>", "sidebar logout")

render_login = r'''      function renderLogin() {
        const error=state.loginMode==='error';
        return `<main id="main-content" style="max-width:480px;padding-top:7vh"><section class="card card-pad" style="box-shadow:var(--shadow)"><div class="brand" style="padding:4px 0 22px"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리 로그인</div></div></div><div class="notice notice-info"><div><strong>아이디에 따라 화면이 분리됩니다.</strong><br>관리자는 관리자 화면만, 메이드는 본인 업무 화면만 이용합니다.</div></div>${error?'<div class="notice notice-danger auth-error" role="alert">아이디 또는 비밀번호가 일치하지 않습니다.</div>':''}<form id="login-form" style="display:grid;gap:12px;margin-top:16px"><div class="field"><label for="login-id">로그인 아이디</label><input id="login-id" class="input-control" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="admin 또는 maid1" required></div><div class="field"><label for="login-password">로그인 비밀번호</label><input id="login-password" class="input-control" type="password" autocomplete="current-password" required><small>와이어프레임: 관리자 admin / admin1234 · 메이드 maid1~maid9 / maid1234</small></div><button class="btn btn-primary btn-block" type="submit">로그인</button></form><div class="auth-role-card" style="margin-top:14px">${icon('shield')}<div><strong>역할 간 직접 전환 없음</strong><span>다른 역할은 로그아웃한 뒤 해당 아이디로 다시 로그인합니다.</span></div></div></section></main>`;
      }'''
html = replace_last_block(html, "      function renderLogin()", "      function openDetail(", render_login, "replace login")

render_topbar = r'''      function renderTopbar() {
        const alertCount=notificationUnreadCount(notificationAudienceKey()),countMarkup=alertCount?`<span class="count-dot">${alertCount}</span>`:'';
        return `<header class="topbar"><div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 ${state.selectedDate.replaceAll('-','.')} ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div><div class="topbar-actions"><button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기 · 안 읽음 ${alertCount}건">${icon('bell')}${countMarkup}</button><button class="btn btn-outline" type="button" data-action="logout" aria-label="로그아웃">${icon('logout','icon-sm')}<span>로그아웃</span></button></div></header>`;
      }'''
html = replace_last_block(html, "      function renderTopbar()", "      function dateObject(", render_topbar, "replace topbar")
html = replace_once(html, "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',alerts:'알림',pay:'내 주급',more:'더보기'};", "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',pay:'내 주급',more:'더보기'};", "remove maid alert title")
html = replace_once(html, "        if (state.maidView==='alerts') return renderMaidAlerts();\n", "", "remove maid alert route")

# ---------------------------------------------------------------------------
# Assignment UX
# ---------------------------------------------------------------------------
html = replace_once(
    html,
    "<tr><td data-label=\"객실·타입·요금\"><div class=\"assignment-cell-stack\"><strong>${item.room}호</strong><span class=\"assignment-room-type\">${esc(context.type.name)}</span>",
    "<tr id=\"assignment-room-${item.room}\" data-assignment-room=\"${item.room}\"><td data-label=\"객실·타입·요금\"><div class=\"assignment-cell-stack\"><strong>${item.room}호</strong><button class=\"assignment-room-type assignment-room-type-link\" type=\"button\" data-action=\"room-detail\" data-id=\"${item.room}\" aria-label=\"${item.room}호 ${esc(context.type.name)} 상세정보 열기\">${esc(context.type.name)}</button>",
    "clickable assignment room type",
)
html = replace_once(
    html,
    "const unassignedList=unassigned.length?unassigned.map(item=>{const context=assignmentContext(item);return `<span class=\"maid-order-unassigned-chip\">${item.room}호 · ${esc(context.type.name)} · ${esc(elevatorLabel(context.room))} · ${money(context.type.rate)}</span>`;}).join(''):'<span class=\"maid-order-unassigned-chip\">미배정 객실 없음</span>';",
    "const unassignedList=unassigned.length?unassigned.map(item=>{const context=assignmentContext(item);return `<button class=\"maid-order-unassigned-chip\" type=\"button\" data-action=\"focus-assignment-room\" data-room=\"${item.room}\" aria-label=\"${item.room}호 객실별 담당 수정으로 이동\">${item.room}호 · ${esc(context.type.name)} · ${esc(elevatorLabel(context.room))} · ${money(context.type.rate)}</button>`;}).join(''):'<span class=\"maid-order-unassigned-chip\">미배정 객실 없음</span>';",
    "unassigned room focus buttons",
)
availability_pattern = re.compile(r'<section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>(.*?)</p></div>(\$\{statusBadge\(.*?\)\})</div>\$\{renderAvailabilityMatrix\(\)\}</section>', re.S)
match = availability_pattern.search(html)
require(match is not None, "admin availability panel not found")
replacement = '<details class="card assignment-panel assignment-availability-disclosure"><summary class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>' + match.group(1) + '</p></div><div class="badge-row">' + match.group(2) + '<span class="disclosure-chevron" aria-hidden="true">${icon(\'arrowDown\',\'icon-sm\')}</span></div></summary><div class="assignment-disclosure-body">${renderAvailabilityMatrix()}</div></details>'
html = html[:match.start()] + replacement + html[match.end():]

# ---------------------------------------------------------------------------
# Maid availability: open only during registration window
# ---------------------------------------------------------------------------
maid_schedule = r'''      function renderMaidSchedule() {
        const maidId=signedInMaidId(),accountActive=signedInMaidIsActive(),dayNames=[['월','17'],['화','18'],['수','19'],['목','20'],['금','21'],['토','22'],['일','23']],phase=availabilitySubmissionPhase(),submitted=state.availabilitySubmitted,editing=!!state.availabilityEditing&&phase==='open',savedSelected=state.weeklyAvailability?.[maidId]?.days||[],selected=editing||!submitted?state.availabilityDraft||[]:savedSelected,availableCount=selected.length;
        const assigned=notifiedAssignmentEntriesForMaid(maidId);
        const assignedCards=assigned.length?assigned.map(({item})=>{const guestCount=assignmentGuestCount(item);return `<div class="assigned-preview-grid"><div><span>근무일</span><strong>${esc(dateLabel(targetEffectiveDate(item)))}</strong></div><div><span>객실</span><strong>${item.room}호</strong></div><div><span>업무</span><strong>${esc(item.kind)}</strong></div>${guestCount?`<div><span>숙박 인원</span><strong>${esc(guestCountLabel(guestCount))}</strong></div>`:'<div><span>예약 연결</span><strong>없음</strong></div>'}<div><span>시작 가능</span><strong>${item.checkout} 이후</strong></div>${item.carryReason?`<div><span>이월</span><strong>원 계획 ${esc(dateLabel(targetPlanDate(item)))}</strong></div>`:''}</div>`;}).join(''):'<div class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 근무일 전날 밤 객실 담당을 확정하면 여기에 표시됩니다.</p></div>';
        const submissionWindow=availabilitySubmissionWindowLabel(),phaseText=!accountActive?'비활성 계정 · 과거 제출 읽기 전용':phase==='before'?`${submissionWindow} 제출 가능`:phase==='open'?`${submissionWindow} · 지금 제출 가능`:`${submissionWindow} 마감 · 변경은 관리자 확인 필요`;
        const editorLocked=!accountActive||submitted&&!editing||state.availabilityChangeRequested||phase!=='open'||isLocked();
        let actionMarkup='';
        if(!accountActive)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>가능일 수정 잠금</strong><br>비활성 처리 중이거나 비활성인 계정은 과거 제출만 조회할 수 있습니다.</div></div>';
        else if(state.availabilityChangeRequested)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>관리자 확인 요청됨</strong><br>기존 제출은 유지되고 변경 요청이 관리자 알림에 남았습니다.</div></div>';
        else if(editing)actionMarkup=button('수정 내용 다시 제출','submit-week-availability','primary',isLocked()?'disabled':'');
        else if(submitted&&phase==='open')actionMarkup=button('제출 내용 수정','edit-week-availability','primary',isLocked()?'disabled':'');
        else if(submitted&&phase==='closed')actionMarkup=button('가능일 변경 요청','request-availability-change','outline',isLocked()?'disabled':'');
        else if(submitted)actionMarkup=button('제출 기간 아님','edit-week-availability','outline','disabled');
        else actionMarkup=button(phase==='open'?'다음 주 가능일 제출':phase==='before'?`${submissionWindow} 제출`:'제출 마감','submit-week-availability','primary',phase==='open'&&!isLocked()?'':'disabled');
        const openAttr=phase==='open'?' open':'';
        return renderCoach()+renderNetworkNotice()+`<div class="weekly-availability"><details class="card week-card weekly-availability-disclosure"${openAttr}><summary class="week-card-head"><div><h2>8월 17일 (월)–8월 23일 (일)</h2><p>다음 주에 근무 가능한 요일을 모두 선택해 주세요.</p></div><div class="badge-row">${statusBadge(state.availabilityChangeRequested?'변경 요청':editing?'수정 중':submitted?'제출 완료':'미제출',state.availabilityChangeRequested||editing?'amber':submitted?'green':'amber')}<span class="disclosure-chevron" aria-hidden="true">${icon('arrowDown','icon-sm')}</span></div></summary><div class="weekly-availability-body"><div class="deadline-bar">${icon('clock','icon-sm')}<span>${phaseText}</span></div><div class="week-days" aria-label="다음 주 근무 가능일">${dayNames.map((day,index)=>{const active=selected.includes(index);return `<button class="week-day" type="button" data-action="toggle-week-day" data-day="${index}" aria-pressed="${active}" ${editorLocked?'disabled':''}><strong>${day[0]} ${day[1]}</strong><span>${active?'근무 가능':'근무 불가'}</span><i class="week-toggle" aria-hidden="true"></i></button>`;}).join('')}</div><div class="week-total">${icon('calendar','icon-sm')}가능 ${availableCount}일 · 불가 ${7-availableCount}일</div><div class="week-submit-actions">${actionMarkup}</div><div class="assignment-notice">${icon('user')}<p>관리자가 각 근무일 전날 밤 객실을 직접 배정합니다. 메이드는 객실을 선택하거나 다른 메이드에게 배정할 수 없습니다.</p></div></div></details><section class="card assigned-preview"><div class="section-head"><div><h2>배정된 내 업무</h2><span class="meta">관리자 통보 완료 건만 표시</span></div>${statusBadge(`${assigned.length}건`,'blue')}</div>${assignedCards}<p class="audit-note" style="margin:10px 0 0">배정이 바뀌면 기존 담당 구간은 이력으로 남고 상단 알림에서 변경 내용을 확인할 수 있습니다.</p></section></div>`;
      }'''
html = replace_last_block(html, "      function renderMaidSchedule()", "      function renderMaidAlerts(", maid_schedule, "replace maid schedule")

# ---------------------------------------------------------------------------
# Reservation editor and optional long-stay end date
# ---------------------------------------------------------------------------
preview_source = r'''      function reservationPreviewMarkup(checkinAt,checkoutAt,{longStay=false}={}) {
        const knownEnd=longStay&&!!checkoutAt&&checkoutAt!==LONG_STAY_OPEN_END_AT,status=reservationTimeStatus(checkinAt,longStay&&!knownEnd?'':checkoutAt),valid=!!checkinAt&&(longStay&&!knownEnd||!!checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10)),nights=!longStay&&valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0,endText=longStay?(knownEnd?`종료 ${reservationMomentLabel(checkoutAt)}`:'종료일 미정'):reservationStatusText(status,'checkout');
        return `<div class="field field-full"><div class="notice notice-info" style="margin:0"><div style="width:100%"><strong>예약 기간</strong><div class="info-grid" id="reservation-time-preview" aria-live="polite" style="margin-top:10px"><div class="info-item"><span>구분</span><strong data-reservation-night-status>${longStay?'장기':valid?`${nights}박`:'입퇴실 시각 확인 필요'}</strong></div><div class="info-item"><span>체크인 · 16:00 기준</span><strong data-reservation-checkin-status>${esc(reservationStatusText(status,'checkin'))}</strong></div><div class="info-item"><span>${longStay?'장기 종료':'체크아웃 · 11:00 기준'}</span><strong data-reservation-checkout-status>${esc(endText)}</strong></div></div></div></div><small>${longStay?'종료일이 정해졌다면 입력하고, 모르면 비워 두세요.':'체크인 다음에 체크아웃을 입력하며 1시간 단위로 선택합니다.'}</small></div>`;
      }'''
html = replace_last_block(html, "      function reservationPreviewMarkup(", "      function updateReservationTimePreview(", preview_source, "replace reservation preview")
update_preview_source = r'''      function updateReservationTimePreview() {
        const checkinAt=document.getElementById('res-checkin')?.value||'',checkout=document.getElementById('res-checkout'),longStay=!!document.getElementById('res-long-stay')?.checked,checkoutAt=checkout?.value||'',knownEnd=longStay&&!!checkoutAt,status=reservationTimeStatus(checkinAt,longStay&&!knownEnd?'':checkoutAt);
        const label=document.querySelector('[data-res-checkout-label]'),help=document.querySelector('[data-res-checkout-help]'),checkinStatus=document.querySelector('[data-reservation-checkin-status]'),checkoutStatus=document.querySelector('[data-reservation-checkout-status]'),nightStatus=document.querySelector('[data-reservation-night-status]');
        if(checkout){checkout.required=!longStay;checkout.disabled=false;}
        if(label)label.textContent=longStay?'2. 종료 일시 (선택)':'2. 체크아웃 일시';
        if(help)help.textContent=longStay?'종료일을 알면 입력하고, 미정이면 비워 두세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃';
        if(checkinStatus)checkinStatus.textContent=reservationStatusText(status,'checkin');
        if(checkoutStatus)checkoutStatus.textContent=longStay?(knownEnd?`종료 ${reservationMomentLabel(checkoutAt)}`:'종료일 미정'):reservationStatusText(status,'checkout');
        if(nightStatus){const valid=checkinAt&&(longStay&&!knownEnd||checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10)),nights=!longStay&&valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;nightStatus.textContent=longStay?'장기':valid?`${nights}박`:'입퇴실 시각 확인 필요';}
      }'''
html = replace_last_block(html, "      function updateReservationTimePreview()", "      function updateReservationGuestControls(", update_preview_source, "replace preview updater")

modal_old = "defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no)"
modal_new = "defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),longStay=reservationIsLongStay(existing)||currentEntry&&room.longStay===true,checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?(room.longStayEndAt||''):existing?(reservationHasKnownEnd(existing)?existing.checkOutAt:''):`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no)"
html = replace_once(html, modal_old, modal_new, "reservation modal long-stay state")
html = replace_once(html, "subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.'", "subtitle:longStay?'장기 투숙의 시작일과 선택 종료일을 입력합니다.':'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.'", "long-stay modal subtitle")
html = replace_once(
    html,
    "</div></div><div class=\"field\"><label for=\"res-checkin\">1. 체크인 일시</label>",
    "</div></div><div class=\"field field-full\"><label class=\"reservation-long-stay-toggle\" for=\"res-long-stay\"><input id=\"res-long-stay\" type=\"checkbox\" data-control=\"reservation-long-stay\" ${longStay?'checked':''}><span><strong>장기 투숙으로 등록</strong><span>종료일을 알면 입력하고, 모르면 비워 둔 채 ‘종료일 미정’으로 저장합니다.</span></span></label></div><div class=\"field\"><label for=\"res-checkin\">1. 체크인 일시</label>",
    "insert long-stay toggle",
)
html = replace_once(
    html,
    "<div class=\"field\"><label for=\"res-checkout\">2. 체크아웃 일시</label><input id=\"res-checkout\" class=\"input-control\" type=\"datetime-local\" step=\"3600\" value=\"${esc(checkoutAt)}\" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>",
    "<div class=\"field\"><label for=\"res-checkout\" data-res-checkout-label>${longStay?'2. 종료 일시 (선택)':'2. 체크아웃 일시'}</label><input id=\"res-checkout\" class=\"input-control\" type=\"datetime-local\" step=\"3600\" value=\"${esc(checkoutAt)}\" ${longStay?'':'required'}><small data-res-checkout-help>${longStay?'종료일을 알면 입력하고, 미정이면 비워 두세요.':currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>",
    "optional long-stay end field",
)
html = replace_once(html, "${reservationPreviewMarkup(checkinAt,checkoutAt)}", "${reservationPreviewMarkup(checkinAt,checkoutAt,{longStay})}", "long-stay preview call")
html = replace_once(
    html,
    "confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수'",
    "confirmLabel:longStay?(existing?'장기 투숙 수정 저장':'장기 투숙 등록'):currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수'",
    "long-stay save label",
)
html = replace_once(
    html,
    "<span class=\"reservation-list-meta\">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span>",
    "<span class=\"reservation-list-meta\">${reservationStayLengthLabel(reservation)} · ${reservationGuestCount(reservation)}명</span>",
    "reservation list long-stay label",
)
html = replace_once(
    html,
    "const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정')",
    "const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=reservationIsLongStay(reservation)?`장기 투숙 · ${reservationLongStayEndLabel(reservation)}`:readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정')",
    "reservation list long-stay status",
)

upsert_source = r'''      function reservationPayloadMatches(item,{roomNo,checkInAt,checkOutAt,guestCount,isLongStay=false}) { return item?.status==='active'&&item.room===String(roomNo)&&item.checkInAt===checkInAt&&item.checkOutAt===checkOutAt&&reservationGuestCount(item)===Number(guestCount)&&reservationIsLongStay(item)===!!isLongStay; }
      function clearLongStayCleaningArtifacts(reservation) {
        const draftIds=new Set((state.drafts||[]).filter(draft=>draft.reservationId===reservation.id).map(draft=>draft.id));
        state.drafts=(state.drafts||[]).filter(draft=>draft.reservationId!==reservation.id);state.selectedDrafts=(state.selectedDrafts||[]).filter(id=>!draftIds.has(id));
        draftIds.forEach(targetId=>{const record=state.assignments?.[targetId];if(record&&!record.maidId&&!record.previousMaidId)delete state.assignments[targetId];const target=state.cleaningTargets?.[targetId];if(target&&!target.currentAttemptId)delete state.cleaningTargets[targetId];});
      }
      function upsertReservationRecord({id='',roomNo,checkInAt,checkOutAt,guestCount,source='card',currentStay=false,isLongStay=false}) {
        const openEndedLongStay=!!isLongStay&&!checkOutAt;if(openEndedLongStay)checkOutAt=LONG_STAY_OPEN_END_AT;
        const previous=id?state.reservations.find(item=>item.id===id&&item.status==='active')||null:null,before=previous?{...previous}:null,room=ROOMS.find(item=>item.no===String(roomNo)),beforeReservations=activeReservationsFor(state,String(roomNo)).map(item=>({...item}));
        if(!room)return {error:'객실 정보를 찾을 수 없습니다.'};
        if(id&&!previous)return {error:'이 예약은 이미 변경되었거나 취소되었습니다. 최신 예약을 다시 열어 주세요.'};
        const now=reservationCurrentMoment(),linkedCurrentStay=!!before&&room.occupancy==='occupied'&&currentOccupiedReservation(room)?.id===before.id,unchangedPastStaySchedule=linkedCurrentStay&&before.checkInAt===checkInAt&&before.checkOutAt===checkOutAt&&reservationIsLongStay(before)===!!isLongStay;
        if(previous&&reservationRecordIsPast(previous))return {error:'지난 예약 기록은 조회만 가능하며 수정할 수 없습니다.'};
        if(!openEndedLongStay&&checkOutAt<=now&&!unchangedPastStaySchedule)return {error:'이미 지난 일정은 예약으로 새로 등록하거나 옮길 수 없습니다. 현재 투숙 중이면 종료일을 미래 시각으로 연장해 주세요.'};
        const policy=guestPolicyForRoom(room.no),resolvedGuestCount=guestCount===undefined||guestCount===null||guestCount===''?(previous?reservationGuestCount(previous):policy.defaultGuestCount):Number(guestCount);
        if(!Number.isInteger(resolvedGuestCount)||resolvedGuestCount<1||resolvedGuestCount>policy.maxGuestCount)return {error:`${ROOM_TYPES[policy.typeId].name} 객실은 숙박 인원을 1명부터 최대 ${policy.maxGuestCount}명까지 저장할 수 있습니다.`,guestError:true};
        const registeringCurrentStay=!before&&currentStay===true&&room.occupancy==='occupied'&&!occupiedReservationEnd(room)&&checkInAt<=now&&(openEndedLongStay||checkOutAt>now);
        if(currentStay===true&&!registeringCurrentStay)return {error:'현재 투숙 정보는 실제 체크인이 현재 시각 이전이어야 합니다. 종료일이 있으면 현재 이후로 입력해 주세요.'};
        if(checkInAt<now&&!registeringCurrentStay&&!linkedCurrentStay&&(!before||checkInAt!==before.checkInAt))return {error:'새 예약과 미래 예약 변경은 현재 시각 이후의 체크인으로 입력해 주세요.'};
        if(linkedCurrentStay&&checkInAt>now)return {error:'현재 투숙 중인 예약의 체크인을 미래 시각으로 옮길 수 없습니다. 실제 입실 시각을 확인해 주세요.'};
        const payload={roomNo:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,isLongStay},duplicateReservation=!id?activeReservationsFor(state,room.no).find(item=>reservationPayloadMatches(item,payload))||null:null,unchangedReservation=!!previous&&reservationPayloadMatches(previous,payload);
        if(duplicateReservation)return {reservation:duplicateReservation,previous:null,duplicate:true,unchanged:true};
        if(unchangedReservation)return {reservation:previous,previous:before,duplicate:true,unchanged:true};
        const scheduleChanged=!!before&&(before.checkInAt!==checkInAt||before.checkOutAt!==checkOutAt||reservationIsLongStay(before)!==!!isLongStay),guestCountChanged=!!before&&reservationGuestCount(before)!==resolvedGuestCount,candidate={...(previous||{}),id:id||'reservation-candidate',room:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,isLongStay:!!isLongStay,status:'active'},prospectiveReservations=[...beforeReservations.filter(item=>item.id!==candidate.id),candidate].sort((left,right)=>left.checkInAt.localeCompare(right.checkInAt)),cleaningChanges=reservationCleaningChanges(beforeReservations,prospectiveReservations),roomCleaningChanged=cleaningChanges.length>0;
        if(roomCleaningChanged&&reservationCleaningChangeTouchesPublic(cleaningChanges,room.no))return {error:`${room.no}호의 영향을 받는 청소 작업이 이미 공개되어 예약 일정·인원을 바로 바꿀 수 없습니다. 청소 화면에서 공개·담당 영향을 먼저 조율해 주세요.`};
        if(roomCleaningChanged&&reservationCleaningChangeTouchesRandom(cleaningChanges))return {error:'이 예약과 연결된 랜덤 배정 초안이 있습니다. 해당 청소 배정에서 초안을 되돌린 뒤 다시 저장해 주세요.'};
        const activeAttempt=activeUnfinishedAttempt(room.no),linkedAttemptBefore=before?reservationAutomaticCleaningAttempt(before,activeAttempt):null,attemptScheduleLocked=activeAttempt&&(!!activeAttempt.startedAt||roomPinWasViewed(room.no,activeAttempt.id)||activeAttempt.accessReviewRequired||!['scheduled','claimed','unassigned'].includes(state.jobs[room.no]));
        if(linkedAttemptBefore?.performerId&&before.checkOutAt.slice(0,10)!==checkOutAt.slice(0,10))return {error:`${room.no}호 퇴실 청소 담당의 업무일이 이미 ${quickDateLabel(before.checkOutAt.slice(0,10))}로 잡혀 있습니다. 종료 날짜를 바꾸려면 청소 화면에서 담당·업무일을 먼저 조율해 주세요.`};
        if(attemptScheduleLocked){const workDate=attemptWorkDate(activeAttempt,state.selectedDate),timingChanged=reservationWorkTimingFingerprint(beforeReservations,workDate)!==reservationWorkTimingFingerprint(prospectiveReservations,workDate);if(timingChanged)return {error:`${room.no}호는 연결된 퇴실 청소가 있거나 PIN 사용이 시작되어 출입 시각·준비 마감을 바꿀 수 없습니다.`};}
        const exactOverlap=reservationOverlaps(room.no,checkInAt,checkOutAt,id);if(exactOverlap)return {error:`${room.no}호 ${quickRangeLabel(exactOverlap)} · 기존 예약과 실제 체크인·종료 시각이 겹칩니다.`,conflict:exactOverlap};
        if(!openEndedLongStay){const firstNight=checkInAt.slice(0,10),lastNight=shiftIsoDate(checkOutAt.slice(0,10),-1),conflict=quickReservationConflict(room.no,firstNight,lastNight,id,checkInAt,checkOutAt,registeringCurrentStay);if(conflict)return {error:`${room.no}호 ${quickDateLabel(conflict.date)} · ${conflict.reason}`,conflict};}
        const reservationId=id||`reservation-${room.no}-${checkInAt.slice(0,10).replaceAll('-','')}-${++state.reservationSequence}`;
        const reservation=previous||{id:reservationId,room:room.no,source,status:'active',createdAt:`${state.selectedDate}T${state.time}`};
        Object.assign(reservation,{room:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,isLongStay:!!isLongStay,source:previous?.source||source,status:'active',updatedAt:`${state.selectedDate}T${state.time}`});
        if(!previous)state.reservations.push(reservation);
        if(registeringCurrentStay||linkedCurrentStay||isLongStay&&checkInAt<=now){room.actualCheckinAt=checkInAt;room.plannedCheckoutAt=checkOutAt;room.currentStayReservationId=reservation.id;room.longStay=!!isLongStay;room.longStayEndAt=reservationHasKnownEnd(reservation)?checkOutAt:null;}
        if(openEndedLongStay)clearLongStayCleaningArtifacts(reservation);else{syncReservationCleaningDraft(reservation,before);syncUnstartedReservationCleaningAttempt(reservation,linkedAttemptBefore);const checkoutDate=reservation.checkOutAt.slice(0,10),checkoutDateChanged=!before||!reservationHasKnownEnd(before)||before.checkOutAt.slice(0,10)!==checkoutDate;if(checkoutDateChanged){const {record,changed,maidId}=syncReservationAssignmentScheduleState(reservation,checkoutDate,{reopenSameReservation:true});if(record&&maidId&&changed)appendEvent(`${room.no}호 ${isLongStay?'장기 종료':'예약 체크아웃'} 이동 · 청소 재통보 필요`,`${reservation.checkOutAt.slice(11,16)} 종료 · ${maidName(maidId)}의 기존 통보 일정 유지`,{maidIds:[maidId],roomId:room.no});}}
        syncAdjacentReservationCleaningSchedules(room.no,beforeReservations);projectReservationState(state,room.no);state.reservationSaved=true;
        const guestChange=guestCountChanged?` · 숙박 인원 ${reservationGuestCount(before)}명 → ${resolvedGuestCount}명`:` · 숙박 인원 ${resolvedGuestCount}명`,endChange=isLongStay?` · ${reservationLongStayEndLabel(reservation)}`:'';
        appendEvent(`${room.no}호 ${isLongStay?'장기 투숙':'예약'} ${previous?'변경':'접수'}`,`${previous?`${quickRangeLabel(before)} → `:''}${quickRangeLabel(reservation)} · ${reservationStayLengthLabel(reservation)}${endChange}${guestChange}${previous?' · 예약정보 수정':openEndedLongStay?' · 퇴실 청소는 실제 종료 시 생성':' · 종료일 퇴실 청소 준비'}`,{roomId:room.no,dedupeKey:`reservation:${reservation.id}:${reservationFingerprint(reservation)}`});
        return {reservation,previous:before};
      }'''
html = replace_last_block(html, "      function reservationPayloadMatches(", "      function clearOrphanedReservationDraftJob(", upsert_source, "replace reservation upsert")

save_fields_pattern = r"const checkinAt=document\.getElementById\('res-checkin'\)\?\.value\|\|'', checkoutAt=document\.getElementById\('res-checkout'\)\?\.value\|\|'',guestCount=document\.getElementById\('res-guests'\)\?\.value\?\?'',currentStay=document\.getElementById\('res-current-stay'\)\?\.value==='1';"
save_fields_replacement = "const checkinAt=document.getElementById('res-checkin')?.value||'',isLongStay=!!document.getElementById('res-long-stay')?.checked,enteredCheckoutAt=document.getElementById('res-checkout')?.value||'',checkoutAt=isLongStay&&!enteredCheckoutAt?LONG_STAY_OPEN_END_AT:enteredCheckoutAt,guestCount=document.getElementById('res-guests')?.value??'',currentStay=document.getElementById('res-current-stay')?.value==='1';"
html = regex_once(html, save_fields_pattern, save_fields_replacement, "long-stay save fields", flags=0)
html = replace_once(
    html,
    "if(!validDateTime(checkinAt)||!validDateTime(checkoutAt)||checkinAt>=checkoutAt||checkinAt.slice(0,10)>=checkoutAt.slice(0,10))",
    "if(!validDateTime(checkinAt)||(!isLongStay||enteredCheckoutAt)&&(!validDateTime(checkoutAt)||checkinAt>=checkoutAt||checkinAt.slice(0,10)>=checkoutAt.slice(0,10)))",
    "optional end date validation",
)
html = replace_once(
    html,
    "if(!checkinTime.endsWith(':00')||!checkoutTime.endsWith(':00'))",
    "if(!checkinTime.endsWith(':00')||(!isLongStay||enteredCheckoutAt)&&!checkoutTime.endsWith(':00'))",
    "optional end hour validation",
)
html = replace_once(
    html,
    "const result=upsertReservationRecord({id:reservationId,roomNo:no,checkInAt:checkinAt,checkOutAt:checkoutAt,guestCount,source:'card',currentStay});",
    "const result=upsertReservationRecord({id:reservationId,roomNo:no,checkInAt:checkinAt,checkOutAt:isLongStay&&!enteredCheckoutAt?'':checkoutAt,guestCount,source:isLongStay?'long-stay':'card',currentStay,isLongStay});",
    "pass long-stay save state",
)
html = replace_once(
    html,
    "toast(`${no}호 ${reservationNights(result.reservation)}박 · ${reservationGuestCount(result.reservation)}명 예약을 저장했습니다.`);",
    "toast(`${no}호 ${reservationStayLengthLabel(result.reservation)} · ${reservationGuestCount(result.reservation)}명 ${isLongStay?`장기 투숙을 저장했습니다. ${reservationLongStayEndLabel(result.reservation)}`:'예약을 저장했습니다.'}`);",
    "long-stay save toast",
)

# ---------------------------------------------------------------------------
# Event handlers: login, logout, role isolation, focus, long-stay toggle
# ---------------------------------------------------------------------------
html = replace_once(html, "['quick-reservation-edit','quick-month-shift'", "['focus-assignment-room','quick-reservation-edit','quick-month-shift'", "register assignment focus action")
role_handler = "if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action=\"switch-role\"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}"
role_replacement = "if(a==='switch-role'){syncAuthState(state);render();toast('역할은 로그인 계정으로 고정됩니다. 다른 역할은 로그아웃 후 로그인하세요.','error');return;}\n        if(a==='logout'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;clearAuthSession();closeModal();state.loggedIn=false;state.authSession=null;state.detail=null;render();requestAnimationFrame(()=>document.getElementById('login-id')?.focus());return;}\n        if(a==='focus-assignment-room'){const roomNo=String(el.dataset.room||'');state.assignmentTypeFilter='all';render();requestAnimationFrame(()=>{const row=document.getElementById(`assignment-room-${roomNo}`);if(!row){toast(`${roomNo}호 담당 수정 행을 찾지 못했습니다.`,'error');return;}row.classList.add('is-focus-target');row.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});row.querySelector('[data-control=\"assignment-maid\"]')?.focus({preventScroll:true});setTimeout(()=>row.classList.remove('is-focus-target'),2000);});return;}"
html = replace_once(html, role_handler, role_replacement, "replace role switch handler")
html = replace_once(html, "'reservation-cancel-reason'].includes(c)", "'reservation-cancel-reason','reservation-long-stay'].includes(c)", "register long-stay control")
html = replace_once(html, "        if(c==='reservation-room'){updateReservationGuestControls(true);return;}", "        if(c==='reservation-long-stay'){updateReservationTimePreview();return;}\n        if(c==='reservation-room'){updateReservationGuestControls(true);return;}", "long-stay toggle handler")
html = replace_once(html, "if(c==='role'){maskPin();closeModal();state.role=e.target.value;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"role\"]')?.focus());return;}", "if(c==='role'){maskPin();closeModal();syncAuthState(state);render();toast('역할은 로그인 계정으로 고정됩니다.','error');return;}", "guard role selector")
html = replace_once(html, "if(c==='maid-account'){if(state.role!=='maid')return;maskPin();closeModal();state.currentMaidId=MAIDS.some(maid=>maid.id===e.target.value)?e.target.value:'m1';syncSignedInMaidAvailability();state.detail=null;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"maid-account\"]')?.focus());toast(`${signedInMaidName()} 계정으로 전환했습니다.`);return;}", "if(c==='maid-account'){maskPin();closeModal();syncAuthState(state);render();toast('메이드 계정은 로그인 아이디로 고정됩니다.','error');return;}", "guard maid account selector")
html = replace_once(
    html,
    "if(e.target.id==='login-form'){e.preventDefault();state.loggedIn=true;state.loginMode='normal';render();toast('데모 역할 화면으로 로그인했습니다.');}",
    "if(e.target.id==='login-form'){e.preventDefault();const loginId=document.getElementById('login-id')?.value.trim().toLowerCase()||'',password=document.getElementById('login-password')?.value||'',account=authAccounts().find(item=>item.id===loginId&&item.password===password);if(!account){state.loginMode='error';render();requestAnimationFrame(()=>document.getElementById('login-id')?.focus());return;}writeAuthSession(account);state.loginMode='normal';state.detail=null;state.adminView='today';state.maidView='my';syncAuthState(state);syncSignedInMaidAvailability();render();toast(`${account.role==='admin'?'관리자':account.name} 계정으로 로그인했습니다.`);}",
    "credential login handler",
)
html = replace_once(html, "else if(a==='logout'){state.loggedIn=false;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('#login-id')?.focus());}", "else if(a==='logout'){clearAuthSession();state.loggedIn=false;state.authSession=null;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('#login-id')?.focus());}", "legacy logout session clear")

# Include long-stay type in durable render mutation checks.
html = replace_once(
    html,
    "reservations:sortedValues(targetState.reservations,item=>({id:item.id,room:item.room,checkInAt:item.checkInAt,checkOutAt:item.checkOutAt,guestCount:reservationGuestCount(item),source:item.source,status:item.status}))",
    "reservations:sortedValues(targetState.reservations,item=>({id:item.id,room:item.room,checkInAt:item.checkInAt,checkOutAt:item.checkOutAt,guestCount:reservationGuestCount(item),source:item.source,status:item.status,isLongStay:reservationIsLongStay(item)}))",
    "durable long-stay state",
)

HTML_PATH.write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# Focused source checks and documentation
# ---------------------------------------------------------------------------
check_path = ROOT / "scripts/check-issue-119.mjs"
check_path.write_text(r'''#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
const html=readFileSync(resolve('WIREFRAME/index.html'),'utf8');
const required=[
  "const AUTH_SESSION_KEY='roomManagementAuthSessionV1'",
  "{id:'admin',password:'admin1234',role:'admin'",
  "password:'maid1234',role:'maid'",
  "const LONG_STAY_OPEN_END_AT='9999-12-31T23:59'",
  'function reservationHasKnownEnd(reservation)',
  "reservationLongStayEndLabel(reservation)?",
  '종료일을 알면 입력하고, 모르면 비워 둔 채',
  'data-res-checkout-label',
  "isLongStay&&!enteredCheckoutAt?LONG_STAY_OPEN_END_AT",
  "reservationIsLongStay(reservation)&&!reservationHasKnownEnd(reservation)",
  'function cleaningTargetVisible(item,targetState=state)',
  '.filter(item=>cleaningTargetVisible(item,targetState))',
  'assignment-availability-disclosure',
  "const openAttr=phase==='open'?' open':''",
  'data-action="focus-assignment-room"',
  'id="assignment-room-${item.room}"',
  'assignment-room-type-link',
  "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',pay:'내 주급',more:'더보기'}",
  'data-action="logout" aria-label="로그아웃"',
];
for(const contract of required){if(!html.includes(contract.replace('reservationLongStayEndLabel(reservation)?','reservationLongStayEndLabel(reservation)')))throw new Error(`Issue #119 contract missing: ${contract}`);}
for(const removed of ["{id:'alerts',label:'알림',icon:'bell'}","if (state.maidView==='alerts') return renderMaidAlerts();","data-action=\"switch-role\" aria-label=\"${state.role==='admin'?'메이드 보기':'관리자 보기'}\""]){if(html.includes(removed))throw new Error(`Removed issue #119 contract remains: ${removed}`);}
const inlineScripts=[...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(match=>match[1]);
if(!inlineScripts.length)throw new Error('No inline application script found.');
for(const script of inlineScripts)new Function(script);
console.log('Issue #119 source contracts and JavaScript syntax verified.');
''', encoding="utf-8")

doc17 = ROOT / "DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md"
doc17.write_text(doc17.read_text(encoding="utf-8") + r'''

## 2026-08-30 · 장기 투숙과 선택 종료일

- `장기 투숙`은 일반 예약과 구분되는 예약 유형으로 저장한다.
- 종료일을 알고 있으면 종료 일시를 입력하고 객실 카드·상세·예약 관리에 표시한다.
- 종료일을 모르면 입력을 비워 두며 화면에는 `종료일 미정`으로 표시한다.
- 두 경우 모두 투숙 기간에는 `장기` 배지를 표시하고 예약 가능 객실에서 제외한다.
- 종료일이 입력된 장기 투숙은 해당 종료일의 퇴실 청소를 준비한다.
- 종료일 미정 장기 투숙은 일반 퇴실 청소를 미리 만들지 않고, 실제 종료가 기록될 때 퇴실 청소를 만든다.
- 연박·추가 청소처럼 관리자가 명시적으로 만든 투숙 중 청소 요청은 계속 허용한다.
''', encoding="utf-8")

qa = ROOT / "WIREFRAME/QA.md"
qa.write_text(qa.read_text(encoding="utf-8") + r'''

## Issue #119 · 역할 로그인·청소 배정·장기 투숙

- [ ] 로그아웃 상태에서는 로그인 화면만 표시된다.
- [ ] `admin / admin1234`는 관리자 화면, `maid1~maid9 / maid1234`는 해당 메이드 화면으로 진입한다.
- [ ] 로그인 후 역할·메이드 계정 직접 전환 UI가 없고, 로그아웃 후 다른 아이디로만 진입한다.
- [ ] 메이드 내비게이션에 알림 탭이 없고 상단 종 모양 알림함은 정상 동작한다.
- [ ] 오늘/내일 청소 배정의 메이드 근무표는 처음에 접혀 있다.
- [ ] 미배정 객실을 누르면 객실별 담당 수정의 같은 객실 행으로 이동·강조된다.
- [ ] 청소 배정 표의 객실 타입을 누르면 해당 객실 상세가 열린다.
- [ ] 정보 확인 필요·운영 중지·종료일 미정 장기 투숙의 일반 퇴실 청소는 배정 목록에 나타나지 않는다.
- [ ] 촛불 미회수 객실은 청소 의무가 있으면 목록에 남되 배정은 차단된다.
- [ ] 근무 가능일은 제출 기간에만 처음부터 펼쳐지고 그 밖의 기간에는 접혀 있다.
- [ ] 장기 투숙 종료일을 입력하면 해당 날짜가 객실 카드·상세·예약 목록에 보인다.
- [ ] 장기 투숙 종료일을 비우면 `종료일 미정`으로 보인다.
- [ ] 종료일이 있는 장기 투숙은 종료일 퇴실 청소가 생성되고, 종료일 미정 장기 투숙은 미리 생성되지 않는다.
''', encoding="utf-8")

readme = ROOT / "WIREFRAME/README.md"
readme.write_text(readme.read_text(encoding="utf-8") + r'''

## Issue #119 데모 로그인

- 관리자: `admin` / `admin1234`
- 메이드: `maid1`~`maid9` / `maid1234`
- 단일 HTML 와이어프레임에서 역할별 화면과 세션 가드를 확인하기 위한 데모다. 운영 환경의 인증·인가와 비밀번호 검증은 백엔드에서 구현해야 한다.
''', encoding="utf-8")

# Refresh hashes for every path already tracked in SHA256SUMS.txt.
sums_path = ROOT / "SHA256SUMS.txt"
refreshed=[]
for raw in sums_path.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    _, rel = raw.split(None, 1)
    path = ROOT / rel
    require(path.exists(), f"SHA256 tracked path missing: {rel}")
    refreshed.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}")
sums_path.write_text("\n".join(refreshed) + "\n", encoding="utf-8")

print("Applied issue #119 v2 changes with optional long-stay end dates.")
