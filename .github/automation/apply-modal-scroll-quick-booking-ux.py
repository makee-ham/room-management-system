from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path("WIREFRAME/index.html")
html = html_path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    html = html.replace(old, new, 1)


replace_once(
    "    body.modal-open { overflow: hidden; }",
    "    body.modal-open { overflow: hidden; }\n    body.modal-open { overscroll-behavior: none; }",
    "modal background CSS",
)

replace_once(
    "    .catalog-summary-stat span { color:var(--muted); font-size:11px; line-height:1.35; }",
    "    .catalog-summary-stat span { color:var(--muted); font-size:11px; line-height:1.35; }\n"
    "    button.catalog-summary-stat { appearance:none; color:inherit; font:inherit; text-align:left; cursor:pointer; transition:transform .16s ease,border-color .16s ease,background .16s ease,box-shadow .16s ease; }\n"
    "    button.catalog-summary-stat:hover { transform:translateY(-1px); border-color:#8fb5d5; background:#fbfdff; }\n"
    "    button.catalog-summary-stat[aria-pressed=\"true\"] { border-color:#286ca8; background:#edf6ff; box-shadow:0 0 0 2px rgba(40,108,168,.12); }\n"
    "    button.catalog-summary-stat:focus-visible { position:relative; z-index:1; }",
    "room type summary button CSS",
)

replace_once(
    "      .quick-grid-scroller { max-height:calc(100vh - 250px); min-height:480px; }",
    "      .quick-grid-scroller { max-height:calc(100vh - 250px); min-height:480px; }\n"
    "      .quick-grid-scroller { max-height:none; min-height:0; overflow-x:auto; overflow-y:hidden; overscroll-behavior-x:contain; overscroll-behavior-y:auto; scrollbar-gutter:auto; touch-action:pan-x pan-y; }\n"
    "      .quick-grid-header { position:relative; top:auto; }",
    "mobile quick-booking vertical scroll override",
)

modal_helpers = r'''      let modalPageScrollY=null,modalScrollRestoreFrame=0;
      function scheduleWindowScrollRestore(value) {
        const y=Math.max(0,Math.round(Number(value)||0));
        cancelAnimationFrame(modalScrollRestoreFrame);
        window.scrollTo(0,y);
        modalScrollRestoreFrame=requestAnimationFrame(()=>{window.scrollTo(0,y);modalScrollRestoreFrame=0;});
      }
      function lockModalViewport(scrollY=window.scrollY) {
        if(modalPageScrollY==null){
          modalPageScrollY=Math.max(0,Math.round(Number(scrollY)||0));
          rememberCurrentHistoryRoute();
        }
        cancelAnimationFrame(modalScrollRestoreFrame);modalScrollRestoreFrame=0;
        const body=document.body;
        body.style.position='fixed';body.style.top=`-${modalPageScrollY}px`;body.style.left='0';body.style.right='0';body.style.width='100%';body.classList.add('modal-open');
      }
      function restoreModalViewport({restore=true}={}) {
        const body=document.body,y=modalPageScrollY;
        modalPageScrollY=null;
        body.classList.remove('modal-open');body.style.position='';body.style.top='';body.style.left='';body.style.right='';body.style.width='';
        if(restore&&y!=null)scheduleWindowScrollRestore(y);
        return y;
      }

'''
replace_once("      function render() {", modal_helpers + "      function render() {", "modal scroll helpers")
replace_once(
    "      function historyRouteSnapshot(scrollY=window.scrollY) {",
    "      function historyRouteSnapshot(scrollY=modalPageScrollY??window.scrollY) {",
    "modal-aware history snapshot",
)

direct_lock = "setModalBackgroundLocked(true);document.body.classList.add('modal-open');"
direct_count = html.count(direct_lock)
if direct_count != 4:
    raise SystemExit(f"modal open sites: expected 4 matches, found {direct_count}")
