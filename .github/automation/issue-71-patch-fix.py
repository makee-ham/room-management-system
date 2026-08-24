from pathlib import Path

path = Path('.github/automation/issue-71-checkout-inspection.py')
text = path.read_text(encoding='utf-8')
old = '''replace_once(
    "          if (state.adminView==='today') return renderAdminToday();",
    "          if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();",
    'today checkout inspection summary',
)'''
new = '''today_route = "          if (state.adminView==='today') return renderAdminToday();"
if today_route not in html:
    raise SystemExit('today checkout inspection summary: admin today route not found')
html = html.replace(today_route, "          if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();", 1)'''
if text.count(old) != 1:
    raise SystemExit(f'issue-71 today route patch: expected one match, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
