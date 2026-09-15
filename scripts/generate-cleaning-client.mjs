#!/usr/bin/env node
// Read-only production verification; never changes the runtime release gate.
import { readFile, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const args=process.argv.slice(2),sourceIndex=args.indexOf('--source');
const production=args.includes('--production'),checkOnly=args.includes('--check');
if(production===(sourceIndex>=0))throw new Error('Use --source <OpenAPI JSON> for source QA, or --production after rollout.');
const methods=['get','post','put','patch','delete','head','options'];
function assert(ok,copy){if(!ok)throw new Error(copy);}
export function verifyCleaningContract(doc){
  const paths=doc.paths||{},schemas=doc.components?.schemas||{};
  assert(Object.keys(paths).length===109,'Expected 109 paths.');
  assert(Object.values(paths).reduce((n,p)=>n+Object.keys(p).filter(k=>methods.includes(k)).length,0)===117,'Expected 117 operations.');
  const request=schemas.PublishCleaningTemplateRequest,response=schemas.PublishedCleaningTemplate;
  assert(request&&response,'Cleaning template schemas are missing.');
  assert(!request.required?.includes('durationMinutes'),'durationMinutes must be optional in requests.');
  const nullable=s=>s?.type==='null'||Array.isArray(s?.type)&&s.type.includes('null')||(s?.anyOf||s?.oneOf||[]).some(nullable);
  assert(nullable(request.properties.durationMinutes)&&nullable(response.properties.durationMinutes),'Request and response durations must be nullable.');
  const numberSchema=request.properties.durationMinutes.anyOf?.find(s=>s.type==='integer');
  assert(numberSchema?.minimum===1&&numberSchema?.maximum===10080,'Duration range must remain 1..10080.');
  for(const [path,method] of [['/v1/cleaning-templates','get'],['/v1/cleaning-templates','post'],['/v1/attempts/{attemptId}/start','post'],['/v1/attempts/{attemptId}/checkout-not-completed','post'],['/v1/checkout-incidents/{incidentId}','get'],['/v1/checkout-incidents/{incidentId}/decision','post']])assert(paths[path]?.[method],`Missing ${method.toUpperCase()} ${path}`);
  return schemas;
}
async function jsonFromProduction(){
  const response=await fetch(`${api}/openapi.json`,{cache:'no-store',redirect:'error',signal:AbortSignal.timeout(10000)});
  assert(response.ok&&response.headers.get('sb-project-ref')==='aodikrxcczbogjpsjwjt','Production OpenAPI fetch failed or project differs.');
  const doc=await response.json();verifyCleaningContract(doc);
  const docs=await fetch(`${api}/docs`,{cache:'no-store',redirect:'error',signal:AbortSignal.timeout(10000)});
  assert(docs.ok&&(await docs.text()).includes('openapi.json'),'Production Swagger entry does not reference OpenAPI.');
  return doc;
}
const doc=production?await jsonFromProduction():JSON.parse(await readFile(args[sourceIndex+1],'utf8'));
const schemas=verifyCleaningContract(doc),needed=new Set();
function type(schema={}){
  if(schema.$ref){const name=schema.$ref.split('/').at(-1);needed.add(name);return name;}
  if(schema.const!==undefined)return JSON.stringify(schema.const);
  if(schema.enum)return schema.enum.map(v=>JSON.stringify(v)).join(' | ');
  if(schema.anyOf||schema.oneOf)return (schema.anyOf||schema.oneOf).map(type).join(' | ');
  if(Array.isArray(schema.type))return schema.type.map(t=>type({...schema,type:t})).join(' | ');
  if(schema.type==='object')return `{\n${Object.entries(schema.properties||{}).map(([key,value])=>`  ${key}${schema.required?.includes(key)?'':'?'}: ${type(value)}${key==='durationMinutes'&&!schema.required?.includes(key)?' | undefined':''};`).join('\n')}\n}`;
  if(schema.type==='array')return `Array<${type(schema.items)}>`;
  return {integer:'number',number:'number',boolean:'boolean',string:'string',null:'null'}[schema.type]||'unknown';
}
['PublishCleaningTemplateRequest','PublishedCleaningTemplate','CleaningTemplateRoomTypeState','AttemptExecutionRequest','AttemptExecution','Assignment','CheckoutIncidentReportRequest','CheckoutIncidentDecisionRequest','CheckoutIncidentEnvelope'].forEach(n=>needed.add(n));
let output=`// Generated from ${production?'production OpenAPI after nullable verification':'backend PR #166 exact source 84cf863; production regeneration pending'}.\n// Runtime configuration remains OFF. Do not edit generated types.\n`;
for(const name of needed){assert(schemas[name],`Missing schema ${name}`);output+=`export type ${name} = ${type(schemas[name])};\n\n`;}
if(!checkOnly)await writeFile(resolve(root,'WIREFRAME/cleaning-api.d.ts'),output);
console.log(`[ok] ${production?'Production OpenAPI / Swagger':'Source OpenAPI'}: 109 paths / 117 operations; optional nullable duration 1..10080. ${checkOnly?'Checked without writes.':'Client types regenerated; release gate remains OFF.'}`);
