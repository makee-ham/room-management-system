from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path('/mnt/data/castle_the_art_room_manager_wireframe_v13.html').read_text(encoding='utf-8')
OUT = Path('/mnt/data/castle_the_art_v13_handoff_screens')
OUT.mkdir(exist_ok=True)


def setup(page, role='admin', screen='admin-rooms'):
    page.goto('about:blank')
    page.set_content(HTML, wait_until='load')
    page.evaluate("([role,screen])=>{state=defaultState();state.role=role;state.screen=screen;render();}", [role,screen])
    page.wait_for_timeout(80)


def shot(page, name):
    page.evaluate("toast.classList.remove('show')")
    page.screenshot(path=str(OUT/name), full_page=False)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    ctx=browser.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    page=ctx.new_page()

    setup(page)
    shot(page,'01_admin_dashboard.png')

    setup(page)
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='608';render();")
    shot(page,'02_room_608.png')

    setup(page)
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='412';render();openCandleManagementSheet('412')")
    page.locator('#candleCountInput').fill('1')
    page.locator('#candleLocationsInput').fill('거실 창가 1')
    page.locator('#candleChangeReason').fill('냄새 제거를 위해 촛불 1개 배치')
    page.evaluate("reviewCandleChange('412')")
    shot(page,'03_candle_add_confirm.png')

    setup(page)
    page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='412');r.candleCount=1;r.candleLocations='거실 창가 1';state.screen='admin-room-detail';state.selectedRoomId='412';render();openCandleManagementSheet('412');})()")
    page.locator('#candleCountInput').fill('0')
    page.locator('#candleLocationsInput').fill('')
    page.locator('#candleChangeReason').fill('현장에서 촛불 1개 전량 회수 확인')
    page.evaluate("reviewCandleChange('412')")
    shot(page,'04_candle_recovery_confirm.png')

    setup(page)
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='1502';render();openGuestAllocationSheet('1502')")
    shot(page,'05_reserved_candle_conflict.png')

    setup(page, 'maid','maid-task')
    page.evaluate("state.selectedRoomId='1004';state.taskStarted['1004']=true;state.taskCandleCounts['1004']=1;render();")
    shot(page,'06_maid_candle_floor.png')

    setup(page, 'maid','maid-task')
    page.evaluate("state.selectedRoomId='1004';state.taskStarted['1004']=true;state.taskChecks['1004']=[0,1,2,3,4,5];state.taskPhotos['1004']=[0,1,2,3,4,5,6,7];state.taskCandleCounts['1004']=2;render();openTaskCompleteConfirm('1004')")
    shot(page,'07_maid_completion_confirm.png')

    setup(page, 'admin','admin-inspection-detail')
    page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='903');r.candleCount=1;r.candleLocations='욕실 선반 1';state.selectedRoomId='903';state.photoReviews['903']=state.inspectionPhotos['903'].map((_,i)=>i);render();openInspectionApprovalConfirm('903');})()")
    shot(page,'08_inspection_candle_block.png')

    setup(page)
    page.locator('[data-room-filter="guest-unavailable"]').first.click()
    page.locator('#app').evaluate("el=>el.scrollTop=615")
    page.wait_for_timeout(100)
    shot(page,'09_unavailable_candle_group.png')

    setup(page)
    page.evaluate("openCalendarSheet()")
    shot(page,'10_calendar.png')

    ctx.close(); browser.close()
print(OUT)