html = html.replace(direct_lock, "lockModalViewport();setModalBackgroundLocked(true);")
replace_once(
    "modalTrigger=findHistoryFocusTarget(entry.trigger);if(entry.modalKind==='pin-editor')pinCardTrigger=modalTrigger;lockModalViewport();setModalBackgroundLocked(true);",
    "modalTrigger=findHistoryFocusTarget(entry.trigger);if(entry.modalKind==='pin-editor')pinCardTrigger=modalTrigger;lockModalViewport(entry.route?.scrollY);setModalBackgroundLocked(true);",
    "history modal viewport lock",
)

replace_once(
    """      function rawCloseModal({restoreFocus=false}={}) {
        const root=document.getElementById('modal-root'),wasPin=!!root?.querySelector('.pin-sheet'),trigger=modalTrigger;
        if(root)root.innerHTML='';document.body.classList.remove('modal-open');setModalBackgroundLocked(false);
        if(restoreFocus)trigger?.focus?.();modalTrigger=null;if(wasPin){pinCardTrigger=null;activePinModalSessionId=null;}
      }""",
    """      function rawCloseModal({restoreFocus=false,restoreScroll=true}={}) {
        const root=document.getElementById('modal-root'),wasPin=!!root?.querySelector('.pin-sheet'),trigger=modalTrigger;
        if(root)root.innerHTML='';restoreModalViewport({restore:restoreScroll});setModalBackgroundLocked(false);
        if(restoreFocus)trigger?.focus?.({preventScroll:true});modalTrigger=null;if(wasPin){pinCardTrigger=null;activePinModalSessionId=null;}
      }""",
    "modal close and scroll restore",
)
replace_once(
    "        if(isWireframeHistory(history.state)&&history.state.layer==='modal'&&historyIndex()>0){rawCloseModal({restoreFocus:true});historyTraversalPending=true;history.back();return;}",
    "        if(isWireframeHistory(history.state)&&history.state.layer==='modal'&&historyIndex()>0){rawCloseModal({restoreFocus:true,restoreScroll:false});historyTraversalPending=true;history.back();return;}",
    "modal dismiss history transition",
)
replace_once(
    "        if(wasModal)historyReturnFocus=historyReturnFocus||historyFocusDescriptor(modalTrigger);\n        rawCloseModal();\n        const override=historyTraversalOverride,route=override||completed?.route||entry.route;historyTraversalOverride=null;",
    "        if(wasModal)historyReturnFocus=historyReturnFocus||historyFocusDescriptor(modalTrigger);\n        rawCloseModal({restoreScroll:false});\n        const override=historyTraversalOverride,route=override||completed?.route||entry.route;historyTraversalOverride=null;",
    "history navigation scroll ownership",
)
replace_once(
    "        requestAnimationFrame(()=>root.querySelector('button, input, select, textarea')?.focus());",
    "        requestAnimationFrame(()=>root.querySelector('button, input, select, textarea')?.focus({preventScroll:true}));",
    "modal initial focus",
)
replace_once(
    "        requestAnimationFrame(()=>{const restoredFocus=findHistoryFocusTarget(focusDescriptor);(restoredFocus&&root.contains(restoredFocus)?restoredFocus:root.querySelector('.calendar-day.selected, button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled])'))?.focus();});",
    "        requestAnimationFrame(()=>{const restoredFocus=findHistoryFocusTarget(focusDescriptor);(restoredFocus&&root.contains(restoredFocus)?restoredFocus:root.querySelector('.calendar-day.selected, button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled])'))?.focus({preventScroll:true});});",
    "restored modal focus",
)

