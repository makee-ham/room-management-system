from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML_PATH = Path("WIREFRAME/index.html")
html = HTML_PATH.read_text(encoding="utf-8")


def replace_between(source: str, start_marker: str, end_marker: str, replacement: str, *, use_last: bool = False) -> str:
    start = source.rfind(start_marker) if use_last else source.find(start_marker)
    if start < 0:
        raise SystemExit(f"start marker not found: {start_marker[:90]}")
    end = source.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"end marker not found after {start_marker[:60]}: {end_marker[:90]}")
    return source[:start] + replacement + source[end:]


css = r'''

    /* Event-based notification center */
    .notification-toolbar { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; flex-wrap:wrap; }
    .notification-filter-group { display:flex; align-items:center; gap:6px; padding:4px; border:1px solid var(--line); border-radius:12px; background:var(--surface-soft); }
    .notification-filter-group .btn { min-height:38px; padding:7px 11px; }
    .notification-filter-group .btn[aria-pressed="true"] { color:#fff; background:var(--navy); border-color:var(--navy); }
    .notification-toolbar-actions { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
    .notification-list { display:grid; gap:9px; }
    .notification-card { position:relative; display:grid; grid-template-columns:12px minmax(0,1fr) auto; align-items:start; gap:12px; width:100%; min-height:92px; padding:14px; border:1px solid var(--line); border-radius:13px; color:var(--ink); background:#fff; text-align:left; }
    .notification-card:hover { border-color:var(--line-strong); background:#fbfdff; }
    .notification-card.unread { border-color:#bfd4e5; background:#f5faff; box-shadow:inset 3px 0 0 var(--blue); }
    .notification-card.urgent { border-color:#efb5ba; background:var(--red-soft); box-shadow:inset 3px 0 0 var(--red); }
    .notification-dot { width:9px; height:9px; margin-top:7px; border-radius:50%; background:transparent; }
    .notification-card.unread .notification-dot { background:var(--blue); box-shadow:0 0 0 4px rgba(40,108,168,.12); }
    .notification-card.urgent .notification-dot { background:var(--red); box-shadow:0 0 0 4px rgba(207,51,64,.12); }
    .notification-copy { min-width:0; }
    .notification-title-line { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:4px; }
    .notification-title-line strong { font-size:14px; }
    .notification-copy p { margin:0 0 7px; color:var(--muted); font-size:13px; overflow-wrap:anywhere; }
    .notification-meta { display:flex; align-items:center; gap:7px; flex-wrap:wrap; color:var(--subtle); font-size:12px; }
    .notification-chip { display:inline-flex; align-items:center; min-height:24px; padding:2px 7px; border-radius:999px; color:var(--navy); background:#eef3f7; font-size:11px; font-weight:800; }
    .notification-chip.action { color:#8a5400; background:var(--amber-soft); }
    .notification-chip.handled { color:#17644d; background:var(--green-soft); }
    .notification-cta { display:flex; align-items:center; gap:5px; align-self:center; color:var(--navy); font-size:12px; font-weight:800; white-space:nowrap; }
    .notification-empty { padding:26px 18px; border:1px dashed var(--line-strong); border-radius:13px; background:var(--surface-soft); text-align:center; }
    .notification-empty h3 { margin-bottom:5px; }
    .notification-empty p { margin:0; color:var(--muted); font-size:13px; }
    .notification-activity { margin-top:18px; padding-top:16px; border-top:1px solid var(--line); }
    .notification-activity h3 { margin-bottom:4px; }
    .notification-activity > p { margin-bottom:10px; color:var(--muted); font-size:12px; }
    .notification-activity-list { display:grid; gap:7px; }
    .notification-activity-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:12px; padding:10px 12px; border-radius:10px; background:var(--surface-soft); }
    .notification-activity-row strong { display:block; font-size:13px; }
    .notification-activity-row span { color:var(--muted); font-size:12px; }
    .notification-push-note { margin:0 0 12px; }

    @media (max-width: 720px) {
      .notification-toolbar { align-items:stretch; }
      .notification-filter-group { width:100%; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); }
      .notification-toolbar-actions { width:100%; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); }
      .notification-toolbar-actions .btn { width:100%; }
      .notification-card { grid-template-columns:10px minmax(0,1fr); padding:13px 12px; }
      .notification-cta { grid-column:2; justify-self:start; }
      .notification-activity-row { grid-template-columns:1fr; gap:3px; }
    }
'''
if "/* Event-based notification center */" not in html:
    if "</style>" not in html:
        raise SystemExit("style closing tag missing")
    html = html.replace("</style>", css + "\n  </style>", 1)

