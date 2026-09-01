#!/usr/bin/env node

import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const WIREFRAME = path.join(ROOT, "WIREFRAME");
const OUTPUT = path.join(ROOT, "_site");
const DOCUMENTED_PROJECT_REF = "aodikrxcczbogjpsjwjt";

function parseEnv(source) {
  const values = {};
  for (const rawLine of source.split(/\r?\n/u)) {
    let line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    if (line.startsWith("export ")) line = line.slice(7).trimStart();
    const separator = line.indexOf("=");
    if (separator < 1) continue;
    const name = line.slice(0, separator).trim();
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/u.test(name)) continue;
    let value = line.slice(separator + 1).trim();
    if (value.length >= 2 && value[0] === value.at(-1) && ['"', "'"].includes(value[0])) {
      value = value.slice(1, -1);
    } else {
      value = value.replace(/\s+#.*$/u, "").trimEnd();
    }
    values[name] = value;
  }
  return values;
}

async function localEnvironment() {
  try {
    return parseEnv(await readFile(path.join(ROOT, ".env.local"), "utf8"));
  } catch (error) {
    if (error?.code === "ENOENT") return {};
    throw error;
  }
}

function projectRef(value, expectedPath) {
  try {
    const url = new URL(value);
    const normalizedPath = url.pathname.replace(/\/+$/u, "");
    const host = url.hostname.match(/^([a-z0-9]+)\.supabase\.co$/u);
    if (
      url.protocol !== "https:" || url.username || url.password || url.port ||
      url.search || url.hash || normalizedPath !== expectedPath.replace(/\/+$/u, "") || !host
    ) return null;
    return host[1];
  } catch {
    return null;
  }
}

function isBrowserPublishableKey(value) {
  if (/^sb_publishable_[A-Za-z0-9_-]{20,}$/u.test(value)) return true;
  if (!/^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/u.test(value)) return false;
  try {
    return JSON.parse(Buffer.from(value.split(".")[1], "base64url").toString("utf8"))?.role === "anon";
  } catch {
    return false;
  }
}

const fileValues = await localEnvironment();
const value = (name, fallback = "") => String(process.env[name] ?? fileValues[name] ?? fallback).trim();
const runtimeMode = value("RMS_RUNTIME_MODE", "live").toLowerCase();
if (!["demo", "live"].includes(runtimeMode)) {
  throw new Error("Pages runtime mode must be demo or live.");
}

let config;
let projectReference = null;
if (runtimeMode === "demo") {
  config = { mode: "demo" };
} else {
  config = {
    mode: "live",
    apiBaseUrl: value("RMS_API_BASE_URL").replace(/\/+$/u, ""),
    supabaseUrl: value("SUPABASE_URL").replace(/\/+$/u, ""),
    supabasePublishableKey: value("SUPABASE_PUBLISHABLE_KEY"),
    sessionPersistence: value("RMS_SESSION_PERSISTENCE", "session").toLowerCase(),
  };
  const refs = [
    projectRef(config.apiBaseUrl, "/functions/v1/api"),
    projectRef(config.supabaseUrl, ""),
  ];
  if (
    !refs.every(Boolean) || new Set(refs).size !== 1 || refs[0] !== DOCUMENTED_PROJECT_REF ||
    !isBrowserPublishableKey(config.supabasePublishableKey) ||
    !["local", "session"].includes(config.sessionPersistence)
  ) {
    throw new Error("Pages runtime configuration is missing or not browser-safe.");
  }
  projectReference = refs[0];
}

await rm(OUTPUT, { recursive: true, force: true });
await mkdir(OUTPUT, { recursive: true });
await cp(WIREFRAME, OUTPUT, { recursive: true });
await writeFile(
  path.join(OUTPUT, "runtime-config.json"),
  `${JSON.stringify(config)}\n`,
  { encoding: "utf8", mode: 0o600 },
);
console.log(
  runtimeMode === "demo"
    ? "Pages artifact prepared in demo mode without production credentials."
    : `Pages artifact prepared for Supabase project ${projectReference}.`,
);
