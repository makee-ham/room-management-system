from pathlib import Path

path = Path('.github/automation/qa-modal-scroll-quick-booking-ux.mjs')
text = path.read_text(encoding='utf-8')
old = "await mobile.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight));"
new = "await mobile.evaluate(()=>{const root=document.documentElement,previous=root.style.scrollBehavior;root.style.scrollBehavior='auto';window.scrollTo(0,root.scrollHeight);root.style.scrollBehavior=previous;});"
if text.count(old) != 1:
    raise SystemExit(f'QA bottom scroll patch mismatch: {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
