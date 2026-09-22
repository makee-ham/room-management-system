#!/usr/bin/env node
// Browser performance regression for live navigation, lazy reads, request coalescing, and immediate modal feedback.
// Every API request is intercepted by local fixtures; production data is never read or changed.
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';

const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4182';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const ids={admin:'10000000-0000-4000-8000-000000000001',maid1:'10000000-0000-4000-8000-000000000002',maid2:'10000000-0000-4000-8000-000000000003',room:'30000000-0000-4000-8000-000000000001',type:'20000000-0000-4000-8000-000000000001',reservation:'40000000-0000-4000-8000-000000000001'};
const now='2026-09-22T10:00:00+09:00',checkIn='2026-09-23T16:00:00+09:00',checkOut='2026-09-24T11:00:00+09:00';
const room={id:ids.room,roomNumber:'350',roomTypeCode:'standard',roomTypeName:'스탠다드',roomTypeId:ids.type,elevatorZone:'C',dataStatus:'verified',stateVersion:1,evaluatedAt:now,serverTime:now,reservationPhase:'upcoming',occupancyStatus:'VACANT',reservationLifecycle:'RESERVATION_PRESENT',readinessStatus:'READY',primaryDisplayStatus:'RESERVATION_PRESENT',nextReservationId:ids.reservation,nextCheckInAt:checkIn,nextCheckOutAt:checkOut,blockingReasonCodes:[],readinessReasonCodes:[],occupied:false,cleaningRequired:false,candleCount:1,pinSyncStatus:'verified',allocationBlocked:false,allocationReady:true,reasonCodes:[]};
const reservation={id:ids.reservation,roomId:ids.room,reservationType:'standard',checkInAt:checkIn,checkOutAt:checkOut,guestCount:2,status:'active',version:3,actualCheckInAt:null,actualCheckoutAt:null,cancelledAt:null,createdAt:now,updatedAt:now};
const roomTypes=[{id:ids.type,code:'standard',displayName:'스탠다드',baseCleaningFee:16000,baseOccupancy:2,maxOccupancy:2,active:true,version:1,roomCount:1}];
const accounts=[{id:ids.maid1,displayName:'메이드 A',role:'maid',status:'active'},{id:ids.maid2,displayName:'메이드 B',role:'maid',status:'active'}];
const source=await readFile(resolve('WIREFRAME/index.html'),'utf8');
const html=source
  .replace('      function render() {','      function render() { window.__PERF_FULL_RENDER_COUNT=(window.__PERF_FULL_RENDER_COUNT||0)+1;')
  .replace('\n      void bootApplication();',`window.__performanceQA={setup:view=>{localStorage.clear();sessionStorage.clear();LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.authGeneration+=1;LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',sessionPersistence:'session',deploymentChannel:'preview',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${ids.admin}',displayName:'성능 QA 관리자',role:'admin',mustChangePassword:false},session:{accessToken:'qa-access-token',refreshToken:'qa-refresh-token',expiresAt:Date.now()+3600000}};state.role='admin';state.liveView=view;syncAuthState(state);render();},load:(view,options={})=>{state.liveView=view;return loadLiveViewData(view,options);},reset:()=>{window.__PERF_FULL_RENDER_COUNT=0;},get:()=>({fullRenders:window.__PERF_FULL_RENDER_COUNT||0,view:state.liveView,rooms:state.remote.rooms.status,reservations:state.remote.reservations.status,roomTypes:state.remote.roomTypes.status,accounts:state.remote.accounts.status,availability:state.remote.availability.status,workHistory:state.remote.workHistory.status,detailVersion:liveRoomDetail?.stateVersion||null})};`);

