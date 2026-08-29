from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
INDEX = ROOT / "WIREFRAME/index.html"
SHA_FILE = ROOT / "SHA256SUMS.txt"
MANIFEST = ROOT / "manifest.json"
DOCS = [
    ROOT / "WIREFRAME/README.md",
    ROOT / "WIREFRAME/QA.md",
    ROOT / "DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md",
    ROOT / "DOCS/19_TEMPLATE_PARITY_AUDIT.md",
]

PATTERN = re.compile(
    r"\{id:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
    r"zone:(?:'([^']+)'|\"([^\"]+)\")[^\n{}]*"
    r"label:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
    r"description:(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\")[^\n{}]*"
    r"required:(true|false)[^\n{}]*\}"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")


def records(source: str):
    rows=[]
    for m in PATTERN.finditer(source):
        rows.append({
            "id":m.group(1) or m.group(2) or "",
            "zone":m.group(3) or m.group(4) or "",
            "label":(m.group(5) or m.group(6) or "").replace("\\'", "'").replace('\\"','"'),
            "description":(m.group(7) or m.group(8) or "").replace("\\'", "'").replace('\\"','"'),
            "required":m.group(9)=="true",
            "source":m.group(0),
        })
    return rows


def validate(source: str):
    rows=records(source)
    assert len(rows)>=20, len(rows)
    assert not any(row["id"]=="entry-number" for row in rows)
    assert all(row["required"] for row in rows if row["zone"]!="기타")
    others=[row for row in rows if row["zone"]=="기타"]
    assert others
    assert all((not row["required"] and "maxPhotos:10" in row["source"]) for row in others)
    assert "cleaning-photo-presentation-policy" in source
    return rows


def apply():
    html=read(INDEX)
    old_hash=hashlib.sha256(html.encode()).hexdigest()
    html=re.sub(r'\n?<script id="cleaning-photo-presentation-policy">.*?</script>\n?', '\n', html, flags=re.S)
    for pattern in (
        re.compile(r"(?m)^[ \t]*\{id:'entry-number'[^\n]*\},\r?\n"),
        re.compile(r'(?m)^[ \t]*\{id:"entry-number"[^\n]*\},\r?\n'),
        re.compile(r"(?m)^[ \t]*\{[^\n]*(?:slotId|requirementId|photoId):'entry-number'[^\n]*\},?\r?\n"),
        re.compile(r'(?m)^[ \t]*\{[^\n]*(?:slotId|requirementId|photoId):"entry-number"[^\n]*\},?\r?\n'),
    ):
        html=pattern.sub('',html)
    html=re.sub(r"(?<![\w-])['\"]entry-number['\"]\s*,\s*",'',html)
    html=html.replace('객실번호·현관','').replace('객실 번호·현관','')
    output=[]
    for line in html.splitlines(keepends=True):
        if all(token in line for token in ('{id:','zone:','label:','description:','required:')) and 'required:false' in line:
            if "zone:'기타'" not in line and 'zone:"기타"' not in line:
                line=line.replace('required:false','required:true')
        output.append(line)
    html=''.join(output)
    html=re.sub(r"(checkout\s*:\s*\{\s*name\s*:\s*'퇴실 청소'\s*,\s*version\s*:\s*)'v7'",r"\g<1>'v8'",html,count=1)
    rows=records(html)
    assert len(rows)>=20
    assert not any(row['id']=='entry-number' for row in rows)
    assert all(row['required'] for row in rows if row['zone']!='기타')
    assert all((not row['required'] and 'maxPhotos:10' in row['source']) for row in rows if row['zone']=='기타')
    labels=sorted({row['label'] for row in rows if row['label']})
    descriptions=sorted({row['description'] for row in rows if row['description']})
    script=f'''\n<script id="cleaning-photo-presentation-policy">\n(() => {{\n const descriptions=new Set({json.dumps(descriptions,ensure_ascii=False)});\n const labels={json.dumps(labels,ensure_ascii=False)};\n let queued=false;\n const context=node=>{{let el=node instanceof Element?node:node?.parentElement;for(let d=0;el&&d<6;d+=1,el=el.parentElement){{const t=el.textContent||'';if(labels.some(label=>t.includes(label)))return true;}}return false;}};\n const clean=()=>{{queued=false;const root=document.body;if(!root)return;root.querySelectorAll('p,small,span,div').forEach(el=>{{if(el.children.length)return;const t=(el.textContent||'').trim();if(descriptions.has(t)||((t==='필수'||t==='선택')&&context(el))){{el.hidden=true;el.setAttribute('aria-hidden','true');}}}});const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);nodes.forEach(node=>{{if(!context(node))return;const next=(node.nodeValue||'').replace(/\\s*·\\s*(필수|선택)\\b/g,'');if(next!==node.nodeValue)node.nodeValue=next;}});}};\n const schedule=()=>{{if(queued)return;queued=true;queueMicrotask(clean);}};\n const start=()=>{{new MutationObserver(schedule).observe(document.body,{{childList:true,subtree:true,characterData:true}});clean();}};\n if(document.body)start();else document.addEventListener('DOMContentLoaded',start,{{once:true}});\n}})();\n</script>\n'''
    pos=html.rfind('</body>')
    assert pos>=0
    html=html[:pos]+script+html[pos:]
    validate(html)
    write(INDEX,html)
    new_hash=hashlib.sha256(html.encode()).hexdigest()
    section='''## 2026-08-29 청소 인증 사진 단순화\n\n- 업무 정보에 객실 호수가 이미 표시되므로 `객실번호·현관` 촬영 슬롯을 사용하지 않는다.\n- `기타`를 제외한 모든 사진 슬롯은 최소 1장을 등록해야 완료·제출할 수 있다.\n- `기타`만 선택 항목이며 최대 10장을 개별 등록·삭제·확대할 수 있다.\n- 관리자와 메이드 화면에는 회색 설명 문장과 `필수`·`선택` 표기를 노출하지 않는다.\n- 설명·필수 여부·최대 사진 수는 제출 스냅샷의 검증 메타데이터로 보존한다.\n- 새 퇴실 청소 템플릿은 `v8`이며 기존 제출은 당시 스냅샷을 유지한다.\n'''
    for path in DOCS:
        text=read(path)
        text=text.replace('새 퇴실 청소 `v7`','새 퇴실 청소 `v8`').replace('현재 퇴실 청소 v7','현재 퇴실 청소 v8')
        if '## 2026-08-29 청소 인증 사진 단순화' not in text:
            text=text.rstrip()+'\n\n'+section
        write(path,text)
    sha=read(SHA_FILE)
    sha=re.sub(r'^[0-9a-f]{64}\s+WIREFRAME/index\.html$',f'{new_hash}  WIREFRAME/index.html',sha,flags=re.M)
    write(SHA_FILE,sha)
    manifest=json.loads(read(MANIFEST)); size=INDEX.stat().st_size
    def refresh(value):
        if isinstance(value,dict):
            identifies=any(value.get(k)=='WIREFRAME/index.html' for k in ('path','file','filename','name'))
            for key,item in list(value.items()):
                low=key.lower()
                if identifies and low in {'sha256','hash','checksum','digest'} and isinstance(item,str): value[key]=new_hash
                elif identifies and low in {'size','bytes','size_bytes'} and isinstance(item,int): value[key]=size
                else: value[key]=refresh(item)
            return value
        if isinstance(value,list): return [refresh(item) for item in value]
        if isinstance(value,str) and value==old_hash: return new_hash
        return value
    write(MANIFEST,json.dumps(refresh(manifest),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'rows':len(rows),'other':sum(r['zone']=='기타' for r in rows),'sha':new_hash},ensure_ascii=False))


