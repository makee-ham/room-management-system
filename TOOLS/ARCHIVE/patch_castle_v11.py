from pathlib import Path

src = Path('/mnt/data/castle_the_art_room_manager_wireframe_v10.html')
out = Path('/mnt/data/castle_the_art_room_manager_wireframe_v11.html')
text = src.read_text(encoding='utf-8')

def rep(old, new, count=1, label=''):
    global text
    found = text.count(old)
    if found < count:
        raise SystemExit(f'REPLACE FAILED {label or old[:80]!r}: found {found}, need {count}')
    text = text.replace(old, new, count)

rep('<title>Castle The Art 객실관리 — 모바일 와이어프레임 v10</title>', '<title>Castle The Art 객실관리 — 모바일 와이어프레임 v11</title>', label='title')

# CSS: operational state and reservation conflict visuals
css_anchor = """    .guest-allocation-badge.unavailable { color: var(--red); background: #f7dfe1; }\n"""
css_add = css_anchor + """
    .guest-allocation-band.conflict { border-color: #e8b7ba; background: #fff0f1; box-shadow: inset 3px 0 0 var(--red); }
    .guest-allocation-badge.conflict { color: #9f2f35; background: #f6d8da; }
    .operation-band { display:flex; align-items:flex-start; justify-content:space-between; gap:9px; margin-top:9px; padding:10px 11px; border:1px solid var(--line); border-radius:12px; background:var(--surface-2); }
    .operation-band strong { display:block; font-size:10.5px; }
    .operation-band span { display:block; margin-top:3px; color:var(--muted); font-size:8.5px; line-height:1.45; }
    .operation-band.stopped { border-color:#e7c5c7; background:var(--red-soft); }
    .operation-band.stopped strong { color:var(--red); }
    .operation-badge { display:inline-flex; flex:0 0 auto; align-items:center; min-height:25px; padding:0 8px; border-radius:8px; font-size:8.5px; font-weight:900; white-space:nowrap; color:var(--green); background:#dff2e9; }
    .operation-badge.stopped { color:var(--red); background:#f7dfe1; }
    .conflict-alert { margin-top:10px; padding:11px 12px; border:1px solid #e4b8bb; border-radius:13px; background:var(--red-soft); }
    .conflict-alert strong { display:block; color:#9f2f35; font-size:10.5px; }
    .conflict-alert span { display:block; margin-top:4px; color:#6e4d50; font-size:8.7px; line-height:1.5; }
    .conflict-alert .btn { margin-top:9px; }
    .impact-list { display:grid; gap:7px; margin:11px 0; }
    .impact-item { padding:9px 10px; border:1px solid var(--line); border-radius:10px; background:var(--surface-2); font-size:9px; line-height:1.45; }
    .impact-item strong { color:var(--ink); }
"""
rep(css_anchor, css_add, label='css')

# Replace 608 with a consistent out-of-service/no-cleaning seed.
old_608 = """      { id:'608', type:'스탠다드', stayStatus:'오늘 입실', stayTone:'blue', cleaningStatus:'청소 가능', color:'orange', available:'11:00', deadline:'14:10', checkin:'16:00', checkout:'11:00', password:'7284', candleCount:3, candleLocations:'거실 2 · 욕실 1', assignmentEnabled:false, assignmentBlockReason:'냄새 원인 확인 전 관리자 배정 보류', assignmentHistory:[{at:'10:58',from:'배정 가능',to:'배정 불가',by:'관리자',reason:'냄새 원인 확인 전 보류'}], openForClaim:false, assignee:'', cleaningFee:7000, task:'퇴실 청소', canEnter:true, inspection:false, badges:['촛불 있음'], notes:'냄새 제거용 촛불 3개가 있습니다. 거실 2개, 욕실 1개 위치 확인.' },"""
new_608 = """      { id:'608', type:'스탠다드', stayStatus:'공실', stayTone:'gray', cleaningStatus:'청소 제외', color:'gray', available:'-', deadline:'-', checkin:'예약 없음', checkout:'-', password:'7284', candleCount:3, candleLocations:'거실 2 · 욕실 1', operationalStatus:'out-of-service', operationalReason:'냄새 원인 확인 전 객실 운영 중지', cleaningSuppressed:true, assignmentEnabled:false, assignmentBlockReason:'운영 중지 객실은 청소 담당 배정 불가', assignmentHistory:[{at:'10:58',from:'배정 가능',to:'운영 중지 · 청소 제외',by:'관리자',reason:'냄새 원인 확인 전 운영 중지'}], openForClaim:false, assignee:'', cleaningFee:7000, task:'작업 없음', canEnter:false, inspection:false, badges:['운영 중지','촛불 있음'], notes:'냄새 원인 확인을 위해 객실 운영을 중지했습니다. 고객 배정과 메이드 청소를 모두 진행하지 않습니다. 촛불 3개 현황만 기록합니다.' },"""
rep(old_608, new_608, label='608 room')
rep("'608':  { reservationAssigned:true, reservationLabel:'YN-260814-063', entryBlockIssue:'냄새 원인 확인 전 고객 배정 보류' },", "'608':  { reservationAssigned:false, reservationLabel:'', entryBlockIssue:'냄새 원인 확인 전 고객 배정 보류' },", label='608 reservation')
rep("""      '608': [
        { time:'10:58', title:'입실 차단 특이사항', detail:'냄새 원인 확인 전 고객 배정 보류' },
        { time:'11:14', title:'촛불 현황 기록', detail:'거실 2개·욕실 1개, 총 3개 기록' }
      ]""", """      '608': [
        { time:'10:58', title:'객실 운영 중지', detail:'냄새 원인 확인 전 고객 배정·청소 모두 중지' },
        { time:'11:00', title:'예약 충돌 확인 완료', detail:'오늘 입실 예약 없음 · 고객 배정 미등록 확인' },
        { time:'11:14', title:'촛불 현황 기록', detail:'거실 2개·욕실 1개, 총 3개 기록' }
      ]""", label='608 events')

# Operational defaults after schedule seeding.
old_loop = """    defaultRooms.forEach(room => {
      Object.assign(room, {
        earlyCheckinTime:'', lateCheckoutTime:'', standardCheckinTime:'16:00', standardCheckoutTime:'11:00',
        dailyEvents: JSON.parse(JSON.stringify(dailyEventSeed[room.id] || []))
      }, scheduleSeed[room.id] || {});
    });
"""
new_loop = """    defaultRooms.forEach(room => {
      Object.assign(room, {
        earlyCheckinTime:'', lateCheckoutTime:'', standardCheckinTime:'16:00', standardCheckoutTime:'11:00',
        dailyEvents: JSON.parse(JSON.stringify(dailyEventSeed[room.id] || []))
      }, scheduleSeed[room.id] || {});
      room.operationalStatus = room.operationalStatus || 'active';
      room.operationalReason = room.operationalReason || '';
      room.cleaningSuppressed = !!room.cleaningSuppressed;
    });
"""
rep(old_loop, new_loop, label='operational defaults')

# Historical 608 snapshots must reflect historical active operation.
rep("'608': { stayStatus:'공실', stayTone:'gray', cleaningStatus:'입실 준비 완료', color:'green', reservationAssigned:false, entryBlockIssue:'', candleCount:2, candleLocations:'거실 2', assignee:'박미정', dailyEvents:", "'608': { stayStatus:'공실', stayTone:'gray', cleaningStatus:'입실 준비 완료', color:'green', operationalStatus:'active', operationalReason:'', cleaningSuppressed:false, reservationAssigned:false, entryBlockIssue:'', candleCount:2, candleLocations:'거실 2', assignee:'박미정', dailyEvents:", label='day13 608')
rep("'608': { stayStatus:'공실', stayTone:'gray', cleaningStatus:'입실 준비 완료', color:'green', reservationAssigned:false, entryBlockIssue:'', candleCount:0, assignee:'김하나', dailyEvents:", "'608': { stayStatus:'공실', stayTone:'gray', cleaningStatus:'입실 준비 완료', color:'green', operationalStatus:'active', operationalReason:'', cleaningSuppressed:false, reservationAssigned:false, entryBlockIssue:'', candleCount:0, assignee:'김하나', dailyEvents:", label='day12 608')

