from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path.cwd()
INDEX = ROOT / "WIREFRAME/index.html"
CHECKER = ROOT / "scripts/check-workspace.mjs"
README = ROOT / "WIREFRAME/README.md"
QA = ROOT / "WIREFRAME/QA.md"
POLICY = ROOT / "DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md"
AUDIT = ROOT / "DOCS/19_TEMPLATE_PARITY_AUDIT.md"
SHA_FILE = ROOT / "SHA256SUMS.txt"
MANIFEST = ROOT / "manifest.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")


def append_once(value: str, marker: str, block: str) -> str:
    if marker in value:
        return value
    return value.rstrip() + "\n\n" + block.strip() + "\n"


def photo_records(source: str) -> list[dict[str, object]]:
    pattern = re.compile(
        r"\{id:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
        r"zone:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
        r"label:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
        r"description:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
        r"required:(true|false)[^\n{}]*\}"
    )
    result: list[dict[str, object]] = []
    for match in pattern.finditer(source):
        result.append({
            "id": match.group(1) or match.group(2) or "",
            "zone": match.group(3) or match.group(4) or "",
            "label": (match.group(5) or match.group(6) or "").replace("\\'", "'").replace('\\"', '"'),
            "description": (match.group(7) or match.group(8) or "").replace("\\'", "'").replace('\\"', '"'),
            "required": match.group(9) == "true",
            "source": match.group(0),
        })
    return result


html = read(INDEX)
old_sha = hashlib.sha256(html.encode("utf-8")).hexdigest()

# Idempotency: replace an earlier implementation of this narrowly scoped presentation policy.
html = re.sub(
    r"\n?<script id=\"cleaning-photo-presentation-policy\">.*?</script>\n?",
    "\n",
    html,
    flags=re.S,
)

# The task card already contains the room number, so remove the separate entrance/number slot.
for pattern in (
    re.compile(r"(?m)^[ \t]*\{id:'entry-number'[^\n]*\},\r?\n"),
    re.compile(r'(?m)^[ \t]*\{id:"entry-number"[^\n]*\},\r?\n'),
    re.compile(r"(?m)^[ \t]*\{[^\n]*(?:slotId|requirementId|photoId):'entry-number'[^\n]*\},?\r?\n"),
    re.compile(r'(?m)^[ \t]*\{[^\n]*(?:slotId|requirementId|photoId):"entry-number"[^\n]*\},?\r?\n'),
):
    html = pattern.sub("", html)
html = re.sub(r"(?<![\w-])['\"]entry-number['\"]\s*,\s*", "", html)
html = html.replace("객실번호·현관", "").replace("객실 번호·현관", "")

# All photo slots except 기타 require at least one photo. 기타 remains optional and max 10.
normalized: list[str] = []
for line in html.splitlines(keepends=True):
    is_photo_literal = all(token in line for token in ("{id:", "zone:", "label:", "description:", "required:"))
    if is_photo_literal and "required:false" in line:
        is_other = "zone:'기타'" in line or 'zone:"기타"' in line
        if not is_other:
            line = line.replace("required:false", "required:true")
    normalized.append(line)
html = "".join(normalized)

# New work uses a new snapshot version; existing submission objects retain their stored versions.
html = re.sub(
    r"(checkout\s*:\s*\{\s*name\s*:\s*'퇴실 청소'\s*,\s*version\s*:\s*)'v7'",
    r"\g<1>'v8'",
    html,
    count=1,
)

records = photo_records(html)
if len(records) < 20:
    raise RuntimeError(f"Cleaning photo templates could not be parsed: {len(records)} records")
if any(record["id"] == "entry-number" for record in records):
    raise RuntimeError("The entry-number slot remains in a current cleaning template")
if any(not bool(record["required"]) for record in records if record["zone"] != "기타"):
    raise RuntimeError("A non-기타 cleaning photo slot is still optional")
other = [record for record in records if record["zone"] == "기타"]
if not other:
    raise RuntimeError("No 기타 photo slot remains")
for record in other:
    if bool(record["required"]) or "maxPhotos:10" not in str(record["source"]):
        raise RuntimeError(f"기타 must remain optional with maxPhotos 10: {record}")

# Keep descriptions in the immutable template/submission metadata, but suppress them only on
# cleaning-photo presentation surfaces. Requirement markers are removed in the same narrow context.
descriptions = sorted({str(record["description"]) for record in records if str(record["description"]).strip()})
labels = sorted({str(record["label"]) for record in records if str(record["label"]).strip()})
if len(descriptions) < 10 or len(labels) < 10:
    raise RuntimeError("Could not derive cleaning photo labels/descriptions for the presentation policy")

