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
  await writeFile(path.join(fixture, "WIREFRAME/index.html"), "<!doctype html><title>QA</title>");
  for (const channel of ["production", "preview"]) {
    const config = await build({ RMS_DEPLOYMENT_CHANNEL: channel });
    assert.equal(config.mode, "live");
    assert.equal(config.deploymentChannel, channel);
    assert.equal(config.featureFlags.photoUploadSnapshot, true);
    assert.equal(config.featureFlags.optionalCleaningWorkflow, true);
    assert.equal((await build({ RMS_DEPLOYMENT_CHANNEL: channel, RMS_PHOTO_UPLOAD_SNAPSHOT: "false" })).featureFlags.photoUploadSnapshot, false);
  }
  await writeFile(path.join(fixture, ".env.local"), "RMS_PHOTO_UPLOAD_SNAPSHOT=false\n");
  assert.equal((await build()).featureFlags.photoUploadSnapshot, false);
  assert.equal((await build({ RMS_PHOTO_UPLOAD_SNAPSHOT: "true" })).featureFlags.photoUploadSnapshot, true);
  assert.deepEqual(await build({ RMS_RUNTIME_MODE: "demo" }), { mode: "demo" });
  console.log("Photo snapshot rollout: production/preview default on, explicit rollback, environment precedence, demo isolation passed.");
} finally {
  await rm(fixture, { recursive: true, force: true });
}
