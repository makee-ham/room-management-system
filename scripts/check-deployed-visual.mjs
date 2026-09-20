#!/usr/bin/env node
// Read-only hosted static/UI smoke. Runtime config is intercepted as demo so production API data is never touched.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';

const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=String(process.env.RMS_QA_ORIGIN||'https://room-management-system-prod.vercel.app').replace(/\/$/,'');
const localSource=await readFile(resolve('WIREFRAME/index.html'),'utf8'),response=await fetch(`${origin}/index.html`,{cache:'no-store'}),hostedSource=await response.text();
assert.equal(response.status,200);assert.equal(createHash('sha256').update(hostedSource).digest('hex'),createHash('sha256').update(localSource).digest('hex'),'deployed index.html differs from the wireframe source');

const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(12000);const pageErrors=[],consoleProblems=[],passed=[];
page.on('pageerror',error=>pageErrors.push(error.message));
page.on('console',message=>{const text=message.text();if(['warning','error'].includes(message.type())&&!/^Failed to load resource:/.test(text)&&text!=='Service Worker registration blocked by Playwright')consoleProblems.push(text);});
await page.route(`${origin}/runtime-config.json*`,route=>route.fulfill({status:200,contentType:'application/json',headers:{'cache-control':'no-store'},body:'{"mode":"demo"}'}));

async function login(id,password){await page.locator('#login-id').fill(id);await page.locator('#login-password').fill(password);await page.locator('#login-form').press('Enter');await page.locator('[data-action="logout"]:visible').first().waitFor();}
async function visit(view){const nav=page.locator(`[data-action="nav"][data-view="${view}"]:visible`).first();await nav.click();await page.locator('#main-content').waitFor();assert(await nav.getAttribute('aria-current')==='page',`${view} nav is not current`);assert((await page.locator('#main-content').innerText()).trim().length>0,`${view} is empty`);for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:960});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${view} overflows at ${width}px`);}}

try{
  await page.goto(`${origin}/index.html?scenario=0&role=admin&view=today&date=2026-08-15`,{waitUntil:'domcontentloaded'});await login('admin','admin1234');
  for(const view of ['today','rooms','quickReservation','cleaning','maids','more'])await visit(view);
  await visit('rooms');await page.setViewportSize({width:390,height:900});await mkdir(resolve('WIREFRAME/QA/screenshots'),{recursive:true});await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/deployed-v040-rooms-390.png')});
  await visit('quickReservation');await page.setViewportSize({width:1440,height:1000});await page.screenshot({path:resolve('WIREFRAME/QA/screenshots/deployed-v040-calendar-1440.png'),fullPage:true});passed.push('배포본 관리자 오늘·객실·간편 예약·청소·메이드·더보기 전 화면');
  await page.locator('[data-action="logout"]:visible').first().click();await page.locator('#login-form').waitFor();await login('maid1','maid1234');for(const view of ['my','schedule','pay','more'])await visit(view);passed.push('배포본 메이드 내 업무·근무 일정·주급·더보기 전 화면');
  assert.deepEqual(pageErrors,[]);assert.deepEqual(consoleProblems,[]);passed.push('360/390/768/1440px 가로 넘침·페이지 예외·console warning/error 0건');
  passed.forEach(item=>console.log(`[ok] ${item}`));console.log(`[ok] deployed index SHA-256 ${createHash('sha256').update(hostedSource).digest('hex')}`);console.log(`Environment: Chromium ${await browser.version()} via Playwright; Browser plugin unavailable. Hosted runtime config was intercepted as demo and production API data was not accessed.`);
}finally{await browser.close();}
