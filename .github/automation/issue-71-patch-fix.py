from pathlib import Path

path = Path('.github/automation/issue-71-checkout-inspection.py')
text = path.read_text(encoding='utf-8')
old_route = '''replace_once(
    "          if (state.adminView==='today') return renderAdminToday();",
    "          if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();",
    'today checkout inspection summary',
)'''
new_route = '''today_route = "          if (state.adminView==='today') return renderAdminToday();"
if today_route not in html:
    raise SystemExit('today checkout inspection summary: admin today route not found')
html = html.replace(today_route, "          if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();", 1)'''
if text.count(old_route) != 1:
    raise SystemExit(f'issue-71 today route patch: expected one match, found {text.count(old_route)}')
text = text.replace(old_route, new_route, 1)
old_contract = "  'data-action=\"complete-checkout-inspection\"',"
new_contract = "  \"'complete-checkout-inspection'\","
if text.count(old_contract) != 1:
    raise SystemExit(f'issue-71 button contract patch: expected one match, found {text.count(old_contract)}')
text = text.replace(old_contract, new_contract, 1)
path.write_text(text, encoding='utf-8')
