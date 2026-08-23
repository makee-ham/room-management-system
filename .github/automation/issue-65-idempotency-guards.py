from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    html = html.replace(old, new, 1)


def replace_between(start: str, end: str, replacement: str, label: str) -> None:
    global html
    start_index = html.find(start)
    if start_index < 0:
        raise SystemExit(f'{label}: start marker missing')
    end_index = html.find(end, start_index + len(start))
    if end_index < 0:
        raise SystemExit(f'{label}: end marker missing')
    html = html[:start_index] + replacement + html[end_index:]


old_append = '''      function appendEvent(title, detail, {maidIds=[],roomId=null,attemptId=null}={}) {
        const audience=[...new Set(maidIds.filter(id=>MAIDS.some(maid=>maid.id===id)))];
        state.events.unshift({title,time:state.time,detail,maidIds:audience,roomId:roomId||null,attemptId:attemptId||null});
      }'''
new_append = '''      function appendEvent(title, detail, {maidIds=[],roomId=null,attemptId=null,dedupeKey=null}={}) {
        const audience=[...new Set(maidIds.filter(id=>MAIDS.some(maid=>maid.id===id)))];
        if(dedupeKey){const existing=(state.events||[]).find(event=>event.dedupeKey===dedupeKey);if(existing)return existing;}
        const event={title,time:state.time,detail,maidIds:audience,roomId:roomId||null,attemptId:attemptId||null,...(dedupeKey?{dedupeKey}:{})};state.events.unshift(event);return event;
      }
      function durableLedgerSnapshot(targetState=state) {
        const sortedEntries=(record,project)=>Object.entries(record||{}).sort(([left],[right])=>left.localeCompare(right)).map(([key,value])=>[key,project(value,key)]),sortedValues=(values,project)=>[...(values||[])].map(project).sort((left,right)=>String(left.id||left[0]||'').localeCompare(String(right.id||right[0]||'')));
        return {
          reservationSequence:Number(targetState.reservationSequence)||0,
          reservations:sortedValues(targetState.reservations,item=>({id:item.id,room:item.room,checkInAt:item.checkInAt,checkOutAt:item.checkOutAt,guestCount:reservationGuestCount(item),source:item.source,status:item.status})),
          drafts:sortedValues(targetState.drafts,item=>({id:item.id,room:item.room,kind:item.kind,reservationId:item.reservationId||null,date:item.date||null,visibility:item.visibility||null})),
          cleaningSubmissions:sortedEntries(targetState.cleaningSubmissions,item=>({id:item.id,attemptId:item.attemptId,room:item.room,status:item.status,earningId:item.earningId||null,reportId:item.reportId||null,weekStart:item.weekStart,baseRateSnapshot:item.baseRateSnapshot})),
          earningRecords:sortedEntries(targetState.earningRecords,item=>({id:item.id,submissionId:item.submissionId,room:item.room,performerId:item.performerId,weekStart:item.weekStart,base:item.base,bombBonus:item.bombBonus,total:item.total,reportId:item.reportId||null})),
          paymentRecords:sortedEntries(targetState.paymentRecords,item=>({status:item.status,amountSnapshot:item.amountSnapshot??null,taskIds:[...(item.taskIds||[])].sort(),taskFingerprint:item.taskFingerprint||'',startedAt:item.startedAt||null,paidAt:item.paidAt||null,resolutionReason:item.resolutionReason||null})),
          events:(targetState.events||[]).map(item=>({title:item.title,time:item.time,detail:item.detail,maidIds:[...(item.maidIds||[])].sort(),roomId:item.roomId||null,attemptId:item.attemptId||null,dedupeKey:item.dedupeKey||null})),
        };
      }
      function durableLedgerFingerprint(targetState=state) { return JSON.stringify(durableLedgerSnapshot(targetState)); }
      function assertNoDuplicateDurableRecords(targetState=state) {
        const ensureUnique=(label,values)=>{const seen=new Set(),duplicates=[];values.filter(value=>value!==null&&value!==undefined&&value!=='').forEach(value=>{const key=String(value);if(seen.has(key))duplicates.push(key);else seen.add(key);});if(duplicates.length)throw new Error(`${label} 중복: ${[...new Set(duplicates)].join(', ')}`);};
        const reservations=targetState.reservations||[],activeReservations=reservations.filter(item=>item.status==='active');ensureUnique('예약 ID',reservations.map(item=>item.id));ensureUnique('활성 예약 일정',activeReservations.map(item=>`${item.room}|${item.checkInAt}|${item.checkOutAt}`));
        const submissions=Object.entries(targetState.cleaningSubmissions||{});ensureUnique('청소 제출 ID',submissions.map(([,item])=>item.id));ensureUnique('청소 회차 제출',submissions.map(([,item])=>item.attemptId));submissions.forEach(([key,item])=>{if(key!==item.id)throw new Error(`청소 제출 키 불일치: ${key} / ${item.id}`);});
        const earnings=Object.entries(targetState.earningRecords||{});ensureUnique('급여 적립 ID',earnings.map(([,item])=>item.id));ensureUnique('급여 적립 제출',earnings.map(([,item])=>item.submissionId));earnings.forEach(([key,item])=>{if(key!==item.submissionId)throw new Error(`급여 적립 키 불일치: ${key} / ${item.submissionId}`);});
        Object.entries(targetState.paymentRecords||{}).forEach(([key,item])=>{ensureUnique(`지급 기록 ${key} 수익 ID`,item.taskIds||[]);});
        ensureUnique('멱등 이벤트 키',(targetState.events||[]).map(item=>item.dedupeKey));return true;
      }
      let durableRenderBaselineReady=false;
'''
replace_once(old_append, new_append, 'durable ledger and event dedupe helpers')

