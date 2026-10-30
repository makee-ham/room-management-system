#!/usr/bin/env node
// Browser plugin not available. All business API requests use synthetic fixtures.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';

const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const date='2026-10-30',now=date+'T10:00:00+09:00',output='WIREFRAME/QA/screenshots';
const before=process.env.RMS_QA_BASE_REF;
const source=before?execFileSync('git',['show',before+':WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:8*1024*1024}):await readFile('WIREFRAME/index.html','utf8');
const boot='      void bootApplication();';assert.equal(source.split(boot).length,2);
const base={serviceDate:date,projectionMode:'LIVE',evaluatedAt:now,serverTime:now,reservationPhase:'current',occupied:true,roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:1,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',primaryDisplayStatus:'OCCUPIED',allocationBlocked:false,readinessReasonCodes:[],nextReservationId:null,nextCheckInAt:null,roomWorkflow:{incomplete:false,stages:[]},allocationReady:false,displayGuestCount:2,displayBaseOccupancy:2,displayCheckInAt:'2026-10-29T16:00:00+09:00',displayCheckOutAt:date+'T11:00:00+09:00',detailConditionCodes:[]};
const rooms=[
 {roomNumber:'211'},
 {roomNumber:'350',roomTypeCode:'premium',roomTypeName:'프리미어',primaryDisplayStatus:'BLOCKED',allocationBlocked:true,displayCheckOutAt:date+'T13:00:00+09:00',detailConditionCodes:['LATE_CHECK_OUT']},
 {roomNumber:'516',roomTypeCode:'oceanPremium',roomTypeName:'파셜 오션뷰',displayCheckOutAt:'2026-10-31T11:00:00+09:00'},
 {roomNumber:'629',roomTypeCode:'oceanFamily',roomTypeName:'패밀리 투룸',occupied:false,reservationPhase:'upcoming',primaryDisplayStatus:'ARRIVAL_PENDING',displayCheckInAt:date+'T16:00:00+09:00',displayCheckOutAt:'2026-10-31T11:00:00+09:00'},
 {roomNumber:'117',occupied:false,reservationPhase:'none',primaryDisplayStatus:'CLEANING_REQUIRED',displayReservationId:null,displayCheckInAt:null,displayCheckOutAt:null},
 {roomNumber:'762',displayCheckOutAt:null}
].map((r,i)=>({...base,id:'room-'+r.roomNumber,displayReservationId:'reservation-'+i,...r}));
const hook=`window.__checkoutQA={setup:rooms=>{
 LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});
 state.remote=initialRemoteState();state.role='admin';state.liveView='rooms';state.detail=null;liveRoomDetail=null;state.remote.operationalDate='${date}';state.selectedDate='${date}';
 state.remote.auth={...state.remote.auth,status:'authenticated',user:{id:'qa-admin',profileId:'qa-admin',role:'admin',displayName:'데모 QA 관리자',status:'active',mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
 for(const key of ['rooms','accounts','roomTypes','reservations','notifications','availability','complaints','payroll','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});
 state.remote.rooms.items=rooms;state.remote.roomProjection={date:'${date}',status:'ready',items:rooms};Object.assign(state.remote.homeAssignments,{date:'2026-10-31',status:'ready',items:[]});Object.assign(cleaningState(),{status:'ready'});syncAuthState(state);rawCloseModal();render();
 },home:()=>{state.liveView='today';render();},snapshot:()=>({filter:state.remote.rooms.filter,view:state.liveView}),
 replace:(rooms,date,status='ready')=>{state.remote.operationalDate=date;state.selectedDate=date;state.remote.roomProjection={date,status,items:rooms};render();},
 ${before?'':`due:liveRoomCheckoutDue,summary:liveCheckoutDueSummary,
 demo:(reservations,date,time)=>{const previous=[state.reservations,state.selectedDate,state.time];state.reservations=reservations;state.selectedDate=date;state.time=time;try{return roomCheckoutDue('211');}finally{[state.reservations,state.selectedDate,state.time]=previous;}}`}
 };`;
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},timezoneId:'America/New_York',serviceWorkers:'block',reducedMotion:'reduce'});
const page=await context.newPage(),errors=[],unexpected=[];page.setDefaultTimeout(7000);await page.clock.setFixedTime(new Date(now));
page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().includes('Service Worker registration blocked'))errors.push(m.text());});
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());
 if(url.origin===origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,hook)});if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});return route.continue();}
 const path=url.pathname.replace('/functions/v1/api','');
 if(req.method()==='GET'&&req.url().startsWith(api)){
  if(path==='/v1/room-pin-sheet-sync/status')return route.fulfill({json:{sync:{version:1,pending:0,failed:0,operatorBlocked:false,lastSuccessAt:now}}});
  if(path==='/v1/reservations')return route.fulfill({json:{reservations:[],nextCursor:null}});
  if(path==='/v1/rooms')return route.fulfill({json:{rooms,nextCursor:null}});
  if(path==='/v1/assignments/commit-impact')return route.fulfill({json:{impact:{serviceDate:url.searchParams.get('serviceDate'),committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}}});
  if(path==='/v1/assignments')return route.fulfill({json:{assignments:[],nextCursor:null}});
  if(path==='/v1/assignment-change-requests')return route.fulfill({json:{requests:[],nextCursor:null}});
  if(path==='/v1/inspections')return route.fulfill({json:{submissions:[],nextCursor:null}});
  const match=path.match(/^\/v1\/rooms\/(room-\d+)(?:\/(events|operation-blocks|issues|reports|candle-events|pin-sync))?$/);
  if(match){const room=rooms.find(r=>r.id===match[1]);return route.fulfill({json:!match[2]?{room}:match[2]==='pin-sync'?{pinSync:{status:'verified',version:1}}:match[2]==='candle-events'?{events:[]}:{roomId:room.id,roomStateVersion:1,items:[],nextCursor:null}});}
 }
 unexpected.push(req.method()+' '+path);return route.abort();
});
const action=name=>page.locator(`[data-action="${name}"]:visible`).first();
const shortcut=()=>page.locator('.checkout-due-shortcut[data-filter="checkout-due"]:visible');
const card=no=>page.locator(`[data-live-room="${no}"]`);
const shown=()=>page.locator('[data-live-room]').evaluateAll(es=>es.map(e=>e.dataset.liveRoom).sort());
async function shot(name){await page.screenshot({path:`${output}/checkout-due-${name}.png`});}
try{
 await mkdir(output,{recursive:true});await page.goto(origin+'/index.html');await page.evaluate(rooms=>__checkoutQA.setup(rooms),rooms);
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));await shot(`${before?'before':'after'}-${width}`);
 }
 if(before){console.log('[ok] Baseline: same admin, date, rooms and viewports');}
 else{
  assert.equal(await page.title(),'객실 현황 · CASTLE THE ART');assert.match(page.url(),/index.html/);
  assert.match(await shortcut().innerText(),/퇴실 예정 2개/);
  assert.equal(await page.locator('.checkout-due-badge').filter({hasText:'퇴실 예정'}).count(),2);
  assert.match(await card('350').innerText(),/운영 제한/);assert.match(await card('350').innerText(),/13:00/);
  for(const width of [360,390,768,1440]){
   await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));
   assert(await page.locator('#main-content').innerText());assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   assert(await shortcut().evaluate(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44&&!!e.getAttribute('aria-label');}));
   assert(await page.locator('.checkout-due-badge').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&e.scrollWidth<=e.clientWidth+1;})));
   await page.locator('[data-control="live-room-filter"]').selectOption('checkout-due');assert.deepEqual(await shown(),['211','350']);
   await page.locator('#live-room-search').fill('350');assert.deepEqual(await shown(),['350']);assert.match(await shortcut().innerText(),/2개/);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await shortcut().focus();await page.keyboard.press('Enter');assert.deepEqual(await shown(),['211','350']);assert.equal(await page.locator('#live-room-search').inputValue(),'');
   await page.waitForFunction(()=>document.activeElement?.dataset.control==='live-room-filter');
   await action('live-room-export').click();await page.getByRole('dialog').waitFor();await page.keyboard.press('Tab');assert(await page.getByRole('dialog').evaluate(e=>e.contains(document.activeElement)));await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});
   await page.waitForFunction(()=>document.activeElement?.dataset.action==='live-room-export');
   await action('live-room-export').click();await page.getByRole('dialog').waitFor();await page.goBack();await page.getByRole('dialog').waitFor({state:'hidden'});assert.equal((await page.evaluate(()=>__checkoutQA.snapshot())).filter,'checkout-due');
   await card('211').locator('[data-action="open-live-room-reservation-status"]').click();await page.getByRole('dialog').waitFor();assert.match(await page.getByRole('dialog').innerText(),/211호/);await page.keyboard.press('Escape');
   await card('211').locator('[data-action="open-live-room-detail"]').click();await page.getByRole('heading',{name:/211호/}).first().waitFor();await action('back').click();await card('211').waitFor();assert.deepEqual(await shown(),['211','350']);
   if([390,1440].includes(width)){await page.evaluate(()=>scrollTo(0,0));await shot(`filtered-${width}`);await card('211').scrollIntoViewIfNeeded();await shot(`card-${width}`);}
   await page.evaluate(()=>__checkoutQA.home());assert.equal(await page.locator('.today-summary > button').count(),4);assert.match(await shortcut().innerText(),/퇴실 예정 2개/);
   if([390,1440].includes(width)){await page.evaluate(()=>scrollTo(0,0));await shot(`home-${width}`);}
   await shortcut().click();assert.equal((await page.evaluate(()=>__checkoutQA.snapshot())).view,'rooms');assert.deepEqual(await shown(),['211','350']);
   await page.locator('[data-control="live-room-filter"]').selectOption('all');
  }
  console.log('[ok] 360/390/768/1440px: count/filter/search/home, existing destinations, keyboard/focus/modal/Back, overflow, 44px, accessible names');
  await page.locator('[data-action="filter-room-type"][data-type="premium"]').click();await page.locator('[data-control="live-room-filter"]').selectOption('checkout-due');assert.deepEqual(await shown(),['350']);assert.match(await shortcut().innerText(),/2개/);await shortcut().click();assert.deepEqual(await shown(),['211','350']);
  await action('live-room-export').click();await page.locator('#export-filtered').check();const downloaded=page.waitForEvent('download');await action('live-export-csv').click();const file=await downloaded;await file.saveAs('/tmp/rms-checkout-due.csv');const csv=await readFile('/tmp/rms-checkout-due.csv','utf8');assert.equal(csv.trim().split(/\r?\n/).length,3);assert(csv.includes('211')&&csv.includes('350')&&!csv.includes('516'));
  const due=async changes=>page.evaluate(room=>__checkoutQA.due(room),{...rooms[0],...changes});
  assert.equal(await due({evaluatedAt:date+'T10:59:59+09:00'}),true);
  assert.equal(await due({evaluatedAt:date+'T11:00:00+09:00'}),false);
  assert.equal(await due({evaluatedAt:date+'T12:00:00+09:00',displayCheckOutAt:date+'T13:00:00+09:00'}),true);
  assert.equal(await due({displayCheckOutAt:'2026-10-30T02:00:00Z'}),true);
  assert.equal(await due({displayCheckOutAt:'2026-10-30T15:00:00Z'}),false,'KST next day');
  assert.equal(await due({displayCheckOutAt:null}),false);
  assert.equal(await due({reservationPhase:'none',displayReservationId:null}),false,'cancelled/manual checkout removed from projection');
  assert.equal(await due({reservationPhase:'upcoming'}),false);
  assert.equal(await due({reservationPhase:undefined}),null);
  const future=rooms.map(r=>({...r,serviceDate:'2026-10-31',projectionMode:'FUTURE_START_OF_DAY',evaluatedAt:'2026-10-31T00:00:00+09:00',reservationPhase:['516','629'].includes(r.roomNumber)?'current':'none'}));
  await page.evaluate(rooms=>__checkoutQA.replace(rooms,'2026-10-31'),future);assert.match(await shortcut().innerText(),/2개/);await shortcut().click();assert.deepEqual(await shown(),['516','629']);
  const ended=rooms.map(r=>({...r,reservationPhase:'none',displayReservationId:null,displayCheckOutAt:null}));
  await page.evaluate(rooms=>__checkoutQA.replace(rooms,'2026-10-30'),ended);assert.match(await shortcut().innerText(),/0개/);assert.deepEqual(await shown(),[]);await action('clear-room-filters').click();assert.equal((await shown()).length,6);
  await page.evaluate(rooms=>__checkoutQA.replace(rooms,'2026-10-30','loading'),rooms);assert(await shortcut().isDisabled());assert.match(await shortcut().innerText(),/조회 중/);
  await page.evaluate(rooms=>__checkoutQA.replace(rooms,'2026-10-30'),rooms.map(r=>({...r,reservationPhase:undefined})));assert(await shortcut().isDisabled());assert.match(await shortcut().innerText(),/API 미제공/);await page.locator('[data-control="live-room-filter"]').selectOption('checkout-due');assert.match(await page.locator('.inline-empty').innerText(),/API 미제공/);
  const reservation={id:'qa-demo',room:'211',status:'active',checkInAt:'2026-08-14T16:00',checkOutAt:'2026-08-15T13:00'};
  const demo=async(r,day,time)=>page.evaluate(args=>__checkoutQA.demo(...args),[r,day,time]);
  assert.equal(await demo([reservation],'2026-08-15','12:00'),true);assert.equal(await demo([reservation],'2026-08-15','13:00'),false);
  assert.equal(await demo([{...reservation,status:'cancelled'}],'2026-08-15','10:00'),false);assert.equal(await demo([{...reservation,status:'checked-out'}],'2026-08-15','10:00'),false);
  assert.equal(await demo([{...reservation,isLongStay:true}],'2026-08-15','10:00'),true,'known long stay end');
  assert.equal(await demo([{...reservation,isLongStay:true,checkOutAt:'9999-12-31T23:59'}],'2026-08-15','10:00'),false,'unknown long stay end');
  assert.equal(await demo([{...reservation,checkOutAt:'2026-08-16T11:00'}],'2026-08-16','18:00'),true,'future is start of day');
  assert.equal(await demo([{...reservation,checkInAt:'2026-08-13T16:00',checkOutAt:'2026-08-14T11:00'}],'2026-08-14','10:00'),false,'past is end of day');
  console.log('[ok] type/search intersection and filtered CSV; checkout boundary, late checkout, KST/UTC dates, future/past, cancelled/manual checkout, unknown end, loading/missing contract/zero results');
  assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);console.log('[ok] console warning/error, page error, unexpected API requests: 0');
 }
}catch(error){console.error({state:await page.evaluate(()=>__checkoutQA.snapshot()),body:(await page.locator('#main-content').innerText()).slice(0,1800),errors,unexpected});await page.screenshot({path:'/tmp/checkout-due-failure.png'});throw error;}finally{await browser.close();}
