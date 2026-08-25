import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=today&date=2026-08-15&filter=all&type=all&q=';
const browser=await chromium.launch({headless:true});
const errors=[];

async function verify(width,screenshotPath){
  const page=await browser.newPage({viewport:{width,height:900}});
  page.on('pageerror',error=>errors.push(`${width}px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${width}px console: ${message.text()}`);});
  await page.goto(base,{waitUntil:'networkidle'});
  assert.match(await page.title(),/오늘 할 일 · CASTLE THE ART 데모/);
  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,'admin home must not be blank');
  const bodyText=await page.locator('body').innerText();
  assert.doesNotMatch(bodyText,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error/);

  const list=main.locator('.accordion-list');
  await list.waitFor();
  assert.equal(await list.locator(':scope > .accordion').count(),2,'admin home must render exactly two work accordions');
  assert.equal(await list.getByRole('button',{name:/오늘 청소 배정/}).count(),1);
  assert.equal(await list.getByRole('button',{name:/청소 검수/}).count(),1);

  const listText=await list.innerText();
  for(const removed of ['오늘 체크인·체크아웃','담당 취소 요청','담당 취소 처리 결과','배정 준비 청소 작업','검수 대기\n2건','지난주 지급']){
    assert.ok(!listText.includes(removed),`removed admin-home item remains: ${removed}`);
  }
  assert.equal(await main.getByText(/다음 주 가능일 제출/).count(),0,'availability banner must be removed from admin home');

  const assignment=list.getByRole('button',{name:/오늘 청소 배정/});
  assert.equal(await assignment.getAttribute('aria-expanded'),'true');
  await assignment.click();
  assert.equal(await assignment.getAttribute('aria-expanded'),'false');
  await assignment.click();
  assert.equal(await assignment.getAttribute('aria-expanded'),'true');

  const inspection=list.getByRole('button',{name:/청소 검수/});
  await inspection.click();
  assert.equal(await inspection.getAttribute('aria-expanded'),'true');
  await list.getByRole('button',{name:'검수 대기 열기'}).click();
  await page.waitForFunction(()=>location.hash.includes('view=inspection'));
  assert.match(page.url(),/view=inspection/);
  await page.goBack({waitUntil:'networkidle'});
  await page.locator('.accordion-list').waitFor();

  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px document horizontal overflow: ${overflow}`);
  await page.screenshot({path:screenshotPath,fullPage:false});
  await page.close();
}

await verify(1440,'/tmp/admin-home-cleaning-only-1440.png');
await verify(390,'/tmp/admin-home-cleaning-only-390.png');
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Admin-home cleaning-only rendered QA: passed');
