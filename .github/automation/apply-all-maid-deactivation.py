from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML_PATH = Path("WIREFRAME/index.html")
html = HTML_PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    html = html.replace(old, new, 1)


def replace_between(start_marker: str, end_marker: str, replacement: str, label: str, *, use_last: bool = False) -> None:
    global html
    start = html.rfind(start_marker) if use_last else html.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = html.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    html = html[:start] + replacement + html[end:]


replace_once(
    "maidDeactivation:{choice:null,gates:{assignments:false,round:false,lease:false},startedAt:null,completedAt:null},",
    "maidDeactivation:{choice:null,gates:{assignments:false,round:false,lease:false},startedAt:null,completedAt:null}, maidDeactivationById:{},",
    "per-maid deactivation state",
)

status_helpers = r'''      function maidStatusFor(maidId) { return maidId==='m1'?state.maidStatus:(state.maidStatusById?.[maidId]||'inactive'); }
      function setMaidStatusFor(maidId,status) {
        state.maidStatusById=state.maidStatusById||{};state.maidStatusById[maidId]=status;
        if(maidId==='m1')state.maidStatus=status;
        return status;
      }
      function emptyMaidDeactivationFlow(){return {choice:null,activeRoom:null,gates:{assignments:false,round:false,lease:false},startedAt:null,completedAt:null};}
      function maidDeactivationFor(maidId) {
        const flow=maidId==='m1'?state.maidDeactivation:state.maidDeactivationById?.[maidId];
        return flow&&flow.gates?flow:emptyMaidDeactivationFlow();
      }
      function ensureMaidDeactivationFor(maidId) {
        if(maidId==='m1'){
          if(!state.maidDeactivation?.gates)state.maidDeactivation=emptyMaidDeactivationFlow();
          return state.maidDeactivation;
        }
        state.maidDeactivationById=state.maidDeactivationById||{};
        if(!state.maidDeactivationById[maidId]?.gates)state.maidDeactivationById[maidId]=emptyMaidDeactivationFlow();
        return state.maidDeactivationById[maidId];
      }
      function setMaidDeactivationFor(maidId,flow) {
        if(maidId==='m1')state.maidDeactivation=flow;
        state.maidDeactivationById=state.maidDeactivationById||{};state.maidDeactivationById[maidId]=flow;
        return flow;
      }
      function signedInMaidIsActive() { return maidStatusFor(signedInMaidId())==='active'; }
      function maidCanReceiveNewAssignment(maidId) { return maidStatusFor(maidId)==='active'; }
      function pendingInspectionForMaid(maidId) { return validatedSubmissions().find(submission=>submission.performerId===maidId&&submission.status==='pending')||null; }
      function maidCanCompleteRequiredReclean(no) {
        const maidId=signedInMaidId(),attempt=activeRecleanAttempt(no);
        return maidStatusFor(maidId)==='deactivating'&&attempt?.performerId===maidId;
      }
      function maidCanContinueDeactivation(no) {
        const maidId=signedInMaidId(),flow=maidDeactivationFor(maidId),attempt=state.cleaningAttempts?.[currentAttemptId(no)],job=state.jobs[no];
        return maidStatusFor(maidId)==='deactivating'&&attempt?.room===no&&attempt.performerId===maidId&&attempt.kind!=='재청소'&&(job==='upload'||flow?.choice==='finish'&&flow.activeRoom===no&&job==='cleaning');
      }
'''
replace_between(
    "      function maidStatusFor(maidId)",
    "      function activeUnfinishedAttempt(no)",
    status_helpers,
    "generic maid status helpers",
)

