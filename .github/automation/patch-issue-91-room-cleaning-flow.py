from pathlib import Path

path = Path("WIREFRAME/index.html")
source = path.read_text(encoding="utf-8")
original = source


def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    source = source.replace(old, new, 1)
    print(f"patched: {label}")


def replace_all(old: str, new: str, expected: int, label: str) -> None:
    global source
    count = source.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} matches, found {count}")
    source = source.replace(old, new)
    print(f"patched: {label} ({count})")


# 1) User-facing language: request/cancel rather than ON/OFF.
replace_once(
    "if(!adminCanMutate())return '관리자 최신 온라인 상태에서만 청소 필요를 변경할 수 있습니다.';",
    "if(!adminCanMutate())return '관리자 최신 온라인 상태에서만 청소를 요청할 수 있습니다.';",
    "request permission copy",
)
replace_once(
    "const request=activeManualCleaningRequest(no);if(!request)return '현재 켜진 수동 청소 요청이 없습니다.';",
    "const request=activeManualCleaningRequest(no);if(!request)return '현재 취소할 수 있는 수동 청소 요청이 없습니다.';",
    "missing request copy",
)
replace_once(
    "if(!adminCanMutate())return '관리자 최신 온라인 상태에서만 청소 필요를 해제할 수 있습니다.';",
    "if(!adminCanMutate())return '관리자 최신 온라인 상태에서만 청소 요청을 취소할 수 있습니다.';",
    "cancel permission copy",
)
replace_once("sourceLabel:'객실 상세 · 청소 필요 ON'", "sourceLabel:'객실 상세 · 청소 요청'", "request source label")
replace_once("appendEvent(`${no}호 청소 필요 ON`", "appendEvent(`${no}호 청소 요청`", "request event title")
replace_all("객실 상세에서 청소 필요 OFF", "객실 상세에서 청소 요청 취소", 2, "cancel ledger copy")
replace_once("appendEvent(`${no}호 청소 필요 OFF`", "appendEvent(`${no}호 청소 요청 취소`", "cancel event title")
replace_once("현장 완료로 청소 필요 OFF", "현장 완료로 청소 요청 종결", "completion event copy")

# 2) Do not permit duplicate manual requests over scheduled/current work.
replace_once(
    "if(activeUnfinishedAttempt(no)||currentSubmission(no))return '이미 수행 중이거나 검수 중인 청소 작업이 있습니다.';\n        if(roomNeedsCleaningNow(no))return '이미 자동 또는 기존 청소 대상에 포함된 객실입니다.';",
    "const submission=currentSubmission(no);if(activeUnfinishedAttempt(no)||submission&&submission.status!=='approved')return '이미 수행 중이거나 검수 중인 청소 작업이 있습니다.';\n        if(roomHasCleaningWorkflow(no))return '이미 예정되었거나 진행 중인 청소 작업이 있습니다.';",
    "manual request duplicate guard",
)

# 3) Add one shared cleaning control contract for every room card/detail.
insert_anchor = """        if(publication&&(typeof publication!=='object'||publication.status!=='cancelled'))return '메이드에게 공개된 요청은 청소 배정 화면에서 취소해야 합니다.';
        return '';
      }
      function createManualCleaningRequest(no) {"""
insert_value = """        if(publication&&(typeof publication!=='object'||publication.status!=='cancelled'))return '메이드에게 공개된 요청은 청소 배정 화면에서 취소해야 합니다.';
        return '';
      }
      function roomHasCleaningWorkflow(no) {
        no=String(no);const job=state.jobs[no],submission=currentSubmission(no);
        return !!activeManualCleaningRequest(no)||roomNeedsCleaningNow(no)||!!activeUnfinishedAttempt(no)||!!(submission&&submission.status!=='approved')||['public','unassigned','claimed','scheduled','cleaning','upload','inspection','reclean','hold','draft','future','stayover-requested','extra-requested'].includes(job);
      }
      function roomCleaningControl(no) {
        no=String(no);const room=ROOMS.find(item=>item.no===no),request=activeManualCleaningRequest(no),cancelBlock=request?manualCleaningCancelBlockReason(no):'',requestBlock=request?'':manualCleaningRequestBlockReason(no),kind=request?.kind||(room?.occupancy==='occupied'?'연박 청소':'추가 청소');
        if(request&&!cancelBlock)return {action:'toggle-room-cleaning',label:'청소 취소',disabled:false,kind,reason:'배정 전 청소 요청을 취소할 수 있습니다.'};
        if(request||roomHasCleaningWorkflow(no))return {action:'cleaning-detail',label:'청소 진행 보기',disabled:false,kind,reason:cancelBlock||'현재 청소 작업의 단계와 담당을 확인합니다.'};
        return {action:'toggle-room-cleaning',label:'청소 요청',disabled:!!requestBlock,kind,reason:requestBlock||'확인 후 청소 대기열에 등록합니다.'};
      }
      function createManualCleaningRequest(no) {"""
