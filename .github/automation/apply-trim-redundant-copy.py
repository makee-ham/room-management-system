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


replace_once(
    "      function detailHeader(title,subtitle) { return `<div class=\"detail-head\"><button class=\"btn btn-ghost\" type=\"button\" data-action=\"back\">${icon('chevronLeft','icon-sm')}목록</button><div class=\"detail-title\"><h2>${title}</h2><p>${subtitle}</p></div></div>`; }",
    "      function detailHeader(title,subtitle='') { return `<div class=\"detail-head\"><button class=\"btn btn-ghost\" type=\"button\" data-action=\"back\">${icon('chevronLeft','icon-sm')}목록</button><div class=\"detail-title\"><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div></div>`; }",
    "conditional detail subtitle",
)

old_summary = """<section aria-labelledby=\"summary-title\"><div class=\"mobile-section-title\"><div><h2 id=\"summary-title\">오늘 객실 요약</h2><p>네 가지 주 상태로만 계산 · 데모</p></div></div><div class=\"today-summary\"><button class=\"card metric-card neutral\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"occupied\" aria-label=\"투숙 중 객실 ${occupiedCount}개 목록 보기\"><span>투숙 중</span><strong>${occupiedCount}</strong><small>현재 점유 · 회색</small></button><button class=\"card metric-card amber\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"cleaning\" aria-label=\"청소 필요 객실 ${cleaningCount}개 목록 보기\"><span>청소 필요</span><strong>${cleaningCount}</strong><small>퇴실·연박 청소 · 주황</small></button><button class=\"card metric-card green\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"available\" aria-label=\"배정 가능 객실 ${availableCount}개 목록 보기\"><span>배정 가능</span><strong>${availableCount}</strong><small>공실·준비 완료 · 초록</small></button><button class=\"card metric-card red\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"blocked\" aria-label=\"배정 불가 객실 ${blockedCount}개 목록 보기\"><span>배정 불가</span><strong>${blockedCount}</strong><small>촛불·차단 특이사항 등 · 빨강</small></button></div></section>"""
new_summary = """<section aria-labelledby=\"summary-title\"><div class=\"mobile-section-title\"><div><h2 id=\"summary-title\">오늘 객실 요약</h2></div></div><div class=\"today-summary\"><button class=\"card metric-card neutral\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"occupied\" aria-label=\"투숙 중 객실 ${occupiedCount}개 목록 보기\"><span>투숙 중</span><strong>${occupiedCount}</strong></button><button class=\"card metric-card amber\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"cleaning\" aria-label=\"청소 필요 객실 ${cleaningCount}개 목록 보기\"><span>청소 필요</span><strong>${cleaningCount}</strong></button><button class=\"card metric-card green\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"available\" aria-label=\"배정 가능 객실 ${availableCount}개 목록 보기\"><span>배정 가능</span><strong>${availableCount}</strong></button><button class=\"card metric-card red\" type=\"button\" data-action=\"filter-rooms\" data-filter=\"blocked\" aria-label=\"배정 불가 객실 ${blockedCount}개 목록 보기\"><span>배정 불가</span><strong>${blockedCount}</strong></button></div></section>"""
replace_once(old_summary, new_summary, "minimal today summary cards")

replace_once(
    "detailHeader(`${active?.maid||'김민지1'} · ${active?.type||'컴플레인'}`,`주급 자동 차감 없음 · 삭제 이력 보존`)",
    "detailHeader(`${active?.maid||'김민지1'} ${active?.type||'컴플레인'}`)",
    "minimal complaint detail header",
)

# Keep the summary compact after removing its explanatory third line.
compact_css_marker = "    .metric-card small { display:block; color:var(--muted); font-size:12px; line-height:1.45; }"
if compact_css_marker not in html:
    raise SystemExit("metric-card style marker missing")
html = html.replace(
    compact_css_marker,
    compact_css_marker + "\n    .today-summary .metric-card { min-height:96px; display:flex; flex-direction:column; justify-content:center; }\n    .today-summary .metric-card strong { margin-bottom:0; }",
    1,
)

HTML_PATH.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 핵심 정보 중심 문구 정리 (2026-08-26)

- 오늘 객실 요약 카드는 `투숙 중`, `청소 필요`, `배정 가능`, `배정 불가`와 개수만 표시한다.
- 색상명과 상태를 다시 설명하는 보조 문구는 카드 스타일·접근성 라벨과 중복되므로 화면에서 제거한다.
- 컴플레인·벌점 상세 헤더는 `메이드명 유형`만 표시한다. 주급 영향은 상세 정보 표에서, 삭제·정정 보존은 감사 이력에서 각각 한 번만 확인한다.
- 상세 부제가 비어 있으면 빈 문단을 렌더링하지 않는다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-26 · 객실 요약·컴플레인 상세 중복 문구 제거

- 오늘 객실 요약 카드 4개가 상태명과 개수만 표시하는지 확인한다.
- `현재 점유 · 회색`, `퇴실·연박 청소 · 주황`, `공실·준비 완료 · 초록`, `촛불·차단 특이사항 등 · 빨강`, `네 가지 주 상태로만 계산 · 데모`가 렌더링되지 않는지 확인한다.
- 컴플레인 상세 제목이 `메이드명 유형`으로 표시되고 `주급 자동 차감 없음 · 삭제 이력 보존` 부제가 사라지는지 확인한다.
- 실제 판단 정보인 `주급 영향 / 자동 차감 없음`과 감사 이력은 상세 본문에 유지되는지 확인한다.
- 390px·1440px에서 빈 헤더 간격, 문서 가로 넘침, 콘솔·런타임 오류가 없는지 확인한다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker += r'''

for (const contract of [
  "function detailHeader(title,subtitle='')",
  "${subtitle?`<p>${subtitle}</p>`:''}",
  '<h2 id="summary-title">오늘 객실 요약</h2></div></div><div class="today-summary">',
  '<span>투숙 중</span><strong>${occupiedCount}</strong></button>',
  '<span>청소 필요</span><strong>${cleaningCount}</strong></button>',
  '<span>배정 가능</span><strong>${availableCount}</strong></button>',
  '<span>배정 불가</span><strong>${blockedCount}</strong></button>',
  "detailHeader(`${active?.maid||'김민지1'} ${active?.type||'컴플레인'}`)",
  '.today-summary .metric-card { min-height:96px;',
]) {
  if (!html.includes(contract)) throw new Error(`Essential-copy contract missing: ${contract}`);
}
for (const forbidden of [
  '현재 점유 · 회색',
  '퇴실·연박 청소 · 주황',
  '공실·준비 완료 · 초록',
  '촛불·차단 특이사항 등 · 빨강',
  '네 가지 주 상태로만 계산 · 데모',
  '주급 자동 차감 없음 · 삭제 이력 보존',
]) {
  if (html.includes(forbidden)) throw new Error(`Redundant UI copy remains: ${forbidden}`);
}
if (!html.includes('<span>주급 영향</span><strong>자동 차감 없음</strong>')) {
  throw new Error('The single operational payroll-impact fact was removed from complaint details.');
}
if (!html.includes('<h3>감사 이력</h3>')) throw new Error('Complaint audit history was removed.');
console.log('Essential-copy-only static contracts: passed');
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
manifest["version"] = "2026-08-26-essential-copy-only"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
