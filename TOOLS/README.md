# Reproduction tools

## Current reproducible path

From the package root:

```bash
python TOOLS/patch_castle_v13.py
python TOOLS/patch_v13_maid_candle_permissions.py
cp CURRENT/castle_the_art_room_manager_wireframe_v13.html CURRENT/index.html
```

The two patch scripts are package-relative. They transform `HISTORY/castle_the_art_room_manager_wireframe_v12.html` into the final v13 prototype, then apply the maid candle-permission guard. The resulting v13 file must match the SHA-256 recorded in `manifest.json`.

Run the current verification suites afterward:

```bash
python QA/focused_v13/qa_castle_v13.py
python QA/extended_v13/qa_castle_v13_handoff.py
node --check CURRENT/castle_v13_script.js
```

The Playwright scripts use `CHROMIUM_PATH` when set, otherwise they search common Chromium/Chrome executable names and finally fall back to Playwright's installed browser.

## Archive

`ARCHIVE/` contains environment-specific build/capture scripts and pre-v13 patch scripts retained only for traceability. Do not use them as the implementation source of truth.
