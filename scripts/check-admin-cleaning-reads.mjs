#!/usr/bin/env node
// Intercepted synthetic GETs only: parallel reads, cursor completion and invalidated loads.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const source=await readFile('WIREFRAME/index.html','utf8'),baseline=execFileSync('git',['show','ac4c6f0:WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:4e6});
const date='2026-10-22',tomorrow='2026-10-23',id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const paths=['/v1/assignments','/v1/assignment-change-requests','/v1/inspections'];
const browser=await chromium.launch({headless:true});
async function fixture({old=false,gated=false,mode=''}={}){
  const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage(),calls=[],problems=[],release=new Map(),started=new Map();
  const startPromises=paths.map(path=>new Promise(resolve=>started.set(path,resolve)));
  const gates=new Map(paths.map(path=>[path,new Promise(resolve=>release.set(path,resolve))]));
  const html=(old?baseline:source).replace('\n      void bootApplication();',`window.__readsQA={setup:()=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${id(4)}',displayName:'데모 QA 관리자',role:'admin',mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};state.role='admin';state.liveView='cleaning';state.cleaningTab='progress';for(const key of ['accounts','notifications','rooms'])Object.assign(state.remote[key],{status:'ready',items:[],lastSuccessAt:new Date().toISOString()});render();},records:tab=>{state.cleaningTab=tab;cleaningState().assignments=Array.from({length:3},(_,i)=>({...cleaningState().assignments[0],assignmentId:'qa-assignment-'+i,roomNumber:String(101+i),maidDisplayName:i===1?'데모 이름이 긴 담당 메이드':'데모 메이드',dueAt:i===2?'${date}T07:00:00Z':null}));cleaningState().inspections=Array.from({length:3},(_,i)=>({id:'qa-submission-'+i,reviewContext:{roomNumber:String(101+i)},photoCount:i+1,submittedAt:'${date}T03:00:00Z'}));Object.assign(state.remote.cleaningHistory,{status:'ready',items:Array.from({length:3},(_,i)=>({attemptId:'qa-attempt-'+i,submissionId:i===2?null:'qa-submission-'+i,roomNumber:String(101+i),cleaningKind:'checkout',roomTypeName:'데모 디럭스',performerDisplayName:'데모 메이드',serviceDate:'${date}',fieldCompletedAt:'${date}T03:00:00Z',submittedAt:'${date}T04:00:00Z',decidedAt:'${date}T05:00:00Z',inspectionStatus:i===1?'rejected':'approved',mediaAvailability:i===1?'purged':'available',photoCount:2,expiresAt:'2026-10-29T05:00:00Z',baseFeeSnapshot:20000,earningTotalAmount:i===1?null:20000})),date:'${date}',fromDate:'2026-10-16',toDate:'${date}'});render();},load:(date='${date}')=>{cleaningState().serviceDate=date;window.__readsDone=false;void loadLiveCleaning().then(()=>window.__readsDone=true);},invalidate:()=>{cleaningState().loadRevision++;},logout:()=>{LIVE_RUNTIME.authGeneration++;state.remote=initialRemoteState();state.liveView=null;render();},get:()=>({done:window.__readsDone,status:cleaningState().status,error:cleaningState().error?.code,assignments:cleaningState().assignments.map(a=>a.serviceDate),inspections:cleaningState().inspections.length,changes:cleaningState().changeRequests.length})};`);
  page.on('pageerror',e=>problems.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))problems.push(m.text());});
  await page.clock.setFixedTime(new Date(date+'T15:00:00+09:00'));
  await page.route('**/*',async route=>{
    const req=route.request(),url=new URL(req.url()),path=url.pathname.replace('/functions/v1/api','');
    if(url.origin===origin)return url.pathname==='/index.html'?route.fulfill({contentType:'text/html',body:html.replace('<body>','<body><div style="position:fixed;top:6px;right:12px;z-index:10000;background:white;font-size:10px;padding:4px 6px;border:1px solid #cad6e2;border-radius:6px">합성 데모 · 운영 데이터 아님</div>')}):route.continue();
    assert.equal(url.origin,new URL(api).origin);assert.equal(req.method(),'GET','QA must not send writes');
    calls.push({path,cursor:url.searchParams.get('cursor'),date:url.searchParams.get('serviceDate')});started.get(path)?.();
    if(gated&&paths.includes(path)&&!url.searchParams.has('cursor'))await gates.get(path);
    const reply=(data,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(data)});
    if(path==='/v1/assignments')return reply({assignments:[{assignmentId:id(1),cleaningTargetId:id(2),roomId:id(3),roomNumber:'101',maidDisplayName:'데모 메이드',maidProfileId:id(5),serviceDate:url.searchParams.get('serviceDate'),revision:1,isCurrent:true,notifiedAt:date+'T00:00:00Z',availableFrom:date+'T02:00:00Z',dueAt:null}]});
    if(path==='/v1/assignment-change-requests'||path==='/v1/inspections'){
      if(mode===path||mode==='failed-load'&&path==='/v1/inspections')return reply({error:{code:'UPSTREAM_UNAVAILABLE'},requestId:'qa-read-only'},503);
      const key=path==='/v1/inspections'?'submissions':'requests',nextCursor=['paged','failed-load'].includes(mode)&&!url.searchParams.has('cursor')?'next':mode==='loop'?'same':null;
      return reply({[key]:[],nextCursor});
    }
    if(path==='/v1/checkout-incidents')return reply({items:[],nextCursor:null});
    throw new Error('Unexpected QA route '+path);
  });
  await page.goto(origin+'/index.html');await page.evaluate(()=>__readsQA.setup());
  return {page,calls,release:path=>release.get(path)(),releaseAll:()=>paths.forEach(path=>release.get(path)()),async concurrent(){let timer;try{await Promise.race([Promise.all(startPromises),new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('Independent reads did not start together')),3000);})]);}finally{clearTimeout(timer);}},async done(){await page.waitForFunction(()=>__readsQA.get().done);},async close(){assert.deepEqual(problems,[]);await context.close();}};
}
try{
  const parallel=await fixture({gated:true});await parallel.page.evaluate(()=>__readsQA.load());await parallel.concurrent();assert.equal(await parallel.page.getByRole('button',{name:'배정 관리',exact:true}).count(),0);parallel.releaseAll();await parallel.done();assert.equal(await parallel.page.getByRole('button',{name:'배정 관리',exact:true}).count(),1);await parallel.close();
  console.log('[ok] independent assignments/change requests/inspections start before any response; no incomplete actionable cards');
  for(const mode of ['paged','loop',...paths.slice(1)]){
    const f=await fixture({mode});await f.page.evaluate(()=>__readsQA.load());await f.done();const result=await f.page.evaluate(()=>__readsQA.get());
    assert.equal(result.status,mode==='paged'?'ready':'error');if(mode==='paged')for(const path of paths.slice(1))assert.equal(f.calls.filter(c=>c.path===path).length,2);
    else {assert.equal(await f.page.getByRole('button',{name:'배정 관리',exact:true}).count(),0);assert.equal(await f.page.getByRole('button',{name:'다시 불러오기',exact:true}).count(),1);}await f.close();
  }
  console.log('[ok] complete cursor lists; repeated cursor/503 show errors, never empty success');
  const failed=await fixture({gated:true,mode:'failed-load'});await failed.page.evaluate(()=>__readsQA.load());await failed.concurrent();failed.release('/v1/inspections');await failed.done();assert.equal((await failed.page.evaluate(()=>__readsQA.get())).status,'error');failed.releaseAll();await failed.page.waitForResponse(r=>r.url().includes('/v1/assignment-change-requests'));await failed.page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));assert.equal(failed.calls.filter(c=>c.cursor).length,0);await failed.close();
  console.log('[ok] a failed sibling read stops remaining cursor pages without making actions available');
  for(const action of ['invalidate','logout']){
    const f=await fixture({gated:true,mode:'paged'});await f.page.evaluate(()=>__readsQA.load());await f.concurrent();await f.page.evaluate(action=>__readsQA[action](),action);f.releaseAll();await f.done();assert.equal(f.calls.filter(c=>c.cursor).length,0);assert.equal(await f.page.getByRole('button',{name:'배정 관리',exact:true}).count(),0);await f.close();
  }
  const race=await fixture({gated:true,mode:'paged'});await race.page.evaluate(()=>__readsQA.load());await race.concurrent();await race.page.evaluate(date=>__readsQA.load(date),tomorrow);race.releaseAll();await race.done();await race.page.waitForFunction(date=>__readsQA.get().assignments[0]===date,tomorrow);assert.deepEqual(await race.page.evaluate(()=>__readsQA.get().assignments),[tomorrow]);assert.equal(race.calls.filter(c=>c.cursor).length,2);await race.close();
  console.log('[ok] date/revision/session invalidation discards responses and stops old cursor pages');
  const before=await fixture({old:true}),after=await fixture();
  for(const f of [before,after]){await f.page.evaluate(()=>__readsQA.load());await f.done();}
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  for(const width of [360,390,768,1440]){
    await after.page.setViewportSize({width,height:900});assert.equal(await after.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    assert.deepEqual(await after.page.locator('[data-cleaning-assignment] button').allTextContents(),['배정 이력','배정 관리']);
    await after.page.screenshot({path:`WIREFRAME/QA/screenshots/cleaning-list-progress-${width}.png`});
    if([390,1440].includes(width)){await before.page.setViewportSize({width,height:900});assert.deepEqual(await after.page.locator('[data-cleaning-assignment] button').evaluateAll(nodes=>nodes.map(n=>[n.textContent,n.dataset.action,n.dataset.id])),await before.page.locator('[data-cleaning-assignment] button').evaluateAll(nodes=>nodes.map(n=>[n.textContent,n.dataset.action,n.dataset.id])));const oldHeight=(await before.page.locator('[data-cleaning-assignment]').boundingBox()).height,newHeight=(await after.page.locator('[data-cleaning-assignment]').boundingBox()).height;assert(newHeight<oldHeight*.75,`row density ${width}: ${oldHeight} -> ${newHeight}`);console.log(`[ok] progress row height ${width}: ${oldHeight}px -> ${newHeight}px`);await before.page.screenshot({path:`WIREFRAME/QA/screenshots/cleaning-list-before-${width}.png`});}
  }
  await after.page.getByRole('button',{name:'배정 관리',exact:true}).press('Enter');assert.equal(await after.page.getByRole('heading',{name:'101호 배정 관리',exact:true}).count(),1);await after.page.keyboard.press('Tab');assert(await after.page.evaluate(()=>!!document.activeElement.closest('#modal-root')));await after.page.keyboard.press('Escape');await after.page.waitForFunction(()=>document.activeElement?.dataset.action==='cleaning-assignment-manage');
  await after.page.getByRole('button',{name:'배정 관리',exact:true}).click();await after.page.goBack();await after.page.getByRole('heading',{name:'101호 배정 관리',exact:true}).waitFor({state:'hidden'});
  assert((await after.page.title()).includes('청소 관리'));assert((await after.page.locator('#main-content').innerText()).trim());assert.equal(await after.page.locator('nextjs-portal,vite-error-overlay').count(),0);await before.close();await after.close();
  console.log('[ok] compact rows/unchanged destinations; 360/390/768/1440px, Enter/Tab/Escape/Back/focus, page/console/overflow');
  const lists=await fixture();await lists.page.evaluate(()=>__readsQA.load());await lists.done();
  for(const tab of ['progress','inspection','done']){
    await lists.page.evaluate(tab=>__readsQA.records(tab),tab);
    for(const width of [360,390,768,1440]){
      await lists.page.setViewportSize({width,height:1000});
      assert.equal(await lists.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${tab} overflow ${width}`);
      const selector=tab==='progress'?'[data-cleaning-assignment]':tab==='inspection'?'.cleaning-inspection-row':'[data-live-cleaning-history]';
      assert.equal(await lists.page.locator(selector).count(),3);
      assert(await lists.page.locator(selector).evaluateAll(rows=>rows.every(row=>getComputedStyle(row).boxShadow==='none'&&getComputedStyle(row).borderRadius==='0px')));
      assert(await lists.page.locator(selector+' button').evaluateAll(nodes=>nodes.every(n=>n.getBoundingClientRect().height>=44&&n.getBoundingClientRect().width>=44&&(n.getAttribute('aria-label')||n.textContent.trim()))));
      await lists.page.screenshot({path:`WIREFRAME/QA/screenshots/cleaning-list-${tab}-${width}.png`,fullPage:true});
    }
    if(tab==='done'){assert.equal(await lists.page.getByText('7일 보관 만료 · 원본 삭제',{exact:true}).count(),1);assert.equal(await lists.page.locator('[data-live-cleaning-history] button:disabled').count(),1);}
  }
  await lists.close();console.log('[ok] 3-row progress/inspection/history, long names/unset dates/expired media/disabled detail, all four widths and 44px controls');
  console.log('Playwright Chromium '+await browser.version()+'; Browser plugin not available. All API requests were intercepted synthetic GETs.');
}finally{await browser.close();}
