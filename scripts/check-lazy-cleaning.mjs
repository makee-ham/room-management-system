#!/usr/bin/env node
// All data and writes are intercepted fixtures, never operational records.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const source=await readFile('WIREFRAME/index.html','utf8');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>`78000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul'}).format(new Date());
const assignments=[0,1,2].map(i=>({assignmentId:id(10+i),cleaningTargetId:id(20+i),roomId:id(30+i),roomNumber:String(211+i),roomTypeCode:'standard',roomTypeName:'QA 스탠다드',maidProfileId:id(1),maidDisplayName:'QA 메이드',serviceDate:date,revision:1,isCurrent:true,notifiedAt:date+'T01:00:00Z',feeSnapshot:16000,availableFrom:date+'T01:00:00Z'}));
const attempts=assignments.map((a,i)=>({attemptId:id(40+i),assignmentId:a.assignmentId,assignmentRevision:1,executionVersion:1,status:['field_completed','scheduled','submitted'][i],startedAt:i===1?null:date+'T02:00:00Z',fieldCompletedAt:i===1?null:date+'T03:00:00Z'}));
const slots=assignments.map((a,i)=>({slotId:id(50+i),slotKey:'cleaning-proof',required:true,maxPhotos:20,collectionRevision:20,photoCount:20,uploadStatus:'verified',photos:Array.from({length:20},(_,j)=>({photoId:id(100+i*30+j),photoItemId:id(300+i*30+j),itemRevision:1,displayOrder:j,uploadStatus:'verified',mediaAvailability:'available'}))}));
const payload=i=>({attemptId:attempts[i].attemptId,assignmentId:assignments[i].assignmentId,assignmentRevision:1,slots:[slots[i]]});
const submission={id:id(60),attemptId:attempts[2].attemptId,assignmentId:assignments[2].assignmentId,version:1,current:true,status:'submitted',candleCount:3,submittedAt:date+'T03:00:00Z'};
const boot=`window.__lazyQA={setup:()=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_qa_fixture_not_a_real_key_1234567890',featureFlags:{optionalCleaningWorkflow:true,photoUploadSnapshot:true}});state.remote=initialRemoteState();state.role='maid';state.liveView='my';state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${id(1)}',role:'maid',displayName:'QA 메이드'},session:{accessToken:'qa-fixture',expiresAt:Date.now()+3600000}};for(const key of ['rooms','notifications','complaints','availability','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});syncAuthState(state);window.__lazyDone=false;void loadLiveCleaning().then(()=>{window.__lazyDone=true;});},get:()=>({done:window.__lazyDone,busy:cleaningState().busy,status:cleaningState().status,reads:[...(cleaningState().maidReads||new Map())].map(([id,r])=>({id,summary:r.summaryStatus,detail:r.detailStatus,post:!!r.postPromise})),photoUrls:LIVE_CLEANING_ACTIVE_PHOTO_URLS.size,photoLoading:LIVE_CLEANING_ACTIVE_PHOTO_LOADING.size}),reload:()=>loadLiveCleaning({quiet:true}),viewReload:()=>{window.__viewDone=false;void loadLiveViewData('my',{force:true}).then(()=>{window.__viewDone=true;});},expire:id=>{const r=cleaningState().maidReads.get(id);r.summaryAt=0;r.detailAt=0;},defaults:()=>({sections:state.todaySections,pay:state.maidPayOpenWeek,week:!!state.weekAvailabilityOpen,assignment:!!state.assignmentAvailabilityOpen}),invalidate:()=>{LIVE_RUNTIME.authGeneration++;state.remote=initialRemoteState();clearActiveCleaningPhotoUrls();},render:()=>render(),demo:(role,view)=>{LIVE_RUNTIME.mode='demo';writeAuthSession(authAccounts().find(a=>a.role===role));state=makeScenario(0);state.role=role;state.adminView=view;state.maidView=view;render();}};`;
const browser=await chromium.launch({headless:true});
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const until=async test=>{for(let n=0;n<300&&!test();n++)await pause(10);assert(test(),'fixture signal timeout');};
const json=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(data)});
let jpeg;
async function fixture(html,{delays=false}={}){
  const page=await browser.newPage({viewport:{width:390,height:900},serviceWorkers:'block'});
  const calls=[],errors=[],unexpected=[];
  const gate={detail:null,release:null,post:false,releasePost:null,summary:false,releaseSummary:null,failDetail:null,failPhoto:null,active:0,maxActive:0,slowPhotos:false};
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))errors.push(m.text());});
  await page.route('**/*',async route=>{
    const req=route.request(),url=new URL(req.url()),method=req.method();
    if(url.origin===origin){if(url.pathname==='/index.html')return route.fulfill({contentType:'text/html',body:html.replace('\n      void bootApplication();',boot)});return route.continue();}
    if(!req.url().startsWith(api+'/')){unexpected.push(url.origin);return route.abort();}
    const path=url.pathname.replace('/functions/v1/api','');calls.push({path,method,assignment:url.searchParams.get('assignmentId'),at:Date.now()});
    if(delays)await pause(path==='/v1/assignments'?100:path.includes('/attempts/current')?200:path.includes('/supplemental-room-issues')||path==='/v1/rooms/candles'?200:100);
    if(path==='/v1/assignments')return json(route,{assignments:url.searchParams.get('serviceDate')===date?assignments:[]});
    if(path==='/v1/assignment-change-requests')return json(route,{requests:[],nextCursor:null});
    if(path==='/v1/notifications')return json(route,{notifications:[],nextCursor:null});
    if(path==='/v1/complaints')return json(route,{complaints:[],nextCursor:null});
    if(path==='/v1/attempts/current'){
      if(gate.summary===true||gate.summary===url.searchParams.get('assignmentId')){gate.summary=false;await new Promise(resolve=>{gate.releaseSummary=resolve;});}
      return json(route,{attempt:attempts[assignments.findIndex(a=>a.assignmentId===url.searchParams.get('assignmentId'))]});
    }
    if(path.startsWith('/v1/photos/')){
      gate.active++;gate.maxActive=Math.max(gate.maxActive,gate.active);await pause(gate.slowPhotos?200:30);gate.active--;
      if(gate.failPhoto&&path.includes(gate.failPhoto)){gate.failPhoto=null;return json(route,{error:{code:'PHOTO_CONTENT_UNAVAILABLE'}},503);}
      return route.fulfill({contentType:'image/jpeg',body:jpeg});
    }
    if(path.endsWith('/supplemental-room-issues')){if(gate.post){gate.post=false;await new Promise(resolve=>{gate.releasePost=resolve;});}return json(route,{source:{sourceSubmissionId:submission.id,sourceStatus:'submitted'},reports:[]});}
    if(path==='/v1/rooms/candles')return json(route,{items:[{roomId:assignments[2].roomId,count:3,roomStateVersion:1}]});
    const i=attempts.findIndex(a=>path.startsWith('/v1/attempts/'+a.attemptId+'/'));
    if(i>=0){
      if(path.endsWith('/photo-slots')){
        if(gate.failDetail===i){gate.failDetail=null;return json(route,{error:{code:'UPSTREAM_UNAVAILABLE'}},503);}
        if(gate.detail===i){gate.detail=null;await new Promise(resolve=>{gate.release=resolve;});}
        return json(route,payload(i));
      }
      if(path.endsWith('/submissions'))return json(route,{submissions:i===2?[submission]:[]});
      if(path.endsWith('/start')){assert.equal(method,'POST');attempts[i].status='in_progress';attempts[i].executionVersion++;attempts[i].startedAt=date+'T04:00:00Z';return json(route,{attempt:attempts[i]});}
    }
    unexpected.push(method+' '+path);return json(route,{error:{code:'QA_UNEXPECTED'}},400);
  });
  await page.goto(origin+'/index.html');
  jpeg||=Buffer.from(await page.evaluate(()=>{const c=document.createElement('canvas');c.width=300;c.height=200;const x=c.getContext('2d');x.fillStyle='#237957';x.fillRect(0,0,300,200);x.fillStyle='#fff';x.fillText('SYNTHETIC QA PHOTO',40,100);return c.toDataURL('image/jpeg').split(',')[1];}),'base64');
  return {page,calls,errors,unexpected,gate};
}
const toggle=(page,i)=>page.locator(`[data-action="cleaning-maid-room-toggle"][data-id="${assignments[i].assignmentId}"]`);
const card=(page,i)=>page.locator(`[data-maid-room-task="${assignments[i].assignmentId}"]`);
const waitDetail=(page,i)=>page.waitForFunction(id=>__lazyQA.get().reads.find(r=>r.id===id)?.detail==='ready',assignments[i].assignmentId);
const detailCalls=calls=>calls.filter(c=>/photo-slots$|\/submissions$|supplemental-room-issues$|\/rooms\/candles$|\/photos\//.test(c.path));
try{
  if(process.env.RMS_QA_BASELINE){
    const baseline=execFileSync('git',['show',`${process.env.RMS_QA_BASELINE}:WIREFRAME/index.html`],{encoding:'utf8',maxBuffer:4e6});
    for(const [label,html]of [['before',baseline],['after',source]]){
      const f=await fixture(html,{delays:true}),start=Date.now();await f.page.evaluate(()=>__lazyQA.setup());await card(f.page,0).waitFor();const firstCardMs=Date.now()-start;
      await f.page.waitForFunction(()=>__lazyQA.get().done);console.log(JSON.stringify({benchmark:label,firstCardMs,detailRequests:detailCalls(f.calls).length,totalRequests:f.calls.length}));
      assert.deepEqual(f.errors,[]);assert.deepEqual(f.unexpected,[]);await f.page.close();
    }
  }
  const f=await fixture(source),{page,calls,gate,errors,unexpected}=f;
  gate.summary=true;await page.evaluate(()=>__lazyQA.setup());await card(page,0).waitFor();await until(()=>!!gate.releaseSummary);
  assert.equal(await page.locator('[data-maid-room-task]').count(),3);assert.equal(await page.locator('[data-maid-room-task] [aria-expanded="true"]').count(),0);assert.equal(detailCalls(calls).length,0);
  gate.releaseSummary();gate.releaseSummary=null;await page.waitForFunction(()=>__lazyQA.get().done);
  assert.equal(detailCalls(calls).length,0,'collapsed rooms must not read detail, post operations or photos');
  assert.deepEqual(await page.evaluate(()=>__lazyQA.defaults()),{sections:{schedule:false,assignment:false,drafts:false,inspection:false,pay:false},pay:null,week:false,assignment:false});
  console.log('[ok] list renders before slow status; collapsed rooms issue zero detail/photo requests');
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo(0,0));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    assert(await page.locator('[data-action="cleaning-maid-room-toggle"]').evaluateAll(buttons=>buttons.every(b=>b.getBoundingClientRect().height>=44)));
    assert.equal(await page.locator('button:visible').evaluateAll(buttons=>buttons.filter(b=>!(b.textContent.trim()||b.getAttribute('aria-label'))).length),0);
    await page.screenshot({path:`WIREFRAME/QA/screenshots/lazy-cleaning-collapsed-${width}.png`});
  }
  await page.setViewportSize({width:390,height:900});gate.detail=0;
  await toggle(page,0).press('Enter');await until(()=>!!gate.release);assert.equal(await toggle(page,0).getAttribute('aria-expanded'),'true');
  await toggle(page,0).press('Space');gate.release();gate.release=null;await waitDetail(page,0);
  assert.equal(await toggle(page,0).getAttribute('aria-expanded'),'false');assert.equal(calls.filter(c=>c.path.startsWith('/v1/photos/')).length,0);
  const metadataCount=()=>calls.filter(c=>/photo-slots$|\/submissions$/.test(c.path)).length;
  const beforeReopen=metadataCount();await toggle(page,0).press('Enter');await card(page,0).locator('[data-cleaning-assignment]').waitFor();
  assert.equal(metadataCount(),beforeReopen,'fresh reopen reuses verified detail');
  assert.equal(await card(page,0).locator('[data-live-photo-id]').last().locator('img').count(),0,'offscreen photos wait for viewport');
  await card(page,0).locator('[data-live-photo-id]').first().scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>[...document.querySelectorAll('[data-cleaning-photo-item] img')].some(img=>img.complete&&img.naturalWidth>0));
  const loadedFirst=calls.filter(c=>c.path.startsWith('/v1/photos/')).length;assert(loadedFirst>0&&loadedFirst<20,`near viewport loaded ${loadedFirst}/20`);
  console.log(`[ok] expand/collapse while loading, keyboard, fresh cache; viewport reads ${loadedFirst}/20 photos initially`);
  await page.locator('[data-action="live-cleaning-photo"]:visible:not(:disabled)').first().click();await page.waitForFunction(()=>document.body.classList.contains('modal-open'));await page.goBack();await page.waitForFunction(()=>!document.body.classList.contains('modal-open'));
  await page.waitForFunction(()=>document.activeElement?.dataset.action==='live-cleaning-photo');
  gate.slowPhotos=true;
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:900});await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`WIREFRAME/QA/screenshots/lazy-cleaning-expanded-${width}.png`});
  }
  await page.setViewportSize({width:1440,height:8000});await page.evaluate(()=>scrollTo(0,0));
  await page.waitForFunction(()=>__lazyQA.get().photoUrls===20);assert(gate.maxActive<=4,`global photo reads ${gate.maxActive}`);
  await page.setViewportSize({width:390,height:900});await toggle(page,0).click();
  gate.failDetail=1;await toggle(page,1).click();await card(page,1).locator('[data-action="cleaning-maid-detail-retry"]').waitFor();
  assert.equal(await toggle(page,0).getAttribute('aria-expanded'),'false');assert.equal((await page.evaluate(()=>__lazyQA.get())).status,'ready');
  await card(page,1).locator('[data-action="cleaning-maid-detail-retry"]').click();await waitDetail(page,1);
  const beforeCommand=calls.length;await card(page,1).locator('[data-action="cleaning-start"]').click();await page.waitForFunction(()=>!__lazyQA.get().busy);
  const commandReads=calls.slice(beforeCommand).filter(c=>c.method==='GET'&&!c.path.startsWith('/v1/photos/'));
  assert.equal(commandReads.length,3);assert(commandReads.every(c=>c.assignment===assignments[1].assignmentId||c.path.includes(attempts[1].attemptId)));
  console.log('[ok] room-scoped error/retry and mutation refresh; no assignment or other-room reload');
  gate.detail=2;await toggle(page,2).click();await until(()=>!!gate.release);await toggle(page,2).click();gate.release();gate.release=null;await waitDetail(page,2);
  assert.equal(calls.filter(c=>c.path.endsWith('/supplemental-room-issues')).length,0);
  gate.post=true;await toggle(page,2).click();await until(()=>!!gate.releasePost);
  await card(page,2).locator('[data-live-photo-id]').first().scrollIntoViewIfNeeded();
  await page.waitForFunction(id=>document.querySelector(`[data-live-photo-id="${id}"] img`)?.naturalWidth>0,slots[2].photos[0].photoId);
  assert(await card(page,2).locator('[data-action="live-post-new"]').isDisabled());
  gate.releasePost();gate.releasePost=null;await page.waitForFunction(()=>!document.querySelector('[data-action="live-post-new"]')?.disabled);
  assert((await card(page,2).locator('.candle-stepper-value').innerText()).includes('3개'));
  console.log('[ok] cached detail reopen loads candles/issues; slow post operations do not block photos');
  gate.failPhoto=slots[2].photos[19].photoId;await page.setViewportSize({width:1440,height:8000});await page.evaluate(()=>scrollTo(0,0));
  await page.waitForFunction(()=>__lazyQA.get().photoUrls===59);assert.equal(gate.maxActive,4,'all open rooms share four content reads');
  await card(page,2).locator('[data-action="cleaning-photo-preview-retry"]').click();await page.waitForFunction(()=>__lazyQA.get().photoUrls===60);
  await page.setViewportSize({width:390,height:900});console.log('[ok] two open rooms share four reads; failed thumbnail retries independently');
  gate.summary=assignments[1].assignmentId;await page.evaluate(()=>__lazyQA.viewReload());await until(()=>!!gate.releaseSummary);
  await page.waitForFunction(id=>__lazyQA.get().reads.find(r=>r.id===id)?.summary==='ready',assignments[0].assignmentId);await toggle(page,0).click();await waitDetail(page,0);
  const candleInput=card(page,0).locator('[id^="cleaning-candles-"]');await candleInput.fill('7');await candleInput.evaluate(el=>{window.__focusedCandle=el;});
  gate.releaseSummary();gate.releaseSummary=null;await page.waitForFunction(()=>window.__viewDone);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  assert(await candleInput.evaluate(el=>el===window.__focusedCandle&&document.activeElement===el&&el.value==='7'),'late screen load must preserve input node and focus');await toggle(page,0).click();
  console.log('[ok] late whole-view completion preserves active room input and focus');
  slots[0].photos[0].mediaAvailability='expired';await page.evaluate(id=>__lazyQA.expire(id),assignments[0].assignmentId);await toggle(page,0).click();await waitDetail(page,0);
  await card(page,0).getByText('보관 기간 만료',{exact:true}).waitFor();assert.equal(await card(page,0).locator(`[data-live-photo-id="${slots[0].photos[0].photoId}"] img`).count(),0);
  assert.equal((await page.evaluate(()=>__lazyQA.get())).photoUrls,59);await toggle(page,0).click();console.log('[ok] expired metadata revokes cached content and removes enlargement');
  await page.evaluate(()=>__lazyQA.expire(''+__lazyQA.get().reads[0].id));gate.detail=0;await toggle(page,0).click();await until(()=>!!gate.release);
  const nextDate=new Date(Date.parse(date+'T00:00:00Z')+86400000).toISOString().slice(0,10);
  await page.locator('#cleaning-service-date').fill(nextDate);await page.locator('#cleaning-service-date').dispatchEvent('change');
  await page.waitForFunction(()=>document.querySelectorAll('[data-maid-room-task]').length===0);gate.release();gate.release=null;await pause(100);
  assert.equal(await page.locator('[data-maid-room-task]').count(),0);assert.equal((await page.evaluate(()=>__lazyQA.get())).photoUrls,0);
  console.log('[ok] date change ignores late detail and clears private photo URLs');
  await page.evaluate(()=>__lazyQA.setup());await page.waitForFunction(()=>__lazyQA.get().done);gate.detail=0;await toggle(page,0).click();await until(()=>!!gate.release);
  await page.evaluate(()=>__lazyQA.invalidate());gate.release();gate.release=null;await pause(100);
  assert.equal((await page.evaluate(()=>__lazyQA.get())).photoUrls,0);assert.deepEqual((await page.evaluate(()=>__lazyQA.get())).reads,[]);
  assert.equal(await page.evaluate(()=>Object.values(localStorage).some(v=>v.includes('blob:'))||Object.values(sessionStorage).some(v=>v.includes('blob:'))),false);
  await page.evaluate(()=>__lazyQA.demo('admin','today'));assert.equal(await page.locator('.accordion-toggle[aria-expanded="true"]').count(),0);
  await page.locator('[data-action="toggle-section"][data-key="assignment"]').click();assert.equal(await page.locator('[data-action="go-cleaning-assignment"]:visible').count(),1);
  await page.evaluate(()=>__lazyQA.demo('admin','cleaning'));const availability=page.locator('.assignment-availability-disclosure');assert.equal(await availability.getAttribute('open'),null);await availability.locator('summary').click();await page.waitForFunction(()=>__lazyQA.defaults().assignment);await page.evaluate(()=>__lazyQA.render());assert.equal(await availability.getAttribute('open'),'');
  await page.evaluate(()=>__lazyQA.demo('maid','schedule'));const week=page.locator('.weekly-availability-disclosure');assert.equal(await week.getAttribute('open'),null);await week.locator('summary').click();await page.waitForFunction(()=>__lazyQA.defaults().week);await page.evaluate(()=>__lazyQA.render());assert.equal(await week.getAttribute('open'),'');
  await page.evaluate(()=>__lazyQA.demo('maid','pay'));assert.equal(await page.locator('.maid-pay-disclosure[aria-expanded="true"]').count(),0);await page.locator('.maid-pay-disclosure').first().click();assert.equal(await page.locator('.maid-pay-disclosure[aria-expanded="true"]').count(),1);
  console.log('[ok] existing home, availability and pay disclosures start closed and retain explicit expansion');
  assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);
  console.log('[ok] auth reset rejects late reads; no private persistence or console/page errors');
  console.log(`Environment: Chromium ${await browser.version()}, Playwright (Browser plugin unavailable); synthetic fixtures only.`);
}finally{await browser.close();}
