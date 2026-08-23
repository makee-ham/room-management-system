from __future__ import annotations

import hashlib
import json
from pathlib import Path

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')
old = "        const existing=earningRecordFor(no);if(existing)return {record:existing,created:false,unpaid:false};"
new = "        const existing=state.earningRecords?.[submission.id]||earningRecordFor(no);if(existing)return {record:existing,created:false,unpaid:false};"
count = html.count(old)
if count != 1:
    raise SystemExit(f'earning direct-key guard mismatch: {count}')
html_path.write_text(html.replace(old, new, 1), encoding='utf-8')

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
