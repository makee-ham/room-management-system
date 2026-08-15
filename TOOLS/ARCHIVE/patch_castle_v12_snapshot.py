from pathlib import Path
import re

src = Path('/mnt/data/castle_the_art_room_manager_wireframe_v11_snapshot_0905.html')
out = Path('/mnt/data/castle_the_art_room_manager_wireframe_v12.html')
text = src.read_text(encoding='utf-8')

def must_replace(old, new, label, count=1):
    global text
    n = text.count(old)
    if n < count:
        raise RuntimeError(f'{label}: expected {count}, found {n}')
    text = text.replace(old, new, count)

def replace_block(start_marker, end_marker, new_block, label):
    global text
    a = text.find(start_marker)
    if a < 0: raise RuntimeError(f'{label}: start not found')
    b = text.find(end_marker, a)
    if b < 0: raise RuntimeError(f'{label}: end not found')
    text = text[:a] + new_block + text[b:]

# Version and navigation copy.
must_replace('모바일 와이어프레임 v11</title>', '모바일 와이어프레임 v12</title>', 'title')
must_replace('모바일 와이어프레임 v10</h1>', '모바일 와이어프레임 v12</h1>', 'sidebar version')
must_replace('객실 운영 안전장치에 더해 관리자가 메이드 벌점을 부여·삭제·복구하고, 메이드는 사유와 연결 객실을 확인할 수 있도록 확장한 구조입니다.',
             '객실 운영 중지·예약·입실·청소의 모순을 차단하고, 중요한 변경은 영향 범위를 검토한 뒤 최종 확정하도록 강화한 Codex 이관용 프로토타입입니다.', 'sidebar copy')
must_replace('<button class="preview-btn" data-demo-view="guest-allocation">고객 객실 배정</button>',
             '<button class="preview-btn" data-demo-view="guest-allocation">고객 객실 배정</button>\n          <button class="preview-btn" data-demo-view="room-operation">608호 운영 중지</button>', 'operation quick link')
must_replace('날짜 선택 → 객실 운영 조회 → 청소 담당 배정·변경 → 인증사진 검수 → 주급 지급·취소 → 벌점 부여·삭제·복구 → 메이드 통지와 일자별 이력 보존.',
             '날짜 선택 → 객실 운영 조회 → 운영 중지·예약 충돌 검사 → 고객 배정·입실 → 청소 담당 배정 → 사진 검수 → 주급·벌점 처리 → 변경 이력 보존.', 'flow copy')

# Coherent 608 state: an out-of-service room has no arrival, guest assignment, or cleaning work.
must_replace("{ id:'608', type:'스탠다드', stayStatus:'공실', stayTone:'gray', cleaningStatus:'청소 제외'",
             "{ id:'608', type:'스탠다드', stayStatus:'운영 중지', stayTone:'gray', cleaningStatus:'작업 없음'", '608 status')
must_replace("'608':  { reservationAssigned:false, reservationLabel:'', entryBlockIssue:'냄새 원인 확인 전 고객 배정 보류' },",
             "'608':  { reservationAssigned:false, reservationLabel:'', entryBlockIssue:'' },", '608 allocation seed')

# Check-in guard functions.
anchor = "    function availableTransferRooms(sourceRoom) {\n"
helpers = """    const checkinBlockReason = (room) => {
      if (isOutOfService(room)) return `객실 운영 중지 · ${operationReason(room)}`;
      if (!room.reservationAssigned) return '고객 예약이 배정되지 않음';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return '이미 고객이 입실한 객실';
      if (room.cleaningStatus !== '입실 준비 완료') return `${room.cleaningStatus} · 청소 및 검수 승인 필요`;
      if (room.entryBlockIssue) return `입실 차단 특이사항 · ${room.entryBlockIssue}`;
      return '';
    };
    const canProcessCheckin = (room) => !checkinBlockReason(room);

"""
must_replace(anchor, helpers + anchor, 'checkin helper')

# Operation stop/resume semantics.
must_replace("room.cleaningStatus = '청소 제외'; room.task = '작업 없음'; room.color = 'gray';", "room.cleaningStatus = '작업 없음'; room.task = '작업 없음'; room.color = 'gray';", 'operation stop cleaning')
must_replace("if (!room.reservationAssigned) { room.stayStatus = '공실'; room.stayTone = 'gray'; room.checkin = '예약 없음'; }",
             "if (!room.reservationAssigned) { room.stayStatus = '운영 중지'; room.stayTone = 'gray'; room.checkin = '예약 없음'; room.checkout = '-'; }", 'operation stop stay')