notification_helpers = r'''      const NOTIFICATION_SCHEMA_VERSION=1;
      const NOTIFICATION_BUNDLE_WINDOW_MINUTES=10;
      const NOTIFICATION_CATEGORY_LABELS={inspection:'청소 검수',assignment:'청소 배정',cancellation:'담당 취소',issue:'현장 문제',delay:'마감·지연',availability:'근무 가능일',complaint:'컴플레인·이의',conflict:'충돌·동기화',payroll:'주급',general:'업무 업데이트'};

      function notificationAudienceKey(role=state.role,maidId=role==='maid'?signedInMaidId():null){return role==='admin'?'admin':`maid:${maidId||signedInMaidId()}`;}
      function notificationPushKey(role=state.role,maidId=role==='maid'?signedInMaidId():null){return notificationAudienceKey(role,maidId);}
      function notificationSeedEvents(){return [
        {id:'notification-seed-admin-inspection',title:'639호 청소 검수 요청',time:'10:18',createdAt:'2026-08-15 10:18',detail:'이서연이 전체 청소 제출을 완료했습니다.',roomId:'639',maidIds:[],notify:true,audience:['admin'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-inspection'},groupKey:'admin:inspection:639',readBy:[]},
        {id:'notification-seed-admin-cancel',title:'332호 담당 취소 요청',time:'10:07',createdAt:'2026-08-15 10:07',detail:'김민지1 · 투숙객이 객실에 머물고 있음 · 결정 전 담당 유지',roomId:'332',maidIds:['m1'],notify:true,audience:['admin'],category:'cancellation',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'cancel-review'},groupKey:'admin:cancellation:332',readBy:[]},
        {id:'notification-seed-admin-availability',title:'다음 주 가능일 미제출 2명',time:'09:30',createdAt:'2026-08-15 09:30',detail:'마감 전 한 번만 묶어 알립니다.',maidIds:[],notify:true,audience:['admin'],category:'availability',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-workforce'},groupKey:'admin:availability:next-week',readBy:[]},
        {id:'notification-seed-admin-handled',title:'350호 미배정 청소 조치 완료',time:'08:55',createdAt:'2026-08-15 08:55',detail:'담당 지정 완료 · 사건 기록 보존',roomId:'350',maidIds:[],notify:true,audience:['admin'],category:'assignment',priority:'normal',push:false,actionRequired:false,status:'handled',target:{action:'go-cleaning-assignment',data:{day:'today'}},groupKey:'admin:assignment:350',readBy:['admin']},
        {id:'notification-seed-maid-correction',title:'350호 보완 청소 요청',time:'10:05',createdAt:'2026-08-15 10:05',detail:'욕실 거울과 TV 전원 사진을 다시 확인해 주세요.',roomId:'350',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'inspection',priority:'high',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:inspection:350',readBy:[]},
        {id:'notification-seed-maid-reminder',title:'332호 청소 시작 60분 전',time:'09:55',createdAt:'2026-08-15 09:55',detail:'오늘 10:55 시작 예정 · 예정 업무를 확인하세요.',roomId:'332',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'delay',priority:'normal',push:true,actionRequired:false,status:'open',target:{action:'go-my'},groupKey:'maid:m1:delay:332',readBy:[]},
        {id:'notification-seed-maid-order',title:'117호 청소 순서 변경',time:'09:45',createdAt:'2026-08-15 09:45',detail:'2번째에서 1번째 청소로 변경되었습니다.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
        {id:'notification-seed-maid-assignment',title:'117호 퇴실 청소 배정',time:'09:40',createdAt:'2026-08-15 09:40',detail:'오늘 13:00까지 완료해 주세요.',roomId:'117',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'assignment',priority:'normal',push:true,actionRequired:true,status:'open',target:{action:'go-my'},groupKey:'maid:m1:assignment:117',readBy:[]},
        {id:'notification-seed-maid-payroll',title:'이번 주 주급 정산 확정',time:'09:20',createdAt:'2026-08-15 09:20',detail:'객실별 승인 합계가 주급 내역에 반영되었습니다.',maidIds:['m1'],notify:true,audience:['maid:m1'],category:'payroll',priority:'normal',push:false,pushOptional:true,actionRequired:false,status:'handled',target:{action:'go-maid-pay'},groupKey:'maid:m1:payroll:2026-08-10',readBy:['maid:m1']}
      ];}
      function nextNotificationEventId(){state.notificationSequence=Number(state.notificationSequence||0)+1;return `notification-${state.selectedDate||'demo'}-${state.time?.replace(':','')||'0000'}-${state.notificationSequence}`;}
      function notificationMinuteValue(event){const text=String(event?.createdAt||`${state.selectedDate||'2026-08-15'} ${event?.time||'00:00'}`),match=text.match(/(\d{4})-(\d{2})-(\d{2})[^\d]?(\d{2}):(\d{2})/);if(!match)return 0;return Math.floor(Date.UTC(Number(match[1]),Number(match[2])-1,Number(match[3]),Number(match[4]),Number(match[5]))/60000);}
      function notificationRoomFromText(title,detail,roomId=null){if(roomId)return String(roomId);return String(title||'').match(/(\d{3})호/)?.[1]||String(detail||'').match(/(\d{3})호/)?.[1]||null;}
      function notificationMaidIdsForRoom(roomId){if(!roomId)return [];const submission=typeof currentSubmission==='function'?currentSubmission(String(roomId)):null,attempt=typeof currentAttemptId==='function'?state.cleaningAttempts?.[currentAttemptId(String(roomId))]:null,assignee=ROOMS.find(room=>room.no===String(roomId))?.assignee,assigneeId=MAIDS.find(maid=>maid.name===assignee)?.id;return [...new Set([submission?.performerId,attempt?.performerId,assigneeId].filter(id=>MAIDS.some(maid=>maid.id===id)))];}
      function notificationMaidIdsForComplaint(){const item=(state.complaints||[]).find(entry=>!entry.deleted&&['unread','ruled','objected'].includes(entry.responseStatus))||(state.complaints||[])[0],maidId=MAIDS.find(maid=>maid.name===item?.maid)?.id;return maidId?[maidId]:[];}
      function notificationCategoryFromText(text){if(/검수|전체 제출|보완|재청소/.test(text))return 'inspection';if(/배정|담당 변경|순서 변경|청소 취소 통보/.test(text))return 'assignment';if(/취소 요청|취소 승인|취소 거절|담당 취소/.test(text))return 'cancellation';if(/입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text))return 'issue';if(/마감|지연|미시작|60분 전|시작 시각/.test(text))return 'delay';if(/가능일/.test(text))return 'availability';if(/컴플레인|이의|판정/.test(text))return 'complaint';if(/충돌|동기화 실패|저장 충돌|오래된 데이터/.test(text))return 'conflict';if(/주급|지급|정산/.test(text))return 'payroll';return 'general';}
      function notificationTargetFor(category,recipientRole,roomId,options={}){if(options.target)return options.target;if(recipientRole==='admin'){if(category==='inspection')return {action:'go-inspection'};if(category==='assignment'||category==='delay')return {action:'go-cleaning-assignment',data:{day:'today'}};if(category==='cancellation')return {action:'cancel-review'};if(category==='issue'||category==='conflict')return roomId?{action:'room-detail',id:roomId}:{action:'alerts'};if(category==='availability')return {action:'go-workforce'};if(category==='complaint')return {action:'complaint-detail'};if(category==='payroll')return {action:'go-payroll'};return {action:'alerts'};}if(category==='payroll')return {action:'go-maid-pay'};if(category==='availability')return {action:'go-schedule'};if(category==='complaint')return {action:'complaint-detail'};return {action:'go-my'};}
      function notificationPolicyForEvent(title,detail,options={}){
        if(options.notification===false)return null;
        const actorRole=options.actorRole||state.role||'system',actorMaidId=options.actorMaidId||(actorRole==='maid'?signedInMaidId():null),text=`${title||''} ${detail||''}`,roomId=notificationRoomFromText(title,detail,options.roomId),requestedMaidIds=[...new Set((options.maidIds||[]).filter(id=>MAIDS.some(maid=>maid.id===id)))],category=options.category||notificationCategoryFromText(text);
        if(options.notification&&typeof options.notification==='object'){
          const explicit=options.notification,audience=[...new Set(explicit.audience||[])];if(!audience.length)return null;const recipientRole=audience[0]==='admin'?'admin':'maid';return {...explicit,audience,category:explicit.category||category,roomId,priority:explicit.priority||'normal',push:explicit.push!==false,actionRequired:explicit.actionRequired!==false,status:explicit.status||'open',target:notificationTargetFor(explicit.category||category,recipientRole,roomId,explicit),groupKey:explicit.groupKey||`${audience.join('|')}:${explicit.category||category}:${roomId||'general'}`,actorRole,actorMaidId};
        }
        if(actorRole==='maid'){
          if(/청소 전체 제출|검수 요청|재검수 요청/.test(text))return {audience:['admin'],category:'inspection',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('inspection','admin',roomId),groupKey:`admin:inspection:${roomId||'general'}`,actorRole,actorMaidId};
          if(/담당 취소 요청|취소 요청/.test(text))return {audience:['admin'],category:'cancellation',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('cancellation','admin',roomId),groupKey:`admin:cancellation:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
          if(/이의 제출|입실 불가|투숙객|도어락|파손|분실|비품 부족|안전 문제|문제 보고/.test(text)){const adminCategory=/이의/.test(text)?'complaint':'issue';return {audience:['admin'],category:adminCategory,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(adminCategory,'admin',roomId),groupKey:`admin:${adminCategory}:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};}
          if(/시작 지연|완료 지연|마감 초과/.test(text))return {audience:['admin'],category:'delay',roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor('delay','admin',roomId),groupKey:`admin:delay:${roomId||actorMaidId||'general'}`,actorRole,actorMaidId};
          return null;
        }
        if(actorRole==='admin'){
          let targetMaidIds=[...requestedMaidIds];
          if(/전체 제출 승인|검수 승인|전체 제출 반려|보완 청소|재청소/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForRoom(roomId);
          if(/컴플레인 판정|이의 답변/.test(text)&&!targetMaidIds.length)targetMaidIds=notificationMaidIdsForComplaint();
          const maidNotice=/^내 |통보|안내|배정|담당 변경|순서 변경|취소|시작 시각|보류|시작 가능|전체 제출 승인|검수 승인|전체 제출 반려|보완|재청소|컴플레인 판정|이의 답변|주급|지급|마감|지연|비활성/.test(text);
          if(targetMaidIds.length&&maidNotice){const audience=targetMaidIds.map(id=>`maid:${id}`),informational=/승인|종결|확정|지급 완료|처리 결과|비활성 완료/.test(text)&&!/보완|재청소|지연|마감/.test(text),priority=/긴급|보완|재청소|반려|지연|마감|취소/.test(text)?'high':'normal',pushOptional=category==='payroll'&&/정산 확정/.test(text);return {audience,category,roomId,priority,push:!pushOptional,pushOptional,actionRequired:!informational,status:informational?'handled':'open',target:notificationTargetFor(category,'maid',roomId),groupKey:`${audience.join('|')}:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
          if(/미배정.*남|미배정 청소|가능일.*미제출|동기화 실패|저장 충돌|주급.*오류|지급.*예외/.test(text)){return {audience:['admin'],category,roomId,priority:'high',push:true,actionRequired:true,status:'open',target:notificationTargetFor(category,'admin',roomId),groupKey:`admin:${category}:${roomId||'general'}`,actorRole,actorMaidId};}
          return null;
        }
        return null;
      }
      function normalizeNotificationEvent(event,index=0){if(!event||typeof event!=='object')return event;event.id=event.id||`event-${index}-${String(event.time||'0000').replace(/\D/g,'')}`;event.time=event.time||state.time;event.createdAt=event.createdAt||`${state.selectedDate||'2026-08-15'} ${event.time}`;event.maidIds=Array.isArray(event.maidIds)?event.maidIds:[];event.audience=Array.isArray(event.audience)?event.audience:[];event.readBy=Array.isArray(event.readBy)?event.readBy:[];event.notify=event.notify===true;if(event.notify){event.category=event.category||notificationCategoryFromText(`${event.title} ${event.detail}`);event.priority=event.priority||'normal';event.status=event.status||'open';event.actionRequired=event.actionRequired!==false;event.groupKey=event.groupKey||`${event.audience.join('|')}:${event.category}:${event.roomId||'general'}`;event.target=event.target||notificationTargetFor(event.category,event.audience[0]==='admin'?'admin':'maid',event.roomId);}return event;}
      function ensureNotificationState(){state.events=Array.isArray(state.events)?state.events:[];state.notificationPushSettings=state.notificationPushSettings&&typeof state.notificationPushSettings==='object'?state.notificationPushSettings:{};state.notificationFilter=['all','unread','action'].includes(state.notificationFilter)?state.notificationFilter:'all';if(state.notificationSchemaVersion!==NOTIFICATION_SCHEMA_VERSION){const existingIds=new Set(state.events.map(event=>event?.id).filter(Boolean)),seeds=notificationSeedEvents().filter(event=>!existingIds.has(event.id));state.events=[...seeds,...state.events];state.notificationSchemaVersion=NOTIFICATION_SCHEMA_VERSION;}state.notificationSequence=Number(state.notificationSequence||state.events.length);state.events.forEach(normalizeNotificationEvent);return state.events;}
      function notificationEventsForKey(key=notificationAudienceKey()){ensureNotificationState();return state.events.filter(event=>event.notify&&event.audience.includes(key)).sort((left,right)=>notificationMinuteValue(right)-notificationMinuteValue(left));}
      function notificationBundlesForKey(key=notificationAudienceKey()){
        const bundles=[];for(const event of notificationEventsForKey(key)){const stamp=notificationMinuteValue(event),groupKey=event.groupKey||event.id,existing=bundles.find(bundle=>bundle.groupKey===groupKey&&Math.abs(bundle.latestStamp-stamp)<=NOTIFICATION_BUNDLE_WINDOW_MINUTES);if(existing){existing.events.push(event);existing.eventIds.push(event.id);existing.bundleCount+=1;existing.unread=existing.unread||!event.readBy.includes(key);existing.actionRequired=existing.actionRequired||event.actionRequired&&event.status!=='handled';existing.latestStamp=Math.max(existing.latestStamp,stamp);if(stamp>=notificationMinuteValue(existing.latest)){existing.latest=event;existing.title=event.title;existing.detail=event.detail;}}else bundles.push({id:event.id,groupKey,latest:event,events:[event],eventIds:[event.id],bundleCount:1,title:event.title,detail:event.detail,latestStamp:stamp,unread:!event.readBy.includes(key),actionRequired:event.actionRequired&&event.status!=='handled'});}return bundles.sort((left,right)=>right.latestStamp-left.latestStamp);
      }
      function notificationUnreadCount(key=notificationAudienceKey()){return notificationBundlesForKey(key).filter(bundle=>bundle.unread).length;}
      function markNotificationRead(ids,key=notificationAudienceKey()){ensureNotificationState();const targetIds=new Set(Array.isArray(ids)?ids:[ids]);state.events.forEach(event=>{if(targetIds.has(event.id)&&event.notify&&!event.readBy.includes(key))event.readBy.push(key);});}
      function markAllNotificationsRead(key=notificationAudienceKey()){notificationEventsForKey(key).forEach(event=>{if(!event.readBy.includes(key))event.readBy.push(key);});}
      function notificationPushEnabled(key=notificationPushKey()){ensureNotificationState();if(!(key in state.notificationPushSettings))state.notificationPushSettings[key]=!!state.notificationsEnabled;return !!state.notificationPushSettings[key];}
      function setNotificationPushEnabled(enabled,key=notificationPushKey()){ensureNotificationState();state.notificationPushSettings[key]=!!enabled;state.notificationsEnabled=!!enabled;}
      function queueForegroundNotification(event){if(!event?.notify||!event.push)return;const currentKey=notificationAudienceKey(),actorKey=event.actorRole==='admin'?'admin':event.actorRole==='maid'&&event.actorMaidId?`maid:${event.actorMaidId}`:null;if(!event.audience.includes(currentKey)||actorKey===currentKey||!notificationPushEnabled(currentKey))return;event.pushState='foreground';event.pushDeliveredAt=`${state.selectedDate} ${state.time}`;if(typeof Notification!=='undefined'&&Notification.permission==='granted'){try{new Notification(event.title,{body:event.detail||'CASTLE THE ART 업무 업데이트'});}catch(error){event.pushState='in-app-fallback';}}}
      function resolveRelatedAdminNotification(title,roomId){if(state.role!=='admin'||!/승인|반려|거절|종결|처리 완료|취소 승인|취소 거절/.test(String(title||'')))return;const category=/취소/.test(title)?'cancellation':/컴플레인|이의|판정/.test(title)?'complaint':'inspection';notificationEventsForKey('admin').forEach(event=>{if(event.category===category&&(!roomId||event.roomId===roomId)&&event.status!=='handled'){event.status='handled';event.actionRequired=false;event.resolvedAt=`${state.selectedDate} ${state.time}`;}});}
      function appendEvent(title,detail,options={}){
        ensureNotificationState();const maidIds=[...new Set((options.maidIds||[]).filter(id=>MAIDS.some(maid=>maid.id===id)))],roomId=notificationRoomFromText(title,detail,options.roomId),attemptId=options.attemptId||null,dedupeKey=options.dedupeKey||null;if(dedupeKey){const existing=(state.events||[]).find(event=>event.dedupeKey===dedupeKey);if(existing)return existing;}
        resolveRelatedAdminNotification(title,roomId);const actorRole=options.actorRole||state.role||'system',actorMaidId=options.actorMaidId||(actorRole==='maid'?signedInMaidId():null),policy=notificationPolicyForEvent(title,detail,{...options,maidIds,roomId,actorRole,actorMaidId}),event={id:nextNotificationEventId(),title,time:state.time,createdAt:`${state.selectedDate} ${state.time}`,detail,maidIds:[...maidIds],roomId:roomId||null,attemptId,actorRole,actorMaidId,...(dedupeKey?{dedupeKey}:{})};
        if(policy){Object.assign(event,{notify:true,audience:policy.audience,category:policy.category,priority:policy.priority,push:policy.push,pushOptional:!!policy.pushOptional,actionRequired:policy.actionRequired,status:policy.status,target:policy.target,groupKey:policy.groupKey,readBy:[]});for(const key of policy.audience){if(key.startsWith('maid:')){const id=key.slice(5);if(!event.maidIds.includes(id))event.maidIds.push(id);}}}else Object.assign(event,{notify:false,audience:[],readBy:[]});state.events.unshift(event);queueForegroundNotification(event);return event;
      }
'''

