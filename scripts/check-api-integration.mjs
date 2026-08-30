#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ENV_FILE = path.join(ROOT, ".env.local");
const DOCUMENTED_PROJECT_REF = "aodikrxcczbogjpsjwjt";
const REQUIRE_DEDICATED_ORIGIN = process.env.RMS_REQUIRE_DEDICATED_ORIGIN === "true";
const TEST_ORIGIN = String(
  process.env.RMS_TEST_ORIGIN || (REQUIRE_DEDICATED_ORIGIN ? "" : "http://127.0.0.1:4173"),
).replace(/\/+$/u, "");
const ACTUAL_APP_ORIGIN = String(process.env.RMS_ACTUAL_APP_ORIGIN || "").replace(/\/+$/u, "");
const REQUIRED_PATHS = new Map([
  ["/health", ["get"]],
  ["/openapi.json", ["get"]],
  ["/docs", ["get"]],
  ["/v1/auth/login", ["post"]],
  ["/v1/auth/me", ["get"]],
  ["/v1/auth/password", ["post"]],
  ["/v1/accounts", ["get", "post"]],
  ["/v1/accounts/{profileId}/role", ["patch"]],
  ["/v1/accounts/{profileId}/status", ["patch"]],
  ["/v1/accounts/{profileId}/unlock", ["post"]],
  ["/v1/accounts/{profileId}/password-reset", ["post"]],
  ["/v1/rooms", ["get"]],
]);

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
    if (
      value.length >= 2 &&
      ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'")))
    ) {
      value = value.slice(1, -1);
    } else {
      value = value.replace(/\s+#.*$/u, "").trimEnd();
    }
    values[name] = value;
  }
  return values;
}

async function loadEnvironment() {
  let fileValues = {};
  try {
    fileValues = parseEnv(await readFile(ENV_FILE, "utf8"));
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
  return {
    apiBaseUrl: process.env.RMS_API_BASE_URL ?? fileValues.RMS_API_BASE_URL ?? "",
    supabaseUrl: process.env.SUPABASE_URL ?? fileValues.SUPABASE_URL ?? "",
    supabasePublishableKey:
      process.env.SUPABASE_PUBLISHABLE_KEY ?? fileValues.SUPABASE_PUBLISHABLE_KEY ?? "",
  };
}

function projectRefFromUrl(value, expectedPath) {
  try {
    const url = new URL(value);
    const normalizedPath = url.pathname.replace(/\/+$/u, "");
    if (
      url.protocol !== "https:" ||
      url.username ||
      url.password ||
      url.port ||
      url.search ||
      url.hash ||
      normalizedPath !== expectedPath.replace(/\/+$/u, "")
    ) {
      return null;
    }
    const match = url.hostname.toLowerCase().match(/^([a-z0-9]+)\.supabase\.co$/u);
    return match?.[1] ?? null;
  } catch {
    return null;
  }
}

function isBrowserPublishableKey(value) {
  if (/^sb_publishable_[A-Za-z0-9_-]{20,}$/u.test(value)) return true;
  if (!/^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/u.test(value)) return false;
  try {
    const payload = JSON.parse(Buffer.from(value.split(".")[1], "base64url").toString("utf8"));
    return payload?.role === "anon";
  } catch {
    return false;
  }
}

function testPublishableKeyGuard() {
  const encoded = (value) => Buffer.from(JSON.stringify(value)).toString("base64url");
  const jwt = (role) => `${encoded({ alg: "HS256", typ: "JWT" })}.${encoded({ role })}.test-signature`;
  assert(isBrowserPublishableKey(jwt("anon")), "legacy anon JWT를 허용해야 합니다.");
  assert(!isBrowserPublishableKey(jwt("service_role")), "service_role JWT를 브라우저 설정으로 허용하면 안 됩니다.");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function checkTestOrigin() {
  assert(TEST_ORIGIN, "배포용 전용 origin 환경변수가 비어 있습니다.");
  let url;
  try {
    url = new URL(TEST_ORIGIN);
  } catch {
    throw new Error("CORS 검사 origin이 올바른 URL이 아닙니다.");
  }
  assert(["http:", "https:"].includes(url.protocol), "CORS 검사 origin은 HTTP(S)여야 합니다.");
  assert(url.origin === TEST_ORIGIN, "CORS 검사값에는 origin만 넣어야 합니다.");
  if (REQUIRE_DEDICATED_ORIGIN) {
    assert(url.protocol === "https:", "운영 배포 origin은 HTTPS여야 합니다.");
    assert(
      url.hostname !== "makee-ham.github.io",
      "공유 GitHub Pages origin에는 운영 로그인 토큰을 배포하지 않습니다.",
    );
    assert(ACTUAL_APP_ORIGIN, "GitHub Pages가 보고한 실제 origin이 비어 있습니다.");
    let actualUrl;
    try {
      actualUrl = new URL(ACTUAL_APP_ORIGIN);
    } catch {
      throw new Error("GitHub Pages의 실제 origin이 올바른 URL이 아닙니다.");
    }
    assert(actualUrl.origin === ACTUAL_APP_ORIGIN, "GitHub Pages의 실제 주소에는 origin만 있어야 합니다.");
    assert(ACTUAL_APP_ORIGIN === TEST_ORIGIN, "설정한 전용 origin과 실제 GitHub Pages origin이 다릅니다.");
  }
}

function headerTokens(headers, name) {
  return new Set(
    (headers.get(name) ?? "")
      .toLowerCase()
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean),
  );
}

async function checkedFetch(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      ...options,
      redirect: "error",
      signal: AbortSignal.timeout(10_000),
    });
  } catch {
    throw new Error("운영 API 네트워크 요청에 실패했습니다.");
  }
  return response;
}

