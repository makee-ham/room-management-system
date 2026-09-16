#!/usr/bin/env node

import assert from 'node:assert/strict';
import {mkdir, readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';

const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4175';
const source=await readFile(resolve('WIREFRAME/index.html'),'utf8');
const evaluatedAt='2026-09-16T08:00:00.000Z';
const rooms=[
  {id:'10000000-0000-4000-8000-000000000001',roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:1,evaluatedAt,reservationPhase:'current',occupied:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',allocationBlocked:true,allocationReady:false,reasonCodes:['RESERVATION_CURRENT']},
  {id:'10000000-0000-4000-8000-000000000002',roomNumber:'350',roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'C',dataStatus:'verified',stateVersion:2,evaluatedAt,reservationPhase:'none',occupied:false,cleaningRequired:true,candleCount:0,pinSyncStatus:'verified',allocationBlocked:true,allocationReady:false,reasonCodes:['CLEANING_REQUIRED']},
  {id:'10000000-0000-4000-8000-000000000003',roomNumber:'516',roomTypeCode:'oceanPremium',roomTypeName:'파셜 오션뷰',elevatorZone:'A',dataStatus:'verified',stateVersion:3,evaluatedAt,reservationPhase:'upcoming',occupied:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',allocationBlocked:false,allocationReady:true,reasonCodes:[]},
  {id:'10000000-0000-4000-8000-000000000004',roomNumber:'629',roomTypeCode:'oceanFamily',roomTypeName:'패밀리 투룸',elevatorZone:'C',dataStatus:'verified',stateVersion:4,evaluatedAt,reservationPhase:'none',occupied:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',allocationBlocked:false,allocationReady:true,reasonCodes:[]},
  {id:'10000000-0000-4000-8000-000000000005',roomNumber:'632',roomTypeCode:'premium',roomTypeName:'프리미어',elevatorZone:'B',dataStatus:'verification_required',stateVersion:5,evaluatedAt,reservationPhase:'none',occupied:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'unconfigured',allocationBlocked:true,allocationReady:false,reasonCodes:['DATA_UNCONFIRMED']},
];
const reservations=[
  {id:'20000000-0000-4000-8000-000000000001',roomId:rooms[0].id,checkInAt:'2026-09-16T16:00:00+09:00',checkOutAt:'2026-09-17T11:00:00+09:00',guestCount:2,status:'active',version:1,actualCheckInAt:null,actualCheckoutAt:null},
  {id:'20000000-0000-4000-8000-000000000002',roomId:rooms[2].id,checkInAt:'2026-09-20T16:00:00+09:00',checkOutAt:'2026-09-21T11:00:00+09:00',guestCount:2,status:'active',version:1,actualCheckInAt:null,actualCheckoutAt:null},
  {id:'20000000-0000-4000-8000-000000000003',roomId:rooms[0].id,checkInAt:'2026-09-22T16:00:00+09:00',checkOutAt:'2026-09-23T11:00:00+09:00',guestCount:2,status:'active',version:1,actualCheckInAt:null,actualCheckoutAt:null},
];
const html=source.replace('\n      void bootApplication();',`window.__roomCurrentStatusQA={setup(){LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',sessionPersistence:'session'});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'30000000-0000-4000-8000-000000000001',displayName:'QA 관리자',role:'admin',mustChangePassword:false},session:{accessToken:'qa-access-token',refreshToken:'qa-refresh-token',expiresAt:Date.now()+3600000}};state.remote.rooms={...state.remote.rooms,status:'ready',items:${JSON.stringify(rooms)},lastSuccessAt:'${evaluatedAt}'};state.remote.reservations={...state.remote.reservations,status:'ready',items:${JSON.stringify(reservations)},lastSuccessAt:'${evaluatedAt}'};state.role='admin';state.liveView='today';syncAuthState(state);render();},view(view,filter='all'){liveRoomDetail=null;state.liveView=view;state.remote.rooms.filter=filter;render();},detail(roomId){liveRoomDetail=(state.remote.rooms.items||[]).find(room=>room.id===roomId)||null;state.liveView='rooms';render();},primary(room){return liveRoomPrimary(room);},primaryReservation(room){return livePrimaryReservation(room);},counts(){return liveRoomPrimaryCounts(state.remote.rooms.items);}};`);

const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
const pageErrors=[],consoleProblems=[];
page.on('pageerror',error=>pageErrors.push(error.message));
page.on('console',message=>{if(['warning','error'].includes(message.type())&&!/^Failed to load resource:/.test(message.text()))consoleProblems.push(message.text());});
await page.route('**/favicon.ico',route=>route.fulfill({status:204,body:''}));
await page.route('**/index.html*',route=>route.fulfill({status:200,contentType:'text/html',body:html}));

try{
  await page.goto(`${origin}/index.html`);
  await page.evaluate(()=>window.__roomCurrentStatusQA.setup());
  assert.deepEqual(await page.evaluate(()=>window.__roomCurrentStatusQA.counts()),{upcoming:1,occupied:1,cleaning:1,ready:1,blocked:1});
  const summary=page.locator('.live-room-summary .metric-card');
  assert.equal(await summary.count(),5);
  assert.deepEqual(await summary.locator('span').allTextContents(),['투숙 예정','투숙 중','청소 필요','배정 가능','배정 불가']);
  await page.locator('[data-action="filter-rooms"][data-filter="upcoming"]').click();
  assert.equal(await page.locator('#live-room-filter').inputValue(),'upcoming');
  assert.equal(await page.locator('[data-live-room]').count(),1);
  assert.equal(await page.locator('[data-live-room]').getAttribute('data-live-room'),'516');
  await page.evaluate(()=>window.__roomCurrentStatusQA.view('rooms','all'));
  const statusByRoom={};
  for(const room of rooms)statusByRoom[room.roomNumber]=await page.locator(`[data-live-room="${room.roomNumber}"] .concept-status-copy strong`).innerText();
  assert.deepEqual(statusByRoom,{'211':'투숙 중','350':'청소 필요','516':'투숙 예정','629':'배정 가능','632':'배정 불가'});
  assert.equal(await page.locator('#live-room-filter option[value="upcoming"]').count(),1);
  await page.locator('#live-room-filter').selectOption('upcoming');
  assert.equal(await page.locator('[data-live-room]').count(),1);
  assert.equal(await page.locator('[data-live-room]').getAttribute('data-live-room'),'516');
  assert.equal(await page.locator('[data-live-room="516"] .concept-status-copy strong').innerText(),'투숙 예정');
  assert.equal(await page.evaluate(room=>window.__roomCurrentStatusQA.primaryReservation(room)?.id,rooms[0]),reservations[0].id);
  await page.evaluate(roomId=>window.__roomCurrentStatusQA.detail(roomId),rooms[2].id);
  assert(await page.getByText('미래 예약은 투숙 예정이며 현재 청소 필요로 전환하지 않습니다.',{exact:true}).isVisible());
  assert.equal(await page.getByText('투숙 예정',{exact:true}).count()>=1,true);
  const mapperCases=await page.evaluate(()=>[
    window.__roomCurrentStatusQA.primary({reservationPhase:'current',occupied:false,cleaningRequired:false,allocationReady:false}),
    window.__roomCurrentStatusQA.primary({reservationPhase:'upcoming',occupied:false,cleaningRequired:true,allocationReady:false}),
    window.__roomCurrentStatusQA.primary({reservationPhase:'upcoming',occupied:false,cleaningRequired:false,allocationReady:true}),
    window.__roomCurrentStatusQA.primary({reservationPhase:'none',occupied:false,cleaningRequired:false,allocationReady:false}),
  ].map(item=>item.key));
  assert.deepEqual(mapperCases,['occupied','cleaning','upcoming','blocked']);
  await mkdir(resolve('WIREFRAME/QA/screenshots'),{recursive:true});
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:1000});
    await page.evaluate(()=>{window.__roomCurrentStatusQA.view('rooms','all');window.scrollTo(0,0);});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`room status overflow at ${width}`);
  }
  await page.setViewportSize({width:390,height:900});
  await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-room-current-status-390.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-room-current-status-1440.png'),fullPage:true});
  assert.deepEqual(pageErrors,[]);
  assert.deepEqual(consoleProblems,[]);
  console.log('Current room status browser regression: passed');
}finally{
  await browser.close();
}
