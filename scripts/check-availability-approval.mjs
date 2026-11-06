#!/usr/bin/env node
// Browser plugin unavailable: isolated Playwright fixtures; no operational writes.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4178';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const source=await readFile(process.env.RMS_QA_SOURCE||'WIREFRAME/index.html','utf8');
const baseline=!!process.env.RMS_QA_SOURCE;
const today='2026-11-04',week='2026-11-02',next='2026-11-09';
const shift=(date,n)=>new Date(Date.parse(date+'T12:00:00Z')+n*86400000).toISOString().slice(0,10);
const id=n=>`11000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const maid={id:id(1),profileId:id(1),displayName:'검증 메이드 · 데모',role:'maid',status:'active',mustChangePassword:false};
const admin={...maid,id:id(2),profileId:id(2),displayName:'검증 관리자 · 데모',role:'admin'};
const version=(start,num,dates)=>({id:id(20+num),maidProfileId:maid.id,weekStart:start,version:num,status:'submitted',current:true,submittedAt:'2026-11-01T10:00:00Z',days:Array.from({length:7},(_,i)=>({workDate:shift(start,i),available:dates.includes(shift(start,i))}))});
let versions=[version(week,1,[week,today]),version(next,1,[next])],changes=[],writes=[],delay=0,conflict=false,role='maid';
const requests=[],errors=[],warnings=[],unexpected=[];
const hook=`window.__availabilityQA={setup:async(role='maid',choice='next')=>{LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:false}});state.remote=initialRemoteState();state.role=role;state.detail=null;state.liveView=role==='admin'?'maids':'schedule';state.adminMaidTab='workforce';state.remote.auth={...state.remote.auth,status:'authenticated',user:role==='admin'?${JSON.stringify(admin)}:${JSON.stringify(maid)},session:{accessToken:'qa-token',refreshToken:'qa-refresh',expiresAt:Date.now()+3600000}};for(const key of ['accounts','rooms','notifications','availability','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});state.remote.accounts.items=[${JSON.stringify(maid)}];state.remote.availability.weekChoice=choice;syncAuthState(state);rawCloseModal();await loadLiveAvailability({quiet:true});render();},demo:(role,reset=false)=>{LIVE_RUNTIME.mode='demo';if(reset)state=makeScenario(0);writeAuthSession(authAccounts().find(a=>a.id===(role==='admin'?'admin':'maid1')));syncAuthState(state);state.detail=null;state.maidView='schedule';state.adminView='maids';state.adminMaidTab='workforce';state.weekChoice='current';render();},demoGet:()=>({requests:state.availabilityRequests||[],current:demoCurrentAvailability('m1')}),get:()=>JSON.parse(JSON.stringify(state.remote.availability)),decide:decideLiveAvailability,refresh:loadLiveAvailability,submit:submitLiveAvailability,modal:()=>showModal({title:'검증 모달',body:'<label for="qa-input">검증 입력</label><input id="qa-input">',confirmLabel:'확인',confirmAction:'close-modal'})};`;
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block',reducedMotion:'reduce',locale:'ko-KR'});
await context.addInitScript(()=>{const RealDate=Date;const now=Date.parse('2026-11-04T01:00:00Z');window.Date=class extends RealDate{constructor(...args){super(...(args.length?args:[now]));}static now(){return now;}};});
const page=await context.newPage();page.setDefaultTimeout(10000);
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&!m.text().startsWith('Failed to load resource:')&&m.text()!=='Service Worker registration blocked by Playwright')warnings.push(m.text());});
const reply=(r,data,status=200)=>r.fulfill({status,contentType:'application/json',headers:{'x-request-id':'qa-availability'},body:JSON.stringify(data)});
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());
 if(url.origin===origin){if(url.pathname==='/runtime-config.json')return reply(route,{mode:'demo'});if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace('      void bootApplication();',hook+'\n      void bootApplication();')});return route.continue();}
 if(!req.url().startsWith(api+'/')){unexpected.push(url.origin);return route.abort();}
 const path=url.pathname.replace('/functions/v1/api',''),body=req.postDataJSON(),method=req.method();requests.push({path,body,method,query:url.search});
 if(path==='/v1/availability'&&method==='GET'){const start=url.searchParams.get('weekStart');return reply(route,{availability:versions.filter(v=>v.weekStart===start)});}
 if(path==='/v1/availability/change-requests'&&method==='GET')return reply(route,{changeRequests:changes.filter(v=>v.weekStart===url.searchParams.get('weekStart')&&(!url.searchParams.has('status')||v.status===url.searchParams.get('status'))).toReversed()});
 if(method==='POST'&&path.startsWith('/v1/availability/')){
  writes.push({path,body,key:req.headers()['idempotency-key'],role});assert(req.headers()['idempotency-key']);if(delay)await new Promise(r=>setTimeout(r,delay));
  if(conflict)return reply(route,{error:{code:'ASSIGNMENT_AVAILABILITY_STALE'}},409);
  if(path==='/v1/availability/submissions'){assert.equal(role,'maid');assert.equal(body.weekStart,next);const old=versions.find(v=>v.weekStart===next);assert.equal(body.expectedVersion,old.version);versions=versions.filter(v=>v.weekStart!==next).concat(version(next,old.version+1,body.availableDates));return reply(route,{availability:versions.at(-1)},201);}
  if(path==='/v1/availability/change-requests'){assert.equal(role,'maid');assert.equal(body.weekStart,week);assert(!changes.some(v=>v.status==='pending'));const old=versions.find(v=>v.weekStart===week);assert.equal(body.expectedVersion,old?.version||0);const change={id:id(50+changes.length),availabilityVersionId:old?.id||null,maidProfileId:maid.id,weekStart:week,sourceVersion:body.expectedVersion,requestedAvailableDates:body.requestedAvailableDates,reasonCode:body.reasonCode,status:'pending',requestedAt:today+'T01:00:00Z',decidedBy:null,decidedAt:null,decisionReasonCode:null,approvedVersionId:null};changes.push(change);return reply(route,{changeRequest:change},201);}
  assert.equal(role,'admin');const change=changes.find(v=>path.includes(v.id));assert(change);assert.equal(body.expectedVersion,change.sourceVersion);assert.equal(change.status,'pending');change.status=body.decision;if(body.decision==='approved')versions=versions.filter(v=>v.weekStart!==week).concat(version(week,body.expectedVersion+1,change.requestedAvailableDates));return reply(route,{changeRequest:change});
 }
 if(path==='/v1/notifications')return reply(route,{items:[],nextCursor:null});
 if(path==='/v1/accounts')return reply(route,{accounts:[maid]});
 if(path==='/v1/work-history')return reply(route,{weekStart:week,weekEnd:shift(week,6),maids:[],summary:{}});
 if(path==='/v1/cleaning-history')return reply(route,{items:[],nextCursor:null});
 if(path==='/v1/payroll')return reply(route,{payroll:[],nextCursor:null});
 if(path==='/v1/rooms')return reply(route,{rooms:[]});
 unexpected.push(method+' '+path);return reply(route,{error:{code:'UNEXPECTED_QA_REQUEST'}},500);
});
const action=(name,extra='')=>page.locator(`[data-action="${name}"]${extra}:visible`).first();
async function setup(nextRole='maid',choice='current'){role=nextRole;await page.evaluate(([r,c])=>window.__availabilityQA.setup(r,c),[nextRole,choice]);}
async function ready(){await page.waitForFunction(()=>window.__availabilityQA.get().status==='ready');}
async function audit(name){
 await page.locator('.toast').waitFor({state:'hidden'});
 for(const width of [360,390,768,1440]){
  await page.setViewportSize({width,height:900});await page.waitForTimeout(220);
  const issues=await page.evaluate(()=>{const issues=[];if(document.documentElement.scrollWidth>innerWidth)issues.push('overflow');for(const e of document.querySelectorAll('#main-content button,#main-content select')){if(!e.checkVisibility())continue;const r=e.getBoundingClientRect();if(r.width<43.5||r.height<43.5)issues.push('small '+e.textContent);if(!e.textContent.trim()&&!e.getAttribute('aria-label'))issues.push('missing name');}return issues;});assert.deepEqual(issues,[],name+'/'+width);
  if([390,1440].includes(width))await page.screenshot({path:`WIREFRAME/QA/screenshots/availability-${baseline?'before-':''}${name}-${width}.png`});
 }
}
try{
 await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await page.goto(origin+'/index.html');await page.locator('#login-form').waitFor();
 if(baseline){await setup('maid','next');await audit('maid-next');await setup('admin','next');await audit('admin-next');console.log('availability baseline screenshots captured');}
 else{
  await setup('maid','next');await audit('maid-next');await action('live-availability-week','[data-week="current"]').click();await ready();
  assert.equal(await page.locator('[data-control="live-availability-date"]:disabled').count(),2);assert(await action('submit-live-availability').isDisabled());
  const changed=shift(today,1);await page.locator(`[data-control="live-availability-date"][value="${changed}"]`).locator('..').click();await page.locator('#availability-reason').selectOption('WORK_SCHEDULE');
  await audit('maid-current');delay=150;await action('submit-live-availability').click();await page.evaluate(()=>window.__availabilityQA.submit());await ready();delay=0;
  assert.equal(writes.length,1);assert.equal(writes[0].body.reasonCode,'WORK_SCHEDULE');assert.deepEqual(writes[0].body.requestedAvailableDates,[week,today,changed]);assert.equal(versions.find(v=>v.weekStart===week).version,1);
  assert(await action('submit-live-availability').isDisabled());assert.equal(await page.locator('[data-control="live-availability-date"]:disabled').count(),7);await audit('maid-pending');
  const before=writes.length;await page.evaluate(()=>window.__availabilityQA.decide('forged','approved',1));assert.equal(writes.length,before);
  await setup('admin');await audit('admin-current');conflict=true;await action('live-availability-decision','[data-decision="approved"]').click();await ready();assert.equal(changes[0].status,'pending');assert.equal(versions.find(v=>v.weekStart===week).version,1);conflict=false;
  await action('live-availability-decision','[data-decision="rejected"]').click();await ready();assert.equal(changes[0].status,'rejected');assert.equal(versions.find(v=>v.weekStart===week).version,1);
  await setup('maid');assert((await page.locator('#main-content').innerText()).includes('반려됨'));await page.locator(`[data-control="live-availability-date"][value="${changed}"]`).locator('..').click();await action('submit-live-availability').click();await ready();
  await setup('admin');await action('live-availability-decision','[data-decision="approved"]').click();await ready();assert.equal(versions.find(v=>v.weekStart===week).version,2);assert.equal(changes[1].status,'approved');
  await setup('maid');assert((await page.locator('#main-content').innerText()).includes('승인됨'));assert(await page.locator(`[value="${changed}"]`).isChecked());
  await action('live-availability-week','[data-week="next"]').click();await ready();await page.locator(`[data-control="live-availability-date"][value="${shift(next,2)}"]`).locator('..').click();await action('submit-live-availability').click();await ready();assert.equal(versions.find(v=>v.weekStart===next).version,2);
  // First submission is also an approval request; missing current data is never fabricated.
  versions=versions.filter(v=>v.weekStart!==week);changes=[];await setup('maid');await page.locator(`[data-control="live-availability-date"][value="${today}"]`).locator('..').click();await action('submit-live-availability').click();await ready();assert.equal(writes.at(-1).body.expectedVersion,0);assert(!versions.some(v=>v.weekStart===week));
  await setup('admin');await action('live-availability-decision','[data-decision="approved"]').click();await ready();assert.equal(versions.find(v=>v.weekStart===week).version,1);
  // Existing card destination, Back, modal focus trap and Escape remain intact.
  await action('live-maid-detail').click();assert((await page.locator('#main-content').innerText()).includes('계정·근무 상태'));await action('back').click();await action('live-availability-week').waitFor();
  await page.evaluate(()=>window.__availabilityQA.modal());await page.locator('[role="dialog"]').waitFor();await page.locator('[role="dialog"] button').last().focus();await page.keyboard.press('Tab');assert(await page.evaluate(()=>!!document.activeElement.closest('[role="dialog"]')));await page.keyboard.press('Escape');await page.locator('[role="dialog"]').waitFor({state:'hidden'});
  await page.evaluate(()=>window.__availabilityQA.demo('maid',true));await audit('demo-maid-current');
  const demoBefore=await page.evaluate(()=>window.__availabilityQA.demoGet());await action('current-availability-day','[data-day="6"]').click();await action('request-current-availability').click();
  assert.deepEqual((await page.evaluate(()=>window.__availabilityQA.demoGet())).current,demoBefore.current);
  await page.evaluate(()=>window.__availabilityQA.demo('admin'));await audit('demo-admin-current');await action('decide-current-availability','[data-decision="rejected"]').click();assert.deepEqual((await page.evaluate(()=>window.__availabilityQA.demoGet())).current,demoBefore.current);
  await page.evaluate(()=>window.__availabilityQA.demo('maid'));await action('current-availability-day','[data-day="6"]').click();await action('request-current-availability').click();await page.evaluate(()=>window.__availabilityQA.demo('admin'));await action('decide-current-availability','[data-decision="approved"]').click();assert.equal((await page.evaluate(()=>window.__availabilityQA.demoGet())).current.version,demoBefore.current.version+1);
  await action('maid-detail').click();await action('back').click();await action('availability-week').waitFor();
  assert.deepEqual(errors,[]);assert.deepEqual(warnings,[]);assert.deepEqual(unexpected,[]);console.log('Availability UI PASS: request / reject / approve / initial request / duplicate lock / role guard / conflict / next-week submission / 4 widths / Back / keyboard / modal / console. Synthetic API only.');
 }
}finally{await browser.close();}