replace_once(
    "      function render() {\n        projectReservationState(state);",
    "      function render() {\n        const durableBefore=durableLedgerFingerprint(state);\n        projectReservationState(state);",
    'render ledger baseline start',
)
replace_once(
    "        if(state.loggedIn&&state.role==='admin'&&state.adminView==='quickReservation'&&!state.detail)restoreQuickGridViewport();\n      }",
    "        if(state.loggedIn&&state.role==='admin'&&state.adminView==='quickReservation'&&!state.detail)restoreQuickGridViewport();\n        const durableAfter=durableLedgerFingerprint(state);if(durableRenderBaselineReady&&durableAfter!==durableBefore)throw new Error('렌더링 중 예약·청소 제출·급여·지급 원장이 변경되었습니다.');durableRenderBaselineReady=true;assertNoDuplicateDurableRecords(state);\n      }",
    'render ledger baseline end',
)

replace_once(
    "      function upsertReservationRecord({id='',roomNo,checkInAt,checkOutAt,guestCount,source='card',currentStay=false}) {",
    "      function reservationPayloadMatches(item,{roomNo,checkInAt,checkOutAt,guestCount}) { return item?.status==='active'&&item.room===String(roomNo)&&item.checkInAt===checkInAt&&item.checkOutAt===checkOutAt&&reservationGuestCount(item)===Number(guestCount); }\n      function upsertReservationRecord({id='',roomNo,checkInAt,checkOutAt,guestCount,source='card',currentStay=false}) {",
    'reservation payload matcher',
)
replace_once(
    "        if(linkedCurrentStay&&checkInAt>now)return {error:'현재 투숙 중인 예약의 체크인을 미래 시각으로 옮길 수 없습니다. 실제 입실 시각을 확인해 주세요.'};\n        const scheduleChanged=!!before&&(before.checkInAt!==checkInAt||before.checkOutAt!==checkOutAt),guestCountChanged=!!before&&reservationGuestCount(before)!==resolvedGuestCount,candidate=",
    "        if(linkedCurrentStay&&checkInAt>now)return {error:'현재 투숙 중인 예약의 체크인을 미래 시각으로 옮길 수 없습니다. 실제 입실 시각을 확인해 주세요.'};\n        const payload={roomNo:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount},duplicateReservation=!id?activeReservationsFor(state,room.no).find(item=>reservationPayloadMatches(item,payload))||null:null,unchangedReservation=!!previous&&reservationPayloadMatches(previous,payload);\n        if(duplicateReservation)return {reservation:duplicateReservation,previous:null,duplicate:true,unchanged:true};\n        if(unchangedReservation)return {reservation:previous,previous:before,duplicate:true,unchanged:true};\n        const scheduleChanged=!!before&&(before.checkInAt!==checkInAt||before.checkOutAt!==checkOutAt),guestCountChanged=!!before&&reservationGuestCount(before)!==resolvedGuestCount,candidate=",
    'reservation duplicate and unchanged guard',
)
replace_once(
    "        appendEvent(`${room.no}호 예약 ${previous?'변경':'접수'}`,`${previous?`${quickRangeLabel(before)} → `:''}${quickRangeLabel(reservation)} · ${reservationNights(reservation)}박${guestChange}${previous?' · 예약정보 수정':' · 퇴실 청소 준비'}`,{roomId:room.no});",
    "        appendEvent(`${room.no}호 예약 ${previous?'변경':'접수'}`,`${previous?`${quickRangeLabel(before)} → `:''}${quickRangeLabel(reservation)} · ${reservationNights(reservation)}박${guestChange}${previous?' · 예약정보 수정':' · 퇴실 청소 준비'}`,{roomId:room.no,dedupeKey:`reservation:${reservation.id}:${reservationFingerprint(reservation)}`});",
    'reservation event dedupe key',
)

