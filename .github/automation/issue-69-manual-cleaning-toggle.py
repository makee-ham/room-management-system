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
    "          reservationSequence:INITIAL_RESERVATIONS.length, reservations:initialReservationState(),\n          publications:{}, cancelRequests:{},",
    "          reservationSequence:INITIAL_RESERVATIONS.length, reservations:initialReservationState(),\n          manualCleaningSequence:0, manualCleaningRequests:{},\n          publications:{}, cancelRequests:{},",
    'manual cleaning state',
)

replace_once(
    "          reservationSequence:Number(targetState.reservationSequence)||0,\n          reservations:sortedValues(targetState.reservations,item=>({id:item.id,room:item.room,checkInAt:item.checkInAt,checkOutAt:item.checkOutAt,guestCount:reservationGuestCount(item),source:item.source,status:item.status})),",
    "          reservationSequence:Number(targetState.reservationSequence)||0,\n          manualCleaningSequence:Number(targetState.manualCleaningSequence)||0,\n          manualCleaningRequests:sortedEntries(targetState.manualCleaningRequests,item=>({id:item.id,room:item.room,kind:item.kind,status:item.status,targetId:item.targetId,date:item.date,previousJob:item.previousJob||null,createdAt:item.createdAt,completedAt:item.completedAt||null,cancelledAt:item.cancelledAt||null})),\n          manualAssignmentTargets:sortedValues(targetState.manualAssignmentTargets,item=>({id:item.id,room:item.room,kind:item.kind,date:item.date,effectiveDate:item.effectiveDate||item.date,source:item.source,cancelled:!!item.cancelled,completed:!!item.completed})),\n          reservations:sortedValues(targetState.reservations,item=>({id:item.id,room:item.room,checkInAt:item.checkInAt,checkOutAt:item.checkOutAt,guestCount:reservationGuestCount(item),source:item.source,status:item.status})),",
    'manual cleaning durable ledger',
)

replace_once(
    "        const reservations=targetState.reservations||[],activeReservations=reservations.filter(item=>item.status==='active');ensureUnique('예약 ID',reservations.map(item=>item.id));ensureUnique('활성 예약 일정',activeReservations.map(item=>`${item.room}|${item.checkInAt}|${item.checkOutAt}`));",
    "        const reservations=targetState.reservations||[],activeReservations=reservations.filter(item=>item.status==='active');ensureUnique('예약 ID',reservations.map(item=>item.id));ensureUnique('활성 예약 일정',activeReservations.map(item=>`${item.room}|${item.checkInAt}|${item.checkOutAt}`));\n        const manualRequests=Object.entries(targetState.manualCleaningRequests||{});ensureUnique('수동 청소 요청 ID',manualRequests.map(([,item])=>item.id));ensureUnique('활성 객실 청소 요청',manualRequests.filter(([,item])=>item.status==='active').map(([,item])=>item.room));ensureUnique('수동 청소 대상 ID',(targetState.manualAssignmentTargets||[]).map(item=>item.id));",
    'manual cleaning duplicate contracts',
)

