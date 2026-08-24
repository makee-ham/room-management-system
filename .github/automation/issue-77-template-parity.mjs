import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function api(page,method,...args){
  return page.evaluate(({method,args})=>{
    const fn=window.__CASTLE_TEST__?.[method];
    if(typeof fn!=='function')throw new Error(`test API missing: ${method}`);
    return fn(...args);
  },{method,args});
}

function contractForDom(items){
  return items.map(({order,id,zone,label,description,required})=>({
    order,
    id,
    zone,
    label,
    description,
    required,
  }));
}

const desktop=await browser.newPage({viewport:{width:1440,height:1000}});
observe(desktop,'desktop');
await desktop.goto(base,{waitUntil:'networkidle'});
assert.match(await desktop.title(),/CASTLE THE ART/);
assert.ok((await desktop.locator('body').innerText()).includes('객실'),'meaningful application content is missing');

const family645=await api(desktop,'showTemplate','oceanFamily:checkout','645');
assert.equal(family645.baseRuleCount,11,'family checkout base rule count changed unexpectedly');
assert.equal(family645.actualSlotCount,15,'645 room must expand to fifteen maid photo slots');
assert.equal(family645.requiredSlotCount,14,'645 room required slot count is incorrect');
assert.equal(family645.optionalSlotCount,1,'645 room optional slot count is incorrect');
assert.equal(family645.verified,true,'645 room must be marked as a verified layout');
assert.deepEqual(family645.layoutProfile,{bedrooms:2,bathrooms:2,drains:2,pantry:false,source:'청소 사진 16장'});

const previewGrid=desktop.locator('[data-template-preview-grid]');
await previewGrid.waitFor();
assert.equal(await previewGrid.getAttribute('data-template-room'),'645');
assert.equal(Number(await previewGrid.getAttribute('data-template-photo-count')),15);
assert.equal(await desktop.locator('[data-template-preview-slot]').count(),15);
const previewDom=await desktop.locator('[data-template-preview-slot]').evaluateAll(nodes=>nodes.map(node=>({
  order:Number(node.dataset.templatePreviewOrder),
  id:node.dataset.templatePreviewSlot,
  zone:node.dataset.templatePreviewZone,
  label:node.dataset.templatePreviewLabel,
  description:node.dataset.templatePreviewDescription,
  required:node.dataset.templatePreviewRequired==='true',
})));
assert.deepEqual(previewDom,contractForDom(family645.contract),'admin preview slots differ from the maid slot contract');
const detailText=await desktop.locator('#main-content').innerText();
assert.match(detailText,/기본 규칙\s*11개/);
assert.match(detailText,/메이드 실제 슬롯\s*15개/);
assert.match(detailText,/레이아웃 확인 완료/);
assert.doesNotMatch(detailText,/여러 장 허용/);

const selector=desktop.locator('[data-control="template-preview-room"]');
await selector.selectOption('542');
await desktop.waitForFunction(()=>document.querySelector('[data-template-preview-grid]')?.dataset.templateRoom==='542');
const family542=await api(desktop,'templateParityData','oceanFamily:checkout','542');
assert.equal(family542.actualSlotCount,11,'542 room must use eleven actual slots');
assert.equal(await desktop.locator('[data-template-preview-slot]').count(),11);
const preview542Dom=await desktop.locator('[data-template-preview-slot]').evaluateAll(nodes=>nodes.map(node=>({
  order:Number(node.dataset.templatePreviewOrder),
  id:node.dataset.templatePreviewSlot,
  zone:node.dataset.templatePreviewZone,
  label:node.dataset.templatePreviewLabel,
  description:node.dataset.templatePreviewDescription,
  required:node.dataset.templatePreviewRequired==='true',
})));
assert.deepEqual(preview542Dom,contractForDom(family542.contract),'542 admin preview differs from the maid slot contract');

await api(desktop,'showTemplateList');
const familyRow=desktop.locator('[data-template-id="oceanFamily:checkout"]');
await familyRow.waitFor();
const familyRowText=await familyRow.innerText();
assert.match(familyRowText,/메이드 실제\s*11~15개 슬롯/,'template list does not show the real slot range');
assert.match(familyRowText,/기본 규칙\s*11개/,'template list does not distinguish base rules');

const versionAudit=await api(desktop,'templateVersionAudit','645');
assert.equal(versionAudit.current.tv,true,'current checkout template lost the TV slot');
assert.equal(versionAudit.legacy.version,'v6');
assert.equal(versionAudit.legacy.tv,false,'legacy v6 must not receive the TV slot retroactively');
assert.equal(versionAudit.current.count,versionAudit.legacy.count+1,'current and legacy checkout slot difference must be the TV slot');

await api(desktop,'resetScenario',0);
const prepared=await api(desktop,'prepareSubmission','528');
assert.equal(prepared.requiredDone,true,'528 required photos were not prepared');
const maidParity=await api(desktop,'maidTemplateParity','528');
assert.equal(maidParity.same,true,'maid task uploads differ from the frozen task snapshot');
assert.deepEqual(maidParity.actual,maidParity.expected);
const submission=await api(desktop,'submitCleaning','528');
assert.ok(submission?.record||submission?.submission||submission?.id,'cleaning submission was not created');
await api(desktop,'showInspection','528');
await desktop.locator('.inspection-template-review').waitFor();
const inspectionParity=await api(desktop,'inspectionTemplateParity','528');
assert.equal(inspectionParity.same,true,'admin inspection slots differ from the maid submission snapshot');
assert.deepEqual(inspectionParity.actual,inspectionParity.expected);
const inspection=desktop.locator('.inspection-template-review');
assert.equal(await inspection.getAttribute('data-template-contract-match'),'true');
assert.equal(Number(await inspection.getAttribute('data-template-photo-count')),inspectionParity.expected.length);
const inspectionText=await inspection.innerText();
assert.match(inspectionText,new RegExp(`메이드 제출 기준\\s*${inspectionParity.expected.length}개 슬롯\\s*·\\s*관리자 검수\\s*${inspectionParity.actual.length}개 슬롯`));
assert.match(inspectionText,/슬롯 구조 일치/);

const rerender=await api(desktop,'repeatRender',8);
assert.equal(rerender.equal,true,'re-rendering changed durable records during template parity review');

for(const width of [390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:1000}});
  observe(page,`responsive-${width}`);
  await page.goto(base,{waitUntil:'domcontentloaded'});
  const data=await api(page,'showTemplate','oceanFamily:checkout','645');
  assert.equal(data.actualSlotCount,15,`${width}px preview did not use expanded slots`);
  await page.locator('[data-template-preview-grid]').waitFor();
  assert.equal(await page.locator('[data-template-preview-slot]').count(),15);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await page.close();
}

await desktop.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered maid/admin template parity and responsive QA: passed');
