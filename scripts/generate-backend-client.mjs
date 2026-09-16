#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import openapiTS, { astToString } from 'openapi-typescript';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const snapshotPath = resolve(root, 'contracts/backend-openapi.json');
const generatedPath = resolve(root, 'WIREFRAME/generated/backend-api.d.ts');
const manifestPath = resolve(root, 'contracts/backend-openapi.manifest.json');
const backendSourceCommit = 'c32aa9eec3945334ddda956afc62cc92d801c410';

const snapshotBytes = await readFile(snapshotPath);
const document = JSON.parse(snapshotBytes.toString('utf8'));
const generated = astToString(await openapiTS(document));
const operations = Object.values(document.paths).reduce(
  (count, pathItem) => count + Object.keys(pathItem).filter((method) => ['get', 'post', 'put', 'patch', 'delete'].includes(method)).length,
  0,
);
const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const manifest = {
  schemaVersion: 1,
  backendRepository: 'https://github.com/wrongstory/room-management-system-backend',
  backendSourceCommit,
  backendSourceCommand: 'npm run openapi:export:full',
  backendSourcePath: 'supabase/functions/_shared/openapi.ts',
  openapiVersion: document.openapi,
  apiVersion: document.info.version,
  pathCount: Object.keys(document.paths).length,
  operationCount: operations,
  snapshotSha256: sha256(snapshotBytes),
  generatedWith: 'openapi-typescript@7.13.0',
  generatedSha256: sha256(generated),
};

await mkdir(dirname(generatedPath), { recursive: true });
await writeFile(generatedPath, generated, 'utf8');
await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
process.stdout.write(`Generated ${manifest.operationCount} operations from backend ${backendSourceCommit.slice(0, 12)}.\n`);
