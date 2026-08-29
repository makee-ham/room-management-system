#!/usr/bin/env python3
"""Apply issue #119 UX, authentication, and long-stay changes to the wireframe."""
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
    require(count == 1, f"{label}: expected exactly one match, got {count}")
    return text.replace(old, new, 1)


def replace_regex(text: str, pattern: str, replacement: str, label: str, flags: int = re.S) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    require(count == 1, f"{label}: expected exactly one regex match, got {count}")
    return updated


def function_block(text: str, start_name: str, next_name: str, new_source: str) -> str:
    pattern = rf"      function {re.escape(start_name)}\([^\n]*?\) \{{.*?\n      \}}\n(?=\n      function {re.escape(next_name)}\()"
    return replace_regex(text, pattern, new_source.rstrip() + "\n", f"replace function {start_name}")


html = HTML_PATH.read_text(encoding="utf-8")
require("Issue #119 role/session contract" not in html, "issue #119 changes already appear to be applied")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
css = r'''

      /* Issue #119 role/session contract */
      .auth-role-card { display:flex; align-items:flex-start; gap:12px; padding:13px 14px; border:1px solid var(--line); border-radius:14px; background:var(--surface-subtle); }
      .auth-role-card strong { display:block; color:var(--ink); }
      .auth-role-card span { display:block; margin-top:3px; color:var(--muted); font-size:.85rem; line-height:1.45; }
      .auth-error { margin-top:14px; }
      .demo-auth-role { min-width:170px; }
      .demo-auth-role strong { font-size:.9rem; }
      .assignment-availability-disclosure, .weekly-availability-disclosure { overflow:visible; }
      .assignment-availability-disclosure > summary, .weekly-availability-disclosure > summary { list-style:none; cursor:pointer; }
      .assignment-availability-disclosure > summary::-webkit-details-marker, .weekly-availability-disclosure > summary::-webkit-details-marker { display:none; }
      .assignment-availability-disclosure > summary .disclosure-chevron, .weekly-availability-disclosure > summary .disclosure-chevron { transition:transform .2s ease; }
      .assignment-availability-disclosure[open] > summary .disclosure-chevron, .weekly-availability-disclosure[open] > summary .disclosure-chevron { transform:rotate(180deg); }
      .assignment-disclosure-body, .weekly-availability-body { padding:0 20px 20px; }
      .assignment-room-type-link { display:inline; margin:0; padding:0; border:0; background:none; color:inherit; font:inherit; text-align:left; text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:3px; cursor:pointer; }
      .assignment-room-type-link:hover, .assignment-room-type-link:focus-visible { color:var(--primary); }
      button.maid-order-unassigned-chip { font:inherit; cursor:pointer; }
      button.maid-order-unassigned-chip:hover, button.maid-order-unassigned-chip:focus-visible { border-color:var(--primary); box-shadow:0 0 0 3px color-mix(in srgb,var(--primary) 14%,transparent); }
      .assignment-table tr.is-focus-target > td { animation:issue119-row-focus 1.8s ease; }
      @keyframes issue119-row-focus { 0%,100%{background:transparent} 18%,72%{background:#fff3d9} }
      .reservation-long-stay-toggle { display:flex; align-items:flex-start; gap:11px; padding:14px; border:1px solid var(--line); border-radius:14px; background:var(--surface-subtle); }
      .reservation-long-stay-toggle input { width:20px; height:20px; margin-top:2px; accent-color:var(--primary); }
      .reservation-long-stay-toggle strong, .reservation-long-stay-toggle span { display:block; }
      .reservation-long-stay-toggle span { margin-top:3px; color:var(--muted); font-size:.86rem; line-height:1.45; }
      .long-stay-badge { background:#efe7ff; color:#5941a9; border-color:#d9ccff; }
      .long-stay-checkout-field[hidden] { display:none !important; }
      @media (max-width: 720px) {
        .assignment-disclosure-body, .weekly-availability-body { padding:0 14px 14px; }
      }
'''
html = replace_once(html, "\n    </style>", css + "\n    </style>", "insert issue 119 CSS")

