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
 {roomNumber:'211',occupied:true,reservationPhase:'current',primaryDisplayStatus:'OCCUPIED',allocationReady:false,displayReservationId:'current-211',displayCheckInAt:'2026-10-30T16:00:00+09:00',displayCheckOutAt:date+'T11:00:00+09:00',nextReservationId:'next-211',nextCheckInAt:date+'T16:00:00+09:00'},
 {roomNumber:'350',allocationBlocked:true,allocationReady:false,cleaningRequired:true,primaryDisplayStatus:'BLOCKED',blockingReasonCodes:['OPERATION_BLOCKED'],readinessReasonCodes:['OPERATION_BLOCKED','CLEANING_REQUIRED'],reasonCodes:['OPERATION_BLOCKED','CLEANING_REQUIRED']},
 {roomNumber:'516',occupied:true,reservationPhase:'current',allocationReady:false,cleaningRequired:true,primaryDisplayStatus:'OCCUPIED',displayReservationId:'current-516',displayCheckInAt:'2026-10-29T16:00:00+09:00',displayCheckOutAt:'2026-11-02T11:00:00+09:00'},
 {roomNumber:'629',reservationPhase:'upcoming',allocationReady:false,cleaningRequired:true,primaryDisplayStatus:'ARRIVAL_PENDING',displayReservationId:'next-629',displayCheckInAt:date+'T16:00:00+09:00',displayCheckOutAt:'2026-11-01T11:00:00+09:00',nextReservationId:'next-629',nextCheckInAt:date+'T16:00:00+09:00'},
 {roomNumber:'117'},
 {roomNumber:'762',occupied:true,reservationPhase:'current',allocationReady:false,primaryDisplayStatus:'OCCUPIED',displayReservationId:'long-762',displayCheckInAt:'2026-10-01T16:00:00+09:00'}
].map(r=>({...base,id:'room-'+r.roomNumber,...r}));
const target=(no,status,extra={})=>({roomId:'room-'+no,cleaningTargetId:'target-'+no,serviceDate:date,effectiveServiceDate:date,cleaningKind:'checkout',targetStatus:status,revision:1,isCurrent:true,endedAt:null,availableFrom:date+'T11:00:00+09:00',...extra});
let cards=[target('350','inspection_pending'),target('516','in_progress',{cleaningKind:'stayover'}),target('629','upload_pending')];
let unassigned=[target('211','unassigned')],serverRooms=rooms,failWorkflow=false,delay=0;
const hook=`window.__axesQA={setup:rooms=>{
 LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});
 state.remote=initialRemoteState();state.role='admin';state.liveView='rooms';state.detail=null;liveRoomDetail=null;state.remote.operationalDate='${date}';state.selectedDate='${date}';
 state.remote.auth={...state.remote.auth,status:'authenticated',user:{id:'qa-admin',profileId:'qa-admin',role:'admin',displayName:'데모 QA 관리자',status:'active',mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
 for(const key of ['rooms','accounts','roomTypes','reservations','notifications','availability','complaints','payroll','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});
 state.remote.rooms.items=rooms;state.remote.roomProjection={date:'${date}',status:'ready',items:rooms,lastSuccessAt:new Date().toISOString()};Object.assign(state.remote.homeAssignments,{date:'2026-11-01',status:'ready',items:[]});cleaningState().status='ready';syncAuthState(state);rawCloseModal();render();
 },home:()=>{state.liveView='today';render();},snapshot:()=>({date:state.remote.roomProjection?.date,filter:state.remote.rooms.filter,view:state.liveView}),
 ${before?'':`refresh:()=>loadLiveRoomProjection(),axes:liveRoomAxes,workflow:roomWorkflowFromRecords,primary:liveRoomPrimary,match:liveRoomMatchesFilter,normalize:normalizeRoomFilter,summary:roomAxisSummary,
 replace:rooms=>{state.remote.roomProjection.items=rooms;render();},date:date=>{state.remote.operationalDate=date;state.selectedDate=date;return loadLiveRoomProjection();},logout:()=>{LIVE_RUNTIME.authGeneration++;state.remote=initialRemoteState();render();},state:()=>state.remote.roomProjection,
 demoStages:()=>{const saved=state,room=ROOMS.find(r=>r.no==='211'),occupancy=room.occupancy,request=room.stayoverRequest;state=structuredClone(state);state.selectedDate='2026-08-15';state.time='10:00';state.reservations=[];state.manualAssignmentTargets=[];state.manualCleaningRequests={};state.cleaningTargets={};state.assignments={};state.cleaningSubmissions={};state.cleaningAttempts={qa:{id:'qa',room:'211',status:'upload',workDate:'2026-08-15',kind:'추가 청소'}};state.currentAttemptByRoom={'211':'qa'};room.occupancy='occupied';room.stayoverRequest=null;try{const result=[];for(const [job,status]of [['upload','upload'],['inspection','submitted'],['reclean','rejected'],['approved','approved']]){state.jobs['211']=job;state.cleaningAttempts.qa.status=status;result.push(demoRoomAxes('211'));}return result;}finally{state=saved;room.occupancy=occupancy;room.stayoverRequest=request;}},
 editor:room=>liveRoomEditorOptions({room,record:{blocks:[],issues:[]},category:'MAINTENANCE',description:''}).body,`}
 };`;
