from __future__ import annotations

import re
from pathlib import Path

path = Path('scripts/check-workspace.mjs')
text = path.read_text(encoding='utf-8')
pattern = r'''\nfor \(const contract of \[\n  "if\(a==='manual-checkout'\)",.*?\n\]\) \{\n  if \(!html\.includes\(contract\)\) throw new Error\(`Manual checkout contract missing: \$\{contract\}`\);\n\}\n'''
text, count = re.subn(pattern, '\n', text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'obsolete manual checkout contract block: expected one match, found {count}')
path.write_text(text, encoding='utf-8')
