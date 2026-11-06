#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const document=JSON.parse(await readFile(new URL('../contracts/cleaning-prices.openapi.json',import.meta.url),'utf8'));
const full=JSON.parse(await readFile(new URL('../contracts/backend-openapi.json',import.meta.url),'utf8'));
for(const [path,item]of Object.entries(document.paths))assert.deepEqual(full.paths[path],item,`full contract drift: ${path}`);
for(const [name,schema]of Object.entries(document.components.schemas))assert.deepEqual(full.components.schemas[name],schema,`full schema drift: ${name}`);
const path='/v1/room-types/{roomTypeId}/cleaning-fee',operation=document.paths[path].put;
assert.deepEqual(operation['x-required-roles'],['admin']);
assert.deepEqual(document.paths['/v1/room-types'].get['x-required-roles'],['admin']);
assert.ok(operation.parameters.some(p=>p.in==='header'&&p.name==='Idempotency-Key'&&p.required));
const body=operation.requestBody.content['application/json'].schema;
assert.equal(body.additionalProperties,false);
assert.deepEqual(body.required,['baseCleaningFee','expectedVersion','confirmFutureTargetsOnly']);
assert.deepEqual(body.properties.baseCleaningFee,{type:'integer',minimum:0,maximum:1073741823});
assert.equal(body.properties.expectedVersion.minimum,1);
assert.equal(body.properties.confirmFutureTargetsOnly.const,true);
const receipt=operation.responses['200'].content['application/json'].schema.properties.roomType;
assert.deepEqual(receipt.required,['roomTypeId','baseCleaningFee','version','effectiveFor']);
assert.equal(receipt.properties.effectiveFor.const,'NEW_TARGETS_ONLY');
for(const status of [400,401,403,404,409,500,503])assert.ok(operation.responses[status]);
const catalog=document.components.schemas.RoomTypeCatalogItem;
for(const field of ['id','displayName','baseCleaningFee','version','active'])assert.ok(catalog.properties[field]);
if(process.env.RMS_QA_LIVE_CONTRACT==='true'){
  const base='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
  const response=await fetch(base+'/openapi.json');assert.equal(response.status,200);const live=await response.json();
  for(const [path,item]of Object.entries(document.paths))assert.deepEqual(live.paths[path],item,`deployed contract drift: ${path}`);
  for(const [name,schema]of Object.entries(document.components.schemas))assert.deepEqual(live.components.schemas[name],schema,`deployed schema drift: ${name}`);
  const origin='https://room-management-system-prod.vercel.app';
  const cors=await fetch(base+path.replace('{roomTypeId}','11000000-0000-4000-8000-000000000001'),{method:'OPTIONS',headers:{Origin:origin,'Access-Control-Request-Method':'PUT','Access-Control-Request-Headers':'authorization,content-type,idempotency-key'}});
  assert.equal(cors.status,204);assert.equal(cors.headers.get('access-control-allow-origin'),origin);assert.match(cors.headers.get('access-control-allow-methods'),/PUT/);
  const unauthorized=await fetch(base+'/v1/room-types');assert.equal(unauthorized.status,401);assert.match(unauthorized.headers.get('cache-control'),/no-store/);
  console.log('PASS: deployed price contracts, production PUT preflight, unauthenticated read denied. No price mutation sent.');
}
console.log('PASS: admin-only price contract, integer limits, explicit confirmation, CAS, idempotency and receipt.');
