"use strict";

const SW_VERSION = "2026-11-06-11";
const CACHE_PREFIX = "castle-the-art-shell-";
const CACHE_NAME = `${CACHE_PREFIX}${SW_VERSION}`;
const APP_DOCUMENT_URL = new URL("./index.html", self.location.href);
const APP_DOCUMENT = APP_DOCUMENT_URL.href;
const APP_DOCUMENT_PATH = APP_DOCUMENT_URL.pathname;
const APP_ROOT_PATH = new URL("./", self.location.href).pathname;
const APP_SHELL_URLS = [
  APP_DOCUMENT,
  new URL("./app.webmanifest", self.location.href).href,
  new URL("./icons/icon-192.png", self.location.href).href,
  new URL("./icons/icon-512.png", self.location.href).href,
  new URL("./icons/icon-maskable-512.png", self.location.href).href
];
const APP_SHELL_PATHS = new Set(APP_SHELL_URLS.map((value) => new URL(value).pathname));

const SENSITIVE_PATH_SEGMENT = /(?:^|\/)(?:api|auth|login|logout|session|sessions|token|tokens|pin|pins|customer|customers|guest|guests|photo|photos|upload|uploads|media|push|subscription|subscriptions|notification|notifications|runtime-config(?:\.json)?)(?:\/|$)/i;
const SENSITIVE_QUERY_KEY = /(?:^|_)(?:token|code|pin|customer|guest|name|phone|email|photo|media|auth|session)(?:_|$)/i;

const PUSH_COPY = Object.freeze({
  assignment_changed: Object.freeze({
    title: "업무 배정이 변경되었습니다",
    body: "앱에서 최신 담당 업무와 일정을 확인해 주세요.",
    tag: "assignment-changed"
  }),
  inspection_ready: Object.freeze({
    title: "새 검수 요청이 있습니다",
    body: "앱에서 검수 대상과 제출 상태를 확인해 주세요.",
    tag: "inspection-ready"
  }),
  schedule_changed: Object.freeze({
    title: "업무 일정이 변경되었습니다",
    body: "앱에서 최신 시작 시각과 처리 상태를 확인해 주세요.",
    tag: "schedule-changed"
  }),
  upload_review: Object.freeze({
    title: "업로드 확인이 필요합니다",
    body: "앱에서 전송 상태와 다음 조치를 확인해 주세요.",
    tag: "upload-review"
  }),
  pay_status: Object.freeze({
    title: "주급 상태가 변경되었습니다",
    body: "앱에서 본인의 최신 주급 상태를 확인해 주세요.",
    tag: "pay-status"
  }),
  action_required: Object.freeze({
    title: "확인할 운영 알림이 있습니다",
    body: "앱 알림함에서 최신 상태와 필요한 조치를 확인해 주세요.",
    tag: "action-required"
  })
});

const ROUTE_URLS = Object.freeze({
  more: new URL("./index.html?view=more", self.location.href).href
});
const SAFE_NOTIFICATION_URLS = new Set(Object.values(ROUTE_URLS));

function decodePathname(pathname) {
  let decoded = pathname;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    try {
      const next = decodeURIComponent(decoded);
      if (next === decoded) break;
      decoded = next;
    } catch {
      break;
    }
  }
  return decoded;
}

function isSensitiveUrl(url) {
  if (url.username || url.password) return true;
  if (SENSITIVE_PATH_SEGMENT.test(decodePathname(url.pathname))) return true;
  for (const key of url.searchParams.keys()) {
    if (SENSITIVE_QUERY_KEY.test(key)) return true;
  }
  return false;
}

function mustBypassCache(request, url) {
  if (request.method !== "GET") return true;
  if (url.origin !== self.location.origin) return true;
  if (request.headers.has("authorization")) return true;
  if (request.cache === "no-store") return true;
  return isSensitiveUrl(url);
}

function isStaticAppShellRequest(request, url) {
  return request.mode !== "navigate" && url.search === "" && APP_SHELL_PATHS.has(url.pathname);
}

async function notifyClients(message) {
  const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  windows.forEach((client) => client.postMessage(message));
}

async function cacheFirstAppShell(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  if (response.ok && response.type === "basic") {
    await cache.put(request, response.clone());
  }
  return response;
}