manual_helpers = r'''      function activeManualCleaningRequest(no,targetState=state) {
        return Object.values(targetState.manualCleaningRequests||{}).find(request=>request.room===String(no)&&request.status==='active')||null;
      }
      function manualCleaningRequestTarget(request,targetState=state) {
        if(!request)return null;
        return (targetState.manualAssignmentTargets||[]).find(target=>target.id===request.targetId)||targetState.cleaningTargets?.[request.targetId]||targetState.assignments?.[request.targetId]?.committedTarget||null;
      }
      function manualCleaningRequestFingerprint(no) {
        const room=ROOMS.find(item=>item.no===String(no)),request=activeManualCleaningRequest(no),target=manualCleaningRequestTarget(request),assignment=request?state.assignments?.[request.targetId]:null,attempt=target?attemptForCleaningTarget(target):activeUnfinishedAttempt(String(no));
        return [no,room?.occupancy||'',state.jobs[String(no)]||'',request?.id||'',request?.status||'',target?.id||'',assignment?.status||'',assignment?.maidId||'',assignment?.previousMaidId||'',attempt?.id||'',attempt?.status||'',attempt?.startedAt||'',attempt?.completedAt||'',state.network,state.listMode].join('|');
      }
      function manualCleaningRequestBlockReason(no) {
        const room=ROOMS.find(item=>item.no===String(no));if(!room)return '객실 정보를 찾을 수 없습니다.';
        if(!adminCanMutate())return '관리자 최신 온라인 상태에서만 청소 필요를 변경할 수 있습니다.';
        if(roomIsOnHold(no))return `${no}호는 객실 정보 확인이 먼저 필요합니다.`;
        if(state.roomStopped[no])return `${no}호는 운영 중지 상태라 청소 요청을 새로 만들 수 없습니다.`;
        if(activeManualCleaningRequest(no))return '';
        if(activeUnfinishedAttempt(no)||currentSubmission(no))return '이미 수행 중이거나 검수 중인 청소 작업이 있습니다.';
        if(roomNeedsCleaningNow(no))return '이미 자동 또는 기존 청소 대상에 포함된 객실입니다.';
        return '';
      }
      function manualCleaningCancelBlockReason(no) {
        const request=activeManualCleaningRequest(no);if(!request)return '현재 켜진 수동 청소 요청이 없습니다.';
        if(!adminCanMutate())return '관리자 최신 온라인 상태에서만 청소 필요를 해제할 수 있습니다.';
        const target=manualCleaningRequestTarget(request),assignment=state.assignments?.[request.targetId],attempt=target?attemptForCleaningTarget(target):activeUnfinishedAttempt(no),publication=state.publications?.[request.targetId];
        if(attempt||currentSubmission(no))return '이미 청소 수행 회차가 만들어져 청소 상세에서 취소·조정해야 합니다.';
        if(assignment?.maidId||assignment?.previousMaidId||['draft','notified'].includes(assignment?.status))return '담당 메이드가 지정되었거나 통보된 요청은 청소 배정 화면에서 취소해야 합니다.';
        if(publication&&(typeof publication!=='object'||publication.status!=='cancelled'))return '메이드에게 공개된 요청은 청소 배정 화면에서 취소해야 합니다.';
        return '';
      }
      function createManualCleaningRequest(no) {
        no=String(no);const duplicate=activeManualCleaningRequest(no);if(duplicate)return {request:duplicate,created:false,duplicate:true};
        const block=manualCleaningRequestBlockReason(no);if(block)return {error:block};
        const room=ROOMS.find(item=>item.no===no),kind=room.occupancy==='occupied'?'연박 청소':'추가 청소',id=`manual-cleaning-${no}-${state.selectedDate.replaceAll('-','')}-${++state.manualCleaningSequence}`,date=state.selectedDate,previousJob=state.jobs[no]||null,templateSnapshot=templateSnapshotFor(no,kind),target={id,room:no,type:room.type,kind,date,planDate:date,effectiveDate:date,checkout:state.time,checkin:'23:59',deadline:'23:30',accessStart:state.time,requestDue:'23:30',accessEnd:'23:59',source:'manual-room-cleaning',sourceLabel:'객실 상세 · 청소 필요 ON',templateSnapshot};
        const request={id,room:no,kind,status:'active',targetId:id,date,previousJob,createdAt:`${state.selectedDate} ${state.time}`};
        state.manualCleaningRequests[id]=request;state.manualAssignmentTargets.push(target);state.drafts.push({id,room:no,kind,created:state.time,date,planDate:date,visibility:'private',source:'manual-room-cleaning',templateSnapshot});state.cleaningTargets[id]=cleaningTargetSnapshot(target,date);state.assignments[id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null};state.jobs[no]='draft';
        appendEvent(`${no}호 청소 필요 ON`,`${kind} · ${dateLabel(date)} · 관리자 배정 대기 · 요청 ${id}`,{roomId:no,dedupeKey:`manual-cleaning:on:${id}`});assertNoDuplicateDurableRecords(state);return {request,target,created:true,duplicate:false};
      }
      function cancelManualCleaningRequest(no) {
        no=String(no);const request=activeManualCleaningRequest(no),block=manualCleaningCancelBlockReason(no);if(!request)return {error:block};if(block)return {error:block};
        const cancelledAt=`${state.selectedDate} ${state.time}`,target=(state.manualAssignmentTargets||[]).find(item=>item.id===request.targetId),ledger=state.cleaningTargets?.[request.targetId],assignment=state.assignments?.[request.targetId];request.status='cancelled';request.cancelledAt=cancelledAt;if(target){target.cancelled=true;target.cancelledAt=cancelledAt;target.cancelledBy='관리자';}if(ledger)Object.assign(ledger,{closed:true,closedAt:cancelledAt,closedBy:'관리자',closeStatus:'cancelled',closeReasonCode:'notNeeded',closeReason:'객실 상세에서 청소 필요 OFF'});if(assignment)Object.assign(assignment,{maidId:'',order:null,status:'cancelled',previousMaidId:null,previousOrder:null,cancelledAt,cancelledBy:'관리자',cancelReasonCode:'notNeeded',cancelReason:'객실 상세에서 청소 필요 OFF',committedTarget:assignment.committedTarget||target||ledger||null});state.drafts=state.drafts.filter(draft=>draft.id!==request.targetId);state.jobs[no]=request.previousJob||'approved';
        appendEvent(`${no}호 청소 필요 OFF`,`${request.kind} 배정 전 요청 취소 · 요청 ${request.id}`,{roomId:no,dedupeKey:`manual-cleaning:off:${request.id}`});assertNoDuplicateDurableRecords(state);return {request,cancelled:true};
      }
      function completeManualCleaningRequestForAttempt(no,attempt) {
        no=String(no);const request=activeManualCleaningRequest(no);if(!request||!attempt||attempt.workTargetId!==request.targetId)return null;
        const completedAt=attempt.completedAt||`${state.selectedDate} ${state.time}`,target=(state.manualAssignmentTargets||[]).find(item=>item.id===request.targetId),ledger=state.cleaningTargets?.[request.targetId];request.status='completed';request.completedAt=completedAt;request.attemptId=attempt.id;if(target){target.completed=true;target.completedAt=completedAt;}if(ledger)Object.assign(ledger,{closed:true,closedAt:completedAt,closedBy:attempt.performerName||'메이드',closeStatus:'completed',closeReason:'현장 청소 완료'});state.drafts=state.drafts.filter(draft=>draft.id!==request.targetId);appendEvent(`${no}호 수동 청소 요청 완료`,`${request.kind} · ${attempt.id} · 현장 완료로 청소 필요 OFF`,{maidIds:attempt.performerId?[attempt.performerId]:[],roomId:no,attemptId:attempt.id,dedupeKey:`manual-cleaning:complete:${request.id}`});return request;
      }
      function renderManualCleaningToggle(no) {
        const request=activeManualCleaningRequest(no),turnOffBlock=request?manualCleaningCancelBlockReason(no):'',turnOnBlock=request?'':manualCleaningRequestBlockReason(no),disabled=!!(request?turnOffBlock:turnOnBlock),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');
        return `<div class="notice ${request?'notice-warning':'notice-info'}" style="margin:14px 0 0"><div style="min-width:0;flex:1"><strong>청소 필요 ${request?'ON':'OFF'} · ${esc(kind)}</strong><br>${esc(request?turnOffBlock||'객실 상태와 관리자 청소 배정 대상에 반영되어 있습니다.':turnOnBlock||'켜면 청소 필요 표시와 미배정 청소 작업이 함께 생성됩니다.')}</div><button class="btn ${request?'btn-danger':'btn-primary'}" type="button" role="switch" aria-checked="${!!request}" data-action="toggle-room-cleaning" data-id="${no}" ${disabled?'disabled':''}>${request?'OFF로 변경':'ON으로 변경'}</button></div>`;
      }

'''
replace_once(
    "      function roomCleaningStageLabel(job) {",
    manual_helpers + "      function roomCleaningStageLabel(job) {",
    'manual cleaning helpers',
)

