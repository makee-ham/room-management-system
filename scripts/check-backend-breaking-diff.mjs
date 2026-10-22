#!/usr/bin/env node

import { readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

import { findBreakingChanges } from './openapi-breaking-diff-lib.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const currentPath = resolve(root, 'contracts/backend-openapi.json');
const args = process.argv.slice(2);
const valueAfter = (name) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
};
const explicitBaseFile = valueAfter('--base-file');
const baseRef = valueAfter('--base-ref') || process.env.CONTRACT_BASE_REF || 'origin/dev';
let basePath = explicitBaseFile ? resolve(root, explicitBaseFile) : undefined;
let temporaryBasePath;

if (!basePath) {
  const shown = spawnSync('git', ['show', `${baseRef}:contracts/backend-openapi.json`], { cwd: root, encoding: 'utf8', maxBuffer: 20 * 1024 * 1024 });
  if (shown.status !== 0) {
    const revision=spawnSync('git',['rev-parse','--verify',`${baseRef}^{commit}`],{cwd:root,encoding:'utf8'});
    if(revision.status!==0)throw new Error('Contract base commit could not be resolved.');
    const listed=spawnSync('git',['ls-tree','--name-only',baseRef,'--','contracts/backend-openapi.json'],{cwd:root,encoding:'utf8'});
    if(listed.status!==0||listed.stdout.trim())throw new Error('Contract base snapshot could not be read.');
    process.stdout.write(`No contract snapshot exists at ${baseRef}; accepting this change as the initial baseline.\n`);
    process.exit(0);
  }
  temporaryBasePath = resolve(root, `.backend-openapi-base-${process.pid}.tmp`);
  basePath = temporaryBasePath;
  await writeFile(basePath, shown.stdout, 'utf8');
}

try {
  const [base, current] = await Promise.all([readFile(basePath, 'utf8').then(JSON.parse), readFile(currentPath, 'utf8').then(JSON.parse)]);
  const breaking = findBreakingChanges(base, current);
  if (breaking.length) throw new Error(`Breaking OpenAPI changes found:\n- ${breaking.join('\n- ')}`);
  process.stdout.write(`No breaking OpenAPI changes found against ${explicitBaseFile || baseRef}.\n`);
} finally {
  if (temporaryBasePath) await rm(temporaryBasePath, { force: true });
}