# Current file already uses operation re-open inspection task; keep it.

# Show check-in only when room is actually ready; otherwise show the blocker.
old_assigned = "${assigned ? `<div class=\"button-row\" style=\"margin-top:13px;\"><button class=\"btn\" data-action=\"confirm-guest-action\" data-id=\"${room.id}\" data-guest-action=\"release\">배정 해제</button><button class=\"btn primary\" data-action=\"save-guest-assignment\" data-id=\"${room.id}\">배정 정보 확인</button></div><button class=\"btn green full\" style=\"margin-top:8px;\" data-action=\"confirm-guest-action\" data-id=\"${room.id}\" data-guest-action=\"checkin\">고객 입실 처리</button>`"
new_assigned = "${assigned ? `<div class=\"button-row\" style=\"margin-top:13px;\"><button class=\"btn\" data-action=\"confirm-guest-action\" data-id=\"${room.id}\" data-guest-action=\"release\">배정 해제</button><button class=\"btn primary\" data-action=\"save-guest-assignment\" data-id=\"${room.id}\">배정 정보 확인</button></div>${canProcessCheckin(room) ? `<button class=\"btn green full\" style=\"margin-top:8px;\" data-action=\"confirm-guest-action\" data-id=\"${room.id}\" data-guest-action=\"checkin\">고객 입실 처리</button>` : `<div class=\"conflict-alert\" style=\"margin-top:8px;\"><strong>입실 처리 잠김</strong><span>${checkinBlockReason(room)}</span></div><button class=\"btn full\" style=\"margin-top:8px;\" disabled>입실 처리 불가</button>`}`"
must_replace(old_assigned, new_assigned, 'checkin UI guard')

# Guard the modal and final execution too.
must_replace("      const labels = {\n", "      if (actionType === 'checkin' && !canProcessCheckin(room)) { showToast(`입실 처리 불가 · ${checkinBlockReason(room)}`); return; }\n      const labels = {\n", 'checkin modal guard')
must_replace("        if (!room) return;\n        if (pending.actionType === 'release') {",
             "        if (!room) return;\n        if (pending.actionType === 'checkin' && !canProcessCheckin(room)) { state.pendingAction = null; closeSheet(); render(); showToast(`입실 처리 불가 · ${checkinBlockReason(room)}`); return; }\n        if (pending.actionType === 'release') {", 'checkin execute guard')

