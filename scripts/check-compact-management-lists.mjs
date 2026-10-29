#!/usr/bin/env node
// Synthetic read-only browser QA. Production business data is never requested.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const source=await readFile('WIREFRAME/index.html','utf8'),baseline=execFileSync('git',['show','a76f0fe:WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:4e6});
const id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`,week='2026-10-19';
const accounts=Array.from({length:3},(_,i)=>({id:id(i+1),profileId:id(i+1),role:'maid',displayName:i===1?'데모 이름이 긴 담당 메이드':'데모 메이드 '+(i+1),status:i===2?'inactive':'active',phoneLastFour:'0000',version:1}));
const cycles=accounts.map((a,i)=>({cycleId:id(i+11),maidProfileId:a.id,weekStart:week,status:'open',version:1,itemCount:0,totalAmount:i===2?0:16000,accrualAmount:i===2?0:16000,payableAmount:i===2?0:16000,expectedAmount:i===2?0:16000,pendingAmount:0,adjustmentAmount:0,carryInAmount:0,carryOutAmount:0,lateEarningAmount:0}));
const marker=(maidProfileId,weekStart)=>({maidProfileId,weekStart,version:1,marked:maidProfileId===id(2),basisFingerprint:'a'.repeat(64),canSet:maidProfileId===id(1),canClear:maidProfileId===id(2),canReconfirm:false,needsReconfirmation:false,setBlockedReason:maidProfileId===id(3)?'NO_PAYROLL_AMOUNT':null});
const hook=`window.__compactQA={setup:(surface,role='admin')=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:role==='maid'?'${id(1)}':'${id(90)}',displayName:'데모 QA 계정',role,mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};state.role=role;state.detail=null;state.liveView=surface==='more'?'more':role==='maid'?'pay':'maids';state.adminMaidTab=surface==='pay'?'pay':'workforce';for(const key of ['accounts','availability','notifications','rooms','complaints','cleaningHistory','payroll'])Object.assign(state.remote[key],{status:'ready',items:[],lastSuccessAt:new Date().toISOString()});state.remote.accounts.items=${JSON.stringify(accounts)};state.remote.availability.weekStart='2026-11-02';state.remote.availability.changeRequests=[];state.remote.availability.items=[{maidProfileId:'${id(1)}',version:2,current:true,status:'submitted',submittedAt:'2026-10-29T01:00:00Z',days:[{workDate:'2026-11-02',available:true}]}];Object.assign(state.remote.payroll,{weekStart:'${week}',listComplete:true,items:${JSON.stringify(cycles)},markers:new Map(${JSON.stringify(accounts.map(a=>[a.id,{value:marker(a.id,week)}]))})});if(role==='maid')state.remote.payroll.items=state.remote.payroll.items.filter(c=>c.maidProfileId==='${id(1)}');syncAuthState(state);render();},guard:()=>openLivePayrollDetail('${id(2)}')};`;
const browser=await chromium.launch({headless:true}),widths=[360,390,768,1440];
await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
async function fixture(old=false,live=true){
  const context=await browser.newContext({viewport:{width:390,height:1000},serviceWorkers:'block'}),page=await context.newPage(),errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:')&&m.text()!=='Service Worker registration blocked by Playwright')errors.push(m.text());});
  await page.clock.setFixedTime(new Date('2026-10-29T10:00:00+09:00'));
  const html=(old?baseline:source).replace(live?'\n      void bootApplication();':'__no_hook__',live?hook:'__no_hook__').replace('<body>','<body><div style="position:fixed;top:5px;right:12px;z-index:10000;background:white;font-size:10px;padding:4px;border:1px solid #cad6e2">합성 데모 · 운영 데이터 아님</div>');
  await page.route('**/*',async route=>{
    const req=route.request(),url=new URL(req.url());
    if(url.origin===origin){if(url.pathname==='/index.html')return route.fulfill({contentType:'text/html',body:html});if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});return route.continue();}
    assert.equal(url.origin,new URL(api).origin);assert.equal(req.method(),'GET','Read-only QA must not mutate business data');
    const path=url.pathname.replace('/functions/v1/api','');requests.push(path);const reply=data=>route.fulfill({json:data});
    if(path==='/v1/payroll/entries')return reply({entries:[],nextCursor:null});
    if(path==='/v1/payroll/work-details'){const cycle=cycles.find(c=>c.maidProfileId===url.searchParams.get('maidProfileId'));return reply({maidProfileId:cycle.maidProfileId,weekStart:cycle.weekStart,kind:url.searchParams.get('kind'),entries:[],summary:{accrualAmount:cycle.accrualAmount},nextCursor:null});}
    if(path==='/v1/cleaning-history')return reply({items:[],nextCursor:null});
    if(path==='/v1/payroll')return reply({payroll:cycles,nextCursor:null});
    if(path==='/v1/payroll/remittance-markers')return reply({weekStart:url.searchParams.get('weekStart'),markers:url.searchParams.get('maidProfileIds').split(',').map(maid=>marker(maid,url.searchParams.get('weekStart')))});
    if(path==='/v1/payroll/remittance-marker')return reply(marker(url.searchParams.get('maidProfileId'),url.searchParams.get('weekStart')));
    throw new Error('Unexpected synthetic route '+path);
  });
  await page.goto(origin+'/index.html?scenario=0&role=admin&view=today&date=2026-08-15');
  return {page,requests,async close(){assert.deepEqual(errors,[]);await context.close();}};
}
const normalize=s=>s.replace(/\s+/g,' ').trim();
const actions=page=>page.locator('#main-content button[data-action]').evaluateAll(nodes=>nodes.map(n=>[n.textContent.trim(),n.dataset.action,n.dataset.id,n.dataset.maid,n.disabled,n.getAttribute('aria-label')]));
try{
  const before=await fixture(true),after=await fixture();
  for(const [surface,role] of [['maids','admin'],['pay','admin'],['more','admin'],['pay','maid'],['more','maid']]){
    for(const f of [before,after])await f.page.evaluate(([surface,role])=>__compactQA.setup(surface,role),[surface,role]);
    const selector=surface==='maids'?'.maid-summary-row':surface==='pay'?'.payroll-summary-row':'.setting-card';
    const oldSelector=surface==='maids'?'[data-live-maid-card]':surface==='pay'?'.payroll-live .pay-person':'.setting-card';
    assert.equal(await after.page.locator(selector).count(),surface==='maids'?3:surface==='pay'?(role==='maid'?1:3):role==='admin'?6:5);
    assert.equal(normalize(await after.page.locator('#main-content').textContent()),normalize(await before.page.locator('#main-content').textContent()),'all information and visible copy preserved');
    assert.deepEqual(await actions(after.page),await actions(before.page),'same action targets, disabled states and accessible names');
    for(const width of widths){
      for(const f of [before,after])await f.page.setViewportSize({width,height:1000});
      assert.equal(await after.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${surface}/${role}/${width} overflow`);
      assert(await after.page.locator(selector).evaluateAll(nodes=>nodes.every(n=>getComputedStyle(n).boxShadow==='none'&&getComputedStyle(n).borderRadius==='0px')));
      assert(await after.page.locator(selector+' button').evaluateAll(nodes=>nodes.every(n=>n.getBoundingClientRect().height>=44&&n.getBoundingClientRect().width>=44&&(n.getAttribute('aria-label')||n.textContent.trim()))));
      if([390,1440].includes(width)){const previous=(await before.page.locator(oldSelector).first().boundingBox()).height,current=(await after.page.locator(selector).first().boundingBox()).height;assert(current<previous,`${surface}/${role}/${width}: ${previous} -> ${current}`);console.log(`[ok] ${surface}/${role}/${width}: ${previous}px -> ${current}px`);await before.page.screenshot({path:`WIREFRAME/QA/screenshots/management-list-before-${surface}-${role}-${width}.png`,fullPage:true});}
      await after.page.screenshot({path:`WIREFRAME/QA/screenshots/management-list-${surface}-${role}-${width}.png`,fullPage:true});
    }
    assert((await after.page.title()).includes('CASTLE THE ART'));assert((await after.page.locator('#main-content').innerText()).trim());assert.equal(await after.page.locator('nextjs-portal,vite-error-overlay').count(),0);
  }
  await after.page.evaluate(()=>__compactQA.setup('more','admin'));
  const account=after.page.locator('[data-action="account-status"]');await account.press('Enter');await after.page.getByRole('heading',{name:'계정·로그인 상태',exact:true}).waitFor();await after.page.keyboard.press('Tab');assert(await after.page.evaluate(()=>!!document.activeElement.closest('#modal-root')));await after.page.keyboard.press('Escape');await after.page.waitForFunction(()=>document.activeElement?.dataset.action==='account-status');await account.click();await after.page.goBack();await after.page.getByRole('heading',{name:'계정·로그인 상태',exact:true}).waitFor({state:'hidden'});
  await after.page.evaluate(()=>__compactQA.setup('pay','admin'));await after.page.locator('[data-action="live-payroll-detail"]').first().click();await after.page.getByRole('heading',{name:'데모 메이드 1 · 주급 산출 내역',exact:true}).waitFor();await after.page.getByRole('heading',{name:'확정 청소비가 없습니다',exact:true}).waitFor();assert(after.requests.includes('/v1/payroll/work-details'));
  await after.page.evaluate(()=>__compactQA.setup('maids','admin'));await after.page.locator('[data-action="live-maid-detail"]').first().click();await after.page.getByRole('heading',{name:'계정·근무 상태',exact:true}).waitFor();for(const width of widths){await after.page.setViewportSize({width,height:1000});assert.equal(await after.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'shared payroll summary in narrow aside');}
  await after.page.evaluate(()=>__compactQA.setup('pay','maid'));const reads=after.requests.length;await after.page.evaluate(()=>__compactQA.guard());assert.equal(after.requests.length,reads);assert.equal(await after.page.locator('[data-action="live-payroll-toggle"]').count(),0);
  await before.close();await after.close();
  console.log('[ok] all live text/targets/states preserved; modal Enter/Tab/Escape/Back/focus, payroll GET/detail, maid/detail aside, foreign maid guard');
  // Exercise actual demo login/navigation and shared rendering without external APIs.
  const demo=await fixture(false,false);await demo.page.locator('#login-id').fill('admin');await demo.page.locator('#login-password').fill('admin1234');await demo.page.locator('#login-form').press('Enter');
  await demo.page.locator('[data-action="nav"][data-view="maids"]:visible').first().click();assert.equal(await demo.page.locator('.maid-summary-row').count(),9);
  for(const surface of ['workforce','pay']){await demo.page.locator(`[data-action="admin-maid-tab"][data-tab="${surface}"]`).click();for(const width of widths){await demo.page.setViewportSize({width,height:1000});assert.equal(await demo.page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`demo ${surface} overflow ${width}`);}}
  await demo.page.locator('[data-action="admin-pay-detail"]').first().click();await demo.page.locator('.pay-ledger-list').waitFor();await demo.page.locator('[data-action="back"]').click();await demo.page.locator('[data-action="nav"][data-view="more"]:visible').first().click();await demo.page.locator('[data-action="account-status"]').press('Enter');await demo.page.getByRole('heading',{name:'계정·로그인 상태',exact:true}).waitFor();await demo.page.keyboard.press('Escape');assert.equal(demo.requests.length,0);await demo.close();
  console.log('[ok] demo 9-maid roster/payroll four widths, ledger and account destinations; no external business requests');
  console.log('Playwright Chromium '+await browser.version()+'; Browser plugin not available. Actual operations/phone UAT not exercised.');
}finally{await browser.close();}
