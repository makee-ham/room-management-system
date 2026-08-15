from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / 'CURRENT' / 'castle_the_art_room_manager_wireframe_v13.html',
    ROOT / 'CURRENT' / 'castle_the_art_room_manager_wireframe_latest.html',
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f'{label}: pattern not found')
    return text.replace(old, new, 1)


for path in FILES:
    text = path.read_text(encoding='utf-8')
    text = replace_once(text,
        "      const candleDraft = state.taskCandleCounts[room.id] ?? room.candleCount ?? 0;\n      const checkItems = [",
        "      const candleFloor = Number(room.candleCount || 0);\n      const candleDraft = Math.max(candleFloor, Number(state.taskCandleCounts[room.id] ?? candleFloor));\n      const candleAddedByMaid = Math.max(0, candleDraft - candleFloor);\n      const checkItems = [",
        'maid task candle floor variables')
    text = replace_once(text,
        "            <div class=\"candle-record\"><div class=\"candle-record-copy\"><strong>객실에 두고 나온 촛불</strong><span>냄새가 나는 객실에 두고 나온 최종 개수를 기록합니다. 메이드의 회수 완료 처리가 아니라 관리자에게 현재 수량을 전달하는 항목입니다.</span></div><div class=\"stepper\"><button data-action=\"task-candle-minus\" data-id=\"${room.id}\" aria-label=\"촛불 수량 줄이기\">−</button><strong>${candleDraft}</strong><button data-action=\"task-candle-plus\" data-id=\"${room.id}\" aria-label=\"촛불 수량 늘리기\">+</button></div></div>",
        "            <div class=\"candle-record\"><div class=\"candle-record-copy\"><strong>청소 후 객실에 둔 촛불</strong><span>${candleFloor > 0 ? `기존 기록 ${candleFloor}개는 관리자가 현장에서 회수 완료 처리해야 줄일 수 있습니다. ` : ''}메이드는 새로 둔 수량만 추가 기록하며, 총 ${candleDraft}개 중 이번 작업 추가분은 ${candleAddedByMaid}개입니다.</span></div><div class=\"stepper\"><button data-action=\"task-candle-minus\" data-id=\"${room.id}\" aria-label=\"새로 둔 촛불 수량 줄이기\" ${candleDraft <= candleFloor ? 'disabled':''}>−</button><strong>${candleDraft}</strong><button data-action=\"task-candle-plus\" data-id=\"${room.id}\" aria-label=\"새로 둔 촛불 수량 늘리기\">+</button></div></div>",
        'maid task candle controls')
    text = replace_once(text,
        "      const candleCount = state.taskCandleCounts[roomId] ?? room.candleCount ?? 0;\n      state.pendingAction = { type:'complete-task', roomId };",
        "      const candleFloor = Number(room.candleCount || 0);\n      const candleCount = Math.max(candleFloor, Number(state.taskCandleCounts[roomId] ?? candleFloor));\n      const candleAddedByMaid = Math.max(0, candleCount - candleFloor);\n      state.pendingAction = { type:'complete-task', roomId, candleFloor, candleCount };",
        'completion candle floor')
    text = replace_once(text,
        "<div><span>청소 후 촛불</span><b>${candleCount}개</b></div><div><span>고객 배정 영향</span>",
        "<div><span>청소 후 촛불</span><b>총 ${candleCount}개 · 이번 작업 +${candleAddedByMaid}</b></div><div><span>고객 배정 영향</span>",
        'completion summary')
    text = replace_once(text,
        "<strong>촛불 회수는 관리자 확인 단계</strong><span>메이드는 청소 후 객실에 둔 수량만 기록합니다. 제출 후 관리자 화면에 ‘촛불 회수 필요’로 표시되고, 전량 회수 전 고객 입실이 잠깁니다.</span>",
        "<strong>기존 촛불 감소·회수는 관리자 전용</strong><span>메이드는 이번 청소에서 새로 둔 촛불만 추가 기록합니다. 기존 ${candleFloor}개를 포함해 총 ${candleCount}개가 남으며, 관리자가 현장에서 전량 회수해 0개로 확정하기 전 고객 배정과 입실이 잠깁니다.</span>",
        'completion safety copy')
    text = replace_once(text,
        "      if (action === 'task-candle-plus' || action === 'task-candle-minus') {\n        const current = state.taskCandleCounts[id] ?? state.rooms.find(r => r.id === id)?.candleCount ?? 0;\n        state.taskCandleCounts[id] = Math.max(0, Math.min(9, current + (action === 'task-candle-plus' ? 1 : -1)));\n        render();\n      }",
        "      if (action === 'task-candle-plus' || action === 'task-candle-minus') {\n        const room = state.rooms.find(r => r.id === id);\n        if (!room) return;\n        const floor = Number(room.candleCount || 0);\n        const current = Math.max(floor, Number(state.taskCandleCounts[id] ?? floor));\n        if (action === 'task-candle-minus' && current <= floor) {\n          showToast(floor > 0 ? `기존 촛불 ${floor}개는 관리자가 회수 완료 처리해야 줄일 수 있습니다.` : '추가한 촛불이 없습니다.');\n          return;\n        }\n        state.taskCandleCounts[id] = Math.max(floor, Math.min(20, current + (action === 'task-candle-plus' ? 1 : -1)));\n        render();\n      }",
        'maid candle stepper handler')
    text = replace_once(text,
        "        room.cleaningStatus = '검수 대기'; room.color = 'orange'; room.inspection = true; room.workStartedAt = room.workStartedAt || '12:20'; room.workFinishedAt = '13:12'; room.submittedAt = '13:18'; room.cleanerNote = state.taskNotes[id] || '특이사항 없음.';\n        room.candleCount = state.taskCandleCounts[id] ?? room.candleCount ?? 0;\n        if (room.candleCount > 0 && !room.candleLocations) room.candleLocations = '메이드 청소 완료 시 수량 기록 · 위치 미입력';",
        "        room.cleaningStatus = '검수 대기'; room.color = 'orange'; room.inspection = true; room.workStartedAt = room.workStartedAt || '12:20'; room.workFinishedAt = '13:12'; room.submittedAt = '13:18'; room.cleanerNote = state.taskNotes[id] || '특이사항 없음.';\n        const candleBeforeSubmit = Number(room.candleCount || 0);\n        const submittedCandleCount = Math.max(candleBeforeSubmit, Number(state.taskCandleCounts[id] ?? candleBeforeSubmit));\n        room.candleCount = submittedCandleCount;\n        if (room.candleCount > 0 && !room.candleLocations) room.candleLocations = '메이드 청소 완료 시 추가 수량 기록 · 위치 미입력';",
        'submit candle floor enforcement')
    text = replace_once(text,
        "addDailyEvent(room, '청소 완료·검수 요청', `인증사진 8장 · 청소 후 촛불 ${room.candleCount}개 기록${room.candleCount > 0 ? ' · 관리자 전량 회수 전 고객 배정·입실 차단' : ''} · 메이드 확인 모달 승인`, '13:18');",
        "addDailyEvent(room, '청소 완료·검수 요청', `인증사진 8장 · 기존 촛불 ${candleBeforeSubmit}개 · 메이드 추가 ${Math.max(0, room.candleCount - candleBeforeSubmit)}개 · 최종 ${room.candleCount}개${room.candleCount > 0 ? ' · 관리자 전량 회수 전 고객 배정·입실 차단' : ''} · 메이드 확인 모달 승인`, '13:18');",
        'submit audit copy')
    path.write_text(text, encoding='utf-8')

script_match = re.search(r'<script>\s*(.*?)\s*</script>\s*</body>', FILES[0].read_text(encoding='utf-8'), flags=re.S)
if not script_match:
    raise RuntimeError('inline script not found')
(ROOT / 'CURRENT' / 'castle_v13_script.js').write_text(script_match.group(1), encoding='utf-8')
print('Applied maid candle permission patch to v13 and latest.')