policy_script = f'''\n<script id="cleaning-photo-presentation-policy">\n(() => {{\n  const hiddenDescriptions = new Set({json.dumps(descriptions, ensure_ascii=False)});\n  const photoLabels = new Set({json.dumps(labels, ensure_ascii=False)});\n  let scheduled = false;\n  const inPhotoContext = (start) => {{\n    let element = start instanceof Element ? start : start?.parentElement;\n    for (let depth = 0; element && depth < 6; depth += 1, element = element.parentElement) {{\n      const text = element.textContent || '';\n      if ([...photoLabels].some((label) => text.includes(label))) return true;\n    }}\n    return false;\n  }};\n  const simplify = () => {{\n    scheduled = false;\n    const root = document.body;\n    if (!root) return;\n    root.querySelectorAll('p, small, span, div').forEach((element) => {{\n      if (element.children.length) return;\n      const text = (element.textContent || '').trim();\n      const description = hiddenDescriptions.has(text);\n      const marker = (text === '필수' || text === '선택') && inPhotoContext(element);\n      if (!description && !marker) return;\n      element.hidden = true;\n      element.setAttribute('aria-hidden', 'true');\n    }});\n    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);\n    const nodes = [];\n    while (walker.nextNode()) nodes.push(walker.currentNode);\n    nodes.forEach((node) => {{\n      if (!inPhotoContext(node)) return;\n      const next = (node.nodeValue || '').replace(/\\s*·\\s*(필수|선택)\\b/g, '');\n      if (next !== node.nodeValue) node.nodeValue = next;\n    }});\n  }};\n  const schedule = () => {{\n    if (scheduled) return;\n    scheduled = true;\n    queueMicrotask(simplify);\n  }};\n  const start = () => {{\n    new MutationObserver(schedule).observe(document.body, {{ childList: true, subtree: true, characterData: true }});\n    simplify();\n  }};\n  if (document.body) start();\n  else document.addEventListener('DOMContentLoaded', start, {{ once: true }});\n}})();\n</script>\n'''
close_body = html.rfind("</body>")
if close_body < 0:
    raise RuntimeError("Closing body tag not found")
html = html[:close_body] + policy_script + html[close_body:]
write(INDEX, html)
new_sha = hashlib.sha256(html.encode("utf-8")).hexdigest()

# Keep product documentation aligned without rewriting unrelated history.
section = '''
## 2026-08-29 청소 인증 사진 단순화

- 새 청소 작업은 업무 정보에 객실 호수가 이미 표시되므로 `객실번호·현관` 사진 슬롯을 사용하지 않는다.
- `기타`를 제외한 모든 사진 슬롯은 최소 1장을 등록해야 현장 완료와 제출이 가능하다.
- `기타`만 선택 항목이며 최대 10장을 개별 등록·삭제·확대할 수 있다.
- 관리자와 메이드 화면에는 사진 슬롯의 회색 설명 문장과 `필수`·`선택` 표기를 노출하지 않는다.
- 설명, 필수 여부, 최대 사진 수는 제출 스냅샷의 검증 메타데이터로 보존한다.
- 새 퇴실 청소 템플릿은 `v8`이며, 기존 제출은 당시 저장된 템플릿 스냅샷을 유지한다.
'''
for path in (README, QA, POLICY, AUDIT):
    text = read(path)
    text = text.replace("새 퇴실 청소 `v7`", "새 퇴실 청소 `v8`")
    text = text.replace("현재 퇴실 청소 v7", "현재 퇴실 청소 v8")
    text = append_once(text, "2026-08-29 청소 인증 사진 단순화", section)
    write(path, text)

# Update exact room-type slot counts where those counts are documented on the same line.
type_counts = [
    (("스탠다드", "standard"), 9, 8),
    (("프리미어", "premium"), 10, 9),
    (("파셜 오션뷰", "oceanPremium"), 12, 11),
    (("패밀리 투룸", "oceanFamily"), 14, 13),
]
for path in (README, QA, POLICY, AUDIT):
    lines: list[str] = []
    for line in read(path).splitlines(keepends=True):
        for names, total, required in type_counts:
            if "슬롯" in line and any(name in line for name in names):
                line = re.sub(r"\b(?:10|11|13|15)개 슬롯\b", f"{total}개 슬롯", line, count=1)
                line = re.sub(r"필수\s*(?:9|10|12|14)", f"필수 {required}", line)
                line = re.sub(r"촬영\s*(?:9|10|12|14)", f"촬영 {required}", line)
        lines.append(line)
    write(path, "".join(lines))

