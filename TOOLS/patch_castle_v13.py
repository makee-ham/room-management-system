from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / 'HISTORY' / 'castle_the_art_room_manager_wireframe_v12.html'
out = ROOT / 'CURRENT' / 'castle_the_art_room_manager_wireframe_v13.html'
text = src.read_text(encoding='utf-8')


def rep(old, new, label, count=1):
    global text
    n = text.count(old)
    if n < count:
        raise RuntimeError(f'{label}: found {n}, expected >= {count}')
    text = text.replace(old, new, count)


def sub(pattern, repl, label, count=1, flags=re.S):
    global text
    text2, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n != count:
        raise RuntimeError(f'{label}: replacements={n}, expected={count}')
    text = text2

# Version and sidebar explanation.
rep('모바일 와이어프레임 v12</title>', '모바일 와이어프레임 v13</title>', 'title')
rep('모바일 와이어프레임 v12</h1>', '모바일 와이어프레임 v13</h1>', 'sidebar version')
rep(
    '객실 운영 중지·예약·입실·청소의 모순을 차단하고, 중요한 변경은 영향 범위를 검토한 뒤 최종 확정하도록 강화한 Codex 이관용 프로토타입입니다.',
    '객실 운영·예약·청소·촛불 상태의 충돌을 차단하고, 촛불 전량 회수 전에는 고객 배정과 입실을 잠그며 중요한 변경은 영향 확인 후 확정하도록 강화한 인수인계용 프로토타입입니다.',
    'sidebar copy'
)
rep(
    '날짜 선택 → 객실 운영 조회 → 운영 중지·예약 충돌 검사 → 고객 배정·입실 → 청소 담당 배정 → 사진 검수 → 주급·벌점 처리 → 변경 이력 보존.',
    '날짜 선택 → 객실 운영 조회 → 운영 중지·예약·촛불 충돌 검사 → 고객 배정·입실 → 청소 담당 배정 → 사진 검수 → 촛불 회수 확인 → 주급·벌점 처리 → 변경 이력 보존.',
    'sidebar flow'
)

# Demo data copy: candles are a hard guest-allocation block until an admin records physical retrieval.
rep(
    "notes:'객실 냄새 제거용 촛불 2개가 있습니다. 입실 즉시 위치를 확인해 주세요.'",
    "notes:'객실 냄새 제거용 촛불 2개가 있습니다. 관리자 전량 회수 완료 처리 전까지 고객 배정·입실이 잠깁니다.'",
    '1502 note'
)
rep(
    "notes:'냉장고 내부와 주방 수납장 전체 확인. 주방 창가에 촛불 1개가 있습니다.'",
    "notes:'냉장고 내부와 주방 수납장 전체 확인. 주방 창가 촛불 1개는 관리자 회수 완료 전 고객 입실이 잠깁니다.'",
    '1004 note'
)
rep(
    "notes:'냄새 원인 확인을 위해 객실 운영을 중지했습니다. 고객 배정과 메이드 청소를 모두 진행하지 않습니다. 촛불 3개 현황만 기록합니다.'",
    "notes:'냄새 원인 확인을 위해 객실 운영을 중지했습니다. 고객 배정과 메이드 청소를 모두 진행하지 않으며, 촛불 3개도 전량 회수되어야 향후 고객 배정 조건을 충족할 수 있습니다.'",
    '608 note'
)
rep(
    "notes:'현관 거울 얼룩 재확인. 현관 선반 촛불 1개 있음.'",
    "notes:'현관 거울 얼룩 재확인. 현관 선반 촛불 1개는 관리자 회수 전 고객 배정·입실 차단.'",
    '108 note'
)

# Candle is a hard guest block and reservation-conflict source.
rep(
    "    const hardGuestBlock = (room) => isOutOfService(room) || !!room.entryBlockIssue;\n    const reservationConflict = (room) => !!room.reservationAssigned && hardGuestBlock(room);",
    "    const candleBlocksGuest = (room) => Number(room.candleCount || 0) > 0;\n    const candleBlockReason = (room) => candleBlocksGuest(room) ? `촛불 ${room.candleCount}개 · 관리자 전량 회수 완료 처리 필요` : '';\n    const hardGuestBlockReasons = (room) => [isOutOfService(room) ? `운영 중지 · ${operationReason(room)}` : '', room.entryBlockIssue ? `입실 차단 특이사항 · ${room.entryBlockIssue}` : '', candleBlockReason(room)].filter(Boolean);\n    const hardGuestBlock = (room) => hardGuestBlockReasons(room).length > 0;\n    const reservationConflict = (room) => !!room.reservationAssigned && hardGuestBlock(room);",
    'hard guest block helpers'
)