replace_once(insert_anchor, insert_value, "shared room cleaning control")

# 4) Replace the old switch-like detail control.
old_toggle = """      function renderManualCleaningToggle(no) {
        const request=activeManualCleaningRequest(no),turnOffBlock=request?manualCleaningCancelBlockReason(no):'',turnOnBlock=request?'':manualCleaningRequestBlockReason(no),disabled=!!(request?turnOffBlock:turnOnBlock),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');
        return `<div class=\"notice ${request?'notice-warning':'notice-info'}\" style=\"margin:14px 0 0\"><div style=\"min-width:0;flex:1\"><strong>청소 필요 ${request?'ON':'OFF'} · ${esc(kind)}</strong><br>${esc(request?turnOffBlock||'객실 상태와 관리자 청소 배정 대상에 반영되어 있습니다.':turnOnBlock||'켜면 청소 필요 표시와 미배정 청소 작업이 함께 생성됩니다.')}</div><button class=\"btn ${request?'btn-danger':'btn-primary'}\" type=\"button\" role=\"switch\" aria-checked=\"${!!request}\" data-action=\"toggle-room-cleaning\" data-id=\"${no}\" ${disabled?'disabled':''}>${request?'OFF로 변경':'ON으로 변경'}</button></div>`;
      }"""
new_toggle = """      function renderManualCleaningToggle(no) {
        const control=roomCleaningControl(no),isCancel=control.label==='청소 취소',isProgress=control.label==='청소 진행 보기',title=isCancel?`${control.kind} 요청 대기 중`:isProgress?`${control.kind} 진행 중`:`${control.kind} 요청`,copy=isCancel?'청소 대기열에 등록되어 있습니다. 배정 전이면 요청을 취소할 수 있습니다.':isProgress?control.reason:'확인 후 청소 대기열에 등록합니다.',variant=isCancel?'btn-danger':isProgress?'btn-outline':'btn-primary';
        return `<div class=\"notice ${isCancel?'notice-warning':'notice-info'}\" data-room-cleaning-panel=\"${no}\" style=\"margin:14px 0 0\"><div style=\"min-width:0;flex:1\"><strong>${esc(title)}</strong><br>${esc(copy)}</div><button class=\"btn ${variant}\" type=\"button\" data-action=\"${control.action}\" data-id=\"${no}\" data-room-cleaning-control=\"${no}\" title=\"${esc(control.reason)}\" ${control.disabled?'disabled':''}>${esc(control.label)}</button></div>`;
      }"""
replace_once(old_toggle, new_toggle, "detail cleaning request control")

