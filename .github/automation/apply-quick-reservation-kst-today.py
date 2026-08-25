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


def replace_last(old: str, new: str, label: str) -> None:
    global html
    index = html.rfind(old)
    if index < 0:
        raise SystemExit(f"{label}: marker not found")
    html = html[:index] + new + html[index + len(old):]


def function_slice(start_marker: str, end_marker: str, label: str) -> tuple[int, int, str]:
    start = html.rfind(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = html.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    return start, end, html[start:end]


def replace_function(start_marker: str, end_marker: str, transform, label: str) -> None:
    global html
    start, end, source = function_slice(start_marker, end_marker, label)
    updated = transform(source)
    if updated == source:
        raise SystemExit(f"{label}: transform made no change")
    html = html[:start] + updated + html[end:]


# 1. 한국 시간 실제 오늘 계산 도우미.
if "function kstTodayIso(" not in html:
    marker = "      const cloneReservation="
    if html.count(marker) != 1:
        raise SystemExit(f"KST helper marker mismatch: {html.count(marker)}")
    helper = """      function kstTodayIso(now=new Date()) {
        const parts=Object.fromEntries(new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now).filter(part=>part.type!=='literal').map(part=>[part.type,part.value]));
        return `${parts.year}-${parts.month}-${parts.day}`;
      }

"""
    html = html.replace(marker, helper + marker, 1)

# 2. 기본 상태와 시나리오는 데모 운영일이 아니라 KST 실제 오늘을 따른다.
replace_once(
    "quickReservationAnchorDate:'2026-08-15', quickReservationType:",
    "quickReservationAnchorDate:null, quickReservationFollowsToday:true, quickReservationType:",
    "quick reservation state defaults",
)
replace_once(
    "        s.quickReservationAnchorDate=s.selectedDate;",
    "        s.quickReservationAnchorDate=kstTodayIso();s.quickReservationFollowsToday=true;",
    "quick reservation scenario anchor",
)

# 3. 오늘 추적 모드는 URL에 날짜를 고정하지 않고, 수동 이동만 bookingAnchor를 보존한다.
replace_once(
    "quickAnchor:state.quickReservationAnchorDate,quickType:state.quickReservationType",
    "quickAnchor:state.quickReservationFollowsToday===false?state.quickReservationAnchorDate:null,quickType:state.quickReservationType",
    "history route quick anchor",
)
replace_once(
    "if(route.quickAnchor&&route.quickAnchor!==route.date)params.set('bookingAnchor',route.quickAnchor);",
    "if(route.quickAnchor)params.set('bookingAnchor',route.quickAnchor);",
    "history URL quick anchor",
)
replace_once(
    "        if(routeQuickAnchor)state.quickReservationAnchorDate=routeQuickAnchor;",
    "        if(routeQuickAnchor){state.quickReservationAnchorDate=routeQuickAnchor;state.quickReservationFollowsToday=false;}else{state.quickReservationAnchorDate=kstTodayIso();state.quickReservationFollowsToday=true;}",
    "history route restore mode",
)

# 4. 열린 오늘 추적 화면은 KST 날짜 변경을 감지한다. 수동 이동 중에는 건드리지 않는다.
watch_marker = "      const QUICK_RESERVATION_PAST_DAYS=7,QUICK_RESERVATION_FUTURE_DAYS=21,QUICK_RESERVATION_DAY_COUNT=QUICK_RESERVATION_PAST_DAYS+1+QUICK_RESERVATION_FUTURE_DAYS;\n"
if html.count(watch_marker) != 1:
    raise SystemExit(f"quick reservation constants mismatch: {html.count(watch_marker)}")
watch_runtime = """      const QUICK_RESERVATION_PAST_DAYS=7,QUICK_RESERVATION_FUTURE_DAYS=21,QUICK_RESERVATION_DAY_COUNT=QUICK_RESERVATION_PAST_DAYS+1+QUICK_RESERVATION_FUTURE_DAYS;
      let quickReservationTodayWatchTimer=0;
      function refreshQuickReservationActualToday({rerender=false}={}) {
        const today=kstTodayIso();
        if(state.quickReservationFollowsToday===false||state.quickReservationAnchorDate===today)return today;
        state.quickReservationAnchorDate=today;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;
        if(rerender&&state.role==='admin'&&state.adminView==='quickReservation'&&!state.detail)render();
        return today;
      }
      function startQuickReservationTodayWatch() {
        if(quickReservationTodayWatchTimer)return;
        quickReservationTodayWatchTimer=window.setInterval(()=>refreshQuickReservationActualToday({rerender:true}),30000);
      }
      startQuickReservationTodayWatch();
"""
html = html.replace(watch_marker, watch_runtime, 1)

# 5. 과거 잠금과 오늘 강조는 실제 KST 오늘을 사용한다.
def patch_quick_cell(source: str) -> str:
    source = source.replace(
        "function quickCellMarkup(room,iso,rowIndex,dayIndex) {",
        "function quickCellMarkup(room,iso,rowIndex,dayIndex,todayIso=kstTodayIso()) {",
        1,
    )
    source, count = re.subn(r"isPast=iso<state\.selectedDate", "isPast=iso<todayIso", source, count=1)
    if count != 1:
        raise SystemExit(f"quick cell past-date replacement mismatch: {count}")
    return source


replace_function(
    "      function quickCellMarkup(room,iso,rowIndex,dayIndex)",
    "      function renderQuickReservation()",
    patch_quick_cell,
    "quick cell actual-today logic",
)


def patch_quick_render(source: str) -> str:
    source, count = re.subn(
        r"(function renderQuickReservation\(\) \{\n\s*)const dates=quickWindowDates\(\),",
        r"\1const actualToday=refreshQuickReservationActualToday({rerender:false}),dates=quickWindowDates(),",
        source,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"quick render actual-today prelude mismatch: {count}")
    source = source.replace(
        "today=iso===state.selectedDate,isPast=iso<state.selectedDate",
        "today=iso===actualToday,isPast=iso<actualToday",
        1,
    )
    source = source.replace(
        "quickCellMarkup(room,iso,rowIndex,dayIndex)",
        "quickCellMarkup(room,iso,rowIndex,dayIndex,actualToday)",
        1,
    )
    source = source.replace(
        "<h2>오늘 전후 29일을 한 화면에서 예약하세요</h2><p>지난 7일은 조회만 가능하고, 오늘부터 21일 뒤까지 월 경계 없이 이어서 예약할 수 있습니다.</p>",
        "<h2>한국 시간 오늘 기준 29일을 한 화면에서 예약하세요</h2><p>매일 실제 오늘의 7일 전부터 21일 뒤까지 월 경계 없이 이어서 표시합니다.</p>",
        1,
    )
    source = source.replace(
        "<small>29일</small>",
        "<small>${state.quickReservationFollowsToday===false?'이동한 29일':'오늘 기준 29일'}</small>",
        1,
    )
    source = source.replace(
        "<span>오늘 기준 -7일 / +21일 · 7일씩 이동</span>",
        "<span>${state.quickReservationFollowsToday===false?'선택 기준 -7일 / +21일':'오늘 기준 -7일 / +21일'} · 7일씩 이동</span>",
        1,
    )
    for contract in [
        "actualToday=refreshQuickReservationActualToday",
        "today=iso===actualToday,isPast=iso<actualToday",
        "quickCellMarkup(room,iso,rowIndex,dayIndex,actualToday)",
        "오늘 기준 29일",
        "이동한 29일",
    ]:
        if contract not in source:
            raise SystemExit(f"quick render contract missing after patch: {contract}")
    return source


replace_function(
    "      function renderQuickReservation()",
    "      function quickGridUsesInternalVerticalScroll()",
    patch_quick_render,
    "quick reservation render",
)

# 6. 데모 운영일을 바꿔도 간편 예약의 실제 오늘 창은 움직이지 않는다.
def patch_operational_date(source: str) -> str:
    source, count1 = re.subn(
        r"const previousDate=targetState\.selectedDate,quickWindowFollowedToday=targetState\.quickReservationAnchorDate===previousDate,advanced=toDate>previousDate;",
        "const previousDate=targetState.selectedDate,advanced=toDate>previousDate;",
        source,
        count=1,
    )
    source, count2 = re.subn(
        r"targetState\.selectedDate=toDate;if\(quickWindowFollowedToday\)\{targetState\.quickReservationAnchorDate=toDate;targetState\.quickGridScrollLeft=null;\}targetState\.calendarMonth=toDate\.slice\(0,7\);",
        "targetState.selectedDate=toDate;targetState.calendarMonth=toDate.slice(0,7);",
        source,
        count=1,
    )
    if count1 != 1 or count2 != 1:
        raise SystemExit(f"operational date decoupling mismatch: {count1}, {count2}")
    return source


replace_function(
    "      function applyOperationalDate(targetState,toDate)",
    "      function automaticAssignmentTargets(",
    patch_operational_date,
    "operational date decoupling",
)

# 7. 좌우 이동은 사용자 지정 모드, 오늘 버튼은 실제 KST 오늘 추적 모드다.
replace_once(
    "rememberQuickGridViewport();state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);",
    "rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);",
    "quick window seven-day navigation mode",
)
replace_once(
    "state.quickReservationAnchorDate=state.selectedDate;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;",
    "state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=kstTodayIso();state.quickGridScrollLeft=null;state.quickGridScrollTop=0;",
    "quick window Today action",
)

# 8. 명시적 bookingAnchor/bookingMonth만 수동 범위로 보존한다.
replace_once(
    "        if(/^\\d{4}-(0[1-9]|1[0-2])-([0-2]\\d|3[01])$/.test(bookingAnchor))state.quickReservationAnchorDate=bookingAnchor;\n        else if(/^\\d{4}-(0[1-9]|1[0-2])$/.test(legacyBookingMonth))state.quickReservationAnchorDate=`${legacyBookingMonth}-15`;",
    "        if(/^\\d{4}-(0[1-9]|1[0-2])-([0-2]\\d|3[01])$/.test(bookingAnchor)){state.quickReservationAnchorDate=bookingAnchor;state.quickReservationFollowsToday=false;}\n        else if(/^\\d{4}-(0[1-9]|1[0-2])$/.test(legacyBookingMonth)){state.quickReservationAnchorDate=`${legacyBookingMonth}-15`;state.quickReservationFollowsToday=false;}\n        else{state.quickReservationAnchorDate=kstTodayIso();state.quickReservationFollowsToday=true;}",
    "hash route quick anchor mode",
)

# 회귀 방지: 운영일 결합과 고정 오늘 URL이 남아 있으면 실패한다.
for forbidden in [
    "s.quickReservationAnchorDate=s.selectedDate",
    "quickWindowFollowedToday=targetState.quickReservationAnchorDate===previousDate",
    "state.quickReservationAnchorDate=state.selectedDate",
    "today=iso===state.selectedDate,isPast=iso<state.selectedDate",
]:
    if forbidden in html:
        raise SystemExit(f"legacy quick-window coupling remains: {forbidden}")

for required in [
    "function kstTodayIso(now=new Date())",
    "quickReservationFollowsToday:true",
    "quickAnchor:state.quickReservationFollowsToday===false?state.quickReservationAnchorDate:null",
    "function refreshQuickReservationActualToday({rerender=false}={})",
    "state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate",
    "state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=kstTodayIso()",
    "today=iso===actualToday,isPast=iso<actualToday",
    "isPast=iso<todayIso",
]:
    if required not in html:
        raise SystemExit(f"KST daily quick-window contract missing: {required}")

HTML_PATH.write_text(html, encoding="utf-8")

# README의 기존 29일 정책을 실제 한국 날짜 기준으로 교체한다.
readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8")
section_pattern = r"## 간편 예약 29일 연속 보기 \(2026-08-24\)\n[\s\S]*?(?=\n## |\Z)"
replacement_section = """## 간편 예약 29일 연속 보기 (2026-08-25)

- 기본 기준일은 데모 운영일이 아니라 브라우저 현재 시각을 `Asia/Seoul`로 환산한 실제 오늘이다.
- 기본 범위는 실제 오늘 `-7일 ~ +21일`, 양 끝을 포함한 29일이다. 오늘이 바뀌면 기본 범위도 하루씩 이동하며 달이 바뀌어도 표를 끊지 않는다.
- 첫 진입과 `오늘` 복귀 시 오늘 열이 객실 정보 열 바로 옆에 오도록 가로 위치를 자동 정렬한다.
- 이전·다음 버튼은 현재 기준일을 7일씩 이동하고 `이동한 29일` 모드로 전환한다. 사용자가 이동한 범위는 자정에 강제로 오늘로 돌아오지 않는다.
- `오늘` 버튼을 누르면 그 시점의 한국 시간 실제 오늘을 다시 기준으로 삼고 자동 오늘 추적 모드로 복귀한다.
- 데모 운영일·객실 업무일을 변경해도 간편 예약 기본 범위는 움직이지 않는다.
- 범위 첫날과 매월 1일은 `월/일`로 표시하고 월 경계선을 둔다. 나머지 날짜는 `일`로 표시한다.
- 실제 오늘 이전 7일의 빈 칸은 조회 전용으로 잠그되 기존 예약은 열어볼 수 있다. 월을 넘는 연박 예약은 같은 예약 ID로 이어서 표시한다.
- 오늘 추적 모드의 URL에는 날짜를 고정하는 `bookingAnchor`를 남기지 않는다. 좌우 이동과 기존 `bookingAnchor=YYYY-MM-DD`, `bookingMonth=YYYY-MM` 링크는 사용자 지정 범위로 계속 호환한다.
"""
readme, count = re.subn(section_pattern, replacement_section.rstrip(), readme, count=1)
if count != 1:
    raise SystemExit(f"README 29-day section replacement mismatch: {count}")
readme_path.write_text(readme.rstrip() + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa_section = """

## 2026-08-25 · 간편 예약 한국 시간 실제 오늘 기준 29일

### 변경

- 간편 예약 기본 기준일을 데모 운영일에서 `Asia/Seoul` 실제 오늘로 분리했다.
- 오늘 추적 모드는 매일 `오늘 -7일 ~ 오늘 +21일`의 29일을 표시하고, 앱을 계속 열어 둔 경우에도 날짜 변경을 감지해 범위를 하루 이동한다.
- 좌우 7일 이동은 사용자 지정 모드로 전환해 자정에 강제로 이동하지 않으며, `오늘`을 누르면 실제 오늘 자동 추적으로 복귀한다.
- 기본 URL에서는 `bookingAnchor`를 제거하고, 명시적 앵커·과거 월 링크만 사용자 지정 범위로 보존한다.
- 과거 날짜 잠금과 오늘 강조도 데모 날짜가 아닌 한국 시간 실제 오늘을 사용한다.

### 검증

- 한국 시간 2026-08-25에서 `2026-08-18 ~ 2026-09-15`, 총 29일인지 확인했다.
- 한국 시간 2026-08-26으로 변경하면 오늘 추적 모드가 `2026-08-19 ~ 2026-09-16`으로 이동하는지 확인했다.
- 7일 이동 후 날짜가 변경돼도 사용자 지정 범위가 유지되고, `오늘` 클릭 후 새 실제 오늘 범위로 복귀하는지 확인했다.
- 데모 운영일을 다른 날짜로 연 링크에서도 실제 오늘 범위가 유지되는지 확인했다.
- 기존 `bookingAnchor`와 `bookingMonth` 링크의 사용자 지정 범위 호환을 확인했다.
- 390·768·1440px에서 가로 넘침과 브라우저 콘솔·런타임 오류가 없는지 확인했다.

### 한계

- 정적 브라우저 앱이므로 현재 시각은 사용자의 기기 시계를 한국 시간으로 환산한다. 실제 운영 서버 연결 시 서버 기준 시각을 정본으로 제공해야 한다.
"""
if "## 2026-08-25 · 간편 예약 한국 시간 실제 오늘 기준 29일" not in qa:
    qa += qa_section
qa_path.write_text(qa + "\n", encoding="utf-8")

# 최신 main의 영구 검사에 고유 변수명으로 계약을 추가한다.
checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker_section = r'''

for (const pr94KstDailyContract of [
  "timeZone:'Asia/Seoul'",
  'function kstTodayIso(now=new Date())',
  'quickReservationFollowsToday:true',
  'function refreshQuickReservationActualToday({rerender=false}={})',
  "window.setInterval(()=>refreshQuickReservationActualToday({rerender:true}),30000)",
  "state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate",
  "state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=kstTodayIso()",
  "quickAnchor:state.quickReservationFollowsToday===false?state.quickReservationAnchorDate:null",
  "today=iso===actualToday,isPast=iso<actualToday",
  "isPast=iso<todayIso",
  '오늘 기준 29일',
  '이동한 29일',
]) {
  if (!html.includes(pr94KstDailyContract)) throw new Error(`KST daily quick-window contract missing: ${pr94KstDailyContract}`);
}
for (const pr94LegacyQuickWindowContract of [
  's.quickReservationAnchorDate=s.selectedDate',
  'quickWindowFollowedToday=targetState.quickReservationAnchorDate===previousDate',
  'state.quickReservationAnchorDate=state.selectedDate',
  'today=iso===state.selectedDate,isPast=iso<state.selectedDate',
]) {
  if (html.includes(pr94LegacyQuickWindowContract)) throw new Error(`Legacy operating-date quick-window coupling remains: ${pr94LegacyQuickWindowContract}`);
}
if (!wireframeReadme.includes('브라우저 현재 시각을 `Asia/Seoul`로 환산한 실제 오늘')) {
  throw new Error('KST daily quick-window README policy is missing.');
}
console.log('KST daily quick-window static contracts: passed');
'''
if "KST daily quick-window static contracts: passed" not in checker:
    checker += checker_section
checker_path.write_text(checker + "\n", encoding="utf-8")

# 정본 무결성 메타데이터 갱신.
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
manifest["version"] = "2026-08-25-kst-daily-quick-window-rebased"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
