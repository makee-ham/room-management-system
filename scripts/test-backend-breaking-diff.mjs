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

process.stdout.write('OpenAPI 3.1 breaking-diff regression tests passed.\n');
