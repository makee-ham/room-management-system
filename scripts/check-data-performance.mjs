#!/usr/bin/env node
// Synthetic, intercepted reads only. No operational accounts or mutations are used.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const source=await readFile('WIREFRAME/index.html','utf8'),baseline=execFileSync('git',['show','e2b95d8:WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:8*1024*1024});
const id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`,week='2026-10-05',nextWeek='2026-10-12',sleep=ms=>new Promise(r=>setTimeout(r,ms));
const browser=await chromium.launch({headless:true}),bench=[],passed=[];
async function fixture({old=false,count=20,mode='',role='admin',markerDelay=80,pageDelay=60}={}){
  const accounts=Array.from({length:count},(_,i)=>({id:id(i+1),displayName:`QA 메이드 ${i+1}`,role:'maid',status:'active'}));
  accounts.push({id:id(999),displayName:'QA 퇴사 계정',role:'maid',status:'departed'});
  const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage(),requests=[],errors=[],warnings=[];
  let active=0,maxActive=0,failedMarker=false;
  const html=(old?baseline:source).replace('\n      void bootApplication();',`window.__dataQA={paint:()=>render(),setup:(view='maids')=>{localStorage.clear();sessionStorage.clear();LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${id(1)}',displayName:'QA 계정',role:'${role}',mustChangePassword:false},session:{accessToken:'qa-token',refreshToken:'qa-refresh',expiresAt:Date.now()+3600000}};state.remote.accounts={...state.remote.accounts,status:'ready',items:${JSON.stringify(accounts)},lastSuccessAt:new Date().toISOString()};state.role='${role}';state.liveView=view;state.adminMaidTab='pay';state.detail=null;state.remote.payroll.weekStart='${week}';syncAuthState(state);render();},start:(selected='${week}')=>{window.__done=false;window.__start=performance.now();void loadLivePayroll({weekStart:selected,quiet:true}).then(()=>{window.__done=true;window.__all=performance.now()-window.__start;});},loadView:view=>loadLiveViewData(view,{force:true}),availability:()=>loadLiveAvailability({quiet:true}),invalidate:()=>{LIVE_RUNTIME.authGeneration++;state.remote=initialRemoteState();},get:()=>({status:state.remote.payroll.status,week:state.remote.payroll.weekStart,count:state.remote.payroll.items.length,complete:state.remote.payroll.listComplete,detail:state.remote.payroll.detail?{loading:state.remote.payroll.detail.loading,error:state.remote.payroll.detail.error?.code}:null,availability:{status:state.remote.availability.status,items:state.remote.availability.items.map(item=>item.maidProfileId)},done:window.__done,all:window.__all}),detail:id=>openLivePayrollDetail(id)};`);
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:'))warnings.push(m.text());});
  await page.clock.setFixedTime(new Date('2026-10-09T10:00:00+09:00'));
  const instrumented=html.replace('window.__dataQA={',`window.__dataQA={noRefresh:()=>{state.remote.auth.session.refreshToken=null;},planning:async()=>{const planning=await loadLiveAssignmentAvailability('${nextWeek}');cleaningState().planningAvailability=planning;document.getElementById('main-content').innerHTML=renderLiveMaidAvailability(state.remote.accounts.items.filter(a=>a.status==='active'),planning,true)+renderLiveRandomAssignmentCard([],[]);return {status:planning.status,count:planning.items.length,candidates:planning.candidates.length};},`);
  await page.route('**/index.html*',r=>r.fulfill({contentType:'text/html',body:instrumented}));
  await page.route('**/favicon.ico',r=>r.fulfill({status:204,body:''}));
  const reply=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',headers:{'x-request-id':'qa-data'},body:JSON.stringify(data)});
  const cycle=(n,selected)=>({maidProfileId:id(n),weekStart:selected,status:'OPEN',totalAmount:16000,accrualAmount:16000,payableAmount:16000,adjustmentAmount:0,carryInAmount:0,lateEarningAmount:0,itemCount:1,expectedAmount:16000,pendingAmount:0});
  await page.route(`${api}/**`,async route=>{
    const url=new URL(route.request().url()),path=url.pathname.replace('/functions/v1/api',''),q=url.searchParams;requests.push({path,query:Object.fromEntries(q),at:Date.now()});
    assert.equal(route.request().method(),'GET','Unexpected mutation');
    if(path==='/v1/payroll'){
      await sleep(mode==='race'&&q.get('weekStart')===week?350:q.has('cursor')?pageDelay:30);
      if(mode==='page-error'&&q.has('cursor'))return reply(route,{error:{code:'INTERNAL_ERROR'}},503);
      const offset=q.has('cursor')?10:0,size=Math.min(10,count-offset),payroll=Array.from({length:size},(_,i)=>cycle(i+1+offset,q.get('weekStart')));
      if(mode==='foreign')payroll[0].maidProfileId=id(77);
      if(mode==='duplicate'&&offset)payroll[0].maidProfileId=id(1);
      return reply(route,{payroll,nextCursor:offset+size<count||mode==='cursor-loop'?'next':null});
    }
    if(path==='/v1/payroll/remittance-marker'){
      active++;maxActive=Math.max(maxActive,active);await sleep(markerDelay);active--;
      if(mode==='marker-error'&&q.get('maidProfileId')===id(1)&&!failedMarker){failedMarker=true;return reply(route,{error:{code:'INTERNAL_ERROR'}},503);}
      return reply(route,{maidProfileId:q.get('maidProfileId'),weekStart:q.get('weekStart'),version:1,marked:false,basisFingerprint:'a'.repeat(64),canSet:false,canClear:false,canReconfirm:false,needsReconfirmation:false,setBlockedReason:'PAYROLL_WEEK_NOT_CLOSED'});
    }
    if(path==='/v1/payroll/remittance-markers'){
      const ids=q.get('maidProfileIds').split(',');assert.equal(q.getAll('maidProfileIds').length,1);assert(ids.length>=1&&ids.length<=10);assert.equal(new Set(ids).size,ids.length);
      if(role==='maid')assert.deepEqual(ids,[id(1)]);
      active++;maxActive=Math.max(maxActive,active);await sleep(markerDelay*(.75+.25*Math.ceil(ids.length/3)));active--;
      if(mode==='legacy')return reply(route,{error:{code:'ROUTE_NOT_FOUND'}},404);
      if(mode==='business-404')return reply(route,{error:{code:'PROFILE_NOT_FOUND'}},404);
      if(['batch-401','batch-403','batch-500'].includes(mode))return reply(route,{error:{code:'QA_BATCH_FAILURE'}},Number(mode.slice(-3)));
      if(mode==='marker-error'&&ids.includes(id(1))&&!failedMarker){failedMarker=true;return reply(route,{error:{code:'INTERNAL_ERROR'}},500);}
      const markers=ids.map(maidProfileId=>({maidProfileId,weekStart:q.get('weekStart'),version:1,marked:false,basisFingerprint:'a'.repeat(64),canSet:false,canClear:false,canReconfirm:false,needsReconfirmation:false,setBlockedReason:'PAYROLL_WEEK_NOT_CLOSED'}));
      if(mode==='batch-order')markers.reverse();
      if(mode==='batch-short')markers.pop();
      if(mode==='batch-invalid')markers.at(-1).version=-1;
      if(mode==='batch-foreign')markers.at(-1).maidProfileId=id(777);
      return reply(route,{weekStart:mode==='batch-week'?'2026-09-28':q.get('weekStart'),markers});
    }
    if(path==='/v1/payroll/entries'){await sleep(90);return reply(route,{entries:[],nextCursor:null});}
    if(path==='/v1/payroll/work-details'){await sleep(130);return reply(route,{maidProfileId:q.get('maidProfileId'),weekStart:q.get('weekStart'),kind:q.get('kind'),entries:[],summary:{accrualAmount:mode==='summary-mismatch'&&q.get('kind')==='workflow'?32000:16000},nextCursor:null});}
    if(path==='/v1/availability'){
      if(mode==='availability-500')return reply(route,{error:{code:'AVAILABILITY_COMMAND_FAILED'}},500);
      await sleep(50);const chosen=q.get('maidProfileId'),ids=chosen?[chosen]:role==='maid'?[id(1)]:mode==='cap'?Array.from({length:1000},(_,i)=>id(i+1)):accounts.map(a=>a.id);
      return reply(route,mode==='invalid-availability'?{}:{availability:ids.map(maidProfileId=>({maidProfileId,weekStart:nextWeek,version:1,current:true,status:'submitted',days:[{workDate:nextWeek,available:true}]}))});
    }
    if(path==='/v1/availability/change-requests'){await sleep(50);return reply(route,mode==='changes-500'?{error:{code:'AVAILABILITY_COMMAND_FAILED'}}:{changeRequests:[]},mode==='changes-500'?500:200);}
    if(path==='/v1/availability/candidates')return reply(route,mode==='candidates-500'?{error:{code:'AVAILABILITY_COMMAND_FAILED'}}:{candidates:accounts.filter(a=>a.status==='active').map(a=>({maidProfileId:a.id,workDate:q.get('workDate'),displayName:a.displayName}))},mode==='candidates-500'?500:200);
    if(path==='/v1/accounts')return reply(route,{accounts});
    if(path==='/v1/notifications'){await sleep(250);return reply(route,{notifications:[],nextCursor:null});}
    if(path==='/v1/work-history')return reply(route,{items:[],nextCursor:null,summary:null,weekStart:week});
    if(path==='/v1/rooms')return reply(route,{rooms:[],nextCursor:null});
    if(path==='/v1/assignments')return reply(route,{assignments:[]});
    if(path==='/v1/inspections')return reply(route,{submissions:[],nextCursor:null});
    if(path==='/v1/assignment-change-requests')return reply(route,{requests:[]});
    return reply(route,{error:{code:'QA_MISSING_ROUTE'}},404);
  });
  await page.goto(`${origin}/index.html`);await page.evaluate(()=>window.__dataQA.setup());
  return {page,requests,get maxActive(){return maxActive;},async close(){assert.deepEqual(errors,[]);assert.deepEqual(warnings,[]);await context.close();}};
}
try{
  if(!process.env.RMS_QA_SKIP_BENCH)for(const old of [true,false])for(const count of [1,10,20])for(let sample=0;sample<3;sample++){
    const f=await fixture({old,count});await f.page.evaluate(()=>{window.__first=null;const observer=new MutationObserver(()=>{if(window.__first===null&&document.querySelector('[data-action="live-payroll-detail"]'))window.__first=performance.now()-window.__start;});observer.observe(document.getElementById('app'),{childList:true,subtree:true});window.__dataQA.start();});
    // Previous quiet loaders rendered only when the enclosing view finished.
    if(old)await f.page.waitForFunction(()=>window.__done).then(()=>f.page.evaluate(()=>window.__dataQA.paint()));
    await f.page.waitForFunction(()=>window.__done&&window.__first!==null);
    await f.page.waitForFunction(()=>!document.getElementById('main-content').textContent.includes('송금 표시 조회 중'));
    bench.push({version:old?'before':'after',count,first:Math.round(await f.page.evaluate(()=>window.__first)),all:Math.round(await f.page.evaluate(()=>performance.now()-window.__start)),requests:f.requests.length,maxMarkers:f.maxActive});await f.close();
  }
  for(const count of [1,10,20]){
    const f=await fixture({count});await f.page.evaluate(()=>window.__dataQA.availability());assert.equal(f.requests.filter(r=>r.path==='/v1/availability').length,1);assert.equal((await f.page.evaluate(()=>window.__dataQA.get())).availability.items.length,count);assert(!f.requests.find(r=>r.query.maidProfileId));await f.close();
  }
  for(const mode of ['cap','invalid-availability','availability-500','changes-500']){const f=await fixture({count:3,mode});await f.page.evaluate(()=>window.__dataQA.availability());const a=(await f.page.evaluate(()=>window.__dataQA.get())).availability;assert.equal(a.status,mode==='cap'?'ready':'error');if(mode==='cap'){assert.equal(a.items.length,3);assert.equal(f.requests.filter(r=>r.path==='/v1/availability').length,1);}else{await f.page.evaluate(()=>{window.__dataQA.paint();});}await f.close();}
  passed.push('가능일 1/10/20명 일괄 1회 · 퇴사 제외 · 서버 완전성 오류/변경 요청 오류는 미제출로 변환 금지');
  for(const mode of ['', 'availability-500', 'candidates-500']){
    const f=await fixture({count:10,mode}),p=f.page,result=await p.evaluate(()=>window.__dataQA.planning());
    assert.equal(result.status,mode?'error':'ready');assert.equal(f.requests.filter(r=>r.path==='/v1/availability').length,1);assert(!f.requests.some(r=>r.path==='/v1/availability'&&r.query.maidProfileId));
    assert.equal(await p.locator('.availability-matrix').count(),mode?0:1);if(mode){assert.equal(result.candidates,0);assert.equal(await p.locator('[data-action="cleaning-refresh"]').count(),1);assert.equal(await p.locator('[data-action="cleaning-preview"]:enabled').count(),0);}else assert.equal(result.count,10);await f.close();
  }
  passed.push('청소 배정 근무표도 전체 1회 · current/candidates 500에 표 대신 재조회 · 랜덤 배정 잠금');
  for(const count of [0,1,10,20]){
    const f=await fixture({count});await f.page.evaluate(()=>window.__dataQA.start());await f.page.waitForFunction(()=>window.__done);assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-markers').length,Math.ceil(count/10));assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-marker').length,0);assert(f.maxActive<=1);await f.close();
  }
  for(const mode of ['legacy','business-404','batch-401','batch-403','batch-500','batch-order','batch-short','batch-week','batch-invalid','batch-foreign']){
    const f=await fixture({count:3,mode}),p=f.page;
    if(mode==='batch-401')await p.evaluate(()=>{window.__dataQA.noRefresh();});
    await p.evaluate(()=>window.__dataQA.start());await p.waitForFunction(()=>window.__done);await sleep(50);
    assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-marker').length,mode==='legacy'?3:0);
    assert.equal(await p.getByRole('button',{name:'송금 표시 재조회'}).count(),mode==='legacy'?0:3);assert(f.maxActive<=3);
    if(mode==='batch-500'){
      for(const width of [360,390,768,1440]){await p.setViewportSize({width,height:900});assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`batch error overflow ${width}`);const retry=p.getByRole('button',{name:'송금 표시 재조회'}).first(),box=await retry.boundingBox();assert(box.width>=44&&box.height>=44);assert(await p.locator('.pay-person .job-actions > .btn').evaluateAll(buttons=>buttons.every(button=>button.scrollWidth<=button.clientWidth)));await p.locator('.pay-person').first().evaluate(el=>window.scrollTo(0,el.getBoundingClientRect().top+scrollY-70));await p.locator('.pay-person').first().screenshot({path:`WIREFRAME/QA/screenshots/v093-error-${width}.png`});}
      await p.getByRole('button',{name:'송금 표시 재조회'}).first().focus();await p.keyboard.press('Enter');await p.waitForFunction(()=>document.querySelectorAll('[data-action="live-payroll-marker-retry"]').length===2);
    }
    await f.close();
  }
  {
    const f=await fixture({count:1,role:'maid'});await f.page.evaluate(()=>window.__dataQA.start());await f.page.waitForFunction(()=>window.__done);assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-markers').length,1);await f.close();
  }
  passed.push('페이지별 CSV 묶음 0/1/10/20명 · 순서/개수/주차/전체 검증 · route 404만 단건 3병렬 fallback · 401/403/500/업무 404 유지 · 메이드 본인 1명');
  {
    const f=await fixture({pageDelay:600,markerDelay:100}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.locator('[data-action="live-payroll-detail"]').first().waitFor();assert.equal(await p.locator('[data-action="live-payroll-detail"]').count(),10);assert.equal(await p.locator('.pay-hero > strong').innerText(),'조회 중');
    await p.getByRole('button',{name:'이전 주',exact:true}).focus();await p.waitForFunction(()=>window.__dataQA.get().done);await sleep(60);assert.equal(await p.locator('.pay-hero > strong').innerText(),'320,000원');assert.equal(await p.evaluate(()=>document.activeElement?.getAttribute('aria-label')),'이전 주');assert(f.maxActive<=3);await f.close();
  }
  passed.push('첫 페이지 즉시 표시 · 불완전 합계 숨김 · 묶음은 최대 1개 진행 · 갱신 중 키보드 포커스 유지');
  for(const mode of ['page-error','duplicate','cursor-loop','marker-error']){
    const f=await fixture({mode}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.waitForFunction(()=>window.__dataQA.get().done);await sleep(50);
    if(mode==='marker-error'){assert.equal(await p.getByRole('button',{name:'송금 표시 재조회'}).count(),10);const before=f.requests.length;await p.getByRole('button',{name:'송금 표시 재조회'}).first().click();await p.waitForFunction(()=>document.querySelectorAll('[data-action="live-payroll-marker-retry"]').length===9);await sleep(120);assert.equal(f.requests.length,before+1);}
    else{assert.equal((await p.evaluate(()=>window.__dataQA.get())).status,'partial');assert.equal(await p.locator('.pay-hero > strong').innerText(),'집계 확인 필요');assert(await p.locator('[data-action="live-payroll-detail"]').count()>0);if(mode==='page-error'){await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await p.screenshot({path:'WIREFRAME/QA/screenshots/data-performance-partial-390.png',fullPage:false});}}
    await f.close();
  }
  passed.push('후속 페이지 실패·중복·반복 cursor에 합계 확정 금지 · 송금 조회 실패는 해당 카드 GET만 재시도');
  for(const mode of ['', 'summary-mismatch']){
    const f=await fixture({count:1,mode}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.waitForFunction(()=>window.__dataQA.get().done);await sleep(40);await p.locator('[data-action="live-payroll-detail"]').click();await p.getByText('주급 산출 내역을 불러오는 중',{exact:true}).waitFor();await p.waitForFunction(()=>window.__dataQA.get().detail&&!window.__dataQA.get().detail.loading);const d=(await p.evaluate(()=>window.__dataQA.get())).detail;assert.equal(d.error,mode?'STALE_VERSION':undefined);const detailReads=f.requests.filter(r=>r.path==='/v1/payroll/entries'||r.path==='/v1/payroll/work-details');assert.equal(detailReads.length,5);assert(Math.max(...detailReads.map(r=>r.at))-Math.min(...detailReads.map(r=>r.at))<100);await f.close();
  }
  passed.push('산출 상세 즉시 진입 · 독립 조회 병행 · 금액 summary 불일치 차단');
  {
    const f=await fixture({count:20,pageDelay:500,markerDelay:150}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.locator('[data-action="live-payroll-detail"]').first().click();await p.waitForFunction(()=>window.__dataQA.get().detail&&!window.__dataQA.get().detail.loading);await p.waitForFunction(()=>window.__done);await sleep(50);assert((await p.evaluate(()=>window.__dataQA.get())).detail);await f.close();
  }
  passed.push('목록 조회 중 산출 상세를 열어도 늦은 목록 응답이 상세를 닫지 않음');
  {
    const f=await fixture({mode:'race'}),p=f.page;await p.evaluate(()=>{window.__dataQA.start();window.__dataQA.start('2026-09-28');});await p.waitForFunction(()=>window.__dataQA.get().status==='ready');await sleep(400);assert.equal((await p.evaluate(()=>window.__dataQA.get())).week,'2026-09-28');assert(!f.requests.some(r=>r.path.includes('remittance')&&r.query.weekStart===week));await f.close();
  }
  {
    const f=await fixture({markerDelay:300,pageDelay:300}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.locator('[data-action="live-payroll-detail"]').first().waitFor();const before=f.requests.length;await p.evaluate(()=>window.__dataQA.invalidate());await sleep(450);assert.equal(f.requests.length,before);assert.equal((await p.evaluate(()=>window.__dataQA.get())).count,0);await f.close();
  }
  {
    const f=await fixture({count:1,mode:'foreign',role:'maid'});await f.page.evaluate(()=>window.__dataQA.start());await f.page.waitForFunction(()=>window.__done);assert.equal((await f.page.evaluate(()=>window.__dataQA.get())).status,'error');assert(!f.requests.some(r=>r.path.includes('remittance')));await f.close();
  }
  passed.push('주차 응답 역전·로그아웃 늦은 결과 폐기/추가 요청 중단 · 메이드 타인 주급 차단');
  {
    const f=await fixture({count:20,markerDelay:300}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.locator('[data-action="live-payroll-detail"]').first().waitFor();await p.evaluate(()=>window.__dataQA.start('2026-09-28'));await p.waitForFunction(()=>window.__dataQA.get().status==='ready');await sleep(100);assert.equal((await p.evaluate(()=>window.__dataQA.get())).week,'2026-09-28');assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-markers'&&r.query.weekStart===week).length,1);assert.equal(await p.getByRole('button',{name:'송금 표시 재조회'}).count(),0);await f.close();
  }
  {
    const f=await fixture({count:20,mode:'legacy'});await f.page.evaluate(()=>window.__dataQA.start());await f.page.waitForFunction(()=>window.__done);assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-markers').length,1);assert.equal(f.requests.filter(r=>r.path==='/v1/payroll/remittance-marker').length,20);assert.equal(f.maxActive,3);await f.close();
  }
  passed.push('진행 중 묶음 뒤 주차 변경 시 후속 대기 묶음 중단 · 20명 legacy 404는 1회만 확인');
  {
    const f=await fixture({count:20,markerDelay:300}),p=f.page;await p.evaluate(()=>{window.__dataQA.setup('today');void window.__dataQA.loadView('today');});await p.locator('[data-admin-home-section="room-summary"]').waitFor();assert.notEqual((await p.evaluate(()=>window.__dataQA.get())).status,'ready');await p.waitForFunction(()=>window.__dataQA.get().status==='ready');await f.close();
  }
  passed.push('홈 객실 요약은 느린 주급·알림 완료 전 표시');
  {
    const f=await fixture({count:3}),p=f.page;await p.evaluate(()=>window.__dataQA.start());await p.waitForFunction(()=>window.__done);await sleep(50);await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
    assert((await p.title()).includes('메이드'));assert((await p.locator('#main-content').innerText()).length>0);assert.equal(await p.locator('nextjs-portal,vite-error-overlay').count(),0);
    for(const width of [360,390,768,1440]){await p.setViewportSize({width,height:900});assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await p.screenshot({path:`WIREFRAME/QA/screenshots/data-performance-${width}.png`,fullPage:false});}
    await p.locator('[data-action="live-payroll-detail"]').first().focus();await p.keyboard.press('Enter');await p.waitForFunction(()=>window.__dataQA.get().detail&&!window.__dataQA.get().detail.loading);await p.goBack();await p.waitForFunction(()=>!window.__dataQA.get().detail);await f.close();
  }
  passed.push('360/390/768/1440px · 기존 카드/목적지 · Enter/Back · 의미 있는 화면/넘침/console 검사');
  {
    const before=await fixture({old:true,count:3}),after=await fixture({count:3});
    for(const f of [before,after]){await f.page.evaluate(()=>window.__dataQA.start());await f.page.waitForFunction(()=>window.__done);await sleep(100);}
    for(const width of [390,1440]){
      const captures=[];for(const [label,f] of [['before',before],['after',after]]){await f.page.setViewportSize({width,height:900});captures.push(await f.page.screenshot({path:`WIREFRAME/QA/screenshots/v093-${label}-${width}.png`,animations:'disabled'}));}
      assert(captures[0].equals(captures[1]),`Existing payroll UI differs at ${width}px`);
    }
    await before.close();await after.close();
  }
  passed.push('변경 전/후 동일 fixture · 390/1440px 완료 화면 PNG byte 일치');
  for(const version of ['before','after'])for(const count of [1,10,20]){const rows=bench.filter(r=>r.version===version&&r.count===count);if(!rows.length)continue;const q=(key,p)=>rows.map(r=>r[key]).sort((a,b)=>a-b)[Math.ceil(rows.length*p)-1];console.log(JSON.stringify({version,count,samples:rows.length,firstP50:q('first',.5),firstP95:q('first',.95),allP50:q('all',.5),allP95:q('all',.95),requests:rows[0].requests,maxMarkers:rows[0].maxMarkers}));}
  passed.forEach(text=>console.log('[ok] '+text));console.log('Playwright / Chromium '+await browser.version()+'; Browser plugin not available. Synthetic timing is not operational mobile performance.');
}finally{await browser.close();}
