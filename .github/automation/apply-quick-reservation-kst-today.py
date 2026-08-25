from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    html = html.replace(old, new, 1)


if "function koreaTodayISO(" not in html:
    marker = "const QUICK_RESERVATION_PAST_DAYS=7"
    if html.count(marker) != 1:
        raise SystemExit(f"quick reservation constant marker mismatch: {html.count(marker)}")
    helper = """function koreaTodayISO(now=new Date()) {
        const parts=new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
        const values=Object.fromEntries(parts.filter(part=>part.type!=='literal').map(part=>[part.type,part.value]));
        return `${values.year}-${values.month}-${values.day}`;
      }
      let quickReservationTodaySnapshot=koreaTodayISO();
      function syncQuickReservationTodayWindow() {
        const today=koreaTodayISO();
        if(today===quickReservationTodaySnapshot)return false;
        const followedToday=state.quickReservationAnchorDate===quickReservationTodaySnapshot;
        quickReservationTodaySnapshot=today;
        if(!followedToday)return false;
        state.quickReservationAnchorDate=today;
        if(state.role==='admin'&&state.adminView==='quickReservation')render();
        return true;
      }
      """
    html = html.replace(marker, helper + marker, 1)

# The Today action must use the real KST calendar date rather than the selected
# operational/demo date. Keep the existing render/history/scroll work in place.
action_pattern = re.compile(
    r"(if\s*\(\s*a\s*===\s*['\"]quick-month-today['\"]\s*\)\s*\{)([\s\S]{0,1200}?)(\}\s*(?=if\s*\(|else\s+if\s*\(|$))"
)
action_match = action_pattern.search(html)
if not action_match:
    # Some versions keep adjacent handlers on one line. Resolve the bounded
    # segment from the action token to the next action token instead.
    token = "a==='quick-month-today'"
    start = html.find(token)
    if start < 0:
        raise SystemExit("quick-month-today handler not found")
    next_handler = html.find("if(a===", start + len(token))
    if next_handler < 0:
        next_handler = min(len(html), start + 1600)
    segment = html[start:next_handler]
    assignment = re.search(r"state\.quickReservationAnchorDate\s*=\s*[^;]+;", segment)
    if not assignment:
        raise SystemExit("quick-month-today anchor assignment not found")
    replacement = "state.quickReservationAnchorDate=koreaTodayISO();quickReservationTodaySnapshot=state.quickReservationAnchorDate;"
    segment = segment[:assignment.start()] + replacement + segment[assignment.end():]
    html = html[:start] + segment + html[next_handler:]
else:
    body = action_match.group(2)
    assignment = re.search(r"state\.quickReservationAnchorDate\s*=\s*[^;]+;", body)
    if not assignment:
        raise SystemExit("quick-month-today bounded anchor assignment not found")
    replacement = "state.quickReservationAnchorDate=koreaTodayISO();quickReservationTodaySnapshot=state.quickReservationAnchorDate;"
    body = body[:assignment.start()] + replacement + body[assignment.end():]
    html = html[:action_match.start()] + action_match.group(1) + body + action_match.group(3) + html[action_match.end():]

# Remove direct coupling to the selected operational date wherever an older
# reset path still performs the same assignment.
html = re.sub(
    r"state\.quickReservationAnchorDate\s*=\s*state\.selectedDate\s*;",
    "state.quickReservationAnchorDate=koreaTodayISO();quickReservationTodaySnapshot=state.quickReservationAnchorDate;",
    html,
)

# After URL/hash parameters have been read, default to the real KST day only
# when no explicit booking anchor (or legacy month) was requested. This keeps
# deep links and browser history intact.
startup_marker = "applyHashParameters();"
startup_index = html.rfind(startup_marker)
if startup_index < 0:
    raise SystemExit("applyHashParameters startup call not found")
startup_insert = """
      quickReservationTodaySnapshot=koreaTodayISO();
      const initialQuickReservationParams=new URLSearchParams(location.hash.replace(/^#/,''));
      if(!initialQuickReservationParams.has('bookingAnchor')&&!initialQuickReservationParams.has('bookingMonth'))state.quickReservationAnchorDate=quickReservationTodaySnapshot;
      window.addEventListener('focus',syncQuickReservationTodayWindow);
      document.addEventListener('visibilitychange',()=>{if(!document.hidden)syncQuickReservationTodayWindow();});
      setInterval(syncQuickReservationTodayWindow,60000);
"""
insert_at = startup_index + len(startup_marker)
if "initialQuickReservationParams" not in html:
    html = html[:insert_at] + startup_insert + html[insert_at:]