append_start = "      function appendEvent(title, detail, {maidIds=[],roomId=null,attemptId=null,dedupeKey=null}={}) {"
append_end = "      function durableLedgerSnapshot(targetState=state) {"
if append_start not in html:
    raise SystemExit("appendEvent legacy block not found")
html = replace_between(html, append_start, append_end, notification_helpers, use_last=False)

notification_ui = r'''      function notificationCategoryLabel(category){return NOTIFICATION_CATEGORY_LABELS[category]||NOTIFICATION_CATEGORY_LABELS.general;}
      function notificationFilterLabel(filter){return filter==='unread'?'안 읽음':filter==='action'?'처리 필요':'전체';}
      function renderNotificationListMarkup({key=notificationAudienceKey(),filter=state.notificationFilter,includeActivity=true}={}){
        ensureNotificationState();const bundles=notificationBundlesForKey(key),filtered=bundles.filter(bundle=>filter==='unread'?bundle.unread:filter==='action'?bundle.actionRequired:true),activity=(state.events||[]).filter(event=>!event.notify).slice(0,5),pushEnabled=notificationPushEnabled(key),filterButtons=[['all','전체'],['unread','안 읽음'],['action','처리 필요']].map(([value,label])=>`<button class="btn btn-ghost" type="button" data-action="notification-filter" data-filter="${value}" aria-pressed="${filter===value}">${label}${value==='unread'?` ${notificationUnreadCount(key)}`:''}</button>`).join('');
        const cards=filtered.map(bundle=>{const event=bundle.latest,priority=event.priority==='urgent'?'urgent':'',status=event.status==='handled'&&!bundle.actionRequired?'처리 완료':bundle.actionRequired?'확인 필요':'안내',statusClass=status==='처리 완료'?'handled':bundle.actionRequired?'action':'',bundleText=bundle.bundleCount>1?` · 업데이트 ${bundle.bundleCount}건`:'';return `<button class="notification-card ${bundle.unread?'unread':''} ${priority}" type="button" data-action="notification-open" data-event-id="${esc(event.id)}" data-event-ids="${esc(bundle.eventIds.join(','))}" data-notification-card="${esc(event.category)}"><span class="notification-dot" aria-hidden="true"></span><span class="notification-copy"><span class="notification-title-line"><strong>${esc(event.title)}</strong>${bundle.bundleCount>1?`<span class="notification-chip">업데이트 ${bundle.bundleCount}건</span>`:''}</span><p>${esc(event.detail||'업무 상태가 변경되었습니다.')}</p><span class="notification-meta"><span>${esc(event.time)}</span><span>${esc(notificationCategoryLabel(event.category))}</span><span class="notification-chip ${statusClass}">${status}</span>${event.pushOptional?'<span>푸시 선택</span>':event.push?'<span>푸시 대상</span>':'<span>앱 내 기록</span>'}${bundleText}</span></span><span class="notification-cta">관련 화면 ${icon('chevronRight','icon-sm')}</span></button>`;}).join('');
        const activityMarkup=includeActivity?`<section class="notification-activity"><h3>최근 활동 기록</h3><p>정상 청소 시작·사진 업로드·가능일 제출·관리자 직접 저장처럼 푸시하지 않는 활동입니다.</p><div class="notification-activity-list">${activity.length?activity.map(event=>`<div class="notification-activity-row"><span><strong>${esc(event.title)}</strong><span>${esc(event.detail||'')}</span></span><span>${esc(event.time||'')}</span></div>`).join(''):'<div class="notification-empty"><p>기록된 일반 활동이 없습니다.</p></div>'}</div></section>`:'';
        return `<div class="notification-toolbar"><div class="notification-filter-group" role="group" aria-label="알림 필터">${filterButtons}</div><div class="notification-toolbar-actions"><button class="btn btn-outline" type="button" data-action="notification-mark-all-read" ${notificationUnreadCount(key)?'':'disabled'}>모두 읽음</button><button class="btn btn-outline" type="button" data-action="notification-toggle-push" aria-pressed="${pushEnabled}">${pushEnabled?'푸시 켜짐':'푸시 꺼짐'}</button></div></div><div class="notice notice-info notification-push-note"><div><strong>앱 내 알림은 항상 보존됩니다.</strong><br>푸시는 지금 확인하거나 행동해야 하는 상태 변경만 대상으로 하며, 이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다.</div></div><div class="notification-list" data-notification-list="${esc(key)}" data-filter="${esc(filter)}">${cards||`<section class="notification-empty"><h3>${notificationFilterLabel(filter)} 알림이 없습니다</h3><p>새 상태 변경이 생기면 발생 시각 순서로 표시됩니다.</p></section>`}</div>${activityMarkup}`;
      }
      function openNotificationCenter(trigger=document.activeElement){const roleLabel=state.role==='admin'?'관리자 알림':'내 알림';showModal({title:roleLabel,subtitle:'업데이트를 시간순으로 보존하고 관련 업무 화면으로 바로 연결합니다.',large:true,trigger,body:renderNotificationListMarkup(),closeLabel:'닫기'});}
      function openAlerts(){openNotificationCenter(document.activeElement);}

'''
html = replace_between(html, "      function openAlerts() {", "      function openPublishConfirm() {", notification_ui + "      function openPublishConfirm() {", use_last=False)