final_render_maids_start = "      function renderMaids() {\n        const tab=state.adminMaidTab||'workforce';"
final_render_maids_end = "      function payrollDateLabel(value) {"
render_maids_block = r'''      function renderMaids() {
        const tab=state.adminMaidTab||'workforce';
        return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>메이드 운영</h2><p>주간 근무 가능일·배정 업무·과거 근무 기록·주급·컴플레인을 분리해 관리합니다.</p></div></div><div class="tabs" role="tablist" aria-label="메이드 관리"><button type="button" role="tab" data-action="admin-maid-tab" data-tab="workforce" aria-selected="${tab==='workforce'}">주간 근무표</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="history" aria-selected="${tab==='history'}">근무 기록</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="pay" aria-selected="${tab==='pay'}">주급 정산</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="complaints" aria-selected="${tab==='complaints'}">컴플레인·벌점</button></div>${tab==='history'?renderWorkHistory():tab==='pay'?renderAdminPayroll():tab==='complaints'?renderComplaintsPanel():renderWorkforce()}</div>`;
      }
      function renderWorkforce() {
        const submitted=Object.values(state.weeklyAvailability).filter(item=>['submitted','change-requested'].includes(item.status)).length;
        const cards=MAIDS.map(maid=>{const record=state.weeklyAvailability[maid.id],availableDays=record.days.map(index=>['월','화','수','목','금','토','일'][index]).join('·')||'없음',accountStatus=maidStatusFor(maid.id),activity=accountStatus==='active'?maid.active:accountStatus==='deactivating'?'비활성 처리 중':'비활성';return `<article class="card pay-person" data-maid-card="${maid.id}"><div class="pay-person-head"><div class="avatar">${maid.name[0]}</div><div><h3>${maid.name} · 데모</h3><p>${maid.phone} · ${activity}</p></div>${statusBadge(accountStatus==='active'?(record.status==='submitted'?'제출 완료':record.status==='change-requested'?'변경 요청':'미제출'):accountStatus==='deactivating'?'비활성 처리 중':'비활성',accountStatus==='active'?(record.status==='submitted'?'green':record.status==='change-requested'?'amber':'red'):accountStatus==='deactivating'?'amber':'neutral')}</div><div class="pay-stats"><div class="pay-stat"><span>다음 주 가능</span><strong>${availableDays}</strong></div><div class="pay-stat"><span>예정 배정</span><strong>${assignmentTargets().filter(item=>assignmentFor(item).maidId===maid.id).length}객실</strong></div><div class="pay-stat"><span>제출 시각</span><strong>${record.submittedAt||'—'}</strong></div></div>${button('상세·이력','maid-detail','outline',`data-id="${maid.id}"`)}</article>`;}).join('');
        return `<section class="card assignment-panel"><div class="assignment-panel-head"><div><h3>메이드 주간 근무표</h3><p>8월 17일–23일 · 일요일 23:59 마감</p></div>${statusBadge(`${submitted}/${MAIDS.length} 제출`,submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section><div class="room-list-v2">${cards}</div>`;
      }
'''
replace_between(final_render_maids_start, final_render_maids_end, render_maids_block, "final maid hub and cards", use_last=True)

