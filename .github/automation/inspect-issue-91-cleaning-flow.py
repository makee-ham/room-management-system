from pathlib import Path

source = Path("WIREFRAME/index.html").read_text(encoding="utf-8")


def section(label: str, needle: str, before: int = 800, after: int = 6500) -> None:
    index = source.find(needle)
    print(f"\n\n===== {label} =====")
    if index < 0:
        print(f"NOT FOUND: {needle}")
        return
    start = max(0, index - before)
    end = min(len(source), index + after)
    print(source[start:end])


queries = [
    ("ROOM PRESENTATION", "function roomPresentation(no)"),
    ("ROOM CARD STATUS AND ACTIONS", "const subBadges="),
    ("ROOM FILTER", "function filteredRooms()"),
    ("MANUAL CLEANING HELPERS", "function activeManualCleaningRequest"),
    ("MANUAL CLEANING CONTROL", "function renderManualCleaningToggle"),
    ("TOGGLE ACTION HANDLER", "case 'toggle-room-cleaning'"),
    ("TOGGLE ACTION IF HANDLER", "action==='toggle-room-cleaning'"),
    ("MODAL HELPERS", "function openModal"),
    ("MODAL CONFIRM HANDLERS", "modal-confirm"),
    ("ROOM DETAIL", "function renderRoomDetail"),
    ("TEST API", "window.__CASTLE_TEST__=Object.freeze"),
]

for label, needle in queries:
    section(label, needle)