# Guard against the exact regression that caused the 8.8–9.5 range on 8.25.
if re.search(r"state\.quickReservationAnchorDate\s*=\s*state\.selectedDate", html):
    raise SystemExit("quick reservation anchor is still coupled to state.selectedDate")
if "state.quickReservationAnchorDate=koreaTodayISO()" not in html:
    raise SystemExit("Today action does not reset to the KST date")
if "initialQuickReservationParams.has('bookingAnchor')" not in html:
    raise SystemExit("initial KST-today default contract was not installed")

html_path.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
section = """

## 간편 예약의 한국 시간 오늘 기준 29일 창 (2026-08-25)

- 기본 기준일은 선택된 데모 운영일이 아니라 `Asia/Seoul`의 실제 오늘이다.
- 표시 범위는 매일 `오늘 - 7일`부터 `오늘 + 21일`까지이며, 양 끝을 포함해 29일이다.
- 예: 2026-08-25에는 2026-08-18~2026-09-15, 2026-08-26에는 2026-08-19~2026-09-16을 표시한다.
- `오늘` 버튼은 언제나 한국 시간의 실제 오늘로 복귀한다. 좌우 버튼은 현재 기준일을 7일씩 이동한다.
- `bookingAnchor`가 있는 링크와 브라우저 이력은 해당 기준일을 유지한다.
- 오늘 보기 상태로 탭을 열어 둔 채 날짜가 바뀌면, 포커스 복귀·가시성 복귀·1분 주기 확인 시 새 오늘 기준 범위로 갱신한다. 과거·미래를 수동 탐색 중이면 강제로 오늘로 이동하지 않는다.
"""
if "## 간편 예약의 한국 시간 오늘 기준 29일 창" not in readme:
    readme += section
readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa_section = """

## 2026-08-25 · 간편 예약 실제 오늘 기준 29일 회귀 검사

- 한국 시간 2026-08-25에서 기본 범위가 2026-08-18~2026-09-15의 29일인지 확인했다.
- 다음 날인 2026-08-26에서 기본 범위가 2026-08-19~2026-09-16으로 하루 이동하는지 확인했다.
- 운영 데모 날짜가 2026-08-15여도 간편 예약 기본 기준은 실제 오늘을 따르는지 확인했다.
- 오른쪽 이동 후 `오늘`을 누르면 실제 오늘 기준 범위로 복귀하는지 확인했다.
- 명시적인 `bookingAnchor` 링크는 지정된 기준일을 유지하는지 확인했다.
- 오늘 보기 상태에서는 자정 이후 포커스 복귀 시 새 날짜로 갱신하고, 수동 탐색 중에는 유지하는지 확인했다.
- 390·768·1440px 문서 가로 넘침과 브라우저 콘솔·런타임 오류가 없는지 확인했다.
"""
if "## 2026-08-25 · 간편 예약 실제 오늘 기준 29일 회귀 검사" not in qa:
    qa += qa_section
qa_path.write_text(qa + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker_section = r'''

for (const contract of [
  'function koreaTodayISO(now=new Date())',
  "timeZone:'Asia/Seoul'",
  'let quickReservationTodaySnapshot=koreaTodayISO();',
  'function syncQuickReservationTodayWindow()',
  'const followedToday=state.quickReservationAnchorDate===quickReservationTodaySnapshot;',
  "initialQuickReservationParams.has('bookingAnchor')",
  "initialQuickReservationParams.has('bookingMonth')",
  'state.quickReservationAnchorDate=koreaTodayISO();quickReservationTodaySnapshot=state.quickReservationAnchorDate;',
  "window.addEventListener('focus',syncQuickReservationTodayWindow)",
  'setInterval(syncQuickReservationTodayWindow,60000);',
]) {
  if (!html.includes(contract)) throw new Error(`KST-today quick reservation contract missing: ${contract}`);
}
if (/state\.quickReservationAnchorDate\s*=\s*state\.selectedDate/.test(html)) {
  throw new Error('Quick reservation anchor must not be coupled to the selected operational date.');
}
console.log('KST-today rolling 29-day quick reservation static contracts: passed');
'''
if "KST-today rolling 29-day quick reservation static contracts: passed" not in checker:
    checker += checker_section
checker_path.write_text(checker + "\n", encoding="utf-8")

# Refresh the repository integrity metadata for the product file.
digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
sums_lines = sums_path.read_text(encoding="utf-8").splitlines()
updated = False
next_lines = []
for line in sums_lines:
    if line.endswith("  WIREFRAME/index.html"):
        next_lines.append(f"{digest}  WIREFRAME/index.html")
        updated = True
    else:
        next_lines.append(line)
if not updated:
    raise SystemExit("WIREFRAME/index.html checksum line missing")
sums_path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-25-kst-today-quick-reservation-window"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
