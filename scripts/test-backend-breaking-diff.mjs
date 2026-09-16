#!/usr/bin/env node

import { findBreakingChanges } from './openapi-breaking-diff-lib.mjs';

const schema = {
  openapi: '3.1.1',
  paths: {
    '/v1/items': {
      post: {
        operationId: 'createItem',
        parameters: [{ in: 'header', name: 'Idempotency-Key', required: true, schema: { type: 'string' } }],
        requestBody: { required: true, content: { 'application/json': { schema: { type: 'object', required: ['name'], properties: { name: { type: 'string' }, note: { type: ['string', 'null'] } } } } } },
        responses: { '201': { content: { 'application/json': { schema: { type: 'object', required: ['id'], properties: { id: { type: 'string' }, label: { type: 'string' } } } } } } },
      },
    },
  },
};
const clone = () => structuredClone(schema);
const assertBreaking = (mutate, expected) => {
  const changed = clone();
  mutate(changed);
  const differences = findBreakingChanges(schema, changed);
  if (!differences.some((difference) => difference.includes(expected))) throw new Error(`Expected breaking difference containing "${expected}", received:\n${differences.join('\n')}`);
};
const assertCompatible = (before, after, label) => {
  const differences = findBreakingChanges(before, after);
  if (differences.length) throw new Error(`${label} must remain compatible, received:\n${differences.join('\n')}`);
};

if (findBreakingChanges(schema, clone()).length) throw new Error('Identical OpenAPI documents must be compatible.');
const additive = clone();
additive.paths['/v1/items'].get = { operationId: 'listItems', responses: { '200': { content: { 'application/json': { schema: { type: 'array', items: { type: 'string' } } } } } } };
if (findBreakingChanges(schema, additive).length) throw new Error('Adding an operation must remain compatible.');

assertBreaking((changed) => delete changed.paths['/v1/items'], 'path was removed');
assertBreaking((changed) => { changed.paths['/v1/items'].post.operationId = 'replaceItem'; }, 'operationId changed');
assertBreaking((changed) => { changed.paths['/v1/items'].post.requestBody.content['application/json'].schema.required.push('note'); }, 'became required in request');
assertBreaking((changed) => { delete changed.paths['/v1/items'].post.responses['201'].content['application/json'].schema.properties.id; }, 'property was removed');
assertBreaking((changed) => { changed.paths['/v1/items'].post.parameters[0].schema.minLength = 10; }, 'minLength was narrowed');

const referencedBefore = clone();
referencedBefore.components = { schemas: { ItemRequest: referencedBefore.paths['/v1/items'].post.requestBody.content['application/json'].schema } };
referencedBefore.paths['/v1/items'].post.requestBody.content['application/json'].schema = { $ref: '#/components/schemas/ItemRequest' };
const referencedAfter = structuredClone(referencedBefore);
referencedAfter.components.schemas.ItemRequest.required.push('note');
if (!findBreakingChanges(referencedBefore, referencedAfter).some((difference) => difference.includes('became required in request'))) {
  throw new Error('Referenced request component changes must be detected.');
}

const requestEnumAddedBefore = clone();
const requestEnumAddedAfter = structuredClone(requestEnumAddedBefore);
requestEnumAddedAfter.paths['/v1/items'].post.requestBody.content['application/json'].schema.properties.name.enum = ['allowed'];
if (!findBreakingChanges(requestEnumAddedBefore, requestEnumAddedAfter).some((difference) => difference.includes('enum became incompatible for request'))) {
  throw new Error('Adding a request enum constraint must be detected as narrowing.');
}
const requestEnumRemovedBefore = structuredClone(requestEnumAddedAfter);
const requestEnumRemovedAfter = clone();
assertCompatible(requestEnumRemovedBefore, requestEnumRemovedAfter, 'Removing a request enum constraint');

const responseEnumRemovedBefore = clone();
responseEnumRemovedBefore.paths['/v1/items'].post.responses['201'].content['application/json'].schema.properties.label.enum = ['ready', 'done'];
const responseEnumRemovedAfter = structuredClone(responseEnumRemovedBefore);
delete responseEnumRemovedAfter.paths['/v1/items'].post.responses['201'].content['application/json'].schema.properties.label.enum;
if (!findBreakingChanges(responseEnumRemovedBefore, responseEnumRemovedAfter).some((difference) => difference.includes('enum became incompatible for response'))) {
  throw new Error('Removing a response enum guarantee must be detected as widening.');
}

