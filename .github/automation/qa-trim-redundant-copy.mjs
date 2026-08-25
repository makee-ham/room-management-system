import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const origin='http://127.0.0.1:4173/index.html';
const homeUrl=`${origin}#scenario=0&role=admin&view=today&date=2026-08-15&filter=all&type=all&q=`;
const maidsUrl=`${origin}#scenario=0&role=admin&view=maids&date=2026-08-15&filter=all&type=all&q=`;
const removedPhrases=[
  '현재 점유 · 회색',
  '퇴실·연박 청소 · 주황',
  '공실·준비 완료 · 초록',
  '촛불·차단 특이사항 등 · 빨강',
  '네 가지 주 상태로만 계산 · 데모',
  '주급 자동 차감 없음 · 삭제 이력 보존',
];
const browser=await chromium.launch({headless:true});
const errors=[];

async function assertHealthy(page,width){
  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,`${width}px main must not be blank`);
  assert.doesNotMatch(await page.locator('body').innerText(),/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error|ReferenceError/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
}

async function verify(width,height){
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(`${width}px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${width}px console: ${message.text()}`);});

  await page.goto(homeUrl,{waitUntil:'networkidle'});
  await assertHealthy(page,width);
  const summary=page.locator('.today-summary');
  await summary.waitFor();
  assert.equal(await summary.locator('.metric-card').count(),4,'today summary must retain four operational cards');
  assert.equal(await summary.locator('small').count(),0,'today summary must not render explanatory third lines');
  const summaryText=(await summary.innerText()).replace(/\s+/g,' ').trim();
  for(const label of ['투숙 중','청소 필요','배정 가능','배정 불가'])assert.match(summaryText,new RegExp(label));
  for(const phrase of removedPhrases)assert.ok(!summaryText.includes(phrase),`summary still shows redundant copy: ${phrase}`);
  assert.equal(await page.locator('#summary-title').locator('xpath=following-sibling::p').count(),0,'summary heading must not render a redundant subtitle');
  const summaryHeights=await summary.locator('.metric-card').evaluateAll(cards=>cards.map(card=>Math.round(card.getBoundingClientRect().height)));
  assert.ok(summaryHeights.every(height=>height<=105),`summary cards should be compact after copy removal: ${summaryHeights.join(',')}`);

  await page.goto(maidsUrl,{waitUntil:'networkidle'});
  await assertHealthy(page,width);
  const complaintsTab=page.locator('[data-action="admin-maid-tab"][data-tab="complaints"]');
  await complaintsTab.waitFor();
  await complaintsTab.click();
  const firstDetail=page.locator('[data-action="complaint-detail"]').first();
  await firstDetail.waitFor();
  await firstDetail.click();
  await page.locator('.detail-head').waitFor();
  const heading=(await page.locator('.detail-title h2').innerText()).trim();
  assert.equal(heading,'김민지1 벌점','complaint heading must keep only maid and record type without a middle dot');
  assert.equal(await page.locator('.detail-title p').count(),0,'empty complaint subtitle must not leave a blank paragraph');
  const detailText=await page.locator('#main-content').innerText();
  for(const phrase of removedPhrases)assert.ok(!detailText.includes(phrase),`complaint detail still shows redundant copy: ${phrase}`);
  assert.match(detailText,/주급 영향\s*자동 차감 없음/,'the one operational payroll-impact fact must remain');
  assert.match(detailText,/감사 이력/,'audit history must remain available');

  await page.screenshot({path:`/tmp/essential-copy-only-${width}.png`,fullPage:false});
  await assertHealthy(page,width);
  await context.close();
}

await verify(1440,1000);
await verify(390,844);
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Essential-copy-only rendered QA: passed');