# Empty-day snapshots include operational fields.
rep("reservationAssigned:false, reservationLabel:'', entryBlockIssue:'', inspection:false, dailyEvents:", "reservationAssigned:false, reservationLabel:'', entryBlockIssue:'', operationalStatus:'active', operationalReason:'', cleaningSuppressed:false, inspection:false, dailyEvents:", label='empty snapshot operation')

# Helper/state rules.
old_rules = """    const claimEligible = (room) => ['청소 가능','입실 대기','연박 청소','재청소 필요'].includes(room.cleaningStatus);
    const assignmentLifecycleEligible = (room) => ['청소 가능','입실 대기','연박 청소','청소 중','재청소 필요'].includes(room.cleaningStatus);
"""
new_rules = """    const isOutOfService = (room) => room.operationalStatus === 'out-of-service';
    const operationLabel = (room) => isOutOfService(room) ? '운영 중지 · 청소 제외' : '정상 운영';
    const operationReason = (room) => isOutOfService(room) ? (room.operationalReason || '관리자 운영 중지') : '고객 배정·청소 작업을 상태에 따라 운영';
    const roomHasReservationOrGuest = (room) => !!room.reservationAssigned || ['오늘 입실','입실 예정','투숙 중','장기투숙'].includes(room.stayStatus);
    const hardGuestBlock = (room) => isOutOfService(room) || !!room.entryBlockIssue;
    const reservationConflict = (room) => !!room.reservationAssigned && hardGuestBlock(room);
    const claimEligible = (room) => !isOutOfService(room) && !room.cleaningSuppressed && ['청소 가능','입실 대기','연박 청소','재청소 필요'].includes(room.cleaningStatus);
    const assignmentLifecycleEligible = (room) => !isOutOfService(room) && !room.cleaningSuppressed && ['청소 가능','입실 대기','연박 청소','청소 중','재청소 필요'].includes(room.cleaningStatus);
"""
rep(old_rules, new_rules, label='eligibility helpers')

# Assignment reason for out-of-service.
rep("""    const assignmentReason = (room) => {
      if (!assignmentLifecycleEligible(room)) {
""", """    const assignmentReason = (room) => {
      if (isOutOfService(room) || room.cleaningSuppressed) return `운영 중지 · 청소 작업 제외 · ${operationReason(room)}`;
      if (!assignmentLifecycleEligible(room)) {
""", label='assignment reason')

# Guest allocation functions block.
old_guest = """    const guestAllocationState = (room) => {
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return 'unavailable';
      if (room.reservationAssigned) return 'assigned';
      if (room.entryBlockIssue) return 'unavailable';
      if (room.cleaningStatus !== '입실 준비 완료') return 'unavailable';
      return 'available';
    };
    const guestAllocationReason = (room) => {
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return `${room.stayStatus} · 현재 고객이 객실 사용 중`;
      if (room.reservationAssigned) {
        const blockers = [room.cleaningStatus !== '입실 준비 완료' ? room.cleaningStatus : '', room.entryBlockIssue ? '입실 차단 특이사항 있음' : ''].filter(Boolean);
        return `${room.reservationLabel || '기존 예약'}에 배정 완료 · 신규 고객 배정 불가${blockers.length ? ` · ${blockers.join(' · ')}` : ''}`;
      }
      if (room.entryBlockIssue) return `고객 배정 차단 특이사항 · ${room.entryBlockIssue}`;
      if (room.cleaningStatus !== '입실 준비 완료') return `${room.cleaningStatus} · 청소 및 검수 완료 전`;
      return '청소·검수 완료 · 고객 배정 차단 특이사항 없음 · 미배정 객실';
    };
    const guestAllocationBadge = (room) => {
      const status = guestAllocationState(room);
      if (status === 'available') return '<span class="guest-allocation-badge available">고객 배정 가능</span>';
      if (status === 'assigned') return '<span class="guest-allocation-badge assigned">예약 배정 완료</span>';
      return '<span class="guest-allocation-badge unavailable">고객 배정 불가</span>';
    };
    const guestAllocationHeadline = (room) => {
      const status = guestAllocationState(room);
      if (status === 'available') return '고객에게 배정 가능';
      if (status === 'assigned') return '예약 배정 완료 · 신규 배정 불가';
      return '고객에게 배정 불가';
    };
    const guestAllocationActionLabel = (room) => {
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return '입·퇴실 상태 관리';
      if (room.reservationAssigned) return '예약 변경·해제';
      if (guestAllocationState(room) === 'available') return '고객에게 배정';
      return '배정 불가 사유';
    };
    const guestUnavailable = (room) => guestAllocationState(room) !== 'available';
    const needsCleaning = (room) => ['입실 대기','청소 가능','청소 중','연박 청소','재청소 필요'].includes(room.cleaningStatus);
    const cleaningKind = (room) => room.task.includes('연박') ? 'stayover' : room.task === '재청소' || room.cleaningStatus === '재청소 필요' ? 'reclean' : 'checkout';
    const unavailableBucket = (room) => {
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return 'occupied';
      if (room.entryBlockIssue) return 'issue';
      if (room.cleaningStatus !== '입실 준비 완료') return 'cleaning';
      if (room.reservationAssigned) return 'reserved';
      return 'other';
    };
"""
new_guest = """    const guestAllocationState = (room) => {
      if (reservationConflict(room)) return 'conflict';
      if (isOutOfService(room)) return 'unavailable';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return 'unavailable';
      if (room.reservationAssigned) return 'assigned';
      if (room.entryBlockIssue) return 'unavailable';
      if (room.cleaningStatus !== '입실 준비 완료') return 'unavailable';
      return 'available';
    };
    const guestAllocationReason = (room) => {
      if (reservationConflict(room)) {
        const blocker = isOutOfService(room) ? operationReason(room) : room.entryBlockIssue;
        return `예약 충돌 · ${room.reservationLabel || '기존 예약'} 배정 중 · ${blocker} · 입실 전 다른 객실 이동 또는 배정 해제 필요`;
      }
      if (isOutOfService(room)) return `운영 중지 · 고객 배정과 청소 모두 차단 · ${operationReason(room)}`;
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return `${room.stayStatus} · 현재 고객이 객실 사용 중`;
      if (room.reservationAssigned) return `${room.reservationLabel || '기존 예약'}에 배정 완료 · 신규 고객 배정 불가`;
      if (room.entryBlockIssue) return `고객 배정 차단 특이사항 · ${room.entryBlockIssue}`;
      if (room.cleaningStatus !== '입실 준비 완료') return `${room.cleaningStatus} · 청소 및 검수 완료 전`;
      return '청소·검수 완료 · 고객 배정 차단 특이사항 없음 · 미배정 객실';
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
      if (status === 'conflict') return '예약 충돌 · 입실 전 조치 필요';
      return '고객에게 배정 불가';
    };
    const guestAllocationActionLabel = (room) => {
      if (reservationConflict(room)) return '예약 충돌 해결';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return '입·퇴실 상태 관리';
      if (room.reservationAssigned) return '예약 변경·해제';
      if (guestAllocationState(room) === 'available') return '고객에게 배정';
      if (isOutOfService(room)) return '운영 중지 확인';
      return '배정 불가 사유';
    };
    const guestUnavailable = (room) => guestAllocationState(room) !== 'available';
    const needsCleaning = (room) => !isOutOfService(room) && !room.cleaningSuppressed && ['입실 대기','청소 가능','청소 중','연박 청소','재청소 필요'].includes(room.cleaningStatus);
    const cleaningKind = (room) => String(room.task || '').includes('연박') ? 'stayover' : room.task === '재청소' || room.cleaningStatus === '재청소 필요' ? 'reclean' : 'checkout';
    const unavailableBucket = (room) => {
      if (reservationConflict(room)) return 'conflict';
      if (isOutOfService(room)) return 'out-of-service';
      if (['투숙 중','장기투숙'].includes(room.stayStatus)) return 'occupied';
      if (room.entryBlockIssue) return 'issue';
      if (room.cleaningStatus !== '입실 준비 완료') return 'cleaning';
      if (room.reservationAssigned) return 'reserved';
      return 'other';
    };
"""
rep(old_guest, new_guest, label='guest allocation rules')

