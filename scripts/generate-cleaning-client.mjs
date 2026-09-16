#!/usr/bin/env node
// Production OpenAPI verification and generated cleaning client types.
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
  assert(doc.info?.version==='0.3.0','Expected production API version 0.3.0.');
  assert(Object.keys(paths).length===109,'Expected 109 paths.');
  assert(Object.values(paths).reduce((n,p)=>n+Object.keys(p).filter(k=>methods.includes(k)).length,0)===117,'Expected 117 operations.');
  const request=schemas.PublishCleaningTemplateRequest,response=schemas.PublishedCleaningTemplate;
  assert(request&&response,'Cleaning template schemas are missing.');
  assert(!request.required?.includes('durationMinutes'),'durationMinutes must be optional in requests.');
  const nullable=s=>s?.type==='null'||Array.isArray(s?.type)&&s.type.includes('null')||(s?.anyOf||s?.oneOf||[]).some(nullable);
  assert(nullable(request.properties.durationMinutes)&&nullable(response.properties.durationMinutes),'Request and response durations must be nullable.');
  const numberSchema=request.properties.durationMinutes.anyOf?.find(s=>s.type==='integer');
  assert(numberSchema?.minimum===1&&numberSchema?.maximum===10080,'Duration range must remain 1..10080.');
  const requiredOperations=[
    ['/v1/assignments','get'],['/v1/assignments/{cleaningTargetId}/history','get'],['/v1/assignments/drafts','post'],['/v1/assignments/preview','post'],['/v1/assignments/commit-impact','get'],['/v1/assignments/commit','post'],['/v1/assignments/{cleaningTargetId}/change','post'],['/v1/assignments/{cleaningTargetId}/unassign','post'],['/v1/assignments/{cleaningTargetId}/cancellation-requests','post'],['/v1/assignment-change-requests','get'],['/v1/assignment-change-requests/{requestId}/decision','post'],
    ['/v1/attempts/current','get'],['/v1/attempts/{attemptId}/lifecycle','post'],['/v1/attempts/{attemptId}/start','post'],['/v1/attempts/{attemptId}/start-with-lease','post'],['/v1/attempts/{attemptId}/complete-field-work','post'],['/v1/attempts/{attemptId}/checkout-not-completed','post'],['/v1/attempts/{attemptId}/bomb-room-reports','post'],['/v1/attempts/{attemptId}/photo-slots','get'],['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload','post'],['/v1/attempts/{attemptId}/submissions','get'],['/v1/attempts/{attemptId}/submissions','post'],['/v1/photos/{photoId}/content','get'],
    ['/v1/inspections','get'],['/v1/inspections/{submissionId}','get'],['/v1/inspections/{submissionId}/approve','post'],['/v1/inspections/{submissionId}/reject','post'],['/v1/inspections/{submissionId}/bomb-room-decision','post'],['/v1/notifications','get'],['/v1/notifications/{notificationId}/read','post']
  ];
  for(const [path,method] of requiredOperations)assert(paths[path]?.[method],`Missing ${method.toUpperCase()} ${path}`);
  const idempotentPosts=requiredOperations.filter(([,method])=>method==='post').filter(([path])=>!['/v1/assignments/preview','/v1/notifications/{notificationId}/read'].includes(path));
  for(const [path] of idempotentPosts){const parameters=paths[path].post.parameters||[];assert(parameters.some(item=>item.name==='Idempotency-Key'&&item.in==='header'&&item.required===true),`Missing required Idempotency-Key on POST ${path}`);}
  assert(paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload'].post.requestBody?.content?.['image/jpeg'],'Photo upload must accept image/jpeg bytes.');
  assert(paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload'].post.requestBody?.content?.['image/webp'],'Photo upload must accept image/webp bytes.');
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
  if(schema.allOf)return schema.allOf.map(type).join(' & ');
  if(Array.isArray(schema.type))return schema.type.map(t=>type({...schema,type:t})).join(' | ');
  if(schema.type==='object')return `{\n${Object.entries(schema.properties||{}).map(([key,value])=>`  ${key}${schema.required?.includes(key)?'':'?'}: ${type(value)}${key==='durationMinutes'&&!schema.required?.includes(key)?' | undefined':''};`).join('\n')}\n}`;
  if(schema.type==='array')return `Array<${type(schema.items)}>`;
  return {integer:'number',number:'number',boolean:'boolean',string:'string',null:'null'}[schema.type]||'unknown';
}
['ErrorCode','ErrorEnvelope','Assignment','AssignmentDraftRequest','AssignmentPreviewRequest','AssignmentPreviewUnconfirmed','AssignmentPreviewResult','AssignmentCommitImpact','AssignmentCommitRequest','AssignmentCommitResult','AssignmentPrestartChangeRequest','AssignmentPrestartUnassignRequest','AssignmentCancellationRequest','AssignmentCancellationDecisionRequest','AssignmentChangeRequest','AssignmentChangeRequestPage','AttemptLifecycleRequest','AttemptLifecycleImpact','AttemptLifecycleResult','AttemptExecutionRequest','AttemptExecution','AttemptWithOfflineLease','CheckoutIncidentReportRequest','CheckoutIncidentDecisionRequest','CheckoutIncidentEnvelope','AttemptPhotoSlots','PhotoUploadResponse','BombRoomReportRequest','BombRoomReportEnvelope','CreateSubmissionRequest','CleaningSubmission','SubmissionEnvelope','SubmissionListEnvelope','BombRoomDecisionRequest','InspectionDecisionRequest','BombRoomDecisionEnvelope','InspectionDecisionEnvelope','Notification','NotificationEnvelope','NotificationListEnvelope','PublishCleaningTemplateRequest','PublishedCleaningTemplate','CleaningTemplateRoomTypeState'].forEach(n=>needed.add(n));
let output=`// Generated from ${production?'production OpenAPI v0.3.0':'an explicitly supplied OpenAPI v0.3.0 source'}.\n// Do not edit generated types directly.\n`;
for(const name of needed){assert(schemas[name],`Missing schema ${name}`);output+=`export type ${name} = ${type(schemas[name])};\n\n`;}
if(!checkOnly)await writeFile(resolve(root,'WIREFRAME/cleaning-api.d.ts'),output);
console.log(`[ok] ${production?'Production OpenAPI / Swagger':'Source OpenAPI'}: 109 paths / 117 operations; cleaning assignment, attempt, photo, submission, inspection, and notification contracts verified. ${checkOnly?'Checked without writes.':'Client types regenerated.'}`);
