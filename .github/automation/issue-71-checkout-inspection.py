from __future__ import annotations

import hashlib
import json
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


replace_once(
    "          manualCleaningSequence:0, manualCleaningRequests:{},\n          publications:{}, cancelRequests:{},",
    "          manualCleaningSequence:0, manualCleaningRequests:{}, checkoutInspections:{},\n          publications:{}, cancelRequests:{},",
    'checkout inspection state',
)
replace_once(
    "          manualCleaningRequests:sortedEntries(targetState.manualCleaningRequests,item=>({id:item.id,room:item.room,kind:item.kind,status:item.status,targetId:item.targetId,date:item.date,previousJob:item.previousJob||null,createdAt:item.createdAt,completedAt:item.completedAt||null,cancelledAt:item.cancelledAt||null})),",
    "          manualCleaningRequests:sortedEntries(targetState.manualCleaningRequests,item=>({id:item.id,room:item.room,kind:item.kind,status:item.status,targetId:item.targetId,date:item.date,previousJob:item.previousJob||null,createdAt:item.createdAt,completedAt:item.completedAt||null,cancelledAt:item.cancelledAt||null})),\n          checkoutInspections:sortedEntries(targetState.checkoutInspections,item=>({id:item.id,reservationId:item.reservationId,room:item.room,checkoutAt:item.checkoutAt,completedAt:item.completedAt,method:item.method,attemptId:item.attemptId||null})),",
    'checkout inspection durable ledger',
)
replace_once(
    "        const manualRequests=Object.entries(targetState.manualCleaningRequests||{});ensureUnique('수동 청소 요청 ID',manualRequests.map(([,item])=>item.id));ensureUnique('활성 객실 청소 요청',manualRequests.filter(([,item])=>item.status==='active').map(([,item])=>item.room));ensureUnique('수동 청소 대상 ID',(targetState.manualAssignmentTargets||[]).map(item=>item.id));",
    "        const manualRequests=Object.entries(targetState.manualCleaningRequests||{});ensureUnique('수동 청소 요청 ID',manualRequests.map(([,item])=>item.id));ensureUnique('활성 객실 청소 요청',manualRequests.filter(([,item])=>item.status==='active').map(([,item])=>item.room));ensureUnique('수동 청소 대상 ID',(targetState.manualAssignmentTargets||[]).map(item=>item.id));\n        const checkoutInspections=Object.entries(targetState.checkoutInspections||{});ensureUnique('퇴실점검 기록 ID',checkoutInspections.map(([,item])=>item.id));ensureUnique('예약별 퇴실점검 기록',checkoutInspections.map(([,item])=>item.reservationId));checkoutInspections.forEach(([key,item])=>{if(key!==item.reservationId)throw new Error(`퇴실점검 키 불일치: ${key} / ${item.reservationId}`);});",
    'checkout inspection duplicate contracts',
)

