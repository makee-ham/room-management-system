#!/usr/bin/env node
// Contract-faithful browser fixtures. No production requests or mutations are allowed.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const roomId=id(1),typeId=id(2),adminId=id(3),maidId=id(4),blockId=id(5),issueId=id(6),quarantineId=id(7);
const now=()=>new Date().toISOString();
const workDate='2026-09-27',targetId=id(11),assignmentId=id(12),attemptId=id(13),requestId=id(14),cycleId=id(15);
let currentAssignment=true;
const assignment={assignmentId,cleaningTargetId:targetId,roomId,roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',maidProfileId:maidId,maidDisplayName:'QA 메이드',serviceDate:workDate,isCurrent:true,notifiedAt:now(),sequenceNumber:1,revision:2,targetAssignmentVersion:7,feeSnapshot:16000};
const cycle={cycleId,maidProfileId:maidId,weekStart:'2026-09-21',status:'open',version:0,itemCount:0,totalAmount:0,payableAmount:0,adjustmentAmount:0,carryInAmount:0,carryOutAmount:0,lateEarningAmount:0,lateEarningCount:0,items:[],adjustments:[],lateEarnings:[]};
const room={id:roomId,roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:12,occupied:false,cleaningRequired:true,candleCount:0,pinSyncStatus:'verified',primaryDisplayStatus:'BLOCKED',allocationReady:false,reasonCodes:['OPERATION_BLOCKED']};
const accounts=[{id:adminId,profileId:adminId,displayName:'QA 관리자',role:'admin',status:'active',version:1},{id:maidId,profileId:maidId,displayName:'QA 메이드',role:'maid',status:'active',version:2,phoneLastFour:'0000',failedLoginCount:0}];
const catalog={generatedAt:now(),summary:{total:1,active:1,inactive:0},roomTypes:[{id:typeId,code:'standard',displayName:'스탠다드',baseOccupancy:2,maxOccupancy:3,active:true,version:4,roomCount:1}],rooms:[{id:roomId,roomNumber:'211',roomTypeId:typeId,roomTypeCode:'standard',active:true,version:12}]};
const source=await readFile('WIREFRAME/index.html','utf8');
const html=source.replace('\n      void bootApplication();',`window.__connectionQA={setup:async role=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${adminId}',displayName:'QA 계정',role,mustChangePassword:false},session:{accessToken:'qa-only',refreshToken:'qa-only-refresh',expiresAt:Date.now()+3600000}};state.role=role;state.liveView=role==='developer'?'rooms':'rooms';state.detail=null;liveRoomDetail=null;for(const name of ['accounts','rooms','roomTypes','reservations','availability','notifications','complaints'])Object.assign(state.remote[name],{status:'ready',lastSuccessAt:new Date().toISOString()});state.remote.accounts.items=${JSON.stringify(accounts)};state.remote.rooms.items=[${JSON.stringify(room)}];state.remote.roomTypes.items=[{id:'${typeId}',code:'standard',displayName:'스탠다드',active:true,baseCleaningFee:16000}];state.remote.cleaning.status='ready';Object.assign(state.remote.developer,{status:'ready',overview:{rooms:{total:1},accounts:{total:2}},lastSuccessAt:new Date().toISOString()});syncAuthState(state);if(role==='developer')await loadLiveCatalog();render();},view:view=>{state.liveView=view;state.detail=null;liveRoomDetail=null;render();},open:openLiveRoomDetailPage,notify:openLiveNotificationTarget,notifications:loadLiveNotifications,get:()=>({busy:liveConnectionBusy,catalog:state.remote.catalog,records:[...state.remote.roomRecords.values()],notifications:state.remote.notifications.items,week:state.remote.payroll.weekStart,view:state.liveView,date:cleaningState().serviceDate,focus:cleaningState().focusRoomId}),expire:()=>{liveConnectionReview.expiresAt='2000-01-01T00:00:00Z';},seed:assignment=>{state.liveView='cleaning';state.cleaningTab='assignment-today';cleaningState().assignments=[assignment];render();},guard:()=>handleLiveConnectionAction('live-catalog-create',{}),gate:()=>canDecideLiveInspection('no-submission')};`);
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block',acceptDownloads:true});
const page=await context.newPage();page.setDefaultTimeout(10000);
const errors=[],requests=[],missing=[],consoleProblems=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))consoleProblems.push(m.text());});
let blocks=[{id:blockId,reasonCode:'MAINTENANCE',startsAt:now(),endsAt:null,status:'active',createdAt:now()}],issues=[{id:issueId,category:'MAINTENANCE',severity:'warning',blocksGuestAssignment:true,description:'QA 시설 확인',status:'open',reportedAt:now()}],resolution=null,conflict=false,notificationPages=0;
const fixture=(route,value,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(value),headers:{'x-request-id':'qa-connections'}});
await page.route('**/*',async route=>{
  const request=route.request(),url=new URL(request.url());
  if(url.origin===new URL(origin).origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:html});return route.continue();}
  if(!request.url().startsWith(api+'/')){missing.push(url.origin);return route.abort();}
  const path=url.pathname.replace('/functions/v1/api',''),method=request.method(),body=request.postData()?JSON.parse(request.postData()):null;requests.push({path,query:url.search,method,body,key:request.headers()['idempotency-key']});
  if(path==='/v1/developer/room-catalog')return fixture(route,{catalog});
  if(path.endsWith('/capacity/preview'))return fixture(route,{preview:{roomTypeId:typeId,current:{baseOccupancy:2,maxOccupancy:3,version:4},proposed:{baseOccupancy:body.baseOccupancy,maxOccupancy:body.maxOccupancy},roomCount:1,activeReservationCount:0,exceedingActiveReservationCount:0,reasonCodes:[],impactFingerprint:'a'.repeat(64),evaluatedAt:now(),expiresAt:new Date(Date.now()+300000).toISOString()}});
  if(path.endsWith('/capacity')&&method==='PATCH'){assert.equal(body.expectedVersion,4);assert.equal(body.impactFingerprint,'a'.repeat(64));assert.equal(body.reasonCode,'CAPACITY_POLICY_CHANGE');if(conflict){conflict=false;return fixture(route,{error:{code:'STALE_VERSION',message:'conflict'}},409);}return fixture(route,{roomType:catalog.roomTypes[0]});}
  if(path==='/v1/developer/rooms'&&method==='POST'){assert.equal(body.expectedRoomTypeVersion,4);assert.equal(body.reasonCode,'ROOM_CATALOG_ADD');return fixture(route,{room:catalog.rooms[0]},201);}
  if(path.endsWith('/deactivation/preview'))return fixture(route,{preview:{roomId,currentlyOccupied:false,activeFutureReservationCount:0,activeCleaningTargetCount:0,activeAssignmentCount:0,activeAttemptCount:0,activePinChangeLease:false,unresolvedOperationCount:0,canDeactivate:true,reasonCodes:[],impactFingerprint:'b'.repeat(64),evaluatedAt:now(),expiresAt:new Date(Date.now()+300000).toISOString()}});
  if(path.endsWith('/deactivate')){assert.equal(body.expectedVersion,12);assert.equal(body.impactFingerprint,'b'.repeat(64));return fixture(route,{room:catalog.rooms[0]});}
  if(path==='/v1/room-pin-sheet-sync/status')return fixture(route,{sync:{pending:1,failed:0,operatorBlocked:false,oldestPendingAt:now(),lastSuccessAt:now(),lastErrorCode:null,version:7,checkedAt:now()}});
  if(path==='/v1/room-pin-sheet-sync/full-resync'){assert.deepEqual(body,{expectedVersion:7});return fixture(route,{sync:{status:'pending',roomCount:121,version:8}},202);}
  if(path==='/v1/rooms')return fixture(route,{rooms:[room]});
  if(path===`/v1/rooms/${roomId}`)return fixture(route,{room});
  if(path===`/v1/rooms/${roomId}/events`)return fixture(route,{roomId,roomStateVersion:12,evaluatedAt:now(),items:[{id:id(9),eventType:'room.report_issue',actorDisplayName:'QA 관리자',effectiveAt:now(),summary:{},reasonCode:'MAINTENANCE'}]});
  if(path===`/v1/rooms/${roomId}/operation-blocks`&&method==='GET')return fixture(route,{roomId,roomStateVersion:12,evaluatedAt:now(),items:blocks,hasMore:false,nextCursor:null});
  if(path===`/v1/rooms/${roomId}/issues`&&method==='GET')return fixture(route,{roomId,roomStateVersion:12,evaluatedAt:now(),items:issues,hasMore:false,nextCursor:null});
  if(path.endsWith('/release')){assert.equal(body.expectedRoomVersion,12);blocks=[];return fixture(route,{operation:{entityId:blockId}});}
  if(path.endsWith('/resolve')&&path.includes('/rooms/')){assert.equal(body.expectedRoomVersion,12);issues=[];return fixture(route,{operation:{entityId:issueId}});}
  if(path.endsWith('/display-status-overrides')){assert.equal(body.expectedRoomVersion,12);assert.equal(body.targetStatus,'CLEANING_REQUIRED');return fixture(route,{operation:{roomId}});}
  if(path==='/v1/reservations')return fixture(route,{reservations:[],nextCursor:null});
  if(path==='/v1/accounts')return fixture(route,{accounts,nextCursor:null});
  if(path==='/v1/notifications'){notificationPages++;return fixture(route,{notifications:[{id:id(notificationPages+20),title:'QA',body:'QA',category:'assignment',roomId:null,cleaningTargetId:null,deepLink:null,groupId:null,requiresAction:false,readAt:null,resolvedAt:null,occurredAt:now()}],nextCursor:url.searchParams.has('cursor')?null:'next-page'});}
  if(path==='/v1/assignment-change-requests')return fixture(route,{requests:[{requestId,cleaningTargetId:targetId,sourceAssignmentRevision:2,status:'pending',reasonCode:'MAID_UNAVAILABLE',requestedAt:now()}],nextCursor:null});
  if(path==='/v1/assignments')return fixture(route,{assignments:currentAssignment?[assignment]:[]});
  if(path===`/v1/assignments/${targetId}/history`)return fixture(route,{assignments:[{...assignment,isCurrent:currentAssignment}]});
  if(path==='/v1/assignments/commit-impact')return fixture(route,{impact:{remainingUnassignedTargets:[],committableDrafts:[],blockedDrafts:[]}});
  if(path==='/v1/availability/candidates')return fixture(route,{candidates:[{workDate:url.searchParams.get('workDate'),weekStart:'2026-09-21',availabilityVersion:1,maidProfileId:maidId,displayName:'QA 메이드'}]});
  if(path==='/v1/availability')return fixture(route,{availability:[]});
  if(path==='/v1/attempts/lifecycle-impact')return fixture(route,{targetAssignmentVersion:7,attempt:{attemptId,assignmentId,status:'in_progress',executionVersion:3,startedAt:now()}});
  if(path===`/v1/assignments/${targetId}/unavailable-cancel`){assert.deepEqual(body,{expectedCurrentAssignmentId:assignmentId,expectedAssignmentVersion:7,expectedAttemptId:attemptId,expectedExecutionVersion:3,reasonCode:'MAID_UNAVAILABLE'});return fixture(route,{assignment});}
  if(path===`/v1/payroll/${cycleId}`)return fixture(route,{cycle});
  if(path==='/v1/payroll')return fixture(route,{payroll:[cycle],nextCursor:null});
  if(path==='/v1/payroll/entries')return fixture(route,{entries:[],nextCursor:null});
  if(path==='/v1/inspections')return fixture(route,{submissions:[],nextCursor:null});
  if(path.startsWith('/v1/developer/')&&path.endsWith('-events'))return fixture(route,{events:[{id:id(10),eventType:'room.master_data_changed',actorDisplayName:'QA 개발자',actorRole:'developer',occurredAt:now(),effectiveAt:now(),reasonCode:'QA_CHANGE',outcome:'success',summary:{}}],nextCursor:null});
  if(path==='/v1/developer/diagnostics')return fixture(route,{diagnostics:{status:'passed',checks:[{id:'database',status:'passed'}],checkedAt:now()}});
  if(path==='/v1/offline-quarantines')return fixture(route,{items:[{quarantineId,actorProfileId:maidId,reasonCode:'CLOCK_CONFLICT',receivedAt:now(),resolution}],nextCursor:null});
  if(path===`/v1/offline-quarantines/${quarantineId}`)return fixture(route,{quarantineId,actorProfileId:maidId,reasonCode:'CLOCK_CONFLICT',receivedAt:now(),occurredAt:now(),resolution,currentAttempt:{executionVersion:3}});
  if(path===`/v1/offline-quarantines/${quarantineId}/resolve`){assert.equal(body.expectedExecutionVersion,3);assert.equal(body.reasonCode,'OFFLINE_CORRECTION_APPROVED');resolution=body.resolution;return fixture(route,{quarantineId,resolution});}
  if(path==='/v1/cleaning-templates'&&method==='GET')return fixture(route,{templates:{cleaningKind:'checkout',roomTypes:['standard','premium','oceanPremium','oceanFamily'].map(roomTypeCode=>({roomTypeCode,roomTypeName:roomTypeCode==='standard'?'스탠다드':roomTypeCode,cleaningKind:'checkout',configured:false,expectedVersion:0,currentPublished:null}))}});
  if(path==='/v1/cleaning-templates'&&method==='POST'){assert.equal(body.expectedVersion,0);assert.equal(body.slots[0].maxPhotos,20);assert.equal(body.slots.length,3);return fixture(route,{template:{version:1}},201);}
  missing.push(`${method} ${path}`);return fixture(route,{error:{code:'QA_MISSING',message:'unhandled route'}},404);
});
async function setup(role){await page.goto(origin+'/index.html');await page.evaluate(role=>__connectionQA.setup(role),role);}
const click=action=>page.locator(`[data-action="${action}"]:visible`).first().click();
async function close(){await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.body.classList.contains('modal-open'));}
async function confirmed(){await click('live-connection-confirm');await page.waitForFunction(()=>!document.body.classList.contains('modal-open')&&!__connectionQA.get().busy);}
async function responsive(name){for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:950});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${name} overflow ${width}`);assert.equal(await page.locator('button:visible').evaluateAll(nodes=>nodes.filter(node=>!(node.getAttribute('aria-label')||node.textContent.trim())).length),0);if(width===390||width===1440){await page.evaluate(()=>{document.getElementById('toast-region').innerHTML='';window.scrollTo(0,0);});await page.waitForTimeout(180);await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:`WIREFRAME/QA/screenshots/live-connections-${name}-${width}.png`,fullPage:true});}}await page.setViewportSize({width:390,height:900});}
try{
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await setup('developer');await page.getByRole('heading',{name:'객실 등록 관리',exact:true}).waitFor();await responsive('catalog');
  await page.locator(`#capacity-base-${typeId}`).fill('2');await page.locator(`#capacity-max-${typeId}`).fill('4');await click('live-capacity-review');await page.getByRole('heading',{name:'스탠다드 인원 변경',exact:true}).waitFor();await confirmed();
  await click('live-capacity-review');await page.getByRole('heading',{name:'스탠다드 인원 변경',exact:true}).waitFor();await page.evaluate(()=>__connectionQA.expire());const writes=requests.filter(r=>r.method==='PATCH').length;await click('live-connection-confirm');assert.equal(requests.filter(r=>r.method==='PATCH').length,writes);await close();
  conflict=true;await click('live-capacity-review');await confirmed();assert.equal(conflict,false);assert.equal((await page.evaluate(()=>__connectionQA.get().catalog.data.roomTypes[0].maxOccupancy)),3);
  await page.locator('#developer-room-number').fill('212');await click('live-catalog-create');await confirmed();await page.locator('#developer-room-delete-number').fill('211');await click('live-catalog-deactivate');await confirmed();
  await page.evaluate(()=>__connectionQA.view('overview'));
  // Read-only tool entry points use the same command dispatcher as visible controls.
  for(const action of ['live-audit-open','live-activity-open','live-diagnostics']){await click(action);await page.locator('#modal-root .modal').waitFor();assert((await page.locator('#modal-root').innerText()).length>20);await close();}
  await setup('admin');await page.evaluate(id=>__connectionQA.open(id),roomId);await page.getByText('QA 시설 확인',{exact:false}).waitFor();await responsive('room');
  await click('review-live-room-resolution');await confirmed();assert.equal(issues.length,0);
  await click('live-room-operations');await page.getByRole('heading',{name:'211호 운영 상태',exact:true}).waitFor();await click('review-live-room-resolution');await confirmed();assert.equal(blocks.length,0);
  await click('live-room-operations');await click('live-room-correction');await page.locator('#room-correction-display').selectOption('CLEANING_REQUIRED');await click('live-room-correction-review');await confirmed();
  await page.evaluate(()=>__connectionQA.view('rooms'));await click('live-room-export');await page.getByRole('heading',{name:'객실 현황 내보내기·동기화',exact:true}).waitFor();const downloading=page.waitForEvent('download');await click('live-export-csv');const download=await downloading;assert(download.suggestedFilename().endsWith('.csv'));assert(!String(await readFile(await download.path(),'utf8')).includes('PIN'));
  await click('live-room-export');await click('live-pin-sheet-review');await confirmed();assert(requests.some(r=>r.path.endsWith('full-resync')&&r.key));
  await page.evaluate(()=>__connectionQA.view('more'));await click('live-accounts-open');await page.getByRole('heading',{name:'메이드·계정 관리',exact:true}).waitFor();await responsive('accounts');
  await page.evaluate(()=>__connectionQA.view('more'));await click('cleaning-template-edit');await page.getByRole('heading',{name:'청소 템플릿',exact:true}).waitFor();await page.locator('#modal-root [data-action="cleaning-template-edit"][data-id="standard"]').click();await click('cleaning-template-publish');await confirmed();
  await page.evaluate(()=>__connectionQA.view('more'));await click('live-quarantines');await click('live-quarantine-open');await page.locator('[data-resolution="correction_link"]').click();await confirmed();assert.equal(resolution,'correction_link');
  notificationPages=0;await page.evaluate(()=>__connectionQA.notifications({quiet:true}));assert.equal(await page.evaluate(()=>__connectionQA.get().notifications.length),2);assert.equal(notificationPages,2);
  await page.evaluate(assignment=>__connectionQA.seed(assignment),assignment);await click('cleaning-unavailable-review');await confirmed();
  await page.evaluate(entityId=>__connectionQA.notify({deepLink:{kind:'cleaningTarget',entityId}}),targetId);assert.equal(await page.evaluate(()=>__connectionQA.get().date),workDate);assert.equal(await page.evaluate(()=>__connectionQA.get().focus),roomId);
  await page.evaluate(entityId=>__connectionQA.notify({deepLink:{kind:'assignmentRequest',entityId}}),requestId);await page.getByRole('heading',{name:'담당 취소 요청',exact:true}).first().waitFor();assert(await page.locator(`#modal-root [data-id="${requestId}"]`).first().isVisible());await close();
  await page.evaluate(entityId=>__connectionQA.notify({deepLink:{kind:'payrollCycle',entityId}}),cycleId);assert.equal(await page.evaluate(()=>__connectionQA.get().week),'2026-09-21');await page.getByText('QA 메이드 · 주급 산출 내역',{exact:true}).waitFor();
  currentAssignment=false;await setup('maid');await page.evaluate(entityId=>__connectionQA.notify({deepLink:{kind:'cleaningTarget',entityId}}),targetId);await page.getByRole('heading',{name:'배정 이력',exact:true}).waitFor();await close();
  await setup('maid');const before=requests.length;await page.evaluate(()=>__connectionQA.guard());assert.equal(requests.length,before);assert.equal(await page.evaluate(()=>__connectionQA.gate()),false);
  assert.deepEqual(missing,[]);assert.deepEqual(errors,[]);assert.deepEqual(consoleProblems,[]);
  console.log('[ok] catalog: load, capacity preview/CAS/expiry/409, create, deactivate');
  console.log('[ok] room: persisted events/issues/blocks, resolution, display correction');
  console.log('[ok] export CSV, PIN-sheet queued sync fence, admin accounts, first template publish');
  console.log('[ok] audit/activity/diagnostics, offline quarantine, notification pagination, role guard');
  console.log('[ok] unavailable cancel exact CAS, notification target/date/request/week, maid historical assignment');
  console.log('[ok] 360/390/768/1440px overflow, accessible button names, screenshots, console');
}catch(error){await page.screenshot({path:'/tmp/live-connections-failure.png',fullPage:true});console.error({errors,missing,consoleProblems});throw error;}finally{await browser.close();}
