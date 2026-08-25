from pathlib import Path

path = Path('.github/automation/apply-event-notification-center.py')
text = path.read_text(encoding='utf-8')
replacements = {
    'html = replace_between(html, "      function openAlerts() {", "      function openPublishConfirm() {", notification_ui + "      function openPublishConfirm() {", use_last=False)':
        'html = replace_between(html, "      function openAlerts() {", "      function openPublishConfirm() {", notification_ui, use_last=False)',
    'html = replace_between(html, "      function openActionAlerts(trigger=document.activeElement) {", "      function adminAuditSummary(detail) {", open_action_replacement + "      function adminAuditSummary(detail) {", use_last=False)':
        'html = replace_between(html, "      function openActionAlerts(trigger=document.activeElement) {", "      function adminAuditSummary(detail) {", open_action_replacement, use_last=False)',
    'html = replace_between(html, "      function renderMaidAlerts() {", "      function renderMaidPay() {", maid_alert_replacement + "      function renderMaidPay() {", use_last=False)':
        'html = replace_between(html, "      function renderMaidAlerts() {", "      function renderMaidPay() {", maid_alert_replacement, use_last=False)',
    'html = replace_between(html, final_topbar_start, "      function dateObject(value=state.selectedDate) {", final_topbar + "      function dateObject(value=state.selectedDate) {", use_last=True)':
        'html = replace_between(html, final_topbar_start, "      function dateObject(value=state.selectedDate) {", final_topbar, use_last=True)',
    "  'same 객실',": "  'NOTIFICATION_BUNDLE_WINDOW_MINUTES=10',",
    '이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다.':
        '이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다. 실제 백그라운드·모바일 푸시는 서비스 워커와 서버 발송 계층이 필요합니다.',
    'click_handler_marker = "      document.addEventListener(\'click\',e=>{"':
        'click_handler_marker = "      function openPublishConfirm() {"',
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f'patcher correction marker missing: {old[:100]}')
    text = text.replace(old, new, 1)

old_checker_line = 'checker = checker_path.read_text(encoding="utf-8").rstrip()'
new_checker_block = """checker = checker_path.read_text(encoding=\"utf-8\")
legacy_maid_start_marker = \"const maidAlertsStart = html.indexOf('function renderMaidAlerts');\"
legacy_maid_end_marker = \"const directAssignStart = html.indexOf('function openDirectAssign');\"
legacy_maid_start = checker.find(legacy_maid_start_marker)
legacy_maid_end = checker.find(legacy_maid_end_marker, legacy_maid_start)
if legacy_maid_start < 0 or legacy_maid_end < 0:
    raise SystemExit(\"legacy maid alert static-check block could not be isolated\")
new_maid_contract = r'''const maidAlertsStart = html.indexOf('function renderMaidAlerts');
const maidAlertsSource = html.slice(maidAlertsStart, html.indexOf('function renderMaidPay', maidAlertsStart));
for (const contract of [
  \"notificationAudienceKey('maid',signedInMaidId())\",
  'renderNotificationListMarkup({key',
  'notificationUnreadCount(key)',
  '배정·검수 결과·취소·마감·주급 업데이트를 시간순으로 확인합니다.',
]) {
  if (!maidAlertsSource.includes(contract)) throw new Error(`Maid event notification contract missing: ${contract}`);
}
'''
checker = checker[:legacy_maid_start] + new_maid_contract + checker[legacy_maid_end:]
checker = checker.rstrip()"""
if old_checker_line not in text:
    raise SystemExit('checker patch marker missing')
text = text.replace(old_checker_line, new_checker_block, 1)
path.write_text(text, encoding='utf-8')