replace_once(
    "      function currentSubmission(no) {\n        const id=state.currentSubmissionByRoom?.[no],submission=id?validatedSubmission(state.cleaningSubmissions?.[id]||null):null;if(!id||!submission)return null;return submission.id===id&&submission.room===no?submission:null;\n      }\n      function activeBombRoomReport(no) {",
    "      function currentSubmission(no) {\n        const id=state.currentSubmissionByRoom?.[no],submission=id?validatedSubmission(state.cleaningSubmissions?.[id]||null):null;if(!id||!submission)return null;return submission.id===id&&submission.room===no?submission:null;\n      }\n      function submissionForAttempt(attemptId) { return attemptId?Object.values(state.cleaningSubmissions||{}).find(item=>item.attemptId===attemptId)||null:null; }\n      function createCleaningSubmissionRecord(no) {\n        const room=ROOMS.find(item=>item.no===String(no)),task=taskState(String(no)),report=activeBombRoomReport(String(no)),attemptId=task.attemptId||currentAttemptId(String(no)),attempt=state.cleaningAttempts?.[attemptId];if(!room||!attemptId||!attempt)return {error:'현재 청소 회차를 찾을 수 없습니다.'};\n        const existing=submissionForAttempt(attemptId);if(existing){state.currentSubmissionByRoom[String(no)]=existing.id;return {submission:existing,created:false,duplicate:true};}\n        const templateSnapshot=task.templateSnapshot||snapshotForAttempt(String(no),attempt),identity={performerId:attempt.performerId,performerName:attempt.performerName},completedAt=attempt.completedAt||`${state.selectedDate} ${state.time}`,submissionId=`submission-${attemptId}`;if(state.cleaningSubmissions?.[submissionId]&&state.cleaningSubmissions[submissionId].attemptId!==attemptId)return {error:'다른 청소 회차가 같은 제출 식별자를 사용 중입니다.'};\n        const submission={id:submissionId,attemptId,room:String(no),...identity,weekStart:weekStartIso(timestampIsoDate(completedAt)),kind:attempt.kind||'퇴실 청소',baseRateSnapshot:cleaningBaseRate(String(no),report,attempt.baseRateSnapshot),roomMetaSnapshot:attempt.roomMetaSnapshot||roomMetadataSnapshot(String(no)),reservationIdSnapshot:attempt.reservationIdSnapshot||null,guestCountSnapshot:guestCountForAttempt(attempt),status:'pending',completedAt,submittedAt:`${state.selectedDate} ${state.time}`,reportId:report?.id||null,note:task.note||'',templateId:templateSnapshot?.id||null,templateVersion:templateSnapshot?.version||null,templateSnapshot,checklist:{},uploads:task.uploads.map(upload=>({...upload,image:upload.image?{...upload.image}:null})),candle:task.candle||0};\n        state.cleaningSubmissions[submissionId]=submission;state.currentSubmissionByRoom[String(no)]=submissionId;attempt.status='submitted';if(report){report.submissionId=submissionId;report.submittedVersion='v2';report.submittedAt=submission.submittedAt;}state.jobs[String(no)]='inspection';state.inspections[String(no)]='pending';appendEvent(`${no}호 청소 전체 제출`,`${submissionId} · 관리자 검수 큐 등록${report?` · 폭탄방 ${report.id} 증빙 잠금`:''}`,{maidIds:[submission.performerId],attemptId,dedupeKey:`submission:${attemptId}`});assertNoDuplicateDurableRecords(state);return {submission,created:true,duplicate:false};\n      }\n      function activeBombRoomReport(no) {",
    'stable cleaning submission helper',
)

