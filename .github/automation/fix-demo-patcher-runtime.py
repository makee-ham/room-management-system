from pathlib import Path

path = Path('.github/automation/apply-demo-date-all-maid-availability.py')
text = path.read_text(encoding='utf-8')
old = '"quickReservationAnchorDate:DEMO_TODAY, quickReservationFollowsToday:true"'
new = '"quickReservationAnchorDate:\'2026-08-15\', quickReservationFollowsToday:true"'
count = text.count(old)
if count != 2:
    raise SystemExit(f'expected two DEMO_TODAY base-anchor contracts, found {count}')
text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
