#!/usr/bin/env node
// Synthetic API fixtures only. No operational uploads or mutations.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
const {chromium}=createRequire(import.meta.url)('playwright');
const source=process.env.RMS_QA_BASELINE?execFileSync('git',['show',`${process.env.RMS_QA_BASELINE}:WIREFRAME/index.html`],{encoding:'utf8',maxBuffer:4e6}):await readFile('WIREFRAME/index.html','utf8');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>`77000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul'}).format(new Date());
const assignments=[0,1].map(i=>({assignmentId:id(10+i),cleaningTargetId:id(20+i),roomId:id(30+i),roomNumber:String(211+i),roomTypeCode:'standard',roomTypeName:'QA 스탠다드',maidProfileId:id(1),maidDisplayName:'QA 메이드',serviceDate:date,revision:1,isCurrent:true,notifiedAt:date+'T01:00:00Z',feeSnapshot:16000,availableFrom:date+'T01:00:00Z'}));
const attempts=assignments.map((a,i)=>({attemptId:id(40+i),assignmentId:a.assignmentId,assignmentRevision:1,executionVersion:1,status:i?'scheduled':'field_completed',startedAt:i?null:date+'T02:00:00Z',fieldCompletedAt:i?null:date+'T03:00:00Z'}));
const slots=assignments.map((a,i)=>['cleaning-proof','issue-proof'].map((slotKey,j)=>({slotId:id(50+i*2+j),slotKey,maxPhotos:j?10:20,required:!j,collectionRevision:0,photos:[],photoCount:0,uploadStatus:'missing'})));
const payload=i=>({attemptId:attempts[i].attemptId,assignmentId:assignments[i].assignmentId,assignmentRevision:1,slots:structuredClone(slots[i])});
const boot=`window.__queueQA={setup:payloads=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_qa_fixture_not_a_real_key_1234567890',featureFlags:{optionalCleaningWorkflow:true,photoUploadSnapshot:true}});state.remote=initialRemoteState();state.role='maid';state.liveView='my';state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${id(1)}',role:'maid',displayName:'QA 메이드'},session:{accessToken:'qa-fixture',expiresAt:Date.now()+3600000}};for(const key of ['rooms','notifications','complaints','availability','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});Object.assign(cleaningState(),{status:'ready',assignments:${JSON.stringify(assignments)},attempts:new Map(${JSON.stringify(attempts.map((a,i)=>[assignments[i].assignmentId,a]))}),photoSlots:new Map(payloads.map(p=>[p.attemptId,p])),expandedMaidAssignments:new Set(${JSON.stringify(assignments.map(a=>a.assignmentId))}),maidAssignmentsInitialized:true});syncAuthState(state);render();},get:()=>({queue:LIVE_PHOTO_QUEUE.length,running:livePhotoQueueRunning,busy:cleaningState().busy,slots:[...cleaningState().photoSlots.values()],attempts:[...cleaningState().attempts.values()]}),reload:()=>loadLiveCleaning({quiet:true})};`;
const browser=await chromium.launch({headless:true});
const helpers='window.__queueQA.merge=(incoming,current)=>mergeLivePhotoSlotRevisions(incoming,current);window.__queueQA.submit=id=>submitLiveCleaning(id);';
const page=await browser.newPage({viewport:{width:390,height:900},serviceWorkers:'block'});
const errors=[],unexpected=[],writes=[];
let releaseUpload=null,holdUploads=true,holdRead=false,releaseRead=null,active=0,maxActive=0,jpeg,failFirstRoom=false;
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))errors.push(m.text());});
const json=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(data)});
await page.route('**/*',async route=>{
  const request=route.request(),url=new URL(request.url()),method=request.method();
  if(url.origin===origin){if(url.pathname==='/index.html')return route.fulfill({contentType:'text/html',body:source.replace('\n      void bootApplication();',boot+helpers)});return route.continue();}
  if(!request.url().startsWith(api+'/')){unexpected.push(url.origin);return route.abort();}
  const path=url.pathname.replace('/functions/v1/api','');
  if(path==='/v1/assignments')return json(route,{assignments});
  if(path==='/v1/assignment-change-requests')return json(route,{requests:[],nextCursor:null});
  if(path==='/v1/notifications')return json(route,{notifications:[],nextCursor:null});
  if(path==='/v1/complaints')return json(route,{complaints:[],nextCursor:null});
  if(path==='/v1/attempts/current')return json(route,{attempt:attempts[assignments.findIndex(a=>a.assignmentId===url.searchParams.get('assignmentId'))]});
  if(path.startsWith('/v1/photos/'))return route.fulfill({contentType:'image/jpeg',body:jpeg});
  const i=attempts.findIndex(a=>path.startsWith('/v1/attempts/'+a.attemptId+'/'));
  if(i>=0){
    if(path.endsWith('/photo-slots')){const response=payload(i);if(holdRead&&i===0){holdRead=false;await new Promise(resolve=>{releaseRead=resolve;});}return json(route,response);}
    if(path.endsWith('/submissions'))return json(route,{submissions:[]});
    if(path.endsWith('/start')||path.endsWith('/complete-field-work')){assert.equal(method,'POST');writes.push({i,path});attempts[i].executionVersion++;attempts[i].status=path.endsWith('/start')?'in_progress':'field_completed';attempts[i].startedAt=date+'T04:00:00Z';if(attempts[i].status==='field_completed')attempts[i].fieldCompletedAt=date+'T04:30:00Z';return json(route,{attempt:attempts[i]});}
    if(path.endsWith('/upload')){
      active++;maxActive=Math.max(maxActive,active);writes.push({i,path,key:request.headers()['idempotency-key']});
      if(holdUploads)await new Promise(resolve=>{releaseUpload=resolve;});
      if(failFirstRoom&&i===0){failFirstRoom=false;active--;return json(route,{error:{code:'PHOTO_PROVIDER_UNAVAILABLE'}},503);}
      const slot=slots[i][0];assert.equal(url.searchParams.get('expectedCollectionRevision'),String(slot.collectionRevision));
      const photoItemId=path.split('/').at(-2),photoId=id(100+i*30+slot.photos.length);slot.collectionRevision++;slot.photoCount++;slot.uploadStatus='verified';slot.photos.push({photoId,photoItemId,itemRevision:1,displayOrder:slot.photos.length,uploadStatus:'verified',mediaAvailability:'available'});active--;
      return json(route,{status:'accepted',photoId,photoItemId,collectionRevision:slot.collectionRevision,itemRevision:1,photoSlots:payload(i)});
    }
  }
  unexpected.push(method+' '+path);return json(route,{error:{code:'QA_UNEXPECTED'}},400);
});
const until=async test=>{for(let n=0;n<200&&!test();n++)await new Promise(resolve=>setTimeout(resolve,10));assert(test(),'fixture signal timeout');};
const gallery=i=>page.locator(`[data-slot="${slots[i][0].slotId}"][data-upload-source="gallery"]`);
const files=n=>Array.from({length:n},(_,i)=>({name:`qa-${i}.jpg`,mimeType:'image/jpeg',buffer:jpeg}));
const settled=()=>page.waitForFunction(()=>!__queueQA.get().running&&!__queueQA.get().busy);
try{
  await page.goto(origin+'/index.html');
  jpeg=Buffer.from(await page.evaluate(()=>{const c=document.createElement('canvas');c.width=300;c.height=200;const x=c.getContext('2d');x.fillStyle='#247c64';x.fillRect(0,0,300,200);x.fillStyle='#fff';x.fillText('QA PHOTO',80,100);return c.toDataURL('image/jpeg').split(',')[1];}),'base64');
  await page.evaluate(p=>__queueQA.setup(p),[payload(0),payload(1)]);
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  await page.screenshot({path:`WIREFRAME/QA/screenshots/photo-queue-idle-${process.env.RMS_QA_BASELINE?'before':'after'}-390.png`});
  await gallery(0).setInputFiles(files(1));await until(()=>!!releaseUpload);
  holdRead=true;
  await page.locator(`[data-action="cleaning-start"][data-id="${assignments[1].assignmentId}"]`).click();
  await until(()=>!!releaseRead);
  holdUploads=false;releaseUpload();releaseUpload=null;
  await page.waitForFunction(()=>!__queueQA.get().running);
  assert.equal((await page.evaluate(()=>__queueQA.get())).slots.find(p=>p.attemptId===attempts[0].attemptId).slots[0].photoCount,1);
  releaseRead();releaseRead=null;await settled();
  assert.equal((await page.evaluate(()=>__queueQA.get())).slots.find(p=>p.attemptId===attempts[0].attemptId).slots[0].photoCount,1,'late unrelated-room reload must not overwrite accepted photos');
  assert.equal(attempts[1].status,'in_progress');
  console.log('[ok] another room starts while upload runs; late read cannot regress accepted photos');
  assert(await page.evaluate(p=>{
    const current=structuredClone(p);current.slots[0].collectionRevision=4;
    const incoming=structuredClone(current);incoming.slots[0].collectionRevision=3;incoming.slots[0].photos=[];
    if(__queueQA.merge(incoming,current).slots[0].photos.length!==1)return false;
    incoming.slots[0].collectionRevision=5;
    if(__queueQA.merge(incoming,current).slots[0].photos.length!==0)return false;
    incoming.slots[0].collectionRevision=4;incoming.slots[0].mediaAvailability='purged';
    if(__queueQA.merge(incoming,current).slots[0].mediaAvailability!=='purged')return false;
    incoming.slots[0].collectionRevision=3;
    for(const key of ['attemptId','assignmentId','assignmentRevision']){
      const changed={...incoming,[key]:key==='assignmentRevision'?2:'changed'};
      if(__queueQA.merge(changed,current).slots[0].photos.length!==0)return false;
    }
    const legacy=structuredClone(current);legacy.slots[0].maxPhotos=1;legacy.slots[0].currentRevision=4;
    const old=structuredClone(legacy);old.slots[0].currentRevision=3;old.slots[0].photos=[];
    return __queueQA.merge(old,legacy).slots[0].photos.length===1;
  },payload(0)));
  console.log('[ok] revision merge preserves newer delete/purge and isolates assignment/attempt changes');

  holdUploads=true;await gallery(0).setInputFiles(files(1));await until(()=>!!releaseUpload);
  const memo=page.locator('#cleaning-issue-memo-'+attempts[1].attemptId);await memo.fill('QA draft stays focused');
  await memo.evaluate(el=>{window.__focusedMemo=el;el.setSelectionRange(3,8);});
  holdUploads=false;releaseUpload();releaseUpload=null;await settled();
  assert(await memo.evaluate(el=>el===window.__focusedMemo&&document.activeElement===el&&el.selectionStart===3&&el.selectionEnd===8),'upload completion must preserve another room input node, focus and selection');
  assert.equal(await memo.inputValue(),'QA draft stays focused');
  console.log('[ok] upload completion preserves unrelated input, cursor and draft');

  holdUploads=true;await gallery(0).setInputFiles(files(2));await until(()=>!!releaseUpload);
  await page.locator(`[data-action="cleaning-complete"][data-id="${assignments[1].assignmentId}"]`).click();
  await page.waitForFunction(()=>!__queueQA.get().busy);assert.equal(attempts[1].status,'field_completed');
  await gallery(1).setInputFiles(files(2));assert.equal((await page.evaluate(()=>__queueQA.get())).queue,4);
  assert(await page.locator(`[data-action="cleaning-submit"][data-id="${assignments[0].assignmentId}"]`).isDisabled());
  assert(await page.locator(`[data-action="cleaning-submit"][data-id="${assignments[1].assignmentId}"]`).isDisabled());
  assert((await page.locator('#toast-region').innerText()).includes('전송 대기'));
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`WIREFRAME/QA/screenshots/photo-queue-handoff-${width}.png`});
  }
  const writeCount=writes.length;await page.evaluate(id=>__queueQA.submit(id),assignments[0].assignmentId);
  assert.equal(writes.length,writeCount,'pending uploads must block submission in the command handler too');
  await page.locator('[data-action="nav"][data-view="more"]:visible').first().click();
  assert((await page.locator('[data-live-photo-queue-status]').innerText()).includes('4장'));
  holdUploads=false;releaseUpload();releaseUpload=null;await settled();
  assert.equal(slots[0][0].photos.length,4);assert.equal(slots[1][0].photos.length,2);assert.equal(maxActive,1);
  await page.locator('[data-action="nav"][data-view="my"]:visible').first().click();await settled();
  await page.waitForFunction(()=>__queueQA.get().slots.reduce((n,p)=>n+p.slots[0].photoCount,0)===6);
  assert.equal(await page.locator('[data-cleaning-photo-item]').count(),6);
  assert.equal(await page.locator(`[data-action="cleaning-submit"][data-id="${assignments[1].assignmentId}"]`).isDisabled(),false);
  console.log('[ok] another room completes; 2-room additions and navigation keep serial uploads and submission guards');

  holdUploads=true;failFirstRoom=true;await gallery(0).setInputFiles(files(1));await until(()=>!!releaseUpload);await gallery(1).setInputFiles(files(1));
  holdUploads=false;releaseUpload();releaseUpload=null;await settled();
  assert.equal(slots[0][0].photos.length,4);assert.equal(slots[1][0].photos.length,3);assert.equal((await page.evaluate(()=>__queueQA.get())).queue,1);
  assert((await page.locator('[data-live-photo-queue-status]').innerText()).includes('확인 필요'));
  const failedWrite=writes.filter(w=>w.i===0&&w.key).at(-1);
  await page.locator(`[data-photo-slot="${slots[0][0].slotId}"] [data-action="live-photo-retry"]`).first().click();await settled();
  assert.equal(slots[0][0].photos.length,5);assert.equal(writes.filter(w=>w.i===0&&w.key).at(-1).key,failedWrite.key);assert.equal(maxActive,1);
  console.log('[ok] one room failure does not stop another room; attention status and same-key retry');
  assert.deepEqual(unexpected,[]);assert.deepEqual(errors,[]);
  console.log('[ok] 360/390/768/1440px, nonblank maid screen, no console/page errors; synthetic writes only');
}finally{releaseUpload?.();releaseRead?.();await browser.close();}