# Schedule summary handles out-of-service.
rep("const scheduleSummary = (room) => `<span>퇴실 <b>${room.checkout}</b></span><span class=\"schedule-arrow\">→</span><span>입실 <b>${room.checkin}</b></span>${timingBadges(room)}`;", "const scheduleSummary = (room) => isOutOfService(room) ? `<span><b>운영 중지</b></span><span class=\"schedule-arrow\">·</span><span>청소 제외 · 예약 없음</span>` : `<span>퇴실 <b>${room.checkout}</b></span><span class=\"schedule-arrow\">→</span><span>입실 <b>${room.checkin}</b></span>${timingBadges(room)}`;", label='schedule summary')

# Search includes operation data.
rep("room.entryBlockIssue || '', room.earlyCheckinTime", "room.entryBlockIssue || '', room.operationalReason || '', room.operationalStatus || '', reservationConflict(room) ? '예약 충돌' : '', room.earlyCheckinTime", label='search operation')

# Filters for conflicts/out-of-service.
rep("""        if (state.roomFilter === 'candle') return room.candleCount > 0;
        return true;
""", """        if (state.roomFilter === 'candle') return room.candleCount > 0;
        if (state.roomFilter === 'reservation-conflict') return reservationConflict(room);
        if (state.roomFilter === 'out-of-service') return isOutOfService(room);
        return true;
""", label='room filters')

# Room row: operation status indicator after schedule.
rep("""        <div class="room-schedule">${scheduleSummary(room)}</div>
        <div class="guest-allocation-band ${guestState}">
""", """        <div class="room-schedule">${scheduleSummary(room)}</div>
        ${(isOutOfService(room) || reservationConflict(room)) ? `<div class="operation-band ${isOutOfService(room) ? 'stopped':''}"><div><strong>${isOutOfService(room) ? operationLabel(room) : '예약 충돌 감지'}</strong><span>${isOutOfService(room) ? operationReason(room) : guestAllocationReason(room)}</span></div><span class="operation-badge ${isOutOfService(room) ? 'stopped':''}">${isOutOfService(room) ? '운영 중지':'즉시 조치'}</span></div>` : ''}
        <div class="guest-allocation-band ${guestState}">
""", label='row operation band')

# Room task line for out-of-service.
rep("""<strong>${cleaningNeeded ? room.task : room.cleaningStatus === '검수 대기' ? '청소 완료 · 검수 대기' : '현재 청소 작업 없음'}</strong><span>${cleaningNeeded ? `${room.available}부터 · ${room.deadline} 마감` : room.cleaningStatus}</span>""", """<strong>${isOutOfService(room) ? '운영 중지 · 청소 제외' : cleaningNeeded ? room.task : room.cleaningStatus === '검수 대기' ? '청소 완료 · 검수 대기' : '현재 청소 작업 없음'}</strong><span>${isOutOfService(room) ? operationReason(room) : cleaningNeeded ? `${room.available}부터 · ${room.deadline} 마감` : room.cleaningStatus}</span>""", label='task line')

# Add operation status button to row controls.
old_controls = """<button class="btn small ${guestAllocationState(room) === 'available' ? 'green' : 'soft'}" data-action="open-guest-allocation" data-id="${room.id}">${guestAllocationActionLabel(room)}</button><button class="btn small ${aState === 'assigned' ? 'soft' : ''}" data-action="open-assignment" data-id="${room.id}">${cleaningNeeded ? (aState === 'assigned' ? '담당 변경·회수' : aState === 'available' ? '청소 담당 배정' : '청소 배정 정보') : '배정 이력'}</button><button class="btn small" data-action="edit-password" data-id="${room.id}">${icon('edit')} 비밀번호</button><button class="btn small soft" data-action="go-admin-room" data-id="${room.id}">전체 상세</button>"""
new_controls = """<button class="btn small ${guestAllocationState(room) === 'available' ? 'green' : reservationConflict(room) ? 'red' : 'soft'}" data-action="open-guest-allocation" data-id="${room.id}">${guestAllocationActionLabel(room)}</button><button class="btn small ${isOutOfService(room) ? 'red':'soft'}" data-action="open-room-operation" data-id="${room.id}">운영 상태</button><button class="btn small ${aState === 'assigned' ? 'soft' : ''}" data-action="open-assignment" data-id="${room.id}">${cleaningNeeded ? (aState === 'assigned' ? '담당 변경·회수' : aState === 'available' ? '청소 담당 배정' : '청소 배정 정보') : '배정 이력'}</button><button class="btn small" data-action="edit-password" data-id="${room.id}">${icon('edit')} 비밀번호</button><button class="btn small soft full" style="grid-column:1/-1;" data-action="go-admin-room" data-id="${room.id}">전체 상세</button>"""
rep(old_controls, new_controls, label='row controls')

# Admin room overview counts/groups/alerts.
rep("""      const candleRooms = state.rooms.filter(r => r.candleCount > 0);
""", """      const candleRooms = state.rooms.filter(r => r.candleCount > 0);
      const conflictRooms = state.rooms.filter(reservationConflict);
      const stoppedRooms = state.rooms.filter(isOutOfService);
""", label='overview counts')
rep("""        const occupied = rooms.filter(r => unavailableBucket(r) === 'occupied');
        const issue = rooms.filter(r => unavailableBucket(r) === 'issue');
        const cleaning = rooms.filter(r => unavailableBucket(r) === 'cleaning');
        const reserved = rooms.filter(r => unavailableBucket(r) === 'reserved');
        listMarkup = `${group('청소·검수 필요', cleaning)}${group('고객 입실 중', occupied)}${group('고객 배정 차단 특이사항', issue)}${group('기존 예약 배정 완료', reserved)}`;
""", """        const conflicts = rooms.filter(r => unavailableBucket(r) === 'conflict');
        const stopped = rooms.filter(r => unavailableBucket(r) === 'out-of-service');
        const occupied = rooms.filter(r => unavailableBucket(r) === 'occupied');
        const issue = rooms.filter(r => unavailableBucket(r) === 'issue');
        const cleaning = rooms.filter(r => unavailableBucket(r) === 'cleaning');
        const reserved = rooms.filter(r => unavailableBucket(r) === 'reserved');
        listMarkup = `${group('예약 충돌 · 즉시 조치', conflicts)}${group('운영 중지 · 청소 제외', stopped)}${group('청소·검수 필요', cleaning)}${group('고객 입실 중', occupied)}${group('고객 배정 차단 특이사항', issue)}${group('기존 예약 배정 완료', reserved)}`;
""", label='unavailable groups')
rep("""      } else {
        const title = state.roomFilter === 'guest-available' ? '고객에게 배정 가능한 객실' : state.roomFilter === 'candle' ? '촛불이 있는 객실' : '선택 일자 전체 객실';
""", """      } else {
        const title = state.roomFilter === 'guest-available' ? '고객에게 배정 가능한 객실' : state.roomFilter === 'candle' ? '촛불이 있는 객실' : state.roomFilter === 'reservation-conflict' ? '예약 충돌 객실' : state.roomFilter === 'out-of-service' ? '운영 중지 객실' : '선택 일자 전체 객실';
""", label='list titles')
rep("""          <div class="search-wrap"><span class="search-icon">${icon('search')}</span><input id="roomSearch" class="input" placeholder="객실·유형·상태·메이드·시간 검색" value="${state.roomSearch}" /></div>
""", """          ${conflictRooms.length ? `<div class="conflict-alert"><strong>예약 충돌 ${conflictRooms.length}건 · 입실 전 조치 필요</strong><span>${conflictRooms.map(room => `${room.id}호 ${room.reservationLabel || '예약'} · ${isOutOfService(room) ? operationReason(room) : room.entryBlockIssue}`).join('<br>')}</span><button class="btn red small full" data-action="view-reservation-conflicts">예약 충돌만 보기</button></div>` : ''}
          <div class="search-wrap"><span class="search-icon">${icon('search')}</span><input id="roomSearch" class="input" placeholder="객실·유형·상태·메이드·시간 검색" value="${state.roomSearch}" /></div>
""", label='conflict alert')
rep("""<button class="chip ${state.roomFilter === 'candle' ? 'active':''}" data-room-filter="candle">촛불 있음</button></div>""", """<button class="chip ${state.roomFilter === 'candle' ? 'active':''}" data-room-filter="candle">촛불 있음</button><button class="chip ${state.roomFilter === 'reservation-conflict' ? 'active':''}" data-room-filter="reservation-conflict">예약 충돌 ${conflictRooms.length}</button><button class="chip ${state.roomFilter === 'out-of-service' ? 'active':''}" data-room-filter="out-of-service">운영 중지 ${stoppedRooms.length}</button></div>""", label='extra filter chips')