maid_detail_block = r'''      function maidById(id) { return MAIDS.find(m=>m.id===id); }
      function maidDeactivationLabel(maidId) {
        const status=maidStatusFor(maidId);
        if(status==='deactivating')return '비활성 처리 중';
        if(status==='inactive')return '비활성';
        return '활성';
      }
      function maidDeactivationBlockers(maidId) {
        const pending=pendingInspectionForMaid(maidId),future=notifiedAssignmentEntriesForMaid(maidId),reclean=unresolvedRecleanForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId),unfinished=unfinishedCurrentAttemptsForMaid(maidId);
        const messages=[future.length?`다음 근무일 통보 ${future.length}건 재배정 필요`:'',pending?`${pending.room}호 검수 결정 필요`:'',reclean?`${reclean.room}호 본인 무급 재청소 완료 필요`:'',conflict?`${conflict.room}호 출입 충돌 종결 필요`:'',unfinished.length?`미종결 수행 회차 ${unfinished.map(item=>item.room+'호').join('·')} 정리 필요`:''].filter(Boolean);
        return {pending,future,reclean,conflict,unfinished,messages};
      }
      function renderMaidDeactivationGate(maidId) {
        const maid=maidById(maidId),flow=maidDeactivationFor(maidId),blockers=maidDeactivationBlockers(maidId),allDone=Object.values(flow.gates).every(Boolean),locked=isLocked();
        if(maidStatusFor(maidId)!=='deactivating')return '';
        const choice=flow.choice==='stop'?'즉시 중단·인계':'현재 작업 마무리 후 비활성';
        return `<div class="maid-deactivation-gate" data-maid-deactivation-gate="${maidId}">${blockers.messages.length?`<div class="notice notice-warning" style="margin-top:12px"><div><strong>완료 전 필수 조치</strong><br>${esc(blockers.messages.join(' · '))}</div></div>`:''}<div class="choice-list" style="margin-top:12px"><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="assignments" ${flow.gates.assignments?'checked':''} ${locked?'disabled':''}><span><strong>담당 정리 완료</strong><span>통보된 미래 담당을 다른 활성 메이드에게 변경 통보 · ${flow.choice==='stop'?'진행 작업 인계자 확정':'현재 작업 외 신규 담당 없음'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="round" ${flow.gates.round?'checked':''} ${locked?'disabled':''}><span><strong>수행 회차·검수 종결</strong><span>${flow.choice==='stop'?'현재 회차를 중단으로 보존하고 새 담당 회차 생성':'현재 회차 제출 뒤 관리자 검수 결정까지 완료'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="lease" ${flow.gates.lease?'checked':''} ${locked?'disabled':''}><span><strong>PIN lease 종료</strong><span>조회 이력은 보존하고 ${esc(maid?.name||maidId)}의 활성 lease만 종료</span></span></label></div><div style="margin-top:12px">${button('비활성 완료','complete-deactivation-v2','danger',`${!allDone||locked||blockers.messages.length?'disabled ':''}data-id="${maidId}"`)}</div><p class="audit-note" style="margin:10px 0 0">선택 방식: ${esc(choice)} · 담당·수행 회차·검수·PIN을 모두 닫은 뒤에만 완료됩니다.</p></div>`;
      }
      function renderMaidAccountManagement(maidId) {
        const maid=maidById(maidId),status=maidStatusFor(maidId),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(maidId);
        const content=status==='active'?`${button('영향 확인·비활성 처리','deactivate-maid-v2','danger',`${isLocked()?'disabled ':''}data-id="${maidId}"`)}`:processing?`<div class="notice notice-danger" style="margin:0"><div><strong>신규 권한 잠금 적용 중</strong><br>${esc(maid?.name||maidId)}의 신규 업무 확인·직접 배정·새 PIN lease 발급이 차단됐습니다.</div></div>${renderMaidDeactivationGate(maidId)}`:`<div class="notice notice-success" style="margin:0"><div><strong>비활성 완료</strong><br>로그인과 신규 업무·PIN 접근은 종료됐고 과거 수행·검수·주급 자료는 그대로 보존됩니다.${flow.completedAt?` · 완료 ${esc(flow.completedAt)}`:''}</div></div>`;
        return `<section class="card card-pad maid-account-management" data-maid-account-management="${maidId}"><div class="section-head"><div><h3>계정 관리</h3><span class="meta">위험 작업 · 상세 화면 마지막 영역</span></div>${statusBadge(maidDeactivationLabel(maidId),status==='active'?'green':processing?'amber':'neutral')}</div><p class="audit-note">비활성 처리는 계정만 닫습니다. 담당 구간·수행 회차·PIN lease는 종결 이벤트를 남기고 과거 이력·검수·수익은 삭제하지 않습니다.</p><div style="margin-top:12px">${content}</div></section>`;
      }
      function renderMaidDetail(id) {
        const m=maidById(id)||MAIDS[0],status=maidStatusFor(m.id),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(m.id),currentApproved=maidPayAmount(m.name),submissions=validatedSubmissions().filter(submission=>submission.performerId===m.id).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))),assignments=ROOMS.filter(room=>room.assignee===m.name),currentAttempts=unfinishedCurrentAttemptsForMaid(m.id),currentRooms=new Set(currentAttempts.map(item=>item.room)),complaintCount=(state.complaints||[]).filter(item=>!item.deleted&&item.maid===m.name).length;
        const submissionHistoryRows=submissions.map(submission=>{
          const record=earningRecordForSubmission(submission),report=bombRoomReportForSubmission(submission),fee=bombRoomBreakdown(submission.room,{reportOverride:report,baseOverride:submission.baseRateSnapshot}),wholeRejected=submission.status==='rejected',decision=report?.status==='approved'?'폭탄방 승인':report?.status==='rejected'?'폭탄방 미인정':report?.status==='pending'?'폭탄방 검수 대기':'폭탄방 신고 없음';
          const submissionStatus=wholeRejected?`전체 반려 · ${decision} 결정 보존 · 적립 0원`:submission.kind==='재청소'?(submission.status==='approved'?'재청소 승인 · 무급 0원':'재청소 검수 대기 · 무급 0원'):record?`${money(record.total)} 확정`:report?.status==='pending'?'폭탄방 검수 대기':submission.status==='approved'?'전체 승인 · 원장 확인':'전체 검수 대기',breakdown=wholeRejected&&report?`기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 실제 적립 0원`:'',evidence=report?.photos?.[0]?button('증빙 보기','bomb-room-photo','outline',`data-room="${submission.room}" data-report="${report.id}" data-photo="${report.photos[0].id}"`):'';
          return `<div class="rail-row"><strong>${submission.room}호 · ${esc(submission.kind||'퇴실 청소')} · ${esc(submission.submittedAt)}</strong><span>${esc(submissionStatus)} · 제출 ${esc(submission.id.split('-').slice(-2).join('-'))}${breakdown?` · ${esc(breakdown)}`:''}${evidence}</span></div>`;
        });
        const currentAttemptRows=currentAttempts.map(({room,attempt})=>`<div class="rail-row"><strong>${room}호 · ${esc(attempt?.kind||'청소')} · 현재 수행 회차</strong><span>${esc(cleaningLabel(state.jobs[room]))} · ${esc(attempt?.id||'회차 정보 없음')}</span></div>`),assignmentRows=assignments.filter(room=>!currentRooms.has(room.no)).map(room=>`<div class="rail-row"><strong>${room.no}호 · 현재 담당</strong><span>${esc(cleaningLabel(state.jobs[room.no]))} · 담당 선택 권한 없음</span></div>`),historyRows=[...currentAttemptRows,...assignmentRows,...submissionHistoryRows],unstartedCount=currentAttempts.filter(({room})=>['scheduled','claimed','unassigned'].includes(state.jobs[room])).length,progressCount=currentAttempts.filter(({room})=>state.jobs[room]==='cleaning').length,uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=submissions.filter(submission=>submission.status==='pending').length,futureCount=notifiedAssignmentEntriesForMaid(m.id).length,pinLeaseCount=activeCleaningFor(m.id)?1:0,stateTone=status==='active'?'green':processing?'amber':'neutral';
        return renderCoach()+renderNetworkNotice()+detailHeader(`${m.name} · 데모`,`불변 사용자 ID 기준 · 모든 메이드에 동일한 계정 관리·이력 보존 규칙 적용`)+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>계정·근무 상태</h3>${statusBadge(maidDeactivationLabel(m.id),stateTone)}</div><div class="info-grid"><div class="info-item"><span>로그인 아이디</span><strong>${esc(m.name)}</strong></div><div class="info-item"><span>휴대폰</span><strong>${esc(m.phone)}</strong></div><div class="info-item"><span>객실 선택 권한</span><strong>없음 · 관리자 전용</strong></div><div class="info-item"><span>배정 업무·PIN</span><strong>${status==='active'?'확인 가능':'잠금'}</strong></div></div></section><section class="card card-pad"><div class="section-head"><h3>업무 영향 요약</h3>${statusBadge(inactive?'정리 완료':'실시간 집계','neutral')}</div><div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${futureCount}건 · ${inactive?'정리 완료':'변경 통보 필요'}</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${unstartedCount+progressCount}건 · ${processing?(flow.choice==='stop'?'인계 필요':'마무리 허용'):inactive?'회차 종결':'처리 방식 선택'}</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · ${uploadCount?'제출 필요':'없음'}</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · ${pendingCount?'관리자 결정 필요':'없음'}</strong></div><div class="info-item"><span>미지급 수익</span><strong>${money(currentApproved)} · 지급 이력 보존</strong></div><div class="info-item"><span>활성 PIN lease</span><strong>${inactive?'0건 · 종료':`${pinLeaseCount}건 · ${processing?'종료 필요':'현재 기준'}`}</strong></div></div></section><section class="card card-pad" data-maid-history="${m.id}"><div class="section-head"><h3>담당·실제 수행 이력</h3><select class="select-control" aria-label="이력 기간"><option>7일</option><option>30일</option></select></div><div class="rail-list">${historyRows.join('')||'<div class="rail-row"><strong>저장된 담당·수행 이력 없음</strong><span>데모 fixture 기준</span></div>'}${m.id==='m1'?'<div class="rail-row"><strong>536호 · 폭탄방 승인 수익 · 과거 데모</strong><span>기본 20,000원 + 해당 객실 추가 20,000원 = 40,000원</span></div>':''}</div></section>${renderMaidAccountManagement(m.id)}</div><aside class="detail-stack"><section class="card card-pad"><h3>평가·컴플레인</h3><p class="cell-sub">등록 ${complaintCount}건 · 주급 자동 차감 없음</p>${complaintCount?button('컴플레인 상세','complaint-detail','outline'):''}</section><section class="card card-pad"><h3>주급</h3><p><strong>이번 주 승인 확정 ${money(currentApproved)}</strong></p><p class="audit-note">다른 메이드의 객실·사진·수익은 이 상세에 섞이지 않습니다.</p>${button('지급 이력','pay-detail','outline')}</section></aside></div>`;
      }

'''
replace_between("      function maidById(id)", "      function renderComplaintDetail()", maid_detail_block, "generic maid detail and lower account management")

