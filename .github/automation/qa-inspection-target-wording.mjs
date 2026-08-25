import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=today&date=2026-08-15&filter=all&type=all&q=';
const browser=await chromium.launch({headless:true});
const errors=[];

async function verify(width,height,screenshotPath){
  const context=await browser.newContext({viewport:{width,height}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(`${width}px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${width}px console: ${message.text()}`);});
  await page.goto(base,{waitUntil:'networkidle'});

  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,`${width}px admin home must not be blank`);
  const bodyText=await page.locator('body').innerText();
  assert.doesNotMatch(bodyText,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error|ReferenceError/);

  const homeList=main.locator('.accordion-list').first();
  const cleaningInspectionAccordion=homeList.getByRole('button',{name:/청소 검수/});
  await cleaningInspectionAccordion.waitFor();
  if((await cleaningInspectionAccordion.getAttribute('aria-expanded'))!=='true')await cleaningInspectionAccordion.click();
  const entryButton=homeList.getByRole('button',{name:'검수 대상 목록 열기'});
  await entryButton.waitFor();
  assert.equal(await homeList.getByRole('button',{name:'검수 대기 열기'}).count(),0,'legacy admin-home entry wording must be gone');
  const accordionText=await homeList.innerText();
  assert.match(accordionText,/검수 요청됨/,'admin-home inspection items must say 검수 요청됨');

  await entryButton.click();
  await page.waitForFunction(()=>location.hash.includes('view=cleaning'));
  const targetTab=page.getByRole('tab',{name:/검수 대상 목록/});
  await targetTab.waitFor();
  assert.equal(await targetTab.getAttribute('aria-selected'),'true','inspection target-list tab must be selected');
  const tabList=page.getByRole('tablist',{name:'청소 상태'});
  assert.equal(await tabList.getByRole('tab',{name:/검수 대기/}).count(),0,'legacy inspection tab label must be gone');

  const cleaningText=await main.innerText();
  assert.match(cleaningText,/검수 요청됨/,'inspection task status must say 검수 요청됨');
  assert.doesNotMatch(cleaningText,/검수 대기 탭/);

  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px document horizontal overflow: ${overflow}`);
  await page.screenshot({path:screenshotPath,fullPage:false});
  await context.close();
}

await verify(1440,1000,'/tmp/admin-inspection-target-list-1440.png');
await verify(390,844,'/tmp/admin-inspection-target-list-390.png');
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Inspection target-list wording rendered QA: passed');