# Retire only obsolete, one-line static expectations and update keyed count maps. Other checks stay intact.
checker = read(CHECKER)
checker = checker.replace("checkout:{name:'퇴실 청소',version:'v7'", "checkout:{name:'퇴실 청소',version:'v8'")
filtered: list[str] = []
for line in checker.splitlines(keepends=True):
    stripped = line.strip()
    obsolete_entry = ("entry-number" in line or "객실번호·현관" in line) and (
        stripped.startswith(("'", '"', "`", "{id:", "Object.freeze({id:"))
        or (stripped.startswith("if (") and stripped.endswith("}"))
    )
    obsolete_visible_marker = (" · 필수" in line or " · 선택" in line) and stripped.startswith(("'", '"', "`"))
    if obsolete_entry or obsolete_visible_marker:
        continue
    filtered.append(line)
checker = "".join(filtered)

count_map = re.compile(
    r"\{(?=[^{}]{0,650}\bstandard\b)(?=[^{}]{0,650}\bpremium\b)"
    r"(?=[^{}]{0,650}\boceanPremium\b)(?=[^{}]{0,650}\boceanFamily\b)[^{}]{0,650}\}",
    re.S,
)

def normalize_map(match: re.Match[str]) -> str:
    block = match.group(0)
    if not all(re.search(rf"\b{key}\b\s*:\s*\d+", block) for key in ("standard", "premium", "oceanPremium", "oceanFamily")):
        return block
    context = checker[max(0, match.start() - 180):match.start()].lower() + block.lower()
    required_map = "required" in context or "필수" in context
    targets = {
        "standard": 8 if required_map else 9,
        "premium": 9 if required_map else 10,
        "oceanPremium": 11 if required_map else 12,
        "oceanFamily": 13 if required_map else 14,
    }
    for key, target in targets.items():
        block = re.sub(rf"(\b{key}\b\s*:\s*)\d+", rf"\g<1>{target}", block)
    return block

checker = count_map.sub(normalize_map, checker)
new_contract = r'''

// Current cleaning-photo template contract.
const cleaningPhotoRows=[...html.matchAll(/\{id:(?:'[^']+'|"[^"]+")[^\n{}]*zone:(?:'([^']+)'|"([^"]+)")[^\n{}]*required:(true|false)[^\n{}]*\}/g)];
if(cleaningPhotoRows.length<20) throw new Error('Cleaning photo templates could not be inspected.');
for(const row of cleaningPhotoRows){
  const zone=row[1]||row[2]||'';
  const required=row[3]==='true';
  if(zone!=='기타'&&!required) throw new Error(`Non-기타 photo slot is optional: ${row[0]}`);
  if(zone==='기타'&&(required||!row[0].includes('maxPhotos:10'))) throw new Error(`기타 photo contract mismatch: ${row[0]}`);
}
if(!html.includes('cleaning-photo-presentation-policy')) throw new Error('Cleaning photo presentation policy is missing.');
'''
if "// Current cleaning-photo template contract." not in checker:
    checker = checker.rstrip() + new_contract + "\n"
write(CHECKER, checker)

# Refresh canonical integrity metadata.
sha_text = read(SHA_FILE)
sha_pattern = re.compile(r"^[0-9a-f]{64}\s+WIREFRAME/index\.html$", re.M)
if not sha_pattern.search(sha_text):
    raise RuntimeError("WIREFRAME/index.html checksum entry is missing")
write(SHA_FILE, sha_pattern.sub(f"{new_sha}  WIREFRAME/index.html", sha_text))

manifest = json.loads(read(MANIFEST))
new_size = INDEX.stat().st_size

def refresh_manifest(value):
    if isinstance(value, dict):
        identifies = any(value.get(key) == "WIREFRAME/index.html" for key in ("path", "file", "filename", "name"))
        for key, item in list(value.items()):
            low = key.lower()
            if identifies and low in {"sha256", "hash", "checksum", "digest"} and isinstance(item, str):
                value[key] = new_sha
            elif identifies and low in {"size", "bytes", "size_bytes"} and isinstance(item, int):
                value[key] = new_size
            else:
                value[key] = refresh_manifest(item)
        return value
    if isinstance(value, list):
        return [refresh_manifest(item) for item in value]
    if isinstance(value, str) and value == old_sha:
        return new_sha
    return value

write(MANIFEST, json.dumps(refresh_manifest(manifest), ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "photo_records": len(records),
    "other_records": len(other),
    "descriptions_hidden": len(descriptions),
    "old_sha": old_sha,
    "new_sha": new_sha,
}, ensure_ascii=False, indent=2))
