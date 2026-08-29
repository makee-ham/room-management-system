from __future__ import annotations

import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path.cwd()
HTML = (ROOT / "WIREFRAME/index.html").read_text(encoding="utf-8")
OUT = Path("/tmp/final-cleaning-template-qa")
OUT.mkdir(parents=True, exist_ok=True)
URL = "http://127.0.0.1:4173/index.html"

record_pattern = re.compile(
    r"\{id:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
    r"zone:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
    r"label:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
    r"description:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
    r"required:(true|false)[^\n{}]*\}"
)
records = []
for match in record_pattern.finditer(HTML):
    records.append({
        "id": match.group(1) or match.group(2) or "",
        "zone": match.group(3) or match.group(4) or "",
        "label": (match.group(5) or match.group(6) or "").replace("\\'", "'").replace('\\"', '"'),
        "description": (match.group(7) or match.group(8) or "").replace("\\'", "'").replace('\\"', '"'),
        "required": match.group(9) == "true",
        "source": match.group(0),
    })

assert len(records) >= 20, len(records)
assert not any(record["id"] == "entry-number" for record in records)
assert not any(not record["required"] for record in records if record["zone"] != "기타")
assert not any(record["required"] or "maxPhotos:10" not in record["source"] for record in records if record["zone"] == "기타")
assert "cleaning-photo-presentation-policy" in HTML
labels = sorted({record["label"] for record in records if record["label"]})
descriptions = sorted({record["description"] for record in records if record["description"]})


def select_options(select):
    return select.locator("option").evaluate_all(
        "els => els.map(el => ({value: el.value, text: (el.textContent || '').trim()}))"
    )


def select_indices(page):
    role_index = None
    scenario_index = None
    scenario_size = -1
    for index in range(page.locator("select").count()):
        select = page.locator("select").nth(index)
        opts = select_options(select)
        values = {item["value"] for item in opts}
        if {"admin", "maid"}.issubset(values):
            role_index = index
        elif len(opts) > scenario_size:
            scenario_size = len(opts)
            scenario_index = index
    return role_index, scenario_index


def visible_cleaning_copy(page):
    return page.evaluate(
        """([labels, descriptions]) => {
          const visible = (el) => {
            const s = getComputedStyle(el), r = el.getBoundingClientRect();
            return !el.hidden && s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
          };
          const inContext = (el) => {
            let node = el;
            for (let depth = 0; node && depth < 6; depth += 1, node = node.parentElement) {
              const text = node.textContent || '';
              if (labels.some(label => text.includes(label))) return true;
            }
            return false;
          };
          const leaves = [...document.querySelectorAll('body *')]
            .filter(el => el.children.length === 0 && visible(el))
            .map(el => ({el, text:(el.textContent || '').trim()}))
            .filter(item => item.text);
          return {
            descriptions: [...new Set(leaves.filter(item => descriptions.includes(item.text)).map(item => item.text))],
            markers: [...new Set(leaves.filter(item => (item.text === '필수' || item.text === '선택') && inContext(item.el)).map(item => item.text))],
            suffixes: leaves.filter(item => /\s·\s(?:필수|선택)\b/.test(item.text) && inContext(item.el)).map(item => item.text).slice(0, 10),
          };
        }""",
        [labels, descriptions],
    )


def assert_page(page, label, require_photo=False):
    page.wait_for_timeout(120)
    data = page.evaluate(
        """() => ({
          inner: innerWidth,
          doc: document.documentElement.scrollWidth,
          body: document.body.scrollWidth,
          title: document.title,
          text: document.body.innerText,
          hasOverlay: !!document.querySelector('[data-nextjs-dialog-overlay], vite-error-overlay, #webpack-dev-server-client-overlay')
        })"""
    )
    assert "CASTLE THE ART" in data["title"], (label, data)
    assert data["doc"] <= data["inner"] + 1 and data["body"] <= data["inner"] + 1, (label, data)
    assert not data["hasOverlay"], (label, data)
    assert "객실번호·현관" not in data["text"], label
    copy = visible_cleaning_copy(page)
    assert not copy["descriptions"], (label, copy)
    assert not copy["markers"], (label, copy)
    assert not copy["suffixes"], (label, copy)
    context = "기타" in data["text"] and any(token in data["text"] for token in ("사진", "촬영", "카메라", "갤러리", "/10"))
    if require_photo:
        assert context, label
    return context


def click_text(page, names):
    for name in names:
        matches = page.get_by_text(name, exact=True)
        for index in range(matches.count()):
            item = matches.nth(index)
            try:
                if item.is_visible() and item.is_enabled():
                    item.click(timeout=900)
                    page.wait_for_timeout(90)
                    break
            except Exception:
                continue


def explore(page, role):
    role_index, scenario_index = select_indices(page)
    assert role_index is not None
    page.locator("select").nth(role_index).select_option(role)
    page.wait_for_timeout(120)
    _, scenario_index = select_indices(page)
    scenario_values = [None]
    if scenario_index is not None:
        scenario_values = [item["value"] for item in select_options(page.locator("select").nth(scenario_index))]
    names = ["내 업무", "청소 진행 보기", "상세 보기"] if role == "maid" else ["청소", "검수 대상 목록", "더보기", "청소 템플릿", "상세 보기"]
    for value in scenario_values:
        role_index, scenario_index = select_indices(page)
        if scenario_index is not None and value is not None:
            try:
                page.locator("select").nth(scenario_index).select_option(value)
                page.wait_for_timeout(90)
            except Exception:
                pass
        click_text(page, names)
        if assert_page(page, f"{role}-{value}"):
            return True
        navs = page.locator(".nav-btn:visible, .bottom-nav button:visible")
        for index in range(min(navs.count(), 10)):
            try:
                navs.nth(index).click(timeout=800)
                page.wait_for_timeout(70)
                click_text(page, names)
                if assert_page(page, f"{role}-{value}-nav-{index}"):
                    return True
            except Exception:
                continue
    return False


report = {
    "browser": "Playwright Chromium fallback; Browser plugin unavailable",
    "widths": [],
    "maid_photo_surface": False,
    "admin_photo_surface": False,
}
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    for width in (320, 360, 390, 420, 421, 768, 1440):
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors = []
        page.on("console", lambda msg, errors=errors: errors.append(msg.text) if msg.type in ("error", "warning") else None)
        page.on("pageerror", lambda exc, errors=errors: errors.append(str(exc)))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(220)
        assert_page(page, f"smoke-{width}")
        assert not errors, (width, errors)
        report["widths"].append(width)
        page.close()

    page = browser.new_page(viewport={"width": 390, "height": 1000})
    runtime_errors = []
    page.on("console", lambda msg: runtime_errors.append(msg.text) if msg.type in ("error", "warning") else None)
    page.on("pageerror", lambda exc: runtime_errors.append(str(exc)))
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(220)
    report["maid_photo_surface"] = explore(page, "maid")
    if report["maid_photo_surface"]:
        page.screenshot(path=str(OUT / "maid-photo-surface-390.png"), full_page=True)
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(220)
    report["admin_photo_surface"] = explore(page, "admin")
    if report["admin_photo_surface"]:
        page.screenshot(path=str(OUT / "admin-photo-surface-390.png"), full_page=True)
    assert not runtime_errors, runtime_errors
    assert report["maid_photo_surface"] and report["admin_photo_surface"], report
    page.set_viewport_size({"width": 320, "height": 900})
    assert_page(page, "final-320", require_photo=True)
    page.screenshot(path=str(OUT / "cleaning-photo-surface-320.png"), full_page=True)
    browser.close()

(OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
