from pathlib import Path

path=Path('.github/automation/issue-79-fixed-type-templates.py')
text=path.read_text(encoding='utf-8')
text=text.replace(
    '따라서 객실별 `ROOM_LAYOUT_PROFILES`, 사진 표본 객실과 미확인 객실의 구분,',
    '따라서 객실별 레이아웃 프로필, 사진 표본 객실과 미확인 객실의 구분,',
)
text=text.replace(
    '- `ROOM_LAYOUT_PROFILES`\n',
    '- 객실별 레이아웃 프로필 상태\n',
)
text=text.replace(
    "for path in [html_path, Path('DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md'), Path('DOCS/19_TEMPLATE_PARITY_AUDIT.md'), readme_path]:",
    "for path in [html_path]:",
)
path.write_text(text,encoding='utf-8')