open_action_replacement = r'''      function openActionAlerts(trigger=document.activeElement){openNotificationCenter(trigger);}

'''
html = replace_between(html, "      function openActionAlerts(trigger=document.activeElement) {", "      function adminAuditSummary(detail) {", open_action_replacement + "      function adminAuditSummary(detail) {", use_last=False)

maid_alert_replacement = r'''      function renderMaidAlerts(){
        const key=notificationAudienceKey('maid',signedInMaidId());ensureNotificationState();return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section><div class="section-head"><div><h2>알림</h2><p class="audit-note">배정·검수 결과·취소·마감·주급 업데이트를 시간순으로 확인합니다.</p></div>${statusBadge(`안 읽음 ${notificationUnreadCount(key)}건`,notificationUnreadCount(key)?'blue':'neutral')}</div><div class="tab-panel">${renderNotificationListMarkup({key,filter:state.notificationFilter,includeActivity:true})}</div></section></div>`;
      }

'''
html = replace_between(html, "      function renderMaidAlerts() {", "      function renderMaidPay() {", maid_alert_replacement + "      function renderMaidPay() {", use_last=False)

final_topbar = r'''      function renderTopbar() {
        const alertCount=notificationUnreadCount(notificationAudienceKey()),countMarkup=alertCount?`<span class="count-dot">${alertCount}</span>`:'';
        return `<header class="topbar"><div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 ${state.selectedDate.replaceAll('-','.')} ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div><div class="topbar-actions"><button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기 · 안 읽음 ${alertCount}건">${icon('bell')}${countMarkup}</button><button class="btn btn-outline" type="button" data-action="switch-role" aria-label="${state.role==='admin'?'메이드 보기':'관리자 보기'}">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button></div></header>`;
      }

'''
final_topbar_start = "      function renderTopbar() {\n        const alertCount=state.role==='admin'?6:(state.events||[]).filter(event=>event.maidIds?.includes(signedInMaidId())).length;"
if final_topbar_start not in html:
    raise SystemExit("final renderTopbar block not found")
