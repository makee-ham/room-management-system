from pathlib import Path

path = Path('.github/automation/apply-demo-date-all-maid-availability.py')
text = path.read_text(encoding='utf-8')

old_output = '"quickReservationAnchorDate:DEMO_TODAY, quickReservationFollowsToday:true"'
new_output = '"quickReservationAnchorDate:\'2026-08-15\', quickReservationFollowsToday:true"'
if text.count(old_output) != 1:
    raise SystemExit(f'expected one base-anchor replacement output, found {text.count(old_output)}')
text = text.replace(old_output, new_output, 1)

old_contract = "'quickReservationAnchorDate:DEMO_TODAY, quickReservationFollowsToday:true'"
new_contract = '"quickReservationAnchorDate:\'2026-08-15\', quickReservationFollowsToday:true"'
if text.count(old_contract) != 1:
    raise SystemExit(f'expected one base-anchor static contract, found {text.count(old_contract)}')
text = text.replace(old_contract, new_contract, 1)

path.write_text(text, encoding='utf-8')