# ---------------------------------------------------------------------------
# Long-stay model and seeded rooms
# ---------------------------------------------------------------------------
html = replace_once(
    html,
    "      const INITIAL_RESERVATIONS = Object.freeze([",
    """      const LONG_STAY_OPEN_END_AT = '9999-12-31T23:59';
      const INITIAL_LONG_STAY_RESERVATIONS = Object.freeze(Object.entries(INITIAL_OCCUPIED_ROOMS).map(([room,stay])=>({
        id:`reservation-long-${room}`,room,checkInAt:`${stay.startedAt||'2026-01-01'}T00:00`,checkOutAt:LONG_STAY_OPEN_END_AT,
        guestCount:guestPolicyForRoom(room).defaultGuestCount,source:'long-stay',status:'active',isLongStay:true
      })));
      const INITIAL_RESERVATIONS = Object.freeze([
        ...INITIAL_LONG_STAY_RESERVATIONS,""",
    "seed long-stay reservations",
)
html = replace_once(
    html,
    "      function initialReservationDrafts(){return INITIAL_RESERVATIONS.map(reservation=>({id:`checkout-${reservation.id}`,room:reservation.room,kind:'퇴실 청소',created:'예약 연동',date:reservation.checkOutAt.slice(0,10),source:'reservation',reservationId:reservation.id,guestCount:reservationGuestCount(reservation),visibility:'private'}));}",
    "      function initialReservationDrafts(){return INITIAL_RESERVATIONS.filter(reservation=>!reservationIsLongStay(reservation)).map(reservation=>({id:`checkout-${reservation.id}`,room:reservation.room,kind:'퇴실 청소',created:'예약 연동',date:reservation.checkOutAt.slice(0,10),source:'reservation',reservationId:reservation.id,guestCount:reservationGuestCount(reservation),visibility:'private'}));}",
    "exclude long stays from initial cleaning drafts",
)
html = replace_once(
    html,
    "      function reservationCurrentMoment() { return `${state.selectedDate}T${state.time}`; }",
    """      function reservationIsLongStay(reservation) { return reservation?.isLongStay===true; }
      function roomHasActiveLongStay(no,targetState=state) { return activeReservationsFor(targetState,String(no)).some(reservationIsLongStay); }
      function reservationStayLengthLabel(reservation) { return reservationIsLongStay(reservation)?'장기':`${reservationNights(reservation)}박`; }
      function reservationCurrentMoment() { return `${state.selectedDate}T${state.time}`; }""",
    "add long-stay helpers",
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
    "long-stay nights",
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
html = function_block(
    html,
    "projectReservationState",
    "roomDataIssue",
    r'''      function projectReservationState(targetState,roomNos=null) {
        const selected=roomNos?new Set([].concat(roomNos).map(String)):null,moment=operationalMoment(targetState);
        ROOMS.forEach(room=>{
          if(selected&&!selected.has(room.no))return;
          const reservations=activeReservationsFor(targetState,room.no),current=reservations.find(item=>item.checkInAt<=moment&&moment<item.checkOutAt)||null,future=reservations.find(item=>item.checkInAt>moment)||null,completed=(targetState.reservations||[]).filter(item=>item.room===room.no&&item.status!=='cancelled'&&item.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null,projected=current||future||completed||null;
          if(projected){const projectedLong=reservationIsLongStay(projected);room.reservationCheckinAt=projected.checkInAt;room.reservationCheckoutAt=projected.checkOutAt;room.nextCheckinAt=projected.checkInAt;room.nextCheckoutAt=projected.checkOutAt;room.reservationProjectionId=projected.id;room.checkin=projected.checkInAt.slice(11,16);room.checkout=projectedLong?'장기':projected.checkOutAt.slice(11,16);room.longStay=projectedLong;}else if(room.reservationProjectionId){delete room.reservationCheckinAt;delete room.reservationCheckoutAt;delete room.nextCheckinAt;delete room.nextCheckoutAt;delete room.reservationProjectionId;delete room.longStay;room.checkin='정보 없음';room.checkout='정보 없음';}
          const override=room.occupancyOverride;
          if(override==='occupied'&&!current){room.occupancy='occupied';room.checkin=room.actualCheckinAt?.slice(11,16)||'투숙 중';room.checkout=room.longStay?'장기':(room.plannedCheckoutAt||room.reservationCheckoutAt||'예정 미입력').slice?.(11,16)||'예정 미입력';return;}
          if(override==='vacant'&&!current){room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;delete room.longStay;if(completed)room.actualCheckoutAt=completed.checkOutAt;return;}
          if(current){const currentLong=reservationIsLongStay(current);room.occupancy='occupied';room.actualCheckinAt=current.checkInAt;room.plannedCheckoutAt=current.checkOutAt;room.currentStayReservationId=current.id;room.longStay=currentLong;delete room.actualCheckoutAt;room.checkin=current.checkInAt.slice(11,16);room.checkout=currentLong?'장기':current.checkOutAt.slice(11,16);return;}
          room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;delete room.longStay;if(completed)room.actualCheckoutAt=completed.checkOutAt;else delete room.actualCheckoutAt;
        });
      }''',
)

# ---------------------------------------------------------------------------
# Authentication and role isolation
# ---------------------------------------------------------------------------
auth_helpers = r'''      const AUTH_SESSION_KEY='roomManagementAuthSessionV1';
      let volatileAuthSession=null;
      function authAccounts() {
        return [{id:'admin',password:'admin1234',role:'admin',name:'관리자',maidId:null},...MAIDS.map((maid,index)=>({id:`maid${index+1}`,password:'maid1234',role:'maid',name:maid.name,maidId:maid.id}))];
      }
      function safeAuthSession(value) {
        if(!value||!['admin','maid'].includes(value.role))return null;
        const account=authAccounts().find(item=>item.id===value.id&&item.role===value.role&&(item.role==='admin'||item.maidId===value.maidId));
        return account?{id:account.id,role:account.role,name:account.name,maidId:account.maidId}:null;
      }
      function readAuthSession() {
        try { const parsed=JSON.parse(sessionStorage.getItem(AUTH_SESSION_KEY)||'null');return safeAuthSession(parsed)||safeAuthSession(volatileAuthSession); }
        catch { return safeAuthSession(volatileAuthSession); }
      }
      function writeAuthSession(account) {
        const session=safeAuthSession(account);volatileAuthSession=session;
        try { if(session)sessionStorage.setItem(AUTH_SESSION_KEY,JSON.stringify(session)); }
        catch {}
        return session;
      }
      function clearAuthSession() { volatileAuthSession=null;try{sessionStorage.removeItem(AUTH_SESSION_KEY);}catch{} }
      function syncAuthState(targetState=state) {
        const session=readAuthSession();targetState.authSession=session;targetState.loggedIn=!!session;
        if(session){targetState.role=session.role;if(session.role==='maid'&&MAIDS.some(maid=>maid.id===session.maidId))targetState.currentMaidId=session.maidId;}
        return session;
      }

'''
html = replace_once(html, "      function baseState(id=0) {", auth_helpers + "      function baseState(id=0) {", "insert authentication helpers")
html = replace_once(html, "loggedIn:true,", "loggedIn:false,authSession:null,", "default logged-out state")
html = replace_once(
    html,
    "        syncAssignmentDateForCleaningTab(s);\n        projectReservationState(s);",
    "        syncAssignmentDateForCleaningTab(s);\n        syncAuthState(s);\n        projectReservationState(s);",
    "sync auth when scenario is created",
)
html = replace_once(
    html,
    "      const maidNav = [\n        {id:'my',label:'내 업무',icon:'briefcase'},\n        {id:'schedule',label:'근무 일정',icon:'calendar'},\n        {id:'alerts',label:'알림',icon:'bell'},\n        {id:'pay',label:'주급',icon:'wallet'},\n        {id:'more',label:'더보기',icon:'more'}\n      ];",
    "      const maidNav = [\n        {id:'my',label:'내 업무',icon:'briefcase'},\n        {id:'schedule',label:'근무 일정',icon:'calendar'},\n        {id:'pay',label:'주급',icon:'wallet'},\n        {id:'more',label:'더보기',icon:'more'}\n      ];",
    "remove maid alert navigation tab",
)
html = replace_once(
    html,
    "        const durableRenderSameState=durableRenderStateRef===state,durableBefore=durableLedgerFingerprint(state);\n        projectReservationState(state);",
    "        const durableRenderSameState=durableRenderStateRef===state,durableBefore=durableLedgerFingerprint(state);\n        syncAuthState(state);\n        projectReservationState(state);",
    "enforce auth at render boundary",
)
html = replace_once(html, "          ${renderDemoStrip()}\n          ${state.loggedIn ? `", "          ${state.loggedIn?renderDemoStrip():''}\n          ${state.loggedIn ? `", "hide demo controls before login")
html = replace_once(html, "        if(['admin','maid'].includes(route.role))state.role=route.role;\n        if(MAIDS.some(maid=>maid.id===route.currentMaidId)){state.currentMaidId=route.currentMaidId;syncSignedInMaidAvailability();}", "        const authSession=syncAuthState(state);\n        if(authSession?.role==='maid'&&MAIDS.some(maid=>maid.id===authSession.maidId)){state.currentMaidId=authSession.maidId;syncSignedInMaidAvailability();}", "block history role crossover")
html = replace_once(html, "        state.loggedIn=route.loggedIn!==false;", "        state.loggedIn=!!authSession;", "history cannot restore logged-in state")

html = function_block(
    html,
    "renderDemoStrip",
    "renderSidebar",
    r'''      function renderDemoStrip() {
        const session=readAuthSession(),roleLabel=session?.role==='admin'?'관리자':`${signedInMaidName()} · 메이드`;
        return `<section class="demo-strip ${state.demoOpen?'open':''}" aria-label="데모 도구">
          <div class="demo-strip-inner">
            <div class="demo-label"><span class="signal"></span>데모 화면 · 실제 운영 데이터 아님</div>
            <button class="icon-btn demo-toggle" type="button" data-action="toggle-demo" aria-expanded="${state.demoOpen}" aria-label="데모 도구 ${state.demoOpen?'접기':'펼치기'}">${icon('settings')}</button>
            <div class="demo-controls">
              <div class="demo-field demo-auth-role"><span>로그인 역할</span><strong>${esc(roleLabel)}</strong><small>역할 변경은 로그아웃 후 다른 아이디로 로그인합니다.</small></div>
              <div class="demo-field"><label for="demo-time">시간</label><select id="demo-time" data-control="time"><option ${state.time==='00:00'?'selected':''}>00:00</option><option ${state.time==='10:30'?'selected':''}>10:30</option><option ${state.time==='10:32'?'selected':''}>10:32</option><option ${state.time==='11:05'?'selected':''}>11:05</option><option ${state.time==='11:59'?'selected':''}>11:59</option><option ${state.time==='12:00'?'selected':''}>12:00</option><option ${state.time==='13:05'?'selected':''}>13:05</option><option ${state.time==='16:05'?'selected':''}>16:05</option><option ${state.time==='21:10'?'selected':''}>21:10</option><option ${state.time==='21:55'?'selected':''}>21:55</option><option ${state.time==='22:15'?'selected':''}>22:15</option><option ${state.time==='23:59'?'selected':''}>23:59</option></select></div>
              <div class="demo-field"><label for="demo-network">네트워크</label><select id="demo-network" data-control="network"><option value="online" ${state.network==='online'?'selected':''}>정상</option><option value="offline" ${state.network==='offline'?'selected':''}>오프라인</option><option value="stale" ${state.network==='stale'?'selected':''}>오래된 데이터</option></select></div>
              <div class="demo-field scenario"><label for="demo-scenario">시나리오</label><select id="demo-scenario" data-control="scenario">${Object.entries(SCENARIOS).map(([id,s])=>`<option value="${id}" ${state.scenario===Number(id)?'selected':''}>${id==='0'?'기본':id+'.'} ${esc(s.title)}</option>`).join('')}</select></div>
              <button class="btn btn-ghost demo-reset" type="button" data-action="reset">${icon('refresh','icon-sm')}초기 상태로 재설정</button>
            </div>
          </div>
        </section>`;
      }''',
)
html = replace_once(html, "<div class=\"side-foot\">${button('로그인 상태 보기','logout','ghost')}</div>", "<div class=\"side-foot\">${button('로그아웃','logout','ghost')}</div>", "sidebar logout label")

html = function_block(
    html,
    "renderLogin",
    "openDetail",
    r'''      function renderLogin() {
        const error=state.loginMode==='error';
        return `<main id="main-content" style="max-width:480px;padding-top:7vh"><section class="card card-pad" style="box-shadow:var(--shadow)"><div class="brand" style="padding:4px 0 22px"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리 로그인</div></div></div><div class="notice notice-info"><div><strong>아이디에 따라 화면이 분리됩니다.</strong><br>관리자는 관리자 화면만, 메이드는 본인 업무 화면만 이용합니다.</div></div>${error?`<div class="notice notice-danger auth-error" role="alert">아이디 또는 비밀번호가 일치하지 않습니다.</div>`:''}<form id="login-form" style="display:grid;gap:12px;margin-top:16px"><div class="field"><label for="login-id">로그인 아이디</label><input id="login-id" class="input-control" autocomplete="username" autocapitalize="none" spellcheck="false" placeholder="admin 또는 maid1" required></div><div class="field"><label for="login-password">로그인 비밀번호</label><input id="login-password" class="input-control" type="password" autocomplete="current-password" required><small>와이어프레임 확인용: 관리자 admin / admin1234 · 메이드 maid1~maid9 / maid1234</small></div><button class="btn btn-primary btn-block" type="submit">로그인</button></form><div class="auth-role-card" style="margin-top:14px">${icon('shield')}<div><strong>역할 간 직접 전환 없음</strong><span>다른 역할을 확인하려면 로그아웃한 뒤 해당 아이디로 다시 로그인합니다.</span></div></div></section></main>`;
      }''',
)
html = replace_once(
    html,
    "<button class=\"btn btn-outline\" type=\"button\" data-action=\"switch-role\" aria-label=\"${state.role==='admin'?'메이드 보기':'관리자 보기'}\">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button>",
    "<button class=\"btn btn-outline\" type=\"button\" data-action=\"logout\" aria-label=\"로그아웃\">${icon('logout','icon-sm')}<span>로그아웃</span></button>",
    "topbar logout",
)
html = replace_once(html, "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',alerts:'알림',pay:'내 주급',more:'더보기'};", "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',pay:'내 주급',more:'더보기'};", "remove maid alert title")
html = replace_once(html, "        if (state.maidView==='alerts') return renderMaidAlerts();\n", "", "remove maid alerts route")

# ---------------------------------------------------------------------------
# Long-stay display, reservation availability, and cleaning exclusion
# ---------------------------------------------------------------------------
html = replace_once(
    html,
    "if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false",
    "if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:room.longStay?'장기 투숙 · 퇴실일 미정':`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false",
    "long-stay room presentation",
)
html = replace_once(
    html,
    "checkinDisplay=closestReservation?reservationMomentLabel(closestReservation.checkInAt):'일정 없음',checkoutDisplay=closestReservation?reservationMomentLabel(closestReservation.checkOutAt):'일정 없음';",
    "checkinDisplay=closestReservation?reservationMomentLabel(closestReservation.checkInAt):'일정 없음',checkoutDisplay=reservationIsLongStay(closestReservation)?'장기':closestReservation?reservationMomentLabel(closestReservation.checkOutAt):'일정 없음';",
    "room card long-stay checkout",
)
html = replace_once(
    html,
    "const detailBadges=[checkoutInspectionPending(no)?'<span class=\"room-detail-badge\">퇴실점검 대상</span>':'',",
    "const detailBadges=[room.longStay?'<span class=\"room-detail-badge long-stay-badge\">장기</span>':'',checkoutInspectionPending(no)?'<span class=\"room-detail-badge\">퇴실점검 대상</span>':'',",
    "long-stay room card badge",
)
html = replace_once(
    html,
    "reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`",
    "reservationActionLabel=room.longStay?'장기 투숙 관리':weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`",
    "long-stay room action label",
)
html = replace_once(
    html,
    "      function quickRangeLabel(reservation) {\n        const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));\n        return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${end.getMonth()+1}/${end.getDate()} ${reservation.checkOutAt.slice(11,16)}`;\n      }",
    "      function quickRangeLabel(reservation) {\n        const start=dateObject(reservation.checkInAt.slice(0,10));\n        if(reservationIsLongStay(reservation))return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → 장기`;\n        const end=dateObject(reservation.checkOutAt.slice(0,10));\n        return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${end.getMonth()+1}/${end.getDate()} ${reservation.checkOutAt.slice(11,16)}`;\n      }",
    "quick long-stay range label",
)
html = replace_once(
    html,
    "      function reservationMomentLabel(value) {\n        if(!/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$/.test(value||''))return '일정 없음';",
    "      function reservationMomentLabel(value) {\n        if(value===LONG_STAY_OPEN_END_AT)return '장기';\n        if(!/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$/.test(value||''))return '일정 없음';",
    "long-stay moment label",
)
html = replace_once(
    html,
    "        if(roomIsOnHold(room.no))return '확인 필요 · 예약 불가';",
    "        if(roomIsOnHold(room.no))return '확인 필요 · 예약 불가';\n        if(roomHasActiveLongStay(room.no))return '장기 투숙 · 예약 불가';",
    "long stay blocks availability",
)
html = replace_once(
    html,
    "      function reservationCheckoutTarget(reservation,assignmentDate=reservation?.checkOutAt?.slice(0,10),targetState=state) {",
    "      function reservationCheckoutTarget(reservation,assignmentDate=reservation?.checkOutAt?.slice(0,10),targetState=state) {\n        if(reservationIsLongStay(reservation))return null;",
    "long stay has no checkout cleaning target",
)
html = replace_once(
    html,
    "      function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {",
    """      function cleaningTargetVisible(item,targetState=state) {
        const room=ROOMS.find(entry=>entry.no===String(item?.room||''));if(!room)return false;
        if(assignmentRoomHoldReason(room.no,targetState))return false;
        const linked=item?.reservationId?(targetState.reservations||[]).find(reservation=>reservation.id===item.reservationId):null;
        if(item?.kind==='퇴실 청소'&&(reservationIsLongStay(linked)||roomHasActiveLongStay(room.no,targetState)))return false;
        return true;
      }
      function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {""",
    "add central cleaning target filter",
)
html = replace_once(html, "        return [...carryovers,...live,...committedOrphans];\n      }\n      function assignmentTargets()", "        return [...carryovers,...live,...committedOrphans].filter(item=>cleaningTargetVisible(item,targetState));\n      }\n      function assignmentTargets()", "filter cleaning targets")

# ---------------------------------------------------------------------------
# Admin assignment UI: disclosures, clickable type, and room scroll focus
# ---------------------------------------------------------------------------
html = replace_once(
    html,
    "<span class=\"assignment-room-type\">${esc(type.name)}</span>",
    "<button class=\"assignment-room-type assignment-room-type-link\" type=\"button\" data-action=\"room-detail\" data-id=\"${item.room}\" aria-label=\"${item.room}호 ${esc(type.name)} 상세정보 열기\">${esc(type.name)}</button>",
    "clickable room type in assignment table",
)
html = replace_once(
    html,
    "<tr><td class=\"assignment-room-cell\">",
    "<tr id=\"assignment-room-${item.room}\" data-assignment-room=\"${item.room}\"><td class=\"assignment-room-cell\">",
    "assignment room row anchor",
)
html = replace_once(
    html,
    "<span class=\"maid-order-unassigned-chip\">${esc(item.room)}호 · ${esc(ROOM_TYPES[item.type]?.name||'객실')} · ${money(assignmentTargetRate(item))}</span>",
    "<button class=\"maid-order-unassigned-chip\" type=\"button\" data-action=\"focus-assignment-room\" data-room=\"${item.room}\" aria-label=\"${item.room}호 담당 수정으로 이동\">${esc(item.room)}호 · ${esc(ROOM_TYPES[item.type]?.name||'객실')} · ${money(assignmentTargetRate(item))}</button>",
    "unassigned room scroll button",
)
html = replace_once(
    html,
    "<section class=\"card assignment-panel\"><div class=\"section-head\"><div><h3>메이드 주간 근무표</h3><p>근무 가능일을 기준으로 담당 후보를 필터링합니다.</p></div></div>${renderAvailabilityMatrix()}</section>",
    "<details class=\"card assignment-panel assignment-availability-disclosure\"><summary class=\"section-head\"><div><h3>메이드 주간 근무표</h3><p>근무 가능일을 기준으로 담당 후보를 필터링합니다.</p></div><span class=\"disclosure-chevron\" aria-hidden=\"true\">${icon('chevronDown')}</span></summary><div class=\"assignment-disclosure-body\">${renderAvailabilityMatrix()}</div></details>",
    "collapsed admin maid schedule",
)

# ---------------------------------------------------------------------------
# Maid weekly availability disclosure
# ---------------------------------------------------------------------------
render_maid_schedule = r'''      function renderMaidSchedule() {
        const phase=availabilitySubmissionPhase(),record=currentAvailabilityRecord(),submitted=state.availabilitySubmitted&&!state.availabilityEditing&&record?.status==='submitted',range=availabilityRangeLabel(),selectedCount=availabilitySelectedDays().length,dayRows=availabilityWeekDates().map((iso,index)=>availabilityCell(index,iso,submitted)).join(''),status=submitted?statusBadge('제출 완료','green'):phase==='open'?statusBadge('등록 가능','amber'):phase==='before'?statusBadge('제출 전','neutral'):statusBadge('마감됨','neutral'),deadline=phase==='before'?`<div class="notice notice-info assignment-notice"><div><strong>일요일 ${AVAILABILITY_OPEN_TIME}부터 ${AVAILABILITY_CLOSE_TIME}까지 제출 가능</strong><br>제출 시간이 되면 근무 가능한 날짜를 선택할 수 있습니다.</div></div>`:phase==='open'?`<div class="notice notice-warning assignment-notice"><div><strong>오늘 ${AVAILABILITY_CLOSE_TIME}까지 제출</strong><br>마감 전에는 다시 제출해 내용을 바꿀 수 있습니다.</div></div>`:`<div class="notice notice-warning assignment-notice"><div><strong>제출 기간이 끝났습니다.</strong><br>변경이 필요하면 관리자에게 변경 요청을 보내세요.</div></div>`;
        const openAttr=phase==='open'?' open':'';
        return renderCoach()+renderNetworkNotice()+`<div class="weekly-availability"><details class="card week-card weekly-availability-disclosure"${openAttr}><summary class="week-card-head"><div><h2>${esc(range)}</h2><p>다음 주 근무 가능일을 제출합니다.</p></div><div class="badge-row">${status}<span class="disclosure-chevron" aria-hidden="true">${icon('chevronDown')}</span></div></summary><div class="weekly-availability-body">${deadline}<div class="availability-list">${dayRows}</div><div class="availability-summary">${icon('calendar')}<strong>가능 ${selectedCount}일 · 불가 ${7-selectedCount}일</strong></div>${submitted?`<div class="job-actions"><button class="btn btn-outline" type="button" data-action="edit-week-availability" ${phase!=='open'?'disabled':''}>제출 내용 수정</button>${phase==='closed'?button('관리자에게 변경 요청','request-availability-change','primary'):''}</div>`:`<button class="btn btn-primary btn-block" type="button" data-action="submit-week-availability" ${phase!=='open'||selectedCount===0?'disabled':''}>근무 가능일 제출</button>`}${state.availabilityChangeRequested?'<div class="notice notice-success"><div><strong>변경 요청을 보냈습니다.</strong><br>처리 결과는 상단 알림에서 확인할 수 있습니다.</div></div>':''}</div></details>${renderMaidAssignedPreview()}</div>`;
      }'''
html = function_block(html, "renderMaidSchedule", "renderMaidAlerts", render_maid_schedule)

# ---------------------------------------------------------------------------
# Reservation modal and long-stay save behavior
# ---------------------------------------------------------------------------
html = function_block(
    html,
    "reservationPreviewMarkup",
    "updateReservationTimePreview",
    r'''      function reservationPreviewMarkup(checkinAt,checkoutAt,{longStay=false}={}) {
        const status=longStay?reservationTimeStatus(checkinAt,''):reservationTimeStatus(checkinAt,checkoutAt),valid=longStay?!!checkinAt:checkinAt&&checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10),nights=!longStay&&valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;
        return `<div class="field field-full"><div class="notice notice-info" style="margin:0"><div style="width:100%"><strong>예약 기간</strong><div class="info-grid" id="reservation-time-preview" aria-live="polite" style="margin-top:10px"><div class="info-item"><span>체크인 → 체크아웃</span><strong data-reservation-night-status>${longStay?'장기':valid?`${nights}박`:'입퇴실 시각 확인 필요'}</strong></div><div class="info-item"><span>체크인 · 16:00 기준</span><strong data-reservation-checkin-status>${esc(reservationStatusText(status,'checkin'))}</strong></div><div class="info-item"><span>체크아웃</span><strong data-reservation-checkout-status>${longStay?'장기 · 퇴실일 미정':esc(reservationStatusText(status,'checkout'))}</strong></div></div></div></div><small>${longStay?'퇴실일을 정하지 않고 투숙 중으로 유지합니다.':'체크인 다음에 체크아웃을 입력하며 1시간 단위로 선택합니다.'}</small></div>`;
      }''',
)
html = function_block(
    html,
    "updateReservationTimePreview",
    "updateReservationGuestControls",
    r'''      function updateReservationTimePreview() {
        const checkinAt=document.getElementById('res-checkin')?.value||'',checkout=document.getElementById('res-checkout'),longStay=!!document.getElementById('res-long-stay')?.checked,checkoutAt=checkout?.value||'',status=reservationTimeStatus(checkinAt,longStay?'':checkoutAt);
        const checkoutField=document.querySelector('[data-long-stay-checkout-field]'),checkinStatus=document.querySelector('[data-reservation-checkin-status]'),checkoutStatus=document.querySelector('[data-reservation-checkout-status]'),nightStatus=document.querySelector('[data-reservation-night-status]');
        if(checkout){checkout.required=!longStay;checkout.disabled=longStay;}
        if(checkoutField)checkoutField.hidden=longStay;
        if(checkinStatus)checkinStatus.textContent=reservationStatusText(status,'checkin');
        if(checkoutStatus)checkoutStatus.textContent=longStay?'장기 · 퇴실일 미정':reservationStatusText(status,'checkout');
        if(nightStatus){const valid=checkinAt&&(longStay||checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10)),nights=!longStay&&valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;nightStatus.textContent=longStay?'장기':valid?`${nights}박`:'입퇴실 시각 확인 필요';}
      }''',
)
html = replace_once(
    html,
    "checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no)",
    "longStay=reservationIsLongStay(existing)||currentEntry&&room.longStay===true,checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':longStay?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no)",
    "reservation modal long-stay calculation",
)
html = replace_once(
    html,
    "subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.'",
    "subtitle:longStay?'퇴실일을 정하지 않은 장기 투숙입니다.':'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.'",
    "reservation modal subtitle",
)
html = replace_once(
    html,
    "</div></div><div class=\"field\"><label for=\"res-checkin\">1. 체크인 일시</label>",
    "</div></div><div class=\"field field-full\"><label class=\"reservation-long-stay-toggle\" for=\"res-long-stay\"><input id=\"res-long-stay\" type=\"checkbox\" data-control=\"reservation-long-stay\" ${longStay?'checked':''}><span><strong>장기 투숙으로 등록</strong><span>퇴실일 없이 투숙 중으로 유지하고 예약 가능 객실·일반 퇴실 청소 대상에서 제외합니다.</span></span></label></div><div class=\"field\"><label for=\"res-checkin\">1. 체크인 일시</label>",
    "insert long-stay reservation toggle",
)
html = replace_once(
    html,
    "<div class=\"field\"><label for=\"res-checkout\">2. 체크아웃 일시</label><input id=\"res-checkout\" class=\"input-control\" type=\"datetime-local\" step=\"3600\" value=\"${esc(checkoutAt)}\" required>",
    "<div class=\"field long-stay-checkout-field\" data-long-stay-checkout-field ${longStay?'hidden':''}><label for=\"res-checkout\">2. 체크아웃 일시</label><input id=\"res-checkout\" class=\"input-control\" type=\"datetime-local\" step=\"3600\" value=\"${esc(checkoutAt)}\" ${longStay?'disabled':'required'}>",
    "hide checkout for long stay",
)
html = replace_once(html, "${reservationPreviewMarkup(checkinAt,checkoutAt)}", "${reservationPreviewMarkup(checkinAt,checkoutAt,{longStay})}", "long-stay reservation preview")
html = replace_once(
    html,
    "<span class=\"reservation-list-meta\">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span>",
    "<span class=\"reservation-list-meta\">${reservationStayLengthLabel(reservation)} · ${reservationGuestCount(reservation)}명</span>",
    "reservation list stay length",
)
html = replace_once(
    html,
    "const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정')",
    "const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=reservationIsLongStay(reservation)?'장기 투숙':readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정')",
    "long stay schedule status",
)
html = replace_regex(
    html,
    r"      function reservationPayloadMatches\(item,\{roomNo,checkInAt,checkOutAt,guestCount\}\) \{.*?\n      \}\n      function clearOrphanedReservationDraftJob",
    r'''      function reservationPayloadMatches(item,{roomNo,checkInAt,checkOutAt,guestCount,isLongStay=false}) { return item?.status==='active'&&item.room===String(roomNo)&&item.checkInAt===checkInAt&&item.checkOutAt===checkOutAt&&reservationGuestCount(item)===Number(guestCount)&&reservationIsLongStay(item)===!!isLongStay; }
      function clearLongStayCleaningArtifacts(reservation) {
        const draftIds=new Set((state.drafts||[]).filter(draft=>draft.reservationId===reservation.id).map(draft=>draft.id));
        state.drafts=(state.drafts||[]).filter(draft=>draft.reservationId!==reservation.id);state.selectedDrafts=(state.selectedDrafts||[]).filter(id=>!draftIds.has(id));
        draftIds.forEach(targetId=>{const record=state.assignments?.[targetId];if(record&&!record.maidId&&!record.previousMaidId)delete state.assignments[targetId];const target=state.cleaningTargets?.[targetId];if(target&&!target.currentAttemptId)delete state.cleaningTargets[targetId];});
      }
      function upsertReservationRecord({id='',roomNo,checkInAt,checkOutAt,guestCount,source='card',currentStay=false,isLongStay=false}) {
        checkOutAt=isLongStay?LONG_STAY_OPEN_END_AT:checkOutAt;
        const previous=id?state.reservations.find(item=>item.id===id&&item.status==='active')||null:null,before=previous?{...previous}:null,room=ROOMS.find(item=>item.no===String(roomNo)),beforeReservations=activeReservationsFor(state,String(roomNo)).map(item=>({...item}));
        if(!room)return {error:'객실 정보를 찾을 수 없습니다.'};
        if(id&&!previous)return {error:'이 예약은 이미 변경되었거나 취소되었습니다. 최신 예약을 다시 열어 주세요.'};
        const now=reservationCurrentMoment(),linkedCurrentStay=!!before&&room.occupancy==='occupied'&&currentOccupiedReservation(room)?.id===before.id,unchangedPastStaySchedule=linkedCurrentStay&&before.checkInAt===checkInAt&&before.checkOutAt===checkOutAt&&reservationIsLongStay(before)===!!isLongStay;
        if(previous&&reservationRecordIsPast(previous))return {error:'지난 예약 기록은 조회만 가능하며 수정할 수 없습니다.'};
        if(!isLongStay&&checkOutAt<=now&&!unchangedPastStaySchedule)return {error:'이미 지난 일정은 예약으로 새로 등록하거나 옮길 수 없습니다. 현재 투숙 중이면 체크아웃을 미래 시각으로 연장해 주세요.'};
        const policy=guestPolicyForRoom(room.no),resolvedGuestCount=guestCount===undefined||guestCount===null||guestCount===''?(previous?reservationGuestCount(previous):policy.defaultGuestCount):Number(guestCount);
        if(!Number.isInteger(resolvedGuestCount)||resolvedGuestCount<1||resolvedGuestCount>policy.maxGuestCount)return {error:`${ROOM_TYPES[policy.typeId].name} 객실은 숙박 인원을 1명부터 최대 ${policy.maxGuestCount}명까지 저장할 수 있습니다.`,guestError:true};
        const registeringCurrentStay=!before&&currentStay===true&&room.occupancy==='occupied'&&!occupiedReservationEnd(room)&&checkInAt<=now&&(isLongStay||checkOutAt>now);
        if(currentStay===true&&!registeringCurrentStay)return {error:'현재 투숙 정보는 실제 체크인이 현재 시각 이전이어야 합니다. 일반 예약은 예정 체크아웃도 현재 이후로 입력해 주세요.'};
        if(checkInAt<now&&!registeringCurrentStay&&!linkedCurrentStay&&(!before||checkInAt!==before.checkInAt))return {error:'새 예약과 미래 예약 변경은 현재 시각 이후의 체크인으로 입력해 주세요.'};
        if(linkedCurrentStay&&checkInAt>now)return {error:'현재 투숙 중인 예약의 체크인을 미래 시각으로 옮길 수 없습니다. 실제 입실 시각을 확인해 주세요.'};
        const payload={roomNo:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,isLongStay},duplicateReservation=!id?activeReservationsFor(state,room.no).find(item=>reservationPayloadMatches(item,payload))||null:null,unchangedReservation=!!previous&&reservationPayloadMatches(previous,payload);
        if(duplicateReservation)return {reservation:duplicateReservation,previous:null,duplicate:true,unchanged:true};
        if(unchangedReservation)return {reservation:previous,previous:before,duplicate:true,unchanged:true};
        const scheduleChanged=!!before&&(before.checkInAt!==checkInAt||before.checkOutAt!==checkOutAt||reservationIsLongStay(before)!==!!isLongStay),guestCountChanged=!!before&&reservationGuestCount(before)!==resolvedGuestCount,candidate={...(previous||{}),id:id||'reservation-candidate',room:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,isLongStay:!!isLongStay,status:'active'},prospectiveReservations=[...beforeReservations.filter(item=>item.id!==candidate.id),candidate].sort((left,right)=>left.checkInAt.localeCompare(right.checkInAt)),cleaningChanges=reservationCleaningChanges(beforeReservations,prospectiveReservations),roomCleaningChanged=cleaningChanges.length>0;
        if(roomCleaningChanged&&reservationCleaningChangeTouchesPublic(cleaningChanges,room.no))return {error:`${room.no}호의 영향을 받는 청소 작업이 이미 공개되어 예약 일정·인원을 바로 바꿀 수 없습니다. 청소 화면에서 공개·담당 영향을 먼저 조율해 주세요.`};
        if(roomCleaningChanged&&reservationCleaningChangeTouchesRandom(cleaningChanges))return {error:'이 예약과 연결된 랜덤 배정 초안이 있습니다. 해당 청소 배정에서 초안을 되돌린 뒤 다시 저장해 주세요.'};
        const activeAttempt=activeUnfinishedAttempt(room.no),linkedAttemptBefore=before?reservationAutomaticCleaningAttempt(before,activeAttempt):null,attemptScheduleLocked=activeAttempt&&(!!activeAttempt.startedAt||roomPinWasViewed(room.no,activeAttempt.id)||activeAttempt.accessReviewRequired||!['scheduled','claimed','unassigned'].includes(state.jobs[room.no]));
        if(linkedAttemptBefore?.performerId&&before.checkOutAt.slice(0,10)!==checkOutAt.slice(0,10))return {error:`${room.no}호 퇴실 청소 담당의 업무일이 이미 ${quickDateLabel(before.checkOutAt.slice(0,10))}로 잡혀 있습니다. 체크아웃 날짜를 바꾸려면 청소 화면에서 담당·업무일을 먼저 조율해 주세요.`};
        if(attemptScheduleLocked){const workDate=attemptWorkDate(activeAttempt,state.selectedDate),timingChanged=reservationWorkTimingFingerprint(beforeReservations,workDate)!==reservationWorkTimingFingerprint(prospectiveReservations,workDate);if(timingChanged)return {error:`${room.no}호는 연결된 퇴실 청소 수행 회차가 있거나 PIN 사용이 시작되어 출입 시각·준비 마감을 바꿀 수 없습니다. 객실의 출입·청소 충돌을 먼저 확인해 주세요.`};}
        const exactOverlap=reservationOverlaps(room.no,checkInAt,checkOutAt,id);if(exactOverlap)return {error:`${room.no}호 ${quickRangeLabel(exactOverlap)} · 기존 예약과 실제 체크인·체크아웃 시각이 겹칩니다.`,conflict:exactOverlap};
        if(!isLongStay){const firstNight=checkInAt.slice(0,10),lastNight=shiftIsoDate(checkOutAt.slice(0,10),-1),conflict=quickReservationConflict(room.no,firstNight,lastNight,id,checkInAt,checkOutAt,registeringCurrentStay);if(conflict)return {error:`${room.no}호 ${quickDateLabel(conflict.date)} · ${conflict.reason}`,conflict};}
        const reservationId=id||`reservation-${room.no}-${checkInAt.slice(0,10).replaceAll('-','')}-${++state.reservationSequence}`;
        const reservation=previous||{id:reservationId,room:room.no,source,status:'active',createdAt:`${state.selectedDate}T${state.time}`};
        Object.assign(reservation,{room:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,isLongStay:!!isLongStay,source:previous?.source||source,status:'active',updatedAt:`${state.selectedDate}T${state.time}`});
        if(!previous)state.reservations.push(reservation);
        if(registeringCurrentStay||linkedCurrentStay||isLongStay){room.actualCheckinAt=checkInAt;room.plannedCheckoutAt=checkOutAt;room.currentStayReservationId=reservation.id;room.longStay=!!isLongStay;}
        if(isLongStay)clearLongStayCleaningArtifacts(reservation);else{syncReservationCleaningDraft(reservation,before);syncUnstartedReservationCleaningAttempt(reservation,linkedAttemptBefore);const checkoutDate=reservation.checkOutAt.slice(0,10),checkoutDateChanged=!before||reservationIsLongStay(before)||before.checkOutAt.slice(0,10)!==checkoutDate;if(checkoutDateChanged){const {record,changed,maidId}=syncReservationAssignmentScheduleState(reservation,checkoutDate,{reopenSameReservation:true});if(record&&maidId&&changed)appendEvent(`${room.no}호 예약 ${before?'체크아웃 이동':'접수'} · 청소 재통보 필요`,`${reservation.checkOutAt.slice(11,16)} 체크아웃 · ${maidName(maidId)}의 기존 통보 일정 유지`,{maidIds:[maidId],roomId:room.no});}}
        syncAdjacentReservationCleaningSchedules(room.no,beforeReservations);projectReservationState(state,room.no);state.reservationSaved=true;
        const guestChange=guestCountChanged?` · 숙박 인원 ${reservationGuestCount(before)}명 → ${resolvedGuestCount}명`:` · 숙박 인원 ${resolvedGuestCount}명`;
        appendEvent(`${room.no}호 ${isLongStay?'장기 투숙':'예약'} ${previous?'변경':'접수'}`,`${previous?`${quickRangeLabel(before)} → `:''}${quickRangeLabel(reservation)} · ${reservationStayLengthLabel(reservation)}${guestChange}${previous?' · 예약정보 수정':isLongStay?' · 퇴실일 미정':' · 퇴실 청소 준비'}`,{roomId:room.no,dedupeKey:`reservation:${reservation.id}:${reservationFingerprint(reservation)}`});
        return {reservation,previous:before};
      }
      function clearOrphanedReservationDraftJob''',
    "replace long-stay-aware reservation upsert",
)
html = replace_once(
    html,
    "const roomNo=document.getElementById('res-room')?.value||'',checkinAt=document.getElementById('res-checkin')?.value||'',checkoutAt=document.getElementById('res-checkout')?.value||'',guestCount=Number(document.getElementById('res-guests')?.value),id=document.getElementById('res-id')?.value||'',expectedFingerprint=document.getElementById('res-fingerprint')?.value||'',currentStay=document.getElementById('res-current-stay')?.value==='1';",
    "const roomNo=document.getElementById('res-room')?.value||'',checkinAt=document.getElementById('res-checkin')?.value||'',isLongStay=!!document.getElementById('res-long-stay')?.checked,enteredCheckoutAt=document.getElementById('res-checkout')?.value||'',checkoutAt=isLongStay?LONG_STAY_OPEN_END_AT:enteredCheckoutAt,guestCount=Number(document.getElementById('res-guests')?.value),id=document.getElementById('res-id')?.value||'',expectedFingerprint=document.getElementById('res-fingerprint')?.value||'',currentStay=document.getElementById('res-current-stay')?.value==='1';",
    "long-stay reservation save fields",
)
html = replace_once(
    html,
    "if(!validDateTime(checkinAt)||!validDateTime(checkoutAt)||checkinAt>=checkoutAt||checkinAt.slice(0,10)>=checkoutAt.slice(0,10))",
    "if(!validDateTime(checkinAt)||!isLongStay&&(!validDateTime(checkoutAt)||checkinAt>=checkoutAt||checkinAt.slice(0,10)>=checkoutAt.slice(0,10)))",
    "long-stay reservation date validation",
)
html = replace_once(
    html,
    "if(checkinAt.slice(14,16)!=='00'||checkoutAt.slice(14,16)!=='00')",
    "if(checkinAt.slice(14,16)!=='00'||!isLongStay&&checkoutAt.slice(14,16)!=='00')",
    "long-stay hour validation",
)
html = replace_once(
    html,
    "const result=upsertReservationRecord({id,roomNo,checkInAt:checkinAt,checkOutAt:checkoutAt,guestCount,currentStay,source:'card'});",
    "const result=upsertReservationRecord({id,roomNo,checkInAt:checkinAt,checkOutAt:checkoutAt,guestCount,currentStay,isLongStay,source:isLongStay?'long-stay':'card'});",
    "pass long-stay to upsert",
)
html = replace_once(
    html,
    "toast(`${roomNo}호 ${result.duplicate?'동일 예약 유지':id?'예약정보 수정':'예약 접수'} · ${reservationNights(result.reservation)}박 · ${reservationGuestCount(result.reservation)}명${earlyLate.length?` · ${earlyLate.join(' · ')}`:''}${result.duplicate?' · 중복 생성 없음':''}`);",
    "toast(`${roomNo}호 ${result.duplicate?'동일 예약 유지':isLongStay?id?'장기 투숙 수정':'장기 투숙 등록':id?'예약정보 수정':'예약 접수'} · ${reservationStayLengthLabel(result.reservation)} · ${reservationGuestCount(result.reservation)}명${earlyLate.length?` · ${earlyLate.join(' · ')}`:''}${result.duplicate?' · 중복 생성 없음':''}`);",
    "long-stay reservation toast",
)

# ---------------------------------------------------------------------------
# Event handlers: role isolation, login/logout, scroll target, long-stay toggle
# ---------------------------------------------------------------------------
html = replace_once(html, "['quick-reservation-edit','quick-month-shift'", "['focus-assignment-room','quick-reservation-edit','quick-month-shift'", "register focus assignment action")
html = replace_once(
    html,
    "if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action=\"switch-role\"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}",
    "if(a==='switch-role'){syncAuthState(state);render();toast('역할은 로그인 계정으로 고정됩니다. 다른 역할은 로그아웃 후 로그인하세요.','error');return;}\n        if(a==='logout'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;clearAuthSession();closeModal();state.loggedIn=false;state.authSession=null;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('#login-id')?.focus());return;}\n        if(a==='focus-assignment-room'){const roomNo=String(el.dataset.room||'');state.assignmentTypeFilter='all';render();requestAnimationFrame(()=>{const row=document.getElementById(`assignment-room-${roomNo}`);if(!row){toast(`${roomNo}호 담당 수정 행을 찾지 못했습니다.`,'error');return;}row.classList.add('is-focus-target');row.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});row.querySelector('[data-action=\"room-detail\"]')?.focus({preventScroll:true});setTimeout(()=>row.classList.remove('is-focus-target'),1900);});return;}",
    "role isolation logout and assignment focus",
)
html = replace_once(html, "'reservation-cancel-reason'].includes(c)", "'reservation-cancel-reason','reservation-long-stay'].includes(c)", "register reservation long-stay control")
html = replace_once(html, "        if(c==='reservation-room'){updateReservationGuestControls(true);return;}", "        if(c==='reservation-long-stay'){updateReservationTimePreview();return;}\n        if(c==='reservation-room'){updateReservationGuestControls(true);return;}", "handle reservation long-stay toggle")
html = replace_once(html, "if(c==='role'){state.role=e.target.value;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"role\"]')?.focus());}", "if(c==='role'){syncAuthState(state);render();toast('역할은 로그인 계정으로 고정됩니다.','error');}", "guard legacy role change")
html = replace_once(html, "if(c==='role'){maskPin();closeModal();state.role=e.target.value;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"role\"]')?.focus());return;}", "if(c==='role'){maskPin();closeModal();syncAuthState(state);render();toast('역할은 로그인 계정으로 고정됩니다.','error');return;}", "guard rebuilt role change")
html = replace_once(html, "if(c==='maid-account'){if(state.role!=='maid')return;maskPin();closeModal();state.currentMaidId=MAIDS.some(maid=>maid.id===e.target.value)?e.target.value:'m1';syncSignedInMaidAvailability();state.detail=null;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"maid-account\"]')?.focus());toast(`${signedInMaidName()} 계정으로 전환했습니다.`);return;}", "if(c==='maid-account'){maskPin();closeModal();syncAuthState(state);render();toast('메이드 계정은 로그인 아이디로 고정됩니다.','error');return;}", "guard maid account change")
html = replace_once(
    html,
    "if(e.target.id==='login-form'){e.preventDefault();state.loggedIn=true;state.loginMode='normal';render();toast('데모 역할 화면으로 로그인했습니다.');}",
    "if(e.target.id==='login-form'){e.preventDefault();const loginId=document.getElementById('login-id')?.value.trim().toLowerCase()||'',password=document.getElementById('login-password')?.value||'',account=authAccounts().find(item=>item.id===loginId&&item.password===password);if(!account){state.loginMode='error';render();requestAnimationFrame(()=>document.getElementById('login-id')?.focus());return;}writeAuthSession(account);state.loginMode='normal';state.detail=null;state.adminView='today';state.maidView='my';syncAuthState(state);syncSignedInMaidAvailability();render();toast(`${account.role==='admin'?'관리자':account.name} 계정으로 로그인했습니다.`);}",
    "real demo login submit",
)
html = replace_once(html, "else if(a==='logout'){state.loggedIn=false;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('#login-id')?.focus());}", "else if(a==='logout'){clearAuthSession();state.loggedIn=false;state.authSession=null;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('#login-id')?.focus());}", "legacy logout clears session")

# ---------------------------------------------------------------------------
# Documentation labels and static source checks
# ---------------------------------------------------------------------------
html = html.replace("${esc(plannedCheckoutLabel(room))}", "${esc(room.longStay?'장기':plannedCheckoutLabel(room))}")
html = replace_once(html, "activeReservationsFor(targetState).filter(reservation=>reservation.checkOutAt.slice(0,10)===assignmentDate)", "activeReservationsFor(targetState).filter(reservation=>!reservationIsLongStay(reservation)&&reservation.checkOutAt.slice(0,10)===assignmentDate)", "automatic long-stay cleaning exclusion")

HTML_PATH.write_text(html, encoding="utf-8")

check_path = ROOT / "scripts/check-issue-119.mjs"
check_path.write_text(r'''#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const html=readFileSync(resolve('WIREFRAME/index.html'),'utf8');
const required=[
  "const AUTH_SESSION_KEY='roomManagementAuthSessionV1'",
  "{id:'admin',password:'admin1234',role:'admin'",
  "password:'maid1234',role:'maid'",
  'clearAuthSession();state.loggedIn=false',
  "const LONG_STAY_OPEN_END_AT = '9999-12-31T23:59'",
  'isLongStay:true',
  "reservationIsLongStay(reservation)?'장기'",
  'id="res-long-stay"',
  "isLongStay?LONG_STAY_OPEN_END_AT",
  'function cleaningTargetVisible(item,targetState=state)',
  '.filter(item=>cleaningTargetVisible(item,targetState))',
  'assignment-availability-disclosure',
  "phase==='open'?' open':''",
  'data-action="focus-assignment-room"',
  'id="assignment-room-${item.room}"',
  'assignment-room-type-link',
  "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',pay:'내 주급',more:'더보기'}",
];
for(const contract of required){if(!html.includes(contract))throw new Error(`Issue #119 contract missing: ${contract}`);}
for(const removed of ["{id:'alerts',label:'알림',icon:'bell'}","if (state.maidView==='alerts') return renderMaidAlerts();","data-action=\"switch-role\" aria-label=\"${state.role==='admin'?'메이드 보기':'관리자 보기'}\""]){if(html.includes(removed))throw new Error(`Issue #119 removed contract remains: ${removed}`);}
const inlineScripts=[...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(match=>match[1]);
if(!inlineScripts.length)throw new Error('No inline script found.');
for(const script of inlineScripts)new Function(script);
console.log('Issue #119 source contracts and JavaScript syntax verified.');
''', encoding="utf-8")

doc17 = ROOT / "DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md"
doc17.write_text(doc17.read_text(encoding="utf-8") + r'''

## 2026-08-30 · 종료일 미정 장기 투숙 결정

- `장기 투숙`은 체크아웃 날짜가 없는 별도 예약 유형으로 저장한다.
- 화면에는 내부 종료일 표현을 노출하지 않고 `장기` 배지만 표시한다.
- 장기 투숙 객실은 `투숙 중`을 유지하며 예약 가능 객실과 일반 퇴실 청소 후보에서 제외한다.
- 연박·추가 청소처럼 관리자가 명시적으로 만든 청소 요청은 계속 허용한다.
- 실제 퇴실이 확인되면 `지금 체크아웃`으로 투숙을 종료하고 그 시점에 퇴실 청소를 만든다.
''', encoding="utf-8")

qa = ROOT / "WIREFRAME/QA.md"
qa.write_text(qa.read_text(encoding="utf-8") + r'''

## Issue #119 · 역할 로그인·청소 배정·장기 투숙

- [ ] 로그아웃 상태에서 관리자/메이드 화면이 보이지 않고 로그인 화면만 표시된다.
- [ ] `admin / admin1234`는 관리자 화면, `maid1~maid9 / maid1234`는 각 메이드 화면으로 진입한다.
- [ ] 로그인 후 역할 전환 UI가 없고 로그아웃 후 다른 역할로만 진입할 수 있다.
- [ ] 메이드 내비게이션에 알림 탭이 없고 상단 종 모양 알림함은 정상 동작한다.
- [ ] 오늘/내일 청소 배정의 메이드 근무표가 처음에는 접혀 있다.
- [ ] 미배정 객실 버튼을 누르면 객실별 담당 수정의 같은 객실 행으로 이동·강조된다.
- [ ] 청소 배정 표의 객실 타입을 누르면 해당 객실 상세가 열린다.
- [ ] 정보 확인 필요·운영 중지·촛불 미회수·장기 투숙의 일반 퇴실 청소는 배정 목록에 나타나지 않는다.
- [ ] 근무 가능일은 제출 기간에만 처음부터 펼쳐지고 그 밖의 기간에는 접혀 있다.
- [ ] 예약 등록/수정에서 장기 투숙을 선택하면 체크아웃 입력이 사라지고 `장기`로 저장된다.
- [ ] 장기 투숙 객실은 투숙 중, `장기` 배지, 예약 불가 상태를 유지한다.
''', encoding="utf-8")

readme = ROOT / "WIREFRAME/README.md"
readme.write_text(readme.read_text(encoding="utf-8") + r'''

## Issue #119 데모 로그인

- 관리자: `admin` / `admin1234`
- 메이드: `maid1`~`maid9` / `maid1234`
- 이 로그인은 단일 HTML 와이어프레임의 역할별 화면·세션 가드 확인용이다. 운영 환경의 실제 인증·인가와 비밀번호 검증은 백엔드에서 구현해야 한다.
''', encoding="utf-8")

sums_path = ROOT / "SHA256SUMS.txt"
lines=[]
for raw in sums_path.read_text(encoding="utf-8").splitlines():
    if not raw.strip():
        continue
    _, rel = raw.split(None, 1)
    data=(ROOT / rel).read_bytes()
    lines.append(f"{hashlib.sha256(data).hexdigest()}  {rel}")
sums_path.write_text("\n".join(lines), encoding="utf-8")

print("Applied issue #119 changes.")
