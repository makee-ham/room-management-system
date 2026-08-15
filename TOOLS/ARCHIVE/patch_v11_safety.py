from pathlib import Path

paths = [
    Path('/mnt/data/castle_the_art_room_manager_wireframe_v11.html'),
    Path('/mnt/data/castle_the_art_room_manager_wireframe_latest.html'),
]

for path in paths:
    text = path.read_text(encoding='utf-8')

    text = text.replace(
        "<button class=\"btn primary\" data-action=\"save-stay-time\" data-id=\"${room.id}\">시간 저장</button>",
        "<button class=\"btn primary\" data-action=\"review-stay-time\" data-id=\"${room.id}\">변경 내용 확인</button>"
    )
    text = text.replace(
        "<button class=\"btn primary\" data-action=\"save-entry-issue\" data-id=\"${room.id}\">저장</button>",
        "<button class=\"btn primary\" data-action=\"review-entry-issue\" data-id=\"${room.id}\">차단 등록 확인</button>"
    )

    old_hist = "'open-entry-issue','save-entry-issue','resolve-entry-issue','candle-plus','candle-minus','open-stay-time','save-stay-time'"
    new_hist = "'open-entry-issue','review-entry-issue','confirm-save-entry-issue','resolve-entry-issue','confirm-resolve-entry-issue','candle-plus','candle-minus','open-stay-time','review-stay-time','confirm-stay-time'"
    if old_hist not in text:
        raise SystemExit(f'historical action set not found in {path}')
    text = text.replace(old_hist, new_hist)

    text = text.replace("'정상 운영 · 청소 필요 생성'", "'정상 운영 · 점검 청소 생성'")
    text = text.replace("퇴실 청소 작업을 ‘담당 미지정·선택 클로즈’로 생성", "운영 재개 점검 청소를 ‘담당 미지정·선택 클로즈’로 생성")
    text = text.replace("room.cleaningStatus = '청소 가능'; room.task = '퇴실 청소';", "room.cleaningStatus = '청소 가능'; room.task = '운영 재개 점검 청소';", 1)
    text = text.replace("`${pending.reason} · 퇴실 청소 작업 생성 · 담당 미지정`", "`${pending.reason} · 운영 재개 점검 청소 생성 · 담당 미지정`")

    old_stay = '''      if (action === 'save-stay-time') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const early = document.getElementById('earlyCheckinInput')?.value || '';
        const late = document.getElementById('lateCheckoutInput')?.value || '';
        const before = `${room.earlyCheckinTime || '없음'} / ${room.lateCheckoutTime || '없음'}`;
        room.earlyCheckinTime = early;
        room.lateCheckoutTime = late;
        if (early) room.checkin = early;
        else if (room.checkin !== '예약 없음' && room.checkin !== '투숙 중') room.checkin = room.standardCheckinTime || '16:00';
        if (late) room.checkout = late;
        else if (!['-'].includes(room.checkout) && !String(room.checkout).includes('내일') && !String(room.checkout).includes('8월')) room.checkout = room.standardCheckoutTime || '11:00';
        addDailyEvent(room, '입·퇴실 시간 수정', `얼리 ${early || '없음'} · 레이트 ${late || '없음'} (이전 ${before})`);
        closeSheet(); render(); showToast(`${id}호 얼리·레이트 시각을 저장했습니다.`);
      }
'''
    new_stay = '''      if (action === 'review-stay-time') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const early = document.getElementById('earlyCheckinInput')?.value || '';
        const late = document.getElementById('lateCheckoutInput')?.value || '';
        const standardIn = room.standardCheckinTime || DEFAULT_CHECKIN_TIME;
        const standardOut = room.standardCheckoutTime || DEFAULT_CHECKOUT_TIME;
        if (early && early >= standardIn) { showToast(`얼리 체크인은 기본 체크인 ${standardIn}보다 이른 시각이어야 합니다.`); return; }
        if (late && late <= standardOut) { showToast(`레이트 체크아웃은 기본 체크아웃 ${standardOut}보다 늦은 시각이어야 합니다.`); return; }
        if (early === (room.earlyCheckinTime || '') && late === (room.lateCheckoutTime || '')) { showToast('변경된 시간이 없습니다.'); return; }
        state.pendingAction = { type:'stay-time', roomId:id, early, late };
        const cleaningWarning = room.task && room.task !== '작업 없음' ? `<div class="impact-item">청소 가능·마감 시각과 메이드 우선순위를 다시 확인해야 합니다.</div>` : '';
        sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${id}호 입·퇴실 시간을 변경할까요?</h3><p>예약과 청소 순서에 영향을 줄 수 있는 변경입니다. 저장 전 시각을 다시 확인하세요.</p><div class="safety-summary"><div><span>기본 시각</span><b>체크인 ${standardIn} · 체크아웃 ${standardOut}</b></div><div><span>현재 예외 시각</span><b>얼리 ${room.earlyCheckinTime || '없음'} · 레이트 ${room.lateCheckoutTime || '없음'}</b></div><div><span>변경 후</span><b>얼리 ${early || '없음'} · 레이트 ${late || '없음'}</b></div></div><div class="impact-list"><div class="impact-item">관리자 일자별 이력에 변경 전·후 시각이 기록됩니다.</div>${cleaningWarning}</div><div class="button-row"><button class="btn" data-action="open-stay-time" data-id="${id}">돌아가기</button><button class="btn primary" data-action="confirm-stay-time">시간 변경 확정</button></div></div>`;
        sheet.classList.add('open'); sheetBackdrop.classList.add('open'); return;
      }
      if (action === 'confirm-stay-time') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'stay-time') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        const before = `${room.earlyCheckinTime || '없음'} / ${room.lateCheckoutTime || '없음'}`;
        room.earlyCheckinTime = pending.early;
        room.lateCheckoutTime = pending.late;
        if (pending.early) room.checkin = pending.early;
        else if (room.checkin !== '예약 없음' && room.checkin !== '투숙 중') room.checkin = room.standardCheckinTime || DEFAULT_CHECKIN_TIME;
        if (pending.late) room.checkout = pending.late;
        else if (!['-'].includes(room.checkout) && !String(room.checkout).includes('내일') && !String(room.checkout).includes('8월')) room.checkout = room.standardCheckoutTime || DEFAULT_CHECKOUT_TIME;
        addDailyEvent(room, '입·퇴실 시간 수정', `얼리 ${pending.early || '없음'} · 레이트 ${pending.late || '없음'} (이전 ${before}) · 확인 모달 승인`);
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호 얼리·레이트 시각을 변경했습니다.`); return;
      }
'''
    if old_stay not in text:
        raise SystemExit(f'stay handler not found in {path}')
    text = text.replace(old_stay, new_stay)

    old_issue = '''      if (action === 'save-entry-issue') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const value = (document.getElementById('entryIssueInput')?.value || '').trim();
        if (!value) { showToast('입실 차단 사유를 입력해 주세요.'); return; }
        room.entryBlockIssue = value;
        addDailyEvent(room, '고객 배정 차단 특이사항 등록', value);
        closeSheet(); render(); showToast(`${id}호를 고객 배정 불가로 표시했습니다.`);
      }
'''
    new_issue = '''      if (action === 'review-entry-issue') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const value = (document.getElementById('entryIssueInput')?.value || '').trim();
        if (!value) { showToast('입실 차단 사유를 입력해 주세요.'); return; }
        if (value === (room.entryBlockIssue || '')) { showToast('변경된 특이사항이 없습니다.'); return; }
        const conflict = room.reservationAssigned || ['오늘 입실','투숙 중'].includes(room.stayStatus);
        state.pendingAction = { type:'save-entry-issue', roomId:id, value };
        sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${id}호를 고객 배정 불가로 전환할까요?</h3><p>입실 차단 특이사항은 청소 완료 여부와 무관하게 고객 배정을 막습니다.</p><div class="safety-summary"><div><span>차단 사유</span><b>${value}</b></div><div><span>현재 운영</span><b>${operationLabel(room)}</b></div><div><span>현재 예약·투숙</span><b>${room.reservationLabel || room.stayStatus || '없음'}</b></div></div><div class="impact-list"><div class="impact-item">고객 배정 가능 목록에서 즉시 제외됩니다.</div><div class="impact-item">문제가 해결될 때까지 신규 입실 처리가 차단됩니다.</div>${conflict ? `<div class="impact-item danger">현재 예약 또는 투숙 상태와 충돌합니다. 등록 후 예약 이동·배정 해제 또는 현장 조치가 필요합니다.</div>` : ''}</div><div class="button-row"><button class="btn" data-action="open-entry-issue" data-id="${id}">돌아가기</button><button class="btn red" data-action="confirm-save-entry-issue">차단 등록 확정</button></div></div>`;
        sheet.classList.add('open'); sheetBackdrop.classList.add('open'); return;
      }
      if (action === 'confirm-save-entry-issue') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'save-entry-issue') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        const previous = room.entryBlockIssue || '없음';
        room.entryBlockIssue = pending.value;
        addDailyEvent(room, '고객 배정 차단 특이사항 등록', `${pending.value} (이전 ${previous}) · 확인 모달 승인`);
        const conflict = reservationConflict(room) || ['오늘 입실','투숙 중'].includes(room.stayStatus);
        state.pendingAction = null; closeSheet(); render();
        showToast(conflict ? `${room.id}호 차단 등록 완료 · 예약/투숙 충돌을 확인해 주세요.` : `${room.id}호를 고객 배정 불가로 전환했습니다.`); return;
      }
'''
    if old_issue not in text:
        raise SystemExit(f'issue handler not found in {path}')
    text = text.replace(old_issue, new_issue)

    path.write_text(text, encoding='utf-8')
    print('patched', path, len(text))