submit_handler = r'''        if(a==='submit-cleaning-v2'){
          const task=taskState(id),existingSubmission=submissionForAttempt(task.attemptId||currentAttemptId(id));
          if(existingSubmission){state.currentSubmissionByRoom[id]=existingSubmission.id;render();focusAfterRender();toast('이 청소 회차는 이미 제출되어 기존 검수 건을 유지합니다.');return;}
          const req=taskRequirements(id);if(!maidCanEditCleaning(id,['upload'])){toast('본인 담당 업로드 단계의 최신 상태에서만 전체 제출할 수 있습니다.','error');return;}
          if(!req.requiredDone||req.failed){toast('필수 촬영 구역을 모두 완료하고 미전송 사진을 재시도하세요.','error');return;}
          const result=createCleaningSubmissionRecord(id);if(result.error){render();toast(result.error,'error');return;}
          render();focusAfterRender();toast(`청소 전체를 제출해 검수 대기로 전환했습니다.${result.submission.reportId?' 폭탄방 증빙도 함께 잠겼습니다.':''}`);return;
        }
'''
replace_between("        if(a==='submit-cleaning-v2'){", "        if(a==='approve-inspection-v2')", submit_handler, 'idempotent cleaning submission handler')

replace_once(
    "          if(unpaid)appendEvent(`${id}호 재청소 전체 승인`,`제출 ${submission.id} · 처음 청소한 ${submission.performerName} 본인 완료 · 무급 0원 · 수익 원장 없음`,{maidIds:[submission.performerId]});\n          else appendEvent(`${id}호 청소 전체 승인`,`제출 ${submission.id} · 해당 객실 기본 ${money(record.base)} + 폭탄방 추가 ${money(record.bombBonus)} = ${money(record.total)} · ${created?'수익 1건 생성':'기존 수익 유지'}`,{maidIds:[submission.performerId]});",
    "          if(unpaid)appendEvent(`${id}호 재청소 전체 승인`,`제출 ${submission.id} · 처음 청소한 ${submission.performerName} 본인 완료 · 무급 0원 · 수익 원장 없음`,{maidIds:[submission.performerId],attemptId:submission.attemptId,dedupeKey:`approval:${submission.id}:unpaid`});\n          else appendEvent(`${id}호 청소 전체 승인`,`제출 ${submission.id} · 해당 객실 기본 ${money(record.base)} + 폭탄방 추가 ${money(record.bombBonus)} = ${money(record.total)} · ${created?'수익 1건 생성':'기존 수익 유지'}`,{maidIds:[submission.performerId],attemptId:submission.attemptId,dedupeKey:`approval:${submission.id}:paid`});",
    'approval event dedupe keys',
)

