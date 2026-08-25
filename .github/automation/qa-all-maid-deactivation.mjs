import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=maids&date=2026-08-15&filter=all&type=all&q=';
const maidIds=['m1','m2','m3','m4','m5','m6','m7','m8','m9'];
const browser=await chromium.launch({headless:true});
const errors=[];

async function assertHealthy(page,width){
  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,`${width}px main must not be blank`);
  const text=await page.locator('body').innerText();
  assert.doesNotMatch(text,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error|ReferenceError/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
}

async function openMaidDetail(page,maidId){
  if(!location.href?.includes('noop')){}
  if(!page.url().includes('view=maids')||page.url().includes('detail=')){
    await page.goto(base,{waitUntil:'networkidle'});
  }
  const card=page.locator(`[data-maid-card="${maidId}"]`);
  await card.waitFor();
  await card.locator('[data-action="maid-detail"]').click();
  await page.waitForFunction(id=>location.hash.includes(`detail=maid%3A${id}`)||location.hash.includes(`detail=maid:${id}`),maidId);
  await page.locator(`[data-maid-account-management="${maidId}"]`).waitFor();
}

async function verifyAllDetails(page){
  for(const maidId of maidIds){
    await openMaidDetail(page,maidId);
    const account=page.locator(`[data-maid-account-management="${maidId}"]`);
    const history=page.locator(`[data-maid-history="${maidId}"]`);
    assert.equal(await account.count(),1,`${maidId} must have one account-management section`);
    assert.equal(await history.count(),1,`${maidId} must have one history section`);
    assert.equal(await account.locator(`[data-action="deactivate-maid-v2"][data-id="${maidId}"]`).count(),1,`${maidId} must have a deactivation button`);
    const placement=await page.evaluate(id=>{
      const history=document.querySelector(`[data-maid-history="${id}"]`),account=document.querySelector(`[data-maid-account-management="${id}"]`),topCard=document.querySelector('.detail-stack > section.card');
      return {following:!!(history.compareDocumentPosition(account)&Node.DOCUMENT_POSITION_FOLLOWING),topHasButton:!!topCard?.querySelector('[data-action="deactivate-maid-v2"]')};
    },maidId);
    assert.equal(placement.following,true,`${maidId} account management must follow work history`);
    assert.equal(placement.topHasButton,false,`${maidId} top account-status card must not contain the dangerous action`);
    await page.locator('[data-action="back"]').first().click();
    await page.locator(`[data-maid-card="${maidId}"]`).waitFor();
  }
}

async function verifyIndependentDeactivation(page){
  await openMaidDetail(page,'m4');
  await page.locator('[data-maid-account-management="m4"] [data-action="deactivate-maid-v2"]').click();
  let dialog=page.getByRole('dialog');
  await dialog.waitFor();
  assert.equal(await dialog.getByRole('heading',{name:'박소영 비활성 영향 확인'}).count(),1);
  await dialog.getByRole('button',{name:'비활성 처리 시작'}).click();
  await page.locator('[data-maid-account-management="m4"] [data-maid-deactivation-gate="m4"]').waitFor();
  for(const gate of ['assignments','round','lease']){
    await page.locator(`[data-control="maid-deactivation-gate"][data-maid-id="m4"][value="${gate}"]`).check();
  }
  const complete=page.locator('[data-action="complete-deactivation-v2"][data-id="m4"]');
  assert.equal(await complete.isEnabled(),true,'m4 completion must enable after all clear gates');
  await complete.click();
  const account=page.locator('[data-maid-account-management="m4"]');
  assert.match(await account.innerText(),/비활성 완료/);
  assert.equal(await account.locator('[data-action="deactivate-maid-v2"]').count(),0,'inactive account must not show a second start button');

  await page.locator('[data-action="back"]').first().click();
  const m4Card=page.locator('[data-maid-card="m4"]');
  await m4Card.waitFor();
  assert.match(await m4Card.innerText(),/비활성/,'m4 list card must reflect inactive status');
  const m1Card=page.locator('[data-maid-card="m1"]');
  assert.doesNotMatch(await m1Card.innerText(),/비활성 처리 중|비활성$/m,'m1 must remain active when m4 is deactivated');

  await openMaidDetail(page,'m2');
  await page.locator('[data-maid-account-management="m2"] [data-action="deactivate-maid-v2"]').click();
  dialog=page.getByRole('dialog');
  await dialog.waitFor();
  assert.equal(await dialog.getByRole('heading',{name:'김민지2 비활성 영향 확인'}).count(),1,'non-m1 deactivation modal must use the selected maid');
  await dialog.getByRole('button',{name:'닫기'}).click();
}

async function run(width,height){
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(`${width}px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${width}px console: ${message.text()}`);});
  await page.goto(base,{waitUntil:'networkidle'});
  await assertHealthy(page,width);
  assert.equal(await page.locator('[data-maid-card]').count(),9,'workforce must show nine maid cards');
  await verifyAllDetails(page);
  if(width===1440)await verifyIndependentDeactivation(page);
  await assertHealthy(page,width);
  await page.screenshot({path:`/tmp/all-maid-deactivation-${width}.png`,fullPage:false});
  await context.close();
}

await run(1440,1000);
await run(390,844);
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('All-maid lower account-management deactivation QA: passed');
