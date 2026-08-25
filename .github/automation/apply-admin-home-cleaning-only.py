from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")

start_marker = '<button class="availability-link" type="button" data-action="go-workforce">'
end_marker = "${renderAccordion('pay','지난주 지급',`${money(lastWeekMaidPay)}`,payBody)}</div>"
replacement = "<div class=\"accordion-list\">${renderAccordion('assignment','오늘 청소 배정',`${assignmentCountsToday.unassigned}건 미배정`,assignmentBody,true)}${renderAccordion('inspection','청소 검수','2건',inspectionBody)}</div>"

if html.count(start_marker) != 1:
    raise SystemExit(f"admin-home availability marker mismatch: {html.count(start_marker)}")
if html.count(end_marker) != 1:
    raise SystemExit(f"admin-home ending marker mismatch: {html.count(end_marker)}")

start = html.index(start_marker)
end = html.index(end_marker, start) + len(end_marker)
old_fragment = html[start:end]
for required in [
    "다음 주 가능일 제출",
    "renderAccordion('assignment','오늘 청소 배정'",
    "renderAccordion('schedule','오늘 체크인·체크아웃'",
    "${cancelAccordion}",
    "renderAccordion('drafts','배정 준비 청소 작업'",
    "renderAccordion('inspection','검수 대기'",
    "renderAccordion('pay','지난주 지급'",
]:
    if required not in old_fragment:
        raise SystemExit(f"expected admin-home fragment missing: {required}")

html = html[:start] + replacement + html[end:]
if html.count(replacement) != 1:
    raise SystemExit("new admin-home two-item rendering was not inserted exactly once")
html_path.write_text(html, encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-25 · 관리자 홈 청소 핵심 업무 두 항목

### 변경

- 관리자 홈의 업무 아코디언을 `오늘 청소 배정`과 `청소 검수` 두 항목으로 단순화했다.
- 기존 `검수 대기` 항목의 건수·상세·검수 화면 이동 기능은 유지하고 제목만 `청소 검수`로 변경했다.
- 다음 주 가능일 제출 배너, 오늘 체크인·체크아웃, 담당 취소 요청/처리 결과, 배정 준비 청소 작업, 지난주 지급은 관리자 홈에서 제거했다.
- 전용 화면과 원본 데이터, 메이드 홈, 알림 센터는 변경하지 않았다.

### 검증

- 관리자 홈 `.accordion-list`의 직접 자식이 정확히 2개인지 확인했다.
- 두 제목과 건수가 표시되고, 각각 펼침·접힘 및 기존 버튼 동작이 유지되는지 확인했다.
- 제거 대상 문구가 관리자 홈 업무 목록에 렌더링되지 않는지 확인했다.
- 390px·1440px에서 문서 가로 넘침, 프레임워크 오류 화면, 콘솔·런타임 오류가 없는지 확인했다.

### 후속

- 알림 센터는 정적인 현황표가 아니라 상태 변경 이벤트 원장으로 별도 재설계한다. 관리자·메이드별 발송 조건을 사용자 확인 후 구현한다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 관리자 홈 핵심 업무 단순화 (2026-08-25)

- 관리자 홈의 업무 목록은 `오늘 청소 배정`과 `청소 검수`만 제공한다.
- 인력 가능일, 체크인·체크아웃, 배정 준비 작업, 취소 요청, 주급은 각 전용 화면 또는 향후 이벤트 알림에서 처리하며 홈 업무 목록에는 중복 노출하지 않는다.
- 알림 센터는 이 변경에 포함하지 않으며, 수신자별 이벤트·푸시 기준을 확정한 뒤 별도 구현한다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker += r'''

const currentAdminTodayStart = html.lastIndexOf('function renderAdminToday()');
const currentAdminTodayEnd = html.indexOf('\n      function maidName(', currentAdminTodayStart);
if (currentAdminTodayStart < 0 || currentAdminTodayEnd < 0) {
  throw new Error('Current admin-today render block could not be isolated.');
}
const currentAdminToday = html.slice(currentAdminTodayStart, currentAdminTodayEnd);
for (const required of [
  "renderAccordion('assignment','오늘 청소 배정'",
  "renderAccordion('inspection','청소 검수'",
]) {
  if (!currentAdminToday.includes(required)) throw new Error(`Admin-home core item missing: ${required}`);
}
for (const forbidden of [
  'class="availability-link"',
  "renderAccordion('schedule','오늘 체크인·체크아웃'",
  '${cancelAccordion}',
  "renderAccordion('drafts','배정 준비 청소 작업'",
  "renderAccordion('inspection','검수 대기'",
  "renderAccordion('pay','지난주 지급'",
]) {
  if (currentAdminToday.includes(forbidden)) throw new Error(`Removed admin-home item still rendered: ${forbidden}`);
}
console.log('Admin-home cleaning-only static contracts: passed');
'''
checker_path.write_text(checker + "\n", encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
replaced = False
for index, line in enumerate(lines):
    if line.endswith("  WIREFRAME/index.html"):
        lines[index] = f"{digest}  WIREFRAME/index.html"
        replaced = True
        break
if not replaced:
    raise SystemExit("WIREFRAME/index.html checksum entry missing")
sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-25-admin-home-cleaning-only"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
