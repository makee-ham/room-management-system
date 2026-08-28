import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=today&date=2026-08-15&filter=all&type=all&q=';
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

  const main=page.locator('#main-content');
  const summary=main.locator('[data-admin-home-section="room-summary"]');
  const actions=main.locator('[data-admin-home-section="cleaning-actions"]');
  const costSection=main.locator('[data-admin-home-section="cleaning-cost"]');
  await summary.waitFor();
  await actions.waitFor();
  await costSection.waitFor();

  const order=await page.evaluate(()=>{
    const summary=document.querySelector('[data-admin-home-section="room-summary"]');
    const actions=document.querySelector('[data-admin-home-section="cleaning-actions"]');
    const cost=document.querySelector('[data-admin-home-section="cleaning-cost"]');
    const precedes=(left,right)=>!!(left.compareDocumentPosition(right)&Node.DOCUMENT_POSITION_FOLLOWING);
    return {summaryBeforeActions:precedes(summary,actions),actionsBeforeCost:precedes(actions,cost)};
  });
  assert.equal(order.summaryBeforeActions,true,'room summary must precede cleaning actions');
  assert.equal(order.actionsBeforeCost,true,'cleaning actions must precede cleaning-cost shortcut');

  assert.equal(await summary.getByRole('heading',{name:'오늘 객실 요약'}).count(),1);
  const actionButtons=actions.locator(':scope > .accordion > button');
  assert.equal(await actionButtons.count(),2,'home must retain exactly two cleaning work accordions');
  assert.match(await actionButtons.nth(0).innerText(),/오늘 청소 배정/);
  assert.match(await actionButtons.nth(1).innerText(),/청소 검수/);

  const shortcut=costSection.locator('[data-dashboard-cost-shortcut="today"]');
  await shortcut.waitFor();
  const shortcutText=(await shortcut.innerText()).replace(/\s+/g,' ').trim();
  assert.match(shortcutText,/청소비 예상 지출/);
  assert.match(shortcutText,/오늘 \d+건/);
  assert.match(shortcutText,/\d{1,3}(,\d{3})*원/);
  assert.match(shortcutText,/주급 정산/);
  for(const verbose of ['이번 주 예상','현재 확정','검수 대기 최대','검수 요청 금액 최대','미시작','앱은 실제 송금을 실행하지 않습니다','수익 귀속']){
    assert.ok(!shortcutText.includes(verbose),`compact shortcut still shows verbose copy: ${verbose}`);
  }
  const shortcutHeight=await shortcut.evaluate(node=>Math.round(node.getBoundingClientRect().height));
  assert.ok(shortcutHeight<=80,`cleaning-cost shortcut must remain compact, got ${shortcutHeight}px`);
  const ariaLabel=await shortcut.getAttribute('aria-label');
  assert.match(ariaLabel,/현재 확정/,'detailed cost context must remain available to assistive technology');
  assert.match(ariaLabel,/주급 정산 화면 열기/);

  await page.screenshot({path:`/tmp/admin-home-priority-cost-${width}.png`,fullPage:false});
  await shortcut.click();
  await page.waitForFunction(()=>location.hash.includes('view=maids')||document.querySelector('#main-content')?.textContent?.includes('주급 정산'));
  const payrollTab=page.getByRole('tab',{name:/주급 정산/});
  await payrollTab.waitFor();
  assert.equal(await payrollTab.getAttribute('aria-selected'),'true','cost shortcut must open the payroll tab');
  assert.match(await main.innerText(),/주급 정산/);
  await assertHealthy(page,width);
  await context.close();
}

await verify(1440,1000);
await verify(768,900);
await verify(390,844);
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Admin-home priority and compact cleaning-cost shortcut QA: passed');
