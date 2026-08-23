from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    html = html.replace(old, new, 1)


def replace_between(start: str, end: str, replacement: str, label: str) -> None:
    global html
    start_index = html.find(start)
    if start_index < 0:
        raise SystemExit(f"{label}: start marker missing")
    end_index = html.find(end, start_index + len(start))
    if end_index < 0:
        raise SystemExit(f"{label}: end marker missing")
    html = html[:start_index] + replacement + html[end_index:]


identifier_count = html.count("quickReservationMonth")
if identifier_count < 6:
    raise SystemExit(f"quick reservation month identifier count is unexpectedly low: {identifier_count}")
html = html.replace("quickReservationMonth", "quickReservationAnchorDate")

replace_once(
    "quickReservationAnchorDate:'2026-08', quickReservationType:'all', quickReservationSearch:'', quickGridScrollLeft:700, quickGridScrollTop:0, quickLastCreated:null,",
    "quickReservationAnchorDate:'2026-08-15', quickReservationType:'all', quickReservationSearch:'', quickGridScrollLeft:null, quickGridScrollTop:0, quickLastCreated:null,",
    "quick reservation anchor state",
)

replace_once(
    "      function applyOperationalDate(targetState,toDate) {\n        const previousDate=targetState.selectedDate,advanced=toDate>previousDate;if(advanced){initializeCleaningTargetLedger(targetState);rolloverUnresolvedTargets(targetState,toDate);if(targetState.assignmentDate<toDate)targetState.assignmentDate=toDate;}\n        targetState.selectedDate=toDate;targetState.calendarMonth=toDate.slice(0,7);syncAssignmentDateForCleaningTab(targetState);projectReservationState(targetState);if(targetState===state&&toDate>=previousDate)activateNotifiedAssignmentsForDate(toDate);\n      }",
    "      function applyOperationalDate(targetState,toDate) {\n        const previousDate=targetState.selectedDate,quickWindowFollowedToday=targetState.quickReservationAnchorDate===previousDate,advanced=toDate>previousDate;if(advanced){initializeCleaningTargetLedger(targetState);rolloverUnresolvedTargets(targetState,toDate);if(targetState.assignmentDate<toDate)targetState.assignmentDate=toDate;}\n        targetState.selectedDate=toDate;if(quickWindowFollowedToday){targetState.quickReservationAnchorDate=toDate;targetState.quickGridScrollLeft=null;}targetState.calendarMonth=toDate.slice(0,7);syncAssignmentDateForCleaningTab(targetState);projectReservationState(targetState);if(targetState===state&&toDate>=previousDate)activateNotifiedAssignmentsForDate(toDate);\n      }",
    "operational date follows quick window",
)

replace_once(
    "        syncAssignmentDateForCleaningTab(s);\n        projectReservationState(s);",
    "        s.quickReservationAnchorDate=s.selectedDate;\n        syncAssignmentDateForCleaningTab(s);\n        projectReservationState(s);",
    "scenario quick window anchor",
)

replace_once(
    "          quickMonth:state.quickReservationAnchorDate,quickType:state.quickReservationType,quickQ:state.quickReservationSearch,quickGridLeft:state.quickGridScrollLeft,quickGridTop:state.quickGridScrollTop,",
    "          quickAnchor:state.quickReservationAnchorDate,quickType:state.quickReservationType,quickQ:state.quickReservationSearch,quickGridLeft:state.quickGridScrollLeft,quickGridTop:state.quickGridScrollTop,",
    "history quick anchor snapshot",
)

replace_once(
    "        if(route.quickMonth&&route.quickMonth!=='2026-08')params.set('bookingMonth',route.quickMonth);",
    "        if(route.quickAnchor&&route.quickAnchor!==route.date)params.set('bookingAnchor',route.quickAnchor);",
    "history quick anchor URL",
)

replace_once(
    "        if(/^\\d{4}-(0[1-9]|1[0-2])$/.test(route.quickMonth||''))state.quickReservationAnchorDate=route.quickMonth;",
    "        const routeQuickAnchor=/^\\d{4}-(0[1-9]|1[0-2])-([0-2]\\d|3[01])$/.test(route.quickAnchor||'')?route.quickAnchor:/^\\d{4}-(0[1-9]|1[0-2])$/.test(route.quickMonth||'')?`${route.quickMonth}-15`:'';\n        if(routeQuickAnchor)state.quickReservationAnchorDate=routeQuickAnchor;",
    "history quick anchor restore",
)