# Replace guest allocation rule/reason/headline/action/buckets with candle-aware logic.
sub(
    r"    const guestAllocationState = \(room\) => \{.*?    const timingBadges = \(room\) =>",
    r'''    const guestAllocationState = (room) => {
      if (reservationConflict(room)) return 'conflict';
      if (isOutOfService(room)) return 'unavailable';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return 'unavailable';
      if (room.reservationAssigned) return 'assigned';
      if (room.entryBlockIssue) return 'unavailable';
      if (candleBlocksGuest(room)) return 'unavailable';
      if (room.cleaningStatus !== '입실 준비 완료') return 'unavailable';
      return 'available';
    };
    const guestAllocationReason = (room) => {
      if (reservationConflict(room)) {
        return `예약 충돌 · ${room.reservationLabel || '기존 예약'} 배정 중 · ${hardGuestBlockReasons(room).join(' · ')} · 입실 전 차단 원인 해결, 다른 객실 이동 또는 배정 해제 필요`;
      }
      if (isOutOfService(room)) return `운영 중지 · 고객 배정과 청소 모두 차단 · ${operationReason(room)}`;
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return `${room.stayStatus} · 현재 고객이 객실 사용 중`;
      if (room.reservationAssigned) return `${room.reservationLabel || '기존 예약'}에 배정 완료 · 신규 고객 배정 불가`;
      if (room.entryBlockIssue) return `고객 배정 차단 특이사항 · ${room.entryBlockIssue}`;
      if (candleBlocksGuest(room)) return `${candleBlockReason(room)} · 촛불이 0개가 되어야 고객 배정 가능`;
      if (room.cleaningStatus !== '입실 준비 완료') return `${room.cleaningStatus} · 청소 및 검수 완료 전`;
      return '청소·검수 완료 · 촛불 0개 · 고객 배정 차단 특이사항 없음 · 미배정 객실';
    };
    const guestAllocationBadge = (room) => {
      const status = guestAllocationState(room);
      if (status === 'available') return '<span class="guest-allocation-badge available">고객 배정 가능</span>';
      if (status === 'assigned') return '<span class="guest-allocation-badge assigned">예약 배정 완료</span>';
      if (status === 'conflict') return '<span class="guest-allocation-badge conflict">예약 충돌</span>';
      return '<span class="guest-allocation-badge unavailable">고객 배정 불가</span>';
    };
    const guestAllocationHeadline = (room) => {
      const status = guestAllocationState(room);
      if (status === 'available') return '고객에게 배정 가능';
      if (status === 'assigned') return '예약 배정 완료 · 신규 배정 불가';
      if (status === 'conflict') return candleBlocksGuest(room) ? '예약 충돌 · 촛불 회수 전 입실 불가' : '예약 충돌 · 입실 전 조치 필요';
      if (candleBlocksGuest(room)) return '촛불 회수 전 고객 배정 불가';
      return '고객에게 배정 불가';
    };
    const guestAllocationActionLabel = (room) => {
      if (reservationConflict(room)) return candleBlocksGuest(room) ? '촛불 회수·충돌 해결' : '예약 충돌 해결';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return '입·퇴실 상태 관리';
      if (room.reservationAssigned) return '예약 변경·해제';
      if (guestAllocationState(room) === 'available') return '고객에게 배정';
      if (isOutOfService(room)) return '운영 중지 확인';
      if (candleBlocksGuest(room)) return '촛불 회수 처리';
      return '배정 불가 사유';
    };
    const guestUnavailable = (room) => guestAllocationState(room) !== 'available';
    const needsCleaning = (room) => !isOutOfService(room) && !room.cleaningSuppressed && ['입실 대기','청소 가능','청소 중','연박 청소','재청소 필요'].includes(room.cleaningStatus);
    const cleaningKind = (room) => String(room.task || '').includes('연박') ? 'stayover' : room.task === '재청소' || room.cleaningStatus === '재청소 필요' ? 'reclean' : 'checkout';
    const unavailableBucket = (room) => {
      if (reservationConflict(room)) return 'conflict';
      if (isOutOfService(room)) return 'out-of-service';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return 'occupied';
      if (candleBlocksGuest(room)) return 'candle';
      if (room.entryBlockIssue) return 'issue';
      if (room.cleaningStatus !== '입실 준비 완료') return 'cleaning';
      if (room.reservationAssigned) return 'reserved';
      return 'other';
    };
    const timingBadges = (room) =>''',
    'guest allocation candle logic'
)

