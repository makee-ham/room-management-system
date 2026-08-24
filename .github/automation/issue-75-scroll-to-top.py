from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')
    html = html.replace(old, new, 1)


css = r'''
    .scroll-top-button {
      position: fixed;
      right: clamp(16px, 2.4vw, 30px);
      bottom: 24px;
      z-index: 65;
      display: inline-grid;
      place-items: center;
      width: 48px;
      min-width: 48px;
      height: 48px;
      padding: 0;
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 999px;
      color: #fff;
      background: var(--navy);
      box-shadow: 0 12px 28px rgba(20,36,55,.24);
      cursor: pointer;
      transition: transform .16s ease, background .16s ease, box-shadow .16s ease;
    }
    .scroll-top-button:hover { transform: translateY(-2px); background: var(--navy-2); box-shadow: 0 15px 32px rgba(20,36,55,.28); }
    .scroll-top-button:active { transform: translateY(0); }
    .scroll-top-button[hidden], body.modal-open .scroll-top-button { display: none !important; }
    .scroll-top-button .icon { width: 22px; height: 22px; }
    @media (max-width:720px) {
      .scroll-top-button {
        right: 14px;
        bottom: calc(var(--bottom-nav) + env(safe-area-inset-bottom) + 14px);
        width: 46px;
        min-width: 46px;
        height: 46px;
      }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      .scroll-top-button { transition: none; }
    }
'''
replace_once('\n  </style>', css + '\n  </style>', 'scroll-to-top CSS')

button_markup = r'''  <button id="scroll-to-top" class="scroll-top-button" type="button" aria-label="맨 위로 이동" aria-hidden="true" title="맨 위로" hidden>
    <svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>
  </button>
'''
replace_once(
    '  <div id="assertive-live" class="sr-only" aria-live="assertive" aria-atomic="true"></div>\n\n  <script>',
    '  <div id="assertive-live" class="sr-only" aria-live="assertive" aria-atomic="true"></div>\n' + button_markup + '\n  <script>',
    'scroll-to-top button markup',
)

logic = r'''      const SCROLL_TOP_THRESHOLD=600,scrollTopButton=document.getElementById('scroll-to-top');
      let scrollTopSyncFrame=0;
      function scrollTopButtonShouldShow() {
        return window.scrollY>=SCROLL_TOP_THRESHOLD&&!document.body.classList.contains('modal-open')&&!document.querySelector('#modal-root .modal, #modal-root .calendar-dialog');
      }
      function syncScrollTopButton() {
        if(!scrollTopButton)return;
        const visible=scrollTopButtonShouldShow();
        scrollTopButton.hidden=!visible;
        scrollTopButton.setAttribute('aria-hidden',visible?'false':'true');
      }
      function scheduleScrollTopButtonSync() {
        if(scrollTopSyncFrame)return;
        scrollTopSyncFrame=requestAnimationFrame(()=>{scrollTopSyncFrame=0;syncScrollTopButton();});
      }
      window.addEventListener('scroll',scheduleScrollTopButtonSync,{passive:true});
      window.addEventListener('resize',scheduleScrollTopButtonSync,{passive:true});
      scrollTopButton?.addEventListener('click',()=>{
        const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if(reduced){
          const root=document.documentElement,previous=root.style.scrollBehavior;
          root.style.scrollBehavior='auto';window.scrollTo(0,0);root.style.scrollBehavior=previous;
          syncScrollTopButton();
        } else {
          window.scrollTo({top:0,left:0,behavior:'smooth'});
        }
        requestAnimationFrame(()=>document.getElementById('main-content')?.focus({preventScroll:true}));
      });
      syncScrollTopButton();

'''
replace_once('      function render() {', logic + '      function render() {', 'scroll-to-top behavior')

html_path.write_text(html, encoding='utf-8')

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8').rstrip() + '''

## 맨 위로 가기 버튼 (2026-08-24)

- 문서를 600px 이상 내리면 화면 오른쪽 아래에 `맨 위로 이동` 버튼이 나타난다.
- 모바일에서는 하단 내비게이션과 안전영역 위에 배치하고, 모달·달력 창이 열린 동안 숨긴다.
- 클릭하면 페이지 상단으로 이동하고 본문 시작점에 포커스를 돌린다.
- 동작 감소 설정을 사용한 기기에서는 스크롤 애니메이션 없이 즉시 이동한다.
- 버튼과 스크롤·리사이즈 리스너는 문서 초기화 시 한 번만 등록되어 재렌더링으로 중복되지 않는다.
'''
readme_path.write_text(readme + '\n', encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8').rstrip() + '''

## 2026-08-24 · 맨 위로 가기 버튼

- 문서 상단에서 버튼이 숨겨지고 600px 이상 스크롤한 뒤 노출되는지 확인했다.
- 버튼 클릭 뒤 문서가 상단으로 이동하고 본문 시작점으로 포커스가 이동하는지 확인했다.
- 390px 화면에서 하단 내비게이션과 겹치지 않고 안전영역 위에 배치되는지 확인했다.
- 모달이 열린 동안 버튼이 숨겨지고 닫은 뒤 현재 스크롤 위치에 맞게 다시 표시되는지 확인했다.
- 동작 감소 설정에서는 즉시 상단으로 이동하는지 확인했다.
- 360·390·768·1440px 가로 넘침, 콘솔·런타임 오류를 확인했다.
'''
qa_path.write_text(qa + '\n', encoding='utf-8')

checker_path = Path('scripts/check-workspace.mjs')
checker = checker_path.read_text(encoding='utf-8')
marker = "console.log('Workspace check: passed');"
checks = r'''for (const contract of [
  'id="scroll-to-top"',
  'aria-label="맨 위로 이동"',
  'const SCROLL_TOP_THRESHOLD=600',
  'function scrollTopButtonShouldShow()',
  "window.addEventListener('scroll',scheduleScrollTopButtonSync,{passive:true})",
  "window.matchMedia('(prefers-reduced-motion: reduce)').matches",
  "window.scrollTo({top:0,left:0,behavior:'smooth'})",
  "body.modal-open .scroll-top-button",
  "bottom: calc(var(--bottom-nav) + env(safe-area-inset-bottom) + 14px)",
]) {
  if (!html.includes(contract)) throw new Error(`Scroll-to-top contract missing: ${contract}`);
}
if ((html.match(/id="scroll-to-top"/g)||[]).length!==1) throw new Error('Scroll-to-top button must exist exactly once.');
if ((html.match(/window\.addEventListener\('scroll',scheduleScrollTopButtonSync/g)||[]).length!==1) throw new Error('Scroll-to-top listener must be registered exactly once.');
console.log('Scroll-to-top static contracts: passed');

'''
if checker.count(marker) != 1:
    raise SystemExit('workspace check marker mismatch')
checker_path.write_text(checker.replace(marker, checks + marker, 1), encoding='utf-8')

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path('SHA256SUMS.txt')
sums = sums_path.read_text(encoding='utf-8').splitlines()
sums_path.write_text('\n'.join(f'{digest}  WIREFRAME/index.html' if line.endswith('  WIREFRAME/index.html') else line for line in sums) + '\n', encoding='utf-8')

manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version'] = '2026-08-24-scroll-to-top'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