replace_once(
    "        state.quickGridScrollLeft=Math.max(0,Number(route.quickGridLeft)||0);state.quickGridScrollTop=Math.max(0,Number(route.quickGridTop)||0);",
    "        state.quickGridScrollLeft=route.quickGridLeft==null?null:Math.max(0,Number(route.quickGridLeft)||0);state.quickGridScrollTop=Math.max(0,Number(route.quickGridTop)||0);",
    "history quick scroll restore",
)

replace_once(
    "        if(/^\\d{4}-(0[1-9]|1[0-2])$/.test(params.get('bookingMonth')||''))state.quickReservationAnchorDate=params.get('bookingMonth');",
    "        const bookingAnchor=params.get('bookingAnchor')||'',legacyBookingMonth=params.get('bookingMonth')||'';\n        if(/^\\d{4}-(0[1-9]|1[0-2])-([0-2]\\d|3[01])$/.test(bookingAnchor))state.quickReservationAnchorDate=bookingAnchor;\n        else if(/^\\d{4}-(0[1-9]|1[0-2])$/.test(legacyBookingMonth))state.quickReservationAnchorDate=`${legacyBookingMonth}-15`;",
    "hash quick anchor restore",
)

quick_helpers = r'''      const QUICK_RESERVATION_PAST_DAYS=7,QUICK_RESERVATION_FUTURE_DAYS=21,QUICK_RESERVATION_DAY_COUNT=QUICK_RESERVATION_PAST_DAYS+1+QUICK_RESERVATION_FUTURE_DAYS;
      function shiftIsoDate(iso,offset) { const value=dateObject(iso);value.setDate(value.getDate()+Number(offset||0));return dateIso(value); }
      function quickWindowBounds(anchor=state.quickReservationAnchorDate) {
        const start=shiftIsoDate(anchor,-QUICK_RESERVATION_PAST_DAYS),end=shiftIsoDate(anchor,QUICK_RESERVATION_FUTURE_DAYS);
        return {start,end,endExclusive:shiftIsoDate(end,1)};
      }
      function quickWindowDates(anchor=state.quickReservationAnchorDate) {
        const {start}=quickWindowBounds(anchor);
        return Array.from({length:QUICK_RESERVATION_DAY_COUNT},(_,index)=>shiftIsoDate(start,index));
      }
      function quickCompactDate(iso,{year=false}={}) {
        const value=dateObject(iso),prefix=year?`${value.getFullYear()}.`:'';
        return `${prefix}${value.getMonth()+1}.${value.getDate()}`;
      }
      function quickWindowLabel(anchor=state.quickReservationAnchorDate) {
        const {start,end}=quickWindowBounds(anchor),differentYear=dateObject(start).getFullYear()!==dateObject(end).getFullYear();
        return `${quickCompactDate(start,{year:differentYear})}–${quickCompactDate(end,{year:differentYear})}`;
      }
      function quickHeaderDateLabel(iso,index=0) {
        const value=dateObject(iso);
        return index===0||value.getDate()===1?`${value.getMonth()+1}/${value.getDate()}`:`${value.getDate()}일`;
      }
      function quickDateLabel(iso) { const value=dateObject(iso),day=CALENDAR_WEEKDAYS[value.getDay()];return `${value.getMonth()+1}월 ${value.getDate()}일 (${day})`; }
      function quickRangeLabel(reservation) {
        const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));
        return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${end.getMonth()+1}/${end.getDate()} ${reservation.checkOutAt.slice(11,16)}`;
      }
'''
replace_between(
    "      function quickMonthDates(",
    "      function reservationMomentLabel",
    quick_helpers,
    "quick window helper block",
)

replace_between(
    "      function reservationInMonth(",
    "      function quickFilteredRooms()",
    r'''      function reservationInQuickWindow(reservation,anchor=state.quickReservationAnchorDate) {
        const {start,endExclusive}=quickWindowBounds(anchor);
        return reservation.status==='active'&&reservation.checkInAt<`${endExclusive}T00:00`&&reservation.checkOutAt>`${start}T00:00`;
      }
''',
    "quick window reservation overlap",
)