# Dashboard group and copy.
rep(
    "        const issue = rooms.filter(r => unavailableBucket(r) === 'issue');\n        const cleaning = rooms.filter(r => unavailableBucket(r) === 'cleaning');",
    "        const candle = rooms.filter(r => unavailableBucket(r) === 'candle');\n        const issue = rooms.filter(r => unavailableBucket(r) === 'issue');\n        const cleaning = rooms.filter(r => unavailableBucket(r) === 'cleaning');",
    'unavailable candle group var'
)
rep(
    "        listMarkup = `${group('예약 충돌 · 즉시 조치', conflicts)}${group('운영 중지 · 청소 제외', stopped)}${group('청소·검수 필요', cleaning)}${group('고객 입실 중', occupied)}${group('고객 배정 차단 특이사항', issue)}${group('기존 예약 배정 완료', reserved)}`;",
    "        listMarkup = `${group('예약 충돌 · 즉시 조치', conflicts)}${group('운영 중지 · 청소 제외', stopped)}${group('청소·검수 필요', cleaning)}${group('고객 입실 중', occupied)}${group('촛불 회수 필요', candle)}${group('고객 배정 차단 특이사항', issue)}${group('기존 예약 배정 완료', reserved)}`;",
    'unavailable candle group markup'
)
rep(
    '<span>청소·검수 완료, 차단 특이사항 없음</span>',
    '<span>청소·검수 완료, 촛불 0개, 차단 특이사항 없음</span>',
    'available card copy'
)
rep(
    '<span>청소·검수, 차단 특이사항, 입실·예약</span>',
    '<span>청소·검수, 촛불, 차단 특이사항, 입실·예약</span>',
    'unavailable card copy'
)
rep(
    '<span>객실 보유 현황만 표시 · 배정 판정과 무관</span>',
    '<span>전량 회수 전 고객 배정·입실 불가</span>',
    'candle card copy'
)
rep(
    "${conflictRooms.map(room => `${room.id}호 ${room.reservationLabel || '예약'} · ${isOutOfService(room) ? operationReason(room) : room.entryBlockIssue}`).join('<br>')}",
    "${conflictRooms.map(room => `${room.id}호 ${room.reservationLabel || '예약'} · ${hardGuestBlockReasons(room).join(' · ')}`).join('<br>')}",
    'conflict alert detail'
)

# Room detail and candle copy.
rep('현재 예약과 운영 상태가 충돌합니다', '현재 예약과 객실 차단 상태가 충돌합니다', 'detail conflict title')
rep('>예약 이동·해제</button>', '>충돌 해결</button>', 'detail conflict button')
rep(
    "${room.candleCount > 0 ? `${room.candleCount}개 · 배정 판정과 무관` : '없음'}",
    "${room.candleCount > 0 ? `${room.candleCount}개 · 전량 회수 전 배정·입실 불가` : '없음 · 촛불 조건 충족'}",
    'detail candle allocation copy'
)
rep(
    '고객 객실 배정은 청소 담당 배정과 별개입니다. 예약 배정 완료·투숙 중인 객실은 신규 고객에게 자동으로 배정 불가가 되며, 관리자가 예약 해제 또는 퇴실 처리하면 조건을 다시 계산합니다.',
    '고객 객실 배정은 청소 담당 배정과 별개입니다. 촛불이 1개 이상이면 신규 배정과 입실이 잠기며, 관리자가 실제 전량 회수 후 촛불 수량을 0개로 확정하면 다른 조건과 함께 다시 계산합니다.',
    'guest action hint candle'
)
old_candle_panel = '''          <div class="panel"><div class="panel-header"><div><div class="panel-title">촛불 현황</div><div class="panel-subtitle">관리자 또는 메이드가 객실에 두고 나온 개수</div></div></div><div class="panel-body">
            <div class="candle-control"><div class="candle-title">${icon('candle')}<div><strong>${room.candleCount > 0 ? `촛불 ${room.candleCount}개 있음` : '촛불 없음'}</strong><span>${room.candleLocations || '위치 정보 없음'}</span></div></div>${!isHistoricalView() ? `<div class="stepper"><button data-action="candle-minus" data-id="${room.id}" aria-label="촛불 수량 줄이기">−</button><strong>${room.candleCount}</strong><button data-action="candle-plus" data-id="${room.id}" aria-label="촛불 수량 늘리기">+</button></div>` : ''}</div>
            <div class="callout gold" style="margin-top:9px;">촛불은 냄새가 나는 객실에 두고 나온 현황을 기록합니다. 메이드의 회수 의무 항목이 아니며, 촛불이 있어도 다른 조건이 충족되면 고객 배정 가능합니다.</div>
          </div></div>'''
