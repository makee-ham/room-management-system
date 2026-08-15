from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = PACKAGE_ROOT / 'CURRENT' / 'castle_the_art_room_manager_wireframe_v13.html'
OUT_DIR = Path(__file__).resolve().parent / 'runtime_screens'
OUT_DIR.mkdir(exist_ok=True)
html = HTML_PATH.read_text(encoding='utf-8')
results = []
errors = []




def launch_chromium(playwright):
    executable = (
        os.environ.get('CHROMIUM_PATH')
        or shutil.which('chromium')
        or shutil.which('chromium-browser')
        or shutil.which('google-chrome')
        or shutil.which('google-chrome-stable')
    )
    kwargs = {'headless': True, 'args': ['--no-sandbox']}
    if executable:
        kwargs['executable_path'] = executable
    return playwright.chromium.launch(**kwargs)

def check(name, ok, detail=''):
    results.append({'name': name, 'passed': bool(ok), 'detail': detail})
    if not ok:
        print('FAIL', name, detail)


def setup(page, role='admin', screen='admin-rooms'):
    page.goto('about:blank')
    page.set_content(html, wait_until='load')
    page.evaluate(f"state=defaultState();state.role='{role}';state.screen='{screen}';render();")
    page.wait_for_timeout(30)


def shot(page, name):
    page.screenshot(path=str(OUT_DIR / name), full_page=False)


