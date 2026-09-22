#!/usr/bin/env node
// Browser regression for the live room candle stepper. Every API request is intercepted locally.
import assert from 'node:assert/strict';
import {mkdir,readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';

const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4190';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const roomId='30000000-0000-4000-8000-000000000352',roomTypeId='20000000-0000-4000-8000-000000000001';
const evaluatedAt='2026-09-22T10:00:00+09:00';
const roomFixture={id:roomId,roomNumber:'352',roomTypeId,roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:2,evaluatedAt,serverTime:evaluatedAt,occupancyStatus:'VACANT',reservationPhase:'none',reservationLifecycle:'NONE',readinessStatus:'READY',primaryDisplayStatus:'READY',nextReservationId:null,nextCheckInAt:null,nextCheckOutAt:null,blockingReasonCodes:[],readinessReasonCodes:[],reasonCodes:[],occupied:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',pinVersion:1,allocationBlocked:false,allocationReady:true};
const roomTypeFixture={id:roomTypeId,code:'standard',displayName:'스탠다드',baseCleaningFee:16000,baseOccupancy:2,maxOccupancy:2,active:true,version:1,roomCount:1};
let serverRoom={...roomFixture},failNextDecrement=false;
const requests=[];

const source=await readFile(resolve('WIREFRAME/index.html'),'utf8');
const html=source.replace('\n      void bootApplication();',`\n      window.__candleQA={setup:()=>{localStorage.clear();sessionStorage.clear();LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',sessionPersistence:'session',deploymentChannel:'preview',featureFlags:{optionalCleaningWorkflow:false}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'10000000-0000-4000-8000-000000000001',displayName:'QA 관리자',role:'admin',mustChangePassword:false},session:{accessToken:'qa-access-token',refreshToken:'qa-refresh-token',expiresAt:Date.now()+3600000}};state.remote.accounts={...state.remote.accounts,status:'ready',items:[]};state.remote.rooms={...state.remote.rooms,status:'ready',items:[window.__QA_ROOM],lastSuccessAt:new Date().toISOString()};state.remote.roomTypes={...state.remote.roomTypes,status:'ready',items:[window.__QA_ROOM_TYPE]};state.remote.reservations={...state.remote.reservations,status:'ready',items:[]};state.remote.availability={...state.remote.availability,status:'ready',items:[],changeRequests:[]};state.role='admin';state.liveView='rooms';syncAuthState(state);liveRoomDetail=state.remote.rooms.items[0];render();},snapshot:()=>({room:liveRoomDetail,uncertain:!!uncertainLiveMutation})};`);
assert.notEqual(html,source,'QA hook replaced application boot');

const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(12000);
const pageErrors=[],consoleProblems=[];
page.on('pageerror',error=>pageErrors.push(error.message));
page.on('console',message=>{if(['warning','error'].includes(message.type())&&!/^Failed to load resource:/.test(message.text()))consoleProblems.push(message.text());});
await page.addInitScript(({room,roomType})=>{window.__QA_ROOM=room;window.__QA_ROOM_TYPE=roomType;},{room:roomFixture,roomType:roomTypeFixture});
await page.route('**/favicon.ico',route=>route.fulfill({status:204,body:''}));
await page.route('**/index.html*',route=>route.fulfill({status:200,contentType:'text/html',body:html}));
await page.route(`${api}/**`,async route=>{
  const request=route.request(),url=new URL(request.url()),path=url.pathname.replace('/functions/v1/api',''),method=request.method(),payload=request.postData()?JSON.parse(request.postData()):null,idempotencyKey=request.headers()['idempotency-key']||'';
  requests.push({path,method,payload,idempotencyKey});
  const json=(value,status=200)=>route.fulfill({status,contentType:'application/json',headers:{'x-request-id':`qa-candle-${requests.length}`},body:JSON.stringify(value)});
  if(method==='GET'&&path==='/v1/rooms')return json({rooms:[serverRoom]});
  if(method==='POST'&&path===`/v1/rooms/${roomId}/candles`){
    assert(idempotencyKey,'candle mutation requires an idempotency key');
    if(failNextDecrement){failNextDecrement=false;serverRoom={...serverRoom,candleCount:3,stateVersion:serverRoom.stateVersion+1};return json({error:{code:'STALE_VERSION',message:'stale fixture'},requestId:'qa-candle-stale'},409);}
    assert.equal(payload.expectedRoomVersion,serverRoom.stateVersion,'candle mutation uses the latest room version');
    if(payload.count<serverRoom.candleCount&&!payload.physicallyVerified)return json({error:{code:'VALIDATION_ERROR',message:'physical verification required'},requestId:'qa-candle-verify'},422);
    serverRoom={...serverRoom,candleCount:payload.count,stateVersion:serverRoom.stateVersion+1};return json({room:serverRoom,event:{id:`event-${requests.length}`}});
  }
  return json({error:{code:'QA_ROUTE_MISSING',message:`Missing ${method} ${path}`},requestId:'qa-missing'},404);
});

const candlePosts=()=>requests.filter(item=>item.method==='POST'&&item.path.endsWith('/candles'));
const group=page.getByRole('group',{name:'352호 관리자 촛불 수량'});
const plus=page.getByRole('button',{name:'촛불 1개 늘리기'}),minus=page.getByRole('button',{name:'촛불 1개 줄이기'});
const waitCount=count=>group.getByText(`${count}개`,{exact:true}).waitFor();
const modalTitle=()=>page.getByText('352호 촛불 수량 기록',{exact:true});

try{
  await mkdir(resolve('WIREFRAME/QA/screenshots'),{recursive:true});
  await page.goto(`${origin}/index.html?role=admin&view=rooms`,{waitUntil:'domcontentloaded'});await page.evaluate(()=>window.__candleQA.setup());
  assert.equal(new URL(page.url()).origin,new URL(origin).origin,'page identity uses the requested QA origin');assert((await page.title()).trim().length>0,'page title is present');
  await page.getByText('352호 객실 상세',{exact:true}).waitFor();await waitCount(0);assert.equal(await page.locator('nextjs-portal, vite-error-overlay, webpack-dev-server-client-overlay').count(),0,'framework overlay is absent');

  for(const width of [390,1440]){await page.setViewportSize({width,height:width===390?900:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`room detail has no horizontal overflow at ${width}px`);const sizes=await group.getByRole('button').evaluateAll(buttons=>buttons.map(button=>({width:button.getBoundingClientRect().width,height:button.getBoundingClientRect().height})));assert(sizes.every(size=>size.width>=44&&size.height>=44),`candle buttons are at least 44px at ${width}px`);}
  await page.setViewportSize({width:390,height:900});

  await plus.click();await waitCount(1);assert.equal(candlePosts().length,1);assert.deepEqual(candlePosts()[0].payload,{expectedRoomVersion:2,reasonCode:'ADMIN_ROOM_STATE_UPDATED',count:1,physicallyVerified:false});
  await plus.click();await waitCount(2);assert.equal(candlePosts().length,2);assert.equal(candlePosts()[1].payload.expectedRoomVersion,3);assert.equal(candlePosts()[1].payload.count,2);await page.locator('#toast-region').evaluate(node=>node.replaceChildren());

  await minus.focus();await minus.press('Enter');await modalTitle().waitFor();assert.equal(await page.locator('#live-room-candle-count').inputValue(),'1');assert.equal(candlePosts().length,2,'opening decrement confirmation does not call the API');
  await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-room-candle-decrease-confirm-390.png'),fullPage:false});
  await page.setViewportSize({width:1440,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'desktop confirmation has no horizontal overflow');await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-room-candle-decrease-confirm-1440.png'),fullPage:false});
  await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.modal'));await page.waitForFunction(()=>document.activeElement?.getAttribute('aria-label')==='촛불 1개 줄이기');

  await minus.press('Enter');await modalTitle().waitFor();await page.getByRole('button',{name:'서버에 기록',exact:true}).click();assert.equal(candlePosts().length,2,'unverified decrement never reaches the API');assert(await page.locator('#toast-region').getByText('촛불을 줄이려면 현장에서 회수한 사실을 확인해 주세요.',{exact:true}).isVisible());assert(await modalTitle().isVisible(),'unverified decrement keeps confirmation open');
  await page.getByRole('checkbox',{name:/현장에서 직접 확인함/}).check();await page.getByRole('button',{name:'서버에 기록',exact:true}).click();await page.waitForFunction(()=>!document.querySelector('.modal'));await waitCount(1);assert.equal(candlePosts().length,3);assert.equal(candlePosts()[2].payload.expectedRoomVersion,4);assert.equal(candlePosts()[2].payload.count,1);assert.equal(candlePosts()[2].payload.physicallyVerified,true);

  await plus.click();await waitCount(2);assert.equal(candlePosts()[3].payload.expectedRoomVersion,5,'re-increment uses the version returned after decrement');

  await minus.click();await modalTitle().waitFor();await page.getByRole('checkbox',{name:/현장에서 직접 확인함/}).check();await page.locator('#toast-region').evaluate(node=>node.replaceChildren());failNextDecrement=true;await page.getByRole('button',{name:'서버에 기록',exact:true}).click();await page.waitForFunction(()=>!document.querySelector('.modal'));await waitCount(3);assert.equal((await page.evaluate(()=>window.__candleQA.snapshot())).room.stateVersion,7,'failed mutation refreshes the latest room version');assert.equal(await page.locator('#toast-region').getByText(/최신 내용을 다시 확인해 주세요/).isVisible(),true,'failure is shown as an error');assert.equal((await page.locator('#toast-region').innerText()).includes('운영 상태를 기록했습니다.'),false,'failure is not shown as success');
  await plus.click();await waitCount(4);assert.equal(candlePosts().at(-1).payload.expectedRoomVersion,7,'operation after refresh uses the latest room version');assert.equal((await page.evaluate(()=>window.__candleQA.snapshot())).uncertain,false,'definitive 409 does not leave an uncertain mutation lock');

  const serviceWorker=await readFile(resolve('WIREFRAME/sw.js'),'utf8');assert(serviceWorker.includes('const SW_VERSION = "2026-09-22-3";'),'PWA cache version is bumped');assert(source.includes("navigator.serviceWorker.register('./sw.js'"),'application registers the service worker');
  assert.deepEqual(pageErrors,[]);assert.deepEqual(consoleProblems,[]);
  console.log('[ok] 0→1→2 연속 증가와 최신 room version');
  console.log('[ok] 감소 확인 모달·미확인 API 0건·확인 후 2→1 physicallyVerified=true');
  console.log('[ok] 재증가와 실패 뒤 최신 객실 재조회·오류 표시·후속 증가');
  console.log('[ok] 390/1440px 가로 넘침·44px 버튼·Escape 초점 복귀·console/page error 0건');
  console.log('[ok] PWA cache 2026-09-22-3');
  console.log(`Environment: Chromium ${await browser.version()} via Playwright; Browser plugin unavailable. All API traffic was intercepted by local fixtures.`);
}catch(error){console.error('page errors',pageErrors);console.error('console problems',consoleProblems);console.error('requests',requests);await page.screenshot({path:'/tmp/candle-stepper-qa-failure.png',fullPage:true});throw error;}finally{await browser.close();}