new_candle_panel = '''          <div class="panel"><div class="panel-header"><div><div class="panel-title">촛불 현황</div><div class="panel-subtitle">메이드는 청소 후 둔 수량을 기록하고, 관리자는 실제 회수 후 상태를 확정</div></div>${!isHistoricalView() ? `<button class="btn small ${room.candleCount > 0 ? 'red':'soft'}" data-action="open-candle-management" data-id="${room.id}">${room.candleCount > 0 ? '회수·수량 관리':'촛불 기록'}</button>` : ''}</div><div class="panel-body">
            <div class="candle-control"><div class="candle-title">${icon('candle')}<div><strong>${room.candleCount > 0 ? `촛불 ${room.candleCount}개 있음 · 고객 배정 불가` : '촛불 없음 · 고객 배정 조건 충족'}</strong><span>${room.candleLocations || '위치 정보 없음'}</span></div></div><span class="guest-allocation-badge ${room.candleCount > 0 ? 'unavailable':'available'}">${room.candleCount > 0 ? '회수 필요':'0개 확인'}</span></div>
            <div class="callout gold" style="margin-top:9px;">촛불이 1개 이상이면 고객 객실 배정과 입실 처리를 모두 잠급니다. 메이드는 청소 후 둔 개수를 기록하고, 관리자는 현장에서 전량 회수한 뒤 0개로 변경해야 합니다. 수량 변경은 영향 확인 모달과 감사 이력을 남깁니다.</div>
          </div></div>'''
rep(old_candle_panel, new_candle_panel, 'candle panel')

# Maid candle copy and completion warning.
rep(
    '현재 기록상 촛불 ${room.candleCount}개</strong><br>${room.candleLocations || \'위치 정보 없음\'}. 청소 후 객실에 몇 개를 두고 나왔는지 아래에서 최종 수량을 기록해 주세요.',
    '현재 기록상 촛불 ${room.candleCount}개</strong><br>${room.candleLocations || \'위치 정보 없음\'}. 청소 후 객실에 두고 나오는 최종 수량을 기록해 주세요. 1개 이상이면 관리자 전량 회수 전 고객 배정·입실이 잠깁니다.',
    'maid current candle callout'
)
rep(
    '냄새가 나는 객실이라 촛불을 두었다면 개수를 기록합니다. 회수 확인 항목이 아닙니다.',
    '냄새가 나는 객실에 두고 나온 최종 개수를 기록합니다. 메이드의 회수 완료 처리가 아니라 관리자에게 현재 수량을 전달하는 항목입니다.',
    'maid candle record copy'
)

# Inspection approval reflects candle block.
sub(
    r"    function openInspectionApprovalConfirm\(roomId\) \{.*?\n    \}\n\n    function openGuestAllocationSheet",
    r'''    function openInspectionApprovalConfirm(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.pendingAction = { type:'inspection-approval', roomId };
      const allocationAfter = candleBlocksGuest(room) ? `촛불 ${room.candleCount}개 회수 전 고객 배정 불가` : room.entryBlockIssue ? '입실 차단 특이사항 해결 전 고객 배정 불가' : isOutOfService(room) ? '운영 중지로 고객 배정 불가' : '다른 조건에 따라 고객 배정 상태 재계산';
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 검수를 승인할까요?</h3><p>승인하면 청소 주급과 청소 품질만 확정됩니다. 촛불, 입실 차단 특이사항, 운영 중지는 별도 차단 조건으로 그대로 유지됩니다.</p><div class="safety-summary"><div><span>담당 메이드</span><b>${room.assignee || '미지정'}</b></div><div><span>청소 금액</span><b>${room.cleaningFee.toLocaleString()}원</b></div><div><span>촛불</span><b>${room.candleCount > 0 ? `${room.candleCount}개 · 회수 필요` : '0개'}</b></div><div><span>승인 후 고객 배정</span><b>${allocationAfter}</b></div><div><span>차단 특이사항</span><b>${room.entryBlockIssue || '없음'}</b></div><div><span>운영 상태</span><b>${operationLabel(room)}</b></div></div><div class="button-row"><button class="btn" data-action="close-sheet">취소</button><button class="btn green" data-action="confirm-approve-inspection">검수 승인 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openGuestAllocationSheet''',
    'inspection approval candle summary'
)