# Safety modal helpers.
func_anchor = "    function openMaidSheet(maidId = null) {\n"
funcs = r'''    function openClaimVisibilityConfirm(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room || room.assignee || !canOpenForClaim(room)) { showToast('현재 선택 공개를 변경할 수 없는 객실입니다.'); return; }
      const open = !room.openForClaim;
      state.pendingAction = { type:'claim-visibility', roomId, open };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 일감을 ${open ? '오픈':'클로즈'}할까요?</h3><p>${open ? '메이드가 금액과 시간을 보고 직접 선택할 수 있게 됩니다.' : '메이드 일감 찾기 목록에서 즉시 숨겨집니다.'}</p><div class="safety-summary"><div><span>현재</span><b>${room.openForClaim ? '선택 오픈':'선택 클로즈'}</b></div><div><span>변경 후</span><b>${open ? '선택 오픈':'선택 클로즈'}</b></div><div><span>일감</span><b>${room.task} · ${room.cleaningFee.toLocaleString()}원</b></div></div><div class="button-row"><button class="btn" data-action="close-sheet">취소</button><button class="btn ${open ? 'green':'red'}" data-action="confirm-claim-visibility">${open ? '오픈':'클로즈'} 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openInspectionRejectFinalConfirm(roomId, index, reason, detail) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      const photo = inspectionPhotosFor(room)[index];
      state.pendingAction = { type:'inspection-reject', roomId, index, reason, detail };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 검수를 반려할까요?</h3><p>확정하면 객실은 ‘재청소 필요’로 바뀌고 담당 메이드에게 사진·사유와 함께 즉시 알림이 갑니다.</p><div class="safety-summary"><div><span>대상 사진</span><b>${photo?.label || '인증사진'}</b></div><div><span>반려 사유</span><b>${reason} · ${detail}</b></div><div><span>담당</span><b>${room.assignee || '미지정'}</b></div><div><span>주급</span><b>검수 전 · 미확정</b></div></div><div class="button-row"><button class="btn" data-action="confirm-reject-inspection" data-id="${room.id}">돌아가기</button><button class="btn red" data-action="confirm-submit-reject-inspection">검수 반려 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openTaskStartConfirm(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room || isOutOfService(room) || room.assignee !== '김하나') { showToast('현재 시작할 수 없는 작업입니다.'); return; }
      state.pendingAction = { type:'task-start', roomId };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 청소를 시작할까요?</h3><p>시작 시각이 기록되고 상태가 ‘청소 중’으로 변경됩니다.</p><div class="safety-summary"><div><span>유형</span><b>${room.task}</b></div><div><span>완료 마감</span><b>${room.deadline}</b></div><div><span>취소</span><b>관리자에게 담당 회수 요청</b></div></div><div class="button-row"><button class="btn" data-action="close-sheet">취소</button><button class="btn green" data-action="confirm-start-task">청소 시작 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openRestoreMaidConfirm(maidId) {
      const maid = state.maids.find(m => m.id === maidId && m.status === 'retired');
      if (!maid) return;
      state.pendingAction = { type:'restore-maid', maidId };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${maid.name}님의 퇴사 처리를 취소할까요?</h3><p>복구 후 바로 활동 계정이 되지 않고 ‘비활성’ 상태가 됩니다. 정보 확인 후 별도로 활성화해야 합니다.</p><div class="safety-summary"><div><span>현재</span><b>퇴사 처리</b></div><div><span>복구 후</span><b>비활성 · 로그인 불가</b></div><div><span>과거 이력</span><b>그대로 보존</b></div></div><div class="button-row"><button class="btn" data-action="close-sheet">취소</button><button class="btn green" data-action="confirm-restore-maid">퇴사 취소 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openMaidSaveConfirm(payload) {
      const existing = payload.id ? state.maids.find(m => m.id === payload.id) : null;
      state.pendingAction = { type:'maid-save', ...payload };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">메이드 계정을 ${existing ? '수정':'추가'}할까요?</h3><p>로그인 권한과 담당 이력 연결에 영향을 주는 변경입니다.</p><div class="safety-summary"><div><span>이름</span><b>${existing ? `${existing.name} → ${payload.name}` : payload.name}</b></div><div><span>로그인 ID</span><b>${payload.loginId}</b></div><div><span>초기 상태</span><b>${existing ? maidStatusLabel(existing.status) : '활동 중'}</b></div></div><div class="button-row"><button class="btn" data-action="${existing ? 'edit-maid':'add-maid'}" data-id="${payload.id || ''}">돌아가기</button><button class="btn green" data-action="confirm-save-maid">${existing ? '정보 수정':'계정 추가'} 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openHistoryCorrectionConfirm(payload) {
      const room = state.rooms.find(r => r.id === payload.roomId);
      if (!room) return;
      state.pendingAction = { type:'history-correction', ...payload };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${payload.roomId}호 과거 기록 정정을 추가할까요?</h3><p>원본 기록은 바꾸지 않고 정정 이벤트를 별도로 남깁니다.</p><div class="safety-summary"><div><span>대상 일자</span><b>${formatSelectedDate()}</b></div><div><span>정정 항목</span><b>${payload.category}</b></div><div><span>정정 내용</span><b>${payload.content}</b></div><div><span>사유</span><b>${payload.reason}</b></div></div><div class="button-row"><button class="btn" data-action="history-correction">돌아가기</button><button class="btn primary" data-action="confirm-history-correction">정정 이력 추가 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

'''
must_replace(func_anchor, funcs + func_anchor, 'safety helper functions')

# Button labels now make the review step explicit.
must_replace('data-action="submit-history-correction">정정 이력 추가</button>', 'data-action="submit-history-correction">정정 내용 확인</button>', 'history button')
must_replace('${maid ? \'수정 저장\' : \'계정 추가\'}</button>', '${maid ? \'수정 내용 확인\' : \'계정 추가 확인\'}</button>', 'maid save button')
must_replace('data-action="submit-reject-inspection" data-id="${room.id}" data-index="${index}">재청소 요청</button>', 'data-action="submit-reject-inspection" data-id="${room.id}" data-index="${index}">재청소 요청 내용 확인</button>', 'reject button')