helpers=r'''      function checkoutInspectionRecordFor(reservationId,targetState=state) { return reservationId?targetState.checkoutInspections?.[reservationId]||null:null; }
      function checkoutInspectionReservationForRoom(no,targetState=state) {
        if(reservationAtOperationalMoment(no,targetState))return null;
        return latestCheckedOutReservationForRoom(no,targetState);
      }
      function checkoutInspectionPendingForReservation(reservation,targetState=state) {
        return !!reservation&&!checkoutInspectionRecordFor(reservation.id,targetState)&&!checkoutCleaningCompletedForReservation(reservation,targetState);
      }
      function checkoutInspectionPending(no,targetState=state) { return checkoutInspectionPendingForReservation(checkoutInspectionReservationForRoom(String(no),targetState),targetState); }
      function checkoutInspectionCompletion(no,targetState=state) {
        const reservation=checkoutInspectionReservationForRoom(String(no),targetState);if(!reservation)return null;
        const record=checkoutInspectionRecordFor(reservation.id,targetState);if(record)return record;
        if(checkoutCleaningCompletedForReservation(reservation,targetState))return {id:null,reservationId:reservation.id,room:reservation.room,checkoutAt:reservation.checkOutAt,completedAt:null,method:'cleaning-derived',attemptId:null};
        return null;
      }
      function completeCheckoutInspection(no,{method='manual',attempt=null}={}) {
        no=String(no);const reservation=attempt?.reservationIdSnapshot?(state.reservations||[]).find(item=>item.id===attempt.reservationIdSnapshot&&item.room===no)||null:checkoutInspectionReservationForRoom(no);
        if(!reservation||reservation.checkOutAt>operationalMoment(state))return {error:'체크아웃이 완료된 예약을 찾을 수 없습니다.'};
        const existing=checkoutInspectionRecordFor(reservation.id);if(existing)return {record:existing,created:false,duplicate:true};
        if(method==='cleaning'&&attempt&&(attempt.kind!=='퇴실 청소'||attempt.reservationIdSnapshot!==reservation.id))return {error:'해당 체크아웃 예약의 퇴실 청소가 아닙니다.'};
        if(method==='manual'&&!checkoutInspectionPendingForReservation(reservation))return {error:'이미 청소 완료로 점검이 대체되었거나 점검 대상이 아닙니다.'};
        const completedAt=attempt?.completedAt||`${state.selectedDate} ${state.time}`,record={id:`checkout-inspection-${reservation.id}`,reservationId:reservation.id,room:no,checkoutAt:reservation.checkOutAt,completedAt,method:method==='cleaning'?'cleaning':'manual',attemptId:attempt?.id||null,completedBy:method==='cleaning'?(attempt?.performerName||'메이드'):'관리자'};
        if(!state.checkoutInspections)state.checkoutInspections={};state.checkoutInspections[reservation.id]=record;appendEvent(`${no}호 퇴실점검 완료`,`${reservationMomentLabel(reservation.checkOutAt)} 퇴실 · ${record.method==='cleaning'?'퇴실 청소 현장 완료로 점검 대체':`관리자 점검 완료`} · 예약 ${reservation.id}`,{maidIds:attempt?.performerId?[attempt.performerId]:[],roomId:no,attemptId:attempt?.id||null,dedupeKey:`checkout-inspection:${reservation.id}`});assertNoDuplicateDurableRecords(state);return {record,created:true,duplicate:false};
      }
      function completeCheckoutInspectionForAttempt(no,attempt) {
        if(!attempt||attempt.kind!=='퇴실 청소'||!attempt.completedAt||!attempt.reservationIdSnapshot)return null;
        return completeCheckoutInspection(no,{method:'cleaning',attempt});
      }
      function renderCheckoutInspectionPanel(no) {
        const reservation=checkoutInspectionReservationForRoom(no);if(!reservation)return '';
        const pending=checkoutInspectionPendingForReservation(reservation),completion=checkoutInspectionCompletion(no),method=completion?.method;
        return `<section class="card card-pad" aria-labelledby="checkout-inspection-${no}" data-checkout-inspection-room="${no}" data-checkout-inspection-pending="${pending}"><div class="section-head"><div><h3 id="checkout-inspection-${no}">퇴실점검</h3><p class="audit-note">고객 퇴실 뒤 객실 상태를 청소 전에 확인하는 운영 단계입니다.</p></div>${statusBadge(pending?'점검 대상':'점검 완료',pending?'amber':'green')}</div><div class="info-grid"><div class="info-item"><span>대상 예약</span><strong>${esc(reservation.id)}</strong></div><div class="info-item"><span>체크아웃</span><strong>${esc(reservationMomentLabel(reservation.checkOutAt))}</strong></div><div class="info-item"><span>완료 방식</span><strong>${pending?'미완료':method==='manual'?'관리자 점검 완료':'퇴실 청소 완료로 대체'}</strong></div></div>${pending?`<div class="notice notice-warning" style="margin:12px 0 0"><div style="min-width:0;flex:1"><strong>청소 전 퇴실점검이 남아 있습니다.</strong><br>직접 점검 완료를 기록하거나 해당 예약의 퇴실 청소를 현장 완료하면 자동으로 해제됩니다.</div>${button('퇴실점검 완료','complete-checkout-inspection','primary',`data-id="${no}" ${isLocked()?'disabled':''}`)}</div>`:`<div class="notice notice-success" style="margin:12px 0 0"><div><strong>퇴실점검 상태가 해제되었습니다.</strong><br>${esc(method==='manual'?'관리자가 점검 완료를 기록했습니다.':'퇴실 청소 현장 완료가 점검을 대체했습니다.')}</div></div>`}</section>`;
      }
      function renderCheckoutInspectionQueueSummary() {
        const rooms=ROOMS.filter(room=>checkoutInspectionPending(room.no));if(!rooms.length)return '';
        return `<section class="notice notice-warning" aria-label="퇴실점검 대상 요약"><div style="min-width:0;flex:1"><strong>퇴실점검 대상 ${rooms.length}개 객실</strong><br>고객 퇴실 후 청소 전 확인이 남은 객실입니다. 청소가 현장 완료되면 자동으로 목록에서 빠집니다.</div><button class="btn btn-outline" type="button" data-action="filter-rooms" data-filter="checkout-inspection">대상 객실 보기</button></section>`;
      }

'''
replace_once("      function projectReservationState(targetState,roomNos=null) {",helpers+"      function projectReservationState(targetState,roomNos=null) {",'checkout inspection helpers')

