#!/usr/bin/env node
// Browser plugin not available. All API calls are isolated fixtures, never operational writes.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>`71000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul'}).format(new Date());
const maid={id:id(1),profileId:id(1),role:'maid',displayName:'QA 메이드',loginId:'QA',status:'active'};
const room={id:id(2),roomNumber:'211',roomTypeCode:'standard',stateVersion:1,candleCount:1};
const assignment={assignmentId:id(3),cleaningTargetId:id(4),roomId:room.id,roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',maidProfileId:maid.id,maidDisplayName:maid.displayName,serviceDate:date,revision:1,isCurrent:true,notifiedAt:date+'T01:00:00Z',feeSnapshot:16000,cleaningKind:'checkout',targetStatus:'notified',availableFrom:date+'T01:00:00Z'};
let attempt={attemptId:id(5),assignmentId:assignment.assignmentId,assignmentRevision:1,executionVersion:1,status:'in_progress',startedAt:date+'T02:00:00Z'};
let submission={id:id(6),attemptId:attempt.attemptId,version:1,currentRevision:1,current:true,status:'approved',candleCount:3,submittedAt:date+'T03:00:00Z',reviewContext:{roomNumber:'211',maidDisplayName:'QA 메이드',cleaningTargetId:assignment.cleaningTargetId},photos:Array.from({length:8},(_,i)=>({photoId:id(20+i),slotKey:'cleaning-proof',mediaAvailability:i===7?'expired':'available'}))};
const historyItem={submissionId:submission.id,attemptId:attempt.attemptId,roomId:room.id,roomNumber:'211',roomTypeName:'스탠다드',performerProfileId:maid.id,performerDisplayName:maid.displayName,fieldCompletedAt:date+'T03:00:00Z',serviceDate:date,inspectionStatus:'approved',photoCount:8,mediaAvailability:'available',baseFeeSnapshot:16000,earningTotalAmount:16000};
let slot={slotId:id(7),slotKey:'cleaning-proof',maxPhotos:20,required:true,collectionRevision:0,photoCount:0,photos:[],uploadStatus:'missing'};
const slots=()=>({attemptId:attempt.attemptId,assignmentId:assignment.assignmentId,assignmentRevision:1,slots:[slot]});
let candle={roomId:room.id,roomNumber:'211',count:1,roomStateVersion:1},submitted=false;
let detailDelay=0,photoDelay=0,failPhoto=null,failDetail=false,failCandle=false,photoActive=0,photoMax=0,uploadsActive=0,uploadsMax=0;
const requests=[],errors=[],warnings=[],missing=[];
const source=await readFile('WIREFRAME/index.html','utf8');
const boot=`window.__fixQA={setup:({role='maid',view='done',assignment,attempt,payload,historyItem})=>{
  clearCleaningPhotoUrls();clearActiveCleaningPhotoUrls();LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});
  state.remote=initialRemoteState();state.detail=null;liveRoomDetail=null;state.role=role;state.liveView=view;state.remote.auth={...state.remote.auth,status:'authenticated',user:{...${JSON.stringify(maid)},role},session:{accessToken:'qa-only',refreshToken:'qa-refresh',expiresAt:Date.now()+3600000}};
  for(const key of ['rooms','accounts','roomTypes','reservations','notifications','availability','complaints','payroll','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});
  state.remote.accounts.items=[${JSON.stringify(maid)}];state.remote.rooms.items=[${JSON.stringify(room)}];Object.assign(state.remote.cleaningHistory,{items:[historyItem],date:'${date}',fromDate:'${date}',toDate:'${date}'});
  Object.assign(cleaningState(),{status:'ready',assignments:[assignment],attempts:new Map([[assignment.assignmentId,attempt]]),photoSlots:new Map([[attempt.attemptId,payload]]),expandedMaidAssignments:new Set([assignment.assignmentId]),maidAssignmentsInitialized:true});syncAuthState(state);rawCloseModal();render();
},render:()=>render(),state:()=>({busy:cleaningState().busy,queue:LIVE_PHOTO_QUEUE.length,running:livePhotoQueueRunning,detail:cleaningState().inspectionDetail?.status,photoUrls:LIVE_CLEANING_PHOTO_URLS.size}),refresh:()=>loadLiveCleaning(),blocked:()=>{state.detail={type:'liveAccounts'};render();},accountRender:()=>renderLiveAccounts(),view:view=>{state.liveView=view;render();},attemptStatus:status=>{cleaningState().attempts.get('${assignment.assignmentId}').status=status;render();}};`;
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(10000);
page.on('pageerror',error=>errors.push(error.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))warnings.push(m.text());});
const jpeg=Buffer.from(await page.evaluate(()=>{const c=document.createElement('canvas');c.width=2400;c.height=1600;const ctx=c.getContext('2d');ctx.fillStyle='#2b8369';ctx.fillRect(0,0,c.width,c.height);ctx.fillStyle='#fff';ctx.font='120px sans-serif';ctx.fillText('QA PHOTO FIXTURE',150,750);return c.toDataURL('image/jpeg',1).split(',')[1];}),'base64');
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const reply=(route,value,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(value)});
await page.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());
  if(url.origin===new URL(origin).origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace('\n      void bootApplication();',boot)});return route.continue();}
  if(!req.url().startsWith(api+'/')){missing.push(url.origin);return route.abort();}
  const path=url.pathname.replace('/functions/v1/api',''),method=req.method(),body=req.headers()['content-type']?.includes('application/json')?req.postDataJSON():null;
  requests.push({path,method,body,bytes:req.postDataBuffer()?.length||0});
  if(path==='/v1/cleaning-history/'+submission.id){await wait(detailDelay);return reply(route,failDetail?{error:{code:'CLEANING_HISTORY_ACCESS_REQUIRED'}}:{submission},failDetail?403:200);}
  if(path.startsWith('/v1/photos/')){photoActive++;photoMax=Math.max(photoMax,photoActive);await wait(photoDelay);photoActive--;if(path.includes(failPhoto))return reply(route,{error:{code:'PHOTO_CONTENT_UNAVAILABLE'}},503);return route.fulfill({contentType:'image/jpeg',body:jpeg});}
  if(path.endsWith('/supplemental-room-issues'))return reply(route,{source:{sourceSubmissionId:submission.id,sourceStatus:submission.status},reports:[]});
  if(path==='/v1/rooms/candles')return reply(route,{items:[candle],nextCursor:null});
  if(path===`/v1/rooms/${room.id}/candles`){assert.equal(body.expectedRoomVersion,candle.roomStateVersion);if(failCandle)return reply(route,{error:{code:'STALE_VERSION'}},409);if(body.count<candle.count)assert.equal(body.physicallyVerified,true);candle={...candle,count:body.count,roomStateVersion:candle.roomStateVersion+1};return reply(route,{operation:{roomId:room.id,roomStateVersion:candle.roomStateVersion}});}
  if(path==='/v1/assignments')return reply(route,{assignments:[assignment]});
  if(path==='/v1/assignment-change-requests')return reply(route,{requests:[],nextCursor:null});
  if(path==='/v1/attempts/current')return reply(route,{attempt});
  if(path===`/v1/attempts/${attempt.attemptId}/photo-slots`)return reply(route,slots());
  if(path.endsWith('/upload')){
    uploadsActive++;uploadsMax=Math.max(uploadsMax,uploadsActive);await wait(20);uploadsActive--;assert.equal(url.searchParams.get('expectedCollectionRevision'),String(slot.collectionRevision));
    const photoId=id(100+slot.photos.length),photoItemId=path.split('/').at(-2);slot.collectionRevision++;slot.photoCount++;slot.uploadStatus='verified';slot.photos.push({photoId,photoItemId,itemRevision:1,displayOrder:slot.photos.length,uploadStatus:'verified',mediaAvailability:'available'});return reply(route,{status:'accepted',photoId,collectionRevision:slot.collectionRevision,itemRevision:1});
  }
  if(path===`/v1/attempts/${attempt.attemptId}/complete-field-work`){attempt={...attempt,status:'field_completed',executionVersion:attempt.executionVersion+1,fieldCompletedAt:new Date().toISOString()};return reply(route,{attempt});}
  if(path===`/v1/attempts/${attempt.attemptId}/submissions`){if(method==='GET')return reply(route,{submissions:submitted?[submission]:[]});assert.equal(body.candleCount,candle.count);submitted=true;submission={...submission,status:'submitted',candleCount:body.candleCount,photos:slot.photos};attempt.status='submitted';return reply(route,{submission});}
  if(path==='/v1/cleaning-history')return reply(route,{items:[historyItem],fromDate:date,toDate:date,nextCursor:null});
  if(path==='/v1/notifications')return reply(route,{notifications:[],nextCursor:null});
  if(path==='/v1/accounts')return reply(route,{accounts:[maid]});
  missing.push(method+' '+path);return reply(route,{error:{code:'QA_UNEXPECTED'}},400);
});
const setup=async(role='maid',view='done')=>page.evaluate(data=>__fixQA.setup(data),{role,view,assignment,attempt,payload:slots(),historyItem});
const click=action=>page.locator(`[data-action="${action}"]:visible`).first().click();
const settled=()=>page.waitForFunction(()=>{const s=__fixQA.state();return !s.busy&&!s.queue&&!s.running;});
const shot=async name=>{await wait(150);await page.locator('#toast-region').evaluate(el=>el.replaceChildren());await page.evaluate(async()=>{document.activeElement?.blur();scrollTo({top:0,behavior:'instant'});await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));});if(name.startsWith('submission-'))await page.locator('[data-cleaning-submission]').scrollIntoViewIfNeeded();await page.screenshot({path:`WIREFRAME/QA/screenshots/maid-fixes-${name}.png`,fullPage:!name.startsWith('submission-')});};
try{
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await page.goto(origin+'/index.html');
  await setup('admin','more');assert.equal(await page.locator('[data-action="live-accounts-open"]').count(),0);await page.evaluate(()=>__fixQA.blocked());assert.equal(await page.getByRole('heading',{name:'계정 관리',exact:true}).count(),0);assert.equal(await page.evaluate(()=>__fixQA.accountRender()),'');
  const before=requests.length;for(const action of ['live-accounts-open','open-live-account-create','confirm-live-account-role','confirm-live-account-status','confirm-live-account-unlock','confirm-live-account-reset-password'])await page.evaluate(({action,id})=>{const b=document.createElement('button');b.dataset.action=action;b.dataset.id=id;b.dataset.role='admin';b.dataset.status='inactive';document.body.append(b);b.click();b.remove();},{action,id:maid.id});assert.equal(requests.length,before);assert.equal(await page.getByRole('dialog').count(),0);
  await shot('admin-more-390');await setup('developer','accounts');assert(await page.getByRole('heading',{name:'계정 관리',exact:true,level:2}).isVisible());await click('open-live-account-create');assert(await page.getByRole('dialog').isVisible());await page.keyboard.press('Escape');console.log('[ok] 계정 관리 개발자 전용 · 관리자 메뉴/직접 액션/구 이력 차단');
  await setup();detailDelay=650;photoDelay=450;failPhoto=id(21);await click('live-cleaning-history-detail');assert(await page.getByText('제출 내역을 불러오는 중입니다.',{exact:true}).isVisible());assert.equal(await page.title(),'청소 상세 · CASTLE THE ART');await page.getByRole('heading',{name:'청소 사진',exact:true}).waitFor();assert.equal(await page.locator('.inspection-gallery img').count(),0);await page.locator('.inspection-gallery img').first().waitFor();assert(await page.getByText('불러오는 중',{exact:true}).count()>0);await page.locator('[data-action="live-inspection-photo-retry"]').waitFor();await page.waitForFunction(()=>!document.querySelector('.inspection-gallery')?.textContent.includes('불러오는 중'));assert.equal(photoMax,4);assert.equal(requests.filter(r=>r.path.includes(id(27))).length,0,'expired photo never fetched');
  failPhoto=null;await click('live-inspection-photo-retry');await page.waitForFunction(()=>document.querySelectorAll('.inspection-gallery img').length===7);assert.equal(await page.locator('.inspection-gallery img').evaluateAll(imgs=>imgs.every(img=>img.complete&&img.naturalWidth>0)),true);assert.equal(await page.locator('.candle-stepper-value strong').innerText(),'1개','do not restore an old submission over recovered candles');
  await click('live-inspection-photo');await page.locator('.photo-viewer-visual img').waitFor();await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});await click('back');await page.getByRole('button',{name:'사진·제출 상세',exact:true}).waitFor();assert.equal(await page.evaluate(()=>__fixQA.state().photoUrls),0);
  failDetail=true;await click('live-cleaning-history-detail');await page.getByRole('button',{name:'다시 불러오기'}).waitFor();failDetail=false;detailDelay=0;photoDelay=0;await click('live-cleaning-history-detail');await page.getByRole('heading',{name:'청소 사진',exact:true}).waitFor();await page.waitForFunction(()=>!document.querySelector('.inspection-gallery')?.textContent.includes('불러오는 중'));await shot('history-390');console.log('[ok] 내역 버튼 즉시 진입 · 4개 제한 점진 표시 · 실패 재시도 · 만료/확대/뒤로가기');
  await setup('maid','my');const section=page.locator('[data-cleaning-submission]');assert.equal(await section.locator('[data-action="cleaning-complete"]').count(),1);assert.equal(await page.locator('[data-cleaning-assignment] [data-action="cleaning-complete"]').count(),0);await click('cleaning-complete');await page.waitForFunction(()=>!__fixQA.state().busy&&document.querySelector('[id^="cleaning-candles-"]')&&!document.querySelector('[id^="cleaning-candles-"]').disabled);
  const input=page.locator('[id^="cleaning-candles-"]');await input.fill('3');const beforeUploads=requests.length;await page.locator('[data-upload-source="gallery"]').first().setInputFiles(Array.from({length:20},(_,i)=>({name:`qa-${i}.jpg`,mimeType:'image/jpeg',buffer:jpeg})));await settled();assert.equal(slot.photos.length,20);assert.equal(uploadsMax,1);assert.equal(await input.inputValue(),'3','upload rerenders retain candle draft');
  const batch=requests.slice(beforeUploads),reads=batch.filter(r=>r.path.endsWith('/photo-slots')).length,contents=batch.filter(r=>r.path.startsWith('/v1/photos/')).length,uploads=batch.filter(r=>r.path.endsWith('/upload'));assert.equal(reads,21);assert.equal(contents,0);assert(uploads.every(r=>r.bytes<jpeg.length));console.log(`[ok] 20장 일괄 업로드: metadata GET 40→${reads}, 재다운로드 20→${contents}, 동시 쓰기 ${uploadsMax}, bytes ${jpeg.length}→${uploads[0].bytes}`);
  for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.equal(await section.locator('[data-action="cleaning-complete"]').evaluate(el=>el.getBoundingClientRect().height>=44),true);await shot('submission-'+width);}
  await page.setViewportSize({width:390,height:900});await click('cleaning-submit');await settled();assert.equal(candle.count,3);assert.equal(submission.candleCount,3);await page.waitForFunction(()=>document.querySelector('.candle-stepper-value strong')?.textContent==='3개');console.log('[ok] 현장 완료 위치 · 촛불 초안 유지 · 제출/현재 수량 3개 동기화 · 4개 폭');
  submitted=false;attempt.status='field_completed';await setup('maid','my');await input.fill('1');await click('cleaning-submit');await page.getByRole('heading',{name:'촛불을 회수했나요?',exact:true}).waitFor();assert.equal(submitted,false);candle.roomStateVersion++;await click('cleaning-submit-confirm');await settled();assert.equal(submitted,false,'stale confirmation cannot submit');await click('cleaning-submit');await page.getByRole('heading',{name:'촛불을 회수했나요?',exact:true}).waitFor();await click('cleaning-submit-confirm');await settled();assert.equal(submitted,true);assert.equal(candle.count,1);
  submitted=false;attempt.status='field_completed';await setup('maid','my');await input.fill('3');failCandle=true;await click('cleaning-submit');await settled();assert.equal(submitted,false);assert.equal(candle.count,1);failCandle=false;console.log('[ok] 촛불 감소 물리 확인 · stale CAS/저장 실패 시 제출 차단');
  await setup();detailDelay=300;await click('live-cleaning-history-detail');await page.locator('[data-action="nav"][data-view="more"]:visible').first().click();await wait(800);assert.equal(await page.locator('.inspection-gallery').count(),0);assert.equal(await page.evaluate(()=>__fixQA.state().photoUrls),0);assert(!JSON.stringify(await page.evaluate(()=>history.state)).includes('blob:'));
  assert.deepEqual(missing,[]);assert.deepEqual(errors,[]);assert.deepEqual(warnings,[]);console.log('[ok] 조회 중 이동·늦은 응답 차단 · history 사진 원문 없음 · console/page error 없음');
}finally{await browser.close();}