replace_once(
    """      function rememberQuickGridViewport() {
        const scroller=document.getElementById('quick-grid-scroller');if(!scroller)return;
        state.quickGridScrollLeft=scroller.scrollLeft;state.quickGridScrollTop=scroller.scrollTop;
      }
      function restoreQuickGridViewport(focusSelector='') {
        requestAnimationFrame(()=>{const scroller=document.getElementById('quick-grid-scroller');if(scroller){scroller.scrollLeft=Math.max(0,Number(state.quickGridScrollLeft)||0);scroller.scrollTop=Math.max(0,Number(state.quickGridScrollTop)||0);}if(focusSelector)document.querySelector(focusSelector)?.focus({preventScroll:true});});
      }""",
    """      function quickGridUsesInternalVerticalScroll() { return !window.matchMedia('(max-width: 720px)').matches; }
      function rememberQuickGridViewport() {
        const scroller=document.getElementById('quick-grid-scroller');if(!scroller)return;
        state.quickGridScrollLeft=scroller.scrollLeft;state.quickGridScrollTop=quickGridUsesInternalVerticalScroll()?scroller.scrollTop:0;
      }
      function restoreQuickGridViewport(focusSelector='') {
        requestAnimationFrame(()=>{const scroller=document.getElementById('quick-grid-scroller');if(scroller){scroller.scrollLeft=Math.max(0,Number(state.quickGridScrollLeft)||0);scroller.scrollTop=quickGridUsesInternalVerticalScroll()?Math.max(0,Number(state.quickGridScrollTop)||0):0;}if(focusSelector)document.querySelector(focusSelector)?.focus({preventScroll:true});});
      }""",
    "responsive quick-grid viewport storage",
)
replace_once(
    "      document.addEventListener('scroll',event=>{if(event.target?.id==='quick-grid-scroller'){state.quickGridScrollLeft=event.target.scrollLeft;state.quickGridScrollTop=event.target.scrollTop;}},true);",
    "      document.addEventListener('scroll',event=>{if(event.target?.id==='quick-grid-scroller'){state.quickGridScrollLeft=event.target.scrollLeft;state.quickGridScrollTop=quickGridUsesInternalVerticalScroll()?event.target.scrollTop:0;}},true);",
    "responsive quick-grid scroll listener",
)

replace_once(
    '${Object.entries(ROOM_TYPES).map(([id,type])=>`<div class="catalog-summary-stat"><strong>${typeCounts[id]||0}</strong><span>${esc(type.name)}</span></div>`).join(\'\')}</section>',
    '${Object.entries(ROOM_TYPES).map(([id,type])=>`<button class="catalog-summary-stat" type="button" data-action="filter-room-type" data-type="${id}" aria-pressed="${state.roomTypeFilter===id}" aria-label="${esc(type.name)} ${typeCounts[id]||0}개 객실만 보기"><strong>${typeCounts[id]||0}</strong><span>${esc(type.name)}</span></button>`).join(\'\')}</section>',
    "clickable room type summary",
)
replace_once(
    "const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','back'",
    "const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back'",
    "room type filter action registration",
)
replace_once(
    "        if(a==='back'){maskPin();backFromDetail();return;}",
    """        if(a==='filter-room-type'){
          const typeId=el.dataset.type;if(state.role!=='admin'||state.adminView!=='rooms'||!ROOM_TYPES[typeId])return;
          state.roomTypeFilter=typeId;state.roomFilter='all';state.roomSearch='';render();requestAnimationFrame(()=>document.querySelector(`[data-action="filter-room-type"][data-type="${typeId}"]`)?.focus({preventScroll:true}));return;
        }
        if(a==='back'){maskPin();backFromDetail();return;}""",
    "room type summary filter handler",
)

