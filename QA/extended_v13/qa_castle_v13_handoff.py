from pathlib import Path
import json
import os
import shutil
from playwright.sync_api import sync_playwright

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = PACKAGE_ROOT / 'CURRENT' / 'castle_the_art_room_manager_wireframe_v13.html'
OUT_DIR = Path(__file__).resolve().parent / 'runtime_screens'
OUT_DIR.mkdir(parents=True, exist_ok=True)
html = HTML_PATH.read_text(encoding='utf-8')
results, errors = [], []



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
        print('FAIL:', name, detail)

def setup(page, role='admin', screen='admin-rooms'):
    page.goto('about:blank')
    page.set_content(html, wait_until='load')
    page.evaluate("([role,screen])=>{state=defaultState();state.role=role;state.screen=screen;render();}", [role, screen])
    page.wait_for_timeout(80)

def shot(page, name, full=False):
    page.screenshot(path=str(OUT_DIR / name), full_page=full)

with sync_playwright() as p:
    browser = launch_chromium(p)
    context = browser.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, is_mobile=True, has_touch=True)
    page = context.new_page()
    page.on('console', lambda m: errors.append(f'console:{m.type}:{m.text}') if m.type == 'error' else None)
    page.on('pageerror', lambda e: errors.append(f'pageerror:{e}'))

    # 608 invariant and admin dashboard.
    setup(page)
    s608 = page.evaluate("""(() => {const r=state.rooms.find(x=>x.id==='608'); return {
      operationalStatus:r.operationalStatus, stayStatus:r.stayStatus, cleaningStatus:r.cleaningStatus,
      reservationAssigned:!!r.reservationAssigned, checkin:r.checkin, task:r.task, assignee:r.assignee,
      openForClaim:r.openForClaim, assignmentEnabled:r.assignmentEnabled,
      cleaningSuppressed:r.cleaningSuppressed, guestState:guestAllocationState(r),
      reservationConflict:reservationConflict(r), needsCleaning:needsCleaning(r),
      claimEligible:canOpenForClaim(r), candleCount:r.candleCount, candleBlocked:candleBlocksGuest(r)
    };})()""")
    expected = {
      'operationalStatus':'out-of-service','stayStatus':'공실','cleaningStatus':'작업 없음',
      'reservationAssigned':False,'checkin':'예약 없음','task':'작업 없음','assignee':'',
      'openForClaim':False,'assignmentEnabled':False,'cleaningSuppressed':True,
      'guestState':'unavailable','reservationConflict':False,'needsCleaning':False,'claimEligible':False,
      'candleCount':3,'candleBlocked':True
    }
    check('608 운영 중지 불변식', s608 == expected, json.dumps(s608, ensure_ascii=False))
    shot(page, '01_admin_dashboard_608.png', full=True)

    # 608 guest assignment is blocked and has no accidental arrival controls.
    page.evaluate("openGuestAllocationSheet('608')")
    txt = page.locator('#sheet').inner_text()
    check('608 고객 배정 불가 안내', '현재 고객 배정 불가' in txt and '운영 중지' in txt, txt[:500])
    check('608 예약 저장 버튼 없음', page.locator('#sheet [data-action="save-guest-assignment"]').count() == 0)
    check('608 입실 버튼 없음', page.locator('#sheet [data-guest-action="checkin"]').count() == 0)
    shot(page, '02_608_guest_assignment_blocked.png')

    # Resuming 608 requires a review modal and creates an inspection-cleaning task, not saleable inventory.
    page.evaluate("closeSheet();state.screen='admin-room-detail';state.selectedRoomId='608';render();openRoomOperationSheet('608');")
    page.locator('#operationStatusInput').select_option('active')
    page.locator('#operationReasonInput').fill('냄새 원인 해결 및 환기 완료 확인')
    page.evaluate("reviewRoomOperation('608')")
    title = page.locator('#sheetTitle').inner_text()
    check('608 운영 재개 최종 확인 모달', '정상 운영 재개' in title)
    before = page.evaluate("state.rooms.find(r=>r.id==='608').operationalStatus")
    check('확정 전 운영 상태 유지', before == 'out-of-service', before)
    shot(page, '03_608_resume_operation_confirm.png')
    page.locator('[data-action="confirm-room-operation"]').click()
    resumed = page.evaluate("""(() => {const r=state.rooms.find(x=>x.id==='608'); return {
      op:r.operationalStatus, clean:r.cleaningStatus, task:r.task, assignee:r.assignee,
      open:r.openForClaim, assign:r.assignmentEnabled, guest:guestAllocationState(r)
    };})()""")
    check('운영 재개 후 점검청소·미배정·클로즈', resumed == {
      'op':'active','clean':'청소 가능','task':'운영 재개 점검 청소','assignee':'',
      'open':False,'assign':True,'guest':'unavailable'
    }, json.dumps(resumed, ensure_ascii=False))

    # A reserved room cannot be stopped without transfer/release.
    setup(page)
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='1502';render();openRoomOperationSheet('1502');")
    page.locator('#operationStatusInput').select_option('out-of-service')
    page.locator('#operationReasonInput').fill('긴급 시설 점검')
    page.evaluate("reviewRoomOperation('1502')")
    conflict = page.locator('#sheet').inner_text()
    check('예약 보유 객실 운영 중지 차단', '예약 충돌' in conflict and ('이동' in conflict or '해제' in conflict), conflict[:600])
    check('충돌 해결 전 운영 중지 확정 없음', page.locator('#sheet [data-action="confirm-room-operation"]').count() == 0)
    shot(page, '04_operation_stop_reservation_conflict.png')

    # Check-in guard: not-ready room is locked, ready room requires final confirmation.
    setup(page)
    page.evaluate("openGuestAllocationSheet('1502')")
    locked = page.locator('#sheet').inner_text()
    check('예약 객실 입실 차단 조건 잠금', '입실 처리' in locked and '잠김' in locked and ('청소' in locked or '촛불' in locked or '차단' in locked), locked[:550])
    shot(page, '05_checkin_locked_not_ready.png')
    page.evaluate("closeSheet();openGuestAllocationSheet('802')")
    check('입실 준비 완료 객실 입실 버튼', page.locator('#sheet [data-guest-action="checkin"]').count() == 1)
    page.locator('#sheet [data-guest-action="checkin"]').click()
    check('고객 입실 최종 확인 모달', '입실 처리할까요' in page.locator('#sheetTitle').inner_text())
    check('확정 전 고객 상태 유지', page.evaluate("state.rooms.find(r=>r.id==='802').stayStatus") == '오늘 입실')
    shot(page, '06_guest_checkin_confirm.png')

    # Maid-market visibility needs a confirmation before open/close.
    setup(page, screen='admin-open')
    initial = page.evaluate("state.rooms.find(r=>r.id==='1502').openForClaim")
    page.evaluate("openClaimVisibilityConfirm('1502')")
    vis = page.locator('#sheet').inner_text()
    check('개별 일감 공개 변경 확인 모달', ('오픈할까요' in vis or '클로즈할까요' in vis) and '메이드' in vis)
    check('확정 전 공개 상태 유지', page.evaluate("state.rooms.find(r=>r.id==='1502').openForClaim") == initial)
    shot(page, '07_job_visibility_confirm.png')
    page.locator('[data-action="confirm-claim-visibility"]').click()
    check('확정 후 공개 상태 변경', page.evaluate("state.rooms.find(r=>r.id==='1502').openForClaim") != initial)

    # Maid claim warns that only an admin can undo it.
    setup(page, role='maid', screen='maid-market')
    claim = page.locator('[data-action="claim-job"]')
    check('메이드 선택 가능 일감 존재', claim.count() > 0, str(claim.count()))
    if claim.count():
        room_id = claim.first.get_attribute('data-id')
        claim.first.click()
        claim_txt = page.locator('#sheet').inner_text()
        check('메이드 일감 선택 취소 제한 안내', '직접 취소할 수 없습니다' in claim_txt and '관리자' in claim_txt, claim_txt[:450])
        before_claim = page.evaluate("id=>state.rooms.find(r=>r.id===id).assignee", room_id)
        check('확정 전 담당자 미변경', before_claim == '')
        shot(page, '08_maid_claim_confirm.png')
        page.locator('[data-action="confirm-claim-job"]').click()
        claimed = page.evaluate("id=>{const r=state.rooms.find(x=>x.id===id);return [r.assignee,r.openForClaim]}", room_id)
        check('확정 후 메이드 담당·자동 클로즈', claimed == ['김하나',False], str(claimed))

    # Admin assignment can be changed or returned to unassigned.
    setup(page)
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='1004';render();openAssignmentSheet('1004');")
    # select the active maid whose name is 이소라; option values use maid IDs.
    page.locator('#assigneeSelect').select_option('maid03')
    page.locator('#assignmentReasonInput').fill('마감 임박으로 담당 교체')
    page.locator('[data-action="save-assignee"]').click()
    change_txt = page.locator('#sheet').inner_text()
    check('담당자 변경 최종 확인 모달', '담당' in change_txt and '변경' in change_txt and '이소라' in change_txt, change_txt[:550])
    check('확정 전 담당자 유지', page.evaluate("state.rooms.find(r=>r.id==='1004').assignee") == '박미정')
    shot(page, '09_assignee_change_confirm.png')
    page.locator('[data-action="confirm-save-assignee"]').click()
    check('확정 후 담당자 변경', page.evaluate("state.rooms.find(r=>r.id==='1004').assignee") == '이소라')
    page.evaluate("openAssignmentSheet('1004')")
    page.locator('#assignmentReasonInput').fill('현장 일정 변경')
    page.locator('#releaseMode').select_option('closed')
    page.locator('[data-action="release-assignee"]').click()
    release_txt = page.locator('#sheet').inner_text()
    check('담당자 미배정 회수 확인 모달', '미배정' in release_txt and ('회수' in release_txt or '돌릴까요' in release_txt), release_txt[:550])
    page.locator('[data-action="confirm-release-assignee"]').click()
    released = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='1004');return [r.assignee,r.openForClaim]})()")
    check('확정 후 미배정·선택 클로즈', released == ['',False], str(released))

    # Inspection reject is a two-stage action and sets an unread maid notification.
    setup(page, screen='admin-inspection-detail')
    page.evaluate("state.selectedRoomId='903';render();openInspectionRejectFinalConfirm('903',0,'청소 얼룩·먼지','욕실 바닥을 다시 닦고 같은 각도로 촬영')")
    reject_txt = page.locator('#sheet').inner_text()
    check('검수 반려 최종 확인 모달', '검수를 반려할까요' in reject_txt and '즉시 알림' in reject_txt)
    check('확정 전 검수대기 유지', page.evaluate("state.rooms.find(r=>r.id==='903').cleaningStatus") == '검수 대기')
    shot(page, '10_inspection_reject_confirm.png')
    page.locator('[data-action="confirm-submit-reject-inspection"]').click()
    rejected = page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='903');return [r.cleaningStatus,r.maidUnreadRejection,r.rejectionReason]})()")
    check('반려 후 재청소·미확인 알림', rejected[0]=='재청소 필요' and rejected[1] is True and '욕실 바닥' in rejected[2], str(rejected))
    page.evaluate("state.role='maid';state.screen='maid-tasks';render();")
    maid_text = page.locator('body').inner_text()
    check('메이드 화면 재청소 결과 노출', '903호' in maid_text and '재청소' in maid_text, maid_text[:700])

    # Task start is confirmed; completion already has its own confirmation.
    setup(page, role='maid', screen='maid-task')
    page.evaluate("""(() => {const r=state.rooms.find(x=>x.id==='1502');r.assignee='김하나';r.openForClaim=false;
      r.cleaningStatus='청소 가능';r.task='퇴실 청소';state.selectedRoomId='1502';render();openTaskStartConfirm('1502');})()""")
    start_txt = page.locator('#sheet').inner_text()
    check('청소 시작 확인 모달', '청소를 시작할까요' in start_txt and '시작 시각' in start_txt)
    check('확정 전 청소 가능 유지', page.evaluate("state.rooms.find(r=>r.id==='1502').cleaningStatus") == '청소 가능')
    shot(page, '11_task_start_confirm.png')
    page.locator('[data-action="confirm-start-task"]').click()
    check('확정 후 청소 중', page.evaluate("state.rooms.find(r=>r.id==='1502').cleaningStatus") == '청소 중')

    # Reversible weekly-payment state with reason.
    setup(page, screen='admin-settlement')
    paid_before = page.evaluate("state.maids.find(m=>m.id==='maid02').weeklyPaid")
    page.locator('[data-action="toggle-weekly-payment"][data-id="maid02"]').click()
    pay_txt = page.locator('#sheet').inner_text()
    check('주급 지급 완료 취소 확인', '미지급으로 되돌릴까요' in pay_txt and '사유' in pay_txt)
    check('확정 전 주급 지급액 유지', page.evaluate("state.maids.find(m=>m.id==='maid02').weeklyPaid") == paid_before)
    page.locator('#paymentReason').fill('송금 계좌 착오 확인')
    page.locator('[data-action="confirm-weekly-payment"]').click()
    check('확정 후 미지급 전환', page.evaluate("state.maids.find(m=>m.id==='maid02').weeklyPaid") == 0)

    # Soft-deleted maid restore is confirmed and returns inactive.
    setup(page, screen='admin-maid-detail')
    page.evaluate("state.selectedMaidId='maid05';render();openRestoreMaidConfirm('maid05')")
    restore_txt = page.locator('#sheet').inner_text()
    check('퇴사 취소 확인 모달', '퇴사 처리를 취소할까요' in restore_txt and '비활성' in restore_txt)
    check('확정 전 퇴사 유지', page.evaluate("state.maids.find(m=>m.id==='maid05').status") == 'retired')
    shot(page, '12_restore_retired_maid_confirm.png')
    page.locator('[data-action="confirm-restore-maid"]').click()
    check('복구 후 비활성', page.evaluate("state.maids.find(m=>m.id==='maid05').status") == 'inactive')

    # Calendar and historical correction confirmation.
    setup(page)
    page.locator('[data-action="open-calendar"]').click()
    check('달력 날짜 선택 UI', page.locator('[data-action="select-calendar-date"]').count() >= 28)
    shot(page, '13_calendar_picker.png')

    # v13: candles are a hard guest-assignment and check-in block until an admin records recovery to zero.
    setup(page)
    check('촛불 객실 고객 배정 차단', page.evaluate("state.rooms.filter(r=>r.candleCount>0).every(r=>guestAllocationState(r)!=='available')"))
    check('예약+촛불 충돌 감지', page.evaluate("reservationConflict(state.rooms.find(r=>r.id==='1502'))"))
    page.evaluate("state.screen='admin-room-detail';state.selectedRoomId='412';render();openCandleManagementSheet('412')")
    page.locator('#candleCountInput').fill('1')
    page.locator('#candleLocationsInput').fill('거실 창가 1')
    page.locator('#candleChangeReason').fill('냄새 제거를 위해 촛불 1개 배치')
    page.evaluate("reviewCandleChange('412')")
    check('촛불 배치 최종 확인', '고객 배정·입실 차단' in page.locator('#sheet').inner_text())
    page.locator('[data-action="confirm-candle-change"]').click()
    check('촛불 배치 후 즉시 배정 불가', page.evaluate("guestAllocationState(state.rooms.find(r=>r.id==='412'))") == 'unavailable')
    page.evaluate("openCandleManagementSheet('412')")
    page.locator('#candleCountInput').fill('0')
    page.locator('#candleLocationsInput').fill('')
    page.locator('#candleChangeReason').fill('현장에서 촛불 전량 회수 확인')
    page.evaluate("reviewCandleChange('412')")
    check('촛불 전량 회수 최종 확인', '전량 회수' in page.locator('#sheetTitle').inner_text())
    page.locator('[data-action="confirm-candle-change"]').click()
    check('촛불 0개 후 다른 조건 충족 시 배정 가능', page.evaluate("guestAllocationState(state.rooms.find(r=>r.id==='412'))") == 'available')

    setup(page, screen='admin-inspection-detail')
    page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='903');r.candleCount=1;r.candleLocations='욕실 선반 1';state.selectedRoomId='903';state.photoReviews['903']=state.inspectionPhotos['903'].map((_,i)=>i);render();})()")
    page.locator('[data-action="approve-inspection"]').click()
    check('검수 승인과 촛불 차단 분리', '회수 전 고객 배정 불가' in page.locator('#sheet').inner_text())
    page.locator('[data-action="confirm-approve-inspection"]').click()
    check('검수 승인 후 촛불 남으면 배정 불가', page.evaluate("(() => {const r=state.rooms.find(x=>x.id==='903');return r.cleaningStatus==='입실 준비 완료' && guestAllocationState(r)==='unavailable'})()"))

    setup(page)
    page.locator('[data-room-filter="guest-unavailable"]').first.click()
    check('배정 불가 목록 촛불 회수 그룹', '촛불 회수 필요 · 다른 사유와 중복 표시' in page.locator('#app').inner_text())

    # Maid can add candle counts but cannot reduce an existing positive count; admin recovery is required.
    setup(page, role='maid', screen='maid-task')
    page.evaluate("state.selectedRoomId='1004';state.taskStarted['1004']=true;state.taskCandleCounts['1004']=1;render();")
    check('메이드 기존 촛불 감소 버튼 비활성', page.locator('[data-action=\"task-candle-minus\"]').is_disabled())
    page.evaluate("state.taskChecks['1004']=[0,1,2,3,4,5];state.taskPhotos['1004']=[0,1,2,3,4,5,6,7];state.taskCandleCounts['1004']=0;render();")
    page.locator('[data-action="complete-task"]').click()
    check('메이드 제출 시 기존 촛불 하한 보존', '총 1개 · 이번 작업 +0' in page.locator('#sheet').inner_text())
    page.locator('[data-action="confirm-complete-task"]').click()
    check('메이드가 기존 촛불을 0개로 해제하지 못함', page.evaluate("state.rooms.find(r=>r.id==='1004').candleCount") == 1)

    # Ensure critical confirmations are represented in the implementation.
    critical_actions = [
      'confirm-room-operation','confirm-reservation-transfer','confirm-save-guest-assignment',
      'execute-guest-action','confirm-save-password','confirm-toggle-assignment-enabled',
      'confirm-save-assignee','confirm-release-assignee','confirm-claim-visibility',
      'confirm-batch-claim-visibility','confirm-claim-job','confirm-start-task',
      'confirm-complete-task','confirm-approve-inspection','confirm-submit-reject-inspection',
      'confirm-weekly-payment','confirm-add-penalty','confirm-delete-penalty',
      'confirm-restore-penalty','confirm-toggle-maid-status','confirm-retire-maid',
      'confirm-restore-maid','confirm-save-maid','confirm-history-correction',
      'confirm-stay-time','confirm-save-entry-issue','confirm-resolve-entry-issue',
      'open-candle-management','review-candle-change','confirm-candle-change'
    ]
    missing = [a for a in critical_actions if a not in html]
    check('중요 변경 확인 액션 구현', not missing, ', '.join(missing))

    # Responsive checks for primary screens.
    for width in (360,390,430):
        rctx = browser.new_context(viewport={'width':width,'height':844}, device_scale_factor=1, is_mobile=True, has_touch=True)
        rpage = rctx.new_page()
        rerr=[]
        rpage.on('pageerror', lambda e: rerr.append(str(e)))
        rpage.set_content(html, wait_until='load')
        rpage.evaluate("state=defaultState();state.role='admin';state.screen='admin-rooms';render();")
        overflow = rpage.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        check(f'{width}px 가로 넘침 없음', not overflow, f"scroll={rpage.evaluate('document.documentElement.scrollWidth')}")
        check(f'{width}px 페이지 오류 없음', not rerr, '\n'.join(rerr))
        rctx.close()

    check('브라우저 오류 없음', not errors, '\n'.join(errors))
    browser.close()

report = {
    'html': str(HTML_PATH),
    'screenshots': str(OUT_DIR),
    'passed': sum(1 for r in results if r['passed']),
    'total': len(results),
    'all_passed': all(r['passed'] for r in results),
    'results': results,
    'errors': errors,
}
report_path = Path(__file__).resolve().parent / 'runtime_qa_report.json'
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
if not report['all_passed']:
    raise SystemExit(1)
