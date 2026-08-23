from __future__ import annotations

import hashlib
import json
from pathlib import Path

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')

replacements = [
    (
        '      let durableRenderBaselineReady=false;',
        '      let durableRenderStateRef=null;',
        'render state reference declaration',
    ),
    (
        '      function render() {\n        const durableBefore=durableLedgerFingerprint(state);\n        projectReservationState(state);',
        '      function render() {\n        const durableRenderSameState=durableRenderStateRef===state,durableBefore=durableLedgerFingerprint(state);\n        projectReservationState(state);',
        'render state reference start',
    ),
    (
        "        const durableAfter=durableLedgerFingerprint(state);if(durableRenderBaselineReady&&durableAfter!==durableBefore)throw new Error('렌더링 중 예약·청소 제출·급여·지급 원장이 변경되었습니다.');durableRenderBaselineReady=true;assertNoDuplicateDurableRecords(state);",
        "        const durableAfter=durableLedgerFingerprint(state);if(durableRenderSameState&&durableAfter!==durableBefore)throw new Error('렌더링 중 예약·청소 제출·급여·지급 원장이 변경되었습니다.');durableRenderStateRef=state;assertNoDuplicateDurableRecords(state);",
        'render state reference end',
    ),
]

for old, new, label in replacements:
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    html = html.replace(old, new, 1)

html_path.write_text(html, encoding='utf-8')

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path('SHA256SUMS.txt')
lines = sums_path.read_text(encoding='utf-8').splitlines()
found = False
updated = []
for line in lines:
    if line.endswith('  WIREFRAME/index.html'):
        updated.append(f'{digest}  WIREFRAME/index.html')
        found = True
    else:
        updated.append(line)
if not found:
    raise SystemExit('WIREFRAME/index.html checksum line missing')
sums_path.write_text('\n'.join(updated) + '\n', encoding='utf-8')

manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
