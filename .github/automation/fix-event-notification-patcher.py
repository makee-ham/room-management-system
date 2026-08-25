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

old_action_insertion = """html = html.replace(action_marker, notification_actions, 1)

# Add target dispatcher immediately before the delegated click handler.
"""
new_action_insertion = """html = html.replace(action_marker, notification_actions, 1)

# The rebuilt delegated click handler ignores actions that are not in this allow-list.
# Register the new notification controls in the same active router whose branches were patched above.
rebuilt_actions_marker = \"deprecatedStateActions.forEach(action=>rebuiltActions.add(action));\"
if rebuilt_actions_marker not in html:
    raise SystemExit(\"rebuilt action allow-list marker not found\")
html = html.replace(
    rebuilt_actions_marker,
    rebuilt_actions_marker + \"\\n      ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));\",
    1,
)

# Add target dispatcher immediately before the delegated click handler.
"""
if old_action_insertion not in text:
    raise SystemExit('notification action insertion marker missing')
text = text.replace(old_action_insertion, new_action_insertion, 1)

old_dispatch = """      function dispatchNotificationTarget(event){
        const target=event?.target||{},action=target.action||'alerts',button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.click();button.remove();
      }
"""
new_dispatch = """      function dispatchNotificationTarget(event){
        const target=event?.target||{},action=target.action||'alerts';
        if(action==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
        if(action==='go-cleaning-assignment'){const day=target.data?.day==='tomorrow'?'tomorrow':'today';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
        if(action==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
        if(action==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
        if(action==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
        if(action==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
        const button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));button.remove();
      }
      function closeNotificationModalAndNavigate(notificationEvent){
        const navigate=()=>requestAnimationFrame(()=>dispatchNotificationTarget(notificationEvent)),entry=history.state;
        if(isWireframeHistory(entry)&&entry.layer==='modal'){
          let completed=false;
          const onPop=()=>{if(completed)return;completed=true;setTimeout(navigate,0);};
          window.addEventListener('popstate',onPop,{once:true});
          closeModal();
          return;
        }
        rawCloseModal();navigate();
      }
      document.addEventListener('click',browserEvent=>{
        const el=browserEvent.target.closest?.('[data-action]'),action=el?.dataset.action;
        if(!['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].includes(action))return;
        browserEvent.preventDefault();browserEvent.stopImmediatePropagation();
        if(action==='notification-filter'){
          const filter=el.dataset.filter;if(!['all','unread','action'].includes(filter))return;
          state.notificationFilter=filter;rawCloseModal();openNotificationCenter(el);return;
        }
        if(action==='notification-mark-all-read'){
          markAllNotificationsRead();render();rawCloseModal();openNotificationCenter(el);toast('현재 계정의 알림을 모두 읽음 처리했습니다.');return;
        }
        if(action==='notification-toggle-push'){
          const enabled=!notificationPushEnabled();setNotificationPushEnabled(enabled);appendEvent('기기 푸시 설정 변경',enabled?'현재 계정 푸시 켜짐 · 앱 내 알림은 항상 유지':'현재 계정 푸시 꺼짐 · 앱 내 알림은 항상 유지',{notification:false});render();rawCloseModal();openNotificationCenter(el);toast(enabled?'행동이 필요한 업데이트의 푸시를 켰습니다.':'푸시를 껐습니다. 앱 내 알림은 계속 남습니다.');return;
        }
        const ids=String(el.dataset.eventIds||el.dataset.eventId||'').split(',').filter(Boolean),eventId=el.dataset.eventId||ids[0],notificationEvent=(state.events||[]).find(item=>item.id===eventId);
        markNotificationRead(ids);render();if(notificationEvent)closeNotificationModalAndNavigate(notificationEvent);
      },true);
"""
if old_dispatch not in text:
    raise SystemExit('notification target dispatcher marker missing')
text = text.replace(old_dispatch, new_dispatch, 1)

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
