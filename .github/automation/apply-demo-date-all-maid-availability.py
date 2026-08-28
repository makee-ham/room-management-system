from __future__ import annotations

import hashlib
import json
import re
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


def replace_count(old: str, new: str, expected: int, label: str) -> None:
    global html
    count = html.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} matches, found {count}")
    html = html.replace(old, new)


# 1) Keep the quick-reservation mock anchored to the fixture's operating day.
replace_once(
    "quickReservationAnchorDate:null, quickReservationFollowsToday:true",
    "quickReservationAnchorDate:DEMO_TODAY, quickReservationFollowsToday:true",
    "quick reservation base anchor",
)
replace_once(
    "const today=kstTodayIso();",
    "const today=DEMO_TODAY;",
    "quick reservation demo today refresh",
)
replace_count(
    "else{state.quickReservationAnchorDate=kstTodayIso();state.quickReservationFollowsToday=true;}",
    "else{state.quickReservationAnchorDate=DEMO_TODAY;state.quickReservationFollowsToday=true;}",
    2,
    "quick reservation route fallbacks",
)
replace_once(
    "state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=kstTodayIso();",
    "state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;",
    "quick reservation reset button",
)
replace_once(
    'data-action="quick-month-today">오늘</button>',
    'data-action="quick-month-today">기준일</button>',
    "quick reservation reset label",
)
replace_once(
    "state.quickReservationFollowsToday===false?'이동한 29일':'오늘 기준 29일'",
    "state.quickReservationFollowsToday===false?'이동한 29일':'8월 15일 기준 29일'",
    "quick reservation anchor status label",
)
replace_once(
    "state.quickReservationFollowsToday===false?'선택 기준 -7일 / +21일':'오늘 기준 -7일 / +21일'",
    "state.quickReservationFollowsToday===false?'선택 기준 -7일 / +21일':'8월 15일 기준 -7일 / +21일'",
    "quick reservation grid status label",
)
replace_once(
    "<h2>한국 시간 오늘 기준 29일을 한 화면에서 예약하세요</h2><p>매일 실제 오늘의 7일 전부터 21일 뒤까지 월 경계 없이 이어서 표시합니다.</p>",
    "<h2>목업 기준일 8월 15일 전후 29일을 한 화면에서 예약하세요</h2><p>8월 15일의 7일 전부터 21일 뒤까지 월 경계 없이 이어서 표시합니다.</p>",
    "quick reservation hero copy",
)
replace_once(
    "<h2>간편 예약</h2>${infoTip('quick-booking'",
    "<h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking'",
    "admin concise quick reservation title",
)

# 2) Every active maid submits the next-week schedule and is available on the
#    random-assignment simulation date, Monday 2026-08-17.
replace_once(
    "m2:{days:[1,2,3,4,5],status:'submitted',submittedAt:'8/16 20:42'}",
    "m2:{days:[0,1,2,3,4,5],status:'submitted',submittedAt:'8/16 20:42'}",
    "m2 current availability",
)
replace_once(
    "m7:{days:[1,2,4],status:'submitted',submittedAt:'8/16 18:56'}",
    "m7:{days:[0,1,2,4],status:'submitted',submittedAt:'8/16 18:56'}",
    "m7 current availability",
)
replace_once(
    "{id:'availability-m2-2026-08-17-v1',maidId:'m2',weekStart:'2026-08-17',days:[1,2,3,4,5],submittedAt:'8/16 20:42',version:1}",
    "{id:'availability-m2-2026-08-17-v1',maidId:'m2',weekStart:'2026-08-17',days:[0,1,2,3,4,5],submittedAt:'8/16 20:42',version:1}",
    "m2 availability history",
)
replace_once(
    "{id:'availability-m7-2026-08-17-v1',maidId:'m7',weekStart:'2026-08-17',days:[1,2,4],submittedAt:'8/16 18:56',version:1}",
    "{id:'availability-m7-2026-08-17-v1',maidId:'m7',weekStart:'2026-08-17',days:[0,1,2,4],submittedAt:'8/16 18:56',version:1}",
    "m7 availability history",
)

