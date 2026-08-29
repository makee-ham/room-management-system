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


def replace_function(name: str, replacement: str) -> None:
    global html
    marker = f"function {name}"
    starts = []
    cursor = 0
    while True:
        index = html.find(marker, cursor)
        if index < 0:
            break
        starts.append(index)
        cursor = index + len(marker)
    if len(starts) != 1:
        raise SystemExit(f"function {name}: expected exactly one declaration, found {len(starts)}")
    start = starts[0]
    brace = html.find("{", start)
    if brace < 0:
        raise SystemExit(f"function {name}: opening brace missing")
    depth = 0
    quote: str | None = None
    escape = False
    end = -1
    for index in range(brace, len(html)):
        char = html[index]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end < 0:
        raise SystemExit(f"function {name}: closing brace missing")
    html = html[:start] + replacement.rstrip() + html[end:]


simulation_source = r'''
      const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY = Object.freeze({
        m1:Object.freeze([0,1,3,4,5,6]),
        m2:Object.freeze([1,2,4,5,6]),
        m3:Object.freeze([0,2,3,4,5,6]),
        m4:Object.freeze([0,1,2,3,4,5,6]),
        m5:Object.freeze([0,2,3,5,6]),
        m6:Object.freeze([0,1,4,5,6]),
        m7:Object.freeze([1,2,4,5,6]),
        m8:Object.freeze([0,1,2,3,4,5,6]),
        m9:Object.freeze([0,3,4,5,6])
      });
      const TOMORROW_ASSIGNMENT_SIMULATION_DATE='2026-08-16';
      const TOMORROW_ASSIGNMENT_SIMULATION_TARGETS = Object.freeze([
        {room:'621',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'352',code:'checkout',kind:'퇴실 청소',checkout:'10:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'516',code:'early',kind:'퇴실 청소',checkout:'11:00',checkin:'14:00',deadline:'13:30',source:'checkout',sourceLabel:'예약 체크아웃 · 얼리 체크인',guestCount:2},
        {room:'552',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'15:00',deadline:'14:30',source:'checkout',sourceLabel:'예약 체크아웃 · 조기 입실',guestCount:2},
        {room:'556',code:'late',kind:'퇴실 청소',checkout:'13:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 레이트 체크아웃',guestCount:2},
        {room:'652',code:'checkout',kind:'퇴실 청소',checkout:'10:30',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'657',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'660',code:'checkout',kind:'퇴실 청소',checkout:'10:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'662',code:'checkout',kind:'퇴실 청소',checkout:'12:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'720',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'723',code:'checkout',kind:'퇴실 청소',checkout:'10:30',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'726',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'729',code:'checkout',kind:'퇴실 청소',checkout:'12:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'750',code:'manual',kind:'퇴실 청소',checkout:'10:30',checkin:'16:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청',guestCount:2},
        {room:'752',code:'checkout',kind:'퇴실 청소',checkout:'10:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'753',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'756',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'760',code:'checkout',kind:'퇴실 청소',checkout:'12:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'762',code:'hold',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 정보 확인 필요',guestCount:2},
        {room:'135',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:3},
        {room:'136',code:'checkout',kind:'퇴실 청소',checkout:'10:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'240',code:'checkout',kind:'퇴실 청소',checkout:'12:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:3},
        {room:'454',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'455',code:'manual',kind:'퇴실 청소',checkout:'10:30',checkin:'16:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 추가 요청',guestCount:2},
        {room:'459',code:'checkout',kind:'퇴실 청소',checkout:'10:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:3},
        {room:'527',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'531',code:'checkout',kind:'퇴실 청소',checkout:'12:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:3},
        {room:'534',code:'checkout',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 일반',guestCount:2},
        {room:'540',code:'started',kind:'퇴실 청소',checkout:'10:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 사전 청소 시작',guestCount:2},
        {room:'541',code:'stayover',kind:'연박 청소',accessStart:'12:30',requestDue:'14:00',accessEnd:'15:00',deadline:'14:00',source:'stayover',sourceLabel:'연박 청소 신청',guestCount:2},
        {room:'549',code:'stayover',kind:'연박 청소',accessStart:'13:00',requestDue:'14:30',accessEnd:'15:30',deadline:'14:30',source:'stayover',sourceLabel:'연박 청소 신청',guestCount:3},
        {room:'554',code:'manual',kind:'퇴실 청소',checkout:'11:30',checkin:'16:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 추가 청소 요청',guestCount:2},
        {room:'640',code:'stayover',kind:'연박 청소',accessStart:'12:00',requestDue:'14:00',accessEnd:'15:00',deadline:'14:00',source:'stayover',sourceLabel:'연박 청소 신청',guestCount:4},
        {room:'608',code:'stopped',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 운영 중지',guestCount:4},
        {room:'211',code:'candle',kind:'퇴실 청소',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃 · 촛불 회수 필요',guestCount:4}
      ].map(item=>{
        const catalog=ROOM_CATALOG.find(([roomNo])=>roomNo===item.room),type=catalog?.[1]||'standard';
        return Object.freeze({id:`sim-${item.room}-${item.code}-${TOMORROW_ASSIGNMENT_SIMULATION_DATE}`,date:TOMORROW_ASSIGNMENT_SIMULATION_DATE,planDate:TOMORROW_ASSIGNMENT_SIMULATION_DATE,effectiveDate:TOMORROW_ASSIGNMENT_SIMULATION_DATE,type,...item});
      }));
      function applyTomorrowAssignmentSimulation(targetState) {
        const currentIds=new Set((targetState.manualAssignmentTargets||[]).map(item=>item.id));
        targetState.manualAssignmentTargets=targetState.manualAssignmentTargets||[];
        TOMORROW_ASSIGNMENT_SIMULATION_TARGETS.forEach(item=>{if(!currentIds.has(item.id))targetState.manualAssignmentTargets.push({...item});});
        targetState.availabilityHistory=targetState.availabilityHistory||[];
        Object.entries(CURRENT_WEEK_ASSIGNMENT_AVAILABILITY).forEach(([maidId,days],index)=>{
          const id=`availability-${maidId}-2026-08-10-v2`;
          targetState.availabilityHistory=targetState.availabilityHistory.filter(item=>item.id!==id);
          targetState.availabilityHistory.push({id,maidId,weekStart:'2026-08-10',days:[...days],submittedAt:`8/9 ${String(21-Math.floor(index/3)).padStart(2,'0')}:${String(12+index*4).padStart(2,'0')}`,version:2});
        });
        targetState.roomStopped=targetState.roomStopped||{};targetState.roomStopReasons=targetState.roomStopReasons||{};
        targetState.roomStopped['608']=true;targetState.roomStopReasons['608']='608호 운영 중지 · 청소 배정 제외';
        targetState.candles=targetState.candles||{};targetState.candles['211']=Math.max(1,Number(targetState.candles['211']||0));
        targetState.assignments=targetState.assignments||{};
        const notified623={id:'checkout-623-2026-08-16',room:'623',type:'standard',kind:'퇴실 청소',date:'2026-08-16',planDate:'2026-08-16',effectiveDate:'2026-08-16',checkout:'11:00',checkin:'16:00',deadline:'15:30',source:'checkout',sourceLabel:'예약 체크아웃',reservationId:'reservation-demo-623',guestCount:2,rateSnapshot:16000,minutesSnapshot:55,elevatorSnapshot:'A'};
        targetState.assignments[notified623.id]={maidId:'m2',order:1,status:'notified',previousMaidId:'m2',previousOrder:1,notifiedAt:'8월 15일 (토) 18:00',notificationRevision:1,committedTarget:{...notified623}};
        const startedTarget=TOMORROW_ASSIGNMENT_SIMULATION_TARGETS.find(item=>item.room==='540'),attemptId='attempt-540-simulation-20260816';
        targetState.assignments[startedTarget.id]={maidId:'m4',order:1,status:'notified',previousMaidId:'m4',previousOrder:1,notifiedAt:'8월 15일 (토) 09:35',notificationRevision:1,committedTarget:{...startedTarget,rateSnapshot:20000,minutesSnapshot:65,elevatorSnapshot:'C'}};
        targetState.jobs=targetState.jobs||{};targetState.jobs['540']='cleaning';
        targetState.currentAttemptByRoom=targetState.currentAttemptByRoom||{};targetState.currentAttemptByRoom['540']=attemptId;
        targetState.cleaningAttempts=targetState.cleaningAttempts||{};
        targetState.cleaningAttempts[attemptId]={id:attemptId,room:'540',performerId:'m4',performerName:'박소영',status:'cleaning',startedAt:'2026.08.15 09:40',createdAt:'2026.08.15 09:35',workDate:'2026-08-16',effectiveDate:'2026-08-16',workTargetId:startedTarget.id,kind:'퇴실 청소',baseRateSnapshot:20000,checkoutSnapshot:startedTarget.checkout,checkinSnapshot:startedTarget.checkin,deadlineSnapshot:startedTarget.deadline,guestCountSnapshot:startedTarget.guestCount};
        targetState.activeCleaningByMaid=targetState.activeCleaningByMaid||{};targetState.activeCleaningByMaid.m4='540';
        if(targetState.taskInputs?.['332']){
          const task=JSON.parse(JSON.stringify(targetState.taskInputs['332']));task.attemptId=attemptId;task.uploads=(task.uploads||[]).map((upload,index)=>({...upload,status:index===0?'done':'empty'}));targetState.taskInputs['540']=task;
        }
        const room540=ROOMS.find(room=>room.no==='540'),room623=ROOMS.find(room=>room.no==='623');
        if(room540){room540.assignee='박소영';room540.cleaning='cleaning';}
        if(room623)room623.assignee='김민지2';
        return targetState;
      }
'''