replace_once(
    "return ({public:'청소 미배정',unassigned:'청소 미배정',claimed:'담당 확정',scheduled:'시작 예정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 대기',reclean:'재청소',hold:'관리자 조치',draft:'배정 준비',future:'예정','stayover-requested':'연박 청소 요청'})[job]||'';",
    "return ({public:'청소 미배정',unassigned:'청소 미배정',claimed:'담당 확정',scheduled:'시작 예정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 대기',reclean:'재청소',hold:'관리자 조치',draft:'배정 준비',future:'예정','stayover-requested':'연박 청소 요청','extra-requested':'추가 청소 요청'})[job]||'';",
    'extra cleaning stage label',
)

replace_once(
    "      function roomNeedsCleaningNow(no) {\n        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no];if(!room)return false;",
    "      function roomNeedsCleaningNow(no) {\n        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no];if(!room)return false;\n        if(activeManualCleaningRequest(no))return true;",
    'manual request drives room cleaning status',
)

replace_once(
    "        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no],special=cardReservationStatus(no),blockers=roomBlockingReasons(no),cleaning=roomNeedsCleaningNow(no),cleaningStage=roomCleaningStageLabel(job);",
    "        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no],manualRequest=activeManualCleaningRequest(no),special=cardReservationStatus(no),blockers=roomBlockingReasons(no),cleaning=roomNeedsCleaningNow(no),cleaningStage=roomCleaningStageLabel(job);",
    'manual request in room presentation',
)
replace_once(
    "        if(cleaning)return {key:'cleaning',tone:'amber',status:'청소 필요',reason:room.occupancy==='occupied'?'연박 청소 필요':job==='reclean'?'재청소 필요':'퇴실 청소 필요',available:false,cleaning:true,cleaningStage,blockers:[],early:special.early,late:special.late};",
    "        if(cleaning)return {key:'cleaning',tone:'amber',status:'청소 필요',reason:manualRequest?`${manualRequest.kind} 필요`:room.occupancy==='occupied'?'연박 청소 필요':job==='reclean'?'재청소 필요':'퇴실 청소 필요',available:false,cleaning:true,cleaningStage,blockers:[],early:special.early,late:special.late};",
    'manual cleaning reason',
)