open_deactivation_block = r'''      function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
        const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
        if(!maid)return;
        showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
        const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
      }

'''
replace_between("      function openMaidDeactivationV2(", "      document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');", open_deactivation_block, "generic deactivation modal")

action_block = r'''        if(a==='deactivate-maid-v2'){
          const maidId=id||el.dataset.id,maid=maidById(maidId),reclean=unresolvedRecleanForMaid(maidId),pending=pendingInspectionForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId);
          if(!maid){toast('메이드 계정을 찾을 수 없습니다.','error');return;}
          if(!adminCanMutate()){toast('관리자 최신 상태에서만 비활성 처리를 시작할 수 있습니다.','error');return;}
          if(maidStatusFor(maidId)!=='active'){toast(`${maid.name} 계정은 이미 ${maidDeactivationLabel(maidId)} 상태입니다.`,'error');return;}
          if(reclean||pending||conflict){toast(reclean?`${reclean.room}호 본인 무급 재청소를 완료한 뒤 비활성 처리할 수 있습니다.`:pending?`${pending.room}호 검수 결정을 완료한 뒤 비활성 처리를 시작할 수 있습니다.`:`${conflict.room}호 출입·청소 충돌을 종결한 뒤 비활성 처리를 시작할 수 있습니다.`,'error');return;}
          openMaidDeactivationV2(maidId,el);return;
        }
        if(a==='confirm-start-deactivation-v2'){
          const maidId=id||el.dataset.id,maid=maidById(maidId),reclean=unresolvedRecleanForMaid(maidId),pending=pendingInspectionForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId);
          if(!maid||!adminCanMutate()||maidStatusFor(maidId)!=='active'||reclean||pending||conflict){closeModal();render();toast(reclean?`${reclean.room}호 본인 무급 재청소가 남아 비활성 처리를 시작하지 않았습니다.`:pending?`${pending.room}호 검수 결정이 남아 비활성 처리를 시작하지 않았습니다.`:conflict?`${conflict.room}호 출입 충돌이 남아 비활성 처리를 시작하지 않았습니다.`:'메이드 계정 상태·관리자 권한 또는 최신 상태가 바뀌어 비활성 처리를 시작하지 않았습니다.','error');return;}
          const choice=document.querySelector('input[name="maid-deactivation-choice"]:checked')?.value||'finish',activeRoom=activeCleaningFor(maidId),activeAttempt=activeRoom?state.cleaningAttempts?.[currentAttemptId(activeRoom)]:null,ownsActive=activeAttempt?.room===activeRoom&&activeAttempt.performerId===maidId&&activeAttempt.kind!=='재청소',flow={choice,activeRoom:ownsActive?activeRoom:null,gates:{assignments:false,round:false,lease:false},startedAt:state.time,completedAt:null};
          setMaidStatusFor(maidId,'deactivating');setMaidDeactivationFor(maidId,flow);if(maidId==='m1')state.handoff=choice;
          if(choice==='stop'&&ownsActive){setActiveCleaningFor(maidId,null);if(state.jobs[activeRoom]==='cleaning'){state.jobs[activeRoom]='unassigned';const room=ROOMS.find(item=>item.no===activeRoom);if(room)room.assignee='미정';}}
          appendEvent(`${maid.name} 비활성 처리 시작`,choice==='stop'?'즉시 중단·인계 · 신규 업무/배정/PIN 잠금':'현재 작업 마무리 후 비활성 · 신규 업무/배정/PIN 잠금',{maidIds:[maidId]});
          closeModal();render();focusAfterRender(`[data-maid-account-management="${maidId}"]`);toast(`${maid.name}의 신규 업무 확인·직접 배정·PIN lease를 잠그고 종결 확인을 시작했습니다.`);return;
        }
        if(a==='complete-deactivation-v2'){
          const maidId=id||el.dataset.id,maid=maidById(maidId),flow=maidDeactivationFor(maidId),blockers=maidDeactivationBlockers(maidId);
          if(!maid||!adminCanMutate()||blockers.reclean||blockers.pending||blockers.conflict||blockers.future.length||blockers.unfinished.length){toast(blockers.reclean?`${blockers.reclean.room}호 본인 무급 재청소가 남아 비활성 처리를 완료할 수 없습니다.`:blockers.pending?`${blockers.pending.room}호 검수 결정을 완료한 뒤 비활성 처리할 수 있습니다.`:blockers.conflict?`${blockers.conflict.room}호 출입 충돌을 종결한 뒤 비활성 처리할 수 있습니다.`:blockers.future.length?`다음 근무일에 통보된 ${blockers.future.length}건을 활성 메이드에게 변경 통보한 뒤 완료하세요.`:blockers.unfinished.length?`${blockers.unfinished.map(item=>item.room+'호').join('·')} 미종결 수행 회차를 제출·검수하거나 활성 메이드에게 인계한 뒤 완료하세요.`:'관리자 최신 상태에서만 비활성 처리를 완료할 수 있습니다.','error');return;}
          if(maidStatusFor(maidId)!=='deactivating'||!Object.values(flow.gates).every(Boolean)){toast('담당·수행 회차·PIN lease 종결을 모두 확인하세요.','error');return;}
          const choice=flow.choice,activeRoom=flow.activeRoom;
          if(choice==='finish'&&activeRoom&&!['inspection','approved'].includes(state.jobs[activeRoom])){toast(`${activeRoom}호 현재 작업을 전체 제출한 뒤 비활성 처리를 완료할 수 있습니다.`,'error');return;}
          setMaidStatusFor(maidId,'inactive');flow.completedAt=state.time;setMaidDeactivationFor(maidId,flow);if(activeCleaningFor(maidId)===activeRoom)setActiveCleaningFor(maidId,null);
          appendEvent(`${maid.name} 비활성 완료`,`${choice==='stop'?'즉시 중단·인계':'현재 작업 마무리'} · 담당/회차/PIN lease 종결 · 과거 이력/검수/수익 보존`,{maidIds:[maidId]});
          render();focusAfterRender(`[data-maid-account-management="${maidId}"]`);toast(`${maid.name} 계정을 비활성으로 전환하고 과거 이력·검수·수익을 보존했습니다.`);return;
        }
'''
replace_between("        if(a==='deactivate-maid-v2')", "        if(a==='complaint-detail')", action_block, "generic deactivation actions")

