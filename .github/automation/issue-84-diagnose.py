from pathlib import Path

text = Path('WIREFRAME/index.html').read_text(encoding='utf-8')


def show(label: str, start: str, end: str, occurrence: int = 1) -> None:
    offset = 0
    index = -1
    for _ in range(occurrence):
        index = text.find(start, offset)
        if index < 0:
            print(f'===== {label}: START NOT FOUND: {start} =====')
            return
        offset = index + len(start)
    finish = text.find(end, index + len(start))
    if finish < 0:
        print(f'===== {label}: END NOT FOUND: {end} =====')
        return
    print(f'\n===== {label} =====\n')
    print(text[index:finish])

show('TYPE LAYOUT PROFILES', '      const TYPE_LAYOUT_PROFILES', '      function layoutProfileFor')
show('TYPE PHOTO GROUPS', '      const TYPE_PHOTO_GROUPS', '      const TEMPLATE_KIND_DEMO')
show('TEMPLATE SNAPSHOT', '      function templateSnapshotFor(roomNo', '      function legacyCheckoutTemplateSnapshotFor')
show('LEGACY SNAPSHOTS', '      function legacyCheckoutTemplateSnapshotFor', '      function templateSnapshotForSubmission')
show('TEMPLATE LIST', '      function renderTemplateList()', '      function renderTemplateTimeline')
show('TEMPLATE DETAIL', '      function renderTemplateDetail(id', '      function readTemplateChange')
show('INSPECTION HELPERS', '      function inspectionTemplateUploadItems', '      function openInspectionPhoto')
show('INSPECTION DETAIL', '      function renderInspectionDetail(no)', '      function renderPayDetail')
show('RENDER DETAIL', '      function renderDetail()', '      function renderCoach')
show('TITLE', '      function titleForView()', '      function renderMain()')
show('CHANGE HANDLER', "      document.addEventListener('change',e=>{", "      document.addEventListener('input'")
show('TEMPLATE CLICK HANDLERS', "        if(a==='template')", "        if(a==='inspection-photo')")
show('TEST API', '        window.__CASTLE_TEST__=Object.freeze({', '        });\n      }')
