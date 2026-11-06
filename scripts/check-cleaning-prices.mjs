#!/usr/bin/env node
// Isolated browser fixtures; never changes production prices or operational records.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)(process.env.RMS_QA_PLAYWRIGHT_MODULE||'playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4185';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const output=process.env.RMS_QA_OUTPUT||'WIREFRAME/QA/screenshots';
const source=await readFile(process.env.RMS_QA_SOURCE||'WIREFRAME/index.html','utf8');
const baseline=!!process.env.RMS_QA_SOURCE;
const id=n=>`11000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const seed=[['standard','스탠다드 더블 로프트',16000],['premier','프리미어 더블 로프트',20000],['ocean_premier','파셜 오션뷰 프리미어 더블 로프트',20000],['family','파셜 오션뷰 패밀리 투룸 로프트',30000]].map(([code,displayName,baseCleaningFee],i)=>({id:id(i+1),code,displayName,baseCleaningFee,version:1,active:true,baseOccupancy:2,maxOccupancy:4}));
let items=structuredClone(seed),requests=[],unexpected=[],errors=[],warnings=[],readFailure=false,empty=false,missing=false,readDelay=0,saveDelay=0,nextError=null,replay=null,latePrice=null,invalidReceipt=false;
const hook=`window.__ratesQA={setup:(role='admin',forced=false)=>{LIVE_RUNTIME.authGeneration++;clearLiveAuthSurface();LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:false}});state.remote=initialRemoteState();state.role=role;state.liveView='more';state.detail=null;state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'${id(20)}',displayName:'합성 QA 계정 · 데모',role,mustChangePassword:forced},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};for(const key of ['accounts','rooms','roomTypes','reservations','availability','developer','notifications','complaints'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});state.remote.roomTypes.items=${JSON.stringify(seed)};state.remote.developer.overview={};state.remote.developer.runtime={};state.remote.developer.database={};state.remote.developer.scheduler={};state.remote.complaints.items=[];syncAuthState(state);render();},open:openActionRates,expire:()=>{liveRatesEditor.loadedAt=0;},save:()=>saveLiveRate(),get:()=>({request:liveRatesEditor?.request,uncertain:!!uncertainLiveMutation,items:state.remote.roomTypes.items}),demo:()=>{LIVE_RUNTIME.mode='demo';state=makeScenario(0);writeAuthSession(authAccounts().find(a=>a.id==='admin'));syncAuthState(state);state.adminView='more';render();}};`;
const html=source.replace('\n      void bootApplication();',hook).replace('<body>','<body><div style="position:fixed;top:0;right:0;z-index:99999;background:white;color:#18334c;font-size:12px;padding:3px 6px;pointer-events:none">합성 QA · 데모 데이터</div>');
const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_EXECUTABLE?{executablePath:process.env.RMS_QA_BROWSER_EXECUTABLE}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block',reducedMotion:'reduce',locale:'ko-KR',timezoneId:'America/New_York'});
const page=await context.newPage();page.setDefaultTimeout(10000);
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:')&&m.text()!=='Service Worker registration blocked by Playwright')warnings.push(m.text());});
const reply=(route,data,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(data),headers:{'cache-control':'no-store'}});
await page.route('**/*',async route=>{
  const req=route.request(),url=new URL(req.url());
  if(url.origin===new URL(origin).origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:html});return route.continue();}
  if(!req.url().startsWith(api+'/')){unexpected.push(url.pathname);return route.abort();}
  const path=url.pathname.replace('/functions/v1/api',''),method=req.method(),body=req.postData()?JSON.parse(req.postData()):null,key=req.headers()['idempotency-key'];
  requests.push({path,method,body,key});
  if(path==='/v1/room-types'&&method==='GET'){
    if(readDelay)await new Promise(r=>setTimeout(r,readDelay));
    if(readFailure)return reply(route,{error:{code:'AUTH_CONTEXT_UNAVAILABLE'}},503);
    if(missing)return reply(route,{});
    return reply(route,{items:empty?[]:items});
  }
  if(path==='/v1/auth/me')return reply(route,{user:{profileId:id(20),displayName:'QA 관리자 · 데모',role:'admin',mustChangePassword:true}});
  if(path.endsWith('/cleaning-fee')&&method==='PUT'){
    assert.match(key,/^[A-Za-z0-9._:-]{8,128}$/);
    assert.deepEqual(Object.keys(body).sort(),['baseCleaningFee','confirmFutureTargetsOnly','expectedVersion'].sort());
    assert.equal(body.confirmFutureTargetsOnly,true);assert.equal(typeof body.baseCleaningFee,'number');
    if(saveDelay)await new Promise(r=>setTimeout(r,saveDelay));
    const type=items.find(item=>path.includes(item.id));assert.ok(type);
    if(replay){assert.equal(key,replay.key);assert.deepEqual(body,replay.body);const result=replay.result;replay=null;if(latePrice!==null){type.baseCleaningFee=latePrice;type.version++;latePrice=null;}return reply(route,result);}
    if(nextError){const error=nextError;nextError=null;
      if(error==='network-after-commit'){type.baseCleaningFee=body.baseCleaningFee;type.version++;replay={key,body,result:{roomType:{roomTypeId:type.id,baseCleaningFee:type.baseCleaningFee,version:type.version,effectiveFor:'NEW_TARGETS_ONLY'}}};return route.abort('failed');}
      if(error.status===409){type.baseCleaningFee=17000;type.version++;}
      return reply(route,{error:{code:error.code||'TEST_ERROR',message:'server text must not leak'}},error.status);
    }
    if(body.expectedVersion!==type.version)return reply(route,{error:{code:'STALE_VERSION'}},409);
    if(type.baseCleaningFee!==body.baseCleaningFee){type.baseCleaningFee=body.baseCleaningFee;type.version++;}
    const result={roomType:{roomTypeId:type.id,baseCleaningFee:type.baseCleaningFee,version:type.version,effectiveFor:'NEW_TARGETS_ONLY'}};
    if(invalidReceipt){invalidReceipt=false;replay={key,body,result};return reply(route,{roomType:{...result.roomType,roomTypeId:id(99)}});}
    return reply(route,result);
  }
  if(path==='/v1/notifications')return reply(route,{items:[],nextCursor:null});
  unexpected.push(method+' '+path);return reply(route,{error:{code:'UNEXPECTED_QA_REQUEST'}},500);
});
const button=action=>page.locator(`[data-action="${action}"]`);
const amount=()=>page.locator(`[data-rate-id="${id(1)}"]`);
const review=()=>button('live-rates-review').first().click();
const ready=()=>page.waitForFunction(()=>document.querySelectorAll('[data-rate-id]').length===4);
const setup=async role=>{await page.goto(origin+'/index.html?view=more');await page.evaluate(role=>window.__ratesQA.setup(role),role||'admin');};
const open=async()=>{await button('rates').click();await ready();};
const prepare=async value=>{await amount().fill(String(value));await review();await page.locator('#live-rate-confirm-scope').check();};
const save=async()=>{await button('live-rates-save').click();await ready();};
const screenshot=async name=>{await mkdir(output,{recursive:true});await page.screenshot({path:`${output}/cleaning-prices-${name}.png`,fullPage:false});};
try{
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:900});await setup();
    assert.equal(new URL(page.url()).searchParams.get('view'),'more');assert.match(await page.title(),/CASTLE THE ART/);assert.ok((await page.locator('#main-content').innerText()).includes('계정·로그인'));
    assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);
    if([390,1440].includes(width))await screenshot(`${baseline?'before':'after'}-more-${width}`);
    if(baseline)continue;
    await button('rates').focus();await page.keyboard.press('Enter');await ready();
    assert.equal(await page.locator('#modal-title').innerText(),'청소 가격표');
    assert.ok(await page.evaluate(()=>document.querySelector('#app').inert));
    const metrics=await page.locator('[data-live-rates]').evaluate(el=>({overflow:document.documentElement.scrollWidth>innerWidth||el.scrollWidth>el.clientWidth+1,small:[...el.querySelectorAll('button,input')].filter(e=>{const r=e.getBoundingClientRect();return r.width<44||r.height<44;}).length}));
    assert.equal(metrics.overflow,false);assert.equal(metrics.small,0);
    assert.equal(await amount().getAttribute('aria-label'),seed[0].displayName+' 변경할 청소 금액');
    if([390,1440].includes(width))await screenshot(`list-${width}`);
    await amount().fill('18,000');await review();
    assert.equal(await button('live-rates-save').isDisabled(),true);
    assert.match(await page.locator('[data-live-rates]').innerText(),/이미 생성된 미래 청소·진행 청소·확정 수당·주급/);
    assert.match(await page.locator('[data-live-rates]').innerText(),/18,000원/);
    if([390,1440].includes(width))await screenshot(`confirm-${width}`);
    const focusables=page.locator('.modal button:not([disabled]),.modal input:not([disabled])');await focusables.last().focus();await page.keyboard.press('Tab');assert.ok(await focusables.first().evaluate(el=>el===document.activeElement));await page.keyboard.press('Shift+Tab');assert.ok(await focusables.last().evaluate(el=>el===document.activeElement));
    await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.modal'));await page.waitForFunction(()=>document.activeElement?.dataset.action==='rates');
    await open();await page.goBack();await page.waitForFunction(()=>!document.querySelector('.modal'));await page.waitForFunction(()=>document.activeElement?.dataset.action==='rates');
    // Existing settings destinations remain intact.
    await button('account-status').click();assert.match(await page.locator('.modal').innerText(),/계정|로그인/);await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.modal'));
  }
  if(!baseline){
    await setup();await open();
    for(const value of ['', '-1','1.5','1e3','1,2','1073741824','null']){await amount().fill(value);await review();assert.equal(await button('live-rates-save').count(),0);assert.equal(await amount().getAttribute('aria-invalid'),'true');}
    assert.equal(requests.filter(x=>x.method==='PUT').length,0);
    for(const value of [18000,12000,0,0,1073741823]){await prepare(value);const count=requests.length;await save();const mutations=requests.slice(count).filter(x=>x.method==='PUT');assert.equal(mutations.length,1);assert.equal(mutations[0].body.baseCleaningFee,value);assert.equal(await amount().inputValue(),String(value));assert.ok(requests.slice(count).some(x=>x.method==='GET'));}
    await prepare(15000);const offlineCount=requests.length;await context.setOffline(true);await button('live-rates-save').click();assert.equal(requests.length,offlineCount);await context.setOffline(false);readFailure=true;await button('live-rates-save').click();await page.getByText('청소 가격표를 불러오지 못했습니다. 입력한 금액은 유지됩니다.').waitFor();assert.equal(await amount().count(),0);readFailure=false;await button('live-rates-refresh').click();await ready();assert.equal(await amount().inputValue(),'15000');
    // Concurrent update retains input and requires a fresh confirmation/key/version.
    nextError={status:409,code:'STALE_VERSION'};await prepare(19000);await save();assert.equal(await amount().inputValue(),'19000');assert.match(await page.locator('[data-live-rates]').innerText(),/현재 17,000원/);const conflicted=requests.findLast(x=>x.method==='PUT');await review();assert.equal(await button('live-rates-save').isDisabled(),true);await page.locator('#live-rate-confirm-scope').check();await save();const latest=requests.findLast(x=>x.method==='PUT');assert.notEqual(latest.key,conflicted.key);assert.equal(latest.body.expectedVersion,conflicted.body.expectedVersion+1);
    // Replayed receipt can be older than the authoritative latest GET.
    nextError='network-after-commit';await prepare(21000);await button('live-rates-save').click();await page.waitForFunction(()=>document.querySelector('[data-action="live-rates-save"]')?.textContent==='같은 요청 결과 확인');assert.equal(await amount().count(),0);latePrice=22000;await save();assert.equal(await amount().inputValue(),'22000');
    invalidReceipt=true;await prepare(23000);await button('live-rates-save').click();await page.waitForFunction(()=>document.querySelector('[data-action="live-rates-save"]')?.textContent==='같은 요청 결과 확인');await save();assert.equal(await amount().inputValue(),'23000');
    // 503 leaves exactly the same command pending, even after closing/reopening.
    nextError={status:503,code:'AUTH_CONTEXT_UNAVAILABLE'};await prepare(24000);await button('live-rates-save').click();await page.waitForFunction(()=>document.querySelector('[data-action="live-rates-save"]')?.textContent==='같은 요청 결과 확인');const failed=requests.findLast(x=>x.method==='PUT');await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('.modal'));await button('confirm-uncertain-live-mutation').click();await button('live-rates-save').click();await ready();assert.deepEqual(requests.findLast(x=>x.method==='PUT'),failed);
    await amount().fill('25000');await page.evaluate(()=>window.__ratesQA.expire());await review();await ready();assert.equal(await button('live-rates-save').count(),0);assert.equal(await amount().inputValue(),'25000');
    nextError={status:400};await prepare(25000);await save();assert.equal(await amount().inputValue(),'25000');assert.equal((await page.locator('[data-live-rates]').innerText()).includes('server text'),false);
    nextError={status:404};await prepare(25000);await save();assert.equal(await amount().inputValue(),'25000');
    nextError={status:403,code:'ADMIN_REQUIRED'};await prepare(25000);await save();assert.equal(await amount().isDisabled(),true);
    // Read failures and missing envelopes must not be rendered as a zero price/empty success.
    readFailure=true;await setup();await button('rates').click();await page.getByText('청소 가격표를 불러오지 못했습니다. 입력한 금액은 유지됩니다.').waitFor();assert.equal(await amount().count(),0);readFailure=false;await button('live-rates-refresh').click();await ready();
    await amount().fill('26000');readFailure=true;await button('live-rates-refresh').click();await page.getByText('청소 가격표를 불러오지 못했습니다. 입력한 금액은 유지됩니다.').waitFor();readFailure=false;await button('live-rates-refresh').click();await ready();assert.equal(await amount().inputValue(),'26000');
    empty=true;await button('live-rates-refresh').click();await page.getByText('등록된 객실 타입이 없습니다.').waitFor();empty=false;
    missing=true;await button('live-rates-refresh').click();await page.getByText('청소 가격표를 불러오지 못했습니다. 입력한 금액은 유지됩니다.').waitFor();missing=false;
    items[0].baseCleaningFee=null;await button('live-rates-refresh').click();await ready();assert.equal(await amount().inputValue(),'26000');assert.equal(await amount().isDisabled(),true);items=structuredClone(seed);
    await setup();readDelay=500;await button('rates').click();await page.getByText('청소 가격표를 불러오는 중입니다.').waitFor();await page.keyboard.press('Escape');await page.waitForTimeout(650);assert.equal(await page.locator('.modal').count(),0);readDelay=0;
    // Double click / close during save: one command, no resurrected modal.
    await open();await prepare(27000);saveDelay=400;const before=requests.filter(x=>x.method==='PUT').length;await page.evaluate(()=>{window.__ratesQA.save();window.__ratesQA.save();});await page.keyboard.press('Escape');await page.waitForTimeout(650);saveDelay=0;assert.equal(requests.filter(x=>x.method==='PUT').length,before+1);assert.equal(await page.locator('.modal').count(),0);
    await open();await prepare(28000);nextError={status:401,code:'SESSION_REVOKED'};await button('live-rates-save').click();await page.locator('#login-id').waitFor();assert.equal(await page.locator('.modal').count(),0);
    await setup();await open();await prepare(29000);nextError={status:403,code:'PASSWORD_CHANGE_REQUIRED'};await button('live-rates-save').click();await page.locator('#new-password').waitFor();assert.equal(await page.locator('.modal').count(),0);
    // Role/forced-password guards also apply to direct handler entry and delayed responses.
    for(const role of ['developer','maid']){await setup(role);assert.equal(await button('rates').count(),0);const count=requests.length;await page.evaluate(()=>window.__ratesQA.open());assert.equal(await page.locator('.modal').count(),0);assert.equal(requests.length,count);}
    await setup();await page.evaluate(()=>window.__ratesQA.setup('admin',true));const count=requests.length;await page.evaluate(()=>window.__ratesQA.open());assert.equal(requests.length,count);
    await setup();readDelay=500;await button('rates').click();await page.evaluate(()=>window.__ratesQA.setup('maid'));await page.waitForTimeout(650);readDelay=0;assert.equal(await page.locator('.modal').count(),0);assert.equal(await button('rates').count(),0);
    await page.evaluate(()=>window.__ratesQA.demo());await button('rates').click();assert.match(await page.locator('.modal').innerText(),/객실 타입 청소요금·예상시간/);assert.equal(await button('live-rates-save').count(),0);
  }
  assert.deepEqual(errors,[]);assert.deepEqual(warnings,[]);assert.deepEqual(unexpected,[]);
  console.log(JSON.stringify({result:'PASS',baseline,browser:browser.version(),viewports:[360,390,768,1440],writes:requests.filter(x=>x.method==='PUT').length,unexpected,errors,warnings,scope:'synthetic APIs only; production mutations not run'}));
}finally{await browser.close();}