html = replace_between(html, final_topbar_start, "      function dateObject(value=state.selectedDate) {", final_topbar + "      function dateObject(value=state.selectedDate) {", use_last=True)

action_marker = "        else if(a==='alert-link'){closeModal();openDetail(el.dataset.type,el.dataset.id,el);}"
notification_actions = r'''        else if(a==='notification-filter'){const filter=el.dataset.filter;if(!['all','unread','action'].includes(filter))return;state.notificationFilter=filter;openNotificationCenter(el);return;}
        else if(a==='notification-mark-all-read'){markAllNotificationsRead();render();openNotificationCenter(el);toast('현재 계정의 알림을 모두 읽음 처리했습니다.');return;}
        else if(a==='notification-toggle-push'){const enabled=!notificationPushEnabled();setNotificationPushEnabled(enabled);appendEvent('기기 푸시 설정 변경',enabled?'현재 계정 푸시 켜짐 · 앱 내 알림은 항상 유지':'현재 계정 푸시 꺼짐 · 앱 내 알림은 항상 유지',{notification:false});render();openNotificationCenter(el);toast(enabled?'행동이 필요한 업데이트의 푸시를 켰습니다.':'푸시를 껐습니다. 앱 내 알림은 계속 남습니다.');return;}
        else if(a==='notification-open'){const ids=String(el.dataset.eventIds||el.dataset.eventId||'').split(',').filter(Boolean),eventId=el.dataset.eventId||ids[0],event=(state.events||[]).find(item=>item.id===eventId);markNotificationRead(ids);closeModal();render();if(event)requestAnimationFrame(()=>dispatchNotificationTarget(event));return;}
        else if(a==='alert-link'){closeModal();openDetail(el.dataset.type,el.dataset.id,el);}'''