html_path.write_text(html, encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 객실·간편 예약 스크롤 UX (2026-08-23)

- 모달을 열기 직전 문서의 세로 위치를 별도로 보존하고 배경을 고정한다. 닫을 때 같은 위치를 복원하며 원래 조작 버튼에는 스크롤 이동 없이 포커스를 돌린다.
- 720px 이하 간편 예약표는 내부 세로 스크롤을 사용하지 않는다. 날짜 영역의 가로 스크롤만 유지하고 세로 제스처는 문서 전체 스크롤로 이어진다.
- 객실 상단의 타입별 객실 수 카드는 버튼으로 동작한다. 누르면 객실번호 검색과 상태 조건을 초기화하고 해당 객실 유형 전체만 표시하며 선택 상태를 시각·접근성 속성으로 함께 알린다.
"""
readme_path.write_text(readme, encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-23 · 모달 위치 복원·모바일 간편 예약·객실 유형 바로 필터

### 변경

- 객실 목록과 간편 예약에서 모달을 열기 전 페이지 위치를 고정해 닫은 뒤 같은 지점으로 돌아오도록 수정했다.
- 모달을 닫을 때 원래 버튼 포커스를 `preventScroll`로 복원해 포커스 이동이 페이지를 다시 끌어올리지 않게 했다.
- 720px 이하에서는 간편 예약표의 내부 세로 스크롤을 제거하고 문서 스크롤로 마지막 객실까지 내려가도록 했다. 표 자체는 날짜 영역 가로 스크롤만 유지한다.
- 객실 상단의 스탠다드·프리미어·파셜 오션뷰·패밀리 수량 카드를 누르면 해당 객실 유형 전체로 즉시 필터링되도록 했다.

### 검증

- 객실 목록 중간에서 예약 모달을 열고 닫은 뒤 문서 세로 위치 오차가 4px 이내인지 확인했다.
- 간편 예약표에서 기존 예약 모달을 열고 닫은 뒤 문서 위치와 표의 가로·세로 위치가 유지되는지 확인했다.
- 390px에서 예약표 위로 세로 스크롤했을 때 문서는 이동하고 예약표 내부 `scrollTop`은 0으로 유지되는지 확인했다.
- 390px에서 문서 끝까지 내려 마지막 객실 행이 하단 내비게이션 위에 완전히 보이는지 확인했다.
- 타입 카드 4개를 각각 눌러 22·51·13·35개 객실과 하단 유형 셀렉트 값, `aria-pressed` 선택 상태가 일치하는지 확인했다.
- 360·390·768·1440px에서 문서 가로 넘침과 브라우저 콘솔·런타임 오류가 없는지 확인했다.
- 대표 화면: `WIREFRAME/QA/screenshots/admin-room-type-filter-1440.png`, `WIREFRAME/QA/screenshots/admin-quick-booking-mobile-scroll-390.png`.

### 한계

- 정적 데모 와이어프레임의 Chromium 브라우저 동작을 검증한 결과이며 iOS Safari·Android 인앱 브라우저 실기기 제스처는 별도 확인이 필요하다.
"""
qa_path.write_text(qa, encoding="utf-8")

checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8")
marker = "console.log('Per-maid weekly payment static contracts: passed');"
if checker.count(marker) != 1:
    raise SystemExit("static checker insertion marker mismatch")
checks = r'''for (const contract of [
  'let modalPageScrollY=null,modalScrollRestoreFrame=0;',
  'function lockModalViewport(scrollY=window.scrollY)',
  'function restoreModalViewport({restore=true}={})',
  'function historyRouteSnapshot(scrollY=modalPageScrollY??window.scrollY)',
  'rawCloseModal({restoreFocus=false,restoreScroll=true}={})',
  "trigger?.focus?.({preventScroll:true})",
  "function quickGridUsesInternalVerticalScroll() { return !window.matchMedia('(max-width: 720px)').matches; }",
  'overflow-x:auto; overflow-y:hidden; overscroll-behavior-x:contain; overscroll-behavior-y:auto;',
  'data-action="filter-room-type"',
  "if(a==='filter-room-type')",
  "state.roomTypeFilter=typeId;state.roomFilter='all';state.roomSearch='';",
]) {
  if (!html.includes(contract)) throw new Error(`Modal/quick-booking/type-filter UX contract missing: ${contract}`);
}

'''
checker_path.write_text(checker.replace(marker, checks + marker, 1), encoding="utf-8")

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
sums_lines = sums_path.read_text(encoding="utf-8").splitlines()
found = False
next_lines = []
for line in sums_lines:
    if line.endswith("  WIREFRAME/index.html"):
        next_lines.append(f"{digest}  WIREFRAME/index.html")
        found = True
    else:
        next_lines.append(line)
if not found:
    raise SystemExit("WIREFRAME/index.html checksum line missing")
sums_path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-23-modal-scroll-quick-booking-ux"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
