from __future__ import annotations

import hashlib
import json
from pathlib import Path

html_path=Path('WIREFRAME/index.html')
html=html_path.read_text(encoding='utf-8')
old="TV 슬롯은 켜짐·화면 출력과 계정·QR·알림 없는 중립 화면까지 확인하세요."
new="TV 항목은 켜짐·화면 출력 요구사항까지 확인하세요. 계정·QR·알림 없는 중립 화면인지도 확인하세요."
if html.count(old)!=1:
    raise SystemExit(f'TV inspection compatibility copy: expected one match, found {html.count(old)}')
html_path.write_text(html.replace(old,new,1),encoding='utf-8')

digest=hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path=Path('SHA256SUMS.txt')
lines=sums_path.read_text(encoding='utf-8').splitlines()
sums_path.write_text('\n'.join(f'{digest}  WIREFRAME/index.html' if line.endswith('  WIREFRAME/index.html') else line for line in lines)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