if action_marker not in html:
    raise SystemExit("legacy alert-link action marker not found")
html = html.replace(action_marker, notification_actions, 1)

# Add target dispatcher immediately before the delegated click handler.
click_handler_marker = "      document.addEventListener('click',e=>{"
dispatcher = r'''      function dispatchNotificationTarget(event){
        const target=event?.target||{},action=target.action||'alerts',button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.click();button.remove();
      }

'''
if click_handler_marker not in html:
    raise SystemExit("delegated click handler marker not found")
html = html.replace(click_handler_marker, dispatcher + click_handler_marker, 1)

permission_marker = "state.notificationsEnabled=true;appendEvent('기기 알림 허용 상태 변경','정적 데모 · 앱 내부 알림은 항상 유지');"
if permission_marker in html:
    html = html.replace(permission_marker, "setNotificationPushEnabled(true);appendEvent('기기 알림 허용 상태 변경','정적 데모 · 앱 내부 알림은 항상 유지',{notification:false});", 1)

# Documentation.
policy_path = Path("DOCS/19_EVENT_NOTIFICATION_POLICY.md")
policy_path.write_text("""# 이벤트 기반 알림·푸시 정책

## 원칙

- 앱 내 알림은 푸시 수신 여부와 관계없이 시간순으로 보존한다.
- 알림은 읽음·안 읽음, 처리 필요·처리 완료, 관련 객실/업무, 발생 시각, 바로가기를 가진다.
- 해결된 사건도 삭제하지 않고 처리 완료 상태로 남긴다.
- 같은 객실·같은 범주의 업데이트가 10분 안에 이어지면 한 묶음으로 표시한다.
- 사용자가 직접 수행한 정상 행동은 자기 푸시를 만들지 않고 토스트와 일반 활동 기록만 남긴다.

## 관리자 푸시

검수·재검수 요청, 담당 취소 요청, 입실 불가·투숙객 체류·도어락·파손·분실·비품·안전 문제, 시작·완료 지연, 미배정 묶음, 컴플레인·판정 이의, 저장 충돌·동기화 실패, 가능일 미제출 마감 임박, 주급 오류·지급 예외를 보낸다.

정상 청소 시작, 사진 한 장 업로드, 정상 가능일 제출, 관리자의 직접 배정 저장, 정상 동기화, 관리자의 직접 검수 승인은 관리자 자기 푸시 대상이 아니다.

## 메이드 푸시

신규 배정·배정 변경·취소, 긴급 청소, 보완 청소, 재검수 승인, 담당 취소 결정, 문제·컴플레인·이의 답변, 시작 60분 전과 마감 지연, 가능일 마감 임박, 주급 확정·지급·예외를 보낸다. 주급 정산 확정은 앱 내 알림이 기본이며 푸시는 선택 항목이다.

청소 시작, 사진 업로드, 검수 요청, 가능일 제출, 담당 취소 요청은 본인이 방금 한 행동이므로 자기 푸시를 만들지 않는다.

## 정적 데모 범위

이 저장소의 단일 HTML 데모는 앱 내 알림, 읽음 상태, 역할별 수신 범위, 묶음, 딥링크와 브라우저가 열려 있는 동안의 포그라운드 알림 메타데이터를 검증한다. 실제 백그라운드·모바일 푸시에는 서비스 워커, 기기별 푸시 토큰, 서버 발송·재시도·수신 거부 동기화 계층이 별도로 필요하다.
""", encoding="utf-8")