insert_marker = "      const WORK_HISTORY_FIXTURES = ["
if html.count(insert_marker) != 1:
    raise SystemExit(f"simulation insertion marker mismatch: {html.count(insert_marker)}")
html = html.replace(insert_marker, simulation_source + "\n" + insert_marker, 1)

replace_once(
    "        const s = baseState(id);",
    "        const s = baseState(id);\n        if(Number(id)===0)applyTomorrowAssignmentSimulation(s);",
    "default-scenario simulation fixture",
)

replace_function(
    "renderAvailabilityMatrix",
    r'''function renderAvailabilityMatrix() {
        const start=weekStartIso(state.assignmentDate),days=['월','화','수','목','금','토','일'].map((name,index)=>{const iso=addIsoDays(start,index);return {name,iso,day:Number(iso.slice(8))};});
        return `<div class="availability-matrix-wrap"><table class="availability-matrix"><thead><tr><th scope="col">메이드</th>${days.map(day=>`<th scope="col">${day.name} ${day.day}</th>`).join('')}</tr></thead><tbody>${MAIDS.map(maid=>`<tr><th scope="row">${esc(maid.name)}</th>${days.map((day,index)=>`<td>${availabilityCell(maid.id,index,day.iso)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="assignment-foot"><p>✓ 가능 · × 불가 · — 미제출. ${days[assignmentDayIndex()].name}요일 배정 후보는 해당 날짜 가능 제출자만 표시합니다.</p></div>`;
      }''',
)

