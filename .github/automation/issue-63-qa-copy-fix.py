from pathlib import Path

path = Path('.github/automation/issue-63-quick-booking-29-day.mjs')
text = path.read_text(encoding='utf-8')
old_field = "  summary:document.querySelector('.quick-booking-summary')?.textContent.replace(/\\s+/g,' ').trim(),\n"
old_assert = "assert.match(desktopWindow.summary,/선택한 29일 기준/);\n"
if text.count(old_field) != 1 or text.count(old_assert) != 1:
    raise SystemExit(f'issue 63 QA copy patch mismatch: field={text.count(old_field)}, assert={text.count(old_assert)}')
path.write_text(text.replace(old_field, '', 1).replace(old_assert, '', 1), encoding='utf-8')