qa_path = Path("WIREFRAME/QA.md")
qa = qa_path.read_text(encoding="utf-8").rstrip()
qa += """

## 2026-08-25 · 이벤트 기반 알림 센터

### 변경

- 관리자·메이드의 정적인 `알림 현황`을 역할별 시간순 이벤트 센터로 교체했다.
- 전체 / 안 읽음 / 처리 필요 필터, 개별·전체 읽음 처리, 상단 미확인 배지, 처리 완료 보존, 관련 화면 바로가기를 추가했다.
- 같은 객실·범주의 10분 이내 업데이트는 한 묶음으로 표시한다.
- 청소 시작·사진 업로드·정상 가능일 제출·관리자 직접 저장·정상 동기화는 푸시하지 않고 활동 기록에만 남긴다.
- 검수 요청·보완, 배정·취소, 지연, 가능일 마감, 컴플레인·이의, 충돌·오류, 주급 예외는 승인된 역할별 정책으로 분류한다.

### 검증

- 관리자와 메이드가 서로의 알림을 보지 않는지 확인한다.
- 117호 배정·순서 변경 두 건이 한 묶음으로 표시되는지 확인한다.
- 알림 클릭 후 읽지 않은 배지가 감소하고 검수·내 업무 등 관련 화면으로 이동하는지 확인한다.
- 푸시를 꺼도 앱 내 알림 목록과 읽음 상태가 유지되는지 확인한다.
- 메이드의 청소 시작은 자기 알림을 만들지 않고, 전체 제출은 관리자 알림을 만드는지 확인한다.
- 390px·1440px에서 가로 넘침, 콘솔·런타임 오류가 없는지 확인한다.

### 운영 구현 주의

정적 데모는 브라우저가 열린 동안의 알림 동작까지만 표현한다. 실제 백그라운드·모바일 푸시는 서비스 워커·푸시 토큰·서버 발송 계층이 필요하다.
"""
qa_path.write_text(qa + "\n", encoding="utf-8")