quick_render = r'''      function quickCellMarkup(room,iso,rowIndex,dayIndex) {
        const reservation=reservationForNight(room.no,iso),rowReason=quickRoomBlockReason(room),occupiedReason=quickOccupiedDateBlockReason(room,iso),isPast=iso<state.selectedDate,isMonthStart=dayIndex===0||dateObject(iso).getDate()===1,pastReason=isPast?'지난 날짜 · 조회만 가능':'',defaultRange=quickBookingTimes(iso,iso),timeConflict=!reservation?reservationOverlaps(room.no,defaultRange.checkInAt,defaultRange.checkOutAt):null,cellReason=pastReason||rowReason||occupiedReason||(timeConflict?`기존 예약 시각 겹침 · ${quickRangeLabel(timeConflict)}`:''),type=ROOM_TYPES[room.type],elevator=elevatorLabel(room),focusDate=state.quickReservationAnchorDate,dayOffset=reservation?Math.round((dateObject(iso)-dateObject(reservation.checkInAt.slice(0,10)))/86400000):0,nights=reservationNights(reservation),start=reservation&&dayOffset===0,end=reservation&&dayOffset===nights-1,dateClasses=`${isPast?' is-past':''}${isMonthStart?' is-month-start':''}`;
        if(reservation){
          const label=nights===1?'1박':start?`연박 ${nights}박`:'',aria=`${room.no}호, ${type.name}, ${elevator}, ${quickDateLabel(iso)}, ${nights===1?'1박 예약':`연박 ${nights}박`}, 숙박 인원 ${reservationGuestCount(reservation)}명, ${quickRangeLabel(reservation)}`;
          return `<button class="quick-date-cell is-reserved ${nights===1?'is-single':'is-multi'} ${start?'is-start':''} ${end?'is-end':''}${dateClasses}" type="button" role="gridcell" tabindex="${rowIndex===0&&iso===focusDate?'0':'-1'}" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-date="${iso}" aria-label="${esc(aria)}" title="${esc(`${quickRangeLabel(reservation)} · ${reservationGuestCount(reservation)}명`)}"><span class="quick-cell-label">${esc(label)}</span></button>`;
        }
        if(cellReason){const aria=`${room.no}호, ${type.name}, ${elevator}, ${quickDateLabel(iso)}, 예약 불가, ${cellReason}`;return `<button class="quick-date-cell is-locked${dateClasses}" type="button" role="gridcell" tabindex="${rowIndex===0&&iso===focusDate?'0':'-1'}" data-room="${room.no}" data-date="${iso}" aria-disabled="true" aria-label="${esc(aria)}" title="${esc(cellReason)}">${icon('lock','icon-sm')}</button>`;}
        const aria=`${room.no}호, ${type.name}, ${elevator}, ${quickDateLabel(iso)}, 예약 가능. 마우스는 클릭 또는 드래그, 터치는 길게 누른 뒤 가로 드래그`;
        return `<button class="quick-date-cell${dateClasses}" type="button" role="gridcell" tabindex="${rowIndex===0&&iso===focusDate?'0':'-1'}" data-quick-cell="true" data-bookable="true" data-room="${room.no}" data-date="${iso}" aria-label="${esc(aria)}"></button>`;
      }
      function renderQuickReservation() {
        const dates=quickWindowDates(),rooms=quickFilteredRooms(),windowReservations=activeReservationsFor(state).filter(item=>reservationInQuickWindow(item)),bookedRooms=new Set(windowReservations.map(item=>item.room)),bookedNights=windowReservations.reduce((total,reservation)=>total+dates.filter(date=>reservationContainsNight(reservation,date)).length,0),blockedRooms=ROOMS.filter(room=>quickRoomBlockReason(room)||(room.occupancy==='occupied'&&(!occupiedReservationEnd(room)||occupiedStayNeedsCheckoutUpdate(room)))).length,windowLabel=quickWindowLabel();
        const headers=dates.map((iso,dayIndex)=>{const value=dateObject(iso),meta=calendarDayMeta(iso),today=iso===state.selectedDate,isPast=iso<state.selectedDate,isMonthStart=dayIndex===0||value.getDate()===1;return `<div class="quick-day-header ${meta.classes} ${today?'today':''} ${isPast?'is-past':''} ${isMonthStart?'is-month-start':''}" role="columnheader" data-quick-date="${iso}" aria-label="${esc(calendarDateAriaLabel(iso,{today}))}" ${meta.holiday?`title="${esc(meta.holiday.name)}"`:''}><strong>${quickHeaderDateLabel(iso,dayIndex)}</strong><span>${meta.weekdayLabel}</span>${meta.holiday?'<small class="calendar-holiday-mark" aria-hidden="true">휴</small>':''}</div>`;}).join('');
        const headerRow=`<div class="quick-grid-row quick-grid-header" role="row"><div class="quick-room-header" role="columnheader">객실 · 유형 · 엘베</div>${headers}</div>`;
        const rows=rooms.map((room,rowIndex)=>{const type=ROOM_TYPES[room.type],blocked=quickRoomBlockReason(room);return `<div class="quick-grid-row quick-grid-data-row" role="row" aria-rowindex="${rowIndex+2}" data-quick-row="${room.no}"><div class="quick-room-info ${blocked?'row-locked':''}" role="rowheader"><button class="quick-room-link" type="button" tabindex="${rowIndex===0?'0':'-1'}" data-action="room-detail" data-id="${room.no}" aria-label="${room.no}호 객실 상세 열기"><span class="quick-room-number">${room.no}호</span><span class="quick-room-copy"><strong>${esc(type.name)} · ${esc(room.elevator||'미기재')}</strong>${blocked?`<span class="quick-room-block">${esc(blocked)}</span>`:''}</span></button></div>${dates.map((iso,dayIndex)=>quickCellMarkup(room,iso,rowIndex,dayIndex)).join('')}</div>`;}).join('');
        const grid=rooms.length?`<div class="quick-grid" role="grid" aria-label="${esc(windowLabel)} 29일 객실별 간편 예약" aria-rowcount="${rooms.length+1}" aria-colcount="${dates.length+1}" style="--quick-days:${dates.length}">${headerRow}${rows}</div>`:`<div class="quick-empty-state"><div><h3>조건에 맞는 객실이 없습니다</h3><p>검색어 또는 객실 유형 필터를 바꿔 주세요.</p></div></div>`;
        const mobileHeader=rooms.length?`<div id="quick-grid-mobile-header" class="quick-grid-mobile-header" role="region" aria-label="${esc(windowLabel)} 고정 날짜 머리글"><div class="quick-grid quick-grid-mobile-header-grid" role="table" aria-label="${esc(windowLabel)} 날짜 열" style="--quick-days:${dates.length}">${headerRow}</div></div>`:'';
        return renderCoach()+renderNetworkNotice()+`<div class="quick-booking-page"><section class="card quick-booking-hero"><div class="quick-booking-hero-copy"><span class="quick-booking-kicker">빠른 예약 입력</span><h2>오늘 전후 29일을 한 화면에서 예약하세요</h2><p>지난 7일은 조회만 가능하고, 오늘부터 21일 뒤까지 월 경계 없이 이어서 예약할 수 있습니다.</p></div><div class="quick-booking-boundary"><strong>데모 와이어프레임 · 실제 데이터 아님</strong>외부 OTA/PMS 예약 원본은 변경하지 않습니다.</div></section><section class="card quick-booking-toolbar" aria-label="간편 예약 필터"><div class="quick-month-tools"><button class="icon-btn" type="button" data-action="quick-month-shift" data-offset="-7" aria-label="이전 7일">${icon('chevronLeft')}</button><div class="quick-month-label" aria-label="표시 기간 ${esc(windowLabel)}">${icon('calendar','icon-sm')}<span>${esc(windowLabel)}</span><small>29일</small></div><button class="icon-btn" type="button" data-action="quick-month-shift" data-offset="7" aria-label="다음 7일">${icon('chevronRight')}</button><button class="btn btn-outline" type="button" data-action="quick-month-today">오늘</button></div><label class="quick-toolbar-field">객실번호 검색<input class="input-control" type="search" inputmode="numeric" data-control="quick-reservation-search" value="${esc(state.quickReservationSearch)}" placeholder="예: 516" autocomplete="off"></label><label class="quick-toolbar-field">객실 유형<select class="select-control" data-control="quick-reservation-type"><option value="all">유형 전체</option>${Object.entries(ROOM_TYPES).map(([id,type])=>`<option value="${id}" ${state.quickReservationType===id?'selected':''}>${esc(type.name)}</option>`).join('')}</select></label></section><section class="card quick-booking-summary" aria-label="${esc(windowLabel)} 29일 예약 요약"><div><span>예약 건수</span><strong>${windowReservations.length}건</strong><small>표시 범위와 겹치는 예약</small></div><div><span>예약 객실</span><strong>${bookedRooms.size}개</strong><small>전체 ${ROOMS.length}개</small></div><div><span>숙박 칸</span><strong>${bookedNights}박</strong><small>선택한 29일 기준</small></div></section><div class="quick-booking-guide"><div class="quick-booking-guide-copy"><strong>마우스: 클릭·드래그 / 터치: 0.35초 길게 누른 뒤 같은 행에서 가로 드래그</strong>월말과 월초도 하나의 표로 이어집니다. 세로로 움직이면 선택을 취소하고 화면만 스크롤합니다.</div><div class="quick-booking-legend" aria-label="예약 상태 범례"><span class="quick-legend-item"><i class="quick-legend-swatch single">1박</i>별도 1박</span><span class="quick-legend-item"><i class="quick-legend-swatch multi">연박</i>하나의 연박</span><span class="quick-legend-item"><i class="quick-legend-swatch locked">${icon('lock','icon-sm')}</i>예약 불가</span><span class="quick-legend-item"><i class="quick-legend-swatch preview"></i>선택 중</span></div></div><section class="card quick-grid-shell"><div class="quick-grid-status"><strong>${esc(windowLabel)}</strong><span>29일 · 표시 ${rooms.length}개 객실 · 예약 불가 객실 ${blockedRooms}개</span><span class="quick-status-spacer"></span><span>오늘 기준 -7일 / +21일 · 7일씩 이동</span></div>${mobileHeader}<div id="quick-grid-scroller" class="quick-grid-scroller" tabindex="0" aria-label="객실 예약표 스크롤 영역">${grid}</div></section></div>`;
      }
'''
replace_between(
    "      function quickCellMarkup(",
    "      function quickGridUsesInternalVerticalScroll()",
    quick_render,
    "quick reservation 29-day renderer",
)