const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:390,height:900},timezoneId:'America/New_York',serviceWorkers:'block',reducedMotion:'reduce'}),page=await context.newPage(),errors=[],unexpected=[],requests=[];
page.setDefaultTimeout(7000);await page.clock.setFixedTime(new Date(now));
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!/Service Worker registration blocked|Failed to load resource.*503/.test(m.text()))errors.push(m.text());});
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());if(url.origin===origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,hook)});if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});return route.continue();}
 const path=url.pathname.replace('/functions/v1/api',''),day=url.searchParams.get('serviceDate')||date;requests.push(path);
 if(req.method()==='GET'&&req.url().startsWith(api)){
  if(path==='/v1/rooms'){const snapshot=structuredClone(serverRooms);await new Promise(r=>setTimeout(r,delay));return route.fulfill({json:{rooms:snapshot.map(room=>({...room,serviceDate:day}))}});}
  if(path==='/v1/assignments')return route.fulfill(failWorkflow?{status:503,json:{error:{code:'QA_UNAVAILABLE'}}}:{json:{assignments:cards}});
  if(path==='/v1/assignments/commit-impact')return route.fulfill(failWorkflow?{status:503,json:{error:{code:'QA_UNAVAILABLE'}}}:{json:{impact:{serviceDate:day,committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:unassigned}}});
  if(path==='/v1/room-pin-sheet-sync/status')return route.fulfill({json:{sync:{version:1,pending:0,failed:0,operatorBlocked:false,lastSuccessAt:now}}});
  if(path==='/v1/reservations')return route.fulfill({json:{reservations:[],nextCursor:null}});
  if(path==='/v1/assignment-change-requests')return route.fulfill({json:{requests:[],nextCursor:null}});
  if(path==='/v1/inspections')return route.fulfill({json:{submissions:[],nextCursor:null}});
  const match=path.match(/^\/v1\/rooms\/(room-\d+)(?:\/(events|operation-blocks|issues|reports|candle-events|pin-sync))?$/);
  if(match){const room=rooms.find(r=>r.id===match[1]);return route.fulfill({json:!match[2]?{room}:match[2]==='pin-sync'?{pinSync:{status:'verified',version:1}}:match[2]==='candle-events'?{events:[]}:{roomId:room.id,roomStateVersion:1,items:[],nextCursor:null}});}
 }
 unexpected.push(req.method()+' '+path);return route.abort();
});
const action=name=>page.locator(`[data-action="${name}"]:visible`).first(),shortcut=key=>page.locator(`.checkout-due-shortcut[data-filter="${key}"]:visible`),card=no=>page.locator(`[data-live-room="${no}"]`),shown=()=>page.locator('[data-live-room]').evaluateAll(es=>es.map(e=>e.dataset.liveRoom).sort());
const setup=async()=>{await page.evaluate(rooms=>__axesQA.setup(rooms),rooms);if(!before)await page.evaluate(()=>__axesQA.refresh());};
const shot=async name=>page.screenshot({path:`${output}/room-state-axes-${name}.png`});
try{
 await mkdir(output,{recursive:true});await page.goto(origin+'/index.html');await setup();
 for(const width of [390,1440]){await page.setViewportSize({width,height:900});await shot(`${before?'before':'after'}-${width}`);}
 if(before){console.log('[ok] Same synthetic rooms, date, role and viewports baseline');}
 else{
  assert.equal(await page.title(),'객실 현황 · CASTLE THE ART');assert.match(page.url(),/index.html/);
  const summaries=await page.evaluate(()=>Object.fromEntries(['occupied','vacant','arrival','checkout','cleaning','ready','blocked'].map(k=>[k,__axesQA.summary(k).count])));
  assert.deepEqual(summaries,{occupied:3,vacant:3,arrival:2,checkout:1,cleaning:4,ready:1,blocked:1});
  assert.match(await card('211').innerText(),/투숙 중/);assert.match(await card('211').innerText(),/입실 예정/);assert.match(await card('211').innerText(),/퇴실 예정/);assert.match(await card('211').innerText(),/퇴실 대기/);assert.match(await card('350').innerText(),/운영 제한/);assert.match(await card('350').innerText(),/검수 대기/);
  const options=await page.locator('[data-control="live-room-filter"]').innerText();assert(!/예약 있음|퇴실점검 대상|배정 가능|배정 불가/.test(options));
  for(const width of [360,390,768,1440]){
   await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));assert(await page.locator('#main-content').innerText());assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   for(const [filter,expected] of [['occupied',['211','516','762']],['vacant',['117','350','629']],['arrival',['211','629']],['checkout-due',['211']],['cleaning',['211','350','516','629']],['blocked',['350']],['ready',['117']]]){await page.locator('[data-control="live-room-filter"]').selectOption(filter);assert.deepEqual(await shown(),expected);}
   await page.locator('#live-room-search').fill('629');await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await shortcut('arrival').focus();await page.keyboard.press('Enter');assert.deepEqual(await shown(),['211','629']);assert.equal(await page.locator('#live-room-search').inputValue(),'');await page.waitForFunction(()=>document.activeElement?.dataset.control==='live-room-filter');
   assert(await shortcut('arrival').evaluate(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44&&!!e.getAttribute('aria-label');}));
   await action('live-room-export').click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Tab');assert(await page.getByRole('dialog').evaluate(e=>e.contains(document.activeElement)));await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});await page.waitForFunction(()=>document.activeElement?.dataset.action==='live-room-export');
   await action('live-room-export').click();await page.getByRole('dialog').waitFor();await page.goBack();await page.getByRole('dialog').waitFor({state:'hidden'});assert.equal((await page.evaluate(()=>__axesQA.snapshot())).filter,'arrival');
   await card('211').locator('[data-action="open-live-room-reservation-status"]').click();await page.getByRole('dialog').waitFor();assert.match(await page.getByRole('dialog').innerText(),/211호/);await page.keyboard.press('Escape');
   await card('211').locator('[data-action="open-live-room-detail"]').click();await page.getByRole('heading',{name:/211호/}).first().waitFor();await action('back').click();await card('211').waitFor();assert.deepEqual(await shown(),['211','629']);
   if([390,1440].includes(width)){await page.evaluate(()=>scrollTo(0,0));await shot(`filtered-${width}`);await card('211').scrollIntoViewIfNeeded();await shot(`turnover-${width}`);}
   await page.evaluate(()=>__axesQA.home());assert.equal(await page.locator('.today-summary > button').count(),4);assert.match(await shortcut('arrival').innerText(),/입실 예정 2개/);assert.match(await shortcut('checkout-due').innerText(),/퇴실 예정 1개/);
   if([390,1440].includes(width)){await page.evaluate(()=>scrollTo(0,0));await shot(`home-${width}`);}
   await page.locator('[data-action="filter-rooms"][data-filter="cleaning"]').click();assert.deepEqual(await shown(),['211','350','516','629']);
  }
  console.log('[ok] Independent counts/filters overlap; 4 widths, destinations, keyboard/focus/modal/Back, 44px/accessibility/overflow');
  const workflow=async(row,changes={},options={complete:true})=>page.evaluate(([room,rows,options])=>__axesQA.workflow(room,rows,options),[{...rooms[0],...changes},Array.isArray(row)?row:[row],options]);
  for(const [status,label]of [['unassigned','퇴실 대기'],['draft_assigned','퇴실 대기'],['notified','퇴실 대기'],['in_progress','청소 중'],['upload_pending','업로드 대기'],['inspection_pending','검수 대기'],['rejected','재청소']]){const w=await workflow(target('211',status));assert.equal(w.incomplete,true);assert.deepEqual(w.stages,[label]);}
  assert.deepEqual((await workflow(target('211','notified',{currentDeparture:{actualCheckoutAt:date+'T09:00:00+09:00'}}))).stages,['청소 대기']);
  assert.deepEqual((await workflow(target('211','notified',{availableFrom:date+'T09:00:00+09:00',cleaningKind:'stayover'}))).stages,['청소 대기']);
  for(const status of ['approved','cancelled'])assert.equal((await workflow(target('211',status))).incomplete,false);
  assert.equal((await workflow(target('211','upload_pending',{attemptStatus:'field_completed'}))).incomplete,true);
  assert.equal((await workflow(target('211','inspection_pending',{attemptStatus:'submitted'}))).incomplete,true);
  const older=target('211','notified',{revision:1,isCurrent:false}),approved=target('211','approved',{revision:2});assert.equal((await workflow([older,approved])).incomplete,false);
  assert.deepEqual((await workflow([target('211','in_progress'),target('211','in_progress')])).stages,['청소 중']);
  assert.equal((await workflow([approved,target('211','inspection_pending',{cleaningTargetId:'another'})])).incomplete,true);
  assert.equal((await workflow([],{cleaningRequired:true})).incomplete,true,'unlisted earlier-date active obligation remains included');
  assert.equal((await workflow([],{cleaningRequired:false},{complete:false})).incomplete,null);
  const result=await page.evaluate(room=>({axes:__axesQA.axes(room),primary:__axesQA.primary(room),editor:__axesQA.editor(room)}),{...rooms[1],primaryDisplayStatus:'READY',displayStatusOverride:'READY',roomWorkflow:{incomplete:true,stages:['검수 대기']}});assert.equal(result.primary.key,'blocked');assert.equal(result.axes.cleaning,true);assert(!result.editor.includes('room-correction-display'));assert(!result.editor.includes('data-kind="status"'));assert(result.editor.includes('운영 중지 등록'));
  assert.deepEqual(await page.evaluate(()=>['reserved','reservation','checkout-inspection','default'].map(__axesQA.normalize)),['all','all','all','vacant']);
  const demoStages=await page.evaluate(()=>__axesQA.demoStages());assert.deepEqual(demoStages.map(a=>a.cleaning),[true,true,true,false]);assert.deepEqual(demoStages.slice(0,3).map(a=>a.stages[0]),['업로드 대기','검수 대기','재청소']);assert(demoStages.every(a=>a.occupied));
  console.log('[ok] Stages through inspection approval, cancellation/reclean, duplicate/replaced targets, independent override-free presentation');
  serverRooms=[...rooms,rooms[0]];await page.evaluate(()=>__axesQA.refresh());assert.equal(await page.evaluate(()=>__axesQA.summary('cleaning').count),4);assert.equal((await page.evaluate(()=>__axesQA.state())).items.length,6);
  failWorkflow=true;await page.evaluate(()=>__axesQA.refresh());assert.equal(await page.evaluate(()=>__axesQA.summary('cleaning').count),null);await page.locator('[data-control="live-room-filter"]').selectOption('cleaning');assert.match(await page.locator('.inline-empty').innerText(),/청소 상세 조회 실패/);assert.deepEqual(await shown(),['350','516','629'],'known cleaning rooms remain visible during partial failure');assert.match(await page.locator('#main-content').innerText(),/0건으로 표시하지 않습니다/);
  failWorkflow=false;serverRooms=rooms;await setup();const readCount=requests.filter(p=>p==='/v1/assignments/commit-impact').length;await page.evaluate(()=>__axesQA.date('2026-11-03'));assert.equal(requests.filter(p=>p==='/v1/assignments/commit-impact').length,readCount);assert.equal(await page.evaluate(()=>__axesQA.summary('cleaning').count),null);assert.match(await page.locator('#main-content').innerText(),/미배정 청소 대상 API 미제공/);
  await page.evaluate(()=>__axesQA.date('2026-10-29'));assert.equal(await page.evaluate(()=>__axesQA.summary('cleaning').count),3);assert.match(await page.locator('#main-content').innerText(),/과거 진행 단계 API 미제공/);
  await setup();delay=200;await page.evaluate(()=>{void __axesQA.refresh();});await page.evaluate(()=>__axesQA.date('2026-11-01'));await page.waitForTimeout(250);assert.equal((await page.evaluate(()=>__axesQA.state())).date,'2026-11-01');await page.evaluate(()=>{void __axesQA.refresh();__axesQA.logout();});await page.waitForTimeout(250);assert.notEqual((await page.evaluate(()=>__axesQA.state()))?.status,'ready');
  console.log('[ok] Real loader composition, unique rooms, partial API failures, future/past limits, date/session race guards');
  assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);console.log('[ok] console warnings/errors, page exceptions, unexpected requests: 0');
 }
}catch(e){console.error({body:(await page.locator('#main-content').innerText()).slice(0,2200),errors,unexpected});await page.screenshot({path:'/tmp/rms-axes-failure.png'});throw e;}finally{await browser.close();}
