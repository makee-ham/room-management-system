#!/usr/bin/env node
// Live adapters against isolated API fixtures; never writes to operational data.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const today=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const shift=(date,days)=>new Date(Date.parse(date+'T12:00:00Z')+days*86400000).toISOString().slice(0,10);
const rooms=[{id:id(1),roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:1,occupied:false,cleaningRequired:true,candleCount:2,pinSyncStatus:'verified',primaryDisplayStatus:'CLEANING_REQUIRED',allocationReady:false,reasonCodes:['CLEANING_REQUIRED'],serviceDate:today,projectionMode:'LIVE',detailConditionCodes:['EXTRA_GUESTS','VACANT','CANDLE_PRESENT','ROOM_ISSUE_PRESENT','EARLY_CHECK_IN','LATE_CHECK_OUT','CHECKOUT_INSPECTION_REQUIRED']},{id:id(2),roomNumber:'350',roomTypeCode:'premium',roomTypeName:'프리미어',elevatorZone:'B',dataStatus:'verified',stateVersion:2,occupied:true,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',primaryDisplayStatus:'OCCUPIED',allocationReady:false,reasonCodes:[],serviceDate:today,projectionMode:'LIVE',detailConditionCodes:['LATE_CHECK_OUT']}];
const types=[{id:id(10),code:'standard',displayName:'스탠다드',baseOccupancy:2,maxOccupancy:4,baseCleaningFee:16000},{id:id(11),code:'premium',displayName:'프리미어',baseOccupancy:2,maxOccupancy:4,baseCleaningFee:20000}];
const reservations=[{id:id(20),roomId:id(1),status:'active',version:1,guestCount:3,checkInAt:today+'T14:00:00+09:00',checkOutAt:shift(today,1)+'T13:00:00+09:00'},{id:id(21),roomId:id(2),status:'active',version:1,guestCount:2,checkInAt:shift(today,-1)+'T16:00:00+09:00',checkOutAt:today+'T13:00:00+09:00'}];
const accounts=[{profileId:id(30),displayName:'QA 관리자',role:'admin',status:'active'},{profileId:id(31),displayName:'QA 메이드',role:'maid',status:'active'}];
const source=await readFile('WIREFRAME/index.html','utf8');
const boot=`window.__parityQA={setup:()=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.role='admin';state.liveView='rooms';state.remote.auth={...state.remote.auth,status:'authenticated',user:{...${JSON.stringify(accounts[0])},mustChangePassword:false},session:{accessToken:'qa-parity-token',refreshToken:'qa-refresh',expiresAt:Date.now()+3600000}};for(const key of ['accounts','rooms','roomTypes','reservations','notifications','complaints','availability','payroll'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});state.remote.accounts.items=${JSON.stringify(accounts)};state.remote.rooms.items=${JSON.stringify(rooms)};state.remote.roomProjection={date:'${today}',status:'ready',items:${JSON.stringify(rooms)}};state.remote.roomTypes.items=${JSON.stringify(types)};state.remote.reservations.items=${JSON.stringify(reservations)};state.remote.cleaning.status='ready';syncAuthState(state);render();},view:async view=>{rawCloseModal();state.liveView=view;state.detail=null;liveRoomDetail=null;if(view==='cleaning'){state.cleaningTab='assignment-today';cleaningState().serviceDate=liveOperationalDate();await loadLiveCleaning({quiet:true});}render();},get:()=>({date:liveOperationalDate(),dateStatus:state.remote.roomProjection?.status,homeDate:state.remote.homeAssignments.date}),changeDate:selectLiveOperationalDate};`;
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(10000);
const errors=[],consoleProblems=[],requests=[],unexpected=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('console',message=>{if(['warning','error'].includes(message.type())&&!message.text().startsWith('Failed to load resource:'))consoleProblems.push(message.text());});
let issueCount=1,slowDate=null;
const reply=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',headers:{'x-request-id':'qa-parity'},body:JSON.stringify(data)});
await page.route('**/*',async route=>{
  const request=route.request(),url=new URL(request.url());
  if(url.origin===new URL(origin).origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace('\n      void bootApplication();',boot)});return route.continue();}
  if(!request.url().startsWith(api+'/')){unexpected.push(url.origin);return route.abort();}
  const path=url.pathname.replace('/functions/v1/api',''),method=request.method(),body=request.postData()?JSON.parse(request.postData()):null;requests.push({path,method,body,query:url.search,key:request.headers()['idempotency-key']});
  if(path==='/v1/rooms'){const date=url.searchParams.get('serviceDate')||today;if(date===slowDate)await new Promise(resolve=>setTimeout(resolve,250));return reply(route,{rooms:rooms.map(room=>({...room,serviceDate:date,projectionMode:date===today?'LIVE':date<today?'PAST_END_OF_DAY':'FUTURE_START_OF_DAY'}))});}
  if(path==='/v1/room-types')return reply(route,{items:types});
  if(path.endsWith('/reports'))return reply(route,{roomId:path.split('/')[3],items:[],nextCursor:null});
  if(path==='/v1/accounts')return reply(route,{accounts});
  if(path==='/v1/reservations'){
    const date=url.searchParams.get('from')?.slice(0,10);if(date===slowDate)await new Promise(resolve=>setTimeout(resolve,250));
    return reply(route,{reservations:date&&date!==today?[{...reservations[0],checkInAt:date+'T16:00:00+09:00',checkOutAt:shift(date,1)+'T11:00:00+09:00'}]:reservations,nextCursor:null});
  }
  if(/\/rooms\/[^/]+\/(events|operation-blocks|issues)$/.test(path)&&method==='GET'){
    if(path.endsWith('/operation-blocks'))assert.equal(url.searchParams.get('status'),'actionable');
    if(path.endsWith('/issues'))assert.equal(url.searchParams.get('status'),'open');
    if(!path.endsWith('/events'))assert.equal(url.searchParams.has('limit'),false,'hosted route rejects explicit pagination limit');
    const roomId=path.split('/')[3];return reply(route,{roomId,roomStateVersion:1,items:path.endsWith('/issues')&&roomId===id(1)&&issueCount?[{id:id(40),category:'MAINTENANCE',severity:'warning',blocksGuestAssignment:false,status:'open',description:'QA 점검',reportedAt:new Date().toISOString()}]:[],nextCursor:null});
  }
  if(path===`/v1/rooms/${id(1)}/issues`&&method==='POST'){assert.equal(body.expectedRoomVersion,1);assert.equal(body.category,'DAMAGE');assert.equal(body.severity,'critical');assert.equal(body.blocksGuestAssignment,false);assert.equal(body.description,'QA 싱크대 점검');assert(request.headers()['idempotency-key']);issueCount++;return reply(route,{operation:{entityId:id(41)}},201);}
  if(path==='/v1/assignments')return reply(route,{assignments:[]});
  if(path==='/v1/assignments/commit-impact')return reply(route,{impact:{serviceDate:today,committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:rooms.map(room=>({cleaningTargetId:id(50+Number(room.stateVersion)),roomId:room.id,roomNumber:room.roomNumber,targetAssignmentVersion:1,serviceDate:today,status:'unassigned',sourceKind:'scheduled_checkout',roomTypeSnapshot:{code:room.roomTypeCode,name:room.roomTypeName,elevatorZone:room.elevatorZone},feeSnapshot:types.find(type=>type.code===room.roomTypeCode).baseCleaningFee,scheduleSnapshot:{isEarlyCheckIn:room.id===id(1),isLateCheckout:room.id===id(2),nextCheckInAt:today+'T14:00:00+09:00',plannedCheckoutAt:today+'T13:00:00+09:00'},availableFrom:today+'T11:00:00+09:00',dueAt:today+'T16:00:00+09:00'}))}});
  if(path==='/v1/availability/candidates')return reply(route,{candidates:[{maidProfileId:id(31),displayName:'QA 메이드',availabilityVersion:1,workDate:url.searchParams.get('workDate')}]});
  if(path==='/v1/availability')return reply(route,{availability:[]});
  if(path==='/v1/assignment-change-requests')return reply(route,{requests:[],nextCursor:null});
  if(path==='/v1/notifications')return reply(route,{notifications:[],nextCursor:null});
  if(path==='/v1/inspections')return reply(route,{submissions:[],nextCursor:null});
  if(path==='/v1/payroll')return reply(route,{payroll:[],nextCursor:null});
  unexpected.push(method+' '+path);return reply(route,{error:{code:'QA_UNEXPECTED_REQUEST'}},400);
});
const click=action=>page.locator(`[data-action="${action}"]:visible`).first().click();
const screenshot=async(name,fullPage=true)=>{await page.locator('#toast-region').evaluate(node=>node.replaceChildren());return page.screenshot({path:`WIREFRAME/QA/screenshots/parity-${name}.png`,fullPage});};
try{
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await page.goto(origin+'/index.html');await page.evaluate(()=>__parityQA.setup());
  const detailOptions=await page.locator('#live-room-filter optgroup[label="상세 조건"] option').allTextContents();
  assert.deepEqual(detailOptions,['퇴실점검 대상','인원 추가','공실','촛불 있음','특이사항 있음','얼리 체크인','레이트 체크아웃']);
  for(const [filter,n] of [['extra-guests',1],['vacant',1],['candle',1],['early',1],['late',2]]){await page.locator('#live-room-filter').selectOption(filter);assert.equal(await page.locator('[data-live-room]').count(),n,filter);}
  await page.locator('#live-room-filter').selectOption('issues');await page.getByText('특이사항 조회 중',{exact:true}).waitFor({state:'hidden'});assert.equal(await page.locator('[data-live-room]').count(),1);
  await page.locator('#live-room-filter').selectOption('checkout-inspection');assert.equal(await page.locator('[data-live-room]').count(),1);
  await page.locator('#live-room-filter').selectOption('all');await screenshot('filters-390');
  await page.locator(`[data-live-room="211"] [data-action="live-room-operations"]`).click();await click('open-live-room-issue');await page.getByRole('heading',{name:'211호 객실 이슈 등록',exact:true}).waitFor();
  await page.locator('#live-room-issue-category').selectOption('DAMAGE');await page.locator('#live-room-issue-severity').selectOption('critical');await page.locator('#live-room-issue-blocks').uncheck();await page.locator('#live-room-issue-description').fill('QA 싱크대 점검');
  for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.keyboard.press('Tab');assert(await page.locator('#modal-root').evaluate(root=>root.contains(document.activeElement)));}
  await page.setViewportSize({width:390,height:900});await screenshot('room-issue-390',false);await click('submit-live-room-issue');await page.getByRole('heading',{name:'211호 객실 이슈 등록',exact:true}).waitFor({state:'hidden'});assert.equal(issueCount,2);
  console.log('[ok] 상세 조건 7개 · 실제 데이터 필터 · 운영 상태 이슈 등록/CAS/멱등성/포커스');
  await click('date-shift');await page.waitForFunction(()=>__parityQA.get().dateStatus==='ready');assert.equal(await page.evaluate(()=>__parityQA.get().date),shift(today,-1));assert(requests.some(item=>item.path==='/v1/rooms'&&item.query==='?serviceDate='+shift(today,-1)));assert(await page.getByText(/선택일 종료 기준/).isVisible());assert.equal(await page.locator('[data-live-room="211"] [data-action="live-pin-show"]').isDisabled(),true);
  await page.goBack();await page.waitForFunction(today=>__parityQA.get().date===today,today);await page.goForward();await page.waitForFunction(date=>__parityQA.get().date===date,shift(today,-1));
  await click('open-calendar');await page.locator(`[data-action="calendar-select"][data-date="${today}"]`).click();await page.waitForFunction(today=>__parityQA.get().date===today&&__parityQA.get().dateStatus==='ready',today);
  slowDate=shift(today,-2);await page.evaluate(async ({slow,fast})=>{const pending=__parityQA.changeDate(slow);await __parityQA.changeDate(fast);await pending;},{slow:slowDate,fast:shift(today,-1)});assert.equal(await page.evaluate(()=>__parityQA.get().date),shift(today,-1));await click('date-today');await page.waitForFunction(today=>__parityQA.get().date===today&&__parityQA.get().dateStatus==='ready',today);
  await page.evaluate(()=>__parityQA.view('today'));await click('date-shift');await page.waitForFunction(()=>__parityQA.get().dateStatus==='ready');assert.equal(await page.evaluate(()=>__parityQA.get().homeDate),today);await screenshot('home-date-390');
  await click('go-cleaning-assignment');await page.getByRole('heading',{name:'내일 청소 배정',exact:true}).waitFor();
  await page.locator('[data-action="cleaning-tab"][data-tab="assignment-today"]').click();
  await page.waitForFunction(date=>document.querySelector('.assignment-intro p')?.textContent.includes(`${Number(date.slice(5,7))}월 ${Number(date.slice(8))}일`),shift(today,-1));
  assert(requests.some(item=>item.path==='/v1/assignments'&&item.query===`?serviceDate=${shift(today,-1)}`));
  await page.evaluate(()=>__parityQA.view('today'));await click('date-today');await page.waitForFunction(today=>__parityQA.get().date===today&&__parityQA.get().dateStatus==='ready',today);
  console.log('[ok] 홈·객실 날짜 이동/달력/오늘 · KST 범위 요청 · 느린 이전 응답 차단');
  await page.evaluate(()=>__parityQA.view('cleaning'));
  const ids=await page.locator('.assignment-page [id^="cleaning-section-"]').evaluateAll(nodes=>nodes.map(node=>node.id));assert.deepEqual(ids,['cleaning-section-overview','cleaning-section-availability','cleaning-section-random','cleaning-section-assignees','cleaning-section-summary','cleaning-section-history']);
  assert.equal(await page.locator('.assignment-intro .job-actions button').count(),2);assert.equal(await page.locator('.assignment-row-options').count(),0);assert.equal(await page.locator('.assignment-table th').count(),5);assert.equal(await page.locator('.assignment-type-filter').count(),5);assert.equal(await page.locator('.assignment-fee').first().innerText(),'16,000원');assert(await page.getByText('얼리 체크인 14:00',{exact:true}).isVisible());assert(await page.getByText('레이트 체크아웃 13:00',{exact:true}).isVisible());assert(!/청소 순서|업무 순서/.test(await page.locator('main').innerText()));
  for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.equal(await page.locator('button:visible').evaluateAll(nodes=>nodes.filter(node=>!(node.getAttribute('aria-label')||node.textContent.trim())).length),0);await screenshot('cleaning-'+width);}
  console.log('[ok] 정본 공통 배정 레이아웃 · 6개 섹션/5개 열 · 실제 단가/얼리·레이트 · 4개 폭');
  assert.deepEqual(unexpected,[]);assert.deepEqual(errors,[]);assert.deepEqual(consoleProblems,[]);
  console.log(`Environment: Chromium ${await browser.version()} via Playwright. Browser plugin unavailable. All API traffic intercepted; screenshots contain synthetic data only.`);
}catch(error){console.error({errors,unexpected,consoleProblems});await page.screenshot({path:'/tmp/parity-failure.png',fullPage:true});throw error;}finally{await browser.close();}
