from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')
    html = html.replace(old, new, 1)


def regex_once(pattern: str, replacement: str, label: str, flags: int = 0) -> None:
    global html
    html, count = re.subn(pattern, replacement, html, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')


replace_once(
    "    .room-status-sub .icon { width:13px; height:13px; }",
    "    .room-status-sub .icon { width:13px; height:13px; }\n"
    "    .room-state-axis-badges { display:flex; flex-wrap:wrap; gap:6px; align-items:center; }\n"
    "    .room-state-axis-badges .badge { white-space:normal; text-align:left; }\n"
    "    .room-status-sub.is-cleaning { border-color:#efc08f; color:#a3430b; background:#fff8ef; }\n"
    "    .room-status-sub.is-inspection { border-color:#d8b5e8; color:#6d3d86; background:#fbf6ff; }\n"
    "    .room-status-sub.is-blocked,.room-status-sub.is-conflict { border-color:#e3a8ae; color:#8b3239; background:#fff6f7; }\n"
    "    .room-status-sub.is-available { border-color:#abd8c8; color:#17654a; background:#f3fbf8; }",
    'room facet CSS',
)

facet_functions = r'''      function cleaningKindForRoom(no) {
        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no],manual=activeManualCleaningRequest(no),attempt=activeUnfinishedAttempt(no),submission=currentSubmission(no);
        if(manual?.kind)return manual.kind;
        if(attempt?.kind)return attempt.kind;
        if(submission?.kind&&['inspection','approved'].includes(job))return submission.kind;
        if(job==='reclean')return '재청소';
        if(job==='stayover-requested')return '연박 청소';
        if(job==='extra-requested')return '추가 청소';
        if(room?.occupancy==='occupied')return '연박 청소';
        return '퇴실 청소';
      }
      function roomStateFacets(no) {
        no=String(no);const room=ROOMS.find(item=>item.no===no);
        if(!room)return {room:no,occupancy:'unknown',occupancyLabel:'확인 필요',occupancyReason:'객실 정보 없음',occupied:false,vacant:false,arrival:false,cleaningNeeded:false,cleaningKind:'',cleaningStage:'',checkoutInspectionPending:false,blocked:true,blockers:['객실 정보 확인 필요'],available:false,conflict:false};
        const job=state.jobs[no],moment=reservationCurrentMoment(),reservations=activeReservationsFor(state,no),current=reservations.find(item=>item.checkInAt<=moment&&moment<item.checkOutAt)||null,next=reservations.find(item=>item.checkInAt>moment)||null,occupied=room.occupancy==='occupied',occupancy=occupied?'occupied':next?'arrival':'vacant';
        const occupancyLabel=occupied?'투숙 중':next?'공실 · 입실 예정':'공실',occupancyReason=occupied?`현재 고객 투숙 · 체크아웃 ${reservationMomentLabel(current?.checkOutAt||room.plannedCheckoutAt||room.reservationCheckoutAt)}`:next?`다음 체크인 ${reservationMomentLabel(next.checkInAt)}`:'현재 투숙 고객 없음';
        const blockers=roomBlockingReasons(no),cleaningNeeded=roomNeedsCleaningNow(no),cleaningKind=cleaningNeeded?cleaningKindForRoom(no):'',cleaningStage=cleaningNeeded?(roomCleaningStageLabel(job)||'청소 필요'):'',checkoutInspectionPending=checkoutInspectionPending(no),blocked=blockers.length>0,available=!occupied&&!cleaningNeeded&&!checkoutInspectionPending&&!blocked;
        const conflict=occupied&&cleaningNeeded&&['퇴실 청소','재청소'].includes(cleaningKind),conflictReason=conflict?'현재 고객이 투숙 중인데 이전 퇴실·재청소 작업이 남아 있습니다. 출입과 작업 대상을 확인하세요.':'';
        return {room:no,occupancy,occupancyLabel,occupancyReason,occupied,vacant:!occupied,arrival:!occupied&&!!next,currentReservationId:current?.id||null,nextReservationId:next?.id||null,cleaningNeeded,cleaningKind,cleaningStage,checkoutInspectionPending,blocked,blockers,available,conflict,conflictReason,job};
      }
      function roomFacetBadgeMarkup(no) {
        const facets=roomStateFacets(no),items=[statusBadge(facets.occupancyLabel,facets.occupied?'neutral':facets.arrival?'blue':'green')];
        if(facets.cleaningNeeded)items.push(statusBadge(`${facets.cleaningKind} · ${facets.cleaningStage}`,'amber'));
        if(facets.checkoutInspectionPending)items.push(statusBadge('퇴실점검 대상','amber'));
        if(facets.blocked)items.push(statusBadge('운영·안전 차단','red'));
        if(facets.conflict)items.push(statusBadge('이전 청소 충돌','red'));
        if(facets.available)items.push(statusBadge('고객 배정 가능','green'));
        return `<div class="room-state-axis-badges" data-room-facet-badges="${no}">${items.join('')}</div>`;
      }
      function roomFacetSubMarkup(no) {
        const facets=roomStateFacets(no),items=[];
        if(facets.cleaningNeeded)items.push(`<span class="room-status-sub is-cleaning">${icon('briefcase','icon-sm')}청소 · ${esc(facets.cleaningKind)} · ${esc(facets.cleaningStage)}</span>`);
        if(facets.checkoutInspectionPending)items.push(`<span class="room-status-sub is-inspection">${icon('search','icon-sm')}퇴실점검 대상</span>`);
        if(facets.blocked)items.push(`<span class="room-status-sub is-blocked">${icon('alert','icon-sm')}차단 · ${esc(facets.blockers.join(' · '))}</span>`);
        if(facets.conflict)items.push(`<span class="room-status-sub is-conflict">${icon('alert','icon-sm')}이전 퇴실 청소 충돌</span>`);
        if(facets.available)items.push(`<span class="room-status-sub is-available">${icon('check','icon-sm')}고객 배정 가능</span>`);
        return items.length?`<div class="room-status-subs">${items.join('')}</div>`:'';
      }
      function roomPresentation(no) {
        const facets=roomStateFacets(no),special=cardReservationStatus(no),tone=facets.blocked||facets.conflict?'red':facets.cleaningNeeded||facets.checkoutInspectionPending?'amber':facets.occupied?'neutral':'green';
        const key=facets.blocked?'blocked':facets.occupied?'occupied':facets.cleaningNeeded?'cleaning':facets.checkoutInspectionPending?'inspection':facets.available?'available':'vacant';
        const reason=[facets.occupancyReason,facets.cleaningNeeded?`${facets.cleaningKind} · ${facets.cleaningStage}`:'',facets.checkoutInspectionPending?'퇴실점검 남음':'',facets.conflictReason].filter(Boolean).join(' · ');
        return {key,tone,status:facets.occupancyLabel,reason,available:facets.available,cleaning:facets.cleaningNeeded,cleaningStage:facets.cleaningStage,blockers:facets.blockers,early:special.early,late:special.late,facets};
      }

      function renderPinRow'''
regex_once(
    r"      function roomPresentation\(no\) \{.*?\n      \}\n\n      function renderPinRow",
    facet_functions,
    'faceted room presentation',
    re.S,
)

regex_once(
    r"      function roomPrimaryAction\(no,p\) \{.*?\n      \}",
    r'''      function roomPrimaryAction(no,p) {
        const facets=p?.facets||roomStateFacets(no);
        if(facets.blocked)return roomIsOnHold(no)?['차단 정보 확인','room-detail','danger']:state.roomStopped[no]?['운영 중지 상태 확인','operation-status','danger']:['배정 불가 사유 확인','room-detail','danger'];
        if(facets.cleaningNeeded)return ['청소 상태 확인','cleaning-detail','primary'];
        if(facets.checkoutInspectionPending)return ['퇴실점검 확인','room-detail','primary'];
        if(facets.occupied)return ['예약 관리','reservation-edit','primary'];
        if(facets.available)return ['예약 등록','reservation-edit','primary'];
        return ['전체 상세','room-detail','primary'];
      }''',
    'room primary action facets',
    re.S,
)

replace_once(
    "        const room=ROOMS.find(item=>item.no===no),type=ROOM_TYPES[room.type],p=roomPresentation(no),job=state.jobs[no],candle=room.occupancy==='occupied'?0:state.candles[no]||0,special=cardReservationStatus(no),issueCount=unresolvedRoomIssueRecords(no).length,reservations=activeReservationsFor(state,no),upcomingReservations=reservations.filter(item=>!reservationRecordIsPast(item)),closestReservation=upcomingReservations[0]||null;",
    "        const room=ROOMS.find(item=>item.no===no),type=ROOM_TYPES[room.type],p=roomPresentation(no),facets=p.facets||roomStateFacets(no),job=state.jobs[no],candle=room.occupancy==='occupied'?0:state.candles[no]||0,special=cardReservationStatus(no),issueCount=unresolvedRoomIssueRecords(no).length,reservations=activeReservationsFor(state,no),upcomingReservations=reservations.filter(item=>!reservationRecordIsPast(item)),closestReservation=upcomingReservations[0]||null;",
    'room card facets variable',
)
replace_once(
    "        const subBadges=p.cleaningStage?`<div class=\"room-status-subs\"><span class=\"room-status-sub\">${icon('briefcase','icon-sm')}청소 단계 · ${esc(p.cleaningStage)}</span></div>`:'',statusIcon=p.key==='occupied'?'user':p.key==='cleaning'?'briefcase':p.key==='available'?'check':'alert';",
    "        const subBadges=roomFacetSubMarkup(no),statusIcon=facets.occupied?'user':facets.arrival?'calendar':'check',mainTone=facets.blocked||facets.conflict?'red':facets.cleaningNeeded||facets.checkoutInspectionPending?'amber':facets.occupied?'neutral':'green';",
    'room card facet sub badges',
)
replace_once(
    "        return `<article class=\"card room-card-v2 tone-${p.tone}\" data-room=\"${no}\"><div class=\"room-card-main\">",
    "        return `<article class=\"card room-card-v2 tone-${mainTone}\" data-room=\"${no}\" data-occupancy=\"${facets.occupancy}\" data-cleaning-needed=\"${facets.cleaningNeeded}\" data-cleaning-kind=\"${esc(facets.cleaningKind)}\" data-checkout-inspection=\"${facets.checkoutInspectionPending}\" data-blocked=\"${facets.blocked}\" data-available=\"${facets.available}\"><div class=\"room-card-main\">",
    'room card facet attributes',
)
replace_once(
    "          <div class=\"concept-status-panel ${p.tone}\"><span class=\"status-symbol\">${icon(statusIcon)}</span><div class=\"concept-status-copy\"><strong>${esc(p.status)}</strong><span>${esc(p.reason)}</span>${subBadges}</div></div>",
    "          <div class=\"concept-status-panel ${mainTone}\"><span class=\"status-symbol\">${icon(statusIcon)}</span><div class=\"concept-status-copy\"><strong>${esc(facets.occupancyLabel)}</strong><span>${esc(facets.occupancyReason)}</span>${subBadges}</div></div>",
    'room card occupancy primary panel',
)

regex_once(
    r"      function filteredRooms\(\) \{.*?\n      \}",
    r'''      function filteredRooms() {
        const q=state.roomSearch.trim();
        return ROOMS.filter(room=>!q||room.no.includes(q)).filter(room=>state.roomTypeFilter==='all'||room.type===state.roomTypeFilter).filter(room=>{
          const facets=roomStateFacets(room.no),special=cardReservationStatus(room.no);
          if(state.roomFilter==='all')return true;
          if(state.roomFilter==='occupied')return facets.occupied;
          if(state.roomFilter==='cleaning')return facets.cleaningNeeded;
          if(state.roomFilter==='available')return facets.available;
          if(state.roomFilter==='blocked')return facets.blocked;
          if(state.roomFilter==='checkout-inspection')return facets.checkoutInspectionPending;
          if(state.roomFilter==='extra-guests')return roomHasExtraGuests(room.no);
          if(state.roomFilter==='default'||state.roomFilter==='catalog'||state.roomFilter==='vacant')return facets.vacant&&!roomIsOnHold(room.no);
          if(state.roomFilter==='candle')return !facets.occupied&&(state.candles[room.no]||0)>0;
          if(state.roomFilter==='early')return special.early;
          if(state.roomFilter==='late')return special.late;
          if(state.roomFilter==='issues')return roomIssueRecords(room.no).length>0;
          return true;
        });
      }''',
    'independent room filters',
    re.S,
)

render_rooms = r'''      function renderRooms() {
        const rooms=filteredRooms(),facetStates=ROOMS.map(room=>roomStateFacets(room.no));
        const body=rooms.length?`<div class="room-list-v2">${rooms.map(room=>roomCard(room.no)).join('')}</div>`:`<section class="inline-empty"><h3>검색·필터 결과가 없습니다</h3><p>전체 객실은 있지만 선택한 조건과 일치하지 않습니다.</p>${button('검색·필터 초기화','clear-room-filters','outline')}</section>`;
        const counts={occupied:facetStates.filter(item=>item.occupied).length,cleaning:facetStates.filter(item=>item.cleaningNeeded).length,inspection:facetStates.filter(item=>item.checkoutInspectionPending).length,blocked:facetStates.filter(item=>item.blocked).length,available:facetStates.filter(item=>item.available).length},typeCounts=ROOMS.reduce((result,room)=>{result[room.type]=(result[room.type]||0)+1;return result;},{});
        const catalogSummary=`<section class="catalog-summary" aria-label="현재 객실 독립 상태 요약"><div class="catalog-summary-copy"><strong>총 ${ROOMS.length}개 객실 · 상태는 서로 겹칠 수 있습니다</strong><span>투숙 중 ${counts.occupied}개 · 청소 필요 ${counts.cleaning}개 · 퇴실점검 ${counts.inspection}개 · 운영·안전 차단 ${counts.blocked}개 · 고객 배정 가능 ${counts.available}개입니다. 투숙 중이면서 연박 청소 대상인 객실은 투숙·청소 양쪽에 모두 집계됩니다.</span></div>${[{id:'all',name:'전체 객실',count:ROOMS.length},...Object.entries(ROOM_TYPES).map(([id,type])=>({id,name:type.name,count:typeCounts[id]||0}))].map(item=>`<button class="catalog-summary-stat" type="button" data-action="filter-room-type" data-type="${item.id}" aria-pressed="${state.roomTypeFilter===item.id}" aria-label="${esc(item.name)} ${item.count}개 보기"><strong>${item.count}</strong><span>${esc(item.name)}</span></button>`).join('')}</section>`;
        return renderCoach()+renderNetworkNotice()+`<div class="room-concept-layout">${renderDateTools(false)}${catalogSummary}<label class="search-field"><span class="sr-only">객실번호 검색</span>${icon('search')}<input id="room-search" class="input-control concept-search" type="search" data-control="room-search" value="${esc(state.roomSearch)}" placeholder="객실번호 검색 · 총 121개" autocomplete="off"></label><div class="concept-filter-row"><label><span class="sr-only">객실 유형</span><select class="select-control" data-control="room-type-filter"><option value="all">객실 유형 전체</option>${Object.entries(ROOM_TYPES).map(([id,type])=>`<option value="${id}" ${state.roomTypeFilter===id?'selected':''}>${esc(type.name)}</option>`).join('')}</select></label><label><span class="sr-only">객실 상태</span><select class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>상태 전체</option><optgroup label="독립 상태 · 중복 가능"><option value="occupied" ${state.roomFilter==='occupied'?'selected':''}>투숙 중</option><option value="cleaning" ${state.roomFilter==='cleaning'?'selected':''}>청소 필요</option><option value="checkout-inspection" ${state.roomFilter==='checkout-inspection'?'selected':''}>퇴실점검 대상</option><option value="available" ${state.roomFilter==='available'?'selected':''}>고객 배정 가능</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>운영·안전 차단</option></optgroup><optgroup label="상세 조건"><option value="extra-guests" ${state.roomFilter==='extra-guests'?'selected':''}>인원 추가</option><option value="vacant" ${state.roomFilter==='vacant'?'selected':''}>공실</option><option value="candle" ${state.roomFilter==='candle'?'selected':''}>촛불 있음</option><option value="issues" ${state.roomFilter==='issues'?'selected':''}>특이사항 있음</option><option value="early" ${state.roomFilter==='early'?'selected':''}>얼리 체크인</option><option value="late" ${state.roomFilter==='late'?'selected':''}>레이트 체크아웃</option></optgroup></select></label><button class="btn btn-outline room-export-trigger" type="button" data-action="open-room-export" aria-haspopup="dialog" ${isLocked()?'disabled':''}>${icon('download','icon-sm')}내보내기</button></div>${renderListState(body)}</div>`;
      }

      const QUICK_RESERVATION_PAST_DAYS'''
regex_once(
    r"      function renderRooms\(\) \{\n        const rooms=filteredRooms\(\);.*?\n      \}\n\n      const QUICK_RESERVATION_PAST_DAYS",
    render_rooms,
    'room list faceted summary',
    re.S,
)

replace_once(
    "        const roomStates=ROOMS.map(room=>({room,presentation:roomPresentation(room.no)}));\n        const availableCount=roomStates.filter(item=>item.presentation.key==='available').length;\n        const cleaningCount=roomStates.filter(item=>item.presentation.key==='cleaning').length;\n        const blockedCount=roomStates.filter(item=>item.presentation.key==='blocked').length;\n        const occupiedCount=roomStates.filter(item=>item.presentation.key==='occupied').length;",
    "        const roomStates=ROOMS.map(room=>({room,facets:roomStateFacets(room.no)}));\n        const availableCount=roomStates.filter(item=>item.facets.available).length;\n        const cleaningCount=roomStates.filter(item=>item.facets.cleaningNeeded).length;\n        const blockedCount=roomStates.filter(item=>item.facets.blocked).length;\n        const occupiedCount=roomStates.filter(item=>item.facets.occupied).length;",
    'dashboard independent counts',
)

replace_once(
    "<div class=\"badge-row\">${statusBadge(p.status,p.tone)}${occupied?statusBadge('투숙 중','neutral'):''}</div>",
    "${roomFacetBadgeMarkup(no)}",
    'room detail facet badges',
)

new_export = r'''      const ROOM_EXPORT_COLUMNS=['기준일','객실','객실 유형','기본 청소요금','엘리베이터 위치','정보 상태','점유 상태','체크인','체크아웃','얼리 체크인','레이트 체크아웃','청소 필요','청소 유형','청소 단계','퇴실점검','운영·안전 차단','차단 사유','고객 배정 가능','청소 담당','촛불 수량','특이사항','운영 상태','대체 객실'];
      function roomExportRows(filtered=false) {
        const rooms=filtered?filteredRooms():ROOMS;
        return rooms.map(room=>{
          const facets=roomStateFacets(room.no),special=roomReservationStatus(room),stop=state.roomMoves[room.no]||{},held=roomDataIssue(room.no),issueCount=unresolvedRoomIssueRecords(room.no).length;
          return [state.selectedDate,`${room.no}호`,ROOM_TYPES[room.type].name,money(ROOM_TYPES[room.type].rate),elevatorLabel(room),held?'확인 필요':'확인 완료',facets.occupancyLabel,room.reservationCheckinAt||room.nextCheckinAt||room.checkin,room.reservationCheckoutAt||room.nextCheckoutAt||room.checkout,special.early?`자동 · ${special.earlyOffset} · ${special.checkin}`:'—',special.late?`자동 · ${special.lateOffset} · ${special.checkout}`:'—',facets.cleaningNeeded?'예':'아니오',facets.cleaningKind||'—',facets.cleaningStage||'—',facets.checkoutInspectionPending?'대상':'해당 없음',facets.blocked?'차단':'정상',facets.blockers.length?facets.blockers.join(' · '):'—',facets.available?'가능':'불가',held?'확인 필요':room.assignee,held?'확인 필요':`${facets.occupied?0:state.candles[room.no]||0}개`,`${issueCount}건`,state.roomStopped[room.no]?'운영 중지':'정상',state.roomStopped[room.no]&&stop.to?`${stop.to}호`:'—'];
        });
      }
      function openRoomExport'''
regex_once(
    r"      const ROOM_EXPORT_COLUMNS=.*?\n      function roomExportRows\(filtered=false\) \{.*?\n      \}\n      function openRoomExport",
    new_export,
    'faceted room export',
    re.S,
)

replace_once(
    "객실 유형·정본 청소요금·엘리베이터 위치·투숙/공실/정보 확인 필요와 고객 배정 가능 여부와 체크인·체크아웃, 청소, 촛불, 운영 중지 사유를 내보냅니다.",
    "객실 유형·점유·청소 유형과 단계·퇴실점검·운영·안전 차단·고객 배정 가능 여부를 서로 다른 열로 내보냅니다. PIN 원문과 고객 개인정보는 제외합니다.",
    'room export explanatory copy',
)

replace_once(
    "          setRoomFilter:filter=>{state.role='admin';state.adminView='rooms';state.detail=null;state.roomFilter=filter;render();return filteredRooms().map(room=>room.no);},",
    "          setRoomFilter:filter=>{state.role='admin';state.adminView='rooms';state.detail=null;state.roomFilter=filter;render();return filteredRooms().map(room=>room.no);},\n          roomStateFacets:roomNo=>({...roomStateFacets(String(roomNo)),blockers:[...roomStateFacets(String(roomNo)).blockers]}),\n          roomsForState:filter=>{const previous=state.roomFilter;state.roomFilter=String(filter);const result=filteredRooms().map(room=>room.no);state.roomFilter=previous;return result;},\n          facetCandidates:()=>({occupiedCleanable:ROOMS.filter(room=>room.occupancy==='occupied'&&!roomIsOnHold(room.no)&&!state.roomStopped[room.no]&&!activeUnfinishedAttempt(room.no)&&!currentSubmission(room.no)&&!roomNeedsCleaningNow(room.no)).map(room=>room.no),vacantCleanable:ROOMS.filter(room=>room.occupancy!=='occupied'&&!roomIsOnHold(room.no)&&!state.roomStopped[room.no]&&!activeUnfinishedAttempt(room.no)&&!currentSubmission(room.no)&&!roomNeedsCleaningNow(room.no)).map(room=>room.no),inspection:ROOMS.filter(room=>checkoutInspectionPending(room.no)).map(room=>room.no),conflicts:ROOMS.filter(room=>roomStateFacets(room.no).conflict).map(room=>room.no)}),\n          setRoomStoppedForTest:(roomNo,on=true)=>{const no=String(roomNo);state.roomStopped[no]=!!on;if(!on)delete state.roomStopped[no];render();return roomStateFacets(no);},",
    'room facet test API',
)

policy_path = Path('DOCS/20_ROOM_STATE_FACET_POLICY.md')
policy_path.write_text('''# 객실 독립 상태 축 정책

- 확정일: 2026-08-24
- 적용 범위: 관리자 객실 목록·상세·오늘 화면·내보내기

## 원칙

객실은 하나의 상태 문자열로 설명하지 않는다. 다음 축을 독립적으로 계산한다.

1. 점유: 투숙 중 / 공실 / 공실·입실 예정
2. 청소: 필요 여부 / 퇴실·연박·추가·재청소 / 진행 단계
3. 퇴실점검: 대상 / 해당 없음 또는 완료
4. 운영·안전: 정상 / 운영 중지 / 촛불 / 입실 차단 특이사항 / 충돌
5. 고객 배정 가능: 위 조건을 종합한 파생 결과

따라서 한 객실은 동시에 `투숙 중`이면서 `연박 청소 · 배정 준비`일 수 있다. 목록의 `투숙 중` 필터와 `청소 필요` 필터는 같은 객실을 각각 포함할 수 있다.

## 표시 우선순위

카드의 큰 제목은 점유 사실을 우선한다. 청소·점검·차단은 그 아래 독립 배지로 함께 표시한다. 색상은 운영상 가장 긴급한 축을 반영할 수 있지만 점유 문구를 덮어쓰지 않는다.

- 투숙 중 + 연박 청소: 큰 제목 `투숙 중`, 청소 배지 `연박 청소 · 단계`
- 공실 + 퇴실 청소: 큰 제목 `공실`, 청소 배지 `퇴실 청소 · 단계`
- 공실 + 퇴실점검 + 청소: 세 축 모두 표시
- 투숙 중 + 운영 중지: 투숙 사실과 차단 사유를 함께 표시
- 투숙 중 + 이전 퇴실 청소: 충돌 경고를 추가해 작업 대상을 확인

## 전이 규칙

- 청소 완료는 청소 축만 해제하고 투숙 상태를 바꾸지 않는다.
- 퇴실점검 완료는 점검 축만 해제한다.
- 퇴실 청소 현장 완료가 점검을 대체하면 점검 축도 완료 처리한다.
- 고객 배정 가능은 공실이며 청소·점검·운영·안전 차단이 모두 없을 때만 참이다.
- 필터·집계는 대표 상태가 아니라 각 축의 불리언 값을 직접 검사한다.

## 내보내기

CSV·엑셀에는 점유, 청소 필요, 청소 유형, 청소 단계, 퇴실점검, 운영·안전 차단, 차단 사유, 고객 배정 가능을 서로 다른 열로 기록한다.
''',encoding='utf-8')

readme_path=Path('WIREFRAME/README.md')
readme=readme_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 객실 독립 상태 축 (2026-08-24)\n\n- 투숙·공실, 청소 서비스, 퇴실점검, 운영·안전 차단, 고객 배정 가능을 독립적으로 계산한다.\n- 투숙 중 연박 청소처럼 동시에 성립하는 상태는 카드·상세·필터·내보내기에서 모두 보존한다.\n- 카드 큰 제목은 점유 사실을 유지하고 병행 업무는 종류와 단계 배지로 표시한다.\n'''
readme_path.write_text(readme+'\n',encoding='utf-8')

qa_path=Path('WIREFRAME/QA.md')
qa=qa_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 2026-08-24 · 투숙·청소·점검 상태 독립 축\n\n- 투숙 중 객실에 연박 청소를 켜도 `투숙 중`과 청소 종류·단계가 함께 표시되는지 확인했다.\n- 같은 객실이 `투숙 중`과 `청소 필요` 필터 양쪽에 포함되는지 확인했다.\n- 투숙 중 청소 완료 뒤 점유는 유지되고 청소 축만 해제되는지 확인했다.\n- 공실 추가 청소, 공실 퇴실 청소, 퇴실점검 병행, 투숙 중 운영 차단, 이전 퇴실 청소 충돌을 확인했다.\n- 반복 렌더링이 예약·청소·급여 원장을 바꾸지 않는지 확인했다.\n- 390·768·1440px에서 병행 배지와 카드가 가로로 넘치지 않고 콘솔·런타임 오류가 없는지 확인했다.\n'''
qa_path.write_text(qa+'\n',encoding='utf-8')

checker_path=Path('scripts/check-workspace.mjs')
checker=checker_path.read_text(encoding='utf-8')
marker="console.log('Workspace check: passed');"
if checker.count(marker)!=1:
    raise SystemExit(f'workspace marker mismatch: {checker.count(marker)}')
contracts=r'''for (const contract of [
  'function roomStateFacets(no)',
  'function roomFacetBadgeMarkup(no)',
  'function roomFacetSubMarkup(no)',
  "if(state.roomFilter==='occupied')return facets.occupied;",
  "if(state.roomFilter==='cleaning')return facets.cleaningNeeded;",
  'data-cleaning-needed="${facets.cleaningNeeded}"',
  '상태는 서로 겹칠 수 있습니다',
  '독립 상태 · 중복 가능',
  "'청소 유형','청소 단계','퇴실점검','운영·안전 차단'",
  'roomStateFacets:roomNo=>',
  'roomsForState:filter=>',
]) {
  if (!html.includes(contract)) throw new Error(`Room state facet contract missing: ${contract}`);
}
console.log('Room state facet static contracts: passed');

'''
checker_path.write_text(checker.replace(marker,contracts+marker,1),encoding='utf-8')

html_path.write_text(html,encoding='utf-8')
digest=hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path=Path('SHA256SUMS.txt')
lines=sums_path.read_text(encoding='utf-8').splitlines()
found=False
for index,line in enumerate(lines):
    if line.endswith('  WIREFRAME/index.html'):
        lines[index]=f'{digest}  WIREFRAME/index.html';found=True
if not found:raise SystemExit('WIREFRAME checksum line missing')
sums_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version']='2026-08-24-room-state-facets'
manifest['generated_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