# Guest allocation sheet: candle conflicts can be resolved by recovery, not only moving reservations.
sub(
    r"      if \(conflict\) \{\n        const transferCount = availableTransferRooms\(room\)\.length;\n        controls = `.*?`;\n      \} else if \(occupied\)",
    r'''      if (conflict) {
        const transferCount = availableTransferRooms(room).length;
        const resolutionButtons = `${candleBlocksGuest(room) ? `<button class="btn green full" style="margin-top:8px;" data-action="open-candle-management" data-id="${room.id}">촛불 전량 회수 처리</button>` : ''}${isOutOfService(room) ? `<button class="btn soft full" style="margin-top:8px;" data-action="open-room-operation" data-id="${room.id}">운영 상태 확인</button>` : ''}${room.entryBlockIssue ? `<button class="btn soft full" style="margin-top:8px;" data-action="open-entry-issue" data-id="${room.id}">차단 특이사항 확인</button>` : ''}`;
        controls = `<div class="conflict-alert"><strong>예약과 객실 상태가 충돌합니다</strong><span>${guestAllocationReason(room)}</span></div><div class="impact-list"><div class="impact-item">입실 처리는 잠김</div><div class="impact-item">촛불 회수·차단 사유 해결 또는 예약 이동·배정 해제로 충돌 해소</div><div class="impact-item">이동 가능한 객실 ${transferCount}개</div></div><div class="button-row"><button class="btn" data-action="confirm-guest-action" data-id="${room.id}" data-guest-action="release">배정 해제</button><button class="btn red" data-action="open-reservation-transfer" data-id="${room.id}" ${transferCount ? '' : 'disabled'}>다른 객실로 이동</button></div>${resolutionButtons}`;
      } else if (occupied)''',
    'guest allocation conflict controls'
)
rep(
    '운영 중지, 청소·검수 미완료 또는 입실 차단 특이사항이 남아 있으면 고객 배정 버튼을 잠급니다. 원인을 해결하면 자동으로 다시 계산합니다.',
    '운영 중지, 청소·검수 미완료, 촛불 1개 이상 또는 입실 차단 특이사항이 남아 있으면 고객 배정 버튼을 잠급니다. 원인을 해결하면 자동으로 다시 계산합니다.',
    'guest allocation unavailable copy'
)
# Add candle manage button in unavailable branch.
rep(
    "${isOutOfService(room) ? `<button class=\"btn red full\" style=\"margin-top:11px;\" data-action=\"open-room-operation\" data-id=\"${room.id}\">운영 상태 관리</button>` : room.entryBlockIssue ? `<button class=\"btn soft full\" style=\"margin-top:11px;\" data-action=\"open-entry-issue\" data-id=\"${room.id}\">입실 차단 특이사항 관리</button>` : ''}<button",
    "${isOutOfService(room) ? `<button class=\"btn red full\" style=\"margin-top:11px;\" data-action=\"open-room-operation\" data-id=\"${room.id}\">운영 상태 관리</button>` : candleBlocksGuest(room) ? `<button class=\"btn green full\" style=\"margin-top:11px;\" data-action=\"open-candle-management\" data-id=\"${room.id}\">촛불 회수·수량 관리</button>` : room.entryBlockIssue ? `<button class=\"btn soft full\" style=\"margin-top:11px;\" data-action=\"open-entry-issue\" data-id=\"${room.id}\">입실 차단 특이사항 관리</button>` : ''}<button",
    'unavailable candle action'
)

# Check-in block reason includes candles.
rep(
    "      if (room.cleaningStatus !== '입실 준비 완료') return `${room.cleaningStatus} · 청소 및 검수 승인 필요`;\n      if (room.entryBlockIssue) return `입실 차단 특이사항 · ${room.entryBlockIssue}`;",
    "      if (room.cleaningStatus !== '입실 준비 완료') return `${room.cleaningStatus} · 청소 및 검수 승인 필요`;\n      if (room.entryBlockIssue) return `입실 차단 특이사항 · ${room.entryBlockIssue}`;\n      if (candleBlocksGuest(room)) return `${candleBlockReason(room)} · 전량 회수 전 입실 불가`;",
    'checkin candle guard'
)

