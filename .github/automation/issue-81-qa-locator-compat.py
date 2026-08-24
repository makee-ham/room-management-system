from pathlib import Path

path=Path('.github/automation/issue-81-room-facets.mjs')
text=path.read_text(encoding='utf-8')
old='locator(`[data-room="${'
new='locator(`article.room-card-v2[data-room="${'
count=text.count(old)
if count < 5:
    raise SystemExit(f'expected at least five room-card locators, found {count}')
path.write_text(text.replace(old,new),encoding='utf-8')