async function networkFirstNavigation(request) {
  const requestUrl = new URL(request.url);
  const isAppDocument = requestUrl.origin === self.location.origin && [APP_DOCUMENT_PATH, APP_ROOT_PATH].includes(requestUrl.pathname);
  let response;
  try {
    response = await fetch(request);
  } catch {
    if (isAppDocument) {
      try {
        const cached = await caches.match(APP_DOCUMENT, { cacheName: CACHE_NAME });
        if (cached) return cached;
      } catch {
        // Fall through to a complete offline response when cache storage is unavailable.
      }
    }
    return new Response("<!doctype html><html lang=\"ko\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>오프라인 · CASTLE THE ART</title><body><main><h1>네트워크 연결을 확인해 주세요.</h1><p>연결이 복구되면 이 페이지를 다시 열어 주세요. 예약 요청은 저장하거나 자동 재시도하지 않습니다.</p></main></body></html>", {
      status: 503,
      statusText: "Service Unavailable",
      headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" }
    });
  }
  if (isAppDocument && response.ok && response.headers.get("content-type")?.toLowerCase().includes("text/html")) {
    try {
      const cache = await caches.open(CACHE_NAME);
      await cache.put(APP_DOCUMENT, response.clone());
    } catch {
      // The online response is still usable when storage is full or unavailable.
    }
  }
  return response;
}

const PUSH_UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const PUSH_LINK_KINDS = new Set(["cleaningTarget", "assignmentRequest", "submission", "complaintCase", "payrollCycle", "payrollProfile", "availabilityRequest"]);
const PUSH_SEEN_TTL = 24 * 60 * 60 * 1000;
const PUSH_SEEN_LIMIT = 1000;

// Only a stable notification ID and receipt time are persisted, never payloads.
function openPushReceiptStore() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("castle-art-push-receipts", 1);
    request.onupgradeneeded = () => {
      const store = request.result.createObjectStore("receipts", { keyPath: "id" });
      store.createIndex("receivedAt", "receivedAt");
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
async function claimPushReceipt(id) {
  let db;
  try {
    db = await openPushReceiptStore();
    return await new Promise((resolve, reject) => {
      const tx = db.transaction("receipts", "readwrite"), store = tx.objectStore("receipts");
      const now = Date.now();
      let claimed = false;
      const lookup = store.get(id);
      lookup.onsuccess = () => {
        if (!lookup.result || lookup.result.receivedAt <= now - PUSH_SEEN_TTL) {
          store.put({ id, receivedAt: now });
          claimed = true;
        }
        // Newest first: keep at most 1000 receipts within the last 24 hours.
        let kept = 0;
        store.index("receivedAt").openCursor(null, "prev").onsuccess = (event) => {
          const cursor = event.target.result;
          if (!cursor) return;
          if (cursor.value.receivedAt <= now - PUSH_SEEN_TTL || kept >= PUSH_SEEN_LIMIT) cursor.delete();
          else kept += 1;
          cursor.continue();
        };
      };
      tx.oncomplete = () => resolve(claimed);
      tx.onabort = tx.onerror = () => reject(tx.error);
    });
  } catch {
    // Storage can be disabled. The stable browser tag still replaces duplicates.
    const visible = await self.registration.getNotifications?.({ tag: id }).catch(() => []);
    return !visible?.length;
  } finally { db?.close(); }
}
async function releasePushReceipt(id) {
  let db;
  try {
    db = await openPushReceiptStore();
    await new Promise((resolve, reject) => {
      const tx = db.transaction("receipts", "readwrite");
      tx.objectStore("receipts").delete(id);
      tx.oncomplete = resolve;
      tx.onabort = tx.onerror = () => reject(tx.error);
    });
  } catch {} finally { db?.close(); }
}
function typedNotificationUrl(id) {
  const url = new URL(ROUTE_URLS.more);
  url.searchParams.set("notice", id.toLowerCase());
  return url.href;
}

function readPushPayload(data) {
  if (!data) return { kind: "action_required", route: "more" };

  let value;
  try {
    value = data.json();
  } catch {
    return { kind: "action_required", route: "more" };
  }

  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return { kind: "action_required", route: "more" };
  }

  const keys = Object.keys(value);
  if (value.payloadVersion === 1 && PUSH_UUID.test(value.notificationId) &&
      value.deepLink && PUSH_LINK_KINDS.has(value.deepLink.kind) && PUSH_UUID.test(value.deepLink.entityId) &&
      keys.every((key) => ["payloadVersion", "notificationId", "title", "body", "deepLink"].includes(key)) &&
      Object.keys(value.deepLink).every((key) => ["kind", "entityId"].includes(key))) {
    return { kind: "action_required", route: "more", notificationId: value.notificationId.toLowerCase() };
  }
  if (keys.some((key) => key !== "kind" && key !== "route")) {
    return { kind: "action_required", route: "more" };
  }

  return {
    kind: Object.hasOwn(PUSH_COPY, value.kind) ? value.kind : "action_required",
    route: Object.hasOwn(ROUTE_URLS, value.route) ? value.route : "more"
  };
}