replace_once(
    "      function setPaymentStatusFor(context,status) {\n        const key=paymentRecordKey(context.cfg.start,context.maid.id),confirmedTasks=context.tasks.filter(task=>task.stage==='confirmed'),previous=paymentRecordFor(context.cfg.start,context.maid.id);\n        const timestamp=",
    "      function setPaymentStatusFor(context,status) {\n        const key=paymentRecordKey(context.cfg.start,context.maid.id),confirmedTasks=context.tasks.filter(task=>task.stage==='confirmed'),previous=paymentRecordFor(context.cfg.start,context.maid.id);if(previous.status===status)return previous.status;\n        const timestamp=",
    'payment same-status no-op',
)

replace_once(
    "          appendEvent(`${context.maid.name} ${weekRangeLabel(context.cfg.start)} 지급 진행 선점`,`${money(context.totals.confirmed)} · 확정 청소 ${context.tasks.filter(task=>task.stage==='confirmed').length}건 · 금액·수익 ID 잠금 · 다른 메이드 상태 불변`,{maidIds:[context.maid.id]});",
    "          appendEvent(`${context.maid.name} ${weekRangeLabel(context.cfg.start)} 지급 진행 선점`,`${money(context.totals.confirmed)} · 확정 청소 ${context.tasks.filter(task=>task.stage==='confirmed').length}건 · 금액·수익 ID 잠금 · 다른 메이드 상태 불변`,{maidIds:[context.maid.id],dedupeKey:`payment:${paymentRecordKey(context.cfg.start,context.maid.id)}:PAYING:${taskFingerprint}`});",
    'payment start event dedupe key',
)
replace_once(
    "          appendEvent(`${context.maid.name} ${weekRangeLabel(context.cfg.start)} 정산 확인 필요`,`${money(currentRecord.amountSnapshot||0)} · 잠근 수익 ${currentRecord.taskIds.length}건 · 송금 여부 확인 전 자동 복귀 금지`,{maidIds:[context.maid.id]});",
    "          appendEvent(`${context.maid.name} ${weekRangeLabel(context.cfg.start)} 정산 확인 필요`,`${money(currentRecord.amountSnapshot||0)} · 잠근 수익 ${currentRecord.taskIds.length}건 · 송금 여부 확인 전 자동 복귀 금지`,{maidIds:[context.maid.id],dedupeKey:`payment:${paymentRecordKey(context.cfg.start,context.maid.id)}:CHECK:${currentRecord.taskFingerprint}`});",
    'payment check event dedupe key',
)
replace_once(
    "          appendEvent(`${context.maid.name} ${weekRangeLabel(context.cfg.start)} 지급 완료 기록`,`${money(currentRecord.amountSnapshot||0)} · 잠근 수익 ${currentRecord.taskIds.length}건 · 다른 메이드 상태 불변 · 앱 밖 전액 송금 완료만 기록`,{maidIds:[context.maid.id]});",
    "          appendEvent(`${context.maid.name} ${weekRangeLabel(context.cfg.start)} 지급 완료 기록`,`${money(currentRecord.amountSnapshot||0)} · 잠근 수익 ${currentRecord.taskIds.length}건 · 다른 메이드 상태 불변 · 앱 밖 전액 송금 완료만 기록`,{maidIds:[context.maid.id],dedupeKey:`payment:${paymentRecordKey(context.cfg.start,context.maid.id)}:PAID:${currentRecord.taskFingerprint}`});",
    'payment completion event dedupe key',
)