function checkProjectRefs(config) {
  const refs = [
    projectRefFromUrl(config.apiBaseUrl, "/functions/v1/api"),
    projectRefFromUrl(config.supabaseUrl, ""),
  ];
  assert(refs.every(Boolean), "운영 공개 URL이 비어 있거나 project ref를 확인할 수 없습니다.");
  assert(new Set(refs).size === 1, "운영 공개 환경변수의 Supabase project ref가 서로 다릅니다.");
  assert(refs[0] === DOCUMENTED_PROJECT_REF, "운영 project ref가 연동 문서의 정본과 다릅니다.");
  assert(isBrowserPublishableKey(config.supabasePublishableKey), "브라우저용 Supabase publishable key 형식이 아닙니다.");
}

async function checkHealth(apiBaseUrl) {
  const response = await checkedFetch(`${apiBaseUrl}/health`, {
    headers: { Accept: "application/json", Origin: TEST_ORIGIN },
  });
  assert(response.status === 200, "health 응답이 200이 아닙니다.");
  assert(response.headers.get("cache-control")?.includes("no-store"), "health 응답에 no-store가 없습니다.");
  assert(response.headers.get("sb-project-ref") === DOCUMENTED_PROJECT_REF, "health 응답 project ref가 다릅니다.");
  let body;
  try {
    body = await response.json();
  } catch {
    throw new Error("health 응답이 JSON이 아닙니다.");
  }
  assert(body?.status === "ok", "health 응답 상태가 ok가 아닙니다.");
}

async function checkSupabasePublishableKey(config) {
  const response = await checkedFetch(`${config.supabaseUrl.replace(/\/+$/u, "")}/auth/v1/settings`, {
    headers: {
      Accept: "application/json",
      apikey: config.supabasePublishableKey,
      Origin: TEST_ORIGIN,
    },
  });
  assert(response.status === 200, "Supabase publishable key가 운영 project에서 거부됐습니다.");
  assert(
    response.headers.get("sb-project-ref") === DOCUMENTED_PROJECT_REF,
    "Supabase publishable key 확인 응답의 project ref가 다릅니다.",
  );
}

