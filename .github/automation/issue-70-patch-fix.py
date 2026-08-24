from pathlib import Path

path = Path('.github/automation/issue-70-auto-occupancy.py')
text = path.read_text(encoding='utf-8')
old = '''regex_once(r"\\n        if\\(a==='manual-checkout'\\)\\{.*?\\n        if\\(a==='create-stayover'\\)\\{","\\n        if(a==='create-stayover'){",'remove manual check-in/out handlers',re.S)'''
new = "# 수동 입퇴실 핸들러는 액션 등록과 화면에서만 차단하고, 기존 예약 저장 흐름을 보존한다."
if text.count(old) != 1:
    raise SystemExit(f'issue-70 broad handler removal: expected one match, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
