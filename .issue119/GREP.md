# Issue #119 targeted source contexts

Generated only for implementation review; remove before the final PR commit.

## state declaration: `const state =`

matches: 0

## default state: `function createDefaultState`

matches: 0

## state normalization: `function normalize`

matches: 5

### occurrence 1 · line 2650

```html
  2634 |           if(/담당 취소 요청|취소 요청/.test(text))return {audience:['admin'],category:'cancellation',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('cancellation','admin',roomId),groupKey:`admin:cancellation:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2635 |           if(/이의 제출|입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text)){const adminCategory=/이의/.test(text)?'complaint':'issue';return {audience:['admin'],category:adminCategory,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(adminCategory,'admin',roomId),groupKey:`admin:${adminCategory}:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};}
  2636 |           if(/시작 지연|완료 지연|마감 초과/.test(text))return {audience:['admin'],category:'delay',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('delay','admin',roomId),groupKey:`admin:delay:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2637 |           return null;
  2638 |         }
  2639 |         if(actorRole==='admin'){
  2640 |           let targetMaidIds=[...requestedMaidIds];
  2641 |           if(/전체 제출 승인|검수 승인|전체 제출 반려|보완 청소|재청소/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForRoom(roomId);
  2642 |           if(/컴플레인 판정|이의 답변/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForComplaint();
  2643 |           const maidNotice=/^내 |통보|안내|배정|담당 변경|순서 변경|취소|시작 시각|보류|시작 가능|전체 제출 승인|검수 승인|전체 제출 반려|보완|재청소|컴플레인 판정|이의 답변|주급|지급|마감|지연|비활성/.test(text);
  2644 |           if(targetMaidIds.length&&maidNotice){const audience=targetMaidIds.map(id=>`maid:${id}`),informational=/승인|종결|확정|지급 완료|처리 결과|비활성 완료/.test(text)&&!/보완|재청소|지연|마감/.test(text),priority=/긴급|보완|재청소|반려|지연|마감|취소/.test(text)?'high':'normal',pushOptional=category==='payroll'&&/정산 확정/.test(text);return {audience,category,roomId,priority,push:!pushOptional,pushOptional,actionRequired:!informational,status:informational?'handled':'open',target:notificationTargetFor(category,'maid',roomId),groupKey:`${audience.join('|')}:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
  2645 |           if(/미배정.*남|미배정 청소|가능일.*미제출|동기화 실패|저장 충돌|주급.*오류|지급.*예외/.test(text)){return {audience:['admin'],category,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(category,'admin',roomId),groupKey:`admin:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
  2646 |           return null;
  2647 |         }
  2648 |         return null;
  2649 |       }
  2650 |       function normalizeNotificationEvent(event,index=0){if(!event||typeof event!=='object')return event;event.id=event.id||`event-${index}-${String(event.time||'0000').replace(/\D/g,'')}`;event.time=event.time||state.time;event.createdAt=event.createdAt||`${state.selectedDate||'2026-08-15'} ${event.time}`;event.maidIds=Array.isArray(event.maidIds)?event.maidIds:[];event.audience=Array.isArray(event.audience)?event.audience:[];event.readBy=Array.isArray(event.readBy)?event.readBy:[];event.notify=event.notify===true;if(event.notify){event.category=event.category||notificationCategoryFromText(`${event.title} ${event.detail}`);event.priority=event.priority||'normal';event.status=event.status||'open';event.actionRequired=event.actionRequired!==false;event.groupKey=event.groupKey||`${event.audience.join('|')}:${event.category}:${event.roomId||'general'}`;event.target=event.target||notificationTargetFor(event.category,event.audience[0]==='admin'?'admin':'maid',event.roomId);}return event;}
  2651 |       function ensureNotificationState(){state.events=Array.isArray(state.events)?state.events:[];state.notificationPushSettings=state.notificationPushSettings&&typeof state.notificationPushSettings==='object'?state.notificationPushSettings:{};state.notificationFilter=['all','unread','action'].includes(state.notificationFilter)?state.notificationFilter:'all';if(state.notificationSchemaVersion!==NOTIFICATION_SCHEMA_VERSION){const existingIds=new Set(state.events.map(event=>event?.id).filter(Boolean)),seeds=notificationSeedEvents().filter(event=>!existingIds.has(event.id));state.events=[...seeds,...state.events];state.notificationSchemaVersion=NOTIFICATION_SCHEMA_VERSION;}state.notificationSequence=Number(state.notificationSequence||state.events.length);state.events.forEach(normalizeNotificationEvent);return state.events;}
  2652 |       function notificationEventsForKey(key=notificationAudienceKey()){ensureNotificationState();return state.events.filter(event=>event.notify&&event.audience.includes(key)).sort((left,right)=>notificationMinuteValue(right)-notificationMinuteValue(left));}
  2653 |       function notificationBundlesForKey(key=notificationAudienceKey()){
  2654 |         const bundles=[];for(const event of notificationEventsForKey(key)){const stamp=notificationMinuteValue(event),groupKey=event.groupKey||event.id,existing=bundles.find(bundle=>bundle.groupKey===groupKey&&Math.abs(bundle.latestStamp-stamp)<=NOTIFICATION_BUNDLE_WINDOW_MINUTES);if(existing){existing.events.push(event);existing.eventIds.push(event.id);existing.bundleCount+=1;existing.unread=existing.unread||!event.readBy.includes(key);existing.actionRequired=existing.actionRequired||event.actionRequired&&event.status!=='handled';existing.latestStamp=Math.max(existing.latestStamp,stamp);if(stamp>=notificationMinuteValue(existing.latest)){existing.latest=event;existing.title=event.title;existing.detail=event.detail;}}else bundles.push({id:event.id,groupKey,latest:event,events:[event],eventIds:[event.id],bundleCount:1,title:event.title,detail:event.detail,latestStamp:stamp,unread:!event.readBy.includes(key),actionRequired:event.actionRequired&&event.status!=='handled'});}return bundles.sort((left,right)=>right.latestStamp-left.latestStamp);
  2655 |       }
  2656 |       function notificationUnreadCount(key=notificationAudienceKey()){return notificationBundlesForKey(key).filter(bundle=>bundle.unread).length;}
  2657 |       function markNotificationRead(ids,key=notificationAudienceKey()){ensureNotificationState();const targetIds=new Set(Array.isArray(ids)?ids:[ids]);state.events.forEach(event=>{if(targetIds.has(event.id)&&event.notify&&!event.readBy.includes(key))event.readBy.push(key);});}
  2658 |       function markAllNotificationsRead(key=notificationAudienceKey()){notificationEventsForKey(key).forEach(event=>{if(!event.readBy.includes(key))event.readBy.push(key);});}
  2659 |       function notificationPushEnabled(key=notificationPushKey()){ensureNotificationState();if(!(key in state.notificationPushSettings))state.notificationPushSettings[key]=!!state.notificationsEnabled;return !!state.notificationPushSettings[key];}
  2660 |       function setNotificationPushEnabled(enabled,key=notificationPushKey()){ensureNotificationState();state.notificationPushSettings[key]=!!enabled;state.notificationsEnabled=!!enabled;}
  2661 |       function queueForegroundNotification(event){if(!event?.notify||!event.push)return;const currentKey=notificationAudienceKey(),actorKey=event.actorRole==='admin'?'admin':event.actorRole==='maid'&&event.actorMaidId?`maid:${event.actorMaidId}`:null;if(!event.audience.includes(currentKey)||actorKey===currentKey||!notificationPushEnabled(currentKey))return;event.pushState='foreground';event.pushDeliveredAt=`${state.selectedDate} ${state.time}`;if(typeof Notification!=='undefined'&&Notification.permission==='granted'){try{new Notification(event.title,{body:event.detail||'CASTLE THE ART 업무 업데이트'});}catch(error){event.pushState='in-app-fallback';}}}
  2662 |       function resolveRelatedAdminNotification(title,roomId){if(state.role!=='admin'||!/승인|반려|거절|종결|처리 완료|취소 승인|취소 거절/.test(String(title||'')))return;const category=/취소/.test(title)?'cancellation':/컴플레인|이의|판정/.test(title)?'complaint':'inspection';notificationEventsForKey('admin').forEach(event=>{if(event.category===category&&(!roomId||event.roomId===roomId)&&event.status!=='handled'){event.status='handled';event.actionRequired=false;event.resolvedAt=`${state.selectedDate} ${state.time}`;}});}
  2663 |       function appendEvent(title,detail,options={}){
  2664 |         ensureNotificationState();const maidIds=[...new Set((options.maidIds||[]).filter(id=>MAIDS.some(maid=>maid.id===id)))],roomId=notificationRoomFromText(title,detail,options.roomId),attemptId=options.attemptId||null,dedupeKey=options.dedupeKey||null;if(dedupeKey){const existing=(state.events||[]).find(event=>event.dedupeKey===dedupeKey);if(existing)return existing;}
  2665 |         resolveRelatedAdminNotification(title,roomId);const actorRole=options.actorRole||state.role||'system',actorMaidId=options.actorMaidId||(actorRole==='maid'?signedInMaidId():null),policy=notificationPolicyForEvent(title,detail,{...options,maidIds,roomId,actorRole,actorMaidId}),event={id:nextNotificationEventId(),title,time:state.time,createdAt:`${state.selectedDate} ${state.time}`,detail,maidIds:[...maidIds],roomId:roomId||null,attemptId,actorRole,actorMaidId,...(dedupeKey?{dedupeKey}:{})};
  2666 |         if(policy){Object.assign(event,{notify:true,audience:policy.audience,category:policy.category,priority:policy.priority,push:policy.push,pushOptional:!!policy.pushOptional,actionRequired:policy.actionRequired,status:policy.status,target:policy.target,groupKey:policy.groupKey,readBy:[]});for(const key of policy.audience){if(key.startsWith('maid:')){const id=key.slice(5);if(!event.maidIds.includes(id))event.maidIds.push(id);}}}else Object.assign(event,{notify:false,audience:[],readBy:[]});state.events.unshift(event);queueForegroundNotification(event);return event;
  2667 |       }
  2668 |       function durableLedgerSnapshot(targetState=state) {
  2669 |         const sortedEntries=(record,project)=>Object.entries(record||{}).sort(([left],[right])=>left.localeCompare(right)).map(([key,value])=>[key,project(value,key)]),sortedValues=(values,project)=>[...(values||[])].map(project).sort((left,right)=>String(left.id||left[0]||'').localeCompare(String(right.id||right[0]||'')));
  2670 |         return {
  2671 |           reservationSequence:Number(targetState.reservationSequence)||0,
  2672 |           manualCleaningSequence:Number(targetState.manualCleaningSequence)||0,
  2673 |           manualCleaningRequests:sortedEntries(targetState.manualCleaningRequests,item=>({id:item.id,room:item.room,kind:item.kind,status:item.status,targetId:item.targetId,date:item.date,previousJob:item.previousJob||null,createdAt:item.createdAt,completedAt:item.completedAt||null,cancelledAt:item.cancelledAt||null})),
  2674 |           checkoutInspections:sortedEntries(targetState.checkoutInspections,item=>({id:item.id,reservationId:item.reservationId,room:item.room,checkoutAt:item.checkoutAt,completedAt:item.completedAt,method:item.method,attemptId:item.attemptId||null})),
  2675 |           manualAssignmentTargets:sortedValues(targetState.manualAssignmentTargets,item=>({id:item.id,room:item.room,kind:item.kind,date:item.date,effectiveDate:item.effectiveDate||item.date,source:item.source,cancelled:!!item.cancelled,completed:!!item.completed})),
  2676 |           reservations:sortedValues(targetState.reservations,item=>({id:item.id,room:item.room,checkInAt:item.checkInAt,checkOutAt:item.checkOutAt,guestCount:reservationGuestCount(item),source:item.source,status:item.status})),
  2677 |           drafts:sortedValues(targetState.drafts,item=>({id:item.id,room:item.room,kind:item.kind,reservationId:item.reservationId||null,date:item.date||null,visibility:item.visibility||null})),
  2678 |           cleaningSubmissions:sortedEntries(targetState.cleaningSubmissions,item=>({id:item.id,attemptId:item.attemptId,room:item.room,status:item.status,earningId:item.earningId||null,reportId:item.reportId||null,weekStart:item.weekStart,baseRateSnapshot:item.baseRateSnapshot,template:{id:item.templateSnapshot?.id||item.templateId||null,version:item.templateSnapshot?.version||item.templateVersion||null,typeId:item.templateSnapshot?.typeId||null,photoIds:(item.templateSnapshot?.photos||[]).map(photo=>photo.id)},uploads:(item.uploads||[]).map(upload=>({id:upload.id,status:upload.status,maxPhotos:photoUploadLimit(upload),fixture:upload.image?.fixture||null,uploadedAt:upload.image?.uploadedAt||null,photos:uploadPhotoEntries(upload).map(photo=>({id:photo.id,status:photo.status,fixture:photo.image?.fixture||null,uploadedAt:photo.image?.uploadedAt||null}))})),roomIssueIds:[...(item.roomIssueIds||[])],roomIssuePhotoCounts:(item.roomIssuesSnapshot||[]).map(issue=>({id:issue.id,photoIds:(issue.photos||[]).map(photo=>photo.id)})),bombReportSnapshot:item.bombRoomReportSnapshot?{id:item.bombRoomReportSnapshot.id,status:item.bombRoomReportSnapshot.status,photoIds:(item.bombRoomReportSnapshot.photos||[]).map(photo=>photo.id)}:null,candleCountSnapshot:item.candleCountSnapshot??null})),
  2679 |           bombRoomReports:sortedEntries(targetState.bombRoomReports,item=>({id:item.id,attemptId:item.attemptId,submissionId:item.submissionId||null,room:item.room,status:item.status,reportedById:item.reportedById,baseRateSnapshot:item.baseRateSnapshot,photoIds:(item.photos||[]).map(photo=>photo.id)})),
  2680 |           roomIssues:sortedEntries(targetState.roomIssues,(items,room)=>({room,records:(items||[]).map(item=>({id:item.id,attemptId:item.attemptId||null,submissionId:item.submissionId||null,status:item.status,photoIds:(item.photos||[]).map(photo=>photo.id)}))})),
  2681 |           earningRecords:sortedEntries(targetState.earningRecords,item=>({id:item.id,submissionId:item.submissionId,room:item.room,performerId:item.performerId,weekStart:item.weekStart,base:item.base,bombBonus:item.bombBonus,total:item.total,reportId:item.reportId||null})),
  2682 |           paymentRecords:sortedEntries(targetState.paymentRecords,item=>({status:item.status,amountSnapshot:item.amountSnapshot??null,taskIds:[...(item.taskIds||[])].sort(),taskFingerprint:item.taskFingerprint||'',startedAt:item.startedAt||null,paidAt:item.paidAt||null,resolutionReason:item.resolutionReason||null})),
  2683 |           events:(targetState.events||[]).map(item=>({title:item.title,time:item.time,detail:item.detail,maidIds:[...(item.maidIds||[])].sort(),roomId:item.roomId||null,attemptId:item.attemptId||null,dedupeKey:item.dedupeKey||null})),
  2684 |         };
```

### occurrence 2 · line 4088

```html
  4072 |       function calendarDateAriaLabel(iso,{today=false,weekSelected=false}={}) {
  4073 |         const value=dateObject(iso),meta=calendarDayMeta(iso),parts=[`${value.getFullYear()}년 ${value.getMonth()+1}월 ${value.getDate()}일 ${meta.weekdayLabel}요일`];
  4074 |         if(meta.holiday)parts.push(meta.holiday.name);
  4075 |         if(today)parts.push('오늘');
  4076 |         if(weekSelected)parts.push('선택 주차');
  4077 |         return parts.join(', ');
  4078 |       }
  4079 |       function dateLabel(value=state.selectedDate) {
  4080 |         const d=dateObject(value), day=CALENDAR_WEEKDAYS[d.getDay()];
  4081 |         return `${d.getMonth()+1}월 ${d.getDate()}일 (${day})`;
  4082 |       }
  4083 |       function weekStartIso(value) {
  4084 |         const d=dateObject(value), offset=(d.getDay()+6)%7;
  4085 |         d.setDate(d.getDate()-offset);
  4086 |         return dateIso(d);
  4087 |       }
  4088 |       function normalizePayWeek(value) {
  4089 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4090 |         const date=dateObject(value);
  4091 |         if(dateIso(date)!==value)return null;
  4092 |         const start=weekStartIso(value);
  4093 |         return start<='2026-08-10'?start:null;
  4094 |       }
  4095 |       function normalizeWorkHistoryWeek(value) {
  4096 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4097 |         const date=dateObject(value);
  4098 |         if(dateIso(date)!==value)return null;
  4099 |         const start=weekStartIso(value);
  4100 |         return start<='2026-08-17'?start:null;
  4101 |       }
  4102 |       function workHistoryCalendarAllowed() { return state.loggedIn!==false&&state.role==='admin'&&state.adminView==='maids'&&state.adminMaidTab==='history'; }
  4103 |       function weekRangeLabel(start,withYear=false) {
  4104 |         const from=dateObject(start),to=new Date(from);to.setDate(from.getDate()+6);
  4105 |         const prefix=withYear?`${from.getFullYear()}년 `:'';
  4106 |         const fromText=`${from.getMonth()+1}월 ${from.getDate()}일(월)`;
  4107 |         const toText=from.getMonth()===to.getMonth()?`${to.getDate()}일(일)`:`${to.getMonth()+1}월 ${to.getDate()}일(일)`;
  4108 |         return `${prefix}${fromText}–${toText}`;
  4109 |       }
  4110 |       function renderDateTools(showFilters=false) {
  4111 |         return `<div class="date-tools calendar-anchor">
  4112 |           <button class="icon-btn" type="button" data-action="date-shift" data-offset="-1" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  4113 |           <button id="date-picker-trigger" class="date-current" type="button" data-action="open-calendar" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${esc(dateLabel())}</span>${icon('chevronRight','icon-sm')}</button>
  4114 |           <button class="icon-btn" type="button" data-action="date-shift" data-offset="1" aria-label="다음 날짜">${icon('chevronRight')}</button>
  4115 |           ${button('오늘','date-today','outline')}
  4116 |           ${showFilters?`<div class="filter-wrap"><label for="room-status-filter">상태</label><select id="room-status-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>상태 전체</option><option value="occupied" ${state.roomFilter==='occupied'?'selected':''}>투숙 중</option><option value="cleaning" ${state.roomFilter==='cleaning'?'selected':''}>청소 필요</option><option value="available" ${state.roomFilter==='available'?'selected':''}>배정 가능</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>배정 불가</option><option value="candle" ${state.roomFilter==='candle'?'selected':''}>촛불 있음</option><option value="checkout-inspection" ${state.roomFilter==='checkout-inspection'?'selected':''}>퇴실점검 대상</option></select></div>`:''}
  4117 |         </div>`;
  4118 |       }
  4119 | 
  4120 |       function calendarMarkup() {
  4121 |         const [year,month]=state.calendarMonth.split('-').map(Number);
  4122 |         const constrainedWeekMode=['admin-pay','maid-pay','work-history'].includes(state.calendarContext),weekMode=constrainedWeekMode||state.calendarContext==='reservation-week';
```

### occurrence 3 · line 4095

```html
  4079 |       function dateLabel(value=state.selectedDate) {
  4080 |         const d=dateObject(value), day=CALENDAR_WEEKDAYS[d.getDay()];
  4081 |         return `${d.getMonth()+1}월 ${d.getDate()}일 (${day})`;
  4082 |       }
  4083 |       function weekStartIso(value) {
  4084 |         const d=dateObject(value), offset=(d.getDay()+6)%7;
  4085 |         d.setDate(d.getDate()-offset);
  4086 |         return dateIso(d);
  4087 |       }
  4088 |       function normalizePayWeek(value) {
  4089 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4090 |         const date=dateObject(value);
  4091 |         if(dateIso(date)!==value)return null;
  4092 |         const start=weekStartIso(value);
  4093 |         return start<='2026-08-10'?start:null;
  4094 |       }
  4095 |       function normalizeWorkHistoryWeek(value) {
  4096 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4097 |         const date=dateObject(value);
  4098 |         if(dateIso(date)!==value)return null;
  4099 |         const start=weekStartIso(value);
  4100 |         return start<='2026-08-17'?start:null;
  4101 |       }
  4102 |       function workHistoryCalendarAllowed() { return state.loggedIn!==false&&state.role==='admin'&&state.adminView==='maids'&&state.adminMaidTab==='history'; }
  4103 |       function weekRangeLabel(start,withYear=false) {
  4104 |         const from=dateObject(start),to=new Date(from);to.setDate(from.getDate()+6);
  4105 |         const prefix=withYear?`${from.getFullYear()}년 `:'';
  4106 |         const fromText=`${from.getMonth()+1}월 ${from.getDate()}일(월)`;
  4107 |         const toText=from.getMonth()===to.getMonth()?`${to.getDate()}일(일)`:`${to.getMonth()+1}월 ${to.getDate()}일(일)`;
  4108 |         return `${prefix}${fromText}–${toText}`;
  4109 |       }
  4110 |       function renderDateTools(showFilters=false) {
  4111 |         return `<div class="date-tools calendar-anchor">
  4112 |           <button class="icon-btn" type="button" data-action="date-shift" data-offset="-1" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  4113 |           <button id="date-picker-trigger" class="date-current" type="button" data-action="open-calendar" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${esc(dateLabel())}</span>${icon('chevronRight','icon-sm')}</button>
  4114 |           <button class="icon-btn" type="button" data-action="date-shift" data-offset="1" aria-label="다음 날짜">${icon('chevronRight')}</button>
  4115 |           ${button('오늘','date-today','outline')}
  4116 |           ${showFilters?`<div class="filter-wrap"><label for="room-status-filter">상태</label><select id="room-status-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>상태 전체</option><option value="occupied" ${state.roomFilter==='occupied'?'selected':''}>투숙 중</option><option value="cleaning" ${state.roomFilter==='cleaning'?'selected':''}>청소 필요</option><option value="available" ${state.roomFilter==='available'?'selected':''}>배정 가능</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>배정 불가</option><option value="candle" ${state.roomFilter==='candle'?'selected':''}>촛불 있음</option><option value="checkout-inspection" ${state.roomFilter==='checkout-inspection'?'selected':''}>퇴실점검 대상</option></select></div>`:''}
  4117 |         </div>`;
  4118 |       }
  4119 | 
  4120 |       function calendarMarkup() {
  4121 |         const [year,month]=state.calendarMonth.split('-').map(Number);
  4122 |         const constrainedWeekMode=['admin-pay','maid-pay','work-history'].includes(state.calendarContext),weekMode=constrainedWeekMode||state.calendarContext==='reservation-week';
  4123 |         const weekSelectedStart=state.calendarContext==='admin-pay'?state.adminPayWeek:state.calendarContext==='maid-pay'?(state.maidPaySelectedWeek||state.maidPayOpenWeek||'2026-08-03'):state.calendarContext==='reservation-week'?state.reservationWeekStart:state.workHistoryWeek;
  4124 |         const latestWeek=state.calendarContext==='work-history'?'2026-08-17':'2026-08-10';
  4125 |         const first=new Date(year,month-1,1),offset=first.getDay(),start=new Date(year,month-1,1-offset);
  4126 |         const days=Array.from({length:42},(_,i)=>{const d=new Date(start);d.setDate(start.getDate()+i);return d;});
  4127 |         return `<div class="calendar-backdrop" data-action="calendar-backdrop"><section class="calendar-dialog" role="dialog" aria-modal="true" aria-labelledby="calendar-title">
  4128 |           <div class="calendar-head"><button class="icon-btn" type="button" data-action="calendar-month" data-offset="-1" aria-label="이전 달">${icon('chevronLeft')}</button><strong id="calendar-title">${year}년 ${month}월</strong><button class="icon-btn" type="button" data-action="calendar-month" data-offset="1" aria-label="다음 달">${icon('chevronRight')}</button></div>
  4129 |           ${weekMode?`<p class="pay-week-calendar-note">날짜를 누르면 그 날짜가 포함된 월요일–일요일 주차를 선택합니다.</p>`:''}
```

### occurrence 4 · line 5133

```html
  5117 |       function guestCountForAttempt(attempt) {
  5118 |         const value=Number(attempt?.guestCountSnapshot);return Number.isInteger(value)&&value>=1?value:null;
  5119 |       }
  5120 |       function attemptWorkDate(attempt,fallback=state.selectedDate) { const timestamp=attempt?.startedAt||attempt?.createdAt;return attempt?.workDate||(timestamp?timestampIsoDate(timestamp,fallback):fallback); }
  5121 |       function attemptOperationalDate(attempt,fallback=state.selectedDate) { return attempt?.effectiveDate||attemptWorkDate(attempt,fallback); }
  5122 |       function directAssignmentWorkDate(no) { const attempt=activeUnfinishedAttempt(no);return attempt?attemptOperationalDate(attempt,state.selectedDate):state.assignmentDate; }
  5123 |       function directAssignmentDayIndex(no) { return weekdayIndex(directAssignmentWorkDate(no)); }
  5124 |       function assignmentHistoryTargetId(no,kind,workDate) { return (workDate===state.assignmentDate?assignmentTargets().find(item=>item.room===no&&item.kind===kind)?.id:null)||`work-${no}-${String(kind).replaceAll(' ','-')}-${workDate}`; }
  5125 |       function directAssignmentTarget(no) {
  5126 |         const room=ROOMS.find(entry=>entry.no===no)||ROOMS[0],attempt=activeUnfinishedAttempt(no),workDate=directAssignmentWorkDate(no);
  5127 |         if(attempt)return {id:attempt.workTargetId||assignmentHistoryTargetId(no,attempt.kind,workDate),room:no,type:room.type,kind:attempt.kind,date:attemptWorkDate(attempt,workDate),planDate:attemptWorkDate(attempt,workDate),effectiveDate:attemptOperationalDate(attempt,workDate),checkout:attempt.checkoutSnapshot||attempt.accessStart||startTimeFor(no),checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||'—',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||attempt.checkoutSnapshot||null,source:'manual',sourceLabel:'현재 작업',reservationId:attempt.reservationIdSnapshot||null,guestCount:attempt.guestCountSnapshot??null};
  5128 |         const targets=assignmentTargets().filter(item=>item.room===no);
  5129 |         if(targets.length>1)return null;
  5130 |         if(targets.length===1)return targets[0];
  5131 |         const kind='퇴실 청소';return {id:assignmentHistoryTargetId(no,kind,workDate),room:no,type:room.type,kind,checkout:startTimeFor(no),deadline:'—',source:'manual',sourceLabel:'현재 작업'};
  5132 |       }
  5133 |       function normalizeAssignmentOrderFor(maidId) {
  5134 |         if(!maidId)return;
  5135 |         const ordered=orderedAssignmentsForMaid(maidId);ordered.forEach((item,index)=>{assignmentFor(item).order=index+1;});ordered.forEach(syncAssignmentDraftStatus);
  5136 |       }
  5137 |       function commitRemainingNotifiedOrdersAfterCancellation(maidId,assignmentDate=state.assignmentDate) {
  5138 |         if(!maidId)return {changes:[],route:[]};
  5139 |         const entries=Object.entries(state.assignments||{}).map(([targetId,record])=>({targetId,record,item:record?.committedTarget})).filter(entry=>entry.record?.status!=='cancelled'&&entry.record?.previousMaidId===maidId&&entry.item&&targetEffectiveDate(entry.item,'')===assignmentDate).sort((left,right)=>(Number(left.record.previousOrder)||Number.MAX_SAFE_INTEGER)-(Number(right.record.previousOrder)||Number.MAX_SAFE_INTEGER)||left.item.room.localeCompare(right.item.room,'ko',{numeric:true}));
  5140 |         const changes=[];
  5141 |         entries.forEach((entry,index)=>{
  5142 |           const nextOrder=index+1,beforeOrder=entry.record.previousOrder;
  5143 |           entry.record.previousOrder=nextOrder;if(entry.record.status==='notified'&&entry.record.maidId===maidId)entry.record.order=nextOrder;
  5144 |           if(beforeOrder!==nextOrder){changes.push({item:entry.item,beforeOrder,afterOrder:nextOrder});state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:entry.targetId,assignmentDate,room:entry.item.room,beforeMaidId:maidId,afterMaidId:maidId,before:`${maidName(maidId)} · ${beforeOrder||'순서 없음'}${beforeOrder?'번째':''}`,after:`${maidName(maidId)} · ${nextOrder}번째`,reason:'청소 대상 취소 · 남은 순서 자동 정리'});}
  5145 |         });
  5146 |         return {changes,route:entries.map(entry=>({item:entry.item,order:entry.record.previousOrder}))};
  5147 |       }
  5148 |       function cancelPendingStayoverTargetsAfterCheckout(roomNo,preserveTargetId=null) {
  5149 |         const room=ROOMS.find(item=>item.no===roomNo),candidateById=new Map(),addCandidate=item=>{
  5150 |           if(!item?.id||item.id===preserveTargetId||item.room!==roomNo||item.kind!=='연박 청소'||targetEffectiveDate(item,'')<state.selectedDate)return;
  5151 |           const assignment=state.assignments?.[item.id],ledger=state.cleaningTargets?.[item.id];
  5152 |           if(assignment?.status==='cancelled'||ledger?.closed)return;
  5153 |           candidateById.set(item.id,{...cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate)),...item});
  5154 |         };
  5155 |         const dates=new Set([state.selectedDate,state.assignmentDate,room?.stayoverRequest?.date].filter(date=>date&&date>=state.selectedDate));
  5156 |         dates.forEach(date=>assignmentTargetsForDate(date).forEach(addCandidate));
  5157 |         (state.manualAssignmentTargets||[]).filter(item=>!item.cancelled).forEach(addCandidate);
  5158 |         Object.values(state.cleaningTargets||{}).forEach(addCandidate);
  5159 |         Object.values(state.assignments||{}).forEach(record=>addCandidate(record?.committedTarget));
  5160 |         Object.values(state.cleaningAttempts||{}).forEach(attempt=>{
  5161 |           if(attempt?.room!==roomNo||attempt.kind!=='연박 청소'||attempt.startedAt||attempt.completedAt||['submitted','approved','rejected','superseded'].includes(attempt.status)||attemptOperationalDate(attempt,'')<state.selectedDate)return;
  5162 |           const item=state.cleaningTargets?.[attempt.workTargetId]||state.assignments?.[attempt.workTargetId]?.committedTarget||(state.manualAssignmentTargets||[]).find(target=>target.id===attempt.workTargetId)||{id:attempt.workTargetId,room:roomNo,type:attempt.roomMetaSnapshot?.typeId||room?.type||'standard',kind:'연박 청소',date:attemptWorkDate(attempt,state.selectedDate),effectiveDate:attemptOperationalDate(attempt,state.selectedDate),accessStart:attempt.accessStart||null,requestDue:attempt.requestDue||null,accessEnd:attempt.accessEnd||null,source:'attempt',sourceLabel:'미시작 수행 회차'};
  5163 |           addCandidate(item);
  5164 |         });
  5165 |         const cancelledAt=`${state.selectedDate} ${state.time}`,reasonCode='reservation',reason='실제 체크아웃 기록 · 투숙 중 청소 종료',notices=[];
  5166 |         [...candidateById.values()].forEach(item=>{
  5167 |           const assignment=state.assignments[item.id]||(state.assignments[item.id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null}),selectedMaidId=assignment.maidId||null,notifiedMaidId=assignment.previousMaidId||(assignment.status==='notified'?assignment.maidId:null),notifiedOrder=assignment.previousOrder??assignment.order,beforeMaidId=notifiedMaidId||selectedMaidId||null,beforeOrder=notifiedOrder??assignment.order??null,snapshot=assignment.committedTarget||cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate)),attempt=attemptForCleaningTarget(item),targetRecord=state.cleaningTargets[item.id]||cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate));
```

### occurrence 5 · line 5479

```html
  5463 |       function payrollTaskDateIso(value,weekStart) {
  5464 |         const direct=timestampIsoDate(value,'');
  5465 |         if(direct)return direct;
  5466 |         const match=String(value||'').match(/(\d{1,2})월\s*(\d{1,2})일/),weekEnd=addIsoDays(weekStart,6),baseYear=Number(String(weekStart).slice(0,4));
  5467 |         if(!match)return '';
  5468 |         for(const year of [baseYear-1,baseYear,baseYear+1]){const candidate=`${year}-${String(Number(match[1])).padStart(2,'0')}-${String(Number(match[2])).padStart(2,'0')}`;if(candidate>=weekStart&&candidate<=weekEnd)return candidate;}
  5469 |         return '';
  5470 |       }
  5471 |       function roomMetadataSnapshot(no) {
  5472 |         const room=ROOMS.find(item=>item.no===String(no)),type=room?ROOM_TYPES[room.type]:null;
  5473 |         return room&&type?{roomNo:room.no,typeId:room.type,typeName:type.name,elevator:room.elevator||null}:null;
  5474 |       }
  5475 |       function payrollTaskRoomContext(roomNo,snapshot=null) {
  5476 |         const baseline=ROOM_BASELINE.find(item=>item.no===String(roomNo)),room=snapshot?null:baseline,typeId=snapshot?.typeId||room?.type||null,type=typeId?ROOM_TYPES[typeId]:null,elevator=snapshot?.elevator??room?.elevator??null;
  5477 |         return {room,type,typeName:snapshot?.typeName||type?.name||'객실 타입 미입력',elevator:elevator?`${elevator} 엘리베이터`:'엘리베이터 미기재'};
  5478 |       }
  5479 |       function normalizePayrollFixture(task,weekStart,maidId) {
  5480 |         const roomNo=String(task.room),context=payrollTaskRoomContext(roomNo),base=Number(task.base??context.type?.rate??0),bombBonus=Number(task.bombBonus||0),amount=base+bombBonus;
  5481 |         return {...task,id:task.id||`pay-${weekStart}-${maidId}-${roomNo}`,weekStart,maidId,roomNo,room:`${roomNo}호`,typeName:context.typeName,elevator:context.elevator,earnedOn:payrollTaskDateIso(task.date,weekStart),baseAmount:base,bombBonus,amount,total:amount,stage:'confirmed',status:task.status||'승인 확정',tone:'green',bombStatus:bombBonus?'approved':'none',source:'fixture',included:true,potential:false};
  5482 |       }
  5483 |       function currentPayrollTasks(maidId,weekStart='2026-08-10') {
  5484 |         const confirmed=validatedEarningRecords().filter(record=>record.weekStart===weekStart&&record.performerId===maidId).sort((a,b)=>String(b.creditedAt).localeCompare(String(a.creditedAt))).map(record=>{
  5485 |           const submission=validatedSubmission(state.cleaningSubmissions?.[record.submissionId]||null),report=bombRoomReportForSubmission(submission),context=payrollTaskRoomContext(record.room,submission?.roomMetaSnapshot);
  5486 |           return {id:record.id,weekStart,maidId,roomNo:record.room,room:`${record.room}호`,typeName:context.typeName,elevator:context.elevator,kind:submission?.kind||'퇴실 청소',date:payrollDateLabel(submission?.completedAt||submission?.submittedAt),earnedOn:timestampIsoDate(submission?.completedAt||submission?.submittedAt,weekStart),baseAmount:record.base,bombBonus:record.bombBonus,amount:record.total,total:record.total,stage:'confirmed',status:record.bombBonus?'폭탄방 승인 · ×2':report?.status==='rejected'?'폭탄방 미인정 · 승인 확정':'승인 확정',tone:'green',bombStatus:report?.status||'none',reportId:report?.id||null,photoId:report?.photos?.[0]?.id||null,submissionId:submission?.id||record.submissionId,attemptId:submission?.attemptId||null,roundLabel:String(record.submissionId||'').split('-').slice(-2).join('-'),source:'earning',included:true,potential:false};
  5487 |         });
  5488 |         const unsettled=validatedSubmissions().filter(submission=>submission.weekStart===weekStart&&submission.performerId===maidId&&!earningRecordForSubmission(submission)&&(['pending','rejected'].includes(submission.status)||(submission.status==='approved'&&submission.kind==='재청소'))).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))).map(submission=>{
  5489 |           const report=bombRoomReportForSubmission(submission),wholeRejected=submission.status==='rejected',unpaidReclean=submission.kind==='재청소',unpaidApproved=unpaidReclean&&submission.status==='approved',fee=bombRoomBreakdown(submission.room,{pendingAsBonus:!wholeRejected&&!unpaidReclean&&report?.status==='pending',reportOverride:report,baseOverride:submission.baseRateSnapshot}),context=payrollTaskRoomContext(submission.room,submission.roomMetaSnapshot),stage=wholeRejected||unpaidReclean?'excluded':'pending';
  5490 |           const decision=report?.status==='approved'?'폭탄방 승인 결정':report?.status==='rejected'?'폭탄방 미인정 결정':report?.status==='pending'?'폭탄방 검수 대기':'폭탄방 신고 없음',status=wholeRejected?`청소 전체 반려 · ${decision} 보존`:unpaidApproved?'재청소 승인 · 무급 0원':unpaidReclean?'재청소 검수 대기 · 무급 0원':report?.status==='pending'?'폭탄방 검수 대기':report?.status==='approved'?'폭탄방 인정 · 전체 검수 대기':report?.status==='rejected'?'폭탄방 미인정 · 전체 검수 대기':'검수 대기';
  5491 |           return {id:`pay-${submission.id}`,weekStart,maidId,roomNo:submission.room,room:`${submission.room}호`,typeName:context.typeName,elevator:context.elevator,kind:submission.kind||'퇴실 청소',date:payrollDateLabel(submission.completedAt||submission.submittedAt),earnedOn:timestampIsoDate(submission.completedAt||submission.submittedAt,weekStart),baseAmount:unpaidReclean?0:fee.base,bombBonus:unpaidReclean?0:fee.bonus,amount:stage==='pending'?fee.total:0,total:stage==='pending'?fee.total:0,referenceBase:fee.base,referenceBombBonus:fee.bonus,referenceTotal:fee.total,stage,status,tone:wholeRejected?'red':unpaidApproved?'green':'amber',bombStatus:report?.status||'none',reportId:report?.id||null,photoId:report?.photos?.[0]?.id||null,submissionId:submission.id,attemptId:submission.attemptId,roundLabel:String(submission.id).split('-').slice(-2).join('-'),source:'submission',included:false,potential:stage==='pending',breakdownText:wholeRejected&&report?`${decision} · 기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 실제 적립 0원`:unpaidReclean?'처음 청소한 본인 재청소 · 적립 0원 · 수익 원장 없음':''};
  5492 |         });
  5493 |         const aborted=Object.values(state.bombRoomReports||{}).filter(report=>!report.submissionId&&report.attemptStatus==='superseded'&&report.reportedById===maidId&&weekStartIso(timestampIsoDate(report.reportedAt))===weekStart).map(report=>{const attempt=state.cleaningAttempts?.[report.attemptId],context=payrollTaskRoomContext(report.room,attempt?.roomMetaSnapshot);return {id:`pay-${report.id}`,weekStart,maidId,roomNo:report.room,room:`${report.room}호`,typeName:context.typeName,elevator:context.elevator,kind:attempt?.kind||'퇴실 청소',date:payrollDateLabel(report.reportedAt),earnedOn:timestampIsoDate(report.reportedAt,weekStart),baseAmount:report.baseRateSnapshot,bombBonus:0,amount:0,total:0,referenceBase:report.baseRateSnapshot,referenceBombBonus:0,referenceTotal:report.baseRateSnapshot,stage:'excluded',status:'제출 전 회차 종료 · 적립 없음',tone:'red',bombStatus:report.status,reportId:report.id,photoId:report.photos?.[0]?.id||null,attemptId:report.attemptId,roundLabel:String(report.attemptId||'').split('-').slice(-2).join('-'),source:'report',included:false,potential:false,breakdownText:'미제출 폭탄방 증빙 보존 · 담당 변경으로 회차 종료 · 적립 0원'};});
  5494 |         return [...confirmed,...unsettled,...aborted];
  5495 |       }
  5496 |       function payrollTasksFor(weekStart,maidId) {
  5497 |         const fixtures=(PAYROLL_CLEANING_FIXTURES[weekStart]?.[maidId]||[]).map(task=>normalizePayrollFixture(task,weekStart,maidId));
  5498 |         return weekStart==='2026-08-10'?[...currentPayrollTasks(maidId,weekStart),...fixtures]:fixtures;
  5499 |       }
  5500 |       function payrollTaskTotals(tasks=[]) {
  5501 |         return tasks.reduce((sum,task)=>{if(task.stage==='confirmed')sum.confirmed+=task.amount;if(task.stage==='pending')sum.pending+=task.amount;return sum;},{confirmed:0,pending:0});
  5502 |       }
  5503 |       function adminPayDetailId(weekStart,maidId) { return `${weekStart}_${maidId}`; }
  5504 |       function parseAdminPayDetailId(value) {
  5505 |         const match=String(value||'').match(/^(\d{4}-\d{2}-\d{2})_(m\d+)$/);
  5506 |         if(!match||!MAIDS.some(maid=>maid.id===match[2]))return null;
  5507 |         return {weekStart:match[1],maidId:match[2]};
  5508 |       }
  5509 |       const DEMO_TODAY='2026-08-15';
  5510 |       const CURRENT_PAYMENT_WEEK_START='2026-08-10';
  5511 |       const FIRST_OPEN_PAYMENT_WEEK_START='2026-08-03';
  5512 |       function paymentRecordKey(weekStart,maidId) { return `${weekStart}:${maidId}`; }
  5513 |       function defaultPaymentStatus(weekStart) { return weekStart<FIRST_OPEN_PAYMENT_WEEK_START?'PAID':'OPEN'; }
```

## main render: `function render()`

matches: 1

### occurrence 1 · line 2783

```html
  2767 |       }
  2768 |       window.addEventListener('scroll',scheduleScrollTopButtonSync,{passive:true});
  2769 |       window.addEventListener('resize',scheduleScrollTopButtonSync,{passive:true});
  2770 |       scrollTopButton?.addEventListener('click',()=>{
  2771 |         const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  2772 |         if(reduced){
  2773 |           const root=document.documentElement,previous=root.style.scrollBehavior;
  2774 |           root.style.scrollBehavior='auto';window.scrollTo(0,0);root.style.scrollBehavior=previous;
  2775 |           syncScrollTopButton();
  2776 |         } else {
  2777 |           window.scrollTo({top:0,left:0,behavior:'smooth'});
  2778 |         }
  2779 |         requestAnimationFrame(()=>document.getElementById('main-content')?.focus({preventScroll:true}));
  2780 |       });
  2781 |       syncScrollTopButton();
  2782 | 
  2783 |       function render() {
  2784 |         const durableRenderSameState=durableRenderStateRef===state,durableBefore=durableLedgerFingerprint(state);
  2785 |         projectReservationState(state);
  2786 |         const nav=currentNav();
  2787 |         const app=document.getElementById('app');
  2788 |         app.className=state.role==='admin'?'admin-mode':'';
  2789 |         app.innerHTML=`
  2790 |           ${renderDemoStrip()}
  2791 |           ${state.loggedIn ? `
  2792 |           <div class="app-shell">
  2793 |             ${renderSidebar(nav)}
  2794 |             <div class="workspace">
  2795 |               ${renderTopbar()}
  2796 |               <main id="main-content" tabindex="-1">${renderMain()}</main>
  2797 |               ${renderBottomNav(nav)}
  2798 |             </div>
  2799 |           </div>` : renderLogin()}
  2800 |         `;
  2801 |         applyAdminCopyPolicy(app);
  2802 |         document.documentElement.style.setProperty('--nav-count', nav.length);
  2803 |         document.title=`${titleForView()} · CASTLE THE ART 데모`;
  2804 |         syncUrlState();
  2805 |         if(state.loggedIn&&state.role==='admin'&&state.adminView==='quickReservation'&&!state.detail)restoreQuickGridViewport();
  2806 |         const durableAfter=durableLedgerFingerprint(state);if(durableRenderSameState&&durableAfter!==durableBefore)throw new Error('렌더링 중 예약·청소 제출·급여·지급 원장이 변경되었습니다.');durableRenderStateRef=state;assertNoDuplicateDurableRecords(state);
  2807 |       }
  2808 | 
  2809 |       function historyRouteSnapshot(scrollY=modalPageScrollY??window.scrollY) {
  2810 |         return {
  2811 |           scenario:Number(state.scenario),role:state.role,currentMaidId:signedInMaidId(),view:currentView(),
  2812 |           detail:state.detail?{type:String(state.detail.type),id:String(state.detail.id),...(state.detail.mode?{mode:String(state.detail.mode)}:{})}:null,
  2813 |           date:state.selectedDate,filter:state.roomFilter,typeFilter:state.roomTypeFilter,q:state.roomSearch,
  2814 |           quickAnchor:state.quickReservationFollowsToday===false?state.quickReservationAnchorDate:null,quickType:state.quickReservationType,quickQ:state.quickReservationSearch,quickGridLeft:state.quickGridScrollLeft,quickGridTop:state.quickGridScrollTop,
  2815 |           reservationWeekStart:state.reservationWeekStart,reservationWeekRoom:state.reservationWeekRoom,
  2816 |           scrollY:Math.max(0,Math.round(Number(scrollY)||0)),loggedIn:state.loggedIn!==false,
  2817 |           adminMaidTab:state.adminMaidTab,workHistoryWeek:state.workHistoryWeek,workHistoryMaid:state.workHistoryMaid,calendarContext:state.calendarContext,calendarMonth:state.calendarMonth,cleaningTab:state.cleaningTab,assignmentTypeFilter:state.assignmentTypeFilter,adminPayWeek:state.adminPayWeek,
```

## shell render: `function renderShell`

matches: 0

## admin navigation: `ADMIN_NAV`

matches: 0

## maid navigation: `MAID_NAV`

matches: 0

## maid route: `function renderMaid`

matches: 18

### occurrence 1 · line 3355

```html
  3339 | 
  3340 |       function renderScenario13Controls() {
  3341 |         if (state.scenario!==13) return '';
  3342 |         return `<section class="notice notice-info"><div style="flex:1"><strong>목록 상태 계약 데모</strong><br>상태를 바꾸면 정상 데이터·위험 행동 잠금 여부가 함께 변합니다.</div><label for="list-mode" class="sr-only">목록 상태</label><select id="list-mode" class="select-control" data-control="list-mode"><option value="loading" ${state.listMode==='loading'?'selected':''}>불러오는 중</option><option value="empty" ${state.listMode==='empty'?'selected':''}>진짜 0건</option><option value="filterEmpty" ${state.listMode==='filterEmpty'?'selected':''}>필터 결과 없음</option><option value="data" ${state.listMode==='data'?'selected':''}>데이터 있음</option><option value="stale" ${state.listMode==='stale'?'selected':''}>오래된 데이터·오류</option></select></section>`;
  3343 |       }
  3344 | 
  3345 |       function renderDraftRail() {
  3346 |         return `<section class="card"><div class="section-head"><h3>배정 준비 청소 작업</h3><span class="meta">${state.drafts.length}건</span></div><p class="cell-sub">근무일 전날 관리자 담당 배정을 기다립니다.</p><div class="rail-list">${state.drafts.length?state.drafts.map(d=>`<label class="rail-row"><input type="checkbox" data-control="draft" value="${d.id}" ${state.selectedDrafts.includes(d.id)?'checked':''} ${isLocked()?'disabled':''}><strong>${d.room}호 · ${d.kind}</strong><span>${d.created}</span></label>`).join(''):'<div class="state-panel" style="padding:12px"><p>배정 준비 작업 0건</p></div>'}</div>${button('내일 배정에서 보기','publish-selected','success',`${isLocked()?'disabled':''}`)}</section>`;
  3347 |       }
  3348 |       function renderInspectionRail() { return `<section class="card"><div class="section-head"><h3>검수 대상 목록</h3><span class="meta">4건</span></div><div class="rail-list"><div class="rail-row"><strong>639호 · 전체 제출 v2</strong><span>10:18</span></div><div class="rail-row"><strong>528호 · 업로드 완료</strong><span>10:14</span></div></div>${button('검수 대상 목록 보기','cleaning-detail','outline','data-id="639"')}</section>`; }
  3349 |       function renderPayRail() { const summary=paymentWeekSummaryFor();return `<section class="card"><div class="section-head"><h3>지난주 지급</h3>${statusBadge(summary.label,summary.tone)}</div><p class="cell-sub">메이드별 외부 전액 송금 완료를 각각 기록합니다. 앱은 송금하지 않습니다.</p>${button('지급 주차 상세','pay-detail','outline')}</section>`; }
  3350 | 
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
  3354 | 
  3355 |       function renderMaids() {
  3356 |         const cards=MAIDS.map(m=>`<article class="card setting-card"><div class="avatar">${m.name[0]}</div><div style="min-width:0;flex:1"><h3>${m.name} · 데모</h3><p>${m.phone} · 관리자 배정 ${m.assigned}건<br>${m.id==='m1'&&state.maidStatus!=='active'?state.maidStatus:m.active}</p>${button('상세 보기','maid-detail','outline',`data-id="${m.id}"`)}</div></article>`).join('');
  3357 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>메이드 계정·업무 현황</h2><span class="meta">담당·실제 수행·제출·수익 귀속을 분리해 보존</span></div><div class="actions">${button('계정 추가','demo-info','primary')}</div></div><div class="settings-grid">${cards}</div>`;
  3358 |       }
  3359 | 
  3360 |       function renderAdminMore() {
  3361 |         return renderCoach()+renderNetworkNotice()+`<div class="settings-grid">
  3362 |           ${settingCard('wallet','주급·지급',`지난주 상태 ${paymentWeekSummaryFor().label} · 메이드별 외부 송금 기록`,button('지급 상세','pay-detail','outline'))}
  3363 |           ${settingCard('settings','객실 타입 청소요금·예상시간','청소요금은 8월 시트 정본 · 예상시간은 데모',button('청소요금 보기','rates','outline'))}
  3364 |           ${settingCard('list','청소 템플릿',`초안·미리보기·게시 버전 · 현재 ${state.template}`,button('템플릿 관리','template','outline'))}
  3365 |           ${settingCard('bell','알림 상태',state.notificationsEnabled?'이 기기 알림 허용 데모':'권한 요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}
  3366 |           ${settingCard('shield','감사 이력','PIN 조회 사실·검수·단가·지급 수행자 기록',button('최근 이력 보기','audit-log','outline'))}
  3367 |           ${settingCard('lock','로그인·보안 상태','최초 변경·5회 실패·15분 잠금 데모',button('로그인 상태 보기','logout','outline'))}
  3368 |         </div>`;
  3369 |       }
  3370 | 
  3371 |       function settingCard(iconName,title,desc,action) { return `<article class="card setting-card"><div class="setting-icon">${icon(iconName)}</div><div style="min-width:0;flex:1"><h3>${title}</h3><p>${desc}</p>${action}</div></article>`; }
  3372 | 
  3373 |       function publicJobs() {
  3374 |         return [
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
```

### occurrence 2 · line 3386

```html
  3370 | 
  3371 |       function settingCard(iconName,title,desc,action) { return `<article class="card setting-card"><div class="setting-icon">${icon(iconName)}</div><div style="min-width:0;flex:1"><h3>${title}</h3><p>${desc}</p>${action}</div></article>`; }
  3372 | 
  3373 |       function publicJobs() {
  3374 |         return [
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
  3390 | 
  3391 |       function renderMaidMy() {
  3392 |         const myJobs=[
  3393 |           {room:'350',type:'standard',kind:'퇴실 청소',status:state.jobs['350'],schedule:'11:00부터 시작 · 15:30 준비 마감'},
  3394 |           {room:'528',type:'premium',kind:'퇴실 청소',status:state.jobs['528'],schedule:'10:00 시작 가능 · 14:00 다음 입실'}
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
```

### occurrence 3 · line 3391

```html
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
  3390 | 
  3391 |       function renderMaidMy() {
  3392 |         const myJobs=[
  3393 |           {room:'350',type:'standard',kind:'퇴실 청소',status:state.jobs['350'],schedule:'11:00부터 시작 · 15:30 준비 마감'},
  3394 |           {room:'528',type:'premium',kind:'퇴실 청소',status:state.jobs['528'],schedule:'10:00 시작 가능 · 14:00 다음 입실'}
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
  3425 |       }
```

### occurrence 4 · line 3411

```html
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
  3425 |       }
  3426 | 
  3427 |       function renderMaidMore() {
  3428 |         return `<div class="settings-grid">${settingCard('user','내 정보','김민지1 · 데모 · 휴대폰 •••• 4821',button('정보 보기','demo-info','outline'))}${settingCard('bell','알림 권한',state.notificationsEnabled?'허용 · 앱 내부 알림 사용':'요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}${settingCard('lock','로그인 비밀번호','개인 숫자 6자리 이상 · 객실 PIN과 분리',button('변경 데모','demo-info','outline'))}</div>`;
  3429 |       }
  3430 | 
  3431 |       function renderDetail() {
  3432 |         if(!state.detail||!detailAllowedForRole(state.detail.type,state.role)){state.detail=null;return renderMain();}
  3433 |         if (state.detail.type==='templates') return renderTemplateList();
  3434 |         if (state.detail.type==='template') return renderTemplateDetail(state.detail.id,state.detail.mode||'view');
  3435 |         if (state.detail.type==='room') return renderRoomDetail(state.detail.id);
  3436 |         if (state.detail.type==='cleaning') return renderCleaningDetail(state.detail.id);
  3437 |         if (state.detail.type==='maid') return renderMaidDetail(state.detail.id);
  3438 |         if (state.detail.type==='complaint') return renderComplaintDetail();
  3439 |         if (state.detail.type==='pay') return renderPayDetail();
  3440 |         return '';
  3441 |       }
  3442 | 
  3443 |       function detailHeader(title,subtitle='') { return `<div class="detail-head"><button class="btn btn-ghost" type="button" data-action="back">${icon('chevronLeft','icon-sm')}목록</button><div class="detail-title"><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div></div>`; }
  3444 | 
  3445 |       function renderRoomDetailLegacy(no) {
```

### occurrence 5 · line 3417

```html
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
  3425 |       }
  3426 | 
  3427 |       function renderMaidMore() {
  3428 |         return `<div class="settings-grid">${settingCard('user','내 정보','김민지1 · 데모 · 휴대폰 •••• 4821',button('정보 보기','demo-info','outline'))}${settingCard('bell','알림 권한',state.notificationsEnabled?'허용 · 앱 내부 알림 사용':'요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}${settingCard('lock','로그인 비밀번호','개인 숫자 6자리 이상 · 객실 PIN과 분리',button('변경 데모','demo-info','outline'))}</div>`;
  3429 |       }
  3430 | 
  3431 |       function renderDetail() {
  3432 |         if(!state.detail||!detailAllowedForRole(state.detail.type,state.role)){state.detail=null;return renderMain();}
  3433 |         if (state.detail.type==='templates') return renderTemplateList();
  3434 |         if (state.detail.type==='template') return renderTemplateDetail(state.detail.id,state.detail.mode||'view');
  3435 |         if (state.detail.type==='room') return renderRoomDetail(state.detail.id);
  3436 |         if (state.detail.type==='cleaning') return renderCleaningDetail(state.detail.id);
  3437 |         if (state.detail.type==='maid') return renderMaidDetail(state.detail.id);
  3438 |         if (state.detail.type==='complaint') return renderComplaintDetail();
  3439 |         if (state.detail.type==='pay') return renderPayDetail();
  3440 |         return '';
  3441 |       }
  3442 | 
  3443 |       function detailHeader(title,subtitle='') { return `<div class="detail-head"><button class="btn btn-ghost" type="button" data-action="back">${icon('chevronLeft','icon-sm')}목록</button><div class="detail-title"><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div></div>`; }
  3444 | 
  3445 |       function renderRoomDetailLegacy(no) {
  3446 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room.type], p=roomPresentation(no);
  3447 |         let special='';
  3448 |         if (no==='350') special=`<section class="card card-pad"><div class="section-head"><h3>입실 준비 조건</h3>${statusBadge(p.status,p.tone)}</div><div class="info-grid"><div class="info-item"><span>청소 검수</span><strong>${state.jobs['350']==='approved'?'승인':'미검수'}</strong></div><div class="info-item"><span>촛불 전체 수량</span><strong>${state.candles['350']}개</strong></div><div class="info-item"><span>운영 상태</span><strong>정상</strong></div><div class="info-item"><span>미해결 차단</span><strong>${state.candles['350']>0?'촛불 회수 필요':'없음'}</strong></div></div>${state.candles['350']>0?`<div style="margin-top:12px">${button('촛불 1개 회수','recover-candle','danger',isLocked()?'disabled':'')}</div>`:`<div class="notice notice-success" style="margin:12px 0 0">${timeMinutes(state.time)>=timeMinutes('16:00')?'입실 시각 후 조건이 해소되어 예약상 투숙 중 전이를 한 번 기록했습니다.':'검수 승인·촛불 0·차단 없음으로 입실 준비가 완료됐습니다.'}</div>`}</section>`;
  3449 |         if (no==='332'&&state.conflict==='active') special=`<section class="card card-pad"><div class="section-head"><h3>레이트 체크아웃·청소 출입 충돌</h3>${statusBadge('즉시 조치','red','alert')}</div><p>11:00 자동 체크아웃 뒤 PIN이 조회되고 청소가 시작된 상태에서 체크아웃이 13:00으로 변경됐습니다. 단순 재잠금으로 해결할 수 없습니다.</p><div class="info-grid"><div class="info-item"><span>변경 전 / 후</span><strong>11:00 → 13:00</strong></div><div class="info-item"><span>PIN 조회</span><strong>11:06 · 김민지1</strong></div><div class="info-item"><span>수행 단계</span><strong>청소 중</strong></div><div class="info-item"><span>필요 항목</span><strong>조율 · 재계획 · PIN 교체</strong></div></div><div style="margin-top:12px">${button('영향 확인·충돌 해결','resolve-conflict','danger',isLocked()?'disabled':'')}</div></section>`;
  3450 |         if (no==='142') special=`<section class="card card-pad"><div class="section-head"><h3>현재 예약 · 연박 청소</h3>${statusBadge('예약상 투숙 중','neutral')}</div><p>연박 청소는 투숙객 요청이 있을 때만 만들며 예약 점유를 종료하거나 다음 예약 입실 준비로 사용하지 않습니다.</p>${state.stayoverCreated?`<div class="notice notice-success">연박 청소 배정 준비 작업이 관리자 내일 배정 목록에 추가됐습니다.</div>${button('오늘 운영 보기','go-today','outline')}`:button('연박 청소 생성','create-stayover','primary',isLocked()?'disabled':'')}</section>`;
  3451 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${no}호 · 데모`,type.name)+`<div class="detail-grid"><div class="detail-stack">${special}<section class="card card-pad"><h3>예약·일정</h3><div class="info-grid"><div class="info-item"><span>체크인 일시</span><strong>${room.checkin}</strong></div><div class="info-item"><span>체크아웃 일시</span><strong>${room.checkout}</strong></div><div class="info-item"><span>청소요금 · 8월 시트</span><strong>${money(type.rate)}</strong></div><div class="info-item"><span>예상시간 · 데모</span><strong>${type.minutes}분</strong></div></div>${no==='211'?`<div class="notice notice-info" style="margin:12px 0 0"><strong>고객 이름</strong>&nbsp; 홍길동 (데모) · 관리자 예약 상세에서만 표시</div>`:''}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>객실 사건 타임라인</h3>${renderTimeline(no)}</section><section class="card card-pad"><h3>객실 PIN</h3><p class="cell-sub">목록·알림·영속 저장소에는 원문을 두지 않습니다.</p><div class="pin-box"><span class="pin-value">••••</span>${button('변경 이력','demo-info','outline')}</div></section></aside></div>`;
```

### occurrence 6 · line 3423

```html
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
  3425 |       }
  3426 | 
  3427 |       function renderMaidMore() {
  3428 |         return `<div class="settings-grid">${settingCard('user','내 정보','김민지1 · 데모 · 휴대폰 •••• 4821',button('정보 보기','demo-info','outline'))}${settingCard('bell','알림 권한',state.notificationsEnabled?'허용 · 앱 내부 알림 사용':'요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}${settingCard('lock','로그인 비밀번호','개인 숫자 6자리 이상 · 객실 PIN과 분리',button('변경 데모','demo-info','outline'))}</div>`;
  3429 |       }
  3430 | 
  3431 |       function renderDetail() {
  3432 |         if(!state.detail||!detailAllowedForRole(state.detail.type,state.role)){state.detail=null;return renderMain();}
  3433 |         if (state.detail.type==='templates') return renderTemplateList();
  3434 |         if (state.detail.type==='template') return renderTemplateDetail(state.detail.id,state.detail.mode||'view');
  3435 |         if (state.detail.type==='room') return renderRoomDetail(state.detail.id);
  3436 |         if (state.detail.type==='cleaning') return renderCleaningDetail(state.detail.id);
  3437 |         if (state.detail.type==='maid') return renderMaidDetail(state.detail.id);
  3438 |         if (state.detail.type==='complaint') return renderComplaintDetail();
  3439 |         if (state.detail.type==='pay') return renderPayDetail();
  3440 |         return '';
  3441 |       }
  3442 | 
  3443 |       function detailHeader(title,subtitle='') { return `<div class="detail-head"><button class="btn btn-ghost" type="button" data-action="back">${icon('chevronLeft','icon-sm')}목록</button><div class="detail-title"><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div></div>`; }
  3444 | 
  3445 |       function renderRoomDetailLegacy(no) {
  3446 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room.type], p=roomPresentation(no);
  3447 |         let special='';
  3448 |         if (no==='350') special=`<section class="card card-pad"><div class="section-head"><h3>입실 준비 조건</h3>${statusBadge(p.status,p.tone)}</div><div class="info-grid"><div class="info-item"><span>청소 검수</span><strong>${state.jobs['350']==='approved'?'승인':'미검수'}</strong></div><div class="info-item"><span>촛불 전체 수량</span><strong>${state.candles['350']}개</strong></div><div class="info-item"><span>운영 상태</span><strong>정상</strong></div><div class="info-item"><span>미해결 차단</span><strong>${state.candles['350']>0?'촛불 회수 필요':'없음'}</strong></div></div>${state.candles['350']>0?`<div style="margin-top:12px">${button('촛불 1개 회수','recover-candle','danger',isLocked()?'disabled':'')}</div>`:`<div class="notice notice-success" style="margin:12px 0 0">${timeMinutes(state.time)>=timeMinutes('16:00')?'입실 시각 후 조건이 해소되어 예약상 투숙 중 전이를 한 번 기록했습니다.':'검수 승인·촛불 0·차단 없음으로 입실 준비가 완료됐습니다.'}</div>`}</section>`;
  3449 |         if (no==='332'&&state.conflict==='active') special=`<section class="card card-pad"><div class="section-head"><h3>레이트 체크아웃·청소 출입 충돌</h3>${statusBadge('즉시 조치','red','alert')}</div><p>11:00 자동 체크아웃 뒤 PIN이 조회되고 청소가 시작된 상태에서 체크아웃이 13:00으로 변경됐습니다. 단순 재잠금으로 해결할 수 없습니다.</p><div class="info-grid"><div class="info-item"><span>변경 전 / 후</span><strong>11:00 → 13:00</strong></div><div class="info-item"><span>PIN 조회</span><strong>11:06 · 김민지1</strong></div><div class="info-item"><span>수행 단계</span><strong>청소 중</strong></div><div class="info-item"><span>필요 항목</span><strong>조율 · 재계획 · PIN 교체</strong></div></div><div style="margin-top:12px">${button('영향 확인·충돌 해결','resolve-conflict','danger',isLocked()?'disabled':'')}</div></section>`;
  3450 |         if (no==='142') special=`<section class="card card-pad"><div class="section-head"><h3>현재 예약 · 연박 청소</h3>${statusBadge('예약상 투숙 중','neutral')}</div><p>연박 청소는 투숙객 요청이 있을 때만 만들며 예약 점유를 종료하거나 다음 예약 입실 준비로 사용하지 않습니다.</p>${state.stayoverCreated?`<div class="notice notice-success">연박 청소 배정 준비 작업이 관리자 내일 배정 목록에 추가됐습니다.</div>${button('오늘 운영 보기','go-today','outline')}`:button('연박 청소 생성','create-stayover','primary',isLocked()?'disabled':'')}</section>`;
  3451 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${no}호 · 데모`,type.name)+`<div class="detail-grid"><div class="detail-stack">${special}<section class="card card-pad"><h3>예약·일정</h3><div class="info-grid"><div class="info-item"><span>체크인 일시</span><strong>${room.checkin}</strong></div><div class="info-item"><span>체크아웃 일시</span><strong>${room.checkout}</strong></div><div class="info-item"><span>청소요금 · 8월 시트</span><strong>${money(type.rate)}</strong></div><div class="info-item"><span>예상시간 · 데모</span><strong>${type.minutes}분</strong></div></div>${no==='211'?`<div class="notice notice-info" style="margin:12px 0 0"><strong>고객 이름</strong>&nbsp; 홍길동 (데모) · 관리자 예약 상세에서만 표시</div>`:''}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>객실 사건 타임라인</h3>${renderTimeline(no)}</section><section class="card card-pad"><h3>객실 PIN</h3><p class="cell-sub">목록·알림·영속 저장소에는 원문을 두지 않습니다.</p><div class="pin-box"><span class="pin-value">••••</span>${button('변경 이력','demo-info','outline')}</div></section></aside></div>`;
  3452 |       }
  3453 | 
  3454 |       function renderTimeline(no) {
  3455 |         const base=[{title:`${no}호 상태 조회`,time:state.time,detail:'현재 상태 확인'},{title:'예약 일정 확인',time:'09:10',detail:'외부 예약은 별도 확인'},{title:'청소 일정 확인',time:'09:12',detail:'담당·수행·제출 내용 확인'}];
  3456 |         const scoped=state.events.filter(event=>event.roomId===no).slice(0,4);
  3457 |         return `<ol class="timeline">${[...scoped,...base].map(e=>`<li><strong>${esc(e.title)}</strong><span>${esc(e.time)} · ${esc(e.detail)}</span></li>`).join('')}</ol>`;
```

### occurrence 7 · line 3427

```html
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
  3425 |       }
  3426 | 
  3427 |       function renderMaidMore() {
  3428 |         return `<div class="settings-grid">${settingCard('user','내 정보','김민지1 · 데모 · 휴대폰 •••• 4821',button('정보 보기','demo-info','outline'))}${settingCard('bell','알림 권한',state.notificationsEnabled?'허용 · 앱 내부 알림 사용':'요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}${settingCard('lock','로그인 비밀번호','개인 숫자 6자리 이상 · 객실 PIN과 분리',button('변경 데모','demo-info','outline'))}</div>`;
  3429 |       }
  3430 | 
  3431 |       function renderDetail() {
  3432 |         if(!state.detail||!detailAllowedForRole(state.detail.type,state.role)){state.detail=null;return renderMain();}
  3433 |         if (state.detail.type==='templates') return renderTemplateList();
  3434 |         if (state.detail.type==='template') return renderTemplateDetail(state.detail.id,state.detail.mode||'view');
  3435 |         if (state.detail.type==='room') return renderRoomDetail(state.detail.id);
  3436 |         if (state.detail.type==='cleaning') return renderCleaningDetail(state.detail.id);
  3437 |         if (state.detail.type==='maid') return renderMaidDetail(state.detail.id);
  3438 |         if (state.detail.type==='complaint') return renderComplaintDetail();
  3439 |         if (state.detail.type==='pay') return renderPayDetail();
  3440 |         return '';
  3441 |       }
  3442 | 
  3443 |       function detailHeader(title,subtitle='') { return `<div class="detail-head"><button class="btn btn-ghost" type="button" data-action="back">${icon('chevronLeft','icon-sm')}목록</button><div class="detail-title"><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div></div>`; }
  3444 | 
  3445 |       function renderRoomDetailLegacy(no) {
  3446 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room.type], p=roomPresentation(no);
  3447 |         let special='';
  3448 |         if (no==='350') special=`<section class="card card-pad"><div class="section-head"><h3>입실 준비 조건</h3>${statusBadge(p.status,p.tone)}</div><div class="info-grid"><div class="info-item"><span>청소 검수</span><strong>${state.jobs['350']==='approved'?'승인':'미검수'}</strong></div><div class="info-item"><span>촛불 전체 수량</span><strong>${state.candles['350']}개</strong></div><div class="info-item"><span>운영 상태</span><strong>정상</strong></div><div class="info-item"><span>미해결 차단</span><strong>${state.candles['350']>0?'촛불 회수 필요':'없음'}</strong></div></div>${state.candles['350']>0?`<div style="margin-top:12px">${button('촛불 1개 회수','recover-candle','danger',isLocked()?'disabled':'')}</div>`:`<div class="notice notice-success" style="margin:12px 0 0">${timeMinutes(state.time)>=timeMinutes('16:00')?'입실 시각 후 조건이 해소되어 예약상 투숙 중 전이를 한 번 기록했습니다.':'검수 승인·촛불 0·차단 없음으로 입실 준비가 완료됐습니다.'}</div>`}</section>`;
  3449 |         if (no==='332'&&state.conflict==='active') special=`<section class="card card-pad"><div class="section-head"><h3>레이트 체크아웃·청소 출입 충돌</h3>${statusBadge('즉시 조치','red','alert')}</div><p>11:00 자동 체크아웃 뒤 PIN이 조회되고 청소가 시작된 상태에서 체크아웃이 13:00으로 변경됐습니다. 단순 재잠금으로 해결할 수 없습니다.</p><div class="info-grid"><div class="info-item"><span>변경 전 / 후</span><strong>11:00 → 13:00</strong></div><div class="info-item"><span>PIN 조회</span><strong>11:06 · 김민지1</strong></div><div class="info-item"><span>수행 단계</span><strong>청소 중</strong></div><div class="info-item"><span>필요 항목</span><strong>조율 · 재계획 · PIN 교체</strong></div></div><div style="margin-top:12px">${button('영향 확인·충돌 해결','resolve-conflict','danger',isLocked()?'disabled':'')}</div></section>`;
  3450 |         if (no==='142') special=`<section class="card card-pad"><div class="section-head"><h3>현재 예약 · 연박 청소</h3>${statusBadge('예약상 투숙 중','neutral')}</div><p>연박 청소는 투숙객 요청이 있을 때만 만들며 예약 점유를 종료하거나 다음 예약 입실 준비로 사용하지 않습니다.</p>${state.stayoverCreated?`<div class="notice notice-success">연박 청소 배정 준비 작업이 관리자 내일 배정 목록에 추가됐습니다.</div>${button('오늘 운영 보기','go-today','outline')}`:button('연박 청소 생성','create-stayover','primary',isLocked()?'disabled':'')}</section>`;
  3451 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${no}호 · 데모`,type.name)+`<div class="detail-grid"><div class="detail-stack">${special}<section class="card card-pad"><h3>예약·일정</h3><div class="info-grid"><div class="info-item"><span>체크인 일시</span><strong>${room.checkin}</strong></div><div class="info-item"><span>체크아웃 일시</span><strong>${room.checkout}</strong></div><div class="info-item"><span>청소요금 · 8월 시트</span><strong>${money(type.rate)}</strong></div><div class="info-item"><span>예상시간 · 데모</span><strong>${type.minutes}분</strong></div></div>${no==='211'?`<div class="notice notice-info" style="margin:12px 0 0"><strong>고객 이름</strong>&nbsp; 홍길동 (데모) · 관리자 예약 상세에서만 표시</div>`:''}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>객실 사건 타임라인</h3>${renderTimeline(no)}</section><section class="card card-pad"><h3>객실 PIN</h3><p class="cell-sub">목록·알림·영속 저장소에는 원문을 두지 않습니다.</p><div class="pin-box"><span class="pin-value">••••</span>${button('변경 이력','demo-info','outline')}</div></section></aside></div>`;
  3452 |       }
  3453 | 
  3454 |       function renderTimeline(no) {
  3455 |         const base=[{title:`${no}호 상태 조회`,time:state.time,detail:'현재 상태 확인'},{title:'예약 일정 확인',time:'09:10',detail:'외부 예약은 별도 확인'},{title:'청소 일정 확인',time:'09:12',detail:'담당·수행·제출 내용 확인'}];
  3456 |         const scoped=state.events.filter(event=>event.roomId===no).slice(0,4);
  3457 |         return `<ol class="timeline">${[...scoped,...base].map(e=>`<li><strong>${esc(e.title)}</strong><span>${esc(e.time)} · ${esc(e.detail)}</span></li>`).join('')}</ol>`;
  3458 |       }
  3459 | 
  3460 |       function renderCleaningDetail(no) {
  3461 |         const baseRoom=ROOMS.find(r=>r.no===no)||ROOMS[0], room=no==='332'&&state.conflict==='resolved'?{...baseRoom,checkout:state.conflictRecord.afterCheckout}:baseRoom, type=ROOM_TYPES[room.type], job=state.jobs[no]||'claimed';
```

### occurrence 8 · line 3601

```html
  3585 |         const status=state.inspection.status;
  3586 |         return renderCoach()+detailHeader(`${no}호 전체 제출 검수`,'구역별 청소 사진 전체를 확인합니다.')+`<section class="card card-pad"><div class="section-head"><h3>구역별 청소 사진</h3>${statusBadge(status==='approved'?'승인 완료':'검수 요청됨',status==='approved'?'green':'amber')}</div></section>`;
  3587 |       }
  3588 | 
  3589 |       function maidById(id) { return MAIDS.find(m=>m.id===id); }
  3590 |       function maidDeactivationLabel(maidId) {
  3591 |         const status=maidStatusFor(maidId);
  3592 |         if(status==='deactivating')return '비활성 처리 중';
  3593 |         if(status==='inactive')return '비활성';
  3594 |         return '활성';
  3595 |       }
  3596 |       function maidDeactivationBlockers(maidId) {
  3597 |         const pending=pendingInspectionForMaid(maidId),future=notifiedAssignmentEntriesForMaid(maidId),reclean=unresolvedRecleanForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId),unfinished=unfinishedCurrentAttemptsForMaid(maidId);
  3598 |         const messages=[future.length?`다음 근무일 통보 ${future.length}건 재배정 필요`:'',pending?`${pending.room}호 검수 결정 필요`:'',reclean?`${reclean.room}호 본인 무급 재청소 완료 필요`:'',conflict?`${conflict.room}호 출입 충돌 종결 필요`:'',unfinished.length?`미종결 수행 회차 ${unfinished.map(item=>item.room+'호').join('·')} 정리 필요`:''].filter(Boolean);
  3599 |         return {pending,future,reclean,conflict,unfinished,messages};
  3600 |       }
  3601 |       function renderMaidDeactivationGate(maidId) {
  3602 |         const maid=maidById(maidId),flow=maidDeactivationFor(maidId),blockers=maidDeactivationBlockers(maidId),allDone=Object.values(flow.gates).every(Boolean),locked=isLocked();
  3603 |         if(maidStatusFor(maidId)!=='deactivating')return '';
  3604 |         const choice=flow.choice==='stop'?'즉시 중단·인계':'현재 작업 마무리 후 비활성';
  3605 |         return `<div class="maid-deactivation-gate" data-maid-deactivation-gate="${maidId}">${blockers.messages.length?`<div class="notice notice-warning" style="margin-top:12px"><div><strong>완료 전 필수 조치</strong><br>${esc(blockers.messages.join(' · '))}</div></div>`:''}<div class="choice-list" style="margin-top:12px"><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="assignments" ${flow.gates.assignments?'checked':''} ${locked?'disabled':''}><span><strong>담당 정리 완료</strong><span>통보된 미래 담당을 다른 활성 메이드에게 변경 통보 · ${flow.choice==='stop'?'진행 작업 인계자 확정':'현재 작업 외 신규 담당 없음'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="round" ${flow.gates.round?'checked':''} ${locked?'disabled':''}><span><strong>수행 회차·검수 종결</strong><span>${flow.choice==='stop'?'현재 회차를 중단으로 보존하고 새 담당 회차 생성':'현재 회차 제출 뒤 관리자 검수 결정까지 완료'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="lease" ${flow.gates.lease?'checked':''} ${locked?'disabled':''}><span><strong>PIN lease 종료</strong><span>조회 이력은 보존하고 ${esc(maid?.name||maidId)}의 활성 lease만 종료</span></span></label></div><div style="margin-top:12px">${button('비활성 완료','complete-deactivation-v2','danger',`${!allDone||locked||blockers.messages.length?'disabled ':''}data-id="${maidId}"`)}</div><p class="audit-note" style="margin:10px 0 0">선택 방식: ${esc(choice)} · 담당·수행 회차·검수·PIN을 모두 닫은 뒤에만 완료됩니다.</p></div>`;
  3606 |       }
  3607 |       function renderMaidAccountManagement(maidId) {
  3608 |         const maid=maidById(maidId),status=maidStatusFor(maidId),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(maidId);
  3609 |         const content=status==='active'?`${button('영향 확인·비활성 처리','deactivate-maid-v2','danger',`${isLocked()?'disabled ':''}data-id="${maidId}"`)}`:processing?`<div class="notice notice-danger" style="margin:0"><div><strong>신규 권한 잠금 적용 중</strong><br>${esc(maid?.name||maidId)}의 신규 업무 확인·직접 배정·새 PIN lease 발급이 차단됐습니다.</div></div>${renderMaidDeactivationGate(maidId)}`:`<div class="notice notice-success" style="margin:0"><div><strong>비활성 완료</strong><br>로그인과 신규 업무·PIN 접근은 종료됐고 과거 수행·검수·주급 자료는 그대로 보존됩니다.${flow.completedAt?` · 완료 ${esc(flow.completedAt)}`:''}</div></div>`;
  3610 |         return `<section class="card card-pad maid-account-management" data-maid-account-management="${maidId}"><div class="section-head"><div><h3>계정 관리</h3><span class="meta">위험 작업 · 상세 화면 마지막 영역</span></div>${statusBadge(maidDeactivationLabel(maidId),status==='active'?'green':processing?'amber':'neutral')}</div><p class="audit-note">비활성 처리는 계정만 닫습니다. 담당 구간·수행 회차·PIN lease는 종결 이벤트를 남기고 과거 이력·검수·수익은 삭제하지 않습니다.</p><div style="margin-top:12px">${content}</div></section>`;
  3611 |       }
  3612 |       function renderMaidDetail(id) {
  3613 |         const m=maidById(id)||MAIDS[0],status=maidStatusFor(m.id),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(m.id),currentApproved=maidPayAmount(m.name),submissions=validatedSubmissions().filter(submission=>submission.performerId===m.id).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))),assignments=ROOMS.filter(room=>room.assignee===m.name),currentAttempts=unfinishedCurrentAttemptsForMaid(m.id),currentRooms=new Set(currentAttempts.map(item=>item.room)),complaintCount=(state.complaints||[]).filter(item=>!item.deleted&&item.maid===m.name).length;
  3614 |         const submissionHistoryRows=submissions.map(submission=>{
  3615 |           const record=earningRecordForSubmission(submission),report=bombRoomReportForSubmission(submission),fee=bombRoomBreakdown(submission.room,{reportOverride:report,baseOverride:submission.baseRateSnapshot}),wholeRejected=submission.status==='rejected',decision=report?.status==='approved'?'폭탄방 승인':report?.status==='rejected'?'폭탄방 미인정':report?.status==='pending'?'폭탄방 검수 대기':'폭탄방 신고 없음';
  3616 |           const submissionStatus=wholeRejected?`전체 반려 · ${decision} 결정 보존 · 적립 0원`:submission.kind==='재청소'?(submission.status==='approved'?'재청소 승인 · 무급 0원':'재청소 검수 대기 · 무급 0원'):record?`${money(record.total)} 확정`:report?.status==='pending'?'폭탄방 검수 대기':submission.status==='approved'?'전체 승인 · 원장 확인':'전체 검수 대기',breakdown=wholeRejected&&report?`기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 실제 적립 0원`:'',evidence=report?.photos?.[0]?button('증빙 보기','bomb-room-photo','outline',`data-room="${submission.room}" data-report="${report.id}" data-photo="${report.photos[0].id}"`):'';
  3617 |           return `<div class="rail-row"><strong>${submission.room}호 · ${esc(submission.kind||'퇴실 청소')} · ${esc(submission.submittedAt)}</strong><span>${esc(submissionStatus)} · 제출 ${esc(submission.id.split('-').slice(-2).join('-'))}${breakdown?` · ${esc(breakdown)}`:''}${evidence}</span></div>`;
  3618 |         });
  3619 |         const currentAttemptRows=currentAttempts.map(({room,attempt})=>`<div class="rail-row"><strong>${room}호 · ${esc(attempt?.kind||'청소')} · 현재 수행 회차</strong><span>${esc(cleaningLabel(state.jobs[room]))} · ${esc(attempt?.id||'회차 정보 없음')}</span></div>`),assignmentRows=assignments.filter(room=>!currentRooms.has(room.no)).map(room=>`<div class="rail-row"><strong>${room.no}호 · 현재 담당</strong><span>${esc(cleaningLabel(state.jobs[room.no]))} · 담당 선택 권한 없음</span></div>`),historyRows=[...currentAttemptRows,...assignmentRows,...submissionHistoryRows],unstartedCount=currentAttempts.filter(({room})=>['scheduled','claimed','unassigned'].includes(state.jobs[room])).length,progressCount=currentAttempts.filter(({room})=>state.jobs[room]==='cleaning').length,uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=submissions.filter(submission=>submission.status==='pending').length,futureCount=notifiedAssignmentEntriesForMaid(m.id).length,pinLeaseCount=activeCleaningFor(m.id)?1:0,stateTone=status==='active'?'green':processing?'amber':'neutral';
  3620 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${m.name} · 데모`,`불변 사용자 ID 기준 · 모든 메이드에 동일한 계정 관리·이력 보존 규칙 적용`)+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>계정·근무 상태</h3>${statusBadge(maidDeactivationLabel(m.id),stateTone)}</div><div class="info-grid"><div class="info-item"><span>로그인 아이디</span><strong>${esc(m.name)}</strong></div><div class="info-item"><span>휴대폰</span><strong>${esc(m.phone)}</strong></div><div class="info-item"><span>객실 선택 권한</span><strong>없음 · 관리자 전용</strong></div><div class="info-item"><span>배정 업무·PIN</span><strong>${status==='active'?'확인 가능':'잠금'}</strong></div></div></section><section class="card card-pad"><div class="section-head"><h3>업무 영향 요약</h3>${statusBadge(inactive?'정리 완료':'실시간 집계','neutral')}</div><div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${futureCount}건 · ${inactive?'정리 완료':'변경 통보 필요'}</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${unstartedCount+progressCount}건 · ${processing?(flow.choice==='stop'?'인계 필요':'마무리 허용'):inactive?'회차 종결':'처리 방식 선택'}</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · ${uploadCount?'제출 필요':'없음'}</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · ${pendingCount?'관리자 결정 필요':'없음'}</strong></div><div class="info-item"><span>미지급 수익</span><strong>${money(currentApproved)} · 지급 이력 보존</strong></div><div class="info-item"><span>활성 PIN lease</span><strong>${inactive?'0건 · 종료':`${pinLeaseCount}건 · ${processing?'종료 필요':'현재 기준'}`}</strong></div></div></section><section class="card card-pad" data-maid-history="${m.id}"><div class="section-head"><h3>담당·실제 수행 이력</h3><select class="select-control" aria-label="이력 기간"><option>7일</option><option>30일</option></select></div><div class="rail-list">${historyRows.join('')||'<div class="rail-row"><strong>저장된 담당·수행 이력 없음</strong><span>데모 fixture 기준</span></div>'}${m.id==='m1'?'<div class="rail-row"><strong>536호 · 폭탄방 승인 수익 · 과거 데모</strong><span>기본 20,000원 + 해당 객실 추가 20,000원 = 40,000원</span></div>':''}</div></section>${renderMaidAccountManagement(m.id)}</div><aside class="detail-stack"><section class="card card-pad"><h3>평가·컴플레인</h3><p class="cell-sub">등록 ${complaintCount}건 · 주급 자동 차감 없음</p>${complaintCount?button('컴플레인 상세','complaint-detail','outline'):''}</section><section class="card card-pad"><h3>주급</h3><p><strong>이번 주 승인 확정 ${money(currentApproved)}</strong></p><p class="audit-note">다른 메이드의 객실·사진·수익은 이 상세에 섞이지 않습니다.</p>${button('지급 이력','pay-detail','outline')}</section></aside></div>`;
  3621 |       }
  3622 | 
  3623 |       function renderComplaintDetail() {
  3624 |         const c=state.complaint;
  3625 |         return renderCoach()+detailHeader('컴플레인 C-014 · 데모','332호 청소 연결 · 벌점은 주급을 자동 차감하지 않음')+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>판정 상태</h3>${statusBadge(complaintLabel(c),c==='closed'?'green':c==='objected'?'red':'amber')}</div><div class="info-grid"><div class="info-item"><span>분류</span><strong>청소 미흡</strong></div><div class="info-item"><span>관련 작업</span><strong>332호 · CL-332-08</strong></div><div class="info-item"><span>접수일</span><strong>2026.08.14</strong></div><div class="info-item"><span>주급 영향</span><strong>자동 차감 없음</strong></div></div><div class="notice notice-warning" style="margin:14px 0">고객 개인정보를 제외한 가림 처리 운영 문구: 욕실 거울 얼룩이 남아 있었음.</div>${renderComplaintActions(c)}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>사건 타임라인</h3><ol class="timeline"><li><strong>접수</strong><span>09:20 · 관리자</span></li><li><strong>사실 확인</strong><span>10:10 · 증빙 검토</span></li><li style="opacity:${['ruled','acknowledged','objected','closed'].includes(c)?1:.45}"><strong>판정</strong><span>${['ruled','acknowledged','objected','closed'].includes(c)?'확인됨 · 평가 참고':'대기'}</span></li><li style="opacity:${['acknowledged','objected','closed'].includes(c)?1:.45}"><strong>메이드 응답</strong><span>${c==='objected'?'이의 메모':c==='acknowledged'?'내용 확인':'대기'}</span></li><li style="opacity:${c==='closed'?1:.45}"><strong>종결</strong><span>${c==='closed'?'원본 삭제 없이 이벤트 보존':'대기'}</span></li></ol></section></aside></div>`;
  3626 |       }
  3627 |       function complaintLabel(c){return ({received:'확인 중',ruled:'판정 완료 · 메이드 확인 대기',acknowledged:'메이드 확인',objected:'메이드 이의 · 재검토 필요',closed:'종결'})[c]||c;}
  3628 |       function renderComplaintActions(c) {
  3629 |         if (state.role==='admin'&&c==='received') return button('관리자 판정','rule-complaint','primary',isLocked()?'disabled':'');
  3630 |         if (state.role==='maid'&&c==='ruled') return `<div class="job-actions">${button('내용 확인','ack-complaint','outline')}${button('이의 메모','object-complaint','primary')}</div>`;
  3631 |         if (state.role==='admin'&&['acknowledged','objected'].includes(c)) return `<div class="job-actions">${button(c==='objected'?'판정 유지·종결':'종결','close-complaint','primary')}${c==='objected'?button('판정 정정','correct-complaint','outline'):''}</div>`;
  3632 |         if (c==='ruled') return `<div class="notice notice-info" style="margin:0">메이드 역할로 전환해 판정 확인 또는 이의를 진행하세요.</div>`;
  3633 |         return `<div class="notice notice-success" style="margin:0">원본과 모든 정정 이벤트를 보존한 채 종결됐습니다.</div>`;
  3634 |       }
  3635 | 
```

### occurrence 9 · line 3607

```html
  3591 |         const status=maidStatusFor(maidId);
  3592 |         if(status==='deactivating')return '비활성 처리 중';
  3593 |         if(status==='inactive')return '비활성';
  3594 |         return '활성';
  3595 |       }
  3596 |       function maidDeactivationBlockers(maidId) {
  3597 |         const pending=pendingInspectionForMaid(maidId),future=notifiedAssignmentEntriesForMaid(maidId),reclean=unresolvedRecleanForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId),unfinished=unfinishedCurrentAttemptsForMaid(maidId);
  3598 |         const messages=[future.length?`다음 근무일 통보 ${future.length}건 재배정 필요`:'',pending?`${pending.room}호 검수 결정 필요`:'',reclean?`${reclean.room}호 본인 무급 재청소 완료 필요`:'',conflict?`${conflict.room}호 출입 충돌 종결 필요`:'',unfinished.length?`미종결 수행 회차 ${unfinished.map(item=>item.room+'호').join('·')} 정리 필요`:''].filter(Boolean);
  3599 |         return {pending,future,reclean,conflict,unfinished,messages};
  3600 |       }
  3601 |       function renderMaidDeactivationGate(maidId) {
  3602 |         const maid=maidById(maidId),flow=maidDeactivationFor(maidId),blockers=maidDeactivationBlockers(maidId),allDone=Object.values(flow.gates).every(Boolean),locked=isLocked();
  3603 |         if(maidStatusFor(maidId)!=='deactivating')return '';
  3604 |         const choice=flow.choice==='stop'?'즉시 중단·인계':'현재 작업 마무리 후 비활성';
  3605 |         return `<div class="maid-deactivation-gate" data-maid-deactivation-gate="${maidId}">${blockers.messages.length?`<div class="notice notice-warning" style="margin-top:12px"><div><strong>완료 전 필수 조치</strong><br>${esc(blockers.messages.join(' · '))}</div></div>`:''}<div class="choice-list" style="margin-top:12px"><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="assignments" ${flow.gates.assignments?'checked':''} ${locked?'disabled':''}><span><strong>담당 정리 완료</strong><span>통보된 미래 담당을 다른 활성 메이드에게 변경 통보 · ${flow.choice==='stop'?'진행 작업 인계자 확정':'현재 작업 외 신규 담당 없음'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="round" ${flow.gates.round?'checked':''} ${locked?'disabled':''}><span><strong>수행 회차·검수 종결</strong><span>${flow.choice==='stop'?'현재 회차를 중단으로 보존하고 새 담당 회차 생성':'현재 회차 제출 뒤 관리자 검수 결정까지 완료'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="lease" ${flow.gates.lease?'checked':''} ${locked?'disabled':''}><span><strong>PIN lease 종료</strong><span>조회 이력은 보존하고 ${esc(maid?.name||maidId)}의 활성 lease만 종료</span></span></label></div><div style="margin-top:12px">${button('비활성 완료','complete-deactivation-v2','danger',`${!allDone||locked||blockers.messages.length?'disabled ':''}data-id="${maidId}"`)}</div><p class="audit-note" style="margin:10px 0 0">선택 방식: ${esc(choice)} · 담당·수행 회차·검수·PIN을 모두 닫은 뒤에만 완료됩니다.</p></div>`;
  3606 |       }
  3607 |       function renderMaidAccountManagement(maidId) {
  3608 |         const maid=maidById(maidId),status=maidStatusFor(maidId),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(maidId);
  3609 |         const content=status==='active'?`${button('영향 확인·비활성 처리','deactivate-maid-v2','danger',`${isLocked()?'disabled ':''}data-id="${maidId}"`)}`:processing?`<div class="notice notice-danger" style="margin:0"><div><strong>신규 권한 잠금 적용 중</strong><br>${esc(maid?.name||maidId)}의 신규 업무 확인·직접 배정·새 PIN lease 발급이 차단됐습니다.</div></div>${renderMaidDeactivationGate(maidId)}`:`<div class="notice notice-success" style="margin:0"><div><strong>비활성 완료</strong><br>로그인과 신규 업무·PIN 접근은 종료됐고 과거 수행·검수·주급 자료는 그대로 보존됩니다.${flow.completedAt?` · 완료 ${esc(flow.completedAt)}`:''}</div></div>`;
  3610 |         return `<section class="card card-pad maid-account-management" data-maid-account-management="${maidId}"><div class="section-head"><div><h3>계정 관리</h3><span class="meta">위험 작업 · 상세 화면 마지막 영역</span></div>${statusBadge(maidDeactivationLabel(maidId),status==='active'?'green':processing?'amber':'neutral')}</div><p class="audit-note">비활성 처리는 계정만 닫습니다. 담당 구간·수행 회차·PIN lease는 종결 이벤트를 남기고 과거 이력·검수·수익은 삭제하지 않습니다.</p><div style="margin-top:12px">${content}</div></section>`;
  3611 |       }
  3612 |       function renderMaidDetail(id) {
  3613 |         const m=maidById(id)||MAIDS[0],status=maidStatusFor(m.id),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(m.id),currentApproved=maidPayAmount(m.name),submissions=validatedSubmissions().filter(submission=>submission.performerId===m.id).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))),assignments=ROOMS.filter(room=>room.assignee===m.name),currentAttempts=unfinishedCurrentAttemptsForMaid(m.id),currentRooms=new Set(currentAttempts.map(item=>item.room)),complaintCount=(state.complaints||[]).filter(item=>!item.deleted&&item.maid===m.name).length;
  3614 |         const submissionHistoryRows=submissions.map(submission=>{
  3615 |           const record=earningRecordForSubmission(submission),report=bombRoomReportForSubmission(submission),fee=bombRoomBreakdown(submission.room,{reportOverride:report,baseOverride:submission.baseRateSnapshot}),wholeRejected=submission.status==='rejected',decision=report?.status==='approved'?'폭탄방 승인':report?.status==='rejected'?'폭탄방 미인정':report?.status==='pending'?'폭탄방 검수 대기':'폭탄방 신고 없음';
  3616 |           const submissionStatus=wholeRejected?`전체 반려 · ${decision} 결정 보존 · 적립 0원`:submission.kind==='재청소'?(submission.status==='approved'?'재청소 승인 · 무급 0원':'재청소 검수 대기 · 무급 0원'):record?`${money(record.total)} 확정`:report?.status==='pending'?'폭탄방 검수 대기':submission.status==='approved'?'전체 승인 · 원장 확인':'전체 검수 대기',breakdown=wholeRejected&&report?`기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 실제 적립 0원`:'',evidence=report?.photos?.[0]?button('증빙 보기','bomb-room-photo','outline',`data-room="${submission.room}" data-report="${report.id}" data-photo="${report.photos[0].id}"`):'';
  3617 |           return `<div class="rail-row"><strong>${submission.room}호 · ${esc(submission.kind||'퇴실 청소')} · ${esc(submission.submittedAt)}</strong><span>${esc(submissionStatus)} · 제출 ${esc(submission.id.split('-').slice(-2).join('-'))}${breakdown?` · ${esc(breakdown)}`:''}${evidence}</span></div>`;
  3618 |         });
  3619 |         const currentAttemptRows=currentAttempts.map(({room,attempt})=>`<div class="rail-row"><strong>${room}호 · ${esc(attempt?.kind||'청소')} · 현재 수행 회차</strong><span>${esc(cleaningLabel(state.jobs[room]))} · ${esc(attempt?.id||'회차 정보 없음')}</span></div>`),assignmentRows=assignments.filter(room=>!currentRooms.has(room.no)).map(room=>`<div class="rail-row"><strong>${room.no}호 · 현재 담당</strong><span>${esc(cleaningLabel(state.jobs[room.no]))} · 담당 선택 권한 없음</span></div>`),historyRows=[...currentAttemptRows,...assignmentRows,...submissionHistoryRows],unstartedCount=currentAttempts.filter(({room})=>['scheduled','claimed','unassigned'].includes(state.jobs[room])).length,progressCount=currentAttempts.filter(({room})=>state.jobs[room]==='cleaning').length,uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=submissions.filter(submission=>submission.status==='pending').length,futureCount=notifiedAssignmentEntriesForMaid(m.id).length,pinLeaseCount=activeCleaningFor(m.id)?1:0,stateTone=status==='active'?'green':processing?'amber':'neutral';
  3620 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${m.name} · 데모`,`불변 사용자 ID 기준 · 모든 메이드에 동일한 계정 관리·이력 보존 규칙 적용`)+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>계정·근무 상태</h3>${statusBadge(maidDeactivationLabel(m.id),stateTone)}</div><div class="info-grid"><div class="info-item"><span>로그인 아이디</span><strong>${esc(m.name)}</strong></div><div class="info-item"><span>휴대폰</span><strong>${esc(m.phone)}</strong></div><div class="info-item"><span>객실 선택 권한</span><strong>없음 · 관리자 전용</strong></div><div class="info-item"><span>배정 업무·PIN</span><strong>${status==='active'?'확인 가능':'잠금'}</strong></div></div></section><section class="card card-pad"><div class="section-head"><h3>업무 영향 요약</h3>${statusBadge(inactive?'정리 완료':'실시간 집계','neutral')}</div><div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${futureCount}건 · ${inactive?'정리 완료':'변경 통보 필요'}</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${unstartedCount+progressCount}건 · ${processing?(flow.choice==='stop'?'인계 필요':'마무리 허용'):inactive?'회차 종결':'처리 방식 선택'}</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · ${uploadCount?'제출 필요':'없음'}</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · ${pendingCount?'관리자 결정 필요':'없음'}</strong></div><div class="info-item"><span>미지급 수익</span><strong>${money(currentApproved)} · 지급 이력 보존</strong></div><div class="info-item"><span>활성 PIN lease</span><strong>${inactive?'0건 · 종료':`${pinLeaseCount}건 · ${processing?'종료 필요':'현재 기준'}`}</strong></div></div></section><section class="card card-pad" data-maid-history="${m.id}"><div class="section-head"><h3>담당·실제 수행 이력</h3><select class="select-control" aria-label="이력 기간"><option>7일</option><option>30일</option></select></div><div class="rail-list">${historyRows.join('')||'<div class="rail-row"><strong>저장된 담당·수행 이력 없음</strong><span>데모 fixture 기준</span></div>'}${m.id==='m1'?'<div class="rail-row"><strong>536호 · 폭탄방 승인 수익 · 과거 데모</strong><span>기본 20,000원 + 해당 객실 추가 20,000원 = 40,000원</span></div>':''}</div></section>${renderMaidAccountManagement(m.id)}</div><aside class="detail-stack"><section class="card card-pad"><h3>평가·컴플레인</h3><p class="cell-sub">등록 ${complaintCount}건 · 주급 자동 차감 없음</p>${complaintCount?button('컴플레인 상세','complaint-detail','outline'):''}</section><section class="card card-pad"><h3>주급</h3><p><strong>이번 주 승인 확정 ${money(currentApproved)}</strong></p><p class="audit-note">다른 메이드의 객실·사진·수익은 이 상세에 섞이지 않습니다.</p>${button('지급 이력','pay-detail','outline')}</section></aside></div>`;
  3621 |       }
  3622 | 
  3623 |       function renderComplaintDetail() {
  3624 |         const c=state.complaint;
  3625 |         return renderCoach()+detailHeader('컴플레인 C-014 · 데모','332호 청소 연결 · 벌점은 주급을 자동 차감하지 않음')+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>판정 상태</h3>${statusBadge(complaintLabel(c),c==='closed'?'green':c==='objected'?'red':'amber')}</div><div class="info-grid"><div class="info-item"><span>분류</span><strong>청소 미흡</strong></div><div class="info-item"><span>관련 작업</span><strong>332호 · CL-332-08</strong></div><div class="info-item"><span>접수일</span><strong>2026.08.14</strong></div><div class="info-item"><span>주급 영향</span><strong>자동 차감 없음</strong></div></div><div class="notice notice-warning" style="margin:14px 0">고객 개인정보를 제외한 가림 처리 운영 문구: 욕실 거울 얼룩이 남아 있었음.</div>${renderComplaintActions(c)}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>사건 타임라인</h3><ol class="timeline"><li><strong>접수</strong><span>09:20 · 관리자</span></li><li><strong>사실 확인</strong><span>10:10 · 증빙 검토</span></li><li style="opacity:${['ruled','acknowledged','objected','closed'].includes(c)?1:.45}"><strong>판정</strong><span>${['ruled','acknowledged','objected','closed'].includes(c)?'확인됨 · 평가 참고':'대기'}</span></li><li style="opacity:${['acknowledged','objected','closed'].includes(c)?1:.45}"><strong>메이드 응답</strong><span>${c==='objected'?'이의 메모':c==='acknowledged'?'내용 확인':'대기'}</span></li><li style="opacity:${c==='closed'?1:.45}"><strong>종결</strong><span>${c==='closed'?'원본 삭제 없이 이벤트 보존':'대기'}</span></li></ol></section></aside></div>`;
  3626 |       }
  3627 |       function complaintLabel(c){return ({received:'확인 중',ruled:'판정 완료 · 메이드 확인 대기',acknowledged:'메이드 확인',objected:'메이드 이의 · 재검토 필요',closed:'종결'})[c]||c;}
  3628 |       function renderComplaintActions(c) {
  3629 |         if (state.role==='admin'&&c==='received') return button('관리자 판정','rule-complaint','primary',isLocked()?'disabled':'');
  3630 |         if (state.role==='maid'&&c==='ruled') return `<div class="job-actions">${button('내용 확인','ack-complaint','outline')}${button('이의 메모','object-complaint','primary')}</div>`;
  3631 |         if (state.role==='admin'&&['acknowledged','objected'].includes(c)) return `<div class="job-actions">${button(c==='objected'?'판정 유지·종결':'종결','close-complaint','primary')}${c==='objected'?button('판정 정정','correct-complaint','outline'):''}</div>`;
  3632 |         if (c==='ruled') return `<div class="notice notice-info" style="margin:0">메이드 역할로 전환해 판정 확인 또는 이의를 진행하세요.</div>`;
  3633 |         return `<div class="notice notice-success" style="margin:0">원본과 모든 정정 이벤트를 보존한 채 종결됐습니다.</div>`;
  3634 |       }
  3635 | 
  3636 |       function renderPayDetail() {
  3637 |         const paidAmount=maidPayAmount('김민지1','2026-08-03'),paymentStatus=paymentStatusFor('2026-08-03','m1');
  3638 |         return renderCoach()+renderNetworkNotice()+detailHeader('김민지1 × 8월 3일–9일 지급','메이드별 지난주 전액 · 부분 지급 없음 · 실제 송금은 앱 밖에서')+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>지급 상태</h3>${statusBadge(payLabel(paymentStatus),paymentStatus==='PAID'?'green':paymentStatus==='PAYING'||paymentStatus==='CHECK'?'amber':'neutral')}</div><div class="info-grid"><div class="info-item"><span>지급 대상</span><strong>${money(paidAmount)} · 데모</strong></div><div class="info-item"><span>포함 수익</span><strong>승인 청소 6건</strong></div><div class="info-item"><span>지급 주차</span><strong>8/3(월)–8/9(일)</strong></div><div class="info-item"><span>외부 송금</span><strong>${paymentStatus==='PAID'?'완료 기록':'앱에서 실행 안 함'}</strong></div></div>${renderPayActions()}</section><section class="card card-pad"><h3>수익 원장 · 데모</h3><div class="rail-list"><div class="rail-row"><strong>536호 · 폭탄방 승인 · ×2</strong><span>기본 20,000원 + 추가 20,000원 = 40,000원</span></div><div class="rail-row"><strong>350호 · 승인</strong><span>16,000원</span></div><div class="rail-row"><strong>142호 · 연박 승인</strong><span>30,000원</span></div></div><p class="audit-note">폭탄방 배율은 536호에만 적용됐으며 이 주차의 다른 객실 금액은 변하지 않았습니다.</p></section></div><aside class="detail-stack"><section class="card card-pad"><h3>상태 전이</h3><ol class="timeline"><li><strong>OPEN</strong><span>늦은 승인·정정 반영 가능</span></li><li style="opacity:${paymentStatus!=='OPEN'?1:.45}"><strong>PAYING</strong><span>금액·수익 ID·관리자 잠금</span></li><li style="opacity:${paymentStatus==='PAID'?1:.45}"><strong>PAID</strong><span>외부 전액 송금 후 기록</span></li></ol></section></aside></div>`;
  3639 |       }
  3640 |       function payLabel(s){ return s==='CHECK'?'정산 확인 필요':s; }
  3641 |       function renderPayActions(){const paidAmount=maidPayAmount('김민지1','2026-08-03'),paymentStatus=paymentStatusFor('2026-08-03','m1');if(paymentStatus==='OPEN')return `<div style="margin-top:14px">${button('지급 진행 선점','start-payment','primary',isLocked()?'disabled':'')}</div>`;if(paymentStatus==='PAYING')return `<div class="notice notice-warning" style="margin:14px 0 10px">관리자 데모가 ${money(paidAmount)}을 선점했습니다. 외부 송금 뒤 결과를 기록하세요.</div><div class="job-actions">${button('기록 실패 · 확인 필요','payment-check','outline')}${button('외부 송금 완료 기록','finish-payment','success')}</div>`;if(paymentStatus==='CHECK')return `<div class="notice notice-danger" style="margin:14px 0 10px">자동 OPEN 복귀 금지. 송금 여부를 확인해야 합니다.</div><div class="job-actions">${button('송금하지 않음 · OPEN 복귀','payment-open','outline')}${button('송금 완료 재기록','finish-payment','success')}</div>`;return `<div class="notice notice-success" style="margin:14px 0 0">지급 완료 기록은 삭제하지 않으며 이후 차이는 다음 주 정정·상계로 이월합니다.</div>`;}
```

### occurrence 10 · line 3612

```html
  3596 |       function maidDeactivationBlockers(maidId) {
  3597 |         const pending=pendingInspectionForMaid(maidId),future=notifiedAssignmentEntriesForMaid(maidId),reclean=unresolvedRecleanForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId),unfinished=unfinishedCurrentAttemptsForMaid(maidId);
  3598 |         const messages=[future.length?`다음 근무일 통보 ${future.length}건 재배정 필요`:'',pending?`${pending.room}호 검수 결정 필요`:'',reclean?`${reclean.room}호 본인 무급 재청소 완료 필요`:'',conflict?`${conflict.room}호 출입 충돌 종결 필요`:'',unfinished.length?`미종결 수행 회차 ${unfinished.map(item=>item.room+'호').join('·')} 정리 필요`:''].filter(Boolean);
  3599 |         return {pending,future,reclean,conflict,unfinished,messages};
  3600 |       }
  3601 |       function renderMaidDeactivationGate(maidId) {
  3602 |         const maid=maidById(maidId),flow=maidDeactivationFor(maidId),blockers=maidDeactivationBlockers(maidId),allDone=Object.values(flow.gates).every(Boolean),locked=isLocked();
  3603 |         if(maidStatusFor(maidId)!=='deactivating')return '';
  3604 |         const choice=flow.choice==='stop'?'즉시 중단·인계':'현재 작업 마무리 후 비활성';
  3605 |         return `<div class="maid-deactivation-gate" data-maid-deactivation-gate="${maidId}">${blockers.messages.length?`<div class="notice notice-warning" style="margin-top:12px"><div><strong>완료 전 필수 조치</strong><br>${esc(blockers.messages.join(' · '))}</div></div>`:''}<div class="choice-list" style="margin-top:12px"><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="assignments" ${flow.gates.assignments?'checked':''} ${locked?'disabled':''}><span><strong>담당 정리 완료</strong><span>통보된 미래 담당을 다른 활성 메이드에게 변경 통보 · ${flow.choice==='stop'?'진행 작업 인계자 확정':'현재 작업 외 신규 담당 없음'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="round" ${flow.gates.round?'checked':''} ${locked?'disabled':''}><span><strong>수행 회차·검수 종결</strong><span>${flow.choice==='stop'?'현재 회차를 중단으로 보존하고 새 담당 회차 생성':'현재 회차 제출 뒤 관리자 검수 결정까지 완료'}</span></span></label><label class="choice"><input type="checkbox" data-control="maid-deactivation-gate" data-maid-id="${maidId}" value="lease" ${flow.gates.lease?'checked':''} ${locked?'disabled':''}><span><strong>PIN lease 종료</strong><span>조회 이력은 보존하고 ${esc(maid?.name||maidId)}의 활성 lease만 종료</span></span></label></div><div style="margin-top:12px">${button('비활성 완료','complete-deactivation-v2','danger',`${!allDone||locked||blockers.messages.length?'disabled ':''}data-id="${maidId}"`)}</div><p class="audit-note" style="margin:10px 0 0">선택 방식: ${esc(choice)} · 담당·수행 회차·검수·PIN을 모두 닫은 뒤에만 완료됩니다.</p></div>`;
  3606 |       }
  3607 |       function renderMaidAccountManagement(maidId) {
  3608 |         const maid=maidById(maidId),status=maidStatusFor(maidId),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(maidId);
  3609 |         const content=status==='active'?`${button('영향 확인·비활성 처리','deactivate-maid-v2','danger',`${isLocked()?'disabled ':''}data-id="${maidId}"`)}`:processing?`<div class="notice notice-danger" style="margin:0"><div><strong>신규 권한 잠금 적용 중</strong><br>${esc(maid?.name||maidId)}의 신규 업무 확인·직접 배정·새 PIN lease 발급이 차단됐습니다.</div></div>${renderMaidDeactivationGate(maidId)}`:`<div class="notice notice-success" style="margin:0"><div><strong>비활성 완료</strong><br>로그인과 신규 업무·PIN 접근은 종료됐고 과거 수행·검수·주급 자료는 그대로 보존됩니다.${flow.completedAt?` · 완료 ${esc(flow.completedAt)}`:''}</div></div>`;
  3610 |         return `<section class="card card-pad maid-account-management" data-maid-account-management="${maidId}"><div class="section-head"><div><h3>계정 관리</h3><span class="meta">위험 작업 · 상세 화면 마지막 영역</span></div>${statusBadge(maidDeactivationLabel(maidId),status==='active'?'green':processing?'amber':'neutral')}</div><p class="audit-note">비활성 처리는 계정만 닫습니다. 담당 구간·수행 회차·PIN lease는 종결 이벤트를 남기고 과거 이력·검수·수익은 삭제하지 않습니다.</p><div style="margin-top:12px">${content}</div></section>`;
  3611 |       }
  3612 |       function renderMaidDetail(id) {
  3613 |         const m=maidById(id)||MAIDS[0],status=maidStatusFor(m.id),processing=status==='deactivating',inactive=status==='inactive',flow=maidDeactivationFor(m.id),currentApproved=maidPayAmount(m.name),submissions=validatedSubmissions().filter(submission=>submission.performerId===m.id).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))),assignments=ROOMS.filter(room=>room.assignee===m.name),currentAttempts=unfinishedCurrentAttemptsForMaid(m.id),currentRooms=new Set(currentAttempts.map(item=>item.room)),complaintCount=(state.complaints||[]).filter(item=>!item.deleted&&item.maid===m.name).length;
  3614 |         const submissionHistoryRows=submissions.map(submission=>{
  3615 |           const record=earningRecordForSubmission(submission),report=bombRoomReportForSubmission(submission),fee=bombRoomBreakdown(submission.room,{reportOverride:report,baseOverride:submission.baseRateSnapshot}),wholeRejected=submission.status==='rejected',decision=report?.status==='approved'?'폭탄방 승인':report?.status==='rejected'?'폭탄방 미인정':report?.status==='pending'?'폭탄방 검수 대기':'폭탄방 신고 없음';
  3616 |           const submissionStatus=wholeRejected?`전체 반려 · ${decision} 결정 보존 · 적립 0원`:submission.kind==='재청소'?(submission.status==='approved'?'재청소 승인 · 무급 0원':'재청소 검수 대기 · 무급 0원'):record?`${money(record.total)} 확정`:report?.status==='pending'?'폭탄방 검수 대기':submission.status==='approved'?'전체 승인 · 원장 확인':'전체 검수 대기',breakdown=wholeRejected&&report?`기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 실제 적립 0원`:'',evidence=report?.photos?.[0]?button('증빙 보기','bomb-room-photo','outline',`data-room="${submission.room}" data-report="${report.id}" data-photo="${report.photos[0].id}"`):'';
  3617 |           return `<div class="rail-row"><strong>${submission.room}호 · ${esc(submission.kind||'퇴실 청소')} · ${esc(submission.submittedAt)}</strong><span>${esc(submissionStatus)} · 제출 ${esc(submission.id.split('-').slice(-2).join('-'))}${breakdown?` · ${esc(breakdown)}`:''}${evidence}</span></div>`;
  3618 |         });
  3619 |         const currentAttemptRows=currentAttempts.map(({room,attempt})=>`<div class="rail-row"><strong>${room}호 · ${esc(attempt?.kind||'청소')} · 현재 수행 회차</strong><span>${esc(cleaningLabel(state.jobs[room]))} · ${esc(attempt?.id||'회차 정보 없음')}</span></div>`),assignmentRows=assignments.filter(room=>!currentRooms.has(room.no)).map(room=>`<div class="rail-row"><strong>${room.no}호 · 현재 담당</strong><span>${esc(cleaningLabel(state.jobs[room.no]))} · 담당 선택 권한 없음</span></div>`),historyRows=[...currentAttemptRows,...assignmentRows,...submissionHistoryRows],unstartedCount=currentAttempts.filter(({room})=>['scheduled','claimed','unassigned'].includes(state.jobs[room])).length,progressCount=currentAttempts.filter(({room})=>state.jobs[room]==='cleaning').length,uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=submissions.filter(submission=>submission.status==='pending').length,futureCount=notifiedAssignmentEntriesForMaid(m.id).length,pinLeaseCount=activeCleaningFor(m.id)?1:0,stateTone=status==='active'?'green':processing?'amber':'neutral';
  3620 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${m.name} · 데모`,`불변 사용자 ID 기준 · 모든 메이드에 동일한 계정 관리·이력 보존 규칙 적용`)+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>계정·근무 상태</h3>${statusBadge(maidDeactivationLabel(m.id),stateTone)}</div><div class="info-grid"><div class="info-item"><span>로그인 아이디</span><strong>${esc(m.name)}</strong></div><div class="info-item"><span>휴대폰</span><strong>${esc(m.phone)}</strong></div><div class="info-item"><span>객실 선택 권한</span><strong>없음 · 관리자 전용</strong></div><div class="info-item"><span>배정 업무·PIN</span><strong>${status==='active'?'확인 가능':'잠금'}</strong></div></div></section><section class="card card-pad"><div class="section-head"><h3>업무 영향 요약</h3>${statusBadge(inactive?'정리 완료':'실시간 집계','neutral')}</div><div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${futureCount}건 · ${inactive?'정리 완료':'변경 통보 필요'}</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${unstartedCount+progressCount}건 · ${processing?(flow.choice==='stop'?'인계 필요':'마무리 허용'):inactive?'회차 종결':'처리 방식 선택'}</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · ${uploadCount?'제출 필요':'없음'}</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · ${pendingCount?'관리자 결정 필요':'없음'}</strong></div><div class="info-item"><span>미지급 수익</span><strong>${money(currentApproved)} · 지급 이력 보존</strong></div><div class="info-item"><span>활성 PIN lease</span><strong>${inactive?'0건 · 종료':`${pinLeaseCount}건 · ${processing?'종료 필요':'현재 기준'}`}</strong></div></div></section><section class="card card-pad" data-maid-history="${m.id}"><div class="section-head"><h3>담당·실제 수행 이력</h3><select class="select-control" aria-label="이력 기간"><option>7일</option><option>30일</option></select></div><div class="rail-list">${historyRows.join('')||'<div class="rail-row"><strong>저장된 담당·수행 이력 없음</strong><span>데모 fixture 기준</span></div>'}${m.id==='m1'?'<div class="rail-row"><strong>536호 · 폭탄방 승인 수익 · 과거 데모</strong><span>기본 20,000원 + 해당 객실 추가 20,000원 = 40,000원</span></div>':''}</div></section>${renderMaidAccountManagement(m.id)}</div><aside class="detail-stack"><section class="card card-pad"><h3>평가·컴플레인</h3><p class="cell-sub">등록 ${complaintCount}건 · 주급 자동 차감 없음</p>${complaintCount?button('컴플레인 상세','complaint-detail','outline'):''}</section><section class="card card-pad"><h3>주급</h3><p><strong>이번 주 승인 확정 ${money(currentApproved)}</strong></p><p class="audit-note">다른 메이드의 객실·사진·수익은 이 상세에 섞이지 않습니다.</p>${button('지급 이력','pay-detail','outline')}</section></aside></div>`;
  3621 |       }
  3622 | 
  3623 |       function renderComplaintDetail() {
  3624 |         const c=state.complaint;
  3625 |         return renderCoach()+detailHeader('컴플레인 C-014 · 데모','332호 청소 연결 · 벌점은 주급을 자동 차감하지 않음')+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>판정 상태</h3>${statusBadge(complaintLabel(c),c==='closed'?'green':c==='objected'?'red':'amber')}</div><div class="info-grid"><div class="info-item"><span>분류</span><strong>청소 미흡</strong></div><div class="info-item"><span>관련 작업</span><strong>332호 · CL-332-08</strong></div><div class="info-item"><span>접수일</span><strong>2026.08.14</strong></div><div class="info-item"><span>주급 영향</span><strong>자동 차감 없음</strong></div></div><div class="notice notice-warning" style="margin:14px 0">고객 개인정보를 제외한 가림 처리 운영 문구: 욕실 거울 얼룩이 남아 있었음.</div>${renderComplaintActions(c)}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>사건 타임라인</h3><ol class="timeline"><li><strong>접수</strong><span>09:20 · 관리자</span></li><li><strong>사실 확인</strong><span>10:10 · 증빙 검토</span></li><li style="opacity:${['ruled','acknowledged','objected','closed'].includes(c)?1:.45}"><strong>판정</strong><span>${['ruled','acknowledged','objected','closed'].includes(c)?'확인됨 · 평가 참고':'대기'}</span></li><li style="opacity:${['acknowledged','objected','closed'].includes(c)?1:.45}"><strong>메이드 응답</strong><span>${c==='objected'?'이의 메모':c==='acknowledged'?'내용 확인':'대기'}</span></li><li style="opacity:${c==='closed'?1:.45}"><strong>종결</strong><span>${c==='closed'?'원본 삭제 없이 이벤트 보존':'대기'}</span></li></ol></section></aside></div>`;
  3626 |       }
  3627 |       function complaintLabel(c){return ({received:'확인 중',ruled:'판정 완료 · 메이드 확인 대기',acknowledged:'메이드 확인',objected:'메이드 이의 · 재검토 필요',closed:'종결'})[c]||c;}
  3628 |       function renderComplaintActions(c) {
  3629 |         if (state.role==='admin'&&c==='received') return button('관리자 판정','rule-complaint','primary',isLocked()?'disabled':'');
  3630 |         if (state.role==='maid'&&c==='ruled') return `<div class="job-actions">${button('내용 확인','ack-complaint','outline')}${button('이의 메모','object-complaint','primary')}</div>`;
  3631 |         if (state.role==='admin'&&['acknowledged','objected'].includes(c)) return `<div class="job-actions">${button(c==='objected'?'판정 유지·종결':'종결','close-complaint','primary')}${c==='objected'?button('판정 정정','correct-complaint','outline'):''}</div>`;
  3632 |         if (c==='ruled') return `<div class="notice notice-info" style="margin:0">메이드 역할로 전환해 판정 확인 또는 이의를 진행하세요.</div>`;
  3633 |         return `<div class="notice notice-success" style="margin:0">원본과 모든 정정 이벤트를 보존한 채 종결됐습니다.</div>`;
  3634 |       }
  3635 | 
  3636 |       function renderPayDetail() {
  3637 |         const paidAmount=maidPayAmount('김민지1','2026-08-03'),paymentStatus=paymentStatusFor('2026-08-03','m1');
  3638 |         return renderCoach()+renderNetworkNotice()+detailHeader('김민지1 × 8월 3일–9일 지급','메이드별 지난주 전액 · 부분 지급 없음 · 실제 송금은 앱 밖에서')+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>지급 상태</h3>${statusBadge(payLabel(paymentStatus),paymentStatus==='PAID'?'green':paymentStatus==='PAYING'||paymentStatus==='CHECK'?'amber':'neutral')}</div><div class="info-grid"><div class="info-item"><span>지급 대상</span><strong>${money(paidAmount)} · 데모</strong></div><div class="info-item"><span>포함 수익</span><strong>승인 청소 6건</strong></div><div class="info-item"><span>지급 주차</span><strong>8/3(월)–8/9(일)</strong></div><div class="info-item"><span>외부 송금</span><strong>${paymentStatus==='PAID'?'완료 기록':'앱에서 실행 안 함'}</strong></div></div>${renderPayActions()}</section><section class="card card-pad"><h3>수익 원장 · 데모</h3><div class="rail-list"><div class="rail-row"><strong>536호 · 폭탄방 승인 · ×2</strong><span>기본 20,000원 + 추가 20,000원 = 40,000원</span></div><div class="rail-row"><strong>350호 · 승인</strong><span>16,000원</span></div><div class="rail-row"><strong>142호 · 연박 승인</strong><span>30,000원</span></div></div><p class="audit-note">폭탄방 배율은 536호에만 적용됐으며 이 주차의 다른 객실 금액은 변하지 않았습니다.</p></section></div><aside class="detail-stack"><section class="card card-pad"><h3>상태 전이</h3><ol class="timeline"><li><strong>OPEN</strong><span>늦은 승인·정정 반영 가능</span></li><li style="opacity:${paymentStatus!=='OPEN'?1:.45}"><strong>PAYING</strong><span>금액·수익 ID·관리자 잠금</span></li><li style="opacity:${paymentStatus==='PAID'?1:.45}"><strong>PAID</strong><span>외부 전액 송금 후 기록</span></li></ol></section></aside></div>`;
  3639 |       }
  3640 |       function payLabel(s){ return s==='CHECK'?'정산 확인 필요':s; }
  3641 |       function renderPayActions(){const paidAmount=maidPayAmount('김민지1','2026-08-03'),paymentStatus=paymentStatusFor('2026-08-03','m1');if(paymentStatus==='OPEN')return `<div style="margin-top:14px">${button('지급 진행 선점','start-payment','primary',isLocked()?'disabled':'')}</div>`;if(paymentStatus==='PAYING')return `<div class="notice notice-warning" style="margin:14px 0 10px">관리자 데모가 ${money(paidAmount)}을 선점했습니다. 외부 송금 뒤 결과를 기록하세요.</div><div class="job-actions">${button('기록 실패 · 확인 필요','payment-check','outline')}${button('외부 송금 완료 기록','finish-payment','success')}</div>`;if(paymentStatus==='CHECK')return `<div class="notice notice-danger" style="margin:14px 0 10px">자동 OPEN 복귀 금지. 송금 여부를 확인해야 합니다.</div><div class="job-actions">${button('송금하지 않음 · OPEN 복귀','payment-open','outline')}${button('송금 완료 재기록','finish-payment','success')}</div>`;return `<div class="notice notice-success" style="margin:14px 0 0">지급 완료 기록은 삭제하지 않으며 이후 차이는 다음 주 정정·상계로 이월합니다.</div>`;}
  3642 | 
  3643 |       function renderLogin() {
  3644 |         const locked=state.loginMode==='locked';
  3645 |         return `<main id="main-content" style="max-width:460px;padding-top:7vh"><section class="card card-pad" style="box-shadow:var(--shadow)"><div class="brand" style="padding:4px 0 22px"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리 · 데모 로그인</div></div></div><div class="notice notice-info">실제 인증이 아닌 화면 상태 데모입니다. 입력값은 저장하지 않습니다.</div><div class="tabs" role="tablist" aria-label="로그인 상태"><button type="button" role="tab" data-action="login-mode" data-mode="normal" aria-selected="${state.loginMode==='normal'}">일반</button><button type="button" role="tab" data-action="login-mode" data-mode="first" aria-selected="${state.loginMode==='first'}">최초 변경</button><button type="button" role="tab" data-action="login-mode" data-mode="locked" aria-selected="${locked}">잠금</button><button type="button" role="tab" data-action="login-mode" data-mode="error" aria-selected="${state.loginMode==='error'}">오류</button></div>${locked?`<div class="notice notice-danger" style="margin-top:14px">연속 5회 실패로 14분 28초 동안 잠겼습니다. 추가 시도로 종료 시각을 늘리지 않습니다.</div>`:''}${state.loginMode==='error'?`<div class="notice notice-danger" style="margin-top:14px">아이디 또는 로그인 비밀번호가 일치하지 않습니다. 객실 4자리 PIN과 다른 값입니다.</div>`:''}<form id="login-form" style="display:grid;gap:12px;margin-top:16px"><div class="field"><label for="login-id">로그인 아이디</label><input id="login-id" class="input-control" value="${state.role==='admin'?'관리자':'김민지1'}" autocomplete="username" ${locked?'disabled':''}></div><div class="field"><label for="login-password">로그인 비밀번호</label><input id="login-password" class="input-control" type="password" inputmode="numeric" value="04821" autocomplete="current-password" ${locked?'disabled':''}><small>숫자 6자리 이상 · 데모 입력은 서버로 전송되지 않음</small></div><button class="btn btn-primary btn-block" type="submit" ${locked?'disabled':''}>${state.loginMode==='first'?'개인 로그인 비밀번호 변경':'로그인'}</button></form></section></main>`;
  3646 |       }
```

### occurrence 11 · line 5205

```html
  5189 |         return `<div class="assignment-type-filters" role="group" aria-label="청소대상 객실 타입 필터">${items.map(item=>`<button class="assignment-type-filter" type="button" data-action="assignment-type-filter" data-type="${esc(item.id)}" aria-pressed="${filter===item.id}" aria-label="${esc(item.name)} ${item.count}건${item.id==='all'?'':`, 청소 요금 ${item.meta.replace('객실당 ','')}`} 보기"><strong>${esc(item.name)}</strong><span>${item.count}건</span><small>${esc(item.meta)}</small></button>`).join('')}</div>`;
  5190 |       }
  5191 |       function assignmentRouteReference(item) {
  5192 |         const assignment=assignmentFor(item);
  5193 |         if(!assignment.maidId){const random=state.randomAssignments?.[item.id];return random?`<span class="assignment-random-note is-warning">${icon('alert','icon-sm')}${esc(random.reason)}</span>`:'<span class="assignment-route-reference">담당 선택 후 아래 순서 보드에 추가</span>';}
  5194 |         return `<span class="assignment-route-reference">${esc(maidName(assignment.maidId))} · 순서 보드 ${assignment.order}번째</span>${randomAssignmentNote(item)}`;
  5195 |       }
  5196 |       function maidOrderItemMarkup(item,ordered,index) {
  5197 |         const assignment=assignmentFor(item),context=assignmentContext(item),name=maidName(assignment.maidId),first=index===0,last=index===ordered.length-1,status=assignment.status==='notified'?'통보 완료':'저장 전',scheduleBadges=assignmentSchedulePriorityBadges(item),guestCount=assignmentGuestCount(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item),disabled=adjustmentBlock?'disabled':'',previous=ordered[index-1],next=ordered[index+1],upDisabled=first||!!adjustmentBlock||!!previous&&!cleaningTargetCanAdjust(previous),downDisabled=last||!!adjustmentBlock||!!next&&!cleaningTargetCanAdjust(next);
  5198 |         return `<article class="maid-order-item ${scheduleBadges.length?'has-schedule-attention':''}"><span class="maid-order-number" aria-hidden="true">${assignment.order}</span><div class="maid-order-copy"><strong>${assignment.order}번째 · ${item.room}호</strong>${scheduleBadges.length?`<div class="maid-order-schedule-badges" aria-label="${item.room}호 일정 주의">${scheduleBadges.join('')}</div>`:''}<span>${esc(context.type.name)} · ${money(context.type.rate)}${guestCount?` · 숙박 ${guestCountLabel(guestCount)}`:''}</span><span>${esc(elevatorLabel(context.room))} · ${esc(item.kind)} · ${status}</span>${adjustmentBlock?`<span>${esc(adjustmentBlock)}</span>`:''}</div><label class="maid-order-assignee"><span class="sr-only">${item.room}호 담당 메이드 변경</span><select class="select-control" data-control="assignment-maid" data-location="board" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 변경" ${disabled}>${assignmentOptions(item)}</select></label><div class="maid-order-controls"><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="up" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 위로 이동" ${upDisabled?'disabled':''}>${icon('arrowUp','icon-sm')}</button><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="down" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 아래로 이동" ${downDisabled?'disabled':''}>${icon('arrowDown','icon-sm')}</button></div></article>`;
  5199 |       }
  5200 |       function renderRandomAssignmentCard() {
  5201 |         const eligible=eligibleAssignmentMaids(),unassigned=assignmentTargets().filter(item=>!assignmentFor(item).maidId&&!roomIsOnHold(item.room)&&cleaningTargetCanAdjust(item)),summary=state.randomAssignmentSummary||{assigned:0,skipped:0},active=!!state.randomAssignmentSnapshot,disabled=state.role!=='admin'||isLocked()||!eligible.length||(!active&&!unassigned.length);
  5202 |         const actions=active?`${button('다시 동선 고려 랜덤 배정','random-assignments','outline',disabled?'disabled':'')}${button('랜덤 배정 전으로 되돌리기','undo-random-assignment','outline',disabled?'disabled':'')}`:button(`미배정 ${unassigned.length}건 동선 고려 랜덤 배정`,'random-assignments','primary',disabled?'disabled':'');
  5203 |         return `<section class="card assignment-random" aria-labelledby="assignment-random-title"><div class="assignment-random-copy"><span class="random-kicker">2단계 · 저장 전 랜덤 초안</span><div class="assignment-random-title-row"><h3 id="assignment-random-title">동선 고려 랜덤 배정</h3><div class="assignment-rule-help"><button class="assignment-rule-help-button" type="button" aria-label="랜덤 배정 기준 설명" aria-describedby="assignment-random-tooltip">${icon('info','icon-sm')}</button><div class="assignment-rule-tooltip" id="assignment-random-tooltip" role="tooltip"><strong>랜덤 배정 기준</strong><span>근무 가능·마감을 먼저 확인합니다.</span><span>총 청소요금 균형을 우선합니다.</span><span>같은 점수에서는 같은 엘리베이터·가까운 호수를 봅니다.</span><span>관리자가 담당과 순서를 최종 수정합니다.</span><span>실제 이동시간을 계산하는 경로 최적화는 아닙니다.</span></div></div></div><p>미배정 객실만 저장 전 초안으로 배정합니다.</p></div><div class="assignment-random-stats"><div><span>근무 가능</span><strong>${eligible.length}명</strong></div><div><span>초안 배정</span><strong>${active?`${summary.assigned}객실`:'실행 전'}</strong></div><div><span>남은 미배정</span><strong>${active?`${summary.skipped}객실`:`${unassigned.length}객실`}</strong></div></div><div class="assignment-random-actions"><div class="random-live" aria-live="polite">${active?`${summary.assigned}건을 랜덤 배정했습니다. 아래에서 담당과 순서를 바꾼 뒤 저장·통보하세요.`:'기존 통보와 관리자가 정한 담당은 유지하고 미배정 객실만 채웁니다.'}</div>${actions}</div></section>`;
  5204 |       }
  5205 |       function renderMaidOrderBoardContent() {
  5206 |         const targets=assignmentTargets(),unassigned=targets.filter(item=>!assignmentFor(item).maidId),assignedMaidIds=new Set(targets.map(item=>assignmentFor(item).maidId).filter(Boolean)),isEditingBalance=targets.some(item=>assignmentFor(item).status==='draft');
  5207 |         const visibleMaidIds=isEditingBalance?new Set([...assignedMaidIds,...eligibleAssignmentMaids().map(maid=>maid.id)]):assignedMaidIds,visibleMaids=MAIDS.filter(maid=>visibleMaidIds.has(maid.id));
  5208 |         const lanes=visibleMaids.map(maid=>{const ordered=orderedAssignmentsForMaid(maid.id),total=ordered.reduce((sum,item)=>sum+assignmentTargetRate(item),0);return `<section class="maid-order-lane" id="maid-order-${maid.id}" aria-labelledby="maid-order-title-${maid.id}"><div class="maid-order-lane-head"><div class="maid-order-lane-copy"><h4 id="maid-order-title-${maid.id}">${esc(maid.name)} 배정 객실·청소 순서</h4><p>각 객실의 담당을 바꾸거나 위·아래 버튼으로 1–N 순서를 조정할 수 있습니다.</p></div><div class="maid-order-lane-total" data-maid-id="${maid.id}" data-maid-total="${total}"><span>총 청소요금 · ${ordered.length}건</span><strong>${money(total)}</strong></div></div><div class="maid-order-list">${ordered.length?ordered.map((item,index)=>maidOrderItemMarkup(item,ordered,index)).join(''):'<div class="maid-order-empty">배정된 객실이 없습니다.</div>'}</div></section>`;}).join('');
  5209 |         const unassignedList=unassigned.length?unassigned.map(item=>{const context=assignmentContext(item);return `<span class="maid-order-unassigned-chip">${item.room}호 · ${esc(context.type.name)} · ${esc(elevatorLabel(context.room))} · ${money(context.type.rate)}</span>`;}).join(''):'<span class="maid-order-unassigned-chip">미배정 객실 없음</span>';
  5210 |         return `<section class="card maid-order-panel" aria-labelledby="maid-order-board-title"><div class="assignment-panel-head"><div><span class="assignment-step-label">4단계 · 세부 수정</span><h3 id="maid-order-board-title">메이드별 청소 순서 수정</h3><p>얼리 체크인·레이트 체크아웃의 조정된 예정 시각을 먼저 확인하고, 객실 담당과 1–N 순서를 직접 수정합니다.</p></div>${statusBadge(`${unassigned.length}건 미배정`,unassigned.length?'red':'green')}</div><div class="maid-order-board ${lanes?'':'is-empty'}">${lanes||'<div class="maid-order-empty">아직 배정된 객실이 없습니다. 랜덤 배정하거나 위 객실 표에서 담당을 선택하세요.</div>'}</div><div class="maid-order-unassigned"><div><h4>아직 순서가 없는 객실</h4><p>미배정 상태로 남겨 두고 담당이 정해진 객실만 먼저 통보할 수 있습니다.</p></div><div class="maid-order-unassigned-list">${unassignedList}</div></div><div class="assignment-foot"><p>랜덤 배정은 저장 전 초안입니다. 담당과 연속 순서가 정해진 객실만 저장·통보합니다.</p>${button(`배정된 변경 ${assignmentTargets().filter(item=>assignmentHasNetChange(item)&&assignmentFor(item).maidId).length}건 저장·통보`,'save-assignments','primary',assignmentCanSave()?'':'disabled')}</div></section>`;
  5211 |       }
  5212 |       function assignmentCountsForDate(assignmentDate=state.assignmentDate) {
  5213 |         const targets=assignmentTargetsForDate(assignmentDate),rows=targets.map(item=>state.assignments?.[item.id]||{maidId:'',status:'unassigned'}),assigned=rows.filter(item=>item.maidId).length,notified=targets.filter(item=>{const record=state.assignments?.[item.id];return !!(record?.status==='notified'&&record.maidId||record?.previousMaidId);}).length;
  5214 |         return {total:rows.length,assigned,notified,unassigned:rows.length-assigned,carryover:targets.filter(item=>item.carryReason).length,automatic:targets.filter(item=>item.source!=='manual').length,manual:targets.filter(item=>item.source==='manual').length,checkout:targets.filter(item=>item.source==='checkout').length,stayover:targets.filter(item=>item.source==='stayover').length,submitted:MAIDS.filter(maid=>availabilityForWorkDate(maid.id,assignmentDate)!=='missing').length};
  5215 |       }
  5216 |       function assignmentCounts() { return assignmentCountsForDate(state.assignmentDate); }
  5217 |       function assignmentCanSave() {
  5218 |         const targets=assignmentTargets(),changedTargets=targets.filter(item=>assignmentHasNetChange(item)&&!!assignmentFor(item).maidId),affectedMaidIds=[...new Set(changedTargets.flatMap(item=>[assignmentFor(item).maidId,assignmentFor(item).previousMaidId]).filter(Boolean))],allAssignedToAvailable=changedTargets.every(item=>availabilityForWorkDate(assignmentFor(item).maidId,targetEffectiveDate(item))==='available');
  5219 |         const continuousOrders=affectedMaidIds.every(maidId=>orderedAssignmentsForMaid(maidId).every((item,index)=>assignmentFor(item).order===index+1));
  5220 |         const allAssignedToActiveMaids=changedTargets.every(item=>maidCanReceiveNewAssignment(assignmentFor(item).maidId));
  5221 |         const noHeldRoomChanges=changedTargets.every(item=>!roomIsOnHold(item.room)&&item.carryReason!=='access-review');
  5222 |         const noStartedRoomChanges=changedTargets.every(cleaningTargetCanAdjust);
  5223 |         const randomFresh=!state.randomAssignmentSnapshot||(state.randomAssignmentSnapshot.contextSignature===randomAssignmentContextSignature()&&randomAssignmentStateMatches());
  5224 |         return changedTargets.length>0&&noHeldRoomChanges&&noStartedRoomChanges&&allAssignedToAvailable&&allAssignedToActiveMaids&&continuousOrders&&randomFresh&&!isLocked();
  5225 |       }
  5226 |       function renderAvailabilityMatrix() {
  5227 |         const start=weekStartIso(state.assignmentDate),days=['월','화','수','목','금','토','일'].map((name,index)=>{const iso=addIsoDays(start,index);return {name,iso,day:Number(iso.slice(8))};});
  5228 |         return `<div class="availability-matrix-wrap"><table class="availability-matrix"><thead><tr><th scope="col">메이드</th>${days.map(day=>`<th scope="col">${day.name} ${day.day}</th>`).join('')}</tr></thead><tbody>${MAIDS.map(maid=>`<tr><th scope="row">${esc(maid.name)}</th>${days.map((day,index)=>`<td>${availabilityCell(maid.id,index,day.iso)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="assignment-foot"><p>✓ 가능 · × 불가 · — 미제출. ${days[assignmentDayIndex()].name}요일 배정 후보는 해당 날짜 가능 제출자만 표시합니다.</p></div>`;
  5229 |       }
  5230 |       function assignmentOptions(item) {
  5231 |         const selected=assignmentFor(item).maidId||'',effectiveDate=targetEffectiveDate(item);
  5232 |         const eligible=MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,effectiveDate)==='available');
  5233 |         const legacy=selected&&!eligible.some(maid=>maid.id===selected)?`<option value="${esc(selected)}" selected disabled>${esc(maidName(selected))} (기존 담당 · 신규 배정 불가)</option>`:'';
  5234 |         return `<option value="">담당 선택</option>${legacy}${eligible.map(maid=>`<option value="${maid.id}" ${selected===maid.id?'selected':''}>${esc(maid.name)} (근무 가능)</option>`).join('')}${eligible.length?'':'<option value="" disabled>근무 가능 메이드 없음</option>'}`;
  5235 |       }
  5236 |       function assignmentContext(item) {
  5237 |         const liveRoom=ROOMS.find(entry=>entry.no===item.room),snapshot=assignmentPricingSnapshot(item),room=liveRoom?{...liveRoom,elevator:snapshot.elevator}:liveRoom,type={...(ROOM_TYPES[snapshot.typeId]||ROOM_TYPES.standard),rate:snapshot.rate,minutes:snapshot.minutes};
  5238 |         const roomStatus=roomReservationStatus(room),status=item.source==='stayover'?reservationTimeStatus(null,null):reservationTimeStatus(item.checkin||roomStatus.checkin,item.checkout||roomStatus.checkout);
  5239 |         return {room,type,...status};
```

### occurrence 12 · line 5450

```html
  5434 |       }
  5435 |       function workHistoryWeeks() {
  5436 |         const fixtures=WORK_HISTORY_FIXTURES.map(week=>({...week,records:Object.fromEntries(Object.entries(week.records).map(([maidId,record])=>[maidId,{...record,assigned:[...new Set([...(record.assigned||[]),...assignedWorkDaysForWeek(week.start,maidId)])].sort((left,right)=>left-right),completed:[...new Set([...(record.completed||[]),...completedWorkDaysForWeek(week.start,maidId)])].sort((left,right)=>left-right)}]))}));
  5437 |         return [currentWorkHistoryWeek(),...fixtures];
  5438 |       }
  5439 |       function renderWorkHistory() {
  5440 |         const weeks=workHistoryWeeks(),week=weeks.find(item=>item.start===state.workHistoryWeek)||{start:state.workHistoryWeek,status:'기록 없음',records:{}},selectedMaid=state.workHistoryMaid||'all';
  5441 |         const people=MAIDS.filter(maid=>selectedMaid==='all'||maid.id===selectedMaid).map(maid=>({maid,record:week.records[maid.id]})).filter(item=>item.record);
  5442 |         const totals=people.reduce((sum,item)=>({submitted:sum.submitted+item.record.submitted.length,assigned:sum.assigned+item.record.assigned.length,completed:sum.completed+item.record.completed.length}),{submitted:0,assigned:0,completed:0});
  5443 |         const maidCounts={submitted:people.filter(item=>item.record.submitted.length>0).length,assigned:people.filter(item=>item.record.assigned.length>0).length,completed:people.filter(item=>item.record.completed.length>0).length};
  5444 |         const dayNames=['월','화','수','목','금','토','일'];
  5445 |         const cards=people.map(({maid,record})=>{const days=dayNames.map((name,index)=>{const iso=addIsoDays(week.start,index),flags=[];if(record.submitted.includes(index))flags.push('<span class="work-history-flag">가능 제출</span>');if(record.assigned.includes(index))flags.push('<span class="work-history-flag assigned">담당 통보</span>');if(record.completed.includes(index))flags.push('<span class="work-history-flag completed">실근무 완료</span>');return `<div class="work-history-day"><strong>${name}요일</strong><span>${shortIsoDate(iso)}</span>${flags.length?`<div class="work-history-flags">${flags.join('')}</div>`:'<span class="work-history-empty">기록 없음</span>'}</div>`;}).join('');return `<article class="card work-history-person"><div class="work-history-person-head"><div><h3>${esc(record.nameSnapshot)} · 데모</h3><p>당시 이름 스냅샷 · 가능일 제출 ${esc(record.submittedAt)}${record.submissionVersions?` · 제출 버전 ${record.submissionVersions}개 보존`:''}</p></div><div class="work-history-counts">${statusBadge(`가능 ${record.submitted.length}일`,'blue')}${statusBadge(`배정 ${record.assigned.length}일`,'amber')}${statusBadge(`실근무 ${record.completed.length}일`,'green')}</div></div><div class="work-history-days" aria-label="${esc(record.nameSnapshot)} ${weekRangeLabel(week.start)} 주간 기록">${days}</div></article>`;}).join('');
  5446 |         const list=cards||`<section class="card empty-state"><h3>이 주차에는 저장된 근무 기록이 없습니다.</h3><p>다른 주차를 달력에서 선택하거나 메이드 필터를 바꿔 보세요.</p></section>`;
  5447 |         return `<div class="work-history-page"><section class="card work-history-hero"><div><h2>주간 근무 기록</h2><p>가능일 제출, 관리자 배정 통보, 실제 청소 완료일을 구분해 사람별·주차별로 확인합니다.</p></div>${statusBadge(`${week.status} · 관리자 전용`,week.status==='계획 중'?'blue':'neutral')}</section><section class="card"><div class="work-history-toolbar"><div class="work-history-week-field"><span id="work-history-week-label">조회 주차</span><button class="pay-week-picker work-history-week-picker" type="button" data-action="open-work-history-calendar" aria-haspopup="dialog" aria-labelledby="work-history-week-label work-history-week-value">${icon('calendar','icon-sm')}<span id="work-history-week-value">${weekRangeLabel(week.start,true)} · ${week.status}</span>${icon('chevronRight','icon-sm')}</button></div><label for="work-history-maid">메이드<select id="work-history-maid" class="select-control" data-control="work-history-maid"><option value="all" ${selectedMaid==='all'?'selected':''}>전체 메이드</option>${MAIDS.map(maid=>`<option value="${maid.id}" ${selectedMaid===maid.id?'selected':''}>${esc(maid.name)}</option>`).join('')}</select></label></div><div class="work-history-summary"><div class="planned"><span>가능 제출 메이드</span><strong>${maidCounts.submitted}명</strong><small>메이드별 가능일 합계 ${totals.submitted}일</small></div><div class="assigned"><span>담당 통보 메이드</span><strong>${maidCounts.assigned}명</strong><small>메이드별 배정일 합계 ${totals.assigned}일</small></div><div class="completed"><span>실제 근무 메이드</span><strong>${maidCounts.completed}명</strong><small>메이드별 실근무일 합계 ${totals.completed}일</small></div></div><p class="work-history-unit-note"><strong>단위 안내:</strong> ‘명’은 해당 기록이 한 번 이상 있는 메이드 수, ‘일’은 메이드별 기록 날짜를 합한 일수입니다.</p><div class="work-history-legend"><span><i class="history-dot"></i>가능 제출 · 계획</span><span><i class="history-dot assigned"></i>담당 통보 · 예정</span><span><i class="history-dot completed"></i>실근무 완료 · 수행 실적</span></div></section><div class="work-history-list">${list}</div><section class="card work-history-contract"><p><strong>기록 기준:</strong> 가능일은 제출 버전, 배정일은 관리자 통보 이벤트, 실근무일은 정상 청소 수행 회차의 현장 완료일입니다. 가능일만 제출한 날짜는 실제 근무로 세지 않으며, 과거 주차는 현재 제출·재배정으로 덮어쓰지 않습니다. 이 화면은 서버 영속 저장이 아닌 결정적 데모 fixture입니다.</p></section></div>`;
  5448 |       }
  5449 | 
  5450 |       function renderMaids() {
  5451 |         const tab=state.adminMaidTab||'workforce';
  5452 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>메이드 운영</h2><p>주간 근무 가능일·배정 업무·과거 근무 기록·주급·컴플레인을 분리해 관리합니다.</p></div></div><div class="tabs" role="tablist" aria-label="메이드 관리"><button type="button" role="tab" data-action="admin-maid-tab" data-tab="workforce" aria-selected="${tab==='workforce'}">주간 근무표</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="history" aria-selected="${tab==='history'}">근무 기록</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="pay" aria-selected="${tab==='pay'}">주급 정산</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="complaints" aria-selected="${tab==='complaints'}">컴플레인·벌점</button></div>${tab==='history'?renderWorkHistory():tab==='pay'?renderAdminPayroll():tab==='complaints'?renderComplaintsPanel():renderWorkforce()}</div>`;
  5453 |       }
  5454 |       function renderWorkforce() {
  5455 |         const submitted=Object.values(state.weeklyAvailability).filter(item=>['submitted','change-requested'].includes(item.status)).length;
  5456 |         const cards=MAIDS.map(maid=>{const record=state.weeklyAvailability[maid.id],availableDays=record.days.map(index=>['월','화','수','목','금','토','일'][index]).join('·')||'없음',accountStatus=maidStatusFor(maid.id),activity=accountStatus==='active'?maid.active:accountStatus==='deactivating'?'비활성 처리 중':'비활성';return `<article class="card pay-person" data-maid-card="${maid.id}"><div class="pay-person-head"><div class="avatar">${maid.name[0]}</div><div><h3>${maid.name} · 데모</h3><p>${maid.phone} · ${activity}</p></div>${statusBadge(accountStatus==='active'?(record.status==='submitted'?'제출 완료':record.status==='change-requested'?'변경 요청':'미제출'):accountStatus==='deactivating'?'비활성 처리 중':'비활성',accountStatus==='active'?(record.status==='submitted'?'green':record.status==='change-requested'?'amber':'red'):accountStatus==='deactivating'?'amber':'neutral')}</div><div class="pay-stats"><div class="pay-stat"><span>다음 주 가능</span><strong>${availableDays}</strong></div><div class="pay-stat"><span>예정 배정</span><strong>${assignmentTargets().filter(item=>assignmentFor(item).maidId===maid.id).length}객실</strong></div><div class="pay-stat"><span>제출 시각</span><strong>${record.submittedAt||'—'}</strong></div></div>${button('상세·이력','maid-detail','outline',`data-id="${maid.id}"`)}</article>`;}).join('');
  5457 |         return `<section class="card assignment-panel"><div class="assignment-panel-head"><div><h3>메이드 주간 근무표</h3><p>8월 17일–23일 · 일요일 23:59 마감</p></div>${statusBadge(`${submitted}/${MAIDS.length} 제출`,submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section><div class="room-list-v2">${cards}</div>`;
  5458 |       }
  5459 |       function payrollDateLabel(value) {
  5460 |         const match=String(value||'').match(/(?:\d{4}[.-])?(\d{1,2})[.-](\d{1,2})/);
  5461 |         return match?`${Number(match[1])}월 ${Number(match[2])}일`:'날짜 미입력';
  5462 |       }
  5463 |       function payrollTaskDateIso(value,weekStart) {
  5464 |         const direct=timestampIsoDate(value,'');
  5465 |         if(direct)return direct;
  5466 |         const match=String(value||'').match(/(\d{1,2})월\s*(\d{1,2})일/),weekEnd=addIsoDays(weekStart,6),baseYear=Number(String(weekStart).slice(0,4));
  5467 |         if(!match)return '';
  5468 |         for(const year of [baseYear-1,baseYear,baseYear+1]){const candidate=`${year}-${String(Number(match[1])).padStart(2,'0')}-${String(Number(match[2])).padStart(2,'0')}`;if(candidate>=weekStart&&candidate<=weekEnd)return candidate;}
  5469 |         return '';
  5470 |       }
  5471 |       function roomMetadataSnapshot(no) {
  5472 |         const room=ROOMS.find(item=>item.no===String(no)),type=room?ROOM_TYPES[room.type]:null;
  5473 |         return room&&type?{roomNo:room.no,typeId:room.type,typeName:type.name,elevator:room.elevator||null}:null;
  5474 |       }
  5475 |       function payrollTaskRoomContext(roomNo,snapshot=null) {
  5476 |         const baseline=ROOM_BASELINE.find(item=>item.no===String(roomNo)),room=snapshot?null:baseline,typeId=snapshot?.typeId||room?.type||null,type=typeId?ROOM_TYPES[typeId]:null,elevator=snapshot?.elevator??room?.elevator??null;
  5477 |         return {room,type,typeName:snapshot?.typeName||type?.name||'객실 타입 미입력',elevator:elevator?`${elevator} 엘리베이터`:'엘리베이터 미기재'};
  5478 |       }
  5479 |       function normalizePayrollFixture(task,weekStart,maidId) {
  5480 |         const roomNo=String(task.room),context=payrollTaskRoomContext(roomNo),base=Number(task.base??context.type?.rate??0),bombBonus=Number(task.bombBonus||0),amount=base+bombBonus;
  5481 |         return {...task,id:task.id||`pay-${weekStart}-${maidId}-${roomNo}`,weekStart,maidId,roomNo,room:`${roomNo}호`,typeName:context.typeName,elevator:context.elevator,earnedOn:payrollTaskDateIso(task.date,weekStart),baseAmount:base,bombBonus,amount,total:amount,stage:'confirmed',status:task.status||'승인 확정',tone:'green',bombStatus:bombBonus?'approved':'none',source:'fixture',included:true,potential:false};
  5482 |       }
  5483 |       function currentPayrollTasks(maidId,weekStart='2026-08-10') {
  5484 |         const confirmed=validatedEarningRecords().filter(record=>record.weekStart===weekStart&&record.performerId===maidId).sort((a,b)=>String(b.creditedAt).localeCompare(String(a.creditedAt))).map(record=>{
```

## maid schedule: `function renderMaidSchedule`

matches: 1

### occurrence 1 · line 6061

```html
  6045 |         return config?standardModalMarkup(config):'';
  6046 |       }
  6047 |       function openRoomIssuePhoto(no,issueId,photoId,trigger=document.activeElement) {
  6048 |         const payload={source:'room-issue',room:no,recordId:issueId,photoId},config=photoViewerConfig(payload);
  6049 |         if(!config){toast('이 사진을 볼 권한이 없거나 기록을 찾을 수 없습니다.','error');return;}
  6050 |         showModal({...config,trigger,historyKind:'photo-viewer',historyPayload:payload});
  6051 |       }
  6052 |       function openBombRoomPhoto(no,reportId,photoId,trigger=document.activeElement) {
  6053 |         const payload={source:'bomb-room',room:no,recordId:reportId,photoId},config=photoViewerConfig(payload);
  6054 |         if(!config){toast('이 폭탄방 증빙을 볼 권한이 없거나 기록을 찾을 수 없습니다.','error');return;}
  6055 |         showModal({...config,trigger,historyKind:'photo-viewer',historyPayload:payload});
  6056 |       }
  6057 |       function renderAvailabilityCard() {
  6058 |         const saved=state.weeklyAvailability?.[signedInMaidId()]?.days||[],hasCommitted=state.availabilitySubmitted||state.availabilityChangeRequested,selected=hasCommitted?saved:state.availabilityDraft||[],statusLabel=state.availabilityChangeRequested?'다음 주 변경 요청':state.availabilitySubmitted?'다음 주 제출 완료':'다음 주 미제출';
  6059 |         return `<section class="card availability-card"><div class="availability-result">${statusBadge(statusLabel,state.availabilitySubmitted?'green':'amber')}<div><strong>8월 17일–23일 · 가능 ${selected.length}일</strong><span>${availabilitySubmissionWindowLabel()} 제출 · 객실 담당은 관리자만 배정</span></div>${button('근무 일정 열기','go-schedule','outline')}</div></section>`;
  6060 |       }
  6061 |       function renderMaidSchedule() {
  6062 |         const maidId=signedInMaidId(),accountActive=signedInMaidIsActive(),dayNames=[['월','17'],['화','18'],['수','19'],['목','20'],['금','21'],['토','22'],['일','23']],phase=availabilitySubmissionPhase(),submitted=state.availabilitySubmitted,editing=!!state.availabilityEditing&&phase==='open',savedSelected=state.weeklyAvailability?.[maidId]?.days||[],selected=editing||!submitted?state.availabilityDraft||[]:savedSelected,availableCount=selected.length;
  6063 |         const assigned=notifiedAssignmentEntriesForMaid(maidId);
  6064 |         const assignedCards=assigned.length?assigned.map(({item})=>{const guestCount=assignmentGuestCount(item);return `<div class="assigned-preview-grid"><div><span>근무일</span><strong>${esc(dateLabel(targetEffectiveDate(item)))}</strong></div><div><span>객실</span><strong>${item.room}호</strong></div><div><span>업무</span><strong>${esc(item.kind)}</strong></div>${guestCount?`<div><span>숙박 인원</span><strong>${esc(guestCountLabel(guestCount))}</strong></div>`:`<div><span>예약 연결</span><strong>없음</strong></div>`}<div><span>시작 가능</span><strong>${item.checkout} 이후</strong></div>${item.carryReason?`<div><span>이월</span><strong>원 계획 ${esc(dateLabel(targetPlanDate(item)))}</strong></div>`:''}</div>`;}).join(''):`<div class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 근무일 전날 밤 객실 담당을 확정하면 여기에 표시됩니다.</p></div>`;
  6065 |         const submissionWindow=availabilitySubmissionWindowLabel(),phaseText=!accountActive?'비활성 계정 · 과거 제출 읽기 전용':phase==='before'?`${submissionWindow} 제출 가능`:phase==='open'?`${submissionWindow} · 지금 제출 가능`:`${submissionWindow} 마감 · 변경은 관리자 확인 필요`;
  6066 |         const editorLocked=!accountActive||submitted&&!editing||state.availabilityChangeRequested||phase!=='open'||isLocked();
  6067 |         let actionMarkup='';
  6068 |         if(!accountActive)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>가능일 수정 잠금</strong><br>비활성 처리 중이거나 비활성인 계정은 과거 제출만 조회할 수 있습니다.</div></div>';
  6069 |         else if(state.availabilityChangeRequested)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>관리자 확인 요청됨</strong><br>기존 제출은 유지되고 변경 요청이 관리자 알림에 남았습니다.</div></div>';
  6070 |         else if(editing)actionMarkup=button('수정 내용 다시 제출','submit-week-availability','primary',isLocked()?'disabled':'');
  6071 |         else if(submitted&&phase==='open')actionMarkup=button('제출 내용 수정','edit-week-availability','primary',isLocked()?'disabled':'');
  6072 |         else if(submitted&&phase==='closed')actionMarkup=button('가능일 변경 요청','request-availability-change','outline',isLocked()?'disabled':'');
  6073 |         else if(submitted)actionMarkup=button('제출 기간 아님','edit-week-availability','outline','disabled');
  6074 |         else actionMarkup=button(phase==='open'?'다음 주 가능일 제출':phase==='before'?`${submissionWindow} 제출`:'제출 마감','submit-week-availability','primary',phase==='open'&&!isLocked()?'':'disabled');
  6075 |         return renderCoach()+renderNetworkNotice()+`<div class="weekly-availability"><section class="card week-card"><div class="week-card-head"><div><h2>8월 17일 (월)–8월 23일 (일)</h2><p>다음 주에 근무 가능한 요일을 모두 선택해 주세요.</p></div>${statusBadge(state.availabilityChangeRequested?'변경 요청':editing?'수정 중':submitted?'제출 완료':'미제출',state.availabilityChangeRequested||editing?'amber':submitted?'green':'amber')}</div><div class="deadline-bar">${icon('clock','icon-sm')}<span>${phaseText}</span></div><div class="week-days" aria-label="다음 주 근무 가능일">${dayNames.map((day,index)=>{const active=selected.includes(index);return `<button class="week-day" type="button" data-action="toggle-week-day" data-day="${index}" aria-pressed="${active}" ${editorLocked?'disabled':''}><strong>${day[0]} ${day[1]}</strong><span>${active?'근무 가능':'근무 불가'}</span><i class="week-toggle" aria-hidden="true"></i></button>`;}).join('')}</div><div class="week-total">${icon('calendar','icon-sm')}가능 ${availableCount}일 · 불가 ${7-availableCount}일</div><div class="week-submit-actions">${actionMarkup}</div><div class="assignment-notice">${icon('user')}<p>관리자가 각 근무일 전날 밤 객실을 직접 배정합니다. 메이드는 객실을 선택하거나 다른 메이드에게 배정할 수 없습니다.</p></div></section><section class="card assigned-preview"><div class="section-head"><div><h2>배정된 내 업무</h2><span class="meta">관리자 통보 완료 건만 표시</span></div>${statusBadge(`${assigned.length}건`,'blue')}</div>${assignedCards}<p class="audit-note" style="margin:10px 0 0">배정이 바뀌면 기존 담당 구간은 이력으로 남고 알림에서 변경 내용을 확인할 수 있습니다.</p></section></div>`;
  6076 |       }
  6077 |       function publicJobCard(no) {
  6078 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room?.type||'standard'];
  6079 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${esc(cleaningLabel(state.jobs[no]))}</h3><p>${esc(type.name)}</p></div>${statusBadge('관리자 배정','green')}</div><div class="schedule-line">${icon('clock','icon-sm')}<span>시작 가능 ${startTimeFor(no)} · 담당 ${esc(room?.assignee||'미정')}</span></div><div class="notice notice-info" style="margin:0">메이드는 관리자에게 통보받은 업무만 확인하고 수행할 수 있습니다.</div></article>`;
  6080 |       }
  6081 |       function renderMaidOpen() {
  6082 |         return renderMaidSchedule();
  6083 |       }
  6084 |       function myJobCard(no) {
  6085 |         const job=state.jobs[no], room=ROOMS.find(r=>r.no===no),attempt=state.cleaningAttempts?.[currentAttemptId(no)],access=attemptAccessStatus(no,attempt),start=access.start,reached=access.allowed,rollover=rolloverMetaForRoom(no);
  6086 |         const guestCount=guestCountForAttempt(attempt),guestCountDisplay=guestCount?guestCountLabel(guestCount):'미기록',reclean=attempt?.kind==='재청소'?{reason:attempt.reason||'전체 반려 뒤 본인 재청소',previousMaid:currentSubmission(no)?.performerName||room?.assignee||'기존 메이드',originalKind:currentSubmission(no)?.kind||'퇴실 청소'}:null;
  6087 |         const labels={scheduled:reached?'일 시작':'시작 시각 대기',claimed:reached?'일 시작':'시작 시각 대기',cleaning:'계속 청소',upload:taskState(no).uploads.some(u=>u.status==='failed')?'미전송 재시도':'청소 전체 제출',inspection:'제출 결과 보기',approved:'완료 결과 보기',reclean:reached?'재청소 시작':'시작 시각 대기'};
  6088 |         const action='cleaning-detail';
  6089 |         const bomb=bombRoomReport(no),bombMeta=bombRoomStatusMeta(bomb),tone=job==='approved'?'green':job==='cleaning'||job==='upload'?'amber':job==='inspection'?'blue':'neutral';
  6090 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${reclean?'재청소':cleaningLabel(job)}</h3><p>${esc(ROOM_TYPES[room?.type||'standard'].name)}</p></div><div class="badge-row">${statusBadge(statusLabel(job),tone)}${bomb?statusBadge(bombMeta.label,bombMeta.tone):''}</div></div>${rolloverBadgeMarkup(rollover,{compact:true})}<div class="schedule-line">${icon('clock','icon-sm')}<span>${job==='upload'?'현장 완료 · 사진 전송·전체 제출 필요':job==='cleaning'&&rollover?'계속 청소 가능':`시작 가능 ${start} · ${reached?'지금 시작 가능':esc(access.reason)}`}</span></div><div class="schedule-line">${icon('user','icon-sm')}<span>숙박 인원 ${guestCountDisplay}</span></div>${reclean?`<div class="job-meta"><div><span>재청소 요금</span><strong>0원 · 무급</strong></div><div><span>원 작업</span><strong>${no}호 ${esc(reclean.originalKind)}</strong></div></div><div class="notice notice-warning" style="margin:0"><div>처음 청소한 ${esc(reclean.previousMaid)} 본인에게 자동 배정 · 다른 메이드에게 넘길 수 없음 · ${esc(reclean.reason)}</div></div>`:''}<button class="btn ${job==='upload'&&taskState(no).uploads.some(u=>u.status==='failed')?'btn-danger':'btn-primary'} btn-block" type="button" data-action="${action}" data-id="${no}">${labels[job]||'상세 보기'}</button></article>`;
  6091 |       }
  6092 |       function renderMaidMy() {
  6093 |         const maidId=signedInMaidId(),maidName=signedInMaidName(),activeCleaning=activeCleaningFor(maidId),own=Object.entries(state.jobs).filter(([no,v])=>['scheduled','claimed','cleaning','upload','inspection','approved','reclean'].includes(v)&&(ROOMS.find(r=>r.no===no)?.assignee===maidName||(['inspection','approved'].includes(v)&&currentSubmission(no)?.performerId===maidId))).map(([no])=>no);
  6094 |         const upcoming=notifiedAssignmentEntriesForMaid(maidId);
  6095 |         const upcomingNotice=upcoming.length?`<div class="assignment-notice">${icon('bell')}<div><p><strong>통보된 청소 일정 ${upcoming.length}건</strong><br>오늘·내일 날짜와 관리자가 확정한 순서입니다.</p><ol class="maid-assignment-route">${upcoming.map(({item,assignment})=>`<li><b>${assignment.order}</b><span>${esc(dateLabel(targetEffectiveDate(item)))} · ${item.room}호 · ${esc(item.kind)} · ${esc(assignmentScheduleText(item))}${assignment.activationBlockedBy?' · 관리자 확인 대기':''}</span></li>`).join('')}</ol></div></div>`:'';
```

## maid availability: `근무 가능일`

matches: 12

### occurrence 1 · line 2297

```html
  2281 |           ],
  2282 |           m2:[
  2283 |             {id:'pay-20260706-m2-528',room:'528',kind:'퇴실 청소',date:'7월 12일',base:20000},
  2284 |             {id:'pay-20260706-m2-540',room:'540',kind:'퇴실 청소',date:'7월 10일',base:20000},
  2285 |             {id:'pay-20260706-m2-639',room:'639',kind:'퇴실 청소',date:'7월 8일',base:20000},
  2286 |             {id:'pay-20260706-m2-350',room:'350',kind:'퇴실 청소',date:'7월 6일',base:16000}
  2287 |           ],
  2288 |           m3:[
  2289 |             {id:'pay-20260706-m3-332',room:'332',kind:'퇴실 청소',date:'7월 12일',base:20000},
  2290 |             {id:'pay-20260706-m3-536',room:'536',kind:'퇴실 청소',date:'7월 9일',base:20000},
  2291 |             {id:'pay-20260706-m3-639',room:'639',kind:'퇴실 청소',date:'7월 6일',base:20000}
  2292 |           ]
  2293 |         }
  2294 |       };
  2295 |       const SCENARIOS = {
  2296 |         0: { title:'기본 운영판', role:'admin', view:'today', next:'오늘 조치 큐와 일별 객실 현황을 탐색하세요.' },
  2297 |         1: { title:'일요일 다음 주 근무 가능일 제출', role:'maid', view:'schedule', next:'월·화·목·금을 선택하고 다음 주 가능일을 제출하세요.' },
  2298 |         2: { title:'자동 청소대상 → 담당·순서 지정 → 통보', role:'admin', view:'cleaning', next:'자동·직접 등록 대상을 확인하고 담당과 메이드별 객실 청소 순서를 지정하세요.' },
  2299 |         3: { title:'구역별 사진 → 업로드 실패/재시도 → 제출', role:'maid', view:'my', next:'528호 청소 상세에서 인증 사진을 완료하세요.' },
  2300 |         4: { title:'전체 검수 → 승인 또는 반려·재청소', role:'admin', view:'cleaning', next:'검수 대상 목록 탭에서 639호 전체 제출을 검수하세요.' },
  2301 |         5: { title:'촛불 1개 입실 차단 → 회수 → 준비 완료', role:'admin', view:'rooms', next:'350호 상세에서 촛불 1개를 회수하세요.' },
  2302 |         6: { title:'레이트 체크아웃 → PIN·청소 충돌 해결', role:'admin', view:'rooms', next:'332호 영향 확인에서 조율·재계획·PIN 교체를 완료하세요.' },
  2303 |         7: { title:'메이드 담당 취소 요청 → 관리자 결정', role:'admin', view:'today', next:'취소 요청 카드에서 승인 또는 거절하고 후속 처리를 고르세요.' },
  2304 |         8: { title:'활성 예약 → 연박 청소 → 배정 준비 작업', role:'admin', view:'rooms', next:'142호 상세에서 연박 청소를 생성하세요.' },
  2305 |         9: { title:'메이드 비활성 → 인계 → 업로드 전용', role:'admin', view:'maids', next:'김민지1 상세에서 영향을 확인하고 비활성 처리하세요.' },
  2306 |         10:{ title:'메이드별 지급 진행 → 외부 송금 완료 기록', role:'admin', view:'maids', next:'주급 정산에서 한 메이드의 지급 진행을 시작하고 외부 송금 완료까지 기록하세요.' },
  2307 |         11:{ title:'컴플레인 판정 → 확인/이의 → 종결', role:'admin', view:'maids', next:'김민지1 컴플레인 상세에서 판정하세요.' },
  2308 |         12:{ title:'날짜·필터·스크롤 복원', role:'admin', view:'rooms', next:'날짜와 필터를 바꾼 뒤 객실 상세에 들어갔다가 돌아오세요.' },
  2309 |         13:{ title:'목록 4상태와 오래된 데이터 행동 잠금', role:'admin', view:'today', next:'목록 상태 선택에서 불러오기·0건·필터 없음·오류를 전환하세요.' },
  2310 |         14:{ title:'전날 미배정·미완료 청소 다음 날 이월', role:'admin', view:'cleaning', next:'전일 이월 객실의 담당을 다시 정하고, 진행 중 청소는 같은 사진 상태로 이어지는지 확인하세요.' }
  2311 |       };
  2312 | 
  2313 |       function baseState(scenario = 0) {
  2314 |         const cfg = SCENARIOS[scenario] || SCENARIOS[0];
  2315 |         return {
  2316 |           scenario:Number(scenario), role:cfg.role, currentMaidId:'m1', adminView:cfg.role === 'admin' ? cfg.view : 'today', maidView:cfg.role === 'maid' ? cfg.view : 'my',
  2317 |           detail:null, returnContext:null, demoOpen:false, time:'10:32', network:'online', listMode:'data', loggedIn:true, loginMode:'normal',
  2318 |           selectedDate:'2026-08-15', calendarMonth:'2026-08', calendarContext:null, reservationWeekStart:'2026-08-10', reservationWeekRoom:null, roomFilter:'all', roomTypeFilter:'all', roomSearch:'', selectedDrafts:[], reservationSaved:false,
  2319 |           quickReservationAnchorDate:'2026-08-15', quickReservationFollowsToday:true, quickReservationType:'all', quickReservationSearch:'', quickGridScrollLeft:null, quickGridScrollTop:0, quickLastCreated:null,
  2320 |           reservationSequence:INITIAL_RESERVATIONS.length, reservations:initialReservationState(),
  2321 |           manualCleaningSequence:0, manualCleaningRequests:{}, checkoutInspections:{},
  2322 |           publications:{}, cancelRequests:{},
  2323 |           todaySections:{schedule:true,assignment:true,drafts:false,inspection:false,pay:false}, cleaningTab:'assignment-today', assignmentTypeFilter:'all', adminMaidTab:'workforce', adminPayWeek:'2026-08-03', workHistoryWeek:'2026-08-10', workHistoryMaid:'all',
  2324 |           drafts:[{id:'d536-next',room:'536',kind:'퇴실 청소',created:'09:55',date:'8월 16일'},...initialReservationDrafts()],
  2325 |           jobs:{'117':'scheduled','350':'inspection','332':'cleaning','528':'upload','536':'approved','639':'inspection','142':'stayover-requested','211':'draft','352':'approved'},
  2326 |           candles:{'117':0,'350':0,'332':0,'528':0,'536':0,'639':0,'142':0,'211':1,'352':0},
  2327 |           inspections:{'350':'pending','639':'pending'}, inspection:{room:'639',status:'pending',reclean:'none'}, earningsAddedByRoom:{}, earningRecords:{},
  2328 |           currentAttemptByRoom:{'117':'attempt-117-20260815-a','350':'attempt-350-20260815-a','332':'attempt-332-20260815-a','528':'attempt-528-20260815-a','639':'attempt-639-20260815-a'},
  2329 |           cleaningAttempts:{
  2330 |             'attempt-117-20260815-a':{id:'attempt-117-20260815-a',room:'117',performerId:'m1',performerName:'김민지1',status:'active',startedAt:null,workDate:'2026-08-15',workTargetId:'checkout-117-2026-08-15',kind:'퇴실 청소',baseRateSnapshot:20000,accessStart:'13:00',reservationIdSnapshot:'reservation-demo-117',guestCountSnapshot:2,checkoutSnapshot:'13:00',checkinSnapshot:'16:00',deadlineSnapshot:'15:30',nextReservationIdSnapshot:null},
  2331 |             'attempt-350-20260815-a':{id:'attempt-350-20260815-a',room:'350',performerId:'m3',performerName:'이서연',status:'submitted',startedAt:'2026.08.15 10:03',completedAt:'2026.08.15 10:46',workDate:'2026-08-15',workTargetId:'work-350-퇴실-청소-2026-08-15',kind:'퇴실 청소',baseRateSnapshot:16000},
```

### occurrence 2 · line 2604

```html
  2588 |       }
  2589 |       function unresolvedRecleanForMaid(maidId) {
  2590 |         for(const room of Object.keys(state.currentAttemptByRoom||{})){const attempt=activeRecleanAttempt(room);if(attempt?.performerId===maidId)return {room,attempt};}
  2591 |         return null;
  2592 |       }
  2593 |       function unfinishedCurrentAttemptsForMaid(maidId) {
  2594 |         return Object.keys(state.currentAttemptByRoom||{}).map(room=>({room,attempt:activeUnfinishedAttempt(room)})).filter(item=>item.attempt?.performerId===maidId);
  2595 |       }
  2596 |       function unresolvedCleaningConflictForMaid(maidId) {
  2597 |         if(state.conflict!=='active')return null;const room='332',attempt=state.cleaningAttempts?.[currentAttemptId(room)];return attempt?.performerId===maidId?{room,attempt}:null;
  2598 |       }
  2599 |       function activeCleaningFor(maidId=signedInMaidId()) { return state.activeCleaningByMaid?.[maidId]??(maidId==='m1'?state.activeCleaning:null); }
  2600 |       function setActiveCleaningFor(maidId,no) { if(!state.activeCleaningByMaid)state.activeCleaningByMaid=Object.fromEntries(MAIDS.map(maid=>[maid.id,maid.id==='m1'?state.activeCleaning||null:null]));state.activeCleaningByMaid[maidId]=no||null;if(maidId==='m1')state.activeCleaning=no||null; }
  2601 |       function syncSignedInMaidAvailability() { const record=state.weeklyAvailability?.[signedInMaidId()]||{days:[],status:'unsubmitted'};state.availabilityDraft=[...(record.days||[])];state.availabilitySubmitted=record.status==='submitted';state.availabilityEditing=false;state.availabilityChangeRequested=record.status==='change-requested'; }
  2602 |       const NOTIFICATION_SCHEMA_VERSION=1;
  2603 |       const NOTIFICATION_BUNDLE_WINDOW_MINUTES=10;
  2604 |       const NOTIFICATION_CATEGORY_LABELS={inspection:'청소 검수',assignment:'청소 배정',cancellation:'담당 취소',issue:'현장 문제',delay:'마감·지연',availability:'근무 가능일',complaint:'컴플레인·이의',conflict:'충돌·동기화',payroll:'주급',general:'업무 업데이트'};
  2605 | 
  2606 |       function notificationAudienceKey(role=state.role,maidId=role==='maid'?signedInMaidId():null){return role==='admin'?'admin':`maid:${maidId||signedInMaidId()}`;}
  2607 |       function notificationPushKey(role=state.role,maidId=role==='maid'?signedInMaidId():null){return notificationAudienceKey(role,maidId);}
  2608 |       function notificationSeedEvents(){return [
  2609 |         {id:'notification-seed-admin-inspection',title:'639호 청소 검수 요청',time:'10:18',createdAt:'2026-08-15 10:18',detail:'이서연이 전체 청소 제출을 완료했습니다.',roomId:'639',maidIds:[],notify:true,audience:['admin'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-inspection'},groupKey:'admin:inspection:639',readBy:[]},
  2610 |         {id:'notification-seed-admin-cancel',title:'332호 담당 취소 요청',time:'10:07',createdAt:'2026-08-15 10:07',detail:'김민지1 · 투숙객이 객실에 머물고 있음 · 결정 전 담당 유지',roomId:'332',maidIds:['m1'],notify:true,audience:['admin'],category:'cancellation',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'cancel-review'},groupKey:'admin:cancellation:332',readBy:[]},
  2611 |         {id:'notification-seed-admin-availability',title:'다음 주 가능일 전원 제출 완료',time:'09:30',createdAt:'2026-08-15 09:30',detail:'등록된 메이드 9명이 모두 근무 가능일을 제출했습니다.',maidIds:[],notify:true,audience:['admin'],category:'availability',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-workforce'},groupKey:'admin:availability:next-week',readBy:['admin']},
  2612 |         {id:'notification-seed-admin-handled',title:'350호 미배정 청소 조치 완료',time:'08:55',createdAt:'2026-08-15 08:55',detail:'담당 지정 완료 · 사건 기록 보존',roomId:'350',maidIds:[],notify:true,audience:['admin'],category:'assignment',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-cleaning-assignment',data:{day:'today'}},groupKey:'admin:assignment:350',readBy:['admin']},
  2613 |         {id:'notification-seed-maid-correction',title:'350호 보완 청소 요청',time:'10:05',createdAt:'2026-08-15 10:05',detail:'욕실 거울과 TV 전원 사진을 다시 확인해 주세요.',roomId:'350',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:inspection:350',readBy:[]},
  2614 |         {id:'notification-seed-maid-reminder',title:'332호 청소 시작 60분 전',time:'09:55',createdAt:'2026-08-15 09:55',detail:'오늘 10:55 시작 예정 · 예정 업무를 확인하세요.',roomId:'332',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'delay',priority:'normal',push:true,actionRequired:false,status:'open',target:{action:'go-my'},groupKey:'maid:m1:delay:332',readBy:[]},
  2615 |         {id:'notification-seed-maid-order',title:'117호 청소 순서 변경',time:'09:45',createdAt:'2026-08-15 09:45',detail:'2번째에서 1번째 청소로 변경되었습니다.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
  2616 |         {id:'notification-seed-maid-assignment',title:'117호 퇴실 청소 배정',time:'09:40',createdAt:'2026-08-15 09:40',detail:'오늘 13:00까지 완료해 주세요.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
  2617 |         {id:'notification-seed-maid-payroll',title:'이번 주 주급 정산 확정',time:'09:20',createdAt:'2026-08-15 09:20',detail:'객실별 승인 합계가 주급 내역에 반영되었습니다.',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'payroll',priority:'normal',push:false,pushOptional:true,actionRequired:false,status:'handled',target:{action:'go-maid-pay'},groupKey:'maid:m1:payroll:2026-08-10',readBy:['maid:m1']}
  2618 |       ];}
  2619 |       function nextNotificationEventId(){state.notificationSequence=Number(state.notificationSequence||0)+1;return `notification-${state.selectedDate||'demo'}-${state.time?.replace(':','')||'0000'}-${state.notificationSequence}`;}
  2620 |       function notificationMinuteValue(event){const text=String(event?.createdAt||`${state.selectedDate||'2026-08-15'} ${event?.time||'00:00'}`),match=text.match(/(\d{4})-(\d{2})-(\d{2})[^\d]?(\d{2}):(\d{2})/);if(!match)return 0;return Math.floor(Date.UTC(Number(match[1]),Number(match[2])-1,Number(match[3]),Number(match[4]),Number(match[5]))/60000);}
  2621 |       function notificationRoomFromText(title,detail,roomId=null){if(roomId)return String(roomId);return String(title||'').match(/(\d{3})호/)?.[1]||String(detail||'').match(/(\d{3})호/)?.[1]||null;}
  2622 |       function notificationMaidIdsForRoom(roomId){if(!roomId)return [];const submission=typeof currentSubmission==='function'?currentSubmission(String(roomId)):null,attempt=typeof currentAttemptId==='function'?state.cleaningAttempts?.[currentAttemptId(String(roomId))]:null,assignee=ROOMS.find(room=>room.no===String(roomId))?.assignee,assigneeId=MAIDS.find(maid=>maid.name===assignee)?.id;return [...new Set([submission?.performerId,attempt?.performerId,assigneeId].filter(id=>MAIDS.some(maid=>maid.id===id)))];}
  2623 |       function notificationMaidIdsForComplaint(){const item=(state.complaints||[]).find(entry=>!entry.deleted&&['unread','ruled','objected'].includes(entry.responseStatus))||(state.complaints||[])[0],maidId=MAIDS.find(maid=>maid.name===item?.maid)?.id;return maidId?[maidId]:[];}
  2624 |       function notificationCategoryFromText(text){if(/검수|전체 제출|보완|재청소/.test(text))return 'inspection';if(/배정|담당 변경|순서 변경|청소 취소 통보/.test(text))return 'assignment';if(/취소 요청|취소 승인|취소 거절|담당 취소/.test(text))return 'cancellation';if(/입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text))return 'issue';if(/마감|지연|미시작|60분 전|시작 시각/.test(text))return 'delay';if(/가능일/.test(text))return 'availability';if(/컴플레인|이의|판정/.test(text))return 'complaint';if(/충돌|동기화 실패|저장 충돌|오래된 데이터/.test(text))return 'conflict';if(/주급|지급|정산/.test(text))return 'payroll';return 'general';}
  2625 |       function notificationTargetFor(category,recipientRole,roomId,options={}){if(options.target)return options.target;if(recipientRole==='admin'){if(category==='inspection')return {action:'go-inspection'};if(category==='assignment'||category==='delay')return {action:'go-cleaning-assignment',data:{day:'today'}};if(category==='cancellation')return {action:'cancel-review'};if(category==='issue'||category==='conflict')return roomId?{action:'room-detail',id:roomId}:{action:'alerts'};if(category==='availability')return {action:'go-workforce'};if(category==='complaint')return {action:'complaint-detail'};if(category==='payroll')return {action:'go-payroll'};return {action:'alerts'};}if(category==='payroll')return {action:'go-maid-pay'};if(category==='availability')return {action:'go-schedule'};if(category==='complaint')return {action:'complaint-detail'};return {action:'go-my'};}
  2626 |       function notificationPolicyForEvent(title,detail,options={}){
  2627 |         if(options.notification===false)return null;
  2628 |         const actorRole=options.actorRole||state.role||'system',actorMaidId=options.actorMaidId||(actorRole==='maid'?signedInMaidId():null),text=`${title||''} ${detail||''}`,roomId=notificationRoomFromText(title,detail,options.roomId),requestedMaidIds=[...new Set((options.maidIds||[]).filter(id=>MAIDS.some(maid=>maid.id===id)))],category=options.category||notificationCategoryFromText(text);
  2629 |         if(options.notification&&typeof options.notification==='object'){
  2630 |           const explicit=options.notification,audience=[...new Set(explicit.audience||[])];if(!audience.length)return null;const recipientRole=audience[0]==='admin'?'admin':'maid';return {...explicit,audience,category:explicit.category||category,roomId,priority:explicit.priority||'normal',push:explicit.push!==false,actionRequired:explicit.actionRequired!==false,status:explicit.status||'open',target:notificationTargetFor(explicit.category||category,recipientRole,roomId,explicit),groupKey:explicit.groupKey||`${audience.join('|')}:${explicit.category||category}:${roomId||'general'}`,actorRole,actorMaidId};
  2631 |         }
  2632 |         if(actorRole==='maid'){
  2633 |           if(/청소 전체 제출|검수 요청|재검수 요청/.test(text))return {audience:['admin'],category:'inspection',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('inspection','admin',roomId),groupKey:`admin:inspection:${roomId||'general'}`,actorRole,actorMaidId};
  2634 |           if(/담당 취소 요청|취소 요청/.test(text))return {audience:['admin'],category:'cancellation',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('cancellation','admin',roomId),groupKey:`admin:cancellation:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2635 |           if(/이의 제출|입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text)){const adminCategory=/이의/.test(text)?'complaint':'issue';return {audience:['admin'],category:adminCategory,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(adminCategory,'admin',roomId),groupKey:`admin:${adminCategory}:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};}
  2636 |           if(/시작 지연|완료 지연|마감 초과/.test(text))return {audience:['admin'],category:'delay',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('delay','admin',roomId),groupKey:`admin:delay:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2637 |           return null;
  2638 |         }
```

### occurrence 3 · line 2611

```html
  2595 |       }
  2596 |       function unresolvedCleaningConflictForMaid(maidId) {
  2597 |         if(state.conflict!=='active')return null;const room='332',attempt=state.cleaningAttempts?.[currentAttemptId(room)];return attempt?.performerId===maidId?{room,attempt}:null;
  2598 |       }
  2599 |       function activeCleaningFor(maidId=signedInMaidId()) { return state.activeCleaningByMaid?.[maidId]??(maidId==='m1'?state.activeCleaning:null); }
  2600 |       function setActiveCleaningFor(maidId,no) { if(!state.activeCleaningByMaid)state.activeCleaningByMaid=Object.fromEntries(MAIDS.map(maid=>[maid.id,maid.id==='m1'?state.activeCleaning||null:null]));state.activeCleaningByMaid[maidId]=no||null;if(maidId==='m1')state.activeCleaning=no||null; }
  2601 |       function syncSignedInMaidAvailability() { const record=state.weeklyAvailability?.[signedInMaidId()]||{days:[],status:'unsubmitted'};state.availabilityDraft=[...(record.days||[])];state.availabilitySubmitted=record.status==='submitted';state.availabilityEditing=false;state.availabilityChangeRequested=record.status==='change-requested'; }
  2602 |       const NOTIFICATION_SCHEMA_VERSION=1;
  2603 |       const NOTIFICATION_BUNDLE_WINDOW_MINUTES=10;
  2604 |       const NOTIFICATION_CATEGORY_LABELS={inspection:'청소 검수',assignment:'청소 배정',cancellation:'담당 취소',issue:'현장 문제',delay:'마감·지연',availability:'근무 가능일',complaint:'컴플레인·이의',conflict:'충돌·동기화',payroll:'주급',general:'업무 업데이트'};
  2605 | 
  2606 |       function notificationAudienceKey(role=state.role,maidId=role==='maid'?signedInMaidId():null){return role==='admin'?'admin':`maid:${maidId||signedInMaidId()}`;}
  2607 |       function notificationPushKey(role=state.role,maidId=role==='maid'?signedInMaidId():null){return notificationAudienceKey(role,maidId);}
  2608 |       function notificationSeedEvents(){return [
  2609 |         {id:'notification-seed-admin-inspection',title:'639호 청소 검수 요청',time:'10:18',createdAt:'2026-08-15 10:18',detail:'이서연이 전체 청소 제출을 완료했습니다.',roomId:'639',maidIds:[],notify:true,audience:['admin'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-inspection'},groupKey:'admin:inspection:639',readBy:[]},
  2610 |         {id:'notification-seed-admin-cancel',title:'332호 담당 취소 요청',time:'10:07',createdAt:'2026-08-15 10:07',detail:'김민지1 · 투숙객이 객실에 머물고 있음 · 결정 전 담당 유지',roomId:'332',maidIds:['m1'],notify:true,audience:['admin'],category:'cancellation',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'cancel-review'},groupKey:'admin:cancellation:332',readBy:[]},
  2611 |         {id:'notification-seed-admin-availability',title:'다음 주 가능일 전원 제출 완료',time:'09:30',createdAt:'2026-08-15 09:30',detail:'등록된 메이드 9명이 모두 근무 가능일을 제출했습니다.',maidIds:[],notify:true,audience:['admin'],category:'availability',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-workforce'},groupKey:'admin:availability:next-week',readBy:['admin']},
  2612 |         {id:'notification-seed-admin-handled',title:'350호 미배정 청소 조치 완료',time:'08:55',createdAt:'2026-08-15 08:55',detail:'담당 지정 완료 · 사건 기록 보존',roomId:'350',maidIds:[],notify:true,audience:['admin'],category:'assignment',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-cleaning-assignment',data:{day:'today'}},groupKey:'admin:assignment:350',readBy:['admin']},
  2613 |         {id:'notification-seed-maid-correction',title:'350호 보완 청소 요청',time:'10:05',createdAt:'2026-08-15 10:05',detail:'욕실 거울과 TV 전원 사진을 다시 확인해 주세요.',roomId:'350',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:inspection:350',readBy:[]},
  2614 |         {id:'notification-seed-maid-reminder',title:'332호 청소 시작 60분 전',time:'09:55',createdAt:'2026-08-15 09:55',detail:'오늘 10:55 시작 예정 · 예정 업무를 확인하세요.',roomId:'332',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'delay',priority:'normal',push:true,actionRequired:false,status:'open',target:{action:'go-my'},groupKey:'maid:m1:delay:332',readBy:[]},
  2615 |         {id:'notification-seed-maid-order',title:'117호 청소 순서 변경',time:'09:45',createdAt:'2026-08-15 09:45',detail:'2번째에서 1번째 청소로 변경되었습니다.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
  2616 |         {id:'notification-seed-maid-assignment',title:'117호 퇴실 청소 배정',time:'09:40',createdAt:'2026-08-15 09:40',detail:'오늘 13:00까지 완료해 주세요.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
  2617 |         {id:'notification-seed-maid-payroll',title:'이번 주 주급 정산 확정',time:'09:20',createdAt:'2026-08-15 09:20',detail:'객실별 승인 합계가 주급 내역에 반영되었습니다.',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'payroll',priority:'normal',push:false,pushOptional:true,actionRequired:false,status:'handled',target:{action:'go-maid-pay'},groupKey:'maid:m1:payroll:2026-08-10',readBy:['maid:m1']}
  2618 |       ];}
  2619 |       function nextNotificationEventId(){state.notificationSequence=Number(state.notificationSequence||0)+1;return `notification-${state.selectedDate||'demo'}-${state.time?.replace(':','')||'0000'}-${state.notificationSequence}`;}
  2620 |       function notificationMinuteValue(event){const text=String(event?.createdAt||`${state.selectedDate||'2026-08-15'} ${event?.time||'00:00'}`),match=text.match(/(\d{4})-(\d{2})-(\d{2})[^\d]?(\d{2}):(\d{2})/);if(!match)return 0;return Math.floor(Date.UTC(Number(match[1]),Number(match[2])-1,Number(match[3]),Number(match[4]),Number(match[5]))/60000);}
  2621 |       function notificationRoomFromText(title,detail,roomId=null){if(roomId)return String(roomId);return String(title||'').match(/(\d{3})호/)?.[1]||String(detail||'').match(/(\d{3})호/)?.[1]||null;}
  2622 |       function notificationMaidIdsForRoom(roomId){if(!roomId)return [];const submission=typeof currentSubmission==='function'?currentSubmission(String(roomId)):null,attempt=typeof currentAttemptId==='function'?state.cleaningAttempts?.[currentAttemptId(String(roomId))]:null,assignee=ROOMS.find(room=>room.no===String(roomId))?.assignee,assigneeId=MAIDS.find(maid=>maid.name===assignee)?.id;return [...new Set([submission?.performerId,attempt?.performerId,assigneeId].filter(id=>MAIDS.some(maid=>maid.id===id)))];}
  2623 |       function notificationMaidIdsForComplaint(){const item=(state.complaints||[]).find(entry=>!entry.deleted&&['unread','ruled','objected'].includes(entry.responseStatus))||(state.complaints||[])[0],maidId=MAIDS.find(maid=>maid.name===item?.maid)?.id;return maidId?[maidId]:[];}
  2624 |       function notificationCategoryFromText(text){if(/검수|전체 제출|보완|재청소/.test(text))return 'inspection';if(/배정|담당 변경|순서 변경|청소 취소 통보/.test(text))return 'assignment';if(/취소 요청|취소 승인|취소 거절|담당 취소/.test(text))return 'cancellation';if(/입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text))return 'issue';if(/마감|지연|미시작|60분 전|시작 시각/.test(text))return 'delay';if(/가능일/.test(text))return 'availability';if(/컴플레인|이의|판정/.test(text))return 'complaint';if(/충돌|동기화 실패|저장 충돌|오래된 데이터/.test(text))return 'conflict';if(/주급|지급|정산/.test(text))return 'payroll';return 'general';}
  2625 |       function notificationTargetFor(category,recipientRole,roomId,options={}){if(options.target)return options.target;if(recipientRole==='admin'){if(category==='inspection')return {action:'go-inspection'};if(category==='assignment'||category==='delay')return {action:'go-cleaning-assignment',data:{day:'today'}};if(category==='cancellation')return {action:'cancel-review'};if(category==='issue'||category==='conflict')return roomId?{action:'room-detail',id:roomId}:{action:'alerts'};if(category==='availability')return {action:'go-workforce'};if(category==='complaint')return {action:'complaint-detail'};if(category==='payroll')return {action:'go-payroll'};return {action:'alerts'};}if(category==='payroll')return {action:'go-maid-pay'};if(category==='availability')return {action:'go-schedule'};if(category==='complaint')return {action:'complaint-detail'};return {action:'go-my'};}
  2626 |       function notificationPolicyForEvent(title,detail,options={}){
  2627 |         if(options.notification===false)return null;
  2628 |         const actorRole=options.actorRole||state.role||'system',actorMaidId=options.actorMaidId||(actorRole==='maid'?signedInMaidId():null),text=`${title||''} ${detail||''}`,roomId=notificationRoomFromText(title,detail,options.roomId),requestedMaidIds=[...new Set((options.maidIds||[]).filter(id=>MAIDS.some(maid=>maid.id===id)))],category=options.category||notificationCategoryFromText(text);
  2629 |         if(options.notification&&typeof options.notification==='object'){
  2630 |           const explicit=options.notification,audience=[...new Set(explicit.audience||[])];if(!audience.length)return null;const recipientRole=audience[0]==='admin'?'admin':'maid';return {...explicit,audience,category:explicit.category||category,roomId,priority:explicit.priority||'normal',push:explicit.push!==false,actionRequired:explicit.actionRequired!==false,status:explicit.status||'open',target:notificationTargetFor(explicit.category||category,recipientRole,roomId,explicit),groupKey:explicit.groupKey||`${audience.join('|')}:${explicit.category||category}:${roomId||'general'}`,actorRole,actorMaidId};
  2631 |         }
  2632 |         if(actorRole==='maid'){
  2633 |           if(/청소 전체 제출|검수 요청|재검수 요청/.test(text))return {audience:['admin'],category:'inspection',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('inspection','admin',roomId),groupKey:`admin:inspection:${roomId||'general'}`,actorRole,actorMaidId};
  2634 |           if(/담당 취소 요청|취소 요청/.test(text))return {audience:['admin'],category:'cancellation',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('cancellation','admin',roomId),groupKey:`admin:cancellation:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2635 |           if(/이의 제출|입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text)){const adminCategory=/이의/.test(text)?'complaint':'issue';return {audience:['admin'],category:adminCategory,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(adminCategory,'admin',roomId),groupKey:`admin:${adminCategory}:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};}
  2636 |           if(/시작 지연|완료 지연|마감 초과/.test(text))return {audience:['admin'],category:'delay',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('delay','admin',roomId),groupKey:`admin:delay:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2637 |           return null;
  2638 |         }
  2639 |         if(actorRole==='admin'){
  2640 |           let targetMaidIds=[...requestedMaidIds];
  2641 |           if(/전체 제출 승인|검수 승인|전체 제출 반려|보완 청소|재청소/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForRoom(roomId);
  2642 |           if(/컴플레인 판정|이의 답변/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForComplaint();
  2643 |           const maidNotice=/^내 |통보|안내|배정|담당 변경|순서 변경|취소|시작 시각|보류|시작 가능|전체 제출 승인|검수 승인|전체 제출 반려|보완|재청소|컴플레인 판정|이의 답변|주급|지급|마감|지연|비활성/.test(text);
  2644 |           if(targetMaidIds.length&&maidNotice){const audience=targetMaidIds.map(id=>`maid:${id}`),informational=/승인|종결|확정|지급 완료|처리 결과|비활성 완료/.test(text)&&!/보완|재청소|지연|마감/.test(text),priority=/긴급|보완|재청소|반려|지연|마감|취소/.test(text)?'high':'normal',pushOptional=category==='payroll'&&/정산 확정/.test(text);return {audience,category,roomId,priority,push:!pushOptional,pushOptional,actionRequired:!informational,status:informational?'handled':'open',target:notificationTargetFor(category,'maid',roomId),groupKey:`${audience.join('|')}:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
  2645 |           if(/미배정.*남|미배정 청소|가능일.*미제출|동기화 실패|저장 충돌|주급.*오류|지급.*예외/.test(text)){return {audience:['admin'],category,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(category,'admin',roomId),groupKey:`admin:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
```

### occurrence 4 · line 3129

```html
  3113 |         root.querySelectorAll('.cleaning-section-body > .audit-note,.room-issue-form > .audit-note,.bomb-room-editor > .audit-note').forEach(note=>{if(/현재 탭|실제 서버|영속|흐름만 검증|지원 기기/.test(note.textContent))note.remove();});
  3114 |         root.querySelectorAll('.photo-template-banner .badge-row').forEach(row=>{if(!row.children.length)row.remove();});
  3115 |         root.querySelectorAll('.timeline li span').forEach(copy=>{copy.textContent=adminAuditSummary(copy.textContent.replace(/\s*·\s*(?:이력 보존|조건 미충족)$/,''));});
  3116 |         root.querySelectorAll('.photo-meta .info-item').forEach(item=>{const label=item.querySelector('span');if(label&&/제출 버전|관리자 결정·회차|보존 상태/.test(label.textContent))item.remove();});
  3117 |         root.querySelectorAll('.photo-viewer-visual + .photo-meta ~ .audit-note').forEach(note=>note.remove());
  3118 |         const modalTitle=root.querySelector('#modal-title'),modalDescription=root.querySelector('#modal-desc');
  3119 |         if(modalTitle?.textContent.includes('내 업무 이력'))modalTitle.textContent='내 업무 이력';
  3120 |         if(modalTitle?.textContent.includes('내 알림'))modalTitle.textContent='내 알림';
  3121 |         if(modalTitle?.textContent.includes('알림 상태'))modalTitle.textContent='알림 상태';
  3122 |         if(modalTitle?.textContent.includes('알림을 켤까요'))modalTitle.textContent='알림을 켤까요?';
  3123 |         if(modalDescription&&/본인 담당·수행·응답 기록|이 브라우저|실제 운영에서는 브라우저 권한/.test(modalDescription.textContent))modalDescription.remove();
  3124 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3125 |           if(/허용 여부와 관계없이 앱 내부 알림/.test(notice.textContent)){notice.textContent='기기 알림을 켜도 앱 안 알림은 그대로 확인할 수 있습니다.';return;}
  3126 |           if(/정적 데모|정적 파일|현재 탭 메모리|브라우저의 화면 상태/.test(notice.textContent))notice.remove();
  3127 |         });
  3128 |         root.querySelectorAll('.rail-row span').forEach(copy=>{copy.textContent=copy.textContent.replace(/\s*·\s*내 담당 작업만 표시/g,'').replace(/\s*·\s*본인 기록만 확인/g,'').replace(/\s*·\s*객실별 합계/g,'');});
  3129 |         addAdminHelp(root,'8월 17일 (월)–8월 23일 (일)','maid-schedule','근무 가능일','일요일 12:00부터 23:59까지 다음 주에 일할 수 있는 요일을 모두 고른 뒤 제출하세요. 객실과 순서는 관리자가 각 근무일 전날 배정합니다.');
  3130 |         addAdminHelp(root,'배정된 내 업무','maid-assigned','배정된 업무','관리자가 통보한 업무만 표시합니다. 담당이나 순서가 바뀌면 알림에서 확인할 수 있습니다.');
  3131 |         root.querySelectorAll('.mobile-section-title h2').forEach((heading,index)=>{if(heading.textContent.trim().startsWith('내 업무 '))addAdminHelpToElement(heading,`maid-my-${index}`,'내 업무','관리자가 통보한 업무만 표시하며 청소는 한 번에 한 객실씩 진행합니다.');});
  3132 |         addAdminHelp(root,'지금까지 주급 내역','maid-pay','주급 내역','월요일부터 일요일까지 관리자 승인을 받은 청소비를 합산합니다. 검수 대기는 예상 금액에만 표시되고, 폭탄방 승인 시 해당 객실 기본요금과 같은 추가요금이 반영됩니다. 컴플레인·벌점은 자동 차감되지 않습니다.');
  3133 |         const cameraBanner=root.querySelector('.cleaning-sections .photo-template-banner');
  3134 |         if(cameraBanner&&!cameraBanner.previousElementSibling?.classList.contains('task-photo-help')){
  3135 |           const help=document.createElement('div');help.className='help-title task-photo-help';help.innerHTML=`<h3>촬영 방법</h3>${infoTip(`maid-camera-${state.detail?.id||'task'}`,'촬영 방법','구역별 인증 사진을 촬영하세요. 바로 촬영은 후면 카메라를 열고 갤러리는 저장된 사진을 선택합니다. 다시 촬영하면 해당 사진을 교체합니다.')}`;cameraBanner.before(help);
  3136 |         }
  3137 |         const notificationCard=[...root.querySelectorAll('.setting-card')].find(card=>card.querySelector('h3')?.textContent.trim()==='알림 설정');
  3138 |         if(notificationCard){const heading=notificationCard.querySelector('h3');addAdminHelpToElement(heading,'maid-notifications','알림 설정','기기 알림을 끄더라도 앱 안의 배정 변경·검수·주급 알림은 계속 확인할 수 있습니다.');}
  3139 |         const replacements=new Map([
  3140 |           ['데모 메모리 이미지','사진'],['현재 원장','현재 합계'],['객실별 원장','객실별 청소 내역'],['수익 원장','청소비 내역'],['새 청소비 내역','추가 청소비'],['스냅샷','기준'],['fixture','데모 기록'],['수행 회차','청소 작업'],['회차 종료','청소 종료'],['제출 버전','제출 내용'],['데모 지급 이력','지급 이력'],['데모 금액','금액'],['브라우저 세션','현재 기록']
  3141 |         ]);
  3142 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3143 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\b(?:ATT|SUB|REPORT|PAY|LEASE|work|target)-[A-Za-z0-9-]+\b/gi,'').replace(/\s*·\s*v\d+(?:\.\d+)?\b/gi,'').replace(/\s*·\s*데모(?:\s+(?:기록|지급 이력|금액))?/g,'').replace(/\(데모\)/g,'').replace(/\s{2,}/g,' ');node.nodeValue=value;});
  3144 |       }
  3145 | 
  3146 |       function applyAdminCopyPolicy(root) {
  3147 |         if(state.role==='maid'){applyMaidCopyPolicy(root);return;}
  3148 |         if(state.role!=='admin')return;
  3149 |         root.querySelectorAll('.work-history-person-head p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.replace(/^당시 이름 스냅샷\s*·\s*/,'').replace(/\s*·\s*제출 버전.*$/,'');});
  3150 |         root.querySelectorAll('.pay-ledger-room p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.split(' · ').slice(0,3).join(' · ');});
  3151 |         root.querySelectorAll('.audit-note,.scenario-coach,.mobile-section-title p,.quick-booking-boundary,.quick-booking-guide-copy,.quick-booking-summary small,.quick-grid-status span:last-child,.assignment-random-copy p,.random-rule,.maid-order-lane-head p,.assignment-panel-head p,.maid-order-unassigned p,.assignment-target-rule,.work-history-unit-note,.work-history-contract,.work-history-hero p,.tab-header p,.pay-week-toolbar p,.pay-ledger-reconcile,.template-page > .notice-info,.template-row-version,.template-hero-stat,.template-hero p,.template-evidence,.template-timeline').forEach(element=>element.remove());
  3152 |         root.querySelectorAll('.cleaning-cost-foot').forEach(foot=>{const range=foot.querySelector('b');foot.replaceChildren(range||document.createTextNode(''));});
  3153 |         const costCard=root.querySelector('.cleaning-cost-card');
  3154 |         if(costCard)costCard.setAttribute('aria-label',`청소비 예상 지출. 오늘과 이번 주 금액을 확인하고 주급 정산으로 이동합니다.`);
  3155 |         const assignmentIntro=root.querySelector('.assignment-intro p');if(assignmentIntro)assignmentIntro.textContent=assignmentIntro.textContent.split(' · ')[0];
  3156 |         root.querySelectorAll('.assignment-normal,.assignment-table .cell-sub').forEach(element=>element.remove());
  3157 |         root.querySelectorAll('.assignment-route-reference').forEach(element=>{if(element.textContent.includes('담당 선택 후'))element.remove();});
  3158 |         const randomKicker=root.querySelector('.random-kicker');if(randomKicker)randomKicker.textContent='미배정 객실 자동 분배';
  3159 |         const randomLive=root.querySelector('.random-live');if(randomLive)randomLive.textContent=state.randomAssignmentSnapshot?`${state.randomAssignmentSummary?.assigned||0}건 배정됨 · 아래에서 수정하세요`:'미배정 객실만 배정합니다.';
  3160 |         const filterContext=root.querySelector('.assignment-filter-context span');if(filterContext)filterContext.innerHTML=`<strong>${esc(ROOM_TYPES[state.assignmentTypeFilter]?.name||'전체 객실 타입')}</strong> · 배정된 객실만 저장·통보`;
  3161 |         root.querySelectorAll('.template-group-head p').forEach(paragraph=>{paragraph.textContent=`${paragraph.textContent.split(' · ')[0]} · 기본 청소요금`;});
  3162 |         root.querySelectorAll('.template-group-head > .badge').forEach(badge=>badge.remove());
  3163 |         root.querySelectorAll('[data-action="admin-pay-detail"]').forEach(button=>{
```

### occurrence 5 · line 3174

```html
  3158 |         const randomKicker=root.querySelector('.random-kicker');if(randomKicker)randomKicker.textContent='미배정 객실 자동 분배';
  3159 |         const randomLive=root.querySelector('.random-live');if(randomLive)randomLive.textContent=state.randomAssignmentSnapshot?`${state.randomAssignmentSummary?.assigned||0}건 배정됨 · 아래에서 수정하세요`:'미배정 객실만 배정합니다.';
  3160 |         const filterContext=root.querySelector('.assignment-filter-context span');if(filterContext)filterContext.innerHTML=`<strong>${esc(ROOM_TYPES[state.assignmentTypeFilter]?.name||'전체 객실 타입')}</strong> · 배정된 객실만 저장·통보`;
  3161 |         root.querySelectorAll('.template-group-head p').forEach(paragraph=>{paragraph.textContent=`${paragraph.textContent.split(' · ')[0]} · 기본 청소요금`;});
  3162 |         root.querySelectorAll('.template-group-head > .badge').forEach(badge=>badge.remove());
  3163 |         root.querySelectorAll('[data-action="admin-pay-detail"]').forEach(button=>{
  3164 |           button.textContent=button.textContent.replace('산출 보기','상세 보기');
  3165 |           button.setAttribute('aria-label',(button.getAttribute('aria-label')||'').replace(/현재 원장/g,'현재 합계').replace(/산출 근거 보기/g,'청소 내역 보기'));
  3166 |         });
  3167 |         root.querySelectorAll('.toggle-row span').forEach(span=>{if(['외부 송금을 시작하기 전입니다.','확정 지급액이 생기면 이 자리에서 기록합니다.'].includes(span.textContent.trim()))span.remove();});
  3168 |         const quickCopy=root.querySelector('.quick-booking-hero-copy');
  3169 |         if(quickCopy)quickCopy.innerHTML=`<span class="quick-booking-kicker">빠른 예약 등록</span><div class="help-title"><h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking','간편 예약','빈 날짜를 클릭하거나 같은 객실 행에서 가로로 드래그하세요. 터치는 0.35초 길게 누른 뒤 드래그합니다. 한 번 선택한 범위는 예약 한 건으로 저장됩니다.')}</div>`;
  3170 |         root.querySelectorAll('p').forEach(paragraph=>{if(!paragraph.closest('.notice')&&/서버 영속|fixture|스냅샷|불변 사용자 ID|PIN lease|식별값|이력 연결키|원장 비연결|예약 가능과 현재 입실 가능을 별도로 판단|사진 원본은 앱에 저장하지 않음/.test(paragraph.textContent))paragraph.remove();});
  3171 |         root.querySelectorAll('.meta').forEach(meta=>{if(/데모|스냅샷|정본/.test(meta.textContent))meta.remove();});
  3172 |         addAdminHelp(root,'총 청소요금을 먼저 맞추고 가까운 객실로 배정','random-assignment','랜덤 배정','근무 가능한 메이드의 총 청소요금이 비슷해지도록 먼저 나누고, 같은 엘리베이터와 가까운 호수를 다음 기준으로 사용합니다. 결과는 저장 전에 담당과 순서를 바꿀 수 있습니다.',{rename:'랜덤 배정'});
  3173 |         addAdminHelp(root,'메이드별 청소 순서 수정','assignment-result','청소 순서 수정','얼리 체크인·레이트 체크아웃의 예정 시각을 먼저 확인하고, 객실별 담당 메이드를 바꾸거나 위·아래 버튼으로 1번부터 순서를 정하세요. 담당과 순서가 정해진 객실만 저장·통보됩니다.');
  3174 |         addAdminHelp(root,'내일 청소 배정','next-day-assignment','내일 청소 배정','근무 가능일을 제출한 메이드에게만 배정할 수 있습니다. 랜덤 배정 뒤에도 객실별 담당과 메이드별 청소 순서를 직접 바꾼 다음 저장·통보하세요.');
  3175 |         addAdminHelp(root,'주간 근무 기록','work-history','주간 근무 기록','명은 해당 기록이 있는 메이드 수이고, 일은 메이드별 기록 날짜를 합한 값입니다. 가능 제출·담당 통보·실근무 완료를 서로 다른 표시로 확인합니다.');
  3176 |         addAdminHelp(root,'주별 지급 이력','weekly-pay','주별 지급 이력','월요일부터 일요일까지의 승인 청소를 합산합니다. 검수 대기는 예상액에만, 전체 반려와 본인 재청소는 0원으로 표시됩니다.');
  3177 |         addAdminHelp(root,'객실 기본정보','room-basics','객실 기본정보','관리자는 객실 타입과 엘리베이터를 수정할 수 있습니다. 변경값은 새로 만드는 작업부터 적용되고 객실번호는 이 화면에서 바꿀 수 없습니다.');
  3178 |         addAdminHelp(root,'현재 투숙 상태','occupancy','현재 투숙 상태','투숙 중에는 지금 체크아웃하거나 투숙 중 청소를 요청할 수 있습니다. 지금 체크아웃하면 공실·청소 필요 상태로 바뀝니다.');
  3179 |         addAdminHelp(root,'예약·입퇴실','reservation-times','예약·입퇴실','한 고객의 체크인부터 체크아웃 순서로 입력합니다. 체크인 16:00보다 빠르거나 체크아웃 11:00보다 늦으면 자동으로 표시되고, 체크아웃 날짜에 퇴실 청소가 추가됩니다.');
  3180 |         addAdminHelp(root,'타입별 촬영 구역을 확인하세요','templates','청소 템플릿','객실 타입과 실제 침실·욕실 수에 맞춰 촬영 구역을 정합니다. 수정한 내용은 새 작업부터 적용됩니다. 연락처·얼굴·고객 물품은 제외하고, TV는 켠 뒤 계정·QR·알림 없는 기본 화면을 촬영합니다.',{rename:'타입별 청소 템플릿'});
  3181 |         root.querySelectorAll('h3').forEach((heading,index)=>{if(/^왜 .+인가요\?$/.test(heading.textContent.trim()))addAdminHelpToElement(heading,`pay-detail-${index}`,'주급 계산','확정된 객실별 청소요금을 합산합니다. 폭탄방은 해당 객실만 기본요금을 한 번 더하고, 검수 대기 금액은 확정 주급에 포함하지 않습니다.');});
  3182 |         root.querySelectorAll('h3').forEach(heading=>{
  3183 |           const text=heading.textContent.trim();
  3184 |           if(text==='계산 규칙'||text==='객실 사건 타임라인')heading.closest('.card')?.remove();
  3185 |           if(text==='폭탄방 요금 원장')heading.textContent='폭탄방 청소비';
  3186 |           if(text==='저장된 전체 과거 주차')heading.textContent='과거 주차';
  3187 |         });
  3188 |         root.querySelectorAll('th').forEach(heading=>{if(heading.textContent.trim()==='청소 정보·등록 근거')heading.textContent='청소 유형';});
  3189 |         root.querySelectorAll('#modal-desc').forEach(description=>{
  3190 |           if(/이력 연결키|식별값/.test(description.textContent))description.textContent='객실 타입과 엘리베이터를 수정합니다.';
  3191 |           if(/시트 정본|예상시간만 데모/.test(description.textContent))description.textContent='객실 타입별 청소요금과 예상시간을 확인합니다.';
  3192 |         });
  3193 |         root.querySelectorAll('.field small').forEach(note=>{if(/PIN·청소·주급 이력|식별값/.test(note.textContent))note.remove();});
  3194 |         root.querySelectorAll('.field label').forEach(label=>{if(/예약 식별|예약 ID/.test(label.textContent))label.closest('.field')?.remove();});
  3195 |         root.querySelectorAll('.info-item').forEach(item=>{
  3196 |           const label=item.querySelector('span'),value=item.querySelector('strong');if(!label||!value)return;
  3197 |           if(/PIN lease 영향|lease 영향/.test(label.textContent)){label.textContent='PIN 조회 처리';value.textContent='기존 조회 종료 후 다시 확인';}
  3198 |           if(/이전 PIN lease/.test(label.textContent)){label.textContent='이전 PIN 조회';value.textContent='종료됨';}
  3199 |           if(/활성 PIN lease/.test(label.textContent)){label.textContent='활성 PIN 조회';value.textContent=value.textContent.replace(/^[^·]+/,'1건');}
  3200 |         });
  3201 |         root.querySelectorAll('.choice').forEach(choice=>{
  3202 |           const title=choice.querySelector('strong'),copy=title?.nextElementSibling;if(!title||!copy)return;
  3203 |           if(title.textContent.includes('작업 재계획 완료')){title.textContent='청소 일정 변경 완료';copy.textContent=copy.textContent.replace('기존 수행 회차','진행 중 청소').replace('새 회차','새 청소');}
  3204 |           if(title.textContent.includes('필요 PIN 교체')){title.textContent='도어락 PIN 확인 완료';copy.textContent='기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.';}
  3205 |         });
  3206 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3207 |           if(/새 작업은 시트 청소요금을 스냅샷|기존 확정 이력은 당시 기록|새 담당 구간이 타임라인/.test(notice.textContent))notice.textContent=/담당/.test(notice.textContent)?'저장하면 담당 메이드에게 통보됩니다.':'변경한 청소요금은 새 작업부터 적용됩니다.';
  3208 |           if(/새 타입·엘리베이터는 이후 생성하는 작업/.test(notice.textContent))notice.textContent='변경한 정보는 새 작업부터 적용됩니다.';
```

### occurrence 6 · line 4027

```html
  4011 |         return {id,minutes};
  4012 |       }
  4013 |       function openTemplateReview(id) {
  4014 |         const template=templateById(id),change=readTemplateChange(id);if(!template||!change)return;
  4015 |         pendingTemplateChange=change;rememberCurrentHistoryRoute();
  4016 |         const nextVersion=`v${Number(template.version.replace(/\D/g,''))+1}`;
  4017 |         showModal({title:'템플릿 변경 내용 확인',subtitle:`${ROOM_TYPES[template.typeId].name} · ${template.name} · 데모`,body:`<div class="template-review-summary"><div class="template-review-row"><span>활성 버전</span><strong>${esc(template.version)} → ${esc(nextVersion)}</strong></div><div class="template-review-row"><span>예상시간 · 데모</span><strong>${template.minutes}분 → ${change.minutes}분</strong></div><div class="template-review-row"><span>촬영 규칙</span><strong>인증 ${template.photos.filter(item=>item.required).length}개 · 기타 ${template.photos.filter(item=>!item.required).length}개</strong></div></div><div class="notice notice-warning" style="margin:12px 0 0">사진 구역은 유지되고 예상시간 변경은 새 작업부터 적용됩니다.</div>`,confirmLabel:'변경 저장·활성',confirmAction:'template-save',confirmVariant:'primary',historyKind:'template-review',historyPayload:change});
  4018 |         document.querySelector('[data-action="template-save"]')?.setAttribute('data-id',id);
  4019 |       }
  4020 | 
  4021 |       function titleForView() {
  4022 |         if (state.detail) {
  4023 |           const map={room:`${state.detail.id}호 객실 상세`,cleaning:`${state.detail.id}호 청소 상세`,maid:`${maidById(state.detail.id)?.name||'메이드'} 상세`,complaint:'컴플레인·벌점 상세',pay:'주급 정산 상세',templates:'청소 템플릿 설정',template:'청소 템플릿 상세'};
  4024 |           return map[state.detail.type]||'상세';
  4025 |         }
  4026 |         const admin={today:'오늘 할 일',rooms:'객실 현황',quickReservation:'간편 예약',cleaning:'청소 관리',maids:'메이드',more:'더보기'};
  4027 |         const maid={my:'내 업무',schedule:'다음 주 근무 가능일',alerts:'알림',pay:'내 주급',more:'더보기'};
  4028 |         return (state.role==='admin'?admin:maid)[currentView()]||'객실관리';
  4029 |       }
  4030 | 
  4031 |       function renderMain() {
  4032 |         if (!state.loggedIn) return renderLogin();
  4033 |         if (state.detail) return renderDetail();
  4034 |         if (state.role==='admin') {
  4035 |           if (state.adminView==='today') return renderAdminToday();
  4036 |           if (state.adminView==='rooms') return renderRooms();
  4037 |           if (state.adminView==='quickReservation') return renderQuickReservation();
  4038 |           if (state.adminView==='cleaning') return renderCleaningHub();
  4039 |           if (state.adminView==='maids') return renderMaids();
  4040 |           return renderAdminMore();
  4041 |         }
  4042 |         if (state.maidView==='my') return renderMaidMy();
  4043 |         if (state.maidView==='schedule') return renderMaidSchedule();
  4044 |         if (state.maidView==='alerts') return renderMaidAlerts();
  4045 |         if (state.maidView==='pay') return renderMaidPay();
  4046 |         return renderMaidMore();
  4047 |       }
  4048 | 
  4049 |       function renderTopbar() {
  4050 |         const alertCount=notificationUnreadCount(notificationAudienceKey()),countMarkup=alertCount?`<span class="count-dot">${alertCount}</span>`:'';
  4051 |         return `<header class="topbar"><div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 ${state.selectedDate.replaceAll('-','.')} ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div><div class="topbar-actions"><button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기 · 안 읽음 ${alertCount}건">${icon('bell')}${countMarkup}</button><button class="btn btn-outline" type="button" data-action="switch-role" aria-label="${state.role==='admin'?'메이드 보기':'관리자 보기'}">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button></div></header>`;
  4052 |       }
  4053 | 
  4054 |       function dateObject(value=state.selectedDate) {
  4055 |         const [y,m,d]=value.split('-').map(Number);
  4056 |         return new Date(y,m-1,d);
  4057 |       }
  4058 |       function dateIso(date) {
  4059 |         return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
  4060 |       }
  4061 |       function calendarDayMeta(iso) {
```

### occurrence 7 · line 5361

```html
  5345 |       }
  5346 |       function assignmentSourceMarkup(item) {
  5347 |         const cls=item.source==='manual'?'manual':item.source==='stayover'?'stayover':'',label=item.sourceLabel||'직접 등록';
  5348 |         const rollover=item.carryReason?`<span class="assignment-source stayover">${icon('clock','icon-sm')}${item.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료'}</span>`:'';
  5349 |         return `${rollover}<span class="assignment-source ${cls}">${icon(item.source==='manual'?'user':'sync','icon-sm')}${item.source==='manual'?'직접 등록':`자동 · ${esc(label)}`}</span>`;
  5350 |       }
  5351 |       function assignmentAdjustmentMarkup(item) {
  5352 |         const assignment=assignmentFor(item),activationBlocked=!!assignment.activationBlockedBy&&targetEffectiveDate(item)===state.selectedDate,status=activationBlocked?'활성화 보류':assignment.status==='notified'?'통보 완료':assignment.maidId?'저장 전':'미배정',tone=activationBlocked?'amber':assignment.status==='notified'?'green':assignment.maidId?'amber':'red',notified=!!(assignment.previousMaidId||assignment.status==='notified'),block=cleaningTargetAdjustmentBlock(item),label=notified?'청소 취소·통보':'청소대상 취소';
  5353 |         return `<div class="assignment-cell-stack">${statusBadge(status,tone)}${assignment.maidId?'<span class="cell-sub">순서 보드 반영</span>':''}${button(label,'cancel-cleaning-target','outline',`data-target="${esc(item.id)}" aria-label="${esc(dateLabel(targetEffectiveDate(item)))} ${item.room}호 ${esc(label)}" ${block?'disabled':''}`)}${block?`<span class="cell-sub">${esc(block)}</span>`:''}</div>`;
  5354 |       }
  5355 |       function renderAssignmentDashboard() {
  5356 |         const counts=assignmentCounts(),targets=assignmentTargets(),visibleTargets=filteredAssignmentTargets(),activeType=state.assignmentTypeFilter==='all'?null:ROOM_TYPES[state.assignmentTypeFilter];
  5357 |         const rows=visibleTargets.map(item=>{const context=assignmentContext(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item);return `<tr><td data-label="객실·타입·요금"><div class="assignment-cell-stack"><strong>${item.room}호</strong><span class="assignment-room-type">${esc(context.type.name)}</span><span class="assignment-elevator">${icon('mapPin','icon-sm')}${esc(elevatorLabel(context.room))}</span><span class="assignment-fee">${money(context.type.rate)} · 8월 시트</span></div></td><td data-label="청소 정보"><div class="assignment-cell-stack"><strong>${esc(item.kind)}</strong>${assignmentSourceMarkup(item)}</div></td><td data-label="일정">${assignmentScheduleMarkup(item)}</td><td data-label="담당 메이드"><div class="assignment-assignee"><select class="select-control" data-control="assignment-maid" data-location="table" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 · 근무 가능 제출자만 표시" ${adjustmentBlock?'disabled':''}>${assignmentOptions(item)}</select>${assignmentRouteReference(item)}</div></td><td data-label="상태·조정">${assignmentAdjustmentMarkup(item)}</td></tr>`;}).join('');
  5358 |         const history=state.assignmentHistory.map(entry=>`<div class="assignment-history-row"><strong>${esc(entry.time)}</strong><span>${esc(entry.room)}호</span><span>${esc(entry.before)} → ${esc(entry.after)}</span><span>${esc(entry.reason)}</span></div>`).join('');
  5359 |         const emptyRows=`<tr><td colspan="5"><div class="inline-empty"><h3>이 타입의 청소대상이 없습니다</h3><p>다른 타입을 선택하거나 전체 객실을 확인하세요.</p></div></td></tr>`;
  5360 |         const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일',weekStart=weekStartIso(state.assignmentDate),weekEnd=addIsoDays(weekStart,6);
  5361 |         return `<div class="assignment-page"><div class="assignment-intro"><div><h2>${dayWord} 청소 배정</h2><p>${dateLabel(state.assignmentDate)} · 근무표 확인 → 동선 고려 랜덤 초안 → 담당·순서 수정 → 저장·통보</p></div><div class="job-actions">${button('주간 근무 기록','go-work-history','outline')}${button(`${dayWord} 청소 추가`,'new-cleaning','outline')}</div></div><section class="card assignment-summary"><div><span>근무 가능일 제출</span><strong>${counts.submitted} / ${MAIDS.length}</strong><small>메이드 제출 현황</small></div><div><span>${dayWord} 청소 대상 객실</span><strong>${counts.total}</strong><small>전일 이월 ${counts.carryover} · 신규 ${counts.total-counts.carryover}</small></div><div class="summary-good"><span>담당 선택</span><strong>${counts.assigned}</strong><small>통보 완료 ${counts.notified}건</small></div><div class="summary-warn"><span>미배정</span><strong>${counts.unassigned}</strong><small>대기 유지 · 후속 배정 가능</small></div></section><section class="assignment-target-rule" aria-label="청소대상 자동 구성">${icon('sync')}<div><strong>${dayWord} 체크아웃·투숙 중 청소·전일 이월 객실을 한 목록에 모읍니다.</strong><p>${dayWord} 생긴 현장 요청은 직접 추가하고, 미시작 대상은 사유를 남겨 취소·통보할 수 있습니다.</p></div><div class="badge-row">${statusBadge(`전일 이월 ${counts.carryover}`,'amber')}${statusBadge(`체크아웃 ${counts.checkout}`,'blue')}${statusBadge(`연박 ${counts.stayover}`,'neutral')}${statusBadge(`직접 ${counts.manual}`,'amber')}</div></section><section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>${dateLabel(weekStart)}–${dateLabel(weekEnd)} · Asia/Seoul</p></div>${statusBadge(`${counts.submitted}/${MAIDS.length} 제출`,counts.submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section>${renderRandomAssignmentCard()}<section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">3단계 · 세부 수정</span><h3>객실별 담당 수정</h3><p>랜덤 초안 뒤 필요한 객실만 조정합니다. 얼리·레이트·연박 일정은 해당 객실 행에서 함께 확인합니다.</p></div>${statusBadge(`${visibleTargets.length}/${targets.length}건 표시`,'blue')}</div>${assignmentTypeFiltersMarkup()}<div class="assignment-filter-context">${icon('filter','icon-sm')}<span><strong>${activeType?esc(activeType.name):'전체 객실 타입'}</strong> ${visibleTargets.length}건 표시 · 전체 ${targets.length}건 현황을 유지하며 배정된 객실만 통보합니다.</span></div><div class="assignment-table-wrap"><table class="assignment-table"><thead><tr><th scope="col">객실·타입·요금</th><th scope="col">청소 정보·등록 근거</th><th scope="col">일정</th><th scope="col">담당 메이드</th><th scope="col">상태·조정</th></tr></thead><tbody>${rows||emptyRows}</tbody></table></div><div class="assignment-foot"><p>담당을 바꾸면 해당 객실이 새 메이드 순서의 마지막으로 이동합니다. 이미 시작한 청소는 진행 중 탭에서 관리합니다.</p></div></section>${renderMaidOrderBoardContent()}<section class="card assignment-history"><div class="assignment-panel-head"><div><h3>배정·순서 통보 이력</h3><p>담당과 청소 순서의 이전 값을 덮어쓰지 않고 변경 이력을 추가합니다.</p></div>${statusBadge('관리자 전용','neutral')}</div><div class="assignment-history-list">${history}</div></section></div>`;
  5362 |       }
  5363 |       function cleaningTabButton(id,label,count) { return `<button type="button" role="tab" data-action="cleaning-tab" data-tab="${id}" aria-selected="${state.cleaningTab===id}">${label} ${count}</button>`; }
  5364 |       function rolloverMetaForRoom(no) {
  5365 |         const attempt=state.cleaningAttempts?.[currentAttemptId(no)];if(attemptIsRollover(attempt))return {carryReason:attempt.carryReason||'started-unfinished',planDate:attemptPlanDate(attempt),effectiveDate:attemptEffectiveDate(attempt),rolloverCount:Number(attempt.rolloverCount)||1};
  5366 |         const target=Object.values(state.cleaningTargets||{}).find(item=>item.room===no&&item.carryReason&&!item.closed);return target?{carryReason:target.carryReason,planDate:targetPlanDate(target),effectiveDate:targetEffectiveDate(target),rolloverCount:Number(target.rolloverCount)||1}:null;
  5367 |       }
  5368 |       function rolloverBadgeMarkup(meta,{compact=false}={}) {
  5369 |         if(!meta)return '';
  5370 |         const label=meta.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료',detail=`원 계획 ${dateLabel(meta.planDate)} · 이월 ${meta.rolloverCount}일째`;
  5371 |         return `<div class="badge-row${compact?' compact':''}" style="margin-top:7px">${statusBadge(label,'amber')}<span class="cell-sub">${esc(detail)}</span></div>`;
  5372 |       }
  5373 |       function cleaningProgressEntries() {
  5374 |         const allowed=['scheduled','claimed','cleaning','upload','reclean','hold'];
  5375 |         return Object.entries(state.jobs).filter(([no,job])=>{
  5376 |           if(!allowed.includes(job))return false;
  5377 |           const rollover=rolloverMetaForRoom(no);
  5378 |           return !rollover||rollover.carryReason==='started-unfinished'||!!activeUnfinishedAttempt(no);
  5379 |         });
  5380 |       }
  5381 |       function renderCleaningHub() {
  5382 |         const todayDate=state.selectedDate,tomorrowDate=addIsoDays(state.selectedDate,1),tabCounts={today:assignmentCountsForDate(todayDate).total,tomorrow:assignmentCountsForDate(tomorrowDate).total,progress:cleaningProgressEntries().length,inspection:Object.values(state.jobs).filter(v=>v==='inspection').length,done:Object.values(state.jobs).filter(v=>v==='approved').length};
  5383 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>청소 관리</h2><p>오늘 운영 조정과 내일 사전 배정을 분리하고, 변경 내용은 해당 메이드에게 다시 알립니다.</p></div></div><div class="tabs" role="tablist" aria-label="청소 상태">${cleaningTabButton('assignment-today','오늘 배정',tabCounts.today)}${cleaningTabButton('assignment-tomorrow','내일 배정',tabCounts.tomorrow)}${cleaningTabButton('progress','진행 중',tabCounts.progress)}${cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)}${cleaningTabButton('done','완료',tabCounts.done)}</div>${renderListState(renderCleaningTab())}</div>`;
  5384 |       }
  5385 |       function taskRow(no,job,extra='') {
  5386 |         const room=ROOMS.find(r=>r.no===no),liveType=ROOM_TYPES[room?.type||'standard'],validSubmission=currentSubmission(no),submittedContext=['inspection','approved'].includes(job),submission=submittedContext?(validSubmission||currentSubmissionRecord(no)):validSubmission,submissionMeta=submission?.roomMetaSnapshot,displayType=submittedContext?(ROOM_TYPES[submissionMeta?.typeId]||liveType):liveType,displayTypeName=submittedContext?(submissionMeta?.typeName||displayType.name):displayType.name,displayElevator=submittedContext?(submissionMeta?.elevator?`${submissionMeta.elevator} 엘리베이터`:'엘리베이터 미기재'):elevatorLabel(room),activeAttempt=state.cleaningAttempts?.[currentAttemptId(no)],rollover=rolloverMetaForRoom(no),report=submittedContext?(validSubmission?submittedBombRoomReport(no):rawBombRoomReportForSubmission(submission)):activeBombRoomReport(no),record=submittedContext?earningRecordFor(no):earningRecordForReport(report),wholeRejected=submittedContext&&submission?.status==='rejected',unpaidReclean=submittedContext?submission?.kind==='재청소':activeAttempt?.kind==='재청소',bombMeta=wholeRejected?{label:'청소 전체 반려 · 적립 없음',tone:'red'}:bombRoomStatusMeta(report),fee=record||bombRoomBreakdown(no,{pendingAsBonus:!unpaidReclean&&(submittedContext?submission?.status==='pending':true)&&report?.status==='pending',reportOverride:report,baseOverride:submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot}),performer=submittedContext?submission?.performerName:room?.assignee;
  5387 |         const displayRate=unpaidReclean?0:record?.base??(submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot)??displayType.rate,displayKind=(submittedContext?submission?.kind:activeAttempt?.kind)||(job==='reclean'?'재청소':'퇴실 청소');
  5388 |         const action=job==='inspection'?['전체 검수','cleaning-detail']:job==='approved'?['결과 보기','cleaning-detail']:['진행 보기','cleaning-detail'];
  5389 |         return `<article class="card task-row"><div><h3>${no}호 · ${esc(displayKind)} · ${statusLabel(job)}</h3><p>${esc(displayTypeName)} · ${esc(displayElevator)} · ${money(displayRate)} · ${submission?.templateSnapshot?.minutes??displayType.minutes}분 · 데모</p>${rolloverBadgeMarkup(rollover,{compact:true})}${submittedContext&&!validSubmission?`<div class="badge-row" style="margin-top:7px">${statusBadge('제출 연결 확인 필요','red')}</div>`:''}${report?`<div class="badge-row" style="margin-top:7px">${statusBadge(bombMeta.label,bombMeta.tone)}<span class="cell-sub">${wholeRejected?'적립':record?'확정':report.status==='pending'?'폭탄방 승인 시':'전체 승인 시'} ${money(wholeRejected?0:fee.total)}</span></div>`:unpaidReclean?`<div class="badge-row" style="margin-top:7px">${statusBadge('본인 재청소 · 무급','neutral')}<span class="cell-sub">수익 원장 없음 · 0원</span></div>`:''}${extra}</div><div class="task-meta"><span>일정</span><strong>${room?.checkout||'11:00'} → ${room?.checkin||'16:00'}</strong></div><div class="task-meta"><span>${submittedContext?'수행자':'담당'}</span><strong>${esc(performer||'미정')}</strong></div><div class="task-row-action">${button(action[0],action[1],job==='inspection'?'primary':'outline',`data-id="${no}"`)}</div></article>`;
  5390 |       }
  5391 |       function renderCleaningTab() {
  5392 |         if(isCleaningAssignmentTab(state.cleaningTab))return renderAssignmentDashboard();
  5393 |         const allowed=state.cleaningTab==='progress'?['scheduled','claimed','cleaning','upload','reclean','hold']:state.cleaningTab==='inspection'?['inspection']:['approved'];
  5394 |         const entries=state.cleaningTab==='progress'?cleaningProgressEntries():Object.entries(state.jobs).filter(([,v])=>allowed.includes(v)),rows=entries.map(([no,v])=>taskRow(no,v)).join('');
  5395 |         return `<div class="tab-panel">${rows||`<section class="inline-empty"><h3>이 상태의 작업이 없습니다</h3><p>다른 탭에서 진행 상태를 확인하세요.</p></section>`}</div>`;
```

### occurrence 8 · line 5452

```html
  5436 |         const fixtures=WORK_HISTORY_FIXTURES.map(week=>({...week,records:Object.fromEntries(Object.entries(week.records).map(([maidId,record])=>[maidId,{...record,assigned:[...new Set([...(record.assigned||[]),...assignedWorkDaysForWeek(week.start,maidId)])].sort((left,right)=>left-right),completed:[...new Set([...(record.completed||[]),...completedWorkDaysForWeek(week.start,maidId)])].sort((left,right)=>left-right)}]))}));
  5437 |         return [currentWorkHistoryWeek(),...fixtures];
  5438 |       }
  5439 |       function renderWorkHistory() {
  5440 |         const weeks=workHistoryWeeks(),week=weeks.find(item=>item.start===state.workHistoryWeek)||{start:state.workHistoryWeek,status:'기록 없음',records:{}},selectedMaid=state.workHistoryMaid||'all';
  5441 |         const people=MAIDS.filter(maid=>selectedMaid==='all'||maid.id===selectedMaid).map(maid=>({maid,record:week.records[maid.id]})).filter(item=>item.record);
  5442 |         const totals=people.reduce((sum,item)=>({submitted:sum.submitted+item.record.submitted.length,assigned:sum.assigned+item.record.assigned.length,completed:sum.completed+item.record.completed.length}),{submitted:0,assigned:0,completed:0});
  5443 |         const maidCounts={submitted:people.filter(item=>item.record.submitted.length>0).length,assigned:people.filter(item=>item.record.assigned.length>0).length,completed:people.filter(item=>item.record.completed.length>0).length};
  5444 |         const dayNames=['월','화','수','목','금','토','일'];
  5445 |         const cards=people.map(({maid,record})=>{const days=dayNames.map((name,index)=>{const iso=addIsoDays(week.start,index),flags=[];if(record.submitted.includes(index))flags.push('<span class="work-history-flag">가능 제출</span>');if(record.assigned.includes(index))flags.push('<span class="work-history-flag assigned">담당 통보</span>');if(record.completed.includes(index))flags.push('<span class="work-history-flag completed">실근무 완료</span>');return `<div class="work-history-day"><strong>${name}요일</strong><span>${shortIsoDate(iso)}</span>${flags.length?`<div class="work-history-flags">${flags.join('')}</div>`:'<span class="work-history-empty">기록 없음</span>'}</div>`;}).join('');return `<article class="card work-history-person"><div class="work-history-person-head"><div><h3>${esc(record.nameSnapshot)} · 데모</h3><p>당시 이름 스냅샷 · 가능일 제출 ${esc(record.submittedAt)}${record.submissionVersions?` · 제출 버전 ${record.submissionVersions}개 보존`:''}</p></div><div class="work-history-counts">${statusBadge(`가능 ${record.submitted.length}일`,'blue')}${statusBadge(`배정 ${record.assigned.length}일`,'amber')}${statusBadge(`실근무 ${record.completed.length}일`,'green')}</div></div><div class="work-history-days" aria-label="${esc(record.nameSnapshot)} ${weekRangeLabel(week.start)} 주간 기록">${days}</div></article>`;}).join('');
  5446 |         const list=cards||`<section class="card empty-state"><h3>이 주차에는 저장된 근무 기록이 없습니다.</h3><p>다른 주차를 달력에서 선택하거나 메이드 필터를 바꿔 보세요.</p></section>`;
  5447 |         return `<div class="work-history-page"><section class="card work-history-hero"><div><h2>주간 근무 기록</h2><p>가능일 제출, 관리자 배정 통보, 실제 청소 완료일을 구분해 사람별·주차별로 확인합니다.</p></div>${statusBadge(`${week.status} · 관리자 전용`,week.status==='계획 중'?'blue':'neutral')}</section><section class="card"><div class="work-history-toolbar"><div class="work-history-week-field"><span id="work-history-week-label">조회 주차</span><button class="pay-week-picker work-history-week-picker" type="button" data-action="open-work-history-calendar" aria-haspopup="dialog" aria-labelledby="work-history-week-label work-history-week-value">${icon('calendar','icon-sm')}<span id="work-history-week-value">${weekRangeLabel(week.start,true)} · ${week.status}</span>${icon('chevronRight','icon-sm')}</button></div><label for="work-history-maid">메이드<select id="work-history-maid" class="select-control" data-control="work-history-maid"><option value="all" ${selectedMaid==='all'?'selected':''}>전체 메이드</option>${MAIDS.map(maid=>`<option value="${maid.id}" ${selectedMaid===maid.id?'selected':''}>${esc(maid.name)}</option>`).join('')}</select></label></div><div class="work-history-summary"><div class="planned"><span>가능 제출 메이드</span><strong>${maidCounts.submitted}명</strong><small>메이드별 가능일 합계 ${totals.submitted}일</small></div><div class="assigned"><span>담당 통보 메이드</span><strong>${maidCounts.assigned}명</strong><small>메이드별 배정일 합계 ${totals.assigned}일</small></div><div class="completed"><span>실제 근무 메이드</span><strong>${maidCounts.completed}명</strong><small>메이드별 실근무일 합계 ${totals.completed}일</small></div></div><p class="work-history-unit-note"><strong>단위 안내:</strong> ‘명’은 해당 기록이 한 번 이상 있는 메이드 수, ‘일’은 메이드별 기록 날짜를 합한 일수입니다.</p><div class="work-history-legend"><span><i class="history-dot"></i>가능 제출 · 계획</span><span><i class="history-dot assigned"></i>담당 통보 · 예정</span><span><i class="history-dot completed"></i>실근무 완료 · 수행 실적</span></div></section><div class="work-history-list">${list}</div><section class="card work-history-contract"><p><strong>기록 기준:</strong> 가능일은 제출 버전, 배정일은 관리자 통보 이벤트, 실근무일은 정상 청소 수행 회차의 현장 완료일입니다. 가능일만 제출한 날짜는 실제 근무로 세지 않으며, 과거 주차는 현재 제출·재배정으로 덮어쓰지 않습니다. 이 화면은 서버 영속 저장이 아닌 결정적 데모 fixture입니다.</p></section></div>`;
  5448 |       }
  5449 | 
  5450 |       function renderMaids() {
  5451 |         const tab=state.adminMaidTab||'workforce';
  5452 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>메이드 운영</h2><p>주간 근무 가능일·배정 업무·과거 근무 기록·주급·컴플레인을 분리해 관리합니다.</p></div></div><div class="tabs" role="tablist" aria-label="메이드 관리"><button type="button" role="tab" data-action="admin-maid-tab" data-tab="workforce" aria-selected="${tab==='workforce'}">주간 근무표</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="history" aria-selected="${tab==='history'}">근무 기록</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="pay" aria-selected="${tab==='pay'}">주급 정산</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="complaints" aria-selected="${tab==='complaints'}">컴플레인·벌점</button></div>${tab==='history'?renderWorkHistory():tab==='pay'?renderAdminPayroll():tab==='complaints'?renderComplaintsPanel():renderWorkforce()}</div>`;
  5453 |       }
  5454 |       function renderWorkforce() {
  5455 |         const submitted=Object.values(state.weeklyAvailability).filter(item=>['submitted','change-requested'].includes(item.status)).length;
  5456 |         const cards=MAIDS.map(maid=>{const record=state.weeklyAvailability[maid.id],availableDays=record.days.map(index=>['월','화','수','목','금','토','일'][index]).join('·')||'없음',accountStatus=maidStatusFor(maid.id),activity=accountStatus==='active'?maid.active:accountStatus==='deactivating'?'비활성 처리 중':'비활성';return `<article class="card pay-person" data-maid-card="${maid.id}"><div class="pay-person-head"><div class="avatar">${maid.name[0]}</div><div><h3>${maid.name} · 데모</h3><p>${maid.phone} · ${activity}</p></div>${statusBadge(accountStatus==='active'?(record.status==='submitted'?'제출 완료':record.status==='change-requested'?'변경 요청':'미제출'):accountStatus==='deactivating'?'비활성 처리 중':'비활성',accountStatus==='active'?(record.status==='submitted'?'green':record.status==='change-requested'?'amber':'red'):accountStatus==='deactivating'?'amber':'neutral')}</div><div class="pay-stats"><div class="pay-stat"><span>다음 주 가능</span><strong>${availableDays}</strong></div><div class="pay-stat"><span>예정 배정</span><strong>${assignmentTargets().filter(item=>assignmentFor(item).maidId===maid.id).length}객실</strong></div><div class="pay-stat"><span>제출 시각</span><strong>${record.submittedAt||'—'}</strong></div></div>${button('상세·이력','maid-detail','outline',`data-id="${maid.id}"`)}</article>`;}).join('');
  5457 |         return `<section class="card assignment-panel"><div class="assignment-panel-head"><div><h3>메이드 주간 근무표</h3><p>8월 17일–23일 · 일요일 23:59 마감</p></div>${statusBadge(`${submitted}/${MAIDS.length} 제출`,submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section><div class="room-list-v2">${cards}</div>`;
  5458 |       }
  5459 |       function payrollDateLabel(value) {
  5460 |         const match=String(value||'').match(/(?:\d{4}[.-])?(\d{1,2})[.-](\d{1,2})/);
  5461 |         return match?`${Number(match[1])}월 ${Number(match[2])}일`:'날짜 미입력';
  5462 |       }
  5463 |       function payrollTaskDateIso(value,weekStart) {
  5464 |         const direct=timestampIsoDate(value,'');
  5465 |         if(direct)return direct;
  5466 |         const match=String(value||'').match(/(\d{1,2})월\s*(\d{1,2})일/),weekEnd=addIsoDays(weekStart,6),baseYear=Number(String(weekStart).slice(0,4));
  5467 |         if(!match)return '';
  5468 |         for(const year of [baseYear-1,baseYear,baseYear+1]){const candidate=`${year}-${String(Number(match[1])).padStart(2,'0')}-${String(Number(match[2])).padStart(2,'0')}`;if(candidate>=weekStart&&candidate<=weekEnd)return candidate;}
  5469 |         return '';
  5470 |       }
  5471 |       function roomMetadataSnapshot(no) {
  5472 |         const room=ROOMS.find(item=>item.no===String(no)),type=room?ROOM_TYPES[room.type]:null;
  5473 |         return room&&type?{roomNo:room.no,typeId:room.type,typeName:type.name,elevator:room.elevator||null}:null;
  5474 |       }
  5475 |       function payrollTaskRoomContext(roomNo,snapshot=null) {
  5476 |         const baseline=ROOM_BASELINE.find(item=>item.no===String(roomNo)),room=snapshot?null:baseline,typeId=snapshot?.typeId||room?.type||null,type=typeId?ROOM_TYPES[typeId]:null,elevator=snapshot?.elevator??room?.elevator??null;
  5477 |         return {room,type,typeName:snapshot?.typeName||type?.name||'객실 타입 미입력',elevator:elevator?`${elevator} 엘리베이터`:'엘리베이터 미기재'};
  5478 |       }
  5479 |       function normalizePayrollFixture(task,weekStart,maidId) {
  5480 |         const roomNo=String(task.room),context=payrollTaskRoomContext(roomNo),base=Number(task.base??context.type?.rate??0),bombBonus=Number(task.bombBonus||0),amount=base+bombBonus;
  5481 |         return {...task,id:task.id||`pay-${weekStart}-${maidId}-${roomNo}`,weekStart,maidId,roomNo,room:`${roomNo}호`,typeName:context.typeName,elevator:context.elevator,earnedOn:payrollTaskDateIso(task.date,weekStart),baseAmount:base,bombBonus,amount,total:amount,stage:'confirmed',status:task.status||'승인 확정',tone:'green',bombStatus:bombBonus?'approved':'none',source:'fixture',included:true,potential:false};
  5482 |       }
  5483 |       function currentPayrollTasks(maidId,weekStart='2026-08-10') {
  5484 |         const confirmed=validatedEarningRecords().filter(record=>record.weekStart===weekStart&&record.performerId===maidId).sort((a,b)=>String(b.creditedAt).localeCompare(String(a.creditedAt))).map(record=>{
  5485 |           const submission=validatedSubmission(state.cleaningSubmissions?.[record.submissionId]||null),report=bombRoomReportForSubmission(submission),context=payrollTaskRoomContext(record.room,submission?.roomMetaSnapshot);
  5486 |           return {id:record.id,weekStart,maidId,roomNo:record.room,room:`${record.room}호`,typeName:context.typeName,elevator:context.elevator,kind:submission?.kind||'퇴실 청소',date:payrollDateLabel(submission?.completedAt||submission?.submittedAt),earnedOn:timestampIsoDate(submission?.completedAt||submission?.submittedAt,weekStart),baseAmount:record.base,bombBonus:record.bombBonus,amount:record.total,total:record.total,stage:'confirmed',status:record.bombBonus?'폭탄방 승인 · ×2':report?.status==='rejected'?'폭탄방 미인정 · 승인 확정':'승인 확정',tone:'green',bombStatus:report?.status||'none',reportId:report?.id||null,photoId:report?.photos?.[0]?.id||null,submissionId:submission?.id||record.submissionId,attemptId:submission?.attemptId||null,roundLabel:String(record.submissionId||'').split('-').slice(-2).join('-'),source:'earning',included:true,potential:false};
```

### occurrence 9 · line 6075

```html
  6059 |         return `<section class="card availability-card"><div class="availability-result">${statusBadge(statusLabel,state.availabilitySubmitted?'green':'amber')}<div><strong>8월 17일–23일 · 가능 ${selected.length}일</strong><span>${availabilitySubmissionWindowLabel()} 제출 · 객실 담당은 관리자만 배정</span></div>${button('근무 일정 열기','go-schedule','outline')}</div></section>`;
  6060 |       }
  6061 |       function renderMaidSchedule() {
  6062 |         const maidId=signedInMaidId(),accountActive=signedInMaidIsActive(),dayNames=[['월','17'],['화','18'],['수','19'],['목','20'],['금','21'],['토','22'],['일','23']],phase=availabilitySubmissionPhase(),submitted=state.availabilitySubmitted,editing=!!state.availabilityEditing&&phase==='open',savedSelected=state.weeklyAvailability?.[maidId]?.days||[],selected=editing||!submitted?state.availabilityDraft||[]:savedSelected,availableCount=selected.length;
  6063 |         const assigned=notifiedAssignmentEntriesForMaid(maidId);
  6064 |         const assignedCards=assigned.length?assigned.map(({item})=>{const guestCount=assignmentGuestCount(item);return `<div class="assigned-preview-grid"><div><span>근무일</span><strong>${esc(dateLabel(targetEffectiveDate(item)))}</strong></div><div><span>객실</span><strong>${item.room}호</strong></div><div><span>업무</span><strong>${esc(item.kind)}</strong></div>${guestCount?`<div><span>숙박 인원</span><strong>${esc(guestCountLabel(guestCount))}</strong></div>`:`<div><span>예약 연결</span><strong>없음</strong></div>`}<div><span>시작 가능</span><strong>${item.checkout} 이후</strong></div>${item.carryReason?`<div><span>이월</span><strong>원 계획 ${esc(dateLabel(targetPlanDate(item)))}</strong></div>`:''}</div>`;}).join(''):`<div class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 근무일 전날 밤 객실 담당을 확정하면 여기에 표시됩니다.</p></div>`;
  6065 |         const submissionWindow=availabilitySubmissionWindowLabel(),phaseText=!accountActive?'비활성 계정 · 과거 제출 읽기 전용':phase==='before'?`${submissionWindow} 제출 가능`:phase==='open'?`${submissionWindow} · 지금 제출 가능`:`${submissionWindow} 마감 · 변경은 관리자 확인 필요`;
  6066 |         const editorLocked=!accountActive||submitted&&!editing||state.availabilityChangeRequested||phase!=='open'||isLocked();
  6067 |         let actionMarkup='';
  6068 |         if(!accountActive)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>가능일 수정 잠금</strong><br>비활성 처리 중이거나 비활성인 계정은 과거 제출만 조회할 수 있습니다.</div></div>';
  6069 |         else if(state.availabilityChangeRequested)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>관리자 확인 요청됨</strong><br>기존 제출은 유지되고 변경 요청이 관리자 알림에 남았습니다.</div></div>';
  6070 |         else if(editing)actionMarkup=button('수정 내용 다시 제출','submit-week-availability','primary',isLocked()?'disabled':'');
  6071 |         else if(submitted&&phase==='open')actionMarkup=button('제출 내용 수정','edit-week-availability','primary',isLocked()?'disabled':'');
  6072 |         else if(submitted&&phase==='closed')actionMarkup=button('가능일 변경 요청','request-availability-change','outline',isLocked()?'disabled':'');
  6073 |         else if(submitted)actionMarkup=button('제출 기간 아님','edit-week-availability','outline','disabled');
  6074 |         else actionMarkup=button(phase==='open'?'다음 주 가능일 제출':phase==='before'?`${submissionWindow} 제출`:'제출 마감','submit-week-availability','primary',phase==='open'&&!isLocked()?'':'disabled');
  6075 |         return renderCoach()+renderNetworkNotice()+`<div class="weekly-availability"><section class="card week-card"><div class="week-card-head"><div><h2>8월 17일 (월)–8월 23일 (일)</h2><p>다음 주에 근무 가능한 요일을 모두 선택해 주세요.</p></div>${statusBadge(state.availabilityChangeRequested?'변경 요청':editing?'수정 중':submitted?'제출 완료':'미제출',state.availabilityChangeRequested||editing?'amber':submitted?'green':'amber')}</div><div class="deadline-bar">${icon('clock','icon-sm')}<span>${phaseText}</span></div><div class="week-days" aria-label="다음 주 근무 가능일">${dayNames.map((day,index)=>{const active=selected.includes(index);return `<button class="week-day" type="button" data-action="toggle-week-day" data-day="${index}" aria-pressed="${active}" ${editorLocked?'disabled':''}><strong>${day[0]} ${day[1]}</strong><span>${active?'근무 가능':'근무 불가'}</span><i class="week-toggle" aria-hidden="true"></i></button>`;}).join('')}</div><div class="week-total">${icon('calendar','icon-sm')}가능 ${availableCount}일 · 불가 ${7-availableCount}일</div><div class="week-submit-actions">${actionMarkup}</div><div class="assignment-notice">${icon('user')}<p>관리자가 각 근무일 전날 밤 객실을 직접 배정합니다. 메이드는 객실을 선택하거나 다른 메이드에게 배정할 수 없습니다.</p></div></section><section class="card assigned-preview"><div class="section-head"><div><h2>배정된 내 업무</h2><span class="meta">관리자 통보 완료 건만 표시</span></div>${statusBadge(`${assigned.length}건`,'blue')}</div>${assignedCards}<p class="audit-note" style="margin:10px 0 0">배정이 바뀌면 기존 담당 구간은 이력으로 남고 알림에서 변경 내용을 확인할 수 있습니다.</p></section></div>`;
  6076 |       }
  6077 |       function publicJobCard(no) {
  6078 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room?.type||'standard'];
  6079 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${esc(cleaningLabel(state.jobs[no]))}</h3><p>${esc(type.name)}</p></div>${statusBadge('관리자 배정','green')}</div><div class="schedule-line">${icon('clock','icon-sm')}<span>시작 가능 ${startTimeFor(no)} · 담당 ${esc(room?.assignee||'미정')}</span></div><div class="notice notice-info" style="margin:0">메이드는 관리자에게 통보받은 업무만 확인하고 수행할 수 있습니다.</div></article>`;
  6080 |       }
  6081 |       function renderMaidOpen() {
  6082 |         return renderMaidSchedule();
  6083 |       }
  6084 |       function myJobCard(no) {
  6085 |         const job=state.jobs[no], room=ROOMS.find(r=>r.no===no),attempt=state.cleaningAttempts?.[currentAttemptId(no)],access=attemptAccessStatus(no,attempt),start=access.start,reached=access.allowed,rollover=rolloverMetaForRoom(no);
  6086 |         const guestCount=guestCountForAttempt(attempt),guestCountDisplay=guestCount?guestCountLabel(guestCount):'미기록',reclean=attempt?.kind==='재청소'?{reason:attempt.reason||'전체 반려 뒤 본인 재청소',previousMaid:currentSubmission(no)?.performerName||room?.assignee||'기존 메이드',originalKind:currentSubmission(no)?.kind||'퇴실 청소'}:null;
  6087 |         const labels={scheduled:reached?'일 시작':'시작 시각 대기',claimed:reached?'일 시작':'시작 시각 대기',cleaning:'계속 청소',upload:taskState(no).uploads.some(u=>u.status==='failed')?'미전송 재시도':'청소 전체 제출',inspection:'제출 결과 보기',approved:'완료 결과 보기',reclean:reached?'재청소 시작':'시작 시각 대기'};
  6088 |         const action='cleaning-detail';
  6089 |         const bomb=bombRoomReport(no),bombMeta=bombRoomStatusMeta(bomb),tone=job==='approved'?'green':job==='cleaning'||job==='upload'?'amber':job==='inspection'?'blue':'neutral';
  6090 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${reclean?'재청소':cleaningLabel(job)}</h3><p>${esc(ROOM_TYPES[room?.type||'standard'].name)}</p></div><div class="badge-row">${statusBadge(statusLabel(job),tone)}${bomb?statusBadge(bombMeta.label,bombMeta.tone):''}</div></div>${rolloverBadgeMarkup(rollover,{compact:true})}<div class="schedule-line">${icon('clock','icon-sm')}<span>${job==='upload'?'현장 완료 · 사진 전송·전체 제출 필요':job==='cleaning'&&rollover?'계속 청소 가능':`시작 가능 ${start} · ${reached?'지금 시작 가능':esc(access.reason)}`}</span></div><div class="schedule-line">${icon('user','icon-sm')}<span>숙박 인원 ${guestCountDisplay}</span></div>${reclean?`<div class="job-meta"><div><span>재청소 요금</span><strong>0원 · 무급</strong></div><div><span>원 작업</span><strong>${no}호 ${esc(reclean.originalKind)}</strong></div></div><div class="notice notice-warning" style="margin:0"><div>처음 청소한 ${esc(reclean.previousMaid)} 본인에게 자동 배정 · 다른 메이드에게 넘길 수 없음 · ${esc(reclean.reason)}</div></div>`:''}<button class="btn ${job==='upload'&&taskState(no).uploads.some(u=>u.status==='failed')?'btn-danger':'btn-primary'} btn-block" type="button" data-action="${action}" data-id="${no}">${labels[job]||'상세 보기'}</button></article>`;
  6091 |       }
  6092 |       function renderMaidMy() {
  6093 |         const maidId=signedInMaidId(),maidName=signedInMaidName(),activeCleaning=activeCleaningFor(maidId),own=Object.entries(state.jobs).filter(([no,v])=>['scheduled','claimed','cleaning','upload','inspection','approved','reclean'].includes(v)&&(ROOMS.find(r=>r.no===no)?.assignee===maidName||(['inspection','approved'].includes(v)&&currentSubmission(no)?.performerId===maidId))).map(([no])=>no);
  6094 |         const upcoming=notifiedAssignmentEntriesForMaid(maidId);
  6095 |         const upcomingNotice=upcoming.length?`<div class="assignment-notice">${icon('bell')}<div><p><strong>통보된 청소 일정 ${upcoming.length}건</strong><br>오늘·내일 날짜와 관리자가 확정한 순서입니다.</p><ol class="maid-assignment-route">${upcoming.map(({item,assignment})=>`<li><b>${assignment.order}</b><span>${esc(dateLabel(targetEffectiveDate(item)))} · ${item.room}호 · ${esc(item.kind)} · ${esc(assignmentScheduleText(item))}${assignment.activationBlockedBy?' · 관리자 확인 대기':''}</span></li>`).join('')}</ol></div></div>`:'';
  6096 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack">${upcomingNotice}<section class="card work-hero"><span>${esc(maidName)} 현재 작업 상태</span><strong>${activeCleaning?`${activeCleaning}호 청소 중`:'청소 중 없음'}</strong><p>관리자에게 배정·통보된 업무만 표시합니다. 동시에 청소 중 한 건만 가능합니다.</p></section><div class="mobile-section-title"><div><h2>내 업무 ${own.length}건</h2><p>담당 확정부터 검수 결과까지 이어집니다.</p></div></div>${renderListState(own.length?`<div class="job-list">${own.map(myJobCard).join('')}</div>`:`<section class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 오늘·내일 배정을 통보하면 내 업무와 알림에 표시됩니다.</p>${button('근무 가능일 확인','go-schedule','primary')}</section>`)}</div>`;
  6097 |       }
  6098 |       function renderMaidAlerts(){
  6099 |         const key=notificationAudienceKey('maid',signedInMaidId());ensureNotificationState();return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section><div class="section-head"><div><h2>알림</h2><p class="audit-note">배정·검수 결과·취소·마감·주급 업데이트를 시간순으로 확인합니다.</p></div>${statusBadge(`안 읽음 ${notificationUnreadCount(key)}건`,notificationUnreadCount(key)?'blue':'neutral')}</div><div class="tab-panel">${renderNotificationListMarkup({key,filter:state.notificationFilter,includeActivity:true})}</div></section></div>`;
  6100 |       }
  6101 | 
  6102 |       function renderMaidPay() {
  6103 |         return renderMaidPayFromLedger();
  6104 |         const paid=paymentStatusFor('2026-08-03',signedInMaidId())==='PAID',currentMaid=signedInMaid();
  6105 |         const currentWeekStart='2026-08-10',currentMaidId=currentMaid.id,submissionDate=submission=>{const match=String(submission?.submittedAt||'').match(/(?:\d{4}[.-])?(\d{1,2})[.-](\d{1,2})/);return match?`${Number(match[1])}월 ${Number(match[2])}일`:'이번 주';},taskKind=(room,record)=>record?.kind||(room==='142'?'연박 청소':'퇴실 청소'),roundLabel=id=>id?String(id).split('-').slice(-2).join('-'):'';
  6106 |         const baselineTasksByMaid={
  6107 |           m1:[{room:'352호',kind:'퇴실 청소',date:'8월 14일',amount:16000,status:'승인 확정',tone:'green'},{room:'350호',kind:'퇴실 청소',date:'8월 13일',amount:16000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 11일',amount:20000,status:'승인 확정',tone:'green'}],
  6108 |           m2:[{room:'142호',kind:'연박 청소',date:'8월 14일',amount:30000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 12일',amount:20000,status:'승인 확정',tone:'green'},{room:'350호',kind:'퇴실 청소',date:'8월 10일',amount:16000,status:'승인 확정',tone:'green'}],
  6109 |           m3:[{room:'142호',kind:'연박 청소',date:'8월 15일',amount:30000,status:'승인 확정',tone:'green'},{room:'639호',kind:'퇴실 청소',date:'8월 13일',amount:20000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 10일',amount:20000,status:'승인 확정',tone:'green'}]
```

### occurrence 10 · line 6096

```html
  6080 |       }
  6081 |       function renderMaidOpen() {
  6082 |         return renderMaidSchedule();
  6083 |       }
  6084 |       function myJobCard(no) {
  6085 |         const job=state.jobs[no], room=ROOMS.find(r=>r.no===no),attempt=state.cleaningAttempts?.[currentAttemptId(no)],access=attemptAccessStatus(no,attempt),start=access.start,reached=access.allowed,rollover=rolloverMetaForRoom(no);
  6086 |         const guestCount=guestCountForAttempt(attempt),guestCountDisplay=guestCount?guestCountLabel(guestCount):'미기록',reclean=attempt?.kind==='재청소'?{reason:attempt.reason||'전체 반려 뒤 본인 재청소',previousMaid:currentSubmission(no)?.performerName||room?.assignee||'기존 메이드',originalKind:currentSubmission(no)?.kind||'퇴실 청소'}:null;
  6087 |         const labels={scheduled:reached?'일 시작':'시작 시각 대기',claimed:reached?'일 시작':'시작 시각 대기',cleaning:'계속 청소',upload:taskState(no).uploads.some(u=>u.status==='failed')?'미전송 재시도':'청소 전체 제출',inspection:'제출 결과 보기',approved:'완료 결과 보기',reclean:reached?'재청소 시작':'시작 시각 대기'};
  6088 |         const action='cleaning-detail';
  6089 |         const bomb=bombRoomReport(no),bombMeta=bombRoomStatusMeta(bomb),tone=job==='approved'?'green':job==='cleaning'||job==='upload'?'amber':job==='inspection'?'blue':'neutral';
  6090 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${reclean?'재청소':cleaningLabel(job)}</h3><p>${esc(ROOM_TYPES[room?.type||'standard'].name)}</p></div><div class="badge-row">${statusBadge(statusLabel(job),tone)}${bomb?statusBadge(bombMeta.label,bombMeta.tone):''}</div></div>${rolloverBadgeMarkup(rollover,{compact:true})}<div class="schedule-line">${icon('clock','icon-sm')}<span>${job==='upload'?'현장 완료 · 사진 전송·전체 제출 필요':job==='cleaning'&&rollover?'계속 청소 가능':`시작 가능 ${start} · ${reached?'지금 시작 가능':esc(access.reason)}`}</span></div><div class="schedule-line">${icon('user','icon-sm')}<span>숙박 인원 ${guestCountDisplay}</span></div>${reclean?`<div class="job-meta"><div><span>재청소 요금</span><strong>0원 · 무급</strong></div><div><span>원 작업</span><strong>${no}호 ${esc(reclean.originalKind)}</strong></div></div><div class="notice notice-warning" style="margin:0"><div>처음 청소한 ${esc(reclean.previousMaid)} 본인에게 자동 배정 · 다른 메이드에게 넘길 수 없음 · ${esc(reclean.reason)}</div></div>`:''}<button class="btn ${job==='upload'&&taskState(no).uploads.some(u=>u.status==='failed')?'btn-danger':'btn-primary'} btn-block" type="button" data-action="${action}" data-id="${no}">${labels[job]||'상세 보기'}</button></article>`;
  6091 |       }
  6092 |       function renderMaidMy() {
  6093 |         const maidId=signedInMaidId(),maidName=signedInMaidName(),activeCleaning=activeCleaningFor(maidId),own=Object.entries(state.jobs).filter(([no,v])=>['scheduled','claimed','cleaning','upload','inspection','approved','reclean'].includes(v)&&(ROOMS.find(r=>r.no===no)?.assignee===maidName||(['inspection','approved'].includes(v)&&currentSubmission(no)?.performerId===maidId))).map(([no])=>no);
  6094 |         const upcoming=notifiedAssignmentEntriesForMaid(maidId);
  6095 |         const upcomingNotice=upcoming.length?`<div class="assignment-notice">${icon('bell')}<div><p><strong>통보된 청소 일정 ${upcoming.length}건</strong><br>오늘·내일 날짜와 관리자가 확정한 순서입니다.</p><ol class="maid-assignment-route">${upcoming.map(({item,assignment})=>`<li><b>${assignment.order}</b><span>${esc(dateLabel(targetEffectiveDate(item)))} · ${item.room}호 · ${esc(item.kind)} · ${esc(assignmentScheduleText(item))}${assignment.activationBlockedBy?' · 관리자 확인 대기':''}</span></li>`).join('')}</ol></div></div>`:'';
  6096 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack">${upcomingNotice}<section class="card work-hero"><span>${esc(maidName)} 현재 작업 상태</span><strong>${activeCleaning?`${activeCleaning}호 청소 중`:'청소 중 없음'}</strong><p>관리자에게 배정·통보된 업무만 표시합니다. 동시에 청소 중 한 건만 가능합니다.</p></section><div class="mobile-section-title"><div><h2>내 업무 ${own.length}건</h2><p>담당 확정부터 검수 결과까지 이어집니다.</p></div></div>${renderListState(own.length?`<div class="job-list">${own.map(myJobCard).join('')}</div>`:`<section class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 오늘·내일 배정을 통보하면 내 업무와 알림에 표시됩니다.</p>${button('근무 가능일 확인','go-schedule','primary')}</section>`)}</div>`;
  6097 |       }
  6098 |       function renderMaidAlerts(){
  6099 |         const key=notificationAudienceKey('maid',signedInMaidId());ensureNotificationState();return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section><div class="section-head"><div><h2>알림</h2><p class="audit-note">배정·검수 결과·취소·마감·주급 업데이트를 시간순으로 확인합니다.</p></div>${statusBadge(`안 읽음 ${notificationUnreadCount(key)}건`,notificationUnreadCount(key)?'blue':'neutral')}</div><div class="tab-panel">${renderNotificationListMarkup({key,filter:state.notificationFilter,includeActivity:true})}</div></section></div>`;
  6100 |       }
  6101 | 
  6102 |       function renderMaidPay() {
  6103 |         return renderMaidPayFromLedger();
  6104 |         const paid=paymentStatusFor('2026-08-03',signedInMaidId())==='PAID',currentMaid=signedInMaid();
  6105 |         const currentWeekStart='2026-08-10',currentMaidId=currentMaid.id,submissionDate=submission=>{const match=String(submission?.submittedAt||'').match(/(?:\d{4}[.-])?(\d{1,2})[.-](\d{1,2})/);return match?`${Number(match[1])}월 ${Number(match[2])}일`:'이번 주';},taskKind=(room,record)=>record?.kind||(room==='142'?'연박 청소':'퇴실 청소'),roundLabel=id=>id?String(id).split('-').slice(-2).join('-'):'';
  6106 |         const baselineTasksByMaid={
  6107 |           m1:[{room:'352호',kind:'퇴실 청소',date:'8월 14일',amount:16000,status:'승인 확정',tone:'green'},{room:'350호',kind:'퇴실 청소',date:'8월 13일',amount:16000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 11일',amount:20000,status:'승인 확정',tone:'green'}],
  6108 |           m2:[{room:'142호',kind:'연박 청소',date:'8월 14일',amount:30000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 12일',amount:20000,status:'승인 확정',tone:'green'},{room:'350호',kind:'퇴실 청소',date:'8월 10일',amount:16000,status:'승인 확정',tone:'green'}],
  6109 |           m3:[{room:'142호',kind:'연박 청소',date:'8월 15일',amount:30000,status:'승인 확정',tone:'green'},{room:'639호',kind:'퇴실 청소',date:'8월 13일',amount:20000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 10일',amount:20000,status:'승인 확정',tone:'green'}]
  6110 |         },baselineTasks=baselineTasksByMaid[currentMaidId]||[],baselineConfirmed=baselineTasks.reduce((sum,task)=>sum+task.amount,0);
  6111 |         const currentEarningTasks=validatedEarningRecords().filter(record=>record.weekStart===currentWeekStart&&record.performerId===currentMaidId).sort((a,b)=>String(b.creditedAt).localeCompare(String(a.creditedAt))).map(record=>{const submission=validatedSubmission(state.cleaningSubmissions?.[record.submissionId]||null),report=bombRoomReportForSubmission(submission);return {room:`${record.room}호`,roomNo:record.room,kind:taskKind(record.room,submission),date:submissionDate(submission),amount:record.total,status:record.bombBonus?'폭탄방 승인 · ×2':report?.status==='rejected'?'폭탄방 미인정 · 승인 확정':'승인 확정',tone:'green',baseAmount:record.base,bombBonus:record.bombBonus,bombStatus:report?.status||'none',reportId:report?.id||null,photoId:report?.photos?.[0]?.id||null,submissionId:record.submissionId,roundLabel:roundLabel(record.submissionId)};});
  6112 |         const isUnpaidRecleanSubmission=submission=>submission?.kind==='재청소';
  6113 |         const currentUnsettledTasks=validatedSubmissions().filter(submission=>submission.weekStart===currentWeekStart&&submission.performerId===currentMaidId&&!earningRecordForSubmission(submission)&&(['pending','rejected'].includes(submission.status)||(submission.status==='approved'&&isUnpaidRecleanSubmission(submission)))).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))).map(submission=>{
  6114 |           const report=bombRoomReportForSubmission(submission),wholeRejected=submission.status==='rejected',unpaidReclean=isUnpaidRecleanSubmission(submission),unpaidApproved=unpaidReclean&&submission.status==='approved',fee=bombRoomBreakdown(submission.room,{pendingAsBonus:!wholeRejected&&!unpaidReclean&&report?.status==='pending',reportOverride:report,baseOverride:submission.baseRateSnapshot});
  6115 |           const rejectedDecision=report?.status==='approved'?'폭탄방 승인 결정':report?.status==='rejected'?'폭탄방 미인정 결정':'폭탄방 신고 없음',status=wholeRejected?`청소 전체 반려 · ${rejectedDecision} 보존`:unpaidApproved?'재청소 승인 · 무급':unpaidReclean?'재청소 검수 대기 · 무급':report?.status==='pending'?'폭탄방 검수 대기':report?.status==='approved'?'폭탄방 인정 · 전체 검수 대기':report?.status==='rejected'?'폭탄방 미인정 · 전체 검수 대기':'검수 대기';
  6116 |           const rejectedBreakdown=wholeRejected?`${rejectedDecision} · 기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 청소 전체 반려로 실제 적립 0원`:'';
  6117 |           return {room:`${submission.room}호`,roomNo:submission.room,kind:taskKind(submission.room,submission),date:submissionDate(submission),amount:wholeRejected||unpaidReclean?0:fee.total,status,tone:wholeRejected?'red':unpaidApproved?'green':'amber',baseAmount:unpaidReclean?0:fee.base,bombBonus:unpaidReclean?0:fee.bonus,bombStatus:report?.status||'none',reportId:report?.id||null,photoId:report?.photos?.[0]?.id||null,potential:!wholeRejected&&!unpaidReclean,submissionId:submission.id,roundLabel:roundLabel(submission.id),breakdownText:rejectedBreakdown||(unpaidReclean?'처음 청소한 본인 재청소 · 적립 0원 · 수익 원장 없음':'')};
  6118 |         });
  6119 |         const currentAbortedReportTasks=Object.values(state.bombRoomReports||{}).filter(report=>!report.submissionId&&report.attemptStatus==='superseded'&&report.reportedById===currentMaidId&&weekStartIso(timestampIsoDate(report.reportedAt))===currentWeekStart).map(report=>({room:`${report.room}호`,roomNo:report.room,kind:taskKind(report.room,state.cleaningAttempts?.[report.attemptId]),date:String(report.reportedAt).split(' ')[0].replace(/^2026[.-]/,'').replace(/[.-]/,'월 ')+'일',amount:0,status:'제출 전 회차 종료 · 적립 없음',tone:'red',baseAmount:report.baseRateSnapshot,bombBonus:0,bombStatus:report.status,reportId:report.id,photoId:report.photos?.[0]?.id||null,roundLabel:roundLabel(report.attemptId),breakdownText:'미제출 폭탄방 증빙 보존 · 담당 변경으로 회차 종료 · 적립 0원'}));
  6120 |         const currentTasks=[...currentEarningTasks,...currentUnsettledTasks,...currentAbortedReportTasks,...baselineTasks];
  6121 |         const currentConfirmed=baselineConfirmed+currentEarningTasks.reduce((sum,task)=>sum+task.amount,0);
  6122 |         const currentPending=currentUnsettledTasks.filter(task=>task.potential).reduce((sum,task)=>sum+task.amount,0);
  6123 |         const currentExpected=currentConfirmed+currentPending;
  6124 |         const weeks=[
  6125 |           {id:'2026-08-10',group:'current',label:'이번 주',period:weekRangeLabel('2026-08-10'),confirmed:currentConfirmed,pending:currentPending,status:'적립 중',tone:'blue',paidAt:'다음 월요일 지급 예정',tasks:currentTasks},
  6126 |           ...(currentMaidId==='m1'?[{id:'2026-08-03',group:'last',label:'지난주',period:weekRangeLabel('2026-08-03'),confirmed:138000,pending:0,status:paid?'지급 완료':'지급 대기',tone:paid?'green':'amber',paidAt:paid?'8월 10일 지급 기록':'외부 송금 확인 대기',tasks:[
  6127 |             {room:'536호',kind:'퇴실 청소',date:'8월 9일',amount:40000,status:'폭탄방 승인 · ×2',tone:'green',baseAmount:20000,bombBonus:20000,bombStatus:'approved'},
  6128 |             {room:'639호',kind:'퇴실 청소',date:'8월 8일',amount:20000,status:'승인 확정',tone:'green'},
  6129 |             {room:'142호',kind:'연박 청소',date:'8월 7일',amount:30000,status:'승인 확정',tone:'green'},
  6130 |             {room:'350호',kind:'퇴실 청소',date:'8월 6일',amount:16000,status:'승인 확정',tone:'green'},
```

## maid alert route: `maidAlerts`

matches: 0

## maid session: `roomManagementMaidSession`

matches: 0

## logout action: `logout`

matches: 8

### occurrence 1 · line 1720

```html
  1704 |         alert: '<path d="M10.3 3.7 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.7a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
  1705 |         clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  1706 |         upload: '<path d="M12 3v12M7 8l5-5 5 5"/><path d="M5 21h14"/>',
  1707 |         download: '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 21h14"/>',
  1708 |         refresh: '<path d="M20 7h-5V2M4 17h5v5"/><path d="M5.5 9A8 8 0 0 1 19 6.5L20 7M4 17l1-1a8 8 0 0 0 13.5-2"/>',
  1709 |         shield: '<path d="M12 2 4 5v6c0 5 3.4 9.3 8 11 4.6-1.7 8-6 8-11V5z"/><path d="m9 12 2 2 4-5"/>',
  1710 |         key: '<circle cx="8" cy="15" r="4"/><path d="m11 12 9-9M17 6l2 2M14 9l2 2"/>',
  1711 |         camera: '<path d="M4 7h4l2-3h4l2 3h4a2 2 0 0 1 2 2v10H2V9a2 2 0 0 1 2-2z"/><circle cx="12" cy="13" r="4"/>',
  1712 |         search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  1713 |         mapPin: '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="2.5"/>',
  1714 |         filter: '<path d="M3 5h18l-7 8v6l-4 2v-8z"/>',
  1715 |         arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  1716 |         arrowUp: '<path d="M12 19V5M6 11l6-6 6 6"/>',
  1717 |         arrowDown: '<path d="M12 5v14M18 13l-6 6-6-6"/>',
  1718 |         user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  1719 |         settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21H9.6v-.1A1.7 1.7 0 0 0 8.5 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H3V9.6h.1A1.7 1.7 0 0 0 4.6 8.5a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V3h4v.1A1.7 1.7 0 0 0 15.5 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9c.1.4.3.7.6 1 .3.3.7.4 1.1.4h.1v4h-.1c-.4 0-.8.1-1.1.4-.3.3-.5.6-.6 1z"/>',
  1720 |         logout: '<path d="M10 17l5-5-5-5M15 12H3"/><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>',
  1721 |         candle: '<path d="M9 22V9h6v13M8 22h8M12 9c-2-2-1-5 1-7 1 2 3 3 2 5-.5 1-1.5 2-3 2z"/>',
  1722 |         sync: '<path d="M20 11a8 8 0 0 0-14.8-4M4 3v4h4M4 13a8 8 0 0 0 14.8 4M20 21v-4h-4"/>',
  1723 |         info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  1724 |         lock: '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>'
  1725 |       };
  1726 | 
  1727 |       const icon = (name, cls = '') => `<svg class="icon ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ICONS.more}</svg>`;
  1728 |       const money = n => new Intl.NumberFormat('ko-KR').format(n) + '원';
  1729 |       const esc = v => String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
  1730 |       const DEFAULT_CHECKIN_TIME='16:00', DEFAULT_CHECKOUT_TIME='11:00';
  1731 |       const CALENDAR_WEEKDAYS=Object.freeze(['일','월','화','수','목','금','토']);
  1732 |       const KR_HOLIDAY_FIXTURE=Object.freeze({
  1733 |         jurisdiction:'KR',mode:'demo-static',coverage:['2026-01-01','2026-12-31'],verifiedAt:'2026-08-18',
  1734 |         sources:Object.freeze([
  1735 |           'https://www.kasa.go.kr/bbs/BBSMSTR_000000000010/view.do?nttId=B000000001860Pe2zT3',
  1736 |           'https://www.law.go.kr/LSW/lsRvsDocListP.do?chrClsCd=010202&lsId=002404&lsRvsGubun=all',
  1737 |           'https://www.nec.go.kr/site/nec/ex/bbs/View.do?bcIdx=289351&cbIdx=1104'
  1738 |         ]),
  1739 |         dates:Object.freeze({
  1740 |           '2026-01-01':{name:'신정',kind:'national'},
  1741 |           '2026-02-16':{name:'설날 연휴',kind:'traditional'},
  1742 |           '2026-02-17':{name:'설날',kind:'traditional'},
  1743 |           '2026-02-18':{name:'설날 연휴',kind:'traditional'},
  1744 |           '2026-03-01':{name:'삼일절',kind:'national'},
  1745 |           '2026-03-02':{name:'삼일절 대체공휴일',kind:'substitute'},
  1746 |           '2026-05-01':{name:'노동절',kind:'national'},
  1747 |           '2026-05-05':{name:'어린이날',kind:'national'},
  1748 |           '2026-05-24':{name:'부처님오신날',kind:'traditional'},
  1749 |           '2026-05-25':{name:'부처님오신날 대체공휴일',kind:'substitute'},
  1750 |           '2026-06-03':{name:'제9회 전국동시지방선거',kind:'election'},
  1751 |           '2026-06-06':{name:'현충일',kind:'national'},
  1752 |           '2026-07-17':{name:'제헌절',kind:'national'},
  1753 |           '2026-08-15':{name:'광복절',kind:'national'},
  1754 |           '2026-08-17':{name:'광복절 대체공휴일',kind:'substitute'},
```

### occurrence 2 · line 3076

```html
  3060 |               ${state.role==='maid'?`<div class="demo-field"><label for="demo-maid-account">메이드 계정</label><select id="demo-maid-account" data-control="maid-account">${MAIDS.map(maid=>`<option value="${maid.id}" ${signedInMaidId()===maid.id?'selected':''}>${esc(maid.name)}</option>`).join('')}</select></div>`:''}
  3061 |               <div class="demo-field"><label for="demo-time">시간</label><select id="demo-time" data-control="time"><option ${state.time==='00:00'?'selected':''}>00:00</option><option ${state.time==='10:30'?'selected':''}>10:30</option><option ${state.time==='10:32'?'selected':''}>10:32</option><option ${state.time==='11:05'?'selected':''}>11:05</option><option ${state.time==='11:59'?'selected':''}>11:59</option><option ${state.time==='12:00'?'selected':''}>12:00</option><option ${state.time==='13:05'?'selected':''}>13:05</option><option ${state.time==='16:05'?'selected':''}>16:05</option><option ${state.time==='21:10'?'selected':''}>21:10</option><option ${state.time==='21:55'?'selected':''}>21:55</option><option ${state.time==='22:15'?'selected':''}>22:15</option><option ${state.time==='23:59'?'selected':''}>23:59</option></select></div>
  3062 |               <div class="demo-field"><label for="demo-network">네트워크</label><select id="demo-network" data-control="network"><option value="online" ${state.network==='online'?'selected':''}>정상</option><option value="offline" ${state.network==='offline'?'selected':''}>오프라인</option><option value="stale" ${state.network==='stale'?'selected':''}>오래된 데이터</option></select></div>
  3063 |               <div class="demo-field scenario"><label for="demo-scenario">시나리오</label><select id="demo-scenario" data-control="scenario">${Object.entries(SCENARIOS).map(([id,s])=>`<option value="${id}" ${state.scenario===Number(id)?'selected':''}>${id==='0'?'기본':id+'.'} ${esc(s.title)}</option>`).join('')}</select></div>
  3064 |               <button class="btn btn-ghost demo-reset" type="button" data-action="reset">${icon('refresh','icon-sm')}초기 상태로 재설정</button>
  3065 |             </div>
  3066 |           </div>
  3067 |         </section>`;
  3068 |       }
  3069 | 
  3070 |       function renderSidebar(nav) {
  3071 |         const maid=signedInMaid();
  3072 |         return `<aside class="sidebar" aria-label="주요 내비게이션">
  3073 |           <div class="brand"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리</div></div></div>
  3074 |           <div class="identity"><div class="avatar">${state.role==='admin'?'관':esc(maid.name[0])}</div><div><strong>${state.role==='admin'?'관리자':esc(maid.name)}</strong><span>${state.role==='admin'?'최고 관리자':'메이드'}</span></div></div>
  3075 |           <nav class="side-nav">${nav.map(n=>`<button class="nav-btn" type="button" data-action="nav" data-view="${n.id}" ${currentView()===n.id&&!state.detail?'aria-current="page"':''}>${icon(n.icon)}<span>${n.label}</span></button>`).join('')}</nav>
  3076 |           <div class="side-foot">${button('로그인 상태 보기','logout','ghost')}</div>
  3077 |         </aside>`;
  3078 |       }
  3079 | 
  3080 |       function addAdminHelp(root,headingText,id,label,text,{rename=''}={}) {
  3081 |         [...root.querySelectorAll('h2,h3')].filter(heading=>heading.textContent.trim()===headingText).forEach((heading,index)=>{
  3082 |           if(rename)heading.textContent=rename;
  3083 |           if(heading.closest('.help-title'))return;
  3084 |           const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(`${id}-${index}`,label,text));
  3085 |         });
  3086 |       }
  3087 |       function addAdminHelpToElement(heading,id,label,text) {
  3088 |         if(!heading||heading.closest('.help-title'))return;
  3089 |         const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(id,label,text));
  3090 |       }
  3091 |       function applyMaidCopyPolicy(root) {
  3092 |         if(state.role!=='maid')return;
  3093 |         root.querySelectorAll('.scenario-coach,.week-card-head p,.weekly-availability .assignment-notice,.assigned-preview .meta,.assigned-preview > .audit-note,.work-hero p,.mobile-section-title p,.pay-week-toolbar p,.maid-pay-history-head p,.maid-pay-footnote').forEach(element=>element.remove());
  3094 |         root.querySelectorAll('.assignment-notice p').forEach(paragraph=>{const title=paragraph.querySelector('strong');if(title)paragraph.replaceChildren(title);});
  3095 |         root.querySelectorAll('.task-row p').forEach(paragraph=>{
  3096 |           if(paragraph.textContent.includes('해당 객실별 승인 합계'))paragraph.textContent=paragraph.textContent.replace('해당 객실별 승인 합계','승인 금액');
  3097 |           if(paragraph.textContent.includes('판정 확인 또는 이의 메모만 가능합니다'))paragraph.remove();
  3098 |         });
  3099 |         root.querySelectorAll('.pay-hero > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*데모 (?:지급 이력|금액)$/,'');});
  3100 |         root.querySelectorAll('.maid-pay-week-head small').forEach(label=>{label.textContent=label.textContent.includes('지급 기록액')?'지급 기록액':'승인 확정';});
  3101 |         root.querySelectorAll('.maid-pay-week-stats span').forEach(label=>{if(label.textContent.trim()==='현재 원장 예상')label.textContent='예상 금액';});
  3102 |         root.querySelectorAll('.maid-pay-disclosure > span:first-child').forEach(label=>{label.textContent=label.textContent.replace('작업 상세','청소 내역');});
  3103 |         root.querySelectorAll('.maid-pay-task > div:first-child > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*제출\/회차.*$/,'');});
  3104 |         root.querySelectorAll('.maid-pay-week .notice-danger strong').forEach(label=>{label.textContent=label.textContent.replace('현재 원장','현재 합계');});
  3105 |         root.querySelectorAll('.setting-card p').forEach(copy=>{
  3106 |           const text=copy.textContent.trim();
  3107 |           if(text==='담당·시작·완료·제출 이력')copy.textContent='최근 업무 확인';
  3108 |           if(text==='브라우저 알림 권한 전')copy.textContent='알림 권한 확인 필요';
  3109 |           if(text==='판정 확인·이의 메모만 가능')copy.textContent='판정과 답변 확인';
  3110 |         });
```

### occurrence 3 · line 3367

```html
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
  3354 | 
  3355 |       function renderMaids() {
  3356 |         const cards=MAIDS.map(m=>`<article class="card setting-card"><div class="avatar">${m.name[0]}</div><div style="min-width:0;flex:1"><h3>${m.name} · 데모</h3><p>${m.phone} · 관리자 배정 ${m.assigned}건<br>${m.id==='m1'&&state.maidStatus!=='active'?state.maidStatus:m.active}</p>${button('상세 보기','maid-detail','outline',`data-id="${m.id}"`)}</div></article>`).join('');
  3357 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>메이드 계정·업무 현황</h2><span class="meta">담당·실제 수행·제출·수익 귀속을 분리해 보존</span></div><div class="actions">${button('계정 추가','demo-info','primary')}</div></div><div class="settings-grid">${cards}</div>`;
  3358 |       }
  3359 | 
  3360 |       function renderAdminMore() {
  3361 |         return renderCoach()+renderNetworkNotice()+`<div class="settings-grid">
  3362 |           ${settingCard('wallet','주급·지급',`지난주 상태 ${paymentWeekSummaryFor().label} · 메이드별 외부 송금 기록`,button('지급 상세','pay-detail','outline'))}
  3363 |           ${settingCard('settings','객실 타입 청소요금·예상시간','청소요금은 8월 시트 정본 · 예상시간은 데모',button('청소요금 보기','rates','outline'))}
  3364 |           ${settingCard('list','청소 템플릿',`초안·미리보기·게시 버전 · 현재 ${state.template}`,button('템플릿 관리','template','outline'))}
  3365 |           ${settingCard('bell','알림 상태',state.notificationsEnabled?'이 기기 알림 허용 데모':'권한 요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}
  3366 |           ${settingCard('shield','감사 이력','PIN 조회 사실·검수·단가·지급 수행자 기록',button('최근 이력 보기','audit-log','outline'))}
  3367 |           ${settingCard('lock','로그인·보안 상태','최초 변경·5회 실패·15분 잠금 데모',button('로그인 상태 보기','logout','outline'))}
  3368 |         </div>`;
  3369 |       }
  3370 | 
  3371 |       function settingCard(iconName,title,desc,action) { return `<article class="card setting-card"><div class="setting-icon">${icon(iconName)}</div><div style="min-width:0;flex:1"><h3>${title}</h3><p>${desc}</p>${action}</div></article>`; }
  3372 | 
  3373 |       function publicJobs() {
  3374 |         return [
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
  3390 | 
  3391 |       function renderMaidMy() {
  3392 |         const myJobs=[
  3393 |           {room:'350',type:'standard',kind:'퇴실 청소',status:state.jobs['350'],schedule:'11:00부터 시작 · 15:30 준비 마감'},
  3394 |           {room:'528',type:'premium',kind:'퇴실 청소',status:state.jobs['528'],schedule:'10:00 시작 가능 · 14:00 다음 입실'}
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
```

### occurrence 4 · line 5625

```html
  5609 |       }
  5610 |       function renderAdminPayDetailView() {
  5611 |         const parsed=parseAdminPayDetailId(state.detail?.id),weeks=adminPayWeeks(),cfg=parsed?weeks.find(week=>week.start===parsed.weekStart):null,maid=parsed?MAIDS.find(item=>item.id===parsed.maidId):null;
  5612 |         if(state.role!=='admin'||!cfg||!maid)return renderCoach()+renderNetworkNotice()+detailHeader('주급 산출 내역을 열 수 없습니다','관리자 권한과 저장된 주차·메이드 식별자를 다시 확인합니다.')+`<section class="card card-pad"><div class="notice notice-danger"><div><strong>유효한 주급 원장을 찾지 못했습니다.</strong><br>주급 정산 목록으로 돌아가 저장된 메이드의 산출 보기 버튼을 선택하세요.</div></div></section>`;
  5613 |         state.adminView='maids';state.adminMaidTab='pay';state.adminPayWeek=parsed.weekStart;
  5614 |         const tasks=cfg.tasksByMaid?.[maid.id]||[],totals=payrollTaskTotals(tasks),record=paymentRecordFor(cfg.start,maid.id),payment=paymentStatusMeta(cfg.start,maid.id,totals.confirmed),paymentAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=paymentAmount!==totals.confirmed,confirmedTasks=tasks.filter(task=>task.stage==='confirmed'),pendingTasks=tasks.filter(task=>task.stage==='pending'),excludedTasks=tasks.filter(task=>task.stage==='excluded'),calculatedConfirmed=confirmedTasks.reduce((sum,task)=>sum+(task.amount||0),0),calculatedPending=pendingTasks.reduce((sum,task)=>sum+(task.amount||0),0),matches=calculatedConfirmed===totals.confirmed&&calculatedPending===totals.pending;
  5615 |         const rows=tasks.length?tasks.map(renderAdminPayLedgerRow).join(''):`<section class="inline-empty"><h3>저장된 청소 내역이 없습니다</h3><p>이 주차의 객실별 주급 산출 원장이 생성되면 여기에 표시합니다.</p></section>`;
  5616 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${esc(maid.name)} · 주급 산출 내역`,`${weekRangeLabel(cfg.start,true)} · 객실별 청소 원장 · 관리자 전용`)+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="section-head"><div><h3>왜 ${money(totals.confirmed)}인가요?</h3><span class="meta">확정 포함 행만 더한 객실별 계산</span></div>${statusBadge(payment.label,payment.tone)}</div>${paymentDrift?`<div class="notice notice-danger" style="margin-bottom:12px"><div><strong>지급 기록액 ${money(paymentAmount)} · 현재 원장 ${money(totals.confirmed)}</strong><br>지급 진행 뒤 원장이 바뀌어 차이가 생겼습니다. 완료 기록을 직접 고치지 말고 정정·상계로 처리합니다.</div></div>`:''}<div class="pay-ledger-summary"><div><span>확정 주급</span><strong>${money(totals.confirmed)}</strong><small>${confirmedTasks.length}건 합계</small></div><div><span>검수 전 예상</span><strong>${money(totals.confirmed+totals.pending)}</strong><small>확정 + 대기</small></div><div><span>검수 대기</span><strong>${money(totals.pending)}</strong><small>${pendingTasks.length}건</small></div><div><span>${['PAYING','CHECK','PAID'].includes(payment.status)?'잠근 지급액':'합계 제외'}</span><strong>${['PAYING','CHECK','PAID'].includes(payment.status)?money(paymentAmount):`${excludedTasks.length}건`}</strong><small>${['PAYING','CHECK','PAID'].includes(payment.status)?`${payment.label} · ${paymentManagerLabel(record)}`:'실제 반영 0원'}</small></div></div></section><section class="pay-ledger-list" aria-label="${esc(maid.name)} ${weekRangeLabel(cfg.start)} 객실별 청소 산출 내역">${rows}</section><section class="card card-pad pay-ledger-reconcile"><div><span>객실별 확정 행 합계</span><strong>${money(calculatedConfirmed)}</strong></div><div><span>카드의 현재 원장</span><strong>${money(totals.confirmed)}</strong></div><div><span>검수 대기 행 합계</span><strong>${money(calculatedPending)}</strong></div><div>${statusBadge(matches?'원장 합계 일치':'원장 합계 불일치',matches?'green':'red')}</div></section></div><aside class="detail-stack"><section class="card card-pad"><h3>계산 규칙</h3><ul class="bullet-list"><li>객실 타입 기본 청소요금은 8월 객실현황 시트 정본을 사용합니다.</li><li>폭탄방 승인 시 <strong>해당 객실</strong> 기본요금만 같은 금액으로 한 번 더합니다.</li><li>청소 전체 반려와 처음 청소한 본인의 재청소는 0원이며 합계에 포함하지 않습니다.</li><li>검수 대기 금액은 예상에만 보이고 확정 주급에는 포함하지 않습니다.</li></ul></section><section class="card card-pad"><h3>데이터 범위</h3><p class="audit-note">객실 타입·기본 청소요금은 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모 스냅샷입니다. 앱은 실제 송금이나 자동 차감을 수행하지 않습니다.</p></section></aside></div>`;
  5617 |       }
  5618 |       function renderComplaintsPanel() {
  5619 |         const active=state.complaints.filter(c=>!c.deleted);
  5620 |         const maidOptions=MAIDS.map(maid=>`<option value="${maid.name}">${esc(maid.name)}</option>`).join('');
  5621 |         return `<div class="notice notice-info">컴플레인·벌점은 주급에서 자동 차감되지 않습니다. 삭제는 활성 목록에서만 숨기고 감사 이력은 남깁니다.</div><form id="complaint-form" class="card complaint-form"><div class="field"><label for="complaint-maid">메이드</label><select id="complaint-maid" class="select-control">${maidOptions}</select></div><div class="field"><label for="complaint-kind">기록 종류</label><select id="complaint-kind" class="select-control" data-control="complaint-type"><option value="complaint" ${state.complaintType==='complaint'?'selected':''}>컴플레인</option><option value="penalty" ${state.complaintType==='penalty'?'selected':''}>벌점</option></select></div><div class="field reason-field"><label for="complaint-reason">사유</label><input id="complaint-reason" class="input-control" required placeholder="사유를 입력하세요"></div><div class="field"><label for="complaint-points">벌점</label><input id="complaint-points" class="input-control" type="number" min="1" max="10" value="1" ${state.complaintType==='penalty'?'':'disabled'}></div><button class="btn btn-primary" type="submit">기록 추가</button></form><section class="card" aria-label="활성 컴플레인과 벌점">${active.length?active.map(c=>`<div class="complaint-row"><strong>${esc(c.maid)}</strong><span>${statusBadge(c.type,c.type==='벌점'?'amber':'neutral')}</span><span>${esc(c.reason)}</span><span>${c.points?`${c.points}점`:'—'}</span><div class="job-actions">${button('상세','complaint-detail','outline',`data-id="${c.id}"`)}${button('삭제','delete-complaint','outline',`data-id="${c.id}" ${isLocked()?'disabled':''}`)}</div></div>`).join(''):`<div class="state-panel"><p>활성 기록이 없습니다. 삭제 이력은 감사 기록에 남아 있습니다.</p></div>`}</section>`;
  5622 |       }
  5623 | 
  5624 |       function renderAdminMore() {
  5625 |         return renderCoach()+renderNetworkNotice()+`<div class="settings-grid">${settingCard('alert','컴플레인·벌점','메이드 지정 · 사유 입력 · 삭제/복구 이력',button('관리','go-complaints','outline'))}${settingCard('list','전체 이력','PIN 원문을 제외한 예약·업무·지급 감사 이력',button('이력 보기','audit-log','outline'))}${settingCard('settings','청소 설정','시트 청소요금·데모 예상시간과 템플릿',`${button('청소요금 보기','rates','outline')}${button('템플릿','template','soft')}`)}${settingCard('shield','계정·로그인','로그인 비밀번호는 객실 PIN과 분리',button('로그인 상태','logout','outline'))}</div>`;
  5626 |       }
  5627 | 
  5628 |       function startTimeFor(no) { const actual=ROOMS.find(room=>room.no===no)?.actualCheckoutAt?.slice(11,16);if(actual)return actual;if(no==='332'&&state.conflict==='resolved')return state.conflictRecord.afterCheckout;return ({'117':'13:00','350':'11:00','332':'11:00','528':'10:00','536':'11:00','639':'11:00','142':'13:00','211':'11:00','352':'10:00'})[no]||'11:00'; }
  5629 |       function attemptPlanDate(attempt,fallback=state.selectedDate) { return attempt?.workDate||timestampIsoDate(attempt?.createdAt||attempt?.startedAt,fallback)||fallback; }
  5630 |       function attemptEffectiveDate(attempt,fallback=state.selectedDate) { return attempt?.effectiveDate||attemptPlanDate(attempt,fallback); }
  5631 |       function attemptIsRollover(attempt) { return !!attempt&&attemptEffectiveDate(attempt)!==attemptPlanDate(attempt); }
  5632 |       function attemptAccessStatus(no,attempt=state.cleaningAttempts?.[currentAttemptId(no)]) {
  5633 |         if(!attempt)return {allowed:false,reason:'수행 회차 없음',start:startTimeFor(no),end:null,workDate:null};
  5634 |         const workDate=attemptPlanDate(attempt,state.selectedDate),effectiveDate=attemptEffectiveDate(attempt,state.selectedDate),continued=attemptIsRollover(attempt)&&!!attempt.startedAt,rolledCheckout=attemptIsRollover(attempt)&&attempt.kind==='퇴실 청소'&&!attempt.accessReviewRequired,start=continued||rolledCheckout?'00:00':attempt.accessStart||attempt.checkoutSnapshot||startTimeFor(no),end=(continued||rolledCheckout)&&!attempt.accessReviewRequired?null:attempt.accessEnd||null,minutes=timeMinutes(state.time),sameEffectiveDate=state.selectedDate===effectiveDate;
  5635 |         if(attempt.accessReviewRequired)return {allowed:false,reason:'출입시간 재확인 필요',start:attempt.accessStart||attempt.checkoutSnapshot||startTimeFor(no),end:attempt.accessEnd||null,workDate,effectiveDate};
  5636 |         return {allowed:sameEffectiveDate&&minutes>=timeMinutes(start)&&(!end||minutes<=timeMinutes(end)),reason:!sameEffectiveDate?`${dateLabel(effectiveDate)} 수행일 대기`:minutes<timeMinutes(start)?`${start} 시작 대기`:end&&minutes>timeMinutes(end)?`${end} 출입 종료`:'출입 가능',start,end,workDate,effectiveDate};
  5637 |       }
  5638 |       function snapshotForAttempt(no,attempt) {
  5639 |         if(attempt?.templateSnapshot)return attempt.templateSnapshot;
  5640 |         const snapshot=templateSnapshotFor(no,attempt?.kind||'퇴실 청소');
  5641 |         if(attempt&&snapshot)attempt.templateSnapshot=snapshot;
  5642 |         return snapshot;
  5643 |       }
  5644 |       function uploadFromPhotoRule(rule,status='empty',priorUpload=null) {
  5645 |         const upload={...demoUpload(rule.id,rule.label,rule.required,status,rule.fixture||'supply'),zone:rule.zone||'사진',description:rule.description||'청소 완료 상태를 촬영합니다.',fixture:rule.fixture||priorUpload?.fixture||'supply',multiple:!!rule.multiple,maxPhotos:photoUploadLimit(rule),repeatable:!!rule.repeatable,instance:rule.instance||1,instanceCount:rule.instanceCount||1};
  5646 |         if(uploadUsesPhotoCollection(upload)){
  5647 |           const priorItems=Array.isArray(priorUpload?.images)?priorUpload.images.map(item=>({...item,image:item.image?{...item.image}:null})):priorUpload?.image&&['done','failed','uploading'].includes(priorUpload.status)?[{id:`${rule.id}-photo-legacy-1`,status:priorUpload.status,image:{...priorUpload.image}}]:[];
  5648 |           upload.images=priorItems.slice(0,photoUploadLimit(upload));upload.image=null;
  5649 |           if(!upload.images.length&&status==='done')upload.images=[{id:`${rule.id}-photo-demo-1`,status:'done',image:{...demoUploadImageFixture(rule.fixture||'supply')}}];
  5650 |           syncPhotoCollectionStatus(upload);
  5651 |         }else if(priorUpload?.image)upload.image={...priorUpload.image};
  5652 |         return upload;
  5653 |       }
  5654 |       function createTaskInputsFromSnapshot(snapshot,prior={}) {
  5655 |         const priorUploads=prior.uploads||[],priorFor=rule=>{
  5656 |           const exact=priorUploads.find(upload=>upload.id===rule.id);
  5657 |           if(exact)return {status:exact.status||'empty',upload:exact};
  5658 |           return {status:'empty',upload:null};
  5659 |         };
```

### occurrence 5 · line 6173

```html
  6157 |             {room:'350호',kind:'퇴실 청소',date:'7월 6일',amount:16000,status:'승인 확정',tone:'green'}
  6158 |           ]}]:adminPayWeeks().slice(1).map((adminWeek,index)=>{const amount=adminWeek.people.find(person=>person[0]===currentMaid.name)?.[1]||0;return {id:adminWeek.start,group:index===0?'last':'older',label:index===0?'지난주':'이전 주',period:weekRangeLabel(adminWeek.start),confirmed:amount,pending:0,status:adminWeek.status,tone:adminWeek.tone,paidAt:adminWeek.status==='지급 완료'?`${addIsoDays(adminWeek.start,7).replace(/^2026-0?/,'').replace('-','월 ')}일 지급 기록`:'외부 송금 확인 대기',tasks:[{room:'주간 합계',kind:'승인 객실별 합계 스냅샷',date:weekRangeLabel(adminWeek.start),amount,status:'승인 원장 합계 · 데모',tone:'green'}]};}))
  6159 |         ];
  6160 |         const selectedWeek=state.maidPaySelectedWeek;
  6161 |         const pastWeeks=weeks.filter(week=>week.id!=='2026-08-10');
  6162 |         const shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  6163 |         const weekCard=week=>{
  6164 |           const open=state.maidPayOpenWeek===week.id;
  6165 |           return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>승인 확정 · ${esc(currentMaid.name)} 데모 금액</small></div>${statusBadge(week.status,week.tone)}</div><div class="maid-pay-week-stats"><div><span>검수 전 예상</span><strong>${money(week.confirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${task.room} · ${task.kind}</strong><span>${task.date}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''} · 데모 금액</span>${task.breakdownText?`<span class="bomb-room-pay-breakdown">${esc(task.breakdownText)}</span>`:task.bombStatus&&task.bombStatus!=='none'?`<span class="bomb-room-pay-breakdown">기본 ${money(task.baseAmount)} + 폭탄방 추가 ${money(task.bombBonus)} = ${money(task.amount)}</span>`:''}${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.potential?'승인 시 ':''}${money(task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;
  6166 |         };
  6167 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택';
  6168 |         const historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  6169 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel('2026-08-10')} · 데모 금액</span><strong>${money(currentConfirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(currentExpected)}</b></div><div><span>검수 대기</span><b>${money(currentPending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong><br>청소 완료 후 관리자 검수 승인을 받은 금액만 확정됩니다. 폭탄방 승인 건은 내역에서 기본 요금과 같은 추가 요금을 분리해 표시합니다.</div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>모든 기록을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">표시 금액과 객실은 기능 확인을 위한 데모 데이터입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  6170 |       }
  6171 | 
  6172 |       function renderMaidMore() {
  6173 |         return renderCoach()+`<div class="settings-grid">${settingCard('user','내 정보','로그인 비밀번호·연락처·계정 상태',button('계정 상태','logout','outline'))}${settingCard('alert','내 컴플레인','판정 확인·이의 메모만 가능',button('내용 보기','complaint-detail','outline'))}${settingCard('list','업무 이력','담당·시작·완료·제출 이력',button('이력 보기','audit-log','outline'))}${settingCard('bell','알림 설정',state.notificationsEnabled?'앱 내부 알림 확인 가능':'브라우저 알림 권한 전',button('알림 설정','notification-permission','outline'))}</div>`;
  6174 |       }
  6175 | 
  6176 |       function roomPrimaryAction(no,p) {
  6177 |         const room=ROOMS.find(item=>item.no===no);
  6178 |         if(p.key==='blocked')return roomIsOnHold(no)?['차단 정보 확인','room-detail','danger']:state.roomStopped[no]?['운영 중지 상태 확인','operation-status','danger']:['배정 불가 사유 확인','room-detail','danger'];
  6179 |         if(p.key==='cleaning')return ['청소 상태 확인','cleaning-detail','primary'];
  6180 |         if(p.key==='occupied')return ['예약 관리','reservation-edit','primary'];
  6181 |         if(p.key==='available')return ['예약 등록','reservation-edit','primary'];
  6182 |         return ['전체 상세','demo-info','primary'];
  6183 |       }
  6184 |       function renderStayoverPanel(no='142') {
  6185 |         const room=ROOMS.find(item=>item.no===no),draft=state.drafts.find(item=>item.room===no&&item.kind==='연박 청소'),snapshot=draft?.templateSnapshot||templateSnapshotFor(no,'연박 청소'),request=room?.stayoverRequest;
  6186 |         return `<section class="card card-pad" aria-labelledby="stayover-panel-${no}"><div class="section-head"><div><h3 id="stayover-panel-${no}">투숙 중 청소 요청</h3><p class="audit-note">손님은 계속 투숙하고 청소 작업만 별도로 배정합니다.</p></div>${statusBadge(draft?'배정 준비 작업 생성됨':'요청 미입력','neutral')}</div><div class="info-grid"><div class="info-item"><span>현재 상태</span><strong>투숙 중 유지</strong></div><div class="info-item"><span>다음 입실 준비</span><strong>별도 작업</strong></div><div class="info-item"><span>청소요금 · 8월 시트</span><strong>${money(snapshot?.rate??ROOM_TYPES[room?.type||'standard'].rate)}</strong></div><div class="info-item"><span>예상시간 · 데모</span><strong>${snapshot?.minutes??ROOM_TYPES[room?.type||'standard'].minutes}분</strong></div></div>${draft&&request?`<div class="notice notice-success" style="margin:12px 0"><div><strong>${esc(request.date)} 투숙 중 청소 배정 준비</strong><br>출입 ${esc(request.accessStart)}–${esc(request.accessEnd)} · ${esc(request.requestDue)}까지 요청 완료 · ${esc(snapshot?.name||'연박 청소')} ${esc(snapshot?.version||'v3')} 스냅샷</div></div><p class="audit-note">관리자 배정 전에는 메이드에게 보이지 않으며, 이 작업만으로 다음 예약 준비가 완료되지는 않습니다.</p>${button('내일 배정에서 확인','go-cleaning-drafts','outline')}`:''}</section>`;
  6187 |       }
  6188 |       function renderRoomDetailStandard(no) {
  6189 |         const room=ROOMS.find(r=>r.no===no)||ROOMS[0], type=ROOM_TYPES[room.type], p=roomPresentation(no), candle=state.candles[no]||0, primary=roomPrimaryAction(no,p), special=roomReservationStatus(room);
  6190 |         const occupied=room.occupancy==='occupied',reservation=currentOccupiedReservation(room)||state.reservations.find(item=>item.id===room.reservationProjectionId&&item.status==='active')||null,reservationActionLabel=occupied&&!reservation?'투숙 정보 입력':room.reservationCheckinAt?'예약 관리':'예약 등록',reservationRegistrationStatus=occupied&&!occupiedReservationEnd(room)?'현재 투숙 정보 입력 후 가능':occupiedStayNeedsCheckoutUpdate(room)?'현재 체크아웃 갱신 후 가능':'가능',checkinDisplay=reservationMomentLabel(reservation?.checkInAt||room.reservationCheckinAt),checkoutDisplay=reservationMomentLabel(reservation?.checkOutAt||room.reservationCheckoutAt);
  6191 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${no}호`,`${type.name} · ${elevatorLabel(room)}`)+`<div class="detail-grid"><div class="detail-stack"><section class="card card-pad"><div class="room-card-head"><div><h3>${no}호 현재 상태</h3><p>예약 가능과 현재 입실 가능을 별도로 판단합니다.</p></div><div class="badge-row">${statusBadge(p.status,p.tone)}${p.cleaning&&p.key!=='cleaning'?statusBadge(`청소 필요 · ${p.cleaningKind||'청소'}`,'amber'):''}</div></div><div class="time-band" aria-label="한 고객 예약의 체크인부터 체크아웃까지"><span>체크인 <strong>${esc(checkinDisplay)}</strong></span><span>→</span><span>체크아웃 <strong>${esc(checkoutDisplay)}</strong></span>${special.early?`<span class="special">얼리 체크인 · ${esc(special.earlyOffset)}</span>`:''}${special.late?`<span class="special">레이트 체크아웃 · ${esc(special.lateOffset)}</span>`:''}</div><div class="status-band ${p.tone}"><div><strong>${esc(p.status)}</strong><span>${esc(p.reason)}</span></div>${statusBadge(p.available===null?'입실 판단 전':p.available?'현재 입실 가능':'현재 입실 불가',p.available?'green':occupied?'neutral':p.tone)}</div>${renderPinRow(no)}</section><section class="card card-pad"><div class="section-head"><h3>예약·입퇴실</h3><div class="actions">${button(reservationActionLabel,'reservation-edit','outline',`data-id="${no}"`)}</div></div><div class="info-grid"><div class="info-item"><span>예약 등록</span><strong>${esc(reservationRegistrationStatus)}</strong></div><div class="info-item"><span>현재 입실</span><strong>${p.available===null?'판단 전':p.available?'가능':'불가'}</strong></div><div class="info-item"><span>체크인 일시</span><strong>${esc(checkinDisplay)}</strong></div><div class="info-item"><span>체크아웃 일시</span><strong>${esc(checkoutDisplay)}</strong></div><div class="info-item"><span>체크인 상태 · 16:00 기준</span><strong>${esc(reservationStatusText(special,'checkin'))}</strong></div><div class="info-item"><span>체크아웃 상태 · 11:00 기준</span><strong>${esc(reservationStatusText(special,'checkout'))}</strong></div></div><p class="audit-note" style="margin:10px 0 0">체크인·체크아웃 시각에 따라 얼리 체크인과 레이트 체크아웃 여부를 확인합니다. 미래 예약은 객실이 아직 준비되지 않아도 등록할 수 있지만 현재 입실은 준비 완료 전까지 차단됩니다.</p></section>${renderOccupancyPanel(no)}${renderCheckoutInspectionPanel(no)}${occupied&&room.stayoverRequest?renderStayoverPanel(no):''}${occupied?'':`<section class="card card-pad"><div class="section-head"><h3>촛불 현황</h3>${statusBadge(candle?`${candle}개`:'없음',candle?'amber':'green')}</div><p class="audit-note">투숙 중이 아닌 객실은 운영 상황에 맞게 관리자가 유연하게 변경할 수 있습니다.</p><div class="candle-stepper" role="group" aria-label="${no}호 관리자 촛불 수량"><button class="btn btn-outline" type="button" data-action="candle-change" data-id="${no}" data-delta="-1" aria-label="촛불 1개 줄이기" ${candle<1?'disabled':''}>−</button><div class="candle-stepper-value" aria-live="polite"><strong>${candle}개</strong><span>현재 객실 수량</span></div><button class="btn btn-outline" type="button" data-action="candle-change" data-id="${no}" data-delta="1" aria-label="촛불 1개 늘리기">+</button></div></section>`}<section class="card card-pad"><div class="section-head"><h3>청소 작업</h3>${statusBadge(statusLabel(state.jobs[no]),['cleaning','upload','inspection'].includes(state.jobs[no])?'amber':'neutral')}</div><div class="info-grid"><div class="info-item"><span>작업</span><strong>${cleaningLabel(state.jobs[no])}</strong></div><div class="info-item"><span>담당</span><strong>${esc(room.assignee)}</strong></div><div class="info-item"><span>청소요금 · 8월 시트</span><strong>${money(type.rate)}</strong></div><div class="info-item"><span>예상시간 · 데모</span><strong>${type.minutes}분</strong></div></div>${['public','draft','future','scheduled'].includes(state.jobs[no])?`<div style="margin-top:12px">${button('청소 담당 직접 배정','direct-assign','primary',`data-id="${no}"`)}</div>`:''}${renderManualCleaningToggle(no)}</section></div><aside class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>운영 상태</h3>${statusBadge(state.roomStopped[no]?'운영 중지':'정상',state.roomStopped[no]?'red':'green')}</div>${state.roomStopped[no]?`<div class="notice notice-danger">고객 배정이 중지됐습니다.${state.roomMoves[no]?` 대체 객실 ${state.roomMoves[no].to}호를 배정했고 원 이력은 보존됩니다.`:''}</div>${button('운영 재개','resume-operation','success',`data-id="${no}"`)}`:`<p class="audit-note">모든 객실 상태에서 운영 중지할 수 있으며, 다른 객실 배정은 이 흐름 안에서만 진행합니다.</p>${button('운영 중지·대체 객실','operation-status','danger',`data-id="${no}"`)}`}</section><section class="card card-pad"><h3>객실 사건 타임라인</h3>${renderTimeline(no)}</section></aside></div><div class="sticky-command"><button class="btn btn-${primary[2]}" type="button" data-action="${primary[1]}" data-id="${no}">${primary[0]}</button></div>`;
  6192 |       }
  6193 | 
  6194 |       function renderRoomConflict332() {
  6195 |         const room=ROOMS.find(r=>r.no==='332'), type=ROOM_TYPES[room.type], record=state.conflictRecord, active=state.conflict==='active', special=reservationTimeStatus(room.checkin,record.afterCheckout);
  6196 |         const statePanel=active?`<section class="card card-pad" style="border-color:#e4a5aa;background:var(--red-soft)"><div class="section-head"><h3>레이트 체크아웃·청소 출입/PIN 충돌</h3>${statusBadge('즉시 조치','red','alert')}</div><p class="audit-note" style="color:#7d2d34">${record.autoCheckoutAt} 자동 체크아웃 뒤 예약 체크아웃이 ${record.afterCheckout}으로 바뀌었습니다. 자동 체크아웃 기록은 삭제하지 않고 <strong>점유 재개 보정 이벤트</strong>를 추가했습니다.</p><div class="info-grid"><div class="info-item"><span>변경 전 → 후</span><strong>${record.beforeCheckout} → ${record.afterCheckout}</strong></div><div class="info-item"><span>점유 보정</span><strong>체크아웃 완료 → 투숙 중 재개</strong></div><div class="info-item"><span>청소 담당</span><strong>${record.assignee}</strong></div><div class="info-item"><span>수행 단계</span><strong>${record.stage} · 일시 정지 필요</strong></div><div class="info-item"><span>PIN 조회</span><strong>${record.pinViewedAt} · ${record.assignee}</strong></div><div class="info-item"><span>PIN lease 영향</span><strong>${record.leaseId} · 종료/교체 판단</strong></div></div><div class="notice notice-danger" style="margin:12px 0 0"><div><strong>종결 전 객실·작업 상태 고정</strong><br>현장 조율, 작업 재계획, 필요 시 PIN 교체를 모두 확인하기 전에는 충돌을 닫을 수 없습니다.</div></div><div style="margin-top:12px">${button('영향 확인·충돌 해결','resolve-conflict-v2','danger',isLocked()?'disabled':'')}</div></section>`:`<section class="card card-pad"><div class="section-head"><h3>출입 충돌 종결</h3>${statusBadge('재계산 완료','green')}</div><div class="notice notice-success" style="margin:0 0 12px"><div><strong>점유 재개·작업 재계획 완료</strong><br>${record.beforeCheckout} 자동 체크아웃은 감사 이력에 남기고 ${record.afterCheckout} 체크아웃까지 투숙 중으로 보정했습니다.</div></div><div class="info-grid"><div class="info-item"><span>새 청소 계획</span><strong>${record.afterCheckout} · ${record.assignee}</strong></div><div class="info-item"><span>이전 수행 회차</span><strong>중단 이력 보존</strong></div><div class="info-item"><span>이전 PIN lease</span><strong>${record.leaseId} · 종료됨</strong></div><div class="info-item"><span>종결 시각</span><strong>${record.resolvedAt||state.time}</strong></div></div></section>`;
  6197 |         return renderCoach()+renderNetworkNotice()+detailHeader('332호',`${type.name} · 레이트 체크아웃 예외`)+`<div class="detail-grid"><div class="detail-stack">${statePanel}<section class="card card-pad"><div class="room-card-head"><div><h3>332호 현재 상태</h3><p>자동 체크아웃 삭제 없이 점유 재개 보정을 반영합니다.</p></div><div class="badge-row">${statusBadge(active?'출입 충돌':'점유 재개·재계획 완료',active?'red':'green')}${statusBadge('투숙 중','neutral')}</div></div><div class="time-band" aria-label="한 고객 예약의 체크인부터 체크아웃까지"><span>체크인 <strong>${esc(room.checkin)}</strong></span><span>→</span><span>체크아웃 <strong>${record.afterCheckout}</strong></span><span class="special">${esc(reservationStatusText(special,'checkout'))}</span></div><div class="status-band ${active?'red':'green'}"><div><strong>${active?'현재 입실·청소 출입 차단':'13:00까지 점유 유지'}</strong><span>${active?'충돌 종결 전 일정·lease 재검증 필요':'청소는 13:00으로 재계획됨'}</span></div>${statusBadge('현재 입실 불가','neutral')}</div>${renderPinRow('332')}</section><section class="card card-pad"><div class="section-head"><h3>예약·청소 영향</h3>${statusBadge(active?'보정 대기':'보정 완료',active?'red':'green')}</div><div class="info-grid"><div class="info-item"><span>예약 체크아웃</span><strong>${record.afterCheckout}</strong></div><div class="info-item"><span>자동 상태 · 11:00 기준</span><strong>${esc(reservationStatusText(special,'checkout'))}</strong></div><div class="info-item"><span>현재 점유</span><strong>투숙 중</strong></div><div class="info-item"><span>청소 담당</span><strong>${record.assignee}</strong></div><div class="info-item"><span>청소 단계</span><strong>${active?'기존 회차 일시 정지':'13:00 새 회차 예정'}</strong></div></div></section></div><aside class="detail-stack"><section class="card card-pad"><div class="section-head"><h3>운영 상태</h3>${statusBadge(active?'충돌 잠금':'정상 보정','green')}</div><p class="audit-note">예약·작업·PIN lease 이벤트를 삭제하지 않고 순서대로 보존합니다.</p></section><section class="card card-pad"><h3>객실 사건 타임라인</h3>${renderTimeline('332')}</section></aside></div><div class="sticky-command"><button class="btn btn-${active?'danger':'primary'}" type="button" data-action="${active?'resolve-conflict-v2':'cleaning-detail'}" data-id="332" ${active&&isLocked()?'disabled':''}>${active?'영향 확인·충돌 해결':'재계획된 청소 보기'}</button></div>`;
  6198 |       }
  6199 | 
  6200 |       function renderRoomOperationDetailPanel(no) {
  6201 |         const room=ROOMS.find(item=>item.no===no);
  6202 |         if(state.roomStopped[no]){
  6203 |           const move=state.roomMoves[no]||{}, reason=state.roomStopReasons[no]||move.reason||'사유 확인 필요';
  6204 |           return `<section class="card card-pad" style="border-color:#e4a5aa;background:var(--red-soft)"><div class="section-head"><h3>운영 상태</h3>${statusBadge('운영 중지','red')}</div><div class="info-grid"><div class="info-item"><span>중지 사유</span><strong>${esc(reason)}</strong></div><div class="info-item"><span>대체 객실</span><strong>${move.to?`${esc(move.to)}호`:'배정 없음'}</strong></div></div><p class="audit-note" style="margin:10px 0">예약·청소·충돌 이력은 삭제하지 않고 운영 재개 뒤에도 감사 이력에 보존됩니다.</p>${button('운영 재개','resume-operation','success',`data-id="${no}"`)}</section>`;
  6205 |         }
  6206 |         const conflictLocked=no==='332'&&state.conflict==='active';
  6207 |         return `<section class="card card-pad"><div class="section-head"><h3>운영 상태</h3>${statusBadge(conflictLocked?'충돌 잠금':'정상',conflictLocked?'amber':'green')}</div><p class="audit-note">${conflictLocked?'출입 충돌 해결 전에도 별도 운영 중지는 가능하며 예약·작업 이력은 삭제하지 않습니다.':'모든 객실 상태에서 운영 중지할 수 있으며, 다른 객실 배정은 이 흐름 안에서만 진행합니다.'}</p>${button('운영 중지·대체 객실','operation-status','danger',`data-id="${no}"`)}</section>`;
```

### occurrence 6 · line 6750

```html
  6734 |         showModal({title:'332호 영향 확인·충돌 해결',subtitle:'변경된 체크아웃과 현재 청소·PIN 조회 영향을 확인하세요.',large:true,trigger,body:`<div class="notice notice-danger"><div><strong>현재 상태 확인</strong><br>${record.autoCheckoutAt} 자동 체크아웃 기록은 남기고 ${record.afterCheckout}까지 투숙 중으로 표시합니다.</div></div><div class="info-grid"><div class="info-item"><span>체크아웃 전 → 후</span><strong>${record.beforeCheckout} → ${record.afterCheckout}</strong></div><div class="info-item"><span>청소 담당·단계</span><strong>${record.assignee} · ${record.stage}</strong></div><div class="info-item"><span>PIN 조회</span><strong>${record.pinViewedAt}</strong></div><div class="info-item"><span>PIN 조회 처리</span><strong>기존 조회 종료 후 다시 확인</strong></div></div><div class="choice-list" style="margin-top:14px"><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="coordinate" ${state.conflictSteps.coordinate?'checked':''} ${isLocked()?'disabled':''}><span><strong>현장 조율 완료</strong><span>투숙객·${record.assignee}에게 변경된 체크아웃과 출입 중단을 확인</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="replan" ${state.conflictSteps.replan?'checked':''} ${isLocked()?'disabled':''}><span><strong>청소 일정 변경 완료</strong><span>진행 중 청소를 중단 처리하고 ${record.afterCheckout} 새 청소 생성</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="pin" ${state.conflictSteps.pin?'checked':''} ${isLocked()?'disabled':''}><span><strong>도어락 PIN 확인 완료</strong><span>기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.</span></span></label></div>`,confirmLabel:'조치 완료',confirmAction:'confirm-conflict-v2',confirmVariant:'danger'});
  6735 |         const confirm=document.querySelector('[data-action="confirm-conflict-v2"]');
  6736 |         if(confirm)confirm.disabled=isLocked()||!Object.values(state.conflictSteps).every(Boolean);
  6737 |       }
  6738 | 
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
```

### occurrence 7 · line 6879

```html
  6863 |           render();focusAfterRender(`[data-maid-account-management="${maidId}"]`);toast(`${maid.name} 계정을 비활성으로 전환하고 과거 이력·검수·수익을 보존했습니다.`);return;
  6864 |         }
  6865 |         if(a==='complaint-detail'){const item=id?complaintForExactAction(id):complaintForAction();maskPin();openDetail('complaint',item?.id||'none',el);return;}
  6866 |         if(a==='admin-pay-detail'){
  6867 |           const parsed=parseAdminPayDetailId(id),cfg=parsed?adminPayWeeks().find(week=>week.start===parsed.weekStart):null;
  6868 |           if(!state.loggedIn||state.role!=='admin'||state.adminView!=='maids'||state.adminMaidTab!=='pay'||!cfg||!cfg.tasksByMaid?.[parsed.maidId]){toast('관리자 주급 정산의 저장된 청소 원장에서만 상세를 열 수 있습니다.','error');return;}
  6869 |           state.adminPayWeek=parsed.weekStart;maskPin();openDetail('pay',adminPayDetailId(parsed.weekStart,parsed.maidId),el);return;
  6870 |         }
  6871 |         if(a==='pay-detail'){
  6872 |           if(!state.loggedIn||state.role!=='admin'){toast('관리자만 주급 산출 상세를 볼 수 있습니다.','error');return;}
  6873 |           const maidId=state.detail?.type==='maid'&&MAIDS.some(maid=>maid.id===state.detail.id)?state.detail.id:'m1',week=adminPayWeeks().some(item=>item.start===state.adminPayWeek)?state.adminPayWeek:'2026-08-03';
  6874 |           state.adminView='maids';state.adminMaidTab='pay';state.adminPayWeek=week;maskPin();openDetail('pay',adminPayDetailId(week,maidId),el);return;
  6875 |         }
  6876 |         if(a==='alerts'){openActionAlerts(el);return;}
  6877 |         if(a==='audit-log'){openActionAuditLog(el);return;}
  6878 |         if(a==='rates'){openActionRates(el);return;}
  6879 |         if(a==='logout'){openAccountStatus(el);return;}
  6880 |         if(a==='demo-info'){openDemoInformation(el);return;}
  6881 |         if(a==='notification-permission'){
  6882 |           if(!state.notificationsEnabled&&isLocked()){toast('최신 상태를 확인하기 전에는 알림 허용 상태를 바꿀 수 없습니다.','error');return;}
  6883 |           openNotificationStatus(el);return;
  6884 |         }
  6885 |         if(a==='confirm-notification-permission'){
  6886 |           if(isLocked()){closeModal();render();toast('동기화 상태가 바뀌어 알림 허용 상태를 저장하지 않았습니다.','error');return;}
  6887 |           setNotificationPushEnabled(true);appendEvent('기기 알림 허용 상태 변경','정적 데모 · 앱 내부 알림은 항상 유지',{notification:false});closeModal();render();toast('알림 허용 상태로 표시했습니다.');return;
  6888 |         }
  6889 |         if(a==='retry-network'){
  6890 |           const retryState=state;
  6891 |           if(state.network==='online'&&state.listMode!=='stale'){toast('이미 최신 상태입니다.');return;}
  6892 |           state.listMode='loading';render();focusAfterRender();
  6893 |           setTimeout(()=>{if(state!==retryState)return;state.network='online';state.listMode='data';appendEvent('최신 상태 다시 확인','권한·목록 버전 재검증 완료');render();focusAfterRender();toast('최신 상태와 권한을 다시 검증했습니다.');},500);
  6894 |           return;
  6895 |         }
  6896 |         if(a==='template'){if(state.role!=='admin')return;maskPin();openDetail('templates','all',el);return;}
  6897 |         if(a==='template-detail'){if(state.role!=='admin')return;state.returnContext={view:currentView(),scrollY:window.scrollY,focusId:id,focusAction:'template-detail'};pushPageTransition(()=>{state.detail={type:'template',id,mode:'view'};});return;}
  6898 |         if(a==='template-back-list'){if(state.role!=='admin')return;backPageTransition(()=>{state.detail={type:'templates',id:'all'};},{action:'template-detail',id});return;}
  6899 |         if(a==='template-edit'){if(!adminCanMutate())return;pushPageTransition(()=>{pendingTemplateChange=null;state.detail={type:'template',id,mode:'edit'};},'#template-minutes');return;}
  6900 |         if(a==='template-cancel-edit'){if(state.role!=='admin')return;pendingTemplateChange=null;backPageTransition(()=>{state.detail={type:'template',id,mode:'view'};},{action:'template-edit',id});return;}
  6901 |         if(a==='template-review'){if(!adminCanMutate())return;openTemplateReview(id);return;}
  6902 |         if(a==='template-save'){
  6903 |           if(!adminCanMutate()){closeModal();render();toast('관리자 권한 또는 최신 상태가 바뀌어 템플릿을 저장하지 않았습니다.','error');return;}
  6904 |           const change=pendingTemplateChange,template=change&&templateById(change.id);if(!template||change.id!==id)return;
  6905 |           const previous={version:template.version,savedAt:template.lastSaved,minutes:template.minutes};
  6906 |           template.history.unshift(previous);template.version=`v${Number(template.version.replace(/\D/g,''))+1}`;template.minutes=change.minutes;template.lastSaved=`2026.08.18 ${state.time}`;state.template=`published ${template.version}`;
  6907 |           appendEvent(`${ROOM_TYPES[template.typeId].name} · ${template.name} ${template.version} 저장`,'기존 작업 스냅샷 유지 · 새 작업부터 적용 · 데모');pendingTemplateChange=null;closeModal();state.detail={type:'template',id:template.id,mode:'view'};render();toast(`${template.version}을 활성화했습니다. 기존 작업은 변경되지 않습니다.`);return;
  6908 |         }
  6909 |         if(a==='inspection-photo'){openInspectionPhoto(el.dataset.room,el.dataset.submission,el.dataset.photo,el);return;}
  6910 |         if(a==='bomb-room-photo'){openBombRoomPhoto(el.dataset.room,el.dataset.report,el.dataset.photo,el);return;}
  6911 |         if(a==='choose-bomb-room-files'){
  6912 |           const no=el.dataset.room;
  6913 |           if(!maidCanCreateBombRoomReport(no)){toast('본인 담당 객실의 전체 제출 전 단계에서만 폭탄방 증빙을 선택할 수 있습니다.','error');return;}
```

### occurrence 8 · line 7725

```html
  7709 |         else if(a==='rule-complaint')showModal({title:'컴플레인 관리자 판정',subtitle:'반려와 별개인 평가 참고 기록이며 주급을 자동 차감하지 않습니다.',body:`<div class="choice-list"><label class="choice"><input type="radio" name="ruling" checked><span><strong>확인됨</strong><span>선택 벌점 1점 · 평가 참고</span></span></label><label class="choice"><input type="radio" name="ruling"><span><strong>확인 불가</strong><span>근거 부족 기록</span></span></label><label class="choice"><input type="radio" name="ruling"><span><strong>사실 아님</strong><span>판정 근거 기록</span></span></label></div>`,confirmLabel:'판정 알림',confirmAction:'confirm-ruling'});
  7710 |         else if(a==='confirm-ruling'){state.complaint='ruled';appendEvent('컴플레인 판정','확인됨 · 메이드 응답 대기');closeModal();render();toast('메이드 판정 확인 대기로 전환했습니다.');}
  7711 |         else if(a==='ack-complaint'){state.complaint='acknowledged';appendEvent('메이드 내용 확인','판정 변경 없음');render();toast('내용 확인을 기록했습니다.');}
  7712 |         else if(a==='object-complaint')showModal({title:'판정 이의 메모',subtitle:'메이드는 판정·벌점·재청소를 직접 바꿀 수 없습니다.',body:`<div class="field"><label for="objection">이의 메모 · 데모</label><textarea id="objection" class="input-control" rows="4">작업 종료 당시 사진을 다시 확인해 주세요.</textarea></div>`,confirmLabel:'이의 제출',confirmAction:'confirm-objection'});
  7713 |         else if(a==='confirm-objection'){state.complaint='objected';appendEvent('메이드 이의 제출','관리자 재검토 필요');closeModal();render();toast('관리자 재검토 상태로 전환했습니다.');}
  7714 |         else if(a==='close-complaint'||a==='correct-complaint'){state.complaint='closed';appendEvent('컴플레인 종결',a==='correct-complaint'?'판정 정정 이벤트 추가':'판정 유지');render();toast('원본을 보존한 채 종결했습니다.');}
  7715 |         else if(a==='notification-filter'){const filter=el.dataset.filter;if(!['all','unread','action'].includes(filter))return;state.notificationFilter=filter;openNotificationCenter(el);return;}
  7716 |         else if(a==='notification-mark-all-read'){markAllNotificationsRead();render();openNotificationCenter(el);toast('현재 계정의 알림을 모두 읽음 처리했습니다.');return;}
  7717 |         else if(a==='notification-toggle-push'){const enabled=!notificationPushEnabled();setNotificationPushEnabled(enabled);appendEvent('기기 푸시 설정 변경',enabled?'현재 계정 푸시 켜짐 · 앱 내 알림은 항상 유지':'현재 계정 푸시 꺼짐 · 앱 내 알림은 항상 유지',{notification:false});render();openNotificationCenter(el);toast(enabled?'행동이 필요한 업데이트의 푸시를 켰습니다.':'푸시를 껐습니다. 앱 내 알림은 계속 남습니다.');return;}
  7718 |         else if(a==='notification-open'){const ids=String(el.dataset.eventIds||el.dataset.eventId||'').split(',').filter(Boolean),eventId=el.dataset.eventId||ids[0],event=(state.events||[]).find(item=>item.id===eventId);markNotificationRead(ids);closeModal();render();if(event)requestAnimationFrame(()=>dispatchNotificationTarget(event));return;}
  7719 |         else if(a==='alert-link'){closeModal();openDetail(el.dataset.type,el.dataset.id,el);}
  7720 |         else if(a==='date-prev'||a==='date-next'){state.selectedDate=a==='date-prev'?'2026-08-13':'2026-08-15';render();toast(`${state.selectedDate} 객실판을 표시합니다.`);}
  7721 |         else if(a==='date-today'){state.selectedDate='2026-08-14';render();}
  7722 |         else if(a==='clear-filter'){state.roomFilter='all';state.listMode='data';render();focusAfterRender('[data-control="list-mode"]');}
  7723 |         else if(a==='retry-network'){state.network='online';state.listMode='loading';render();focusAfterRender();setTimeout(()=>{state.listMode='data';render();focusAfterRender();toast('최신 상태와 권한을 다시 검증했습니다.');},500);}
  7724 |         else if(a==='view-open-jobs'){state.role='maid';state.maidView='open';render();focusAfterRender();}
  7725 |         else if(a==='logout'){state.loggedIn=false;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('#login-id')?.focus());}
  7726 |         else if(a==='login-mode'){const mode=el.dataset.mode;state.loginMode=mode;render();requestAnimationFrame(()=>document.querySelector(`[data-action="login-mode"][data-mode="${mode}"]`)?.focus());}
  7727 |         else if(a==='notification-permission'){state.notificationsEnabled=true;render();toast('알림 권한 허용 상태를 데모로 전환했습니다.');}
  7728 |         else if(a==='rates')showModal({title:'객실 타입 청소요금·예상시간',subtitle:'청소요금은 객실현황(26.08) 8월 시트 정본이며 예상시간만 데모입니다.',large:true,body:`<div class="rail-list">${Object.values(ROOM_TYPES).map(t=>`<div class="rail-row"><strong>${t.name}</strong><span>${money(t.rate)} · 8월 시트 · 예상 ${t.minutes}분(데모)</span></div>`).join('')}</div>`});
  7729 |         else if(a==='template')showModal({title:'청소 템플릿 · 데모',subtitle:'객실 타입 × 퇴실·연박·재청소 조합',body:`<div class="notice notice-info">현재 초안 v4 · 미리보기와 인증 항목 검증 전에는 신규 작업에 사용되지 않습니다.</div><div class="check-list"><div class="check-row">${icon('check')}<span><strong>침대·욕실·바닥·문 잠금</strong><span>체크 4개 · 인증 사진 3개 · 기타 사진 1개</span></span></div></div>`,confirmLabel:state.template==='draft'?'미리보기·게시':'확인',confirmAction:'publish-template'});
  7730 |         else if(a==='publish-template'){state.template='published v4';appendEvent('청소 템플릿 v4 게시','새 작업부터 적용 · 기존 작업 불변');closeModal();render();toast('새 버전을 게시했습니다.');}
  7731 |         else if(a==='audit-log')showModal({title:'최근 변경 이력',subtitle:'PIN 원문·로그인 비밀번호·휴대폰 원문은 기록하지 않습니다.',large:true,body:`<ol class="timeline">${state.events.map(e=>`<li><strong>${esc(adminAuditTitle(e.title))}</strong><span>${esc(e.time)} · ${esc(adminAuditSummary(e.detail))}</span></li>`).join('')}</ol>`});
  7732 |         else if(a==='demo-info')toast('객실번호·타입·엘리베이터·청소요금은 8월 시트 정본이며, 인명·예약·상태·예상시간은 화면 구조 데모입니다.');
  7733 |         else if(a==='request-cancel')toast('담당 취소 요청을 모든 관리자 오늘 큐에 등록했습니다.');
  7734 |       });
  7735 | 
  7736 |       document.addEventListener('change', e => {
  7737 |         const c=e.target.dataset.control; if(!c) return;
  7738 |         if(c==='role'){state.role=e.target.value;state.detail=null;render();requestAnimationFrame(()=>document.querySelector('[data-control="role"]')?.focus());}
  7739 |         else if(c==='time'){state.time=e.target.value;render();requestAnimationFrame(()=>document.querySelector('[data-control="time"]')?.focus());toast(`${state.time} 한국시간으로 시뮬레이션합니다.`);}
  7740 |         else if(c==='network'){state.network=e.target.value;if(state.network!=='online')state.listMode='stale';else if(state.listMode==='stale')state.listMode='data';render();requestAnimationFrame(()=>document.querySelector('[data-control="network"]')?.focus());}
  7741 |         else if(c==='scenario'){state=makeScenario(Number(e.target.value));hydrateTemplateSnapshotsForState();render();requestAnimationFrame(()=>document.querySelector('[data-control="scenario"]')?.focus());toast(`${state.scenario}번 시나리오를 불러왔습니다.`);}
  7742 |         else if(c==='room-filter'){state.roomFilter=e.target.value;render();requestAnimationFrame(()=>document.querySelector('[data-control="room-filter"]')?.focus());}
  7743 |         else if(c==='draft'){const value=e.target.value;state.selectedDrafts=e.target.checked?[...state.selectedDrafts,value]:state.selectedDrafts.filter(v=>v!==value);render();requestAnimationFrame(()=>document.querySelector(`[data-control="draft"][value="${value}"]`)?.focus());}
  7744 |         else if(c==='conflict-step'){state.conflictSteps[e.target.value]=e.target.checked;}
  7745 |         else if(c==='list-mode'){state.listMode=e.target.value;if(state.listMode==='stale')state.network='stale';else if(state.network==='stale')state.network='online';render();requestAnimationFrame(()=>document.querySelector('[data-control="list-mode"]')?.focus());}
  7746 |       });
  7747 | 
  7748 |       document.addEventListener('submit', e => {
  7749 |         if(e.target.id==='login-form'){e.preventDefault();state.loggedIn=true;state.loginMode='normal';render();toast('데모 역할 화면으로 로그인했습니다.');}
  7750 |       });
  7751 | 
  7752 |       document.addEventListener('keydown', e => {
  7753 |         const modal=document.querySelector('.modal');
  7754 |         if(!modal) return;
  7755 |         if(e.key==='Escape'){e.preventDefault();dismissModal();return;}
  7756 |         if(e.key==='Tab'){
  7757 |           const focusable=[...modal.querySelectorAll('button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),a[href]')];
  7758 |           if(!focusable.length)return;
  7759 |           const first=focusable[0],last=focusable[focusable.length-1];
```

## room presentation: `function roomPresentation`

matches: 1

### occurrence 1 · line 4284

```html
  4268 | 
  4269 |       function roomCleaningStageLabel(job) {
  4270 |         return ({public:'청소 미배정',unassigned:'청소 미배정',claimed:'담당 확정',scheduled:'시작 예정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',reclean:'재청소',hold:'관리자 조치',draft:'배정 준비',future:'예정','stayover-requested':'연박 청소 요청','extra-requested':'추가 청소 요청'})[job]||'';
  4271 |       }
  4272 |       function roomNeedsCleaningNow(no) {
  4273 |         const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no];if(!room)return false;
  4274 |         if(activeManualCleaningRequest(no))return true;
  4275 |         if(room.occupancy!=='occupied'&&roomCheckoutCleaningDue(no))return true;
  4276 |         const attempt=activeUnfinishedAttempt(no),workDate=attempt?attemptWorkDate(attempt,state.selectedDate):room.actualCheckoutAt?.slice(0,10)||null,currentOrPast=!workDate||workDate<=state.selectedDate;
  4277 |         if(room.occupancy==='occupied'){const due=!room.stayoverRequest?.date||room.stayoverRequest.date<=state.selectedDate,stayoverStage=job==='stayover-requested'||(!!room.stayoverRequest&&['public','unassigned','claimed','scheduled','cleaning','upload','inspection','reclean','hold','draft'].includes(job));return due&&stayoverStage&&job!=='approved';}
  4278 |         if(['cleaning','upload','inspection','reclean','hold'].includes(job))return true;
  4279 |         if(['public','unassigned','claimed','scheduled'].includes(job))return currentOrPast;
  4280 |         if(job==='draft')return !!room.actualCheckoutAt&&room.actualCheckoutAt.slice(0,10)<=state.selectedDate;
  4281 |         if(job==='stayover-requested')return !room.stayoverRequest?.date||room.stayoverRequest.date<=state.selectedDate;
  4282 |         return false;
  4283 |       }
  4284 |       function roomPresentation(no) {
  4285 |         const room=ROOMS.find(item=>item.no===String(no)),job=state.jobs[no],manualRequest=activeManualCleaningRequest(no),special=cardReservationStatus(no),blockers=roomBlockingReasons(no),cleaning=roomNeedsCleaningNow(no),cleaningStage=roomCleaningStageLabel(job),cleaningKind=manualRequest?.kind||(job==='extra-requested'?'추가 청소':room?.occupancy==='occupied'?'연박 청소':job==='reclean'?'재청소':'퇴실 청소');
  4286 |         if(!room)return {key:'blocked',tone:'red',status:'배정 불가',reason:'객실 정보 확인 필요',available:false,cleaning:false,cleaningKind:'',blockers:['객실 정보 확인 필요']};
  4287 |         if(blockers.length)return {key:'blocked',tone:'red',status:'배정 불가',reason:blockers.join(' · '),available:false,cleaning,cleaningKind:cleaning?cleaningKind:'',cleaningStage:cleaning?cleaningStage:'',blockers,early:special.early,late:special.late};
  4288 |         if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false,cleaning,cleaningKind:cleaning?cleaningKind:'',cleaningStage:cleaning?cleaningStage:'',blockers:[],early:special.early,late:special.late};
  4289 |         if(cleaning)return {key:'cleaning',tone:'amber',status:'청소 필요',reason:`${cleaningKind} 필요`,available:false,cleaning:true,cleaningKind,cleaningStage,blockers:[],early:special.early,late:special.late};
  4290 |         return {key:'available',tone:'green',status:'배정 가능',reason:'공실 · 청소·운영·안전 조건 완료',available:true,cleaning:false,cleaningKind:'',cleaningStage:'',blockers:[],early:special.early,late:special.late};
  4291 |       }
  4292 | 
  4293 |       function renderPinRow(no,{editable=true,maid=false}={}) {
  4294 |         const allowed=!isLocked()&&(!maid||maidPinAllowed(no));
  4295 |         const visible=allowed&&state.pinVisibleRoom===no&&state.pinVisibleUntil>Date.now()&&activePinRevealSecret?.room===no&&activePinRevealSecret.expiresAt>Date.now();
  4296 |         return `<div class="pin-row concept-pin" data-pin-room="${no}"><div class="pin-copy"><span>객실 PIN</span><strong>${visible?esc(activePinRevealSecret.value):'••••'}</strong>${visible?`<span>30초 후 자동 숨김</span>`:''}</div>${visible?button('숨기기','pin-hide','outline',`data-id="${no}"`):button('보기','pin-show','outline',`data-id="${no}" ${allowed?'':'disabled'}`)}${editable&&!maid?button('수정','pin-edit','primary',`data-id="${no}" ${isLocked()?'disabled':''}`):''}</div>`;
  4297 |       }
  4298 |       function maidPinAllowed(no) {
  4299 |         const job=state.jobs[no],start=startTimeFor(no),room=ROOMS.find(item=>item.no===no),task=state.taskInputs?.[no],attemptId=state.currentAttemptByRoom?.[no],attempt=attemptId?state.cleaningAttempts?.[attemptId]:null;
  4300 |         return state.role==='maid'&&(signedInMaidIsActive()||maidCanContinueDeactivation(no)||maidCanCompleteRequiredReclean(no))&&room?.assignee===signedInMaidName()&&task?.attemptId===attemptId&&attempt?.performerId===signedInMaidId()&&['claimed','scheduled','reclean','cleaning'].includes(job)&&attemptAccessStatus(no,attempt).allowed;
  4301 |       }
  4302 | 
  4303 |       function roomCard(no) {
  4304 |         const room=ROOMS.find(item=>item.no===no),type=ROOM_TYPES[room.type],p=roomPresentation(no),job=state.jobs[no],candle=room.occupancy==='occupied'?0:state.candles[no]||0,special=cardReservationStatus(no),issueCount=unresolvedRoomIssueRecords(no).length,reservations=activeReservationsFor(state,no),upcomingReservations=reservations.filter(item=>!reservationRecordIsPast(item)),closestReservation=upcomingReservations[0]||null;
  4305 |         const cardWeekAnchor=closestReservation&&closestReservation.checkInAt.slice(0,10)>state.selectedDate?closestReservation.checkInAt.slice(0,10):state.selectedDate,reservationBuckets=reservationBucketsForRoom(state,no,cardWeekAnchor),weekReservations=reservationBuckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),pastReservationCount=reservationBuckets.records.filter(reservationRecordIsPast).length;
  4306 |         const stayProgress=roomStayProgress(room,reservations),earlyTime=special.checkin||DEFAULT_CHECKIN_TIME,lateTime=special.checkout||DEFAULT_CHECKOUT_TIME,checkinDisplay=closestReservation?reservationMomentLabel(closestReservation.checkInAt):'일정 없음',checkoutDisplay=closestReservation?reservationMomentLabel(closestReservation.checkOutAt):'일정 없음';
  4307 |         const cardGuestCount=closestReservation&&reservationHasExtraGuests(closestReservation)?reservationGuestCount(closestReservation):null;
  4308 |         const scheduleBadges=[cardGuestCount?`<span class="schedule-priority-badge guests" aria-label="숙박 인원 ${cardGuestCount}명">${icon('user','icon-sm')}${cardGuestCount}명</span>`:'',stayProgress?`<span class="schedule-priority-badge stayover">${icon('calendar','icon-sm')}${esc(stayProgress.label)}</span>`:'',special.early?`<span class="schedule-priority-badge">${icon('clock','icon-sm')}얼리 체크인 ${esc(earlyTime)} · ${esc(special.earlyOffset)} 빠름</span>`:'',special.late?`<span class="schedule-priority-badge late">${icon('clock','icon-sm')}레이트 체크아웃 ${esc(lateTime)} · ${esc(special.lateOffset)} 늦음</span>`:''].filter(Boolean).join('');
  4309 |         const detailBadges=[checkoutInspectionPending(no)?'<span class="room-detail-badge">퇴실점검 대상</span>':'',roomIsOnHold(no)?'<span class="room-detail-badge">정보 확인 필요</span>':'',state.roomStopped[no]?'<span class="room-detail-badge">운영 중지</span>':'',no==='332'&&state.conflict==='active'?'<span class="room-detail-badge">출입·PIN 충돌</span>':'',candle?`<span class="room-detail-badge">${icon('candle','icon-sm')}촛불 ${candle}개</span>`:'',issueCount?`<span class="room-detail-badge">특이사항 ${issueCount}건</span>`:''].filter(Boolean).join('');
  4310 |         const statusIcon=p.key==='occupied'?'user':p.key==='cleaning'?'briefcase':p.key==='available'?'check':'alert';
  4311 |         const cleaningControl=roomCleaningControl(no),operationAction=roomIsOnHold(no)?'room-detail':'operation-status',operationLabel=roomIsOnHold(no)?'정보 입력':'운영 상태',reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`:pastReservationCount?`예약 기록 ${pastReservationCount}건`:room.occupancy==='occupied'&&!occupiedReservationEnd(room)?'투숙 정보 입력':'예약 등록';
  4312 |         return `<article class="card room-card-v2 tone-${p.tone}" data-room="${no}"><div class="room-card-main"><div class="room-card-head"><div><h3>${no}호</h3><p>${esc(type.name)}</p><span class="room-location-line">${icon('mapPin','icon-sm')}${esc(elevatorLabel(room))}</span></div><div class="badge-row room-schedule-badges">${scheduleBadges}${detailBadges}</div></div>
  4313 |           <div class="time-band" aria-label="한 고객 예약의 체크인부터 체크아웃까지">${icon('clock','icon-sm')}<span>체크인 <strong>${esc(checkinDisplay)}</strong></span><span aria-hidden="true">→</span><span>체크아웃 <strong>${esc(checkoutDisplay)}</strong></span></div>
  4314 |           <div class="concept-status-panel ${p.tone}"><span class="status-symbol">${icon(statusIcon)}</span><div class="concept-status-copy"><strong>${esc(p.status)}</strong></div></div>
  4315 |           ${roomIsOnHold(no)?'':renderPinRow(no)}</div>
  4316 |           <div class="room-quick-actions"><button class="btn btn-ghost" type="button" data-action="${closestReservation?'quick-reservation-edit':'reservation-edit'}" data-id="${closestReservation?esc(closestReservation.id):no}" ${closestReservation?`data-room="${no}"`:''}>${icon('calendar')}${esc(reservationActionLabel)}</button><button class="btn btn-ghost" type="button" data-action="${operationAction}" data-id="${no}">${icon('shield')}${operationLabel}</button><button class="btn btn-ghost" type="button" data-action="${cleaningControl.action}" data-id="${no}" data-room-cleaning-control="${no}" title="${esc(cleaningControl.reason)}" aria-label="${no}호 ${esc(cleaningControl.label)}" ${cleaningControl.disabled?'disabled':''}>${icon('briefcase')}${esc(cleaningControl.label)}</button><button class="btn btn-ghost" type="button" data-action="room-detail" data-id="${no}">${icon('list')}전체 상세</button></div></article>`;
  4317 |       }
  4318 |       function cleaningLabel(job) { return ({scheduled:'퇴실 청소 · 시작 예정',inspection:'퇴실 청소 · 검수 대기',cleaning:'퇴실 청소 · 청소 중',upload:'퇴실 청소 · 업로드 대기',approved:'현재 청소 작업 없음',reclean:'재청소 · 시작 예정',public:'청소 · 관리자 배정 대기',unassigned:'청소 · 관리자 배정 대기',claimed:'퇴실 청소 · 관리자 배정 확정',hold:'관리자 조치 대기',draft:'배정 준비 청소 작업',future:'미래 퇴실 청소 예정','stayover-requested':'연박 청소 요청','extra-requested':'추가 청소 요청'})[job]||'현재 청소 작업 없음'; }
```

## room card: `function roomCard`

matches: 1

### occurrence 1 · line 4303

```html
  4287 |         if(blockers.length)return {key:'blocked',tone:'red',status:'배정 불가',reason:blockers.join(' · '),available:false,cleaning,cleaningKind:cleaning?cleaningKind:'',cleaningStage:cleaning?cleaningStage:'',blockers,early:special.early,late:special.late};
  4288 |         if(room.occupancy==='occupied')return {key:'occupied',tone:'neutral',status:'투숙 중',reason:`현재 투숙 중 · 체크아웃 ${special.checkout||'일정 미입력'}`,available:false,cleaning,cleaningKind:cleaning?cleaningKind:'',cleaningStage:cleaning?cleaningStage:'',blockers:[],early:special.early,late:special.late};
  4289 |         if(cleaning)return {key:'cleaning',tone:'amber',status:'청소 필요',reason:`${cleaningKind} 필요`,available:false,cleaning:true,cleaningKind,cleaningStage,blockers:[],early:special.early,late:special.late};
  4290 |         return {key:'available',tone:'green',status:'배정 가능',reason:'공실 · 청소·운영·안전 조건 완료',available:true,cleaning:false,cleaningKind:'',cleaningStage:'',blockers:[],early:special.early,late:special.late};
  4291 |       }
  4292 | 
  4293 |       function renderPinRow(no,{editable=true,maid=false}={}) {
  4294 |         const allowed=!isLocked()&&(!maid||maidPinAllowed(no));
  4295 |         const visible=allowed&&state.pinVisibleRoom===no&&state.pinVisibleUntil>Date.now()&&activePinRevealSecret?.room===no&&activePinRevealSecret.expiresAt>Date.now();
  4296 |         return `<div class="pin-row concept-pin" data-pin-room="${no}"><div class="pin-copy"><span>객실 PIN</span><strong>${visible?esc(activePinRevealSecret.value):'••••'}</strong>${visible?`<span>30초 후 자동 숨김</span>`:''}</div>${visible?button('숨기기','pin-hide','outline',`data-id="${no}"`):button('보기','pin-show','outline',`data-id="${no}" ${allowed?'':'disabled'}`)}${editable&&!maid?button('수정','pin-edit','primary',`data-id="${no}" ${isLocked()?'disabled':''}`):''}</div>`;
  4297 |       }
  4298 |       function maidPinAllowed(no) {
  4299 |         const job=state.jobs[no],start=startTimeFor(no),room=ROOMS.find(item=>item.no===no),task=state.taskInputs?.[no],attemptId=state.currentAttemptByRoom?.[no],attempt=attemptId?state.cleaningAttempts?.[attemptId]:null;
  4300 |         return state.role==='maid'&&(signedInMaidIsActive()||maidCanContinueDeactivation(no)||maidCanCompleteRequiredReclean(no))&&room?.assignee===signedInMaidName()&&task?.attemptId===attemptId&&attempt?.performerId===signedInMaidId()&&['claimed','scheduled','reclean','cleaning'].includes(job)&&attemptAccessStatus(no,attempt).allowed;
  4301 |       }
  4302 | 
  4303 |       function roomCard(no) {
  4304 |         const room=ROOMS.find(item=>item.no===no),type=ROOM_TYPES[room.type],p=roomPresentation(no),job=state.jobs[no],candle=room.occupancy==='occupied'?0:state.candles[no]||0,special=cardReservationStatus(no),issueCount=unresolvedRoomIssueRecords(no).length,reservations=activeReservationsFor(state,no),upcomingReservations=reservations.filter(item=>!reservationRecordIsPast(item)),closestReservation=upcomingReservations[0]||null;
  4305 |         const cardWeekAnchor=closestReservation&&closestReservation.checkInAt.slice(0,10)>state.selectedDate?closestReservation.checkInAt.slice(0,10):state.selectedDate,reservationBuckets=reservationBucketsForRoom(state,no,cardWeekAnchor),weekReservations=reservationBuckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),pastReservationCount=reservationBuckets.records.filter(reservationRecordIsPast).length;
  4306 |         const stayProgress=roomStayProgress(room,reservations),earlyTime=special.checkin||DEFAULT_CHECKIN_TIME,lateTime=special.checkout||DEFAULT_CHECKOUT_TIME,checkinDisplay=closestReservation?reservationMomentLabel(closestReservation.checkInAt):'일정 없음',checkoutDisplay=closestReservation?reservationMomentLabel(closestReservation.checkOutAt):'일정 없음';
  4307 |         const cardGuestCount=closestReservation&&reservationHasExtraGuests(closestReservation)?reservationGuestCount(closestReservation):null;
  4308 |         const scheduleBadges=[cardGuestCount?`<span class="schedule-priority-badge guests" aria-label="숙박 인원 ${cardGuestCount}명">${icon('user','icon-sm')}${cardGuestCount}명</span>`:'',stayProgress?`<span class="schedule-priority-badge stayover">${icon('calendar','icon-sm')}${esc(stayProgress.label)}</span>`:'',special.early?`<span class="schedule-priority-badge">${icon('clock','icon-sm')}얼리 체크인 ${esc(earlyTime)} · ${esc(special.earlyOffset)} 빠름</span>`:'',special.late?`<span class="schedule-priority-badge late">${icon('clock','icon-sm')}레이트 체크아웃 ${esc(lateTime)} · ${esc(special.lateOffset)} 늦음</span>`:''].filter(Boolean).join('');
  4309 |         const detailBadges=[checkoutInspectionPending(no)?'<span class="room-detail-badge">퇴실점검 대상</span>':'',roomIsOnHold(no)?'<span class="room-detail-badge">정보 확인 필요</span>':'',state.roomStopped[no]?'<span class="room-detail-badge">운영 중지</span>':'',no==='332'&&state.conflict==='active'?'<span class="room-detail-badge">출입·PIN 충돌</span>':'',candle?`<span class="room-detail-badge">${icon('candle','icon-sm')}촛불 ${candle}개</span>`:'',issueCount?`<span class="room-detail-badge">특이사항 ${issueCount}건</span>`:''].filter(Boolean).join('');
  4310 |         const statusIcon=p.key==='occupied'?'user':p.key==='cleaning'?'briefcase':p.key==='available'?'check':'alert';
  4311 |         const cleaningControl=roomCleaningControl(no),operationAction=roomIsOnHold(no)?'room-detail':'operation-status',operationLabel=roomIsOnHold(no)?'정보 입력':'운영 상태',reservationActionLabel=weekReservations.length?`${room.occupancy==='occupied'?'예약 관리':'예약 수정'} · ${weekReservations.length}건`:pastReservationCount?`예약 기록 ${pastReservationCount}건`:room.occupancy==='occupied'&&!occupiedReservationEnd(room)?'투숙 정보 입력':'예약 등록';
  4312 |         return `<article class="card room-card-v2 tone-${p.tone}" data-room="${no}"><div class="room-card-main"><div class="room-card-head"><div><h3>${no}호</h3><p>${esc(type.name)}</p><span class="room-location-line">${icon('mapPin','icon-sm')}${esc(elevatorLabel(room))}</span></div><div class="badge-row room-schedule-badges">${scheduleBadges}${detailBadges}</div></div>
  4313 |           <div class="time-band" aria-label="한 고객 예약의 체크인부터 체크아웃까지">${icon('clock','icon-sm')}<span>체크인 <strong>${esc(checkinDisplay)}</strong></span><span aria-hidden="true">→</span><span>체크아웃 <strong>${esc(checkoutDisplay)}</strong></span></div>
  4314 |           <div class="concept-status-panel ${p.tone}"><span class="status-symbol">${icon(statusIcon)}</span><div class="concept-status-copy"><strong>${esc(p.status)}</strong></div></div>
  4315 |           ${roomIsOnHold(no)?'':renderPinRow(no)}</div>
  4316 |           <div class="room-quick-actions"><button class="btn btn-ghost" type="button" data-action="${closestReservation?'quick-reservation-edit':'reservation-edit'}" data-id="${closestReservation?esc(closestReservation.id):no}" ${closestReservation?`data-room="${no}"`:''}>${icon('calendar')}${esc(reservationActionLabel)}</button><button class="btn btn-ghost" type="button" data-action="${operationAction}" data-id="${no}">${icon('shield')}${operationLabel}</button><button class="btn btn-ghost" type="button" data-action="${cleaningControl.action}" data-id="${no}" data-room-cleaning-control="${no}" title="${esc(cleaningControl.reason)}" aria-label="${no}호 ${esc(cleaningControl.label)}" ${cleaningControl.disabled?'disabled':''}>${icon('briefcase')}${esc(cleaningControl.label)}</button><button class="btn btn-ghost" type="button" data-action="room-detail" data-id="${no}">${icon('list')}전체 상세</button></div></article>`;
  4317 |       }
  4318 |       function cleaningLabel(job) { return ({scheduled:'퇴실 청소 · 시작 예정',inspection:'퇴실 청소 · 검수 대기',cleaning:'퇴실 청소 · 청소 중',upload:'퇴실 청소 · 업로드 대기',approved:'현재 청소 작업 없음',reclean:'재청소 · 시작 예정',public:'청소 · 관리자 배정 대기',unassigned:'청소 · 관리자 배정 대기',claimed:'퇴실 청소 · 관리자 배정 확정',hold:'관리자 조치 대기',draft:'배정 준비 청소 작업',future:'미래 퇴실 청소 예정','stayover-requested':'연박 청소 요청','extra-requested':'추가 청소 요청'})[job]||'현재 청소 작업 없음'; }
  4319 |       function filteredRooms() {
  4320 |         const q=state.roomSearch.trim();
  4321 |         return ROOMS.filter(r=>!q||r.no.includes(q)).filter(r=>state.roomTypeFilter==='all'||r.type===state.roomTypeFilter).filter(r=>{const p=roomPresentation(r.no),special=cardReservationStatus(r.no);if(state.roomFilter==='all')return true;if(state.roomFilter==='occupied')return r.occupancy==='occupied';if(state.roomFilter==='cleaning')return roomNeedsCleaningNow(r.no);if(['available','blocked'].includes(state.roomFilter))return p.key===state.roomFilter;if(state.roomFilter==='checkout-inspection')return checkoutInspectionPending(r.no);if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);if(state.roomFilter==='default'||state.roomFilter==='catalog'||state.roomFilter==='vacant')return r.occupancy==='vacant'&&!roomIsOnHold(r.no);if(state.roomFilter==='candle')return r.occupancy!=='occupied'&&(state.candles[r.no]||0)>0;if(state.roomFilter==='early')return special.early;if(state.roomFilter==='late')return special.late;if(state.roomFilter==='issues')return roomIssueRecords(r.no).length>0;return true;});
  4322 |       }
  4323 | 
  4324 |       function renderRooms() {
  4325 |         const rooms=filteredRooms();
  4326 |         const body=rooms.length?`<div class="room-list-v2">${rooms.map(r=>roomCard(r.no)).join('')}</div>`:`<section class="inline-empty"><h3>검색·필터 결과가 없습니다</h3><p>전체 객실은 있지만 선택한 조건과 일치하지 않습니다.</p>${button('검색·필터 초기화','clear-room-filters','outline')}</section>`;
  4327 |         const primaryCounts=ROOMS.reduce((counts,room)=>{const p=roomPresentation(room.no);if(room.occupancy==='occupied')counts.occupied++;if(roomNeedsCleaningNow(room.no))counts.cleaning++;if(p.key==='available')counts.available++;if(p.key==='blocked')counts.blocked++;return counts;},{occupied:0,cleaning:0,available:0,blocked:0}),typeCounts=ROOMS.reduce((counts,room)=>{counts[room.type]=(counts[room.type]||0)+1;return counts;},{});
  4328 |         const catalogSummary=`<section class="catalog-summary" aria-label="현재 객실 상태 요약"><div class="catalog-summary-copy"><strong>총 ${ROOMS.length}개 객실</strong><span>투숙 중 ${primaryCounts.occupied||0}개 · 청소 필요 ${primaryCounts.cleaning||0}개 · 배정 가능 ${primaryCounts.available||0}개 · 배정 불가 ${primaryCounts.blocked||0}개입니다. 촛불·특이사항·청소 단계는 이유와 서브 배지로 유지됩니다.</span></div>${[{id:'all',name:'전체 객실',count:ROOMS.length},...Object.entries(ROOM_TYPES).map(([id,type])=>({id,name:type.name,count:typeCounts[id]||0}))].map(item=>`<button class="catalog-summary-stat" type="button" data-action="filter-room-type" data-type="${item.id}" aria-pressed="${state.roomTypeFilter===item.id}" aria-label="${esc(item.name)} ${item.count}개 보기"><strong>${item.count}</strong><span>${esc(item.name)}</span></button>`).join('')}</section>`;
  4329 |         return renderCoach()+renderNetworkNotice()+`<div class="room-concept-layout">${renderDateTools(false)}${catalogSummary}<div class="concept-filter-row"><label class="search-field concept-filter-search"><span class="sr-only">객실번호 검색</span>${icon('search')}<input id="room-search" class="input-control concept-search" type="search" data-control="room-search" value="${esc(state.roomSearch)}" placeholder="객실번호 검색" autocomplete="off"></label><label class="concept-status-filter"><span class="sr-only">객실 상태</span><select class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>상태 전체</option><optgroup label="상태 조건"><option value="occupied" ${state.roomFilter==='occupied'?'selected':''}>투숙 중</option><option value="cleaning" ${state.roomFilter==='cleaning'?'selected':''}>청소 필요</option><option value="available" ${state.roomFilter==='available'?'selected':''}>배정 가능</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>배정 불가</option></optgroup><optgroup label="상세 조건"><option value="checkout-inspection" ${state.roomFilter==='checkout-inspection'?'selected':''}>퇴실점검 대상</option><option value="extra-guests" ${state.roomFilter==='extra-guests'?'selected':''}>인원 추가</option><option value="vacant" ${state.roomFilter==='vacant'?'selected':''}>공실</option><option value="candle" ${state.roomFilter==='candle'?'selected':''}>촛불 있음</option><option value="issues" ${state.roomFilter==='issues'?'selected':''}>특이사항 있음</option><option value="early" ${state.roomFilter==='early'?'selected':''}>얼리 체크인</option><option value="late" ${state.roomFilter==='late'?'selected':''}>레이트 체크아웃</option></optgroup></select></label><button class="btn btn-outline room-export-trigger" type="button" data-action="open-room-export" aria-haspopup="dialog" ${isLocked()?'disabled':''}>${icon('download','icon-sm')}내보내기</button></div>${renderListState(body)}</div>`;
  4330 |       }
  4331 | 
  4332 |       const QUICK_RESERVATION_PAST_DAYS=7,QUICK_RESERVATION_FUTURE_DAYS=21,QUICK_RESERVATION_DAY_COUNT=QUICK_RESERVATION_PAST_DAYS+1+QUICK_RESERVATION_FUTURE_DAYS;
  4333 |       let quickReservationTodayWatchTimer=0;
  4334 |       function refreshQuickReservationActualToday({rerender=false}={}) {
  4335 |         const today=DEMO_TODAY;
  4336 |         if(state.quickReservationFollowsToday===false||state.quickReservationAnchorDate===today)return today;
  4337 |         state.quickReservationAnchorDate=today;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;
```

## room table: `function renderRoomTable`

matches: 1

### occurrence 1 · line 3301

```html
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
  3318 |       function queueCard(tone,badge,title,count,desc,action,label,id='') {
  3319 |         return `<article class="card queue-card ${tone}">${statusBadge(badge,tone==='danger'?'red':tone==='warning'?'amber':tone==='success'?'green':'neutral')}<h3>${title}</h3><div class="count">${count}</div><p>${desc}</p><button class="btn ${tone==='danger'?'btn-danger':'btn-outline'}" type="button" data-action="${action}" ${id?`data-id="${id}"`:''} ${isLocked()&&action!=='room-detail'?'disabled':''}>${label}</button></article>`;
  3320 |       }
  3321 | 
  3322 |       function renderAdminToday() {
  3323 |         const content=`
  3324 |           <section class="section-head"><h2>즉시 조치 큐</h2><span class="meta">색상은 원본 상태에서 파생 · 우선순위는 마감 여유로 계산</span></section>
  3325 |           <div class="queue-grid">
  3326 |             ${queueCard('danger','긴급','350호 입실 미준비','1건','미검수 · 촛불 1개','room-detail','입실 차단 해결','350')}
  3327 |             ${queueCard('warning','대기','관리자 미배정 작업','3건','시작 가능 시각이 지나 재배정이 필요한 작업','view-open-jobs','목록 보기')}
  3328 |             ${queueCard('warning','주의','마감 위험','2건','예상 소요시간 반영 시 여유 부족','view-open-jobs','목록 보기')}
  3329 |             ${queueCard('success','대기','검수 대상 목록','4건','전체 제출 검수가 필요합니다','cleaning-detail','639호 검수','639')}
  3330 |             ${queueCard('neutral','요청','담당 취소 요청','1건',state.cancelRequest==='requested'?'15분 이내 관리자 결정 필요':'처리 완료 · 타임라인 보존','cancel-review',state.cancelRequest==='requested'?'요청 처리':'결과 보기')}
  3331 |             ${queueCard('neutral','동기화','동기화·PIN·정산','2건','충돌 또는 확인 필요 사건','alerts','알림 보기')}
  3332 |           </div>
  3333 |           <div class="dashboard-layout">
  3334 |             <div><div class="section-head"><h2>객실 일별 현황</h2><span class="meta">총 7개 · 한국시간</span></div>${renderDateTools()}${renderRoomTable()}</div>
  3335 |             <aside class="rail" aria-label="보조 운영 큐">${renderDraftRail()}${renderInspectionRail()}${renderPayRail()}</aside>
```

## room detail: `function openRoom`

matches: 3

### occurrence 1 · line 6047

```html
  6031 |           return {title:`${no}호 · ${upload.label}`,subtitle:captured?'메이드가 전체 제출에 포함한 현장 촬영 이미지':'메이드가 전체 제출에 포함한 데모 이미지',large:true,body:`<div class="photo-viewer-visual">${inspectionPhotoSvg(upload,`${no}호 ${upload.label}`)}</div><div class="photo-meta"><div class="info-item"><span>구분</span><strong>${esc(collectionLabel)}</strong></div><div class="info-item"><span>촬영</span><strong>${esc(upload.image?.uploadedAt||'시각 없음')}</strong></div><div class="info-item"><span>제출 버전</span><strong>${esc(upload.image?.version||'현장 촬영')} · ${upload.status==='failed'?'검증 실패':'검증 완료'}</strong></div></div><p class="audit-note" style="margin:12px 0 0">확대 보기는 검수 참고용이며 사진별 승인·반려는 제공하지 않습니다. 사진 원문과 파일명은 URL·브라우저 이력에 저장하지 않습니다.</p>`};
  6032 |         }
  6033 |         if(payload?.source==='bomb-room'){
  6034 |           const linkedSubmission=Object.values(state.cleaningSubmissions||{}).find(item=>item.room===no&&item.reportId===payload?.recordId)||null,report=linkedSubmission?rawBombRoomReportForSubmission(linkedSubmission):state.bombRoomReports?.[payload?.recordId]||bombRoomReport(no),photo=report?.photos?.find(item=>item.id===payload.photoId),meta=bombRoomStatusMeta(report),submission=linkedSubmission||(report?.submissionId?state.cleaningSubmissions?.[report.submissionId]||null:null);
  6035 |           if(!report||report.room!==no||!photo||state.role!=='admin'&&report.reportedById!==signedInMaidId()&&submission?.performerId!==signedInMaidId())return null;
  6036 |           const decision=report.attemptStatus==='superseded'?`회차 종료 · ${esc(report.supersededAt||'시각 없음')} · ${esc(report.supersededReason||'담당 변경')}`:report.status==='pending'?'관리자 결정 대기':`${esc(report.decidedAt||'결정 시각 없음')} · ${esc(report.decisionReason|| (report.status==='approved'?'폭탄방 인정':'일반 청소 범위'))}`;
  6037 |           return {title:`${no}호 · 폭탄방 증빙`,subtitle:`${report.reportedBy} 신고 · ${meta.label} · 데모 메모리 이미지`,large:true,body:`<div class="photo-viewer-visual">${roomIssuePhotoVisual(photo,`${no}호 폭탄방 증빙 이미지`)}</div><div class="photo-meta"><div class="info-item"><span>신고자</span><strong>${esc(report.reportedBy)}</strong></div><div class="info-item"><span>신고 시각</span><strong>${esc(report.reportedAt)}</strong></div><div class="info-item"><span>검수 상태</span><strong>${esc(meta.label)}</strong></div><div class="info-item"><span>관리자 결정·회차</span><strong>${decision}</strong></div></div>${report.note?`<div class="notice notice-info" style="margin-top:12px"><div><strong>신고 메모</strong><br>${esc(report.note)}</div></div>`:''}<p class="audit-note" style="margin:12px 0 0">사진 파일명과 원본은 URL·알림·감사 이력·브라우저 영속 저장소에 남기지 않습니다.</p>`};
  6038 |         }
  6039 |         const linkedSubmission=Object.values(state.cleaningSubmissions||{}).find(item=>item.room===no&&item.roomIssuesSnapshot?.some(record=>record.id===payload?.recordId))||null,snapshotRecord=linkedSubmission?.roomIssuesSnapshot?.find(item=>item.id===payload?.recordId)||null,record=snapshotRecord||roomIssueRecords(no).find(item=>item.id===payload?.recordId),photo=record?.photos?.find(item=>item.id===payload?.photoId);
  6040 |         if(!record||!photo||state.role!=='admin'&&record.createdById!==signedInMaidId()&&linkedSubmission?.performerId!==signedInMaidId())return null;
  6041 |         return {title:`${no}호 · ${record.type||'객실 특이사항'}`,subtitle:`${record.createdBy} 등록 · 관리자 조회 가능 · 데모 메모리 이미지`,large:true,body:`<div class="photo-viewer-visual">${roomIssuePhotoVisual(photo,`${no}호 ${record.type} 특이사항 이미지`)}</div><div class="photo-meta"><div class="info-item"><span>등록자</span><strong>${esc(record.createdBy)}</strong></div><div class="info-item"><span>등록 시각</span><strong>${esc(record.createdAt)}</strong></div><div class="info-item"><span>보존 상태</span><strong>현재 탭 메모리 · 데모</strong></div></div><p class="audit-note" style="margin:12px 0 0">사진 파일명과 원본은 URL·알림·감사 이력·브라우저 영속 저장소에 남기지 않습니다.</p>`};
  6042 |       }
  6043 |       function photoViewerModalMarkup(payload) {
  6044 |         const config=photoViewerConfig(payload);
  6045 |         return config?standardModalMarkup(config):'';
  6046 |       }
  6047 |       function openRoomIssuePhoto(no,issueId,photoId,trigger=document.activeElement) {
  6048 |         const payload={source:'room-issue',room:no,recordId:issueId,photoId},config=photoViewerConfig(payload);
  6049 |         if(!config){toast('이 사진을 볼 권한이 없거나 기록을 찾을 수 없습니다.','error');return;}
  6050 |         showModal({...config,trigger,historyKind:'photo-viewer',historyPayload:payload});
  6051 |       }
  6052 |       function openBombRoomPhoto(no,reportId,photoId,trigger=document.activeElement) {
  6053 |         const payload={source:'bomb-room',room:no,recordId:reportId,photoId},config=photoViewerConfig(payload);
  6054 |         if(!config){toast('이 폭탄방 증빙을 볼 권한이 없거나 기록을 찾을 수 없습니다.','error');return;}
  6055 |         showModal({...config,trigger,historyKind:'photo-viewer',historyPayload:payload});
  6056 |       }
  6057 |       function renderAvailabilityCard() {
  6058 |         const saved=state.weeklyAvailability?.[signedInMaidId()]?.days||[],hasCommitted=state.availabilitySubmitted||state.availabilityChangeRequested,selected=hasCommitted?saved:state.availabilityDraft||[],statusLabel=state.availabilityChangeRequested?'다음 주 변경 요청':state.availabilitySubmitted?'다음 주 제출 완료':'다음 주 미제출';
  6059 |         return `<section class="card availability-card"><div class="availability-result">${statusBadge(statusLabel,state.availabilitySubmitted?'green':'amber')}<div><strong>8월 17일–23일 · 가능 ${selected.length}일</strong><span>${availabilitySubmissionWindowLabel()} 제출 · 객실 담당은 관리자만 배정</span></div>${button('근무 일정 열기','go-schedule','outline')}</div></section>`;
  6060 |       }
  6061 |       function renderMaidSchedule() {
  6062 |         const maidId=signedInMaidId(),accountActive=signedInMaidIsActive(),dayNames=[['월','17'],['화','18'],['수','19'],['목','20'],['금','21'],['토','22'],['일','23']],phase=availabilitySubmissionPhase(),submitted=state.availabilitySubmitted,editing=!!state.availabilityEditing&&phase==='open',savedSelected=state.weeklyAvailability?.[maidId]?.days||[],selected=editing||!submitted?state.availabilityDraft||[]:savedSelected,availableCount=selected.length;
  6063 |         const assigned=notifiedAssignmentEntriesForMaid(maidId);
  6064 |         const assignedCards=assigned.length?assigned.map(({item})=>{const guestCount=assignmentGuestCount(item);return `<div class="assigned-preview-grid"><div><span>근무일</span><strong>${esc(dateLabel(targetEffectiveDate(item)))}</strong></div><div><span>객실</span><strong>${item.room}호</strong></div><div><span>업무</span><strong>${esc(item.kind)}</strong></div>${guestCount?`<div><span>숙박 인원</span><strong>${esc(guestCountLabel(guestCount))}</strong></div>`:`<div><span>예약 연결</span><strong>없음</strong></div>`}<div><span>시작 가능</span><strong>${item.checkout} 이후</strong></div>${item.carryReason?`<div><span>이월</span><strong>원 계획 ${esc(dateLabel(targetPlanDate(item)))}</strong></div>`:''}</div>`;}).join(''):`<div class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 근무일 전날 밤 객실 담당을 확정하면 여기에 표시됩니다.</p></div>`;
  6065 |         const submissionWindow=availabilitySubmissionWindowLabel(),phaseText=!accountActive?'비활성 계정 · 과거 제출 읽기 전용':phase==='before'?`${submissionWindow} 제출 가능`:phase==='open'?`${submissionWindow} · 지금 제출 가능`:`${submissionWindow} 마감 · 변경은 관리자 확인 필요`;
  6066 |         const editorLocked=!accountActive||submitted&&!editing||state.availabilityChangeRequested||phase!=='open'||isLocked();
  6067 |         let actionMarkup='';
  6068 |         if(!accountActive)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>가능일 수정 잠금</strong><br>비활성 처리 중이거나 비활성인 계정은 과거 제출만 조회할 수 있습니다.</div></div>';
  6069 |         else if(state.availabilityChangeRequested)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>관리자 확인 요청됨</strong><br>기존 제출은 유지되고 변경 요청이 관리자 알림에 남았습니다.</div></div>';
  6070 |         else if(editing)actionMarkup=button('수정 내용 다시 제출','submit-week-availability','primary',isLocked()?'disabled':'');
  6071 |         else if(submitted&&phase==='open')actionMarkup=button('제출 내용 수정','edit-week-availability','primary',isLocked()?'disabled':'');
  6072 |         else if(submitted&&phase==='closed')actionMarkup=button('가능일 변경 요청','request-availability-change','outline',isLocked()?'disabled':'');
  6073 |         else if(submitted)actionMarkup=button('제출 기간 아님','edit-week-availability','outline','disabled');
  6074 |         else actionMarkup=button(phase==='open'?'다음 주 가능일 제출':phase==='before'?`${submissionWindow} 제출`:'제출 마감','submit-week-availability','primary',phase==='open'&&!isLocked()?'':'disabled');
  6075 |         return renderCoach()+renderNetworkNotice()+`<div class="weekly-availability"><section class="card week-card"><div class="week-card-head"><div><h2>8월 17일 (월)–8월 23일 (일)</h2><p>다음 주에 근무 가능한 요일을 모두 선택해 주세요.</p></div>${statusBadge(state.availabilityChangeRequested?'변경 요청':editing?'수정 중':submitted?'제출 완료':'미제출',state.availabilityChangeRequested||editing?'amber':submitted?'green':'amber')}</div><div class="deadline-bar">${icon('clock','icon-sm')}<span>${phaseText}</span></div><div class="week-days" aria-label="다음 주 근무 가능일">${dayNames.map((day,index)=>{const active=selected.includes(index);return `<button class="week-day" type="button" data-action="toggle-week-day" data-day="${index}" aria-pressed="${active}" ${editorLocked?'disabled':''}><strong>${day[0]} ${day[1]}</strong><span>${active?'근무 가능':'근무 불가'}</span><i class="week-toggle" aria-hidden="true"></i></button>`;}).join('')}</div><div class="week-total">${icon('calendar','icon-sm')}가능 ${availableCount}일 · 불가 ${7-availableCount}일</div><div class="week-submit-actions">${actionMarkup}</div><div class="assignment-notice">${icon('user')}<p>관리자가 각 근무일 전날 밤 객실을 직접 배정합니다. 메이드는 객실을 선택하거나 다른 메이드에게 배정할 수 없습니다.</p></div></section><section class="card assigned-preview"><div class="section-head"><div><h2>배정된 내 업무</h2><span class="meta">관리자 통보 완료 건만 표시</span></div>${statusBadge(`${assigned.length}건`,'blue')}</div>${assignedCards}<p class="audit-note" style="margin:10px 0 0">배정이 바뀌면 기존 담당 구간은 이력으로 남고 알림에서 변경 내용을 확인할 수 있습니다.</p></section></div>`;
  6076 |       }
  6077 |       function publicJobCard(no) {
  6078 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room?.type||'standard'];
  6079 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${esc(cleaningLabel(state.jobs[no]))}</h3><p>${esc(type.name)}</p></div>${statusBadge('관리자 배정','green')}</div><div class="schedule-line">${icon('clock','icon-sm')}<span>시작 가능 ${startTimeFor(no)} · 담당 ${esc(room?.assignee||'미정')}</span></div><div class="notice notice-info" style="margin:0">메이드는 관리자에게 통보받은 업무만 확인하고 수행할 수 있습니다.</div></article>`;
  6080 |       }
  6081 |       function renderMaidOpen() {
```

### occurrence 2 · line 6444

```html
  6428 |           ['_rels/.rels','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'],
  6429 |           ['xl/workbook.xml','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="객실 현황" sheetId="1" r:id="rId1"/></sheets></workbook>'],
  6430 |           ['xl/_rels/workbook.xml.rels','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'],
  6431 |           ['xl/worksheets/sheet1.xml',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${sheetRows}</sheetData></worksheet>`]
  6432 |         ];
  6433 |         return new Blob([xlsxZipStore(files)],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  6434 |       }
  6435 |       const ROOM_EXPORT_COLUMNS=['기준일','객실','객실 유형','기본 청소요금','엘리베이터 위치','정보 상태','투숙 상태','카드 주 상태','예정 체크아웃','실제 체크아웃','체크인','얼리 체크인','레이트 체크아웃','예약 등록','현재 입실','청소 상태','청소 담당','촛불 수량','운영 상태','운영 중지 사유','대체 객실'];
  6436 |       function roomExportRows(filtered=false) {
  6437 |         const rooms=filtered?filteredRooms():ROOMS;
  6438 |         return rooms.map(room=>{
  6439 |           const p=roomPresentation(room.no),special=roomReservationStatus(room),stop=state.roomMoves[room.no]||{},stopReason=state.roomStopReasons[room.no]||stop.reason||'사유 확인 필요',held=roomDataIssue(room.no);
  6440 |           const informationStatus=held?'확인 필요':'확인 완료',occupancyStatus=held?'미확정':room.occupancy==='occupied'?'투숙 중':'공실';
  6441 |           return [state.selectedDate,`${room.no}호`,ROOM_TYPES[room.type].name,money(ROOM_TYPES[room.type].rate),elevatorLabel(room),informationStatus,occupancyStatus,p.status,room.reservationCheckoutAt||room.nextCheckoutAt||room.checkout,room.actualCheckoutAt||'—',room.checkin,special.early?`자동 · ${special.earlyOffset} · ${special.checkin}`:'—',special.late?`자동 · ${special.lateOffset} · ${special.checkout}`:'—',held?'확인 필요':'가능',p.available?'가능':'불가',cleaningLabel(state.jobs[room.no]),held?'확인 필요':room.assignee,held?'확인 필요':`${room.occupancy==='occupied'?0:state.candles[room.no]||0}개`,held?'확인 필요':state.roomStopped[room.no]?'운영 중지':'정상',held||state.roomStopped[room.no]?held||stopReason:'—',state.roomStopped[room.no]&&stop.to?`${stop.to}호`:'—'];
  6442 |         });
  6443 |       }
  6444 |       function openRoomExport(trigger=document.activeElement) {
  6445 |         if(state.role!=='admin'){toast('객실 현황 내보내기는 관리자만 사용할 수 있습니다.','error');return;}
  6446 |         if(isLocked()){toast('최신 객실 상태를 확인한 뒤 내보낼 수 있습니다.','error');return;}
  6447 |         const filteredCount=filteredRooms().length;
  6448 |         showModal({title:'객실 현황 전체 내보내기',subtitle:`${dateLabel()} · 전체 ${ROOMS.length}객실 · 데모 화면 스냅샷`,trigger,body:`<div class="notice notice-info"><div><strong>PIN 원문과 고객 개인정보는 파일에 포함하지 않습니다.</strong><br>객실 유형·정본 청소요금·엘리베이터 위치·투숙/공실/정보 확인 필요와 고객 배정 가능 여부와 체크인·체크아웃, 청소, 촛불, 운영 중지 사유를 내보냅니다.</div></div><label class="room-export-scope" for="export-filtered"><input id="export-filtered" type="checkbox"><span><strong>현재 검색·필터 결과만 내보내기 · ${filteredCount}객실</strong><span>선택하지 않으면 ${dateLabel()} 전체 ${ROOMS.length}객실을 저장합니다.</span></span></label><div class="room-export-options"><button class="btn btn-outline" type="button" data-action="export-rooms-csv">${icon('download','icon-sm')}CSV 다운로드</button><button class="btn btn-primary" type="button" data-action="export-rooms-xls">${icon('download','icon-sm')}엑셀(.xlsx) 다운로드</button></div>`});
  6449 |       }
  6450 |       function downloadRoomExport(format) {
  6451 |         if(state.role!=='admin'){closeModal();toast('객실 현황 내보내기는 관리자만 사용할 수 있습니다.','error');return;}
  6452 |         if(isLocked()){closeModal();toast('오래된 데이터는 내보내지 않았습니다. 다시 시도해 최신 상태를 확인하세요.','error');return;}
  6453 |         const filtered=!!document.getElementById('export-filtered')?.checked,rows=roomExportRows(filtered),suffix=filtered?'filtered':'all',base=`castle-the-art_rooms_${state.selectedDate}_${suffix}_demo`;
  6454 |         if(filtered&&!rows.length){toast('현재 검색·필터 결과가 없어 파일을 만들지 않았습니다.','error');return;}
  6455 |         let blob,name;
  6456 |         if(format==='csv'){
  6457 |           const quote=value=>`"${spreadsheetSafeCell(value).replaceAll('"','""')}"`,csv=[ROOM_EXPORT_COLUMNS,...rows].map(row=>row.map(quote).join(',')).join('\r\n');
  6458 |           blob=new Blob(['\ufeff',csv],{type:'text/csv;charset=utf-8'});name=`${base}.csv`;
  6459 |         } else {
  6460 |           blob=createRoomXlsx([ROOM_EXPORT_COLUMNS,...rows]);name=`${base}.xlsx`;
  6461 |         }
  6462 |         const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;link.hidden=true;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);appendEvent('객실 현황 내보내기',`${name} · ${rows.length}객실 · PIN 제외`);closeModal();toast(`${format==='csv'?'CSV':'엑셀'} 파일 다운로드를 시작했습니다.`);
  6463 |       }
  6464 | 
  6465 |       function secureFourDigits() {
  6466 |         const a=new Uint16Array(1);let n;
  6467 |         do { crypto.getRandomValues(a); n=a[0]; } while(n>=60000);
  6468 |         return String(n%10000).padStart(4,'0');
  6469 |       }
  6470 |       function pinEditorMarkup(no,value='') {
  6471 |         return `<div class="modal-backdrop pin-backdrop" data-action="backdrop-close"><section class="modal pin-sheet" role="dialog" aria-modal="true" aria-labelledby="pin-sheet-title" aria-describedby="pin-sheet-desc"><div class="pin-sheet-body"><h2 id="pin-sheet-title">${no}호 객실 PIN 수정</h2><p id="pin-sheet-desc">숫자 4자리를 직접 입력하거나 랜덤 생성하세요.</p><div class="field"><label for="pin-edit-input">새 4자리 PIN</label><div class="pin-edit-preview"><div class="pin-input-wrap"><input id="pin-edit-input" class="input-control" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="off" aria-describedby="pin-edit-help" value="${esc(value)}"><button class="icon-btn pin-clear" type="button" data-action="pin-clear" aria-label="입력한 PIN 지우기">${icon('x')}</button></div><button class="btn btn-outline" type="button" data-action="pin-random">${icon('refresh','icon-sm')}랜덤 생성</button></div><small id="pin-edit-help">앞자리 0도 유지됩니다.</small></div></div><footer class="modal-foot"><button class="btn btn-outline" type="button" data-action="close-modal">취소</button><button class="btn btn-primary" type="button" data-action="pin-review" data-id="${no}">변경 내용 확인</button></footer></section></div>`;
  6472 |       }
  6473 |       function pinReviewMarkup(no,value) {
  6474 |         return `<div class="modal-backdrop pin-backdrop" data-action="backdrop-close"><section class="modal pin-sheet" role="dialog" aria-modal="true" aria-labelledby="pin-review-title"><div class="pin-sheet-body"><h2 id="pin-review-title">${no}호 변경 내용 확인</h2><p>저장할 새 객실 PIN을 다시 확인하세요.</p><div class="pin-edit-preview"><div class="input-control" style="min-height:58px;display:flex;align-items:center;font-size:1.3rem;font-weight:900;letter-spacing:.22em">${esc(value)}</div><div class="btn btn-soft" aria-hidden="true">새 PIN</div></div><p class="audit-note" style="margin-top:12px">감사 이력에는 PIN 원문을 남기지 않습니다.</p></div><footer class="modal-foot"><button class="btn btn-outline" type="button" data-action="pin-back" data-id="${no}">돌아가서 수정</button><button class="btn btn-primary" type="button" data-action="pin-save" data-id="${no}">저장</button></footer></section></div>`;
  6475 |       }
  6476 |       function openPinEditor(no,trigger=pinCardTrigger||document.activeElement) {
  6477 |         pendingPin=null;if(trigger?.dataset?.action==='pin-edit')pinCardTrigger=trigger;modalTrigger=pinCardTrigger||trigger;
  6478 |         const current=readProtectedPin(no);
```

### occurrence 3 · line 6520

```html
  6504 |       function updateReservationTimePreview() {
  6505 |         const checkinAt=document.getElementById('res-checkin')?.value||'',checkoutAt=document.getElementById('res-checkout')?.value||'',status=reservationTimeStatus(checkinAt,checkoutAt);
  6506 |         const checkinStatus=document.querySelector('[data-reservation-checkin-status]'),checkoutStatus=document.querySelector('[data-reservation-checkout-status]'),nightStatus=document.querySelector('[data-reservation-night-status]');
  6507 |         if(checkinStatus)checkinStatus.textContent=reservationStatusText(status,'checkin');
  6508 |         if(checkoutStatus)checkoutStatus.textContent=reservationStatusText(status,'checkout');
  6509 |         if(nightStatus){const valid=checkinAt&&checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10),nights=valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;nightStatus.textContent=valid?`${nights}박`:'입퇴실 시각 확인 필요';}
  6510 |       }
  6511 |       function updateReservationGuestControls(resetToDefault=false) {
  6512 |         const roomNo=document.getElementById('res-room')?.value||'',policy=guestPolicyForRoom(roomNo),input=document.getElementById('res-guests'),value=document.getElementById('res-guests-value'),help=document.getElementById('res-guests-help'),stepper=document.getElementById('reservation-guest-stepper'),minus=document.querySelector('[data-action="reservation-guest-change"][data-delta="-1"]'),plus=document.querySelector('[data-action="reservation-guest-change"][data-delta="1"]');
  6513 |         if(!input||!value||!stepper)return;
  6514 |         const current=resetToDefault?policy.defaultGuestCount:Number(input.value),count=Number.isInteger(current)&&current>=1&&current<=policy.maxGuestCount?current:policy.defaultGuestCount;
  6515 |         input.value=String(count);value.textContent=guestCountLabel(count);if(help)help.textContent=`기본 ${policy.defaultGuestCount}명 · 최대 ${policy.maxGuestCount}명`;
  6516 |         stepper.dataset.max=String(policy.maxGuestCount);
  6517 |         if(minus){minus.disabled=count<=1;minus.setAttribute('aria-label',`${roomNo}호 예약 인원수 1명 줄이기`);}
  6518 |         if(plus){plus.disabled=count>=policy.maxGuestCount;plus.setAttribute('aria-label',`${roomNo}호 예약 인원수 1명 늘리기, 최대 ${policy.maxGuestCount}명`);}
  6519 |       }
  6520 |       function openRoomInfoEditor(no,trigger=document.activeElement) {
  6521 |         const room=ROOMS.find(item=>item.no===no);
  6522 |         if(!room||state.role!=='admin'||isLocked()){toast('관리자 최신 상태에서만 객실 정보를 수정할 수 있습니다.','error');return;}
  6523 |         maskPin();
  6524 |         const held=roomIsOnHold(no),typeOptions=Object.entries(ROOM_TYPES).map(([id,type])=>`<option value="${id}" ${room.type===id?'selected':''}>${esc(type.name)} · ${money(type.rate)}</option>`).join('');
  6525 |         showModal({title:`${no}호 객실 정보 수정`,subtitle:'객실번호는 이력 연결키로 유지하고 타입·엘리베이터를 수정합니다.',trigger,body:`<form id="room-info-form" class="form-grid"><div class="field"><label for="room-info-number">객실번호</label><input id="room-info-number" class="input-control" value="${no}" readonly aria-readonly="true"><small>PIN·청소·주급 이력과 연결된 식별값</small></div><div class="field"><label for="room-info-type">객실 타입</label><select id="room-info-type" class="select-control">${typeOptions}</select></div><div class="field"><label for="room-info-elevator">엘리베이터</label><select id="room-info-elevator" class="select-control"><option value="" ${room.elevator?'':'selected'}>미기재</option>${['A','B','C'].map(value=>`<option value="${value}" ${room.elevator===value?'selected':''}>${value} 엘리베이터</option>`).join('')}</select></div>${held?`<div class="field"><label for="room-info-occupancy">현재 투숙 상태</label><select id="room-info-occupancy" class="select-control"><option value="">선택하세요</option><option value="vacant">공실</option><option value="occupied">투숙 중</option></select><small>선택하면 정보 확인 필요 상태가 해제됩니다.</small></div>`:''}<div class="field field-full"><div class="notice notice-info"><div><strong>적용 범위</strong><br>새 타입·엘리베이터는 이후 생성하는 작업부터 적용됩니다. 이미 완료·제출된 청소의 당시 단가와 템플릿은 그대로 보존됩니다.</div></div></div></form>`,confirmLabel:held?'정보 확정·보류 해제':'객실 정보 저장',confirmAction:'save-room-info'});
  6526 |         const confirm=document.querySelector('[data-action="save-room-info"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6527 |       }
  6528 |       function recordManualCheckoutScheduleChange(no,attempt,previousWorkDate,previousAccessStart) {
  6529 |         if(!attempt)return;
  6530 |         const targetId=attempt.workTargetId||assignmentHistoryTargetId(no,attempt.kind,previousWorkDate),record=state.assignments?.[targetId]||null,maidId=MAIDS.some(maid=>maid.id===attempt.performerId)?attempt.performerId:null,order=record?.order||record?.previousOrder||null,maidLabel=maidId?maidName(maidId):'미배정',room=ROOMS.find(item=>item.no===no),typeId=attempt.roomMetaSnapshot?.typeId||room?.type||'standard',type=ROOM_TYPES[typeId]||ROOM_TYPES.standard,ledgerTarget=state.cleaningTargets?.[targetId]||null,committed=record?.committedTarget||ledgerTarget||{id:targetId,room:no,type:typeId,kind:attempt.kind,source:'manual',sourceLabel:'현재 작업',rateSnapshot:Number(attempt.baseRateSnapshot)||Number(attempt.templateSnapshot?.rate)||type.rate,minutesSnapshot:Number(attempt.templateSnapshot?.minutes)||type.minutes,elevatorSnapshot:Object.prototype.hasOwnProperty.call(attempt.roomMetaSnapshot||{},'elevator')?attempt.roomMetaSnapshot.elevator:room?.elevator||null},committedReservationId=committed.reservationId||attempt.reservationIdSnapshot||null,committedGuestCount=assignmentGuestCount(committed)||(committedReservationId&&committedReservationId===attempt.reservationIdSnapshot?guestCountForAttempt(attempt):null),planDate=committed.planDate||committed.date||previousWorkDate,targetSnapshot={...committed,id:targetId,currentAttemptId:attempt.id,room:no,date:planDate,planDate,effectiveDate:state.selectedDate,checkout:attempt.checkoutSnapshot||state.time,checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||'15:30',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||state.time,reservationId:committedReservationId,guestCount:committedGuestCount};
  6531 |         if(record){
  6532 |           record.committedTarget=targetSnapshot;record.status='notified';record.scheduleChanged=false;record.guestCountChanged=false;record.reservationChanged=false;record.targetChanged=false;
  6533 |           if(record.maidId){record.previousMaidId=record.maidId;record.previousOrder=record.order;}
  6534 |         }
  6535 |         state.cleaningTargets[targetId]={...cleaningTargetSnapshot(targetSnapshot,planDate),...(state.cleaningTargets?.[targetId]||{}),...targetSnapshot,currentAttemptId:attempt.id};
  6536 |         state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId,attemptId:attempt.id,assignmentDate:state.selectedDate,room:no,beforeMaidId:maidId,afterMaidId:maidId,before:maidId?`${maidLabel}${order?` · ${order}번째`:''} · ${dateLabel(previousWorkDate)} ${previousAccessStart}`:'미배정',after:maidId?`${maidLabel}${order?` · ${order}번째`:''} · ${dateLabel(state.selectedDate)} ${state.time}`:'미배정',reason:'실제 체크아웃 반영 · 기존 담당·수행 회차 유지 · 시작 시각 변경 재통보'});
  6537 |         if(maidId)appendEvent('내 청소 시작 시각 변경 통보',`${no}호 · ${dateLabel(previousWorkDate)} ${previousAccessStart} → ${dateLabel(state.selectedDate)} ${state.time} · 담당·회차 ${attempt.id} 유지`,{maidIds:[maidId],roomId:no});
  6538 |       }
  6539 |       function openManualCheckout(no,trigger=document.activeElement) {
  6540 |         const room=ROOMS.find(item=>item.no===no),blockingAttempt=manualCheckoutBlockingAttempt(no),unstartedAttempt=activeUnfinishedAttempt(no),pinViewed=unstartedAttempt&&roomPinWasViewed(no,unstartedAttempt.id);
  6541 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='occupied'){toast('관리자 최신 상태의 투숙 중 객실만 지금 체크아웃할 수 있습니다.','error');return;}
  6542 |         if(blockingAttempt){toast(`진행 중인 ${blockingAttempt.kind} ${blockingAttempt.id}을 먼저 마무리하세요.`,'error');return;}
  6543 |         showModal({title:`${no}호 지금 체크아웃`,subtitle:'예정 일정은 남기고 실제 퇴실만 지금 기록합니다.',trigger,body:`<div class="info-grid"><div class="info-item"><span>현재 상태</span><strong>투숙 중</strong></div><div class="info-item"><span>실제 체크아웃</span><strong>${dateLabel(state.selectedDate)} ${esc(state.time)}</strong></div><div class="info-item"><span>예정 체크아웃</span><strong>${esc(plannedCheckoutLabel(room))}</strong></div><div class="info-item"><span>처리 결과</span><strong>공실 · 퇴실 청소 필요</strong></div></div><div class="notice notice-warning" style="margin-top:14px"><div><strong>예약 취소가 아닙니다.</strong><br>예정 일정과 미래 예약은 유지하고 오늘 퇴실 청소는 한 건만 만듭니다.${unstartedAttempt?'<br>이미 배정된 미시작 청소는 담당과 순서를 유지하고 실제 퇴실 시각부터 시작할 수 있습니다.':''}${pinViewed?'<br>기존 PIN 조회는 종료되며 실제 퇴실 시각 이후 다시 확인할 수 있습니다.':''}</div></div>`,confirmLabel:'투숙 종료·청소 준비',confirmAction:'confirm-manual-checkout',confirmVariant:'danger'});
  6544 |         const confirm=document.querySelector('[data-action="confirm-manual-checkout"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6545 |       }
  6546 |       function openManualCheckin(no,trigger=document.activeElement) {
  6547 |         const room=ROOMS.find(item=>item.no===no),presentation=roomPresentation(no);
  6548 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='vacant'||presentation.available!==true){toast('청소·촛불·운영 조건이 모두 준비된 공실만 투숙 중으로 바꿀 수 있습니다.','error');return;}
  6549 |         showModal({title:`${no}호 투숙 시작`,subtitle:'현재 객실에 손님이 들어온 사실만 기록합니다.',trigger,body:`<div class="notice notice-info"><div><strong>고객 개인정보는 입력하지 않습니다.</strong><br>${dateLabel(state.selectedDate)} ${esc(state.time)}부터 객실 상태를 투숙 중으로 바꿉니다.</div></div>`,confirmLabel:'투숙 중으로 변경',confirmAction:'confirm-manual-checkin'});
  6550 |         const confirm=document.querySelector('[data-action="confirm-manual-checkin"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6551 |       }
  6552 |       function reservationNextRegistrationState(room,existing,buckets) {
  6553 |         const weekPast=reservationWeekIsPast(buckets.window.startDate),occupiedEnd=occupiedReservationEnd(room),needsCheckoutUpdate=occupiedStayNeedsCheckoutUpdate(room);
  6554 |         return {canAdd:!!existing&&!weekPast&&adminCanMutate()&&(room.occupancy!=='occupied'||!!occupiedEnd&&!needsCheckoutUpdate),nextDate:suggestedReservationStartDate(room.no),weekPast,occupiedEnd,needsCheckoutUpdate};
```

## room detail action: `room-detail`

matches: 21

### occurrence 1 · line 843

```html
   827 |     .room-card-v2 { border:1px solid #d7dfe8; border-left-width:1px; border-radius:17px; box-shadow:0 7px 22px rgba(24,49,76,.055); }
   828 |     .room-card-v2.tone-green,.room-card-v2.tone-amber,.room-card-v2.tone-red,.room-card-v2.tone-neutral { border-left-color:#d7dfe8; }
   829 |     .room-card-main { padding:18px 18px 0; }
   830 |     .room-card-head h3 { color:#102f5d; font-size:1.55rem; letter-spacing:-.035em; }
   831 |     .room-card-head p { margin-top:3px; color:#2e3f52; font-size:14px; }
   832 |     .room-location-line { color:#45627f; font-size:13px; }
   833 |     .concept-tag { display:inline-flex; align-items:center; min-height:34px; padding:5px 10px; border:1px solid #b8c5d4; border-radius:9px; color:#244366; background:#fff; font-size:12px; font-weight:850; }
   834 |     .concept-tag.blue { color:#1e64b1; border-color:#9bc0ee; background:#f7fbff; }
   835 |     .concept-tag.green { color:#16714f; border-color:#9bcfb9; background:#f5fbf8; }
   836 |     .concept-tag.orange { color:#ca5715; border-color:#f2af84; background:#fff9f4; }
   837 |     .room-schedule-badges { flex:1; justify-content:flex-end; }
   838 |     .schedule-priority-badge { display:inline-flex; align-items:center; gap:5px; min-height:36px; padding:6px 10px; border:1px solid transparent; border-radius:999px; color:#fff; background:#245fa6; box-shadow:0 4px 12px rgba(36,95,166,.18); font-size:11px; font-weight:900; line-height:1.25; }
   839 |     .schedule-priority-badge.late { background:#8b416d; box-shadow:0 4px 12px rgba(139,65,109,.18); }
   840 |     .schedule-priority-badge.stayover { background:#67509a; box-shadow:0 4px 12px rgba(103,80,154,.18); }
   841 |     .schedule-priority-badge.guests { background:#17314a; box-shadow:0 4px 12px rgba(23,49,74,.2); }
   842 |     .schedule-priority-badge .icon { flex:0 0 auto; width:14px; height:14px; }
   843 |     .room-detail-badge { display:inline-flex; align-items:center; gap:4px; min-height:28px; padding:4px 8px; border:1px solid #d8b1b5; border-radius:999px; color:#8a343a; background:#fff7f7; font-size:11px; font-weight:850; line-height:1.25; }
   844 |     .room-card-v2 .time-band { min-height:56px; margin-top:16px; padding:12px 14px; border:1px solid #dbe3eb; border-radius:11px 11px 0 0; color:#174e99; background:#fff; font-size:14px; }
   845 |     .room-card-v2 .time-band .special { color:#ca5715; background:transparent; font-size:12px; }
   846 |     .concept-status-panel { display:flex; align-items:center; gap:13px; min-height:96px; padding:15px 16px; border:1px solid #c8d9ef; border-top:0; background:#edf5ff; }
   847 |     .concept-status-panel.amber { border-color:#f0c9a5; background:#fff3e7; }
   848 |     .concept-status-panel.green { border-color:#b8ddcf; background:#edf8f3; }
   849 |     .concept-status-panel.red { border-color:#efb7bd; background:#fff0f1; }
   850 |     .concept-status-panel.neutral { border-color:#d8dee5; background:#f2f4f6; }
   851 |     .status-symbol { display:grid; place-items:center; flex:0 0 auto; width:46px; height:46px; border-radius:50%; color:#fff; background:#236cda; }
   852 |     .concept-status-panel.amber .status-symbol { background:#ed6814; }
   853 |     .concept-status-panel.green .status-symbol { background:var(--green); }
   854 |     .concept-status-panel.red .status-symbol { background:var(--red); }
   855 |     .concept-status-panel.neutral .status-symbol { background:#6b7280; }
   856 |     .concept-status-copy { min-width:0; flex:1; }
   857 |     .concept-status-copy strong { display:block; color:#123e78; font-size:1.16rem; line-height:1.25; }
   858 |     .concept-status-panel.amber .concept-status-copy strong { color:#c94e0a; }
   859 |     .concept-status-panel.neutral .concept-status-copy strong { color:#344054; }
   860 |     .concept-status-copy span { display:block; margin-top:3px; color:#52677e; font-size:13px; }
   861 |     .room-status-subs { display:flex; flex-wrap:wrap; gap:5px; margin-top:8px; }
   862 |     .concept-status-copy .room-status-sub { display:inline-flex; align-items:center; gap:4px; width:max-content; max-width:100%; min-height:25px; margin-top:0; padding:3px 7px; border:1px solid #d7dfe8; border-radius:999px; color:#5f6f82; background:rgba(255,255,255,.68); font-size:10px; font-weight:850; line-height:1.3; }
   863 |     .room-status-sub .icon { width:13px; height:13px; }
   864 |     .concept-candle { display:flex; align-items:center; gap:7px; flex:0 0 auto; color:#253b53; font-size:13px; font-weight:800; }
   865 |     .concept-status-panel .btn { flex:0 0 auto; min-height:46px; }
   866 |     .pin-row.concept-pin { min-height:70px; margin-top:0; padding:12px 14px; border-width:0 1px 1px; border-radius:0; background:#fff; }
   867 |     .concept-pin .pin-copy { display:flex; align-items:center; gap:14px; }
   868 |     .concept-pin .pin-copy span:first-child { color:#1a2f49; font-size:14px; font-weight:850; }
   869 |     .concept-pin .pin-copy strong { margin:0; color:#162e4e; font-size:18px; letter-spacing:.16em; }
   870 |     .concept-pin .pin-copy span:last-child:not(:first-child) { margin-left:auto; }
   871 |     .concept-pin .btn { min-height:46px; padding-inline:17px; border-radius:9px; }
   872 |     .room-quick-actions { margin:0 18px 18px; border:1px solid var(--line); border-top:0; border-radius:0 0 11px 11px; overflow:hidden; }
   873 |     .room-quick-actions .btn { min-height:58px; color:#273e59; font-size:12px; }
   874 |     .room-quick-actions .icon { margin:0 auto 3px; width:18px; height:18px; }
   875 |     .room-quick-actions .btn { display:flex; flex-direction:column; }
   876 |     .pin-sheet { width:min(620px,100%); }
   877 |     .pin-sheet-body { padding:18px 20px 14px; }
```

### occurrence 2 · line 2625

```html
  2609 |         {id:'notification-seed-admin-inspection',title:'639호 청소 검수 요청',time:'10:18',createdAt:'2026-08-15 10:18',detail:'이서연이 전체 청소 제출을 완료했습니다.',roomId:'639',maidIds:[],notify:true,audience:['admin'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-inspection'},groupKey:'admin:inspection:639',readBy:[]},
  2610 |         {id:'notification-seed-admin-cancel',title:'332호 담당 취소 요청',time:'10:07',createdAt:'2026-08-15 10:07',detail:'김민지1 · 투숙객이 객실에 머물고 있음 · 결정 전 담당 유지',roomId:'332',maidIds:['m1'],notify:true,audience:['admin'],category:'cancellation',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'cancel-review'},groupKey:'admin:cancellation:332',readBy:[]},
  2611 |         {id:'notification-seed-admin-availability',title:'다음 주 가능일 전원 제출 완료',time:'09:30',createdAt:'2026-08-15 09:30',detail:'등록된 메이드 9명이 모두 근무 가능일을 제출했습니다.',maidIds:[],notify:true,audience:['admin'],category:'availability',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-workforce'},groupKey:'admin:availability:next-week',readBy:['admin']},
  2612 |         {id:'notification-seed-admin-handled',title:'350호 미배정 청소 조치 완료',time:'08:55',createdAt:'2026-08-15 08:55',detail:'담당 지정 완료 · 사건 기록 보존',roomId:'350',maidIds:[],notify:true,audience:['admin'],category:'assignment',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-cleaning-assignment',data:{day:'today'}},groupKey:'admin:assignment:350',readBy:['admin']},
  2613 |         {id:'notification-seed-maid-correction',title:'350호 보완 청소 요청',time:'10:05',createdAt:'2026-08-15 10:05',detail:'욕실 거울과 TV 전원 사진을 다시 확인해 주세요.',roomId:'350',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:inspection:350',readBy:[]},
  2614 |         {id:'notification-seed-maid-reminder',title:'332호 청소 시작 60분 전',time:'09:55',createdAt:'2026-08-15 09:55',detail:'오늘 10:55 시작 예정 · 예정 업무를 확인하세요.',roomId:'332',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'delay',priority:'normal',push:true,actionRequired:false,status:'open',target:{action:'go-my'},groupKey:'maid:m1:delay:332',readBy:[]},
  2615 |         {id:'notification-seed-maid-order',title:'117호 청소 순서 변경',time:'09:45',createdAt:'2026-08-15 09:45',detail:'2번째에서 1번째 청소로 변경되었습니다.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
  2616 |         {id:'notification-seed-maid-assignment',title:'117호 퇴실 청소 배정',time:'09:40',createdAt:'2026-08-15 09:40',detail:'오늘 13:00까지 완료해 주세요.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
  2617 |         {id:'notification-seed-maid-payroll',title:'이번 주 주급 정산 확정',time:'09:20',createdAt:'2026-08-15 09:20',detail:'객실별 승인 합계가 주급 내역에 반영되었습니다.',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'payroll',priority:'normal',push:false,pushOptional:true,actionRequired:false,status:'handled',target:{action:'go-maid-pay'},groupKey:'maid:m1:payroll:2026-08-10',readBy:['maid:m1']}
  2618 |       ];}
  2619 |       function nextNotificationEventId(){state.notificationSequence=Number(state.notificationSequence||0)+1;return `notification-${state.selectedDate||'demo'}-${state.time?.replace(':','')||'0000'}-${state.notificationSequence}`;}
  2620 |       function notificationMinuteValue(event){const text=String(event?.createdAt||`${state.selectedDate||'2026-08-15'} ${event?.time||'00:00'}`),match=text.match(/(\d{4})-(\d{2})-(\d{2})[^\d]?(\d{2}):(\d{2})/);if(!match)return 0;return Math.floor(Date.UTC(Number(match[1]),Number(match[2])-1,Number(match[3]),Number(match[4]),Number(match[5]))/60000);}
  2621 |       function notificationRoomFromText(title,detail,roomId=null){if(roomId)return String(roomId);return String(title||'').match(/(\d{3})호/)?.[1]||String(detail||'').match(/(\d{3})호/)?.[1]||null;}
  2622 |       function notificationMaidIdsForRoom(roomId){if(!roomId)return [];const submission=typeof currentSubmission==='function'?currentSubmission(String(roomId)):null,attempt=typeof currentAttemptId==='function'?state.cleaningAttempts?.[currentAttemptId(String(roomId))]:null,assignee=ROOMS.find(room=>room.no===String(roomId))?.assignee,assigneeId=MAIDS.find(maid=>maid.name===assignee)?.id;return [...new Set([submission?.performerId,attempt?.performerId,assigneeId].filter(id=>MAIDS.some(maid=>maid.id===id)))];}
  2623 |       function notificationMaidIdsForComplaint(){const item=(state.complaints||[]).find(entry=>!entry.deleted&&['unread','ruled','objected'].includes(entry.responseStatus))||(state.complaints||[])[0],maidId=MAIDS.find(maid=>maid.name===item?.maid)?.id;return maidId?[maidId]:[];}
  2624 |       function notificationCategoryFromText(text){if(/검수|전체 제출|보완|재청소/.test(text))return 'inspection';if(/배정|담당 변경|순서 변경|청소 취소 통보/.test(text))return 'assignment';if(/취소 요청|취소 승인|취소 거절|담당 취소/.test(text))return 'cancellation';if(/입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text))return 'issue';if(/마감|지연|미시작|60분 전|시작 시각/.test(text))return 'delay';if(/가능일/.test(text))return 'availability';if(/컴플레인|이의|판정/.test(text))return 'complaint';if(/충돌|동기화 실패|저장 충돌|오래된 데이터/.test(text))return 'conflict';if(/주급|지급|정산/.test(text))return 'payroll';return 'general';}
  2625 |       function notificationTargetFor(category,recipientRole,roomId,options={}){if(options.target)return options.target;if(recipientRole==='admin'){if(category==='inspection')return {action:'go-inspection'};if(category==='assignment'||category==='delay')return {action:'go-cleaning-assignment',data:{day:'today'}};if(category==='cancellation')return {action:'cancel-review'};if(category==='issue'||category==='conflict')return roomId?{action:'room-detail',id:roomId}:{action:'alerts'};if(category==='availability')return {action:'go-workforce'};if(category==='complaint')return {action:'complaint-detail'};if(category==='payroll')return {action:'go-payroll'};return {action:'alerts'};}if(category==='payroll')return {action:'go-maid-pay'};if(category==='availability')return {action:'go-schedule'};if(category==='complaint')return {action:'complaint-detail'};return {action:'go-my'};}
  2626 |       function notificationPolicyForEvent(title,detail,options={}){
  2627 |         if(options.notification===false)return null;
  2628 |         const actorRole=options.actorRole||state.role||'system',actorMaidId=options.actorMaidId||(actorRole==='maid'?signedInMaidId():null),text=`${title||''} ${detail||''}`,roomId=notificationRoomFromText(title,detail,options.roomId),requestedMaidIds=[...new Set((options.maidIds||[]).filter(id=>MAIDS.some(maid=>maid.id===id)))],category=options.category||notificationCategoryFromText(text);
  2629 |         if(options.notification&&typeof options.notification==='object'){
  2630 |           const explicit=options.notification,audience=[...new Set(explicit.audience||[])];if(!audience.length)return null;const recipientRole=audience[0]==='admin'?'admin':'maid';return {...explicit,audience,category:explicit.category||category,roomId,priority:explicit.priority||'normal',push:explicit.push!==false,actionRequired:explicit.actionRequired!==false,status:explicit.status||'open',target:notificationTargetFor(explicit.category||category,recipientRole,roomId,explicit),groupKey:explicit.groupKey||`${audience.join('|')}:${explicit.category||category}:${roomId||'general'}`,actorRole,actorMaidId};
  2631 |         }
  2632 |         if(actorRole==='maid'){
  2633 |           if(/청소 전체 제출|검수 요청|재검수 요청/.test(text))return {audience:['admin'],category:'inspection',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('inspection','admin',roomId),groupKey:`admin:inspection:${roomId||'general'}`,actorRole,actorMaidId};
  2634 |           if(/담당 취소 요청|취소 요청/.test(text))return {audience:['admin'],category:'cancellation',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('cancellation','admin',roomId),groupKey:`admin:cancellation:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2635 |           if(/이의 제출|입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text)){const adminCategory=/이의/.test(text)?'complaint':'issue';return {audience:['admin'],category:adminCategory,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(adminCategory,'admin',roomId),groupKey:`admin:${adminCategory}:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};}
  2636 |           if(/시작 지연|완료 지연|마감 초과/.test(text))return {audience:['admin'],category:'delay',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('delay','admin',roomId),groupKey:`admin:delay:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
  2637 |           return null;
  2638 |         }
  2639 |         if(actorRole==='admin'){
  2640 |           let targetMaidIds=[...requestedMaidIds];
  2641 |           if(/전체 제출 승인|검수 승인|전체 제출 반려|보완 청소|재청소/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForRoom(roomId);
  2642 |           if(/컴플레인 판정|이의 답변/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForComplaint();
  2643 |           const maidNotice=/^내 |통보|안내|배정|담당 변경|순서 변경|취소|시작 시각|보류|시작 가능|전체 제출 승인|검수 승인|전체 제출 반려|보완|재청소|컴플레인 판정|이의 답변|주급|지급|마감|지연|비활성/.test(text);
  2644 |           if(targetMaidIds.length&&maidNotice){const audience=targetMaidIds.map(id=>`maid:${id}`),informational=/승인|종결|확정|지급 완료|처리 결과|비활성 완료/.test(text)&&!/보완|재청소|지연|마감/.test(text),priority=/긴급|보완|재청소|반려|지연|마감|취소/.test(text)?'high':'normal',pushOptional=category==='payroll'&&/정산 확정/.test(text);return {audience,category,roomId,priority,push:!pushOptional,pushOptional,actionRequired:!informational,status:informational?'handled':'open',target:notificationTargetFor(category,'maid',roomId),groupKey:`${audience.join('|')}:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
  2645 |           if(/미배정.*남|미배정 청소|가능일.*미제출|동기화 실패|저장 충돌|주급.*오류|지급.*예외/.test(text)){return {audience:['admin'],category,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(category,'admin',roomId),groupKey:`admin:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
  2646 |           return null;
  2647 |         }
  2648 |         return null;
  2649 |       }
  2650 |       function normalizeNotificationEvent(event,index=0){if(!event||typeof event!=='object')return event;event.id=event.id||`event-${index}-${String(event.time||'0000').replace(/\D/g,'')}`;event.time=event.time||state.time;event.createdAt=event.createdAt||`${state.selectedDate||'2026-08-15'} ${event.time}`;event.maidIds=Array.isArray(event.maidIds)?event.maidIds:[];event.audience=Array.isArray(event.audience)?event.audience:[];event.readBy=Array.isArray(event.readBy)?event.readBy:[];event.notify=event.notify===true;if(event.notify){event.category=event.category||notificationCategoryFromText(`${event.title} ${event.detail}`);event.priority=event.priority||'normal';event.status=event.status||'open';event.actionRequired=event.actionRequired!==false;event.groupKey=event.groupKey||`${event.audience.join('|')}:${event.category}:${event.roomId||'general'}`;event.target=event.target||notificationTargetFor(event.category,event.audience[0]==='admin'?'admin':'maid',event.roomId);}return event;}
  2651 |       function ensureNotificationState(){state.events=Array.isArray(state.events)?state.events:[];state.notificationPushSettings=state.notificationPushSettings&&typeof state.notificationPushSettings==='object'?state.notificationPushSettings:{};state.notificationFilter=['all','unread','action'].includes(state.notificationFilter)?state.notificationFilter:'all';if(state.notificationSchemaVersion!==NOTIFICATION_SCHEMA_VERSION){const existingIds=new Set(state.events.map(event=>event?.id).filter(Boolean)),seeds=notificationSeedEvents().filter(event=>!existingIds.has(event.id));state.events=[...seeds,...state.events];state.notificationSchemaVersion=NOTIFICATION_SCHEMA_VERSION;}state.notificationSequence=Number(state.notificationSequence||state.events.length);state.events.forEach(normalizeNotificationEvent);return state.events;}
  2652 |       function notificationEventsForKey(key=notificationAudienceKey()){ensureNotificationState();return state.events.filter(event=>event.notify&&event.audience.includes(key)).sort((left,right)=>notificationMinuteValue(right)-notificationMinuteValue(left));}
  2653 |       function notificationBundlesForKey(key=notificationAudienceKey()){
  2654 |         const bundles=[];for(const event of notificationEventsForKey(key)){const stamp=notificationMinuteValue(event),groupKey=event.groupKey||event.id,existing=bundles.find(bundle=>bundle.groupKey===groupKey&&Math.abs(bundle.latestStamp-stamp)<=NOTIFICATION_BUNDLE_WINDOW_MINUTES);if(existing){existing.events.push(event);existing.eventIds.push(event.id);existing.bundleCount+=1;existing.unread=existing.unread||!event.readBy.includes(key);existing.actionRequired=existing.actionRequired||event.actionRequired&&event.status!=='handled';existing.latestStamp=Math.max(existing.latestStamp,stamp);if(stamp>=notificationMinuteValue(existing.latest)){existing.latest=event;existing.title=event.title;existing.detail=event.detail;}}else bundles.push({id:event.id,groupKey,latest:event,events:[event],eventIds:[event.id],bundleCount:1,title:event.title,detail:event.detail,latestStamp:stamp,unread:!event.readBy.includes(key),actionRequired:event.actionRequired&&event.status!=='handled'});}return bundles.sort((left,right)=>right.latestStamp-left.latestStamp);
  2655 |       }
  2656 |       function notificationUnreadCount(key=notificationAudienceKey()){return notificationBundlesForKey(key).filter(bundle=>bundle.unread).length;}
  2657 |       function markNotificationRead(ids,key=notificationAudienceKey()){ensureNotificationState();const targetIds=new Set(Array.isArray(ids)?ids:[ids]);state.events.forEach(event=>{if(targetIds.has(event.id)&&event.notify&&!event.readBy.includes(key))event.readBy.push(key);});}
  2658 |       function markAllNotificationsRead(key=notificationAudienceKey()){notificationEventsForKey(key).forEach(event=>{if(!event.readBy.includes(key))event.readBy.push(key);});}
  2659 |       function notificationPushEnabled(key=notificationPushKey()){ensureNotificationState();if(!(key in state.notificationPushSettings))state.notificationPushSettings[key]=!!state.notificationsEnabled;return !!state.notificationPushSettings[key];}
```

### occurrence 3 · line 3273

```html
  3257 |       function renderNetworkNotice() {
  3258 |         if (state.network==='online' && state.listMode!=='stale') return '';
  3259 |         return `<div class="notice notice-danger">${icon('sync')}<div><strong>${state.network==='offline'?'오프라인 · 읽기 전용':'오래된 데이터 · 변경할 수 없음'}</strong><br>마지막 연결 09:48. 인터넷에 연결한 뒤 다시 시도하세요.</div>${button('다시 시도','retry-network','outline')}</div>`;
  3260 |       }
  3261 | 
  3262 |       function renderListState(content, kind='queue') {
  3263 |         if (state.listMode==='loading') return `<section class="card" aria-busy="true" aria-label="불러오는 중"><div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></section>`;
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
```

### occurrence 4 · line 3274

```html
  3258 |         if (state.network==='online' && state.listMode!=='stale') return '';
  3259 |         return `<div class="notice notice-danger">${icon('sync')}<div><strong>${state.network==='offline'?'오프라인 · 읽기 전용':'오래된 데이터 · 변경할 수 없음'}</strong><br>마지막 연결 09:48. 인터넷에 연결한 뒤 다시 시도하세요.</div>${button('다시 시도','retry-network','outline')}</div>`;
  3260 |       }
  3261 | 
  3262 |       function renderListState(content, kind='queue') {
  3263 |         if (state.listMode==='loading') return `<section class="card" aria-busy="true" aria-label="불러오는 중"><div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></section>`;
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
```

### occurrence 5 · line 3276

```html
  3260 |       }
  3261 | 
  3262 |       function renderListState(content, kind='queue') {
  3263 |         if (state.listMode==='loading') return `<section class="card" aria-busy="true" aria-label="불러오는 중"><div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></section>`;
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
```

### occurrence 6 · line 3278

```html
  3262 |       function renderListState(content, kind='queue') {
  3263 |         if (state.listMode==='loading') return `<section class="card" aria-busy="true" aria-label="불러오는 중"><div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></section>`;
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
```

### occurrence 7 · line 3280

```html
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
```

### occurrence 8 · line 3282

```html
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
```

### occurrence 9 · line 3283

```html
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
```

### occurrence 10 · line 3296

```html
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
  3318 |       function queueCard(tone,badge,title,count,desc,action,label,id='') {
  3319 |         return `<article class="card queue-card ${tone}">${statusBadge(badge,tone==='danger'?'red':tone==='warning'?'amber':tone==='success'?'green':'neutral')}<h3>${title}</h3><div class="count">${count}</div><p>${desc}</p><button class="btn ${tone==='danger'?'btn-danger':'btn-outline'}" type="button" data-action="${action}" ${id?`data-id="${id}"`:''} ${isLocked()&&action!=='room-detail'?'disabled':''}>${label}</button></article>`;
  3320 |       }
  3321 | 
  3322 |       function renderAdminToday() {
  3323 |         const content=`
  3324 |           <section class="section-head"><h2>즉시 조치 큐</h2><span class="meta">색상은 원본 상태에서 파생 · 우선순위는 마감 여유로 계산</span></section>
  3325 |           <div class="queue-grid">
  3326 |             ${queueCard('danger','긴급','350호 입실 미준비','1건','미검수 · 촛불 1개','room-detail','입실 차단 해결','350')}
  3327 |             ${queueCard('warning','대기','관리자 미배정 작업','3건','시작 가능 시각이 지나 재배정이 필요한 작업','view-open-jobs','목록 보기')}
  3328 |             ${queueCard('warning','주의','마감 위험','2건','예상 소요시간 반영 시 여유 부족','view-open-jobs','목록 보기')}
  3329 |             ${queueCard('success','대기','검수 대상 목록','4건','전체 제출 검수가 필요합니다','cleaning-detail','639호 검수','639')}
  3330 |             ${queueCard('neutral','요청','담당 취소 요청','1건',state.cancelRequest==='requested'?'15분 이내 관리자 결정 필요':'처리 완료 · 타임라인 보존','cancel-review',state.cancelRequest==='requested'?'요청 처리':'결과 보기')}
```

### occurrence 11 · line 3319

```html
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
  3318 |       function queueCard(tone,badge,title,count,desc,action,label,id='') {
  3319 |         return `<article class="card queue-card ${tone}">${statusBadge(badge,tone==='danger'?'red':tone==='warning'?'amber':tone==='success'?'green':'neutral')}<h3>${title}</h3><div class="count">${count}</div><p>${desc}</p><button class="btn ${tone==='danger'?'btn-danger':'btn-outline'}" type="button" data-action="${action}" ${id?`data-id="${id}"`:''} ${isLocked()&&action!=='room-detail'?'disabled':''}>${label}</button></article>`;
  3320 |       }
  3321 | 
  3322 |       function renderAdminToday() {
  3323 |         const content=`
  3324 |           <section class="section-head"><h2>즉시 조치 큐</h2><span class="meta">색상은 원본 상태에서 파생 · 우선순위는 마감 여유로 계산</span></section>
  3325 |           <div class="queue-grid">
  3326 |             ${queueCard('danger','긴급','350호 입실 미준비','1건','미검수 · 촛불 1개','room-detail','입실 차단 해결','350')}
  3327 |             ${queueCard('warning','대기','관리자 미배정 작업','3건','시작 가능 시각이 지나 재배정이 필요한 작업','view-open-jobs','목록 보기')}
  3328 |             ${queueCard('warning','주의','마감 위험','2건','예상 소요시간 반영 시 여유 부족','view-open-jobs','목록 보기')}
  3329 |             ${queueCard('success','대기','검수 대상 목록','4건','전체 제출 검수가 필요합니다','cleaning-detail','639호 검수','639')}
  3330 |             ${queueCard('neutral','요청','담당 취소 요청','1건',state.cancelRequest==='requested'?'15분 이내 관리자 결정 필요':'처리 완료 · 타임라인 보존','cancel-review',state.cancelRequest==='requested'?'요청 처리':'결과 보기')}
  3331 |             ${queueCard('neutral','동기화','동기화·PIN·정산','2건','충돌 또는 확인 필요 사건','alerts','알림 보기')}
  3332 |           </div>
  3333 |           <div class="dashboard-layout">
  3334 |             <div><div class="section-head"><h2>객실 일별 현황</h2><span class="meta">총 7개 · 한국시간</span></div>${renderDateTools()}${renderRoomTable()}</div>
  3335 |             <aside class="rail" aria-label="보조 운영 큐">${renderDraftRail()}${renderInspectionRail()}${renderPayRail()}</aside>
  3336 |           </div>`;
  3337 |         return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);
  3338 |       }
  3339 | 
  3340 |       function renderScenario13Controls() {
  3341 |         if (state.scenario!==13) return '';
  3342 |         return `<section class="notice notice-info"><div style="flex:1"><strong>목록 상태 계약 데모</strong><br>상태를 바꾸면 정상 데이터·위험 행동 잠금 여부가 함께 변합니다.</div><label for="list-mode" class="sr-only">목록 상태</label><select id="list-mode" class="select-control" data-control="list-mode"><option value="loading" ${state.listMode==='loading'?'selected':''}>불러오는 중</option><option value="empty" ${state.listMode==='empty'?'selected':''}>진짜 0건</option><option value="filterEmpty" ${state.listMode==='filterEmpty'?'selected':''}>필터 결과 없음</option><option value="data" ${state.listMode==='data'?'selected':''}>데이터 있음</option><option value="stale" ${state.listMode==='stale'?'selected':''}>오래된 데이터·오류</option></select></section>`;
  3343 |       }
  3344 | 
  3345 |       function renderDraftRail() {
  3346 |         return `<section class="card"><div class="section-head"><h3>배정 준비 청소 작업</h3><span class="meta">${state.drafts.length}건</span></div><p class="cell-sub">근무일 전날 관리자 담당 배정을 기다립니다.</p><div class="rail-list">${state.drafts.length?state.drafts.map(d=>`<label class="rail-row"><input type="checkbox" data-control="draft" value="${d.id}" ${state.selectedDrafts.includes(d.id)?'checked':''} ${isLocked()?'disabled':''}><strong>${d.room}호 · ${d.kind}</strong><span>${d.created}</span></label>`).join(''):'<div class="state-panel" style="padding:12px"><p>배정 준비 작업 0건</p></div>'}</div>${button('내일 배정에서 보기','publish-selected','success',`${isLocked()?'disabled':''}`)}</section>`;
  3347 |       }
  3348 |       function renderInspectionRail() { return `<section class="card"><div class="section-head"><h3>검수 대상 목록</h3><span class="meta">4건</span></div><div class="rail-list"><div class="rail-row"><strong>639호 · 전체 제출 v2</strong><span>10:18</span></div><div class="rail-row"><strong>528호 · 업로드 완료</strong><span>10:14</span></div></div>${button('검수 대상 목록 보기','cleaning-detail','outline','data-id="639"')}</section>`; }
  3349 |       function renderPayRail() { const summary=paymentWeekSummaryFor();return `<section class="card"><div class="section-head"><h3>지난주 지급</h3>${statusBadge(summary.label,summary.tone)}</div><p class="cell-sub">메이드별 외부 전액 송금 완료를 각각 기록합니다. 앱은 송금하지 않습니다.</p>${button('지급 주차 상세','pay-detail','outline')}</section>`; }
  3350 | 
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
```

### occurrence 12 · line 3326

```html
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
  3318 |       function queueCard(tone,badge,title,count,desc,action,label,id='') {
  3319 |         return `<article class="card queue-card ${tone}">${statusBadge(badge,tone==='danger'?'red':tone==='warning'?'amber':tone==='success'?'green':'neutral')}<h3>${title}</h3><div class="count">${count}</div><p>${desc}</p><button class="btn ${tone==='danger'?'btn-danger':'btn-outline'}" type="button" data-action="${action}" ${id?`data-id="${id}"`:''} ${isLocked()&&action!=='room-detail'?'disabled':''}>${label}</button></article>`;
  3320 |       }
  3321 | 
  3322 |       function renderAdminToday() {
  3323 |         const content=`
  3324 |           <section class="section-head"><h2>즉시 조치 큐</h2><span class="meta">색상은 원본 상태에서 파생 · 우선순위는 마감 여유로 계산</span></section>
  3325 |           <div class="queue-grid">
  3326 |             ${queueCard('danger','긴급','350호 입실 미준비','1건','미검수 · 촛불 1개','room-detail','입실 차단 해결','350')}
  3327 |             ${queueCard('warning','대기','관리자 미배정 작업','3건','시작 가능 시각이 지나 재배정이 필요한 작업','view-open-jobs','목록 보기')}
  3328 |             ${queueCard('warning','주의','마감 위험','2건','예상 소요시간 반영 시 여유 부족','view-open-jobs','목록 보기')}
  3329 |             ${queueCard('success','대기','검수 대상 목록','4건','전체 제출 검수가 필요합니다','cleaning-detail','639호 검수','639')}
  3330 |             ${queueCard('neutral','요청','담당 취소 요청','1건',state.cancelRequest==='requested'?'15분 이내 관리자 결정 필요':'처리 완료 · 타임라인 보존','cancel-review',state.cancelRequest==='requested'?'요청 처리':'결과 보기')}
  3331 |             ${queueCard('neutral','동기화','동기화·PIN·정산','2건','충돌 또는 확인 필요 사건','alerts','알림 보기')}
  3332 |           </div>
  3333 |           <div class="dashboard-layout">
  3334 |             <div><div class="section-head"><h2>객실 일별 현황</h2><span class="meta">총 7개 · 한국시간</span></div>${renderDateTools()}${renderRoomTable()}</div>
  3335 |             <aside class="rail" aria-label="보조 운영 큐">${renderDraftRail()}${renderInspectionRail()}${renderPayRail()}</aside>
  3336 |           </div>`;
  3337 |         return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);
  3338 |       }
  3339 | 
  3340 |       function renderScenario13Controls() {
  3341 |         if (state.scenario!==13) return '';
  3342 |         return `<section class="notice notice-info"><div style="flex:1"><strong>목록 상태 계약 데모</strong><br>상태를 바꾸면 정상 데이터·위험 행동 잠금 여부가 함께 변합니다.</div><label for="list-mode" class="sr-only">목록 상태</label><select id="list-mode" class="select-control" data-control="list-mode"><option value="loading" ${state.listMode==='loading'?'selected':''}>불러오는 중</option><option value="empty" ${state.listMode==='empty'?'selected':''}>진짜 0건</option><option value="filterEmpty" ${state.listMode==='filterEmpty'?'selected':''}>필터 결과 없음</option><option value="data" ${state.listMode==='data'?'selected':''}>데이터 있음</option><option value="stale" ${state.listMode==='stale'?'selected':''}>오래된 데이터·오류</option></select></section>`;
  3343 |       }
  3344 | 
  3345 |       function renderDraftRail() {
  3346 |         return `<section class="card"><div class="section-head"><h3>배정 준비 청소 작업</h3><span class="meta">${state.drafts.length}건</span></div><p class="cell-sub">근무일 전날 관리자 담당 배정을 기다립니다.</p><div class="rail-list">${state.drafts.length?state.drafts.map(d=>`<label class="rail-row"><input type="checkbox" data-control="draft" value="${d.id}" ${state.selectedDrafts.includes(d.id)?'checked':''} ${isLocked()?'disabled':''}><strong>${d.room}호 · ${d.kind}</strong><span>${d.created}</span></label>`).join(''):'<div class="state-panel" style="padding:12px"><p>배정 준비 작업 0건</p></div>'}</div>${button('내일 배정에서 보기','publish-selected','success',`${isLocked()?'disabled':''}`)}</section>`;
  3347 |       }
  3348 |       function renderInspectionRail() { return `<section class="card"><div class="section-head"><h3>검수 대상 목록</h3><span class="meta">4건</span></div><div class="rail-list"><div class="rail-row"><strong>639호 · 전체 제출 v2</strong><span>10:18</span></div><div class="rail-row"><strong>528호 · 업로드 완료</strong><span>10:14</span></div></div>${button('검수 대상 목록 보기','cleaning-detail','outline','data-id="639"')}</section>`; }
  3349 |       function renderPayRail() { const summary=paymentWeekSummaryFor();return `<section class="card"><div class="section-head"><h3>지난주 지급</h3>${statusBadge(summary.label,summary.tone)}</div><p class="cell-sub">메이드별 외부 전액 송금 완료를 각각 기록합니다. 앱은 송금하지 않습니다.</p>${button('지급 주차 상세','pay-detail','outline')}</section>`; }
  3350 | 
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
  3354 | 
  3355 |       function renderMaids() {
  3356 |         const cards=MAIDS.map(m=>`<article class="card setting-card"><div class="avatar">${m.name[0]}</div><div style="min-width:0;flex:1"><h3>${m.name} · 데모</h3><p>${m.phone} · 관리자 배정 ${m.assigned}건<br>${m.id==='m1'&&state.maidStatus!=='active'?state.maidStatus:m.active}</p>${button('상세 보기','maid-detail','outline',`data-id="${m.id}"`)}</div></article>`).join('');
  3357 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>메이드 계정·업무 현황</h2><span class="meta">담당·실제 수행·제출·수익 귀속을 분리해 보존</span></div><div class="actions">${button('계정 추가','demo-info','primary')}</div></div><div class="settings-grid">${cards}</div>`;
  3358 |       }
  3359 | 
  3360 |       function renderAdminMore() {
```

## reservation modal: `function openReservation`

matches: 3

### occurrence 1 · line 3703

```html
  3687 |         rawCloseModal();
  3688 |         if(!hadModal||!isWireframeHistory(entry)||entry.layer!=='modal'||historyTraversalPending)return;
  3689 |         queueMicrotask(()=>{
  3690 |           if(historyTraversalPending||history.state?.modalEntryId!==modalEntryId)return;
  3691 |           const route=historyRouteSnapshot(),depth=Math.max(1,Number(entry.modalDepth)||1);
  3692 |           if(!completedModalSessions.some(session=>session.modalSessionId===entry.modalSessionId))completedModalSessions.push({modalSessionId:entry.modalSessionId,route});
  3693 |           if(isPinHistoryKind(entry.modalKind))clearPinModalSecret(entry.modalSessionId);
  3694 |           historyTraversalOverride=route;historyTraversalPending=true;history.go(-depth);
  3695 |         });
  3696 |       }
  3697 |       function adminOperatorText(message) {
  3698 |         if(state.role!=='admin')return String(message||'');
  3699 |         return String(message||'').replace(/PIN lease|\blease\b/gi,'PIN 조회').replace(/수익 ID/g,'청소 내역').replace(/수익 원장|청소 원장|주급 원장/g,'청소 내역').replace(/스냅샷/g,'기준').replace(/fingerprint/gi,'확인값').replace(/수행 회차/g,'청소 작업').replace(/회차/g,'작업').replace(/미종결/g,'미완료').replace(/종결/g,'조치 완료').replace(/재계산/g,'다시 확인').replace(/충돌을 조치 완료하고/g,'충돌 조치를 완료하고').replace(/충돌을 조치 완료하지/g,'충돌 조치를 완료하지').replace(/청소 작업가/g,'청소 작업이').replace(/청소 작업를/g,'청소 작업을').replace(/담당·청소 작업·PIN 조회 조치 완료/g,'담당 변경·진행 중 청소·PIN 조회 확인').replace(/비공개 퇴실 청소 초안|퇴실 청소 초안/g,'퇴실 청소').replace(/\bOPEN\b/g,'지급 대기').replace(/\bPAYING\b/g,'지급 진행').replace(/\bCHECK\b/g,'정산 확인 필요').replace(/\bPAID\b/g,'지급 완료');
  3700 |       }
  3701 |       function toast(message,type='') { const display=adminOperatorText(message),root=document.getElementById('toast-region');root.innerHTML=`<div class="toast ${type}" role="status">${esc(display)}</div>`;clearTimeout(toastTimer);toastTimer=setTimeout(()=>root.innerHTML='',3400);document.getElementById('assertive-live').textContent=display; }
  3702 | 
  3703 |       function openReservation() {
  3704 |         showModal({title:'예약 등록 · 데모',subtitle:'체크인과 체크아웃 일정을 입력하세요.',large:true,body:`<form id="reservation-form" class="form-grid"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control"><option>211호 · 데모</option></select></div><div class="field"><label for="res-customer">고객 이름 · 선택</label><input id="res-customer" class="input-control" value="홍길동 (데모)"><small>관리자 예약 상세에서만 표시</small></div><div class="field"><label for="res-checkin">예정 체크인</label><input id="res-checkin" class="input-control" type="datetime-local" value="2026-08-15T16:00"></div><div class="field"><label for="res-checkout">예정 체크아웃</label><input id="res-checkout" class="input-control" type="datetime-local" value="2026-08-16T11:00"></div><div class="field"><label for="early">얼리 체크인</label><select id="early" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div><div class="field"><label for="late">레이트 체크아웃</label><select id="late" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div></form>`,confirmLabel:'예약 저장',confirmAction:'save-reservation',historyKind:'reservation',historyPayload:{room:'211'}});
  3705 |       }
  3706 | 
  3707 |       function notificationCategoryLabel(category){return NOTIFICATION_CATEGORY_LABELS[category]||NOTIFICATION_CATEGORY_LABELS.general;}
  3708 |       function notificationFilterLabel(filter){return filter==='unread'?'안 읽음':filter==='action'?'처리 필요':'전체';}
  3709 |       function renderNotificationListMarkup({key=notificationAudienceKey(),filter=state.notificationFilter,includeActivity=true}={}){
  3710 |         ensureNotificationState();const bundles=notificationBundlesForKey(key),filtered=bundles.filter(bundle=>filter==='unread'?bundle.unread:filter==='action'?bundle.actionRequired:true),activity=(state.events||[]).filter(event=>!event.notify).slice(0,5),pushEnabled=notificationPushEnabled(key),filterButtons=[['all','전체'],['unread','안 읽음'],['action','처리 필요']].map(([value,label])=>`<button class="btn btn-ghost" type="button" data-action="notification-filter" data-filter="${value}" aria-pressed="${filter===value}">${label}${value==='unread'?` ${notificationUnreadCount(key)}`:''}</button>`).join('');
  3711 |         const cards=filtered.map(bundle=>{const event=bundle.latest,priority=event.priority==='urgent'?'urgent':'',status=event.status==='handled'&&!bundle.actionRequired?'처리 완료':bundle.actionRequired?'확인 필요':'안내',statusClass=status==='처리 완료'?'handled':bundle.actionRequired?'action':'',bundleText=bundle.bundleCount>1?` · 업데이트 ${bundle.bundleCount}건`:'';return `<button class="notification-card ${bundle.unread?'unread':''} ${priority}" type="button" data-action="notification-open" data-event-id="${esc(event.id)}" data-event-ids="${esc(bundle.eventIds.join(','))}" data-notification-card="${esc(event.category)}"><span class="notification-dot" aria-hidden="true"></span><span class="notification-copy"><span class="notification-title-line"><strong>${esc(event.title)}</strong>${bundle.bundleCount>1?`<span class="notification-chip">업데이트 ${bundle.bundleCount}건</span>`:''}</span><p>${esc(event.detail||'업무 상태가 변경되었습니다.')}</p><span class="notification-meta"><span>${esc(event.time)}</span><span>${esc(notificationCategoryLabel(event.category))}</span><span class="notification-chip ${statusClass}">${status}</span>${event.pushOptional?'<span>푸시 선택</span>':event.push?'<span>푸시 대상</span>':'<span>앱 내 기록</span>'}${bundleText}</span></span><span class="notification-cta">관련 화면 ${icon('chevronRight','icon-sm')}</span></button>`;}).join('');
  3712 |         const activityMarkup=includeActivity?`<section class="notification-activity"><h3>최근 활동 기록</h3><p>정상 청소 시작·사진 업로드·가능일 제출·관리자 직접 저장처럼 푸시하지 않는 활동입니다.</p><div class="notification-activity-list">${activity.length?activity.map(event=>`<div class="notification-activity-row"><span><strong>${esc(event.title)}</strong><span>${esc(event.detail||'')}</span></span><span>${esc(event.time||'')}</span></div>`).join(''):'<div class="notification-empty"><p>기록된 일반 활동이 없습니다.</p></div>'}</div></section>`:'';
  3713 |         return `<div class="notification-toolbar"><div class="notification-filter-group" role="group" aria-label="알림 필터">${filterButtons}</div><div class="notification-toolbar-actions"><button class="btn btn-outline" type="button" data-action="notification-mark-all-read" ${notificationUnreadCount(key)?'':'disabled'}>모두 읽음</button><button class="btn btn-outline" type="button" data-action="notification-toggle-push" aria-pressed="${pushEnabled}">${pushEnabled?'푸시 켜짐':'푸시 꺼짐'}</button></div></div><div class="notice notice-info notification-push-note"><div><strong>앱 내 알림은 항상 보존됩니다.</strong><br>푸시는 지금 확인하거나 행동해야 하는 상태 변경만 대상으로 하며, 이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다. 실제 백그라운드·모바일 푸시는 서비스 워커와 서버 발송 계층이 필요합니다.</div></div><div class="notification-list" data-notification-list="${esc(key)}" data-filter="${esc(filter)}">${cards||`<section class="notification-empty"><h3>${notificationFilterLabel(filter)} 알림이 없습니다</h3><p>새 상태 변경이 생기면 발생 시각 순서로 표시됩니다.</p></section>`}</div>${activityMarkup}`;
  3714 |       }
  3715 |       function openNotificationCenter(trigger=document.activeElement){const roleLabel=state.role==='admin'?'관리자 알림':'내 알림';showModal({title:roleLabel,subtitle:'업데이트를 시간순으로 보존하고 관련 업무 화면으로 바로 연결합니다.',large:true,trigger,body:renderNotificationListMarkup(),closeLabel:'닫기'});}
  3716 |       function openAlerts(){openNotificationCenter(document.activeElement);}
  3717 | 
  3718 |       function dispatchNotificationTarget(event){
  3719 |         const target=event?.target||{},action=target.action||'alerts';
  3720 |         if(action==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
  3721 |         if(action==='go-cleaning-assignment'){const day=target.data?.day==='tomorrow'?'tomorrow':'today';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
  3722 |         if(action==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
  3723 |         if(action==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  3724 |         if(action==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  3725 |         if(action==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  3726 |         const button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));button.remove();
  3727 |       }
  3728 |       function closeNotificationModalAndNavigate(notificationEvent){
  3729 |         const navigate=()=>requestAnimationFrame(()=>dispatchNotificationTarget(notificationEvent)),entry=history.state;
  3730 |         if(isWireframeHistory(entry)&&entry.layer==='modal'){
  3731 |           let completed=false;
  3732 |           const onPop=()=>{if(completed)return;completed=true;setTimeout(navigate,0);};
  3733 |           window.addEventListener('popstate',onPop,{once:true});
  3734 |           closeModal();
  3735 |           return;
  3736 |         }
  3737 |         rawCloseModal();navigate();
```

### occurrence 2 · line 6575

```html
  6559 |           return readOnly?`<div class="reservation-list-row reservation-history-row" aria-label="${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}">${content}</div>`:`<button class="reservation-list-row" type="button" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-week="${buckets.window.startDate}" ${existing?.id===reservation.id?'aria-current="true"':''}>${content}</button>`;
  6560 |         }).join('');
  6561 |         const list=rows?`<div class="reservation-list"><div class="reservation-list-head" aria-hidden="true"><span>예약 일정</span><span>숙박 · 인원</span><span>청소 상태</span><span></span></div>${rows}</div>`:`<p class="reservation-schedule-empty">이 주의 예약 기록이 없습니다.</p>`;
  6562 |         return `<div class="field field-full reservation-schedule"><section class="reservation-schedule-window" aria-label="${room.no}호 ${esc(weekRangeLabel(buckets.window.startDate))} 예약"><div class="reservation-week-nav"><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="-1" aria-label="이전 주 예약 보기">${icon('chevronLeft')}</button><button class="reservation-week-range" type="button" data-action="open-reservation-week-calendar" data-room="${room.no}" aria-haspopup="dialog" aria-label="${esc(weekRangeLabel(buckets.window.startDate,true))} 주차 선택, ${countLabel}"><strong>${esc(weekRangeLabel(buckets.window.startDate))}</strong><span>${countLabel}</span></button><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="1" aria-label="다음 주 예약 보기">${icon('chevronRight')}</button></div>${nextRegistration.weekPast?`<p class="reservation-week-note">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}${eligibilityNote}${list}</section></div>`;
  6563 |       }
  6564 |       function reservationModalConfig(roomNo='211',reservationId='',newDate='') {
  6565 |         const requestedCurrent=reservationId==='__current__',isNew=reservationId==='__new__'||requestedCurrent,requestedId=reservationId&&!isNew?reservationId:'',requested=requestedId?state.reservations.find(item=>item.id===requestedId)||null:null,stale=!!(requestedId&&!requested);
  6566 |         const room=ROOMS.find(item=>item.no===(requested?.room||String(roomNo)))||ROOMS.find(item=>item.no==='211')||ROOMS[0],selectedWeek=weekStartIso(state.reservationWeekStart||state.selectedDate),buckets=reservationBucketsForRoom(state,room.no,selectedWeek),requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id,requestedVisible=requested&&(requestedCurrentStay||requested.checkInAt<buckets.window.endAt&&requested.checkOutAt>buckets.window.startAt)?requested:null,editableInWeek=buckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),existing=requestedVisible||(!reservationId?editableInWeek[0]||null:null),weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),validNewDate=/^\d{4}-\d{2}-\d{2}$/.test(newDate||'')?newDate:'',roomSpecificNew=reservationId==='__new__'&&!!validNewDate,baseDefaultDate=selectedWeek===weekStartIso(state.selectedDate)?state.selectedDate:selectedWeek,defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no),guestCount=existing?reservationGuestCount(existing):guestPolicy.defaultGuestCount,cancelImpact=existing&&!readOnly?reservationCancellationImpact(existing):null,editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id,historyReservationId=currentEntry?'__current__':isNew?'__new__':existing?.id||'';
  6567 |         const roomOptions=(currentEntry||roomSpecificNew?[room]:ROOMS.filter(item=>item.no===room.no||!quickRoomBlockReason(item)&&(item.occupancy!=='occupied'||!!occupiedReservationEnd(item)))).map(item=>`<option value="${item.no}" ${item.no===room.no?'selected':''}>${item.no}호 · ${esc(ROOM_TYPES[item.type].name)} · ${esc(item.elevator||'미기재')}</option>`).join('');
  6568 |         const scheduleList=reservationWeekScheduleMarkup(room,existing,buckets),nextRegistration=reservationNextRegistrationState(room,existing,buckets);
  6569 |         const managementNotice=existing&&!readOnly?`<div class="field field-full"><div class="notice ${cancelImpact.blockedReason?'notice-warning':'notice-info'}"><div><strong>${cancelImpact.stayStarted?'현재 예약 수정 가능 · 예약 취소 불가':cancelImpact.blockedReason?'예약 취소 불가':'예약정보 수정 또는 취소'}</strong><br>${cancelImpact.stayStarted?'인원수와 일정은 위에서 수정할 수 있습니다. 실제 투숙 종료는 객실 상세의 지금 체크아웃으로 처리하세요.':cancelImpact.blockedReason?esc(cancelImpact.blockedReason):'날짜·시각은 위에서 수정하고, 예약을 없앨 때만 예약 취소를 누르세요.'}</div></div></div>`:'';
  6570 |         const occupiedNotice=!existing&&room.occupancy==='occupied'?`<div class="field field-full"><div class="notice ${currentEntry?'notice-warning':'notice-info'}"><div><strong>${currentEntry?'현재 투숙 정보 입력':'현재 투숙 중 · 다음 예약 등록'}</strong><br>${currentEntry?'실제 체크인과 예정 체크아웃, 숙박 인원을 확인해 입력하세요. 체크아웃을 저장한 뒤 다음 예약을 등록할 수 있습니다.':`${quickDateLabel(occupiedReservationEnd(room).slice(0,10))} ${occupiedReservationEnd(room).slice(11,16)} 체크아웃 이후의 겹치지 않는 일정만 등록할 수 있습니다.`}</div></div></div>`:'';
  6571 |         if(stale)return {room:room.no,reservationId:requestedId,title:`${room.no}호 예약을 다시 확인해 주세요`,subtitle:'열어 둔 예약이 이미 변경되었거나 취소되었습니다.',closeLabel:'닫기',large:true,body:`<div class="notice notice-warning"><div><strong>최신 예약 목록에서 다시 선택해 주세요.</strong></div></div>${scheduleList}`,confirmLabel:'',confirmAction:''};
  6572 |         if(readOnly)return {room:room.no,reservationId:historyReservationId,title:`${room.no}호 지난 예약 기록`,subtitle:`${weekRangeLabel(selectedWeek,true)} · 지난 기록은 수정하거나 취소할 수 없습니다.`,closeLabel:'닫기',large:true,body:scheduleList,confirmLabel:'',confirmAction:''};
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
  6590 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null;
  6591 |         if(!adminCanMutate()){toast('관리자 최신 온라인 상태에서만 예약을 취소할 수 있습니다.','error');return;}
  6592 |         if(!reservation||reservationFingerprint(reservation)!==expectedFingerprint){toast('예약 일정이 바뀌었거나 이미 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  6593 |         const impact=reservationCancellationImpact(reservation);if(impact.blockedReason){toast(impact.blockedReason,'error');return;}
  6594 |         const assignmentStatus=impact.manualTarget?`별도 등록한 현장 청소 요청 · 담당과 일정 유지`:impact.assignmentRecord?(impact.notifiedMaidId?`${maidName(impact.notifiedMaidId)} · 통보 완료 → 담당 취소 통보`:(impact.selectedMaidId?`${maidName(impact.selectedMaidId)} · 저장 전 선택 해제`:'미배정 상태 취소')):'청소 미배정',adjacentText=impact.adjacentChanges.length?impact.adjacentChanges.map(entry=>`${entry.reservation.room}호 ${quickRangeLabel(entry.reservation)} · 준비 마감 ${entry.before.deadline} → ${entry.after.deadline}`).join('<br>'):'변경되는 인접 예약 없음',impactFingerprint=reservationCancellationImpactFingerprint(reservation,impact);
  6595 |         showModal({title:`${reservation.room}호 예약을 취소할까요?`,subtitle:'청소 담당과 일정 영향을 확인한 뒤 취소하세요.',trigger,historyKind:'reservation-cancel',historyPayload:{room:reservation.room,reservationId:reservation.id},historyStack:true,closeLabel:'돌아가기',body:`<div class="info-grid"><div class="info-item"><span>취소 대상</span><strong>${reservation.room}호 · ${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</strong></div><div class="info-item"><span>예약 일정</span><strong>${esc(quickRangeLabel(reservation))}</strong></div><div class="info-item"><span>퇴실 청소 준비</span><strong>${impact.privateDrafts.length}건 · 함께 취소</strong></div><div class="info-item"><span>청소 담당 영향</span><strong>${esc(assignmentStatus)}</strong></div><div class="info-item"><span>인접 예약 청소 마감</span><strong>${adjacentText}</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>외부 예약은 취소되지 않습니다.</strong><br>외부 OTA/PMS에서도 예약 취소 여부를 따로 확인하세요.</div></div><div class="field" style="margin-top:14px"><label for="reservation-cancel-reason">예약 취소 사유</label><select id="reservation-cancel-reason" class="select-control" data-control="reservation-cancel-reason" required><option value="">사유를 선택하세요</option>${Object.entries(RESERVATION_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.</small></div>`,confirmLabel:'예약 취소 확정',confirmAction:'confirm-reservation-cancel',confirmVariant:'danger'});
  6596 |         const confirm=document.querySelector('[data-action="confirm-reservation-cancel"]');if(confirm){confirm.dataset.id=reservation.id;confirm.dataset.fingerprint=expectedFingerprint;confirm.dataset.impact=impactFingerprint;confirm.disabled=true;}
  6597 |       }
  6598 |       function openPaymentConfirm(weekStart,maidId,trigger=document.activeElement) {
  6599 |         const context=paymentContextFor(weekStart,maidId);
  6600 |         if(!context||context.meta.locked||!['OPEN','PAYING','CHECK'].includes(context.meta.status)){toast(context?.meta.status==='PAID'?'지급 완료 기록은 직접 취소하지 않고 정정·상계로 처리합니다.':'현재 이 메이드의 지급 상태를 변경할 수 없습니다.','error');return;}
  6601 |         const bindRecordAction=(action,expected=context.meta.status)=>{const target=document.querySelector(`[data-action="${action}"]`);if(target){target.dataset.week=context.cfg.start;target.dataset.maid=context.maid.id;target.dataset.expected=expected;target.dataset.record=paymentRecordFingerprint(context.record);}};
  6602 |         if(context.meta.status==='PAYING'){
  6603 |           showModal({title:`${context.maid.name} 송금 결과를 기록할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확인합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>실제 전액 송금이 끝난 경우에만 완료하세요.</strong><br>송금 여부가 불명확하면 확인 필요로 두고, 송금하지 않았다면 사유를 남겨 지급 대기로 돌립니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 확인 전이라 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금 여부 확인 필요','mark-payment-check','outline')}${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6604 |           bindRecordAction('confirm-finish-payment','PAYING');bindRecordAction('mark-payment-check','PAYING');bindRecordAction('confirm-payment-open-v2','PAYING');return;
  6605 |         }
  6606 |         if(context.meta.status==='CHECK'){
  6607 |           showModal({title:`${context.maid.name} 지급 결과를 다시 확인하세요`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 송금 결과를 확인해 상태를 정합니다.`,trigger,body:`<div class="notice notice-danger"><div><strong>외부 송금 결과를 확인한 뒤 한 가지 결과만 기록하세요.</strong><br>완료라면 이번 지급액과 청소 내역으로 지급 완료를 기록하고, 미송금이면 사유를 남겨 지급 대기로 돌아갑니다.</div></div><div class="info-grid"><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 오류를 확인해 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 재기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6608 |           bindRecordAction('confirm-finish-payment','CHECK');bindRecordAction('confirm-payment-open-v2','CHECK');return;
  6609 |         }
```

### occurrence 3 · line 6589

```html
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
  6590 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null;
  6591 |         if(!adminCanMutate()){toast('관리자 최신 온라인 상태에서만 예약을 취소할 수 있습니다.','error');return;}
  6592 |         if(!reservation||reservationFingerprint(reservation)!==expectedFingerprint){toast('예약 일정이 바뀌었거나 이미 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  6593 |         const impact=reservationCancellationImpact(reservation);if(impact.blockedReason){toast(impact.blockedReason,'error');return;}
  6594 |         const assignmentStatus=impact.manualTarget?`별도 등록한 현장 청소 요청 · 담당과 일정 유지`:impact.assignmentRecord?(impact.notifiedMaidId?`${maidName(impact.notifiedMaidId)} · 통보 완료 → 담당 취소 통보`:(impact.selectedMaidId?`${maidName(impact.selectedMaidId)} · 저장 전 선택 해제`:'미배정 상태 취소')):'청소 미배정',adjacentText=impact.adjacentChanges.length?impact.adjacentChanges.map(entry=>`${entry.reservation.room}호 ${quickRangeLabel(entry.reservation)} · 준비 마감 ${entry.before.deadline} → ${entry.after.deadline}`).join('<br>'):'변경되는 인접 예약 없음',impactFingerprint=reservationCancellationImpactFingerprint(reservation,impact);
  6595 |         showModal({title:`${reservation.room}호 예약을 취소할까요?`,subtitle:'청소 담당과 일정 영향을 확인한 뒤 취소하세요.',trigger,historyKind:'reservation-cancel',historyPayload:{room:reservation.room,reservationId:reservation.id},historyStack:true,closeLabel:'돌아가기',body:`<div class="info-grid"><div class="info-item"><span>취소 대상</span><strong>${reservation.room}호 · ${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</strong></div><div class="info-item"><span>예약 일정</span><strong>${esc(quickRangeLabel(reservation))}</strong></div><div class="info-item"><span>퇴실 청소 준비</span><strong>${impact.privateDrafts.length}건 · 함께 취소</strong></div><div class="info-item"><span>청소 담당 영향</span><strong>${esc(assignmentStatus)}</strong></div><div class="info-item"><span>인접 예약 청소 마감</span><strong>${adjacentText}</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>외부 예약은 취소되지 않습니다.</strong><br>외부 OTA/PMS에서도 예약 취소 여부를 따로 확인하세요.</div></div><div class="field" style="margin-top:14px"><label for="reservation-cancel-reason">예약 취소 사유</label><select id="reservation-cancel-reason" class="select-control" data-control="reservation-cancel-reason" required><option value="">사유를 선택하세요</option>${Object.entries(RESERVATION_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.</small></div>`,confirmLabel:'예약 취소 확정',confirmAction:'confirm-reservation-cancel',confirmVariant:'danger'});
  6596 |         const confirm=document.querySelector('[data-action="confirm-reservation-cancel"]');if(confirm){confirm.dataset.id=reservation.id;confirm.dataset.fingerprint=expectedFingerprint;confirm.dataset.impact=impactFingerprint;confirm.disabled=true;}
  6597 |       }
  6598 |       function openPaymentConfirm(weekStart,maidId,trigger=document.activeElement) {
  6599 |         const context=paymentContextFor(weekStart,maidId);
  6600 |         if(!context||context.meta.locked||!['OPEN','PAYING','CHECK'].includes(context.meta.status)){toast(context?.meta.status==='PAID'?'지급 완료 기록은 직접 취소하지 않고 정정·상계로 처리합니다.':'현재 이 메이드의 지급 상태를 변경할 수 없습니다.','error');return;}
  6601 |         const bindRecordAction=(action,expected=context.meta.status)=>{const target=document.querySelector(`[data-action="${action}"]`);if(target){target.dataset.week=context.cfg.start;target.dataset.maid=context.maid.id;target.dataset.expected=expected;target.dataset.record=paymentRecordFingerprint(context.record);}};
  6602 |         if(context.meta.status==='PAYING'){
  6603 |           showModal({title:`${context.maid.name} 송금 결과를 기록할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확인합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>실제 전액 송금이 끝난 경우에만 완료하세요.</strong><br>송금 여부가 불명확하면 확인 필요로 두고, 송금하지 않았다면 사유를 남겨 지급 대기로 돌립니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 확인 전이라 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금 여부 확인 필요','mark-payment-check','outline')}${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6604 |           bindRecordAction('confirm-finish-payment','PAYING');bindRecordAction('mark-payment-check','PAYING');bindRecordAction('confirm-payment-open-v2','PAYING');return;
  6605 |         }
  6606 |         if(context.meta.status==='CHECK'){
  6607 |           showModal({title:`${context.maid.name} 지급 결과를 다시 확인하세요`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 송금 결과를 확인해 상태를 정합니다.`,trigger,body:`<div class="notice notice-danger"><div><strong>외부 송금 결과를 확인한 뒤 한 가지 결과만 기록하세요.</strong><br>완료라면 이번 지급액과 청소 내역으로 지급 완료를 기록하고, 미송금이면 사유를 남겨 지급 대기로 돌아갑니다.</div></div><div class="info-grid"><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 오류를 확인해 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 재기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6608 |           bindRecordAction('confirm-finish-payment','CHECK');bindRecordAction('confirm-payment-open-v2','CHECK');return;
  6609 |         }
  6610 |         const confirmedTasks=context.tasks.filter(task=>task.stage==='confirmed'),bombTasks=confirmedTasks.filter(task=>task.bombBonus>0),bombText=bombTasks.length?bombTasks.map(task=>`${task.room} · ${money(task.baseAmount)} + ${money(task.bombBonus)} = ${money(task.amount)}`).join('<br>'):'해당 없음';
  6611 |         showModal({title:`${context.maid.name} 지급 진행을 시작할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확정합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong><br>외부 송금을 마친 뒤 같은 메이드 스위치에서 지급 완료를 기록하세요. 다른 메이드 상태는 바뀌지 않습니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>지급 주차</span><strong>${weekRangeLabel(context.cfg.start)}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.totals.confirmed)} · 데모</strong></div><div class="info-item"><span>확정 청소</span><strong>${confirmedTasks.length}건</strong></div><div class="info-item field-full"><span>폭탄방 포함 내역</span><strong>${bombText}</strong></div></div>`,confirmLabel:'지급 진행 시작',confirmAction:'confirm-toggle-payment',confirmVariant:'primary'});
  6612 |         const confirm=document.querySelector('[data-action="confirm-toggle-payment"]');if(confirm){confirm.dataset.week=context.cfg.start;confirm.dataset.maid=context.maid.id;confirm.dataset.expected='OPEN';confirm.dataset.amount=String(context.totals.confirmed);confirm.dataset.tasks=paymentTaskFingerprint(context);}
  6613 |       }
  6614 | 
  6615 |       function timeMinutes(t){const [h,m]=String(t).split(':').map(Number);return h*60+m;}
  6616 | 
  6617 |       function maskPin() {
  6618 |         clearTimeout(pinTimer);pinTimer=null;state.pinVisibleRoom=null;state.pinVisibleUntil=0;activePinRevealSecret=null;clearAllPinModalSecrets(true);
  6619 |       }
  6620 |       function revealPin(no) {
  6621 |         maskPin();const expiresAt=Date.now()+30000;state.pinVisibleRoom=no;state.pinVisibleUntil=expiresAt;activePinRevealSecret={room:no,value:readProtectedPin(no),expiresAt};
  6622 |         appendEvent(`${no}호 PIN 조회`,'원문 없이 조회 사용자·시각만 감사 기록',{maidIds:state.role==='maid'?[signedInMaidId()]:[],roomId:no,attemptId:currentAttemptId(no)||null});render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${no}"] [data-action="pin-hide"]`)?.focus());
  6623 |         pinTimer=setTimeout(()=>{if(state.pinVisibleRoom===no){maskPin();render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${no}"] [data-action="pin-show"]`)?.focus());toast('30초가 지나 객실 PIN을 다시 가렸습니다.');}},30000);
```

## reservation form: `reservation-form`

matches: 2

### occurrence 1 · line 3704

```html
  3688 |         if(!hadModal||!isWireframeHistory(entry)||entry.layer!=='modal'||historyTraversalPending)return;
  3689 |         queueMicrotask(()=>{
  3690 |           if(historyTraversalPending||history.state?.modalEntryId!==modalEntryId)return;
  3691 |           const route=historyRouteSnapshot(),depth=Math.max(1,Number(entry.modalDepth)||1);
  3692 |           if(!completedModalSessions.some(session=>session.modalSessionId===entry.modalSessionId))completedModalSessions.push({modalSessionId:entry.modalSessionId,route});
  3693 |           if(isPinHistoryKind(entry.modalKind))clearPinModalSecret(entry.modalSessionId);
  3694 |           historyTraversalOverride=route;historyTraversalPending=true;history.go(-depth);
  3695 |         });
  3696 |       }
  3697 |       function adminOperatorText(message) {
  3698 |         if(state.role!=='admin')return String(message||'');
  3699 |         return String(message||'').replace(/PIN lease|\blease\b/gi,'PIN 조회').replace(/수익 ID/g,'청소 내역').replace(/수익 원장|청소 원장|주급 원장/g,'청소 내역').replace(/스냅샷/g,'기준').replace(/fingerprint/gi,'확인값').replace(/수행 회차/g,'청소 작업').replace(/회차/g,'작업').replace(/미종결/g,'미완료').replace(/종결/g,'조치 완료').replace(/재계산/g,'다시 확인').replace(/충돌을 조치 완료하고/g,'충돌 조치를 완료하고').replace(/충돌을 조치 완료하지/g,'충돌 조치를 완료하지').replace(/청소 작업가/g,'청소 작업이').replace(/청소 작업를/g,'청소 작업을').replace(/담당·청소 작업·PIN 조회 조치 완료/g,'담당 변경·진행 중 청소·PIN 조회 확인').replace(/비공개 퇴실 청소 초안|퇴실 청소 초안/g,'퇴실 청소').replace(/\bOPEN\b/g,'지급 대기').replace(/\bPAYING\b/g,'지급 진행').replace(/\bCHECK\b/g,'정산 확인 필요').replace(/\bPAID\b/g,'지급 완료');
  3700 |       }
  3701 |       function toast(message,type='') { const display=adminOperatorText(message),root=document.getElementById('toast-region');root.innerHTML=`<div class="toast ${type}" role="status">${esc(display)}</div>`;clearTimeout(toastTimer);toastTimer=setTimeout(()=>root.innerHTML='',3400);document.getElementById('assertive-live').textContent=display; }
  3702 | 
  3703 |       function openReservation() {
  3704 |         showModal({title:'예약 등록 · 데모',subtitle:'체크인과 체크아웃 일정을 입력하세요.',large:true,body:`<form id="reservation-form" class="form-grid"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control"><option>211호 · 데모</option></select></div><div class="field"><label for="res-customer">고객 이름 · 선택</label><input id="res-customer" class="input-control" value="홍길동 (데모)"><small>관리자 예약 상세에서만 표시</small></div><div class="field"><label for="res-checkin">예정 체크인</label><input id="res-checkin" class="input-control" type="datetime-local" value="2026-08-15T16:00"></div><div class="field"><label for="res-checkout">예정 체크아웃</label><input id="res-checkout" class="input-control" type="datetime-local" value="2026-08-16T11:00"></div><div class="field"><label for="early">얼리 체크인</label><select id="early" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div><div class="field"><label for="late">레이트 체크아웃</label><select id="late" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div></form>`,confirmLabel:'예약 저장',confirmAction:'save-reservation',historyKind:'reservation',historyPayload:{room:'211'}});
  3705 |       }
  3706 | 
  3707 |       function notificationCategoryLabel(category){return NOTIFICATION_CATEGORY_LABELS[category]||NOTIFICATION_CATEGORY_LABELS.general;}
  3708 |       function notificationFilterLabel(filter){return filter==='unread'?'안 읽음':filter==='action'?'처리 필요':'전체';}
  3709 |       function renderNotificationListMarkup({key=notificationAudienceKey(),filter=state.notificationFilter,includeActivity=true}={}){
  3710 |         ensureNotificationState();const bundles=notificationBundlesForKey(key),filtered=bundles.filter(bundle=>filter==='unread'?bundle.unread:filter==='action'?bundle.actionRequired:true),activity=(state.events||[]).filter(event=>!event.notify).slice(0,5),pushEnabled=notificationPushEnabled(key),filterButtons=[['all','전체'],['unread','안 읽음'],['action','처리 필요']].map(([value,label])=>`<button class="btn btn-ghost" type="button" data-action="notification-filter" data-filter="${value}" aria-pressed="${filter===value}">${label}${value==='unread'?` ${notificationUnreadCount(key)}`:''}</button>`).join('');
  3711 |         const cards=filtered.map(bundle=>{const event=bundle.latest,priority=event.priority==='urgent'?'urgent':'',status=event.status==='handled'&&!bundle.actionRequired?'처리 완료':bundle.actionRequired?'확인 필요':'안내',statusClass=status==='처리 완료'?'handled':bundle.actionRequired?'action':'',bundleText=bundle.bundleCount>1?` · 업데이트 ${bundle.bundleCount}건`:'';return `<button class="notification-card ${bundle.unread?'unread':''} ${priority}" type="button" data-action="notification-open" data-event-id="${esc(event.id)}" data-event-ids="${esc(bundle.eventIds.join(','))}" data-notification-card="${esc(event.category)}"><span class="notification-dot" aria-hidden="true"></span><span class="notification-copy"><span class="notification-title-line"><strong>${esc(event.title)}</strong>${bundle.bundleCount>1?`<span class="notification-chip">업데이트 ${bundle.bundleCount}건</span>`:''}</span><p>${esc(event.detail||'업무 상태가 변경되었습니다.')}</p><span class="notification-meta"><span>${esc(event.time)}</span><span>${esc(notificationCategoryLabel(event.category))}</span><span class="notification-chip ${statusClass}">${status}</span>${event.pushOptional?'<span>푸시 선택</span>':event.push?'<span>푸시 대상</span>':'<span>앱 내 기록</span>'}${bundleText}</span></span><span class="notification-cta">관련 화면 ${icon('chevronRight','icon-sm')}</span></button>`;}).join('');
  3712 |         const activityMarkup=includeActivity?`<section class="notification-activity"><h3>최근 활동 기록</h3><p>정상 청소 시작·사진 업로드·가능일 제출·관리자 직접 저장처럼 푸시하지 않는 활동입니다.</p><div class="notification-activity-list">${activity.length?activity.map(event=>`<div class="notification-activity-row"><span><strong>${esc(event.title)}</strong><span>${esc(event.detail||'')}</span></span><span>${esc(event.time||'')}</span></div>`).join(''):'<div class="notification-empty"><p>기록된 일반 활동이 없습니다.</p></div>'}</div></section>`:'';
  3713 |         return `<div class="notification-toolbar"><div class="notification-filter-group" role="group" aria-label="알림 필터">${filterButtons}</div><div class="notification-toolbar-actions"><button class="btn btn-outline" type="button" data-action="notification-mark-all-read" ${notificationUnreadCount(key)?'':'disabled'}>모두 읽음</button><button class="btn btn-outline" type="button" data-action="notification-toggle-push" aria-pressed="${pushEnabled}">${pushEnabled?'푸시 켜짐':'푸시 꺼짐'}</button></div></div><div class="notice notice-info notification-push-note"><div><strong>앱 내 알림은 항상 보존됩니다.</strong><br>푸시는 지금 확인하거나 행동해야 하는 상태 변경만 대상으로 하며, 이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다. 실제 백그라운드·모바일 푸시는 서비스 워커와 서버 발송 계층이 필요합니다.</div></div><div class="notification-list" data-notification-list="${esc(key)}" data-filter="${esc(filter)}">${cards||`<section class="notification-empty"><h3>${notificationFilterLabel(filter)} 알림이 없습니다</h3><p>새 상태 변경이 생기면 발생 시각 순서로 표시됩니다.</p></section>`}</div>${activityMarkup}`;
  3714 |       }
  3715 |       function openNotificationCenter(trigger=document.activeElement){const roleLabel=state.role==='admin'?'관리자 알림':'내 알림';showModal({title:roleLabel,subtitle:'업데이트를 시간순으로 보존하고 관련 업무 화면으로 바로 연결합니다.',large:true,trigger,body:renderNotificationListMarkup(),closeLabel:'닫기'});}
  3716 |       function openAlerts(){openNotificationCenter(document.activeElement);}
  3717 | 
  3718 |       function dispatchNotificationTarget(event){
  3719 |         const target=event?.target||{},action=target.action||'alerts';
  3720 |         if(action==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
  3721 |         if(action==='go-cleaning-assignment'){const day=target.data?.day==='tomorrow'?'tomorrow':'today';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
  3722 |         if(action==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
  3723 |         if(action==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  3724 |         if(action==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  3725 |         if(action==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  3726 |         const button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));button.remove();
  3727 |       }
  3728 |       function closeNotificationModalAndNavigate(notificationEvent){
  3729 |         const navigate=()=>requestAnimationFrame(()=>dispatchNotificationTarget(notificationEvent)),entry=history.state;
  3730 |         if(isWireframeHistory(entry)&&entry.layer==='modal'){
  3731 |           let completed=false;
  3732 |           const onPop=()=>{if(completed)return;completed=true;setTimeout(navigate,0);};
  3733 |           window.addEventListener('popstate',onPop,{once:true});
  3734 |           closeModal();
  3735 |           return;
  3736 |         }
  3737 |         rawCloseModal();navigate();
  3738 |       }
```

### occurrence 2 · line 6573

```html
  6557 |         const nextRegistration=reservationNextRegistrationState(room,existing,buckets),records=buckets.weekRecords,countLabel=nextRegistration.weekPast?`기록 ${records.length}건`:`예약 ${records.filter(item=>item.status==='active'&&!reservationRecordIsPast(item)).length}건`,eligibilityNote=existing&&!nextRegistration.weekPast&&room.occupancy==='occupied'&&(!nextRegistration.occupiedEnd||nextRegistration.needsCheckoutUpdate)?`<p class="reservation-week-note">${icon('alert','icon-sm')}${nextRegistration.needsCheckoutUpdate?'예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리하세요.':'현재 투숙의 체크아웃을 먼저 입력하세요.'}</p>`:'',rows=records.map(reservation=>{
  6558 |           const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정'),content=`<span class="reservation-list-period"><strong>${esc(quickRangeLabel(reservation))}</strong></span><span class="reservation-list-meta">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span><span class="reservation-list-status">${esc(status)}</span><span class="reservation-list-arrow">${readOnly?'':icon('chevronRight','icon-sm')}</span>`;
  6559 |           return readOnly?`<div class="reservation-list-row reservation-history-row" aria-label="${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}">${content}</div>`:`<button class="reservation-list-row" type="button" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-week="${buckets.window.startDate}" ${existing?.id===reservation.id?'aria-current="true"':''}>${content}</button>`;
  6560 |         }).join('');
  6561 |         const list=rows?`<div class="reservation-list"><div class="reservation-list-head" aria-hidden="true"><span>예약 일정</span><span>숙박 · 인원</span><span>청소 상태</span><span></span></div>${rows}</div>`:`<p class="reservation-schedule-empty">이 주의 예약 기록이 없습니다.</p>`;
  6562 |         return `<div class="field field-full reservation-schedule"><section class="reservation-schedule-window" aria-label="${room.no}호 ${esc(weekRangeLabel(buckets.window.startDate))} 예약"><div class="reservation-week-nav"><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="-1" aria-label="이전 주 예약 보기">${icon('chevronLeft')}</button><button class="reservation-week-range" type="button" data-action="open-reservation-week-calendar" data-room="${room.no}" aria-haspopup="dialog" aria-label="${esc(weekRangeLabel(buckets.window.startDate,true))} 주차 선택, ${countLabel}"><strong>${esc(weekRangeLabel(buckets.window.startDate))}</strong><span>${countLabel}</span></button><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="1" aria-label="다음 주 예약 보기">${icon('chevronRight')}</button></div>${nextRegistration.weekPast?`<p class="reservation-week-note">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}${eligibilityNote}${list}</section></div>`;
  6563 |       }
  6564 |       function reservationModalConfig(roomNo='211',reservationId='',newDate='') {
  6565 |         const requestedCurrent=reservationId==='__current__',isNew=reservationId==='__new__'||requestedCurrent,requestedId=reservationId&&!isNew?reservationId:'',requested=requestedId?state.reservations.find(item=>item.id===requestedId)||null:null,stale=!!(requestedId&&!requested);
  6566 |         const room=ROOMS.find(item=>item.no===(requested?.room||String(roomNo)))||ROOMS.find(item=>item.no==='211')||ROOMS[0],selectedWeek=weekStartIso(state.reservationWeekStart||state.selectedDate),buckets=reservationBucketsForRoom(state,room.no,selectedWeek),requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id,requestedVisible=requested&&(requestedCurrentStay||requested.checkInAt<buckets.window.endAt&&requested.checkOutAt>buckets.window.startAt)?requested:null,editableInWeek=buckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),existing=requestedVisible||(!reservationId?editableInWeek[0]||null:null),weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),validNewDate=/^\d{4}-\d{2}-\d{2}$/.test(newDate||'')?newDate:'',roomSpecificNew=reservationId==='__new__'&&!!validNewDate,baseDefaultDate=selectedWeek===weekStartIso(state.selectedDate)?state.selectedDate:selectedWeek,defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no),guestCount=existing?reservationGuestCount(existing):guestPolicy.defaultGuestCount,cancelImpact=existing&&!readOnly?reservationCancellationImpact(existing):null,editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id,historyReservationId=currentEntry?'__current__':isNew?'__new__':existing?.id||'';
  6567 |         const roomOptions=(currentEntry||roomSpecificNew?[room]:ROOMS.filter(item=>item.no===room.no||!quickRoomBlockReason(item)&&(item.occupancy!=='occupied'||!!occupiedReservationEnd(item)))).map(item=>`<option value="${item.no}" ${item.no===room.no?'selected':''}>${item.no}호 · ${esc(ROOM_TYPES[item.type].name)} · ${esc(item.elevator||'미기재')}</option>`).join('');
  6568 |         const scheduleList=reservationWeekScheduleMarkup(room,existing,buckets),nextRegistration=reservationNextRegistrationState(room,existing,buckets);
  6569 |         const managementNotice=existing&&!readOnly?`<div class="field field-full"><div class="notice ${cancelImpact.blockedReason?'notice-warning':'notice-info'}"><div><strong>${cancelImpact.stayStarted?'현재 예약 수정 가능 · 예약 취소 불가':cancelImpact.blockedReason?'예약 취소 불가':'예약정보 수정 또는 취소'}</strong><br>${cancelImpact.stayStarted?'인원수와 일정은 위에서 수정할 수 있습니다. 실제 투숙 종료는 객실 상세의 지금 체크아웃으로 처리하세요.':cancelImpact.blockedReason?esc(cancelImpact.blockedReason):'날짜·시각은 위에서 수정하고, 예약을 없앨 때만 예약 취소를 누르세요.'}</div></div></div>`:'';
  6570 |         const occupiedNotice=!existing&&room.occupancy==='occupied'?`<div class="field field-full"><div class="notice ${currentEntry?'notice-warning':'notice-info'}"><div><strong>${currentEntry?'현재 투숙 정보 입력':'현재 투숙 중 · 다음 예약 등록'}</strong><br>${currentEntry?'실제 체크인과 예정 체크아웃, 숙박 인원을 확인해 입력하세요. 체크아웃을 저장한 뒤 다음 예약을 등록할 수 있습니다.':`${quickDateLabel(occupiedReservationEnd(room).slice(0,10))} ${occupiedReservationEnd(room).slice(11,16)} 체크아웃 이후의 겹치지 않는 일정만 등록할 수 있습니다.`}</div></div></div>`:'';
  6571 |         if(stale)return {room:room.no,reservationId:requestedId,title:`${room.no}호 예약을 다시 확인해 주세요`,subtitle:'열어 둔 예약이 이미 변경되었거나 취소되었습니다.',closeLabel:'닫기',large:true,body:`<div class="notice notice-warning"><div><strong>최신 예약 목록에서 다시 선택해 주세요.</strong></div></div>${scheduleList}`,confirmLabel:'',confirmAction:''};
  6572 |         if(readOnly)return {room:room.no,reservationId:historyReservationId,title:`${room.no}호 지난 예약 기록`,subtitle:`${weekRangeLabel(selectedWeek,true)} · 지난 기록은 수정하거나 취소할 수 없습니다.`,closeLabel:'닫기',large:true,body:scheduleList,confirmLabel:'',confirmAction:''};
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
  6590 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null;
  6591 |         if(!adminCanMutate()){toast('관리자 최신 온라인 상태에서만 예약을 취소할 수 있습니다.','error');return;}
  6592 |         if(!reservation||reservationFingerprint(reservation)!==expectedFingerprint){toast('예약 일정이 바뀌었거나 이미 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  6593 |         const impact=reservationCancellationImpact(reservation);if(impact.blockedReason){toast(impact.blockedReason,'error');return;}
  6594 |         const assignmentStatus=impact.manualTarget?`별도 등록한 현장 청소 요청 · 담당과 일정 유지`:impact.assignmentRecord?(impact.notifiedMaidId?`${maidName(impact.notifiedMaidId)} · 통보 완료 → 담당 취소 통보`:(impact.selectedMaidId?`${maidName(impact.selectedMaidId)} · 저장 전 선택 해제`:'미배정 상태 취소')):'청소 미배정',adjacentText=impact.adjacentChanges.length?impact.adjacentChanges.map(entry=>`${entry.reservation.room}호 ${quickRangeLabel(entry.reservation)} · 준비 마감 ${entry.before.deadline} → ${entry.after.deadline}`).join('<br>'):'변경되는 인접 예약 없음',impactFingerprint=reservationCancellationImpactFingerprint(reservation,impact);
  6595 |         showModal({title:`${reservation.room}호 예약을 취소할까요?`,subtitle:'청소 담당과 일정 영향을 확인한 뒤 취소하세요.',trigger,historyKind:'reservation-cancel',historyPayload:{room:reservation.room,reservationId:reservation.id},historyStack:true,closeLabel:'돌아가기',body:`<div class="info-grid"><div class="info-item"><span>취소 대상</span><strong>${reservation.room}호 · ${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</strong></div><div class="info-item"><span>예약 일정</span><strong>${esc(quickRangeLabel(reservation))}</strong></div><div class="info-item"><span>퇴실 청소 준비</span><strong>${impact.privateDrafts.length}건 · 함께 취소</strong></div><div class="info-item"><span>청소 담당 영향</span><strong>${esc(assignmentStatus)}</strong></div><div class="info-item"><span>인접 예약 청소 마감</span><strong>${adjacentText}</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>외부 예약은 취소되지 않습니다.</strong><br>외부 OTA/PMS에서도 예약 취소 여부를 따로 확인하세요.</div></div><div class="field" style="margin-top:14px"><label for="reservation-cancel-reason">예약 취소 사유</label><select id="reservation-cancel-reason" class="select-control" data-control="reservation-cancel-reason" required><option value="">사유를 선택하세요</option>${Object.entries(RESERVATION_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.</small></div>`,confirmLabel:'예약 취소 확정',confirmAction:'confirm-reservation-cancel',confirmVariant:'danger'});
  6596 |         const confirm=document.querySelector('[data-action="confirm-reservation-cancel"]');if(confirm){confirm.dataset.id=reservation.id;confirm.dataset.fingerprint=expectedFingerprint;confirm.dataset.impact=impactFingerprint;confirm.disabled=true;}
  6597 |       }
  6598 |       function openPaymentConfirm(weekStart,maidId,trigger=document.activeElement) {
  6599 |         const context=paymentContextFor(weekStart,maidId);
  6600 |         if(!context||context.meta.locked||!['OPEN','PAYING','CHECK'].includes(context.meta.status)){toast(context?.meta.status==='PAID'?'지급 완료 기록은 직접 취소하지 않고 정정·상계로 처리합니다.':'현재 이 메이드의 지급 상태를 변경할 수 없습니다.','error');return;}
  6601 |         const bindRecordAction=(action,expected=context.meta.status)=>{const target=document.querySelector(`[data-action="${action}"]`);if(target){target.dataset.week=context.cfg.start;target.dataset.maid=context.maid.id;target.dataset.expected=expected;target.dataset.record=paymentRecordFingerprint(context.record);}};
  6602 |         if(context.meta.status==='PAYING'){
  6603 |           showModal({title:`${context.maid.name} 송금 결과를 기록할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확인합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>실제 전액 송금이 끝난 경우에만 완료하세요.</strong><br>송금 여부가 불명확하면 확인 필요로 두고, 송금하지 않았다면 사유를 남겨 지급 대기로 돌립니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 확인 전이라 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금 여부 확인 필요','mark-payment-check','outline')}${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6604 |           bindRecordAction('confirm-finish-payment','PAYING');bindRecordAction('mark-payment-check','PAYING');bindRecordAction('confirm-payment-open-v2','PAYING');return;
  6605 |         }
  6606 |         if(context.meta.status==='CHECK'){
  6607 |           showModal({title:`${context.maid.name} 지급 결과를 다시 확인하세요`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 송금 결과를 확인해 상태를 정합니다.`,trigger,body:`<div class="notice notice-danger"><div><strong>외부 송금 결과를 확인한 뒤 한 가지 결과만 기록하세요.</strong><br>완료라면 이번 지급액과 청소 내역으로 지급 완료를 기록하고, 미송금이면 사유를 남겨 지급 대기로 돌아갑니다.</div></div><div class="info-grid"><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 오류를 확인해 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 재기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
```

## reservation save: `save-reservation`

matches: 7

### occurrence 1 · line 3704

```html
  3688 |         if(!hadModal||!isWireframeHistory(entry)||entry.layer!=='modal'||historyTraversalPending)return;
  3689 |         queueMicrotask(()=>{
  3690 |           if(historyTraversalPending||history.state?.modalEntryId!==modalEntryId)return;
  3691 |           const route=historyRouteSnapshot(),depth=Math.max(1,Number(entry.modalDepth)||1);
  3692 |           if(!completedModalSessions.some(session=>session.modalSessionId===entry.modalSessionId))completedModalSessions.push({modalSessionId:entry.modalSessionId,route});
  3693 |           if(isPinHistoryKind(entry.modalKind))clearPinModalSecret(entry.modalSessionId);
  3694 |           historyTraversalOverride=route;historyTraversalPending=true;history.go(-depth);
  3695 |         });
  3696 |       }
  3697 |       function adminOperatorText(message) {
  3698 |         if(state.role!=='admin')return String(message||'');
  3699 |         return String(message||'').replace(/PIN lease|\blease\b/gi,'PIN 조회').replace(/수익 ID/g,'청소 내역').replace(/수익 원장|청소 원장|주급 원장/g,'청소 내역').replace(/스냅샷/g,'기준').replace(/fingerprint/gi,'확인값').replace(/수행 회차/g,'청소 작업').replace(/회차/g,'작업').replace(/미종결/g,'미완료').replace(/종결/g,'조치 완료').replace(/재계산/g,'다시 확인').replace(/충돌을 조치 완료하고/g,'충돌 조치를 완료하고').replace(/충돌을 조치 완료하지/g,'충돌 조치를 완료하지').replace(/청소 작업가/g,'청소 작업이').replace(/청소 작업를/g,'청소 작업을').replace(/담당·청소 작업·PIN 조회 조치 완료/g,'담당 변경·진행 중 청소·PIN 조회 확인').replace(/비공개 퇴실 청소 초안|퇴실 청소 초안/g,'퇴실 청소').replace(/\bOPEN\b/g,'지급 대기').replace(/\bPAYING\b/g,'지급 진행').replace(/\bCHECK\b/g,'정산 확인 필요').replace(/\bPAID\b/g,'지급 완료');
  3700 |       }
  3701 |       function toast(message,type='') { const display=adminOperatorText(message),root=document.getElementById('toast-region');root.innerHTML=`<div class="toast ${type}" role="status">${esc(display)}</div>`;clearTimeout(toastTimer);toastTimer=setTimeout(()=>root.innerHTML='',3400);document.getElementById('assertive-live').textContent=display; }
  3702 | 
  3703 |       function openReservation() {
  3704 |         showModal({title:'예약 등록 · 데모',subtitle:'체크인과 체크아웃 일정을 입력하세요.',large:true,body:`<form id="reservation-form" class="form-grid"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control"><option>211호 · 데모</option></select></div><div class="field"><label for="res-customer">고객 이름 · 선택</label><input id="res-customer" class="input-control" value="홍길동 (데모)"><small>관리자 예약 상세에서만 표시</small></div><div class="field"><label for="res-checkin">예정 체크인</label><input id="res-checkin" class="input-control" type="datetime-local" value="2026-08-15T16:00"></div><div class="field"><label for="res-checkout">예정 체크아웃</label><input id="res-checkout" class="input-control" type="datetime-local" value="2026-08-16T11:00"></div><div class="field"><label for="early">얼리 체크인</label><select id="early" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div><div class="field"><label for="late">레이트 체크아웃</label><select id="late" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div></form>`,confirmLabel:'예약 저장',confirmAction:'save-reservation',historyKind:'reservation',historyPayload:{room:'211'}});
  3705 |       }
  3706 | 
  3707 |       function notificationCategoryLabel(category){return NOTIFICATION_CATEGORY_LABELS[category]||NOTIFICATION_CATEGORY_LABELS.general;}
  3708 |       function notificationFilterLabel(filter){return filter==='unread'?'안 읽음':filter==='action'?'처리 필요':'전체';}
  3709 |       function renderNotificationListMarkup({key=notificationAudienceKey(),filter=state.notificationFilter,includeActivity=true}={}){
  3710 |         ensureNotificationState();const bundles=notificationBundlesForKey(key),filtered=bundles.filter(bundle=>filter==='unread'?bundle.unread:filter==='action'?bundle.actionRequired:true),activity=(state.events||[]).filter(event=>!event.notify).slice(0,5),pushEnabled=notificationPushEnabled(key),filterButtons=[['all','전체'],['unread','안 읽음'],['action','처리 필요']].map(([value,label])=>`<button class="btn btn-ghost" type="button" data-action="notification-filter" data-filter="${value}" aria-pressed="${filter===value}">${label}${value==='unread'?` ${notificationUnreadCount(key)}`:''}</button>`).join('');
  3711 |         const cards=filtered.map(bundle=>{const event=bundle.latest,priority=event.priority==='urgent'?'urgent':'',status=event.status==='handled'&&!bundle.actionRequired?'처리 완료':bundle.actionRequired?'확인 필요':'안내',statusClass=status==='처리 완료'?'handled':bundle.actionRequired?'action':'',bundleText=bundle.bundleCount>1?` · 업데이트 ${bundle.bundleCount}건`:'';return `<button class="notification-card ${bundle.unread?'unread':''} ${priority}" type="button" data-action="notification-open" data-event-id="${esc(event.id)}" data-event-ids="${esc(bundle.eventIds.join(','))}" data-notification-card="${esc(event.category)}"><span class="notification-dot" aria-hidden="true"></span><span class="notification-copy"><span class="notification-title-line"><strong>${esc(event.title)}</strong>${bundle.bundleCount>1?`<span class="notification-chip">업데이트 ${bundle.bundleCount}건</span>`:''}</span><p>${esc(event.detail||'업무 상태가 변경되었습니다.')}</p><span class="notification-meta"><span>${esc(event.time)}</span><span>${esc(notificationCategoryLabel(event.category))}</span><span class="notification-chip ${statusClass}">${status}</span>${event.pushOptional?'<span>푸시 선택</span>':event.push?'<span>푸시 대상</span>':'<span>앱 내 기록</span>'}${bundleText}</span></span><span class="notification-cta">관련 화면 ${icon('chevronRight','icon-sm')}</span></button>`;}).join('');
  3712 |         const activityMarkup=includeActivity?`<section class="notification-activity"><h3>최근 활동 기록</h3><p>정상 청소 시작·사진 업로드·가능일 제출·관리자 직접 저장처럼 푸시하지 않는 활동입니다.</p><div class="notification-activity-list">${activity.length?activity.map(event=>`<div class="notification-activity-row"><span><strong>${esc(event.title)}</strong><span>${esc(event.detail||'')}</span></span><span>${esc(event.time||'')}</span></div>`).join(''):'<div class="notification-empty"><p>기록된 일반 활동이 없습니다.</p></div>'}</div></section>`:'';
  3713 |         return `<div class="notification-toolbar"><div class="notification-filter-group" role="group" aria-label="알림 필터">${filterButtons}</div><div class="notification-toolbar-actions"><button class="btn btn-outline" type="button" data-action="notification-mark-all-read" ${notificationUnreadCount(key)?'':'disabled'}>모두 읽음</button><button class="btn btn-outline" type="button" data-action="notification-toggle-push" aria-pressed="${pushEnabled}">${pushEnabled?'푸시 켜짐':'푸시 꺼짐'}</button></div></div><div class="notice notice-info notification-push-note"><div><strong>앱 내 알림은 항상 보존됩니다.</strong><br>푸시는 지금 확인하거나 행동해야 하는 상태 변경만 대상으로 하며, 이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다. 실제 백그라운드·모바일 푸시는 서비스 워커와 서버 발송 계층이 필요합니다.</div></div><div class="notification-list" data-notification-list="${esc(key)}" data-filter="${esc(filter)}">${cards||`<section class="notification-empty"><h3>${notificationFilterLabel(filter)} 알림이 없습니다</h3><p>새 상태 변경이 생기면 발생 시각 순서로 표시됩니다.</p></section>`}</div>${activityMarkup}`;
  3714 |       }
  3715 |       function openNotificationCenter(trigger=document.activeElement){const roleLabel=state.role==='admin'?'관리자 알림':'내 알림';showModal({title:roleLabel,subtitle:'업데이트를 시간순으로 보존하고 관련 업무 화면으로 바로 연결합니다.',large:true,trigger,body:renderNotificationListMarkup(),closeLabel:'닫기'});}
  3716 |       function openAlerts(){openNotificationCenter(document.activeElement);}
  3717 | 
  3718 |       function dispatchNotificationTarget(event){
  3719 |         const target=event?.target||{},action=target.action||'alerts';
  3720 |         if(action==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
  3721 |         if(action==='go-cleaning-assignment'){const day=target.data?.day==='tomorrow'?'tomorrow':'today';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
  3722 |         if(action==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
  3723 |         if(action==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  3724 |         if(action==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  3725 |         if(action==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  3726 |         const button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));button.remove();
  3727 |       }
  3728 |       function closeNotificationModalAndNavigate(notificationEvent){
  3729 |         const navigate=()=>requestAnimationFrame(()=>dispatchNotificationTarget(notificationEvent)),entry=history.state;
  3730 |         if(isWireframeHistory(entry)&&entry.layer==='modal'){
  3731 |           let completed=false;
  3732 |           const onPop=()=>{if(completed)return;completed=true;setTimeout(navigate,0);};
  3733 |           window.addEventListener('popstate',onPop,{once:true});
  3734 |           closeModal();
  3735 |           return;
  3736 |         }
  3737 |         rawCloseModal();navigate();
  3738 |       }
```

### occurrence 2 · line 6573

```html
  6557 |         const nextRegistration=reservationNextRegistrationState(room,existing,buckets),records=buckets.weekRecords,countLabel=nextRegistration.weekPast?`기록 ${records.length}건`:`예약 ${records.filter(item=>item.status==='active'&&!reservationRecordIsPast(item)).length}건`,eligibilityNote=existing&&!nextRegistration.weekPast&&room.occupancy==='occupied'&&(!nextRegistration.occupiedEnd||nextRegistration.needsCheckoutUpdate)?`<p class="reservation-week-note">${icon('alert','icon-sm')}${nextRegistration.needsCheckoutUpdate?'예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리하세요.':'현재 투숙의 체크아웃을 먼저 입력하세요.'}</p>`:'',rows=records.map(reservation=>{
  6558 |           const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정'),content=`<span class="reservation-list-period"><strong>${esc(quickRangeLabel(reservation))}</strong></span><span class="reservation-list-meta">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span><span class="reservation-list-status">${esc(status)}</span><span class="reservation-list-arrow">${readOnly?'':icon('chevronRight','icon-sm')}</span>`;
  6559 |           return readOnly?`<div class="reservation-list-row reservation-history-row" aria-label="${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}">${content}</div>`:`<button class="reservation-list-row" type="button" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-week="${buckets.window.startDate}" ${existing?.id===reservation.id?'aria-current="true"':''}>${content}</button>`;
  6560 |         }).join('');
  6561 |         const list=rows?`<div class="reservation-list"><div class="reservation-list-head" aria-hidden="true"><span>예약 일정</span><span>숙박 · 인원</span><span>청소 상태</span><span></span></div>${rows}</div>`:`<p class="reservation-schedule-empty">이 주의 예약 기록이 없습니다.</p>`;
  6562 |         return `<div class="field field-full reservation-schedule"><section class="reservation-schedule-window" aria-label="${room.no}호 ${esc(weekRangeLabel(buckets.window.startDate))} 예약"><div class="reservation-week-nav"><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="-1" aria-label="이전 주 예약 보기">${icon('chevronLeft')}</button><button class="reservation-week-range" type="button" data-action="open-reservation-week-calendar" data-room="${room.no}" aria-haspopup="dialog" aria-label="${esc(weekRangeLabel(buckets.window.startDate,true))} 주차 선택, ${countLabel}"><strong>${esc(weekRangeLabel(buckets.window.startDate))}</strong><span>${countLabel}</span></button><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="1" aria-label="다음 주 예약 보기">${icon('chevronRight')}</button></div>${nextRegistration.weekPast?`<p class="reservation-week-note">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}${eligibilityNote}${list}</section></div>`;
  6563 |       }
  6564 |       function reservationModalConfig(roomNo='211',reservationId='',newDate='') {
  6565 |         const requestedCurrent=reservationId==='__current__',isNew=reservationId==='__new__'||requestedCurrent,requestedId=reservationId&&!isNew?reservationId:'',requested=requestedId?state.reservations.find(item=>item.id===requestedId)||null:null,stale=!!(requestedId&&!requested);
  6566 |         const room=ROOMS.find(item=>item.no===(requested?.room||String(roomNo)))||ROOMS.find(item=>item.no==='211')||ROOMS[0],selectedWeek=weekStartIso(state.reservationWeekStart||state.selectedDate),buckets=reservationBucketsForRoom(state,room.no,selectedWeek),requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id,requestedVisible=requested&&(requestedCurrentStay||requested.checkInAt<buckets.window.endAt&&requested.checkOutAt>buckets.window.startAt)?requested:null,editableInWeek=buckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),existing=requestedVisible||(!reservationId?editableInWeek[0]||null:null),weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),validNewDate=/^\d{4}-\d{2}-\d{2}$/.test(newDate||'')?newDate:'',roomSpecificNew=reservationId==='__new__'&&!!validNewDate,baseDefaultDate=selectedWeek===weekStartIso(state.selectedDate)?state.selectedDate:selectedWeek,defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no),guestCount=existing?reservationGuestCount(existing):guestPolicy.defaultGuestCount,cancelImpact=existing&&!readOnly?reservationCancellationImpact(existing):null,editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id,historyReservationId=currentEntry?'__current__':isNew?'__new__':existing?.id||'';
  6567 |         const roomOptions=(currentEntry||roomSpecificNew?[room]:ROOMS.filter(item=>item.no===room.no||!quickRoomBlockReason(item)&&(item.occupancy!=='occupied'||!!occupiedReservationEnd(item)))).map(item=>`<option value="${item.no}" ${item.no===room.no?'selected':''}>${item.no}호 · ${esc(ROOM_TYPES[item.type].name)} · ${esc(item.elevator||'미기재')}</option>`).join('');
  6568 |         const scheduleList=reservationWeekScheduleMarkup(room,existing,buckets),nextRegistration=reservationNextRegistrationState(room,existing,buckets);
  6569 |         const managementNotice=existing&&!readOnly?`<div class="field field-full"><div class="notice ${cancelImpact.blockedReason?'notice-warning':'notice-info'}"><div><strong>${cancelImpact.stayStarted?'현재 예약 수정 가능 · 예약 취소 불가':cancelImpact.blockedReason?'예약 취소 불가':'예약정보 수정 또는 취소'}</strong><br>${cancelImpact.stayStarted?'인원수와 일정은 위에서 수정할 수 있습니다. 실제 투숙 종료는 객실 상세의 지금 체크아웃으로 처리하세요.':cancelImpact.blockedReason?esc(cancelImpact.blockedReason):'날짜·시각은 위에서 수정하고, 예약을 없앨 때만 예약 취소를 누르세요.'}</div></div></div>`:'';
  6570 |         const occupiedNotice=!existing&&room.occupancy==='occupied'?`<div class="field field-full"><div class="notice ${currentEntry?'notice-warning':'notice-info'}"><div><strong>${currentEntry?'현재 투숙 정보 입력':'현재 투숙 중 · 다음 예약 등록'}</strong><br>${currentEntry?'실제 체크인과 예정 체크아웃, 숙박 인원을 확인해 입력하세요. 체크아웃을 저장한 뒤 다음 예약을 등록할 수 있습니다.':`${quickDateLabel(occupiedReservationEnd(room).slice(0,10))} ${occupiedReservationEnd(room).slice(11,16)} 체크아웃 이후의 겹치지 않는 일정만 등록할 수 있습니다.`}</div></div></div>`:'';
  6571 |         if(stale)return {room:room.no,reservationId:requestedId,title:`${room.no}호 예약을 다시 확인해 주세요`,subtitle:'열어 둔 예약이 이미 변경되었거나 취소되었습니다.',closeLabel:'닫기',large:true,body:`<div class="notice notice-warning"><div><strong>최신 예약 목록에서 다시 선택해 주세요.</strong></div></div>${scheduleList}`,confirmLabel:'',confirmAction:''};
  6572 |         if(readOnly)return {room:room.no,reservationId:historyReservationId,title:`${room.no}호 지난 예약 기록`,subtitle:`${weekRangeLabel(selectedWeek,true)} · 지난 기록은 수정하거나 취소할 수 없습니다.`,closeLabel:'닫기',large:true,body:scheduleList,confirmLabel:'',confirmAction:''};
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
  6590 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null;
  6591 |         if(!adminCanMutate()){toast('관리자 최신 온라인 상태에서만 예약을 취소할 수 있습니다.','error');return;}
  6592 |         if(!reservation||reservationFingerprint(reservation)!==expectedFingerprint){toast('예약 일정이 바뀌었거나 이미 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  6593 |         const impact=reservationCancellationImpact(reservation);if(impact.blockedReason){toast(impact.blockedReason,'error');return;}
  6594 |         const assignmentStatus=impact.manualTarget?`별도 등록한 현장 청소 요청 · 담당과 일정 유지`:impact.assignmentRecord?(impact.notifiedMaidId?`${maidName(impact.notifiedMaidId)} · 통보 완료 → 담당 취소 통보`:(impact.selectedMaidId?`${maidName(impact.selectedMaidId)} · 저장 전 선택 해제`:'미배정 상태 취소')):'청소 미배정',adjacentText=impact.adjacentChanges.length?impact.adjacentChanges.map(entry=>`${entry.reservation.room}호 ${quickRangeLabel(entry.reservation)} · 준비 마감 ${entry.before.deadline} → ${entry.after.deadline}`).join('<br>'):'변경되는 인접 예약 없음',impactFingerprint=reservationCancellationImpactFingerprint(reservation,impact);
  6595 |         showModal({title:`${reservation.room}호 예약을 취소할까요?`,subtitle:'청소 담당과 일정 영향을 확인한 뒤 취소하세요.',trigger,historyKind:'reservation-cancel',historyPayload:{room:reservation.room,reservationId:reservation.id},historyStack:true,closeLabel:'돌아가기',body:`<div class="info-grid"><div class="info-item"><span>취소 대상</span><strong>${reservation.room}호 · ${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</strong></div><div class="info-item"><span>예약 일정</span><strong>${esc(quickRangeLabel(reservation))}</strong></div><div class="info-item"><span>퇴실 청소 준비</span><strong>${impact.privateDrafts.length}건 · 함께 취소</strong></div><div class="info-item"><span>청소 담당 영향</span><strong>${esc(assignmentStatus)}</strong></div><div class="info-item"><span>인접 예약 청소 마감</span><strong>${adjacentText}</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>외부 예약은 취소되지 않습니다.</strong><br>외부 OTA/PMS에서도 예약 취소 여부를 따로 확인하세요.</div></div><div class="field" style="margin-top:14px"><label for="reservation-cancel-reason">예약 취소 사유</label><select id="reservation-cancel-reason" class="select-control" data-control="reservation-cancel-reason" required><option value="">사유를 선택하세요</option>${Object.entries(RESERVATION_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.</small></div>`,confirmLabel:'예약 취소 확정',confirmAction:'confirm-reservation-cancel',confirmVariant:'danger'});
  6596 |         const confirm=document.querySelector('[data-action="confirm-reservation-cancel"]');if(confirm){confirm.dataset.id=reservation.id;confirm.dataset.fingerprint=expectedFingerprint;confirm.dataset.impact=impactFingerprint;confirm.disabled=true;}
  6597 |       }
  6598 |       function openPaymentConfirm(weekStart,maidId,trigger=document.activeElement) {
  6599 |         const context=paymentContextFor(weekStart,maidId);
  6600 |         if(!context||context.meta.locked||!['OPEN','PAYING','CHECK'].includes(context.meta.status)){toast(context?.meta.status==='PAID'?'지급 완료 기록은 직접 취소하지 않고 정정·상계로 처리합니다.':'현재 이 메이드의 지급 상태를 변경할 수 없습니다.','error');return;}
  6601 |         const bindRecordAction=(action,expected=context.meta.status)=>{const target=document.querySelector(`[data-action="${action}"]`);if(target){target.dataset.week=context.cfg.start;target.dataset.maid=context.maid.id;target.dataset.expected=expected;target.dataset.record=paymentRecordFingerprint(context.record);}};
  6602 |         if(context.meta.status==='PAYING'){
  6603 |           showModal({title:`${context.maid.name} 송금 결과를 기록할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확인합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>실제 전액 송금이 끝난 경우에만 완료하세요.</strong><br>송금 여부가 불명확하면 확인 필요로 두고, 송금하지 않았다면 사유를 남겨 지급 대기로 돌립니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 확인 전이라 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금 여부 확인 필요','mark-payment-check','outline')}${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6604 |           bindRecordAction('confirm-finish-payment','PAYING');bindRecordAction('mark-payment-check','PAYING');bindRecordAction('confirm-payment-open-v2','PAYING');return;
  6605 |         }
  6606 |         if(context.meta.status==='CHECK'){
  6607 |           showModal({title:`${context.maid.name} 지급 결과를 다시 확인하세요`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 송금 결과를 확인해 상태를 정합니다.`,trigger,body:`<div class="notice notice-danger"><div><strong>외부 송금 결과를 확인한 뒤 한 가지 결과만 기록하세요.</strong><br>완료라면 이번 지급액과 청소 내역으로 지급 완료를 기록하고, 미송금이면 사유를 남겨 지급 대기로 돌아갑니다.</div></div><div class="info-grid"><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 오류를 확인해 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 재기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
```

### occurrence 3 · line 6750

```html
  6734 |         showModal({title:'332호 영향 확인·충돌 해결',subtitle:'변경된 체크아웃과 현재 청소·PIN 조회 영향을 확인하세요.',large:true,trigger,body:`<div class="notice notice-danger"><div><strong>현재 상태 확인</strong><br>${record.autoCheckoutAt} 자동 체크아웃 기록은 남기고 ${record.afterCheckout}까지 투숙 중으로 표시합니다.</div></div><div class="info-grid"><div class="info-item"><span>체크아웃 전 → 후</span><strong>${record.beforeCheckout} → ${record.afterCheckout}</strong></div><div class="info-item"><span>청소 담당·단계</span><strong>${record.assignee} · ${record.stage}</strong></div><div class="info-item"><span>PIN 조회</span><strong>${record.pinViewedAt}</strong></div><div class="info-item"><span>PIN 조회 처리</span><strong>기존 조회 종료 후 다시 확인</strong></div></div><div class="choice-list" style="margin-top:14px"><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="coordinate" ${state.conflictSteps.coordinate?'checked':''} ${isLocked()?'disabled':''}><span><strong>현장 조율 완료</strong><span>투숙객·${record.assignee}에게 변경된 체크아웃과 출입 중단을 확인</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="replan" ${state.conflictSteps.replan?'checked':''} ${isLocked()?'disabled':''}><span><strong>청소 일정 변경 완료</strong><span>진행 중 청소를 중단 처리하고 ${record.afterCheckout} 새 청소 생성</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="pin" ${state.conflictSteps.pin?'checked':''} ${isLocked()?'disabled':''}><span><strong>도어락 PIN 확인 완료</strong><span>기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.</span></span></label></div>`,confirmLabel:'조치 완료',confirmAction:'confirm-conflict-v2',confirmVariant:'danger'});
  6735 |         const confirm=document.querySelector('[data-action="confirm-conflict-v2"]');
  6736 |         if(confirm)confirm.disabled=isLocked()||!Object.values(state.conflictSteps).every(Boolean);
  6737 |       }
  6738 | 
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
```

### occurrence 4 · line 6754

```html
  6738 | 
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
  6785 |         if(a==='open-reservation-week-calendar'){
  6786 |           if(state.role!=='admin')return;state.reservationWeekRoom=el.dataset.room||state.reservationWeekRoom||'211';state.calendarMonth=weekStartIso(state.reservationWeekStart||state.selectedDate).slice(0,7);openCalendar(el,'reservation-week',true);return;
  6787 |         }
  6788 |         if(a==='reservation-add'){
```

### occurrence 5 · line 6755

```html
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
  6785 |         if(a==='open-reservation-week-calendar'){
  6786 |           if(state.role!=='admin')return;state.reservationWeekRoom=el.dataset.room||state.reservationWeekRoom||'211';state.calendarMonth=weekStartIso(state.reservationWeekStart||state.selectedDate).slice(0,7);openCalendar(el,'reservation-week',true);return;
  6787 |         }
  6788 |         if(a==='reservation-add'){
  6789 |           const room=ROOMS.find(item=>item.no===String(el.dataset.room||'')),newDate=el.dataset.date||suggestedReservationStartDate(room?.no||'');
```

### occurrence 6 · line 7090

```html
  7074 |           pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);});toast('청소 작업은 내일 배정에서 담당과 순서를 지정해 주세요.');return;
  7075 |         }
  7076 |         if(a==='confirm-publish'){
  7077 |           pendingDraftPublish=null;closeModal();pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);});toast('공개 전환은 중단되었습니다. 담당 메이드를 내일 배정 화면에서 지정해 주세요.');return;
  7078 |         }
  7079 |         if(a==='reservation-edit'||a==='new-reservation'){
  7080 |           const roomRecords=id?(state.reservations||[]).filter(reservation=>reservation.room===String(id)):[],historyOnly=roomRecords.length>0&&roomRecords.every(reservationRecordIsPast);
  7081 |           if(!adminCanMutate()&&!(a==='reservation-edit'&&historyOnly)){toast('관리자 최신 상태에서만 예약을 등록·변경할 수 있습니다.','error');return;}
  7082 |           const block=id?quickRoomBlockReason(ROOMS.find(room=>room.no===id)):'' ,hasExisting=id?activeReservationsFor(state,id).length>0:false;if(block&&(a==='new-reservation'||!hasExisting)&&!historyOnly){toast(`${id}호는 ${block} 상태라 새 예약을 등록할 수 없습니다.`,'error');return;}openReservation(id||'211',a==='new-reservation'?'__new__':'');return;
  7083 |         }
  7084 |         if(a==='reservation-guest-change'){
  7085 |           const input=document.getElementById('res-guests'),roomNo=document.getElementById('res-room')?.value||'',policy=guestPolicyForRoom(roomNo),delta=Number(el.dataset.delta),current=Number(input?.value);
  7086 |           if(!input||!Number.isInteger(current)||![-1,1].includes(delta))return;
  7087 |           const next=current+delta;if(next<1||next>policy.maxGuestCount)return;
  7088 |           input.value=String(next);updateReservationGuestControls();const focusTarget=el.disabled?document.querySelector(`[data-action="reservation-guest-change"][data-delta="${-delta}"]`):el;focusTarget?.focus();return;
  7089 |         }
  7090 |         if(a==='save-reservation-v2'){
  7091 |           if(!adminCanMutate()){closeModal();render();toast('관리자 권한 또는 최신 상태가 바뀌어 예약을 저장하지 않았습니다.','error');return;}
  7092 |           const reservationId=document.getElementById('res-id')?.value||'',existing=reservationId?state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null:null,no=existing?.room||document.getElementById('res-room')?.value||'211',room=ROOMS.find(item=>item.no===no);
  7093 |           if(reservationId&&!existing){closeModal();render();toast('이 예약은 이미 변경되었거나 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  7094 |           if(reservationWeekIsPast()||reservationRecordIsPast(existing)){closeModal();render();toast('지난 예약 기록은 조회만 가능하며 수정할 수 없습니다.','error');return;}
  7095 |           if(existing&&reservationFingerprint(existing)!==(document.getElementById('res-fingerprint')?.value||'')){closeModal();render();toast('예약 일정이 다른 화면에서 바뀌었습니다. 최신 예약을 다시 확인해 주세요.','error');return;}
  7096 |           if(!room||!existing&&quickRoomBlockReason(room)){closeModal();render();toast(`${no}호는 ${quickRoomBlockReason(room)||'객실 정보 없음'} 상태라 새 예약을 저장하지 않았습니다.`,'error');return;}
  7097 |           const checkinAt=document.getElementById('res-checkin')?.value||'', checkoutAt=document.getElementById('res-checkout')?.value||'',guestCount=document.getElementById('res-guests')?.value??'',currentStay=document.getElementById('res-current-stay')?.value==='1';
  7098 |           const validDateTime=value=>/^\d{4}-\d{2}-\d{2}T([01]\d|2[0-3]):[0-5]\d$/.test(value);
  7099 |           if(!validDateTime(checkinAt)||!validDateTime(checkoutAt)||checkinAt>=checkoutAt||checkinAt.slice(0,10)>=checkoutAt.slice(0,10)){toast('한 고객의 체크인 다음에 체크아웃이 오도록 입력하세요.','error');document.getElementById(!validDateTime(checkinAt)?'res-checkin':'res-checkout')?.focus();return;}
  7100 |           const checkinTime=checkinAt.slice(11,16), checkoutTime=checkoutAt.slice(11,16);
  7101 |           if(!checkinTime.endsWith(':00')||!checkoutTime.endsWith(':00')){toast('예정 체크인·체크아웃은 1시간 단위로 입력하세요.','error');(!checkinTime.endsWith(':00')?document.getElementById('res-checkin'):document.getElementById('res-checkout'))?.focus();return;}
  7102 |           const result=upsertReservationRecord({id:reservationId,roomNo:no,checkInAt:checkinAt,checkOutAt:checkoutAt,guestCount,source:'card',currentStay});
  7103 |           if(result.error){const overlap=result.conflict?.reservation||result.conflict?.checkInAt&&result.conflict,conflictField=overlap&&checkinAt<overlap.checkInAt?'res-checkout':'res-checkin';toast(result.error,'error');document.getElementById(result.guestError?'reservation-guest-stepper':result.conflict?conflictField:'res-checkin')?.focus();return;}
  7104 |           const cardReservation=activeReservationsFor(state,no).find(item=>!reservationRecordIsPast(item))||result.reservation;
  7105 |           state.quickLastCreated=null;historyReturnFocus=state.adminView==='quickReservation'?{quickCell:true,room:no,date:result.reservation.checkInAt.slice(0,10)}:state.detail?.type==='room'?{action:'reservation-edit',id:no}:{action:'quick-reservation-edit',id:cardReservation.id,room:no};closeModal();render();toast(`${no}호 ${reservationNights(result.reservation)}박 · ${reservationGuestCount(result.reservation)}명 예약을 저장했습니다.`);return;
  7106 |         }
  7107 |         if(a==='complete-checkout-inspection'){
  7108 |           const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!reservation||!checkoutInspectionPendingForReservation(reservation)){toast('현재 퇴실점검 대상이 아니거나 이미 완료되었습니다.','error');return;}showModal({title:`${no}호 퇴실점검을 완료할까요?`,subtitle:`${reservationMomentLabel(reservation.checkOutAt)} 체크아웃 · 예약 ${reservation.id}`,trigger:el,body:'<div class="notice notice-warning"><div><strong>청소 완료 처리와는 별도입니다.</strong><br>퇴실점검 대상 상태만 해제하고 객실의 청소 필요·배정 상태는 그대로 유지합니다.</div></div>',confirmLabel:'퇴실점검 완료 기록',confirmAction:'confirm-checkout-inspection',confirmVariant:'primary'});const confirm=document.querySelector('[data-action="confirm-checkout-inspection"]');if(confirm){confirm.dataset.id=no;confirm.dataset.reservation=reservation.id;}return;
  7109 |         }
  7110 |         if(a==='confirm-checkout-inspection'){
  7111 |           const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!adminCanMutate()||!reservation||reservation.id!==el.dataset.reservation||!checkoutInspectionPendingForReservation(reservation)){closeModal();render();toast('퇴실점검 대상 또는 관리자 최신 상태가 바뀌어 완료하지 않았습니다.','error');return;}const result=completeCheckoutInspection(no,{method:'manual'});if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-checkout-inspection-room="${no}"]`);toast(`${no}호 퇴실점검을 완료했습니다. 청소 필요 상태는 유지됩니다.`);return;
  7112 |         }
  7113 |         if(a==='toggle-room-cleaning'){
  7114 |           const no=String(id||''),request=activeManualCleaningRequest(no),block=request?manualCleaningCancelBlockReason(no):manualCleaningRequestBlockReason(no);if(block){toast(block,'error');return;}
  7115 |           const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:request?`${no}호 청소 요청을 취소할까요?`:`${no}호 청소를 요청할까요?`,subtitle:request?`${kind} · 대기열에서 취소`:`${kind} · 청소 대기열 등록`,trigger:el,body:request?'<div class="notice notice-warning"><div><strong>청소 대기열에서 요청을 취소합니다.</strong><br>아직 미배정·미공개·미착수인 요청만 취소되며, 이미 시작된 작업은 청소 상세에서 확인해야 합니다.</div></div>':'<div class="notice notice-info"><div><strong>확인하면 청소 대기열에 작업 1건을 등록합니다.</strong><br>투숙 중 객실은 연박 청소, 공실 객실은 추가 청소로 등록되며 담당은 관리자 배정 화면에서 정합니다.</div></div>',confirmLabel:request?'청소 취소':'청소 대기열에 넣기',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action="${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;
  7116 |         }
  7117 |         if(a==='confirm-room-cleaning-on'){
  7118 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 만들지 않았습니다.','error');return;}const result=createManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind}를 청소 대기열에 넣었습니다.`);return;
  7119 |         }
  7120 |         if(a==='confirm-room-cleaning-off'){
  7121 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 취소하지 않았습니다.','error');return;}const result=cancelManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind} 요청을 취소했습니다.`);return;
  7122 |         }
  7123 |         if(a==='create-stayover'){
  7124 |           const no=id||'142',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
```

### occurrence 7 · line 7667

```html
  7651 |       document.addEventListener('click', e => {
  7652 |         const el=e.target.closest('[data-action]'); if(!el) return; const a=el.dataset.action,id=el.dataset.id;
  7653 |         if (a==='backdrop-close' && e.target!==el) return;
  7654 |         if (a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();}
  7655 |         else if(a==='reset'){state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();toast('시나리오를 초기 상태로 재설정했습니다.');}
  7656 |         else if(a==='switch-role'){state.role=state.role==='admin'?'maid':'admin';state.detail=null;render();toast(`${state.role==='admin'?'관리자':'메이드'} 데모로 전환했습니다.`);}
  7657 |         else if(a==='nav'){state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;render();requestAnimationFrame(()=>document.getElementById('main-content')?.focus());}
  7658 |         else if(a==='alerts')openAlerts();
  7659 |         else if(a==='close-modal'||a==='backdrop-close')dismissModal();
  7660 |         else if(a==='back')backFromDetail();
  7661 |         else if(a==='room-detail')openDetail('room',id||'350',el);
  7662 |         else if(a==='cleaning-detail')openDetail('cleaning',id||'639',el);
  7663 |         else if(a==='maid-detail')openDetail('maid',id||'m1',el);
  7664 |         else if(a==='complaint-detail')openDetail('complaint','c1',el);
  7665 |         else if(a==='pay-detail')openDetail('pay','week',el);
  7666 |         else if(a==='new-reservation')openReservation();
  7667 |         else if(a==='save-reservation'){state.reservationSaved=true;if(!state.drafts.some(d=>d.room==='211'))state.drafts.push({id:'d211',room:'211',kind:'퇴실 청소',created:state.time});state.jobs['211']='draft';appendEvent('211호 예약 저장','퇴실 청소 준비');closeModal();render();toast('211호 예약을 저장했습니다.');}
  7668 |         else if(a==='publish-selected'){if(!state.selectedDrafts.length)return;openPublishConfirm();}
  7669 |         else if(a==='confirm-publish'){closeModal();state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);render();toast('내일 배정에서 담당 메이드를 직접 지정해 주세요.');}
  7670 |         else if(a==='claim-job'||a==='confirm-claim'){closeModal();state.maidView='schedule';render();toast('메이드는 객실을 선택할 권한이 없습니다. 관리자 배정 통보를 확인해 주세요.','error');}
  7671 |         else if(a==='go-my'){state.maidView='my';render();}
  7672 |         else if(a==='show-pin'){state.pinVisibleUntil=Date.now()+30000;appendEvent(`${state.detail?.id||'350'}호 PIN 조회`,'원문 없이 조회 사실만 감사 기록');render();clearTimeout(pinTimer);pinTimer=setTimeout(()=>{state.pinVisibleUntil=0;render();toast('30초가 지나 객실 PIN을 다시 가렸습니다.');},30000);}
  7673 |         else if(a==='hide-pin'){state.pinVisibleUntil=0;clearTimeout(pinTimer);render();}
  7674 |         else if(a==='start-cleaning')showModal({title:`${id||state.detail?.id||'350'}호 청소를 시작할까요?`,subtitle:'다른 청소 중 작업이 없는지 온라인으로 다시 검증하는 데모입니다.',body:`<div class="notice notice-warning">시작하면 이 작업이 유일한 청소 중 슬롯을 사용합니다.</div>`,confirmLabel:'청소 시작',confirmAction:'confirm-start'}),document.querySelector('#modal-root [data-action="confirm-start"]')?.setAttribute('data-id',id||state.detail?.id||'350');
  7675 |         else if(a==='confirm-start'){const room=id||'350';state.jobs[room]='cleaning';state.activeCleaning=room;state.detail={type:'cleaning',id:room};appendEvent(`${room}호 청소 시작`,'활성 수행 회차 1건');closeModal();render();toast('청소 중 상태와 타임라인이 갱신됐습니다.');}
  7676 |         else if(a==='retry-photo'){const u=state.uploads.find(x=>x.id===id);if(u){u.status='uploading';render();setTimeout(()=>{u.status='done';render();toast('사진 재전송에 성공했습니다.');},450);}}
  7677 |         else if(a==='field-complete'){const room=id||state.detail?.id||'528';state.jobs[room]='upload';state.activeCleaning=null;appendEvent(`${room}호 현장 완료`,'물리적 진행 슬롯 해제 · 미디어 검증 대기');render();toast('현장 완료·업로드 대기로 전환했습니다.');}
  7678 |         else if(a==='submit-cleaning'){const room=id||state.detail?.id||'528';if(state.uploads.some(u=>u.status!=='done')){state.uploads.filter(u=>u.status==='failed').forEach(u=>u.status='done');render();toast('미전송 사진을 재시도했습니다.');}else{state.jobs[room]='inspection';appendEvent(`${room}호 청소 전체 제출`,'필수 파일 검증 완료 · 검수 대기');render();toast('전체 제출 후 검수 대기로 전환했습니다.');}}
  7679 |         else if(a==='approve-inspection')openInspectionDecision('approve');
  7680 |         else if(a==='reject-inspection')openInspectionDecision('reject');
  7681 |         else if(a==='confirm-approve'){state.inspection.status='approved';state.jobs['639']='approved';state.earningsAddedByRoom['639']=true;appendEvent('639호 전체 제출 승인','수익 1건 · 객실 상태 재계산');closeModal();render();toast('전체 승인과 수익 귀속을 반영했습니다.');}
  7682 |         else if(a==='confirm-reject'){
  7683 |           if(!adminCanMutate()){closeModal();render();toast('관리자 최신 상태에서만 전체 반려를 저장할 수 있습니다.','error');return;}
  7684 |           const no='639',submission=currentSubmission(no),room=ROOMS.find(item=>item.no===no),performer=submission?.performerName||room?.assignee||'이서연',performerId=submission?.performerId||performerIdentity(no,performer).performerId;
  7685 |           if(room)room.assignee=performer;state.inspection.status='rejected';state.inspection.reclean='existing';state.inspections[no]='rejected';state.jobs[no]='reclean';beginCleaningAttempt(no,{performerId,performerName:performer,reason:'전체 반려 뒤 처음 청소한 본인 무급 재청소',baseRateSnapshot:0,kind:'재청소',reservationIdSnapshot:submission?.reservationIdSnapshot,guestCountSnapshot:submission?.guestCountSnapshot});appendEvent('639호 전체 제출 반려',`${performer} 본인 무급 재청소 자동 귀속 · 타 메이드 이관 없음`);closeModal();render();toast(`${performer} 본인에게 무급 재청소를 자동 배정했습니다.`);
  7686 |         }
  7687 |         else if(a==='recover-candle')showModal({title:'350호 촛불 1개를 회수할까요?',subtitle:'검수 승인은 촛불 수량을 자동으로 0개로 만들지 않습니다.',body:`<div class="info-grid"><div class="info-item"><span>현재</span><strong>촛불 1개 · 입실 차단</strong></div><div class="info-item"><span>변경 후</span><strong>촛불 0개 · 상태 재계산</strong></div></div>`,confirmLabel:'1개 회수',confirmAction:'confirm-candle',confirmVariant:'danger'});
  7688 |         else if(a==='confirm-candle'){state.candles['350']=0;appendEvent('350호 촛불 1개 회수',timeMinutes(state.time)>=timeMinutes('16:00')?'입실 시각 후 조건 해소 · 예약상 투숙 중 전이 1회':'관리자 데모 · 입실 조건 재계산');closeModal();render();toast(timeMinutes(state.time)>=timeMinutes('16:00')?'촛불 0개와 예약상 투숙 중 전이를 반영했습니다.':'촛불 0개와 입실 준비 완료를 함께 반영했습니다.');}
  7689 |         else if(a==='resolve-conflict')openConflictModal();
  7690 |         else if(a==='confirm-conflict'){if(!Object.values(state.conflictSteps).every(Boolean)){toast('조율·재계획·PIN 교체를 모두 확인해야 합니다.','error');return;}state.conflict='resolved';appendEvent('332호 출입 충돌 종결','현장 조율 · 작업 재계획 · PIN 교체 완료');closeModal();render();toast('충돌을 종결하고 객실 상태를 재계산했습니다.');}
  7691 |         else if(a==='cancel-review'){if(isLocked())toast('최신 상태를 확인하기 전에는 담당 취소 요청을 처리할 수 없습니다.','error');else state.cancelRequest==='requested'?openCancelReview():toast('담당 취소 요청은 이미 처리됐습니다.');}
  7692 |         else if(a==='confirm-cancel'){
  7693 |           if(isLocked()){closeModal();render();toast('동기화 상태가 바뀌어 담당 취소 결정을 저장하지 않았습니다.','error');return;}
  7694 |           const chosen=document.querySelector('input[name="cancel-decision"]:checked')?.value||'deny', no=state.cancelRequestRoom||Object.keys(state.cancelRequests||{})[0]||'332', request=state.cancelRequests?.[no], room=ROOMS.find(item=>item.no===no), maid=request?.maid||room?.assignee||'김민지1';
  7695 |           state.cancelDecision=chosen;state.cancelRequest='resolved';if(request){request.status=chosen==='deny'?'denied':'approved';request.decision=chosen;request.decidedAt=`${state.selectedDate} ${state.time}`;}
  7696 |           if(chosen==='republish'){state.jobs[no]='unassigned';if(room)room.assignee='미정';if(state.activeCleaning===no)state.activeCleaning=null;}
  7697 |           if(chosen==='direct'){state.jobs[no]='claimed';if(room)room.assignee='김민지2';if(state.activeCleaning===no)state.activeCleaning=null;}
  7698 |           if(chosen==='hold'){state.jobs[no]='hold';if(state.activeCleaning===no)state.activeCleaning=null;}
  7699 |           appendEvent(`${maid} 담당 취소 요청 처리`,chosen==='deny'?`거절 · ${no}호 담당 유지`:`승인 · ${no}호 ${chosen}`);closeModal();render();focusAfterRender('[data-key="cancel"]');toast('결정과 카드·타임라인을 함께 갱신했습니다.');
  7700 |         }
  7701 |         else if(a==='go-today'){state.detail=null;state.adminView='today';render();}
```

## reservation overlap: `reservationOverlaps`

matches: 6

### occurrence 1 · line 1934

```html
  1918 |       }
  1919 |       function reservationNights(reservation) {
  1920 |         if(!reservation)return 0;
  1921 |         const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));
  1922 |         return Math.max(1,Math.round((end-start)/86400000));
  1923 |       }
  1924 |       function roomStayProgress(room,reservations=activeReservationsFor(state,room?.no||'')) {
  1925 |         if(room?.occupancy!=='occupied')return null;
  1926 |         const pivot=`${state.selectedDate}T${state.time}`,reservation=reservations.find(item=>item.checkInAt<=pivot&&pivot<item.checkOutAt),total=reservationNights(reservation);
  1927 |         if(!reservation||total<2)return null;
  1928 |         const day=Math.max(1,Math.min(total,Math.round((dateObject(state.selectedDate)-dateObject(reservation.checkInAt.slice(0,10)))/86400000)+1));
  1929 |         return {day,total,reservationId:reservation.id,label:`연박 ${day}/${total}일차`};
  1930 |       }
  1931 |       function reservationContainsNight(reservation,isoDate) {
  1932 |         return reservation?.status==='active'&&reservation.checkInAt.slice(0,10)<=isoDate&&isoDate<reservation.checkOutAt.slice(0,10);
  1933 |       }
  1934 |       function reservationOverlaps(roomNo,checkInAt,checkOutAt,ignoreId='') {
  1935 |         return activeReservationsFor(state,roomNo).find(reservation=>reservation.id!==ignoreId&&checkInAt<reservation.checkOutAt&&checkOutAt>reservation.checkInAt)||null;
  1936 |       }
  1937 |       function reservationFingerprint(reservation) {
  1938 |         return reservation?[reservation.id,reservation.room,reservation.checkInAt,reservation.checkOutAt,reservationGuestCount(reservation),reservation.status,reservation.updatedAt||''].join('|'):'';
  1939 |       }
  1940 |       function reservationTurnoverSchedule(reservation,reservations=activeReservationsFor(state,reservation?.room||'')) {
  1941 |         if(!reservation)return {nextReservationId:null,checkin:DEFAULT_CHECKIN_TIME,deadline:'15:30'};
  1942 |         const nextReservation=reservations.find(candidate=>candidate.id!==reservation.id&&candidate.checkInAt>=reservation.checkOutAt),sameDay=nextReservation?.checkInAt.slice(0,10)===reservation.checkOutAt.slice(0,10),checkin=sameDay?nextReservation.checkInAt.slice(11,16):DEFAULT_CHECKIN_TIME;
  1943 |         return {nextReservationId:sameDay?nextReservation.id:null,checkin,deadline:shiftClockTime(checkin,-30)||'15:30'};
  1944 |       }
  1945 |       function operationalMoment(targetState=state) { return `${targetState.selectedDate||'2026-08-15'}T${targetState.time||'00:00'}`; }
  1946 |       function reservationAtOperationalMoment(roomNo,targetState=state) {
  1947 |         const moment=operationalMoment(targetState);
  1948 |         return activeReservationsFor(targetState,String(roomNo)).find(reservation=>reservation.checkInAt<=moment&&moment<reservation.checkOutAt)||null;
  1949 |       }
  1950 |       function latestCheckedOutReservationForRoom(roomNo,targetState=state) {
  1951 |         const moment=operationalMoment(targetState);
  1952 |         return (targetState.reservations||[]).filter(reservation=>reservation.room===String(roomNo)&&reservation.status!=='cancelled'&&reservation.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null;
  1953 |       }
  1954 |       function checkoutCleaningCompletedForReservation(reservation,targetState=state) {
  1955 |         if(!reservation)return false;
  1956 |         const attempts=Object.values(targetState.cleaningAttempts||{}).filter(attempt=>attempt?.room===reservation.room&&attempt.kind==='퇴실 청소'&&(attempt.reservationIdSnapshot===reservation.id||targetState.assignments?.[attempt.workTargetId]?.committedTarget?.reservationId===reservation.id));
  1957 |         if(attempts.some(attempt=>!!attempt.completedAt||['upload','submitted','approved','rejected'].includes(attempt.status)))return true;
  1958 |         return Object.values(targetState.cleaningSubmissions||{}).some(submission=>submission?.room===reservation.room&&submission.reservationIdSnapshot===reservation.id);
  1959 |       }
  1960 |       function roomCheckoutCleaningDue(no,targetState=state) {
  1961 |         if(reservationAtOperationalMoment(no,targetState))return false;
  1962 |         const reservation=latestCheckedOutReservationForRoom(no,targetState);
  1963 |         return !!reservation&&!checkoutCleaningCompletedForReservation(reservation,targetState);
  1964 |       }
  1965 |       function checkoutInspectionRecordFor(reservationId,targetState=state) { return reservationId?targetState.checkoutInspections?.[reservationId]||null:null; }
  1966 |       function checkoutInspectionReservationForRoom(no,targetState=state) {
  1967 |         if(reservationAtOperationalMoment(no,targetState))return null;
  1968 |         return latestCheckedOutReservationForRoom(no,targetState);
```

### occurrence 2 · line 4416

```html
  4400 |       }
  4401 |       function occupiedReservationEnd(room) {
  4402 |         const current=currentOccupiedReservation(room);
  4403 |         return room?.actualCheckoutAt||room?.plannedCheckoutAt||current?.checkOutAt||'';
  4404 |       }
  4405 |       function occupiedStayNeedsCheckoutUpdate(room) {
  4406 |         const knownEnd=occupiedReservationEnd(room);
  4407 |         return !!(room?.occupancy==='occupied'&&knownEnd&&knownEnd<=reservationCurrentMoment());
  4408 |       }
  4409 |       function suggestedReservationStartDate(roomNo) {
  4410 |         const room=ROOMS.find(item=>item.no===String(roomNo));
  4411 |         if(!room)return state.selectedDate;
  4412 |         const knownEnd=occupiedReservationEnd(room),current=currentOccupiedReservation(room);
  4413 |         let candidate=(current||room.occupancy==='occupied')?(knownEnd?knownEnd.slice(0,10):shiftIsoDate(state.selectedDate,1)):state.selectedDate;
  4414 |         if(candidate<state.selectedDate)candidate=state.selectedDate;
  4415 |         for(let index=0;index<370;index+=1){
  4416 |           const checkInAt=`${candidate}T${DEFAULT_CHECKIN_TIME}`,checkOutAt=`${shiftIsoDate(candidate,1)}T${DEFAULT_CHECKOUT_TIME}`,overlap=reservationOverlaps(room.no,checkInAt,checkOutAt);
  4417 |           if((!knownEnd||checkInAt>=knownEnd)&&!overlap)return candidate;
  4418 |           const nextDate=overlap?.checkOutAt?.slice(0,10)||shiftIsoDate(candidate,1);candidate=nextDate>candidate?nextDate:shiftIsoDate(candidate,1);
  4419 |         }
  4420 |         return shiftIsoDate(state.selectedDate,1);
  4421 |       }
  4422 |       function quickOccupiedDateBlockReason(room,iso) {
  4423 |         if(!room||room.occupancy!=='occupied')return '';
  4424 |         const knownEnd=occupiedReservationEnd(room);
  4425 |         if(!knownEnd)return '투숙 중 · 체크아웃 일정 미입력';
  4426 |         if(occupiedStayNeedsCheckoutUpdate(room))return '투숙 중 · 예정 체크아웃 경과, 현재 예약을 먼저 갱신';
  4427 |         if(knownEnd&&iso<knownEnd.slice(0,10))return `투숙 중 · ${quickDateLabel(knownEnd.slice(0,10))} ${knownEnd.slice(11,16)} 퇴실 전`;
  4428 |         return '';
  4429 |       }
  4430 |       function reservationForNight(roomNo,iso) { return activeReservationsFor(state,roomNo).find(reservation=>reservationContainsNight(reservation,iso))||null; }
  4431 |       function cleaningAssignmentForReservation(reservation) {
  4432 |         if(!reservation)return {name:'청소 미배정',status:'미배정',maidId:null,assigned:false};
  4433 |         const checkoutDate=reservation.checkOutAt.slice(0,10),expectedId=`checkout-${reservation.room}-${checkoutDate}`;
  4434 |         const liveTarget=liveAssignmentTargets().find(target=>target.reservationId===reservation.id||(target.room===reservation.room&&target.kind==='퇴실 청소'&&(target.date===checkoutDate||target.id===expectedId||target.id.includes(checkoutDate)))),entry=liveTarget&&state.assignments?.[liveTarget.id]?[liveTarget.id,state.assignments[liveTarget.id]]:Object.entries(state.assignments||{}).find(([id,record])=>id===expectedId||(record?.committedTarget?.room===reservation.room&&(record.committedTarget.date===checkoutDate||id.includes(checkoutDate)||record.committedTarget.id===expectedId))),record=entry?.[1];
  4435 |         const maidId=record?.maidId||record?.previousMaidId||null;
  4436 |         if(!maidId)return {name:'청소 미배정',status:'미배정',maidId:null,assigned:false};
  4437 |         const status=record.status==='notified'?'통보 완료':record.status==='draft'?'저장 전':record.status==='cancelled'?'취소됨':'배정됨';
  4438 |         return {name:maidName(maidId),status,maidId,assigned:record.status!=='cancelled'};
  4439 |       }
  4440 |       function quickBookingTimes(firstNight,lastNight) {
  4441 |         const ordered=[firstNight,lastNight].sort();
  4442 |         return {firstNight:ordered[0],lastNight:ordered[1],checkInAt:`${ordered[0]}T${DEFAULT_CHECKIN_TIME}`,checkOutAt:`${shiftIsoDate(ordered[1],1)}T${DEFAULT_CHECKOUT_TIME}`};
  4443 |       }
  4444 |       function quickReservationConflict(roomNo,firstNight,lastNight,ignoreId='',actualCheckInAt='',actualCheckOutAt='',registeringCurrentStay=false) {
  4445 |         const room=ROOMS.find(item=>item.no===String(roomNo)),range=quickBookingTimes(firstNight,lastNight),checkInAt=actualCheckInAt||range.checkInAt,checkOutAt=actualCheckOutAt||range.checkOutAt;
  4446 |         if(!adminCanMutate())return {reason:'관리자 최신 온라인 상태에서만 예약할 수 있습니다.',date:range.firstNight};
  4447 |         const rowReason=reservationHardBlockReason(room);if(rowReason)return {reason:rowReason,date:range.firstNight};
  4448 |         const cursor=dateObject(range.firstNight),end=dateObject(range.lastNight),currentReservation=currentOccupiedReservation(room),editingProjectedStay=!!(ignoreId&&currentReservation?.id===ignoreId),knownOccupancyEnd=occupiedReservationEnd(room);
  4449 |         if(!editingProjectedStay&&!registeringCurrentStay&&room.occupancy==='occupied'&&!knownOccupancyEnd)return {reason:'투숙 중 · 체크아웃 일정을 먼저 입력해 주세요.',date:checkInAt.slice(0,10)};
  4450 |         if(!editingProjectedStay&&!registeringCurrentStay&&occupiedStayNeedsCheckoutUpdate(room))return {reason:'투숙 중 · 예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.',date:checkInAt.slice(0,10)};
```

### occurrence 3 · line 4453

```html
  4437 |         const status=record.status==='notified'?'통보 완료':record.status==='draft'?'저장 전':record.status==='cancelled'?'취소됨':'배정됨';
  4438 |         return {name:maidName(maidId),status,maidId,assigned:record.status!=='cancelled'};
  4439 |       }
  4440 |       function quickBookingTimes(firstNight,lastNight) {
  4441 |         const ordered=[firstNight,lastNight].sort();
  4442 |         return {firstNight:ordered[0],lastNight:ordered[1],checkInAt:`${ordered[0]}T${DEFAULT_CHECKIN_TIME}`,checkOutAt:`${shiftIsoDate(ordered[1],1)}T${DEFAULT_CHECKOUT_TIME}`};
  4443 |       }
  4444 |       function quickReservationConflict(roomNo,firstNight,lastNight,ignoreId='',actualCheckInAt='',actualCheckOutAt='',registeringCurrentStay=false) {
  4445 |         const room=ROOMS.find(item=>item.no===String(roomNo)),range=quickBookingTimes(firstNight,lastNight),checkInAt=actualCheckInAt||range.checkInAt,checkOutAt=actualCheckOutAt||range.checkOutAt;
  4446 |         if(!adminCanMutate())return {reason:'관리자 최신 온라인 상태에서만 예약할 수 있습니다.',date:range.firstNight};
  4447 |         const rowReason=reservationHardBlockReason(room);if(rowReason)return {reason:rowReason,date:range.firstNight};
  4448 |         const cursor=dateObject(range.firstNight),end=dateObject(range.lastNight),currentReservation=currentOccupiedReservation(room),editingProjectedStay=!!(ignoreId&&currentReservation?.id===ignoreId),knownOccupancyEnd=occupiedReservationEnd(room);
  4449 |         if(!editingProjectedStay&&!registeringCurrentStay&&room.occupancy==='occupied'&&!knownOccupancyEnd)return {reason:'투숙 중 · 체크아웃 일정을 먼저 입력해 주세요.',date:checkInAt.slice(0,10)};
  4450 |         if(!editingProjectedStay&&!registeringCurrentStay&&occupiedStayNeedsCheckoutUpdate(room))return {reason:'투숙 중 · 예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.',date:checkInAt.slice(0,10)};
  4451 |         if(!editingProjectedStay&&room.occupancy==='occupied'&&knownOccupancyEnd&&checkInAt<knownOccupancyEnd)return {reason:`투숙 중 · ${quickDateLabel(knownOccupancyEnd.slice(0,10))} ${knownOccupancyEnd.slice(11,16)} 체크아웃 전`,date:checkInAt.slice(0,10)};
  4452 |         while(cursor<=end){const iso=dateIso(cursor),occupiedReason=editingProjectedStay||registeringCurrentStay?'':quickOccupiedDateBlockReason(room,iso),existing=reservationForNight(roomNo,iso);if(occupiedReason)return {reason:occupiedReason,date:iso};if(existing&&existing.id!==ignoreId)return {reason:`기존 예약 · ${quickRangeLabel(existing)}`,date:iso,reservation:existing};cursor.setDate(cursor.getDate()+1);}
  4453 |         const overlap=reservationOverlaps(roomNo,checkInAt,checkOutAt,ignoreId);if(overlap)return {reason:`기존 예약 · ${quickRangeLabel(overlap)}`,date:overlap.checkInAt.slice(0,10),reservation:overlap};
  4454 |         return null;
  4455 |       }
  4456 |       function reservationCheckoutTarget(reservation,date=reservation?.checkOutAt?.slice(0,10)||'',targetState=state,reservations=null) {
  4457 |         if(!reservation||!date)return null;
  4458 |         const room=ROOMS.find(item=>item.no===reservation.room);if(!room)return null;
  4459 |         const schedule=reservationTurnoverSchedule(reservation,reservations||activeReservationsFor(targetState,reservation.room));
  4460 |         return {id:`checkout-${room.no}-${date}`,room:room.no,type:room.type,kind:'퇴실 청소',date,checkout:reservation.checkOutAt.slice(11,16),checkin:schedule.checkin,deadline:schedule.deadline,source:'checkout',sourceLabel:'예약 체크아웃',reservationId:reservation.id,guestCount:reservationGuestCount(reservation),nextReservationId:schedule.nextReservationId};
  4461 |       }
  4462 |       function reservationAssignmentEntryForDate(reservation,date,{reopenSameReservation=false}={}) {
  4463 |         const freshTarget=reservationCheckoutTarget(reservation,date),expectedId=freshTarget?.id||`checkout-${reservation.room}-${date}`,matchesTarget=target=>target?.room===reservation.room&&target.kind==='퇴실 청소'&&((target.reservationId===reservation.id&&(!target.date||target.date===date))||(!target.reservationId&&target.date===date)||target.id===expectedId);
  4464 |         const freshRecord=(id,record)=>record?.status==='cancelled'&&freshTarget?reopenCancelledAssignmentForNewReservation(state,{...freshTarget,id},{allowSameReservation:reopenSameReservation}):record;
  4465 |         const liveTarget=liveAssignmentTargets().find(matchesTarget),liveRecord=liveTarget?freshRecord(liveTarget.id,state.assignments?.[liveTarget.id]):null;
  4466 |         if(liveRecord)return {id:liveTarget.id,record:liveRecord,item:{...freshTarget,id:liveTarget.id}};
  4467 |         const entries=Object.entries(state.assignments||{}),committedEntry=entries.find(([,record])=>record?.committedTarget?.reservationId===reservation.id&&matchesTarget(record.committedTarget))||entries.find(([id,record])=>id===expectedId&&(!record?.committedTarget?.reservationId||record.committedTarget.reservationId===reservation.id))||entries.find(([,record])=>matchesTarget(record?.committedTarget));
  4468 |         const id=committedEntry?.[0]||liveTarget?.id||expectedId,record=freshRecord(id,committedEntry?.[1]||null);
  4469 |         return {id,record,item:freshTarget?{...freshTarget,id}:null};
  4470 |       }
  4471 |       function notifiedMaidForAssignment(record) {
  4472 |         return record?.previousMaidId||(record?.status==='notified'?record.maidId:null)||null;
  4473 |       }
  4474 |       function syncAssignmentScheduleFromItem(record,item) {
  4475 |         if(!record||!item)return {record,item,changed:false,maidId:null};
  4476 |         if(record.status==='cancelled')return {record,item,changed:false,scheduleChanged:false,guestCountChanged:false,reservationChanged:false,maidId:null};
  4477 |         const committed=record.committedTarget,scheduleChanged=!committed||['checkout','checkin','deadline','nextReservationId'].some(key=>(item[key]||'')!==(committed[key]||'')),guestCountChanged=!committed||(item.guestCount??null)!==(committed.guestCount??null),reservationChanged=!committed||(item.reservationId||'')!==(committed.reservationId||''),changed=scheduleChanged||guestCountChanged||reservationChanged,maidId=notifiedMaidForAssignment(record);
  4478 |         record.scheduleChanged=scheduleChanged;
  4479 |         record.guestCountChanged=guestCountChanged;
  4480 |         record.reservationChanged=reservationChanged;
  4481 |         record.targetChanged=changed;
  4482 |         record.status=!record.maidId?'unassigned':record.maidId!==record.previousMaidId||record.order!==record.previousOrder||changed?'draft':'notified';
  4483 |         return {record,item,changed,scheduleChanged,guestCountChanged,reservationChanged,maidId};
  4484 |       }
  4485 |       function syncReservationAssignmentScheduleState(reservation,date,options={}) {
  4486 |         const {record,item}=reservationAssignmentEntryForDate(reservation,date,options);
  4487 |         return syncAssignmentScheduleFromItem(record,item);
```

### occurrence 4 · line 4663

```html
  4647 |         const registeringCurrentStay=!before&&currentStay===true&&room.occupancy==='occupied'&&!occupiedReservationEnd(room)&&checkInAt<=now&&checkOutAt>now;
  4648 |         if(currentStay===true&&!registeringCurrentStay)return {error:'현재 투숙 정보는 실제 체크인이 현재 시각 이전이고 예정 체크아웃이 현재 시각 이후일 때 저장할 수 있습니다.'};
  4649 |         if(checkInAt<now&&!registeringCurrentStay&&!linkedCurrentStay&&(!before||checkInAt!==before.checkInAt))return {error:'새 예약과 미래 예약 변경은 현재 시각 이후의 체크인으로 입력해 주세요.'};
  4650 |         if(linkedCurrentStay&&checkInAt>now)return {error:'현재 투숙 중인 예약의 체크인을 미래 시각으로 옮길 수 없습니다. 실제 입실 시각을 확인해 주세요.'};
  4651 |         const payload={roomNo:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount},duplicateReservation=!id?activeReservationsFor(state,room.no).find(item=>reservationPayloadMatches(item,payload))||null:null,unchangedReservation=!!previous&&reservationPayloadMatches(previous,payload);
  4652 |         if(duplicateReservation)return {reservation:duplicateReservation,previous:null,duplicate:true,unchanged:true};
  4653 |         if(unchangedReservation)return {reservation:previous,previous:before,duplicate:true,unchanged:true};
  4654 |         const scheduleChanged=!!before&&(before.checkInAt!==checkInAt||before.checkOutAt!==checkOutAt),guestCountChanged=!!before&&reservationGuestCount(before)!==resolvedGuestCount,candidate={...(previous||{}),id:id||'reservation-candidate',room:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,status:'active'},prospectiveReservations=[...beforeReservations.filter(item=>item.id!==candidate.id),candidate].sort((left,right)=>left.checkInAt.localeCompare(right.checkInAt)),cleaningChanges=reservationCleaningChanges(beforeReservations,prospectiveReservations),roomCleaningChanged=cleaningChanges.length>0;
  4655 |         if(roomCleaningChanged&&reservationCleaningChangeTouchesPublic(cleaningChanges,room.no))return {error:`${room.no}호의 영향을 받는 청소 작업이 이미 공개되어 예약 일정·인원을 바로 바꿀 수 없습니다. 청소 화면에서 공개·담당 영향을 먼저 조율해 주세요.`};
  4656 |         if(roomCleaningChanged&&reservationCleaningChangeTouchesRandom(cleaningChanges))return {error:'이 예약과 연결된 랜덤 배정 초안이 있습니다. 해당 청소 배정에서 초안을 되돌린 뒤 다시 저장해 주세요.'};
  4657 |         const activeAttempt=activeUnfinishedAttempt(room.no),linkedAttemptBefore=before?reservationAutomaticCleaningAttempt(before,activeAttempt):null,attemptScheduleLocked=activeAttempt&&(!!activeAttempt.startedAt||roomPinWasViewed(room.no,activeAttempt.id)||activeAttempt.accessReviewRequired||!['scheduled','claimed','unassigned'].includes(state.jobs[room.no]));
  4658 |         if(linkedAttemptBefore?.performerId&&before.checkOutAt.slice(0,10)!==checkOutAt.slice(0,10))return {error:`${room.no}호 퇴실 청소 담당의 업무일이 이미 ${quickDateLabel(before.checkOutAt.slice(0,10))}로 잡혀 있습니다. 체크아웃 날짜를 바꾸려면 청소 화면에서 담당·업무일을 먼저 조율해 주세요.`};
  4659 |         if(attemptScheduleLocked){
  4660 |           const workDate=attemptWorkDate(activeAttempt,state.selectedDate),timingChanged=reservationWorkTimingFingerprint(beforeReservations,workDate)!==reservationWorkTimingFingerprint(prospectiveReservations,workDate);
  4661 |           if(timingChanged)return {error:`${room.no}호는 연결된 퇴실 청소 수행 회차가 있거나 PIN 사용이 시작되어 출입 시각·준비 마감을 바꿀 수 없습니다. 객실의 출입·청소 충돌을 먼저 확인해 주세요.`};
  4662 |         }
  4663 |         const exactOverlap=reservationOverlaps(room.no,checkInAt,checkOutAt,id);
  4664 |         if(exactOverlap)return {error:`${room.no}호 ${quickRangeLabel(exactOverlap)} · 기존 예약과 실제 체크인·체크아웃 시각이 겹칩니다.`,conflict:exactOverlap};
  4665 |         const firstNight=checkInAt.slice(0,10),lastNight=shiftIsoDate(checkOutAt.slice(0,10),-1),conflict=quickReservationConflict(room.no,firstNight,lastNight,id,checkInAt,checkOutAt,registeringCurrentStay);
  4666 |         if(conflict)return {error:`${room.no}호 ${quickDateLabel(conflict.date)} · ${conflict.reason}`,conflict};
  4667 |         const reservationId=id||`reservation-${room.no}-${checkInAt.slice(0,10).replaceAll('-','')}-${++state.reservationSequence}`;
  4668 |         const reservation=previous||{id:reservationId,room:room.no,source,status:'active',createdAt:`${state.selectedDate}T${state.time}`};
  4669 |         Object.assign(reservation,{room:room.no,checkInAt,checkOutAt,guestCount:resolvedGuestCount,source:previous?.source||source,status:'active',updatedAt:`${state.selectedDate}T${state.time}`});
  4670 |         if(!previous)state.reservations.push(reservation);
  4671 |         if(registeringCurrentStay||linkedCurrentStay){room.actualCheckinAt=checkInAt;room.plannedCheckoutAt=checkOutAt;room.currentStayReservationId=reservation.id;}
  4672 |         syncReservationCleaningDraft(reservation,before);
  4673 |         syncUnstartedReservationCleaningAttempt(reservation,linkedAttemptBefore);
  4674 |         const checkoutDate=reservation.checkOutAt.slice(0,10),checkoutDateChanged=!before||before.checkOutAt.slice(0,10)!==checkoutDate;
  4675 |         if(checkoutDateChanged){
  4676 |           const {record,changed,maidId}=syncReservationAssignmentScheduleState(reservation,checkoutDate,{reopenSameReservation:true});
  4677 |           if(record&&maidId&&changed)appendEvent(`${room.no}호 예약 ${before?'체크아웃 이동':'접수'} · 청소 재통보 필요`,`${reservation.checkOutAt.slice(11,16)} 체크아웃 · ${maidName(maidId)}의 기존 통보 일정 유지`,{maidIds:[maidId],roomId:room.no});
  4678 |         }
  4679 |         syncAdjacentReservationCleaningSchedules(room.no,beforeReservations);
  4680 |         projectReservationState(state,room.no);state.reservationSaved=true;
  4681 |         const guestChange=guestCountChanged?` · 숙박 인원 ${reservationGuestCount(before)}명 → ${resolvedGuestCount}명`:` · 숙박 인원 ${resolvedGuestCount}명`;
  4682 |         appendEvent(`${room.no}호 예약 ${previous?'변경':'접수'}`,`${previous?`${quickRangeLabel(before)} → `:''}${quickRangeLabel(reservation)} · ${reservationNights(reservation)}박${guestChange}${previous?' · 예약정보 수정':' · 퇴실 청소 준비'}`,{roomId:room.no,dedupeKey:`reservation:${reservation.id}:${reservationFingerprint(reservation)}`});
  4683 |         return {reservation,previous:before};
  4684 |       }
  4685 |       function clearOrphanedReservationDraftJob(roomNo) {
  4686 |         const remainingCleaningDraft=(state.drafts||[]).some(draft=>draft.room===roomNo&&['퇴실 청소','연박 청소','재청소'].includes(draft.kind)),independentTarget=(state.manualAssignmentTargets||[]).some(target=>!target.cancelled&&target.room===roomNo),unfinished=activeUnfinishedAttempt(roomNo);
  4687 |         if(state.jobs[roomNo]!=='draft'||remainingCleaningDraft||independentTarget||unfinished)return false;
  4688 |         delete state.jobs[roomNo];return true;
  4689 |       }
  4690 |       function removeQuickReservation(reservationId,{undo=false}={}) {
  4691 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active'),last=state.quickLastCreated;if(!undo||!reservation||last?.reservationId!==reservationId||Date.now()-Number(last.createdAt)>10500)return false;
  4692 |         const impact=reservationCancellationImpact(reservation),hasPublishedDraft=impact.drafts.some(draft=>state.publications?.[draft.id]),assigned=!!(impact.selectedMaidId||impact.notifiedMaidId||impact.manualTarget||impact.connectedAttempt);if(impact.blockedReason||hasPublishedDraft||assigned)return false;
  4693 |         const beforeReservations=activeReservationsFor(state,reservation.room).map(item=>({...item}));
  4694 |         const removedDraftIds=new Set(impact.drafts.map(draft=>draft.id));reservation.status='cancelled';reservation.cancelledAt=`${state.selectedDate}T${state.time}`;reservation.cancelledBy='관리자 · 데모';reservation.cancelReason='방금 접수 실행 취소';reservation.updatedAt=reservation.cancelledAt;state.drafts=state.drafts.filter(draft=>draft.reservationId!==reservationId);state.selectedDrafts=state.selectedDrafts.filter(id=>!removedDraftIds.has(id));clearOrphanedReservationDraftJob(reservation.room);
  4695 |         if(impact.assignmentRecord)cancelReservationAssignmentRecord(impact.assignmentRecord,{targetId:impact.assignmentEntry.id,room:reservation.room,date:impact.checkoutDate,reservationId:reservation.id,reason:'방금 접수 실행 취소',target:impact.assignmentItem});
  4696 |         syncAdjacentReservationCleaningSchedules(reservation.room,beforeReservations);projectReservationState(state,reservation.room);appendEvent(`${reservation.room}호 예약 접수 실행 취소`,`${quickRangeLabel(reservation)} · 퇴실 청소 준비도 취소`,{roomId:reservation.room});return true;
  4697 |       }
```

### occurrence 5 · line 4723

```html
  4707 |         const beforeReservations=activeReservationsFor(state,reservation.room).map(item=>({...item})),removedDraftIds=new Set(impact.drafts.map(draft=>draft.id));
  4708 |         reservation.status='cancelled';reservation.cancelledAt=`${state.selectedDate}T${state.time}`;reservation.cancelledBy='관리자 · 데모';reservation.cancelReasonCode=reasonCode;reservation.cancelReason=reason;reservation.updatedAt=reservation.cancelledAt;
  4709 |         state.drafts=state.drafts.filter(draft=>draft.reservationId!==reservation.id);state.selectedDrafts=state.selectedDrafts.filter(id=>!removedDraftIds.has(id));const clearedDraftJob=clearOrphanedReservationDraftJob(reservation.room);
  4710 |         let cleaningEffect=`퇴실 청소 준비 ${impact.privateDrafts.length}건 취소${clearedDraftJob?' · 현재 배정 준비 상태 해제':''}`;
  4711 |         if(impact.manualTarget&&impact.assignmentRecord){
  4712 |           const synced=syncAssignmentScheduleFromItem(impact.assignmentRecord,impact.manualTarget);cleaningEffect=`독립 현장 청소 요청 ${impact.manualTarget.id} 유지`;
  4713 |           if(synced.maidId)appendEvent(`${reservation.room}호 예약 취소 · 현장 청소 요청 유지`,synced.changed?`${quickDateLabel(impact.checkoutDate)} 현장 요청 일정과 기존 통보가 달라 ${maidName(synced.maidId)} 재통보 필요`:`${maidName(synced.maidId)} 담당과 현장 요청 일정 유지`,{maidIds:[synced.maidId],roomId:reservation.room});
  4714 |         } else if(impact.assignmentRecord) {
  4715 |           const cancelled=cancelReservationAssignmentRecord(impact.assignmentRecord,{targetId:impact.assignmentEntry.id,room:reservation.room,date:impact.checkoutDate,reservationId:reservation.id,reason:`예약 취소 · ${reason}`,target:impact.assignmentItem});
  4716 |           if(cancelled.alreadyCancelled)cleaningEffect='퇴실 청소 대상 이미 취소됨 · 기존 취소 이력 보존';else if(cancelled.cancelledMaidId)cleaningEffect=`청소 담당 ${maidName(cancelled.cancelledMaidId)} 해제 · 기존 순서와 일정 보존`;
  4717 |         }
  4718 |         syncAdjacentReservationCleaningSchedules(reservation.room,beforeReservations);projectReservationState(state,reservation.room);if(state.quickLastCreated?.reservationId===reservation.id)state.quickLastCreated=null;
  4719 |         appendEvent(`${reservation.room}호 예약 취소`,`${quickRangeLabel(reservation)} · ${reservationNights(reservation)}박 · 숙박 인원 ${reservationGuestCount(reservation)}명 · 사유 ${reason} · ${cleaningEffect} · 외부 OTA/PMS 예약 별도 확인`,{roomId:reservation.room});
  4720 |         return {reservation,impact,reason,cleaningEffect};
  4721 |       }
  4722 |       function quickCellMarkup(room,iso,rowIndex,dayIndex,todayIso=kstTodayIso()) {
  4723 |         const reservation=reservationForNight(room.no,iso),rowReason=quickRoomBlockReason(room),occupiedReason=quickOccupiedDateBlockReason(room,iso),isPast=iso<todayIso,isMonthStart=dayIndex===0||dateObject(iso).getDate()===1,pastReason=isPast?'지난 날짜 · 조회만 가능':'',defaultRange=quickBookingTimes(iso,iso),timeConflict=!reservation?reservationOverlaps(room.no,defaultRange.checkInAt,defaultRange.checkOutAt):null,cellReason=pastReason||rowReason||occupiedReason||(timeConflict?`기존 예약 시각 겹침 · ${quickRangeLabel(timeConflict)}`:''),type=ROOM_TYPES[room.type],elevator=elevatorLabel(room),focusDate=state.quickReservationAnchorDate,dayOffset=reservation?Math.round((dateObject(iso)-dateObject(reservation.checkInAt.slice(0,10)))/86400000):0,nights=reservationNights(reservation),start=reservation&&dayOffset===0,end=reservation&&dayOffset===nights-1,dateClasses=`${isPast?' is-past':''}${isMonthStart?' is-month-start':''}`;
  4724 |         if(reservation){
  4725 |           const label=nights===1?'1박':start?`연박 ${nights}박`:'',aria=`${room.no}호, ${type.name}, ${elevator}, ${quickDateLabel(iso)}, ${nights===1?'1박 예약':`연박 ${nights}박`}, 숙박 인원 ${reservationGuestCount(reservation)}명, ${quickRangeLabel(reservation)}`;
  4726 |           return `<button class="quick-date-cell is-reserved ${nights===1?'is-single':'is-multi'} ${start?'is-start':''} ${end?'is-end':''}${dateClasses}" type="button" role="gridcell" tabindex="${rowIndex===0&&iso===focusDate?'0':'-1'}" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-date="${iso}" aria-label="${esc(aria)}" title="${esc(`${quickRangeLabel(reservation)} · ${reservationGuestCount(reservation)}명`)}"><span class="quick-cell-label">${esc(label)}</span></button>`;
  4727 |         }
  4728 |         if(cellReason){const aria=`${room.no}호, ${type.name}, ${elevator}, ${quickDateLabel(iso)}, 예약 불가, ${cellReason}`;return `<button class="quick-date-cell is-locked${dateClasses}" type="button" role="gridcell" tabindex="${rowIndex===0&&iso===focusDate?'0':'-1'}" data-room="${room.no}" data-date="${iso}" aria-disabled="true" aria-label="${esc(aria)}" title="${esc(cellReason)}">${icon('lock','icon-sm')}</button>`;}
  4729 |         const aria=`${room.no}호, ${type.name}, ${elevator}, ${quickDateLabel(iso)}, 예약 가능. 마우스는 클릭 또는 드래그, 터치는 길게 누른 뒤 가로 드래그`;
  4730 |         return `<button class="quick-date-cell${dateClasses}" type="button" role="gridcell" tabindex="${rowIndex===0&&iso===focusDate?'0':'-1'}" data-quick-cell="true" data-bookable="true" data-room="${room.no}" data-date="${iso}" aria-label="${esc(aria)}"></button>`;
  4731 |       }
  4732 |       function renderQuickReservation() {
  4733 |         const actualToday=refreshQuickReservationActualToday({rerender:false}),dates=quickWindowDates(),rooms=quickFilteredRooms(),windowReservations=activeReservationsFor(state).filter(item=>reservationInQuickWindow(item)),bookedRooms=new Set(windowReservations.map(item=>item.room)),bookedNights=windowReservations.reduce((total,reservation)=>total+dates.filter(date=>reservationContainsNight(reservation,date)).length,0),blockedRooms=ROOMS.filter(room=>quickRoomBlockReason(room)||(room.occupancy==='occupied'&&(!occupiedReservationEnd(room)||occupiedStayNeedsCheckoutUpdate(room)))).length,windowLabel=quickWindowLabel();
  4734 |         const headers=dates.map((iso,dayIndex)=>{const value=dateObject(iso),meta=calendarDayMeta(iso),today=iso===actualToday,isPast=iso<actualToday,isMonthStart=dayIndex===0||value.getDate()===1;return `<div class="quick-day-header ${meta.classes} ${today?'today':''} ${isPast?'is-past':''} ${isMonthStart?'is-month-start':''}" role="columnheader" data-quick-date="${iso}" aria-label="${esc(calendarDateAriaLabel(iso,{today}))}" ${meta.holiday?`title="${esc(meta.holiday.name)}"`:''}><strong>${quickHeaderDateLabel(iso,dayIndex)}</strong><span>${meta.weekdayLabel}</span>${meta.holiday?'<small class="calendar-holiday-mark" aria-hidden="true">휴</small>':''}</div>`;}).join('');
  4735 |         const headerRow=`<div class="quick-grid-row quick-grid-header" role="row"><div class="quick-room-header" role="columnheader">객실 · 유형 · 엘베</div>${headers}</div>`;
  4736 |         const rows=rooms.map((room,rowIndex)=>{const type=ROOM_TYPES[room.type],blocked=quickRoomBlockReason(room);return `<div class="quick-grid-row quick-grid-data-row" role="row" aria-rowindex="${rowIndex+2}" data-quick-row="${room.no}"><div class="quick-room-info ${blocked?'row-locked':''}" role="rowheader"><button class="quick-room-link" type="button" tabindex="${rowIndex===0?'0':'-1'}" data-action="room-detail" data-id="${room.no}" aria-label="${room.no}호 객실 상세 열기"><span class="quick-room-number">${room.no}호</span><span class="quick-room-copy"><strong>${esc(type.name)} · ${esc(room.elevator||'미기재')}</strong>${blocked?`<span class="quick-room-block">${esc(blocked)}</span>`:''}</span></button></div>${dates.map((iso,dayIndex)=>quickCellMarkup(room,iso,rowIndex,dayIndex,actualToday)).join('')}</div>`;}).join('');
  4737 |         const grid=rooms.length?`<div class="quick-grid" role="grid" aria-label="${esc(windowLabel)} 29일 객실별 간편 예약" aria-rowcount="${rooms.length+1}" aria-colcount="${dates.length+1}" style="--quick-days:${dates.length}">${headerRow}${rows}</div>`:`<div class="quick-empty-state"><div><h3>조건에 맞는 객실이 없습니다</h3><p>검색어 또는 객실 유형 필터를 바꿔 주세요.</p></div></div>`;
  4738 |         const mobileHeader=rooms.length?`<div id="quick-grid-mobile-header" class="quick-grid-mobile-header" role="region" aria-label="${esc(windowLabel)} 고정 날짜 머리글"><div class="quick-grid quick-grid-mobile-header-grid" role="table" aria-label="${esc(windowLabel)} 날짜 열" style="--quick-days:${dates.length}">${headerRow}</div></div>`:'';
  4739 |         return renderCoach()+renderNetworkNotice()+`<div class="quick-booking-page"><section class="card quick-booking-hero"><div class="quick-booking-hero-copy"><span class="quick-booking-kicker">빠른 예약 입력</span><h2>목업 기준일 8월 15일 전후 29일을 한 화면에서 예약하세요</h2><p>8월 15일의 7일 전부터 21일 뒤까지 월 경계 없이 이어서 표시합니다.</p></div><div class="quick-booking-boundary"><strong>데모 와이어프레임 · 실제 데이터 아님</strong>외부 OTA/PMS 예약 원본은 변경하지 않습니다.</div></section><section class="card quick-booking-toolbar" aria-label="간편 예약 필터"><div class="quick-month-tools"><button class="icon-btn" type="button" data-action="quick-month-shift" data-offset="-7" aria-label="이전 7일">${icon('chevronLeft')}</button><div class="quick-month-label" aria-label="표시 기간 ${esc(windowLabel)}">${icon('calendar','icon-sm')}<span>${esc(windowLabel)}</span><small>${state.quickReservationFollowsToday===false?'이동한 29일':'8월 15일 기준 29일'}</small></div><button class="icon-btn" type="button" data-action="quick-month-shift" data-offset="7" aria-label="다음 7일">${icon('chevronRight')}</button><button class="btn btn-outline" type="button" data-action="quick-month-today">오늘</button></div><label class="quick-toolbar-field">객실번호 검색<input class="input-control" type="search" inputmode="numeric" data-control="quick-reservation-search" value="${esc(state.quickReservationSearch)}" placeholder="예: 516" autocomplete="off"></label><label class="quick-toolbar-field">객실 유형<select class="select-control" data-control="quick-reservation-type"><option value="all">유형 전체</option>${Object.entries(ROOM_TYPES).map(([id,type])=>`<option value="${id}" ${state.quickReservationType===id?'selected':''}>${esc(type.name)}</option>`).join('')}</select></label></section><section class="card quick-booking-summary" aria-label="${esc(windowLabel)} 29일 예약 요약"><div><span>예약 건수</span><strong>${windowReservations.length}건</strong><small>표시 범위와 겹치는 예약</small></div><div><span>예약 객실</span><strong>${bookedRooms.size}개</strong><small>전체 ${ROOMS.length}개</small></div><div><span>숙박 칸</span><strong>${bookedNights}박</strong><small>선택한 29일 기준</small></div></section><div class="quick-booking-guide"><div class="quick-booking-guide-copy"><strong>마우스: 클릭·드래그 / 터치: 0.35초 길게 누른 뒤 같은 행에서 가로 드래그</strong>월말과 월초도 하나의 표로 이어집니다. 세로로 움직이면 선택을 취소하고 화면만 스크롤합니다.</div><div class="quick-booking-legend" aria-label="예약 상태 범례"><span class="quick-legend-item"><i class="quick-legend-swatch single">1박</i>별도 1박</span><span class="quick-legend-item"><i class="quick-legend-swatch multi">연박</i>하나의 연박</span><span class="quick-legend-item"><i class="quick-legend-swatch locked">${icon('lock','icon-sm')}</i>예약 불가</span><span class="quick-legend-item"><i class="quick-legend-swatch preview"></i>선택 중</span></div></div><section class="card quick-grid-shell"><div class="quick-grid-status"><strong>${esc(windowLabel)}</strong><span>29일 · 표시 ${rooms.length}개 객실 · 예약 불가 객실 ${blockedRooms}개</span><span class="quick-status-spacer"></span><span>${state.quickReservationFollowsToday===false?'선택 기준 -7일 / +21일':'8월 15일 기준 -7일 / +21일'} · 7일씩 이동</span></div>${mobileHeader}<div id="quick-grid-scroller" class="quick-grid-scroller" tabindex="0" aria-label="객실 예약표 스크롤 영역">${grid}</div></section></div>`;
  4740 |       }
  4741 |       function quickGridUsesInternalVerticalScroll() { return !window.matchMedia('(max-width: 720px)').matches; }
  4742 |       function quickGridAnchorScrollLeft(scroller) {
  4743 |         const anchor=scroller?.querySelector(`[data-quick-date="${state.quickReservationAnchorDate}"]`),roomHeader=scroller?.querySelector('.quick-room-header');
  4744 |         return anchor&&roomHeader?Math.max(0,anchor.offsetLeft-roomHeader.offsetWidth):0;
  4745 |       }
  4746 |       function syncQuickGridHorizontalScroll(source) {
  4747 |         const scroller=document.getElementById('quick-grid-scroller'),header=document.getElementById('quick-grid-mobile-header');
  4748 |         if(!source||source!==scroller&&source!==header)return;
  4749 |         const left=Math.max(0,Number(source.scrollLeft)||0),peer=source===scroller?header:scroller;
  4750 |         if(peer&&Math.abs(peer.scrollLeft-left)>1)peer.scrollLeft=left;
  4751 |         state.quickGridScrollLeft=left;
  4752 |       }
  4753 |       function rememberQuickGridViewport() {
  4754 |         const scroller=document.getElementById('quick-grid-scroller');if(!scroller)return;
  4755 |         state.quickGridScrollLeft=scroller.scrollLeft;state.quickGridScrollTop=quickGridUsesInternalVerticalScroll()?scroller.scrollTop:0;
  4756 |       }
  4757 |       function restoreQuickGridViewport(focusSelector='') {
```

### occurrence 6 · line 7791

```html
  7775 |         if(['all','vacant','available','blocked','cleaning','occupied','checkout-inspection','extra-guests','candle','issues','early','late'].includes(requestedRoomFilter))state.roomFilter=requestedRoomFilter;
  7776 |         if(['all',...Object.keys(ROOM_TYPES)].includes(params.get('type')))state.roomTypeFilter=params.get('type');
  7777 |         if(['all',...Object.keys(ROOM_TYPES)].includes(params.get('assignmentType')))state.assignmentTypeFilter=params.get('assignmentType');
  7778 |         if(/^\d{0,6}$/.test(params.get('q')||''))state.roomSearch=params.get('q')||'';
  7779 |         const bookingAnchor=params.get('bookingAnchor')||'',legacyBookingMonth=params.get('bookingMonth')||'';
  7780 |         if(/^\d{4}-(0[1-9]|1[0-2])-([0-2]\d|3[01])$/.test(bookingAnchor)){state.quickReservationAnchorDate=bookingAnchor;state.quickReservationFollowsToday=false;}
  7781 |         else if(/^\d{4}-(0[1-9]|1[0-2])$/.test(legacyBookingMonth)){state.quickReservationAnchorDate=`${legacyBookingMonth}-15`;state.quickReservationFollowsToday=false;}
  7782 |         else{state.quickReservationAnchorDate=DEMO_TODAY;state.quickReservationFollowsToday=true;}
  7783 |         if(['all',...Object.keys(ROOM_TYPES)].includes(params.get('bookingType')))state.quickReservationType=params.get('bookingType');
  7784 |         if(/^\d{0,6}$/.test(params.get('bookingQ')||''))state.quickReservationSearch=params.get('bookingQ')||'';
  7785 |         const detailValue=params.get('detail');
  7786 |         if(detailValue){state.detail=null;const separator=detailValue.indexOf(':'),type=separator>0?detailValue.slice(0,separator):'',id=separator>0?detailValue.slice(separator+1):'';if(detailAllowedForRole(type,state.role)&&id)state.detail={type,id,...(params.get('mode')?{mode:params.get('mode')}:{})};}
  7787 |         if(state.cleaningTab==='assignment-today')activateNotifiedAssignmentsForDate(state.selectedDate);
  7788 |         return true;
  7789 |       }
  7790 |       function installCastleTestApi() {
  7791 |         const findReservationInput=(startOffset=30)=>{for(let offset=startOffset;offset<startOffset+120;offset++){const date=shiftIsoDate(state.selectedDate,offset),range=quickBookingTimes(date,date);for(const room of ROOMS){if(roomIsOnHold(room.no)||reservationHardBlockReason(room))continue;if(!reservationOverlaps(room.no,range.checkInAt,range.checkOutAt))return {roomNo:room.no,checkInAt:range.checkInAt,checkOutAt:range.checkOutAt,guestCount:guestPolicyForRoom(room.no).defaultGuestCount,source:'test'};}}throw new Error('중복 방지 테스트용 예약 가능 객실을 찾지 못했습니다.');};
  7792 |         window.__CASTLE_TEST__=Object.freeze({
  7793 |           snapshot:()=>durableLedgerSnapshot(state),fingerprint:()=>durableLedgerFingerprint(state),assertUnique:()=>assertNoDuplicateDurableRecords(state),
  7794 |           repeatRender:(count=1)=>{const before=durableLedgerFingerprint(state);for(let index=0;index<Math.max(1,Number(count)||1);index++)render();const after=durableLedgerFingerprint(state);return {before,after,equal:before===after,snapshot:durableLedgerSnapshot(state)};},
  7795 |           resetScenario:(scenario=0)=>{state=makeScenario(Number(scenario)||0);hydrateTemplateSnapshotsForState();rawCloseModal();render();return durableLedgerSnapshot(state);},
  7796 |           findReservationInput,
  7797 |           createReservationTest:(startOffset=30)=>{const input=findReservationInput(startOffset),result=upsertReservationRecord(input);return {input,result,snapshot:durableLedgerSnapshot(state)};},
  7798 |           upsertReservation:input=>upsertReservationRecord(input),
  7799 |           prepareSubmission:(roomNo='528')=>{const no=String(roomNo),attemptId=currentAttemptId(no),attempt=state.cleaningAttempts?.[attemptId],task=taskState(no);if(!attempt||!task)throw new Error(`${no}호 청소 회차가 없습니다.`);state.jobs[no]='upload';attempt.status='upload';attempt.completedAt=attempt.completedAt||`${state.selectedDate} ${state.time}`;task.uploads.forEach(upload=>{if(upload.required&&upload.status!=='done')upload.status='done';});return {room:no,attemptId,requiredDone:taskRequirements(no).requiredDone};},
  7800 |           submitCleaning:roomNo=>createCleaningSubmissionRecord(String(roomNo)),
  7801 |           confirmEarning:roomNo=>confirmCleaningEarning(String(roomNo)),
  7802 |           paymentTestContext:()=>{for(const maid of MAIDS){const context=paymentContextFor(state.adminPayWeek,maid.id);if(context&&!context.meta.locked&&context.totals.confirmed>0)return {weekStart:context.cfg.start,maidId:maid.id,status:context.meta.status,amount:context.totals.confirmed};}return null;},
  7803 |           setPaymentStatus:(weekStart,maidId,status)=>{const context=paymentContextFor(weekStart,maidId);if(!context)throw new Error('지급 테스트 대상을 찾을 수 없습니다.');const before=durableLedgerSnapshot(state);setPaymentStatusFor(context,status);const record=state.paymentRecords[paymentRecordKey(weekStart,maidId)]||null;assertNoDuplicateDurableRecords(state);return {before,record,after:durableLedgerSnapshot(state)};},
  7804 |           manualCleaningCandidates:()=>ROOMS.filter(room=>!roomIsOnHold(room.no)&&!state.roomStopped[room.no]&&!activeUnfinishedAttempt(room.no)&&!(currentSubmission(room.no)&&currentSubmission(room.no).status!=='approved')&&!roomHasCleaningWorkflow(room.no)).map(room=>({room:room.no,occupancy:room.occupancy,type:room.type})),
  7805 |           roomCleaningControls:()=>ROOMS.map(room=>({room:room.no,...roomCleaningControl(room.no)})),
  7806 |           manualCleaningState:roomNo=>{const no=String(roomNo),request=activeManualCleaningRequest(no),target=manualCleaningRequestTarget(request),assignment=request?state.assignments?.[request.targetId]:null;return {room:no,request:request?{...request}:null,target:target?{...target}:null,assignment:assignment?{...assignment}:null,control:roomCleaningControl(no),presentation:roomPresentation(no),filtered:filteredRooms().some(room=>room.no===no),manualTargetCount:(state.manualAssignmentTargets||[]).filter(item=>item.id===request?.targetId&&!item.cancelled).length};},
  7807 |           setManualCleaning:(roomNo,on=true)=>on?createManualCleaningRequest(String(roomNo)):cancelManualCleaningRequest(String(roomNo)),
  7808 |           completeManualCleaning:(roomNo)=>{const no=String(roomNo),request=activeManualCleaningRequest(no);if(!request)return null;const target=manualCleaningRequestTarget(request),attempt=beginCleaningAttempt(no,{performerId:'m1',performerName:'김민지1',reason:'수동 청소 테스트',kind:request.kind,workDate:request.date,effectiveDate:request.date,workTargetId:request.targetId,templateSnapshot:target?.templateSnapshot||templateSnapshotFor(no,request.kind)});attempt.completedAt=`${state.selectedDate} ${state.time}`;attempt.status='upload';state.jobs[no]='upload';return completeManualCleaningRequestForAttempt(no,attempt);},
  7809 |           showRoom:(roomNo)=>{state.role='admin';state.adminView='rooms';state.detail={type:'room',id:String(roomNo)};render();return roomPresentation(String(roomNo));},
  7810 |           setOperationalMoment:(date,time)=>{state.selectedDate=String(date);state.time=String(time);projectReservationState(state);render();return {date:state.selectedDate,time:state.time};},
  7811 |           occupancyState:roomNo=>{const no=String(roomNo),room=ROOMS.find(item=>item.no===no),current=reservationAtOperationalMoment(no),last=latestCheckedOutReservationForRoom(no);return {room:no,occupancy:room?.occupancy,currentReservationId:current?.id||null,lastCheckoutReservationId:last?.id||null,actualCheckinAt:room?.actualCheckinAt||null,actualCheckoutAt:room?.actualCheckoutAt||null,plannedCheckoutAt:room?.plannedCheckoutAt||null,presentation:roomPresentation(no),checkoutCleaningDue:roomCheckoutCleaningDue(no),checkoutInspectionPending:checkoutInspectionPending(no)};},
  7812 |           checkoutInspectionState:roomNo=>{const no=String(roomNo),reservation=checkoutInspectionReservationForRoom(no),record=reservation?checkoutInspectionRecordFor(reservation.id):null;return {room:no,reservation:reservation?{...reservation}:null,pending:checkoutInspectionPending(no),record:record?{...record}:null,completion:checkoutInspectionCompletion(no),presentation:roomPresentation(no),filtered:filteredRooms().some(room=>room.no===no)};},
  7813 |           completeCheckoutInspection:(roomNo,method='manual')=>completeCheckoutInspection(String(roomNo),{method}),
  7814 |           completeCheckoutInspectionByCleaning:roomNo=>{const no=String(roomNo),reservation=checkoutInspectionReservationForRoom(no),attempt=Object.values(state.cleaningAttempts||{}).find(item=>item.room===no&&item.kind==='퇴실 청소'&&item.reservationIdSnapshot===reservation?.id)||null;if(!reservation||!attempt)throw new Error('퇴실 청소 회차를 찾을 수 없습니다.');attempt.completedAt=attempt.completedAt||`${state.selectedDate} ${state.time}`;attempt.status='upload';state.jobs[no]='upload';return completeCheckoutInspectionForAttempt(no,attempt);},
  7815 |           setReservationTimes:(reservationId,checkInAt,checkOutAt)=>{const reservation=state.reservations.find(item=>item.id===String(reservationId));if(!reservation)throw new Error('예약을 찾을 수 없습니다.');reservation.checkInAt=String(checkInAt);reservation.checkOutAt=String(checkOutAt);reservation.updatedAt=`${state.selectedDate}T${state.time}`;projectReservationState(state,reservation.room);render();return {...reservation};},
  7816 |           setRoomFilter:filter=>{state.role='admin';state.adminView='rooms';state.detail=null;state.roomFilter=filter;render();return filteredRooms().map(room=>room.no);},
  7817 |           showTemplateList:()=>{state.role='admin';state.detail={type:'templates',id:'all'};render();return Object.values(templateCatalog()).map(template=>({id:template.id,...templateSlotStats(template)}));},
  7818 |           showTemplate:(templateId,roomNo=null)=>{const template=templateById(String(templateId));if(!template)throw new Error('템플릿을 찾을 수 없습니다.');if(roomNo&&!templateRooms(template).some(room=>room.no===String(roomNo)))throw new Error('템플릿 타입과 객실이 일치하지 않습니다.');state.role='admin';state.detail={type:'template',id:template.id,mode:'view'};render();return templateParityData(template.id,roomNo);},
  7819 |           templateParityData:(templateId,roomNo=null)=>templateParityData(String(templateId),roomNo),
  7820 |           typeTemplateParity:(typeId,kind='퇴실 청소')=>typeTemplateParity(String(typeId),kind),
  7821 |           maidTemplateParity:roomNo=>{const no=String(roomNo),task=taskState(no),snapshot=task.templateSnapshot||snapshotForAttempt(no,state.cleaningAttempts?.[task.attemptId]),expected=photoSlotContract(snapshot?.photos||[]),actual=photoSlotContract(task.uploads||[]);return {room:no,version:snapshot?.version||null,expected,actual,same:JSON.stringify(expected)===JSON.stringify(actual)};},
  7822 |           inspectionTemplateParity:roomNo=>{const no=String(roomNo),submission=currentSubmission(no),attempt=submission?.attemptId?state.cleaningAttempts?.[submission.attemptId]:null,template=templateSnapshotForSubmission(no,submission,attempt),expected=photoSlotContract(template?.photos||[]),actual=photoSlotContract(inspectionTemplateUploadItems(no,template,submission,attempt));return {room:no,submissionId:submission?.id||null,version:template?.version||null,expected,actual,same:JSON.stringify(expected)===JSON.stringify(actual)};},
  7823 |           submissionEvidenceParity:roomNo=>{const no=String(roomNo),raw=currentSubmissionRecord(no),submission=currentSubmission(no),template=raw?.templateSnapshot,report=rawBombRoomReportForSubmission(raw),expectedIds=(template?.photos||[]).map(item=>item.id),actualIds=(raw?.uploads||[]).map(item=>item.id),issues=raw?.roomIssuesSnapshot||[],other=(raw?.uploads||[]).find(item=>uploadUsesPhotoCollection(item));return {room:no,submissionId:raw?.id||null,valid:!!submission,templateTypeId:template?.typeId||null,templateVersion:template?.version||null,expectedIds,actualIds,slotsMatch:JSON.stringify(expectedIds)===JSON.stringify(actualIds),photoCount:actualIds.length,imageCount:(raw?.uploads||[]).reduce((total,item)=>total+uploadPhotoCount(item),0),donePhotoCount:(raw?.uploads||[]).filter(item=>item.status==='done').length,otherPhotoCount:other?uploadPhotoCount(other):0,otherMaxPhotos:other?photoUploadLimit(other):0,bombPhotoCount:report?.photos?.length||0,issueCount:issues.length,issuePhotoCount:issues.reduce((total,item)=>total+(item.photos?.length||0),0),candleCount:raw?.candleCountSnapshot??null};},
  7824 |           setOtherEvidencePhotos:(roomNo='528',count=10)=>{const no=String(roomNo),task=taskState(no),upload=task.uploads.find(item=>uploadUsesPhotoCollection(item));if(!upload)throw new Error(`${no}호 기타 사진 슬롯이 없습니다.`);const total=Math.max(0,Math.min(photoUploadLimit(upload),Number(count)||0));upload.images=Array.from({length:total},(_,index)=>({id:`${upload.id}-qa-${index+1}`,status:'done',image:{...demoUploadImageFixture(['supply','bed','bath','floor'][index%4]),uploadedAt:`${state.selectedDate} 12:${String(index).padStart(2,'0')}`,version:'QA 기타 사진'}}));syncPhotoCollectionStatus(upload);render();return {room:no,slotId:upload.id,count:uploadPhotoCount(upload),maxPhotos:photoUploadLimit(upload),zone:upload.zone};},
  7825 |           evidenceDamageAudit:(roomNo='639')=>{const no=String(roomNo),raw=currentSubmissionRecord(no),liveReport=raw?.reportId?state.bombRoomReports?.[raw.reportId]||null:null;if(!raw||!liveReport)throw new Error(`${no}호 제출 증빙 점검 대상을 찾을 수 없습니다.`);const priorRole=state.role,liveReportPhotos=liveReport.photos,firstLivePhoto=liveReportPhotos?.[0]||null,firstLivePhotoBackup=firstLivePhoto?{...firstLivePhoto}:null,issueSnapshots=raw.roomIssuesSnapshot,liveIssues=state.roomIssues?.[no];try{state.role='admin';liveReport.photos=[];const preservedReport=rawBombRoomReportForSubmission(raw),inspectionPhotoId=raw.uploads?.find(upload=>upload.image)?.id,bombPhotoId=preservedReport?.photos?.[0]?.id,bombFallback={submissionValid:!!validatedSubmission(raw),photoCount:preservedReport?.photos?.length||0,inspectionViewer:!!photoViewerConfig({source:'inspection',room:no,recordId:raw.id,photoId:inspectionPhotoId}),bombViewer:!!photoViewerConfig({source:'bomb-room',room:no,recordId:raw.reportId,photoId:bombPhotoId})};liveReport.photos=liveReportPhotos;if(firstLivePhoto){delete firstLivePhoto.image;delete firstLivePhoto.src;}const payloadReport=rawBombRoomReportForSubmission(raw),payloadFallback={submissionValid:!!validatedSubmission(raw),photoCount:payloadReport?.photos?.length||0,preservedVisual:!!(payloadReport?.photos?.[0]?.image||payloadReport?.photos?.[0]?.src),viewer:!!photoViewerConfig({source:'bomb-room',room:no,recordId:raw.reportId,photoId:payloadReport?.photos?.[0]?.id})};if(firstLivePhoto){Object.keys(firstLivePhoto).forEach(key=>delete firstLivePhoto[key]);Object.assign(firstLivePhoto,firstLivePhotoBackup);}raw.roomIssuesSnapshot=[];const issueMismatchRejected=!validatedSubmission(raw);raw.roomIssuesSnapshot=issueSnapshots;if(state.roomIssues)state.roomIssues[no]=[];const issue=issueSnapshots?.[0],issueViewer=!!photoViewerConfig({source:'room-issue',room:no,recordId:issue?.id,photoId:issue?.photos?.[0]?.id});return {bombFallback,payloadFallback,issueMismatchRejected,issueViewer};}finally{state.role=priorRole;liveReport.photos=liveReportPhotos;if(firstLivePhoto&&firstLivePhotoBackup){Object.keys(firstLivePhoto).forEach(key=>delete firstLivePhoto[key]);Object.assign(firstLivePhoto,firstLivePhotoBackup);}raw.roomIssuesSnapshot=issueSnapshots;if(state.roomIssues)state.roomIssues[no]=liveIssues;}},
```

## reservation availability: `availableRooms`

matches: 0

## assignment targets: `function assignmentTargets`

matches: 2

### occurrence 1 · line 5050

```html
  5034 |             const checkout=room.nextCheckoutAt.slice(11,16),checkin=room.nextCheckinAt?.slice(11,16)||room.checkin||'16:00';
  5035 |             const id=`checkout-${room.no}-${assignmentDate}`;targets.push({id,room:room.no,type:room.type,kind:'퇴실 청소',date:assignmentDate,checkout,checkin,deadline:shiftClockTime(checkin,-30)||'15:30',source:'checkout',sourceLabel:'예정 체크아웃'});targetIds.add(id);
  5036 |           }
  5037 |           if(room.stayoverRequest?.date===assignmentDate){
  5038 |             const request=room.stayoverRequest,reservation=activeReservationsFor(targetState,room.no).find(item=>reservationContainsNight(item,assignmentDate));
  5039 |             targets.push({id:`stayover-${room.no}-${assignmentDate}`,room:room.no,type:room.type,kind:'연박 청소',date:assignmentDate,checkout:request.accessStart,deadline:request.requestDue,accessStart:request.accessStart,requestDue:request.requestDue,accessEnd:request.accessEnd,source:'stayover',sourceLabel:'연박 청소 신청',reservationId:reservation?.id||null,guestCount:reservation?reservationGuestCount(reservation):null});
  5040 |           }
  5041 |         });
  5042 |         return targets;
  5043 |       }
  5044 |       function liveAssignmentTargetsForState(targetState=state,assignmentDate=targetState.assignmentDate) {
  5045 |         const automatic=automaticAssignmentTargets(targetState,assignmentDate),manual=(targetState.manualAssignmentTargets||[]).filter(item=>!item.cancelled&&targetEffectiveDate(item,assignmentDate)===assignmentDate),automaticKeys=new Set(automatic.map(item=>`${item.room}:${item.kind}`));
  5046 |         const normalizedAutomatic=automatic.map(item=>{const duplicate=manual.find(candidate=>candidate.room===item.room&&candidate.kind===item.kind);return duplicate?{...item,id:duplicate.id}:item;});
  5047 |         return [...normalizedAutomatic,...manual.filter(item=>!automaticKeys.has(`${item.room}:${item.kind}`))];
  5048 |       }
  5049 |       function liveAssignmentTargets() { return liveAssignmentTargetsForState(state); }
  5050 |       function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {
  5051 |         const carryovers=Object.values(targetState.cleaningTargets||{}).filter(item=>item&&!item.closed&&targetEffectiveDate(item)===assignmentDate&&item.carryReason&&item.carryReason!=='started-unfinished').sort((left,right)=>targetPlanDate(left).localeCompare(targetPlanDate(right))||left.room.localeCompare(right.room,'ko',{numeric:true})),carryRoomKinds=new Set(carryovers.map(item=>`${item.room}:${item.kind}`));
  5052 |         const live=liveAssignmentTargetsForState(targetState,assignmentDate).filter(item=>{const record=targetState.assignments?.[item.id];if(record?.status==='cancelled'&&reopenCancelledAssignmentForNewReservation(targetState,item)===record)return false;return !carryRoomKinds.has(`${item.room}:${item.kind}`);}),liveIds=new Set([...carryovers,...live].map(item=>item.id));
  5053 |         const committedOrphans=Object.values(targetState.assignments||{}).filter(record=>record?.status!=='cancelled').map(record=>record?.committedTarget).filter(item=>item?.id&&!liveIds.has(item.id)&&targetEffectiveDate(item)===assignmentDate&&!carryRoomKinds.has(`${item.room}:${item.kind}`));
  5054 |         return [...carryovers,...live,...committedOrphans];
  5055 |       }
  5056 |       function assignmentTargets() { return assignmentTargetsForDate(state.assignmentDate,state); }
  5057 |       function activateNotifiedAssignmentsForDate(date=state.selectedDate) {
  5058 |         if(date!==state.selectedDate)return 0;
  5059 |         let activated=0;
  5060 |         assignmentTargetsForDate(date,state).forEach(item=>{
  5061 |           const assignment=state.assignments?.[item.id];
  5062 |           if(assignment?.status!=='notified'||!assignment.maidId||attemptForCleaningTarget(item))return;
  5063 |           const roomAttempt=activeUnfinishedAttempt(item.room),roomAttemptBlocksActivation=!!roomAttempt;
  5064 |           if(roomAttemptBlocksActivation){
  5065 |             const blockSignature=`${roomAttempt.id}:${roomAttempt.status}:${roomAttempt.startedAt||''}:${roomAttempt.completedAt||''}`;
  5066 |             if(assignment.activationBlockedBy!==blockSignature){assignment.activationBlockedBy=blockSignature;assignment.activationBlockedAt=`${state.selectedDate} ${state.time}`;const blockDetail=`${dateLabel(date)} · ${item.kind} · 기존 ${roomAttempt.kind} ${roomAttempt.status} 회차를 진행 중·청소 상세에서 먼저 종결`;appendEvent(`${item.room}호 당일 청소 활성화 보류`,blockDetail);appendEvent('내 청소 시작 보류 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 대기 · 시작 불가`,{maidIds:[assignment.maidId]});}
  5067 |             return;
  5068 |           }
  5069 |           const wasActivationBlocked=!!assignment.activationBlockedBy;delete assignment.activationBlockedBy;delete assignment.activationBlockedAt;
  5070 |           const snapshot=assignmentPricingSnapshot(item),room=ROOMS.find(entry=>entry.no===item.room),performerName=maidName(assignment.maidId),templateSnapshot=item.templateSnapshot||state.drafts.find(draft=>draft.id===item.id)?.templateSnapshot||templateSnapshotFor(item.room,item.kind);
  5071 |           const attempt=beginCleaningAttempt(item.room,{performerId:assignment.maidId,performerName,reason:'사전 통보 청소 당일 활성화',baseRateSnapshot:snapshot.rate,kind:item.kind,workDate:targetPlanDate(item),effectiveDate:date,workTargetId:item.id,templateSnapshot,accessStart:item.accessStart||null,requestDue:item.requestDue||null,accessEnd:item.accessEnd||null,reservationIdSnapshot:item.reservationId||null,guestCountSnapshot:item.guestCount??null,carryReason:item.carryReason,carriedFromDate:item.carriedFromDate,rolloverCount:item.rolloverCount});
  5072 |           if(room)room.assignee=performerName;state.jobs[item.room]=item.kind==='재청소'?'reclean':'scheduled';attempt.status='active';item.currentAttemptId=attempt.id;
  5073 |           const targetRecord=state.cleaningTargets?.[item.id];if(targetRecord)targetRecord.currentAttemptId=attempt.id;
  5074 |           if(wasActivationBlocked)appendEvent('내 청소 시작 가능 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 완료 · 기존 통보 순서 유지`,{maidIds:[assignment.maidId]});
  5075 |           activated+=1;
  5076 |         });
  5077 |         return activated;
  5078 |       }
  5079 |       function assignmentFor(item) {
  5080 |         const key=item.id;
  5081 |         const previous=state.assignments[key];
  5082 |         if(previous?.status==='cancelled')reopenCancelledAssignmentForNewReservation(state,item);
  5083 |         if(!state.assignments[key])state.assignments[key]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null};
  5084 |         return state.assignments[key];
```

### occurrence 2 · line 5056

```html
  5040 |           }
  5041 |         });
  5042 |         return targets;
  5043 |       }
  5044 |       function liveAssignmentTargetsForState(targetState=state,assignmentDate=targetState.assignmentDate) {
  5045 |         const automatic=automaticAssignmentTargets(targetState,assignmentDate),manual=(targetState.manualAssignmentTargets||[]).filter(item=>!item.cancelled&&targetEffectiveDate(item,assignmentDate)===assignmentDate),automaticKeys=new Set(automatic.map(item=>`${item.room}:${item.kind}`));
  5046 |         const normalizedAutomatic=automatic.map(item=>{const duplicate=manual.find(candidate=>candidate.room===item.room&&candidate.kind===item.kind);return duplicate?{...item,id:duplicate.id}:item;});
  5047 |         return [...normalizedAutomatic,...manual.filter(item=>!automaticKeys.has(`${item.room}:${item.kind}`))];
  5048 |       }
  5049 |       function liveAssignmentTargets() { return liveAssignmentTargetsForState(state); }
  5050 |       function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {
  5051 |         const carryovers=Object.values(targetState.cleaningTargets||{}).filter(item=>item&&!item.closed&&targetEffectiveDate(item)===assignmentDate&&item.carryReason&&item.carryReason!=='started-unfinished').sort((left,right)=>targetPlanDate(left).localeCompare(targetPlanDate(right))||left.room.localeCompare(right.room,'ko',{numeric:true})),carryRoomKinds=new Set(carryovers.map(item=>`${item.room}:${item.kind}`));
  5052 |         const live=liveAssignmentTargetsForState(targetState,assignmentDate).filter(item=>{const record=targetState.assignments?.[item.id];if(record?.status==='cancelled'&&reopenCancelledAssignmentForNewReservation(targetState,item)===record)return false;return !carryRoomKinds.has(`${item.room}:${item.kind}`);}),liveIds=new Set([...carryovers,...live].map(item=>item.id));
  5053 |         const committedOrphans=Object.values(targetState.assignments||{}).filter(record=>record?.status!=='cancelled').map(record=>record?.committedTarget).filter(item=>item?.id&&!liveIds.has(item.id)&&targetEffectiveDate(item)===assignmentDate&&!carryRoomKinds.has(`${item.room}:${item.kind}`));
  5054 |         return [...carryovers,...live,...committedOrphans];
  5055 |       }
  5056 |       function assignmentTargets() { return assignmentTargetsForDate(state.assignmentDate,state); }
  5057 |       function activateNotifiedAssignmentsForDate(date=state.selectedDate) {
  5058 |         if(date!==state.selectedDate)return 0;
  5059 |         let activated=0;
  5060 |         assignmentTargetsForDate(date,state).forEach(item=>{
  5061 |           const assignment=state.assignments?.[item.id];
  5062 |           if(assignment?.status!=='notified'||!assignment.maidId||attemptForCleaningTarget(item))return;
  5063 |           const roomAttempt=activeUnfinishedAttempt(item.room),roomAttemptBlocksActivation=!!roomAttempt;
  5064 |           if(roomAttemptBlocksActivation){
  5065 |             const blockSignature=`${roomAttempt.id}:${roomAttempt.status}:${roomAttempt.startedAt||''}:${roomAttempt.completedAt||''}`;
  5066 |             if(assignment.activationBlockedBy!==blockSignature){assignment.activationBlockedBy=blockSignature;assignment.activationBlockedAt=`${state.selectedDate} ${state.time}`;const blockDetail=`${dateLabel(date)} · ${item.kind} · 기존 ${roomAttempt.kind} ${roomAttempt.status} 회차를 진행 중·청소 상세에서 먼저 종결`;appendEvent(`${item.room}호 당일 청소 활성화 보류`,blockDetail);appendEvent('내 청소 시작 보류 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 대기 · 시작 불가`,{maidIds:[assignment.maidId]});}
  5067 |             return;
  5068 |           }
  5069 |           const wasActivationBlocked=!!assignment.activationBlockedBy;delete assignment.activationBlockedBy;delete assignment.activationBlockedAt;
  5070 |           const snapshot=assignmentPricingSnapshot(item),room=ROOMS.find(entry=>entry.no===item.room),performerName=maidName(assignment.maidId),templateSnapshot=item.templateSnapshot||state.drafts.find(draft=>draft.id===item.id)?.templateSnapshot||templateSnapshotFor(item.room,item.kind);
  5071 |           const attempt=beginCleaningAttempt(item.room,{performerId:assignment.maidId,performerName,reason:'사전 통보 청소 당일 활성화',baseRateSnapshot:snapshot.rate,kind:item.kind,workDate:targetPlanDate(item),effectiveDate:date,workTargetId:item.id,templateSnapshot,accessStart:item.accessStart||null,requestDue:item.requestDue||null,accessEnd:item.accessEnd||null,reservationIdSnapshot:item.reservationId||null,guestCountSnapshot:item.guestCount??null,carryReason:item.carryReason,carriedFromDate:item.carriedFromDate,rolloverCount:item.rolloverCount});
  5072 |           if(room)room.assignee=performerName;state.jobs[item.room]=item.kind==='재청소'?'reclean':'scheduled';attempt.status='active';item.currentAttemptId=attempt.id;
  5073 |           const targetRecord=state.cleaningTargets?.[item.id];if(targetRecord)targetRecord.currentAttemptId=attempt.id;
  5074 |           if(wasActivationBlocked)appendEvent('내 청소 시작 가능 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 완료 · 기존 통보 순서 유지`,{maidIds:[assignment.maidId]});
  5075 |           activated+=1;
  5076 |         });
  5077 |         return activated;
  5078 |       }
  5079 |       function assignmentFor(item) {
  5080 |         const key=item.id;
  5081 |         const previous=state.assignments[key];
  5082 |         if(previous?.status==='cancelled')reopenCancelledAssignmentForNewReservation(state,item);
  5083 |         if(!state.assignments[key])state.assignments[key]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null};
  5084 |         return state.assignments[key];
  5085 |       }
  5086 |       function orderedAssignmentsForMaid(maidId,notifiedOnly=false) {
  5087 |         return assignmentTargets().filter(item=>{const assignment=assignmentFor(item);return assignment.maidId===maidId&&(!notifiedOnly||assignment.status==='notified');}).sort((left,right)=>{
  5088 |           const leftOrder=Number(assignmentFor(left).order)||Number.MAX_SAFE_INTEGER,rightOrder=Number(assignmentFor(right).order)||Number.MAX_SAFE_INTEGER;
  5089 |           return leftOrder-rightOrder||left.room.localeCompare(right.room,'ko',{numeric:true});
  5090 |         });
```

## live assignment targets: `liveAssignmentTargetsForState`

matches: 4

### occurrence 1 · line 4958

```html
  4942 |         if(!targetState.cleaningTargets)targetState.cleaningTargets={};targetState.cleaningTargets[key]={...cleaningTargetSnapshot(item,targetState.assignmentDate),closed:false,reopenedAt:`${targetState.selectedDate||state.selectedDate} ${targetState.time||state.time}`,reopenReason:'새 예약 청소 의무',closeHistory:[...(ledger?.closeHistory||[]),...(closeRevision?[closeRevision]:[])]};
  4943 |         return reopened;
  4944 |       }
  4945 |       function reopenCancelledManualCleaningTarget(item,reopenReason='관리자 직접 다시 추가') {
  4946 |         const manual=(state.manualAssignmentTargets||[]).find(target=>target.id===item?.id),record=item?.id?state.assignments?.[item.id]:null;
  4947 |         if(!manual||!record||record.status!=='cancelled')return false;
  4948 |         Object.assign(manual,item);delete manual.cancelled;delete manual.cancelledAt;delete manual.cancelledBy;delete manual.closeReasonCode;delete manual.closeReason;
  4949 |         const cancellationRevision={cancelledAt:record.cancelledAt||null,cancelledBy:record.cancelledBy||null,cancelledMaidId:record.cancelledMaidId||null,cancelledNotifiedMaidId:record.cancelledNotifiedMaidId||null,cancelledOrder:record.cancelledOrder??null,cancelledPreviousOrder:record.cancelledPreviousOrder??null,cancelledStatus:record.cancelledStatus||null,cancelReasonCode:record.cancelReasonCode||null,cancelReason:record.cancelReason||record.cancelledReason||null,notifiedAt:record.cancelledNotifiedAt||record.notifiedAt||null,notificationRevision:record.cancelledNotificationRevision??record.notificationRevision??null,committedTarget:record.cancelledTarget||record.committedTarget||null,cancelledReservationId:record.cancelledReservationId||null};
  4950 |         state.assignments[item.id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]};
  4951 |         const closedTarget=state.cleaningTargets?.[item.id]||{},closeRevision={closedAt:closedTarget.closedAt||null,closedBy:closedTarget.closedBy||null,closeReasonCode:closedTarget.closeReasonCode||null,closeReason:closedTarget.closeReason||null,closeStatus:closedTarget.closeStatus||null,target:cleaningTargetOperationalSnapshot(closedTarget,targetPlanDate(item,state.assignmentDate))};
  4952 |         state.cleaningTargets[item.id]={...cleaningTargetSnapshot(item,targetPlanDate(item,state.assignmentDate)),closed:false,reopenedAt:`${state.selectedDate} ${state.time}`,reopenReason,closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]};
  4953 |         state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:item.id,assignmentDate:targetEffectiveDate(item),room:item.room,beforeMaidId:null,afterMaidId:null,before:'청소 대상 취소',after:'미배정',reason:`${reopenReason} · 취소 이력 보존`});
  4954 |         return true;
  4955 |       }
  4956 |       function initializeCleaningTargetLedger(targetState) {
  4957 |         if(!targetState.cleaningTargets)targetState.cleaningTargets={};
  4958 |         const live=liveAssignmentTargetsForState(targetState),committed=Object.values(targetState.assignments||{}).map(record=>record?.committedTarget).filter(Boolean),attemptTargets=Object.entries(targetState.currentAttemptByRoom||{}).map(([roomNo,attemptId])=>{
  4959 |           const attempt=targetState.cleaningAttempts?.[attemptId],room=ROOMS.find(item=>item.no===roomNo);if(!attempt||attempt.status==='superseded'||!attempt.workTargetId)return null;
  4960 |           const planDate=attemptPlanDate(attempt,targetState.selectedDate),effectiveDate=attemptEffectiveDate(attempt,planDate);
  4961 |           const checkout=attempt.checkoutSnapshot||attempt.accessStart||room?.actualCheckoutAt?.slice(11,16)||DEFAULT_CHECKOUT_TIME;
  4962 |           return {id:attempt.workTargetId,currentAttemptId:attempt.id,room:roomNo,type:attempt.roomMetaSnapshot?.typeId||room?.type||'standard',kind:attempt.kind||'퇴실 청소',date:planDate,planDate,effectiveDate,checkout,checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||shiftClockTime(attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,-30)||'15:30',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||attempt.checkoutSnapshot||null,requestDue:attempt.requestDue||null,accessEnd:attempt.accessEnd||null,reservationId:attempt.reservationIdSnapshot||null,guestCount:attempt.guestCountSnapshot??null,source:'attempt',sourceLabel:'수행 회차',rateSnapshot:attempt.baseRateSnapshot||null,minutesSnapshot:attempt.templateSnapshot?.minutes||ROOM_TYPES[room?.type||'standard'].minutes,elevatorSnapshot:attempt.roomMetaSnapshot?.elevator??room?.elevator??null};
  4963 |         }).filter(Boolean);
  4964 |         [...attemptTargets,...live,...committed].forEach(item=>{if(!item?.id)return;const existing=targetState.cleaningTargets[item.id];targetState.cleaningTargets[item.id]=existing?{...cleaningTargetSnapshot(item,targetState.assignmentDate),...existing}:cleaningTargetSnapshot(item,targetState.assignmentDate);});
  4965 |         return targetState.cleaningTargets;
  4966 |       }
  4967 |       function attemptForCleaningTarget(target,targetState=state) {
  4968 |         const attempts=targetState.cleaningAttempts||{},matches=attempt=>attempt?.workTargetId===target.id&&attempt.status!=='superseded',currentId=targetState.currentAttemptByRoom?.[target.room],targetAttemptId=target.currentAttemptId;
  4969 |         if(currentId&&matches(attempts[currentId]))return attempts[currentId];
  4970 |         if(targetAttemptId&&matches(attempts[targetAttemptId]))return attempts[targetAttemptId];
  4971 |         return Object.values(attempts).reverse().find(matches)||null;
  4972 |       }
  4973 |       function cleaningTargetAdjustmentBlock(target) {
  4974 |         if(!target)return '';
  4975 |         const holdReason=assignmentRoomHoldReason(target.room);if(holdReason)return holdReason;
  4976 |         if(target.kind==='재청소')return '재청소는 기존 수행자가 완료해야 합니다.';
  4977 |         if(target.carryReason==='access-review')return 'PIN·출입 영향 확인이 끝난 뒤 조정할 수 있습니다.';
  4978 |         const attempt=attemptForCleaningTarget(target);
  4979 |         const roomAttempt=targetEffectiveDate(target)===state.selectedDate?activeUnfinishedAttempt(target.room):null;
  4980 |         if(roomAttempt&&roomAttempt.workTargetId!==target.id)return roomAttempt.status==='submitted'?'이 객실의 이전 청소 검수가 남아 검수 대기에서 먼저 종결해야 합니다.':'이 객실의 다른 청소가 진행 중이라 청소 상세에서 조정해야 합니다.';
  4981 |         if(!attempt)return '';
  4982 |         if(attempt.startedAt||attempt.completedAt||!['active','scheduled'].includes(attempt.status))return '이미 시작한 청소는 진행 중에서 조정합니다.';
  4983 |         return '';
  4984 |       }
  4985 |       function cleaningTargetCanAdjust(target) { return !cleaningTargetAdjustmentBlock(target); }
  4986 |       function cleaningTargetAdjustmentFingerprint(target) {
  4987 |         const assignment=target?state.assignments?.[target.id]:null,attempt=target?attemptForCleaningTarget(target):null;
  4988 |         return [target?.id||'',target?targetEffectiveDate(target):'',target?.reservationId||'',target?cleaningTargetObligationKey(target):'',target?.kind||'',target?.checkout||'',target?.checkin||'',target?.deadline||'',assignment?.status||'',assignment?.maidId||'',assignment?.order??'',assignment?.previousMaidId||'',assignment?.previousOrder??'',attempt?.id||'',attempt?.status||'',attempt?.startedAt||'',attempt?.completedAt||'',state.currentAttemptByRoom?.[target?.room]||''].join('|');
  4989 |       }
  4990 |       function rolloverUnresolvedTargets(targetState,toDate) {
  4991 |         initializeCleaningTargetLedger(targetState);if(!targetState.rolloverEvents)targetState.rolloverEvents={};if(!targetState.rolloverHistory)targetState.rolloverHistory=[];
  4992 |         Object.values(targetState.cleaningTargets||{}).filter(target=>target&&!target.closed&&targetEffectiveDate(target,'')<toDate).forEach(target=>{
```

### occurrence 2 · line 5044

```html
  5028 |         activeReservationsFor(targetState).filter(reservation=>reservation.checkOutAt.slice(0,10)===assignmentDate).forEach(reservation=>{
  5029 |           const target=reservationCheckoutTarget(reservation,assignmentDate,targetState);if(!target)return;
  5030 |           targets.push(target);targetIds.add(target.id);
  5031 |         });
  5032 |         ROOMS.forEach(room=>{
  5033 |           if(room.nextCheckoutAt?.slice(0,10)===assignmentDate&&!targetIds.has(`checkout-${room.no}-${assignmentDate}`)){
  5034 |             const checkout=room.nextCheckoutAt.slice(11,16),checkin=room.nextCheckinAt?.slice(11,16)||room.checkin||'16:00';
  5035 |             const id=`checkout-${room.no}-${assignmentDate}`;targets.push({id,room:room.no,type:room.type,kind:'퇴실 청소',date:assignmentDate,checkout,checkin,deadline:shiftClockTime(checkin,-30)||'15:30',source:'checkout',sourceLabel:'예정 체크아웃'});targetIds.add(id);
  5036 |           }
  5037 |           if(room.stayoverRequest?.date===assignmentDate){
  5038 |             const request=room.stayoverRequest,reservation=activeReservationsFor(targetState,room.no).find(item=>reservationContainsNight(item,assignmentDate));
  5039 |             targets.push({id:`stayover-${room.no}-${assignmentDate}`,room:room.no,type:room.type,kind:'연박 청소',date:assignmentDate,checkout:request.accessStart,deadline:request.requestDue,accessStart:request.accessStart,requestDue:request.requestDue,accessEnd:request.accessEnd,source:'stayover',sourceLabel:'연박 청소 신청',reservationId:reservation?.id||null,guestCount:reservation?reservationGuestCount(reservation):null});
  5040 |           }
  5041 |         });
  5042 |         return targets;
  5043 |       }
  5044 |       function liveAssignmentTargetsForState(targetState=state,assignmentDate=targetState.assignmentDate) {
  5045 |         const automatic=automaticAssignmentTargets(targetState,assignmentDate),manual=(targetState.manualAssignmentTargets||[]).filter(item=>!item.cancelled&&targetEffectiveDate(item,assignmentDate)===assignmentDate),automaticKeys=new Set(automatic.map(item=>`${item.room}:${item.kind}`));
  5046 |         const normalizedAutomatic=automatic.map(item=>{const duplicate=manual.find(candidate=>candidate.room===item.room&&candidate.kind===item.kind);return duplicate?{...item,id:duplicate.id}:item;});
  5047 |         return [...normalizedAutomatic,...manual.filter(item=>!automaticKeys.has(`${item.room}:${item.kind}`))];
  5048 |       }
  5049 |       function liveAssignmentTargets() { return liveAssignmentTargetsForState(state); }
  5050 |       function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {
  5051 |         const carryovers=Object.values(targetState.cleaningTargets||{}).filter(item=>item&&!item.closed&&targetEffectiveDate(item)===assignmentDate&&item.carryReason&&item.carryReason!=='started-unfinished').sort((left,right)=>targetPlanDate(left).localeCompare(targetPlanDate(right))||left.room.localeCompare(right.room,'ko',{numeric:true})),carryRoomKinds=new Set(carryovers.map(item=>`${item.room}:${item.kind}`));
  5052 |         const live=liveAssignmentTargetsForState(targetState,assignmentDate).filter(item=>{const record=targetState.assignments?.[item.id];if(record?.status==='cancelled'&&reopenCancelledAssignmentForNewReservation(targetState,item)===record)return false;return !carryRoomKinds.has(`${item.room}:${item.kind}`);}),liveIds=new Set([...carryovers,...live].map(item=>item.id));
  5053 |         const committedOrphans=Object.values(targetState.assignments||{}).filter(record=>record?.status!=='cancelled').map(record=>record?.committedTarget).filter(item=>item?.id&&!liveIds.has(item.id)&&targetEffectiveDate(item)===assignmentDate&&!carryRoomKinds.has(`${item.room}:${item.kind}`));
  5054 |         return [...carryovers,...live,...committedOrphans];
  5055 |       }
  5056 |       function assignmentTargets() { return assignmentTargetsForDate(state.assignmentDate,state); }
  5057 |       function activateNotifiedAssignmentsForDate(date=state.selectedDate) {
  5058 |         if(date!==state.selectedDate)return 0;
  5059 |         let activated=0;
  5060 |         assignmentTargetsForDate(date,state).forEach(item=>{
  5061 |           const assignment=state.assignments?.[item.id];
  5062 |           if(assignment?.status!=='notified'||!assignment.maidId||attemptForCleaningTarget(item))return;
  5063 |           const roomAttempt=activeUnfinishedAttempt(item.room),roomAttemptBlocksActivation=!!roomAttempt;
  5064 |           if(roomAttemptBlocksActivation){
  5065 |             const blockSignature=`${roomAttempt.id}:${roomAttempt.status}:${roomAttempt.startedAt||''}:${roomAttempt.completedAt||''}`;
  5066 |             if(assignment.activationBlockedBy!==blockSignature){assignment.activationBlockedBy=blockSignature;assignment.activationBlockedAt=`${state.selectedDate} ${state.time}`;const blockDetail=`${dateLabel(date)} · ${item.kind} · 기존 ${roomAttempt.kind} ${roomAttempt.status} 회차를 진행 중·청소 상세에서 먼저 종결`;appendEvent(`${item.room}호 당일 청소 활성화 보류`,blockDetail);appendEvent('내 청소 시작 보류 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 대기 · 시작 불가`,{maidIds:[assignment.maidId]});}
  5067 |             return;
  5068 |           }
  5069 |           const wasActivationBlocked=!!assignment.activationBlockedBy;delete assignment.activationBlockedBy;delete assignment.activationBlockedAt;
  5070 |           const snapshot=assignmentPricingSnapshot(item),room=ROOMS.find(entry=>entry.no===item.room),performerName=maidName(assignment.maidId),templateSnapshot=item.templateSnapshot||state.drafts.find(draft=>draft.id===item.id)?.templateSnapshot||templateSnapshotFor(item.room,item.kind);
  5071 |           const attempt=beginCleaningAttempt(item.room,{performerId:assignment.maidId,performerName,reason:'사전 통보 청소 당일 활성화',baseRateSnapshot:snapshot.rate,kind:item.kind,workDate:targetPlanDate(item),effectiveDate:date,workTargetId:item.id,templateSnapshot,accessStart:item.accessStart||null,requestDue:item.requestDue||null,accessEnd:item.accessEnd||null,reservationIdSnapshot:item.reservationId||null,guestCountSnapshot:item.guestCount??null,carryReason:item.carryReason,carriedFromDate:item.carriedFromDate,rolloverCount:item.rolloverCount});
  5072 |           if(room)room.assignee=performerName;state.jobs[item.room]=item.kind==='재청소'?'reclean':'scheduled';attempt.status='active';item.currentAttemptId=attempt.id;
  5073 |           const targetRecord=state.cleaningTargets?.[item.id];if(targetRecord)targetRecord.currentAttemptId=attempt.id;
  5074 |           if(wasActivationBlocked)appendEvent('내 청소 시작 가능 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 완료 · 기존 통보 순서 유지`,{maidIds:[assignment.maidId]});
  5075 |           activated+=1;
  5076 |         });
  5077 |         return activated;
  5078 |       }
```

### occurrence 3 · line 5049

```html
  5033 |           if(room.nextCheckoutAt?.slice(0,10)===assignmentDate&&!targetIds.has(`checkout-${room.no}-${assignmentDate}`)){
  5034 |             const checkout=room.nextCheckoutAt.slice(11,16),checkin=room.nextCheckinAt?.slice(11,16)||room.checkin||'16:00';
  5035 |             const id=`checkout-${room.no}-${assignmentDate}`;targets.push({id,room:room.no,type:room.type,kind:'퇴실 청소',date:assignmentDate,checkout,checkin,deadline:shiftClockTime(checkin,-30)||'15:30',source:'checkout',sourceLabel:'예정 체크아웃'});targetIds.add(id);
  5036 |           }
  5037 |           if(room.stayoverRequest?.date===assignmentDate){
  5038 |             const request=room.stayoverRequest,reservation=activeReservationsFor(targetState,room.no).find(item=>reservationContainsNight(item,assignmentDate));
  5039 |             targets.push({id:`stayover-${room.no}-${assignmentDate}`,room:room.no,type:room.type,kind:'연박 청소',date:assignmentDate,checkout:request.accessStart,deadline:request.requestDue,accessStart:request.accessStart,requestDue:request.requestDue,accessEnd:request.accessEnd,source:'stayover',sourceLabel:'연박 청소 신청',reservationId:reservation?.id||null,guestCount:reservation?reservationGuestCount(reservation):null});
  5040 |           }
  5041 |         });
  5042 |         return targets;
  5043 |       }
  5044 |       function liveAssignmentTargetsForState(targetState=state,assignmentDate=targetState.assignmentDate) {
  5045 |         const automatic=automaticAssignmentTargets(targetState,assignmentDate),manual=(targetState.manualAssignmentTargets||[]).filter(item=>!item.cancelled&&targetEffectiveDate(item,assignmentDate)===assignmentDate),automaticKeys=new Set(automatic.map(item=>`${item.room}:${item.kind}`));
  5046 |         const normalizedAutomatic=automatic.map(item=>{const duplicate=manual.find(candidate=>candidate.room===item.room&&candidate.kind===item.kind);return duplicate?{...item,id:duplicate.id}:item;});
  5047 |         return [...normalizedAutomatic,...manual.filter(item=>!automaticKeys.has(`${item.room}:${item.kind}`))];
  5048 |       }
  5049 |       function liveAssignmentTargets() { return liveAssignmentTargetsForState(state); }
  5050 |       function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {
  5051 |         const carryovers=Object.values(targetState.cleaningTargets||{}).filter(item=>item&&!item.closed&&targetEffectiveDate(item)===assignmentDate&&item.carryReason&&item.carryReason!=='started-unfinished').sort((left,right)=>targetPlanDate(left).localeCompare(targetPlanDate(right))||left.room.localeCompare(right.room,'ko',{numeric:true})),carryRoomKinds=new Set(carryovers.map(item=>`${item.room}:${item.kind}`));
  5052 |         const live=liveAssignmentTargetsForState(targetState,assignmentDate).filter(item=>{const record=targetState.assignments?.[item.id];if(record?.status==='cancelled'&&reopenCancelledAssignmentForNewReservation(targetState,item)===record)return false;return !carryRoomKinds.has(`${item.room}:${item.kind}`);}),liveIds=new Set([...carryovers,...live].map(item=>item.id));
  5053 |         const committedOrphans=Object.values(targetState.assignments||{}).filter(record=>record?.status!=='cancelled').map(record=>record?.committedTarget).filter(item=>item?.id&&!liveIds.has(item.id)&&targetEffectiveDate(item)===assignmentDate&&!carryRoomKinds.has(`${item.room}:${item.kind}`));
  5054 |         return [...carryovers,...live,...committedOrphans];
  5055 |       }
  5056 |       function assignmentTargets() { return assignmentTargetsForDate(state.assignmentDate,state); }
  5057 |       function activateNotifiedAssignmentsForDate(date=state.selectedDate) {
  5058 |         if(date!==state.selectedDate)return 0;
  5059 |         let activated=0;
  5060 |         assignmentTargetsForDate(date,state).forEach(item=>{
  5061 |           const assignment=state.assignments?.[item.id];
  5062 |           if(assignment?.status!=='notified'||!assignment.maidId||attemptForCleaningTarget(item))return;
  5063 |           const roomAttempt=activeUnfinishedAttempt(item.room),roomAttemptBlocksActivation=!!roomAttempt;
  5064 |           if(roomAttemptBlocksActivation){
  5065 |             const blockSignature=`${roomAttempt.id}:${roomAttempt.status}:${roomAttempt.startedAt||''}:${roomAttempt.completedAt||''}`;
  5066 |             if(assignment.activationBlockedBy!==blockSignature){assignment.activationBlockedBy=blockSignature;assignment.activationBlockedAt=`${state.selectedDate} ${state.time}`;const blockDetail=`${dateLabel(date)} · ${item.kind} · 기존 ${roomAttempt.kind} ${roomAttempt.status} 회차를 진행 중·청소 상세에서 먼저 종결`;appendEvent(`${item.room}호 당일 청소 활성화 보류`,blockDetail);appendEvent('내 청소 시작 보류 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 대기 · 시작 불가`,{maidIds:[assignment.maidId]});}
  5067 |             return;
  5068 |           }
  5069 |           const wasActivationBlocked=!!assignment.activationBlockedBy;delete assignment.activationBlockedBy;delete assignment.activationBlockedAt;
  5070 |           const snapshot=assignmentPricingSnapshot(item),room=ROOMS.find(entry=>entry.no===item.room),performerName=maidName(assignment.maidId),templateSnapshot=item.templateSnapshot||state.drafts.find(draft=>draft.id===item.id)?.templateSnapshot||templateSnapshotFor(item.room,item.kind);
  5071 |           const attempt=beginCleaningAttempt(item.room,{performerId:assignment.maidId,performerName,reason:'사전 통보 청소 당일 활성화',baseRateSnapshot:snapshot.rate,kind:item.kind,workDate:targetPlanDate(item),effectiveDate:date,workTargetId:item.id,templateSnapshot,accessStart:item.accessStart||null,requestDue:item.requestDue||null,accessEnd:item.accessEnd||null,reservationIdSnapshot:item.reservationId||null,guestCountSnapshot:item.guestCount??null,carryReason:item.carryReason,carriedFromDate:item.carriedFromDate,rolloverCount:item.rolloverCount});
  5072 |           if(room)room.assignee=performerName;state.jobs[item.room]=item.kind==='재청소'?'reclean':'scheduled';attempt.status='active';item.currentAttemptId=attempt.id;
  5073 |           const targetRecord=state.cleaningTargets?.[item.id];if(targetRecord)targetRecord.currentAttemptId=attempt.id;
  5074 |           if(wasActivationBlocked)appendEvent('내 청소 시작 가능 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 완료 · 기존 통보 순서 유지`,{maidIds:[assignment.maidId]});
  5075 |           activated+=1;
  5076 |         });
  5077 |         return activated;
  5078 |       }
  5079 |       function assignmentFor(item) {
  5080 |         const key=item.id;
  5081 |         const previous=state.assignments[key];
  5082 |         if(previous?.status==='cancelled')reopenCancelledAssignmentForNewReservation(state,item);
  5083 |         if(!state.assignments[key])state.assignments[key]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null};
```

### occurrence 4 · line 5052

```html
  5036 |           }
  5037 |           if(room.stayoverRequest?.date===assignmentDate){
  5038 |             const request=room.stayoverRequest,reservation=activeReservationsFor(targetState,room.no).find(item=>reservationContainsNight(item,assignmentDate));
  5039 |             targets.push({id:`stayover-${room.no}-${assignmentDate}`,room:room.no,type:room.type,kind:'연박 청소',date:assignmentDate,checkout:request.accessStart,deadline:request.requestDue,accessStart:request.accessStart,requestDue:request.requestDue,accessEnd:request.accessEnd,source:'stayover',sourceLabel:'연박 청소 신청',reservationId:reservation?.id||null,guestCount:reservation?reservationGuestCount(reservation):null});
  5040 |           }
  5041 |         });
  5042 |         return targets;
  5043 |       }
  5044 |       function liveAssignmentTargetsForState(targetState=state,assignmentDate=targetState.assignmentDate) {
  5045 |         const automatic=automaticAssignmentTargets(targetState,assignmentDate),manual=(targetState.manualAssignmentTargets||[]).filter(item=>!item.cancelled&&targetEffectiveDate(item,assignmentDate)===assignmentDate),automaticKeys=new Set(automatic.map(item=>`${item.room}:${item.kind}`));
  5046 |         const normalizedAutomatic=automatic.map(item=>{const duplicate=manual.find(candidate=>candidate.room===item.room&&candidate.kind===item.kind);return duplicate?{...item,id:duplicate.id}:item;});
  5047 |         return [...normalizedAutomatic,...manual.filter(item=>!automaticKeys.has(`${item.room}:${item.kind}`))];
  5048 |       }
  5049 |       function liveAssignmentTargets() { return liveAssignmentTargetsForState(state); }
  5050 |       function assignmentTargetsForDate(assignmentDate=state.assignmentDate,targetState=state) {
  5051 |         const carryovers=Object.values(targetState.cleaningTargets||{}).filter(item=>item&&!item.closed&&targetEffectiveDate(item)===assignmentDate&&item.carryReason&&item.carryReason!=='started-unfinished').sort((left,right)=>targetPlanDate(left).localeCompare(targetPlanDate(right))||left.room.localeCompare(right.room,'ko',{numeric:true})),carryRoomKinds=new Set(carryovers.map(item=>`${item.room}:${item.kind}`));
  5052 |         const live=liveAssignmentTargetsForState(targetState,assignmentDate).filter(item=>{const record=targetState.assignments?.[item.id];if(record?.status==='cancelled'&&reopenCancelledAssignmentForNewReservation(targetState,item)===record)return false;return !carryRoomKinds.has(`${item.room}:${item.kind}`);}),liveIds=new Set([...carryovers,...live].map(item=>item.id));
  5053 |         const committedOrphans=Object.values(targetState.assignments||{}).filter(record=>record?.status!=='cancelled').map(record=>record?.committedTarget).filter(item=>item?.id&&!liveIds.has(item.id)&&targetEffectiveDate(item)===assignmentDate&&!carryRoomKinds.has(`${item.room}:${item.kind}`));
  5054 |         return [...carryovers,...live,...committedOrphans];
  5055 |       }
  5056 |       function assignmentTargets() { return assignmentTargetsForDate(state.assignmentDate,state); }
  5057 |       function activateNotifiedAssignmentsForDate(date=state.selectedDate) {
  5058 |         if(date!==state.selectedDate)return 0;
  5059 |         let activated=0;
  5060 |         assignmentTargetsForDate(date,state).forEach(item=>{
  5061 |           const assignment=state.assignments?.[item.id];
  5062 |           if(assignment?.status!=='notified'||!assignment.maidId||attemptForCleaningTarget(item))return;
  5063 |           const roomAttempt=activeUnfinishedAttempt(item.room),roomAttemptBlocksActivation=!!roomAttempt;
  5064 |           if(roomAttemptBlocksActivation){
  5065 |             const blockSignature=`${roomAttempt.id}:${roomAttempt.status}:${roomAttempt.startedAt||''}:${roomAttempt.completedAt||''}`;
  5066 |             if(assignment.activationBlockedBy!==blockSignature){assignment.activationBlockedBy=blockSignature;assignment.activationBlockedAt=`${state.selectedDate} ${state.time}`;const blockDetail=`${dateLabel(date)} · ${item.kind} · 기존 ${roomAttempt.kind} ${roomAttempt.status} 회차를 진행 중·청소 상세에서 먼저 종결`;appendEvent(`${item.room}호 당일 청소 활성화 보류`,blockDetail);appendEvent('내 청소 시작 보류 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 대기 · 시작 불가`,{maidIds:[assignment.maidId]});}
  5067 |             return;
  5068 |           }
  5069 |           const wasActivationBlocked=!!assignment.activationBlockedBy;delete assignment.activationBlockedBy;delete assignment.activationBlockedAt;
  5070 |           const snapshot=assignmentPricingSnapshot(item),room=ROOMS.find(entry=>entry.no===item.room),performerName=maidName(assignment.maidId),templateSnapshot=item.templateSnapshot||state.drafts.find(draft=>draft.id===item.id)?.templateSnapshot||templateSnapshotFor(item.room,item.kind);
  5071 |           const attempt=beginCleaningAttempt(item.room,{performerId:assignment.maidId,performerName,reason:'사전 통보 청소 당일 활성화',baseRateSnapshot:snapshot.rate,kind:item.kind,workDate:targetPlanDate(item),effectiveDate:date,workTargetId:item.id,templateSnapshot,accessStart:item.accessStart||null,requestDue:item.requestDue||null,accessEnd:item.accessEnd||null,reservationIdSnapshot:item.reservationId||null,guestCountSnapshot:item.guestCount??null,carryReason:item.carryReason,carriedFromDate:item.carriedFromDate,rolloverCount:item.rolloverCount});
  5072 |           if(room)room.assignee=performerName;state.jobs[item.room]=item.kind==='재청소'?'reclean':'scheduled';attempt.status='active';item.currentAttemptId=attempt.id;
  5073 |           const targetRecord=state.cleaningTargets?.[item.id];if(targetRecord)targetRecord.currentAttemptId=attempt.id;
  5074 |           if(wasActivationBlocked)appendEvent('내 청소 시작 가능 안내',`${dateLabel(date)} · ${item.room}호 ${item.kind} · 관리자 조정 완료 · 기존 통보 순서 유지`,{maidIds:[assignment.maidId]});
  5075 |           activated+=1;
  5076 |         });
  5077 |         return activated;
  5078 |       }
  5079 |       function assignmentFor(item) {
  5080 |         const key=item.id;
  5081 |         const previous=state.assignments[key];
  5082 |         if(previous?.status==='cancelled')reopenCancelledAssignmentForNewReservation(state,item);
  5083 |         if(!state.assignments[key])state.assignments[key]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null};
  5084 |         return state.assignments[key];
  5085 |       }
  5086 |       function orderedAssignmentsForMaid(maidId,notifiedOnly=false) {
```

## filtered assignment targets: `filteredAssignmentTargets`

matches: 2

### occurrence 1 · line 5183

```html
  5167 |           const assignment=state.assignments[item.id]||(state.assignments[item.id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null}),selectedMaidId=assignment.maidId||null,notifiedMaidId=assignment.previousMaidId||(assignment.status==='notified'?assignment.maidId:null),notifiedOrder=assignment.previousOrder??assignment.order,beforeMaidId=notifiedMaidId||selectedMaidId||null,beforeOrder=notifiedOrder??assignment.order??null,snapshot=assignment.committedTarget||cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate)),attempt=attemptForCleaningTarget(item),targetRecord=state.cleaningTargets[item.id]||cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate));
  5168 |           Object.assign(targetRecord,{...cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate)),closed:true,closedAt:cancelledAt,closedBy:'관리자 · 데모',closeReasonCode:reasonCode,closeReason:reason,closeStatus:'cancelled'});state.cleaningTargets[item.id]=targetRecord;
  5169 |           const manualTarget=(state.manualAssignmentTargets||[]).find(target=>target.id===item.id);if(manualTarget)Object.assign(manualTarget,{cancelled:true,cancelledAt,cancelledBy:'관리자 · 데모',closeReasonCode:reasonCode,closeReason:reason});
  5170 |           if(attempt&&!attempt.startedAt&&!attempt.completedAt){attempt.status='superseded';attempt.endedAt=cancelledAt;attempt.endReason=reason;if(state.currentAttemptByRoom?.[roomNo]===attempt.id)delete state.currentAttemptByRoom[roomNo];}
  5171 |           Object.assign(assignment,{maidId:'',order:null,status:'cancelled',previousMaidId:null,previousOrder:null,cancelledMaidId:selectedMaidId,cancelledNotifiedMaidId:notifiedMaidId,cancelledOrder:assignment.order??null,cancelledPreviousOrder:notifiedOrder??null,cancelledStatus:assignment.status||'unassigned',cancelledAt,cancelledBy:'관리자 · 데모',cancelledNotifiedAt:assignment.notifiedAt||null,cancelledNotificationRevision:assignment.notificationRevision||null,cancelReasonCode:reasonCode,cancelReason:reason,cancelledReservationId:item.reservationId||null,cancelledObligationKey:cleaningTargetObligationKey(item),committedTarget:snapshot});
  5172 |           state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:item.id,assignmentDate:targetEffectiveDate(item),room:roomNo,beforeMaidId:beforeMaidId||null,afterMaidId:null,before:beforeMaidId?`${maidName(beforeMaidId)} · ${beforeOrder||'순서 없음'}${beforeOrder?'번째':''}`:'미배정',after:'투숙 종료로 요청 취소',reason});
  5173 |           appendEvent(`${roomNo}호 투숙 중 청소 요청 취소`,`${dateLabel(targetEffectiveDate(item))} · 실제 체크아웃으로 미시작 요청 종료 · 기존 배정·일정 기준 보존`);
  5174 |           if(notifiedMaidId)notices.push({maidId:notifiedMaidId,order:notifiedOrder,date:targetEffectiveDate(item),item});
  5175 |         });
  5176 |         const routeByMaidDate=new Map();notices.forEach(notice=>{const key=`${notice.maidId}:${notice.date}`;if(!routeByMaidDate.has(key))routeByMaidDate.set(key,commitRemainingNotifiedOrdersAfterCancellation(notice.maidId,notice.date));});
  5177 |         notices.forEach(notice=>{const remaining=routeByMaidDate.get(`${notice.maidId}:${notice.date}`),routeText=remaining?.route.length?`남은 순서 ${remaining.route.map(entry=>`${entry.order}.${entry.item.room}호(${assignmentScheduleText(entry.item)})`).join(' → ')}`:'남은 청소 없음';appendEvent('내 투숙 중 청소 요청 취소',`${roomNo}호 · 기존 ${notice.order||'순서 없음'}${notice.order?'번째':''} · 실제 체크아웃으로 미시작 요청 종료 · ${routeText}`,{maidIds:[notice.maidId],roomId:roomNo});});
  5178 |         return candidateById.size;
  5179 |       }
  5180 |       function assignmentTypeId(item) {
  5181 |         return assignmentPricingSnapshot(item).typeId;
  5182 |       }
  5183 |       function filteredAssignmentTargets() {
  5184 |         const filter=state.assignmentTypeFilter||'all';
  5185 |         return assignmentTargets().filter(item=>filter==='all'||assignmentTypeId(item)===filter);
  5186 |       }
  5187 |       function assignmentTypeFiltersMarkup() {
  5188 |         const targets=assignmentTargets(),filter=state.assignmentTypeFilter||'all',items=[{id:'all',name:'전체 객실 타입',count:targets.length,meta:'랜덤 배정 대상'},...Object.entries(ROOM_TYPES).map(([id,type])=>({id,name:type.name,count:targets.filter(item=>assignmentTypeId(item)===id).length,meta:`객실당 ${money(type.rate)}`}))];
  5189 |         return `<div class="assignment-type-filters" role="group" aria-label="청소대상 객실 타입 필터">${items.map(item=>`<button class="assignment-type-filter" type="button" data-action="assignment-type-filter" data-type="${esc(item.id)}" aria-pressed="${filter===item.id}" aria-label="${esc(item.name)} ${item.count}건${item.id==='all'?'':`, 청소 요금 ${item.meta.replace('객실당 ','')}`} 보기"><strong>${esc(item.name)}</strong><span>${item.count}건</span><small>${esc(item.meta)}</small></button>`).join('')}</div>`;
  5190 |       }
  5191 |       function assignmentRouteReference(item) {
  5192 |         const assignment=assignmentFor(item);
  5193 |         if(!assignment.maidId){const random=state.randomAssignments?.[item.id];return random?`<span class="assignment-random-note is-warning">${icon('alert','icon-sm')}${esc(random.reason)}</span>`:'<span class="assignment-route-reference">담당 선택 후 아래 순서 보드에 추가</span>';}
  5194 |         return `<span class="assignment-route-reference">${esc(maidName(assignment.maidId))} · 순서 보드 ${assignment.order}번째</span>${randomAssignmentNote(item)}`;
  5195 |       }
  5196 |       function maidOrderItemMarkup(item,ordered,index) {
  5197 |         const assignment=assignmentFor(item),context=assignmentContext(item),name=maidName(assignment.maidId),first=index===0,last=index===ordered.length-1,status=assignment.status==='notified'?'통보 완료':'저장 전',scheduleBadges=assignmentSchedulePriorityBadges(item),guestCount=assignmentGuestCount(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item),disabled=adjustmentBlock?'disabled':'',previous=ordered[index-1],next=ordered[index+1],upDisabled=first||!!adjustmentBlock||!!previous&&!cleaningTargetCanAdjust(previous),downDisabled=last||!!adjustmentBlock||!!next&&!cleaningTargetCanAdjust(next);
  5198 |         return `<article class="maid-order-item ${scheduleBadges.length?'has-schedule-attention':''}"><span class="maid-order-number" aria-hidden="true">${assignment.order}</span><div class="maid-order-copy"><strong>${assignment.order}번째 · ${item.room}호</strong>${scheduleBadges.length?`<div class="maid-order-schedule-badges" aria-label="${item.room}호 일정 주의">${scheduleBadges.join('')}</div>`:''}<span>${esc(context.type.name)} · ${money(context.type.rate)}${guestCount?` · 숙박 ${guestCountLabel(guestCount)}`:''}</span><span>${esc(elevatorLabel(context.room))} · ${esc(item.kind)} · ${status}</span>${adjustmentBlock?`<span>${esc(adjustmentBlock)}</span>`:''}</div><label class="maid-order-assignee"><span class="sr-only">${item.room}호 담당 메이드 변경</span><select class="select-control" data-control="assignment-maid" data-location="board" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 변경" ${disabled}>${assignmentOptions(item)}</select></label><div class="maid-order-controls"><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="up" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 위로 이동" ${upDisabled?'disabled':''}>${icon('arrowUp','icon-sm')}</button><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="down" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 아래로 이동" ${downDisabled?'disabled':''}>${icon('arrowDown','icon-sm')}</button></div></article>`;
  5199 |       }
  5200 |       function renderRandomAssignmentCard() {
  5201 |         const eligible=eligibleAssignmentMaids(),unassigned=assignmentTargets().filter(item=>!assignmentFor(item).maidId&&!roomIsOnHold(item.room)&&cleaningTargetCanAdjust(item)),summary=state.randomAssignmentSummary||{assigned:0,skipped:0},active=!!state.randomAssignmentSnapshot,disabled=state.role!=='admin'||isLocked()||!eligible.length||(!active&&!unassigned.length);
  5202 |         const actions=active?`${button('다시 동선 고려 랜덤 배정','random-assignments','outline',disabled?'disabled':'')}${button('랜덤 배정 전으로 되돌리기','undo-random-assignment','outline',disabled?'disabled':'')}`:button(`미배정 ${unassigned.length}건 동선 고려 랜덤 배정`,'random-assignments','primary',disabled?'disabled':'');
  5203 |         return `<section class="card assignment-random" aria-labelledby="assignment-random-title"><div class="assignment-random-copy"><span class="random-kicker">2단계 · 저장 전 랜덤 초안</span><div class="assignment-random-title-row"><h3 id="assignment-random-title">동선 고려 랜덤 배정</h3><div class="assignment-rule-help"><button class="assignment-rule-help-button" type="button" aria-label="랜덤 배정 기준 설명" aria-describedby="assignment-random-tooltip">${icon('info','icon-sm')}</button><div class="assignment-rule-tooltip" id="assignment-random-tooltip" role="tooltip"><strong>랜덤 배정 기준</strong><span>근무 가능·마감을 먼저 확인합니다.</span><span>총 청소요금 균형을 우선합니다.</span><span>같은 점수에서는 같은 엘리베이터·가까운 호수를 봅니다.</span><span>관리자가 담당과 순서를 최종 수정합니다.</span><span>실제 이동시간을 계산하는 경로 최적화는 아닙니다.</span></div></div></div><p>미배정 객실만 저장 전 초안으로 배정합니다.</p></div><div class="assignment-random-stats"><div><span>근무 가능</span><strong>${eligible.length}명</strong></div><div><span>초안 배정</span><strong>${active?`${summary.assigned}객실`:'실행 전'}</strong></div><div><span>남은 미배정</span><strong>${active?`${summary.skipped}객실`:`${unassigned.length}객실`}</strong></div></div><div class="assignment-random-actions"><div class="random-live" aria-live="polite">${active?`${summary.assigned}건을 랜덤 배정했습니다. 아래에서 담당과 순서를 바꾼 뒤 저장·통보하세요.`:'기존 통보와 관리자가 정한 담당은 유지하고 미배정 객실만 채웁니다.'}</div>${actions}</div></section>`;
  5204 |       }
  5205 |       function renderMaidOrderBoardContent() {
  5206 |         const targets=assignmentTargets(),unassigned=targets.filter(item=>!assignmentFor(item).maidId),assignedMaidIds=new Set(targets.map(item=>assignmentFor(item).maidId).filter(Boolean)),isEditingBalance=targets.some(item=>assignmentFor(item).status==='draft');
  5207 |         const visibleMaidIds=isEditingBalance?new Set([...assignedMaidIds,...eligibleAssignmentMaids().map(maid=>maid.id)]):assignedMaidIds,visibleMaids=MAIDS.filter(maid=>visibleMaidIds.has(maid.id));
  5208 |         const lanes=visibleMaids.map(maid=>{const ordered=orderedAssignmentsForMaid(maid.id),total=ordered.reduce((sum,item)=>sum+assignmentTargetRate(item),0);return `<section class="maid-order-lane" id="maid-order-${maid.id}" aria-labelledby="maid-order-title-${maid.id}"><div class="maid-order-lane-head"><div class="maid-order-lane-copy"><h4 id="maid-order-title-${maid.id}">${esc(maid.name)} 배정 객실·청소 순서</h4><p>각 객실의 담당을 바꾸거나 위·아래 버튼으로 1–N 순서를 조정할 수 있습니다.</p></div><div class="maid-order-lane-total" data-maid-id="${maid.id}" data-maid-total="${total}"><span>총 청소요금 · ${ordered.length}건</span><strong>${money(total)}</strong></div></div><div class="maid-order-list">${ordered.length?ordered.map((item,index)=>maidOrderItemMarkup(item,ordered,index)).join(''):'<div class="maid-order-empty">배정된 객실이 없습니다.</div>'}</div></section>`;}).join('');
  5209 |         const unassignedList=unassigned.length?unassigned.map(item=>{const context=assignmentContext(item);return `<span class="maid-order-unassigned-chip">${item.room}호 · ${esc(context.type.name)} · ${esc(elevatorLabel(context.room))} · ${money(context.type.rate)}</span>`;}).join(''):'<span class="maid-order-unassigned-chip">미배정 객실 없음</span>';
  5210 |         return `<section class="card maid-order-panel" aria-labelledby="maid-order-board-title"><div class="assignment-panel-head"><div><span class="assignment-step-label">4단계 · 세부 수정</span><h3 id="maid-order-board-title">메이드별 청소 순서 수정</h3><p>얼리 체크인·레이트 체크아웃의 조정된 예정 시각을 먼저 확인하고, 객실 담당과 1–N 순서를 직접 수정합니다.</p></div>${statusBadge(`${unassigned.length}건 미배정`,unassigned.length?'red':'green')}</div><div class="maid-order-board ${lanes?'':'is-empty'}">${lanes||'<div class="maid-order-empty">아직 배정된 객실이 없습니다. 랜덤 배정하거나 위 객실 표에서 담당을 선택하세요.</div>'}</div><div class="maid-order-unassigned"><div><h4>아직 순서가 없는 객실</h4><p>미배정 상태로 남겨 두고 담당이 정해진 객실만 먼저 통보할 수 있습니다.</p></div><div class="maid-order-unassigned-list">${unassignedList}</div></div><div class="assignment-foot"><p>랜덤 배정은 저장 전 초안입니다. 담당과 연속 순서가 정해진 객실만 저장·통보합니다.</p>${button(`배정된 변경 ${assignmentTargets().filter(item=>assignmentHasNetChange(item)&&assignmentFor(item).maidId).length}건 저장·통보`,'save-assignments','primary',assignmentCanSave()?'':'disabled')}</div></section>`;
  5211 |       }
  5212 |       function assignmentCountsForDate(assignmentDate=state.assignmentDate) {
  5213 |         const targets=assignmentTargetsForDate(assignmentDate),rows=targets.map(item=>state.assignments?.[item.id]||{maidId:'',status:'unassigned'}),assigned=rows.filter(item=>item.maidId).length,notified=targets.filter(item=>{const record=state.assignments?.[item.id];return !!(record?.status==='notified'&&record.maidId||record?.previousMaidId);}).length;
  5214 |         return {total:rows.length,assigned,notified,unassigned:rows.length-assigned,carryover:targets.filter(item=>item.carryReason).length,automatic:targets.filter(item=>item.source!=='manual').length,manual:targets.filter(item=>item.source==='manual').length,checkout:targets.filter(item=>item.source==='checkout').length,stayover:targets.filter(item=>item.source==='stayover').length,submitted:MAIDS.filter(maid=>availabilityForWorkDate(maid.id,assignmentDate)!=='missing').length};
  5215 |       }
  5216 |       function assignmentCounts() { return assignmentCountsForDate(state.assignmentDate); }
  5217 |       function assignmentCanSave() {
```

### occurrence 2 · line 5356

```html
  5340 |         else parts.push(`체크아웃 ${item.checkout||'—'} → 준비 마감 ${item.deadline||'—'}`);
  5341 |         if(assignmentGuestCount(item))parts.push(`숙박 인원 ${guestCountLabel(assignmentGuestCount(item))}`);
  5342 |         if(context.early)parts.push(reservationStatusText(context,'checkin'));
  5343 |         if(context.late)parts.push(reservationStatusText(context,'checkout'));
  5344 |         return parts.join(' · ');
  5345 |       }
  5346 |       function assignmentSourceMarkup(item) {
  5347 |         const cls=item.source==='manual'?'manual':item.source==='stayover'?'stayover':'',label=item.sourceLabel||'직접 등록';
  5348 |         const rollover=item.carryReason?`<span class="assignment-source stayover">${icon('clock','icon-sm')}${item.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료'}</span>`:'';
  5349 |         return `${rollover}<span class="assignment-source ${cls}">${icon(item.source==='manual'?'user':'sync','icon-sm')}${item.source==='manual'?'직접 등록':`자동 · ${esc(label)}`}</span>`;
  5350 |       }
  5351 |       function assignmentAdjustmentMarkup(item) {
  5352 |         const assignment=assignmentFor(item),activationBlocked=!!assignment.activationBlockedBy&&targetEffectiveDate(item)===state.selectedDate,status=activationBlocked?'활성화 보류':assignment.status==='notified'?'통보 완료':assignment.maidId?'저장 전':'미배정',tone=activationBlocked?'amber':assignment.status==='notified'?'green':assignment.maidId?'amber':'red',notified=!!(assignment.previousMaidId||assignment.status==='notified'),block=cleaningTargetAdjustmentBlock(item),label=notified?'청소 취소·통보':'청소대상 취소';
  5353 |         return `<div class="assignment-cell-stack">${statusBadge(status,tone)}${assignment.maidId?'<span class="cell-sub">순서 보드 반영</span>':''}${button(label,'cancel-cleaning-target','outline',`data-target="${esc(item.id)}" aria-label="${esc(dateLabel(targetEffectiveDate(item)))} ${item.room}호 ${esc(label)}" ${block?'disabled':''}`)}${block?`<span class="cell-sub">${esc(block)}</span>`:''}</div>`;
  5354 |       }
  5355 |       function renderAssignmentDashboard() {
  5356 |         const counts=assignmentCounts(),targets=assignmentTargets(),visibleTargets=filteredAssignmentTargets(),activeType=state.assignmentTypeFilter==='all'?null:ROOM_TYPES[state.assignmentTypeFilter];
  5357 |         const rows=visibleTargets.map(item=>{const context=assignmentContext(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item);return `<tr><td data-label="객실·타입·요금"><div class="assignment-cell-stack"><strong>${item.room}호</strong><span class="assignment-room-type">${esc(context.type.name)}</span><span class="assignment-elevator">${icon('mapPin','icon-sm')}${esc(elevatorLabel(context.room))}</span><span class="assignment-fee">${money(context.type.rate)} · 8월 시트</span></div></td><td data-label="청소 정보"><div class="assignment-cell-stack"><strong>${esc(item.kind)}</strong>${assignmentSourceMarkup(item)}</div></td><td data-label="일정">${assignmentScheduleMarkup(item)}</td><td data-label="담당 메이드"><div class="assignment-assignee"><select class="select-control" data-control="assignment-maid" data-location="table" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 · 근무 가능 제출자만 표시" ${adjustmentBlock?'disabled':''}>${assignmentOptions(item)}</select>${assignmentRouteReference(item)}</div></td><td data-label="상태·조정">${assignmentAdjustmentMarkup(item)}</td></tr>`;}).join('');
  5358 |         const history=state.assignmentHistory.map(entry=>`<div class="assignment-history-row"><strong>${esc(entry.time)}</strong><span>${esc(entry.room)}호</span><span>${esc(entry.before)} → ${esc(entry.after)}</span><span>${esc(entry.reason)}</span></div>`).join('');
  5359 |         const emptyRows=`<tr><td colspan="5"><div class="inline-empty"><h3>이 타입의 청소대상이 없습니다</h3><p>다른 타입을 선택하거나 전체 객실을 확인하세요.</p></div></td></tr>`;
  5360 |         const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일',weekStart=weekStartIso(state.assignmentDate),weekEnd=addIsoDays(weekStart,6);
  5361 |         return `<div class="assignment-page"><div class="assignment-intro"><div><h2>${dayWord} 청소 배정</h2><p>${dateLabel(state.assignmentDate)} · 근무표 확인 → 동선 고려 랜덤 초안 → 담당·순서 수정 → 저장·통보</p></div><div class="job-actions">${button('주간 근무 기록','go-work-history','outline')}${button(`${dayWord} 청소 추가`,'new-cleaning','outline')}</div></div><section class="card assignment-summary"><div><span>근무 가능일 제출</span><strong>${counts.submitted} / ${MAIDS.length}</strong><small>메이드 제출 현황</small></div><div><span>${dayWord} 청소 대상 객실</span><strong>${counts.total}</strong><small>전일 이월 ${counts.carryover} · 신규 ${counts.total-counts.carryover}</small></div><div class="summary-good"><span>담당 선택</span><strong>${counts.assigned}</strong><small>통보 완료 ${counts.notified}건</small></div><div class="summary-warn"><span>미배정</span><strong>${counts.unassigned}</strong><small>대기 유지 · 후속 배정 가능</small></div></section><section class="assignment-target-rule" aria-label="청소대상 자동 구성">${icon('sync')}<div><strong>${dayWord} 체크아웃·투숙 중 청소·전일 이월 객실을 한 목록에 모읍니다.</strong><p>${dayWord} 생긴 현장 요청은 직접 추가하고, 미시작 대상은 사유를 남겨 취소·통보할 수 있습니다.</p></div><div class="badge-row">${statusBadge(`전일 이월 ${counts.carryover}`,'amber')}${statusBadge(`체크아웃 ${counts.checkout}`,'blue')}${statusBadge(`연박 ${counts.stayover}`,'neutral')}${statusBadge(`직접 ${counts.manual}`,'amber')}</div></section><section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>${dateLabel(weekStart)}–${dateLabel(weekEnd)} · Asia/Seoul</p></div>${statusBadge(`${counts.submitted}/${MAIDS.length} 제출`,counts.submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section>${renderRandomAssignmentCard()}<section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">3단계 · 세부 수정</span><h3>객실별 담당 수정</h3><p>랜덤 초안 뒤 필요한 객실만 조정합니다. 얼리·레이트·연박 일정은 해당 객실 행에서 함께 확인합니다.</p></div>${statusBadge(`${visibleTargets.length}/${targets.length}건 표시`,'blue')}</div>${assignmentTypeFiltersMarkup()}<div class="assignment-filter-context">${icon('filter','icon-sm')}<span><strong>${activeType?esc(activeType.name):'전체 객실 타입'}</strong> ${visibleTargets.length}건 표시 · 전체 ${targets.length}건 현황을 유지하며 배정된 객실만 통보합니다.</span></div><div class="assignment-table-wrap"><table class="assignment-table"><thead><tr><th scope="col">객실·타입·요금</th><th scope="col">청소 정보·등록 근거</th><th scope="col">일정</th><th scope="col">담당 메이드</th><th scope="col">상태·조정</th></tr></thead><tbody>${rows||emptyRows}</tbody></table></div><div class="assignment-foot"><p>담당을 바꾸면 해당 객실이 새 메이드 순서의 마지막으로 이동합니다. 이미 시작한 청소는 진행 중 탭에서 관리합니다.</p></div></section>${renderMaidOrderBoardContent()}<section class="card assignment-history"><div class="assignment-panel-head"><div><h3>배정·순서 통보 이력</h3><p>담당과 청소 순서의 이전 값을 덮어쓰지 않고 변경 이력을 추가합니다.</p></div>${statusBadge('관리자 전용','neutral')}</div><div class="assignment-history-list">${history}</div></section></div>`;
  5362 |       }
  5363 |       function cleaningTabButton(id,label,count) { return `<button type="button" role="tab" data-action="cleaning-tab" data-tab="${id}" aria-selected="${state.cleaningTab===id}">${label} ${count}</button>`; }
  5364 |       function rolloverMetaForRoom(no) {
  5365 |         const attempt=state.cleaningAttempts?.[currentAttemptId(no)];if(attemptIsRollover(attempt))return {carryReason:attempt.carryReason||'started-unfinished',planDate:attemptPlanDate(attempt),effectiveDate:attemptEffectiveDate(attempt),rolloverCount:Number(attempt.rolloverCount)||1};
  5366 |         const target=Object.values(state.cleaningTargets||{}).find(item=>item.room===no&&item.carryReason&&!item.closed);return target?{carryReason:target.carryReason,planDate:targetPlanDate(target),effectiveDate:targetEffectiveDate(target),rolloverCount:Number(target.rolloverCount)||1}:null;
  5367 |       }
  5368 |       function rolloverBadgeMarkup(meta,{compact=false}={}) {
  5369 |         if(!meta)return '';
  5370 |         const label=meta.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료',detail=`원 계획 ${dateLabel(meta.planDate)} · 이월 ${meta.rolloverCount}일째`;
  5371 |         return `<div class="badge-row${compact?' compact':''}" style="margin-top:7px">${statusBadge(label,'amber')}<span class="cell-sub">${esc(detail)}</span></div>`;
  5372 |       }
  5373 |       function cleaningProgressEntries() {
  5374 |         const allowed=['scheduled','claimed','cleaning','upload','reclean','hold'];
  5375 |         return Object.entries(state.jobs).filter(([no,job])=>{
  5376 |           if(!allowed.includes(job))return false;
  5377 |           const rollover=rolloverMetaForRoom(no);
  5378 |           return !rollover||rollover.carryReason==='started-unfinished'||!!activeUnfinishedAttempt(no);
  5379 |         });
  5380 |       }
  5381 |       function renderCleaningHub() {
  5382 |         const todayDate=state.selectedDate,tomorrowDate=addIsoDays(state.selectedDate,1),tabCounts={today:assignmentCountsForDate(todayDate).total,tomorrow:assignmentCountsForDate(tomorrowDate).total,progress:cleaningProgressEntries().length,inspection:Object.values(state.jobs).filter(v=>v==='inspection').length,done:Object.values(state.jobs).filter(v=>v==='approved').length};
  5383 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>청소 관리</h2><p>오늘 운영 조정과 내일 사전 배정을 분리하고, 변경 내용은 해당 메이드에게 다시 알립니다.</p></div></div><div class="tabs" role="tablist" aria-label="청소 상태">${cleaningTabButton('assignment-today','오늘 배정',tabCounts.today)}${cleaningTabButton('assignment-tomorrow','내일 배정',tabCounts.tomorrow)}${cleaningTabButton('progress','진행 중',tabCounts.progress)}${cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)}${cleaningTabButton('done','완료',tabCounts.done)}</div>${renderListState(renderCleaningTab())}</div>`;
  5384 |       }
  5385 |       function taskRow(no,job,extra='') {
  5386 |         const room=ROOMS.find(r=>r.no===no),liveType=ROOM_TYPES[room?.type||'standard'],validSubmission=currentSubmission(no),submittedContext=['inspection','approved'].includes(job),submission=submittedContext?(validSubmission||currentSubmissionRecord(no)):validSubmission,submissionMeta=submission?.roomMetaSnapshot,displayType=submittedContext?(ROOM_TYPES[submissionMeta?.typeId]||liveType):liveType,displayTypeName=submittedContext?(submissionMeta?.typeName||displayType.name):displayType.name,displayElevator=submittedContext?(submissionMeta?.elevator?`${submissionMeta.elevator} 엘리베이터`:'엘리베이터 미기재'):elevatorLabel(room),activeAttempt=state.cleaningAttempts?.[currentAttemptId(no)],rollover=rolloverMetaForRoom(no),report=submittedContext?(validSubmission?submittedBombRoomReport(no):rawBombRoomReportForSubmission(submission)):activeBombRoomReport(no),record=submittedContext?earningRecordFor(no):earningRecordForReport(report),wholeRejected=submittedContext&&submission?.status==='rejected',unpaidReclean=submittedContext?submission?.kind==='재청소':activeAttempt?.kind==='재청소',bombMeta=wholeRejected?{label:'청소 전체 반려 · 적립 없음',tone:'red'}:bombRoomStatusMeta(report),fee=record||bombRoomBreakdown(no,{pendingAsBonus:!unpaidReclean&&(submittedContext?submission?.status==='pending':true)&&report?.status==='pending',reportOverride:report,baseOverride:submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot}),performer=submittedContext?submission?.performerName:room?.assignee;
  5387 |         const displayRate=unpaidReclean?0:record?.base??(submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot)??displayType.rate,displayKind=(submittedContext?submission?.kind:activeAttempt?.kind)||(job==='reclean'?'재청소':'퇴실 청소');
  5388 |         const action=job==='inspection'?['전체 검수','cleaning-detail']:job==='approved'?['결과 보기','cleaning-detail']:['진행 보기','cleaning-detail'];
  5389 |         return `<article class="card task-row"><div><h3>${no}호 · ${esc(displayKind)} · ${statusLabel(job)}</h3><p>${esc(displayTypeName)} · ${esc(displayElevator)} · ${money(displayRate)} · ${submission?.templateSnapshot?.minutes??displayType.minutes}분 · 데모</p>${rolloverBadgeMarkup(rollover,{compact:true})}${submittedContext&&!validSubmission?`<div class="badge-row" style="margin-top:7px">${statusBadge('제출 연결 확인 필요','red')}</div>`:''}${report?`<div class="badge-row" style="margin-top:7px">${statusBadge(bombMeta.label,bombMeta.tone)}<span class="cell-sub">${wholeRejected?'적립':record?'확정':report.status==='pending'?'폭탄방 승인 시':'전체 승인 시'} ${money(wholeRejected?0:fee.total)}</span></div>`:unpaidReclean?`<div class="badge-row" style="margin-top:7px">${statusBadge('본인 재청소 · 무급','neutral')}<span class="cell-sub">수익 원장 없음 · 0원</span></div>`:''}${extra}</div><div class="task-meta"><span>일정</span><strong>${room?.checkout||'11:00'} → ${room?.checkin||'16:00'}</strong></div><div class="task-meta"><span>${submittedContext?'수행자':'담당'}</span><strong>${esc(performer||'미정')}</strong></div><div class="task-row-action">${button(action[0],action[1],job==='inspection'?'primary':'outline',`data-id="${no}"`)}</div></article>`;
  5390 |       }
```

## cleaning target rows: `객실별 담당 수정`

matches: 1

### occurrence 1 · line 5361

```html
  5345 |       }
  5346 |       function assignmentSourceMarkup(item) {
  5347 |         const cls=item.source==='manual'?'manual':item.source==='stayover'?'stayover':'',label=item.sourceLabel||'직접 등록';
  5348 |         const rollover=item.carryReason?`<span class="assignment-source stayover">${icon('clock','icon-sm')}${item.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료'}</span>`:'';
  5349 |         return `${rollover}<span class="assignment-source ${cls}">${icon(item.source==='manual'?'user':'sync','icon-sm')}${item.source==='manual'?'직접 등록':`자동 · ${esc(label)}`}</span>`;
  5350 |       }
  5351 |       function assignmentAdjustmentMarkup(item) {
  5352 |         const assignment=assignmentFor(item),activationBlocked=!!assignment.activationBlockedBy&&targetEffectiveDate(item)===state.selectedDate,status=activationBlocked?'활성화 보류':assignment.status==='notified'?'통보 완료':assignment.maidId?'저장 전':'미배정',tone=activationBlocked?'amber':assignment.status==='notified'?'green':assignment.maidId?'amber':'red',notified=!!(assignment.previousMaidId||assignment.status==='notified'),block=cleaningTargetAdjustmentBlock(item),label=notified?'청소 취소·통보':'청소대상 취소';
  5353 |         return `<div class="assignment-cell-stack">${statusBadge(status,tone)}${assignment.maidId?'<span class="cell-sub">순서 보드 반영</span>':''}${button(label,'cancel-cleaning-target','outline',`data-target="${esc(item.id)}" aria-label="${esc(dateLabel(targetEffectiveDate(item)))} ${item.room}호 ${esc(label)}" ${block?'disabled':''}`)}${block?`<span class="cell-sub">${esc(block)}</span>`:''}</div>`;
  5354 |       }
  5355 |       function renderAssignmentDashboard() {
  5356 |         const counts=assignmentCounts(),targets=assignmentTargets(),visibleTargets=filteredAssignmentTargets(),activeType=state.assignmentTypeFilter==='all'?null:ROOM_TYPES[state.assignmentTypeFilter];
  5357 |         const rows=visibleTargets.map(item=>{const context=assignmentContext(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item);return `<tr><td data-label="객실·타입·요금"><div class="assignment-cell-stack"><strong>${item.room}호</strong><span class="assignment-room-type">${esc(context.type.name)}</span><span class="assignment-elevator">${icon('mapPin','icon-sm')}${esc(elevatorLabel(context.room))}</span><span class="assignment-fee">${money(context.type.rate)} · 8월 시트</span></div></td><td data-label="청소 정보"><div class="assignment-cell-stack"><strong>${esc(item.kind)}</strong>${assignmentSourceMarkup(item)}</div></td><td data-label="일정">${assignmentScheduleMarkup(item)}</td><td data-label="담당 메이드"><div class="assignment-assignee"><select class="select-control" data-control="assignment-maid" data-location="table" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 · 근무 가능 제출자만 표시" ${adjustmentBlock?'disabled':''}>${assignmentOptions(item)}</select>${assignmentRouteReference(item)}</div></td><td data-label="상태·조정">${assignmentAdjustmentMarkup(item)}</td></tr>`;}).join('');
  5358 |         const history=state.assignmentHistory.map(entry=>`<div class="assignment-history-row"><strong>${esc(entry.time)}</strong><span>${esc(entry.room)}호</span><span>${esc(entry.before)} → ${esc(entry.after)}</span><span>${esc(entry.reason)}</span></div>`).join('');
  5359 |         const emptyRows=`<tr><td colspan="5"><div class="inline-empty"><h3>이 타입의 청소대상이 없습니다</h3><p>다른 타입을 선택하거나 전체 객실을 확인하세요.</p></div></td></tr>`;
  5360 |         const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일',weekStart=weekStartIso(state.assignmentDate),weekEnd=addIsoDays(weekStart,6);
  5361 |         return `<div class="assignment-page"><div class="assignment-intro"><div><h2>${dayWord} 청소 배정</h2><p>${dateLabel(state.assignmentDate)} · 근무표 확인 → 동선 고려 랜덤 초안 → 담당·순서 수정 → 저장·통보</p></div><div class="job-actions">${button('주간 근무 기록','go-work-history','outline')}${button(`${dayWord} 청소 추가`,'new-cleaning','outline')}</div></div><section class="card assignment-summary"><div><span>근무 가능일 제출</span><strong>${counts.submitted} / ${MAIDS.length}</strong><small>메이드 제출 현황</small></div><div><span>${dayWord} 청소 대상 객실</span><strong>${counts.total}</strong><small>전일 이월 ${counts.carryover} · 신규 ${counts.total-counts.carryover}</small></div><div class="summary-good"><span>담당 선택</span><strong>${counts.assigned}</strong><small>통보 완료 ${counts.notified}건</small></div><div class="summary-warn"><span>미배정</span><strong>${counts.unassigned}</strong><small>대기 유지 · 후속 배정 가능</small></div></section><section class="assignment-target-rule" aria-label="청소대상 자동 구성">${icon('sync')}<div><strong>${dayWord} 체크아웃·투숙 중 청소·전일 이월 객실을 한 목록에 모읍니다.</strong><p>${dayWord} 생긴 현장 요청은 직접 추가하고, 미시작 대상은 사유를 남겨 취소·통보할 수 있습니다.</p></div><div class="badge-row">${statusBadge(`전일 이월 ${counts.carryover}`,'amber')}${statusBadge(`체크아웃 ${counts.checkout}`,'blue')}${statusBadge(`연박 ${counts.stayover}`,'neutral')}${statusBadge(`직접 ${counts.manual}`,'amber')}</div></section><section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>${dateLabel(weekStart)}–${dateLabel(weekEnd)} · Asia/Seoul</p></div>${statusBadge(`${counts.submitted}/${MAIDS.length} 제출`,counts.submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section>${renderRandomAssignmentCard()}<section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">3단계 · 세부 수정</span><h3>객실별 담당 수정</h3><p>랜덤 초안 뒤 필요한 객실만 조정합니다. 얼리·레이트·연박 일정은 해당 객실 행에서 함께 확인합니다.</p></div>${statusBadge(`${visibleTargets.length}/${targets.length}건 표시`,'blue')}</div>${assignmentTypeFiltersMarkup()}<div class="assignment-filter-context">${icon('filter','icon-sm')}<span><strong>${activeType?esc(activeType.name):'전체 객실 타입'}</strong> ${visibleTargets.length}건 표시 · 전체 ${targets.length}건 현황을 유지하며 배정된 객실만 통보합니다.</span></div><div class="assignment-table-wrap"><table class="assignment-table"><thead><tr><th scope="col">객실·타입·요금</th><th scope="col">청소 정보·등록 근거</th><th scope="col">일정</th><th scope="col">담당 메이드</th><th scope="col">상태·조정</th></tr></thead><tbody>${rows||emptyRows}</tbody></table></div><div class="assignment-foot"><p>담당을 바꾸면 해당 객실이 새 메이드 순서의 마지막으로 이동합니다. 이미 시작한 청소는 진행 중 탭에서 관리합니다.</p></div></section>${renderMaidOrderBoardContent()}<section class="card assignment-history"><div class="assignment-panel-head"><div><h3>배정·순서 통보 이력</h3><p>담당과 청소 순서의 이전 값을 덮어쓰지 않고 변경 이력을 추가합니다.</p></div>${statusBadge('관리자 전용','neutral')}</div><div class="assignment-history-list">${history}</div></section></div>`;
  5362 |       }
  5363 |       function cleaningTabButton(id,label,count) { return `<button type="button" role="tab" data-action="cleaning-tab" data-tab="${id}" aria-selected="${state.cleaningTab===id}">${label} ${count}</button>`; }
  5364 |       function rolloverMetaForRoom(no) {
  5365 |         const attempt=state.cleaningAttempts?.[currentAttemptId(no)];if(attemptIsRollover(attempt))return {carryReason:attempt.carryReason||'started-unfinished',planDate:attemptPlanDate(attempt),effectiveDate:attemptEffectiveDate(attempt),rolloverCount:Number(attempt.rolloverCount)||1};
  5366 |         const target=Object.values(state.cleaningTargets||{}).find(item=>item.room===no&&item.carryReason&&!item.closed);return target?{carryReason:target.carryReason,planDate:targetPlanDate(target),effectiveDate:targetEffectiveDate(target),rolloverCount:Number(target.rolloverCount)||1}:null;
  5367 |       }
  5368 |       function rolloverBadgeMarkup(meta,{compact=false}={}) {
  5369 |         if(!meta)return '';
  5370 |         const label=meta.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료',detail=`원 계획 ${dateLabel(meta.planDate)} · 이월 ${meta.rolloverCount}일째`;
  5371 |         return `<div class="badge-row${compact?' compact':''}" style="margin-top:7px">${statusBadge(label,'amber')}<span class="cell-sub">${esc(detail)}</span></div>`;
  5372 |       }
  5373 |       function cleaningProgressEntries() {
  5374 |         const allowed=['scheduled','claimed','cleaning','upload','reclean','hold'];
  5375 |         return Object.entries(state.jobs).filter(([no,job])=>{
  5376 |           if(!allowed.includes(job))return false;
  5377 |           const rollover=rolloverMetaForRoom(no);
  5378 |           return !rollover||rollover.carryReason==='started-unfinished'||!!activeUnfinishedAttempt(no);
  5379 |         });
  5380 |       }
  5381 |       function renderCleaningHub() {
  5382 |         const todayDate=state.selectedDate,tomorrowDate=addIsoDays(state.selectedDate,1),tabCounts={today:assignmentCountsForDate(todayDate).total,tomorrow:assignmentCountsForDate(tomorrowDate).total,progress:cleaningProgressEntries().length,inspection:Object.values(state.jobs).filter(v=>v==='inspection').length,done:Object.values(state.jobs).filter(v=>v==='approved').length};
  5383 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>청소 관리</h2><p>오늘 운영 조정과 내일 사전 배정을 분리하고, 변경 내용은 해당 메이드에게 다시 알립니다.</p></div></div><div class="tabs" role="tablist" aria-label="청소 상태">${cleaningTabButton('assignment-today','오늘 배정',tabCounts.today)}${cleaningTabButton('assignment-tomorrow','내일 배정',tabCounts.tomorrow)}${cleaningTabButton('progress','진행 중',tabCounts.progress)}${cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)}${cleaningTabButton('done','완료',tabCounts.done)}</div>${renderListState(renderCleaningTab())}</div>`;
  5384 |       }
  5385 |       function taskRow(no,job,extra='') {
  5386 |         const room=ROOMS.find(r=>r.no===no),liveType=ROOM_TYPES[room?.type||'standard'],validSubmission=currentSubmission(no),submittedContext=['inspection','approved'].includes(job),submission=submittedContext?(validSubmission||currentSubmissionRecord(no)):validSubmission,submissionMeta=submission?.roomMetaSnapshot,displayType=submittedContext?(ROOM_TYPES[submissionMeta?.typeId]||liveType):liveType,displayTypeName=submittedContext?(submissionMeta?.typeName||displayType.name):displayType.name,displayElevator=submittedContext?(submissionMeta?.elevator?`${submissionMeta.elevator} 엘리베이터`:'엘리베이터 미기재'):elevatorLabel(room),activeAttempt=state.cleaningAttempts?.[currentAttemptId(no)],rollover=rolloverMetaForRoom(no),report=submittedContext?(validSubmission?submittedBombRoomReport(no):rawBombRoomReportForSubmission(submission)):activeBombRoomReport(no),record=submittedContext?earningRecordFor(no):earningRecordForReport(report),wholeRejected=submittedContext&&submission?.status==='rejected',unpaidReclean=submittedContext?submission?.kind==='재청소':activeAttempt?.kind==='재청소',bombMeta=wholeRejected?{label:'청소 전체 반려 · 적립 없음',tone:'red'}:bombRoomStatusMeta(report),fee=record||bombRoomBreakdown(no,{pendingAsBonus:!unpaidReclean&&(submittedContext?submission?.status==='pending':true)&&report?.status==='pending',reportOverride:report,baseOverride:submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot}),performer=submittedContext?submission?.performerName:room?.assignee;
  5387 |         const displayRate=unpaidReclean?0:record?.base??(submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot)??displayType.rate,displayKind=(submittedContext?submission?.kind:activeAttempt?.kind)||(job==='reclean'?'재청소':'퇴실 청소');
  5388 |         const action=job==='inspection'?['전체 검수','cleaning-detail']:job==='approved'?['결과 보기','cleaning-detail']:['진행 보기','cleaning-detail'];
  5389 |         return `<article class="card task-row"><div><h3>${no}호 · ${esc(displayKind)} · ${statusLabel(job)}</h3><p>${esc(displayTypeName)} · ${esc(displayElevator)} · ${money(displayRate)} · ${submission?.templateSnapshot?.minutes??displayType.minutes}분 · 데모</p>${rolloverBadgeMarkup(rollover,{compact:true})}${submittedContext&&!validSubmission?`<div class="badge-row" style="margin-top:7px">${statusBadge('제출 연결 확인 필요','red')}</div>`:''}${report?`<div class="badge-row" style="margin-top:7px">${statusBadge(bombMeta.label,bombMeta.tone)}<span class="cell-sub">${wholeRejected?'적립':record?'확정':report.status==='pending'?'폭탄방 승인 시':'전체 승인 시'} ${money(wholeRejected?0:fee.total)}</span></div>`:unpaidReclean?`<div class="badge-row" style="margin-top:7px">${statusBadge('본인 재청소 · 무급','neutral')}<span class="cell-sub">수익 원장 없음 · 0원</span></div>`:''}${extra}</div><div class="task-meta"><span>일정</span><strong>${room?.checkout||'11:00'} → ${room?.checkin||'16:00'}</strong></div><div class="task-meta"><span>${submittedContext?'수행자':'담당'}</span><strong>${esc(performer||'미정')}</strong></div><div class="task-row-action">${button(action[0],action[1],job==='inspection'?'primary':'outline',`data-id="${no}"`)}</div></article>`;
  5390 |       }
  5391 |       function renderCleaningTab() {
  5392 |         if(isCleaningAssignmentTab(state.cleaningTab))return renderAssignmentDashboard();
  5393 |         const allowed=state.cleaningTab==='progress'?['scheduled','claimed','cleaning','upload','reclean','hold']:state.cleaningTab==='inspection'?['inspection']:['approved'];
  5394 |         const entries=state.cleaningTab==='progress'?cleaningProgressEntries():Object.entries(state.jobs).filter(([,v])=>allowed.includes(v)),rows=entries.map(([no,v])=>taskRow(no,v)).join('');
  5395 |         return `<div class="tab-panel">${rows||`<section class="inline-empty"><h3>이 상태의 작업이 없습니다</h3><p>다른 탭에서 진행 상태를 확인하세요.</p></section>`}</div>`;
```

## unassigned room cards: `아직 순서가 없는 객실`

matches: 1

### occurrence 1 · line 5210

```html
  5194 |         return `<span class="assignment-route-reference">${esc(maidName(assignment.maidId))} · 순서 보드 ${assignment.order}번째</span>${randomAssignmentNote(item)}`;
  5195 |       }
  5196 |       function maidOrderItemMarkup(item,ordered,index) {
  5197 |         const assignment=assignmentFor(item),context=assignmentContext(item),name=maidName(assignment.maidId),first=index===0,last=index===ordered.length-1,status=assignment.status==='notified'?'통보 완료':'저장 전',scheduleBadges=assignmentSchedulePriorityBadges(item),guestCount=assignmentGuestCount(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item),disabled=adjustmentBlock?'disabled':'',previous=ordered[index-1],next=ordered[index+1],upDisabled=first||!!adjustmentBlock||!!previous&&!cleaningTargetCanAdjust(previous),downDisabled=last||!!adjustmentBlock||!!next&&!cleaningTargetCanAdjust(next);
  5198 |         return `<article class="maid-order-item ${scheduleBadges.length?'has-schedule-attention':''}"><span class="maid-order-number" aria-hidden="true">${assignment.order}</span><div class="maid-order-copy"><strong>${assignment.order}번째 · ${item.room}호</strong>${scheduleBadges.length?`<div class="maid-order-schedule-badges" aria-label="${item.room}호 일정 주의">${scheduleBadges.join('')}</div>`:''}<span>${esc(context.type.name)} · ${money(context.type.rate)}${guestCount?` · 숙박 ${guestCountLabel(guestCount)}`:''}</span><span>${esc(elevatorLabel(context.room))} · ${esc(item.kind)} · ${status}</span>${adjustmentBlock?`<span>${esc(adjustmentBlock)}</span>`:''}</div><label class="maid-order-assignee"><span class="sr-only">${item.room}호 담당 메이드 변경</span><select class="select-control" data-control="assignment-maid" data-location="board" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 변경" ${disabled}>${assignmentOptions(item)}</select></label><div class="maid-order-controls"><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="up" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 위로 이동" ${upDisabled?'disabled':''}>${icon('arrowUp','icon-sm')}</button><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="down" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 아래로 이동" ${downDisabled?'disabled':''}>${icon('arrowDown','icon-sm')}</button></div></article>`;
  5199 |       }
  5200 |       function renderRandomAssignmentCard() {
  5201 |         const eligible=eligibleAssignmentMaids(),unassigned=assignmentTargets().filter(item=>!assignmentFor(item).maidId&&!roomIsOnHold(item.room)&&cleaningTargetCanAdjust(item)),summary=state.randomAssignmentSummary||{assigned:0,skipped:0},active=!!state.randomAssignmentSnapshot,disabled=state.role!=='admin'||isLocked()||!eligible.length||(!active&&!unassigned.length);
  5202 |         const actions=active?`${button('다시 동선 고려 랜덤 배정','random-assignments','outline',disabled?'disabled':'')}${button('랜덤 배정 전으로 되돌리기','undo-random-assignment','outline',disabled?'disabled':'')}`:button(`미배정 ${unassigned.length}건 동선 고려 랜덤 배정`,'random-assignments','primary',disabled?'disabled':'');
  5203 |         return `<section class="card assignment-random" aria-labelledby="assignment-random-title"><div class="assignment-random-copy"><span class="random-kicker">2단계 · 저장 전 랜덤 초안</span><div class="assignment-random-title-row"><h3 id="assignment-random-title">동선 고려 랜덤 배정</h3><div class="assignment-rule-help"><button class="assignment-rule-help-button" type="button" aria-label="랜덤 배정 기준 설명" aria-describedby="assignment-random-tooltip">${icon('info','icon-sm')}</button><div class="assignment-rule-tooltip" id="assignment-random-tooltip" role="tooltip"><strong>랜덤 배정 기준</strong><span>근무 가능·마감을 먼저 확인합니다.</span><span>총 청소요금 균형을 우선합니다.</span><span>같은 점수에서는 같은 엘리베이터·가까운 호수를 봅니다.</span><span>관리자가 담당과 순서를 최종 수정합니다.</span><span>실제 이동시간을 계산하는 경로 최적화는 아닙니다.</span></div></div></div><p>미배정 객실만 저장 전 초안으로 배정합니다.</p></div><div class="assignment-random-stats"><div><span>근무 가능</span><strong>${eligible.length}명</strong></div><div><span>초안 배정</span><strong>${active?`${summary.assigned}객실`:'실행 전'}</strong></div><div><span>남은 미배정</span><strong>${active?`${summary.skipped}객실`:`${unassigned.length}객실`}</strong></div></div><div class="assignment-random-actions"><div class="random-live" aria-live="polite">${active?`${summary.assigned}건을 랜덤 배정했습니다. 아래에서 담당과 순서를 바꾼 뒤 저장·통보하세요.`:'기존 통보와 관리자가 정한 담당은 유지하고 미배정 객실만 채웁니다.'}</div>${actions}</div></section>`;
  5204 |       }
  5205 |       function renderMaidOrderBoardContent() {
  5206 |         const targets=assignmentTargets(),unassigned=targets.filter(item=>!assignmentFor(item).maidId),assignedMaidIds=new Set(targets.map(item=>assignmentFor(item).maidId).filter(Boolean)),isEditingBalance=targets.some(item=>assignmentFor(item).status==='draft');
  5207 |         const visibleMaidIds=isEditingBalance?new Set([...assignedMaidIds,...eligibleAssignmentMaids().map(maid=>maid.id)]):assignedMaidIds,visibleMaids=MAIDS.filter(maid=>visibleMaidIds.has(maid.id));
  5208 |         const lanes=visibleMaids.map(maid=>{const ordered=orderedAssignmentsForMaid(maid.id),total=ordered.reduce((sum,item)=>sum+assignmentTargetRate(item),0);return `<section class="maid-order-lane" id="maid-order-${maid.id}" aria-labelledby="maid-order-title-${maid.id}"><div class="maid-order-lane-head"><div class="maid-order-lane-copy"><h4 id="maid-order-title-${maid.id}">${esc(maid.name)} 배정 객실·청소 순서</h4><p>각 객실의 담당을 바꾸거나 위·아래 버튼으로 1–N 순서를 조정할 수 있습니다.</p></div><div class="maid-order-lane-total" data-maid-id="${maid.id}" data-maid-total="${total}"><span>총 청소요금 · ${ordered.length}건</span><strong>${money(total)}</strong></div></div><div class="maid-order-list">${ordered.length?ordered.map((item,index)=>maidOrderItemMarkup(item,ordered,index)).join(''):'<div class="maid-order-empty">배정된 객실이 없습니다.</div>'}</div></section>`;}).join('');
  5209 |         const unassignedList=unassigned.length?unassigned.map(item=>{const context=assignmentContext(item);return `<span class="maid-order-unassigned-chip">${item.room}호 · ${esc(context.type.name)} · ${esc(elevatorLabel(context.room))} · ${money(context.type.rate)}</span>`;}).join(''):'<span class="maid-order-unassigned-chip">미배정 객실 없음</span>';
  5210 |         return `<section class="card maid-order-panel" aria-labelledby="maid-order-board-title"><div class="assignment-panel-head"><div><span class="assignment-step-label">4단계 · 세부 수정</span><h3 id="maid-order-board-title">메이드별 청소 순서 수정</h3><p>얼리 체크인·레이트 체크아웃의 조정된 예정 시각을 먼저 확인하고, 객실 담당과 1–N 순서를 직접 수정합니다.</p></div>${statusBadge(`${unassigned.length}건 미배정`,unassigned.length?'red':'green')}</div><div class="maid-order-board ${lanes?'':'is-empty'}">${lanes||'<div class="maid-order-empty">아직 배정된 객실이 없습니다. 랜덤 배정하거나 위 객실 표에서 담당을 선택하세요.</div>'}</div><div class="maid-order-unassigned"><div><h4>아직 순서가 없는 객실</h4><p>미배정 상태로 남겨 두고 담당이 정해진 객실만 먼저 통보할 수 있습니다.</p></div><div class="maid-order-unassigned-list">${unassignedList}</div></div><div class="assignment-foot"><p>랜덤 배정은 저장 전 초안입니다. 담당과 연속 순서가 정해진 객실만 저장·통보합니다.</p>${button(`배정된 변경 ${assignmentTargets().filter(item=>assignmentHasNetChange(item)&&assignmentFor(item).maidId).length}건 저장·통보`,'save-assignments','primary',assignmentCanSave()?'':'disabled')}</div></section>`;
  5211 |       }
  5212 |       function assignmentCountsForDate(assignmentDate=state.assignmentDate) {
  5213 |         const targets=assignmentTargetsForDate(assignmentDate),rows=targets.map(item=>state.assignments?.[item.id]||{maidId:'',status:'unassigned'}),assigned=rows.filter(item=>item.maidId).length,notified=targets.filter(item=>{const record=state.assignments?.[item.id];return !!(record?.status==='notified'&&record.maidId||record?.previousMaidId);}).length;
  5214 |         return {total:rows.length,assigned,notified,unassigned:rows.length-assigned,carryover:targets.filter(item=>item.carryReason).length,automatic:targets.filter(item=>item.source!=='manual').length,manual:targets.filter(item=>item.source==='manual').length,checkout:targets.filter(item=>item.source==='checkout').length,stayover:targets.filter(item=>item.source==='stayover').length,submitted:MAIDS.filter(maid=>availabilityForWorkDate(maid.id,assignmentDate)!=='missing').length};
  5215 |       }
  5216 |       function assignmentCounts() { return assignmentCountsForDate(state.assignmentDate); }
  5217 |       function assignmentCanSave() {
  5218 |         const targets=assignmentTargets(),changedTargets=targets.filter(item=>assignmentHasNetChange(item)&&!!assignmentFor(item).maidId),affectedMaidIds=[...new Set(changedTargets.flatMap(item=>[assignmentFor(item).maidId,assignmentFor(item).previousMaidId]).filter(Boolean))],allAssignedToAvailable=changedTargets.every(item=>availabilityForWorkDate(assignmentFor(item).maidId,targetEffectiveDate(item))==='available');
  5219 |         const continuousOrders=affectedMaidIds.every(maidId=>orderedAssignmentsForMaid(maidId).every((item,index)=>assignmentFor(item).order===index+1));
  5220 |         const allAssignedToActiveMaids=changedTargets.every(item=>maidCanReceiveNewAssignment(assignmentFor(item).maidId));
  5221 |         const noHeldRoomChanges=changedTargets.every(item=>!roomIsOnHold(item.room)&&item.carryReason!=='access-review');
  5222 |         const noStartedRoomChanges=changedTargets.every(cleaningTargetCanAdjust);
  5223 |         const randomFresh=!state.randomAssignmentSnapshot||(state.randomAssignmentSnapshot.contextSignature===randomAssignmentContextSignature()&&randomAssignmentStateMatches());
  5224 |         return changedTargets.length>0&&noHeldRoomChanges&&noStartedRoomChanges&&allAssignedToAvailable&&allAssignedToActiveMaids&&continuousOrders&&randomFresh&&!isLocked();
  5225 |       }
  5226 |       function renderAvailabilityMatrix() {
  5227 |         const start=weekStartIso(state.assignmentDate),days=['월','화','수','목','금','토','일'].map((name,index)=>{const iso=addIsoDays(start,index);return {name,iso,day:Number(iso.slice(8))};});
  5228 |         return `<div class="availability-matrix-wrap"><table class="availability-matrix"><thead><tr><th scope="col">메이드</th>${days.map(day=>`<th scope="col">${day.name} ${day.day}</th>`).join('')}</tr></thead><tbody>${MAIDS.map(maid=>`<tr><th scope="row">${esc(maid.name)}</th>${days.map((day,index)=>`<td>${availabilityCell(maid.id,index,day.iso)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="assignment-foot"><p>✓ 가능 · × 불가 · — 미제출. ${days[assignmentDayIndex()].name}요일 배정 후보는 해당 날짜 가능 제출자만 표시합니다.</p></div>`;
  5229 |       }
  5230 |       function assignmentOptions(item) {
  5231 |         const selected=assignmentFor(item).maidId||'',effectiveDate=targetEffectiveDate(item);
  5232 |         const eligible=MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,effectiveDate)==='available');
  5233 |         const legacy=selected&&!eligible.some(maid=>maid.id===selected)?`<option value="${esc(selected)}" selected disabled>${esc(maidName(selected))} (기존 담당 · 신규 배정 불가)</option>`:'';
  5234 |         return `<option value="">담당 선택</option>${legacy}${eligible.map(maid=>`<option value="${maid.id}" ${selected===maid.id?'selected':''}>${esc(maid.name)} (근무 가능)</option>`).join('')}${eligible.length?'':'<option value="" disabled>근무 가능 메이드 없음</option>'}`;
  5235 |       }
  5236 |       function assignmentContext(item) {
  5237 |         const liveRoom=ROOMS.find(entry=>entry.no===item.room),snapshot=assignmentPricingSnapshot(item),room=liveRoom?{...liveRoom,elevator:snapshot.elevator}:liveRoom,type={...(ROOM_TYPES[snapshot.typeId]||ROOM_TYPES.standard),rate:snapshot.rate,minutes:snapshot.minutes};
  5238 |         const roomStatus=roomReservationStatus(room),status=item.source==='stayover'?reservationTimeStatus(null,null):reservationTimeStatus(item.checkin||roomStatus.checkin,item.checkout||roomStatus.checkout);
  5239 |         return {room,type,...status};
  5240 |       }
  5241 |       function eligibleAssignmentMaids() {
  5242 |         return MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,state.assignmentDate)==='available');
  5243 |       }
  5244 |       function assignmentPricingSnapshot(item) {
```

## click delegate: `document.addEventListener('click'`

matches: 6

### occurrence 1 · line 3739

```html
  3723 |         if(action==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  3724 |         if(action==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  3725 |         if(action==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  3726 |         const button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));button.remove();
  3727 |       }
  3728 |       function closeNotificationModalAndNavigate(notificationEvent){
  3729 |         const navigate=()=>requestAnimationFrame(()=>dispatchNotificationTarget(notificationEvent)),entry=history.state;
  3730 |         if(isWireframeHistory(entry)&&entry.layer==='modal'){
  3731 |           let completed=false;
  3732 |           const onPop=()=>{if(completed)return;completed=true;setTimeout(navigate,0);};
  3733 |           window.addEventListener('popstate',onPop,{once:true});
  3734 |           closeModal();
  3735 |           return;
  3736 |         }
  3737 |         rawCloseModal();navigate();
  3738 |       }
  3739 |       document.addEventListener('click',browserEvent=>{
  3740 |         const el=browserEvent.target.closest?.('[data-action]'),action=el?.dataset.action;
  3741 |         if(!['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].includes(action))return;
  3742 |         browserEvent.preventDefault();browserEvent.stopImmediatePropagation();
  3743 |         if(action==='notification-filter'){
  3744 |           const filter=el.dataset.filter;if(!['all','unread','action'].includes(filter))return;
  3745 |           state.notificationFilter=filter;rawCloseModal();openNotificationCenter(el);return;
  3746 |         }
  3747 |         if(action==='notification-mark-all-read'){
  3748 |           markAllNotificationsRead();render();rawCloseModal();openNotificationCenter(el);toast('현재 계정의 알림을 모두 읽음 처리했습니다.');return;
  3749 |         }
  3750 |         if(action==='notification-toggle-push'){
  3751 |           const enabled=!notificationPushEnabled();setNotificationPushEnabled(enabled);appendEvent('기기 푸시 설정 변경',enabled?'현재 계정 푸시 켜짐 · 앱 내 알림은 항상 유지':'현재 계정 푸시 꺼짐 · 앱 내 알림은 항상 유지',{notification:false});render();rawCloseModal();openNotificationCenter(el);toast(enabled?'행동이 필요한 업데이트의 푸시를 켰습니다.':'푸시를 껐습니다. 앱 내 알림은 계속 남습니다.');return;
  3752 |         }
  3753 |         const ids=String(el.dataset.eventIds||el.dataset.eventId||'').split(',').filter(Boolean),eventId=el.dataset.eventId||ids[0],notificationEvent=(state.events||[]).find(item=>item.id===eventId);
  3754 |         markNotificationRead(ids);render();if(notificationEvent)closeNotificationModalAndNavigate(notificationEvent);
  3755 |       },true);
  3756 | 
  3757 |       function openPublishConfirm() {
  3758 |         const selected=state.drafts.filter(d=>state.selectedDrafts.includes(d.id));
  3759 |         showModal({title:'내일 배정으로 이동할까요?',subtitle:'청소 담당은 공개 목록 없이 관리자가 직접 지정합니다.',body:`<div class="rail-list">${selected.map(d=>`<div class="rail-row"><strong>${d.room}호 · ${d.kind}</strong><span>${money(ROOM_TYPES[ROOMS.find(r=>r.no===d.room)?.type||'standard'].rate)} · 8월 시트</span></div>`).join('')}</div>`,confirmLabel:'내일 배정으로 이동',confirmAction:'confirm-publish',confirmVariant:'success'});
  3760 |       }
  3761 | 
  3762 |       function openConflictModal() {
  3763 |         showModal({title:'레이트 체크아웃·청소 출입 충돌 해결',subtitle:'현재 예약·작업 버전을 다시 확인한 뒤 필요한 항목을 모두 완료합니다.',large:true,body:`<div class="info-grid"><div class="info-item"><span>변경</span><strong>체크아웃 11:00 → 13:00</strong></div><div class="info-item"><span>영향</span><strong>PIN 조회 · 청소 시작됨</strong></div></div><div class="choice-list" style="margin-top:14px"><label class="choice"><input type="checkbox" data-control="conflict-step" value="coordinate" ${state.conflictSteps.coordinate?'checked':''}><span><strong>현장 조율 완료</strong><span>투숙객·메이드와 출입 상황 확인</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step" value="replan" ${state.conflictSteps.replan?'checked':''}><span><strong>작업 중단·재계획</strong><span>기존 수행 회차를 이력으로 보존하고 새 일정 확정</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step" value="pin" ${state.conflictSteps.pin?'checked':''}><span><strong>실제 도어락 PIN 교체</strong><span>새 PIN 원문은 이 화면이나 영속 저장소에 보존하지 않음</span></span></label></div>`,confirmLabel:'충돌 종결',confirmAction:'confirm-conflict',confirmVariant:'danger'});
  3764 |       }
  3765 | 
  3766 |       function openCancelReview() {
  3767 |         const requestedEntry=Object.entries(state.cancelRequests||{}).find(([,request])=>request.status==='requested');
  3768 |         const no=requestedEntry?.[0]||state.cancelRequestRoom||'332', request=requestedEntry?.[1], room=ROOMS.find(item=>item.no===no), maid=request?.maid||room?.assignee||'김민지1', reason=request?.reason||'건강상 사유 · 데모';
  3769 |         state.cancelRequestRoom=no;
  3770 |         showModal({title:`${maid} 담당 취소 요청`,subtitle:'관리자 결정 전에는 담당이 유지되며 자동 취소·자동 재배정하지 않습니다.',body:`<div class="notice notice-warning">요청 사유: ${esc(reason)} · ${no}호 ${cleaningLabel(request?.job||state.jobs[no])}</div><div class="choice-list"><label class="choice"><input type="radio" name="cancel-decision" value="deny" checked><span><strong>거절 · 담당 유지</strong><span>메이드에게 관리자 사유 알림</span></span></label><label class="choice"><input type="radio" name="cancel-decision" value="republish"><span><strong>승인 · 관리자 재배정 대기</strong><span>수행 회차를 중단으로 보존하고 관리자 미배정 상태로 전환</span></span></label><label class="choice"><input type="radio" name="cancel-decision" value="direct"><span><strong>승인 · 직접 배정</strong><span>새 책임 메이드 담당 구간 생성</span></span></label><label class="choice"><input type="radio" name="cancel-decision" value="hold"><span><strong>승인 · 보류</strong><span>관리자 조치 대기 상태 유지</span></span></label></div>`,confirmLabel:'결정 저장',confirmAction:'confirm-cancel'});
  3771 |       }
  3772 | 
  3773 |       function openStayover(no='142',trigger=document.activeElement) {
```

### occurrence 2 · line 4826

```html
  4810 |         if((session.pointerType==='touch'||session.pointerType==='pen')&&Math.abs(dy)>14&&Math.abs(dy)>Math.abs(dx)){cancelQuickPointerSession();return;}
  4811 |         if(session.pointerType!=='mouse')event.preventDefault();
  4812 |         const target=document.elementFromPoint(event.clientX,event.clientY)?.closest?.('.quick-date-cell[data-room][data-date]');
  4813 |         if(target&&target.dataset.room===session.room){session.endDate=target.dataset.date;session.invalidReason='';updateQuickSelectionPreview(session.room,session.startDate,session.endDate);}
  4814 |         else {const message=target?'다른 객실 행으로 이동해 예약 선택을 취소했습니다.':'예약표 밖으로 이동해 예약 선택을 취소했습니다.';cancelQuickPointerSession();document.getElementById('assertive-live').textContent=message;toast(message,'error');return;}
  4815 |         const scroller=document.getElementById('quick-grid-scroller');if(scroller){const rect=scroller.getBoundingClientRect(),edge=38;if(event.clientX>rect.right-edge)scroller.scrollLeft+=18;else if(event.clientX<rect.left+edge)scroller.scrollLeft=Math.max(0,scroller.scrollLeft-18);state.quickGridScrollLeft=scroller.scrollLeft;}
  4816 |       },{passive:false});
  4817 |       document.addEventListener('pointerup',event=>{
  4818 |         const session=quickPointerSession;if(!session||session.pointerId!==event.pointerId)return;
  4819 |         clearTimeout(quickTouchArmTimer);quickTouchArmTimer=null;
  4820 |         if(session.scrolling){quickSuppressClickUntil=Date.now()+500;cancelQuickPointerSession();return;}
  4821 |         if(!session.armed){cancelQuickPointerSession();return;}
  4822 |         if(session.invalidReason){const message=session.invalidReason;cancelQuickPointerSession();toast(message,'error');return;}
  4823 |         createQuickReservationFromRange(session.room,session.startDate,session.endDate);
  4824 |       });
  4825 |       document.addEventListener('pointercancel',event=>{if(quickPointerSession?.pointerId===event.pointerId)cancelQuickPointerSession();});
  4826 |       document.addEventListener('click',event=>{
  4827 |         const cell=event.target.closest?.('.quick-date-cell[data-room][data-date]');if(!cell)return;
  4828 |         if(Date.now()<quickSuppressClickUntil){event.preventDefault();event.stopImmediatePropagation();return;}
  4829 |         if(event.detail===0&&cell.dataset.bookable==='true'&&state.role==='admin'&&state.adminView==='quickReservation'&&!state.detail&&!document.querySelector('.modal')){event.preventDefault();event.stopImmediatePropagation();createQuickReservationFromRange(cell.dataset.room,cell.dataset.date,cell.dataset.date);}
  4830 |       },true);
  4831 |       document.addEventListener('contextmenu',event=>{if(event.target.closest?.('.quick-date-cell'))event.preventDefault();});
  4832 |       document.addEventListener('scroll',event=>{const target=event.target;if(!['quick-grid-scroller','quick-grid-mobile-header'].includes(target?.id))return;syncQuickGridHorizontalScroll(target);if(target.id==='quick-grid-scroller')state.quickGridScrollTop=quickGridUsesInternalVerticalScroll()?target.scrollTop:0;},true);
  4833 |       document.addEventListener('focusin',event=>{
  4834 |         const dateCell=event.target.closest?.('.quick-date-cell[data-room][data-date]');if(dateCell&&state.role==='admin'&&state.adminView==='quickReservation'&&!state.detail)ensureQuickDateCellVisible(dateCell);
  4835 |         const roomLink=event.target.closest?.('.quick-room-link[data-id]');if(!roomLink||state.role!=='admin'||state.adminView!=='quickReservation'||state.detail)return;
  4836 |         document.querySelectorAll('.quick-room-link[data-id]').forEach(link=>{link.tabIndex=link===roomLink?0:-1;});
  4837 |       });
  4838 |       document.addEventListener('keydown',event=>{
  4839 |         const roomLink=event.target.closest?.('.quick-room-link[data-id]');if(!roomLink||document.querySelector('.modal')||state.role!=='admin'||state.adminView!=='quickReservation')return;
  4840 |         if(!['ArrowUp','ArrowDown','Home','End'].includes(event.key))return;
  4841 |         event.preventDefault();const links=[...document.querySelectorAll('.quick-room-link[data-id]')],index=links.indexOf(roomLink),nextIndex=event.key==='Home'?0:event.key==='End'?links.length-1:Math.max(0,Math.min(links.length-1,index+(event.key==='ArrowUp'?-1:1))),target=links[nextIndex];
  4842 |         if(!target)return;roomLink.tabIndex=-1;target.tabIndex=0;target.focus({preventScroll:false});
  4843 |       });
  4844 |       document.addEventListener('keydown',event=>{
  4845 |         const cell=event.target.closest?.('.quick-date-cell[data-room][data-date]');if(!cell||document.querySelector('.modal')||state.role!=='admin'||state.adminView!=='quickReservation')return;
  4846 |         if(event.key==='Escape'){event.preventDefault();quickKeyboardSelection=null;clearQuickSelectionPreview();document.getElementById('assertive-live').textContent='예약 날짜 선택을 취소했습니다.';return;}
  4847 |         const arrows=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'];
  4848 |         if(arrows.includes(event.key)){
  4849 |           event.preventDefault();const rows=[...document.querySelectorAll('.quick-grid-data-row')],row=cell.closest('.quick-grid-data-row'),rowIndex=rows.indexOf(row),rowCells=[...row.querySelectorAll('.quick-date-cell')],dayIndex=rowCells.indexOf(cell),nextRowIndex=Math.max(0,Math.min(rows.length-1,rowIndex+(event.key==='ArrowUp'?-1:event.key==='ArrowDown'?1:0))),nextDayIndex=Math.max(0,Math.min(rowCells.length-1,dayIndex+(event.key==='ArrowLeft'?-1:event.key==='ArrowRight'?1:0))),target=[...rows[nextRowIndex].querySelectorAll('.quick-date-cell')][nextDayIndex];
  4850 |           if(!target)return;cell.tabIndex=-1;target.tabIndex=0;target.focus({preventScroll:false});
  4851 |           if(event.shiftKey&&['ArrowLeft','ArrowRight'].includes(event.key)&&(cell.dataset.bookable==='true'||quickKeyboardSelection?.room===cell.dataset.room)){const anchor=quickKeyboardSelection?.room===cell.dataset.room?quickKeyboardSelection.startDate:cell.dataset.date;quickKeyboardSelection={room:cell.dataset.room,startDate:anchor,endDate:target.dataset.date};const conflict=updateQuickSelectionPreview(quickKeyboardSelection.room,quickKeyboardSelection.startDate,quickKeyboardSelection.endDate);document.getElementById('assertive-live').textContent=conflict?`선택 범위 예약 불가. ${conflict.reason}`:`${quickDateLabel(quickKeyboardSelection.startDate)}부터 ${quickDateLabel(quickKeyboardSelection.endDate)}까지 선택.`;}
  4852 |           else {const hadSelection=!!quickKeyboardSelection;quickKeyboardSelection=null;clearQuickSelectionPreview();if(hadSelection)document.getElementById('assertive-live').textContent='예약 날짜 선택을 취소했습니다.';}
  4853 |           return;
  4854 |         }
  4855 |         if(['Enter',' '].includes(event.key)&&quickKeyboardSelection?.room===cell.dataset.room){event.preventDefault();event.stopPropagation();quickSuppressClickUntil=Date.now()+500;createQuickReservationFromRange(quickKeyboardSelection.room,quickKeyboardSelection.startDate,quickKeyboardSelection.endDate);return;}
  4856 |         if(['Enter',' '].includes(event.key)&&!cell.dataset.action){event.preventDefault();if(cell.dataset.bookable!=='true'){toast(cell.title||'이 날짜는 예약할 수 없습니다.','error');return;}quickSuppressClickUntil=Date.now()+500;createQuickReservationFromRange(cell.dataset.room,cell.dataset.date,cell.dataset.date);}
  4857 |       });
  4858 | 
  4859 |       function dashboardCleaningCostSummary() {
  4860 |         const weekStart=CURRENT_PAYMENT_WEEK_START,week=adminPayWeeks().find(item=>item.start===weekStart),tasks=week?Object.values(week.tasksByMaid||{}).flat():[],included=tasks.filter(task=>['confirmed','pending'].includes(task.stage)),todayLabel=payrollDateLabel(DEMO_TODAY),todayTasks=included.filter(task=>(task.earnedOn||payrollTaskDateIso(task.date,weekStart))===DEMO_TODAY),summarize=items=>{const totals=payrollTaskTotals(items);return {...totals,expected:totals.confirmed+totals.pending,count:items.length};};
```

### occurrence 3 · line 6746

```html
  6730 |       }
  6731 | 
  6732 |       function openConflictResolutionV2(trigger=document.activeElement) {
  6733 |         const record=state.conflictRecord;
  6734 |         showModal({title:'332호 영향 확인·충돌 해결',subtitle:'변경된 체크아웃과 현재 청소·PIN 조회 영향을 확인하세요.',large:true,trigger,body:`<div class="notice notice-danger"><div><strong>현재 상태 확인</strong><br>${record.autoCheckoutAt} 자동 체크아웃 기록은 남기고 ${record.afterCheckout}까지 투숙 중으로 표시합니다.</div></div><div class="info-grid"><div class="info-item"><span>체크아웃 전 → 후</span><strong>${record.beforeCheckout} → ${record.afterCheckout}</strong></div><div class="info-item"><span>청소 담당·단계</span><strong>${record.assignee} · ${record.stage}</strong></div><div class="info-item"><span>PIN 조회</span><strong>${record.pinViewedAt}</strong></div><div class="info-item"><span>PIN 조회 처리</span><strong>기존 조회 종료 후 다시 확인</strong></div></div><div class="choice-list" style="margin-top:14px"><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="coordinate" ${state.conflictSteps.coordinate?'checked':''} ${isLocked()?'disabled':''}><span><strong>현장 조율 완료</strong><span>투숙객·${record.assignee}에게 변경된 체크아웃과 출입 중단을 확인</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="replan" ${state.conflictSteps.replan?'checked':''} ${isLocked()?'disabled':''}><span><strong>청소 일정 변경 완료</strong><span>진행 중 청소를 중단 처리하고 ${record.afterCheckout} 새 청소 생성</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="pin" ${state.conflictSteps.pin?'checked':''} ${isLocked()?'disabled':''}><span><strong>도어락 PIN 확인 완료</strong><span>기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.</span></span></label></div>`,confirmLabel:'조치 완료',confirmAction:'confirm-conflict-v2',confirmVariant:'danger'});
  6735 |         const confirm=document.querySelector('[data-action="confirm-conflict-v2"]');
  6736 |         if(confirm)confirm.disabled=isLocked()||!Object.values(state.conflictSteps).every(Boolean);
  6737 |       }
  6738 | 
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
```

### occurrence 4 · line 6759

```html
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
  6785 |         if(a==='open-reservation-week-calendar'){
  6786 |           if(state.role!=='admin')return;state.reservationWeekRoom=el.dataset.room||state.reservationWeekRoom||'211';state.calendarMonth=weekStartIso(state.reservationWeekStart||state.selectedDate).slice(0,7);openCalendar(el,'reservation-week',true);return;
  6787 |         }
  6788 |         if(a==='reservation-add'){
  6789 |           const room=ROOMS.find(item=>item.no===String(el.dataset.room||'')),newDate=el.dataset.date||suggestedReservationStartDate(room?.no||'');
  6790 |           if(state.role!=='admin'||!adminCanMutate()||!room){toast('관리자 최신 상태에서만 다음 예약을 등록할 수 있습니다.','error');return;}
  6791 |           const block=reservationHardBlockReason(room);if(block){toast(`${room.no}호는 ${block} 상태라 다음 예약을 등록할 수 없습니다.`,'error');return;}
  6792 |           if(room.occupancy==='occupied'&&!occupiedReservationEnd(room)){toast('현재 투숙의 체크아웃을 먼저 입력해 주세요.','error');return;}
  6793 |           if(occupiedStayNeedsCheckoutUpdate(room)){toast('예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.','error');return;}
```

### occurrence 5 · line 7637

```html
  7621 |         e.preventDefault();e.stopImmediatePropagation();paymentSwitch.click();
  7622 |       });
  7623 |       document.addEventListener('keydown',e=>{
  7624 |         const ruleHelp=e.target.closest?.('.assignment-rule-help')||document.querySelector('.assignment-rule-help:hover');
  7625 |         if(!ruleHelp||e.key!=='Escape')return;
  7626 |         e.preventDefault();e.stopImmediatePropagation();ruleHelp.classList.add('is-dismissed');
  7627 |       });
  7628 |       document.addEventListener('pointerover',e=>{
  7629 |         const ruleHelp=e.target.closest?.('.assignment-rule-help');
  7630 |         if(ruleHelp&&!ruleHelp.contains(e.relatedTarget))ruleHelp.classList.remove('is-dismissed');
  7631 |       });
  7632 |       document.addEventListener('pointerout',e=>{
  7633 |         const ruleHelp=e.target.closest?.('.assignment-rule-help');
  7634 |         if(ruleHelp&&!ruleHelp.contains(e.relatedTarget))ruleHelp.classList.remove('is-dismissed');
  7635 |       });
  7636 |       document.addEventListener('focusin',e=>e.target.closest?.('.assignment-rule-help')?.classList.remove('is-dismissed'));
  7637 |       document.addEventListener('click',e=>e.target.closest?.('.assignment-rule-help-button')?.parentElement.classList.remove('is-dismissed'));
  7638 |       document.addEventListener('visibilitychange',()=>{if(document.hidden&&state.pinVisibleRoom){maskPin();render();}});
  7639 |       window.addEventListener('pagehide',maskPin);
  7640 |       document.addEventListener('keydown',e=>{
  7641 |         const calendar=document.querySelector('.calendar-dialog');if(!calendar)return;
  7642 |         if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();dismissModal();return;}
  7643 |         if(e.key==='Tab'){
  7644 |           const focusable=[...calendar.querySelectorAll('button:not([disabled])')];if(!focusable.length)return;
  7645 |           const first=focusable[0],last=focusable[focusable.length-1];
  7646 |           if(e.shiftKey&&document.activeElement===first){e.preventDefault();e.stopImmediatePropagation();last.focus();}
  7647 |           else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();e.stopImmediatePropagation();first.focus();}
  7648 |         }
  7649 |       });
  7650 | 
  7651 |       document.addEventListener('click', e => {
  7652 |         const el=e.target.closest('[data-action]'); if(!el) return; const a=el.dataset.action,id=el.dataset.id;
  7653 |         if (a==='backdrop-close' && e.target!==el) return;
  7654 |         if (a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();}
  7655 |         else if(a==='reset'){state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();toast('시나리오를 초기 상태로 재설정했습니다.');}
  7656 |         else if(a==='switch-role'){state.role=state.role==='admin'?'maid':'admin';state.detail=null;render();toast(`${state.role==='admin'?'관리자':'메이드'} 데모로 전환했습니다.`);}
  7657 |         else if(a==='nav'){state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;render();requestAnimationFrame(()=>document.getElementById('main-content')?.focus());}
  7658 |         else if(a==='alerts')openAlerts();
  7659 |         else if(a==='close-modal'||a==='backdrop-close')dismissModal();
  7660 |         else if(a==='back')backFromDetail();
  7661 |         else if(a==='room-detail')openDetail('room',id||'350',el);
  7662 |         else if(a==='cleaning-detail')openDetail('cleaning',id||'639',el);
  7663 |         else if(a==='maid-detail')openDetail('maid',id||'m1',el);
  7664 |         else if(a==='complaint-detail')openDetail('complaint','c1',el);
  7665 |         else if(a==='pay-detail')openDetail('pay','week',el);
  7666 |         else if(a==='new-reservation')openReservation();
  7667 |         else if(a==='save-reservation'){state.reservationSaved=true;if(!state.drafts.some(d=>d.room==='211'))state.drafts.push({id:'d211',room:'211',kind:'퇴실 청소',created:state.time});state.jobs['211']='draft';appendEvent('211호 예약 저장','퇴실 청소 준비');closeModal();render();toast('211호 예약을 저장했습니다.');}
  7668 |         else if(a==='publish-selected'){if(!state.selectedDrafts.length)return;openPublishConfirm();}
  7669 |         else if(a==='confirm-publish'){closeModal();state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);render();toast('내일 배정에서 담당 메이드를 직접 지정해 주세요.');}
  7670 |         else if(a==='claim-job'||a==='confirm-claim'){closeModal();state.maidView='schedule';render();toast('메이드는 객실을 선택할 권한이 없습니다. 관리자 배정 통보를 확인해 주세요.','error');}
  7671 |         else if(a==='go-my'){state.maidView='my';render();}
```

### occurrence 6 · line 7651

```html
  7635 |       });
  7636 |       document.addEventListener('focusin',e=>e.target.closest?.('.assignment-rule-help')?.classList.remove('is-dismissed'));
  7637 |       document.addEventListener('click',e=>e.target.closest?.('.assignment-rule-help-button')?.parentElement.classList.remove('is-dismissed'));
  7638 |       document.addEventListener('visibilitychange',()=>{if(document.hidden&&state.pinVisibleRoom){maskPin();render();}});
  7639 |       window.addEventListener('pagehide',maskPin);
  7640 |       document.addEventListener('keydown',e=>{
  7641 |         const calendar=document.querySelector('.calendar-dialog');if(!calendar)return;
  7642 |         if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();dismissModal();return;}
  7643 |         if(e.key==='Tab'){
  7644 |           const focusable=[...calendar.querySelectorAll('button:not([disabled])')];if(!focusable.length)return;
  7645 |           const first=focusable[0],last=focusable[focusable.length-1];
  7646 |           if(e.shiftKey&&document.activeElement===first){e.preventDefault();e.stopImmediatePropagation();last.focus();}
  7647 |           else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();e.stopImmediatePropagation();first.focus();}
  7648 |         }
  7649 |       });
  7650 | 
  7651 |       document.addEventListener('click', e => {
  7652 |         const el=e.target.closest('[data-action]'); if(!el) return; const a=el.dataset.action,id=el.dataset.id;
  7653 |         if (a==='backdrop-close' && e.target!==el) return;
  7654 |         if (a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();}
  7655 |         else if(a==='reset'){state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();toast('시나리오를 초기 상태로 재설정했습니다.');}
  7656 |         else if(a==='switch-role'){state.role=state.role==='admin'?'maid':'admin';state.detail=null;render();toast(`${state.role==='admin'?'관리자':'메이드'} 데모로 전환했습니다.`);}
  7657 |         else if(a==='nav'){state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;render();requestAnimationFrame(()=>document.getElementById('main-content')?.focus());}
  7658 |         else if(a==='alerts')openAlerts();
  7659 |         else if(a==='close-modal'||a==='backdrop-close')dismissModal();
  7660 |         else if(a==='back')backFromDetail();
  7661 |         else if(a==='room-detail')openDetail('room',id||'350',el);
  7662 |         else if(a==='cleaning-detail')openDetail('cleaning',id||'639',el);
  7663 |         else if(a==='maid-detail')openDetail('maid',id||'m1',el);
  7664 |         else if(a==='complaint-detail')openDetail('complaint','c1',el);
  7665 |         else if(a==='pay-detail')openDetail('pay','week',el);
  7666 |         else if(a==='new-reservation')openReservation();
  7667 |         else if(a==='save-reservation'){state.reservationSaved=true;if(!state.drafts.some(d=>d.room==='211'))state.drafts.push({id:'d211',room:'211',kind:'퇴실 청소',created:state.time});state.jobs['211']='draft';appendEvent('211호 예약 저장','퇴실 청소 준비');closeModal();render();toast('211호 예약을 저장했습니다.');}
  7668 |         else if(a==='publish-selected'){if(!state.selectedDrafts.length)return;openPublishConfirm();}
  7669 |         else if(a==='confirm-publish'){closeModal();state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);render();toast('내일 배정에서 담당 메이드를 직접 지정해 주세요.');}
  7670 |         else if(a==='claim-job'||a==='confirm-claim'){closeModal();state.maidView='schedule';render();toast('메이드는 객실을 선택할 권한이 없습니다. 관리자 배정 통보를 확인해 주세요.','error');}
  7671 |         else if(a==='go-my'){state.maidView='my';render();}
  7672 |         else if(a==='show-pin'){state.pinVisibleUntil=Date.now()+30000;appendEvent(`${state.detail?.id||'350'}호 PIN 조회`,'원문 없이 조회 사실만 감사 기록');render();clearTimeout(pinTimer);pinTimer=setTimeout(()=>{state.pinVisibleUntil=0;render();toast('30초가 지나 객실 PIN을 다시 가렸습니다.');},30000);}
  7673 |         else if(a==='hide-pin'){state.pinVisibleUntil=0;clearTimeout(pinTimer);render();}
  7674 |         else if(a==='start-cleaning')showModal({title:`${id||state.detail?.id||'350'}호 청소를 시작할까요?`,subtitle:'다른 청소 중 작업이 없는지 온라인으로 다시 검증하는 데모입니다.',body:`<div class="notice notice-warning">시작하면 이 작업이 유일한 청소 중 슬롯을 사용합니다.</div>`,confirmLabel:'청소 시작',confirmAction:'confirm-start'}),document.querySelector('#modal-root [data-action="confirm-start"]')?.setAttribute('data-id',id||state.detail?.id||'350');
  7675 |         else if(a==='confirm-start'){const room=id||'350';state.jobs[room]='cleaning';state.activeCleaning=room;state.detail={type:'cleaning',id:room};appendEvent(`${room}호 청소 시작`,'활성 수행 회차 1건');closeModal();render();toast('청소 중 상태와 타임라인이 갱신됐습니다.');}
  7676 |         else if(a==='retry-photo'){const u=state.uploads.find(x=>x.id===id);if(u){u.status='uploading';render();setTimeout(()=>{u.status='done';render();toast('사진 재전송에 성공했습니다.');},450);}}
  7677 |         else if(a==='field-complete'){const room=id||state.detail?.id||'528';state.jobs[room]='upload';state.activeCleaning=null;appendEvent(`${room}호 현장 완료`,'물리적 진행 슬롯 해제 · 미디어 검증 대기');render();toast('현장 완료·업로드 대기로 전환했습니다.');}
  7678 |         else if(a==='submit-cleaning'){const room=id||state.detail?.id||'528';if(state.uploads.some(u=>u.status!=='done')){state.uploads.filter(u=>u.status==='failed').forEach(u=>u.status='done');render();toast('미전송 사진을 재시도했습니다.');}else{state.jobs[room]='inspection';appendEvent(`${room}호 청소 전체 제출`,'필수 파일 검증 완료 · 검수 대기');render();toast('전체 제출 후 검수 대기로 전환했습니다.');}}
  7679 |         else if(a==='approve-inspection')openInspectionDecision('approve');
  7680 |         else if(a==='reject-inspection')openInspectionDecision('reject');
  7681 |         else if(a==='confirm-approve'){state.inspection.status='approved';state.jobs['639']='approved';state.earningsAddedByRoom['639']=true;appendEvent('639호 전체 제출 승인','수익 1건 · 객실 상태 재계산');closeModal();render();toast('전체 승인과 수익 귀속을 반영했습니다.');}
  7682 |         else if(a==='confirm-reject'){
  7683 |           if(!adminCanMutate()){closeModal();render();toast('관리자 최신 상태에서만 전체 반려를 저장할 수 있습니다.','error');return;}
  7684 |           const no='639',submission=currentSubmission(no),room=ROOMS.find(item=>item.no===no),performer=submission?.performerName||room?.assignee||'이서연',performerId=submission?.performerId||performerIdentity(no,performer).performerId;
  7685 |           if(room)room.assignee=performer;state.inspection.status='rejected';state.inspection.reclean='existing';state.inspections[no]='rejected';state.jobs[no]='reclean';beginCleaningAttempt(no,{performerId,performerName:performer,reason:'전체 반려 뒤 처음 청소한 본인 무급 재청소',baseRateSnapshot:0,kind:'재청소',reservationIdSnapshot:submission?.reservationIdSnapshot,guestCountSnapshot:submission?.guestCountSnapshot});appendEvent('639호 전체 제출 반려',`${performer} 본인 무급 재청소 자동 귀속 · 타 메이드 이관 없음`);closeModal();render();toast(`${performer} 본인에게 무급 재청소를 자동 배정했습니다.`);
```

## data issue: `dataIssue`

matches: 5

### occurrence 1 · line 1831

```html
  1815 |       ];
  1816 |       const DEMO_ROOM_OVERRIDES = {
  1817 |         '117':{checkout:'13:00',checkin:'16:00',assignee:'김민지1',occupancy:'occupied',cleaning:'scheduled',actualCheckinAt:'2026-08-14T16:00',plannedCheckoutAt:'2026-08-15T13:00',currentStayReservationId:'reservation-demo-117'},
  1818 |         '350':{checkout:'완료',checkin:'15:00',assignee:'이서연',occupancy:'vacant',cleaning:'inspection',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T15:00'},
  1819 |         '332':{checkout:'11:00 완료',checkin:'16:00',assignee:'김민지1',occupancy:'vacant',cleaning:'cleaning',nextCheckoutAt:'2026-08-17T13:00',nextCheckinAt:'2026-08-17T16:00'},
  1820 |         '528':{checkout:'10:00 완료',checkin:'14:00',assignee:'김민지1',occupancy:'vacant',cleaning:'upload'},
  1821 |         '536':{checkout:'완료',checkin:'17:00',assignee:'김민지2',occupancy:'vacant',cleaning:'approved'},
  1822 |         '639':{checkout:'11:00 완료',checkin:'16:00',assignee:'이서연',occupancy:'vacant',cleaning:'inspection',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T16:00'},
  1823 |         '142':{checkout:'연박 투숙',checkin:'투숙 중',assignee:'미정',occupancy:'occupied',actualCheckinAt:'2026-08-14T16:00',plannedCheckoutAt:'2026-08-18T11:00',currentStayReservationId:'reservation-demo-142',stayover:true,cleaning:'stayover-requested',stayoverRequest:{date:'2026-08-17',accessStart:'13:00',requestDue:'14:30',accessEnd:'15:00'}},
  1824 |         '211':{checkout:'8/16 11:00',checkin:'8/15 16:00',assignee:'미정',occupancy:'vacant',cleaning:'future',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T16:00'},
  1825 |         '352':{checkout:'없음',checkin:'예정 없음',assignee:'미정',occupancy:'vacant',cleaning:'unassigned'}
  1826 |       };
  1827 |       const ROOM_BASELINE = ROOM_CATALOG.map(([no,type,elevator])=>{
  1828 |         const occupiedSeed=INITIAL_OCCUPIED_ROOMS[no],hold=ROOM_STATUS_HOLDS[no];
  1829 |         return {
  1830 |           no,type,elevator,catalogSource:'2026-08',checkout:occupiedSeed?'예정 미입력':'정보 없음',checkin:occupiedSeed?'투숙 중':'정보 없음',assignee:'미정',
  1831 |           catalogStatus:hold?'hold':'available',occupancy:occupiedSeed?'occupied':'vacant',cleaning:'idle',dataIssue:hold||null,
  1832 |           occupancySeedSource:occupiedSeed?'8월 객실현황 초기값':null,...(DEMO_ROOM_OVERRIDES[no]||{})
  1833 |         };
  1834 |       });
  1835 |       const cloneRoomRecord=room=>JSON.parse(JSON.stringify(room));
  1836 |       const ROOMS = ROOM_BASELINE.map(cloneRoomRecord);
  1837 |       function resetRoomCatalogState(){ROOMS.splice(0,ROOMS.length,...ROOM_BASELINE.map(cloneRoomRecord));}
  1838 |       function guestPolicyForRoom(roomNo) {
  1839 |         const room=ROOMS.find(item=>item.no===String(roomNo)),typeId=room?.type||'standard',type=ROOM_TYPES[typeId]||ROOM_TYPES.standard;
  1840 |         return {typeId,defaultGuestCount:type.defaultGuestCount,maxGuestCount:type.maxGuestCount};
  1841 |       }
  1842 |       function reservationGuestCount(reservation) {
  1843 |         const policy=guestPolicyForRoom(reservation?.room),value=Number(reservation?.guestCount);
  1844 |         return Number.isInteger(value)&&value>=1?value:policy.defaultGuestCount;
  1845 |       }
  1846 |       function guestCountLabel(value) { return Number.isInteger(Number(value))&&Number(value)>=1?`${Number(value)}명`:'인원 미기록'; }
  1847 |       function reservationHasExtraGuests(reservation) {
  1848 |         return !!reservation&&reservationGuestCount(reservation)>guestPolicyForRoom(reservation.room).defaultGuestCount;
  1849 |       }
  1850 |       function roomHasExtraGuests(no) {
  1851 |         const reservation=activeReservationsFor(state,String(no)).find(item=>!reservationRecordIsPast(item))||null;
  1852 |         return reservationHasExtraGuests(reservation);
  1853 |       }
  1854 |       const INITIAL_RESERVATIONS = Object.freeze([
  1855 |         {id:'reservation-demo-117',room:'117',checkInAt:'2026-08-14T16:00',checkOutAt:'2026-08-15T13:00',guestCount:2,source:'card',status:'active'},
  1856 |         {id:'reservation-demo-142',room:'142',checkInAt:'2026-08-14T16:00',checkOutAt:'2026-08-18T11:00',source:'card',status:'active'},
  1857 |         {id:'reservation-demo-350',room:'350',checkInAt:'2026-08-16T15:00',checkOutAt:'2026-08-17T11:00',source:'card',status:'active'},
  1858 |         {id:'reservation-demo-350-next',room:'350',checkInAt:'2026-08-17T15:00',checkOutAt:'2026-08-18T11:00',source:'grid',status:'active'},
  1859 |         {id:'reservation-demo-332',room:'332',checkInAt:'2026-08-16T16:00',checkOutAt:'2026-08-17T13:00',source:'card',status:'active'},
  1860 |         {id:'reservation-demo-639',room:'639',checkInAt:'2026-08-16T16:00',checkOutAt:'2026-08-17T11:00',source:'card',status:'active'},
  1861 |         {id:'reservation-demo-211',room:'211',checkInAt:'2026-08-16T16:00',checkOutAt:'2026-08-17T11:00',source:'card',status:'active'},
  1862 |         {id:'reservation-demo-516-a',room:'516',checkInAt:'2026-08-17T16:00',checkOutAt:'2026-08-18T11:00',source:'grid',status:'active'},
  1863 |         {id:'reservation-demo-516-b',room:'516',checkInAt:'2026-08-18T16:00',checkOutAt:'2026-08-19T11:00',source:'grid',status:'active'},
  1864 |         {id:'reservation-demo-516-c',room:'516',checkInAt:'2026-08-19T16:00',checkOutAt:'2026-08-22T11:00',source:'grid',status:'active'},
  1865 |         {id:'reservation-demo-516-d',room:'516',checkInAt:'2026-08-22T16:00',checkOutAt:'2026-08-23T11:00',source:'grid',status:'active'},
```

### occurrence 2 · line 2016

```html
  2000 |         return `<section class="notice notice-warning" aria-label="퇴실점검 대상 요약"><div style="min-width:0;flex:1"><strong>퇴실점검 대상 ${rooms.length}개 객실</strong><br>고객 퇴실 후 청소 전 확인이 남은 객실입니다. 청소가 현장 완료되면 자동으로 목록에서 빠집니다.</div><button class="btn btn-outline" type="button" data-action="filter-rooms" data-filter="checkout-inspection">대상 객실 보기</button></section>`;
  2001 |       }
  2002 | 
  2003 |       function projectReservationState(targetState,roomNos=null) {
  2004 |         const selected=roomNos?new Set([].concat(roomNos).map(String)):null,moment=operationalMoment(targetState);
  2005 |         ROOMS.forEach(room=>{
  2006 |           if(selected&&!selected.has(room.no))return;
  2007 |           const reservations=activeReservationsFor(targetState,room.no),current=reservations.find(item=>item.checkInAt<=moment&&moment<item.checkOutAt)||null,future=reservations.find(item=>item.checkInAt>moment)||null,completed=(targetState.reservations||[]).filter(item=>item.room===room.no&&item.status!=='cancelled'&&item.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null,projected=current||future||completed||null;
  2008 |           if(projected){room.reservationCheckinAt=projected.checkInAt;room.reservationCheckoutAt=projected.checkOutAt;room.nextCheckinAt=projected.checkInAt;room.nextCheckoutAt=projected.checkOutAt;room.reservationProjectionId=projected.id;room.checkin=projected.checkInAt.slice(11,16);room.checkout=projected.checkOutAt.slice(11,16);}else if(room.reservationProjectionId){delete room.reservationCheckinAt;delete room.reservationCheckoutAt;delete room.nextCheckinAt;delete room.nextCheckoutAt;delete room.reservationProjectionId;room.checkin='정보 없음';room.checkout='정보 없음';}
  2009 |           const override=room.occupancyOverride;
  2010 |           if(override==='occupied'&&!current){room.occupancy='occupied';room.checkin=room.actualCheckinAt?.slice(11,16)||'투숙 중';room.checkout=(room.plannedCheckoutAt||room.reservationCheckoutAt||'예정 미입력').slice?.(11,16)||'예정 미입력';return;}
  2011 |           if(override==='vacant'&&!current){room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;if(completed)room.actualCheckoutAt=completed.checkOutAt;return;}
  2012 |           if(current){room.occupancy='occupied';room.actualCheckinAt=current.checkInAt;room.plannedCheckoutAt=current.checkOutAt;room.currentStayReservationId=current.id;delete room.actualCheckoutAt;room.checkin=current.checkInAt.slice(11,16);room.checkout=current.checkOutAt.slice(11,16);return;}
  2013 |           room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;if(completed)room.actualCheckoutAt=completed.checkOutAt;else delete room.actualCheckoutAt;
  2014 |         });
  2015 |       }
  2016 |       function roomDataIssue(no){return ROOMS.find(room=>room.no===String(no))?.dataIssue||'';}
  2017 |       function assignmentRoomHoldReason(no,targetState=state){
  2018 |         const roomNo=String(no),dataIssue=roomDataIssue(roomNo);if(dataIssue)return dataIssue;
  2019 |         if(targetState?.roomStopped?.[roomNo])return targetState.roomStopReasons?.[roomNo]||'운영 중지 · 청소 배정 제외';
  2020 |         const candleCount=Number(targetState?.candles?.[roomNo]||0);if(candleCount>0)return `촛불 ${candleCount}개 회수 후 배정 가능`;
  2021 |         return '';
  2022 |       }
  2023 |       function roomIsOnHold(no){return !!assignmentRoomHoldReason(no);}
  2024 |       const MAIDS = [
  2025 |         { id:'m1', name:'김민지1', phone:'•••• 4821', assigned:2, active:'332호 청소 중' },
  2026 |         { id:'m2', name:'김민지2', phone:'•••• 1174', assigned:1, active:'업무 대기' },
  2027 |         { id:'m3', name:'이서연', phone:'•••• 9032', assigned:2, active:'528호 업로드 대기' },
  2028 |         { id:'m4', name:'박소영', phone:'•••• 6248', assigned:0, active:'업무 대기' },
  2029 |         { id:'m5', name:'최은지', phone:'•••• 3516', assigned:0, active:'업무 대기' },
  2030 |         { id:'m6', name:'정다현', phone:'•••• 8072', assigned:0, active:'업무 대기' },
  2031 |         { id:'m7', name:'오세라', phone:'•••• 1940', assigned:0, active:'업무 대기' },
  2032 |         { id:'m8', name:'한지민', phone:'•••• 7305', assigned:0, active:'업무 대기' },
  2033 |         { id:'m9', name:'윤가영', phone:'•••• 5683', assigned:0, active:'업무 대기' }
  2034 |       ];
  2035 |       const INITIAL_MANUAL_ASSIGNMENT_TARGETS = [
  2036 |         {id:'manual-352-checkout-2026-08-17',room:'352',type:'standard',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:00',deadline:'14:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'}
  2037 |       ];
  2038 |       const SCALE_ASSIGNMENT_TARGETS = [
  2039 |         {id:'manual-516-checkout-2026-08-17',room:'516',type:'standard',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:30',deadline:'14:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2040 |         {id:'manual-623-checkout-2026-08-17',room:'623',type:'standard',kind:'퇴실 청소',date:'2026-08-17',checkout:'11:00',deadline:'15:00',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2041 |         {id:'manual-540-checkout-2026-08-17',room:'540',type:'premium',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:00',deadline:'15:00',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2042 |         {id:'manual-641-checkout-2026-08-17',room:'641',type:'oceanPremium',kind:'퇴실 청소',date:'2026-08-17',checkout:'11:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2043 |         {id:'manual-645-checkout-2026-08-17',room:'645',type:'oceanFamily',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:30',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2044 |         {id:'manual-651-checkout-2026-08-17',room:'651',type:'premium',kind:'퇴실 청소',date:'2026-08-17',checkout:'11:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'}
  2045 |       ];
  2046 | 
  2047 |       const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY = Object.freeze({
  2048 |         m1:Object.freeze([0,1,3,4,5,6]),
  2049 |         m2:Object.freeze([1,2,4,5,6]),
  2050 |         m3:Object.freeze([0,2,3,4,5,6]),
```

### occurrence 3 · line 2018

```html
  2002 | 
  2003 |       function projectReservationState(targetState,roomNos=null) {
  2004 |         const selected=roomNos?new Set([].concat(roomNos).map(String)):null,moment=operationalMoment(targetState);
  2005 |         ROOMS.forEach(room=>{
  2006 |           if(selected&&!selected.has(room.no))return;
  2007 |           const reservations=activeReservationsFor(targetState,room.no),current=reservations.find(item=>item.checkInAt<=moment&&moment<item.checkOutAt)||null,future=reservations.find(item=>item.checkInAt>moment)||null,completed=(targetState.reservations||[]).filter(item=>item.room===room.no&&item.status!=='cancelled'&&item.checkOutAt<=moment).sort((left,right)=>right.checkOutAt.localeCompare(left.checkOutAt)||right.id.localeCompare(left.id))[0]||null,projected=current||future||completed||null;
  2008 |           if(projected){room.reservationCheckinAt=projected.checkInAt;room.reservationCheckoutAt=projected.checkOutAt;room.nextCheckinAt=projected.checkInAt;room.nextCheckoutAt=projected.checkOutAt;room.reservationProjectionId=projected.id;room.checkin=projected.checkInAt.slice(11,16);room.checkout=projected.checkOutAt.slice(11,16);}else if(room.reservationProjectionId){delete room.reservationCheckinAt;delete room.reservationCheckoutAt;delete room.nextCheckinAt;delete room.nextCheckoutAt;delete room.reservationProjectionId;room.checkin='정보 없음';room.checkout='정보 없음';}
  2009 |           const override=room.occupancyOverride;
  2010 |           if(override==='occupied'&&!current){room.occupancy='occupied';room.checkin=room.actualCheckinAt?.slice(11,16)||'투숙 중';room.checkout=(room.plannedCheckoutAt||room.reservationCheckoutAt||'예정 미입력').slice?.(11,16)||'예정 미입력';return;}
  2011 |           if(override==='vacant'&&!current){room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;if(completed)room.actualCheckoutAt=completed.checkOutAt;return;}
  2012 |           if(current){room.occupancy='occupied';room.actualCheckinAt=current.checkInAt;room.plannedCheckoutAt=current.checkOutAt;room.currentStayReservationId=current.id;delete room.actualCheckoutAt;room.checkin=current.checkInAt.slice(11,16);room.checkout=current.checkOutAt.slice(11,16);return;}
  2013 |           room.occupancy='vacant';delete room.actualCheckinAt;delete room.plannedCheckoutAt;delete room.currentStayReservationId;if(completed)room.actualCheckoutAt=completed.checkOutAt;else delete room.actualCheckoutAt;
  2014 |         });
  2015 |       }
  2016 |       function roomDataIssue(no){return ROOMS.find(room=>room.no===String(no))?.dataIssue||'';}
  2017 |       function assignmentRoomHoldReason(no,targetState=state){
  2018 |         const roomNo=String(no),dataIssue=roomDataIssue(roomNo);if(dataIssue)return dataIssue;
  2019 |         if(targetState?.roomStopped?.[roomNo])return targetState.roomStopReasons?.[roomNo]||'운영 중지 · 청소 배정 제외';
  2020 |         const candleCount=Number(targetState?.candles?.[roomNo]||0);if(candleCount>0)return `촛불 ${candleCount}개 회수 후 배정 가능`;
  2021 |         return '';
  2022 |       }
  2023 |       function roomIsOnHold(no){return !!assignmentRoomHoldReason(no);}
  2024 |       const MAIDS = [
  2025 |         { id:'m1', name:'김민지1', phone:'•••• 4821', assigned:2, active:'332호 청소 중' },
  2026 |         { id:'m2', name:'김민지2', phone:'•••• 1174', assigned:1, active:'업무 대기' },
  2027 |         { id:'m3', name:'이서연', phone:'•••• 9032', assigned:2, active:'528호 업로드 대기' },
  2028 |         { id:'m4', name:'박소영', phone:'•••• 6248', assigned:0, active:'업무 대기' },
  2029 |         { id:'m5', name:'최은지', phone:'•••• 3516', assigned:0, active:'업무 대기' },
  2030 |         { id:'m6', name:'정다현', phone:'•••• 8072', assigned:0, active:'업무 대기' },
  2031 |         { id:'m7', name:'오세라', phone:'•••• 1940', assigned:0, active:'업무 대기' },
  2032 |         { id:'m8', name:'한지민', phone:'•••• 7305', assigned:0, active:'업무 대기' },
  2033 |         { id:'m9', name:'윤가영', phone:'•••• 5683', assigned:0, active:'업무 대기' }
  2034 |       ];
  2035 |       const INITIAL_MANUAL_ASSIGNMENT_TARGETS = [
  2036 |         {id:'manual-352-checkout-2026-08-17',room:'352',type:'standard',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:00',deadline:'14:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'}
  2037 |       ];
  2038 |       const SCALE_ASSIGNMENT_TARGETS = [
  2039 |         {id:'manual-516-checkout-2026-08-17',room:'516',type:'standard',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:30',deadline:'14:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2040 |         {id:'manual-623-checkout-2026-08-17',room:'623',type:'standard',kind:'퇴실 청소',date:'2026-08-17',checkout:'11:00',deadline:'15:00',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2041 |         {id:'manual-540-checkout-2026-08-17',room:'540',type:'premium',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:00',deadline:'15:00',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2042 |         {id:'manual-641-checkout-2026-08-17',room:'641',type:'oceanPremium',kind:'퇴실 청소',date:'2026-08-17',checkout:'11:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2043 |         {id:'manual-645-checkout-2026-08-17',room:'645',type:'oceanFamily',kind:'퇴실 청소',date:'2026-08-17',checkout:'10:30',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'},
  2044 |         {id:'manual-651-checkout-2026-08-17',room:'651',type:'premium',kind:'퇴실 청소',date:'2026-08-17',checkout:'11:00',deadline:'15:30',source:'manual',sourceLabel:'직접 등록 · 현장 요청'}
  2045 |       ];
  2046 | 
  2047 |       const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY = Object.freeze({
  2048 |         m1:Object.freeze([0,1,3,4,5,6]),
  2049 |         m2:Object.freeze([1,2,4,5,6]),
  2050 |         m3:Object.freeze([0,2,3,4,5,6]),
  2051 |         m4:Object.freeze([0,1,2,3,4,5,6]),
  2052 |         m5:Object.freeze([0,2,3,5,6]),
```

### occurrence 4 · line 4161

```html
  4145 |       function renderAccordion(key,title,count,body,open=false) {
  4146 |         const expanded=state.todaySections[key] ?? open;
  4147 |         return `<section class="accordion"><button type="button" class="accordion-toggle" data-action="toggle-section" data-key="${key}" aria-expanded="${expanded}">${icon('chevronRight','icon-sm')}<span>${esc(title)}</span><span class="accordion-count">${esc(String(count))}</span></button><div class="accordion-body" ${expanded?'':'hidden'}>${body}</div></section>`;
  4148 |       }
  4149 | 
  4150 |       function elevatorLabel(room) {
  4151 |         return room?.elevator?`${room.elevator} 엘리베이터`:'엘리베이터 미기재';
  4152 |       }
  4153 |       function plannedCheckoutLabel(room) {
  4154 |         if(!room)return '미입력';
  4155 |         const explicit=room.plannedCheckoutAt||room.reservationCheckoutAt||room.nextCheckoutAt;
  4156 |         if(explicit)return explicit;
  4157 |         return !room.actualCheckoutAt&&/^\d{1,2}:\d{2}(?:\s|$)/.test(room.checkout||'')?room.checkout:'미입력';
  4158 |       }
  4159 |       function roomMasterFingerprint(room) {
  4160 |         return room?JSON.stringify([
  4161 |           room.no,room.type,room.elevator||'',room.dataIssue||'',room.occupancy,room.occupancyOverride||'',
  4162 |           room.reservationCheckoutAt||'',room.nextCheckoutAt||'',room.actualCheckoutAt||'',
  4163 |           room.stayoverRequest?.date||'',room.stayoverRequest?.accessStart||'',room.stayoverRequest?.requestDue||'',room.stayoverRequest?.accessEnd||''
  4164 |         ]):'';
  4165 |       }
  4166 |       function renderRoomBasicsPanel(no) {
  4167 |         const room=ROOMS.find(item=>item.no===no),type=ROOM_TYPES[room?.type||'standard'];
  4168 |         if(!room)return '';
  4169 |         return `<section class="card card-pad" aria-labelledby="room-basics-${no}"><div class="section-head"><div><h3 id="room-basics-${no}">객실 기본정보</h3><p class="audit-note">운영자가 수정한 값은 이후 새 작업부터 적용됩니다.</p></div>${button('객실 정보 수정','edit-room-info','outline',`data-id="${no}" ${isLocked()?'disabled':''}`)}</div><div class="info-grid"><div class="info-item"><span>객실번호</span><strong>${no}호</strong></div><div class="info-item"><span>객실 타입</span><strong>${esc(type.name)}</strong></div><div class="info-item"><span>엘리베이터</span><strong>${esc(elevatorLabel(room))}</strong></div><div class="info-item"><span>기본 청소요금</span><strong>${money(type.rate)} · 시트 정본</strong></div></div><p class="audit-note" style="margin:10px 0 0">객실번호는 PIN·청소·주급 이력을 잇는 식별값이라 여기서는 고정합니다. 타입·엘리베이터 수정은 과거 완료 기록을 바꾸지 않습니다.</p></section>`;
  4170 |       }
  4171 |       function renderOccupancyPanel(no) {
  4172 |         const room=ROOMS.find(item=>item.no===no),occupied=room?.occupancy==='occupied',current=room?reservationAtOperationalMoment(no):null,next=room?activeReservationsFor(state,no).find(reservation=>reservation.checkInAt>reservationCurrentMoment())||null:null,actual=room?.actualCheckoutAt;
  4173 |         if(!room)return '';
  4174 |         const stateLabel=occupied?'투숙 중':next?'입실 예정':'공실',tone=occupied?'blue':next?'neutral':'green',schedule=current||next;
  4175 |         return `<section class="card card-pad" aria-labelledby="room-occupancy-${no}"><div class="section-head"><div><h3 id="room-occupancy-${no}">현재 투숙 상태</h3><p class="audit-note">예약에 저장된 체크인·체크아웃 일시를 기준으로 자동 계산합니다.</p></div>${statusBadge(stateLabel,tone)}</div><div class="info-grid"><div class="info-item"><span>현재 상태</span><strong>${esc(stateLabel)}</strong></div><div class="info-item"><span>${current?'체크인':'다음 체크인'}</span><strong>${esc(schedule?reservationMomentLabel(schedule.checkInAt):'일정 없음')}</strong></div><div class="info-item"><span>${current?'예정 체크아웃':'다음 체크아웃'}</span><strong>${esc(schedule?reservationMomentLabel(schedule.checkOutAt):'일정 없음')}</strong></div>${actual&&!occupied?`<div class="info-item"><span>최근 자동 퇴실</span><strong>${esc(reservationMomentLabel(actual))}</strong></div>`:''}</div><div class="notice notice-info" style="margin:12px 0 0"><div><strong>입실·퇴실은 예약 시각에 자동 반영됩니다.</strong><br>얼리 체크인과 레이트 체크아웃도 예약에 저장된 실제 시각을 사용합니다. 시각이 잘못되면 예약 관리에서 수정하세요.</div></div><div class="job-actions" style="margin-top:12px">${button(schedule?'예약 관리':'예약 등록','reservation-edit','outline',`data-id="${no}"`)}</div></section>`;
  4176 |       }
  4177 |       function mergeRoomBasicsPanel(html,no) {
  4178 |         const marker='<div class="detail-stack">',index=html.indexOf(marker);
  4179 |         return index<0?html:html.slice(0,index+marker.length)+renderRoomBasicsPanel(no)+html.slice(index+marker.length);
  4180 |       }
  4181 | 
  4182 |       function unresolvedRoomIssueRecords(no) {
  4183 |         return roomIssueRecords(no).filter(record=>record.status!=='resolved');
  4184 |       }
  4185 |       function blockingRoomIssueRecords(no) {
  4186 |         return unresolvedRoomIssueRecords(no).filter(record=>record.blocksCheckin===true);
  4187 |       }
  4188 |       function cardReservationFor(no) {
  4189 |         const reservations=activeReservationsFor(state,no),pivot=`${state.selectedDate}T00:00`;
  4190 |         return reservations.find(item=>item.checkOutAt>pivot)||reservations[0]||null;
  4191 |       }
  4192 |       function cardReservationStatus(no) {
  4193 |         const reservation=cardReservationFor(no);
  4194 |         return reservationTimeStatus(reservation?.checkInAt,reservation?.checkOutAt);
  4195 |       }
```

### occurrence 5 · line 7022

```html
  7006 |           applyOperationalDate(state,'2026-08-15');closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector('[data-action="open-calendar"]')?.focus());return;
  7007 |         }
  7008 |         if(a==='date-shift'){const d=dateObject();d.setDate(d.getDate()+Number(el.dataset.offset));applyOperationalDate(state,dateIso(d));render();requestAnimationFrame(()=>document.querySelector(`[data-action="date-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;}
  7009 |         if(a==='date-today'){applyOperationalDate(state,'2026-08-15');render();requestAnimationFrame(()=>document.querySelector('[data-action="date-today"]')?.focus());return;}
  7010 |         if(a==='toggle-section'){const key=el.dataset.key;state.todaySections[key]=!state.todaySections[key];render();requestAnimationFrame(()=>document.querySelector(`[data-action="toggle-section"][data-key="${key}"]`)?.focus());return;}
  7011 |         if(a==='clear-room-filters'){state.roomSearch='';state.roomTypeFilter='all';state.roomFilter='all';state.listMode='data';render();focusAfterRender('[data-control="room-filter"]');return;}
  7012 |         if(a==='edit-room-info'){openRoomInfoEditor(id,el);return;}
  7013 |         if(a==='save-room-info'){
  7014 |           const room=ROOMS.find(item=>item.no===id),expected=el.dataset.fingerprint||'',type=document.getElementById('room-info-type')?.value||'',elevator=document.getElementById('room-info-elevator')?.value??'',wasHeld=roomIsOnHold(id),occupancy=document.getElementById('room-info-occupancy')?.value||'';
  7015 |           if(!adminCanMutate()||!room||roomMasterFingerprint(room)!==expected){closeModal();render();toast('객실 정보 또는 관리자 상태가 바뀌어 저장하지 않았습니다. 다시 확인하세요.','error');return;}
  7016 |           if(!ROOM_TYPES[type]||!['','A','B','C'].includes(elevator)){toast('객실 타입과 엘리베이터 값을 다시 확인하세요.','error');return;}
  7017 |           const overCapacity=activeReservationsFor(state,id).find(reservation=>!reservationRecordIsPast(reservation)&&reservationGuestCount(reservation)>ROOM_TYPES[type].maxGuestCount);
  7018 |           if(overCapacity){toast(`${id}호 ${quickRangeLabel(overCapacity)} 예약이 ${reservationGuestCount(overCapacity)}명이라 최대 ${ROOM_TYPES[type].maxGuestCount}명인 ${ROOM_TYPES[type].name} 타입으로 바꿀 수 없습니다.`,'error');document.getElementById('room-info-type')?.focus();return;}
  7019 |           if(wasHeld&&!['vacant','occupied'].includes(occupancy)){toast('현재 투숙 상태를 선택해야 정보 확인 필요 상태를 해제할 수 있습니다.','error');document.getElementById('room-info-occupancy')?.focus();return;}
  7020 |           const before=`${ROOM_TYPES[room.type].name} · ${elevatorLabel(room)}${wasHeld?' · 정보 확인 필요':''}`;
  7021 |           room.type=type;room.elevator=elevator||null;
  7022 |           if(wasHeld){room.occupancyOverride=occupancy;room.occupancy=occupancy;room.catalogStatus='available';room.dataIssue=null;room.checkout=occupancy==='occupied'?'예정 미입력':'정보 없음';room.checkin=occupancy==='occupied'?'투숙 중':'정보 없음';}
  7023 |           const after=`${ROOM_TYPES[room.type].name} · ${elevatorLabel(room)}${wasHeld?` · ${room.occupancy==='occupied'?'투숙 중':'공실'}로 확인`:''}`;
  7024 |           appendEvent(`${id}호 객실 정보 수정`,`${before} → ${after} · 이후 새 작업부터 적용`,{roomId:id});
  7025 |           closeModal();render();focusAfterRender(`[data-action="edit-room-info"][data-id="${id}"]`);toast(wasHeld?'객실 정보를 확정하고 일반 운영 흐름을 열었습니다.':'객실 기본정보를 저장했습니다.');return;
  7026 |         }
  7027 |         if(a==='manual-checkout'){openManualCheckout(id,el);return;}
  7028 |         if(a==='confirm-manual-checkout'){
  7029 |           const room=ROOMS.find(item=>item.no===id),expected=el.dataset.fingerprint||'',blockingAttempt=manualCheckoutBlockingAttempt(id),unstartedAttempt=activeUnfinishedAttempt(id),pinViewed=unstartedAttempt&&roomPinWasViewed(id,unstartedAttempt.id);
  7030 |           if(!adminCanMutate()||!room||roomIsOnHold(id)||room.occupancy!=='occupied'||roomMasterFingerprint(room)!==expected||blockingAttempt){closeModal();render();toast(blockingAttempt?'진행 중인 청소 작업을 먼저 마무리하세요.':'투숙 상태 또는 관리자 최신 상태가 바뀌어 체크아웃하지 않았습니다.','error');return;}
  7031 |           const actualCheckoutAt=`${state.selectedDate}T${state.time}`,plannedCheckout=plannedCheckoutLabel(room),activeReservation=currentOccupiedReservation(room),manualDraftId=`manual-checkout-${id}-${state.selectedDate}`,reservationDraft=activeReservation?state.drafts.find(draft=>draft.reservationId===activeReservation.id)||null:null,existingDraft=reservationDraft||state.drafts.find(draft=>draft.id===manualDraftId)||state.drafts.find(draft=>draft.room===id&&draft.kind==='퇴실 청소'&&!draft.reservationId&&draft.date===state.selectedDate),templateSnapshot=existingDraft?.templateSnapshot||unstartedAttempt?.templateSnapshot||templateSnapshotFor(id,'퇴실 청소'),previousWorkDate=unstartedAttempt?attemptWorkDate(unstartedAttempt,state.selectedDate):null,previousAccessStart=unstartedAttempt?.accessStart||unstartedAttempt?.checkoutSnapshot||startTimeFor(id);
  7032 |           const nextReservation=activeReservationsFor(state,id).filter(reservation=>reservation.id!==activeReservation?.id).find(reservation=>reservation.checkInAt>=actualCheckoutAt)||null,sameDayNext=nextReservation?.checkInAt.slice(0,10)===state.selectedDate,nextCheckinSnapshot=sameDayNext?nextReservation.checkInAt.slice(11,16):DEFAULT_CHECKIN_TIME,nextDeadlineSnapshot=shiftClockTime(nextCheckinSnapshot,-30)||'15:30';
  7033 |           if(existingDraft){existingDraft.date=state.selectedDate;existingDraft.source='manual-checkout';existingDraft.actualCheckoutAt=actualCheckoutAt;if(activeReservation){if(!existingDraft.reservationId)existingDraft.reservationId=activeReservation.id;existingDraft.guestCount=reservationGuestCount(activeReservation);}if(!existingDraft.templateSnapshot)existingDraft.templateSnapshot=templateSnapshot;}
  7034 |           else if(!unstartedAttempt)state.drafts.push({id:manualDraftId,room:id,kind:'퇴실 청소',created:state.time,date:state.selectedDate,source:'manual-checkout',actualCheckoutAt,reservationId:activeReservation?.id||null,guestCount:activeReservation?reservationGuestCount(activeReservation):null,templateSnapshot});
  7035 |           const canonicalCheckoutDraft=existingDraft||state.drafts.find(draft=>draft.id===manualDraftId)||null;
  7036 |           if(canonicalCheckoutDraft)state.drafts=state.drafts.filter(draft=>{if(draft===canonicalCheckoutDraft)return true;const sameReservation=activeReservation&&draft.reservationId===activeReservation.id,sameUnlinkedDay=draft.room===id&&draft.kind==='퇴실 청소'&&!draft.reservationId&&draft.date===state.selectedDate;return !(draft.id===manualDraftId||sameReservation||sameUnlinkedDay);});
  7037 |           if(!unstartedAttempt){
  7038 |             const manualTarget={id:manualDraftId,room:id,type:room.type,kind:'퇴실 청소',date:state.selectedDate,checkout:state.time,checkin:nextCheckinSnapshot,deadline:nextDeadlineSnapshot,nextReservationId:sameDayNext?nextReservation.id:null,source:'manual',sourceLabel:'직접 등록 · 지금 체크아웃',reservationId:activeReservation?.id||null,guestCount:activeReservation?reservationGuestCount(activeReservation):null};
  7039 |             const existingTarget=state.manualAssignmentTargets.find(target=>target.id===manualDraftId),reopened=reopenCancelledManualCleaningTarget(manualTarget,'실제 체크아웃으로 퇴실 청소 다시 생성');if(!reopened){if(existingTarget)Object.assign(existingTarget,manualTarget);else state.manualAssignmentTargets.push(manualTarget);state.cleaningTargets[manualDraftId]=cleaningTargetSnapshot(manualTarget,state.selectedDate);}assignmentFor(manualTarget);
  7040 |           }
  7041 |           if(activeReservation){activeReservation.status='checked-out';activeReservation.actualCheckoutAt=actualCheckoutAt;activeReservation.completedAt=actualCheckoutAt;activeReservation.updatedAt=actualCheckoutAt;}
  7042 |           if(unstartedAttempt){
  7043 |             if(activeReservation&&!unstartedAttempt.reservationIdSnapshot)unstartedAttempt.reservationIdSnapshot=activeReservation.id;
  7044 |             if(activeReservation&&unstartedAttempt.reservationIdSnapshot===activeReservation.id&&!guestCountForAttempt(unstartedAttempt))unstartedAttempt.guestCountSnapshot=reservationGuestCount(activeReservation);
  7045 |             if(pinViewed){maskPin();appendEvent(`${id}호 PIN lease 종료`,'실제 체크아웃 시각 변경 · 기존 조회 원문 폐기 · 새 시작 시각부터 재조회',{maidIds:unstartedAttempt.performerId?[unstartedAttempt.performerId]:[],roomId:id,attemptId:unstartedAttempt.id});}
  7046 |             Object.assign(unstartedAttempt,{workDate:previousWorkDate||state.selectedDate,effectiveDate:state.selectedDate,accessStart:state.time,checkoutSnapshot:state.time,checkinSnapshot:nextCheckinSnapshot,deadlineSnapshot:nextDeadlineSnapshot,nextReservationIdSnapshot:sameDayNext?nextReservation.id:null,actualCheckoutAt,accessReviewRequired:false});recordManualCheckoutScheduleChange(id,unstartedAttempt,previousWorkDate,previousAccessStart);
  7047 |           }
  7048 |           const cancelledStayover=state.drafts.filter(draft=>draft.room===id&&draft.kind==='연박 청소').length;
  7049 |           const cancelledStayoverTargets=cancelPendingStayoverTargetsAfterCheckout(id),cancelledStayoverDraftIds=new Set(state.drafts.filter(draft=>draft.room===id&&draft.kind==='연박 청소').map(draft=>draft.id));
  7050 |           state.drafts=state.drafts.filter(draft=>!cancelledStayoverDraftIds.has(draft.id));state.selectedDrafts=state.selectedDrafts.filter(draftId=>!cancelledStayoverDraftIds.has(draftId));
  7051 |           room.occupancy='vacant';room.plannedCheckoutAt=plannedCheckout==='미입력'?null:plannedCheckout;room.actualCheckoutAt=actualCheckoutAt;delete room.currentStayReservationId;delete room.stayoverRequest;projectReservationState(state,id);room.checkout=`${state.time} 완료`;room.checkin=room.nextCheckinAt?room.nextCheckinAt.slice(11,16):'예정 없음';if(!unstartedAttempt){room.assignee='미정';state.jobs[id]='draft';}state.candles[id]=0;
  7052 |           const cleaningResult=unstartedAttempt?`기존 ${unstartedAttempt.performerName} 담당·${unstartedAttempt.id} 회차 유지`:'퇴실 청소 초안 1건';
  7053 |           appendEvent(`${id}호 지금 체크아웃`,`${dateLabel(state.selectedDate)} ${state.time} 실제 퇴실 · 예정 ${plannedCheckout} 보존 · ${cleaningResult}${activeReservation?` · 예약 ${activeReservation.id} 실제 종료`:''}${cancelledStayover||cancelledStayoverTargets?' · 미시작 투숙 중 청소 요청 종료':''}`,{roomId:id});
  7054 |           closeModal();render();focusAfterRender(`[data-action="room-detail"][data-id="${id}"]`);toast(unstartedAttempt?`${id}호를 공실로 바꾸고 기존 청소 담당·회차의 시작 시각을 갱신했습니다.`:`${id}호를 공실·청소 필요로 바꾸고 퇴실 청소 초안을 연결했습니다.`);return;
  7055 |         }
  7056 |         if(a==='manual-checkin'){openManualCheckin(id,el);return;}
```

## initial occupied: `INITIAL_OCCUPIED_ROOMS`

matches: 2

### occurrence 1 · line 1804

```html
  1788 |       function reservationStatusText(status,kind) {
  1789 |         if(kind==='checkin'&&!status.checkin)return '체크인 일정 없음';
  1790 |         if(kind==='checkout'&&!status.checkout)return '체크아웃 일정 없음';
  1791 |         if(kind==='checkin')return status.early?`얼리 체크인 · ${status.earlyOffset} · 체크인 ${status.checkin}`:`${status.checkin===DEFAULT_CHECKIN_TIME?'기본':'일반'} 체크인 · ${status.checkin||DEFAULT_CHECKIN_TIME}`;
  1792 |         return status.late?`레이트 체크아웃 · ${status.lateOffset} · 체크아웃 ${status.checkout}`:`${status.checkout===DEFAULT_CHECKOUT_TIME?'기본':'일반'} 체크아웃 · ${status.checkout||DEFAULT_CHECKOUT_TIME}`;
  1793 |       }
  1794 | 
  1795 |       const ROOM_TYPES = {
  1796 |         standard: { name: '스탠다드', rate: 16000, minutes: 55, defaultGuestCount:2, maxGuestCount:2, rateSource:'객실현황(26.08) · 8월 시트' },
  1797 |         premium: { name: '프리미어', rate: 20000, minutes: 65, defaultGuestCount:2, maxGuestCount:3, rateSource:'객실현황(26.08) · 8월 시트' },
  1798 |         oceanPremium: { name: '파셜 오션뷰', rate: 20000, minutes: 70, defaultGuestCount:2, maxGuestCount:4, rateSource:'객실현황(26.08) · 8월 시트' },
  1799 |         oceanFamily: { name: '패밀리 투룸', rate: 30000, minutes: 80, defaultGuestCount:4, maxGuestCount:6, rateSource:'객실현황(26.08) · 8월 시트' }
  1800 |       };
  1801 |       const ROOM_CATALOG_SOURCE = '객실현황(26.08) · 8월 시트';
  1802 |       const ROOM_ELEVATOR_SOURCE = '2026-08-18 사용자 제공 건물 지도';
  1803 |       const ROOM_STATUS_HOLDS = {'762':'현재 투숙 상태 확인 필요'};
  1804 |       const INITIAL_OCCUPIED_ROOMS = Object.freeze({
  1805 |         '553':{startedAt:'2025-11-29'},'629':{startedAt:'2025-05-01'},'139':{startedAt:null},
  1806 |         '358':{startedAt:'2026-03-17'},'359':{startedAt:'2026-03-17'},'449':{startedAt:'2026-03-17'},
  1807 |         '458':{startedAt:'2026-03-23'},'461':{startedAt:'2026-03-17'},'558':{startedAt:'2026-06-01'},
  1808 |         '559':{startedAt:'2026-03-17'},'628':{startedAt:'2026-03-31'}
  1809 |       });
  1810 |       const ROOM_CATALOG = [
  1811 |         ['350','standard','C'],['352','standard','C'],['516','standard','A'],['552','standard','C'],['556','standard','C'],['623','standard','A'],['652','standard','C'],['657','standard','B'],['660','standard','B'],['662','standard','B'],['720','standard','A'],['723','standard','A'],['726','standard','A'],['729','standard','B'],['750','standard','C'],['752','standard','C'],['753','standard','C'],['756','standard','C'],['760','standard','B'],['762','standard','B'],['553','standard','C'],['629','standard','B'],
  1812 |         ['117','premium','A'],['135','premium','C'],['136','premium','C'],['240','premium','C'],['332','premium','B'],['454','premium','C'],['455','premium','C'],['459','premium','B'],['527','premium','A'],['528','premium','B'],['531','premium','B'],['534','premium','C'],['540','premium','C'],['541','premium','C'],['549','premium','C'],['554','premium','C'],['555','premium','C'],['561','premium','B'],['603','premium','B'],['621','premium','A'],['624','premium','A'],['634','premium','C'],['635','premium','C'],['649','premium','C'],['651','premium','C'],['654','premium','C'],['655','premium','C'],['658','premium','B'],['661','premium','B'],['721','premium','A'],['722','premium','A'],['724','premium','A'],['727','premium','A'],['730','premium','B'],['731','premium','B'],['732','premium','B'],['749','premium','C'],['751','premium','C'],['754','premium','C'],['755','premium','C'],['759','premium','B'],['761','premium','B'],['139','premium','C'],['358','premium','B'],['359','premium','B'],['449','premium','C'],['458','premium','B'],['461','premium','B'],['558','premium','B'],['559','premium','B'],['628','premium','B'],
  1813 |         ['536','oceanPremium','C'],['639','oceanPremium','C'],['640','oceanPremium','C'],['641','oceanPremium','C'],['701','oceanPremium','B'],['704','oceanPremium','B'],['706','oceanPremium','A'],['707','oceanPremium','A'],['735','oceanPremium','C'],['738','oceanPremium','C'],['739','oceanPremium','C'],['740','oceanPremium','C'],['741','oceanPremium','C'],
  1814 |         ['142','oceanFamily','C'],['211','oceanFamily','A'],['314','oceanFamily','A'],['410','oceanFamily','A'],['413','oceanFamily','A'],['415','oceanFamily','A'],['444','oceanFamily','C'],['509','oceanFamily','A'],['510','oceanFamily','A'],['511','oceanFamily','A'],['512','oceanFamily','A'],['514','oceanFamily','A'],['542','oceanFamily','C'],['544','oceanFamily','C'],['546','oceanFamily','C'],['608','oceanFamily','A'],['609','oceanFamily','A'],['610','oceanFamily','A'],['611','oceanFamily','A'],['612','oceanFamily','A'],['637','oceanFamily','C'],['645','oceanFamily','C'],['646','oceanFamily','C'],['647','oceanFamily','C'],['648','oceanFamily','C'],['708','oceanFamily','A'],['709','oceanFamily','A'],['712','oceanFamily','A'],['737','oceanFamily','C'],['743','oceanFamily','C'],['744','oceanFamily','C'],['745','oceanFamily','C'],['746','oceanFamily','C'],['747','oceanFamily','C'],['748','oceanFamily','C']
  1815 |       ];
  1816 |       const DEMO_ROOM_OVERRIDES = {
  1817 |         '117':{checkout:'13:00',checkin:'16:00',assignee:'김민지1',occupancy:'occupied',cleaning:'scheduled',actualCheckinAt:'2026-08-14T16:00',plannedCheckoutAt:'2026-08-15T13:00',currentStayReservationId:'reservation-demo-117'},
  1818 |         '350':{checkout:'완료',checkin:'15:00',assignee:'이서연',occupancy:'vacant',cleaning:'inspection',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T15:00'},
  1819 |         '332':{checkout:'11:00 완료',checkin:'16:00',assignee:'김민지1',occupancy:'vacant',cleaning:'cleaning',nextCheckoutAt:'2026-08-17T13:00',nextCheckinAt:'2026-08-17T16:00'},
  1820 |         '528':{checkout:'10:00 완료',checkin:'14:00',assignee:'김민지1',occupancy:'vacant',cleaning:'upload'},
  1821 |         '536':{checkout:'완료',checkin:'17:00',assignee:'김민지2',occupancy:'vacant',cleaning:'approved'},
  1822 |         '639':{checkout:'11:00 완료',checkin:'16:00',assignee:'이서연',occupancy:'vacant',cleaning:'inspection',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T16:00'},
  1823 |         '142':{checkout:'연박 투숙',checkin:'투숙 중',assignee:'미정',occupancy:'occupied',actualCheckinAt:'2026-08-14T16:00',plannedCheckoutAt:'2026-08-18T11:00',currentStayReservationId:'reservation-demo-142',stayover:true,cleaning:'stayover-requested',stayoverRequest:{date:'2026-08-17',accessStart:'13:00',requestDue:'14:30',accessEnd:'15:00'}},
  1824 |         '211':{checkout:'8/16 11:00',checkin:'8/15 16:00',assignee:'미정',occupancy:'vacant',cleaning:'future',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T16:00'},
  1825 |         '352':{checkout:'없음',checkin:'예정 없음',assignee:'미정',occupancy:'vacant',cleaning:'unassigned'}
  1826 |       };
  1827 |       const ROOM_BASELINE = ROOM_CATALOG.map(([no,type,elevator])=>{
  1828 |         const occupiedSeed=INITIAL_OCCUPIED_ROOMS[no],hold=ROOM_STATUS_HOLDS[no];
  1829 |         return {
  1830 |           no,type,elevator,catalogSource:'2026-08',checkout:occupiedSeed?'예정 미입력':'정보 없음',checkin:occupiedSeed?'투숙 중':'정보 없음',assignee:'미정',
  1831 |           catalogStatus:hold?'hold':'available',occupancy:occupiedSeed?'occupied':'vacant',cleaning:'idle',dataIssue:hold||null,
  1832 |           occupancySeedSource:occupiedSeed?'8월 객실현황 초기값':null,...(DEMO_ROOM_OVERRIDES[no]||{})
  1833 |         };
  1834 |       });
  1835 |       const cloneRoomRecord=room=>JSON.parse(JSON.stringify(room));
  1836 |       const ROOMS = ROOM_BASELINE.map(cloneRoomRecord);
  1837 |       function resetRoomCatalogState(){ROOMS.splice(0,ROOMS.length,...ROOM_BASELINE.map(cloneRoomRecord));}
  1838 |       function guestPolicyForRoom(roomNo) {
```

### occurrence 2 · line 1828

```html
  1812 |         ['117','premium','A'],['135','premium','C'],['136','premium','C'],['240','premium','C'],['332','premium','B'],['454','premium','C'],['455','premium','C'],['459','premium','B'],['527','premium','A'],['528','premium','B'],['531','premium','B'],['534','premium','C'],['540','premium','C'],['541','premium','C'],['549','premium','C'],['554','premium','C'],['555','premium','C'],['561','premium','B'],['603','premium','B'],['621','premium','A'],['624','premium','A'],['634','premium','C'],['635','premium','C'],['649','premium','C'],['651','premium','C'],['654','premium','C'],['655','premium','C'],['658','premium','B'],['661','premium','B'],['721','premium','A'],['722','premium','A'],['724','premium','A'],['727','premium','A'],['730','premium','B'],['731','premium','B'],['732','premium','B'],['749','premium','C'],['751','premium','C'],['754','premium','C'],['755','premium','C'],['759','premium','B'],['761','premium','B'],['139','premium','C'],['358','premium','B'],['359','premium','B'],['449','premium','C'],['458','premium','B'],['461','premium','B'],['558','premium','B'],['559','premium','B'],['628','premium','B'],
  1813 |         ['536','oceanPremium','C'],['639','oceanPremium','C'],['640','oceanPremium','C'],['641','oceanPremium','C'],['701','oceanPremium','B'],['704','oceanPremium','B'],['706','oceanPremium','A'],['707','oceanPremium','A'],['735','oceanPremium','C'],['738','oceanPremium','C'],['739','oceanPremium','C'],['740','oceanPremium','C'],['741','oceanPremium','C'],
  1814 |         ['142','oceanFamily','C'],['211','oceanFamily','A'],['314','oceanFamily','A'],['410','oceanFamily','A'],['413','oceanFamily','A'],['415','oceanFamily','A'],['444','oceanFamily','C'],['509','oceanFamily','A'],['510','oceanFamily','A'],['511','oceanFamily','A'],['512','oceanFamily','A'],['514','oceanFamily','A'],['542','oceanFamily','C'],['544','oceanFamily','C'],['546','oceanFamily','C'],['608','oceanFamily','A'],['609','oceanFamily','A'],['610','oceanFamily','A'],['611','oceanFamily','A'],['612','oceanFamily','A'],['637','oceanFamily','C'],['645','oceanFamily','C'],['646','oceanFamily','C'],['647','oceanFamily','C'],['648','oceanFamily','C'],['708','oceanFamily','A'],['709','oceanFamily','A'],['712','oceanFamily','A'],['737','oceanFamily','C'],['743','oceanFamily','C'],['744','oceanFamily','C'],['745','oceanFamily','C'],['746','oceanFamily','C'],['747','oceanFamily','C'],['748','oceanFamily','C']
  1815 |       ];
  1816 |       const DEMO_ROOM_OVERRIDES = {
  1817 |         '117':{checkout:'13:00',checkin:'16:00',assignee:'김민지1',occupancy:'occupied',cleaning:'scheduled',actualCheckinAt:'2026-08-14T16:00',plannedCheckoutAt:'2026-08-15T13:00',currentStayReservationId:'reservation-demo-117'},
  1818 |         '350':{checkout:'완료',checkin:'15:00',assignee:'이서연',occupancy:'vacant',cleaning:'inspection',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T15:00'},
  1819 |         '332':{checkout:'11:00 완료',checkin:'16:00',assignee:'김민지1',occupancy:'vacant',cleaning:'cleaning',nextCheckoutAt:'2026-08-17T13:00',nextCheckinAt:'2026-08-17T16:00'},
  1820 |         '528':{checkout:'10:00 완료',checkin:'14:00',assignee:'김민지1',occupancy:'vacant',cleaning:'upload'},
  1821 |         '536':{checkout:'완료',checkin:'17:00',assignee:'김민지2',occupancy:'vacant',cleaning:'approved'},
  1822 |         '639':{checkout:'11:00 완료',checkin:'16:00',assignee:'이서연',occupancy:'vacant',cleaning:'inspection',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T16:00'},
  1823 |         '142':{checkout:'연박 투숙',checkin:'투숙 중',assignee:'미정',occupancy:'occupied',actualCheckinAt:'2026-08-14T16:00',plannedCheckoutAt:'2026-08-18T11:00',currentStayReservationId:'reservation-demo-142',stayover:true,cleaning:'stayover-requested',stayoverRequest:{date:'2026-08-17',accessStart:'13:00',requestDue:'14:30',accessEnd:'15:00'}},
  1824 |         '211':{checkout:'8/16 11:00',checkin:'8/15 16:00',assignee:'미정',occupancy:'vacant',cleaning:'future',nextCheckoutAt:'2026-08-17T11:00',nextCheckinAt:'2026-08-17T16:00'},
  1825 |         '352':{checkout:'없음',checkin:'예정 없음',assignee:'미정',occupancy:'vacant',cleaning:'unassigned'}
  1826 |       };
  1827 |       const ROOM_BASELINE = ROOM_CATALOG.map(([no,type,elevator])=>{
  1828 |         const occupiedSeed=INITIAL_OCCUPIED_ROOMS[no],hold=ROOM_STATUS_HOLDS[no];
  1829 |         return {
  1830 |           no,type,elevator,catalogSource:'2026-08',checkout:occupiedSeed?'예정 미입력':'정보 없음',checkin:occupiedSeed?'투숙 중':'정보 없음',assignee:'미정',
  1831 |           catalogStatus:hold?'hold':'available',occupancy:occupiedSeed?'occupied':'vacant',cleaning:'idle',dataIssue:hold||null,
  1832 |           occupancySeedSource:occupiedSeed?'8월 객실현황 초기값':null,...(DEMO_ROOM_OVERRIDES[no]||{})
  1833 |         };
  1834 |       });
  1835 |       const cloneRoomRecord=room=>JSON.parse(JSON.stringify(room));
  1836 |       const ROOMS = ROOM_BASELINE.map(cloneRoomRecord);
  1837 |       function resetRoomCatalogState(){ROOMS.splice(0,ROOMS.length,...ROOM_BASELINE.map(cloneRoomRecord));}
  1838 |       function guestPolicyForRoom(roomNo) {
  1839 |         const room=ROOMS.find(item=>item.no===String(roomNo)),typeId=room?.type||'standard',type=ROOM_TYPES[typeId]||ROOM_TYPES.standard;
  1840 |         return {typeId,defaultGuestCount:type.defaultGuestCount,maxGuestCount:type.maxGuestCount};
  1841 |       }
  1842 |       function reservationGuestCount(reservation) {
  1843 |         const policy=guestPolicyForRoom(reservation?.room),value=Number(reservation?.guestCount);
  1844 |         return Number.isInteger(value)&&value>=1?value:policy.defaultGuestCount;
  1845 |       }
  1846 |       function guestCountLabel(value) { return Number.isInteger(Number(value))&&Number(value)>=1?`${Number(value)}명`:'인원 미기록'; }
  1847 |       function reservationHasExtraGuests(reservation) {
  1848 |         return !!reservation&&reservationGuestCount(reservation)>guestPolicyForRoom(reservation.room).defaultGuestCount;
  1849 |       }
  1850 |       function roomHasExtraGuests(no) {
  1851 |         const reservation=activeReservationsFor(state,String(no)).find(item=>!reservationRecordIsPast(item))||null;
  1852 |         return reservationHasExtraGuests(reservation);
  1853 |       }
  1854 |       const INITIAL_RESERVATIONS = Object.freeze([
  1855 |         {id:'reservation-demo-117',room:'117',checkInAt:'2026-08-14T16:00',checkOutAt:'2026-08-15T13:00',guestCount:2,source:'card',status:'active'},
  1856 |         {id:'reservation-demo-142',room:'142',checkInAt:'2026-08-14T16:00',checkOutAt:'2026-08-18T11:00',source:'card',status:'active'},
  1857 |         {id:'reservation-demo-350',room:'350',checkInAt:'2026-08-16T15:00',checkOutAt:'2026-08-17T11:00',source:'card',status:'active'},
  1858 |         {id:'reservation-demo-350-next',room:'350',checkInAt:'2026-08-17T15:00',checkOutAt:'2026-08-18T11:00',source:'grid',status:'active'},
  1859 |         {id:'reservation-demo-332',room:'332',checkInAt:'2026-08-16T16:00',checkOutAt:'2026-08-17T13:00',source:'card',status:'active'},
  1860 |         {id:'reservation-demo-639',room:'639',checkInAt:'2026-08-16T16:00',checkOutAt:'2026-08-17T11:00',source:'card',status:'active'},
  1861 |         {id:'reservation-demo-211',room:'211',checkInAt:'2026-08-16T16:00',checkOutAt:'2026-08-17T11:00',source:'card',status:'active'},
  1862 |         {id:'reservation-demo-516-a',room:'516',checkInAt:'2026-08-17T16:00',checkOutAt:'2026-08-18T11:00',source:'grid',status:'active'},
```

## long stay: `장기`

matches: 0