replace_once(
    "'stayover-requested':'연박 청소 요청'})[job]||'현재 청소 작업 없음'; }",
    "'stayover-requested':'연박 청소 요청','extra-requested':'추가 청소 요청'})[job]||'현재 청소 작업 없음'; }",
    'extra cleaning label',
)

replace_once(
    "${['public','draft','future','scheduled'].includes(state.jobs[no])?`<div style=\"margin-top:12px\">${button('청소 담당 직접 배정','direct-assign','primary',`data-id=\"${no}\"`)}</div>`:''}</section>",
    "${['public','draft','future','scheduled'].includes(state.jobs[no])?`<div style=\"margin-top:12px\">${button('청소 담당 직접 배정','direct-assign','primary',`data-id=\"${no}\"`)}</div>`:''}${renderManualCleaningToggle(no)}</section>",
    'manual cleaning toggle in room detail',
)

replace_once(
    "${occupied?button('투숙 중 청소 요청','create-stayover','outline',`data-id=\"${no}\" ${isLocked()?'disabled':''}`):''}",
    "",
    'remove duplicate stayover button',
)

replace_once(
    "'create-stayover','confirm-stayover','operation-status'",
    "'create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','operation-status'",
    'manual cleaning actions',
)
replace_once(
    "const mutationActionLocks=new Set(),mutationActions=new Set(['save-reservation-v2'",
    "const mutationActionLocks=new Set(),mutationActions=new Set(['toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2'",
    'manual cleaning mutation locks',
)

