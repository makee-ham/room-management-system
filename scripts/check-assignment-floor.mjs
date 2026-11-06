#!/usr/bin/env node
// Browser plugin not available. Synthetic demo fixtures; non-local requests are blocked.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import vm from 'node:vm';

const source=await readFile('WIREFRAME/index.html','utf8');
let loads={};
const core=source.slice(source.indexOf('      function assignmentPricingSnapshot('),source.indexOf('      function createRandomAssignment('));
assert(core.includes('function assignmentProximity('));
const sandbox={state:{assignments:{}},ROOMS:[],ROOM_TYPES:{standard:{rate:100,minutes:10}},orderedAssignmentsForMaid:id=>loads[id]||[],timeMinutes:value=>{const [h,m]=value.split(':').map(Number);return h*60+m;}};
const {proximity,trial,elevatorTrials}=vm.runInNewContext(core+';({proximity:assignmentProximity,trial:randomAssignmentTrial,elevatorTrials:assignmentElevatorTrials})',sandbox);
const item=(room,extra={})=>({id:room,room,type:'standard',elevatorSnapshot:'A',rateSnapshot:100,minutesSnapshot:10,...extra});
const maids=[{id:'a'},{id:'b'}],target=item('199');
const run=()=>trial(maids,[target],()=>0.5);
loads={a:[item('120')],b:[item('201')]};
assert.equal(run().plan['199'],'a','same floor wins over numeric room gap');
assert.equal(run().floorDistanceTotal,0);
assert.equal(proximity(target,[item('201'),item('120')]).roomDistance,79,'same-floor room is nearer within an elevator');
loads={a:[item('120',{rateSnapshot:200})],b:[item('201')]};
assert.equal(run().plan['199'],'a','same floor wins inside fee tolerance');
loads={a:[item('120',{elevatorSnapshot:'B'})],b:[item('201')]};
assert.equal(run().plan['199'],'b','same elevator wins over numeric room gap');
loads={a:[item('120')],b:[item('201')]};
assert.equal(trial([maids[1]],[target],()=>0.5).plan['199'],'b','only eligible maids are candidates');
assert.equal(trial(maids,[item('199',{accessStart:'17:55',requestDue:'18:00'})],()=>0.5).skipped,1,'demo time-window constraint remains');
assert.equal(proximity(item('1001'),[item('999')]).floorDistance,1,'four-digit rooms use all digits before the last two');
assert.equal(proximity(item('10'),[item('9')]).floorDistance,0,'legacy room numbers keep room-distance fallback');
assert.equal(proximity(target,[]).floorDistance,0,'empty route has no invented floor movement');
loads={a:[item('198',{elevatorSnapshot:'B'})],b:[item('200',{rateSnapshot:900})]};assert.equal(run().plan['199'],'b','elevator breaks a room-distance tie before floor/fees');
loads={a:[item('198',{rateSnapshot:900})],b:[item('200')]};assert.equal(run().plan['199'],'a','floor breaks a room/elevator tie before fees');
loads={a:[item('198',{rateSnapshot:900})],b:[item('198')]};assert.equal(run().plan['199'],'b','fees break equal location scores');
loads={a:[],b:[]};assert.equal(trial(maids,[item('350'),item('350',{id:'second'})],()=>0.5).assigned,0,'duplicate physical rooms are blocked');
loads={a:[item('350')],b:[]};assert.equal(trial(maids,[item('350',{id:'second'})],()=>0.5).assigned,0,'fixed room cannot be assigned again');
loads={a:[],b:[],c:[]};const clustered=trial([...maids,{id:'c'}],[117,118,349,350,755,756].map(n=>item(String(n))),()=>0.5);for(const [a,b] of [['117','118'],['349','350'],['755','756']])assert.equal(clustered.plan[a],clustered.plan[b]);
loads={a:[],b:[]};const dense=[101,102,103,104,105,106,131,132].map(n=>item(String(n)));const balanced=trial(maids,dense,()=>0.5,true);assert.equal(balanced.assigned,8);assert(balanced.payGap<=100);const groups=maids.map(m=>dense.filter(t=>balanced.plan[t.id]===m.id).map(t=>Number(t.room))).sort((a,b)=>Math.min(...a)-Math.min(...b));assert(Math.max(...groups[0])<Math.min(...groups[1]),'fee-balanced groups stay contiguous');
loads={a:[item('101'),item('102'),item('103')],b:[item('130')]};assert.equal(trial(maids,[item('104')],()=>0.5).plan['104'],'b','fee excess precedes proximity');
const balanceSource=source.slice(source.indexOf('      function assignmentFeeBalanceMarkup('),source.indexOf('      function renderAssignmentSummaryView('));
const balance=vm.runInNewContext(balanceSource+';assignmentFeeBalanceMarkup',{money:n=>n+'원',assignmentPayStats:totals=>({gap:Math.max(...totals)-Math.min(...totals)})});
assert.match(balance([{roomKey:'101',maidId:'a',fee:20000},{roomKey:'102',maidId:'a',fee:20000},{roomKey:'350',fee:900000},{roomKey:'350',fee:900000}],['a','b']),/총요금 차이 40000원 · 목표 20000원 이내 · 목표 초과/,'duplicate blocked fees cannot inflate the limit');
assert.match(balance([{maidId:'a',fee:null}],['a','b']),/확인 불가/,'missing API fee is not zero');
assert.match(balance([{maidId:'a',fee:20000,blocked:true},{maidId:'b',fee:20000}],['a','b']),/총요금 차이 0원/,'manual resolution of an old blocked preview counts actual ownership');
loads={a:[],b:[],c:[]};
const elevatorRooms=[item('556',{elevatorSnapshot:'C'}),item('639',{elevatorSnapshot:'C'}),item('623',{elevatorSnapshot:'A'}),item('720',{elevatorSnapshot:'A'}),item('657',{elevatorSnapshot:'B'}),item('662',{elevatorSnapshot:'B'})];
const zoned=elevatorTrials([...maids,{id:'c'}],elevatorRooms,()=>0.5).sort((a,b)=>a.payExcess-b.payExcess||a.zoneRankTotal-b.zoneRankTotal||a.floorDistanceTotal-b.floorDistanceTotal)[0];
assert.equal(zoned.assigned,6);assert.equal(zoned.payGap,0);assert.equal(zoned.zoneRankTotal,0);assert.equal(zoned.plan['556'],zoned.plan['639']);assert.notEqual(zoned.plan['556'],zoned.plan['623']);
console.log('[ok] one-room fee tolerance, contiguous boundaries, elevator/floor/room/fee precedence, cluster seeds, duplicate/fixed room guards, eligibility, demo deadlines and boundaries');