# Entry issue copy no longer says candles are irrelevant.
rep(
    '이 내용이 남아 있는 동안에는 청소가 완료되어도 고객 객실 배정이 불가능합니다. 촛불 유무는 차단 특이사항이 아니며 촛불 현황에서 따로 기록합니다.',
    '이 내용이 남아 있는 동안에는 청소가 완료되어도 고객 객실 배정이 불가능합니다. 촛불도 별도의 하드 차단 조건이며, 촛불 현황 관리에서 전량 회수를 확인해야 합니다.',
    'entry issue candle copy'
)

# Candle management / confirmation functions inserted before inspection approval.
anchor = '    function openInspectionApprovalConfirm(roomId) {'
functions = r'''    function openCandleManagementSheet(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.selectedRoomId = roomId;
      const impact = room.candleCount > 0 ? '현재 고객 배정·입실 차단 중' : '현재 촛불 조건 충족';
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 촛불 현황 관리</h3><p>실제 객실에 있는 촛불 수량을 기록합니다. 1개 이상이면 고객 배정과 입실이 자동으로 잠기며, 0개는 관리자가 현장에서 전량 회수한 뒤에만 확정해야 합니다.</p><div class="safety-summary"><div><span>현재 수량</span><b>${room.candleCount}개</b></div><div><span>현재 영향</span><b>${impact}</b></div><div><span>현재 위치</span><b>${room.candleLocations || '미입력'}</b></div><div><span>현재 예약</span><b>${room.reservationAssigned ? (room.reservationLabel || '예약 있음') : '없음'}</b></div></div><div class="field-row"><div class="field"><label>변경 후 수량</label><input id="candleCountInput" class="input" type="number" inputmode="numeric" min="0" max="20" step="1" value="${room.candleCount}"></div><div class="field"><label>위치</label><input id="candleLocationsInput" class="input" value="${room.candleLocations || ''}" placeholder="예: 거실 창가 1 · 욕실 1"></div></div><div class="field"><label>변경·회수 사유</label><textarea id="candleChangeReason" class="textarea" placeholder="예: 현장에서 촛불 2개 전량 회수 확인"></textarea></div><div class="safety-card"><strong>0개로 변경할 때</strong><span>앱 수치만 낮추지 말고 실제 전량 회수를 확인해야 합니다. 다른 조건도 충족되면 고객 배정 또는 입실 잠금이 해제될 수 있습니다.</span></div><div class="button-row" style="margin-top:13px;"><button class="btn" data-action="close-sheet">취소</button><button class="btn ${room.candleCount > 0 ? 'green':'primary'}" data-action="review-candle-change" data-id="${room.id}">변경 내용 확인</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function reviewCandleChange(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      const raw = document.getElementById('candleCountInput')?.value ?? '';
      const nextCount = Number(raw);
      const locations = (document.getElementById('candleLocationsInput')?.value || '').trim();
      const reason = (document.getElementById('candleChangeReason')?.value || '').trim();
      if (!Number.isInteger(nextCount) || nextCount < 0 || nextCount > 20) { showToast('촛불 수량은 0–20 사이 정수로 입력해 주세요.'); return; }
      if (!reason) { showToast('변경·회수 사유를 입력해 주세요.'); return; }
      if (nextCount > 0 && !locations) { showToast('촛불 위치를 입력해 주세요.'); return; }
      if (nextCount === room.candleCount && locations === (room.candleLocations || '')) { showToast('변경된 내용이 없습니다.'); return; }
      state.pendingAction = { type:'candle-change', roomId, nextCount, locations: nextCount > 0 ? locations : '', reason };
      const beforeState = guestAllocationHeadline(room);
      const previewRoom = { ...room, candleCount:nextCount, candleLocations:nextCount > 0 ? locations : '' };
      const afterState = guestAllocationHeadline(previewRoom);
      const title = nextCount === 0 && room.candleCount > 0 ? `${room.id}호 촛불 전량 회수를 확정할까요?` : `${room.id}호 촛불 수량을 변경할까요?`;
      const impact = nextCount > 0 ? `고객 배정·입실 차단${room.reservationAssigned ? ' · 기존 예약 충돌 표시':''}` : '촛불 차단 해제 · 다른 조건으로 고객 배정 상태 재계산';
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${title}</h3><p>중요한 객실 가용 상태 변경입니다. 실제 현장 수량과 아래 내용을 다시 확인한 뒤 확정하세요.</p><div class="safety-summary"><div><span>촛불 수량</span><b>${room.candleCount}개 → ${nextCount}개</b></div><div><span>객실 위치</span><b>${nextCount > 0 ? locations : '전량 회수 · 없음'}</b></div><div><span>고객 배정 상태</span><b>${beforeState} → ${afterState}</b></div><div><span>변경 영향</span><b>${impact}</b></div><div><span>사유</span><b>${reason}</b></div></div><div class="button-row"><button class="btn" data-action="open-candle-management" data-id="${room.id}">돌아가기</button><button class="btn ${nextCount === 0 ? 'green':'red'}" data-action="confirm-candle-change">${nextCount === 0 ? '전량 회수 확정':'수량 변경 확정'}</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

'''
rep(anchor, functions + anchor, 'insert candle management functions')