# 5) Keep occupied as the main state and expose cleaning as its subordinate state.
old_presentation = """      function roomPresentation(no) {
        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no],manualRequest=activeManualCleaningRequest(no),special=cardReservationStatus(no),blockers=roomBlockingReasons(no),cleaning=roomNeedsCleaningNow(no),cleaningStage=roomCleaningStageLabel(job);
        if(!room)return {key:'blocked',tone:'red',status:'배정 불가',reason:'객실 정보 확인 필요',available:false,cleaning:false,blockers:['객실 정보 확인 필요']};
        if(blockers.length)return {key:'blocked',tone:'red',status:'배정 불가',reason:blockers.join(' · '),available:false,cleaning,cleaningStage,blockers,early:special.early,late:special.late};
        if(cleaning)return {key:'cleaning',tone:'amber',status:'청소 필요',reason:manualRequest?`${manualRequest.kind} 필요`:room.occupancy==='occupied'?'연박 청소 필요':job==='reclean'?'재청소 필요':'퇴실 청소 필요',available:false,cleaning:true,cleaningStage,blockers:[],early:special.early,late:special.late};
        if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false,cleaning:false,cleaningStage:'',blockers:[],early:special.early,late:special.late};
        return {key:'available',tone:'green',status:'배정 가능',reason:'공실 · 청소·운영·안전 조건 완료',available:true,cleaning:false,cleaningStage:'',blockers:[],early:special.early,late:special.late};
      }"""
new_presentation = """      function roomPresentation(no) {
        const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no],manualRequest=activeManualCleaningRequest(no),special=cardReservationStatus(no),blockers=roomBlockingReasons(no),cleaning=roomNeedsCleaningNow(no),cleaningStage=roomCleaningStageLabel(job),cleaningKind=manualRequest?.kind||(job==='extra-requested'?'추가 청소':room?.occupancy==='occupied'?'연박 청소':job==='reclean'?'재청소':'퇴실 청소');
        if(!room)return {key:'blocked',tone:'red',status:'배정 불가',reason:'객실 정보 확인 필요',available:false,cleaning:false,cleaningKind:'',blockers:['객실 정보 확인 필요']};
        if(blockers.length)return {key:'blocked',tone:'red',status:'배정 불가',reason:blockers.join(' · '),available:false,cleaning,cleaningKind:cleaning?cleaningKind:'',cleaningStage:cleaning?cleaningStage:'',blockers,early:special.early,late:special.late};
        if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false,cleaning,cleaningKind:cleaning?cleaningKind:'',cleaningStage:cleaning?cleaningStage:'',blockers:[],early:special.early,late:special.late};
        if(cleaning)return {key:'cleaning',tone:'amber',status:'청소 필요',reason:`${cleaningKind} 필요`,available:false,cleaning:true,cleaningKind,cleaningStage,blockers:[],early:special.early,late:special.late};
        return {key:'available',tone:'green',status:'배정 가능',reason:'공실 · 청소·운영·안전 조건 완료',available:true,cleaning:false,cleaningKind:'',cleaningStage:'',blockers:[],early:special.early,late:special.late};
      }"""
replace_once(old_presentation, new_presentation, "occupied subordinate cleaning state")

# 6) Use the shared control and subordinate cleaning badge on every room card.
replace_once(
    "const subBadges=p.cleaningStage?`<div class=\"room-status-subs\"><span class=\"room-status-sub\">${icon('briefcase','icon-sm')}청소 단계 · ${esc(p.cleaningStage)}</span></div>`:'',statusIcon=p.key==='occupied'?'user':p.key==='cleaning'?'briefcase':p.key==='available'?'check':'alert';",
    "const cleaningSubLabel=p.cleaning?(p.key==='cleaning'?(p.cleaningStage?`청소 단계 · ${p.cleaningStage}`:`${p.cleaningKind||'청소'} 필요`):`청소 필요 · ${p.cleaningKind||'청소'}${p.cleaningStage?` · ${p.cleaningStage}`:''}`):'',subBadges=cleaningSubLabel?`<div class=\"room-status-subs\"><span class=\"room-status-sub\">${icon('briefcase','icon-sm')}${esc(cleaningSubLabel)}</span></div>`:'',statusIcon=p.key==='occupied'?'user':p.key==='cleaning'?'briefcase':p.key==='available'?'check':'alert';",
    "room card subordinate cleaning badge",
)
replace_once(
    "const directAssignable=['public','draft','future','scheduled','unassigned'].includes(job)&&!roomIsOnHold(no),cleaningDetail=['cleaning','upload','inspection','approved','reclean','claimed','hold'].includes(job),cleaningAction=directAssignable?'direct-assign':cleaningDetail?'cleaning-detail':'room-detail',cleaningActionLabel=directAssignable?'청소 배정':cleaningDetail?'청소 보기':'청소 정보',operationAction=roomIsOnHold(no)?'room-detail':'operation-status',operationLabel=roomIsOnHold(no)?'정보 입력':'운영 상태',reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`:pastReservationCount?`예약 기록 ${pastReservationCount}건`:room.occupancy==='occupied'&&!occupiedReservationEnd(room)?'투숙 정보 입력':'예약 등록';",
    "const cleaningControl=roomCleaningControl(no),operationAction=roomIsOnHold(no)?'room-detail':'operation-status',operationLabel=roomIsOnHold(no)?'정보 입력':'운영 상태',reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`:pastReservationCount?`예약 기록 ${pastReservationCount}건`:room.occupancy==='occupied'&&!occupiedReservationEnd(room)?'투숙 정보 입력':'예약 등록';",
    "room card cleaning control state",
)
replace_once(
    "<button class=\"btn btn-ghost\" type=\"button\" data-action=\"${cleaningAction}\" data-id=\"${no}\">${icon('briefcase')}${cleaningActionLabel}</button>",
    "<button class=\"btn btn-ghost\" type=\"button\" data-action=\"${cleaningControl.action}\" data-id=\"${no}\" data-room-cleaning-control=\"${no}\" title=\"${esc(cleaningControl.reason)}\" aria-label=\"${no}호 ${esc(cleaningControl.label)}\" ${cleaningControl.disabled?'disabled':''}>${icon('briefcase')}${esc(cleaningControl.label)}</button>",
    "room card cleaning button",
)