# Admin room detail: operation panel and badges.
rep("""<div class="detail-statuses">${stayChip(room)}${cleaningChip(room)}${assignmentBadge(room)}""", """<div class="detail-statuses">${stayChip(room)}${cleaningChip(room)}${isOutOfService(room) ? `<span class="status-chip tone-red">운영 중지</span>`:''}${assignmentBadge(room)}""", label='detail operation badge')
operation_panel_anchor = """
          <div class="panel"><div class="panel-header"><div><div class="panel-title">고객 객실 배정 상태</div><div class="panel-subtitle">고객에게 배정하면 신규 배정 불가로 잠기며, 관리자가 변경·해제·입실·퇴실 처리</div></div>${!isHistoricalView() ? `<button class="btn small ${guestAllocationState(room) === 'available' ? 'green':'soft'}" data-action="open-guest-allocation" data-id="${room.id}">${guestAllocationActionLabel(room)}</button>` : ''}</div><div class="panel-body">
"""
operation_panel = """
          <div class="panel"><div class="panel-header"><div><div class="panel-title">객실 운영 상태</div><div class="panel-subtitle">정상 운영 또는 운영 중지·청소 제외를 별도로 관리</div></div>${!isHistoricalView() ? `<button class="btn small ${isOutOfService(room) ? 'red':'soft'}" data-action="open-room-operation" data-id="${room.id}">운영 상태 변경</button>` : ''}</div><div class="panel-body">
            <div class="operation-band ${isOutOfService(room) ? 'stopped':''}" style="margin-top:0;"><div><strong>${operationLabel(room)}</strong><span>${operationReason(room)}</span></div><span class="operation-badge ${isOutOfService(room) ? 'stopped':''}">${isOutOfService(room) ? '판매·청소 중지':'정상'}</span></div>
            <div class="info-row"><span class="info-label">고객 배정</span><span class="info-value">${isOutOfService(room) ? '불가':'객실 조건에 따라 자동 판정'}</span></div>
            <div class="info-row"><span class="info-label">메이드 청소</span><span class="info-value">${isOutOfService(room) ? '작업 생성·선택·배정 모두 제외':'청소 상태에 따라 운영'}</span></div>
            ${reservationConflict(room) ? `<div class="conflict-alert"><strong>현재 예약과 운영 상태가 충돌합니다</strong><span>${guestAllocationReason(room)}</span><button class="btn red small full" data-action="open-guest-allocation" data-id="${room.id}">예약 이동·해제</button></div>`:''}
          </div></div>

          <div class="panel"><div class="panel-header"><div><div class="panel-title">고객 객실 배정 상태</div><div class="panel-subtitle">고객에게 배정하면 신규 배정 불가로 잠기며, 관리자가 변경·해제·입실·퇴실 처리</div></div>${!isHistoricalView() ? `<button class="btn small ${guestAllocationState(room) === 'available' ? 'green':reservationConflict(room) ? 'red':'soft'}" data-action="open-guest-allocation" data-id="${room.id}">${guestAllocationActionLabel(room)}</button>` : ''}</div><div class="panel-body">
"""
rep(operation_panel_anchor, operation_panel, label='operation panel')

# Initialize query preview routes.
rep("""      if (view === 'room-issue') { state.role = 'admin'; state.screen = 'admin-room-detail'; state.selectedRoomId = '608'; }
""", """      if (view === 'room-issue') { state.role = 'admin'; state.screen = 'admin-room-detail'; state.selectedRoomId = '608'; }
      if (view === 'room-operation') { state.role = 'admin'; state.screen = 'admin-room-detail'; state.selectedRoomId = '608'; setTimeout(() => openRoomOperationSheet('608'), 80); }
      if (view === 'reservation-conflict') { state.role = 'admin'; state.screen = 'admin-room-detail'; state.selectedRoomId = '108'; setTimeout(() => openGuestAllocationSheet('108'), 80); }
""", label='query routes')