# Task completion confirmation warns about guest lock.
sub(
    r"    function openTaskCompleteConfirm\(roomId\) \{.*?\n    \}\n\n    function openClaimJobSheet",
    r'''    function openTaskCompleteConfirm(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      const checks = state.taskChecks[roomId] || [];
      const photos = state.taskPhotos[roomId] || [];
      const candleCount = state.taskCandleCounts[roomId] ?? room.candleCount ?? 0;
      state.pendingAction = { type:'complete-task', roomId };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 청소를 완료 제출할까요?</h3><p>확정하면 검수 대기로 넘어가며 메이드가 직접 제출을 취소할 수 없습니다. 수정이 필요하면 관리자가 재청소로 반려해야 합니다.</p><div class="safety-summary"><div><span>체크리스트</span><b>${checks.length}개 완료</b></div><div><span>인증사진</span><b>${photos.length}장 선택</b></div><div><span>청소 후 촛불</span><b>${candleCount}개</b></div><div><span>고객 배정 영향</span><b>${candleCount > 0 ? '관리자 전량 회수 전 배정·입실 불가':'촛불 조건 충족'}</b></div><div><span>주급</span><b>검수 승인 후 확정</b></div></div>${candleCount > 0 ? `<div class="safety-card"><strong>촛불 회수는 관리자 확인 단계</strong><span>메이드는 청소 후 객실에 둔 수량만 기록합니다. 제출 후 관리자 화면에 ‘촛불 회수 필요’로 표시되고, 전량 회수 전 고객 입실이 잠깁니다.</span></div>` : ''}<div class="button-row" style="margin-top:13px;"><button class="btn" data-action="close-sheet">계속 수정</button><button class="btn green" data-action="confirm-complete-task">검수 요청 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openClaimJobSheet''',
    'task completion candle warning'
)

# Historical mutation action list now uses managed candle actions.
rep("'candle-plus','candle-minus'", "'open-candle-management','review-candle-change','confirm-candle-change'", 'historical candle actions')

# Click handlers: add candle sheet/review/confirm, remove direct mutation semantics.
old_handler = '''      if (action === 'candle-plus' || action === 'candle-minus') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        room.candleCount = Math.max(0, Math.min(9, room.candleCount + (action === 'candle-plus' ? 1 : -1)));
        if (room.candleCount === 0) room.candleLocations = '';
        addDailyEvent(room, '촛불 현황 수정', `${room.candleCount}개로 변경`);
        render();
        showToast(`${id}호 촛불 수량을 ${room.candleCount}개로 변경했습니다.`);
      }'''
new_handler = '''      if (action === 'open-candle-management') { openCandleManagementSheet(id || state.selectedRoomId); return; }
      if (action === 'review-candle-change') { reviewCandleChange(id || state.selectedRoomId); return; }
      if (action === 'confirm-candle-change') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'candle-change') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        const before = room.candleCount || 0;
        room.candleCount = pending.nextCount;
        room.candleLocations = pending.locations;
        addDailyEvent(room, room.candleCount === 0 ? '촛불 전량 회수 완료' : '촛불 현황 변경', `${before}개 → ${room.candleCount}개 · ${pending.reason} · 관리자 확인 모달 승인`);
        state.pendingAction = null;
        closeSheet(); render();
        if (room.candleCount > 0) {
          showToast(room.reservationAssigned ? `${room.id}호 촛불 ${room.candleCount}개 · 기존 예약 입실을 잠갔습니다.` : `${room.id}호 촛불 ${room.candleCount}개 · 고객 배정 불가로 전환했습니다.`);
        } else {
          showToast(guestAllocationState(room) === 'available' ? `${room.id}호 촛불 전량 회수 · 고객 배정 가능으로 전환했습니다.` : room.reservationAssigned && canProcessCheckin(room) ? `${room.id}호 촛불 전량 회수 · 고객 입실 잠금이 해제됐습니다.` : `${room.id}호 촛불 전량 회수 · 다른 객실 조건을 확인해 주세요.`);
        }
        return;
      }'''