# 7) Filters/counts are independent: the same occupied room can also be cleaning-needed.
replace_once(
    "if(['available','blocked','cleaning','occupied'].includes(state.roomFilter))return p.key===state.roomFilter;",
    "if(state.roomFilter==='occupied')return r.occupancy==='occupied';if(state.roomFilter==='cleaning')return roomNeedsCleaningNow(r.no);if(['available','blocked'].includes(state.roomFilter))return p.key===state.roomFilter;",
    "independent room filters",
)
replace_once(
    "const primaryCounts=ROOMS.reduce((counts,room)=>{const key=roomPresentation(room.no).key;counts[key]=(counts[key]||0)+1;return counts;},{}),typeCounts=ROOMS.reduce((counts,room)=>{counts[room.type]=(counts[room.type]||0)+1;return counts;},{});",
    "const primaryCounts=ROOMS.reduce((counts,room)=>{const p=roomPresentation(room.no);if(room.occupancy==='occupied')counts.occupied++;if(roomNeedsCleaningNow(room.no))counts.cleaning++;if(p.key==='available')counts.available++;if(p.key==='blocked')counts.blocked++;return counts;},{occupied:0,cleaning:0,available:0,blocked:0}),typeCounts=ROOMS.reduce((counts,room)=>{counts[room.type]=(counts[room.type]||0)+1;return counts;},{});",
    "independent room status counts",
)
replace_once("aria-label=\"현재 객실 네 가지 주 상태 요약\"", "aria-label=\"현재 객실 상태 요약\"", "summary aria copy")
replace_once("총 ${ROOMS.length}개 객실 · 주 상태 4개", "총 ${ROOMS.length}개 객실 · 상태 중복 집계", "summary overlap copy")
replace_once("<optgroup label=\"주 상태\">", "<optgroup label=\"상태 조건 · 중복 가능\">", "filter overlap copy")

# 8) Room detail displays cleaning as a subordinate state without duplicating occupied.
replace_once(
    "${statusBadge(p.status,p.tone)}${occupied?statusBadge('투숙 중','neutral'):''}",
    "${statusBadge(p.status,p.tone)}${p.cleaning&&p.key!=='cleaning'?statusBadge(`청소 필요 · ${p.cleaningKind||'청소'}`,'amber'):''}",
    "room detail subordinate cleaning badge",
)

