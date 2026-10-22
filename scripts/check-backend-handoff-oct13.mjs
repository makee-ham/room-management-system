#!/usr/bin/env node
// Synthetic intercepted API only, including all reservation and PIN commands.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const source=await readFile('WIREFRAME/index.html','utf8');
let renderedSource=source;
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>'79000000-0000-4000-8000-'+String(n).padStart(12,'0');
const room={id:id(1),roomNumber:'211',roomTypeCode:'standard',roomTypeName:'QA 스탠다드',elevatorZone:'A',stateVersion:5,dataStatus:'verified',occupied:false,cleaningRequired:false,candleCount:0,pinSyncStatus:'verified',allocationReady:true,allocationBlocked:false,reasonCodes:[],primaryDisplayStatus:'READY',reservationPhase:'none',displayReservationId:null,detailConditionCodes:[]};
const rooms=[room,{...room,id:id(2),roomNumber:'212'}];
const maid={profileId:id(5),role:'maid',status:'active',displayName:'QA 메이드'};
const actor={profileId:id(4),role:'admin',displayName:'QA 관리자',mustChangePassword:false};
const boot=`window.__handoff={
 setup:(role='admin',flags=true,exportOnly=false)=>{
   LIVE_RUNTIME.authGeneration++;clearLiveAuthSurface();LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';
   LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_qa_only_abcdefghijklmnopqrstuvwxyz',featureFlags:{optionalCleaningWorkflow:true,roomPinExport:exportOnly,roomPinTransfer:flags,assignmentPlanningDate:flags}});
   state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{...${JSON.stringify(actor)},role},session:{accessToken:'qa-fixture',expiresAt:Date.now()+86400000}};
   state.remote.rooms={...state.remote.rooms,status:'ready',items:${JSON.stringify(rooms)},lastSuccessAt:new Date().toISOString()};
   state.remote.roomTypes={...state.remote.roomTypes,status:'ready',items:[{id:'${id(3)}',code:'standard',baseOccupancy:2,maxOccupancy:4,active:true}],lastSuccessAt:new Date().toISOString()};
   state.remote.accounts={...state.remote.accounts,status:'ready',items:[${JSON.stringify(maid)}],lastSuccessAt:new Date().toISOString()};
   cleaningState().status='ready';state.remote.notifications.status='ready';state.remote.notifications.lastSuccessAt=new Date().toISOString();state.role=role;state.liveView=role==='maid'?'my':'rooms';state.cleaningTab='assignment-today';syncAuthState(state);render();
 },
 create:(schedule={})=>openLiveReservationCreate('${id(1)}',document.activeElement,schedule),
 date:date=>{state.remote.operationalDate=date;state.selectedDate=date;},
 clean:()=>{rawCloseModal();state.liveView='cleaning';state.cleaningTab='progress';cleaningState().status='ready';render();},
 incidents:async()=>{const pending=loadLiveCheckoutIncidents();render();await pending;render();},
 refresh:refreshLiveActor,export:openLiveRoomExport,downloadPins:exportLiveRoomPins,pin:()=>openLivePinEditor('${id(1)}'),close:()=>rawCloseModal({restoreFocus:true}),
 midnight:refreshLiveOperationalDay,
 login:()=>loginWithApi('qa-only','qa-only',false),storedSession:()=>!!readStoredLiveSession()?.session,
 plan:async(tab='assignment-today')=>{state.liveView='cleaning';state.cleaningTab=tab;resetLiveCleaningDate(addIsoDays(liveOperationalDate(),tab==='assignment-tomorrow'?1:0));await loadLiveCleaning();},
 queue:()=>LIVE_PHOTO_QUEUE.push({id:'qa-upload',assignmentId:'${id(10)}',status:'queued',file:new File(['qa'],'qa.jpg',{type:'image/jpeg'})}),
 draft:()=>{cleaningState().manualEdits=new Map([['${id(20)}',{serviceDate:cleaningState().serviceDate,maidProfileId:'${id(5)}'}]]);},
 guard:async()=>{try{await mutationApiRequest('/v1/assignments/drafts',{body:{}});return null;}catch(e){return e.code;}},
 change:()=>runLiveCleaningMutation({path:'/v1/assignments/${id(20)}/change',body:{expectedCurrentAssignmentId:'${id(10)}',expectedAssignmentVersion:1,maidProfileId:'${id(5)}',reasonCode:'OPERATIONAL_CHANGE',sequenceNumber:1},reload:false}),
 snapshot:()=>({auth:state.remote.auth.status,authError:state.remote.auth.error?.code,date:liveOperationalDate(),serviceDate:cleaningState().serviceDate,pending:state.remote.dayRefreshPending,assignments:cleaningState().assignments.map(a=>({id:a.cleaningTargetId,date:a.serviceDate,planning:a.planningDate,maid:a.maidProfileId})),edits:cleaningState().manualEdits?.size||0,queue:LIVE_PHOTO_QUEUE.length,hasPreview:!!livePinTransfer?.preview}),
 options:()=>livePinTransferActions(),importOnly:async()=>{await previewLivePinImport();await applyLivePinImport();},directTransfer:async()=>{await previewLivePinImport();await applyLivePinImport();await exportLiveRoomPins();},
 };`;