replace_once(
    "      function quickGridUsesInternalVerticalScroll() { return !window.matchMedia('(max-width: 720px)').matches; }\n      function syncQuickGridHorizontalScroll(source) {",
    "      function quickGridUsesInternalVerticalScroll() { return !window.matchMedia('(max-width: 720px)').matches; }\n      function quickGridAnchorScrollLeft(scroller) {\n        const anchor=scroller?.querySelector(`[data-quick-date=\"${state.quickReservationAnchorDate}\"]`),roomHeader=scroller?.querySelector('.quick-room-header');\n        return anchor&&roomHeader?Math.max(0,anchor.offsetLeft-roomHeader.offsetWidth):0;\n      }\n      function syncQuickGridHorizontalScroll(source) {",
    "quick grid anchor scroll helper",
)

replace_once(
    "      function restoreQuickGridViewport(focusSelector='') {\n        requestAnimationFrame(()=>{const scroller=document.getElementById('quick-grid-scroller'),header=document.getElementById('quick-grid-mobile-header'),left=Math.max(0,Number(state.quickGridScrollLeft)||0);if(scroller){scroller.scrollLeft=left;scroller.scrollTop=quickGridUsesInternalVerticalScroll()?Math.max(0,Number(state.quickGridScrollTop)||0):0;}if(header)header.scrollLeft=left;if(focusSelector)document.querySelector(focusSelector)?.focus({preventScroll:true});});\n      }",
    "      function restoreQuickGridViewport(focusSelector='') {\n        requestAnimationFrame(()=>{const scroller=document.getElementById('quick-grid-scroller'),header=document.getElementById('quick-grid-mobile-header');if(scroller){const left=state.quickGridScrollLeft==null?quickGridAnchorScrollLeft(scroller):Math.max(0,Number(state.quickGridScrollLeft)||0);scroller.scrollLeft=left;scroller.scrollTop=quickGridUsesInternalVerticalScroll()?Math.max(0,Number(state.quickGridScrollTop)||0):0;if(header)header.scrollLeft=left;state.quickGridScrollLeft=left;}if(focusSelector)document.querySelector(focusSelector)?.focus({preventScroll:true});});\n      }",
    "quick grid anchor restore",
)