# 9) Ensure special/hold room details also receive one shared cleaning panel.
old_wrapper = """      function renderRoomDetail(no) {
        const room=ROOMS.find(item=>item.no===no);
        if(roomIsOnHold(no))return mergeRoomBasicsPanel(renderCatalogRoomDetail(no),no);
        if(no==='332'&&['active','resolved'].includes(state.conflict)) {
          return mergeRoomBasicsPanel(mergeRoomIssuesPanel(mergeRoomOperationPanel(renderRoomConflict332(),no),no),no);
        }
        return mergeRoomBasicsPanel(mergeRoomIssuesPanel(mergeRoomOperationPanel(renderRoomDetailStandard(no),no),no),no);
      }"""
new_wrapper = """      function renderRoomCleaningFallbackPanel(no) {
        return `<section class=\"card card-pad\"><div class=\"section-head\"><h3>청소 작업</h3>${statusBadge(statusLabel(state.jobs[no]),roomNeedsCleaningNow(no)?'amber':'neutral')}</div>${renderManualCleaningToggle(no)}</section>`;
      }
      function mergeRoomCleaningPanel(html,no) {
        if(html.includes(`data-room-cleaning-panel=\"${no}\"`))return html;
        const marker='<div class=\"detail-stack\">',index=html.indexOf(marker);
        return index<0?html:html.slice(0,index+marker.length)+renderRoomCleaningFallbackPanel(no)+html.slice(index+marker.length);
      }
      function renderRoomDetail(no) {
        const room=ROOMS.find(item=>item.no===no);
        if(roomIsOnHold(no))return mergeRoomBasicsPanel(mergeRoomCleaningPanel(renderCatalogRoomDetail(no),no),no);
        if(no==='332'&&['active','resolved'].includes(state.conflict)) {
          return mergeRoomBasicsPanel(mergeRoomCleaningPanel(mergeRoomIssuesPanel(mergeRoomOperationPanel(renderRoomConflict332(),no),no),no),no);
        }
        return mergeRoomBasicsPanel(mergeRoomCleaningPanel(mergeRoomIssuesPanel(mergeRoomOperationPanel(renderRoomDetailStandard(no),no),no),no);
      }"""
replace_once(old_wrapper, new_wrapper, "all room details cleaning panel")

# 10) Request/cancel confirmation modal and result copy.
old_modal_line = """          const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:`${no}호 청소 필요를 ${request?'OFF':'ON'}로 바꿀까요?`,subtitle:`${kind} · 객실 상세 상태 변경`,trigger:el,body:request?'<div class=\"notice notice-warning\"><div><strong>아직 미배정·미공개·미착수인 요청만 해제됩니다.</strong><br>객실의 청소 필요 표시와 관리자 배정 대상에서 함께 제거되며 기록은 보존됩니다.</div></div>':'<div class=\"notice notice-info\"><div><strong>청소 필요 표시와 미배정 청소 작업을 함께 만듭니다.</strong><br>투숙 중이면 연박 청소, 공실이면 추가 청소로 등록되어 관리자 배정 화면에서 담당을 정할 수 있습니다.</div></div>',confirmLabel:request?'청소 필요 OFF':'청소 필요 ON',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action=\"${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}\"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;"""
new_modal_line = """          const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:request?`${no}호 청소 요청을 취소할까요?`:`${no}호 청소를 요청할까요?`,subtitle:request?`${kind} · 대기열에서 취소`:`${kind} · 청소 대기열 등록`,trigger:el,body:request?'<div class=\"notice notice-warning\"><div><strong>청소 대기열에서 요청을 취소합니다.</strong><br>아직 미배정·미공개·미착수인 요청만 취소되며, 이미 시작된 작업은 청소 상세에서 확인해야 합니다.</div></div>':'<div class=\"notice notice-info\"><div><strong>확인하면 청소 대기열에 작업 1건을 등록합니다.</strong><br>투숙 중 객실은 연박 청소, 공실 객실은 추가 청소로 등록되며 담당은 관리자 배정 화면에서 정합니다.</div></div>',confirmLabel:request?'청소 취소':'청소 대기열에 넣기',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action=\"${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}\"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;"""
replace_once(old_modal_line, new_modal_line, "request cancel confirmation modal")
replace_once("toast(`${no}호 ${result.request.kind}를 청소 필요 ON으로 등록했습니다.`);", "toast(`${no}호 ${result.request.kind}를 청소 대기열에 넣었습니다.`);", "request result toast")
replace_once("toast(`${no}호 ${result.request.kind}를 청소 필요 OFF로 변경했습니다.`);", "toast(`${no}호 ${result.request.kind} 요청을 취소했습니다.`);", "cancel result toast")