old_availability_notice = "{id:'notification-seed-admin-availability',title:'다음 주 가능일 미제출 2명',time:'09:30',createdAt:'2026-08-15 09:30',detail:'마감 전 한 번만 묶어 알립니다.',maidIds:[],notify:true,audience:['admin'],category:'availability',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-workforce'},groupKey:'admin:availability:next-week',readBy:[]}"
new_availability_notice = "{id:'notification-seed-admin-availability',title:'다음 주 가능일 전원 제출 완료',time:'09:30',createdAt:'2026-08-15 09:30',detail:'등록된 메이드 9명이 모두 근무 가능일을 제출했습니다.',maidIds:[],notify:true,audience:['admin'],category:'availability',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-workforce'},groupKey:'admin:availability:next-week',readBy:['admin']}"
replace_once(old_availability_notice, new_availability_notice, "availability notification fixture")

# 3) The historical weekly schedule must include the six added maids too.
work_history_pattern = re.compile(
    r"      const WORK_HISTORY_FIXTURES = \[[\s\S]*?\n      \];\n      const PAYROLL_CLEANING_FIXTURES = \{"
)
work_history_replacement = """      const WORK_HISTORY_FIXTURES = [
        {
          start:'2026-08-10',status:'마감 기록',
          records:{
            m1:{nameSnapshot:'김민지1',submitted:[0,1,3,4,5],assigned:[0,1,3,4],completed:[0,1,3,4],submittedAt:'8/9 21:14'},
            m2:{nameSnapshot:'김민지2',submitted:[1,2,4,5],assigned:[1,4,5],completed:[1,4],submittedAt:'8/9 20:38'},
            m3:{nameSnapshot:'이서연',submitted:[0,2,3,4,5,6],assigned:[0,2,3,5,6],completed:[0,2,3,5,6],submittedAt:'8/9 19:51'},
            m4:{nameSnapshot:'박소영',submitted:[0,1,2,3,4],assigned:[0,2,4],completed:[0,2,4],submittedAt:'8/9 19:34'},
            m5:{nameSnapshot:'최은지',submitted:[0,2,3,5],assigned:[0,3,5],completed:[0,3,5],submittedAt:'8/9 19:18'},
            m6:{nameSnapshot:'정다현',submitted:[0,1,4,5],assigned:[1,4,5],completed:[1,4,5],submittedAt:'8/9 19:02'},
            m7:{nameSnapshot:'오세라',submitted:[1,2,4],assigned:[1,2,4],completed:[1,2,4],submittedAt:'8/9 18:51'},
            m8:{nameSnapshot:'한지민',submitted:[0,1,2,3,4,5],assigned:[0,2,3,5],completed:[0,2,3,5],submittedAt:'8/9 18:36'},
            m9:{nameSnapshot:'윤가영',submitted:[0,3,4,6],assigned:[0,3,6],completed:[0,3,6],submittedAt:'8/9 18:22'}
          }
        },
        {
          start:'2026-08-03',status:'마감 기록',
          records:{
            m1:{nameSnapshot:'김민지1',submitted:[0,1,2,4,6],assigned:[0,1,4,6],completed:[0,1,4,6],submittedAt:'8/2 21:06'},
            m2:{nameSnapshot:'김민지2',submitted:[1,2,3,4,5],assigned:[1,2,3,5],completed:[1,2,3,5],submittedAt:'8/2 20:19'},
            m3:{nameSnapshot:'이서연',submitted:[0,2,3,4,6],assigned:[0,2,4,6],completed:[0,2,4,6],submittedAt:'8/2 19:43'},
            m4:{nameSnapshot:'박소영',submitted:[0,1,3,4,6],assigned:[0,3,4],completed:[0,3,4],submittedAt:'8/2 19:27'},
            m5:{nameSnapshot:'최은지',submitted:[0,2,4,5],assigned:[0,2,5],completed:[0,2,5],submittedAt:'8/2 19:12'},
            m6:{nameSnapshot:'정다현',submitted:[1,2,3,5],assigned:[1,3,5],completed:[1,3,5],submittedAt:'8/2 18:58'},
            m7:{nameSnapshot:'오세라',submitted:[0,2,4,6],assigned:[0,4,6],completed:[0,4,6],submittedAt:'8/2 18:43'},
            m8:{nameSnapshot:'한지민',submitted:[0,1,2,3,4,5],assigned:[1,2,4,5],completed:[1,2,4,5],submittedAt:'8/2 18:31'},
            m9:{nameSnapshot:'윤가영',submitted:[0,3,5,6],assigned:[0,3,6],completed:[0,3,6],submittedAt:'8/2 18:17'}
          }
        },
        {
          start:'2026-07-27',status:'마감 기록',
          records:{
            m1:{nameSnapshot:'김민지1',submitted:[0,1,3,4],assigned:[0,1,3],completed:[0,1,3],submittedAt:'7/26 20:58'},
            m2:{nameSnapshot:'김민지2',submitted:[1,2,4,5],assigned:[1,2,5],completed:[1,2,5],submittedAt:'7/26 20:22'},
            m3:{nameSnapshot:'이서연',submitted:[0,2,3,4,5,6],assigned:[0,2,3,4,6],completed:[0,2,3,4,6],submittedAt:'7/26 19:36'},
            m4:{nameSnapshot:'박소영',submitted:[0,1,2,4,5],assigned:[0,2,5],completed:[0,2,5],submittedAt:'7/26 19:21'},
            m5:{nameSnapshot:'최은지',submitted:[0,2,3,4],assigned:[0,3,4],completed:[0,3,4],submittedAt:'7/26 19:06'},
            m6:{nameSnapshot:'정다현',submitted:[1,2,4,5],assigned:[1,2,5],completed:[1,2,5],submittedAt:'7/26 18:52'},
            m7:{nameSnapshot:'오세라',submitted:[0,1,3,6],assigned:[0,3,6],completed:[0,3,6],submittedAt:'7/26 18:38'},
            m8:{nameSnapshot:'한지민',submitted:[0,1,2,3,4,5],assigned:[0,1,4,5],completed:[0,1,4,5],submittedAt:'7/26 18:24'},
            m9:{nameSnapshot:'윤가영',submitted:[0,2,4,6],assigned:[0,2,6],completed:[0,2,6],submittedAt:'7/26 18:09'}
          }
        }
      ];
      const PAYROLL_CLEANING_FIXTURES = {"""
