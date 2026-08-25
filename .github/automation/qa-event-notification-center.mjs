import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=today&date=2026-08-15&filter=all&type=all&q=';
const browser=await chromium.launch({headless:true});
const errors=[];

function countFromLabel(label=''){
  const match=String(label).match(/(\d+)건/);
  return match?Number(match[1]):0;
}

async function assertHealthy(page,width){
  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,`${width}px app must not be blank`);
  const bodyText=await page.locator('body').innerText();
  assert.doesNotMatch(bodyText,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px document horizontal overflow: ${overflow}`);
}

async function openBell(page){
  const bell=page.getByRole('button',{name:/알림함 열기/});
  await bell.waitFor();
  await bell.click();
  const dialog=page.getByRole('dialog');
  await dialog.waitFor();
  return dialog;
}

async function verifyDesktop(){
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(`1440px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`1440px console: ${message.text()}`);});
  await page.goto(base,{waitUntil:'networkidle'});
  await assertHealthy(page,1440);

  const main=page.locator('#main-content');
  const homeList=main.locator('.accordion-list').first();
  assert.equal(await homeList.locator(':scope > .accordion').count(),2,'admin home regression: exactly two work accordions');
  assert.equal(await homeList.getByRole('button',{name:/오늘 청소 배정/}).count(),1);
  assert.equal(await homeList.getByRole('button',{name:/청소 검수/}).count(),1);

  const bell=page.getByRole('button',{name:/알림함 열기/});
  const initialAdminCount=countFromLabel(await bell.getAttribute('aria-label'));
  assert.ok(initialAdminCount>=3,`admin unread seed count must be at least 3, got ${initialAdminCount}`);

  let dialog=await openBell(page);
  assert.equal(await dialog.getByRole('heading',{name:'관리자 알림'}).count(),1);
  const dialogText=await dialog.innerText();
  assert.match(dialogText,/앱 내 알림은 항상 보존됩니다/);
  assert.doesNotMatch(dialogText,/동기화\s*최신 상태|담당 취소 요청\s*0건|컴플레인 이의\s*0건|지급 대기 0\/3명/);
  assert.equal(await dialog.locator('[data-action="notification-filter"][data-filter="all"]').count(),1);
  assert.equal(await dialog.locator('[data-action="notification-filter"][data-filter="unread"]').count(),1);
  assert.equal(await dialog.locator('[data-action="notification-filter"][data-filter="action"]').count(),1);
  assert.ok(await dialog.locator('[data-notification-card]').count()>=4,'admin center must retain open and handled events');

  await dialog.getByRole('button',{name:/639호 청소 검수 요청/}).click();
  await page.waitForFunction(()=>location.hash.includes('view=cleaning'));
  const inspectionTab=page.getByRole('tab',{name:/검수 대기/});
  await inspectionTab.waitFor();
  assert.equal(await inspectionTab.getAttribute('aria-selected'),'true','inspection notification must deep-link to inspection tab');
  const afterOneRead=countFromLabel(await page.getByRole('button',{name:/알림함 열기/}).getAttribute('aria-label'));
  assert.equal(afterOneRead,initialAdminCount-1,'opening one admin notification must reduce unread badge by one bundle');

  dialog=await openBell(page);
  const allCardsBefore=await dialog.locator('[data-notification-card]').count();
  await dialog.getByRole('button',{name:'모두 읽음'}).click();
  dialog=page.getByRole('dialog');
  await dialog.waitFor();
  assert.equal(await dialog.locator('.notification-card.unread').count(),0,'mark all read must clear unread styling');
  assert.equal(countFromLabel(await page.locator('[data-action="alerts"]').getAttribute('aria-label')),0,'admin badge must be zero after mark all read');

  const pushButton=dialog.getByRole('button',{name:/푸시 (꺼짐|켜짐)/});
  const beforePushCards=await dialog.locator('[data-notification-card]').count();
  await pushButton.click();
  dialog=page.getByRole('dialog');
  await dialog.waitFor();
  assert.equal(await dialog.locator('[data-notification-card]').count(),beforePushCards,'toggling push must not remove in-app notifications');
  assert.equal(await dialog.getByRole('button',{name:'푸시 켜짐'}).getAttribute('aria-pressed'),'true');
  assert.equal(allCardsBefore,beforePushCards,'read state must not delete handled or read notifications');

  await dialog.getByRole('button',{name:'닫기'}).click();
  await page.getByRole('button',{name:'메이드 보기'}).click();
  await page.waitForFunction(()=>location.hash.includes('role=maid'));
  await assertHealthy(page,1440);

  const maidBell=page.getByRole('button',{name:/알림함 열기/});
  const initialMaidCount=countFromLabel(await maidBell.getAttribute('aria-label'));
  assert.ok(initialMaidCount>=3,`maid unread bundle count must be at least 3, got ${initialMaidCount}`);
  dialog=await openBell(page);
  assert.equal(await dialog.getByRole('heading',{name:'내 알림'}).count(),1);
  const maidText=await dialog.innerText();
  assert.match(maidText,/업데이트 2건/,'same-room assignment updates must be bundled');
  assert.doesNotMatch(maidText,/639호 청소 검수 요청/,'maid must not see admin-only notification');
  await dialog.getByRole('button',{name:/350호 보완 청소 요청/}).click();
  await page.waitForFunction(()=>location.hash.includes('view=my'));
  assert.match(await page.locator('#main-content').innerText(),/내 업무/,'maid correction notification must deep-link to own work');

  const selfPushResult=await page.evaluate(()=>{
    const maidKey=`maid:${signedInMaidId()}`,beforeMaid=notificationUnreadCount(maidKey),beforeAdmin=notificationUnreadCount('admin');
    appendEvent('528호 청소 시작','본인이 청소를 시작했습니다.',{maidIds:[signedInMaidId()],roomId:'528'});
    const afterStartMaid=notificationUnreadCount(maidKey),afterStartAdmin=notificationUnreadCount('admin');
    appendEvent('528호 청소 전체 제출','필수 파일 검증 완료 · 검수 대기',{maidIds:[signedInMaidId()],roomId:'528'});
    return {beforeMaid,beforeAdmin,afterStartMaid,afterStartAdmin,afterSubmitMaid:notificationUnreadCount(maidKey),afterSubmitAdmin:notificationUnreadCount('admin')};
  });
  assert.equal(selfPushResult.afterStartMaid,selfPushResult.beforeMaid,'maid cleaning start must not create self notification');
  assert.equal(selfPushResult.afterStartAdmin,selfPushResult.beforeAdmin,'normal cleaning start must not push admin');
  assert.equal(selfPushResult.afterSubmitMaid,selfPushResult.beforeMaid,'maid inspection request must not self-notify');
  assert.equal(selfPushResult.afterSubmitAdmin,selfPushResult.beforeAdmin+1,'maid inspection request must notify admin');

  const bundleResult=await page.evaluate(()=>{
    const groupKey='admin:issue:516',before=notificationBundlesForKey('admin').length;
    state.time='10:40';
    appendEvent('516호 현장 문제 업데이트','도어락 응답을 확인하고 있습니다.',{actorRole:'system',roomId:'516',notification:{audience:['admin'],category:'issue',priority:'high',push:true,actionRequired:true,status:'open',groupKey,target:{action:'room-detail',id:'516'}}});
    state.time='10:45';
    appendEvent('516호 현장 문제 업데이트','투숙객 연락 결과를 추가했습니다.',{actorRole:'system',roomId:'516',notification:{audience:['admin'],category:'issue',priority:'high',push:true,actionRequired:true,status:'open',groupKey,target:{action:'room-detail',id:'516'}}});
    const bundles=notificationBundlesForKey('admin'),bundle=bundles.find(item=>item.groupKey===groupKey);
    return {before,after:bundles.length,bundleCount:bundle?.bundleCount||0};
  });
  assert.equal(bundleResult.after,bundleResult.before+1,'two related events must add one notification bundle');
  assert.equal(bundleResult.bundleCount,2,'bundle must retain both updates');

  await page.screenshot({path:'/tmp/event-notification-center-admin-1440.png',fullPage:false});
  await assertHealthy(page,1440);
  await context.close();
}

async function verifyMobile(){
  const context=await browser.newContext({viewport:{width:390,height:844}});
  const page=await context.newPage();
  page.on('pageerror',error=>errors.push(`390px pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`390px console: ${message.text()}`);});
  await page.goto(base,{waitUntil:'networkidle'});
  await assertHealthy(page,390);
  let dialog=await openBell(page);
  assert.equal(await dialog.locator('.notification-filter-group').count(),1);
  assert.equal(await dialog.locator('.notification-toolbar-actions').count(),1);
  assert.ok(await dialog.locator('[data-notification-card]').count()>=4);
  await page.screenshot({path:'/tmp/event-notification-center-admin-390.png',fullPage:false});
  await dialog.getByRole('button',{name:'닫기'}).click();
  await page.getByRole('button',{name:/메이드 보기/}).click();
  await page.waitForFunction(()=>location.hash.includes('role=maid'));
  dialog=await openBell(page);
  assert.match(await dialog.innerText(),/업데이트 2건/);
  await page.screenshot({path:'/tmp/event-notification-center-maid-390.png',fullPage:false});
  await assertHealthy(page,390);
  await context.close();
}

await verifyDesktop();
await verifyMobile();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Event notification center rendered QA: passed');
