from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML_PATH = Path("WIREFRAME/index.html")
html = HTML_PATH.read_text(encoding="utf-8")

# Only patch the final active renderAdminToday implementation.
render_start = html.rfind("      function renderAdminToday() {")
render_end = html.find("\n      function maidName(", render_start)
if render_start < 0 or render_end < 0:
    raise SystemExit("active renderAdminToday block could not be isolated")
render_source = html[render_start:render_end]

cost_start_marker = "        const cleaningCost=dashboardCleaningCostSummary(),cleaningCostSection="
cost_end_marker = ";\n        const schedule="
cost_start = render_source.find(cost_start_marker)
cost_end = render_source.find(cost_end_marker, cost_start)
if cost_start < 0 or cost_end < 0:
    raise SystemExit("dashboard cleaning-cost definition could not be isolated")

compact_cost_definition = '''        const cleaningCost=dashboardCleaningCostSummary(),cleaningCostSection=`<section aria-label="청소비 예상 지출"><button class="card cleaning-cost-shortcut" type="button" data-action="go-payroll" data-week="${cleaningCost.weekStart}" data-dashboard-cost-shortcut="today" aria-label="청소비 예상 지출. 오늘 ${cleaningCost.count}건, 검수 통과 시 ${money(cleaningCost.expected)} 예상. 현재 확정 ${money(cleaningCost.confirmed)}, 검수 요청 금액 최대 ${money(cleaningCost.pending)}. 주급 정산 화면 열기"><span class="cleaning-cost-shortcut-main">${icon('wallet')}<span><strong>청소비 예상 지출</strong><small>오늘 ${cleaningCost.count}건 · ${money(cleaningCost.expected)}</small></span></span><span class="cleaning-cost-shortcut-cta">주급 정산${icon('chevronRight','icon-sm')}</span></button></section>`'''
render_source = render_source[:cost_start] + compact_cost_definition + render_source[cost_end:]

content_start_marker = "        const content=`"
content_end_marker = ";\n        return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);"
content_start = render_source.find(content_start_marker)
content_end = render_source.find(content_end_marker, content_start)
if content_start < 0 or content_end < 0:
    raise SystemExit("dashboard content template could not be isolated")

new_content = '''        const content=`<div class="view-stack"><div>${renderDateTools(false)}</div><section aria-labelledby="summary-title" data-admin-home-section="room-summary"><div class="mobile-section-title"><div><h2 id="summary-title">오늘 객실 요약</h2></div></div><div class="today-summary"><button class="card metric-card neutral" type="button" data-action="filter-rooms" data-filter="occupied" aria-label="투숙 중 객실 ${occupiedCount}개 목록 보기"><span>투숙 중</span><strong>${occupiedCount}</strong></button><button class="card metric-card amber" type="button" data-action="filter-rooms" data-filter="cleaning" aria-label="청소 필요 객실 ${cleaningCount}개 목록 보기"><span>청소 필요</span><strong>${cleaningCount}</strong></button><button class="card metric-card green" type="button" data-action="filter-rooms" data-filter="available" aria-label="배정 가능 객실 ${availableCount}개 목록 보기"><span>배정 가능</span><strong>${availableCount}</strong></button><button class="card metric-card red" type="button" data-action="filter-rooms" data-filter="blocked" aria-label="배정 불가 객실 ${blockedCount}개 목록 보기"><span>배정 불가</span><strong>${blockedCount}</strong></button></div></section><div class="accordion-list" data-admin-home-section="cleaning-actions">${renderAccordion('assignment','오늘 청소 배정',`${assignmentCountsToday.unassigned}건 미배정`,assignmentBody,true)}${renderAccordion('inspection','청소 검수','2건',inspectionBody)}</div><div data-admin-home-section="cleaning-cost">${cleaningCostSection}</div></div>`'''
render_source = render_source[:content_start] + new_content + render_source[content_end:]
html = html[:render_start] + render_source + html[render_end:]

# Add a compact, secondary visual treatment without disturbing the detailed payroll screen.
css_marker = "    .cleaning-cost-foot {"
css_index = html.find(css_marker)
if css_index < 0:
    raise SystemExit("cleaning-cost CSS marker missing")
compact_css = '''    /* Admin-home compact cleaning-cost shortcut */
    .cleaning-cost-shortcut { display:flex; align-items:center; justify-content:space-between; gap:16px; width:100%; min-height:62px; padding:12px 16px; color:var(--ink); background:#fff; text-align:left; cursor:pointer; transition:border-color .16s ease, box-shadow .16s ease, transform .16s ease; }
    .cleaning-cost-shortcut:hover { border-color:#9fb5c7; box-shadow:0 8px 20px rgba(20,36,55,.08); transform:translateY(-1px); }
    .cleaning-cost-shortcut:active { transform:translateY(0); }
    .cleaning-cost-shortcut-main { display:flex; align-items:center; gap:11px; min-width:0; }
    .cleaning-cost-shortcut-main > span { min-width:0; }
    .cleaning-cost-shortcut-main strong { display:block; font-size:14px; }
    .cleaning-cost-shortcut-main small { display:block; margin-top:2px; color:var(--muted); font-size:12px; line-height:1.35; }
    .cleaning-cost-shortcut-cta { display:flex; align-items:center; gap:5px; flex:0 0 auto; color:var(--navy); font-size:13px; font-weight:800; white-space:nowrap; }
'''
if "/* Admin-home compact cleaning-cost shortcut */" not in html:
    html = html[:css_index] + compact_css + html[css_index:]

