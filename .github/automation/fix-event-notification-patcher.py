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
path.write_text(text, encoding='utf-8')