with sync_playwright() as p:
    browser = launch_chromium(p)
    ctx = browser.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    page = ctx.new_page()
    page.on('console', lambda msg: errors.append(f'console:{msg.type}:{msg.text}') if msg.type == 'error' else None)
    page.on('pageerror', lambda exc: errors.append(f'pageerror:{exc}'))

    # 1. Version and dashboard semantics.
    setup(page)
    check('v13 제목', 'v13' in page.title(), page.title())
    app_text = page.locator('#app').inner_text()
    check('촛불 하드 차단 안내', '전량 회수 전 고객 배정·입실 불가' in app_text)
    check('촛불 객실이 고객 배정 불가 수에 포함', page.evaluate("state.rooms.filter(candleBlocksGuest).every(r => guestAllocationState(r) !== 'available')"))
    check('촛불 예약 객실 충돌 감지', page.evaluate("reservationConflict(state.rooms.find(r=>r.id==='1502'))"))
    shot(page, '01_admin_dashboard_candle_block.png')

    # 2. 608 canonical invariant: out of service, no reservation/task, candles also block.
    state608 = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='608');return {op:r.operationalStatus,stay:r.stayStatus,clean:r.cleaningStatus,res:r.reservationAssigned,task:r.task,assignee:r.assignee,open:r.openForClaim,assign:r.assignmentEnabled,candles:r.candleCount,guest:guestAllocationState(r)}})()")
    expected608 = {'op':'out-of-service','stay':'공실','clean':'작업 없음','res':False,'task':'작업 없음','assignee':'','open':False,'assign':False,'candles':3,'guest':'unavailable'}
    check('608 운영 중지 불변식', state608 == expected608, json.dumps(state608, ensure_ascii=False))
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='608';render();")
    detail608 = page.locator('#app').inner_text()
    check('608 촛불 회수 필요 표시', '촛불 3개 있음 · 고객 배정 불가' in detail608 and '회수 필요' in detail608)
    shot(page, '02_room_608_out_of_service_and_candles.png')

    # 3. Ready vacant room is available before candle placement.
    setup(page)
    check('412 초기 고객 배정 가능', page.evaluate("guestAllocationState(state.rooms.find(r=>r.id==='412'))") == 'available')

    # 4. Adding a candle requires reason + final confirmation and blocks allocation.
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='412';render();")
    page.locator('[data-action="open-candle-management"]').click()
    check('촛불 관리 시트', '1개 이상이면 고객 배정과 입실이 자동으로 잠기며' in page.locator('#sheet').inner_text())
    page.locator('#candleCountInput').fill('1')
    page.locator('#candleLocationsInput').fill('거실 창가 1')
    page.locator('[data-action="review-candle-change"]').click()
    check('촛불 사유 필수', page.locator('#sheetTitle').inner_text() == '412호 촛불 현황 관리')
    page.locator('#candleChangeReason').fill('냄새 제거를 위해 촛불 1개 배치')
    page.locator('[data-action="review-candle-change"]').click()
    confirm_text = page.locator('#sheet').inner_text()
    check('촛불 변경 최종 확인 모달', '촛불 수량을 변경할까요' in confirm_text and '고객 배정·입실 차단' in confirm_text)
    shot(page, '03_candle_add_confirmation.png')
    page.locator('[data-action="confirm-candle-change"]').click()
    candle_added = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='412');return {count:r.candleCount,state:guestAllocationState(r),reason:guestAllocationReason(r),event:r.dailyEvents[0].title}})()")
    check('촛불 추가 후 고객 배정 불가', candle_added['count'] == 1 and candle_added['state'] == 'unavailable', json.dumps(candle_added, ensure_ascii=False))
    check('촛불 변경 감사 이력', candle_added['event'] == '촛불 현황 변경', candle_added['event'])

    # 5. Physical recovery to zero requires a second confirmation and restores availability.
    page.locator('#app [data-action="open-candle-management"]').click()
    page.locator('#candleCountInput').fill('0')
    page.locator('#candleLocationsInput').fill('')
    page.locator('#candleChangeReason').fill('현장에서 촛불 1개 전량 회수 확인')
    page.locator('[data-action="review-candle-change"]').click()
    recover_text = page.locator('#sheet').inner_text()
    check('전량 회수 최종 확인 모달', '촛불 전량 회수를 확정할까요' in recover_text and '촛불 차단 해제' in recover_text)
    shot(page, '04_candle_recovery_confirmation.png')
    page.locator('[data-action="confirm-candle-change"]').click()
    recovered = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='412');return {count:r.candleCount,state:guestAllocationState(r),locations:r.candleLocations,event:r.dailyEvents[0].title}})()")
    check('전량 회수 후 고객 배정 가능', recovered == {'count':0,'state':'available','locations':'','event':'촛불 전량 회수 완료'}, json.dumps(recovered, ensure_ascii=False))

    # 6. Existing reservation becomes a conflict when a candle is recorded; check-in locks.
    setup(page)
    page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='802');r.candleCount=1;r.candleLocations='거실 1';render();})()")
    assigned_candle = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='802');return {state:guestAllocationState(r),conflict:reservationConflict(r),canCheckin:canProcessCheckin(r),reason:checkinBlockReason(r)}})()")
    check('예약 객실 촛불 충돌', assigned_candle['state']=='conflict' and assigned_candle['conflict'] and not assigned_candle['canCheckin'], json.dumps(assigned_candle, ensure_ascii=False))
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='802';render();")
    page.locator('[data-action="open-guest-allocation"]').first.click()
    conflict_text = page.locator('#sheet').inner_text()
    check('예약 충돌 화면에 촛불 회수 경로', '촛불 전량 회수 처리' in conflict_text and '입실 처리는 잠김' in conflict_text)
    shot(page, '05_reserved_room_candle_conflict.png')

    # 7. Recovering candle on assigned ready room unlocks check-in but keeps reservation assigned.
    page.locator('#sheet [data-action="open-candle-management"]').click()
    page.locator('#candleCountInput').fill('0')
    page.locator('#candleLocationsInput').fill('')
    page.locator('#candleChangeReason').fill('입실 전 촛불 1개 전량 회수 완료')
    page.locator('[data-action="review-candle-change"]').click()
    page.locator('[data-action="confirm-candle-change"]').click()
    assigned_recovered = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='802');return {state:guestAllocationState(r),conflict:reservationConflict(r),canCheckin:canProcessCheckin(r),count:r.candleCount}})()")
    check('예약 유지·입실 잠금 해제', assigned_recovered == {'state':'assigned','conflict':False,'canCheckin':True,'count':0}, json.dumps(assigned_recovered, ensure_ascii=False))

    # 8. Maid completion clearly communicates candle block; maid only records final count.
    setup(page, role='maid', screen='maid-task')
    page.evaluate("state.selectedRoomId='1004';state.taskChecks['1004']=[0,1,2,3,4,5];state.taskPhotos['1004']=[0,1,2,3,4,5,6,7];state.taskCandleCounts['1004']=2;render();")
    page.locator('[data-action="complete-task"]').click()
    complete_text = page.locator('#sheet').inner_text()
    check('메이드 완료 모달 촛불 차단 안내', '관리자 전량 회수 전 배정·입실 불가' in complete_text and '기존 촛불 감소·회수는 관리자 전용' in complete_text)
    shot(page, '06_maid_completion_candle_warning.png')
    page.locator('[data-action="confirm-complete-task"]').click()
    submitted = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='1004');return {clean:r.cleaningStatus,count:r.candleCount,conflict:reservationConflict(r)}})()")
    check('메이드 제출 후 촛불 차단 유지', submitted == {'clean':'검수 대기','count':2,'conflict':True}, json.dumps(submitted, ensure_ascii=False))

    # 8b. Maid cannot reduce an existing candle count; only an admin can record recovery.
    setup(page, role='maid', screen='maid-task')
    page.evaluate("state.selectedRoomId='1004';state.taskStarted['1004']=true;state.taskCandleCounts['1004']=1;render();")
    check('메이드 기존 촛불 감소 버튼 잠금', page.locator('[data-action=\"task-candle-minus\"]').is_disabled())
    page.evaluate("state.taskChecks['1004']=[0,1,2,3,4,5];state.taskPhotos['1004']=[0,1,2,3,4,5,6,7];state.taskCandleCounts['1004']=0;render();")
    page.locator('[data-action="complete-task"]').click()
    check('메이드 제출 모달이 기존 촛불 수량을 보존', '총 1개 · 이번 작업 +0' in page.locator('#sheet').inner_text())
    page.locator('[data-action="confirm-complete-task"]').click()
    check('메이드 조작으로 기존 촛불 0개 처리 불가', page.evaluate("state.rooms.find(r=>r.id==='1004').candleCount") == 1)

    # 9. Inspection approval does not override candle block.
    setup(page, role='admin', screen='admin-inspection-detail')
    page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='903');r.candleCount=1;r.candleLocations='욕실 선반 1';state.selectedRoomId='903';state.photoReviews['903']=state.inspectionPhotos['903'].map((_,i)=>i);render();})()")
    page.locator('[data-action="approve-inspection"]').click()
    approval_text = page.locator('#sheet').inner_text()
    check('검수 승인 모달 촛불 별도 차단', '1개 · 회수 필요' in approval_text and '회수 전 고객 배정 불가' in approval_text)
    shot(page, '07_inspection_approval_candle_block.png')
    page.locator('[data-action="confirm-approve-inspection"]').click()
    approved = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='903');return {clean:r.cleaningStatus,state:guestAllocationState(r),count:r.candleCount}})()")
    check('검수 승인 후에도 촛불 있으면 배정 불가', approved == {'clean':'입실 준비 완료','state':'unavailable','count':1}, json.dumps(approved, ensure_ascii=False))

    # 10. Candle rooms are a dedicated cross-filter and also in unavailable list.
    setup(page)
    page.locator('[data-room-filter="candle"]').first.click()
    visible_text = page.locator('#app').inner_text()
    check('촛불 전용 목록', '촛불이 있는 객실' in visible_text and '1502호' in visible_text and '608호' in visible_text)
    page.locator('[data-room-filter="guest-unavailable"]').first.click()
    unavailable_text = page.locator('#app').inner_text()
    check('배정 불가 목록에 촛불 회수 그룹', '촛불 회수 필요 · 다른 사유와 중복 표시' in unavailable_text)

    # 11. Historical dates are read-only for candle changes.
    setup(page)
    page.evaluate("switchSelectedDate('2026-08-13');state.screen='admin-room-detail';state.selectedRoomId='608';render();")
    check('과거 객실 촛불 관리 버튼 없음', page.locator('[data-action="open-candle-management"]').count() == 0)

    # 12. Existing critical safety flows still work.
    setup(page)
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='608';render();")
    page.locator('[data-action="open-room-operation"]').first.click()
    page.locator('#operationStatusInput').select_option('active')
    page.locator('#operationReasonInput').fill('냄새 원인 해결 및 환기 완료 확인')
    page.locator('[data-action="review-room-operation"]').click()
    check('운영 재개 확인 모달 유지', '정상 운영 재개할까요' in page.locator('#sheetTitle').inner_text())

    setup(page, role='maid', screen='maid-market')
    claim = page.locator('[data-action="claim-job"]')
    check('메이드 선택 가능 일감 존재', claim.count() > 0)
    claim.first.click()
    check('메이드 선택 취소 제한 확인', '직접 취소할 수 없습니다' in page.locator('#sheet').inner_text())

    setup(page, role='admin', screen='admin-settlement')
    page.locator('[data-action="toggle-weekly-payment"][data-id="maid02"]').click()
    check('주급 지급 취소 확인 모달 유지', '미지급으로 되돌릴까요' in page.locator('#sheet').inner_text())

    setup(page, role='admin', screen='admin-penalties')
    page.locator('[data-action="open-add-penalty"]').first.click()
    page.locator('#penaltyReason').fill('필수 인증사진 누락으로 검수 지연')
    page.locator('#penaltyEvidence').fill('903호 인증사진 제출 내역')
    page.locator('[data-action="review-add-penalty"]').click()
    check('벌점 부여 최종 확인 유지', '벌점을 부여할까요' in page.locator('#sheetTitle').inner_text())

    setup(page)
    page.locator('[data-action="open-calendar"]').click()
    check('달력 날짜 선택 유지', page.locator('[data-action="select-calendar-date"]').count() >= 28)
    shot(page, '08_calendar_date_picker.png')

    # 13. Responsive horizontal overflow.
    for width in (360,390,430):
        rctx = browser.new_context(viewport={'width':width,'height':844}, device_scale_factor=1, is_mobile=True, has_touch=True)
        rpage = rctx.new_page()
        rpage.set_content(html, wait_until='load')
        rpage.evaluate("state.role='admin';state.screen='admin-rooms';render();")
        overflow = rpage.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        check(f'모바일 {width}px 가로 넘침 없음', not overflow, f"scroll={rpage.evaluate('document.documentElement.scrollWidth')} client={width}")
        rctx.close()

    check('브라우저 콘솔 오류 없음', len(errors) == 0, '\n'.join(errors))
    browser.close()

report = {
    'html': str(HTML_PATH),
    'passed': sum(1 for r in results if r['passed']),
    'total': len(results),
    'all_passed': all(r['passed'] for r in results),
    'results': results,
    'errors': errors,
}
(Path(__file__).resolve().parent / 'runtime_qa_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
if not report['all_passed']:
    raise SystemExit(1)