# History correction review/final.
replace_block("      if (action === 'submit-history-correction') {", "      const historicalMutationActions = new Set(", """      if (action === 'submit-history-correction') {
        const roomId = document.getElementById('correctionRoom')?.value;
        const category = document.getElementById('correctionCategory')?.value || '기타';
        const content = (document.getElementById('correctionContent')?.value || '').trim();
        const reason = (document.getElementById('correctionReason')?.value || '').trim();
        const room = state.rooms.find(r => r.id === roomId);
        if (!room || !content || !reason) { showToast('정정할 내용과 사유를 모두 입력해 주세요.'); return; }
        openHistoryCorrectionConfirm({ roomId, category, content, reason }); return;
      }
      if (action === 'confirm-history-correction') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'history-correction') return;
        const room = state.rooms.find(r => r.id === pending.roomId); if (!room) return;
        addDailyEvent(room, `기록 정정 · ${pending.category}`, `${pending.content} · 정정 사유: ${pending.reason} · 관리자 확인 모달 승인`, '정정');
        persistDateSnapshot(); state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호에 정정 이력을 추가했습니다.`); return;
      }
""", 'history correction handler')

# Maid add/edit review/final.
replace_block("      if (action === 'save-maid') {", "      if (action === 'toggle-maid-status') {", """      if (action === 'save-maid') {
        const name = (document.getElementById('maidName')?.value || '').trim();
        const loginId = (document.getElementById('maidLoginId')?.value || '').trim();
        const phone = (document.getElementById('maidPhone')?.value || '').trim();
        const note = (document.getElementById('maidNote')?.value || '').trim();
        if (!name || !loginId) { showToast('이름과 로그인 아이디를 입력해 주세요.'); return; }
        const duplicate = state.maids.some(m => m.loginId === loginId && m.id !== id);
        if (duplicate) { showToast('이미 사용 중인 로그인 아이디입니다.'); return; }
        openMaidSaveConfirm({ id:id || '', name, loginId, phone:phone || '미등록', note:note || '메모 없음' }); return;
      }
      if (action === 'confirm-save-maid') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'maid-save') return;
        if (pending.id) {
          const maid = state.maids.find(m => m.id === pending.id); if (!maid) return;
          const oldName = maid.name;
          Object.assign(maid, { name:pending.name, loginId:pending.loginId, phone:pending.phone, note:pending.note });
          state.rooms.forEach(room => { if (room.assignee === oldName) room.assignee = pending.name; });
          state.pendingAction = null; closeSheet(); render(); showToast(`${pending.name}님의 정보를 수정했습니다.`); return;
        }
        const numbers = state.maids.map(m => Number(m.id.replace(/\D/g,''))).filter(Number.isFinite);
        const nextNumber = numbers.length ? Math.max(...numbers) + 1 : 1;
        const newId = `maid${String(nextNumber).padStart(2,'0')}`;
        state.maids.push({ id:newId, name:pending.name, phone:pending.phone, loginId:pending.loginId, status:'active', joined:'2026.08.14', weeklyConfirmed:0, weeklyExpected:0, weeklyPaid:0, completed:0, approval:'-', note:pending.note });
        state.pendingAction = null; closeSheet(); render(); showToast(`${pending.name} 메이드 계정을 추가했습니다.`); return;
      }
""", 'maid save handler')

# Retired account restore requires a final confirmation.
replace_block("      if (action === 'restore-maid') {", "      if (action === 'toggle-weekly-payment')", """      if (action === 'restore-maid') { openRestoreMaidConfirm(id); return; }
      if (action === 'confirm-restore-maid') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'restore-maid') return;
        const maid = state.maids.find(m => m.id === pending.maidId && m.status === 'retired'); if (!maid) return;
        maid.status = 'inactive'; maid.note = `퇴사 취소 ${maid.retiredAt || ''} · 재활성화 전 정보 확인 필요`; maid.retiredAt = ''; maid.retiredReason = '';
        state.pendingAction = null; closeSheet(); render(); showToast(`${maid.name} 계정을 비활성 상태로 복구했습니다.`); return;
      }
""", 'maid restore handler')