replace_once(
    "      const deprecatedStateActions=new Set(['retry-photo'",
    "      const mutationActionLocks=new Set(),mutationActions=new Set(['save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);\n      const deprecatedStateActions=new Set(['retry-photo'",
    'high-risk action lock set',
)
replace_once(
    "        e.preventDefault();e.stopImmediatePropagation();\n        if(deprecatedStateActions.has(a))",
    "        e.preventDefault();e.stopImmediatePropagation();\n        const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}\n        if(deprecatedStateActions.has(a))",
    'same-tick action mutation lock',
)

api_block = r'''      function installCastleTestApi() {
        const findReservationInput=(startOffset=30)=>{for(let offset=startOffset;offset<startOffset+120;offset++){const date=shiftIsoDate(state.selectedDate,offset),range=quickBookingTimes(date,date);for(const room of ROOMS){if(roomIsOnHold(room.no)||reservationHardBlockReason(room))continue;if(!reservationOverlaps(room.no,range.checkInAt,range.checkOutAt))return {roomNo:room.no,checkInAt:range.checkInAt,checkOutAt:range.checkOutAt,guestCount:guestPolicyForRoom(room.no).defaultGuestCount,source:'test'};}}throw new Error('중복 방지 테스트용 예약 가능 객실을 찾지 못했습니다.');};
        window.__CASTLE_TEST__=Object.freeze({
          snapshot:()=>durableLedgerSnapshot(state),fingerprint:()=>durableLedgerFingerprint(state),assertUnique:()=>assertNoDuplicateDurableRecords(state),
          repeatRender:(count=1)=>{const before=durableLedgerFingerprint(state);for(let index=0;index<Math.max(1,Number(count)||1);index++)render();const after=durableLedgerFingerprint(state);return {before,after,equal:before===after,snapshot:durableLedgerSnapshot(state)};},
          resetScenario:(scenario=0)=>{state=makeScenario(Number(scenario)||0);hydrateTemplateSnapshotsForState();rawCloseModal();render();return durableLedgerSnapshot(state);},
          findReservationInput,
          createReservationTest:(startOffset=30)=>{const input=findReservationInput(startOffset),result=upsertReservationRecord(input);return {input,result,snapshot:durableLedgerSnapshot(state)};},
          upsertReservation:input=>upsertReservationRecord(input),
          prepareSubmission:(roomNo='528')=>{const no=String(roomNo),attemptId=currentAttemptId(no),attempt=state.cleaningAttempts?.[attemptId],task=taskState(no);if(!attempt||!task)throw new Error(`${no}호 청소 회차가 없습니다.`);state.jobs[no]='upload';attempt.status='upload';attempt.completedAt=attempt.completedAt||`${state.selectedDate} ${state.time}`;task.uploads.forEach(upload=>{if(upload.required&&upload.status!=='done')upload.status='done';});return {room:no,attemptId,requiredDone:taskRequirements(no).requiredDone};},
          submitCleaning:roomNo=>createCleaningSubmissionRecord(String(roomNo)),
          confirmEarning:roomNo=>confirmCleaningEarning(String(roomNo)),
          paymentTestContext:()=>{for(const maid of MAIDS){const context=paymentContextFor(state.adminPayWeek,maid.id);if(context&&!context.meta.locked&&context.totals.confirmed>0)return {weekStart:context.cfg.start,maidId:maid.id,status:context.meta.status,amount:context.totals.confirmed};}return null;},
          setPaymentStatus:(weekStart,maidId,status)=>{const context=paymentContextFor(weekStart,maidId);if(!context)throw new Error('지급 테스트 대상을 찾을 수 없습니다.');const before=durableLedgerSnapshot(state);setPaymentStatusFor(context,status);const record=state.paymentRecords[paymentRecordKey(weekStart,maidId)]||null;assertNoDuplicateDurableRecords(state);return {before,record,after:durableLedgerSnapshot(state)};},
          counts:()=>({reservations:(state.reservations||[]).length,drafts:(state.drafts||[]).length,submissions:Object.keys(state.cleaningSubmissions||{}).length,earnings:Object.keys(state.earningRecords||{}).length,earningTotal:Object.values(state.earningRecords||{}).reduce((total,item)=>total+Number(item.total||0),0),payments:Object.keys(state.paymentRecords||{}).length,events:(state.events||[]).length}),
        });
      }
      installCastleTestApi();
'''
replace_once(
    "      hydrateTemplateSnapshotsForState();\n      const initialParams=",
    api_block + "      hydrateTemplateSnapshotsForState();\n      const initialParams=",
    'test API installation',
)