function safeNotificationUrl(value) {
  if (typeof value !== "string") return ROUTE_URLS.more;
  try {
    const url = new URL(value, self.location.href);
    if (url.origin !== self.location.origin) return ROUTE_URLS.more;
    const id = url.searchParams.get("notice");
    if (id && PUSH_UUID.test(id) && url.href === typedNotificationUrl(id)) return url.href;
    if (!SAFE_NOTIFICATION_URLS.has(url.href)) return ROUTE_URLS.more;
    if (isSensitiveUrl(url)) return ROUTE_URLS.more;
    return url.href;
  } catch {
    return ROUTE_URLS.more;
  }
}

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(APP_SHELL_URLS);
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names
      .filter((name) => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
      .map((name) => caches.delete(name)));
    await self.clients.claim();
    await notifyClients({ type: "SW_ACTIVATED", version: SW_VERSION });
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (mustBypassCache(request, url)) {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(networkFirstNavigation(request));
    return;
  }

  if (isStaticAppShellRequest(request, url)) {
    event.respondWith(cacheFirstAppShell(request));
    return;
  }

  event.respondWith(fetch(request));
});

self.addEventListener("message", (event) => {
  const type = event.data?.type;
  if (type === "SKIP_WAITING") {
    event.waitUntil(self.skipWaiting());
    return;
  }
  if (type === "GET_VERSION" && event.source?.postMessage) {
    event.source.postMessage({ type: "SW_VERSION", version: SW_VERSION });
  }
});

self.addEventListener("push", (event) => {
  const payload = readPushPayload(event.data);
  const copy = PUSH_COPY[payload.kind];
  const id = payload.notificationId;
  event.waitUntil((async () => {
    if (id && !await claimPushReceipt(id)) return;
    try {
      await self.registration.showNotification(copy.title, {
        body: copy.body,
        tag: id || copy.tag,
        icon: new URL("./icons/icon-192.png", self.location.href).href,
        badge: new URL("./icons/icon-192.png", self.location.href).href,
        data: { url: id ? typedNotificationUrl(id) : ROUTE_URLS[payload.route] },
        renotify: false
      });
    } catch (error) {
      if (id) await releasePushReceipt(id);
      throw error;
    }
    await notifyClients({ type: "PUSH_RECEIVED" });
  })());
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = safeNotificationUrl(event.notification.data?.url);

  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    const appWindow = windows.find((client) => {
      const url = new URL(client.url);
      return url.origin === self.location.origin && [APP_DOCUMENT_PATH, APP_ROOT_PATH].includes(url.pathname);
    });

    if (appWindow) {
      const notificationId = new URL(targetUrl).searchParams.get("notice");
      appWindow.postMessage({ type: "PUSH_NOTIFICATION_OPEN", notificationId });
      await appWindow.focus();
      return;
    }

    await self.clients.openWindow(targetUrl);
  })());
});

self.addEventListener("pushsubscriptionchange", (event) => {
  // The page obtains a fresh session-bound proof before rotating the browser
  // subscription through the authenticated backend endpoint.
  event.waitUntil(notifyClients({ type: "PUSH_SUBSCRIPTION_CHANGE_REQUIRED" }));
});
