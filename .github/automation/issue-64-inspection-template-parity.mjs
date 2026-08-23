import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const adminRoute='#scenario=4&role=admin&view=cleaning&date=2026-08-15&filter=all&type=all&q=&detail=cleaning:639';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

const desktop=await browser.newPage({viewport:{width:1440,height:1000}});
observe(desktop,'desktop');
await desktop.goto(`${base}${adminRoute}`,{waitUntil:'networkidle'});
const review=desktop.locator('.inspection-template-review');
await review.waitFor();

const summary=await review.evaluate(element=>({
  templateId:element.dataset.templateId,
  templateVersion:element.dataset.templateVersion,
  photoCount:Number(element.dataset.templatePhotoCount),
  requiredCount:Number(element.dataset.templateRequiredCount),
  zones:[...element.querySelectorAll('[data-inspection-zone]')].map(zone=>({
    name:zone.dataset.inspectionZone,
    requiredDone:Number(zone.dataset.requiredDone),
    requiredTotal:Number(zone.dataset.requiredTotal),
    photoCount:zone.querySelectorAll('[data-template-photo]').length,
    requiredPhotoCount:zone.querySelectorAll('[data-template-required="true"]').length,
  })),
  photos:[...element.querySelectorAll('[data-template-photo]')].map(photo=>({
    id:photo.dataset.templatePhoto,
    zone:photo.dataset.templateZone,
    required:photo.dataset.templateRequired,
    status:photo.dataset.templateStatus,
    title:photo.querySelector('.task-zone-photo-copy strong')?.textContent.trim(),
    description:photo.querySelector('.task-zone-photo-copy > span:not(.photo-state)')?.textContent.trim(),
    state:photo.querySelector('.photo-state')?.textContent.trim(),
  })),
}));

assert.ok(summary.templateId,'template ID is missing');
assert.ok(summary.templateVersion,'template version is missing');
assert.ok(summary.photoCount>0,'template has no photo items');
assert.ok(summary.requiredCount>0,'template has no required photo items');
assert.equal(summary.photos.length,summary.photoCount);
assert.equal(summary.photos.filter(photo=>photo.required==='true').length,summary.requiredCount);
assert.ok(summary.zones.length>0,'template has no zones');
assert.equal(summary.zones.reduce((total,zone)=>total+zone.photoCount,0),summary.photoCount);
assert.equal(summary.zones.reduce((total,zone)=>total+zone.requiredPhotoCount,0),summary.requiredCount);
assert.ok(summary.photos.every(photo=>photo.id&&photo.zone&&photo.title&&photo.description&&photo.state),'one or more admin photo items lost template metadata');
if(summary.templateVersion==='v7'){
  assert.ok(summary.photos.some(photo=>/TV 켜짐|화면 출력/.test(`${photo.title} ${photo.description}`)&&photo.required==='true'),'required TV-on evidence item is missing from a v7 admin review');
}
assert.ok(summary.photos.every(photo=>['done','failed','uploading','missing','empty'].includes(photo.status)),'unknown inspection photo status');

const zoneNames=summary.zones.map(zone=>zone.name);
assert.equal(new Set(zoneNames).size,zoneNames.length,'duplicate zone cards were rendered');
for(const zone of summary.zones){
  assert.ok(zone.requiredDone<=zone.requiredTotal,`invalid required progress for ${zone.name}`);
}

assert.equal(await review.locator('.task-zone-grid').count(),1);
assert.equal(await review.locator('.task-zone-card').count(),summary.zones.length);
assert.equal(await review.locator('.task-zone-photo').count(),summary.photoCount);
assert.equal(await review.locator('.task-zone-progress > div').count(),2);
assert.match((await review.textContent())||'',/메이드 청소 템플릿 기준 검수/);
assert.match((await review.textContent())||'',/제출 당시 템플릿 기준/);

const photoButton=review.locator('[data-action="inspection-photo"]').first();
if(await photoButton.count()){
  await photoButton.click();
  await desktop.locator('#modal-root .modal').waitFor();
  assert.match((await desktop.locator('#modal-title').textContent())||'',/사진|촬영|확인/);
  await desktop.locator('#modal-root [data-action="close-modal"]').first().click();
  await desktop.waitForFunction(()=>!document.querySelector('#modal-root .modal'));
}

assert.equal(await desktop.locator('[data-action="approve-inspection-v2"]').count(),1);
assert.equal(await desktop.locator('[data-action="reject-inspection-v2"]').count(),1);

const maid=await browser.newPage({viewport:{width:390,height:844}});
observe(maid,'maid');
await maid.goto(`${base}#scenario=3&role=maid&view=my&date=2026-08-15&filter=all&type=all&q=&detail=cleaning:528`,{waitUntil:'networkidle'});
await maid.locator('.task-zone-grid').waitFor();
assert.ok(await maid.locator('.task-zone-card').count()>0,'maid template zone cards are missing');
assert.ok(await maid.locator('.task-zone-photo').count()>0,'maid template photo items are missing');
assert.equal(await maid.locator('.task-zone-progress > div').count(),2);
assert.match((await maid.locator('.photo-template-banner').first().textContent())||'',/필수 사진/);
assert.match((await maid.locator('.task-zone-grid').textContent())||'',/TV 켜짐·화면 출력 확인/,'current v7 maid template lost its required TV-on item');

for(const width of [390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:1000}});
  observe(page,`responsive-${width}`);
  await page.goto(`${base}${adminRoute}`,{waitUntil:'domcontentloaded'});
  await page.locator('.inspection-template-review').waitFor();
  const values=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-window.innerWidth,zones:document.querySelectorAll('.inspection-template-review .task-zone-card').length,photos:document.querySelectorAll('.inspection-template-review .task-zone-photo').length}));
  assert.ok(values.overflow<=1,`${width}px horizontal overflow: ${values.overflow}`);
  assert.ok(values.zones>0&&values.photos>0,`${width}px grouped inspection did not render`);
  await page.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Admin/maid inspection template parity rendered QA: passed');
