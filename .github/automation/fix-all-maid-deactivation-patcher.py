from pathlib import Path

path = Path('.github/automation/apply-all-maid-deactivation.py')
text = path.read_text(encoding='utf-8')

replacements = {
    "function maidStatusFor(maidId) { return maidId==='m1'?state.maidStatus:(state.maidStatusById?.[maidId]||'inactive'); }":
        "function maidStatusFor(maidId) { return maidId==='m1'?state.maidStatus:(state.maidStatusById?.[maidId]||'active'); }",
    "if css_marker in html and \".maid-account-management\" not in html:\n    html = html.replace(css_marker, css_marker + \"\\n    .maid-account-management { margin-top:4px; border-color:#efc3c7; background:#fffafa; }\\n    .maid-account-management .section-head { align-items:flex-start; }\\n    .maid-deactivation-gate { margin-top:12px; padding-top:12px; border-top:1px solid #efd5d7; }\", 1)":
        "if css_marker in html and \"/* All-maid lower account management */\" not in html:\n    html = html.replace(css_marker, css_marker + \"\\n    /* All-maid lower account management */\\n    .maid-account-management { margin-top:4px; border-color:#efc3c7; background:#fffafa; }\\n    .maid-account-management .section-head { align-items:flex-start; }\\n    .maid-deactivation-gate { margin-top:12px; padding-top:12px; border-top:1px solid #efd5d7; }\", 1)",
}

for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'patcher correction marker missing: {old[:120]}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
