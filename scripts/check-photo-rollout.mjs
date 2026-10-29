#!/usr/bin/env node

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const fixture = await mkdtemp(path.join(tmpdir(), "rms-photo-rollout-"));
const env = { ...process.env };
for (const key of Object.keys(env)) {
  if (key.startsWith("RMS_") || key.startsWith("SUPABASE_")) delete env[key];
}
Object.assign(env, {
  RMS_API_BASE_URL: "https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api",
  SUPABASE_URL: "https://aodikrxcczbogjpsjwjt.supabase.co",
  SUPABASE_PUBLISHABLE_KEY: "sb_publishable_qa_fixture_not_a_real_key_1234567890",
  RMS_SESSION_PERSISTENCE: "session",
  VERCEL_GIT_COMMIT_SHA: "1111111111111111111111111111111111111111",
});

async function build(overrides = {}) {
  execFileSync(process.execPath, [path.join(fixture, "scripts/build-pages-artifact.mjs")], {
    cwd: fixture,
    env: { ...env, ...overrides },
    stdio: "pipe",
  });
  return JSON.parse(await readFile(path.join(fixture, "_site/runtime-config.json"), "utf8"));
}

try {
  await mkdir(path.join(fixture, "scripts"));
  await mkdir(path.join(fixture, "WIREFRAME"));
  await copyFile(path.join(root, "scripts/build-pages-artifact.mjs"), path.join(fixture, "scripts/build-pages-artifact.mjs"));
  await copyFile(path.join(root, "scripts/serve.py"), path.join(fixture, "scripts/serve.py"));
  await writeFile(path.join(fixture, "WIREFRAME/index.html"), "<!doctype html><title>QA</title>");
  await copyFile(path.join(root, "WIREFRAME/sw.js"), path.join(fixture, "WIREFRAME/sw.js"));
  for (const channel of ["production", "preview"]) {
    const config = await build({ RMS_DEPLOYMENT_CHANNEL: channel });
    const buildInfo=JSON.parse(await readFile(path.join(fixture,"_site/build-info.json"),"utf8"));
    assert.equal(buildInfo.sourceCommit,env.VERCEL_GIT_COMMIT_SHA);assert.equal(buildInfo.deploymentChannel,channel);assert.equal(buildInfo.indexSha256.length,64);assert.equal(buildInfo.serviceWorkerVersion,"2026-10-29-7");
    assert.equal(config.mode, "live");
    assert.equal(config.deploymentChannel, channel);
    assert.equal(config.featureFlags.photoUploadSnapshot, true);
    assert.equal(config.featureFlags.optionalCleaningWorkflow, true);
    assert.equal(config.featureFlags.assignmentPlanningDate, true);
    assert.equal(config.featureFlags.roomPinExport, true);
    assert.equal(config.featureFlags.roomPinTransfer, false);
    assert.equal(config.featureFlags.supplementalMemoOnly, true);
    assert.equal((await build({ RMS_DEPLOYMENT_CHANNEL: channel, RMS_SUPPLEMENTAL_MEMO_ONLY: "false" })).featureFlags.supplementalMemoOnly, false);
    assert.equal((await build({ RMS_SUPPLEMENTAL_MEMO_ONLY: "true" })).featureFlags.supplementalMemoOnly, true);
    const rollback = await build({ RMS_DEPLOYMENT_CHANNEL: channel, RMS_ASSIGNMENT_PLANNING_DATE: "false", RMS_ROOM_PIN_EXPORT: "false" });
    assert.equal(rollback.featureFlags.assignmentPlanningDate, false);
    assert.equal(rollback.featureFlags.roomPinExport, false);
    assert.equal(rollback.featureFlags.roomPinTransfer, false);
    assert.equal((await build({ RMS_DEPLOYMENT_CHANNEL: channel, RMS_PHOTO_UPLOAD_SNAPSHOT: "false" })).featureFlags.photoUploadSnapshot, false);
  }
  await writeFile(path.join(fixture, ".env.local"), "RMS_PHOTO_UPLOAD_SNAPSHOT=false\n");
  assert.equal((await build()).featureFlags.photoUploadSnapshot, false);
  assert.equal((await build({ RMS_PHOTO_UPLOAD_SNAPSHOT: "true" })).featureFlags.photoUploadSnapshot, true);
  const serveConfig = overrides => JSON.parse(execFileSync(process.env.RMS_QA_PYTHON || "python3", ["-c", "import json,runpy; print(json.dumps(runpy.run_path('scripts/serve.py')['load_runtime_config']()))"], { cwd: fixture, env: { ...env, ...overrides }, encoding: "utf8" }));
  assert.deepEqual(serveConfig({}).featureFlags, (await build()).featureFlags);
  const rollbackFlags = { RMS_ASSIGNMENT_PLANNING_DATE: "false", RMS_ROOM_PIN_EXPORT: "false", RMS_ROOM_PIN_TRANSFER: "true" };
  assert.deepEqual(serveConfig(rollbackFlags).featureFlags, (await build(rollbackFlags)).featureFlags);
  assert.deepEqual(await build({ RMS_RUNTIME_MODE: "demo" }), { mode: "demo" });
  console.log("Rollout: production/preview photo snapshot, planning dates and PIN export and memo-only reports on; Drive import off; rollback, precedence and demo isolation passed.");
} finally {
  await rm(fixture, { recursive: true, force: true });
}