replace_function(
    "roomIsOnHold",
    r'''function assignmentRoomHoldReason(no,targetState=state){
        const roomNo=String(no),dataIssue=roomDataIssue(roomNo);if(dataIssue)return dataIssue;
        if(targetState?.roomStopped?.[roomNo])return targetState.roomStopReasons?.[roomNo]||'운영 중지 · 청소 배정 제외';
        const candleCount=Number(targetState?.candles?.[roomNo]||0);if(candleCount>0)return `촛불 ${candleCount}개 회수 후 배정 가능`;
        return '';
      }
      function roomIsOnHold(no){return !!assignmentRoomHoldReason(no);}''',
)

replace_function(
    "cleaningTargetAdjustmentBlock",
    r'''function cleaningTargetAdjustmentBlock(target) {
        if(!target)return '';
        const holdReason=assignmentRoomHoldReason(target.room);if(holdReason)return holdReason;
        if(target.kind==='재청소')return '재청소는 기존 수행자가 완료해야 합니다.';
        if(target.carryReason==='access-review')return 'PIN·출입 영향 확인이 끝난 뒤 조정할 수 있습니다.';
        const attempt=attemptForCleaningTarget(target);
        const roomAttempt=targetEffectiveDate(target)===state.selectedDate?activeUnfinishedAttempt(target.room):null;
        if(roomAttempt&&roomAttempt.workTargetId!==target.id)return roomAttempt.status==='submitted'?'이 객실의 이전 청소 검수가 남아 검수 대기에서 먼저 종결해야 합니다.':'이 객실의 다른 청소가 진행 중이라 청소 상세에서 조정해야 합니다.';
        if(!attempt)return '';
        if(attempt.startedAt||attempt.completedAt||!['active','scheduled'].includes(attempt.status))return '이미 시작한 청소는 진행 중에서 조정합니다.';
        return '';
      }''',
)

