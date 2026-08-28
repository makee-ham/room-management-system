import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const browser=await chromium.launch({headless:true});
const errors=[];

async function assertHealthy(page,width){
  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,`${width}px main must not be blank`);
  const bodyText=await page.locator('body').innerText();
  assert.doesNotMatch(bodyText,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error|ReferenceError/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
}

async function verify(width,height){
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(`${width}px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${width}px console: ${message.text()}`);});
  await page.goto(base,{waitUntil:'networkidle'});
  await assertHealthy(page,width);

  const summary=page.locator('.catalog-summary-copy > strong');
  await summary.waitFor();
  assert.equal((await summary.innerText()).replace(/\s+/g,' ').trim(),'총 121개 객실');
  assert.ok(!(await page.locator('#main-content').innerText()).includes('상태 중복 집계'),'legacy duplicate-count wording must not be visible');

  const cards=page.locator('.room-card-v2');
  await cards.first().waitFor();
  const cardCount=await cards.count();
  assert.ok(cardCount>0,'room cards must render');
  assert.equal(await page.locator('.room-card-v2 .concept-status-panel').count(),cardCount,'every card must retain one primary-status panel');
  assert.equal(await page.locator('.room-card-v2 .concept-status-copy > strong').count(),cardCount,'every card must retain one primary status label');
  assert.equal(await page.locator('.room-card-v2 .concept-status-copy > span').count(),0,'visible reason text must be removed from every card');
  assert.equal(await page.locator('.room-card-v2 .room-status-subs').count(),0,'secondary cleaning-status chips must be removed from every card');

  const statusReport=await page.locator('.room-card-v2 .concept-status-copy').evaluateAll(nodes=>nodes.map(node=>({
    text:(node.textContent||'').replace(/\s+/g,' ').trim(),
    strong:(node.querySelector(':scope > strong')?.textContent||'').replace(/\s+/g,' ').trim(),
    childTags:[...node.children].map(child=>child.tagName),
  })));
  for(const row of statusReport){
    assert.equal(row.text,row.strong,'status panel must visually contain only the primary status');
    assert.deepEqual(row.childTags,['STRONG'],'status copy must have no secondary visible children');
    assert.match(row.strong,/^(투숙 중|청소 필요|배정 가능|배정 불가)$/);
  }

  assert.equal(await page.locator('.room-card-v2 .room-schedule-badges').count(),cardCount,'upper-right badge containers must remain on every card');
  assert.equal(await page.locator('.room-card-v2 .time-band').count(),cardCount,'check-in and check-out time bands must remain');
  assert.equal(await page.locator('.room-card-v2 .room-quick-actions').count(),cardCount,'quick actions must remain');
  assert.equal(await cards.first().locator('.room-quick-actions button').count(),4,'card quick actions must remain usable');

  await page.screenshot({path:`/tmp/admin-room-card-status-cleanup-${width}.png`,fullPage:false});
  await cards.first().getByRole('button',{name:'전체 상세'}).click();
  await page.locator('#main-content').waitFor();
  assert.match(await page.locator('#main-content').innerText(),/현재 상태|예약·입퇴실/,'room detail must still open from the card');
  await assertHealthy(page,width);
  await context.close();
}

await verify(1440,1000);
await verify(768,900);
await verify(390,844);
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Room catalog total-only heading and primary-status-only cards QA: passed');
