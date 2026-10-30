#!/usr/bin/env node
// Browser plugin not available. All API traffic is intercepted; no operational data is used.
import assert from 'node:assert/strict';
import {readFile, mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';

const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const date='2026-10-30',now=date+'T10:00:00+09:00';
const id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const roomId=id(1),typeId=id(2),reservationId=id(3);
const source=process.env.RMS_QA_BASE_REF?execFileSync('git',['show',process.env.RMS_QA_BASE_REF+':WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:8*1024*1024}):await readFile('WIREFRAME/index.html','utf8');
const boot='      void bootApplication();';assert.equal(source.split(boot).length,2);
const hook=`window.__refreshQA={setup:()=>{
 LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234'});
 state.remote=initialRemoteState();state.role='admin';state.liveView='rooms';state.detail=null;liveRoomDetail=null;state.remote.operationalDate='${date}';state.selectedDate='${date}';
 state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'qa-admin',role:'admin',displayName:'데모 QA 관리자',mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
 syncAuthState(state);render();return loadLiveViewData('rooms',{force:true});
 },get:()=>({projection:state.remote.roomProjection,detail:liveRoomDetail,rooms:state.remote.rooms}),
 date:date=>{state.remote.operationalDate=date;return loadLiveRoomProjection();},
 resetSession:()=>{LIVE_RUNTIME.authGeneration++;state.remote=initialRemoteState();state.loggedIn=false;render();}
};`;
const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const output='WIREFRAME/QA/screenshots';await mkdir(output,{recursive:true});

async function fixture({width=390,failProjection=false,delayProjection=60,delayCalendar=0}={}){
 const context=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block',timezoneId:'Asia/Seoul',reducedMotion:'reduce'});
 const page=await context.newPage(),errors=[],requests=[];let reservation=null,version=1,calendarPending=false;
 page.setDefaultTimeout(5000);await page.clock.setFixedTime(new Date(now));
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))errors.push(m.text());});
 const room=()=>{
  const active=reservation?.status==='active';
  return {id:roomId,roomNumber:'350',roomTypeId:typeId,roomTypeCode:'standard',roomTypeName:'스탠다드 더블 로프트',elevatorZone:'C',dataStatus:'verified',stateVersion:version,evaluatedAt:now,serverTime:now,occupied:false,occupancyStatus:'VACANT',reservationPhase:active?'upcoming':'none',reservationLifecycle:active?'ARRIVAL_PENDING':'NONE',readinessStatus:'READY',primaryDisplayStatus:active?'ARRIVAL_PENDING':'READY',allocationReady:true,allocationBlocked:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',blockingReasonCodes:[],readinessReasonCodes:[],reasonCodes:[],nextReservationId:active?reservation.id:null,nextCheckInAt:active?reservation.checkInAt:null,nextCheckOutAt:active?reservation.checkOutAt:null,displayReservationId:active?reservation.id:null,displayGuestCount:active?reservation.guestCount:null,displayBaseOccupancy:2,displayCheckInAt:active?reservation.checkInAt:null,displayCheckOutAt:active?reservation.checkOutAt:null};
 };
 await page.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url()),method=req.method();
  if(url.origin===origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,hook)});if(url.pathname==='/favicon.ico')return route.fulfill({status:204,body:''});return route.continue();}
  assert(req.url().startsWith(api),'Unexpected external request');
  const path=url.pathname.replace('/functions/v1/api',''),q=url.searchParams,payload=req.postDataJSON();requests.push({path,method,query:Object.fromEntries(q)});
  const reply=(json,status=200)=>route.fulfill({status,json,headers:{'x-request-id':'qa-reservation-refresh'}});
  if(path==='/v1/rooms'&&method==='GET'){
   const snapshot=room(),serviceDate=q.get('serviceDate');
   if(serviceDate){await sleep(version>1?delayProjection:10);if(failProjection&&version>1)return reply({error:{code:'QA_PROJECTION_FAILED'}},503);return reply({rooms:[{...snapshot,serviceDate,projectionMode:serviceDate===date?'LIVE':'FUTURE',detailConditionCodes:snapshot.displayGuestCount>2?['EXTRA_GUESTS']:[]}]});}
   return reply({rooms:[snapshot]});
  }
  if(path===`/v1/rooms/${roomId}`&&method==='GET')return reply({room:room()});
  if(path==='/v1/room-types')return reply({items:[{id:typeId,code:'standard',displayName:'스탠다드',baseOccupancy:2,maxOccupancy:4,active:true,version:1}]});
  if(path==='/v1/reservations'&&method==='GET'){
   if(q.has('from')&&version>1){calendarPending=true;await sleep(delayCalendar);calendarPending=false;}
   return reply({reservations:reservation?[reservation]:[],nextCursor:null,serverTime:now});
  }
  if(path===`/v1/reservations/${reservationId}`&&method==='GET')return reply({reservation});
  if(path==='/v1/reservations/bookability/preview')return reply({preview:{...payload,evaluatedAt:now,commitAuthority:'CREATE_OR_CHANGE_REVALIDATES',candidates:[{roomId,roomNumber:'350',roomTypeId:typeId,roomStateVersion:version,intervalBookable:true,checkInReady:true,reasonCodes:[],evaluatedAt:now}]}});
  if((path==='/v1/reservations'&&method==='POST')||(path===`/v1/reservations/${reservationId}`&&method==='PATCH')){
   const {guestName,expectedRoomVersion,expectedVersion,...fields}=payload;
   version++;reservation={...fields,id:reservationId,status:'active',version,actualCheckInAt:null,actualCheckoutAt:null,createdAt:now,updatedAt:now};return reply({reservation});
  }
  if(path===`/v1/reservations/${reservationId}/cancel`&&method==='POST'){version++;reservation={...reservation,status:'cancelled',version,cancelledAt:now};return reply({reservation});}
  if(path==='/v1/assignments')return reply({assignments:[]});
  if(path==='/v1/assignments/commit-impact')return reply({impact:{serviceDate:q.get('serviceDate'),committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}});
  if(path==='/v1/notifications')return reply({notifications:[],nextCursor:null});
  if(path===`/v1/rooms/${roomId}/candle-events`)return reply({events:[]});
  if(['events','operation-blocks','issues','reports'].some(kind=>path===`/v1/rooms/${roomId}/${kind}`))return reply({roomId,roomStateVersion:version,items:[],nextCursor:null});
  if(path===`/v1/rooms/${roomId}/pin-sync`)return reply({pinSync:{status:'verified',version:1}});
  throw new Error(`Unexpected fixture request: ${method} ${path}`);
 });
 await page.goto(origin+'/index.html');await page.evaluate(()=>__refreshQA.setup());
 const card=()=>page.locator('[data-live-room="350"]');
 const action=name=>page.locator(`[data-action="${name}"]:visible`).first();
 async function create(){
  await card().locator('[data-action="open-live-room-reservation-status"]').click();
  await action('open-live-reservation-create').click();
  await page.locator('#live-reservation-checkin').fill(date+'T16:00');
  await page.locator('#live-reservation-checkout').fill('2026-10-31T11:00');
  await page.getByText('350호 선택 기간 예약 가능',{exact:true}).waitFor();
  await action('submit-live-reservation-create').click();await page.getByRole('dialog').waitFor({state:'hidden'});
 }
 return {page,card,action,create,requests,get calendarPending(){return calendarPending;},async close(){assert.deepEqual(errors,[]);await context.close();}};
}