HTML_PATH.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 배정 대상일 주차와 대규모 랜덤 배정 목업 (2026-08-29)

- 오늘·내일 배정의 메이드 근무표는 고정된 다음 주가 아니라 `배정 대상일이 속한 월요일–일요일`을 표시한다. 따라서 8월 15일과 16일은 8월 10일–16일, 8월 17일은 8월 17일–23일을 사용한다.
- 8월 10일–16일 근무표는 등록된 9명 전원의 제출 기록을 가진다. 8월 16일은 30실 이상 랜덤 배정을 시험할 수 있도록 9명 모두 근무 가능으로 구성하고, 다른 요일은 서로 다르게 유지한다.
- 기본 목업의 8월 16일 청소대상은 자동 체크아웃을 포함해 36실이다. 일반 퇴실, 얼리 체크인, 레이트 체크아웃, 연박 청소, 현장 직접 추가, 통보 완료, 사전 시작, 정보 확인, 운영 중지, 촛불 회수 필요 상태를 함께 둔다.
- 랜덤 배정은 이 중 근무 가능·활성 계정·미배정·조정 가능 객실만 사용한다. 기존 통보, 이미 시작한 청소, 정보 확인·운영 중지·촛불 회수 대상은 보존한다.
- 랜덤 결과는 저장 전 초안이며 `랜덤 배정 전으로 되돌리기`로 정확히 복구한다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-29 · 배정 주차 일치와 내일 36실 랜덤 배정 목업

- 오늘 8월 15일과 내일 8월 16일 배정에서 근무표가 `월 10`부터 `일 16`까지 표시되는지 확인한다.
- 8월 17일 배정에서는 `월 17`부터 `일 23`까지 표시되는지 확인한다.
- 내일 배정의 청소대상이 36실이고, 8월 16일에 9명 모두 근무 가능 후보인지 확인한다.
- 얼리·레이트·연박·직접 추가·통보 완료·이미 시작·정보 확인·운영 중지·촛불 회수 필요 사례가 표에 함께 표시되는지 확인한다.
- 랜덤 배정 전후로 통보 완료·진행 중·차단 객실의 담당과 잠금이 바뀌지 않는지 확인한다.
- 되돌리기 뒤 모든 담당 선택값과 예약·청소·검수·급여 원장이 실행 전과 같은지 확인한다.
- 390px·768px·1440px에서 가로 넘침과 콘솔·런타임 오류가 없는지 확인한다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
legacy_block = """const workforceMatrixStart = html.indexOf('function renderAvailabilityMatrix()');
if (workforceMatrixStart < 0) throw new Error('Workforce availability matrix source could not be isolated.');
const workforceMatrixSource = html.slice(workforceMatrixStart, workforceMatrixStart + 5000);
if (!workforceMatrixSource.includes(\"const start='2026-08-17'\")) {
  throw new Error('Workforce matrix must stay on the submitted 2026-08-17 next-week schedule.');
}
if (workforceMatrixSource.includes('weekStartIso(state.assignmentDate)')) {
  throw new Error('Workforce matrix must not drift with the cleaning assignment date.');
}
console.log('All-maid availability and work-history fixture contracts: passed');"""
replacement_block = """const workforceMatrixStart = html.indexOf('function renderAvailabilityMatrix()');
if (workforceMatrixStart < 0) throw new Error('Workforce availability matrix source could not be isolated.');
const workforceMatrixSource = html.slice(workforceMatrixStart, workforceMatrixStart + 5000);
if (!workforceMatrixSource.includes('const start=weekStartIso(state.assignmentDate)')) {
  throw new Error('Workforce matrix must use the assignment date week.');
}
if (workforceMatrixSource.includes(\"const start='2026-08-17'\")) {
  throw new Error('Legacy fixed 2026-08-17 workforce week remains.');
}
console.log('All-maid availability and work-history fixture contracts: passed');"""
if checker.count(legacy_block) != 1:
    raise SystemExit(f"legacy fixed-week checker mismatch: {checker.count(legacy_block)}")
