from __future__ import annotations

from pathlib import Path

html = Path('WIREFRAME/index.html').read_text(encoding='utf-8')


def extract(marker: str, before: int = 800, after: int = 5000) -> None:
    index = html.find(marker)
    print(f'\n===== {marker} =====')
    if index < 0:
        print('NOT FOUND')
        return
    start = max(0, index - before)
    end = min(len(html), index + after)
    print(html[start:end])


for marker in [
    'function roomPresentation',
    'function filteredRooms',
    'function renderRooms',
    'function renderRoomCard',
    'function roomCard',
    'function renderRoomDetail',
    'function roomNeedsCleaningNow',
    'function roomCleaningStageLabel',
    'function checkoutInspectionPending',
    'function checkoutInspectionCompletion',
    'const ROOM_EXPORT_COLUMNS',
    'function roomExportRows',
    'function renderAdminToday',
    'function todayCheckoutInspection',
    "if(c==='room-filter')",
    "if(a==='filter-room-type')",
    'window.__CASTLE_TEST__',
]:
    extract(marker)

print('\n===== OCCURRENCES: roomPresentation / .status / occupied =====')
for token in ['roomPresentation(', '.status', "roomFilter==='occupied'", "roomFilter==='cleaning'", "roomFilter==='available'", "roomFilter==='blocked'", 'checkout-inspection']:
    print(f'\n--- {token} ---')
    offset = 0
    shown = 0
    while shown < 20:
        index = html.find(token, offset)
        if index < 0:
            break
        print(html[max(0, index-250):min(len(html), index+500)].replace('\n', ' '))
        offset = index + len(token)
        shown += 1
