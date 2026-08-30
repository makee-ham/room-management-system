#!/usr/bin/env python3
"""Update legacy workspace assertions for issue #123 current-stay editing rules."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts/check-workspace.mjs"
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "  \"if(room?.occupancy==='occupied'&&currentOccupiedReservation(room)?.id===reservation.id)return false\",",
        "  'function reservationCanEditCurrentStay(reservation,room=',",
        "current-stay helper",
    ),
    (
        "  'requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id',",
        "  'requestedCurrentStay=!!requested&&reservationCanEditCurrentStay(requested,room)',",
        "requested current stay",
    ),
    (
        "  'readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing)',",
        "  'readOnly=weekPast&&!currentEntry&&!editableCurrentStay',",
        "past-week current-stay edit",
    ),
]

for old, new, label in replacements:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, found {count}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("Updated workspace checks for issue #123 current-stay extensions.")