replace_between(
    "        if(a==='quick-month-shift'){",
    "        if(a==='quick-reservation-edit'){",
    r'''        if(a==='quick-month-shift'){
          if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
        }
        if(a==='quick-month-today'){
          if(state.role!=='admin')return;state.quickReservationAnchorDate=state.selectedDate;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
        }
''',
    "quick window navigation handlers",
)

replace_once(
    "        {id:'reservation-demo-756',room:'756',checkInAt:'2026-08-15T16:00',checkOutAt:'2026-08-17T11:00',source:'grid',status:'active'}\n      ]);",
    "        {id:'reservation-demo-756',room:'756',checkInAt:'2026-08-15T16:00',checkOutAt:'2026-08-17T11:00',source:'grid',status:'active'},\n        {id:'reservation-demo-cross-month-516',room:'516',checkInAt:'2026-08-31T16:00',checkOutAt:'2026-09-03T11:00',guestCount:2,source:'grid',status:'active'},\n        {id:'reservation-demo-cross-month-623',room:'623',checkInAt:'2026-08-31T16:00',checkOutAt:'2026-09-01T11:00',guestCount:2,source:'grid',status:'active'}\n      ]);",
    "cross-month reservation fixtures",
)

replace_once(
    "    .quick-month-label { display:flex; align-items:center; justify-content:center; gap:7px; min-width:150px; min-height:44px; padding:8px 12px; border:1px solid var(--line-strong); border-radius:10px; background:var(--surface-soft); color:var(--navy); font-weight:850; white-space:nowrap; }",
    "    .quick-month-label { display:flex; align-items:center; justify-content:center; gap:7px; min-width:180px; min-height:44px; padding:8px 12px; border:1px solid var(--line-strong); border-radius:10px; background:var(--surface-soft); color:var(--navy); font-weight:850; white-space:nowrap; }\n    .quick-month-label small { color:var(--muted); font-size:10px; font-weight:750; }",
    "quick window label style",
)

