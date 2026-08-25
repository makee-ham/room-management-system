import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const origin='http://127.0.0.1:4173/index.html';
const adminUrl=`${origin}#scenario=0&role=admin&view=today&date=2026-08-15&filter=all&type=all&q=`;
const maidPayUrl=`${origin}#scenario=0&role=maid&view=pay&date=2026-08-15&filter=all&type=all&q=`;
const browser=await chromium.launch({headless:true});
const errors=[];

async function healthy(page,width){
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

  await page.goto(adminUrl,{waitUntil:'networkidle'});
  await healthy(page,width);
  assert.equal(await page.evaluate(()=>typeof window.__CASTLE_NOTIFICATION_QA__),'undefined','QA mutation bridge must not ship');
  const homeList=page.locator('#main-content .accordion-list').first();
  assert.equal(await homeList.locator(':scope > .accordion').count(),2,'admin home must retain two work sections');
  assert.equal(await homeList.getByRole('button',{name:/오늘 청소 배정/}).count(),1);
  assert.equal(await homeList.getByRole('button',{name:/청소 검수/}).count(),1);

  const bell=page.getByRole('button',{name:/알림함 열기/});
  await bell.click();
  let dialog=page.getByRole('dialog');
  await dialog.waitFor();
  assert.equal(await dialog.getByRole('heading',{name:'관리자 알림'}).count(),1);
  assert.ok(await dialog.locator('[data-notification-card]').count()>=4,'admin notifications must render');
  await dialog.getByRole('button',{name:/639호 청소 검수 요청/}).click();
  await page.waitForFunction(()=>location.hash.includes('view=cleaning'));
  const inspectionTab=page.getByRole('tab',{name:/검수 대기/});
  await inspectionTab.waitFor();
  assert.equal(await inspectionTab.getAttribute('aria-selected'),'true');
  await healthy(page,width);

  await page.goto(maidPayUrl,{waitUntil:'networkidle'});
  await healthy(page,width);
  const payText=await page.locator('#main-content').innerText();
  assert.match(payText,/이번 주/);
  assert.match(payText,/지금까지 주급 내역/);
  assert.match(payText,/청소 내역 \d+건/,'maid pay must show the saved week task ledger count');
  const disclosure=page.locator('[data-action="toggle-maid-pay-week"]').first();
  await disclosure.waitFor();
  await disclosure.click();
  assert.equal(await disclosure.getAttribute('aria-expanded'),'true','maid pay week details must expand');
  assert.ok(await page.locator('.maid-pay-task').count()>=1,'maid pay ledger task rows must render');
  const expandedPayText=await page.locator('#main-content').innerText();
  assert.match(expandedPayText,/\d{3}호 · (퇴실|연박) 청소/,'expanded ledger must retain room-level cleaning entries');
  assert.match(expandedPayText,/기본 [\d,]+원 .* = [\d,]+원/,'expanded ledger must retain room-level pay calculations');

  await page.getByRole('button',{name:/알림함 열기/}).click();
  dialog=page.getByRole('dialog');
  await dialog.waitFor();
  assert.equal(await dialog.getByRole('heading',{name:'내 알림'}).count(),1);
  assert.match(await dialog.innerText(),/업데이트 2건/);
  assert.doesNotMatch(await dialog.innerText(),/639호 청소 검수 요청/);

  await page.screenshot({path:`/tmp/notification-maid-pay-${width}.png`,fullPage:false});
  await healthy(page,width);
  await context.close();
}

await verify(1440,1000);
await verify(390,844);
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Notification center and maid-pay regression QA: passed');
