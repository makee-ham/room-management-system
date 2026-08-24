from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path=Path('WIREFRAME/index.html')
html=html_path.read_text(encoding='utf-8')


def replace_once(old:str,new:str,label:str)->None:
    global html
    count=html.count(old)
    if count!=1: raise SystemExit(f'{label}: expected one match, found {count}')
    html=html.replace(old,new,1)


def regex_once(pattern:str,replacement:str,label:str,flags:int=0)->None:
    global html
    html,count=re.subn(pattern,replacement,html,count=1,flags=flags)
    if count!=1: raise SystemExit(f'{label}: expected one match, found {count}')


projector=r'''      function operationalMoment(targetState=state) { return `${targetState.selectedDate||'2026-08-15'}T${targetState.time||'00:00'}`; }
      function reservationAtOperationalMoment(roomNo,targetState=state) {
        const moment=operationalMoment(targetState);
        return activeReservationsFor(targetState,String(roomNo)).find(reservation=>reservation.checkInAt<=moment&&moment<reservation.checkOutAt)||null;
      }
      function latestCheckedOutReservationForRoom(roomNo,targetState=state) {
        const moment=operationalMoment(targetState);
        return (targetState.reservations||[]).filter(reservation=>reservation.room===String(roomNo)&&reservation.status!=='cancelled'&&reservation.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null;
      }
      function checkoutCleaningCompletedForReservation(reservation,targetState=state) {
        if(!reservation)return false;
        const attempts=Object.values(targetState.cleaningAttempts||{}).filter(attempt=>attempt?.room===reservation.room&&attempt.kind==='퇴실 청소'&&(attempt.reservationIdSnapshot===reservation.id||targetState.assignments?.[attempt.workTargetId]?.committedTarget?.reservationId===reservation.id));
        if(attempts.some(attempt=>!!attempt.completedAt||['upload','submitted','approved','rejected'].includes(attempt.status)))return true;
        return Object.values(targetState.cleaningSubmissions||{}).some(submission=>submission?.room===reservation.room&&submission.reservationIdSnapshot===reservation.id);
      }
      function roomCheckoutCleaningDue(no,targetState=state) {
        if(reservationAtOperationalMoment(no,targetState))return false;
        const reservation=latestCheckedOutReservationForRoom(no,targetState);
        return !!reservation&&!checkoutCleaningCompletedForReservation(reservation,targetState);
      }
      function projectReservationState(targetState,roomNos=null) {
        const selected=roomNos?new Set([].concat(roomNos).map(String)):null,moment=operationalMoment(targetState);
        ROOMS.forEach(room=>{
          if(selected&&!selected.has(room.no))return;
          const reservations=activeReservationsFor(targetState,room.no),current=reservations.find(item=>item.checkInAt<=moment&&moment<item.checkOutAt)||null,future=reservations.find(item=>item.checkInAt>moment)||null,completed=(targetState.reservations||[]).filter(item=>item.room===room.no&&item.status!=='cancelled'&&item.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null,projected=current||future||completed||null;
          if(projected){room.reservationCheckinAt=projected.checkInAt;room.reservationCheckoutAt=projected.checkOutAt;room.nextCheckinAt=projected.checkInAt;room.nextCheckoutAt=projected.checkOutAt;room.reservationProjectionId=projected.id;room.checkin=projected.checkInAt.slice(11,16);room.checkout=projected.checkOutAt.slice(11,16);}else if(room.reservationProjectionId){delete room.reservationCheckinAt;delete room.reservationCheckoutAt;delete room.nextCheckinAt;delete room.nextCheckoutAt;delete room.reservationProjectionId;room.checkin='정보 없음';room.checkout='정보 없음';}
          const override=room.occupancyOverride;
          if(override==='occupied'&&!current){room.occupancy='occupied';room.checkin=room.actualCheckinAt?.slice(11,16)||'투숙 중';room.checkout=(room.plannedCheckoutAt||room.reservationCheckoutAt||'예정 미입력').slice?.(11,16)||'예정 미입력';return;}
          if(override==='vacant'&&!current){room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;if(completed)room.actualCheckoutAt=completed.checkOutAt;return;}
          if(current){room.occupancy='occupied';room.actualCheckinAt=current.checkInAt;room.plannedCheckoutAt=current.checkOutAt;room.currentStayReservationId=current.id;delete room.actualCheckoutAt;room.checkin=current.checkInAt.slice(11,16);room.checkout=current.checkOutAt.slice(11,16);return;}
          room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;if(completed)room.actualCheckoutAt=completed.checkOutAt;else delete room.actualCheckoutAt;
        });
      }
'''
regex_once(r"      function projectReservationState\(targetState,roomNos=null\) \{.*?\n      \}\n      function roomDataIssue",projector+"      function roomDataIssue",'exact-time reservation projection',re.S)

replace_once(
    "        if(activeManualCleaningRequest(no))return true;",
    "        if(activeManualCleaningRequest(no))return true;\n        if(room.occupancy!=='occupied'&&roomCheckoutCleaningDue(no))return true;",
    'checked-out room cleaning due',
)