const requests=[];
const sleep=ms=>new Promise(resolveDelay=>setTimeout(resolveDelay,ms));
const json=(route,value,status=200)=>route.fulfill({status,contentType:'application/json',headers:{'x-request-id':'qa-performance'},body:JSON.stringify(value)});
const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(5000);const pageErrors=[],consoleProblems=[];
page.on('pageerror',error=>pageErrors.push(error.message));
page.on('console',message=>{if(['warning','error'].includes(message.type())&&!/^Failed to load resource:/.test(message.text()))consoleProblems.push(message.text());});
await page.route('**/favicon.ico',route=>route.fulfill({status:204,body:''}));
await page.route('**/index.html*',route=>route.fulfill({status:200,contentType:'text/html',body:html}));
await page.route(`${api}/**`,async route=>{
  const request=route.request(),url=new URL(request.url()),path=url.pathname.replace('/functions/v1/api',''),method=request.method();requests.push({method,path,url:request.url()});
  await sleep(path.startsWith('/v1/reservations/')||path==='/v1/reservations/bookability/preview'||path.startsWith('/v1/rooms/')?180:90);
  if(method==='GET'&&path==='/v1/notifications')return json(route,{notifications:[],nextCursor:null});
  if(method==='GET'&&path==='/v1/rooms')return json(route,{rooms:[room]});
  if(method==='GET'&&path===`/v1/rooms/${ids.room}`)return json(route,{room:{...room,stateVersion:2}});
  if(method==='GET'&&path==='/v1/room-types')return json(route,{items:roomTypes});
  if(method==='GET'&&path==='/v1/reservations'){const roomId=url.searchParams.get('roomId');return json(route,{reservations:roomId?[reservation]:[reservation],nextCursor:null,serverTime:now});}
  if(method==='GET'&&path===`/v1/reservations/${ids.reservation}`)return json(route,{reservation:{...reservation,guestName:'로컬 QA 고객'}});
  if(method==='POST'&&path==='/v1/reservations/bookability/preview')return json(route,{preview:{reservationType:'standard',checkInAt:checkIn,checkOutAt:checkOut,guestCount:2,excludeReservationId:ids.reservation,evaluatedAt:now,commitAuthority:'CREATE_OR_CHANGE_REVALIDATES',candidates:[{roomId:ids.room,roomNumber:'350',roomTypeId:ids.type,roomStateVersion:2,intervalBookable:true,checkInReady:true,reasonCodes:[],evaluatedAt:now}]}});
  if(method==='GET'&&path==='/v1/payroll')return json(route,{payroll:[],nextCursor:null});
  if(method==='GET'&&path==='/v1/assignments')return json(route,{assignments:[]});
  if(method==='GET'&&path==='/v1/assignment-change-requests')return json(route,{requests:[]});
  if(method==='GET'&&path==='/v1/inspections')return json(route,{submissions:[]});
  if(method==='GET'&&path==='/v1/accounts')return json(route,{accounts});
  if(method==='GET'&&path==='/v1/availability')return json(route,{availability:[]});
  if(method==='GET'&&path==='/v1/availability/change-requests')return json(route,{changeRequests:[]});
  if(method==='GET'&&path==='/v1/work-history')return json(route,{items:[],nextCursor:null,weekStart:'2026-09-21',weekEnd:'2026-09-27',summary:null});
  if(method==='GET'&&path==='/v1/complaints')return json(route,{complaints:[],nextCursor:null});
  return json(route,{error:{code:'QA_ROUTE_MISSING',message:`Missing ${method} ${path}`},requestId:'qa-missing'},404);
});