try{
 if(process.env.RMS_QA_BASE_REF){
  for(const width of [390,1440]){
   const f=await fixture({width});await f.page.locator('#live-room-search').fill('350');await f.create();await sleep(2500);
   assert.match(await f.card().innerText(),/배정 가능/);assert.match(await f.card().innerText(),/예약 현황 · 1건/);
   await f.page.evaluate(()=>scrollTo(0,0));await f.page.screenshot({path:`${output}/reservation-refresh-before-${width}.png`});await f.close();
  }
  console.log('[ok] Baseline reproduces stale card after successful booking and completed background reads');
 }else{
 for(const width of [360,390,768,1440]){
  const f=await fixture({width,delayCalendar:1800}),{page,card,action}=f;
  assert.equal(await page.title(),'객실 현황 · CASTLE THE ART');assert(await page.locator('#main-content').innerText());assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);
  await page.locator('#live-room-search').fill('350');
  await f.create();
  await page.waitForFunction(()=>__refreshQA.get().projection?.status==='ready'&&document.querySelector('[data-live-room="350"]')?.textContent.includes('입실 예정'),{},{timeout:1200});
  assert(f.calendarPending,'Card should update before the slow calendar read completes');
  assert.equal(await page.locator('#live-room-search').inputValue(),'350');
  assert.match(await card().innerText(),/10\. 30\. 16:00/);
  if([390,1440].includes(width)){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:`${output}/reservation-refresh-after-${width}.png`});}
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  for(const button of await card().locator('button').all()){const box=await button.boundingBox();if(box)assert(box.width>=44&&box.height>=44);assert(await button.getAttribute('aria-label')||await button.innerText());}
  await sleep(1900);
  await card().locator('[data-action="open-live-room-detail"]').click();await page.getByText('350호 현재 상태',{exact:true}).waitFor();
  await page.getByRole('button',{name:'예약 관리',exact:true}).first().click();await page.getByText('350호 예약 상세·변경',{exact:true}).waitFor();
  await page.getByRole('button',{name:'예약 인원수 1명 늘리기'}).click();await page.getByText('350호 선택 기간 예약 가능',{exact:true}).waitFor();
  await action('submit-live-reservation-update').click();await page.getByRole('dialog').waitFor({state:'hidden'});
  await page.waitForFunction(()=>__refreshQA.get().detail?.displayGuestCount===3);
  await action('back').click();await page.waitForFunction(()=>document.querySelector('[data-live-room="350"]')?.textContent.includes('1인 추가'));
  await sleep(1900);
  await card().locator('[data-action="open-live-room-reservation-status"]').focus();await page.keyboard.press('Enter');await action('open-live-reservation-detail').click();await page.getByText('350호 예약 상세·변경',{exact:true}).waitFor();
  await page.keyboard.press('Tab');assert(await page.getByRole('dialog').evaluate(el=>el.contains(document.activeElement)));
  await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});
  await card().locator('[data-action="open-live-room-reservation-status"]').click();await action('open-live-reservation-detail').click();await page.getByText('350호 예약 상세·변경',{exact:true}).waitFor();
  await action('live-reservation-cancel-review').click();await action('confirm-live-reservation-cancel').click();
  await page.waitForFunction(()=>document.querySelector('[data-live-room="350"]')?.textContent.includes('입실 가능'));
  assert.equal(await card().locator('.guests').count(),0);assert(!((await card().innerText()).includes('입실 예정')));
  assert.equal(f.requests.filter(r=>r.path==='/v1/reservations'&&r.method==='POST').length,1);
  await sleep(1900);await f.close();console.log(`[ok] ${width}px: create → card, edit → detail/list, cancel → card, search, keyboard/modal, back, overflow, controls, console`);
 }
 const failure=await fixture({failProjection:true});await failure.create();await failure.page.getByRole('button',{name:'다시 조회',exact:true}).waitFor();assert.equal((await failure.page.evaluate(()=>__refreshQA.get())).projection.status,'error');await failure.close();console.log('[ok] Projection failure shows retry instead of keeping the old ready snapshot');
 const race=await fixture({delayProjection:550});await race.create();await race.page.evaluate(()=>__refreshQA.date('2026-10-31'));await sleep(700);assert.equal((await race.page.evaluate(()=>__refreshQA.get())).projection.date,'2026-10-31');await race.close();console.log('[ok] Date change while refreshing retains the selected date');
 const session=await fixture({delayProjection:550});await session.create();await session.page.evaluate(()=>__refreshQA.resetSession());await sleep(800);assert.equal((await session.page.evaluate(()=>__refreshQA.get())).rooms.items.length,0);await session.close();console.log('[ok] Late responses after session change do not restore room data');
 }
 console.log(`Playwright Chromium ${await browser.version()}; ${origin}; Browser plugin not available; synthetic API fixtures only.`);
}finally{await browser.close();}