checker = checker.replace(legacy_block, replacement_block, 1).rstrip()
checker += r'''

const issue114SimulationContracts = [
  'const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY = Object.freeze({',
  "const TOMORROW_ASSIGNMENT_SIMULATION_DATE='2026-08-16'",
  'const TOMORROW_ASSIGNMENT_SIMULATION_TARGETS = Object.freeze([',
  'function applyTomorrowAssignmentSimulation(targetState)',
  "if(Number(id)===0)applyTomorrowAssignmentSimulation(s)",
  "targetState.roomStopped['608']=true",
  "targetState.candles['211']=Math.max(1",
  "targetState.assignments[notified623.id]",
  "workTargetId:startedTarget.id",
  'function assignmentRoomHoldReason(no,targetState=state)',
  "return `촛불 ${candleCount}개 회수 후 배정 가능`",
  "const start=weekStartIso(state.assignmentDate)",
];
for (const contract of issue114SimulationContracts) {
  if (!html.includes(contract)) throw new Error(`Issue #114 assignment fixture contract missing: ${contract}`);
}
const issue114TargetSourceStart = html.indexOf('const TOMORROW_ASSIGNMENT_SIMULATION_TARGETS');
const issue114TargetSourceEnd = html.indexOf('function applyTomorrowAssignmentSimulation', issue114TargetSourceStart);
const issue114TargetSource = html.slice(issue114TargetSourceStart, issue114TargetSourceEnd);
const issue114TargetRooms = [...issue114TargetSource.matchAll(/room:'(\d+)'/g)].map(match=>match[1]);
if (issue114TargetRooms.length !== 35 || new Set(issue114TargetRooms).size !== 35) {
  throw new Error(`Tomorrow simulation target fixture mismatch: ${issue114TargetRooms.length} rows / ${new Set(issue114TargetRooms).size} unique rooms.`);
}
for (const roomNo of ['516','556','541','455','540','762','608','211']) {
  if (!issue114TargetRooms.includes(roomNo)) throw new Error(`Required varied-state fixture missing: ${roomNo}`);
}
const issue114AvailabilityStart = html.indexOf('const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY');
const issue114AvailabilityEnd = html.indexOf('const TOMORROW_ASSIGNMENT_SIMULATION_DATE', issue114AvailabilityStart);
const issue114AvailabilitySource = html.slice(issue114AvailabilityStart, issue114AvailabilityEnd);
for (let maidIndex=1;maidIndex<=9;maidIndex+=1) {
  const match=issue114AvailabilitySource.match(new RegExp(`m${maidIndex}:Object\\.freeze\\(\\[([^\\]]+)\\]\\)`));
  if (!match || !match[1].split(',').map(value=>Number(value.trim())).includes(6)) {
    throw new Error(`Maid m${maidIndex} must be available on simulation Sunday.`);
  }
}
console.log('Issue #114 assignment-week and varied-fixture static contracts: passed');
'''
checker_path.write_text(checker + "\n", encoding="utf-8")

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
manifest["version"] = "2026-08-29-assignment-week-varied-fixtures"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