handlers = r'''        if(a==='toggle-room-cleaning'){
          const no=String(id||''),request=activeManualCleaningRequest(no),block=request?manualCleaningCancelBlockReason(no):manualCleaningRequestBlockReason(no);if(block){toast(block,'error');return;}
          const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:`${no}호 청소 필요를 ${request?'OFF':'ON'}로 바꿀까요?`,subtitle:`${kind} · 객실 상세 상태 변경`,trigger:el,body:request?'<div class="notice notice-warning"><div><strong>아직 미배정·미공개·미착수인 요청만 해제됩니다.</strong><br>객실의 청소 필요 표시와 관리자 배정 대상에서 함께 제거되며 기록은 보존됩니다.</div></div>':'<div class="notice notice-info"><div><strong>청소 필요 표시와 미배정 청소 작업을 함께 만듭니다.</strong><br>투숙 중이면 연박 청소, 공실이면 추가 청소로 등록되어 관리자 배정 화면에서 담당을 정할 수 있습니다.</div></div>',confirmLabel:request?'청소 필요 OFF':'청소 필요 ON',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action="${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;
        }
        if(a==='confirm-room-cleaning-on'){
          const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 만들지 않았습니다.','error');return;}const result=createManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind}를 청소 필요 ON으로 등록했습니다.`);return;
        }
        if(a==='confirm-room-cleaning-off'){
          const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 해제하지 않았습니다.','error');return;}const result=cancelManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind}를 청소 필요 OFF로 변경했습니다.`);return;
        }
'''
replace_once(
    "        if(a==='create-stayover'){",
    handlers + "        if(a==='create-stayover'){",
    'manual cleaning handlers',
)

replace_once(
    "          state.candles[id]=room?.occupancy==='occupied'?0:task.candle||0;state.jobs[id]='upload';setActiveCleaningFor(attempt?.performerId||signedInMaidId(),null);if(attempt)Object.assign(attempt,{status:'upload',completedAt});",
    "          state.candles[id]=room?.occupancy==='occupied'?0:task.candle||0;state.jobs[id]='upload';setActiveCleaningFor(attempt?.performerId||signedInMaidId(),null);if(attempt)Object.assign(attempt,{status:'upload',completedAt});completeManualCleaningRequestForAttempt(id,attempt);",
    'manual cleaning completes on field completion',
)

replace_once(
    "          counts:()=>({reservations:(state.reservations||[]).length,",
    "          manualCleaningCandidates:()=>ROOMS.filter(room=>!roomIsOnHold(room.no)&&!state.roomStopped[room.no]&&!activeUnfinishedAttempt(room.no)&&!currentSubmission(room.no)&&!roomNeedsCleaningNow(room.no)).map(room=>({room:room.no,occupancy:room.occupancy,type:room.type})),\n          manualCleaningState:roomNo=>{const no=String(roomNo),request=activeManualCleaningRequest(no),target=manualCleaningRequestTarget(request),assignment=request?state.assignments?.[request.targetId]:null;return {room:no,request:request?{...request}:null,target:target?{...target}:null,assignment:assignment?{...assignment}:null,presentation:roomPresentation(no),filtered:filteredRooms().some(room=>room.no===no),manualTargetCount:(state.manualAssignmentTargets||[]).filter(item=>item.id===request?.targetId&&!item.cancelled).length};},\n          setManualCleaning:(roomNo,on=true)=>on?createManualCleaningRequest(String(roomNo)):cancelManualCleaningRequest(String(roomNo)),\n          completeManualCleaning:(roomNo)=>{const no=String(roomNo),request=activeManualCleaningRequest(no);if(!request)return null;const target=manualCleaningRequestTarget(request),attempt=beginCleaningAttempt(no,{performerId:'m1',performerName:'김민지1',reason:'수동 청소 테스트',kind:request.kind,workDate:request.date,effectiveDate:request.date,workTargetId:request.targetId,templateSnapshot:target?.templateSnapshot||templateSnapshotFor(no,request.kind)});attempt.completedAt=`${state.selectedDate} ${state.time}`;attempt.status='upload';state.jobs[no]='upload';return completeManualCleaningRequestForAttempt(no,attempt);},\n          showRoom:(roomNo)=>{state.role='admin';state.adminView='rooms';state.detail={type:'room',id:String(roomNo)};render();return roomPresentation(String(roomNo));},\n          setRoomFilter:filter=>{state.role='admin';state.adminView='rooms';state.detail=null;state.roomFilter=filter;render();return filteredRooms().map(room=>room.no);},\n          counts:()=>({reservations:(state.reservations||[]).length,",
    'manual cleaning test API',
)

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8').rstrip() + '''