readme_path = Path("WIREFRAME/README.md")
readme = readme_path.read_text(encoding="utf-8").rstrip()
readme += """

## 이벤트 기반 알림 센터 (2026-08-25)

- 관리자와 메이드는 본인에게 필요한 상태 변경만 시간순으로 받는다.
- 앱 내 알림은 푸시 설정과 무관하게 보존되며, 읽음·처리 상태와 관련 화면 바로가기를 제공한다.
- 정상 활동은 최근 활동 기록에 남기고, 행동이 필요한 상태 변경만 푸시 대상으로 분류한다.
- 같은 객실의 10분 이내 업데이트는 하나로 묶는다.
- 실제 백그라운드·모바일 푸시는 정적 데모 범위 밖이며 서비스 워커·기기 토큰·서버 발송 계층이 필요하다. 자세한 정책은 `DOCS/19_EVENT_NOTIFICATION_POLICY.md`를 따른다.
"""
readme_path.write_text(readme + "\n", encoding="utf-8")

# Permanent workspace checks.
checker_path = Path("scripts/check-workspace.mjs")
checker = checker_path.read_text(encoding="utf-8").rstrip()
checker += r'''

const notificationContracts = [
  'const NOTIFICATION_SCHEMA_VERSION=1',
  'function notificationPolicyForEvent(',
  'function notificationBundlesForKey(',
  'function notificationUnreadCount(',
  'function markNotificationRead(',
  'function markAllNotificationsRead(',
  'function renderNotificationListMarkup(',
  "data-action=\"notification-open\"",
  "data-action=\"notification-mark-all-read\"",
  "data-action=\"notification-toggle-push\"",
  'same 객실',
  '서비스 워커',
  "const alertCount=notificationUnreadCount(notificationAudienceKey())",
  "if(actorRole==='maid')",
  "if(/청소 전체 제출|검수 요청|재검수 요청/.test(text))",
  "appendEvent('기기 푸시 설정 변경'",
];
for (const contract of notificationContracts) {
  if (!html.includes(contract)) throw new Error(`Event notification contract missing: ${contract}`);
}
const notificationOpenStart = html.indexOf('function openAlerts()');
const notificationOpenEnd = html.indexOf('function openPublishConfirm()', notificationOpenStart);
const notificationOpenSource = html.slice(notificationOpenStart, notificationOpenEnd);
if (notificationOpenStart < 0 || notificationOpenEnd < 0) throw new Error('Notification center source could not be isolated.');
for (const forbidden of [
  "const items=[['350호 입실 미준비'",
  "title:'알림 현황 · 데모'",
  "'동기화',state.network",
  "검수 대기',`${pendingInspections}건",
]) {
  if (notificationOpenSource.includes(forbidden)) throw new Error(`Legacy static alert summary remains: ${forbidden}`);
}
const actionAlertStart = html.indexOf('function openActionAlerts(');
const actionAlertEnd = html.indexOf('function adminAuditSummary(', actionAlertStart);
const actionAlertSource = html.slice(actionAlertStart, actionAlertEnd);
if (!actionAlertSource.includes('openNotificationCenter(trigger)')) throw new Error('Action alert entry point does not use the unified event center.');
if (actionAlertSource.includes('최신 상태') || actionAlertSource.includes('0건')) throw new Error('Static zero/sync alert rows remain in action alert entry point.');
console.log('Event notification center static contracts: passed');
'''
checker_path.write_text(checker + "\n", encoding="utf-8")

HTML_PATH.write_text(html, encoding="utf-8")

digest = hashlib.sha256(HTML_PATH.read_bytes()).hexdigest()
sums_path = Path("SHA256SUMS.txt")
lines = sums_path.read_text(encoding="utf-8").splitlines()
updated = False
for index, line in enumerate(lines):
    if line.endswith("  WIREFRAME/index.html"):
        lines[index] = f"{digest}  WIREFRAME/index.html"
        updated = True
        break
if not updated:
    raise SystemExit("WIREFRAME/index.html checksum entry missing")
sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

manifest_path = Path("manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["version"] = "2026-08-25-event-notification-center"
manifest["generated_at_kst"] = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
manifest.setdefault("sha256", {})["WIREFRAME/index.html"] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