replace_once(
    "          room.no,room.type,room.elevator||'',room.dataIssue||'',room.occupancy,",
    "          room.no,room.type,room.elevator||'',room.dataIssue||'',room.occupancy,room.occupancyOverride||'',",
    'occupancy override fingerprint',
)

occupancy_panel=r'''      function renderOccupancyPanel(no) {
        const room=ROOMS.find(item=>item.no===no),occupied=room?.occupancy==='occupied',current=room?reservationAtOperationalMoment(no):null,next=room?activeReservationsFor(state,no).find(reservation=>reservation.checkInAt>reservationCurrentMoment())||null:null,actual=room?.actualCheckoutAt;
        if(!room)return '';
        const stateLabel=occupied?'투숙 중':next?'입실 예정':'공실',tone=occupied?'blue':next?'neutral':'green',schedule=current||next;
        return `<section class="card card-pad" aria-labelledby="room-occupancy-${no}"><div class="section-head"><div><h3 id="room-occupancy-${no}">현재 투숙 상태</h3><p class="audit-note">예약에 저장된 체크인·체크아웃 일시를 기준으로 자동 계산합니다.</p></div>${statusBadge(stateLabel,tone)}</div><div class="info-grid"><div class="info-item"><span>현재 상태</span><strong>${esc(stateLabel)}</strong></div><div class="info-item"><span>${current?'체크인':'다음 체크인'}</span><strong>${esc(schedule?reservationMomentLabel(schedule.checkInAt):'일정 없음')}</strong></div><div class="info-item"><span>${current?'예정 체크아웃':'다음 체크아웃'}</span><strong>${esc(schedule?reservationMomentLabel(schedule.checkOutAt):'일정 없음')}</strong></div>${actual&&!occupied?`<div class="info-item"><span>최근 자동 퇴실</span><strong>${esc(reservationMomentLabel(actual))}</strong></div>`:''}</div><div class="notice notice-info" style="margin:12px 0 0"><div><strong>입실·퇴실은 예약 시각에 자동 반영됩니다.</strong><br>얼리 체크인과 레이트 체크아웃도 예약에 저장된 실제 시각을 사용합니다. 시각이 잘못되면 예약 관리에서 수정하세요.</div></div><div class="job-actions" style="margin-top:12px">${button(schedule?'예약 관리':'예약 등록','reservation-edit','outline',`data-id="${no}"`)}</div></section>`;
      }
'''
regex_once(r"      function renderOccupancyPanel\(no\) \{.*?\n      \}\n      function mergeRoomBasicsPanel",occupancy_panel+"      function mergeRoomBasicsPanel",'automatic occupancy panel',re.S)

replace_once(
    "        if(p.key==='occupied')return ['지금 체크아웃','manual-checkout','danger'];",
    "        if(p.key==='occupied')return ['예약 관리','reservation-edit','primary'];",
    'occupied primary action',
)

replace_once(
    "'edit-room-info','save-room-info','manual-checkout','confirm-manual-checkout','manual-checkin','confirm-manual-checkin','pin-show'",
    "'edit-room-info','save-room-info','pin-show'",
    'remove manual occupancy actions',
)

# 수동 입퇴실 핸들러는 액션 등록과 화면에서만 차단하고, 기존 예약 저장 흐름을 보존한다.

replace_once(
    "if(wasHeld){room.occupancy=occupancy;room.catalogStatus='available';",
    "if(wasHeld){room.occupancyOverride=occupancy;room.occupancy=occupancy;room.catalogStatus='available';",
    'held room explicit occupancy override',
)
replace_once(
    "case 6: {const room=ROOMS.find(item=>item.no==='332');if(room){room.occupancy='occupied';room.plannedCheckoutAt='2026-08-15T13:00';}",
    "case 6: {const room=ROOMS.find(item=>item.no==='332');if(room){room.occupancyOverride='occupied';room.occupancy='occupied';room.plannedCheckoutAt='2026-08-15T13:00';}",
    'conflict scenario occupancy override',
)

for old,new,label in [
    ('예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리해 주세요.','예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.','reservation add copy'),
    ('투숙 중 · 예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리해 주세요.','투숙 중 · 예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.','quick booking copy'),
    ('체크인이 시작된 예약은 취소하지 않고 객실 상세의 지금 체크아웃으로 처리해야 합니다.','체크인이 시작된 예약은 취소하지 않고 예약 관리에서 실제 체크아웃 시각을 수정해야 합니다.','reservation cancel copy'),
]:
    if old in html: html=html.replace(old,new)