mobile_marker = "    @media (max-width: 720px) {"
mobile_index = html.find(mobile_marker)
if mobile_index < 0:
    raise SystemExit("mobile media-query marker missing")
mobile_insert_at = mobile_index + len(mobile_marker)
mobile_css = '''
      .cleaning-cost-shortcut { min-height:60px; padding:11px 13px; gap:10px; }
      .cleaning-cost-shortcut-main { gap:9px; }
      .cleaning-cost-shortcut-cta { font-size:12px; }
'''
if ".cleaning-cost-shortcut { min-height:60px;" not in html:
    html = html[:mobile_insert_at] + mobile_css + html[mobile_insert_at:]

HTML_PATH.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 관리자 홈 정보 우선순위 (2026-08-28)

- 날짜 선택 도구 아래의 첫 정보 블록은 `오늘 객실 요약`이다.
- 다음으로 `오늘 청소 배정`, `청소 검수`를 배치한다.
- `청소비 예상 지출`은 두 청소 업무 아래의 한 줄짜리 보조 바로가기로 낮춘다.
- 홈에는 오늘 예상 건수와 예상 금액만 표시하고, 이번 주·확정·검수 요청 금액과 산정 기준은 `주급 정산` 화면에서 확인한다.
- 청소비 행 전체를 누르면 현재 연결된 주차의 주급 정산 화면으로 이동한다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-28 · 관리자 홈 객실 요약 우선·청소비 보조 바로가기

- 날짜 선택 다음 첫 정보 블록이 `오늘 객실 요약`인지 확인한다.
- `오늘 청소 배정`, `청소 검수`, `청소비 예상 지출` 순서인지 확인한다.
- 청소비 바로가기에는 오늘 예상 건수·오늘 예상 금액·`주급 정산`만 시각적으로 표시되는지 확인한다.
- 이번 주 예상액·확정액·검수 요청 최대액·송금 관련 설명이 홈에 노출되지 않는지 확인한다.
- 청소비 행 전체를 눌렀을 때 주급 정산 탭으로 이동하는지 확인한다.
- 390px·768px·1440px에서 가로 넘침과 콘솔·런타임 오류가 없는지 확인한다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker += r'''

const adminHomePriorityStart = html.lastIndexOf('function renderAdminToday()');
const adminHomePriorityEnd = html.indexOf('\n      function maidName(', adminHomePriorityStart);
if (adminHomePriorityStart < 0 || adminHomePriorityEnd < 0) throw new Error('Active admin-home source could not be isolated for priority checks.');
const adminHomePrioritySource = html.slice(adminHomePriorityStart, adminHomePriorityEnd);
for (const contract of [
  'data-admin-home-section="room-summary"',
  'data-admin-home-section="cleaning-actions"',
  'data-admin-home-section="cleaning-cost"',
  'data-dashboard-cost-shortcut="today"',
  'class="card cleaning-cost-shortcut"',
  '<strong>청소비 예상 지출</strong>',
  '<small>오늘 ${cleaningCost.count}건 · ${money(cleaningCost.expected)}</small>',
  '<span class="cleaning-cost-shortcut-cta">주급 정산',
  'data-action="go-payroll"',
]) {
  if (!adminHomePrioritySource.includes(contract)) throw new Error(`Admin-home priority/cost shortcut contract missing: ${contract}`);
}
const adminHomeSummaryIndex = adminHomePrioritySource.indexOf('data-admin-home-section="room-summary"');
const adminHomeActionsIndex = adminHomePrioritySource.indexOf('data-admin-home-section="cleaning-actions"');
const adminHomeCostIndex = adminHomePrioritySource.indexOf('data-admin-home-section="cleaning-cost"');
if (!(adminHomeSummaryIndex >= 0 && adminHomeSummaryIndex < adminHomeActionsIndex && adminHomeActionsIndex < adminHomeCostIndex)) {
  throw new Error('Admin-home sections are not ordered summary → cleaning actions → cleaning cost.');
}
for (const forbidden of [
  'class="cleaning-cost-grid"',
  'class="cleaning-cost-foot"',
  '이번 주 예상',
  '검수 통과 시 예상 지출',
  '앱은 실제 송금을 실행하지 않습니다.',
]) {
  if (adminHomePrioritySource.includes(forbidden)) throw new Error(`Verbose cleaning-cost content remains on admin home: ${forbidden}`);
}
if (!html.includes('/* Admin-home compact cleaning-cost shortcut */')) throw new Error('Compact cleaning-cost shortcut styles are missing.');
console.log('Admin-home room-summary priority and compact cost-link contracts: passed');
'''
checker_path.write_text(checker + "\n", encoding="utf-8")

# Refresh repository integrity metadata.
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
manifest["version"] = "2026-08-28-home-priority-cost-link"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