old_gate_handler = "if(c==='maid-deactivation-gate'){state.maidDeactivation.gates[e.target.value]=e.target.checked;const allDone=Object.values(state.maidDeactivation.gates).every(Boolean),blocked=!!pendingInspectionForMaid('m1')||!!unresolvedRecleanForMaid('m1')||!!unresolvedCleaningConflictForMaid('m1')||notifiedAssignmentEntriesForMaid('m1').length>0||unfinishedCurrentAttemptsForMaid('m1').length>0,action=document.querySelector('[data-action=\"complete-deactivation-v2\"]');if(action)action.disabled=isLocked()||!allDone||blocked;return;}"
new_gate_handler = "if(c==='maid-deactivation-gate'){const maidId=e.target.dataset.maidId,flow=ensureMaidDeactivationFor(maidId);flow.gates[e.target.value]=e.target.checked;setMaidDeactivationFor(maidId,flow);const blockers=maidDeactivationBlockers(maidId),allDone=Object.values(flow.gates).every(Boolean),action=document.querySelector(`[data-action=\"complete-deactivation-v2\"][data-id=\"${maidId}\"]`);if(action)action.disabled=isLocked()||!allDone||blockers.messages.length>0;return;}"
replace_once(old_gate_handler, new_gate_handler, "generic deactivation gate change handler")

