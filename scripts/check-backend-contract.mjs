#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import openapiTS, { astToString } from 'openapi-typescript';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const snapshotBytes = await readFile(resolve(root, 'contracts/backend-openapi.json'));
const generated = await readFile(resolve(root, 'WIREFRAME/generated/backend-api.d.ts'), 'utf8');
const manifest = JSON.parse(await readFile(resolve(root, 'contracts/backend-openapi.manifest.json'), 'utf8'));
const document = JSON.parse(snapshotBytes.toString('utf8'));
const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const assert = (condition, message) => {
  if (!condition) throw new Error(message);
};

const operations = [];
for (const [path, pathItem] of Object.entries(document.paths)) {
  for (const [method, operation] of Object.entries(pathItem)) {
    if (['get', 'post', 'put', 'patch', 'delete'].includes(method)) operations.push({ path, method, operation, pathItem });
  }
}

assert(document.openapi === '3.1.1', `Unexpected OpenAPI version: ${document.openapi}`);
assert(document.info.version === '0.2.0', `Unexpected API version: ${document.info.version}`);
assert(Object.keys(document.paths).length === 109, 'Backend path inventory changed; refresh and review the snapshot.');
assert(operations.length === 117, 'Backend operation inventory changed; refresh and review the snapshot.');
assert(document.servers?.length === 1 && document.servers[0].url === 'https://example.supabase.co/functions/v1/api', 'Snapshot must contain only the non-secret example server.');
assert(!snapshotBytes.toString('utf8').includes('aodikrxcczbogjpsjwjt'), 'Production project ref must not be committed in the generated contract snapshot.');

const operationIds = operations.map(({ operation }) => operation.operationId);
assert(operationIds.every(Boolean), 'Every operation must define operationId for stable client generation.');
assert(new Set(operationIds).size === operationIds.length, 'operationId values must be unique.');

const requiredAreas = {
  auth: /^\/v1\/auth\//,
  account: /^\/v1\/accounts(?:\/|$)/,
  room: /^\/v1\/rooms(?:\/|$)/,
  reservation: /^\/v1\/reservations(?:\/|$)/,
  availability: /^\/v1\/availability(?:\/|$)/,
  assignment: /^\/v1\/(?:assignments|assignment-change-requests|assignment-preview)(?:\/|$)/,
  attempt: /^\/v1\/(?:attempts|limited\/attempts)(?:\/|$)/,
  submission: /^\/v1\/attempts\/\{attemptId\}\/submissions$/,
  inspection: /^\/v1\/inspections(?:\/|$)/,
  payroll: /^\/v1\/payroll(?:\/|$)/,
  notification: /^\/v1\/(?:notifications|push-subscriptions)(?:\/|$)/,
  pin: /^\/v1\/(?:rooms\/.*pin|room-pin-sheet-sync)(?:\/|$)/,
};
for (const [area, pattern] of Object.entries(requiredAreas)) {
  assert(operations.some(({ path }) => pattern.test(path)), `Required ${area} API area is missing.`);
}

const resolveRef = (schema, seen = new Set()) => {
  if (!schema?.$ref) return schema;
  assert(!seen.has(schema.$ref), `Circular schema reference while resolving ${schema.$ref}`);
  seen.add(schema.$ref);
  return resolveRef(schema.$ref.slice(2).split('/').reduce((value, key) => value[key], document), seen);
};
const operationParameters = ({ operation, pathItem }) => {
  const parameters = new Map();
  for (const parameterInput of [...(pathItem.parameters ?? []), ...(operation.parameters ?? [])]) {
    const parameter = resolveRef(parameterInput);
    parameters.set(`${parameter.in}:${parameter.name}`, parameter);
  }
  return [...parameters.values()];
};
const assertExactOperationSet = (actualOperations, expectedIds, label) => {
  const actualIds = actualOperations.map(({ operation }) => operation.operationId).sort();
  const expected = [...expectedIds].sort();
  assert(
    JSON.stringify(actualIds) === JSON.stringify(expected),
    `${label} operation inventory changed. Expected ${expected.join(', ')}; received ${actualIds.join(', ')}.`,
  );
};
const schemaHasProperty = (schema, property, seen = new Set()) => {
  schema = resolveRef(schema, seen);
  if (!schema || typeof schema !== 'object') return false;
  if (schema.properties && Object.hasOwn(schema.properties, property)) return true;
  return ['allOf', 'anyOf', 'oneOf'].some((key) => schema[key]?.some((item) => schemaHasProperty(item, property, new Set(seen))));
};
const schemaRequiresProperty = (schema, property, seen = new Set()) => {
  schema = resolveRef(schema, seen);
  if (!schema || typeof schema !== 'object') return false;
  if (schema.required?.includes(property)) return true;
  if (schema.allOf?.some((item) => schemaRequiresProperty(item, property, new Set(seen)))) return true;
  for (const key of ['anyOf', 'oneOf']) {
    if (schema[key]?.length && schema[key].every((item) => schemaRequiresProperty(item, property, new Set(seen)))) return true;
  }
  return false;
};