replace_once(
    "          if (state.adminView==='today') return renderAdminToday();",
    "          if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();",
    'today checkout inspection summary',
)
replace_once(
    "${renderOccupancyPanel(no)}",
    "${renderOccupancyPanel(no)}${renderCheckoutInspectionPanel(no)}",
    'checkout inspection room panel',
)

replace_once(
    "if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);",
    "if(state.roomFilter==='checkout-inspection')return checkoutInspectionPending(r.no);if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);",
    'checkout inspection room filter',
)
replace_once(
    "<optgroup label=\"상세 조건\"><option value=\"extra-guests\"",
    "<optgroup label=\"상세 조건\"><option value=\"checkout-inspection\" ${state.roomFilter==='checkout-inspection'?'selected':''}>퇴실점검 대상</option><option value=\"extra-guests\"",
    'checkout inspection filter option',
)
replace_once(
    "<option value=\"candle\" ${state.roomFilter==='candle'?'selected':''}>촛불 있음</option></select>",
    "<option value=\"candle\" ${state.roomFilter==='candle'?'selected':''}>촛불 있음</option><option value=\"checkout-inspection\" ${state.roomFilter==='checkout-inspection'?'selected':''}>퇴실점검 대상</option></select>",
    'legacy date tools checkout filter',
)
replace_once(
    "if(state.role!=='admin'||!['occupied','cleaning','available','blocked'].includes(filter))return;",
    "if(state.role!=='admin'||!['occupied','cleaning','available','blocked','checkout-inspection'].includes(filter))return;",
    'checkout inspection dashboard filter action',
)
replace_once(
    "if(['all','vacant','available','blocked','cleaning','occupied','extra-guests','candle','issues','early','late'].includes(requestedRoomFilter))state.roomFilter=requestedRoomFilter;",
    "if(['all','vacant','available','blocked','cleaning','occupied','checkout-inspection','extra-guests','candle','issues','early','late'].includes(requestedRoomFilter))state.roomFilter=requestedRoomFilter;",
    'checkout inspection URL filter',
)

replace_once(
    "const detailBadges=[roomIsOnHold(no)?'<span class=\"room-detail-badge\">정보 확인 필요</span>':'',",
    "const detailBadges=[checkoutInspectionPending(no)?'<span class=\"room-detail-badge\">퇴실점검 대상</span>':'',roomIsOnHold(no)?'<span class=\"room-detail-badge\">정보 확인 필요</span>':'',",
    'checkout inspection card badge',
)