replace_once(
    "          showRoom:(roomNo)=>{state.role='admin';state.adminView='rooms';state.detail={type:'room',id:String(roomNo)};render();return roomPresentation(String(roomNo));},",
    "          showRoom:(roomNo)=>{state.role='admin';state.adminView='rooms';state.detail={type:'room',id:String(roomNo)};render();return roomPresentation(String(roomNo));},\n          setOperationalMoment:(date,time)=>{state.selectedDate=String(date);state.time=String(time);projectReservationState(state);render();return {date:state.selectedDate,time:state.time};},\n          occupancyState:roomNo=>{const no=String(roomNo),room=ROOMS.find(item=>item.no===no),current=reservationAtOperationalMoment(no),last=latestCheckedOutReservationForRoom(no);return {room:no,occupancy:room?.occupancy,currentReservationId:current?.id||null,lastCheckoutReservationId:last?.id||null,actualCheckinAt:room?.actualCheckinAt||null,actualCheckoutAt:room?.actualCheckoutAt||null,plannedCheckoutAt:room?.plannedCheckoutAt||null,presentation:roomPresentation(no),checkoutCleaningDue:roomCheckoutCleaningDue(no)};},\n          setReservationTimes:(reservationId,checkInAt,checkOutAt)=>{const reservation=state.reservations.find(item=>item.id===String(reservationId));if(!reservation)throw new Error('예약을 찾을 수 없습니다.');reservation.checkInAt=String(checkInAt);reservation.checkOutAt=String(checkOutAt);reservation.updatedAt=`${state.selectedDate}T${state.time}`;projectReservationState(state,reservation.room);render();return {...reservation};},",
    'automatic occupancy test API',
)

readme_path=Path('WIREFRAME/README.md')
readme=readme_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 예약 시각 기반 자동 입실·퇴실 (2026-08-24)\n\n- 객실 점유 상태는 체크인 이상·체크아웃 미만일 때 투숙 중으로 자동 계산한다.\n- 체크아웃 정시부터 객실은 공실·퇴실 청소 필요로 전환되며 수동 투숙 시작·체크아웃 버튼을 사용하지 않는다.\n- 얼리 체크인과 레이트 체크아웃은 예약에 저장한 실제 일시가 그대로 기준이 된다.\n- 예약 일시를 수정하면 카드·상세·필터·예약 가능 판정이 다음 렌더에서 같은 기준으로 다시 계산된다.\n- 예약이 없는 특수 현장 충돌과 정보 확인 객실만 명시적 점유 예외를 사용할 수 있다.\n'''
readme_path.write_text(readme+'\n',encoding='utf-8')

qa_path=Path('WIREFRAME/QA.md')
qa=qa_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 2026-08-24 · 예약 시각 기반 자동 입실·퇴실\n\n- 체크인 1분 전과 정시, 체크아웃 1분 전과 정시의 점유 전환 확인\n- 얼리 체크인 예약의 저장 시각 기준 전환 확인\n- 예약 시각 수정 직후 객실 상태 재계산 확인\n- 수동 투숙 시작·지금 체크아웃 버튼과 액션 제거 확인\n- 체크아웃 정시 공실·퇴실 청소 필요 전환 확인\n- 반복 렌더 원장 불변, 390·768·1440px 가로 넘침과 콘솔 오류 확인\n'''
qa_path.write_text(qa+'\n',encoding='utf-8')

checker_path=Path('scripts/check-workspace.mjs')
checker=checker_path.read_text(encoding='utf-8')
marker="console.log('Workspace check: passed');"
checks=r'''for (const contract of [
  'function operationalMoment(targetState=state)',
  'function reservationAtOperationalMoment(roomNo,targetState=state)',
  'function latestCheckedOutReservationForRoom(roomNo,targetState=state)',
  'function roomCheckoutCleaningDue(no,targetState=state)',
  "reservation.checkInAt<=moment&&moment<reservation.checkOutAt",
  '입실·퇴실은 예약 시각에 자동 반영됩니다.',
]) {
  if (!html.includes(contract)) throw new Error(`Automatic occupancy contract missing: ${contract}`);
}
const occupancyActionsSource=html.slice(html.indexOf('const rebuiltActions='),html.indexOf('const deprecatedStateActions='));
for (const removed of ["'manual-checkout'","'confirm-manual-checkout'","'manual-checkin'","'confirm-manual-checkin'"]) {
  if (occupancyActionsSource.includes(removed)) throw new Error(`Manual occupancy action remains registered: ${removed}`);
}
if (/data-action="(?:manual-checkout|manual-checkin)"/.test(html)) throw new Error('Manual occupancy button remains in rendered markup.');
console.log('Automatic reservation occupancy static contracts: passed');

'''
if checker.count(marker)!=1: raise SystemExit('workspace check marker mismatch')
checker_path.write_text(checker.replace(marker,checks+marker,1),encoding='utf-8')

html_path.write_text(html,encoding='utf-8')
digest=hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path=Path('SHA256SUMS.txt')
sums=sums_path.read_text(encoding='utf-8').splitlines()
sums_path.write_text('\n'.join(f'{digest}  WIREFRAME/index.html' if line.endswith('  WIREFRAME/index.html') else line for line in sums)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version']='2026-08-24-auto-occupancy'
manifest['generated_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