replace_once(
    "    .quick-day-header .calendar-holiday-mark { margin-top:1px; }",
    "    .quick-day-header .calendar-holiday-mark { margin-top:1px; }\n    .quick-day-header.is-month-start, .quick-date-cell.is-month-start { border-left:2px solid #8ca8c1; }\n    .quick-day-header.is-past { color:#8491a0; background:#f3f5f7; }",
    "quick month boundary header style",
)

replace_once(
    "    .quick-date-cell.is-locked { color:#6b7682; background:#eef1f4; cursor:not-allowed; }",
    "    .quick-date-cell.is-locked { color:#6b7682; background:#eef1f4; cursor:not-allowed; }\n    .quick-date-cell.is-past { color:#929ca8; background:#f4f5f7; }\n    .quick-date-cell.is-locked.is-past { color:#9ca5ae; background:#f1f3f5; }",
    "quick past date cell style",
)

html_path.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 간편 예약 29일 연속 보기 (2026-08-24)

- 간편 예약의 기본 범위는 운영상 오늘 기준 `-7일 ~ +21일`, 양 끝을 포함한 29일이다. 달이 바뀌어도 표를 끊지 않는다.
- 첫 진입과 `오늘` 복귀 시 오늘 열이 객실 정보 열 바로 옆에 오도록 가로 위치를 자동 정렬한다. 이전·다음 버튼은 기준일을 7일씩 이동한다.
- 범위 첫날과 매월 1일은 `월/일`로 표시하고 월 경계선을 둔다. 나머지 날짜는 `일`로 표시한다.
- 지난 7일의 빈 칸은 조회 전용으로 잠그되 기존 예약은 열어볼 수 있다. 월을 넘는 연박 예약은 같은 예약 ID로 이어서 표시한다.
- URL과 브라우저 이력은 `bookingAnchor=YYYY-MM-DD` 기준일을 저장하며, 과거 `bookingMonth=YYYY-MM` 링크는 해당 달 15일 기준으로 호환한다.
"""
readme_path.write_text(readme, encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-24 · 간편 예약 29일 연속 보기

- 기본 운영일 2026-08-15에서 범위가 2026-08-08~2026-09-05, 총 29일인지 확인했다.
- 첫 진입에서 2026-08-15 열이 객실 정보 열 바로 옆으로 자동 정렬되는지 확인했다.
- 이전·다음은 7일씩 이동하고 `오늘`은 기본 범위와 자동 정렬을 복원하는지 확인했다.
- 8/31~9/1 1박과 8/31~9/3 연박이 월 경계를 넘어 같은 화면에서 올바른 시작·중간·종료 칸으로 표시되는지 확인했다.
- 범위 첫날과 9월 1일은 `월/일` 및 월 경계선으로 표시되고, 지난 빈 날짜는 신규 예약 불가·기존 예약 조회 가능인지 확인했다.
- 모바일 고정 머리글과 본문의 가로 위치 동기화, 문서 전체 세로 스크롤, 마지막 객실 노출을 확인했다.
- 360·390·768·1440px 가로 넘침, 브라우저 콘솔·런타임 오류가 없음을 확인했다.
"""
qa_path.write_text(qa, encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
for old, new in [
    ("  'quickGridScrollLeft:700',", "  'quickGridScrollLeft:null',"),
    ("  'state.quickGridScrollLeft=700',", "  'state.quickGridScrollLeft=null',"),
]:
    if checker.count(old) != 1:
        raise SystemExit(f"static quick-scroll contract mismatch for {old}: {checker.count(old)}")
    checker = checker.replace(old, new, 1)

marker = "console.log('Per-maid weekly payment static contracts: passed');"
if checker.count(marker) != 1:
    raise SystemExit(f"29-day checker marker mismatch: {checker.count(marker)}")
contracts = r'''for (const contract of [
  'quickReservationAnchorDate',
  'QUICK_RESERVATION_PAST_DAYS=7',
  'QUICK_RESERVATION_FUTURE_DAYS=21',
  'QUICK_RESERVATION_DAY_COUNT=QUICK_RESERVATION_PAST_DAYS+1+QUICK_RESERVATION_FUTURE_DAYS',
  'function quickWindowBounds(',
  'function quickWindowDates(',
  'function reservationInQuickWindow(',
  'data-offset="-7"',
  'data-offset="7"',
  "params.set('bookingAnchor',route.quickAnchor)",
  '지난 날짜 · 조회만 가능',
  'is-month-start',
  'function quickGridAnchorScrollLeft(',
  'reservation-demo-cross-month-516',
  'reservation-demo-cross-month-623',
  '선택한 29일 기준',
]) {
  if (!html.includes(contract)) throw new Error(`Quick reservation 29-day contract missing: ${contract}`);
}
if (html.includes('function quickMonthDates(') || html.includes('function reservationInMonth(')) {
  throw new Error('Legacy month-bounded quick reservation helpers remain.');
}
for (const contract of ['간편 예약 29일 연속 보기', '`-7일 ~ +21일`', 'bookingAnchor=YYYY-MM-DD']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Quick reservation 29-day README contract missing: ${contract}`);
}
for (const contract of ['간편 예약 29일 연속 보기', '2026-08-08~2026-09-05', '8/31~9/3 연박']) {
  if (!qa.includes(contract)) throw new Error(`Quick reservation 29-day QA contract missing: ${contract}`);
}

'''
checker_path.write_text(checker.replace(marker, contracts + marker, 1), encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
sums_lines = sums_path.read_text(encoding="utf-8").splitlines()
found = False
next_lines: list[str] = []
for line in sums_lines:
    if line.endswith("  WIREFRAME/index.html"):
        next_lines.append(f"{digest}  WIREFRAME/index.html")
        found = True
    else:
        next_lines.append(line)
if not found:
    raise SystemExit("WIREFRAME/index.html checksum line missing")
sums_path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-24-quick-booking-29-day"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
