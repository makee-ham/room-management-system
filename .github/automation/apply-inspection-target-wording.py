from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML_PATH = Path("WIREFRAME/index.html")
html = HTML_PATH.read_text(encoding="utf-8")


def replace_exact(old: str, new: str, label: str, *, minimum: int = 1) -> int:
    global html
    count = html.count(old)
    if count < minimum:
        raise SystemExit(f"{label}: expected at least {minimum} match(es), found {count}")
    html = html.replace(old, new)
    return count


# 관리자 업무 큐의 이름은 목록 목적을, 개별 제출은 메이드가 요청을 보냈음을 표현한다.
replace_exact(
    "next:'검수 대기 탭에서 639호 전체 제출을 검수하세요.'",
    "next:'검수 대상 목록 탭에서 639호 전체 제출을 검수하세요.'",
    "scenario inspection wording",
)
replace_exact(
    "cleaningTabButton('inspection','검수 대기',tabCounts.inspection)",
    "cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)",
    "admin cleaning inspection tab wording",
)
replace_exact(
    "button('검수 대기 열기','go-inspection','outline')",
    "button('검수 대상 목록 열기','go-inspection','outline')",
    "admin home inspection entry wording",
)
replace_exact(
    "<h3>검수 대기</h3><span class=\"meta\">4건</span>",
    "<h3>검수 대상 목록</h3><span class=\"meta\">4건</span>",
    "inspection rail heading wording",
)
replace_exact(
    "button('검수 목록 보기','cleaning-detail','outline'",
    "button('검수 대상 목록 보기','cleaning-detail','outline'",
    "inspection rail button wording",
)
replace_exact(
    "queueCard('success','대기','검수 대기','4건'",
    "queueCard('success','대기','검수 대상 목록','4건'",
    "legacy admin queue wording",
)
replace_exact(
    "inspection:'검수 대기'",
    "inspection:'검수 요청됨'",
    "individual inspection submission status wording",
)
replace_exact(
    "status==='approved'?'승인 완료':'검수 대기'",
    "status==='approved'?'승인 완료':'검수 요청됨'",
    "inspection detail status wording",
)

inspection_body_old = "const inspectionBody=`<div class=\"rail-row\"><strong>350호 · 얼리 체크인 우선</strong><span>검수 대기</span></div><div class=\"rail-row\"><strong>639호 · 전체 제출</strong><span>검수 대기</span></div><div style=\"margin-top:10px\">${button('검수 대상 목록 열기','go-inspection','outline')}</div>`;"
inspection_body_new = "const inspectionBody=`<div class=\"rail-row\"><strong>350호 · 얼리 체크인 우선</strong><span>검수 요청됨</span></div><div class=\"rail-row\"><strong>639호 · 전체 제출</strong><span>검수 요청됨</span></div><div style=\"margin-top:10px\">${button('검수 대상 목록 열기','go-inspection','outline')}</div>`;"
replace_exact(inspection_body_old, inspection_body_new, "admin home inspection item status wording")

HTML_PATH.write_text(html, encoding="utf-8")

# 현재 정본 문서에서 관리자 큐 명칭만 바꾸고, 급여의 '검수 대기 금액' 같은 상태 설명은 유지한다.
for doc_path in [
    Path("WIREFRAME/README.md"),
    Path("WIREFRAME/QA.md"),
    Path("DOCS/02_USER_ROLES_AND_SCREEN_MAP.md"),
    Path("DOCS/04_WORKFLOWS_AND_FLOWCHARTS.md"),
    Path("DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md"),
    Path("DOCS/WIREFRAME_TASK_PROMPT.md"),
]:
    if not doc_path.exists():
        continue
    text = doc_path.read_text(encoding="utf-8")
    text = text.replace("검수 대기 탭", "검수 대상 목록 탭")
    text = text.replace("검수 대기 열기", "검수 대상 목록 열기")
    text = text.replace("검수 대기 목록", "검수 대상 목록")
    doc_path.write_text(text, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 관리자 청소 검수 용어 (2026-08-25)

- 관리자에게 처리해야 할 업무 큐는 `검수 대상 목록`으로 표시한다.
- 목록 안의 개별 청소 제출 상태는 `검수 요청됨`으로 표시한다.
- 메이드가 청소를 끝내고 관리자에게 보내는 행동은 기존대로 `검수 요청`이라고 표현한다.
- 주급에서 아직 승인되지 않은 예상 금액처럼 실제 대기 상태를 설명하는 `검수 대기` 문구는 유지한다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-25 · 관리자 검수 대상 목록 용어

- 관리자 홈의 `검수 대상 목록 열기`가 청소 관리의 `검수 대상 목록` 탭으로 이동하는지 확인한다.
- 검수 대상 카드의 개별 제출 상태가 `검수 요청됨`으로 표시되는지 확인한다.
- 관리자 청소 검수 탭과 진입 버튼에 `검수 대기`가 목록 이름으로 남아 있지 않은지 확인한다.
- 메이드 행동인 `검수 요청`과 주급의 `검수 대기 금액`은 의미가 달라 유지되는지 확인한다.
- 390px·1440px에서 가로 넘침과 콘솔·런타임 오류가 없는지 확인한다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
checker = checker.replace("검수 대기 탭", "검수 대상 목록 탭")
checker = checker.replace("검수 대기 열기", "검수 대상 목록 열기")
checker = checker.rstrip() + r'''

const inspectionWordingContracts = [
  "cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)",
  "button('검수 대상 목록 열기','go-inspection','outline')",
  "inspection:'검수 요청됨'",
  "next:'검수 대상 목록 탭에서 639호 전체 제출을 검수하세요.'",
  '관리자에게 처리해야 할 업무 큐는 `검수 대상 목록`',
  '개별 청소 제출 상태는 `검수 요청됨`',
];
for (const contract of inspectionWordingContracts) {
  if (!html.includes(contract) && !wireframeReadme.includes(contract)) {
    throw new Error(`Inspection target-list wording contract missing: ${contract}`);
  }
}
const cleaningHubStart = html.lastIndexOf('function renderCleaningHub()');
const cleaningHubEnd = html.indexOf('function taskRow(', cleaningHubStart);
const cleaningHubSource = html.slice(cleaningHubStart, cleaningHubEnd);
if (cleaningHubStart < 0 || cleaningHubEnd < 0) throw new Error('Current cleaning hub source could not be isolated.');
if (cleaningHubSource.includes("cleaningTabButton('inspection','검수 대기'")) {
  throw new Error('Legacy admin inspection tab wording remains.');
}
const currentAdminTodayStartForInspectionWording = html.lastIndexOf('function renderAdminToday()');
const currentAdminTodayEndForInspectionWording = html.indexOf('\n      function maidName(', currentAdminTodayStartForInspectionWording);
const currentAdminTodayForInspectionWording = html.slice(currentAdminTodayStartForInspectionWording, currentAdminTodayEndForInspectionWording);
if (currentAdminTodayForInspectionWording.includes("button('검수 대기 열기'")) {
  throw new Error('Legacy admin-home inspection entry wording remains.');
}
console.log('Inspection target-list wording static contracts: passed');
'''
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
manifest["version"] = "2026-08-25-inspection-target-list-wording"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