# Insert new modal/helper functions before openGuestAllocationSheet.
anchor = """    function openGuestAllocationSheet(roomId) {
"""
new_helpers = r'''    function availableTransferRooms(sourceRoom) {
      return state.rooms.filter(room => room.id !== sourceRoom.id && guestAllocationState(room) === 'available' && !isOutOfService(room));
    }

    function openRoomOperationSheet(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.selectedRoomId = roomId;
      const current = isOutOfService(room) ? 'out-of-service' : 'active';
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 운영 상태 변경</h3><p>‘운영 중지’는 고객 배정과 메이드 청소를 모두 막습니다. 기존 예약·투숙이 있으면 먼저 예약을 이동하거나 해제해야 합니다.</p><div class="safety-summary"><div><span>현재 운영</span><b>${operationLabel(room)}</b></div><div><span>현재 예약</span><b>${room.reservationAssigned ? (room.reservationLabel || '예약 있음') : '없음'}</b></div><div><span>현재 청소</span><b>${room.cleaningStatus}</b></div></div><div class="field"><label>변경할 운영 상태</label><select id="operationStatusInput" class="select"><option value="active" ${current === 'active' ? 'selected':''}>정상 운영</option><option value="out-of-service" ${current === 'out-of-service' ? 'selected':''}>운영 중지 · 고객 배정 불가 · 청소 제외</option></select></div><div class="field"><label>변경 사유</label><textarea id="operationReasonInput" class="textarea" placeholder="예: 냄새 원인 확인 전 객실 운영 중지">${room.operationalReason || ''}</textarea></div><div class="safety-card"><strong>예약 충돌 자동 차단</strong><span>예약 배정 또는 투숙 정보가 남아 있으면 운영 중지 확정 버튼을 잠그고 예약 이동·해제 화면으로 안내합니다.</span></div><div class="button-row" style="margin-top:13px;"><button class="btn" data-action="close-sheet">취소</button><button class="btn ${current === 'out-of-service' ? 'green':'red'}" data-action="review-room-operation" data-id="${room.id}">변경 내용 확인</button></div></div>`;
      sheet.classList.add('open');
      sheetBackdrop.classList.add('open');
    }

    function reviewRoomOperation(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      const target = document.getElementById('operationStatusInput')?.value || 'active';
      const reason = (document.getElementById('operationReasonInput')?.value || '').trim();
      if (target === (isOutOfService(room) ? 'out-of-service':'active')) { showToast('현재 운영 상태와 같습니다.'); return; }
      if (!reason) { showToast('운영 상태 변경 사유를 입력해 주세요.'); return; }
      if (target === 'out-of-service' && roomHasReservationOrGuest(room)) {
        const detail = room.reservationAssigned ? `${room.reservationLabel || '예약'}이 배정되어 있습니다.` : `${room.stayStatus} 상태가 남아 있습니다.`;
        sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">운영 중지 전에 예약 충돌을 해결해 주세요</h3><p>${room.id}호를 청소 제외·고객 배정 불가로 바꿀 수 있지만, 현재 예약이나 투숙 상태를 남긴 채 확정할 수는 없습니다.</p><div class="conflict-alert"><strong>${room.id}호 예약 충돌</strong><span>${detail}<br>운영 중지 사유: ${reason}</span></div><div class="impact-list"><div class="impact-item"><strong>1.</strong> 예약을 다른 고객 배정 가능 객실로 이동하거나 배정을 해제합니다.</div><div class="impact-item"><strong>2.</strong> 예약이 없는 상태가 되면 운영 중지를 다시 확정합니다.</div></div><div class="button-row"><button class="btn" data-action="open-room-operation" data-id="${room.id}">돌아가기</button><button class="btn red" data-action="open-guest-allocation" data-id="${room.id}">예약 이동·해제</button></div></div>`;
        sheet.classList.add('open'); sheetBackdrop.classList.add('open');
        return;
      }
      state.pendingAction = { type:'room-operation', roomId, target, reason };
      const stop = target === 'out-of-service';
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호를 ${stop ? '운영 중지':'정상 운영 재개'}할까요?</h3><p>실수 방지를 위한 최종 확인입니다. 확정하면 일자 이력과 관리자 변경 기록에 남습니다.</p><div class="safety-summary"><div><span>현재</span><b>${operationLabel(room)}</b></div><div><span>변경 후</span><b>${stop ? '운영 중지 · 청소 제외':'정상 운영 · 청소 필요 생성'}</b></div><div><span>사유</span><b>${reason}</b></div></div><div class="impact-list">${stop ? `<div class="impact-item">고객 배정 버튼 잠금</div><div class="impact-item">기존 청소 담당 회수·일감 클로즈</div><div class="impact-item">메이드 일감 목록과 검수 대기에서 제외</div>` : `<div class="impact-item">고객 배정은 아직 잠금 상태</div><div class="impact-item">퇴실 청소 작업을 ‘담당 미지정·선택 클로즈’로 생성</div><div class="impact-item">청소·검수 승인 후 고객 배정 가능 여부 재계산</div>`}</div><div class="button-row"><button class="btn" data-action="open-room-operation" data-id="${room.id}">돌아가기</button><button class="btn ${stop ? 'red':'green'}" data-action="confirm-room-operation">${stop ? '운영 중지 확정':'정상 운영 재개'}</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openReservationTransferSheet(sourceId) {
      const source = state.rooms.find(r => r.id === sourceId);
      if (!source || !source.reservationAssigned) return;
      const candidates = availableTransferRooms(source);
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${source.id}호 예약을 다른 객실로 이동</h3><p>예약 충돌을 해소하기 위해 고객 배정 가능 객실로 예약을 옮깁니다. 청소 담당 배정에는 영향을 주지 않습니다.</p><div class="safety-summary"><div><span>이동할 예약</span><b>${source.reservationLabel || '예약 정보 미입력'}</b></div><div><span>현재 객실</span><b>${source.id}호 · ${guestAllocationReason(source)}</b></div><div><span>입실 시각</span><b>${source.checkin || DEFAULT_CHECKIN_TIME}</b></div></div>${candidates.length ? `<div class="field"><label>새 객실</label><select id="transferRoomSelect" class="select">${candidates.map(room => `<option value="${room.id}">${room.id}호 · ${room.type} · 고객 배정 가능</option>`).join('')}</select></div><div class="button-row" style="margin-top:13px;"><button class="btn" data-action="open-guest-allocation" data-id="${source.id}">돌아가기</button><button class="btn primary" data-action="review-reservation-transfer" data-id="${source.id}">이동 내용 확인</button></div>` : `<div class="conflict-alert"><strong>현재 이동 가능한 객실이 없습니다</strong><span>다른 객실의 청소·검수 또는 차단 특이사항을 먼저 해결하거나 예약 배정을 해제해 주세요.</span></div><button class="btn full" data-action="open-guest-allocation" data-id="${source.id}">돌아가기</button>`}</div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function reviewReservationTransfer(sourceId) {
      const source = state.rooms.find(r => r.id === sourceId);
      const targetId = document.getElementById('transferRoomSelect')?.value;
      const target = state.rooms.find(r => r.id === targetId);
      if (!source || !target || guestAllocationState(target) !== 'available') { showToast('이동할 수 있는 고객 배정 가능 객실을 선택해 주세요.'); return; }
      state.pendingAction = { type:'reservation-transfer', sourceId, targetId };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">예약 객실을 ${source.id}호에서 ${target.id}호로 이동할까요?</h3><p>확정하면 원래 객실은 예약 미배정으로 바뀌고 새 객실은 예약 배정 완료로 잠깁니다.</p><div class="safety-summary"><div><span>예약</span><b>${source.reservationLabel}</b></div><div><span>이전 객실</span><b>${source.id}호</b></div><div><span>새 객실</span><b>${target.id}호 · ${target.type}</b></div><div><span>입실</span><b>${source.checkin || DEFAULT_CHECKIN_TIME}</b></div></div><div class="button-row"><button class="btn" data-action="open-reservation-transfer" data-id="${source.id}">돌아가기</button><button class="btn red" data-action="confirm-reservation-transfer">예약 이동 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openGuestAssignmentConfirm(roomId, label, checkinTime) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.pendingAction = { type:'guest-assignment', roomId, label, checkinTime };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호에 고객 예약을 배정할까요?</h3><p>확정하면 이 객실은 신규 고객에게 배정 불가로 잠기며, 이후 변경·해제도 관리자 확인 모달을 거칩니다.</p><div class="safety-summary"><div><span>예약</span><b>${label}</b></div><div><span>객실</span><b>${room.id}호 · ${room.type}</b></div><div><span>입실 시각</span><b>${checkinTime}</b></div><div><span>현재 상태</span><b>${guestAllocationHeadline(room)}</b></div></div><div class="button-row"><button class="btn" data-action="open-guest-allocation" data-id="${room.id}">돌아가기</button><button class="btn green" data-action="confirm-save-guest-assignment">고객 배정 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openPasswordConfirm(roomId, value) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.pendingAction = { type:'password-change', roomId, value };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 비밀번호를 변경할까요?</h3><p>메이드 출입과 현장 운영에 영향을 주는 정보이므로 한 번 더 확인합니다. 실제 도어락 변경과 앱 기록은 별도 연동이 필요합니다.</p><div class="safety-summary"><div><span>기존 비밀번호</span><b>${room.password}</b></div><div><span>새 비밀번호</span><b>${value}</b></div></div><div class="button-row"><button class="btn" data-action="edit-password" data-id="${room.id}">돌아가기</button><button class="btn red" data-action="confirm-save-password">비밀번호 변경 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openAssignmentEnabledConfirm(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      const enable = room.assignmentEnabled === false;
      state.pendingAction = { type:'assignment-enabled', roomId, enable };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 청소 담당 배정을 ${enable ? '허용':'보류'}할까요?</h3><p>${enable ? '관리자가 직접 담당자를 지정할 수 있게 됩니다. 메이드 자유 선택은 별도로 오픈해야 합니다.' : '미배정 상태를 유지하고 메이드 선택 오픈도 자동으로 닫습니다.'}</p><div class="safety-summary"><div><span>현재</span><b>${enable ? '배정 불가':'배정 가능'}</b></div><div><span>변경 후</span><b>${enable ? '배정 가능 · 선택 클로즈':'배정 불가'}</b></div></div><div class="button-row"><button class="btn" data-action="open-assignment" data-id="${room.id}">돌아가기</button><button class="btn ${enable ? 'green':'red'}" data-action="confirm-toggle-assignment-enabled">${enable ? '배정 가능 확정':'배정 보류 확정'}</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

    function openInspectionApprovalConfirm(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.pendingAction = { type:'inspection-approval', roomId };
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 검수를 승인할까요?</h3><p>승인하면 청소 주급이 확정되고 객실의 고객 배정 가능 여부가 다시 계산됩니다. 입실 차단 특이사항이나 운영 중지는 그대로 유지됩니다.</p><div class="safety-summary"><div><span>담당 메이드</span><b>${room.assignee || '미지정'}</b></div><div><span>청소 금액</span><b>${room.cleaningFee.toLocaleString()}원</b></div><div><span>차단 특이사항</span><b>${room.entryBlockIssue || '없음'}</b></div><div><span>운영 상태</span><b>${operationLabel(room)}</b></div></div><div class="button-row"><button class="btn" data-action="close-sheet">취소</button><button class="btn green" data-action="confirm-approve-inspection">검수 승인 확정</button></div></div>`;
      sheet.classList.add('open'); sheetBackdrop.classList.add('open');
    }

'''
rep(anchor, new_helpers + anchor, label='new helpers')

