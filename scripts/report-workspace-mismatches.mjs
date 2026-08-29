#!/usr/bin/env node

import { readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const sourcePath = resolve('scripts/check-workspace.mjs');
const reportPath = resolve('scripts/.check-workspace-report.generated.mjs');
let source = readFileSync(sourcePath, 'utf8');
source = source.replaceAll('throw new Error(', 'console.error(');
source += '\nconsole.log("WORKSPACE_MISMATCH_REPORT_COMPLETE");\n';
writeFileSync(reportPath, source, 'utf8');
try {
  const result = spawnSync(process.execPath, [reportPath], { encoding: 'utf8' });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  console.log(`WORKSPACE_MISMATCH_REPORT_EXIT=${result.status ?? 'null'}`);
} finally {
  unlinkSync(reportPath);
}
