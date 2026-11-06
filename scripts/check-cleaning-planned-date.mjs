#!/usr/bin/env node
// Browser plugin not available. Synthetic API only; no operational writes.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4189',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const source=await readFile(process.env.RMS_QA_HTML||'WIREFRAME/index.html','utf8'),before=process.env.RMS_QA_COMPARE==='before';
const evidence=resolve(process.env.RMS_QA_EVIDENCE||'WIREFRAME/QA/screenshots');await mkdir(evidence,{recursive:true});
const id=n=>`81000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const maid={profileId:id(1),displayName:'메이드 A · 데모',role:'maid',status:'active'},room={id:id(2),roomNumber:'117',roomTypeCode:'premium',roomTypeName:'프리미어 더블 로프트',elevatorZone:'C',stateVersion:1,candleCount:0};
const assignment={assignmentId:id(3),cleaningTargetId:id(4),roomId:room.id,roomNumber:room.roomNumber,maidProfileId:maid.profileId,maidDisplayName:maid.displayName,serviceDate:'2026-10-08',originalServiceDate:'2026-10-08',effectiveServiceDate:'2026-10-08',planningDate:'2026-11-07',revision:1,targetAssignmentVersion:1,sequenceNumber:1,isCurrent:true,notifiedAt:'2026-11-06T19:00:00+09:00',targetStatus:'notified',attemptStatus:null,cleaningKind:'checkout',sourceKind:'scheduled_checkout',roomTypeCode:'premium',roomTypeName:room.roomTypeName,elevatorZone:'C',feeSnapshot:20000,availableFrom:'2026-10-08T11:00:00+09:00',dueAt:null,rolloverCount:0,instructionMemo:'장기 · 데모',scheduleSnapshot:{plannedCheckoutAt:'2026-10-08T11:00:00+09:00'},currentDeparture:{actualCheckoutAt:'2026-10-08T11:00:00+09:00'}};
let attempt=null,role='admin',now='2026-11-06',calls=[];
const boot=`window.__dateQA={setup:async(role)=>{LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{assignmentPlanningDate:true,assignmentInstructionMemo:true,optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.role=role;state.liveView=role==='admin'?'cleaning':'my';state.cleaningTab='assignment-tomorrow';state.detail=null;liveRoomDetail=null;state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:role==='admin'?'${id(9)}':'${maid.profileId}',displayName:'QA 계정 · 데모',role,mustChangePassword:false},session:{accessToken:'qa-only',refreshToken:'qa-refresh',expiresAt:Date.now()+3600000}};for(const name of ['rooms','accounts','roomTypes','reservations','notifications','availability'])Object.assign(state.remote[name],{status:'ready',lastSuccessAt:new Date().toISOString()});state.remote.rooms.items=[${JSON.stringify(room)}];state.remote.accounts.items=[${JSON.stringify(maid)}];syncAuthState(state);resetLiveCleaningDate(role==='admin'?'2026-11-07':liveKstIsoDate());await loadLiveCleaning();render();},notify:()=>openLiveNotificationTarget({deepLink:{kind:'cleaningTarget',entityId:'${assignment.cleaningTargetId}'}}),get:()=>({date:cleaningState().serviceDate,busy:cleaningState().busy,status:cleaningState().status,error:cleaningState().error?.code}),readOnly:(a,t)=>liveMaidAssignmentReadOnly(a,t),render:()=>render()};`;
const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:390,height:950},timezoneId:'America/Los_Angeles',serviceWorkers:'block'}),page=await context.newPage();page.setDefaultTimeout(10000);
await page.clock.install({time:new Date('2026-11-06T19:00:00+09:00')});await page.clock.setFixedTime(new Date('2026-11-06T19:00:00+09:00'));
const errors=[],warnings=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))warnings.push(m.text());});
const json=(r,v,status=200)=>r.fulfill({status,contentType:'application/json',body:JSON.stringify(v)});
await page.route('**/*',async r=>{
 const req=r.request(),u=new URL(req.url());if(u.origin===origin){if(u.pathname==='/index.html')return r.fulfill({contentType:'text/html',body:source.replace('\n      void bootApplication();',boot)});if(u.pathname==='/favicon.ico')return r.fulfill({status:204});return r.continue();}
 assert(req.url().startsWith(api+'/'),'unexpected external request');const path=u.pathname.replace('/functions/v1/api',''),method=req.method(),body=req.postDataJSON();calls.push({path,method,body,date:u.searchParams.get('serviceDate')});
 if(path==='/v1/assignments'){
  const date=u.searchParams.get('serviceDate'),visible=date===now?assignment.planningDate<=now:role==='admin'?assignment.planningDate<=date:assignment.planningDate===date;
  return json(r,{assignments:visible?[{...assignment,attemptStatus:attempt?.status??null}]:[]});
 }
 if(path.endsWith('/history'))return json(r,{assignments:[assignment]});
 if(path==='/v1/assignments/commit-impact')return json(r,{impact:{serviceDate:u.searchParams.get('serviceDate'),impactFingerprint:'a'.repeat(64),committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}});
 if(path==='/v1/availability/candidates')return json(r,{candidates:[{maidProfileId:maid.profileId,displayName:maid.displayName,workDate:u.searchParams.get('workDate'),availabilityVersion:1}]});
 if(path==='/v1/availability')return json(r,{availability:[]});
 if(path==='/v1/availability/me')return json(r,{availability:null});
 if(path==='/v1/accounts')return json(r,{accounts:[maid]});
 if(path==='/v1/assignment-change-requests')return json(r,{requests:[],nextCursor:null});
 if(path==='/v1/inspections')return json(r,{submissions:[],nextCursor:null});
 if(path==='/v1/notifications')return json(r,{notifications:[],nextCursor:null});
 if(path==='/v1/checkout-incidents')return json(r,{items:[],nextCursor:null});
 if(path==='/v1/rooms/candles')return json(r,{items:[],nextCursor:null});
 if(new RegExp('^/v1/rooms/'+room.id+'/(events|operation-blocks|issues|reports)$').test(path))return json(r,{roomId:room.id,roomStateVersion:1,items:[],nextCursor:null});
 if(path==='/v1/rooms')return json(r,{rooms:[room]});
 if(path==='/v1/reservations')return json(r,{reservations:[]});
 if(path==='/v1/room-types')return json(r,{items:[]});
 if(path==='/v1/attempts/current'){assert.equal(role,'maid');return json(r,{attempt});}
 if(path==='/v1/attempts/lifecycle-impact'){assert.equal(role,'admin');return json(r,attempt?{attempt}:{error:{code:'ATTEMPT_ACCESS_REQUIRED'}},attempt?200:403);}
 if(path.endsWith('/photo-slots'))return json(r,{attemptId:attempt.attemptId,assignmentId:assignment.assignmentId,assignmentRevision:1,slots:[]});
 if(path.endsWith('/submissions'))return json(r,{submissions:[]});
 if(path.endsWith('/start')){assert.equal(method,'POST');assert.equal(role,'maid');assert.equal(now,'2026-11-07');assert(req.headers()['idempotency-key']);assert.equal(body.expectedAssignmentId,assignment.assignmentId);attempt={...attempt,status:'in_progress',executionVersion:2,startedAt:'2026-11-07T11:00:00+09:00'};return json(r,{attempt});}
 if(path==='/v1/cleaning-history')return json(r,{items:[],nextCursor:null});
 throw new Error('Unexpected '+method+' '+path);
});
const setup=async next=>{role=next;await page.goto(origin+'/index.html');await page.evaluate(role=>__dateQA.setup(role),role);};
const row=()=>page.locator('[data-assignment-target="'+assignment.cleaningTargetId+'"]');
const task=()=>page.locator('[data-maid-room-task="'+assignment.assignmentId+'"]');
const check=(condition,label)=>{if(before){if(!condition)console.log('REPRODUCED: '+label);}else assert(condition,label);};
async function shot(name,locator){for(const width of [390,1440]){await page.setViewportSize({width,height:950});await locator.evaluate(el=>scrollTo({top:el.getBoundingClientRect().top+scrollY-220,behavior:'instant'}));await page.screenshot({path:resolve(evidence,`cleaning-date-${name}-${before?'before':'after'}-${width}.png`),fullPage:name==='maid-active'&&width===390});}}
try{
 await setup('admin');assert.match(await page.title(),/CASTLE THE ART/);assert((await page.locator('body').innerText()).length>100);
 const schedule=await row().locator('.assignment-schedule').innerText();await shot('admin',row());check(schedule.includes('청소일 2026-11-07'),'admin cleaning date must be November 7');check(!schedule.includes('원 업무일'),'source work date must not appear as current work date');assert(schedule.includes('실제 퇴실 10. 8.'));
 const adminNotificationAt=calls.length;await page.evaluate(()=>__dateQA.notify());check(await page.evaluate(()=>__dateQA.get().date)==='2026-11-07','admin notification must open planned day');if(!before){assert.equal(await page.evaluate(()=>__dateQA.get().status),'ready');assert.equal(calls.slice(adminNotificationAt).filter(c=>c.path==='/v1/attempts/lifecycle-impact').length,0);assert((await page.locator('body').innerText()).includes('2026-11-07'));}
 await setup('maid');assert.equal(await task().count(),0,'tomorrow is not today work');const notificationAt=calls.length;await page.evaluate(()=>__dateQA.notify());
 check(await page.evaluate(()=>__dateQA.get().date)==='2026-11-07','notification must open planned day');
 if(!before){assert(calls.slice(notificationAt).some(c=>c.path==='/v1/assignments'&&c.date==='2026-11-07'));assert.equal(await task().locator('[data-action="cleaning-start"]').count(),0);assert((await task().innerText()).includes('청소 예정'));await shot('maid-planned',task());}
 now='2026-11-07';await page.clock.setFixedTime(new Date('2026-11-07T11:00:00+09:00'));attempt={attemptId:id(5),assignmentId:assignment.assignmentId,assignmentRevision:1,cleaningTargetId:assignment.cleaningTargetId,maidProfileId:maid.profileId,executionVersion:1,status:'scheduled',instructionMemo:assignment.instructionMemo};
 await setup('maid');await task().getByRole('button',{name:/117호/}).click();await page.waitForFunction(()=>!document.querySelector('[data-maid-room-task]')?.textContent.includes('불러오는 중'));
 await shot('maid-active',task());const start=task().locator('[data-action="cleaning-start"]');check(await start.count()===1,'old checkout must not block assigned cleaning on planned day');
 if(!before){assert(await start.isEnabled());assert(!(await task().innerText()).includes('관리자 처리 필요'));await start.click();await page.waitForFunction(()=>!__dateQA.get().busy);assert.equal(attempt.status,'in_progress');assert.equal(calls.filter(c=>c.method==='POST').length,1);}
 assert.equal(assignment.serviceDate,'2026-10-08');assert.equal(assignment.planningDate,'2026-11-07');
 assert(await page.evaluate(([a,t])=>__dateQA.readOnly({...a,planningDate:'2026-11-05'},t),[assignment,attempt]));
 assert(await page.evaluate(([a,t])=>__dateQA.readOnly(a,{...t,status:'approved'}),[assignment,attempt]));
 for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:950});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
 const toggle=task().getByRole('button',{name:/117호/});await toggle.focus();await page.keyboard.press('Enter');assert.equal(await toggle.getAttribute('aria-expanded'),'false');await page.keyboard.press('Enter');assert.equal(await toggle.getAttribute('aria-expanded'),'true');await page.waitForFunction(()=>document.activeElement?.dataset.action==='cleaning-maid-room-toggle');
 assert.deepEqual(errors,[]);assert.deepEqual(warnings,[]);console.log(before?'Baseline date defects reproduced.':'PASS: distinct checkout/planned day, November 6→7 KST from US timezone, notification planned-day navigation, maid start, immutable original dates, historical read-only, 4 widths, keyboard/focus, console.');
}finally{await browser.close();}