const passed=[];
try{
  await page.goto(`${origin}/index.html`);await page.evaluate(()=>window.__performanceQA.setup('today'));assert((await page.title()).includes('오늘 할 일'));assert((await page.locator('#main-content').innerText()).trim().length>0);assert.equal(await page.locator('nextjs-portal,[data-vite-dev-id],vite-error-overlay').count(),0);

  requests.length=0;await page.evaluate(()=>window.__performanceQA.reset());await page.evaluate(()=>window.__performanceQA.load('today'));
  const initialPaths=requests.map(item=>item.path);assert(initialPaths.includes('/v1/rooms'));assert(initialPaths.includes('/v1/payroll'));assert(initialPaths.includes('/v1/assignments'));assert(!initialPaths.includes('/v1/accounts'));assert(!initialPaths.includes('/v1/room-types'));assert(!initialPaths.includes('/v1/reservations'));assert(!initialPaths.includes('/v1/availability'));assert(!initialPaths.includes('/v1/complaints'));assert(!initialPaths.includes('/v1/cleaning-history'));assert(!initialPaths.includes('/v1/work-history'));assert.equal(new Set(requests.map(item=>item.url)).size,requests.length);assert.equal((await page.evaluate(()=>window.__performanceQA.get())).fullRenders,0);passed.push(`현재 화면 우선 로드 · 관리자 첫 화면 ${requests.length}건 · 비관련·중복 API 0건`);

  requests.length=0;await page.evaluate(()=>{window.__performanceQA.reset();document.querySelector('.sidebar').dataset.performanceMarker='preserved';});
  const navigationMs=await page.evaluate(async()=>{const start=performance.now();document.querySelector('[data-action="nav"][data-view="rooms"]').click();await new Promise(resolveFrame=>requestAnimationFrame(()=>requestAnimationFrame(resolveFrame)));return performance.now()-start;});
  await page.locator('[data-live-room="350"]').waitFor();await page.waitForFunction(()=>window.__performanceQA.get().roomTypes==='ready'&&window.__performanceQA.get().reservations==='ready');
  assert.equal(await page.locator('.sidebar').getAttribute('data-performance-marker'),'preserved');assert.equal((await page.evaluate(()=>window.__performanceQA.get())).fullRenders,0);assert(navigationMs<250,`navigation feedback took ${navigationMs.toFixed(1)}ms`);assert.deepEqual([...new Set(requests.map(item=>item.path))].sort(),['/v1/reservations','/v1/room-types']);passed.push(`화면 전환 ${navigationMs.toFixed(1)}ms · 앱 shell 유지 · 전체 렌더 0회`);

  requests.length=0;await page.locator('[data-live-room="350"] [data-action="open-live-room-detail"]').click();await page.getByText('350호 현재 상태',{exact:true}).waitFor({timeout:120});await page.waitForFunction(()=>window.__performanceQA.get().detailVersion===2);assert.equal(requests.filter(item=>item.path===`/v1/rooms/${ids.room}`).length,1);assert.equal(requests.filter(item=>item.path==='/v1/reservations').length,1);passed.push('객실 상세는 캐시 화면을 즉시 표시하고 최신 상세·예약을 병렬 1회 조회');

  requests.length=0;await page.getByRole('button',{name:'예약 관리',exact:true}).first().click();await page.getByText('예약 상세 불러오는 중',{exact:true}).waitFor({timeout:120});await page.getByText('350호 예약 상세·변경',{exact:true}).waitFor();assert.equal(requests.filter(item=>item.path===`/v1/reservations/${ids.reservation}`).length,1);assert.equal(requests.filter(item=>item.path==='/v1/reservations/bookability/preview').length,1);passed.push('예약 모달은 네트워크 완료 전 즉시 열리고 단건 조회→기간 판정으로 갱신');
  await mkdir(resolve('WIREFRAME/QA/screenshots'),{recursive:true});await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-performance-modal-390.png'),fullPage:false});await page.setViewportSize({width:1440,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-performance-modal-1440.png'),fullPage:false});

  await page.locator('[data-action="close-modal"]').last().click();await page.waitForFunction(()=>!document.querySelector('#modal-root .modal'));requests.length=0;await page.evaluate(()=>{window.__performanceQA.reset();return Promise.all([window.__performanceQA.load('maids',{force:true}),window.__performanceQA.load('maids',{force:true}),window.__performanceQA.load('maids',{force:true})]);});
  const urls=requests.map(item=>item.url);assert.equal(new Set(urls).size,urls.length,'동일 GET 요청이 중복 전송됨');assert.equal(requests.filter(item=>item.path==='/v1/accounts').length,1);assert.equal(requests.filter(item=>item.path==='/v1/work-history').length,1);assert.equal(requests.filter(item=>item.path==='/v1/availability').length,2);assert.equal(requests.filter(item=>item.path==='/v1/availability/change-requests').length,1);assert.equal((await page.evaluate(()=>window.__performanceQA.get())).fullRenders,0);passed.push('동시 화면 로드 3회 coalescing · 동일 URL 중복 0건 · 계정 후 가능일 조회');

  assert.deepEqual(pageErrors,[]);assert.deepEqual(consoleProblems,[]);passed.push('페이지 예외·console warning/error 0건');
  passed.forEach(item=>console.log(`[ok] ${item}`));console.log(`Environment: Chromium ${await browser.version()} via Playwright; Browser plugin unavailable. All API traffic was intercepted by delayed local fixtures.`);
}catch(error){console.error('requests',requests.map(item=>`${item.method} ${item.url}`));console.error('page errors',pageErrors);console.error('console problems',consoleProblems);await page.screenshot({path:'/tmp/room-performance-failure.png',fullPage:true});throw error;}finally{await browser.close();}