const python=process.env.RMS_QA_PYTHON||'python3';
const workbook=execFileSync(python,['-c',`import io,sys,openpyxl
w=openpyxl.Workbook();s=w.active;s.title="시트 1"
s["B2"]="객실";s["C2"]="비번";s["B3"]="211";s["C3"]="211-0012";s["B4"]="212";s["C4"]="212-001234"
b=io.BytesIO();w.save(b);sys.stdout.buffer.write(b.getvalue())`]);
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},timezoneId:'America/Los_Angeles',serviceWorkers:'block',acceptDownloads:true});
const page=await context.newPage(),calls=[],errors=[],unexpected=[];
page.setDefaultTimeout(8000);
const gate={bookable:false,previewDelay:0,incidents:'empty',incidentDelay:0,auth503:false,pinPreview:'valid',pinApply:'success',longStay:false,assignmentDelay:0,exportMode:'valid',exportDelay:0};
let downloadCount=0;page.on('download',()=>downloadCount++);
const time='2026-10-13T10:00:00+09:00';
await page.clock.install({time:new Date(time)});await page.clock.setFixedTime(new Date(time));
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))errors.push(m.text());});
const json=(route,value,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(value)});
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const assignment=date=>({assignmentId:id(10),cleaningTargetId:id(20),roomId:id(1),roomNumber:'211',maidProfileId:id(5),maidDisplayName:'QA 메이드',serviceDate:'2026-10-11',planningDate:date,revision:1,targetAssignmentVersion:1,isCurrent:true,notifiedAt:date+'T00:00:00+09:00',feeSnapshot:16000,targetStatus:'notified',attemptStatus:'scheduled',roomTypeCode:'standard',availableFrom:date+'T11:00:00+09:00'});
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());
 if(url.origin===origin){if(url.pathname==='/index.html')return route.fulfill({contentType:'text/html',body:renderedSource.replace('\n      void bootApplication();',boot)});return route.continue();}
 if(!req.url().startsWith(api+'/')){unexpected.push(url.origin);return route.abort();}
 const path=url.pathname.replace('/functions/v1/api',''),body=req.postDataJSON(),method=req.method(),key=req.headers()['idempotency-key'];
 calls.push({path,method,body,key,query:url.searchParams.toString()});
 if(path==='/v1/reservations/bookability/preview'){const blocked=gate.bookable===false;await wait(gate.previewDelay);return json(route,{preview:{...body,candidates:rooms.map((r,i)=>({roomId:r.id,roomNumber:r.roomNumber,roomTypeCode:'standard',roomStateVersion:5,intervalBookable:!blocked||i===1,checkInReady:true,reasonCodes:blocked&&!i?['RESERVATION_OVERLAP']:[],evaluatedAt:time})),evaluatedAt:time}});}
 if(path==='/v1/rooms')return json(route,{rooms:rooms.map(r=>({...r,...(url.searchParams.has('serviceDate')?{serviceDate:url.searchParams.get('serviceDate'),projectionMode:'LIVE'}:{})}))});
 if(path==='/v1/room-types')return json(route,{items:[{id:id(3),code:'standard',baseOccupancy:2,maxOccupancy:4,active:true}]});
 if(path==='/v1/reservations')return json(route,{reservations:[]});
 if(path==='/v1/rooms/'+id(1))return json(route,{room:{...room,reservationPhase:gate.longStay?'current':'none',displayReservationId:gate.longStay?id(30):null}});
 if(path==='/v1/reservations/'+id(30))return json(route,{reservation:{id:id(30),roomId:id(1),status:'active',reservationType:'long_stay'}});
 if(path.endsWith('/pin/reveal'))return json(route,{pin:{roomId:id(1),credential:'211-001234',pinVersion:2,clearAfterSeconds:30,expiresAt:'2026-10-13T10:00:30+09:00'}});
 if(path.endsWith('/pin-changes/prepare'))return json(route,{change:{leaseId:id(40),currentPinVersion:2,proposedPinVersion:3,expiresAt:'2026-10-13T10:05:00+09:00'}},201);
 if(path==='/v1/checkout-incidents'){
   const mode=gate.incidents;await wait(gate.incidentDelay);
   return mode==='error'?json(route,{error:{code:'INTERNAL_SERVER_ERROR'}},500):json(route,{items:mode==='items'?[{incidentId:id(50),roomNumber:'211',status:'open',reportedAt:time}]:[],nextCursor:null});
 }
 if(path==='/v1/auth/me')return gate.auth503?json(route,{error:{code:'AUTH_CONTEXT_UNAVAILABLE'}},503):json(route,{user:actor});
 if(path==='/v1/auth/login')return json(route,{accessToken:'qa-only-access',refreshToken:'qa-only-refresh',expiresIn:3600,user:actor});
 if(path==='/v1/room-pin-sheet-sync/status')return json(route,{sync:{version:1,pending:0,failed:0,operatorBlocked:false,lastSuccessAt:time}});
 if(path==='/v1/rooms/pins/export'){
   assert.equal(req.headers().accept,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');await wait(gate.exportDelay);
   if(gate.exportMode==='denied')return json(route,{error:{code:'PIN_ACCESS_REQUIRED',message:'DO_NOT_DISPLAY_PROVIDER_SECRET'}},403);
   return route.fulfill({contentType:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',body:gate.exportMode==='invalid'?Buffer.from('invalid-workbook'):workbook});
 }
 if(path==='/v1/rooms/pins/import/preview'){
   assert.deepEqual(body,{});const valid=gate.pinPreview!=='invalid';
   if(gate.pinPreview==='config')return json(route,{error:{code:'ROOM_PIN_TRANSFER_NOT_CONFIGURED',message:'DO_NOT_DISPLAY_PROVIDER_SECRET'}},503);
   const now=await page.evaluate(()=>Date.now());
   return json(route,{preview:{valid,total:2,changed:1,unchanged:1,ignored:3,issues:valid?[]:[{row:5,code:'DUPLICATE_ROOM'},{row:6,code:'INVALID_ROOM_CREDENTIAL'},{row:7,code:'DO_NOT_DISPLAY_CELL_VALUE'}],expiresAt:new Date(now+300000).toISOString(),previewToken:valid?(now+300000)+'.'+'a'.repeat(64)+'.'+'b'.repeat(64):null}});
 }
 if(path==='/v1/rooms/pins/import/apply'){
   assert(key);assert.deepEqual(Object.keys(body),['previewToken']);
   if(gate.pinApply==='lost'){gate.pinApply='success';return route.abort();}
   if(gate.pinApply==='stale')return json(route,{error:{code:'ROOM_PIN_TRANSFER_STALE'}},409);
   return json(route,{imported:{updated:1,unchanged:1}});
 }
 if(path==='/v1/assignments'){const d=url.searchParams.get('serviceDate'),delay=gate.assignmentDelay;gate.assignmentDelay=0;await wait(delay);return json(route,{assignments:[assignment(d),{...assignment(d),assignmentId:id(11),cleaningTargetId:id(21)}]});}
 if(path==='/v1/assignments/commit-impact')return json(route,{impact:{serviceDate:url.searchParams.get('serviceDate'),impactFingerprint:'a'.repeat(64),committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}});
 if(path==='/v1/availability/candidates')return json(route,{candidates:[{maidProfileId:maid.profileId,displayName:maid.displayName,workDate:url.searchParams.get('workDate')}]});
 if(path==='/v1/availability')return json(route,{availability:[],changeRequests:[]});
 if(path==='/v1/accounts')return json(route,{accounts:[maid]});
 if(path==='/v1/assignment-change-requests')return json(route,{requests:[],nextCursor:null});
 if(path==='/v1/inspections')return json(route,{submissions:[],nextCursor:null});
 if(path==='/v1/notifications')return json(route,{notifications:[],nextCursor:null});
 if(path==='/v1/attempts/current')return json(route,{attempt:null});
 if(path==='/v1/assignments/'+id(20)+'/change')return json(route,{assignment:assignment(body.serviceDate||'2026-10-11')});
 unexpected.push(method+' '+path);return json(route,{error:{code:'UNEXPECTED_QA_ROUTE'}},400);
});
const setup=async(role='admin',flags=true,exportOnly=false)=>{await page.evaluate(([r,f,e])=>__handoff.setup(r,f,e),[role,flags,exportOnly]);};
const snapshot=()=>page.evaluate(()=>__handoff.snapshot());
const modal=()=>page.locator('#modal-root .modal');
async function responsive(name){
 for(const width of [360,390,768,1440]){
   await page.setViewportSize({width,height:900});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,name+' overflow '+width);
   assert.equal(await page.locator('button:visible').evaluateAll(items=>items.filter(b=>!b.textContent.trim()&&!b.getAttribute('aria-label')).length),0);
   if(name==='pin-export-only'){
     await page.locator('#pin-import-unavailable').scrollIntoViewIfNeeded();
     assert.equal(await page.locator('[aria-label="객실 PIN 전송"] button').evaluateAll(items=>items.filter(b=>{const r=b.getBoundingClientRect();return r.width<44||r.height<44;}).length),0);
   }
   if(['pin-import','reservation-date','pin-export-only'].includes(name))await page.screenshot({path:'WIREFRAME/QA/screenshots/backend-handoff-'+name+'-'+width+'.png'});
 }
 await page.setViewportSize({width:390,height:900});
}
try{
 await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
 await page.goto(origin+'/index.html');assert.match(await page.title(),/CASTLE|캐슬/i);
 for(const clock of ['2026-10-13T10:00:00+09:00','2026-10-13T17:10:00+09:00']){
   await page.clock.setFixedTime(new Date(clock));await setup();await page.evaluate(()=>__handoff.create());
   assert.equal(await page.locator('#live-reservation-checkin').inputValue(),'2026-10-13T16:00');
   assert.equal(await page.locator('#live-reservation-checkout').inputValue(),'2026-10-14T11:00');
   assert.equal(await page.locator('#live-reservation-room').inputValue(),id(1));
   assert(await page.locator('[data-action="submit-live-reservation-create"]').isDisabled());
   await page.evaluate(()=>__handoff.close());
 }
 await page.evaluate(()=>__handoff.date('2026-10-20'));await page.evaluate(()=>__handoff.create());
 assert.equal(await page.locator('#live-reservation-checkin').inputValue(),'2026-10-20T16:00');
 await responsive('reservation-date');await page.evaluate(()=>__handoff.close());
 gate.previewDelay=350;await page.evaluate(()=>{void __handoff.create({checkInAt:'2026-10-22T17:00',checkOutAt:'2026-10-23T11:00'});});
 await page.locator('#live-reservation-checkin').waitFor();await page.locator('#live-reservation-guest-name').fill('QA DRAFT');
 await page.locator('#live-reservation-checkin').fill('2026-10-22T18:00');await wait(500);
 assert.equal(await page.locator('#live-reservation-checkin').inputValue(),'2026-10-22T18:00');
 assert.equal(await page.locator('#live-reservation-guest-name').inputValue(),'QA DRAFT');
 await page.locator('#live-reservation-checkin').dispatchEvent('change');await page.clock.runFor(250);await wait(450);
 await page.locator('#live-reservation-room').selectOption(id(2));
 assert.equal(await page.locator('#live-reservation-checkin').inputValue(),'2026-10-22T18:00');
 await page.evaluate(()=>__handoff.close());await wait(450);assert.equal(await modal().count(),0);gate.previewDelay=0;
 console.log('[ok] KST today before/after 16:00, explicit future date, overlap keeps room/date, delayed preview preserves draft');
 await setup();await page.evaluate(()=>__handoff.clean());gate.incidents='items';await page.evaluate(()=>__handoff.incidents());
 assert(await page.locator('[data-checkout-incidents]').getByText('211호',{exact:true}).isVisible());
 gate.incidents='error';gate.incidentDelay=200;await page.evaluate(()=>{void __handoff.incidents();});
 await page.locator('[data-checkout-incidents]').getByText('조회 중',{exact:true}).waitFor();
 assert.equal(await page.locator('[data-checkout-incidents] [data-action="cleaning-incident-open"]').count(),0);
 await page.locator('[data-action="cleaning-incident-retry"]').waitFor();assert.equal(await page.getByText('확인할 신고가 없습니다.',{exact:true}).count(),0);
 await responsive('incident-error');gate.incidents='empty';
 await page.locator('[data-action="cleaning-incident-retry"]').press('Enter');await page.getByText('확인할 신고가 없습니다.',{exact:true}).waitFor();
 gate.incidentDelay=0;gate.auth503=true;await page.evaluate(()=>__handoff.refresh());
 assert.equal((await snapshot()).auth,'authenticated');assert.equal((await snapshot()).authError,'AUTH_CONTEXT_UNAVAILABLE');
 await page.evaluate(()=>__handoff.login());assert.equal((await snapshot()).auth,'error');assert.equal(await page.evaluate(()=>__handoff.storedSession()),true);gate.auth503=false;
 console.log('[ok] incident loading/error/stale/empty/retry distinct; auth context 503 preserves session');
 for(const role of ['maid','developer']){await setup(role);const n=calls.length;await page.evaluate(()=>__handoff.directTransfer());assert.equal(calls.length,n);assert.equal(await page.evaluate(()=>__handoff.options()),'');}
 await setup('admin',false);let n=calls.length;await page.evaluate(()=>__handoff.directTransfer());assert.equal(calls.length,n);
 for(const role of ['maid','developer']){await setup(role,false,true);n=calls.length;await page.evaluate(()=>__handoff.directTransfer());assert.equal(calls.length,n);}
 await setup('admin',false,true);await page.evaluate(()=>__handoff.export());
 assert(await page.getByRole('button',{name:'내보내기 · 앱 → 엑셀'}).isEnabled());
 assert(await page.getByRole('button',{name:'쓰기 · Drive → 앱'}).isDisabled());
 n=calls.length;await page.evaluate(()=>__handoff.importOnly());
 assert.equal(calls.length,n,'disabled import must block direct commands');
 await responsive('pin-export-only');
 await page.keyboard.press('Tab');assert(await modal().evaluate(el=>el.contains(document.activeElement)));
 await page.keyboard.press('Escape');assert.equal(await modal().count(),0);
 console.log('[ok] independent PIN export gate; Drive import visibly disabled and direct commands blocked; export-only role guards');
 await setup('admin',false,true);await page.evaluate(()=>__handoff.export());
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'내보내기 · 앱 → 엑셀'}).press('Enter');
 const download=await downloadPromise;assert.equal(download.suggestedFilename(),'room-pins.xlsx');
 execFileSync(python,['-c',`import sys,openpyxl
w=openpyxl.load_workbook(open(sys.argv[1],"rb"));assert w.sheetnames==["시트 1"];s=w.active
assert s["B2"].value=="객실" and s["C2"].value=="비번"
assert s["C3"].value=="211-0012" and s["C4"].value=="212-001234"
assert s["C3"].data_type=="s" and s["C4"].data_type=="s"`,await download.path()]);
 const downloadsBeforeFailure=downloadCount;gate.exportDelay=200;
 for(const mode of ['denied','invalid']){
   gate.exportMode=mode;n=calls.filter(c=>c.path.endsWith('/pins/export')).length;
   await page.evaluate(()=>{void __handoff.downloadPins();void __handoff.downloadPins();});
   assert(await page.getByRole('button',{name:'내보내기 · 앱 → 엑셀'}).isDisabled());await wait(350);
   assert.equal(calls.filter(c=>c.path.endsWith('/pins/export')).length,n+1);assert.equal(downloadCount,downloadsBeforeFailure);
   assert(await page.getByRole('button',{name:'내보내기 · 앱 → 엑셀'}).isEnabled());assert(!(await page.locator('#toast-region').innerText()).includes('DO_NOT_DISPLAY'));
 }
 gate.exportMode='valid';await page.evaluate(()=>{void __handoff.downloadPins();__handoff.close();});await wait(350);assert.equal(downloadCount,downloadsBeforeFailure);gate.exportDelay=0;
 await setup('admin',false,true);await page.evaluate(()=>__handoff.export());gate.exportDelay=200;
 n=calls.filter(c=>c.path.endsWith('/pins/export')).length;await page.evaluate(()=>{void __handoff.downloadPins();});await wait(50);
 await setup('admin',false,true);await page.evaluate(()=>__handoff.export());gate.exportDelay=550;await page.evaluate(()=>{void __handoff.downloadPins();});await wait(300);
 await page.evaluate(()=>{void __handoff.downloadPins();});assert.equal(calls.filter(c=>c.path.endsWith('/pins/export')).length,n+2,'old auth response must not unlock a new export');
 await wait(350);assert.equal(downloadCount,downloadsBeforeFailure+1,'only the new session may download');gate.exportDelay=0;
 console.log('[ok] export loading, duplicate clicks, forbidden/malformed responses and modal-exit late response never download');
 await setup();await page.evaluate(()=>__handoff.export());
 await page.getByRole('button',{name:'쓰기 · Drive → 앱'}).click();await page.getByRole('button',{name:'앱에 저장',exact:true}).waitFor();
 assert.equal(await page.locator('[data-pin-import]').getByText('1건',{exact:true}).count(),2);await responsive('pin-import');
 gate.pinApply='lost';await page.getByRole('button',{name:'앱에 저장',exact:true}).click();await page.getByRole('button',{name:'같은 요청 결과 확인'}).waitFor();
 const firstApply=calls.filter(c=>c.path.endsWith('/pins/import/apply')).at(-1);
 await page.evaluate(()=>__handoff.close());await page.evaluate(()=>__handoff.export());await page.getByRole('button',{name:'쓰기 · Drive → 앱'}).click();
 await page.clock.setFixedTime(new Date('2026-10-13T17:20:00+09:00'));
 await page.getByRole('button',{name:'같은 요청 결과 확인'}).click();await page.getByText(/앱 저장 완료/).waitFor();
 const secondApply=calls.filter(c=>c.path.endsWith('/pins/import/apply')).at(-1);
 assert.equal(secondApply.key,firstApply.key);assert.deepEqual(secondApply.body,firstApply.body);assert.equal((await snapshot()).hasPreview,false);
 gate.pinPreview='invalid';await page.getByRole('button',{name:'다시 미리보기'}).click();await page.getByText('5행 · 중복 객실',{exact:true}).waitFor();
 assert.equal(await page.getByRole('button',{name:'앱에 저장',exact:true}).count(),0);assert(!(await page.locator('[data-pin-import]').innerText()).includes('DO_NOT_DISPLAY'));
 gate.pinPreview='config';await page.getByRole('button',{name:'다시 미리보기'}).click();await page.getByText('서버의 Drive 연결 설정이 필요합니다.',{exact:true}).waitFor();
 assert(!(await page.locator('[data-pin-import]').innerText()).includes('DO_NOT_DISPLAY'));
 gate.pinPreview='valid';gate.pinApply='stale';await page.getByRole('button',{name:'다시 미리보기'}).click();await page.getByRole('button',{name:'앱에 저장',exact:true}).click();await page.getByText(/미리보기가 만료/).waitFor();
 assert.equal(await page.getByRole('button',{name:'앱에 저장',exact:true}).count(),0);
 const stored=await page.evaluate(()=>JSON.stringify({local:{...localStorage},session:{...sessionStorage},history:history.state,url:location.href}));
 for(const secret of ['211-0012','001234',firstApply.body.previewToken])assert(!stored.includes(secret));
 console.log('[ok] gated/admin-only PIN transfer, real XLSX parse, string/zero preservation, safe preview, same-key replay after expiry, stale/config errors');
 await setup('admin',false,true);gate.longStay=true;await page.evaluate(()=>__handoff.pin());const input=page.locator('#live-room-pin-digits');
 await input.fill('001234');assert.equal(await input.evaluate(el=>el.checkValidity()),true);
 await input.fill('00123');assert.equal(await input.evaluate(el=>el.checkValidity()),false);
 await page.locator('[data-action="live-pin-random"]').click();assert.equal((await input.inputValue()).length,4);
 await input.fill('001234');await page.locator('[data-action="live-pin-prepare"]').click();await page.locator('[data-action="live-pin-confirm"]').waitFor();
 assert.equal(calls.filter(c=>c.path.endsWith('/pin-changes/prepare')).at(-1).body.pinDigits,'001234');
 await page.evaluate(()=>__handoff.close());gate.longStay=false;await page.evaluate(()=>__handoff.pin());assert.equal(await input.getAttribute('maxlength'),'4');await page.evaluate(()=>__handoff.close());
 console.log('[ok] current server long_stay allows 4/6 digits; ordinary and random PINs use 4');
 await setup('admin',false);await page.evaluate(()=>__handoff.change());assert(!Object.hasOwn(calls.filter(c=>c.path.endsWith('/change')).at(-1).body,'serviceDate'));
 await setup();gate.assignmentDelay=400;await page.evaluate(()=>{void __handoff.plan();});await wait(50);await page.evaluate(()=>__handoff.plan('assignment-tomorrow'));await wait(450);
 assert.equal((await snapshot()).assignments[0].planning,(await snapshot()).serviceDate);
 for(const [before,after] of [['2026-10-18T23:59:59+09:00','2026-10-19T00:00:01+09:00'],['2026-10-31T23:59:59+09:00','2026-11-01T00:00:01+09:00'],['2026-12-31T23:59:59+09:00','2027-01-01T00:00:01+09:00']]){
   await page.clock.setFixedTime(new Date(before));await setup();await page.evaluate(()=>__handoff.plan('assignment-tomorrow'));
   await page.evaluate(()=>__handoff.draft());n=calls.length;await page.clock.setFixedTime(new Date(after));
   assert.equal(await page.evaluate(()=>__handoff.guard()),'PLANNING_DAY_CHANGED');assert.equal(calls.length,n);
   await page.evaluate(()=>__handoff.midnight());const current=await snapshot();
   assert.equal(current.date,after.slice(0,10));assert.equal(current.edits,0);assert.equal(current.assignments.length,2);
   assert.equal(current.assignments[0].date,'2026-10-11');assert.equal(current.assignments[0].maid,id(5));assert.equal(current.assignments[0].planning,current.serviceDate);
   assert.equal(await page.locator('[data-assignment-target]').evaluateAll(rows=>new Set(rows.map(r=>r.id)).size),2);
   assert.equal(new URLSearchParams(calls.filter(c=>c.path==='/v1/availability/candidates').at(-1).query).get('workDate'),current.serviceDate);
   await page.evaluate(()=>__handoff.change());assert.equal(calls.filter(c=>c.path.endsWith('/change')).at(-1).body.serviceDate,current.serviceDate);
 }
 await page.clock.setFixedTime(new Date('2026-10-13T23:59:59+09:00'));await setup('maid');await page.evaluate(()=>__handoff.queue());
 await page.clock.setFixedTime(new Date('2026-10-14T00:00:01+09:00'));await page.evaluate(()=>__handoff.midnight());assert.equal((await snapshot()).queue,1);
 await page.clock.setFixedTime(new Date('2026-10-13T23:59:59+09:00'));await setup();await page.evaluate(()=>__handoff.date('2026-10-11'));
 await page.clock.setFixedTime(new Date('2026-10-14T00:00:01+09:00'));await page.evaluate(()=>__handoff.midnight());assert.equal((await snapshot()).date,'2026-10-11');
 console.log('[ok] KST week/month/year boundaries, stale writes blocked, target IDs/original dates retained, plan-date availability, uploads and pinned date retained');
 await setup('admin',false,true);await page.evaluate(()=>__handoff.export());
 const destinations=()=>page.locator('[data-action="live-export-csv"],[data-action="live-export-xlsx"],[data-action="live-pin-sheet-review"]').evaluateAll(items=>items.map(item=>({label:item.textContent,action:item.dataset.action})));
 const currentDestinations=await destinations();
 renderedSource=execFileSync('git',['show','29bafc9:WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:4e6});
 await page.clock.setFixedTime(new Date('2026-10-13T17:10:00+09:00'));
 await page.goto(origin+'/index.html');await setup('admin',false,true);await page.evaluate(()=>__handoff.export());
 assert.deepEqual(await destinations(),currentDestinations,'original export buttons retain their labels and purposes');
 for(const width of [390,1440]){await page.setViewportSize({width,height:900});await page.screenshot({path:'WIREFRAME/QA/screenshots/backend-handoff-pin-export-before-'+width+'.png'});}
 console.log('[ok] same-role baseline export dialog comparison; original CSV/XLSX/Drive-update destinations retained');
 assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);
 console.log('PASS: Browser plugin not available; intercepted Playwright Chromium '+await browser.version()+', 360/390/768/1440px, America/Los_Angeles timezone.');
}finally{await browser.close();}
