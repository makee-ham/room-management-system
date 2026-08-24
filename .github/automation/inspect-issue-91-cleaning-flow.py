from pathlib import Path
import re

source = Path("WIREFRAME/index.html").read_text(encoding="utf-8")


def section(label: str, needle: str, before: int = 900, after: int = 7000, occurrence: int = 0) -> None:
    indexes=[]
    start=0
    while True:
        index=source.find(needle,start)
        if index<0: break
        indexes.append(index)
        start=index+max(1,len(needle))
    print(f"\n\n===== {label} =====")
    if not indexes:
        print(f"NOT FOUND: {needle}")
        return
    selected=indexes[occurrence] if occurrence < len(indexes) else indexes[-1]
    print(f"occurrences={len(indexes)} selected={occurrence if occurrence < len(indexes) else len(indexes)-1}")
    print(source[max(0,selected-before):min(len(source),selected+after)])


def all_contexts(label: str, needle: str, before: int = 500, after: int = 1800) -> None:
    print(f"\n\n===== {label} =====")
    start=0
    count=0
    while True:
        index=source.find(needle,start)
        if index<0: break
        count+=1
        print(f"\n--- occurrence {count} at {index} ---")
        print(source[max(0,index-before):min(len(source),index+after)])
        start=index+len(needle)
    if not count: print(f"NOT FOUND: {needle}")


for label, needle, occurrence in [
    ("ROOM PRESENTATION", "function roomPresentation(no)", 0),
    ("ROOM CARD STATUS AND ACTIONS", "const subBadges=", 0),
    ("ROOM FILTER", "function filteredRooms()", 0),
    ("MANUAL CLEANING HELPERS", "function activeManualCleaningRequest", 0),
    ("MANUAL CLEANING CONTROL", "function renderManualCleaningToggle", 0),
    ("CURRENT ROOM DETAIL", "function renderRoomDetail(no)", 0),
    ("CURRENT ROOM DETAIL SECOND", "function renderRoomDetail(no)", 1),
    ("CLICK DELEGATION", "closest('[data-action]')", 0),
    ("CLICK DELEGATION DOUBLE QUOTE", 'closest("[data-action]")', 0),
    ("RAW CLOSE MODAL", "rawCloseModal", 0),
    ("MODAL ROOT", "modal-root", 0),
    ("OPEN DIALOG", "showModal()", 0),
    ("TEST API", "window.__CASTLE_TEST__=Object.freeze", 0),
]:
    section(label,needle,occurrence=occurrence)

all_contexts("ALL TOGGLE ACTION OCCURRENCES", "toggle-room-cleaning")
all_contexts("ALL MODAL CONFIRM OCCURRENCES", "confirm-modal")
all_contexts("ALL CLEANING MODAL WORDS", "청소 필요 ON")

print("\n\n===== FUNCTION NAMES CONTAINING MODAL OR CONFIRM =====")
for match in re.finditer(r"function\s+([A-Za-z0-9_$]*(?:Modal|modal|Confirm|confirm)[A-Za-z0-9_$]*)\s*\(",source):
    print(match.group(1), match.start())

print("\n\n===== LINES CONTAINING TOGGLE/MODAL ACTION KEYWORDS =====")
for line_number,line in enumerate(source.splitlines(),1):
    if any(keyword in line for keyword in ["toggle-room-cleaning","rawCloseModal","showModal","modalState","pendingModal","confirmAction","data-modal","modal-confirm"]):
        print(f"{line_number}: {line}")
