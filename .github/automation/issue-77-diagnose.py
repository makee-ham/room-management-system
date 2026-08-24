from pathlib import Path

text = Path('WIREFRAME/index.html').read_text(encoding='utf-8')


def section(label: str, start: str, end: str | None = None, limit: int = 30000) -> None:
    begin = text.find(start)
    if begin < 0:
        print(f'\n===== {label}: START NOT FOUND: {start} =====')
        return
    if end:
        finish = text.find(end, begin + len(start))
        if finish < 0:
            finish = min(len(text), begin + limit)
        else:
            finish += len(end)
    else:
        finish = min(len(text), begin + limit)
    print(f'\n===== {label} =====')
    print(text[begin:finish][:limit])


section('TYPE PHOTO GROUPS', 'const TYPE_PHOTO_GROUPS', 'const TEMPLATE_KIND_DEMO')
section('PHOTO TEMPLATE EVIDENCE', 'const PHOTO_TEMPLATE_EVIDENCE', 'function layoutProfileFor')
section('EXPANSION', 'function expandPhotoRules', 'function templateSnapshotFor')
section('SNAPSHOT', 'function templateSnapshotFor', 'function snapshotPhotoItems')
section('MAID TASK REQUIREMENTS', 'function taskRequirements', 'function renderTaskInputSections')
section('MAID TASK RENDERER', 'function renderTaskInputSections', 'function renderTask')
section('INSPECTION HELPERS', 'function inspectionTemplateUploadItems', 'function renderInspectionTemplateReview')
section('INSPECTION RENDERER', 'function renderInspectionTemplateReview', 'function renderInspection')
section('TEMPLATE CATALOG', 'function templateCatalog', 'function renderTemplateList')
section('TEMPLATE LIST', 'function renderTemplateList', 'function renderTemplateDetail')
section('TEMPLATE DETAIL', 'function renderTemplateDetail', 'function renderTemplate')
section('TEMPLATE ROUTER', 'function renderTemplate', 'function renderAdminMore')
section('INITIAL STATE', 'function initialState', 'function initialTemplateDraft')
section('CONTROL CHANGE HANDLER', "document.addEventListener('change'", "document.addEventListener('input'")
section('CLICK HANDLER TEMPLATE ACTIONS', "if(a==='template')", "if(a==='inspection-photo')")
section('TEST API', 'window.__CASTLE_TEST__', 'applyHashParameters();')

print('\n===== TEMPLATE-RELATED STATE/COPY LINES =====')
for number, line in enumerate(text.splitlines(), 1):
    lowered = line.lower()
    if any(token in lowered for token in ('templatepreview', 'templatepreviewroom', 'templatedetail', 'templateedit', '필수 촬영 구역', '촬영 구역')):
        print(f'{number}: {line}')
