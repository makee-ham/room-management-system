#!/usr/bin/env node
// Local API fixtures only. Browser plugin unavailable; use bundled Playwright.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const id=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const accounts=[{profileId:id(1),role:'admin',displayName:'QA 관리자',status:'active'},{profileId:id(2),role:'maid',displayName:'QA 메이드',status:'active'}];
const room={id:id(3),roomNumber:'211',roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:1,occupied:false,cleaningRequired:true,candleCount:0,pinSyncStatus:'verified',allocationBlocked:true,allocationReady:false,reasonCodes:['CLEANING_REQUIRED'],primaryDisplayStatus:'CLEANING_REQUIRED'};
const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul'}).format(new Date());
const mondayDate=new Date(`${date}T00:00:00Z`);mondayDate.setUTCDate(mondayDate.getUTCDate()-(mondayDate.getUTCDay()+6)%7);
const monday=mondayDate.toISOString().slice(0,10),prior=new Date(mondayDate.getTime()-7*86400000).toISOString().slice(0,10);
const submission={id:id(4),attemptId:id(5),version:1,currentRevision:1,current:true,status:'submitted',submittedBy:id(2),submittedAt:`${date}T12:00:00+09:00`,photoCount:2,candleCount:0,bombReport:null,bombDecision:null,reviewContext:{roomNumber:'211',maidDisplayName:'QA 메이드',cleaningKind:'checkout'},photos:[1,2].map(n=>({photoId:id(n+5),label:`사진 ${n}`,required:true,photoVersion:1}))};
function cycle(week){const amount=week===monday?40000:28000;return {cycleId:null,maidProfileId:id(2),weekStart:week,status:'open',version:0,lockedAmount:null,totalAmount:amount,accrualAmount:amount,expectedAmount:amount+16000,pendingAmount:16000,pendingCount:1,payableAmount:amount,adjustmentAmount:0,carryInAmount:0,carryOutAmount:0,lateEarningAmount:0,lateEarningCount:0,itemCount:2,adjustmentCount:0,items:[],lateEarnings:[],offsetSettled:false};}
const source=await readFile(resolve('WIREFRAME/index.html'),'utf8');
const hook=`window.__navQA={setup:async(role='admin')=>{
  LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});
  state.remote=initialRemoteState();const actor=${JSON.stringify(accounts)}.find(item=>item.role===role);state.role=role;state.remote.auth={...state.remote.auth,status:'authenticated',user:actor,session:{accessToken:'NAV-TOKEN-PRIVATE',refreshToken:'NAV-REFRESH-PRIVATE',expiresAt:Date.now()+3600000}};
  const now=new Date().toISOString();state.remote.accounts={...state.remote.accounts,status:'ready',items:${JSON.stringify(accounts)},lastSuccessAt:now};state.remote.rooms={...state.remote.rooms,status:'ready',items:[${JSON.stringify(room)}],lastSuccessAt:now};
  state.remote.cleaning={...state.remote.cleaning,status:'ready',inspections:[${JSON.stringify(submission)}],lastSuccessAt:now};state.todaySections.inspection=true;state.cleaningTab='assignment-tomorrow';state.liveView=requestedLiveView(role)||defaultLiveView(role);applyLiveLocationRoute();syncAuthState(state);render();await loadLiveViewData();
},get:()=>({view:state.liveView,tab:state.cleaningTab,maidTab:state.adminMaidTab,payroll:state.remote.payroll,detail:!!cleaningState().inspectionDetail,restoring:restoringHistory}),payroll:week=>loadLivePayroll({weekStart:week}),fresh:()=>{state.remote.payroll.lastSuccessAt='2000-01-01T00:00:00Z';},modal:()=>showModal({title:'정보',body:'<p>PRIVATE-MODAL-CONTENT</p>'})};`;
const html=source.replace('\n      void bootApplication();',hook);
const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
const testPhoto=Buffer.from(await page.evaluate(()=>{const canvas=document.createElement('canvas');canvas.width=640;canvas.height=400;const ctx=canvas.getContext('2d');ctx.fillStyle='#edf2f4';ctx.fillRect(0,0,640,400);['#167c65','#cf3445','#1d607f'].forEach((color,index)=>{ctx.fillStyle=color;ctx.fillRect(40+index*195,40,170,245);});ctx.fillStyle='#162b36';ctx.font='22px sans-serif';ctx.fillText('QA FIXTURE / NOT A ROOM PHOTO',40,345);return canvas.toDataURL('image/png').split(',')[1];}),'base64');
page.setDefaultTimeout(10000);
const errors=[],warnings=[],requests=[],missing=[];
let delayedWeek=null,releaseDelay=null,invalidPayroll=false,approved=false,inspectionPages=0;
page.on('pageerror',error=>errors.push(error.message));page.on('console',message=>{if(['warning','error'].includes(message.type())&&!message.text().startsWith('Failed to load resource:'))warnings.push(message.text());});
await page.route('**/index.html*',route=>route.fulfill({contentType:'text/html',body:html}));
await page.route('**/favicon.ico',route=>route.fulfill({status:204,body:''}));
await page.route(`${api}/**`,async route=>{
  const url=new URL(route.request().url()),path=url.pathname.replace('/functions/v1/api','');requests.push(path+url.search);
  const json=data=>route.fulfill({contentType:'application/json',body:JSON.stringify(data)});
  if(path===`/v1/inspections/${submission.id}/approve`&&route.request().method()==='POST'){approved=true;return json({inspection:{submissionId:submission.id,decision:'approved'}});}
  assert.equal(route.request().method(),'GET','Only the explicit fixture approval may mutate');
  if(path==='/v1/payroll'){const week=url.searchParams.get('weekStart');if(week===delayedWeek)await new Promise(resolve=>{releaseDelay=resolve;});return json({payroll:[{...cycle(week),...(invalidPayroll?{totalAmount:null}:{})}],nextCursor:null});}
  if(path==='/v1/payroll/entries')return json({entries:[],nextCursor:null});
  if(path==='/v1/payroll/remittance-marker')return json({maidProfileId:id(2),weekStart:url.searchParams.get('weekStart'),marked:false,version:0,basisFingerprint:'a'.repeat(64),canSet:true,canClear:false,canReconfirm:false,needsReconfirmation:false});
  if(path==='/v1/payroll/work-details')return json({maidProfileId:id(2),weekStart:url.searchParams.get('weekStart'),kind:url.searchParams.get('kind'),summary:{},entries:[],nextCursor:null});
  if(path.endsWith('/supplemental-room-issues'))return json({source:{sourceSubmissionId:submission.id,sourceStatus:'approved',ownership:'original_performer'},reports:[]});
  if(path==='/v1/notifications')return json({notifications:[],nextCursor:null});
  if(path==='/v1/accounts')return json({accounts});
  if(path==='/v1/rooms'){const serviceDate=url.searchParams.get('serviceDate')||date;return json({rooms:[{...room,serviceDate,projectionMode:serviceDate===date?'LIVE':serviceDate<date?'PAST_END_OF_DAY':'FUTURE_START_OF_DAY',detailConditionCodes:['VACANT']}]});}
  if(path===`/v1/rooms/${room.id}`)return json({room});
  if(path==='/v1/reservations')return json({reservations:[],nextCursor:null});
  if(path==='/v1/room-types')return json({items:[]});
  if(path==='/v1/assignments')return json({assignments:[]});
  if(path==='/v1/assignment-change-requests')return json({requests:[],nextCursor:null});
  if(path==='/v1/assignments/commit-impact')return json({impact:{serviceDate:date,committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}});
  if(path==='/v1/inspections'){inspectionPages++;return json({submissions:approved||url.searchParams.has('cursor')?[]:[submission],nextCursor:approved||url.searchParams.has('cursor')?null:'QA-NEXT-PAGE'});}
  if(path===`/v1/inspections/${submission.id}`)return json({submission});
  if(path===`/v1/cleaning-history/${submission.id}`)return json({submission:{...submission,status:'approved'}});
  if(path.startsWith('/v1/photos/'))return route.fulfill({contentType:'image/png',body:testPhoto});
  if(path.startsWith('/v1/availability'))return json({availabilities:[],availability:null,requests:[]});
  if(path==='/v1/work-history')return json({weekStart:monday,items:[],nextCursor:null});
  if(path==='/v1/complaints')return json({complaints:[],nextCursor:null});
  if(path==='/v1/cleaning-history')return json({date,fromDate:date,toDate:date,items:[{attemptId:id(5),submissionId:submission.id,performerProfileId:id(2),performerDisplayName:'QA 메이드',roomNumber:'211',roomTypeName:'스탠다드',cleaningKind:'checkout',fieldCompletedAt:`${date}T12:00:00+09:00`,serviceDate:date,inspectionStatus:'approved',mediaAvailability:'available',photoCount:2,baseFeeSnapshot:16000,earningTotalAmount:16000},{attemptId:id(50),submissionId:id(51),performerProfileId:id(52),performerDisplayName:'다른 QA 메이드',roomNumber:'999',cleaningKind:'checkout',fieldCompletedAt:`${date}T12:00:00+09:00`,serviceDate:date,inspectionStatus:'approved',mediaAvailability:'available'}],nextCursor:null});
  missing.push(path);return route.fulfill({status:404,contentType:'application/json',body:'{}'});
});
const click=action=>page.locator(`[data-action="${action}"]`).filter({visible:true}).first().click();
async function ready(){await page.waitForFunction(()=>!window.__navQA.get().restoring&&window.__navQA.get().payroll.status!=='loading');}
async function stateIs(view,tab){await page.waitForFunction(({view,tab})=>{const s=window.__navQA.get();return !s.restoring&&s.view===view&&(!tab||s.tab===tab||s.maidTab===tab);},{view,tab});}
async function responsive(name){for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${name}: ${width}px overflow`);}await page.setViewportSize({width:390,height:900});}
try{
  await mkdir(resolve('WIREFRAME/QA/screenshots'),{recursive:true});
  await page.goto(`${origin}/index.html`);await page.evaluate(()=>window.__navQA.setup());
  assert.deepEqual(await page.locator('[data-admin-home-section="cleaning-actions"] .accordion-toggle').evaluateAll(elements=>elements.map(el=>el.dataset.key)),['inspection','assignment']);
  await responsive('home');await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-home-tomorrow-390.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-home-tomorrow-1440.png'),fullPage:true});await page.setViewportSize({width:390,height:900});
  await click('go-inspection');await stateIs('cleaning','inspection');assert.match(page.url(),/tab=inspection/);
  await page.goBack();await stateIs('today');await click('go-cleaning-assignment');await stateIs('cleaning','assignment-tomorrow');assert.match(page.url(),/tab=assignment-tomorrow/);
  await page.goBack();await stateIs('today');await page.goForward();await stateIs('cleaning','assignment-tomorrow');
  await page.locator('[data-action="cleaning-tab"][data-tab="assignment-today"]').click();await stateIs('cleaning','assignment-today');
  await page.goBack();await stateIs('cleaning','assignment-tomorrow');
  const tomorrow=new Date(new Date(`${date}T00:00:00Z`).getTime()+86400000).toISOString().slice(0,10);
  assert.equal(new URL(requests.filter(path=>path.startsWith('/v1/assignments?')).at(-1),'https://qa.test').searchParams.get('serviceDate'),tomorrow);
  await page.locator('[data-action="cleaning-tab"][data-tab="inspection"]').click();await stateIs('cleaning','inspection');
  await click('cleaning-inspection-open');await page.waitForFunction(()=>window.__navQA.get().detail);
  await responsive('inspection');await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-inspection-gallery-390.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-inspection-gallery-1440.png'),fullPage:true});await page.setViewportSize({width:390,height:900});
  const beforeImages=requests.filter(path=>path.startsWith('/v1/photos/')).length;
  await click('live-inspection-photo');await page.getByRole('dialog').waitFor();
  assert(await page.locator('.photo-viewer-visual img').evaluate(img=>img.complete&&img.naturalWidth===640&&img.naturalHeight===400));
  for(let i=0;i<8;i++){await page.keyboard.press('Tab');assert(await page.evaluate(()=>!!document.activeElement.closest('[role="dialog"]')),'Focus stays inside the photo dialog');}
  await page.getByRole('button',{name:'다음 사진',exact:true}).click();assert.match(await page.locator('#modal-title').innerText(),/2 \/ 2/);
  await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-inspection-photo-viewer-390.png'),fullPage:true});
  await page.goBack();await page.getByRole('dialog').waitFor({state:'hidden'});assert.equal(await page.evaluate(()=>window.__navQA.get().detail),true);
  assert.equal(requests.filter(path=>path.startsWith('/v1/photos/')).length,beforeImages,'Modal close preserves valid blob URLs');
  await click('back');await page.waitForFunction(()=>!window.__navQA.get().detail&&!window.__navQA.get().restoring);await stateIs('cleaning','inspection');
  await page.locator('[data-action="nav"][data-view="maids"]:visible').first().click();
  await click('live-maid-detail');await page.locator('[data-live-cleaning-history]').waitFor();
  assert.equal(await page.locator('[data-live-cleaning-history]').count(),1,'Maid detail never includes another performer');
  await responsive('maid detail');await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-maid-detail-history-390.png'),fullPage:true});
  await click('live-cleaning-history-detail');await page.waitForFunction(()=>window.__navQA.get().detail);assert.equal(await page.locator('[data-action="cleaning-inspection-approve"]').count(),0);
  await page.goBack();await page.locator('[data-action="live-maid-work-history"]').waitFor();
  await page.goBack();await page.locator('[data-action="live-maid-detail"]').waitFor();
  await page.locator('[data-action="admin-maid-tab"][data-tab="pay"]').click();await ready();assert.equal(await page.evaluate(()=>window.__navQA.get().payroll.weekStart),monday);
  assert.match(await page.locator('.pay-hero').innerText(),/40,000/);assert.equal(await page.locator('[data-action="live-payroll-start-review"]').count(),0);
  await responsive('payroll');await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-weekly-payroll-current-390.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/live-weekly-payroll-current-1440.png'),fullPage:true});await page.setViewportSize({width:390,height:900});
  assert(await page.locator('.pay-week-toolbar button,.inspection-photo').evaluateAll(elements=>elements.every(element=>{const r=element.getBoundingClientRect();return r.width>=44&&r.height>=44;})));
  await page.locator('[data-action="live-payroll-week-shift"][data-offset="-7"]').click();await ready();assert.equal(await page.evaluate(()=>window.__navQA.get().payroll.weekStart),prior);assert.match(await page.locator('.pay-hero').innerText(),/28,000/);
  await click('live-payroll-detail');await page.waitForFunction(()=>!!window.__navQA.get().payroll.detail);await page.goBack();await page.waitForFunction(()=>!window.__navQA.get().payroll.detail&&!window.__navQA.get().restoring);
  await page.goBack();await ready();assert.equal(await page.evaluate(()=>window.__navQA.get().payroll.weekStart),monday);
  // Old responses must not overwrite a newer selected week.
  delayedWeek=prior;await page.evaluate(week=>{void window.__navQA.payroll(week);},prior);
  for(let n=0;n<500&&!releaseDelay;n++)await new Promise(resolve=>setTimeout(resolve,10));assert(releaseDelay,'Delayed payroll request started');
  await page.evaluate(week=>window.__navQA.payroll(week),monday);releaseDelay();delayedWeek=null;
  await ready();await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>window.__navQA.get().payroll.weekStart),monday);
  invalidPayroll=true;await page.evaluate(week=>window.__navQA.payroll(week),monday);assert.equal(await page.locator('.pay-hero').count(),0,'Incomplete API amount must not be shown as zero');invalidPayroll=false;await click('refresh-live-payroll');await ready();
  await page.evaluate(()=>window.__navQA.modal());
  const stored=await page.evaluate(()=>JSON.stringify(history.state));assert(!/PRIVATE-MODAL|NAV-TOKEN|NAV-REFRESH|blob:|<img/.test(stored));
  await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});
  const payrollReadsBefore=requests.filter(path=>path.startsWith('/v1/payroll?')).length;
  await page.locator('[data-action="nav"][data-view="today"]:visible').first().click();await click('go-inspection');await click('cleaning-inspection-open');await page.getByRole('button',{name:'전체 승인',exact:true}).click();await page.waitForFunction(()=>!window.__navQA.get().detail);
  await page.locator('[data-action="nav"][data-view="maids"]:visible').first().click();await page.locator('[data-action="admin-maid-tab"][data-tab="pay"]').click();await ready();
  assert(requests.filter(path=>path.startsWith('/v1/payroll?')).length>payrollReadsBefore,'Approval invalidates payroll cache');
  assert(inspectionPages>1&&requests.some(path=>path.includes('cursor=QA-NEXT-PAGE')),'Inspection cursor pages are consumed');
  await page.goto(`${origin}/index.html?view=cleaning&tab=inspection`);await page.evaluate(()=>window.__navQA.setup());await stateIs('cleaning','inspection');
  await page.goto(`${origin}/index.html?view=cleaning&tab=inspection`);await page.evaluate(()=>window.__navQA.setup('maid'));await stateIs('my');assert.equal(await page.locator('[data-action="cleaning-inspection-open"]').count(),0);
  await page.locator('[data-action="nav"][data-view="pay"]:visible').first().click();await ready();assert.match(await page.locator('.pay-hero').innerText(),/40,000/);await responsive('maid payroll');await page.goBack();await stateIs('my');
  assert.deepEqual(missing,[]);assert.deepEqual(errors,[]);assert.deepEqual(warnings,[]);
  console.log('[ok] Home exact destinations, tabs, page/modal Back and Forward, direct links and maid role guard');
  console.log('[ok] Current-week payroll, prior week, detail return, stale-response guard, missing estimate not fabricated');
  console.log('[ok] Image enlargement, next image, blob lifetime, safe history, keyboard Escape');
  console.log('[ok] Maid detail scoped history and photo Back; inspection pagination; approval refreshes payroll');
  console.log('[ok] 360/390/768/1440px, no overflow or console/page errors');
  console.log(`Chromium ${await browser.version()}; all API traffic intercepted locally; no production writes.`);
}catch(error){console.error({errors,warnings,missing});await page.screenshot({path:'/tmp/live-navigation-failure.png',fullPage:true});throw error;}
finally{releaseDelay?.();await browser.close();}
