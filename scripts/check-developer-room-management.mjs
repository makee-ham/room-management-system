#!/usr/bin/env node
// Browser regression for the developer room count and API-unavailable room management UI.
import assert from 'node:assert/strict';
import { mkdir, readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4175';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const fixture={generatedAt:'2026-09-20T10:00:00+09:00',accounts:{total:12,active:11,byRole:{developer:1,admin:2,maid:9}},rooms:{total:121},auditEventsLast24Hours:28,runtime:{environment:'production',source:{apiVersion:'0.4.0'},projectRef:'aodikrxcczbogjpsjwjt',runtime:{name:'deno',version:'2'},configuration:{schedulerSecret:{configured:true}},checkedAt:'2026-09-20T10:00:00+09:00'},database:{databaseReachable:true,rlsValid:true,migrationDrift:'equal',rlsMissingCount:0,rowCounts:{profiles:12,rooms:121},checkedAt:'2026-09-20T10:00:00+09:00'},scheduler:{status:'healthy',cronConfigured:true,cronActive:true,cadence:'매 5분',schedulerActorValid:true,lastHeartbeat:{completedAt:'2026-09-20T10:00:00+09:00'}}};
const source=await readFile(resolve('WIREFRAME/index.html'),'utf8');
const html=source.replace('\n      void bootApplication();',`LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',sessionPersistence:'session',deploymentChannel:'preview',featureFlags:{optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:'10000000-0000-4000-8000-000000000001',displayName:'QA 개발자',role:'developer',mustChangePassword:false},session:{accessToken:'qa-token-never-log',refreshToken:'qa-refresh-never-log',expiresAt:Date.now()+3600000}};state.remote.developer={...state.remote.developer,status:'ready',overview:${JSON.stringify(fixture)},runtime:${JSON.stringify(fixture.runtime)},database:${JSON.stringify(fixture.database)},scheduler:${JSON.stringify(fixture.scheduler)},lastSuccessAt:${JSON.stringify(fixture.generatedAt)}};state.role='developer';state.liveView='overview';syncAuthState(state);render();`);

const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(10000);
const pageErrors=[],consoleProblems=[],roomMutationRequests=[];
page.on('pageerror',error=>pageErrors.push(error.message));
page.on('console',message=>{if(['warning','error'].includes(message.type())&&!/^Failed to load resource:/.test(message.text()))consoleProblems.push(message.text());});
page.on('request',request=>{if(/\/v1\/rooms(?:\/|$)/.test(request.url())&&['POST','PUT','PATCH','DELETE'].includes(request.method()))roomMutationRequests.push({method:request.method(),url:request.url()});});
await page.route('**/favicon.ico',route=>route.fulfill({status:204,body:''}));
await page.route('**/index.html*',route=>route.fulfill({status:200,contentType:'text/html',body:html}));

async function assertResponsive(width){
  await page.setViewportSize({width,height:width>=768?1000:950});
  await page.waitForTimeout(50);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`horizontal overflow at ${width}px`);
  const controls=page.locator('[data-live-developer-rooms] .select-control, [data-live-developer-rooms] .input-control, [data-live-developer-rooms] .btn');
  for(let index=0;index<await controls.count();index+=1){const box=await controls.nth(index).boundingBox();assert(box&&box.height>=44,`control ${index} is below 44px at ${width}px`);}
}

try{
  await mkdir(resolve('WIREFRAME/QA/screenshots'),{recursive:true});
  await page.goto(`${origin}/index.html`);
  await page.getByText('백엔드 v0.4.0 운영 상태',{exact:true}).waitFor();
  const roomNav=page.locator('[data-action="nav"][data-view="rooms"]:visible').first();
  assert.equal(await roomNav.getAttribute('aria-label'),null);
  assert.match((await roomNav.innerText()).trim(),/객실/);
  await roomNav.click();
  await page.getByRole('heading',{name:'객실 등록 관리',exact:true}).waitFor();
  assert.equal(new URL(page.url()).searchParams.get('view'),'rooms');
  assert.equal(await page.locator('[data-live-developer-rooms]').count(),1);
  assert(await page.getByText('121실',{exact:true}).isVisible());
  assert(await page.getByText('121행',{exact:true}).isVisible());
  assert(await page.getByText('일치',{exact:true}).isVisible());

  const type=page.locator('[data-control="developer-room-type"]'),roomNumber=page.locator('[data-control="developer-room-number"]'),deleteNumber=page.locator('[data-control="developer-room-delete-number"]');
  assert.deepEqual(await type.locator('option').allTextContents(),['스탠다드','프리미어','파셜 오션뷰','패밀리 투룸']);
  await type.selectOption('oceanFamily');
  await roomNumber.fill('516');
  await deleteNumber.fill('350');
  assert.equal(await type.inputValue(),'oceanFamily');
  assert.equal(await roomNumber.inputValue(),'516');
  assert.equal(await deleteNumber.inputValue(),'350');
  assert(await page.getByRole('button',{name:'객실 추가 · API 미제공',exact:true}).isDisabled());
  assert(await page.getByRole('button',{name:'삭제 영향 확인 · API 미제공',exact:true}).isDisabled());
  assert(await page.getByText('객실 추가·삭제 API가 아직 제공되지 않습니다.',{exact:true}).isVisible());

  await type.focus();
  assert.equal(await page.evaluate(()=>document.activeElement?.id),'developer-room-type');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement?.id),'developer-room-number');
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(()=>document.activeElement?.id),'developer-room-delete-number');

  for(const width of [360,390,768,1440]){
    await assertResponsive(width);
    await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});
    await page.waitForTimeout(50);
    if(width===390||width===1440)await page.screenshot({path:resolve(`WIREFRAME/QA/screenshots/live-developer-room-management-${width}.png`),fullPage:width===1440});
  }
  assert.deepEqual(roomMutationRequests,[]);
  assert.deepEqual(pageErrors,[]);
  assert.deepEqual(consoleProblems,[]);
  console.log('[ok] 개발자 객실 내비게이션·현재 등록 수·DB 행 수');
  console.log('[ok] 객실 유형 드롭다운·추가/삭제 호수 입력·키보드 순서');
  console.log('[ok] 추가/삭제 API 미제공 비활성 상태·운영 mutation 0건');
  console.log('[ok] 360/390/768/1440px 가로 넘침·44px 컨트롤·console 오류 검사');
  console.log(`Environment: Chromium ${await browser.version()} via Playwright; Browser plugin unavailable. Production API writes were not executed.`);
}catch(error){
  console.error('page errors',pageErrors);
  console.error('console problems',consoleProblems);
  await page.screenshot({path:'/tmp/developer-room-management-qa-failure.png',fullPage:true});
  throw error;
}finally{
  await browser.close();
}