async function checkOpenApi(apiBaseUrl) {
  const response = await checkedFetch(`${apiBaseUrl}/openapi.json`, {
    headers: { Accept: "application/json", Origin: TEST_ORIGIN },
  });
  assert(response.status === 200, "OpenAPI 응답이 200이 아닙니다.");
  assert(response.headers.get("sb-project-ref") === DOCUMENTED_PROJECT_REF, "OpenAPI 응답 project ref가 다릅니다.");
  let document;
  try {
    document = await response.json();
  } catch {
    throw new Error("OpenAPI 응답이 JSON이 아닙니다.");
  }
  assert(document?.info?.version === "0.2.0", "OpenAPI info.version이 0.2.0이 아닙니다.");
  assert(/^3\.1(?:\.|$)/u.test(document?.openapi ?? ""), "OpenAPI 문서 버전이 3.1 계열이 아닙니다.");
  for (const [endpoint, methods] of REQUIRED_PATHS) {
    assert(document.paths?.[endpoint], `OpenAPI 필수 path가 없습니다: ${endpoint}`);
    for (const method of methods) {
      assert(document.paths[endpoint][method], `OpenAPI 필수 operation이 없습니다: ${method.toUpperCase()} ${endpoint}`);
    }
  }
}

async function checkCors(apiBaseUrl) {
  const response = await checkedFetch(`${apiBaseUrl}/v1/auth/login`, {
    method: "OPTIONS",
    headers: {
      Origin: TEST_ORIGIN,
      "Access-Control-Request-Method": "POST",
      "Access-Control-Request-Headers": "authorization,content-type,idempotency-key",
    },
  });
  assert(response.status === 204, "CORS preflight 응답이 204가 아닙니다.");
  assert(response.headers.get("access-control-allow-origin") === TEST_ORIGIN, "CORS 허용 origin이 요청 origin과 다릅니다.");
  assert(response.headers.get("access-control-allow-credentials") === "true", "CORS credentials 허용이 없습니다.");
  const allowedMethods = headerTokens(response.headers, "access-control-allow-methods");
  for (const method of ["get", "post", "patch", "options"]) {
    assert(allowedMethods.has(method), `CORS 허용 method가 없습니다: ${method.toUpperCase()}`);
  }
  const allowedHeaders = headerTokens(response.headers, "access-control-allow-headers");
  for (const name of ["authorization", "apikey", "content-type", "idempotency-key", "x-request-id"]) {
    assert(allowedHeaders.has(name), `CORS 허용 header가 없습니다: ${name}`);
  }
  assert(headerTokens(response.headers, "vary").has("origin"), "CORS 응답의 Vary에 Origin이 없습니다.");
}

async function main() {
  try {
    testPublishableKeyGuard();
    checkTestOrigin();
    const config = await loadEnvironment();
    checkProjectRefs(config);
    console.log("[ok] 공개 환경변수의 운영 project ref가 정본과 일치합니다.");

    await checkSupabasePublishableKey(config);
    console.log("[ok] Supabase publishable key가 운영 project에서 유효합니다.");

    const apiBaseUrl = config.apiBaseUrl.replace(/\/+$/u, "");
    await checkCors(apiBaseUrl);
    console.log(`[ok] 운영 CORS preflight 계약을 확인했습니다: ${TEST_ORIGIN}`);

    await checkHealth(apiBaseUrl);
    console.log("[ok] 운영 health 계약을 확인했습니다.");

    await checkOpenApi(apiBaseUrl);
    console.log("[ok] OpenAPI 0.2.0과 필수 path를 확인했습니다.");

  } catch (error) {
    console.error(`[fail] ${error instanceof Error ? error.message : "API 계약 검사에 실패했습니다."}`);
    process.exitCode = 1;
  }
}

await main();
