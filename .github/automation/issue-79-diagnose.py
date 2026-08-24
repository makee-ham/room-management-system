from pathlib import Path
import re

html = Path('WIREFRAME/index.html').read_text(encoding='utf-8')


def show(title: str, start: str, end: str | None = None) -> None:
    print(f'\n===== {title} =====')
    begin = html.find(start)
    if begin < 0:
        print(f'START NOT FOUND: {start}')
        return
    if end is None:
        print(html[begin:begin + 6000])
        return
    finish = html.find(end, begin + len(start))
    if finish < 0:
        print(f'END NOT FOUND: {end}')
        print(html[begin:begin + 12000])
        return
    print(html[begin:finish])


show('LAYOUT PROFILE CONSTANTS', 'const DEFAULT_LAYOUT_PROFILES', 'const TYPE_PHOTO_GROUPS')
show('PHOTO RULE EXPANSION', 'function layoutProfileFor', 'const TYPE_PHOTO_GROUPS')
show('TEMPLATE PARITY HELPERS', 'function templateRooms', 'function templateSnapshotFor')
show('TEMPLATE SNAPSHOT', 'function templateSnapshotFor', 'function legacyCheckoutTemplateSnapshotFor')
show('TEMPLATE LIST', 'function renderTemplateList', 'function renderTemplateTimeline')
show('TEMPLATE DETAIL', 'function renderTemplateDetail', 'function readTemplateChange')
show('TASK RENDERER', 'function renderTaskInputSections', 'function cleaningPrimary')
show('INSPECTION REVIEW', 'function renderInspectionTemplateReview', 'function openInspectionPhoto')
show('CONTROL CHANGE HANDLER', "document.addEventListener('change',e=>{", "document.addEventListener('input'")
show('TEST API', 'window.__CASTLE_TEST__=Object.freeze({', '});\n      }\n      installCastleTestApi')

print('\n===== LAYOUT/TEMPLATE COPY MATCHES =====')
for number, line in enumerate(html.splitlines(), 1):
    if any(token in line for token in [
        'ROOM_LAYOUT_PROFILES', 'DEFAULT_LAYOUT_PROFILES', 'templatePreviewRoom',
        'template-preview-room', '레이아웃 확인', '최소 공통', '실제 슬롯',
        'templateSlotRange', 'templateSlotStats', 'templateParityData',
    ]):
        print(f'{number}: {line}')

for path in [
    Path('DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md'),
    Path('DOCS/19_TEMPLATE_PARITY_AUDIT.md'),
    Path('WIREFRAME/QA.md'),
    Path('WIREFRAME/README.md'),
    Path('scripts/check-workspace.mjs'),
]:
    print(f'\n===== {path} =====')
    text = path.read_text(encoding='utf-8')
    if path.name in {'18_TYPE_PHOTO_TEMPLATE_POLICY.md', '19_TEMPLATE_PARITY_AUDIT.md'}:
        print(text)
    else:
        for number, line in enumerate(text.splitlines(), 1):
            if any(token in line for token in [
                'ROOM_LAYOUT_PROFILES', '레이아웃 확인', '최소 공통', '11~15',
                'template parity', 'Template parity', '템플릿 정합', '메이드 실제',
                '645', '542', '112실', '9실', 'template-preview-room',
            ]):
                print(f'{number}: {line}')