# Individual open/close requires confirmation.
replace_block("      if (action === 'toggle-open') {", "      if (action === 'open-all' || action === 'close-all')", """      if (action === 'toggle-open') { openClaimVisibilityConfirm(id); return; }
      if (action === 'confirm-claim-visibility') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'claim-visibility') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room || room.assignee || !canOpenForClaim(room)) { state.pendingAction = null; closeSheet(); render(); showToast('객실 상태가 바뀌어 공개 설정을 변경할 수 없습니다.'); return; }
        room.openForClaim = pending.open;
        addDailyEvent(room, '메이드 선택 공개 변경', `일감을 ${pending.open ? '오픈':'클로즈'}로 변경 · 관리자 확인 모달 승인`);
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호를 메이드 선택 ${pending.open ? '오픈':'클로즈'}했습니다.`); return;
      }
""", 'claim visibility handler')

# Inspection rejection requires a second final confirmation.
replace_block("      if (action === 'submit-reject-inspection') {", "      if (action === 'switch-to-maid')", """      if (action === 'submit-reject-inspection') {
        const room = state.rooms.find(r => r.id === id); if (!room) return;
        const index = Number(actionEl.dataset.index);
        const reason = document.getElementById('rejectReason')?.value || '청소 미흡';
        const detail = (document.getElementById('rejectDetail')?.value || '').trim();
        if (!detail) { showToast('메이드에게 전달할 상세 사유를 입력해 주세요.'); return; }
        openInspectionRejectFinalConfirm(id, index, reason, detail); return;
      }
      if (action === 'confirm-submit-reject-inspection') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'inspection-reject') return;
        const room = state.rooms.find(r => r.id === pending.roomId); if (!room) return;
        const photos = inspectionPhotosFor(room);
        room.cleaningStatus = '재청소 필요'; room.color = 'red'; room.inspection = true;
        room.rejectedPhotoLabel = photos[pending.index]?.label || '인증사진';
        room.rejectionReason = `${pending.reason} · ${pending.detail}`; room.rejectedAt = '13:15'; room.maidUnreadRejection = true;
        state.taskStarted[room.id] = false; state.taskChecks[room.id] = []; state.taskPhotos[room.id] = []; state.taskNotes[room.id] = `검수 반려: ${room.rejectionReason}`;
        addDailyEvent(room, '검수 반려·재청소 요청', `${room.rejectedPhotoLabel} · ${room.rejectionReason} · 메이드 앱 알림 발송 · 관리자 확인 모달 승인`, '13:15');
        state.pendingAction = null; closeSheet(); state.screen = 'admin-inspection'; state.previousScreen = null; render(); showToast(`${room.id}호에 재청소를 요청하고 메이드에게 알렸습니다.`); return;
      }
""", 'inspection reject handler')

# Maid task start confirmation.
replace_block("      if (action === 'start-task') {", "      if (action === 'toggle-check')", """      if (action === 'start-task') { openTaskStartConfirm(id); return; }
      if (action === 'confirm-start-task') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'task-start') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room || isOutOfService(room) || room.assignee !== '김하나') { state.pendingAction = null; closeSheet(); render(); showToast('작업 상태가 바뀌어 시작할 수 없습니다.'); return; }
        state.taskStarted[room.id] = true;
        if (state.taskCandleCounts[room.id] == null) state.taskCandleCounts[room.id] = room.candleCount || 0;
        room.cleaningStatus = '청소 중'; room.color = 'orange';
        addDailyEvent(room, '청소 시작', `${room.assignee} · ${room.task} · 메이드 확인 모달 승인`);
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호 청소를 시작했습니다.`); return;
      }
""", 'task start handler')

# Update read-only action guard with newly added confirmation actions.
must_replace("'confirm-toggle-maid-status','confirm-complete-task'",
             "'confirm-toggle-maid-status','confirm-complete-task','confirm-claim-visibility','confirm-submit-reject-inspection','confirm-start-task','confirm-restore-maid','confirm-save-maid','confirm-history-correction'", 'historical action guard')

out.write_text(text, encoding='utf-8')
Path('/mnt/data/castle_the_art_room_manager_wireframe_latest.html').write_text(text, encoding='utf-8')
print(f'wrote {out} ({len(text)} chars)')
