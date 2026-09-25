#!/usr/bin/env node
// Production OpenAPI verification and generated operational client types.
import { readFile, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const canonicalOpenApi='https://wrongstory.github.io/room-management-system-backend/openapi.json';
const args=process.argv.slice(2),sourceIndex=args.indexOf('--source');
const production=args.includes('--production'),checkOnly=args.includes('--check');
if(production===(sourceIndex>=0))throw new Error('Use --source <OpenAPI JSON> for source QA, or --production after rollout.');
const methods=['get','post','put','patch','delete','head','options'];
function assert(ok,copy){if(!ok)throw new Error(copy);}
export function verifyCleaningContract(doc){
  const paths=doc.paths||{},schemas=doc.components?.schemas||{};
  assert(doc.info?.version==='0.5.1','Expected production API version 0.5.1.');
  assert(Object.keys(paths).length===128,'Expected 128 paths.');
  assert(Object.values(paths).reduce((n,p)=>n+Object.keys(p).filter(k=>methods.includes(k)).length,0)===138,'Expected 138 operations.');
  assert(doc.servers?.[0]?.url===api,'OpenAPI server URL differs from the documented production API.');
  const request=schemas.PublishCleaningTemplateRequest,response=schemas.PublishedCleaningTemplate;
  assert(request&&response,'Cleaning template schemas are missing.');
  assert(!request.required?.includes('durationMinutes'),'durationMinutes must be optional in requests.');
  const nullable=s=>s?.type==='null'||Array.isArray(s?.type)&&s.type.includes('null')||(s?.anyOf||s?.oneOf||[]).some(nullable);
  assert(nullable(request.properties.durationMinutes)&&nullable(response.properties.durationMinutes),'Request and response durations must be nullable.');
  const numberSchema=request.properties.durationMinutes.anyOf?.find(s=>s.type==='integer');
  assert(numberSchema?.minimum===1&&numberSchema?.maximum===10080,'Duration range must remain 1..10080.');
  for(const name of ['ReservationBookabilityStandardPreviewRequest','ReservationBookabilityLongStayPreviewRequest']){
    const previewRequest=schemas[name],guestCount=previewRequest?.properties?.guestCount;assert(guestCount,`${name}.guestCount is missing.`);assert(!previewRequest.required?.includes('guestCount'),`${name}.guestCount must remain optional for interval-only preview.`);assert(nullable(guestCount),`${name}.guestCount must remain nullable.`);const integerGuestCount=guestCount.anyOf?.find(s=>s.type==='integer')||guestCount;assert(integerGuestCount.type==='integer'||Array.isArray(integerGuestCount.type)&&integerGuestCount.type.includes('integer'),`${name}.guestCount must remain an integer when provided.`);assert(integerGuestCount.minimum===1,`${name}.guestCount minimum must remain 1.`);
  }
  for(const name of ['ReservationStandardCreateRequest','ReservationLongStayCreateRequest','ReservationStandardChangeRequest','ReservationLongStayChangeRequest'])assert(schemas[name]?.required?.includes('guestCount'),`${name}.guestCount must remain required.`);
  const requiredOperations=[
    ['/v1/assignments','get'],['/v1/assignments/{cleaningTargetId}/history','get'],['/v1/assignments/drafts','post'],['/v1/assignments/preview','post'],['/v1/assignments/commit-impact','get'],['/v1/assignments/commit','post'],['/v1/assignments/{cleaningTargetId}/change','post'],['/v1/assignments/{cleaningTargetId}/unassign','post'],['/v1/assignments/{cleaningTargetId}/cancellation-requests','post'],['/v1/assignment-change-requests','get'],['/v1/assignment-change-requests/{requestId}/decision','post'],
    ['/v1/attempts/current','get'],['/v1/attempts/{attemptId}/lifecycle','post'],['/v1/attempts/{attemptId}/start','post'],['/v1/attempts/{attemptId}/start-with-lease','post'],['/v1/attempts/{attemptId}/complete-field-work','post'],['/v1/attempts/{attemptId}/checkout-not-completed','post'],['/v1/attempts/{attemptId}/bomb-room-reports','post'],['/v1/attempts/{attemptId}/photo-slots','get'],['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload','post'],['/v1/attempts/{attemptId}/photo-slots/{slotId}/photos/{photoItemId}/upload','post'],['/v1/attempts/{attemptId}/photo-slots/{slotId}/photos/{photoItemId}','delete'],['/v1/attempts/{attemptId}/submissions','get'],['/v1/attempts/{attemptId}/submissions','post'],['/v1/photos/{photoId}/content','get'],
    ['/v1/inspections','get'],['/v1/inspections/{submissionId}','get'],['/v1/inspections/{submissionId}/approve','post'],['/v1/inspections/{submissionId}/reject','post'],['/v1/inspections/{submissionId}/bomb-room-decision','post'],['/v1/notifications','get'],['/v1/notifications/{notificationId}/read','post'],
    ['/v1/payroll','get'],['/v1/payroll/entries','get'],['/v1/payroll/start','post'],['/v1/payroll/carry-forward','post'],['/v1/payroll/adjustments/corrections','post'],['/v1/payroll/adjustments/reversals','post'],['/v1/payroll/late-earnings/{earningId}/carry','post'],['/v1/payroll/payment-attempts/{attemptId}/check','post'],['/v1/payroll/payment-attempts/{attemptId}/paid','post'],['/v1/payroll/payment-attempts/{attemptId}/reopen','post'],
    ['/v1/complaints','get'],['/v1/complaints','post'],['/v1/complaints/{complaintId}','get'],['/v1/complaints/{complaintId}/history','get'],['/v1/complaints/{complaintId}/review','post'],['/v1/complaints/{complaintId}/decision','post'],['/v1/complaints/{complaintId}/corrections','post'],['/v1/complaints/{complaintId}/response','post'],['/v1/complaints/{complaintId}/close','post'],['/v1/complaints/{complaintId}/rework','post'],
    ['/v1/push-subscriptions/config','get'],['/v1/push-subscriptions','post'],['/v1/push-subscriptions/{subscriptionId}/retire','post'],
    ['/v1/room-types','get'],['/v1/reservations/bookability/preview','post'],['/v1/reservations/{reservationId}/room-change/preview','post'],['/v1/reservations/{reservationId}/room-change','post'],['/v1/cleaning-history','get'],['/v1/work-history','get']
  ];
  for(const [path,method] of requiredOperations)assert(paths[path]?.[method],`Missing ${method.toUpperCase()} ${path}`);
  const idempotentPosts=requiredOperations.filter(([,method])=>method==='post').filter(([path])=>!['/v1/assignments/preview','/v1/notifications/{notificationId}/read','/v1/reservations/bookability/preview','/v1/reservations/{reservationId}/room-change/preview'].includes(path));
  for(const [path] of idempotentPosts){const parameters=paths[path].post.parameters||[];assert(parameters.some(item=>item.name==='Idempotency-Key'&&item.in==='header'&&item.required===true),`Missing required Idempotency-Key on POST ${path}`);}
  assert(paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload'].post.requestBody?.content?.['image/jpeg'],'Photo upload must accept image/jpeg bytes.');
  assert(paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload'].post.requestBody?.content?.['image/webp'],'Photo upload must accept image/webp bytes.');
  const photoContent=paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload'].post.requestBody?.content||{};
  for(const mime of ['image/jpeg','image/webp','image/heic','image/heif'])assert(photoContent[mime]?.schema?.maxLength===5242880,`Photo upload ${mime} input must allow exactly 5MiB.`);
  assert(paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/upload'].post.description?.includes('300KiB'),'Photo upload must document the 300KiB normalized stored output.');
  const collectionPath=paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/photos/{photoItemId}'],collectionUpload=paths['/v1/attempts/{attemptId}/photo-slots/{slotId}/photos/{photoItemId}/upload']?.post,collectionContent=collectionUpload?.requestBody?.content||{};
  for(const mime of ['image/jpeg','image/webp','image/heic','image/heif'])assert(collectionContent[mime]?.schema?.maxLength===5242880,`Photo collection upload ${mime} input must allow exactly 5MiB.`);
  assert((collectionPath?.delete?.parameters||[]).some(item=>item.name==='Idempotency-Key'&&item.in==='header'&&item.required===true),'Photo collection DELETE must require Idempotency-Key.');
  assert(schemas.AttemptPhotoSlots?.properties?.slots?.items?.properties?.maxPhotos?.enum?.includes(10),'Attempt photo slots must expose maxPhotos 10.');
  assert(schemas.AttemptPhotoSlots?.properties?.slots?.items?.properties?.photos?.items?.$ref?.endsWith('/AttemptPhotoItem'),'Attempt photo slots must expose collection items.');
  assert(paths['/v1/availability/submissions'].post.description?.includes('어느 요일이든 직접 제출·변경'),'Availability submission must be open on every day and time.');
  assert(schemas.ErrorCode?.enum?.includes('AVAILABILITY_WEEK_OUT_OF_RANGE'),'Availability week-range error must be present.');
  assert(!schemas.ErrorCode?.enum?.includes('OUTSIDE_AVAILABILITY_WINDOW'),'Retired availability submission window error remains.');
  return schemas;
}
async function jsonFromProduction(){
  const response=await fetch(canonicalOpenApi,{cache:'no-store',redirect:'error',signal:AbortSignal.timeout(10000)});
  assert(response.ok,'Canonical OpenAPI fetch failed.');return response.json();
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
['ErrorCode','ErrorEnvelope','RoomProjection','RoomTypeCatalogItem','RoomTypeCatalogEnvelope','Reservation','ReservationType','ReservationRangePageEnvelope','ReservationCreateRequest','ReservationStandardCreateRequest','ReservationLongStayCreateRequest','ReservationChangeRequest','ReservationStandardChangeRequest','ReservationLongStayChangeRequest','ReservationBookabilityReasonCode','ReservationBookabilityCandidate','ReservationBookabilityPreviewRequest','ReservationBookabilityStandardPreviewRequest','ReservationBookabilityLongStayPreviewRequest','ReservationBookabilityPreview','ReservationBookabilityPreviewEnvelope','ReservationRoomMovePreviewRequest','ReservationRoomMovePreview','ReservationRoomMoveCommitRequest','ReservationRoomMoveResult','Assignment','AssignmentDraftRequest','AssignmentPreviewRequest','AssignmentPreviewResult','AssignmentCommitImpact','AssignmentCommitRequest','AssignmentCommitResult','AssignmentPrestartChangeRequest','AssignmentPrestartUnassignRequest','AssignmentCancellationRequest','AssignmentCancellationDecisionRequest','AssignmentChangeRequest','AssignmentChangeRequestPage','AttemptLifecycleRequest','AttemptLifecycleImpact','AttemptLifecycleResult','AttemptExecutionRequest','AttemptExecution','AttemptWithOfflineLease','CheckoutIncidentReportRequest','CheckoutIncidentDecisionRequest','CheckoutIncidentEnvelope','AttemptPhotoSlots','AttemptPhotoItem','PhotoUploadResponse','PhotoCollectionDeleteResponse','BombRoomReportRequest','BombRoomReportEnvelope','CreateSubmissionRequest','CleaningSubmission','SubmissionEnvelope','SubmissionListEnvelope','BombRoomDecisionRequest','InspectionDecisionRequest','BombRoomDecisionEnvelope','InspectionDecisionEnvelope','Notification','NotificationEnvelope','NotificationListEnvelope','CleaningHistoryItem','CleaningHistoryPage','WorkHistoryDay','WorkHistoryItem','WorkHistorySummary','WorkHistoryPage','RoomPinRevealRequest','RoomPinReveal','RoomPinRevealEnvelope','PublishCleaningTemplateRequest','PublishedCleaningTemplate','CleaningTemplateRoomTypeState','PayrollAdjustment','PayrollAdjustmentCorrectionRequest','PayrollAdjustmentEntry','PayrollAdjustmentEnvelope','PayrollAdjustmentReason','PayrollAdjustmentReversalRequest','PayrollCorrectionRequest','PayrollCycle','PayrollCycleEnvelope','PayrollEarningCorrectionRequest','PayrollEarningReversalRequest','PayrollEntriesEnvelope','PayrollItem','PayrollLateCarryRequest','PayrollLateEarning','PayrollListEnvelope','PayrollPaymentCheckRequest','PayrollPaymentPaidRequest','PayrollPaymentReopenRequest','PayrollPaymentResult','PayrollPaymentResultEnvelope','PayrollReversalRequest','PayrollStartRequest','PayrollStatus','Complaint','ComplaintCasRequest','ComplaintCategory','ComplaintCreateRequest','ComplaintDecision','ComplaintDecisionRequest','ComplaintEnvelope','ComplaintFinding','ComplaintHistoryEnvelope','ComplaintHistoryEvent','ComplaintListEnvelope','ComplaintMaidResponse','ComplaintResponseRequest','ComplaintReworkDecision','ComplaintReworkEnvelope','ComplaintReworkRequest','ComplaintStatus','WebPushSubscription','WebPushSubscriptionEnvelope','WebPushSubscriptionRegisterRequest','WebPushSubscriptionRetireRequest'].forEach(n=>needed.add(n));
let output=`// Generated from ${production?'the canonical OpenAPI v0.5.1':'an explicitly supplied OpenAPI v0.5.1 source'}.\n// Do not edit generated types directly.\n`;
for(const name of needed){assert(schemas[name],`Missing schema ${name}`);output+=`export type ${name} = ${type(schemas[name])};\n\n`;}
if(!checkOnly)await writeFile(resolve(root,'WIREFRAME/cleaning-api.d.ts'),output);
console.log(`[ok] ${production?'Canonical OpenAPI':'Source OpenAPI'}: 128 paths / 138 operations; anytime availability, room status, reservation bookability/range/move, cleaning, payroll, complaint, notification, and Web Push contracts verified. ${checkOnly?'Checked without writes.':'Client types regenerated.'}`);