html, work_history_count = work_history_pattern.subn(work_history_replacement, html, count=1)
if work_history_count != 1:
    raise SystemExit(f"work history fixtures: expected exactly one match, found {work_history_count}")

HTML_PATH.write_text(html, encoding="utf-8")

# 4) Update operator documentation without leaving the former real-date policy behind.
readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8")
readme_section_pattern = re.compile(
    r"## 간편 예약 29일 연속 보기 \(2026-08-25\)\n[\s\S]*?(?=\n## )"
)
readme_section = """## 간편 예약 29일 연속 보기 (2026-08-29)

- 목업의 고정 기준일 `2026-08-15`를 간편 예약의 기본 오늘로 사용한다.
- 기본 범위는 `2026-08-08 ~ 2026-09-05`, 양 끝을 포함한 29일이다. 브라우저의 실제 날짜가 바뀌어도 이 목업 범위는 움직이지 않는다.
- 첫 진입과 `기준일` 복귀 시 8월 15일 열이 객실 정보 열 바로 옆에 오도록 가로 위치를 자동 정렬한다.
- 이전·다음 버튼은 현재 기준일을 7일씩 이동하고 `이동한 29일` 모드로 전환한다.
- `기준일` 버튼을 누르면 다시 2026년 8월 15일 기준 범위로 복귀한다.
- 명시적인 `bookingAnchor`와 과거 `bookingMonth` 링크는 사용자 지정 범위로 계속 보존한다.
"""
readme, readme_count = readme_section_pattern.subn(readme_section.rstrip(), readme, count=1)
if readme_count != 1:
    raise SystemExit(f"quick reservation README section: expected exactly one match, found {readme_count}")