replace_once(
    "'confirm-room-cleaning-off','operation-status'",
    "'confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status'",
    'checkout inspection actions',
)
replace_once(
    "mutationActions=new Set(['toggle-room-cleaning'",
    "mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning'",
    'checkout inspection mutation locks',
)

handlers=r'''        if(a==='complete-checkout-inspection'){
          const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!reservation||!checkoutInspectionPendingForReservation(reservation)){toast('현재 퇴실점검 대상이 아니거나 이미 완료되었습니다.','error');return;}showModal({title:`${no}호 퇴실점검을 완료할까요?`,subtitle:`${reservationMomentLabel(reservation.checkOutAt)} 체크아웃 · 예약 ${reservation.id}`,trigger:el,body:'<div class="notice notice-warning"><div><strong>청소 완료 처리와는 별도입니다.</strong><br>퇴실점검 대상 상태만 해제하고 객실의 청소 필요·배정 상태는 그대로 유지합니다.</div></div>',confirmLabel:'퇴실점검 완료 기록',confirmAction:'confirm-checkout-inspection',confirmVariant:'primary'});const confirm=document.querySelector('[data-action="confirm-checkout-inspection"]');if(confirm){confirm.dataset.id=no;confirm.dataset.reservation=reservation.id;}return;
        }
        if(a==='confirm-checkout-inspection'){
          const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!adminCanMutate()||!reservation||reservation.id!==el.dataset.reservation||!checkoutInspectionPendingForReservation(reservation)){closeModal();render();toast('퇴실점검 대상 또는 관리자 최신 상태가 바뀌어 완료하지 않았습니다.','error');return;}const result=completeCheckoutInspection(no,{method:'manual'});if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-checkout-inspection-room="${no}"]`);toast(`${no}호 퇴실점검을 완료했습니다. 청소 필요 상태는 유지됩니다.`);return;
        }
'''
replace_once("        if(a==='toggle-room-cleaning'){",handlers+"        if(a==='toggle-room-cleaning'){",'checkout inspection handlers')

replace_once(
    "if(attempt)Object.assign(attempt,{status:'upload',completedAt});completeManualCleaningRequestForAttempt(id,attempt);",
    "if(attempt)Object.assign(attempt,{status:'upload',completedAt});completeManualCleaningRequestForAttempt(id,attempt);completeCheckoutInspectionForAttempt(id,attempt);",
    'cleaning completion clears checkout inspection',
)

replace_once(
    "          occupancyState:roomNo=>{const no=String(roomNo),room=ROOMS.find(item=>item.no===no),current=reservationAtOperationalMoment(no),last=latestCheckedOutReservationForRoom(no);return {room:no,occupancy:room?.occupancy,currentReservationId:current?.id||null,lastCheckoutReservationId:last?.id||null,actualCheckinAt:room?.actualCheckinAt||null,actualCheckoutAt:room?.actualCheckoutAt||null,plannedCheckoutAt:room?.plannedCheckoutAt||null,presentation:roomPresentation(no),checkoutCleaningDue:roomCheckoutCleaningDue(no)};},",
    "          occupancyState:roomNo=>{const no=String(roomNo),room=ROOMS.find(item=>item.no===no),current=reservationAtOperationalMoment(no),last=latestCheckedOutReservationForRoom(no);return {room:no,occupancy:room?.occupancy,currentReservationId:current?.id||null,lastCheckoutReservationId:last?.id||null,actualCheckinAt:room?.actualCheckinAt||null,actualCheckoutAt:room?.actualCheckoutAt||null,plannedCheckoutAt:room?.plannedCheckoutAt||null,presentation:roomPresentation(no),checkoutCleaningDue:roomCheckoutCleaningDue(no),checkoutInspectionPending:checkoutInspectionPending(no)};},\n          checkoutInspectionState:roomNo=>{const no=String(roomNo),reservation=checkoutInspectionReservationForRoom(no),record=reservation?checkoutInspectionRecordFor(reservation.id):null;return {room:no,reservation:reservation?{...reservation}:null,pending:checkoutInspectionPending(no),record:record?{...record}:null,completion:checkoutInspectionCompletion(no),presentation:roomPresentation(no),filtered:filteredRooms().some(room=>room.no===no)};},\n          completeCheckoutInspection:(roomNo,method='manual')=>completeCheckoutInspection(String(roomNo),{method}),\n          completeCheckoutInspectionByCleaning:roomNo=>{const no=String(roomNo),reservation=checkoutInspectionReservationForRoom(no),attempt=Object.values(state.cleaningAttempts||{}).find(item=>item.room===no&&item.kind==='퇴실 청소'&&item.reservationIdSnapshot===reservation?.id)||null;if(!reservation||!attempt)throw new Error('퇴실 청소 회차를 찾을 수 없습니다.');attempt.completedAt=attempt.completedAt||`${state.selectedDate} ${state.time}`;attempt.status='upload';state.jobs[no]='upload';return completeCheckoutInspectionForAttempt(no,attempt);},",
    'checkout inspection test API',
)

