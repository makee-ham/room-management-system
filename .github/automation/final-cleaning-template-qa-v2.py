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

pattern = re.compile(
    r"\{id:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
    r"zone:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
    r"label:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
    r"description:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
    r"required:(true|false)[^\n{}]*\}"
)
records = []
for match in pattern.finditer(HTML):
    records.append({
        "id": match.group(1) or match.group(2) or "",
        "zone": match.group(3) or match.group(4) or "",
        "label": (match.group(5) or match.group(6) or "").replace("\\'", "'").replace('\\"', '"'),
        "description": (match.group(7) or match.group(8) or "").replace("\\'", "'").replace('\\"', '"'),
        "required": match.group(9) == "true",
        "source": match.group(0),
    })
assert len(records) >= 20
assert not any(row["id"] == "entry-number" for row in records)
assert all(row["required"] for row in records if row["zone"] != "기타")
assert all((not row["required"] and "maxPhotos:10" in row["source"]) for row in records if row["zone"] == "기타")
assert "cleaning-photo-presentation-policy" in HTML
labels = sorted({row["label"] for row in records if row["label"]})
descriptions = sorted({row["description"] for row in records if row["description"]})


def options(select):
    return select.locator("option").evaluate_all("els => els.map(el => ({value:el.value,text:(el.textContent||'').trim()}))")


def selector_indices(page):
    role = None
    scenario = None
    largest = -1
    for index in range(page.locator("select").count()):
        opts = options(page.locator("select").nth(index))
        values = {item["value"] for item in opts}
        if {"admin", "maid"}.issubset(values):
            role = index
        elif len(opts) > largest:
            scenario = index
            largest = len(opts)
    return role, scenario


def visible_policy_failures(page):
    return page.evaluate(
        """([labels, descriptions]) => {
          const visible = el => {
            const s=getComputedStyle(el), r=el.getBoundingClientRect();
            return !el.hidden && s.display!=='none' && s.visibility!=='hidden' && r.width>0 && r.height>0;
          };
          const inContext = el => {
            let node=el;
            for(let depth=0;node && depth<6;depth+=1,node=node.parentElement){
              const text=node.textContent||'';
              if(labels.some(label=>text.includes(label))) return true;
            }
            return false;
          };
          const leaves=[...document.querySelectorAll('body *')]
            .filter(el=>el.children.length===0 && visible(el))
            .map(el=>({el,text:(el.textContent||'').trim()})).filter(x=>x.text);
          return {
            descriptions:[...new Set(leaves.filter(x=>descriptions.includes(x.text)).map(x=>x.text))],
            markers:[...new Set(leaves.filter(x=>(x.text==='필수'||x.text==='선택')&&inContext(x.el)).map(x=>x.text))],
            suffixes:leaves.filter(x=>/\s·\s(?:필수|선택)\b/.test(x.text)&&inContext(x.el)).map(x=>x.text).slice(0,10),
          };
        }""",
        [labels, descriptions],
    )


def assert_page(page, label):
    page.wait_for_timeout(100)
    data = page.evaluate("""() => ({
      inner:innerWidth, doc:document.documentElement.scrollWidth, body:document.body.scrollWidth,
      title:document.title, text:document.body.innerText,
      overlay:!!document.querySelector('[data-nextjs-dialog-overlay],vite-error-overlay,#webpack-dev-server-client-overlay')
    })""")
    assert "CASTLE THE ART" in data["title"], (label, data)
    assert data["doc"] <= data["inner"] + 1 and data["body"] <= data["inner"] + 1, (label, data)
    assert not data["overlay"], (label, data)
    assert "객실번호·현관" not in data["text"], label
    failures = visible_policy_failures(page)
    assert not failures["descriptions"], (label, failures)
    assert not failures["markers"], (label, failures)
    assert not failures["suffixes"], (label, failures)


def set_role(page, role):
    role_index, _ = selector_indices(page)
    assert role_index is not None
    page.locator("select").nth(role_index).select_option(role)
    page.wait_for_timeout(120)


def click_named(page, names):
    for name in names:
        matches = page.get_by_text(name, exact=True)
        for index in range(matches.count()):
            target = matches.nth(index)
            try:
                if target.is_visible() and target.is_enabled():
                    target.click(timeout=850)
                    page.wait_for_timeout(80)
                    break
            except Exception:
                continue


def has_actual_photo_surface(page):
    text = page.locator("body").inner_text()
    return "기타" in text and any(token in text for token in ("카메라", "갤러리", "/10", "사진 추가", "촬영"))


