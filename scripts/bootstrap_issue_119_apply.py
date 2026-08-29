#!/usr/bin/env python3
"""Adjust the one-shot issue #119 generator to the current single-file wireframe."""
from pathlib import Path

path = Path(__file__).with_name("apply_issue_119.py")
text = path.read_text(encoding="utf-8")

replacements = {
    'html = replace_once(html, "\\n    </style>", css + "\\n    </style>", "insert issue 119 CSS")':
        'html = replace_once(html, "\\n  </style>", css + "\\n  </style>", "insert issue 119 CSS")',
    'html = replace_once(html, "      function baseState(id=0) {", auth_helpers + "      function baseState(id=0) {", "insert authentication helpers")':
        'html = replace_once(html, "      function baseState(scenario = 0) {", auth_helpers + "      function baseState(scenario = 0) {", "insert authentication helpers")',
    'pattern = rf"      function {re.escape(start_name)}\\([^\\n]*?\\) \\{{.*?\\n      \\}}\\n(?=\\n      function {re.escape(next_name)}\\()"':
        'pattern = rf"      function {re.escape(start_name)}\\([^\\n]*?\\) \\{{.*?\\n      \\}}\\n(?=\\s*      function {re.escape(next_name)}\\()"',
}

for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("Normalized issue #119 apply script for the current wireframe.")
