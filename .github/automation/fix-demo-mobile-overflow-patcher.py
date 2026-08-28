from pathlib import Path

path = Path('.github/automation/apply-demo-date-all-maid-availability.py')
text = path.read_text(encoding='utf-8')

insert_marker = '''replace_once(
    "<h2>간편 예약</h2>${infoTip('quick-booking'",
    "<h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking'",
    "admin concise quick reservation title",
)
'''
insert = '''
replace_once(
    ".quick-booking-page { display:grid; gap:14px; min-width:0; }",
    ".quick-booking-page { display:grid; grid-template-columns:minmax(0,1fr); gap:14px; min-width:0; }",
    "quick-booking single constrained grid track",
)
replace_once(
    ".quick-grid-shell { overflow:visible; }",
    ".quick-grid-shell { overflow-x:clip; overflow-y:visible; }",
    "mobile quick-grid horizontal clipping",
)
replace_once(
    "box-shadow:0 5px 14px rgba(20,36,55,.12);",
    "box-shadow:inset 0 -1px 0 rgba(20,36,55,.12);",
    "mobile quick-grid sticky-header inset divider",
)
'''
if text.count(insert_marker) != 1:
    raise SystemExit(f'quick-booking insertion marker mismatch: {text.count(insert_marker)}')
if 'quick-booking single constrained grid track' in text:
    raise SystemExit('quick-booking grid-track patch already inserted unexpectedly')
text = text.replace(insert_marker, insert_marker + insert, 1)

contract_marker = '''  '간편 예약 · 8월 15일 기준',
'''
contract_replacement = '''  '간편 예약 · 8월 15일 기준',
  '.quick-booking-page { display:grid; grid-template-columns:minmax(0,1fr); gap:14px; min-width:0; }',
  '.quick-grid-shell { overflow-x:clip; overflow-y:visible; }',
  'box-shadow:inset 0 -1px 0 rgba(20,36,55,.12);',
'''
if text.count(contract_marker) != 1:
    raise SystemExit(f'quick-window contract marker mismatch: {text.count(contract_marker)}')
text = text.replace(contract_marker, contract_replacement, 1)

path.write_text(text, encoding='utf-8')
