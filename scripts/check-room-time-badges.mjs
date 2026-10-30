#!/usr/bin/env node
// Browser plugin not available. Synthetic API fixtures; no operational data or writes.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4179',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const date='2026-10-31',now=date+'T10:00:00+09:00',before=process.env.RMS_QA_BASE_REF,output='WIREFRAME/QA/screenshots';
const source=before?execFileSync('git',['show',before+':WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:8*1024*1024}):await readFile('WIREFRAME/index.html','utf8');
const boot='      void bootApplication();';assert.equal(source.split(boot).length,2);
const base={serviceDate:date,projectionMode:'LIVE',evaluatedAt:now,serverTime:now,reservationPhase:'none',occupied:false,roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:1,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',primaryDisplayStatus:'READY',allocationReady:true,allocationBlocked:false,blockingReasonCodes:[],readinessReasonCodes:[],reasonCodes:[],displayReservationId:null,displayGuestCount:2,displayBaseOccupancy:2,displayCheckInAt:null,displayCheckOutAt:null,nextReservationId:null,nextCheckInAt:null,nextCheckOutAt:null,detailConditionCodes:[]};
const rooms=[
 {roomNumber:'211',occupied:true,reservationPhase:'current',primaryDisplayStatus:'OCCUPIED',allocationReady:false,displayReservationId:'current-211',displayCheckInAt:'2026-10-30T16:00:00+09:00',displayCheckOutAt:date+'T13:00:00+09:00',displayGuestCount:3,displayBaseOccupancy:2,nextReservationId:'next-211',nextCheckInAt:date+'T15:00:00+09:00'},
 {roomNumber:'350',allocationBlocked:true,allocationReady:false,cleaningRequired:true,primaryDisplayStatus:'BLOCKED',blockingReasonCodes:['OPERATION_BLOCKED'],readinessReasonCodes:['OPERATION_BLOCKED','CLEANING_REQUIRED'],reasonCodes:['OPERATION_BLOCKED','CLEANING_REQUIRED']},
 {roomNumber:'516',occupied:true,reservationPhase:'current',allocationReady:false,cleaningRequired:true,primaryDisplayStatus:'OCCUPIED',displayReservationId:'current-516',displayCheckInAt:'2026-10-29T16:00:00+09:00',displayCheckOutAt:'2026-11-02T11:00:00+09:00'},
 {roomNumber:'629',reservationPhase:'upcoming',allocationReady:false,cleaningRequired:true,primaryDisplayStatus:'ARRIVAL_PENDING',displayReservationId:'next-629',displayCheckInAt:date+'T16:00:00+09:00',displayCheckOutAt:'2026-11-01T11:00:00+09:00',nextReservationId:'next-629',nextCheckInAt:date+'T16:00:00+09:00'},
 {roomNumber:'117'},
 {roomNumber:'762',occupied:true,reservationPhase:'current',allocationReady:false,primaryDisplayStatus:'OCCUPIED',displayReservationId:'long-762',displayCheckInAt:'2026-10-01T16:00:00+09:00'}
].map(r=>({...base,id:'room-'+r.roomNumber,...r}));

const assignments=[{assignmentId:'assignment-211',cleaningTargetId:'target-211',roomId:'room-211',roomNumber:'211',maidProfileId:'qa-maid',maidDisplayName:'데모 QA 메이드',serviceDate:date,revision:1,isCurrent:true,endedAt:null,notifiedAt:now,cleaningKind:'checkout',targetStatus:'notified',attemptStatus:'scheduled',availableFrom:date+'T13:00:00+09:00',dueAt:date+'T14:30:00+09:00',roomTypeCode:'standard',scheduleSnapshot:{nextCheckInAt:date+'T15:00:00+09:00',plannedCheckoutAt:date+'T13:00:00+09:00',nextArrivalKind:'check_in',isEarlyCheckIn:true,isLateCheckout:true,isScheduleUpdated:false}},{assignmentId:'assignment-350',cleaningTargetId:'target-350',roomId:'room-350',roomNumber:'350',maidProfileId:'qa-maid',maidDisplayName:'데모 QA 메이드',serviceDate:date,revision:1,isCurrent:true,endedAt:null,notifiedAt:now,cleaningKind:'additional',targetStatus:'notified',attemptStatus:'scheduled',availableFrom:null,dueAt:null,roomTypeCode:'standard',scheduleSnapshot:{nextCheckInAt:'2026-11-01T14:00:00+09:00',plannedCheckoutAt:'2026-10-30T13:00:00+09:00',nextArrivalKind:'check_in',isEarlyCheckIn:true,isLateCheckout:true,isScheduleUpdated:false}}];
const hook=`window.__timeQA={setup:(rooms,assignments,role='admin')=>{
 LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});
 state.remote=initialRemoteState();state.role=role;state.liveView=role==='maid'?'my':'rooms';state.detail=null;liveRoomDetail=null;state.remote.operationalDate='${date}';state.selectedDate='${date}';
 state.remote.auth={...state.remote.auth,status:'authenticated',user:{id:'qa-'+role,profileId:'qa-'+role,role,displayName:'데모 QA '+role,status:'active',mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
 for(const key of ['rooms','accounts','roomTypes','reservations','notifications','availability','complaints','payroll','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});
 state.remote.rooms.items=rooms;state.remote.roomProjection={date:'${date}',status:'ready',items:rooms,lastSuccessAt:new Date().toISOString()};Object.assign(cleaningState(),{status:'ready',serviceDate:'${date}',assignments});if(role==='maid')for(const assignment of assignments){cleaningState().attempts.set(assignment.assignmentId,{attemptId:'attempt-'+assignment.assignmentId,assignmentId:assignment.assignmentId,assignmentRevision:assignment.revision,status:'scheduled'});Object.assign(liveMaidReadRecord(assignment),{summaryStatus:'ready'});}syncAuthState(state);rawCloseModal();render();
 },assignment:liveAssignmentScheduleBadges,axes:liveRoomAxes,match:liveRoomMatchesFilter,${before?'':`timing:liveRoomTimeStatus,`}
 };`;
const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:390,height:900},timezoneId:'America/New_York',serviceWorkers:'block',reducedMotion:'reduce'}),page=await context.newPage(),errors=[],unexpected=[],requests=[];
page.setDefaultTimeout(7000);await page.clock.setFixedTime(new Date(now));
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!/Service Worker registration blocked/.test(m.text()))errors.push(m.text());});
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());if(url.origin===origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,hook)});if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});return route.continue();}
 const path=url.pathname.replace('/functions/v1/api','');requests.push(path);
 if(req.method()==='GET'&&req.url().startsWith(api)){
  if(path==='/v1/rooms')return route.fulfill({json:{rooms}});
  if(path==='/v1/assignments')return route.fulfill({json:{assignments}});
  if(path==='/v1/assignments/commit-impact')return route.fulfill({json:{impact:{serviceDate:date,committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}}});
  if(path==='/v1/room-pin-sheet-sync/status')return route.fulfill({json:{sync:{version:1,pending:0,failed:0,operatorBlocked:false,lastSuccessAt:now}}});
  if(path==='/v1/reservations')return route.fulfill({json:{reservations:[],nextCursor:null}});
  if(path==='/v1/assignment-change-requests')return route.fulfill({json:{requests:[],nextCursor:null}});
  if(path==='/v1/inspections')return route.fulfill({json:{submissions:[],nextCursor:null}});
  if(path==='/v1/attempts/lifecycle-impact')return route.fulfill({json:{attempt:null}});
  if(path==='/v1/attempts/current')return route.fulfill({json:{attempt:null}});
  if(path.endsWith('/photo-slots'))return route.fulfill({json:{attemptId:'attempt-assignment-211',assignmentId:'assignment-211',assignmentRevision:1,slots:[]}});
  if(path.endsWith('/submissions'))return route.fulfill({json:{submissions:[]}});
  const match=path.match(/^\/v1\/rooms\/(room-\d+)(?:\/(events|operation-blocks|issues|reports|candle-events|pin-sync))?$/);
  if(match){const room=rooms.find(r=>r.id===match[1]);return route.fulfill({json:!match[2]?{room}:match[2]==='pin-sync'?{pinSync:{status:'verified',version:1}}:match[2]==='candle-events'?{events:[]}:{roomId:room.id,roomStateVersion:1,items:[],nextCursor:null}});}
 }
 unexpected.push(req.method()+' '+path);return route.abort();
});
const card=no=>page.locator(`[data-live-room="${no}"]`),action=name=>page.locator(`[data-action="${name}"]:visible`).first();
const setup=role=>page.evaluate(([rooms,assignments,role])=>__timeQA.setup(rooms,assignments,role),[rooms,assignments,role]);
const snapshot=async(role,width)=>{await setup(role);await page.setViewportSize({width,height:900});if(role==='admin'){await page.locator('#live-room-search').fill('211');await card('211').scrollIntoViewIfNeeded();}await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await page.screenshot({path:`${output}/room-time-badges-${role}-${before?'before':'after'}-${width}.png`});};
try{
 await mkdir(output,{recursive:true});await page.goto(origin+'/index.html');
 for(const role of ['admin','maid'])for(const width of [390,1440])await snapshot(role,width);
 if(!before){
  for(const role of ['admin','maid'])for(const width of [360,390,768,1440]){
   await setup(role);await page.setViewportSize({width,height:900});assert.match(await page.title(),/CASTLE THE ART/);assert(await page.locator('#main-content').innerText());assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   const container=role==='admin'?card('211'):page.locator('[data-maid-room-task="assignment-211"]');
   assert.equal(await container.locator('.schedule-priority-badge.early').innerText(),'얼리 1시간');assert.equal(await container.locator('.schedule-priority-badge.late').innerText(),'레이트 2시간');
   assert.match(await container.locator('.early').getAttribute('aria-label'),/15:00/);assert.match(await container.locator('.late').getAttribute('aria-label'),/13:00/);
   assert(await container.locator('.schedule-priority-badge').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.left>=0&&r.right<=innerWidth&&e.scrollWidth<=e.clientWidth+1;})));
   if(role==='admin'){
    assert.match(await card('211').innerText(),/퇴실 예정/);assert.match(await card('211').innerText(),/입실 예정/);
    await page.locator('[data-control="live-room-filter"]').selectOption('early');assert.deepEqual(await page.locator('[data-live-room]').evaluateAll(es=>es.map(e=>e.dataset.liveRoom)),['211']);
    await page.locator('[data-control="live-room-filter"]').selectOption('late');assert.deepEqual(await page.locator('[data-live-room]').evaluateAll(es=>es.map(e=>e.dataset.liveRoom)),['211']);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await action('live-room-export').focus();await page.keyboard.press('Enter');await page.getByRole('dialog').waitFor();await page.keyboard.press('Tab');assert(await page.getByRole('dialog').evaluate(e=>e.contains(document.activeElement)));await page.keyboard.press('Escape');await page.waitForFunction(()=>document.activeElement?.dataset.action==='live-room-export');
    await action('live-room-export').click();await page.getByRole('dialog').waitFor();await page.goBack();await page.getByRole('dialog').waitFor({state:'hidden'});
    await card('211').locator('[data-action="open-live-room-reservation-status"]').click();await page.getByRole('dialog').waitFor();assert.match(await page.getByRole('dialog').innerText(),/211호/);await page.keyboard.press('Escape');
    await card('211').locator('[data-action="open-live-room-detail"]').click();await page.getByRole('heading',{name:/211호/}).first().waitFor();await action('back').click();await card('211').waitFor();
   }else{
    assert.equal(await page.locator('[data-maid-room-task="assignment-350"] .schedule-priority-badge').count(),0);const toggle=container.locator('button').first();assert.equal(await toggle.getAttribute('aria-expanded'),'false');assert(await toggle.evaluate(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44&&!!e.textContent.trim();}));await toggle.focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>document.querySelector('[data-maid-room-task="assignment-211"] button').getAttribute('aria-expanded')==='true');assert(await container.locator('.maid-room-task-heading .early').isVisible());await toggle.click();assert.equal(await toggle.getAttribute('aria-expanded'),'false');
    assert.equal(await page.locator('[data-action="open-live-room-detail"],[data-action="live-room-operations"]').count(),0);
   }
  }
  console.log('[ok] Administrator and maid cards: compact badges, 4 widths, matching filters, collapsed/expanded tasks, original destinations, keyboard/focus/modal/Back, no overflow');
  await setup('admin');
  for(const [at,checkout,arrival] of [['12:59:59',true,true],['13:00:00',false,true],['15:00:00',false,false]]){const axes=await page.evaluate(room=>__timeQA.axes(room),{...rooms[0],evaluatedAt:date+'T'+at+'+09:00'});assert.equal(axes.checkout,checkout);assert.equal(axes.arrival,arrival);}
  assert.equal((await page.evaluate(room=>__timeQA.axes(room),{...rooms[0],reservationPhase:'none',displayReservationId:null,displayCheckOutAt:null,nextReservationId:null,nextCheckInAt:null})).arrival,false);
  const timing=async room=>page.evaluate(room=>__timeQA.timing(room),room);
  assert.equal((await timing({...rooms[0],nextCheckInAt:'2026-10-31T05:30:00Z',displayCheckOutAt:'2026-10-31T02:30:00Z'})).earlyOffset,'1시간 30분');assert.equal((await timing({...rooms[0],nextCheckInAt:'2026-10-31T06:30:00Z',displayCheckOutAt:'2026-10-31T02:30:00Z'})).lateOffset,'30분');
  for(const value of [null,'invalid']){const t=await timing({...rooms[0],nextCheckInAt:value,displayCheckInAt:value,displayCheckOutAt:value});assert.equal(t.early,false);assert.equal(t.late,false);}
  const standard=await timing({...rooms[0],nextCheckInAt:date+'T16:00:00+09:00',displayCheckOutAt:date+'T11:00:00+09:00'});assert.equal(standard.early,false);assert.equal(standard.late,false);
  assert.equal((await timing({...rooms[0],displayCheckInAt:'2026-10-30T14:00:00+09:00',nextCheckInAt:null})).early,false,'missing next arrival must not reuse previous guest early check-in');
  const badge=async snapshot=>page.evaluate(([snapshot,serviceDate])=>__timeQA.assignment({serviceDate,scheduleSnapshot:snapshot}),[snapshot,date]),s=assignments[0].scheduleSnapshot;
  assert.match(await badge({...s,nextCheckInAt:'2026-10-31T05:30:00Z',plannedCheckoutAt:'2026-10-31T02:30:00Z'}),/얼리 1시간 30분/);
  for(const snapshot of [null,{...s,isEarlyCheckIn:null,isLateCheckout:null,nextArrivalKind:'room_move'},{...s,nextCheckInAt:null,plannedCheckoutAt:null},{...s,nextCheckInAt:'invalid',plannedCheckoutAt:'invalid'}])assert.equal(await badge(snapshot),'');
  assert.equal((await badge({...s,isEarlyCheckIn:false,isLateCheckout:false})), '');
  assert.equal(await badge(assignments[1].scheduleSnapshot),'','other-day departure and arrival must not appear on a cleaning-day card');
  const nextDay=await page.evaluate(row=>__timeQA.assignment(row),{...assignments[1],effectiveServiceDate:'2026-11-01'});assert.match(nextDay,/얼리 2시간/);assert(!nextDay.includes('레이트'),'effective cleaning day takes precedence on rollover');
  assert.equal(await page.evaluate(snapshot=>__timeQA.assignment({scheduleSnapshot:snapshot}),s),'','missing cleaning date must not imply today');
  assert.match(await badge({...s,nextCheckInAt:'2026-10-30T23:30:00Z'}),/얼리 7시간 30분/,'KST cleaning day, not the UTC date');
  assert(!((await badge({...s,nextCheckInAt:'2026-10-31T16:00:00Z'})).includes('얼리')),'next KST day must be hidden');
  const lateOnly=await badge({...s,nextCheckInAt:'2026-11-01T15:00:00+09:00'});assert.match(lateOnly,/레이트 2시간/);assert(!lateOnly.includes('얼리'));
  const earlyOnly=await badge({...s,plannedCheckoutAt:'2026-10-30T13:00:00+09:00'});assert.match(earlyOnly,/얼리 1시간/);assert(!earlyOnly.includes('레이트'));

  assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);console.log('[ok] Late checkout boundary, next arrival independent, UTC/KST offsets, half-hours, standard time, missing/invalid fields, snapshot flags/moves, exact cleaning day, rollover and adjacent guests; no app console errors or unexpected API calls');
 }else console.log('[ok] Before screenshots: same administrator/maid, schedule fixture, 390/1440px');
}catch(error){console.error({errors,unexpected});await page.screenshot({path:'/tmp/room-time-badges-failure.png',fullPage:true});throw error;}finally{await browser.close();}