# Replace guest allocation sheet with conflict/out-of-service handling.
old_func = text[text.index('    function openGuestAllocationSheet(roomId) {'):text.index('    function openGuestActionConfirm(roomId, actionType) {')]
new_func = r'''    function openGuestAllocationSheet(roomId) {
      const room = state.rooms.find(r => r.id === roomId);
      if (!room) return;
      state.selectedRoomId = roomId;
      const occupied = ['투숙 중','장기투숙'].includes(room.stayStatus);
      const assigned = !!room.reservationAssigned;
      const conflict = reservationConflict(room);
      const canAssign = guestAllocationState(room) === 'available';
      let controls = '';
      if (conflict) {
        const transferCount = availableTransferRooms(room).length;
        controls = `<div class="conflict-alert"><strong>예약과 객실 상태가 충돌합니다</strong><span>${guestAllocationReason(room)}</span></div><div class="impact-list"><div class="impact-item">입실 처리는 잠김</div><div class="impact-item">예약을 고객 배정 가능 객실로 이동하거나 배정을 해제해야 함</div><div class="impact-item">이동 가능한 객실 ${transferCount}개</div></div><div class="button-row"><button class="btn" data-action="confirm-guest-action" data-id="${room.id}" data-guest-action="release">배정 해제</button><button class="btn red" data-action="open-reservation-transfer" data-id="${room.id}" ${transferCount ? '' : 'disabled'}>다른 객실로 이동</button></div>${isOutOfService(room) ? `<button class="btn soft full" style="margin-top:8px;" data-action="open-room-operation" data-id="${room.id}">운영 상태 확인</button>` : `<button class="btn soft full" style="margin-top:8px;" data-action="open-entry-issue" data-id="${room.id}">차단 특이사항 확인</button>`}`;
      } else if (occupied) {
        controls = `<div class="safety-card"><strong>현재 고객 입실 중</strong><span>신규 고객에게는 자동으로 배정 불가입니다. 실제 퇴실을 확인한 뒤 퇴실 처리하면 퇴실 청소 작업이 생성됩니다.</span></div><button class="btn red full" style="margin-top:12px;" data-action="confirm-guest-action" data-id="${room.id}" data-guest-action="checkout">고객 퇴실 처리</button>`;
      } else if (assigned || canAssign) {
        controls = `<div class="field"><label>예약번호·예약자 식별</label><input id="guestReservationLabel" class="input" value="${assigned ? (room.reservationLabel || '') : ''}" placeholder="예: YN-260814-082"></div><div class="field-row"><div class="field"><label>입실 시각</label><input id="guestCheckinTime" class="input" type="time" value="${room.earlyCheckinTime || (room.checkin && room.checkin !== '예약 없음' && room.checkin !== '투숙 중' ? room.checkin : DEFAULT_CHECKIN_TIME)}"></div><div class="field"><label>기본 체크인</label><input class="input" value="${DEFAULT_CHECKIN_TIME}" disabled></div></div><div class="guest-action-hint">예약 저장 전 최종 확인 모달이 한 번 더 열립니다. 확정 후 이 객실은 ‘예약 배정 완료 · 신규 배정 불가’로 바뀝니다.</div>${assigned ? `<div class="button-row" style="margin-top:13px;"><button class="btn" data-action="confirm-guest-action" data-id="${room.id}" data-guest-action="release">배정 해제</button><button class="btn primary" data-action="save-guest-assignment" data-id="${room.id}">배정 정보 확인</button></div><button class="btn green full" style="margin-top:8px;" data-action="confirm-guest-action" data-id="${room.id}" data-guest-action="checkin">고객 입실 처리</button>` : `<div class="button-row" style="margin-top:13px;"><button class="btn" data-action="close-sheet">취소</button><button class="btn green" data-action="save-guest-assignment" data-id="${room.id}">배정 내용 확인</button></div>`}`;
      } else {
        controls = `<div class="assignment-readonly"><strong>현재 고객 배정 불가</strong><span>${guestAllocationReason(room)}</span></div><div class="safety-card"><strong>강제 배정하지 않음</strong><span>운영 중지, 청소·검수 미완료 또는 입실 차단 특이사항이 남아 있으면 고객 배정 버튼을 잠급니다. 원인을 해결하면 자동으로 다시 계산합니다.</span></div>${isOutOfService(room) ? `<button class="btn red full" style="margin-top:11px;" data-action="open-room-operation" data-id="${room.id}">운영 상태 관리</button>` : room.entryBlockIssue ? `<button class="btn soft full" style="margin-top:11px;" data-action="open-entry-issue" data-id="${room.id}">입실 차단 특이사항 관리</button>` : ''}<button class="btn full" style="margin-top:8px;" data-action="close-sheet">닫기</button>`;
      }
      sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${room.id}호 고객 객실 배정</h3><p>청소 담당자 배정과 별도의 객실 판매·입실 상태입니다. 현재: ${guestAllocationHeadline(room)}</p><div class="safety-summary"><div><span>운영 상태</span><b>${operationLabel(room)}</b></div><div><span>객실 상태</span><b>${room.stayStatus}</b></div><div><span>청소·검수</span><b>${room.cleaningStatus}</b></div><div><span>현재 예약</span><b>${room.reservationAssigned ? (room.reservationLabel || '정보 미입력') : '미배정'}</b></div></div>${controls}</div>`;
      sheet.classList.add('open');
      sheetBackdrop.classList.add('open');
    }

'''
text = text.replace(old_func, new_func, 1)

# Password sheet button copy.
rep("<button class=\"btn primary\" data-action=\"save-password\">저장</button>", "<button class=\"btn primary\" data-action=\"save-password\">변경 내용 확인</button>", label='password button')

# Historical actions include operation/transfer and confirmations.
rep("'execute-guest-action']);", "'execute-guest-action','open-room-operation','review-room-operation','confirm-room-operation','open-reservation-transfer','review-reservation-transfer','confirm-reservation-transfer','confirm-save-guest-assignment','confirm-save-password','confirm-toggle-assignment-enabled','confirm-approve-inspection']);", label='historical actions')

# Add demo view handlers.
rep("""        if (view === 'maid-penalties') { state.role = 'maid'; navigate('maid-penalties','maid'); }
""", """        if (view === 'maid-penalties') { state.role = 'maid'; navigate('maid-penalties','maid'); }
        if (view === 'room-operation') { state.role = 'admin'; state.selectedRoomId = '608'; navigate('admin-room-detail','admin'); setTimeout(() => openRoomOperationSheet('608'), 50); }
        if (view === 'reservation-conflict') { state.role = 'admin'; state.selectedRoomId = '108'; navigate('admin-room-detail','admin'); setTimeout(() => openGuestAllocationSheet('108'), 50); }
""", label='demo handlers')