# Add a small visual separation for the danger-zone placement.
css_marker = "    .notification-push-note { margin:0 0 12px; }"
if css_marker in html and ".maid-account-management" not in html:
    html = html.replace(css_marker, css_marker + "\n    .maid-account-management { margin-top:4px; border-color:#efc3c7; background:#fffafa; }\n    .maid-account-management .section-head { align-items:flex-start; }\n    .maid-deactivation-gate { margin-top:12px; padding-top:12px; border-top:1px solid #efd5d7; }", 1)

HTML_PATH.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 모든 메이드 계정 비활성 처리 (2026-08-26)

- 김민지1만 별도 처리하던 분기를 제거하고 9개 모든 메이드에 동일한 비활성 처리 흐름을 제공한다.
- 메이드별 상태와 비활성 종결 게이트는 사용자 ID별로 분리 저장한다. 한 계정의 처리로 다른 계정 상태가 바뀌지 않는다.
- 비활성 버튼과 종결 확인은 상세 화면의 담당·실제 수행 이력 아래 `계정 관리` 영역에 둔다. 상단 계정 상태 카드에는 위험 작업 버튼을 두지 않는다.
- 비활성 처리 중에는 해당 메이드의 신규 업무·직접 배정·PIN 접근을 막고, 담당·수행 회차·검수·PIN 종결 뒤에만 완료한다.
- 비활성 뒤에도 과거 수행자·제출·검수·주급 귀속은 삭제하지 않는다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-26 · 모든 메이드 비활성 처리와 하단 계정 관리

