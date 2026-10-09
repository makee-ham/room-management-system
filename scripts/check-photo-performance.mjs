#!/usr/bin/env node
// Browser plugin not available. Synthetic fixtures only; no operational photo writes.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const baseline=execFileSync('git',['show','314f0d7:WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:4e6});
const source=await readFile('WIREFRAME/index.html','utf8');
const id=n=>`76000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul'}).format(new Date());
const actor={id:id(1),profileId:id(1),role:'maid',displayName:'QA 메이드',loginId:'QA',status:'active'};
const assignment={assignmentId:id(2),cleaningTargetId:id(3),roomId:id(4),roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',maidProfileId:actor.id,maidDisplayName:actor.displayName,serviceDate:date,revision:1,isCurrent:true,notifiedAt:date+'T01:00:00Z',feeSnapshot:16000,availableFrom:date+'T01:00:00Z'};
const attempt={attemptId:id(5),assignmentId:assignment.assignmentId,assignmentRevision:1,executionVersion:1,status:'field_completed',startedAt:date+'T02:00:00Z',fieldCompletedAt:date+'T03:00:00Z'};
const browser=await chromium.launch({headless:true});
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const metrics=[];
let jpeg;
async function fixture({old=false,snapshot=false,mode='valid',prepareMs=0,uploadMs=25,readMs=10,cpu=1}={}){
  const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
  const cdp=await context.newCDPSession(page);await cdp.send('Emulation.setCPUThrottlingRate',{rate:cpu});
  const slot={slotId:id(6),slotKey:'cleaning-proof',maxPhotos:20,required:true,collectionRevision:0,photos:[],photoCount:0,uploadStatus:'missing'};
  const payload=()=>({attemptId:attempt.attemptId,assignmentId:assignment.assignmentId,assignmentRevision:1,slots:[structuredClone(slot)]});
  const calls=[],errors=[],missing=[],receipts=new Map();let active=0,maxActive=0,lost=false,refreshFailed=false,conflict=false,readsActive=0,maxReads=0,operationReady=false;
  const boot=`
    const originalOptimize=optimizeLivePhoto,originalRender=render;let prepares=0,maxPrepares=0,renders=0;
    optimizeLivePhoto=async file=>{prepares++;maxPrepares=Math.max(maxPrepares,prepares);try{await new Promise(resolve=>setTimeout(resolve,${prepareMs}));return await originalOptimize(file);}finally{prepares--;}};
    render=()=>{renders++;return originalRender();};
    window.__photoQA={setup:payload=>{LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true,photoUploadSnapshot:${snapshot}}});
      state.remote=initialRemoteState();state.role='maid';state.liveView='my';state.detail=null;liveRoomDetail=null;state.remote.auth={...state.remote.auth,status:'authenticated',user:${JSON.stringify(actor)},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
      for(const key of ['rooms','accounts','notifications','complaints','availability','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});
      Object.assign(cleaningState(),{status:'ready',assignments:[${JSON.stringify(assignment)}],attempts:new Map([['${assignment.assignmentId}',${JSON.stringify(attempt)}]]),photoSlots:new Map([['${attempt.attemptId}',payload]]),expandedMaidAssignments:new Set(['${assignment.assignmentId}']),maidAssignmentsInitialized:true});syncAuthState(state);render();renders=0;
    },state:()=>({queue:LIVE_PHOTO_QUEUE.length,running:livePhotoQueueRunning,errors:LIVE_PHOTO_QUEUE.filter(job=>job.error).length,prepares,maxPrepares,renders,prepared:LIVE_PHOTO_QUEUE.filter(job=>job.blob).length,previewUrls:LIVE_PHOTO_QUEUE.filter(job=>job.previewUrl).length,activeUrls:LIVE_CLEANING_ACTIVE_PHOTO_URLS.size,progress:cleaningState().uploadStates.get('${slot.slotId}'),jobs:LIVE_PHOTO_QUEUE.map(job=>({id:job.photoItemId,accepted:job.receipt?.status==='accepted'}))}),
      retry:id=>retryLivePhotoQueue(id),discard:()=>discardLivePhotoQueue('${slot.slotId}'),logout:()=>{LIVE_RUNTIME.authGeneration++;clearLiveAuthSurface();state.remote.auth.status='anonymous';render();},
      details:photos=>{clearCleaningPhotoUrls();state.liveView='done';cleaningState().inspectionDetail={readOnly:true,status:'ready',submission:{id:'${id(10)}',status:'approved',submittedAt:new Date().toISOString(),photos},photos:photos.map(photo=>({...photo,loading:true}))};render();return loadLiveInspectionPhotos(cleaningState().inspectionDetail);},
      priority:photos=>{const result=[];while(photos.length)result.push(takeVisibleLivePhoto(photos).photoId);return result;}
    };`;
  page.on('pageerror',error=>errors.push(error.message));
  page.on('console',message=>{if(['warning','error'].includes(message.type())&&!message.text().startsWith('Failed to load resource:')&&!message.text().includes('net::ERR_FAILED'))errors.push(message.text());});
  const json=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(data)});
  await page.route('**/*',async route=>{
    const request=route.request(),url=new URL(request.url());
    if(url.origin===new URL(origin).origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:(old?baseline:source).replace('\n      void bootApplication();',boot)});return route.continue();}
    if(!request.url().startsWith(api+'/')){missing.push(url.origin);return route.abort();}
    const path=url.pathname.replace('/functions/v1/api',''),method=request.method();
    calls.push({path,method,key:request.headers()['idempotency-key'],hash:request.postDataBuffer()?createHash('sha256').update(request.postDataBuffer()).digest('hex'):null,bytes:request.postDataBuffer()?.length||0,optIn:url.searchParams.get('includePhotoSlots'),at:Date.now()});
    if(path.endsWith('/photo-slots')){await wait(readMs);if(mode==='refresh-failure'&&slot.photos.length&&!refreshFailed){refreshFailed=true;return json(route,{error:{code:'PHOTO_CONTENT_UNAVAILABLE'}},503);}return json(route,payload());}
    if(path.endsWith('/upload')){
      active++;maxActive=Math.max(active,maxActive);await wait(uploadMs);active--;
      if(mode==='conflict'&&!conflict){conflict=true;return json(route,{error:{code:'PHOTO_COLLECTION_REVISION_CONFLICT'}},409);}
      if(mode==='validation-after-first'&&slot.photos.length===1&&!conflict){conflict=true;return json(route,{error:{code:'VALIDATION_ERROR'}},400);}
      const key=request.headers()['idempotency-key'];
      let receipt=receipts.get(key);
      if(!receipt){
        assert.equal(url.searchParams.get('expectedCollectionRevision'),String(slot.collectionRevision));
        const photoId=id(100+slot.photos.length),photoItemId=path.split('/').at(-2);slot.collectionRevision++;slot.photoCount++;slot.uploadStatus='verified';slot.photos.push({photoId,photoItemId,itemRevision:1,displayOrder:slot.photos.length,uploadStatus:'verified',mediaAvailability:'available'});
        receipt={operationId:id(50),attemptId:attempt.attemptId,targetSlotId:slot.slotId,photoItemId,status:'accepted',photoId,collectionRevision:slot.collectionRevision,itemRevision:1};receipts.set(key,receipt);
      }
      if(mode==='lost'&&!lost){lost=true;return route.abort('failed');}
      if(mode==='operation'&&!operationReady)return json(route,{...receipt,status:'reconciliation_pending',photoId:null,photoSlots:null});
      const data={...receipt};
      if(url.searchParams.get('includePhotoSlots'))data.photoSlots=['null','refresh-failure'].includes(mode)?null:mode==='mismatch'?{...payload(),assignmentRevision:2}:payload();
      return json(route,data);
    }
    if(path.startsWith('/v1/photo-uploads/'))return json(route,operationReady?[...receipts.values()][0]:{operationId:id(50),status:'reconciliation_pending',photoId:null});
    if(path.startsWith('/v1/photos/')){readsActive++;maxReads=Math.max(maxReads,readsActive);await wait(readMs);readsActive--;return route.fulfill({contentType:'image/jpeg',body:jpeg});}
    if(path==='/v1/notifications')return json(route,{notifications:[],nextCursor:null});
    if(path==='/v1/complaints')return json(route,{complaints:[],nextCursor:null});
    if(path==='/v1/assignments')return json(route,{assignments:[assignment]});
    if(path==='/v1/assignment-change-requests')return json(route,{requests:[],nextCursor:null});
    if(path==='/v1/attempts/current')return json(route,{attempt});
    if(path.endsWith('/submissions'))return json(route,{submissions:[]});
    missing.push(method+' '+path);return json(route,{error:{code:'QA_UNEXPECTED'}},400);
  });
  await page.goto(origin+'/index.html');
  if(!jpeg)jpeg=Buffer.from(await page.evaluate(()=>{const canvas=document.createElement('canvas');canvas.width=2400;canvas.height=1600;const ctx=canvas.getContext('2d');ctx.fillStyle='#2c8968';ctx.fillRect(0,0,2400,1600);ctx.fillStyle='#fff';ctx.font='110px sans-serif';ctx.fillText('QA PHOTO FIXTURE',150,700);return canvas.toDataURL('image/jpeg',1).split(',')[1];}),'base64');
  await page.evaluate(payload=>__photoQA.setup(payload),payload());
  await page.locator('[data-photo-slot]').first().scrollIntoViewIfNeeded();
  const settled=()=>page.waitForFunction(()=>!__photoQA.state().running);
  const upload=async(count,{heic=false}={})=>{await page.locator('[data-upload-source="gallery"]').first().setInputFiles(Array.from({length:count},(_,i)=>({name:`fixture-${i}.${heic?'heic':'jpg'}`,mimeType:heic?'image/heic':'image/jpeg',buffer:heic?Buffer.from('synthetic-undecodable-heic'):jpeg})));};
  return {page,context,calls,slot,upload,settled,payload,operationReady:()=>{operationReady=true;},stats:()=>({maxActive,maxReads}),close:async()=>{assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);await context.close();}};
}
try{
  for(const count of (process.env.RMS_QA_SKIP_BENCH?[]:[1,5,20]))for(const kind of ['baseline','current','snapshot']){
    const f=await fixture({old:kind==='baseline',snapshot:kind==='snapshot',prepareMs:80,uploadMs:140,readMs:60,cpu:4});
    const start=Date.now();await f.upload(count);
    const firstSelector=kind==='baseline'?'[data-cleaning-photo-item] img':'[data-queued-photo] img,[data-cleaning-photo-item] img';
    await f.page.locator(firstSelector).first().waitFor();await f.page.waitForFunction(selector=>{const img=document.querySelector(selector);return img?.complete&&img.naturalWidth>0;},firstSelector);const first=Date.now()-start;
    if(kind!=='baseline')assert.equal(f.calls.filter(call=>call.path.endsWith('/upload')).length,0,'local preview before upload completion');
    await f.settled();const upload=Date.now()-start;
    await f.page.waitForFunction(n=>{const images=[...document.querySelectorAll('[data-cleaning-photo-item] img')];return images.length===n&&images.every(img=>img.complete&&img.naturalWidth>0);},count);const all=Date.now()-start;
    const state=await f.page.evaluate(()=>__photoQA.state());
    assert.equal(f.slot.photos.length,count);assert.equal(f.stats().maxActive,1);assert(state.maxPrepares<=1);assert.equal(state.queue,0);
    const posts=f.calls.filter(call=>call.path.endsWith('/upload')),gets=f.calls.filter(call=>call.path.endsWith('/photo-slots')).length;
    assert.equal(gets,kind==='snapshot'?1:count+1);assert(posts.every(call=>call.optIn===(kind==='snapshot'?'true':null)));
    assert.equal(f.calls.filter(call=>call.path.startsWith('/v1/photos/')).length,0);
    if(kind!=='baseline'){assert.equal(state.progress.completed,count);assert.equal(state.progress.total,count);assert(state.renders<=3,`full renders bounded: ${state.renders}`);}
    metrics.push({kind,count,firstMs:first,uploadMs:upload,allMs:all,slotGET:gets,contentGET:0,fullRenders:state.renders});await f.close();
  }
  if(metrics.length)console.log('[ok] 1/5/20 JPEG · 4x CPU · simulated preparation/network latency · serial CAS · cumulative progress · bounded renders');
  for(const mode of ['null','mismatch','refresh-failure','lost','conflict','operation']){
    const f=await fixture({snapshot:true,mode});await f.upload(2);await f.settled();
    if(['refresh-failure','lost','conflict','operation'].includes(mode)){
      const failed=await f.page.evaluate(()=>__photoQA.state());assert.equal(failed.errors,1,mode);const firstPosts=f.calls.filter(call=>call.path.endsWith('/upload'));
      if(mode==='lost'){await f.page.locator('[data-photo-slot]').first().scrollIntoViewIfNeeded();await f.page.screenshot({path:'WIREFRAME/QA/screenshots/photo-performance-retry-390.png'});}
      f.operationReady();await f.page.locator(`[data-action="live-photo-retry"][data-id="${failed.jobs[0].id}"]`).click();await f.settled();
      const posts=f.calls.filter(call=>call.path.endsWith('/upload'));
      if(['refresh-failure','operation'].includes(mode))assert.equal(posts.length,2,'accepted or pending operation never uploads again');
      else{assert.equal(posts[1].key,firstPosts[0].key);assert.equal(posts[1].hash,firstPosts[0].hash);assert.equal(posts[1].path,firstPosts[0].path);}
    }
    assert.equal(f.slot.photos.length,2);assert.equal((await f.page.evaluate(()=>__photoQA.state())).queue,0);
    if(['null','mismatch'].includes(mode))assert.equal(f.calls.filter(call=>call.path.endsWith('/photo-slots')).length,3);
    await f.close();
  }
  console.log('[ok] snapshot/null/mismatch · accepted GET failure · lost response · 409 · pending operation · exact key/bytes retry');
  const heic=await fixture();await heic.upload(5,{heic:true});await heic.settled();assert.equal(heic.slot.photos.length,5);assert(heic.calls.filter(call=>call.method==='POST').every(call=>call.bytes===Buffer.byteLength('synthetic-undecodable-heic')));await heic.close();
  console.log('[ok] HEIC decode-unavailable original-byte fallback (synthetic, not device codec validation)');
  const added=await fixture({uploadMs:250});await added.upload(3);await added.upload(2);await added.upload(18);await added.settled();assert.equal(added.slot.photos.length,5);assert.equal((await added.page.evaluate(()=>__photoQA.state())).progress.total,5);await added.close();
  console.log('[ok] add photos during upload · combined progress · over-20 selection rejected');
  const replace=await fixture({mode:'validation-after-first'});await replace.upload(3);await replace.settled();assert.equal(replace.slot.photos.length,1);await replace.upload(1);await replace.settled();assert.equal(replace.slot.photos.length,3);assert.equal((await replace.page.evaluate(()=>__photoQA.state())).progress.total,3);assert.equal((await replace.page.evaluate(()=>__photoQA.state())).progress.completed,3);await replace.close();
  const view=await fixture({uploadMs:900,prepareMs:150});await view.upload(5);
  await view.page.waitForFunction(()=>__photoQA.state().prepared>=2);assert.equal((await view.page.evaluate(()=>__photoQA.state())).prepared,2,'current plus one prepared image');
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  for(const width of [360,390,768,1440]){
    await view.page.setViewportSize({width,height:900});await view.page.locator('[data-photo-slot]').first().evaluate(el=>scrollTo({top:scrollY+el.getBoundingClientRect().top-document.querySelector('.topbar').getBoundingClientRect().bottom-16,behavior:'instant'}));
    await view.page.waitForFunction(()=>[...document.querySelectorAll('[data-queued-photo] img')].filter(img=>{const r=img.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0;}).every(img=>img.complete&&img.naturalWidth>0));
    assert.equal(await view.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await view.page.screenshot({path:`WIREFRAME/QA/screenshots/photo-performance-${width}.png`});
  }
  await view.page.locator('[data-action="nav"][data-view="more"]:visible').first().click();
  assert.equal((await view.page.evaluate(()=>__photoQA.state())).previewUrls,0);await view.settled();assert.equal(view.slot.photos.length,5);assert.equal((await view.page.evaluate(()=>__photoQA.state())).activeUrls,0);
  assert(!JSON.stringify(await view.page.evaluate(()=>({history:history.state,local:{...localStorage},session:{...sessionStorage}}))).includes('blob:'));await view.close();
  const logout=await fixture({prepareMs:400,uploadMs:600});await logout.upload(5);await logout.page.evaluate(()=>__photoQA.logout());await wait(1200);
  assert.equal((await logout.page.evaluate(()=>__photoQA.state())).queue,0);assert.equal((await logout.page.evaluate(()=>__photoQA.state())).activeUrls,0);assert.equal(logout.calls.filter(call=>call.method==='POST').length,0);await logout.close();
  const inFlight=await fixture({uploadMs:500});await inFlight.upload(5);await inFlight.page.waitForFunction(()=>__photoQA.state().prepared>=2);await inFlight.page.evaluate(()=>__photoQA.logout());await wait(900);assert.equal((await inFlight.page.evaluate(()=>__photoQA.state())).queue,0);assert.equal((await inFlight.page.evaluate(()=>__photoQA.state())).activeUrls,0);assert.equal(inFlight.calls.filter(call=>call.method==='POST').length,1);await inFlight.close();
  console.log('[ok] 4 viewport layouts · navigation preserves serial queue and clears URLs · logout discards pending preparation');
  const reads=await fixture({readMs:250}),photos=Array.from({length:20},(_,i)=>({photoId:id(300+i),slotKey:'cleaning-proof'}));
  const readStart=Date.now();await reads.page.evaluate(photos=>{void __photoQA.details(photos);},photos);
  const firstCard=reads.page.locator('.inspection-photo').first(),height=await firstCard.evaluate(el=>el.getBoundingClientRect().height);
  await reads.page.waitForFunction(()=>[...document.querySelectorAll('.inspection-gallery img')].some(img=>img.complete&&img.naturalWidth>0));const firstRead=Date.now()-readStart;
  await reads.page.waitForFunction(()=>{const images=[...document.querySelectorAll('.inspection-gallery img')];return images.length===20&&images.every(img=>img.complete&&img.naturalWidth>0);});const allRead=Date.now()-readStart;
  assert.equal(reads.stats().maxReads,4);assert(Math.abs(await firstCard.evaluate(el=>el.getBoundingClientRect().height)-height)<2,'placeholder dimensions stable');
  assert.equal((await reads.page.evaluate(()=>__photoQA.state())).renders,1,'photo reads do not replace the main surface');
  await reads.page.locator('.inspection-photo').nth(16).evaluate(el=>el.scrollIntoView({behavior:'instant',block:'center'}));await wait(100);const prioritized=await reads.page.evaluate(photos=>__photoQA.priority(photos),photos);assert.notEqual(prioritized[0],photos[0].photoId);assert(await reads.page.locator(`[data-live-photo-id="${prioritized[0]}"]`).evaluate(el=>{const r=el.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight;}),'visible photos precede offscreen photos');
  await reads.page.locator('.inspection-photo').nth(16).focus();await reads.page.keyboard.press('Enter');await reads.page.getByRole('dialog').waitFor();await reads.page.keyboard.press('Escape');await reads.page.getByRole('dialog').waitFor({state:'hidden'});
  await reads.page.waitForFunction(id=>document.activeElement?.dataset.id===id,photos[16].photoId,{timeout:2000});await reads.close();
  console.log(`[ok] visible-first 4 reads · stable placeholders · keyboard/viewer/focus · first ${firstRead}ms / all ${allRead}ms (simulated)`);
  console.table(metrics);
}finally{await browser.close();}