const {chromium}=createRequire(import.meta.url)('playwright'),origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177';
const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:390,height:900},locale:'ko-KR',serviceWorkers:'block',reducedMotion:'reduce'}),page=await context.newPage(),errors=[],external=[];
page.setDefaultTimeout(10000);
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&m.text()!=='Service Worker registration blocked by Playwright')errors.push(m.text());});
const boot='      void bootApplication();\n    })();';assert.equal(source.split(boot).length,2);
await page.route('**/*',async route=>{
  const url=new URL(route.request().url());
  if(url.origin!==origin){external.push(url.origin);return route.abort();}
  if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});
  if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,'      window.__floorAssignments=()=>structuredClone(state.assignments);\n'+boot)});
  return route.continue();
});
const action=(name,extra='')=>page.locator(`[data-action="${name}"]${extra}:visible`).first();
try{
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  await page.goto(origin+'/index.html?scenario=0&role=admin&view=today&date=2026-08-15');
  await page.locator('#login-id').fill('admin');await page.locator('#login-password').fill('admin1234');await page.locator('#login-form').press('Enter');await action('logout').waitFor();await page.locator('#toast-region .toast').waitFor({state:'hidden'});
  await action('nav','[data-view="cleaning"]').click();await action('cleaning-tab','[data-tab="assignment-tomorrow"]').click();
  assert.match(await page.title(),/CASTLE THE ART/);assert.match(page.url(),/^http:\/\/127\.0\.0\.1:/);
  const trigger=page.getByRole('button',{name:'랜덤 배정 기준 사용 안내',exact:true}),tip=page.locator('#info-tip-random-assignment-rule');
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:900});await page.waitForTimeout(230);await trigger.scrollIntoViewIfNeeded();await trigger.click();await tip.waitFor({state:'visible'});
    assert.match(await tip.innerText(),/가장 비싼 객실 1건 요금 이내/);assert.match(await tip.innerText(),/같은 엘리베이터 → 가까운 층 → 가까운 호수/);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`overflow at ${width}`);
    assert(await tip.evaluate(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&e.scrollWidth<=e.clientWidth+1;}),'tooltip fits viewport');
    assert.equal(await trigger.getAttribute('aria-describedby'),'info-tip-random-assignment-rule');
    if([390,1440].includes(width))await page.screenshot({path:`WIREFRAME/QA/screenshots/assignment-elevator-rule-${width}.png`});
    await page.keyboard.press('Escape');await tip.waitFor({state:'hidden'});assert(await trigger.evaluate(e=>document.activeElement===e));
    await page.keyboard.press('Enter');await tip.waitFor({state:'visible'});await page.keyboard.press('Escape');
    assert((await page.locator('#main-content').innerText()).length>100);
    assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);
  }
  const before=await page.evaluate(()=>__floorAssignments());
  await action('random-assignments').click();await action('undo-random-assignment').waitFor();
  const after=await page.evaluate(()=>__floorAssignments());
  for(const [id,row] of Object.entries(before))if(row.maidId)assert.deepEqual(after[id],row,'fixed assignment remains unchanged');
  assert(Object.values(after).some(row=>row.maidId&&row.status==='draft'));
  await page.locator('[data-assignment-fee-balance]').waitFor();assert.match(await page.locator('[data-assignment-fee-balance]').innerText(),/총요금 차이.*목표/);
  for(const width of [390,1440]){await page.setViewportSize({width,height:900});await page.locator('[data-assignment-fee-balance]').scrollIntoViewIfNeeded();await page.screenshot({path:`WIREFRAME/QA/screenshots/assignment-elevator-${width}.png`});}
  await action('undo-random-assignment').click();await action('random-assignments').waitFor();
  const restored=await page.evaluate(()=>__floorAssignments());
  for(const [id,row] of Object.entries(before))assert.deepEqual(restored[id],row,'undo restores previous assignment');
  await action('new-cleaning').click();await page.getByRole('dialog').waitFor();await page.goBack();await page.getByRole('dialog').waitFor({state:'hidden'});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log('[ok] 360/390/768/1440px tooltip, keyboard/Escape/focus, no overflow/console errors, draft/fixed preservation/undo, modal back');
}finally{await browser.close();}