- 주간 근무표의 9개 메이드 상세에 `계정 관리` 영역과 비활성 버튼이 각각 하나씩 있는지 확인한다.
- 계정 관리 영역이 `담당·실제 수행 이력`보다 뒤에 렌더링되고 상단 계정 상태 카드에는 비활성 버튼이 없는지 확인한다.
- 업무가 없는 메이드의 비활성 시작·세 게이트 확인·완료를 수행하고 다른 8개 계정이 활성 상태를 유지하는지 확인한다.
- 김민지1의 기존 업무 영향·종결 게이트와 신규 배정 차단이 유지되는지 확인한다.
- 390px·1440px에서 가로 넘침, 콘솔·런타임 오류가 없는지 확인한다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker += r'''

for (const contract of [
  'function setMaidStatusFor(maidId,status)',
  'function maidDeactivationFor(maidId)',
  'function ensureMaidDeactivationFor(maidId)',
  'function maidDeactivationBlockers(maidId)',
  'function renderMaidAccountManagement(maidId)',
  'data-maid-account-management="${maidId}"',
  'data-maid-id="${maidId}"',
  "openMaidDeactivationV2(maidId,el)",
  "setMaidStatusFor(maidId,'deactivating')",
  "setMaidStatusFor(maidId,'inactive')",
  '모든 메이드에 동일한 계정 관리·이력 보존 규칙 적용',
]) {
  if (!html.includes(contract)) throw new Error(`All-maid deactivation contract missing: ${contract}`);
}
const maidDetailStartForAccountManagement=html.indexOf('function renderMaidDetail(id)');
const maidDetailEndForAccountManagement=html.indexOf('function renderComplaintDetail()',maidDetailStartForAccountManagement);
const maidDetailSourceForAccountManagement=html.slice(maidDetailStartForAccountManagement,maidDetailEndForAccountManagement);
if (maidDetailSourceForAccountManagement.includes("if(m.id!=='m1')")) throw new Error('Non-m1 early return still hides deactivation controls.');
const historyIndexForAccountManagement=maidDetailSourceForAccountManagement.indexOf('data-maid-history="${m.id}"');
const accountManagementIndex=maidDetailSourceForAccountManagement.indexOf('renderMaidAccountManagement(m.id)');
if (historyIndexForAccountManagement<0||accountManagementIndex<historyIndexForAccountManagement) throw new Error('Maid account management is not below the work-history section.');
const accountStatusCardEnd=maidDetailSourceForAccountManagement.indexOf('</section><section class="card card-pad"><div class="section-head"><h3>업무 영향 요약');
if (maidDetailSourceForAccountManagement.slice(0,accountStatusCardEnd).includes('deactivate-maid-v2')) throw new Error('Deactivation button still appears in the upper account-status card.');
const finalWorkforceStart=html.lastIndexOf('function renderWorkforce()');
const finalWorkforceEnd=html.indexOf('function payrollDateLabel(',finalWorkforceStart);
const finalWorkforceSource=html.slice(finalWorkforceStart,finalWorkforceEnd);
if (!finalWorkforceSource.includes('accountStatus=maidStatusFor(maid.id)')) throw new Error('Workforce cards do not show per-maid account status.');
console.log('All-maid lower account-management deactivation contracts: passed');
'''
checker_path.write_text(checker + "\n", encoding="utf-8")

# Refresh integrity metadata.
digest = hashlib.sha256(HTML_PATH.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
updated = False
for index, line in enumerate(lines):
    if line.endswith("  WIREFRAME/index.html"):
        lines[index] = f"{digest}  WIREFRAME/index.html"
        updated = True
        break
if not updated:
    raise SystemExit("WIREFRAME/index.html checksum entry missing")
sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-26-all-maid-deactivation"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