# Insert event actions before open guest allocation handler.
handler_anchor = """      if (action === 'go-admin-room') { state.selectedRoomId = id; navigate('admin-room-detail','admin'); }
      if (action === 'open-guest-allocation') { openGuestAllocationSheet(id || state.selectedRoomId); }
"""
handler_new = """      if (action === 'go-admin-room') { state.selectedRoomId = id; navigate('admin-room-detail','admin'); }
      if (action === 'view-reservation-conflicts') { state.roomFilter = 'reservation-conflict'; render(); return; }
      if (action === 'open-room-operation') { openRoomOperationSheet(id || state.selectedRoomId); return; }
      if (action === 'review-room-operation') { reviewRoomOperation(id || state.selectedRoomId); return; }
      if (action === 'confirm-room-operation') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'room-operation') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        if (pending.target === 'out-of-service') {
          if (roomHasReservationOrGuest(room)) { state.pendingAction = null; openGuestAllocationSheet(room.id); showToast('예약 충돌을 먼저 해결해 주세요.'); return; }
          if (room.assignee || state.taskStarted[room.id]) archiveTaskProgress(room, room.assignee || '미배정', pending.reason, '객실 운영 중지로 작업 중단');
          room.operationalStatus = 'out-of-service'; room.operationalReason = pending.reason; room.cleaningSuppressed = true;
          room.cleaningStatus = '청소 제외'; room.task = '작업 없음'; room.color = 'gray'; room.assignmentEnabled = false; room.assignmentBlockReason = '운영 중지 객실은 청소 담당 배정 불가'; room.openForClaim = false; room.assignee = ''; room.canEnter = false; room.available = '-'; room.deadline = '-'; room.inspection = false;
          if (!room.reservationAssigned) { room.stayStatus = '공실'; room.stayTone = 'gray'; room.checkin = '예약 없음'; }
          addDailyEvent(room, '객실 운영 중지', `${pending.reason} · 고객 배정·청소 모두 중지`);
        } else {
          room.operationalStatus = 'active'; room.operationalReason = ''; room.cleaningSuppressed = false;
          room.stayStatus = room.reservationAssigned ? '오늘 입실' : '공실'; room.stayTone = room.reservationAssigned ? 'blue':'gray';
          room.cleaningStatus = '청소 가능'; room.task = '퇴실 청소'; room.color = 'orange'; room.assignmentEnabled = true; room.assignmentBlockReason = ''; room.openForClaim = false; room.assignee = ''; room.canEnter = true; room.available = '지금'; room.deadline = '15:30'; room.inspection = false; room.checkout = DEFAULT_CHECKOUT_TIME; if (!room.reservationAssigned) room.checkin = '예약 없음';
          addDailyEvent(room, '객실 정상 운영 재개', `${pending.reason} · 퇴실 청소 작업 생성 · 담당 미지정`);
        }
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호를 ${isOutOfService(room) ? '운영 중지':'정상 운영 재개'} 상태로 변경했습니다.`); return;
      }
      if (action === 'open-reservation-transfer') { openReservationTransferSheet(id); return; }
      if (action === 'review-reservation-transfer') { reviewReservationTransfer(id); return; }
      if (action === 'confirm-reservation-transfer') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'reservation-transfer') return;
        const source = state.rooms.find(r => r.id === pending.sourceId);
        const target = state.rooms.find(r => r.id === pending.targetId);
        if (!source || !target || !source.reservationAssigned || guestAllocationState(target) !== 'available') { closeSheet(); render(); showToast('예약 이동 조건이 바뀌었습니다. 다시 확인해 주세요.'); return; }
        const label = source.reservationLabel; const checkin = source.checkin || DEFAULT_CHECKIN_TIME; const early = source.earlyCheckinTime || '';
        target.reservationAssigned = true; target.reservationLabel = label; target.stayStatus = '오늘 입실'; target.stayTone = 'blue'; target.checkin = checkin; target.earlyCheckinTime = early;
        source.reservationAssigned = false; source.reservationLabel = ''; source.stayStatus = '공실'; source.stayTone = 'gray'; source.checkin = '예약 없음'; source.earlyCheckinTime = '';
        addDailyEvent(source, '예약 객실 이동', `${label} · ${source.id}호 → ${target.id}호 · 예약 충돌 해소`);
        addDailyEvent(target, '예약 객실 이동 수신', `${label} · ${source.id}호에서 이동 · 입실 ${checkin}`);
        state.pendingAction = null; closeSheet(); render(); showToast(`${label} 예약을 ${target.id}호로 이동했습니다.`); return;
      }
      if (action === 'open-guest-allocation') { openGuestAllocationSheet(id || state.selectedRoomId); }
"""
rep(handler_anchor, handler_new, label='new event handlers')

# Password save now review; add confirmation handler.
old_password_handler = """      if (action === 'save-password') {
        const input = document.getElementById('passwordInput');
        const value = (input?.value || '').replace(/\D/g,'');
        if (value.length !== 4) { showToast('비밀번호는 숫자 4자리로 입력해 주세요.'); return; }
        const room = state.rooms.find(r => r.id === state.selectedRoomId);
        if (room) { room.password = value; addDailyEvent(room, '객실 비밀번호 변경', `4자리 비밀번호를 ${value}로 변경`); }
        closeSheet();
        render();
        showToast(`${state.selectedRoomId}호 비밀번호를 ${value}로 저장했습니다.`);
      }
"""
new_password_handler = """      if (action === 'save-password') {
        const input = document.getElementById('passwordInput');
        const value = (input?.value || '').replace(/\D/g,'');
        if (value.length !== 4) { showToast('비밀번호는 숫자 4자리로 입력해 주세요.'); return; }
        const room = state.rooms.find(r => r.id === state.selectedRoomId);
        if (!room) return;
        if (room.password === value) { showToast('현재 비밀번호와 같습니다.'); return; }
        openPasswordConfirm(room.id, value); return;
      }
      if (action === 'confirm-save-password') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'password-change') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        const old = room.password; room.password = pending.value;
        addDailyEvent(room, '객실 비밀번호 변경', `${old} → ${pending.value} · 관리자 확인 모달 승인`);
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호 비밀번호를 변경했습니다.`); return;
      }
"""
rep(old_password_handler, new_password_handler, label='password handler')

# Assignment enabled direct toggle -> confirm.
old_toggle = """      if (action === 'toggle-assignment-enabled') {
        const room = state.rooms.find(r => r.id === id);
        if (!room || !assignmentLifecycleEligible(room) || room.assignee) { showToast('담당 확정 객실은 먼저 담당을 회수해 주세요.'); return; }
        const before = room.assignmentEnabled === false ? '배정 불가' : '배정 가능';
        room.assignmentEnabled = room.assignmentEnabled === false;
        room.openForClaim = false;
        if (room.assignmentEnabled) room.assignmentBlockReason = '';
        else room.assignmentBlockReason = '관리자 배정 보류';
        addAssignmentHistory(room, before, room.assignmentEnabled ? '배정 가능' : '배정 불가', room.assignmentEnabled ? '관리자 배정 허용' : '관리자 배정 보류');
        closeSheet(); render(); showToast(`${id}호를 ${room.assignmentEnabled ? '배정 가능' : '배정 불가'} 상태로 변경했습니다.`);
      }
"""
new_toggle = """      if (action === 'toggle-assignment-enabled') {
        const room = state.rooms.find(r => r.id === id);
        if (!room || !assignmentLifecycleEligible(room) || room.assignee) { showToast('담당 확정 객실은 먼저 담당을 회수해 주세요.'); return; }
        openAssignmentEnabledConfirm(id); return;
      }
      if (action === 'confirm-toggle-assignment-enabled') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'assignment-enabled') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room || room.assignee || !assignmentLifecycleEligible(room)) return;
        const before = room.assignmentEnabled === false ? '배정 불가' : '배정 가능';
        room.assignmentEnabled = pending.enable; room.openForClaim = false;
        room.assignmentBlockReason = pending.enable ? '' : '관리자 배정 보류';
        addAssignmentHistory(room, before, pending.enable ? '배정 가능' : '배정 불가', pending.enable ? '관리자 배정 허용' : '관리자 배정 보류');
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호를 ${pending.enable ? '배정 가능':'배정 불가'} 상태로 변경했습니다.`); return;
      }
"""
rep(old_toggle, new_toggle, label='assignment toggle handler')

# Guest assignment direct save -> confirm and final handler.
old_guest_save = """      if (action === 'save-guest-assignment') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const label = (document.getElementById('guestReservationLabel')?.value || '').trim();
        const checkinTime = document.getElementById('guestCheckinTime')?.value || DEFAULT_CHECKIN_TIME;
        if (!label) { showToast('예약번호나 예약자 식별 정보를 입력해 주세요.'); return; }
        if (!room.reservationAssigned && guestAllocationState(room) !== 'available') { showToast('청소·검수 또는 차단 특이사항을 먼저 해결해 주세요.'); return; }
        const wasAssigned = room.reservationAssigned;
        room.reservationAssigned = true;
        room.reservationLabel = label;
        room.stayStatus = '오늘 입실';
        room.stayTone = 'blue';
        room.checkin = checkinTime;
        room.earlyCheckinTime = checkinTime !== DEFAULT_CHECKIN_TIME ? checkinTime : '';
        addDailyEvent(room, wasAssigned ? '고객 객실 배정 정보 수정' : '고객 객실 배정 완료', `${label} · 입실 ${checkinTime} · 신규 고객 배정 불가로 전환`);
        closeSheet(); render(); showToast(`${room.id}호를 ${label} 예약에 배정했습니다.`);
        return;
      }
"""
new_guest_save = """      if (action === 'save-guest-assignment') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const label = (document.getElementById('guestReservationLabel')?.value || '').trim();
        const checkinTime = document.getElementById('guestCheckinTime')?.value || DEFAULT_CHECKIN_TIME;
        if (!label) { showToast('예약번호나 예약자 식별 정보를 입력해 주세요.'); return; }
        if (!room.reservationAssigned && guestAllocationState(room) !== 'available') { showToast('운영 상태·청소·검수·차단 특이사항을 먼저 해결해 주세요.'); return; }
        if (isOutOfService(room) || reservationConflict(room)) { showToast('운영 중지 또는 예약 충돌 객실에는 고객을 배정할 수 없습니다.'); return; }
        openGuestAssignmentConfirm(room.id, label, checkinTime); return;
      }
      if (action === 'confirm-save-guest-assignment') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'guest-assignment') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        if (!room.reservationAssigned && guestAllocationState(room) !== 'available') { closeSheet(); render(); showToast('객실 상태가 바뀌어 배정할 수 없습니다. 다시 확인해 주세요.'); return; }
        const wasAssigned = room.reservationAssigned;
        room.reservationAssigned = true; room.reservationLabel = pending.label; room.stayStatus = '오늘 입실'; room.stayTone = 'blue'; room.checkin = pending.checkinTime; room.earlyCheckinTime = pending.checkinTime !== DEFAULT_CHECKIN_TIME ? pending.checkinTime : '';
        addDailyEvent(room, wasAssigned ? '고객 객실 배정 정보 수정' : '고객 객실 배정 완료', `${pending.label} · 입실 ${pending.checkinTime} · 관리자 확인 모달 승인`);
        state.pendingAction = null; closeSheet(); render(); showToast(`${room.id}호를 ${pending.label} 예약에 배정했습니다.`); return;
      }
"""
rep(old_guest_save, new_guest_save, label='guest save handler')