if "## 전체 메이드 근무표·랜덤 배정 데모 (2026-08-29)" not in readme:
    readme = readme.rstrip() + """

## 전체 메이드 근무표·랜덤 배정 데모 (2026-08-29)

- 등록된 메이드 9명 모두 `2026-08-17 ~ 2026-08-23` 근무 가능일을 제출한 상태로 시작한다.
- 랜덤 배정 시뮬레이션 기준일인 8월 17일 월요일은 9명 전원이 근무 가능하다.
- 다른 요일은 메이드별로 서로 다르게 작성해 근무표 필터와 날짜별 후보 변화를 확인할 수 있다.
- 주간 근무 기록의 8월 10일·8월 3일·7월 27일 주차도 9명 전원의 제출·배정·완료 기록을 포함한다.
- 시나리오 2는 확장 청소대상을 사용하므로 랜덤 초안 뒤 9명 전원의 순서 보드를 비교할 수 있다.
"""
readme_path.write_text(readme.rstrip() + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8")
qa = qa.replace("- 검증일: 2026-08-25", "- 검증일: 2026-08-29", 1)
qa_section_pattern = re.compile(
    r"## 2026-08-25 · 간편 예약 한국 시간 실제 오늘 기준 29일\n[\s\S]*?(?=\n## )"
)
qa_section = """## 2026-08-29 · 간편 예약 목업 기준일 8월 15일

### 변경

- 간편 예약 기본 오늘을 브라우저 실제 날짜가 아니라 목업 기준일 `2026-08-15`로 고정했다.
- 기본 범위는 `2026-08-08 ~ 2026-09-05`, 총 29일이다.
- 좌우 7일 이동은 사용자 지정 범위로 전환하고, `기준일`을 누르면 8월 15일 기준 범위로 복귀한다.
- 기본 URL과 기록 복원에서도 별도 앵커가 없으면 8월 15일을 사용한다.
- 오늘 강조와 과거 날짜 잠금 역시 목업의 8월 15일을 기준으로 계산한다.

### 검증

- 1440px·390px에서 첫 열 8월 8일, 오늘 열 8월 15일, 마지막 열 9월 5일과 총 29개 날짜 열을 확인한다.
- 7일 이동 뒤 `기준일`을 누르면 동일 범위와 8월 15일 오늘 강조가 복원되는지 확인한다.
- 기존 `bookingAnchor`와 `bookingMonth` 링크의 사용자 지정 범위 호환을 확인한다.
- 문서 가로 넘침과 브라우저 콘솔·런타임 오류가 없는지 확인한다.
"""
qa, qa_count = qa_section_pattern.subn(qa_section.rstrip(), qa, count=1)
if qa_count != 1:
    raise SystemExit(f"quick reservation QA section: expected exactly one match, found {qa_count}")
if "## 2026-08-29 · 전체 메이드 근무표와 랜덤 배정" not in qa:
    qa = qa.rstrip() + """

## 2026-08-29 · 전체 메이드 근무표와 랜덤 배정

- 메이드 주간 근무표에 9명 전원이 나타나고 제출 현황이 `9/9 제출`인지 확인한다.
- 8월 17일 월요일 셀이 9명 모두 `✓ 가능`인지 확인한다.
- 최근 세 주의 주간 근무 기록에 각 주차마다 9명 전원이 포함되는지 확인한다.
- 시나리오 2의 내일 배정에서 `근무 가능 9명`이 표시되는지 확인한다.
- 동선 고려 랜덤 배정 실행 뒤 메이드별 순서 보드가 9명 전원에 대해 생성되는지 확인한다.
- 390px·1440px에서 담당 선택·랜덤 실행·되돌리기와 가로 넘침, 콘솔·런타임 오류를 확인한다.
"""
qa_path.write_text(qa.rstrip() + "\n", encoding="utf-8")

# 5) Replace the former real-KST quick-window contract and add large-team fixtures checks.
checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
kst_check_pattern = re.compile(
    r"for \(const pr94KstDailyContract of \[[\s\S]*?console\.log\('KST daily quick-window static contracts: passed'\);"
)
demo_check = r'''for (const demoQuickWindowContract of [
  "const DEMO_TODAY='2026-08-15'",
  'quickReservationAnchorDate:DEMO_TODAY, quickReservationFollowsToday:true',
  'function refreshQuickReservationActualToday({rerender=false}={})',
  'const today=DEMO_TODAY;',
  'else{state.quickReservationAnchorDate=DEMO_TODAY;state.quickReservationFollowsToday=true;}',
  'state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;',
  'data-action="quick-month-today">기준일</button>',
  '8월 15일 기준 29일',
  '간편 예약 · 8월 15일 기준',
  "today=iso===actualToday,isPast=iso<actualToday",
]) {
  if (!html.includes(demoQuickWindowContract)) throw new Error(`Demo-date quick-window contract missing: ${demoQuickWindowContract}`);
}
for (const liveDateQuickWindowContract of [
  'const today=kstTodayIso();',
  'state.quickReservationAnchorDate=kstTodayIso()',
  '한국 시간 오늘 기준 29일',
  '매일 실제 오늘의 7일 전부터 21일 뒤까지',
]) {
  if (html.includes(liveDateQuickWindowContract)) throw new Error(`Live-date quick-window coupling remains in the mock: ${liveDateQuickWindowContract}`);
}
if (!wireframeReadme.includes('목업의 고정 기준일 `2026-08-15`')) {
  throw new Error('Demo-date quick-window README policy is missing.');
}
console.log('Demo-date quick-window static contracts: passed');'''
checker, kst_check_count = kst_check_pattern.subn(demo_check, checker, count=1)
if kst_check_count != 1:
    raise SystemExit(f"KST quick-window checker block: expected exactly one match, found {kst_check_count}")

large_team_check = r'''

const upcomingAvailabilityMatch = html.match(/weeklyAvailability:\{\n([\s\S]*?)\n\s*\},\n\s*availabilityHistory:/);
if (!upcomingAvailabilityMatch) throw new Error('Next-week availability fixture could not be isolated.');
const upcomingAvailabilityRows = [...upcomingAvailabilityMatch[1].matchAll(/(m\d+):\{days:\[([^\]]*)\],status:'submitted'/g)].map(match => ({
  maidId: match[1],
  days: match[2].split(',').filter(Boolean).map(Number),
}));
if (upcomingAvailabilityRows.length !== 9 || new Set(upcomingAvailabilityRows.map(row => row.maidId)).size !== 9) {
  throw new Error(`Next-week availability fixture mismatch: ${upcomingAvailabilityRows.length} submitted rows.`);
}
const unavailableOnSimulationMonday = upcomingAvailabilityRows.filter(row => !row.days.includes(0)).map(row => row.maidId);
if (unavailableOnSimulationMonday.length) {
  throw new Error(`Random-assignment simulation Monday is unavailable for: ${unavailableOnSimulationMonday.join(', ')}`);
}
const upcomingHistoryStart = html.indexOf('availabilityHistory:[');
const upcomingHistoryEnd = html.indexOf("assignmentDate:'2026-08-17'", upcomingHistoryStart);
const upcomingHistorySource = html.slice(upcomingHistoryStart, upcomingHistoryEnd);
const upcomingHistoryRows = [...upcomingHistorySource.matchAll(/maidId:'(m\d+)',weekStart:'2026-08-17',days:\[([^\]]*)\]/g)].map(match => ({
  maidId: match[1],
  days: match[2].split(',').filter(Boolean).map(Number),
}));
if (upcomingHistoryRows.length !== 9 || upcomingHistoryRows.some(row => !row.days.includes(0))) {
  throw new Error('Next-week availability history must contain nine Monday-available maid records.');
}
const workHistoryStart = html.indexOf('const WORK_HISTORY_FIXTURES = [');
const workHistoryEnd = html.indexOf('const PAYROLL_CLEANING_FIXTURES = {', workHistoryStart);
const workHistorySource = html.slice(workHistoryStart, workHistoryEnd);
if (workHistoryStart < 0 || workHistoryEnd < 0) throw new Error('Weekly work-history fixture could not be isolated.');
for (const maidId of maidIds) {
  const count = [...workHistorySource.matchAll(new RegExp(`${maidId}:\\{nameSnapshot:`, 'g'))].length;
  if (count !== 3) throw new Error(`Weekly work-history fixture must contain ${maidId} in all three weeks; found ${count}.`);
}
if (html.includes('다음 주 가능일 미제출 2명')) throw new Error('Stale missing-availability notification remains.');
for (const contract of [
  "title:'다음 주 가능일 전원 제출 완료'",
  "detail:'등록된 메이드 9명이 모두 근무 가능일을 제출했습니다.'",
  'return MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,state.assignmentDate)===\'available\');',
  '<strong>${eligible.length}명</strong>',
]) {
  if (!html.includes(contract)) throw new Error(`All-maid random-assignment contract missing: ${contract}`);
}
console.log('All-maid availability and work-history fixture contracts: passed');
'''
if "All-maid availability and work-history fixture contracts: passed" in checker:
    raise SystemExit("all-maid checker already exists unexpectedly")
checker = checker.rstrip() + large_team_check + "\n"
checker_path.write_text(checker, encoding="utf-8")

# Refresh integrity metadata for the single-file application.
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
manifest["version"] = "2026-08-29-demo-date-all-maid-availability"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
