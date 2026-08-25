from pathlib import Path

path = Path('.github/automation/apply-event-notification-center.py')
text = path.read_text(encoding='utf-8')
marker = """        if(policy){Object.assign(event,{notify:true,audience:policy.audience,category:policy.category,priority:policy.priority,push:policy.push,pushOptional:!!policy.pushOptional,actionRequired:policy.actionRequired,status:policy.status,target:policy.target,groupKey:policy.groupKey,readBy:[]});for(const key of policy.audience){if(key.startsWith('maid:')){const id=key.slice(5);if(!event.maidIds.includes(id))event.maidIds.push(id);}}}else Object.assign(event,{notify:false,audience:[],readBy:[]});state.events.unshift(event);queueForegroundNotification(event);return event;
      }
'''"""
replacement = """        if(policy){Object.assign(event,{notify:true,audience:policy.audience,category:policy.category,priority:policy.priority,push:policy.push,pushOptional:!!policy.pushOptional,actionRequired:policy.actionRequired,status:policy.status,target:policy.target,groupKey:policy.groupKey,readBy:[]});for(const key of policy.audience){if(key.startsWith('maid:')){const id=key.slice(5);if(!event.maidIds.includes(id))event.maidIds.push(id);}}}else Object.assign(event,{notify:false,audience:[],readBy:[]});state.events.unshift(event);queueForegroundNotification(event);return event;
      }
      function installNotificationQaBridge(){
        if(new URLSearchParams(location.search).get('notificationQa')!=='1')return;
        Object.defineProperty(window,'__CASTLE_NOTIFICATION_QA__',{configurable:true,value:Object.freeze({
          currentMaidId:()=>signedInMaidId(),
          unreadCount:key=>notificationUnreadCount(key),
          append:(title,detail,options={})=>appendEvent(title,detail,options),
          setTime:value=>{state.time=String(value);return state.time;},
          bundles:key=>notificationBundlesForKey(key).map(bundle=>({groupKey:bundle.groupKey,bundleCount:bundle.bundleCount,title:bundle.title,unread:bundle.unread,actionRequired:bundle.actionRequired}))
        })});
      }
      installNotificationQaBridge();
'''"""
if text.count(marker) != 1:
    raise SystemExit(f'notification QA bridge marker mismatch: {text.count(marker)}')
path.write_text(text.replace(marker, replacement, 1), encoding='utf-8')