## 객실 상세 청소 필요 ON/OFF (2026-08-24)

- 관리자는 객실 상세의 청소 작업 영역에서 청소 필요를 직접 켜고 끌 수 있다.
- 투숙 중 객실은 연박 청소, 공실은 추가 청소로 한 건의 비공개 배정 대상을 만든다.
- ON 상태는 객실 카드·청소 필요 필터·관리자 청소 배정에 함께 반영된다.
- OFF는 미배정·미공개·미착수 수동 요청만 허용하고, 배정·착수 뒤에는 기존 청소 조정 흐름을 사용한다.
- 수동 요청 청소가 현장 완료되면 요청도 완료되어 청소 필요 ON 상태가 자연스럽게 해제된다.
'''
readme_path.write_text(readme + '\n', encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8').rstrip() + '''

## 2026-08-24 · 객실 상세 청소 필요 ON/OFF

- 공실과 투숙 중 후보에서 각각 추가 청소·연박 청소 요청 생성
- 반복 ON 시 활성 요청·초안·배정 대상 한 건 유지
- ON 후 객실 카드 청소 필요 표시, 상태 필터 포함, 관리자 배정 대상 확인
- 미배정 상태 OFF 후 카드·필터·배정 대상 동시 해제
- 담당 또는 수행 회차 생성 뒤 단순 OFF 차단
- 현장 완료 시 수동 요청 완료와 청소 필요 상태 자동 해제
- 반복 렌더링 내구 원장 불변, 390·768·1440px 가로 넘침과 콘솔 오류 확인
'''
qa_path.write_text(qa + '\n', encoding='utf-8')

checker_path = Path('scripts/check-workspace.mjs')
checker = checker_path.read_text(encoding='utf-8')
marker = "console.log('Workspace check: passed');"
checks = r'''for (const contract of [
  'manualCleaningSequence:0, manualCleaningRequests:{}',
  'function activeManualCleaningRequest(no,targetState=state)',
  'function createManualCleaningRequest(no)',
  'function cancelManualCleaningRequest(no)',
  'function completeManualCleaningRequestForAttempt(no,attempt)',
  'data-action="toggle-room-cleaning"',
  "if(a==='confirm-room-cleaning-on')",
  "if(a==='confirm-room-cleaning-off')",
  'if(activeManualCleaningRequest(no))return true;',
]) {
  if (!html.includes(contract)) throw new Error(`Manual cleaning toggle contract missing: ${contract}`);
}
const manualCleaningActionSet = html.slice(html.indexOf('const rebuiltActions='), html.indexOf('const deprecatedStateActions='));
if (!manualCleaningActionSet.includes("'toggle-room-cleaning'") || !manualCleaningActionSet.includes("'confirm-room-cleaning-on'") || !manualCleaningActionSet.includes("'confirm-room-cleaning-off'")) {
  throw new Error('Manual cleaning toggle actions are not registered.');
}
console.log('Manual room-cleaning toggle static contracts: passed');

'''
if checker.count(marker) != 1:
    raise SystemExit('workspace check marker mismatch')
checker_path.write_text(checker.replace(marker, checks + marker, 1), encoding='utf-8')

html_path.write_text(html, encoding='utf-8')
digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path('SHA256SUMS.txt')
sums_lines = sums_path.read_text(encoding='utf-8').splitlines()
sums_path.write_text('\n'.join(f'{digest}  WIREFRAME/index.html' if line.endswith('  WIREFRAME/index.html') else line for line in sums_lines) + '\n', encoding='utf-8')
manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version'] = '2026-08-24-manual-cleaning-toggle'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