readme_path=Path('WIREFRAME/README.md')
readme=readme_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 체크아웃 후 퇴실점검 상태 (2026-08-24)\n\n- 예약 체크아웃 시각이 지나고 해당 퇴실 청소가 현장 완료되기 전인 객실을 퇴실점검 대상으로 계산한다.\n- 객실 상태 필터의 `퇴실점검 대상`에서 한 번에 모아보고 카드·상세에서 같은 배지를 확인한다.\n- 관리자는 객실 상세에서 퇴실점검 완료를 명시적으로 기록할 수 있으며 청소 필요 상태는 그대로 남는다.\n- 관리자가 먼저 처리하지 않아도 해당 예약의 퇴실 청소가 현장 완료되면 청소 완료로 점검이 대체되어 상태가 자동 해제된다.\n- 완료 기록은 예약 ID당 한 건이며 완료 방식·시각·수행 회차를 감사 이력으로 보존한다.\n'''
readme_path.write_text(readme+'\n',encoding='utf-8')

qa_path=Path('WIREFRAME/QA.md')
qa=qa_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 2026-08-24 · 체크아웃 후 퇴실점검 상태\n\n- 체크아웃 1분 전에는 미대상, 정시에 퇴실점검 대상 자동 진입\n- 객실 카드 배지, 상세 패널, 상태 필터와 오늘 요약 목록 일치\n- 관리자 퇴실점검 완료 후 필터 해제와 청소 필요 상태 유지\n- 점검 미완료 상태에서 퇴실 청소 현장 완료 시 자동 해제 및 `cleaning` 완료 방식 기록\n- 수동·청소 완료 반복 실행에도 예약별 기록·이벤트 한 건 유지\n- 연박·추가 청소는 체크아웃 예약 원천이 아니므로 퇴실점검을 만들지 않음\n- 반복 렌더 원장 불변, 390·768·1440px 가로 넘침과 콘솔 오류 확인\n'''
qa_path.write_text(qa+'\n',encoding='utf-8')

checker_path=Path('scripts/check-workspace.mjs')
checker=checker_path.read_text(encoding='utf-8')
marker="console.log('Workspace check: passed');"
checks=r'''for (const contract of [
  'checkoutInspections:{}',
  'function checkoutInspectionPending(no,targetState=state)',
  'function completeCheckoutInspection(no,{method=\'manual\',attempt=null}={})',
  'function completeCheckoutInspectionForAttempt(no,attempt)',
  'function renderCheckoutInspectionPanel(no)',
  'data-filter="checkout-inspection"',
  'value="checkout-inspection"',
  'data-action="complete-checkout-inspection"',
  "if(a==='confirm-checkout-inspection')",
]) {
  if (!html.includes(contract)) throw new Error(`Checkout inspection contract missing: ${contract}`);
}
if (!html.includes('completeCheckoutInspectionForAttempt(id,attempt)')) throw new Error('Field completion does not clear checkout inspection.');
console.log('Checkout inspection static contracts: passed');

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
manifest['version']='2026-08-24-checkout-inspection'
manifest['generated_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