rep(old_handler, new_handler, 'candle click handlers')

# Inspection approval toast explains candle block explicitly.
rep(
    "render(); showToast(guestAllocationState(room) === 'available' ? `${id}호 검수 승인 · 고객 배정 가능으로 전환했습니다.` : `${id}호 검수와 주급은 확정했지만 고객 배정 상태는 별도 사유를 확인해 주세요.`);",
    "render(); showToast(guestAllocationState(room) === 'available' ? `${id}호 검수 승인 · 고객 배정 가능으로 전환했습니다.` : candleBlocksGuest(room) ? `${id}호 검수·주급 확정 · 촛불 ${room.candleCount}개 회수 전 고객 배정 불가입니다.` : `${id}호 검수와 주급은 확정했지만 고객 배정 상태는 별도 사유를 확인해 주세요.`);",
    'inspection approval toast'
)

# Completion event copy explicitly says guest lock.
rep(
    "`인증사진 8장 · 청소 후 촛불 ${room.candleCount}개 기록 · 메이드 확인 모달 승인`",
    "`인증사진 8장 · 청소 후 촛불 ${room.candleCount}개 기록${room.candleCount > 0 ? ' · 관리자 전량 회수 전 고객 배정·입실 차단' : ''} · 메이드 확인 모달 승인`",
    'completion event candle block'
)

# Ensure admin rows can open candle management quickly for current-date candle rooms.
rep(
    '<button class="btn small" data-action="edit-password" data-id="${room.id}">${icon(\'edit\')} 비밀번호</button><button class="btn small soft full"',
    '<button class="btn small" data-action="edit-password" data-id="${room.id}">${icon(\'edit\')} 비밀번호</button>${room.candleCount > 0 ? `<button class="btn small red" data-action="open-candle-management" data-id="${room.id}">촛불 회수</button>` : ``}<button class="btn small soft full"',
    'room row candle button'
)

# Final v13 refinements discovered during QA.
rep(
    "        const candle = rooms.filter(r => unavailableBucket(r) === 'candle');",
    "        const candle = rooms.filter(candleBlocksGuest);",
    'unavailable candle group includes overlaps'
)
rep(
    "${group('촛불 회수 필요', candle)}",
    "${group('촛불 회수 필요 · 다른 사유와 중복 표시', candle, `${candle.length}개 · 전량 회수 전 배정·입실 불가`)}",
    'unavailable candle group label'
)
rep(
    "    .toast.show { transform: translate(-50%, 0); opacity: 1; }",
    "    .toast.show { transform: translate(-50%, 0); opacity: 1; }\n    .phone:has(.sheet.open) .toast { top: calc(14px + var(--safe-top)); bottom: auto; transform: translate(-50%, -15px); }\n    .phone:has(.sheet.open) .toast.show { transform: translate(-50%, 0); }",
    'toast does not cover confirmation sheets'
)

# Final visible rule copy: candle count is a hard guest-assignment/check-in block.
rep(
    '<strong>촛불 유무·개수는 현황 기록이며 고객 배정 가능 여부를 막지 않습니다.</strong>',
    '<strong>촛불이 1개라도 있으면 고객 배정과 입실이 차단되며, 관리자가 현장에서 전량 회수한 뒤 0개로 확정해야 차단이 풀립니다.</strong>',
    'dashboard candle hard-block notice'
)

# Write output and latest aliases.
out.write_text(text, encoding='utf-8')
(ROOT / 'CURRENT' / 'castle_the_art_room_manager_wireframe_latest.html').write_text(text, encoding='utf-8')
# Extract inline JS for handoff.
match = re.search(r'<script>\s*(.*?)\s*</script>\s*</body>', text, flags=re.S)
if not match:
    raise RuntimeError('inline script not found')
(ROOT / 'CURRENT' / 'castle_v13_script.js').write_text(match.group(1), encoding='utf-8')
print(f'Wrote {out} ({out.stat().st_size} bytes)')