def qa():
    from playwright.sync_api import sync_playwright
    html=read(INDEX); rows=validate(html)
    labels=sorted({row['label'] for row in rows if row['label']}); descriptions=sorted({row['description'] for row in rows if row['description']})
    url='http://127.0.0.1:4173/index.html'; widths=(320,360,390,420,421,768,1440)
    out=Path('/tmp/cleaning-template-main-guard'); out.mkdir(parents=True,exist_ok=True)
    def role_index(page):
        for i in range(page.locator('select').count()):
            vals=page.locator('select').nth(i).locator('option').evaluate_all('els=>els.map(e=>e.value)')
            if 'admin' in vals and 'maid' in vals:return i
        raise AssertionError('role selector missing')
    def assert_page(page,label):
        page.wait_for_timeout(100)
        data=page.evaluate("() => ({w:innerWidth,d:document.documentElement.scrollWidth,b:document.body.scrollWidth,t:document.title,x:document.body.innerText})")
        assert 'CASTLE THE ART' in data['t']; assert data['d']<=data['w']+1 and data['b']<=data['w']+1,(label,data); assert '객실번호·현관' not in data['x']
        failures=page.evaluate("""([labels,descriptions])=>{const v=e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return !e.hidden&&s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0};const c=e=>{let n=e;for(let d=0;n&&d<6;d++,n=n.parentElement){const t=n.textContent||'';if(labels.some(l=>t.includes(l)))return true}return false};const a=[...document.querySelectorAll('body *')].filter(e=>e.children.length===0&&v(e)).map(e=>({e,t:(e.textContent||'').trim()})).filter(x=>x.t);return {desc:a.filter(x=>descriptions.includes(x.t)).map(x=>x.t),mark:a.filter(x=>(x.t==='필수'||x.t==='선택'||/\\s·\\s(?:필수|선택)\\b/.test(x.t))&&c(x.e)).map(x=>x.t)}}""",[labels,descriptions])
        assert not failures['desc'],(label,failures); assert not failures['mark'],(label,failures)
    with sync_playwright() as p:
        browser=p.chromium.launch()
        for width in widths:
            page=browser.new_page(viewport={'width':width,'height':900}); errors=[]
            page.on('console',lambda msg,errors=errors: errors.append(msg.text) if msg.type in ('error','warning') else None); page.on('pageerror',lambda exc,errors=errors: errors.append(str(exc)))
            page.goto(url,wait_until='domcontentloaded'); page.wait_for_timeout(180); assert_page(page,f'smoke-{width}'); assert not errors,(width,errors); page.close()
        page=browser.new_page(viewport={'width':390,'height':900})
        for role in ('maid','admin'):
            page.goto(url,wait_until='domcontentloaded'); page.wait_for_timeout(150); page.locator('select').nth(role_index(page)).select_option(role); page.wait_for_timeout(120)
            label=labels[0]; desc=descriptions[0]
            page.evaluate("""([role,label,desc])=>{const s=document.createElement('section');s.id='policy-probe';s.dataset.role=role;s.style.cssText='padding:16px;background:white';s.innerHTML=`<strong>${label}</strong><p>${desc}</p><span>${label} · 필수</span><small>선택</small>`;document.body.append(s)}""",[role,label,desc]); page.wait_for_timeout(150)
            probe=page.locator('#policy-probe'); assert probe.is_visible(); assert not probe.locator('p').is_visible(); assert ' · 필수' not in probe.inner_text(); assert not probe.locator('small').is_visible(); assert_page(page,role); page.screenshot(path=str(out/f'{role}-390.png'),full_page=True)
        browser.close()
    (out/'report.json').write_text(json.dumps({'widths':widths,'roles':['maid','admin'],'browser':'Playwright Chromium fallback'},ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'apply'
    if mode=='apply':apply()
    elif mode=='qa':qa()
    else:raise SystemExit(f'unknown mode: {mode}')
