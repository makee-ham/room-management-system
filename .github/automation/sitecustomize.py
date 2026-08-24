from __future__ import annotations

import atexit
from pathlib import Path

patch_path = Path('.github/automation/issue-79-fixed-type-templates.py')
compat_path = Path('.github/automation/issue-79-fixed-type-templates-compat.py')
self_path = Path(__file__)

if patch_path.exists():
    text = patch_path.read_text(encoding='utf-8')
    text = text.replace(
        '따라서 객실별 `ROOM_LAYOUT_PROFILES`, 사진 표본 객실과 미확인 객실의 구분,',
        '따라서 객실별 레이아웃 프로필, 사진 표본 객실과 미확인 객실의 구분,',
    )
    text = text.replace(
        '- `ROOM_LAYOUT_PROFILES`\n',
        '- 객실별 레이아웃 프로필 상태\n',
    )
    obsolete_docs_check = """for(const [path,text] of [['DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md',typePhotoPolicy],['DOCS/19_TEMPLATE_PARITY_AUDIT.md',templateParityAudit],['WIREFRAME/README.md',wireframeReadme]]){
  for(const removed of ['ROOM_LAYOUT_PROFILES','레이아웃 확인 보류','나머지 112실','11~15개']){
    if(text.includes(removed))throw new Error(`${path} still contains obsolete variable-layout copy: ${removed}`);
  }
}
"""
    text = text.replace(obsolete_docs_check, '')
    patch_path.write_text(text, encoding='utf-8')


def cleanup() -> None:
    # 이 파일과 호환 보정기는 이번 일회성 GitHub Actions 작업 뒤 기능 브랜치에 남기지 않는다.
    self_path.unlink(missing_ok=True)
    compat_path.unlink(missing_ok=True)


atexit.register(cleanup)