const allowedWithoutIdempotency = new Set([
  'login',
  'runDeveloperDiagnostics',
  'syncOfflineCompletion',
  'previewAssignments',
  'markNotificationRead',
  'revealRoomPin',
]);
for (const entry of operations.filter(({ method }) => method !== 'get')) {
  const { method, operation } = entry;
  const parameters = operationParameters(entry);
  assert(
    allowedWithoutIdempotency.has(operation.operationId) || parameters.some((parameter) => parameter.name === 'Idempotency-Key' && parameter.in === 'header' && parameter.required === true),
    `${method.toUpperCase()} ${operation.operationId} is missing Idempotency-Key.`,
  );
}

const casOperations = operations.filter(({ operation }) => schemaHasProperty(resolveRef(operation.requestBody)?.content?.['application/json']?.schema, 'expectedVersion'));
assertExactOperationSet(casOperations, [
  'cancelManualCleaningRequest',
  'cancelReservation',
  'carryForwardPayrollCycle',
  'carryLatePayrollEarning',
  'changeReservation',
  'changeRoomMasterData',
  'closeComplaint',
  'confirmAssignmentDurationPolicy',
  'correctComplaintDecision',
  'createComplaint',
  'decideAvailabilityChange',
  'decideCheckoutIncident',
  'decideComplaint',
  'manualCheckoutReservation',
  'materializeComplaintRework',
  'publishCleaningTemplate',
  'recordPayrollCorrection',
  'recordPayrollPaymentCheck',
  'recordPayrollPaymentPaid',
  'reopenPayrollPaymentAttempt',
  'requestAvailabilityChange',
  'requestRoomPinSheetFullResync',
  'respondComplaint',
  'retireWebPushSubscription',
  'reversePayrollSource',
  'startComplaintReview',
  'startPayrollCycle',
  'submitAvailability',
], 'CAS');
for (const { method, operation } of casOperations) {
  const requestSchema = resolveRef(operation.requestBody)?.content?.['application/json']?.schema;
  assert(schemaRequiresProperty(requestSchema, 'expectedVersion'), `${method.toUpperCase()} ${operation.operationId} must require expectedVersion.`);
}

const cursorOperations = operations.filter((entry) => operationParameters(entry).some((parameter) => parameter.name === 'cursor' && parameter.in === 'query'));
assertExactOperationSet(cursorOperations, [
  'listAssignmentChangeRequests',
  'listComplaintHistory',
  'listComplaints',
  'listDeveloperActivityEvents',
  'listDeveloperAuditEvents',
  'listNotifications',
  'listOfflineQuarantines',
  'listPayrollCycles',
  'listPayrollEntries',
], 'cursor');

const errorEnvelopeRef = '#/components/schemas/ErrorEnvelope';
const allowedWithoutStandardErrors = new Set(['getHealth', 'getOpenApiDocument', 'getSwaggerUi']);
for (const { path, method, operation } of operations) {
  const errorResponses = Object.entries(operation.responses ?? {}).filter(([status]) => Number(status) >= 400);
  assert(
    allowedWithoutStandardErrors.has(operation.operationId) || errorResponses.length > 0,
    `${method.toUpperCase()} ${path} has no standard error response.`,
  );
  for (const [status, responseInput] of errorResponses) {
    const response = resolveRef(responseInput);
    const responseRef = response.content?.['application/json']?.schema?.$ref;
    const previewConflict = operation.operationId === 'previewAssignments' && status === '409' && responseRef === '#/components/schemas/AssignmentPreviewUnconfirmed';
    assert(responseRef === errorEnvelopeRef || previewConflict, `${method.toUpperCase()} ${path} ${status} lost the stable error envelope.`);
  }
}

const forbiddenPropertyNames = new Set(['serviceRoleKey', 'supabaseServiceRoleKey', 'pinPlaintext', 'pinHash', 'pinCiphertext', 'accessTokenHash', 'refreshTokenHash']);
const visitProperties = (value, location = '#') => {
  if (!value || typeof value !== 'object') return;
  if (value.properties) {
    for (const key of Object.keys(value.properties)) assert(!forbiddenPropertyNames.has(key), `Forbidden sensitive field ${key} exposed at ${location}.`);
  }
  for (const [key, child] of Object.entries(value)) visitProperties(child, `${location}/${key}`);
};
visitProperties(document.components?.schemas);

assert(manifest.backendSourceCommit === 'c32aa9eec3945334ddda956afc62cc92d801c410', 'Backend source commit identity changed without regeneration review.');
assert(manifest.snapshotSha256 === sha256(snapshotBytes), 'OpenAPI snapshot hash does not match the manifest.');
assert(manifest.generatedSha256 === sha256(generated), 'Generated TypeScript hash does not match the manifest.');
assert(manifest.pathCount === Object.keys(document.paths).length && manifest.operationCount === operations.length, 'Manifest inventory is stale.');
assert(generated === astToString(await openapiTS(document)), 'Generated TypeScript is stale; run npm run contract:generate.');

process.stdout.write(`Contract check passed: ${manifest.pathCount} paths / ${manifest.operationCount} operations / ${casOperations.length} CAS commands / ${cursorOperations.length} cursor lists.\n`);