# Prevent checkout from auto-generating cleaning for out-of-service room.
rep("""        if (pending.actionType === 'checkout') {
          const old = room.reservationLabel || '투숙객';
          room.reservationAssigned = false; room.reservationLabel = ''; room.stayStatus = '오늘 퇴실'; room.stayTone = 'purple'; room.checkin = DEFAULT_CHECKIN_TIME; room.checkout = DEFAULT_CHECKOUT_TIME; room.earlyCheckinTime = ''; room.lateCheckoutTime = '';
          room.cleaningStatus = '청소 가능'; room.task = '퇴실 청소'; room.color = 'orange'; room.assignmentEnabled = true; room.openForClaim = false; room.assignee = ''; room.canEnter = true; room.available = '지금'; room.deadline = '15:30';
          addDailyEvent(room, '고객 퇴실 처리', `${old} 퇴실 확인 · 퇴실 청소 작업 생성 · 담당 미배정`);
        }
""", """        if (pending.actionType === 'checkout') {
          const old = room.reservationLabel || '투숙객';
          room.reservationAssigned = false; room.reservationLabel = ''; room.stayStatus = '오늘 퇴실'; room.stayTone = 'purple'; room.checkin = DEFAULT_CHECKIN_TIME; room.checkout = DEFAULT_CHECKOUT_TIME; room.earlyCheckinTime = ''; room.lateCheckoutTime = '';
          if (isOutOfService(room) || room.cleaningSuppressed) {
            room.cleaningStatus = '청소 제외'; room.task = '작업 없음'; room.color = 'gray'; room.assignmentEnabled = false; room.openForClaim = false; room.assignee = ''; room.canEnter = false; room.available = '-'; room.deadline = '-';
            addDailyEvent(room, '고객 퇴실 처리', `${old} 퇴실 확인 · 운영 중지 상태로 청소 작업 미생성`);
          } else {
            room.cleaningStatus = '청소 가능'; room.task = '퇴실 청소'; room.color = 'orange'; room.assignmentEnabled = true; room.openForClaim = false; room.assignee = ''; room.canEnter = true; room.available = '지금'; room.deadline = '15:30';
            addDailyEvent(room, '고객 퇴실 처리', `${old} 퇴실 확인 · 퇴실 청소 작업 생성 · 담당 미배정`);
          }
        }
""", label='checkout operation rule')

# Resolve entry issue gets confirmation.
old_resolve = """      if (action === 'resolve-entry-issue') {
        const room = state.rooms.find(r => r.id === id);
        if (!room || !room.entryBlockIssue) return;
        const resolved = room.entryBlockIssue;
        room.entryBlockIssue = '';
        addDailyEvent(room, '고객 배정 차단 특이사항 해결', resolved || '해결 처리');
        render();
        showToast(guestAllocationState(room) === 'available' ? `${id}호 특이사항을 해결해 고객 배정 가능으로 전환했습니다.` : `${id}호 특이사항을 해결했습니다. 청소·예약 상태는 별도로 확인해 주세요.`);
      }
"""
new_resolve = """      if (action === 'resolve-entry-issue') {
        const room = state.rooms.find(r => r.id === id);
        if (!room || !room.entryBlockIssue) return;
        state.pendingAction = { type:'resolve-entry-issue', roomId:id };
        sheet.innerHTML = `<div class="sheet-handle"></div><div class="sheet-scroll"><h3 id="sheetTitle">${id}호 입실 차단 특이사항을 해결 처리할까요?</h3><p>실제 문제가 해결됐는지 확인하세요. 예약이 이미 배정돼 있었다면 해결 후 예약 충돌이 해소될 수 있습니다.</p><div class="safety-summary"><div><span>현재 사유</span><b>${room.entryBlockIssue}</b></div><div><span>운영 상태</span><b>${operationLabel(room)}</b></div><div><span>현재 예약</span><b>${room.reservationLabel || '없음'}</b></div></div><div class="button-row"><button class="btn" data-action="close-sheet">취소</button><button class="btn green" data-action="confirm-resolve-entry-issue">해결 처리 확정</button></div></div>`;
        sheet.classList.add('open'); sheetBackdrop.classList.add('open'); return;
      }
      if (action === 'confirm-resolve-entry-issue') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'resolve-entry-issue') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room || !room.entryBlockIssue) return;
        const resolved = room.entryBlockIssue; room.entryBlockIssue = '';
        addDailyEvent(room, '고객 배정 차단 특이사항 해결', `${resolved} · 관리자 확인 모달 승인`);
        state.pendingAction = null; closeSheet(); render();
        showToast(guestAllocationState(room) === 'available' ? `${room.id}호 특이사항을 해결해 고객 배정 가능으로 전환했습니다.` : `${room.id}호 특이사항을 해결했습니다. 다른 상태를 확인해 주세요.`); return;
      }
"""
rep(old_resolve, new_resolve, label='resolve issue confirmation')

# Inspection approval now confirmation.
old_approve_start = """      if (action === 'approve-inspection') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const photos = inspectionPhotosFor(room);
        const reviewed = state.photoReviews[id] || [];
        if (reviewed.length !== photos.length) { showToast(`인증사진 ${photos.length - reviewed.length}장을 더 확인해 주세요.`); return; }
        room.cleaningStatus = '입실 준비 완료';
"""
new_approve_start = """      if (action === 'approve-inspection') {
        const room = state.rooms.find(r => r.id === id);
        if (!room) return;
        const photos = inspectionPhotosFor(room);
        const reviewed = state.photoReviews[id] || [];
        if (reviewed.length !== photos.length) { showToast(`인증사진 ${photos.length - reviewed.length}장을 더 확인해 주세요.`); return; }
        openInspectionApprovalConfirm(id); return;
      }
      if (action === 'confirm-approve-inspection') {
        const pending = state.pendingAction;
        if (!pending || pending.type !== 'inspection-approval') return;
        const room = state.rooms.find(r => r.id === pending.roomId);
        if (!room) return;
        const id = room.id;
        room.cleaningStatus = '입실 준비 완료';
"""
rep(old_approve_start, new_approve_start, label='inspection confirm start')
# Add clearing pending in inspection approve end.
rep("""        state.screen = 'admin-inspection';
        state.previousScreen = null;
        render(); showToast(guestAllocationState(room) === 'available' ? `${id}호 검수 승인 · 고객 배정 가능으로 전환했습니다.` : `${id}호 검수와 주급은 확정했지만 고객 배정 상태는 별도 사유를 확인해 주세요.`);
      }
""", """        state.pendingAction = null;
        closeSheet(); state.screen = 'admin-inspection';
        state.previousScreen = null;
        render(); showToast(guestAllocationState(room) === 'available' ? `${id}호 검수 승인 · 고객 배정 가능으로 전환했습니다.` : `${id}호 검수와 주급은 확정했지만 고객 배정 상태는 별도 사유를 확인해 주세요.`);
      }
""", label='inspection confirm end')

# Ensure operation actions are recognized in click handler routing (already new functions). Update room issue button class conflict styling handled.

# Save latest too.
out.write_text(text, encoding='utf-8')
Path('/mnt/data/castle_the_art_room_manager_wireframe_latest.html').write_text(text, encoding='utf-8')
print(f'wrote {out} ({len(text)} chars)')