def try_actual_surface(page, role):
    set_role(page, role)
    _, scenario_index = selector_indices(page)
    scenarios = [None]
    if scenario_index is not None:
        scenarios = [item["value"] for item in options(page.locator("select").nth(scenario_index))]
    names = (
        ["내 업무", "청소 시작", "계속 청소", "청소 진행 보기", "업무 상세", "상세 보기", "사진 등록"]
        if role == "maid"
        else ["청소", "검수 대상 목록", "검수하기", "검수 상세", "더보기", "청소 템플릿", "상세 보기"]
    )
    for value in scenarios:
        set_role(page, role)
        _, scenario_index = selector_indices(page)
        if scenario_index is not None and value is not None:
            try:
                page.locator("select").nth(scenario_index).select_option(value)
                page.wait_for_timeout(80)
            except Exception:
                pass
        click_named(page, names)
        assert_page(page, f"{role}-{value}")
        if has_actual_photo_surface(page):
            return True
        # Exercise safe visible controls; confirmation dialogs are closed rather than confirmed.
        controls = page.locator("button:visible, [role=button]:visible")
        for index in range(min(controls.count(), 32)):
            control = controls.nth(index)
            try:
                text = (control.inner_text() or "").strip()
                if any(stop in text for stop in ("삭제", "승인", "반려", "지급", "비활성", "운영 중지")):
                    continue
                control.click(timeout=650)
                page.wait_for_timeout(60)
                page.keyboard.press("Escape")
                if has_actual_photo_surface(page):
                    assert_page(page, f"{role}-{value}-control-{index}")
                    return True
            except Exception:
                continue
    return False


def synthetic_rerender_probe(page, role):
    set_role(page, role)
    label = labels[0]
    description = descriptions[0]
    page.evaluate(
        """([role,label,description]) => {
          document.getElementById('qa-cleaning-policy-probe')?.remove();
          const section=document.createElement('section');
          section.id='qa-cleaning-policy-probe';
          section.setAttribute('data-role',role);
          section.style.cssText='margin:16px;padding:16px;background:white;border:1px solid #dbe3eb';
          const title=document.createElement('strong'); title.textContent=label;
          const desc=document.createElement('p'); desc.textContent=description; desc.style.color='#7d8998';
          const suffix=document.createElement('span'); suffix.textContent=label+' · 필수';
          const marker=document.createElement('small'); marker.textContent='선택';
          section.append(title,desc,suffix,marker); document.body.append(section);
        }""",
        [role, label, description],
    )
    page.wait_for_timeout(150)
    probe = page.locator("#qa-cleaning-policy-probe")
    assert probe.is_visible()
    assert not probe.locator("p").is_visible()
    assert " · 필수" not in probe.inner_text()
    assert not probe.locator("small").is_visible()
    assert_page(page, f"synthetic-{role}")


report = {
    "browser": "Playwright Chromium fallback; Browser plugin unavailable",
    "widths": [],
    "maid_actual_surface": False,
    "admin_actual_surface": False,
    "maid_rerender_policy": False,
    "admin_rerender_policy": False,
}
with sync_playwright() as p:
    browser = p.chromium.launch()
    for width in (320, 360, 390, 420, 421, 768, 1440):
        page = browser.new_page(viewport={"width":width,"height":900})
        errors=[]
        page.on("console",lambda msg,errors=errors: errors.append(msg.text) if msg.type in ("error","warning") else None)
        page.on("pageerror",lambda exc,errors=errors: errors.append(str(exc)))
        page.goto(URL,wait_until="domcontentloaded")
        page.wait_for_timeout(200)
        assert_page(page,f"smoke-{width}")
        assert not errors,(width,errors)
        report["widths"].append(width)
        page.close()

    page = browser.new_page(viewport={"width":390,"height":1000})
    errors=[]
    page.on("console",lambda msg: errors.append(msg.text) if msg.type in ("error","warning") else None)
    page.on("pageerror",lambda exc: errors.append(str(exc)))
    page.goto(URL,wait_until="domcontentloaded")
    page.wait_for_timeout(200)
    report["maid_actual_surface"] = try_actual_surface(page,"maid")
    synthetic_rerender_probe(page,"maid")
    report["maid_rerender_policy"] = True
    page.screenshot(path=str(OUT/"maid-role-policy-390.png"),full_page=True)

    page.goto(URL,wait_until="domcontentloaded")
    page.wait_for_timeout(200)
    report["admin_actual_surface"] = try_actual_surface(page,"admin")
    synthetic_rerender_probe(page,"admin")
    report["admin_rerender_policy"] = True
    page.screenshot(path=str(OUT/"admin-role-policy-390.png"),full_page=True)
    assert not errors,errors

    page.set_viewport_size({"width":320,"height":900})
    assert_page(page,"final-320")
    page.screenshot(path=str(OUT/"cleaning-policy-320.png"),full_page=True)
    browser.close()

assert report["maid_rerender_policy"] and report["admin_rerender_policy"]
(OUT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
