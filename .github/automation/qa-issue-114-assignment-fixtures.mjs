import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const origin='http://127.0.0.1:4173/index.html';
const browser=await chromium.launch({headless:true});
const runtimeErrors=[];

function normalize(value){return String(value||'').replace(/\s+/g,' ').trim();}

async function openAssignment(width,height,{date='2026-08-15',day='tomorrow'}={}){
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  page.on('pageerror',error=>runtimeErrors.push(`${width}px ${date}/${day} pageerror: ${error.stack||error.message}`));
  page.on('console',message=>{if(message.type()==='error')runtimeErrors.push(`${width}px ${date}/${day} console: ${message.text()}`);});
  await page.goto(`${origin}#scenario=0&role=admin&view=cleaning&date=${date}&cleaningDay=${day}&filter=all&type=all&q=`,{waitUntil:'networkidle'});
  await page.locator('.assignment-page').waitFor();
  return {context,page};
}

async function assertHealthy(page,width,label){
  const main=page.locator('#main-content');
  await main.waitFor();
  const text=normalize(await main.innerText());
  assert.ok(text.length>120,`${label}: main content must not be blank`);
  assert.doesNotMatch(text,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error|ReferenceError/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${label}: ${width}px document horizontal overflow: ${overflow}`);
}

async function workforceHeaders(page){
  return (await page.locator('.availability-matrix thead th').allInnerTexts()).map(normalize);
}

async function assignmentSelectState(page){
  return page.locator('select[data-control="assignment-maid"]').evaluateAll(selects=>Object.fromEntries(selects.map(select=>[
    select.dataset.target,
    {value:select.value,disabled:select.disabled}
  ])));
}

async function targetRow(page,targetId){
  const select=page.locator(`select[data-control="assignment-maid"][data-target="${targetId}"]`);
  await select.waitFor();
  return select.locator('xpath=ancestor::tr');
}

async function assertCurrentWeek(page,label){
  assert.deepEqual(await workforceHeaders(page),['메이드','월 10','화 11','수 12','목 13','금 14','토 15','일 16'],`${label}: workforce week must contain assignment date`);
  assert.equal(await page.locator('.availability-matrix tbody tr').count(),9,`${label}: all nine maids must render`);
}

async function tomorrowLargeAssignmentQa(width,height,{runRandom=false}={}){
  const {context,page}=await openAssignment(width,height,{date:'2026-08-15',day:'tomorrow'});
  const label=`tomorrow assignment ${width}px`;
  await assertHealthy(page,width,label);

  assert.match(normalize(await page.locator('.assignment-intro').innerText()),/내일 청소 배정.*8월 16일/);
  await assertCurrentWeek(page,label);
  assert.match(normalize(await page.locator('.assignment-panel').first().innerText()),/8월 10일.*8월 16일/);

  const sundayCells=page.locator('.availability-matrix tbody tr td:last-child');
  assert.equal(await sundayCells.count(),9);
  for(let index=0;index<9;index+=1){
    assert.match(normalize(await sundayCells.nth(index).innerText()),/✓/,`${label}: maid row ${index+1} must be available on Sunday`);
  }

  const targetSummary=page.locator('.assignment-summary > div').filter({hasText:'내일 청소 대상 객실'}).locator('strong');
  assert.equal(normalize(await targetSummary.innerText()),'36',`${label}: tomorrow must have 36 cleaning targets`);
  assert.equal(await page.locator('.assignment-table tbody tr').count(),36,`${label}: all target rows must remain visible`);
  assert.match(normalize(await page.locator('.assignment-random').innerText()),/근무 가능 9명/);

  const variedTargets={
    early:'sim-516-early-2026-08-16',
    late:'sim-556-late-2026-08-16',
    stayover:'sim-541-stayover-2026-08-16',
    manual:'sim-455-manual-2026-08-16',
    notified:'checkout-623-2026-08-16',
    started:'sim-540-started-2026-08-16',
    dataHold:'sim-762-hold-2026-08-16',
    stopped:'sim-608-stopped-2026-08-16',
    candle:'sim-211-candle-2026-08-16',
  };
  assert.match(normalize(await (await targetRow(page,variedTargets.early)).innerText()),/얼리 체크인|체크인 14:00|준비 마감 13:30/);
  assert.match(normalize(await (await targetRow(page,variedTargets.late)).innerText()),/레이트 체크아웃|체크아웃 13:00/);
  assert.match(normalize(await (await targetRow(page,variedTargets.stayover)).innerText()),/연박 청소/);
  assert.match(normalize(await (await targetRow(page,variedTargets.manual)).innerText()),/직접 등록/);
  assert.match(normalize(await (await targetRow(page,variedTargets.notified)).innerText()),/통보 완료/);
  assert.match(normalize(await (await targetRow(page,variedTargets.started)).innerText()),/이미 시작한 청소/);
  assert.match(normalize(await (await targetRow(page,variedTargets.dataHold)).innerText()),/현재 투숙 상태 확인 필요/);
  assert.match(normalize(await (await targetRow(page,variedTargets.stopped)).innerText()),/운영 중지/);
  assert.match(normalize(await (await targetRow(page,variedTargets.candle)).innerText()),/촛불 1개 회수 후 배정 가능/);

  const notifiedSelect=page.locator(`select[data-target="${variedTargets.notified}"]`);
  const startedSelect=page.locator(`select[data-target="${variedTargets.started}"]`);
  assert.equal(await notifiedSelect.inputValue(),'m2','notified assignment must preserve its maid');
  assert.equal(await startedSelect.inputValue(),'m4','started assignment must preserve its maid');
  for(const targetId of [variedTargets.started,variedTargets.dataHold,variedTargets.stopped,variedTargets.candle]){
    assert.equal(await page.locator(`select[data-target="${targetId}"]`).isDisabled(),true,`${targetId} must be locked`);
  }

  if(runRandom){
    const beforeSelects=await assignmentSelectState(page);
    const beforeDurable=await page.evaluate(()=>window.__CASTLE_TEST__?.snapshot?.()||null);
    const protectedIds=[variedTargets.notified,variedTargets.started,variedTargets.dataHold,variedTargets.stopped,variedTargets.candle];
    const protectedBefore=Object.fromEntries(protectedIds.map(id=>[id,beforeSelects[id]]));

    const randomButton=page.locator('[data-action="random-assignments"]').first();
    await randomButton.waitFor();
    assert.equal(await randomButton.isEnabled(),true,'random assignment must be enabled');
    await randomButton.click();
    await page.locator('[data-action="undo-random-assignment"]').waitFor();

    const afterRandom=await assignmentSelectState(page);
    const newlyAssigned=Object.keys(beforeSelects).filter(id=>!beforeSelects[id].value&&afterRandom[id]?.value);
    assert.ok(newlyAssigned.length>=20,`random draft must assign a substantial set of rooms; assigned ${newlyAssigned.length}`);
    assert.equal(await page.locator('.maid-order-lane').count(),9,'random draft must show all nine maid lanes');
    assert.match(normalize(await page.locator('.assignment-random').innerText()),/초안 배정 \d+객실/);
    for(const id of protectedIds)assert.deepEqual(afterRandom[id],protectedBefore[id],`${id} must remain unchanged by random assignment`);

    await page.locator('[data-action="undo-random-assignment"]').click();
    await page.waitForFunction(()=>!document.querySelector('[data-action="undo-random-assignment"]'));
    const afterUndo=await assignmentSelectState(page);
    assert.deepEqual(afterUndo,beforeSelects,'undo must restore every assignment select and lock state exactly');
    const afterDurable=await page.evaluate(()=>window.__CASTLE_TEST__?.snapshot?.()||null);
    if(beforeDurable&&afterDurable)assert.deepEqual(afterDurable,beforeDurable,'random draft and undo must not mutate durable ledgers');
  }

  await page.screenshot({path:`/tmp/issue-114-tomorrow-${width}.png`,fullPage:false});
  await assertHealthy(page,width,label);
  await context.close();
}

async function weekSwitchQa(){
  const today=await openAssignment(768,900,{date:'2026-08-15',day:'today'});
  await assertHealthy(today.page,768,'today assignment week');
  await assertCurrentWeek(today.page,'today assignment week');
  assert.match(normalize(await today.page.locator('.assignment-intro').innerText()),/오늘 청소 배정.*8월 15일/);
  await today.context.close();

  const nextWeek=await openAssignment(768,900,{date:'2026-08-17',day:'today'});
  await assertHealthy(nextWeek.page,768,'next-week assignment');
  assert.deepEqual(await workforceHeaders(nextWeek.page),['메이드','월 17','화 18','수 19','목 20','금 21','토 22','일 23']);
  assert.match(normalize(await nextWeek.page.locator('.assignment-panel').first().innerText()),/8월 17일.*8월 23일/);
  await nextWeek.context.close();
}

try{
  await tomorrowLargeAssignmentQa(1440,1000,{runRandom:true});
  await tomorrowLargeAssignmentQa(768,900);
  await tomorrowLargeAssignmentQa(390,844);
  await weekSwitchQa();
}finally{
  await browser.close();
}

assert.deepEqual(runtimeErrors,[],runtimeErrors.join('\n'));
console.log('Issue #114 assignment week and varied random-assignment fixture QA: passed');
