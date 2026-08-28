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
    ".quick-grid-shell { overflow:visible; }",
    ".quick-grid-shell { overflow-x:clip; overflow-y:visible; }",
    "mobile quick-grid horizontal clipping",
)
'''
if text.count(insert_marker) != 1:
    raise SystemExit(f'quick-booking insertion marker mismatch: {text.count(insert_marker)}')
if 'mobile quick-grid horizontal clipping' in text:
    raise SystemExit('mobile quick-grid overflow patch already inserted unexpectedly')
text = text.replace(insert_marker, insert_marker + insert, 1)

contract_marker = '''  '간편 예약 · 8월 15일 기준',
'''
contract_replacement = '''  '간편 예약 · 8월 15일 기준',
  '.quick-grid-shell { overflow-x:clip; overflow-y:visible; }',
'''
if text.count(contract_marker) != 1:
    raise SystemExit(f'quick-window contract marker mismatch: {text.count(contract_marker)}')
text = text.replace(contract_marker, contract_replacement, 1)

path.write_text(text, encoding='utf-8')