const requestSchemaAddedBefore = clone();
delete requestSchemaAddedBefore.paths['/v1/items'].post.requestBody.content['application/json'].schema;
if (!findBreakingChanges(requestSchemaAddedBefore, clone()).some((difference) => difference.includes('request schema was added'))) {
  throw new Error('Adding a previously absent request schema must be detected.');
}

const responsePatternRemovedBefore = clone();
responsePatternRemovedBefore.paths['/v1/items'].post.responses['201'].content['application/json'].schema.properties.id.pattern = '^[a-z]+$';
const responsePatternRemovedAfter = structuredClone(responsePatternRemovedBefore);
delete responsePatternRemovedAfter.paths['/v1/items'].post.responses['201'].content['application/json'].schema.properties.id.pattern;
if (!findBreakingChanges(responsePatternRemovedBefore, responsePatternRemovedAfter).some((difference) => difference.includes('pattern became incompatible for response'))) {
  throw new Error('Removing a response pattern guarantee must be detected.');
}

const reorderedTypeBefore = clone();
const reorderedTypeAfter = clone();
reorderedTypeAfter.paths['/v1/items'].post.requestBody.content['application/json'].schema.properties.note.type = ['null', 'string'];
assertCompatible(reorderedTypeBefore, reorderedTypeAfter, 'Reordering a type union');

const requestAdditionalPropertiesBefore = clone();
requestAdditionalPropertiesBefore.paths['/v1/items'].post.requestBody.content['application/json'].schema.additionalProperties = true;
const requestAdditionalPropertiesAfter = structuredClone(requestAdditionalPropertiesBefore);
requestAdditionalPropertiesAfter.paths['/v1/items'].post.requestBody.content['application/json'].schema.additionalProperties = { type: 'string' };
if (!findBreakingChanges(requestAdditionalPropertiesBefore, requestAdditionalPropertiesAfter).some((difference) => difference.includes('additionalProperties narrowed for request'))) {
  throw new Error('Narrowing request additionalProperties from true to a schema must be detected.');
}

const responseAdditionalPropertiesBefore = clone();
responseAdditionalPropertiesBefore.paths['/v1/items'].post.responses['201'].content['application/json'].schema.additionalProperties = { type: 'string' };
const responseAdditionalPropertiesAfter = structuredClone(responseAdditionalPropertiesBefore);
responseAdditionalPropertiesAfter.paths['/v1/items'].post.responses['201'].content['application/json'].schema.additionalProperties = true;
if (!findBreakingChanges(responseAdditionalPropertiesBefore, responseAdditionalPropertiesAfter).some((difference) => difference.includes('additionalProperties guarantee widened for response'))) {
  throw new Error('Widening response additionalProperties from a schema to true must be detected.');
}

const exclusiveMinimumBefore = clone();
exclusiveMinimumBefore.paths['/v1/items'].post.requestBody.content['application/json'].schema.properties.name = { type: 'number', exclusiveMinimum: 0 };
const exclusiveMinimumAfter = structuredClone(exclusiveMinimumBefore);
exclusiveMinimumAfter.paths['/v1/items'].post.requestBody.content['application/json'].schema.properties.name.exclusiveMinimum = 1;
if (!findBreakingChanges(exclusiveMinimumBefore, exclusiveMinimumAfter).some((difference) => difference.includes('exclusiveMinimum was narrowed'))) {
  throw new Error('Increasing a request exclusiveMinimum must be detected.');
}

const requestAnyOfBefore = clone();
requestAnyOfBefore.paths['/v1/items'].post.requestBody.content['application/json'].schema.properties.name = {
  anyOf: [{ type: 'string' }],
};
const requestAnyOfAfter = structuredClone(requestAnyOfBefore);
requestAnyOfAfter.paths['/v1/items'].post.requestBody.content['application/json'].schema.properties.name.anyOf.push({ type: 'number' });
assertCompatible(requestAnyOfBefore, requestAnyOfAfter, 'Adding a request anyOf alternative');

process.stdout.write('OpenAPI 3.1 breaking-diff regression tests passed.\n');