html_path.write_text(html, encoding='utf-8')

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8').rstrip()
readme += '''

## 예약·청소·급여 멱등성과 중복 방지 (2026-08-24)

- 렌더링은 예약, 청소 제출, 급여 적립, 메이드별 지급 기록, 감사 이벤트 원장을 추가·수정하지 않는다. 첫 렌더 이후 매 렌더 전후의 내구 원장 지문을 비교하고 달라지면 오류로 중단한다.
- 신규 예약은 객실·체크인·체크아웃·숙박 인원이 같은 활성 예약이 이미 있으면 기존 예약을 반환한다. 기존 예약에 같은 값을 다시 저장해도 청소 초안, 이벤트, 예약 순번을 새로 만들지 않는다.
- 청소 제출 ID는 청소 수행 회차 `attemptId`에서 안정적으로 만든다. 같은 회차를 다시 제출하면 기존 제출을 유지하며 두 번째 검수 건이나 급여 건을 만들지 않는다.
- 급여 적립은 제출 ID를 유일 키로 사용한다. 승인 재시도는 기존 적립을 유지하고 폭탄방 추가요금도 같은 제출·신고 결정에 한 번만 귀속한다.
- 지급 기록은 `(주차, 메이드)` 한 키만 갱신한다. 같은 상태를 다시 적용하면 금액·수익 ID·타임스탬프를 덮어쓰지 않으며, 지급 상태 전환 이벤트에는 멱등 키를 남긴다.
- 저장·제출·승인·지급 완료 버튼은 같은 브라우저 태스크 안의 중복 클릭을 잠근다. 운영 서버 구현에서는 이 클라이언트 보호와 별도로 DB 유니크 제약, 트랜잭션, API idempotency key가 필요하다.
'''
readme_path.write_text(readme, encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8').rstrip()
qa += '''

## 2026-08-24 · 예약·청소·급여 멱등성·중복 방지 회귀 검사

- 같은 상태에서 `render()`를 12회 반복해 예약, 청소 초안, 청소 제출, 급여 적립, 지급 기록, 이벤트 지문이 바뀌지 않는지 확인했다.
- 동일 객실·체크인·체크아웃·숙박 인원의 신규 예약을 두 번 저장해 예약·청소 초안·이벤트가 한 번만 늘어나는지 확인했다.
- 방금 저장한 예약을 같은 값으로 수정해 예약 순번과 이벤트가 늘지 않고, 다른 일정의 정상 예약은 별도 건으로 저장되는지 확인했다.
- 같은 청소 `attemptId`를 두 번 제출해 제출 ID, 검수 건, 이벤트가 한 건으로 유지되는지 확인했다.
- 같은 제출의 급여 적립을 두 번 확정해 `earningRecords[submissionId]` 한 건과 같은 합계가 유지되는지 확인했다.
- 같은 `(주차, 메이드)` 지급 상태를 반복 적용해 지급 레코드 키 수, 금액 스냅샷, 수익 ID가 변하지 않는지 확인했다.
- 예약 ID, 활성 예약 일정, 청소 회차 제출, 제출별 급여 적립, 지급 기록 수익 ID, 멱등 이벤트 키의 중복을 전역 검사했다.
- 390·768·1440px에서 기존 예약·청소·급여 화면, 콘솔·런타임 오류와 문서 가로 넘침을 확인했다.
'''
qa_path.write_text(qa, encoding='utf-8')

checker_path = Path('scripts/check-workspace.mjs')
checker = checker_path.read_text(encoding='utf-8')
marker = "console.log('Per-maid weekly payment static contracts: passed');"
if checker.count(marker) != 1:
    raise SystemExit(f'idempotency checker marker mismatch: {checker.count(marker)}')
checks = r'''for (const contract of [
  'function durableLedgerSnapshot(',
  'function durableLedgerFingerprint(',
  'function assertNoDuplicateDurableRecords(',
  "throw new Error('렌더링 중 예약·청소 제출·급여·지급 원장이 변경되었습니다.')",
  'function reservationPayloadMatches(',
  'duplicateReservation=!id?',
  'unchangedReservation=!!previous',
  'duplicate:true,unchanged:true',
  'dedupeKey:`reservation:${reservation.id}:${reservationFingerprint(reservation)}`',
  'function submissionForAttempt(',
  'function createCleaningSubmissionRecord(',
  'submissionId=`submission-${attemptId}`',
  'dedupeKey:`submission:${attemptId}`',
  'dedupeKey:`approval:${submission.id}:paid`',
  'if(previous.status===status)return previous.status',
  'mutationActionLocks=new Set()',
  'mutationActions=new Set(',
  'window.__CASTLE_TEST__=Object.freeze',
  'repeatRender:',
  'createReservationTest:',
  'prepareSubmission:',
  'confirmEarning:',
  'setPaymentStatus:',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation/cleaning/payroll idempotency contract missing: ${contract}`);
}
const upsertIdempotencyStart=html.indexOf('function upsertReservationRecord');
const upsertIdempotencyEnd=html.indexOf('function clearOrphanedReservationDraftJob',upsertIdempotencyStart);
const upsertIdempotencySource=html.slice(upsertIdempotencyStart,upsertIdempotencyEnd);
if(!upsertIdempotencySource.includes('duplicateReservation')||!upsertIdempotencySource.includes('unchangedReservation')||upsertIdempotencySource.indexOf('duplicateReservation')>upsertIdempotencySource.indexOf('++state.reservationSequence')){
  throw new Error('Reservation duplicate guard must run before generating a new reservation ID.');
}
const submissionIdempotencyStart=html.indexOf('function createCleaningSubmissionRecord');
const submissionIdempotencyEnd=html.indexOf('function activeBombRoomReport',submissionIdempotencyStart);
const submissionIdempotencySource=html.slice(submissionIdempotencyStart,submissionIdempotencyEnd);
if(!submissionIdempotencySource.includes('submissionForAttempt(attemptId)')||/Date\.now\(|\+\+cleaningSubmissionSequence/.test(submissionIdempotencySource)){
  throw new Error('Cleaning submission identity must be stable per attempt and must not use time/random sequence IDs.');
}
for (const contract of ['예약·청소·급여 멱등성과 중복 방지','DB 유니크 제약','API idempotency key']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Idempotency README contract missing: ${contract}`);
}
for (const contract of ['예약·청소·급여 멱등성·중복 방지 회귀 검사','render()`를 12회','같은 청소 `attemptId`','earningRecords[submissionId]']) {
  if (!qa.includes(contract)) throw new Error(`Idempotency QA contract missing: ${contract}`);
}

'''
checker_path.write_text(checker.replace(marker, checks + marker, 1), encoding='utf-8')

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path('SHA256SUMS.txt')
lines = sums_path.read_text(encoding='utf-8').splitlines()
found = False
updated = []
for line in lines:
    if line.endswith('  WIREFRAME/index.html'):
        updated.append(f'{digest}  WIREFRAME/index.html')
        found = True
    else:
        updated.append(line)
if not found:
    raise SystemExit('WIREFRAME/index.html checksum line missing')
sums_path.write_text('\n'.join(updated) + '\n', encoding='utf-8')

manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version'] = '2026-08-24-idempotency-guards'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
