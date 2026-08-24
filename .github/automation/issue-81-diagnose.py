from __future__ import annotations

from pathlib import Path

html = Path('WIREFRAME/index.html').read_text(encoding='utf-8')


def extract(marker: str, before: int = 800, after: int = 7000, start: int = 0) -> int:
    index = html.find(marker, start)
    print(f'\n===== {marker} @ {index} =====')
    if index < 0:
        print('NOT FOUND')
        return -1
    left = max(0, index - before)
    right = min(len(html), index + after)
    print(html[left:right])
    return index


def extract_all(marker: str, before: int = 400, after: int = 5000, limit: int = 10) -> None:
    offset = 0
    count = 0
    while count < limit:
        index = html.find(marker, offset)
        if index < 0:
            break
        extract(marker, before, after, index)
        offset = index + len(marker)
        count += 1
    print(f'\nTOTAL {marker}: {count}')


for marker in [
    'function roomPrimaryAction',
    'function roomPresentation',
    'function roomCard',
    'function filteredRooms',
    'function renderRoomDetailStandard',
    'function renderOccupancyPanel',
    'function renderManualCleaningToggle',
    'function roomNeedsCleaningNow',
    'function roomCleaningStageLabel',
    'function renderCheckoutInspectionPanel',
    'const ROOM_EXPORT_COLUMNS',
    'function roomExportRows',
    'function renderRoomTable',
    'function renderRoomRows',
    'function installCastleTestApi',
    'function renderMain',
    'const originalRenderRooms',
    'renderRooms=',
    'const originalRenderAdminToday',
    'renderAdminToday=',
    '.concept-status-panel {',
    '.room-status-subs {',
]:
    extract(marker)

for marker in [
    'function renderRooms()',
    'function renderAdminToday()',
    'roomPresentation(',
    'primaryCounts=',
    "presentation.key==='occupied'",
    "presentation.key==='cleaning'",
]:
    extract_all(marker)