# 11) Expose the shared controls to browser QA without changing durable state.
replace_once(
    "manualCleaningCandidates:()=>ROOMS.filter(room=>!roomIsOnHold(room.no)&&!state.roomStopped[room.no]&&!activeUnfinishedAttempt(room.no)&&!currentSubmission(room.no)&&!roomNeedsCleaningNow(room.no)).map(room=>({room:room.no,occupancy:room.occupancy,type:room.type})),\n          manualCleaningState:roomNo=>{const no=String(roomNo),request=activeManualCleaningRequest(no),target=manualCleaningRequestTarget(request),assignment=request?state.assignments?.[request.targetId]:null;return {room:no,request:request?{...request}:null,target:target?{...target}:null,assignment:assignment?{...assignment}:null,presentation:roomPresentation(no),filtered:filteredRooms().some(room=>room.no===no),manualTargetCount:(state.manualAssignmentTargets||[]).filter(item=>item.id===request?.targetId&&!item.cancelled).length};},",
    "manualCleaningCandidates:()=>ROOMS.filter(room=>!roomIsOnHold(room.no)&&!state.roomStopped[room.no)&&!activeUnfinishedAttempt(room.no)&&!(currentSubmission(room.no)&&currentSubmission(room.no).status!=='approved')&&!roomHasCleaningWorkflow(room.no)).map(room=>({room:room.no,occupancy:room.occupancy,type:room.type})),\n          roomCleaningControls:()=>ROOMS.map(room=>({room:room.no,...roomCleaningControl(room.no)})),\n          manualCleaningState:roomNo=>{const no=String(roomNo),request=activeManualCleaningRequest(no),target=manualCleaningRequestTarget(request),assignment=request?state.assignments?.[request.targetId]:null;return {room:no,request:request?{...request}:null,target:target?{...target}:null,assignment:assignment?{...assignment}:null,control:roomCleaningControl(no),presentation:roomPresentation(no),filtered:filteredRooms().some(room=>room.no===no),manualTargetCount:(state.manualAssignmentTargets||[]).filter(item=>item.id===request?.targetId&&!item.cancelled).length};},",
    "cleaning control test API",
)

# The previous replacement intentionally contains a syntax-sensitive filter; normalize it here.
replace_once(
    "!state.roomStopped[room.no)&&",
    "!state.roomStopped[room.no]&&",
    "test API bracket normalization",
)

# Final static contracts.
if source == original:
    raise SystemExit("patch produced no changes")
for forbidden in ["ON으로 변경", "OFF로 변경", "청소 필요 ON", "청소 필요 OFF"]:
    if forbidden in source:
        raise SystemExit(f"forbidden user-facing copy remains: {forbidden}")
for required in [
    "청소 대기열에 넣기",
    "data-room-cleaning-control",
    "data-room-cleaning-panel",
    "function roomCleaningControl(no)",
    "if(state.roomFilter==='occupied')return r.occupancy==='occupied'",
    "if(state.roomFilter==='cleaning')return roomNeedsCleaningNow(r.no)",
    "청소 필요 · ${p.cleaningKind||'청소'}",
]:
    if required not in source:
        raise SystemExit(f"required contract missing: {required}")
occupied_branch = source.index("if(room.occupancy==='occupied')return {key:'occupied'", source.index("function roomPresentation(no)"))
cleaning_branch = source.index("if(cleaning)return {key:'cleaning'", source.index("function roomPresentation(no)"))
if occupied_branch > cleaning_branch:
    raise SystemExit("occupied branch must precede generic cleaning branch")
if source.count("data-room-cleaning-control") < 2:
    raise SystemExit("card and detail cleaning controls were not both installed")

path.write_text(source, encoding="utf-8")
print(f"updated {path}: {len(original)} -> {len(source)} chars")
