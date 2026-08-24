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

function domContract(items){
  return items.map(({order,id,zone,label,description,required})=>({order,id,zone,label,description,required}));
}

const expected={
  standard:{rooms:22,slots:10,required:9,optional:1,composition:'원룸형 메인 공간 1 · 주방 1 · 욕실 1'},
  premium:{rooms:51,slots:11,required:10,optional:1,composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1'},
  oceanPremium:{rooms:13,slots:13,required:12,optional:1,composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1'},
  oceanFamily:{rooms:35,slots:15,required:14,optional:1,composition:'주방 1 · 거실 1 · 침실 2 · 욕실 2'},
};

const desktop=await browser.newPage({viewport:{width:1440,height:1000}});
observe(desktop,'desktop');
await desktop.goto(base,{waitUntil:'networkidle'});
assert.match(await desktop.title(),/CASTLE THE ART/);

for(const [typeId,contract] of Object.entries(expected)){
  const parity=await api(desktop,'typeTemplateParity',typeId,'퇴실 청소');
  assert.equal(parity.roomCount,contract.rooms,`${typeId} room-to-type count changed`);
  assert.equal(parity.allSame,true,`${typeId} rooms do not share one fixed slot signature`);
  assert.equal(parity.signatures.length,1,`${typeId} produced more than one slot signature`);
  assert.equal(parity.slotCount,contract.slots,`${typeId} fixed slot count is incorrect`);
  assert.equal(parity.composition,contract.composition,`${typeId} fixed composition is incorrect`);

  const detail=await api(desktop,'showTemplate',`${typeId}:checkout`,parity.rooms[0]);
  assert.equal(detail.fixedByType,true);
  assert.equal(detail.roomCount,contract.rooms);
  assert.equal(detail.actualSlotCount,contract.slots);
  assert.equal(detail.requiredSlotCount,contract.required);
  assert.equal(detail.optionalSlotCount,contract.optional);
  assert.equal(detail.composition,contract.composition);
  const grid=desktop.locator('[data-template-fixed-grid]');
  await grid.waitFor();
  assert.equal(await grid.getAttribute('data-template-type'),typeId);
  assert.equal(Number(await grid.getAttribute('data-template-photo-count')),contract.slots);
  assert.equal(await desktop.locator('[data-template-fixed-slot]').count(),contract.slots);
  assert.equal(await desktop.locator('[data-control="template-preview-room"]').count(),0,'room selector must not exist');
  const text=await desktop.locator('#main-content').innerText();
  assert.ok(text.includes(contract.composition),`${typeId} composition is not visible`);
  assert.match(text,new RegExp(`고정 사진 슬롯\\s*${contract.slots}개`));
}

const family645=await api(desktop,'showTemplate','oceanFamily:checkout','645');
const family645Dom=await desktop.locator('[data-template-fixed-slot]').evaluateAll(nodes=>nodes.map(node=>({
  order:Number(node.dataset.templateFixedOrder),
  id:node.dataset.templateFixedSlot,
  zone:node.dataset.templateFixedZone,
  label:node.dataset.templateFixedLabel,
  description:node.dataset.templateFixedDescription,
  required:node.dataset.templateFixedRequired==='true',
})));
assert.deepEqual(family645Dom,domContract(family645.contract),'admin fixed slot DOM differs from family type contract');
const family542=await api(desktop,'templateParityData','oceanFamily:checkout','542');
assert.equal(family645.actualSlotCount,15);
assert.equal(family542.actualSlotCount,15);
assert.equal(family645.signature,family542.signature,'645 and 542 must share the same family template');
assert.deepEqual(family645.contract,family542.contract);

await api(desktop,'showTemplateList');
for(const [typeId,contract] of Object.entries(expected)){
  const row=desktop.locator(`[data-template-id="${typeId}:checkout"]`);
  await row.waitFor();
  const text=await row.innerText();
  assert.match(text,new RegExp(`메이드 고정\\s*${contract.slots}개 슬롯`),`${typeId} exact slot count is missing from list`);
  assert.doesNotMatch(text,/\d+~\d+개/,'template list must not show a slot range');
}
const listText=await desktop.locator('#main-content').innerText();
assert.doesNotMatch(listText,/레이아웃 확인|최소 공통|객실별 보정/);

const versionAudit=await api(desktop,'templateVersionAudit','645');
assert.equal(versionAudit.current.tv,true,'current family checkout template lost the TV slot');
assert.equal(versionAudit.current.count,15);
assert.equal(versionAudit.legacy.version,'v6');
assert.equal(versionAudit.legacy.tv,false,'legacy v6 must not receive TV retroactively');
assert.equal(versionAudit.legacy.count,14);

await api(desktop,'resetScenario',0);
const prepared=await api(desktop,'prepareSubmission','528');
assert.equal(prepared.requiredDone,true,'528 required photos were not prepared');
const maidParity=await api(desktop,'maidTemplateParity','528');
assert.equal(maidParity.same,true,'maid task slots differ from the frozen task snapshot');
assert.deepEqual(maidParity.actual,maidParity.expected);
const submission=await api(desktop,'submitCleaning','528');
assert.ok(submission?.record||submission?.submission||submission?.id,'cleaning submission was not created');
await api(desktop,'showInspection','528');
await desktop.locator('.inspection-template-review').waitFor();
const inspectionParity=await api(desktop,'inspectionTemplateParity','528');
assert.equal(inspectionParity.same,true,'admin inspection differs from the maid submission snapshot');
assert.deepEqual(inspectionParity.actual,inspectionParity.expected);
const inspection=desktop.locator('.inspection-template-review');
assert.equal(await inspection.getAttribute('data-template-contract-match'),'true');
assert.equal(Number(await inspection.getAttribute('data-template-photo-count')),inspectionParity.expected.length);
assert.match(await inspection.innerText(),new RegExp(`메이드 제출 기준\\s*${inspectionParity.expected.length}개 슬롯\\s*·\\s*관리자 검수\\s*${inspectionParity.actual.length}개 슬롯`));

const rerender=await api(desktop,'repeatRender',8);
assert.equal(rerender.equal,true,'re-rendering changed durable records during fixed-template review');

for(const width of [390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:1000}});
  observe(page,`responsive-${width}`);
  await page.goto(base,{waitUntil:'domcontentloaded'});
  const data=await api(page,'showTemplate','oceanFamily:checkout','645');
  assert.equal(data.actualSlotCount,15,`${width}px family detail did not use fixed slots`);
  await page.locator('[data-template-fixed-grid]').waitFor();
  assert.equal(await page.locator('[data-template-fixed-slot]').count(),15);
  assert.equal(await page.locator('[data-control="template-preview-room"]').count(),0);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await page.close();
}

await desktop.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered fixed room-type templates, maid/admin parity, and responsive QA: passed');
