from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')

subprocess.run(['git', 'fetch', '--no-tags', 'origin', 'main'], check=True)
main_html = subprocess.check_output(['git', 'show', 'origin/main:WIREFRAME/index.html'], text=True)

ledger_start = '      function renderMaidPayFromLedger() {'
ledger_end = '      function renderMaidPay() {'
if ledger_start not in html:
    source_start = main_html.find(ledger_start)
    source_end = main_html.find(ledger_end, source_start)
    target = html.find(ledger_end)
    if min(source_start, source_end, target) < 0:
        raise SystemExit('maid pay ledger restoration markers are missing')
    html = html[:target] + main_html[source_start:source_end] + html[target:]

qa_bridge_start = '      function installNotificationQaBridge(){'
qa_bridge_end = '      installNotificationQaBridge();\n'
if qa_bridge_start in html:
    start = html.find(qa_bridge_start)
    end = html.find(qa_bridge_end, start)
    if end < 0:
        raise SystemExit('notification QA bridge ending marker is missing')
    html = html[:start] + html[end + len(qa_bridge_end):]

main_functions = set(re.findall(r'^\s{6}function\s+([A-Za-z_$][\w$]*)\s*\(', main_html, flags=re.MULTILINE))
feature_functions = set(re.findall(r'^\s{6}function\s+([A-Za-z_$][\w$]*)\s*\(', html, flags=re.MULTILINE))
missing_functions = sorted(main_functions - feature_functions)
if missing_functions:
    raise SystemExit(f'feature branch unexpectedly removed existing functions: {missing_functions}')
if ledger_start not in html:
    raise SystemExit('renderMaidPayFromLedger was not restored')
if '__CASTLE_NOTIFICATION_QA__' in html:
    raise SystemExit('query-gated notification QA bridge must not ship in the product file')

html_path.write_text(html, encoding='utf-8')

checker_path = Path('scripts/check-workspace.mjs')
checker = checker_path.read_text(encoding='utf-8').rstrip()
contract_marker = 'Maid pay ledger notification regression contracts: passed'
if contract_marker not in checker:
    checker += r'''

const maidPayLedgerStart = html.indexOf('function renderMaidPayFromLedger()');
const maidPayRenderStart = html.indexOf('function renderMaidPay()');
if (maidPayLedgerStart < 0 || maidPayRenderStart < 0 || maidPayLedgerStart > maidPayRenderStart) {
  throw new Error('Maid pay ledger renderer was removed while replacing the maid notification screen.');
}
if (html.includes('__CASTLE_NOTIFICATION_QA__')) {
  throw new Error('Notification QA mutation bridge must not be present in the shipped wireframe.');
}
console.log('Maid pay ledger notification regression contracts: passed');
'''
checker_path.write_text(checker + '\n', encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8').rstrip()
qa += '''

### 알림 화면 교체 회귀 보강

- 메이드 알림 화면을 교체하면서 인접한 `renderMaidPayFromLedger`가 함께 제거되지 않는지 영구 계약 검사에 추가했다.
- 메이드 역할의 주급 화면을 직접 렌더링하여 주급 원장·주차별 작업 상세가 정상 표시되는지 확인한다.
- 동적 정책 검증에만 사용한 쿼리 기반 QA 브리지는 최종 배포 파일에서 제거했다.
'''
qa_path.write_text(qa + '\n', encoding='utf-8')

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8').rstrip()
readme += '''

- 알림 센터 교체 후에도 기존 메이드 주급 원장 화면과 주차별 작업 내역은 그대로 유지된다.
'''
readme_path.write_text(readme + '\n', encoding='utf-8')

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path('SHA256SUMS.txt')
lines = sums_path.read_text(encoding='utf-8').splitlines()
for index, line in enumerate(lines):
    if line.endswith('  WIREFRAME/index.html'):
        lines[index] = f'{digest}  WIREFRAME/index.html'
        break
else:
    raise SystemExit('WIREFRAME/index.html checksum entry missing')
sums_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version'] = '2026-08-25-event-notification-center-v2'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
