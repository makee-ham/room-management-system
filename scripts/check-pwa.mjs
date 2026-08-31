import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(scriptDir, "..");
const wireframeDir = path.join(rootDir, "WIREFRAME");

function pngDimensions(buffer) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  assert.deepEqual(buffer.subarray(0, 8), signature, "PNG signature is invalid");
  assert.equal(buffer.subarray(12, 16).toString("ascii"), "IHDR", "PNG is missing IHDR");
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

async function verifyManifest() {
  const manifestPath = path.join(wireframeDir, "app.webmanifest");
  const manifest = JSON.parse(await readFile(manifestPath, "utf8"));

  assert.equal(manifest.start_url, "./index.html");
  assert.equal(manifest.scope, "./");
  assert.equal(manifest.display, "standalone");
  assert.match(manifest.theme_color, /^#[0-9a-f]{6}$/i);
  assert.match(manifest.background_color, /^#[0-9a-f]{6}$/i);

  const expectedIcons = new Map([
    ["icons/icon-192.png", { width: 192, height: 192, purpose: "any" }],
    ["icons/icon-512.png", { width: 512, height: 512, purpose: "any" }],
    ["icons/icon-maskable-512.png", { width: 512, height: 512, purpose: "maskable" }]
  ]);

  assert.equal(manifest.icons.length, expectedIcons.size);
  for (const icon of manifest.icons) {
    const expected = expectedIcons.get(icon.src);
    assert.ok(expected, `Unexpected manifest icon: ${icon.src}`);
    assert.equal(icon.type, "image/png");
    assert.equal(icon.purpose, expected.purpose);
    assert.equal(icon.sizes, `${expected.width}x${expected.height}`);
    const buffer = await readFile(path.join(wireframeDir, icon.src));
    assert.deepEqual(pngDimensions(buffer), { width: expected.width, height: expected.height });
  }
}

async function verifyServiceWorker() {
  const source = await readFile(path.join(wireframeDir, "sw.js"), "utf8");
  new vm.Script(source, { filename: "WIREFRAME/sw.js" });

  const requiredEvents = [
    "install",
    "activate",
    "fetch",
    "message",
    "push",
    "notificationclick",
    "pushsubscriptionchange"
  ];
  for (const eventName of requiredEvents) {
    assert.match(source, new RegExp(`addEventListener\\(\\"${eventName}\\"`));
  }

  assert.match(source, /request\.mode === "navigate"/);
  assert.match(source, /networkFirstNavigation/);
  assert.match(source, /cache\.put\(APP_DOCUMENT, response\.clone\(\)\)/);
  assert.match(source, /\[APP_DOCUMENT_PATH, APP_ROOT_PATH\]\.includes\(requestUrl\.pathname\)/);
  assert.match(source, /content-type.*includes\("text\/html"\)/);
  assert.match(source, /cacheFirstAppShell/);
  assert.match(source, /url\.origin !== self\.location\.origin/);
  assert.match(source, /SENSITIVE_PATH_SEGMENT/);
  assert.match(source, /authorization/);
  assert.match(source, /SKIP_WAITING/);
  assert.match(source, /SAFE_NOTIFICATION_URLS/);

  const installBlock = source.match(/addEventListener\("install",[\s\S]*?\n\}\);/)?.[0] ?? "";
  assert.ok(!installBlock.includes("SW_UPDATE_WAITING"), "First install must not be announced as a waiting update");

  const pageSource = await readFile(path.join(wireframeDir, "index.html"), "utf8");
  assert.match(pageSource, /registration\.addEventListener\('updatefound'/);
  assert.match(pageSource, /requestedLiveView/);
  assert.match(pageSource, /if\(!pwaUpdateRequested\|\|pwaReloading\)return/);
  assert.match(pageSource, /syncLiveViewUrl\(state\.liveView\)/);

  const routeBlock = source.match(/const ROUTE_URLS = Object\.freeze\(\{([\s\S]*?)\}\);/)?.[1] ?? "";
  assert.match(routeBlock, /^\s*more:/);
  assert.ok(!/(?:admin_cleaning|maid_jobs|pay):/.test(routeBlock), "Unsupported live routes must not be advertised");

  const forbiddenShellEntries = ["api", "auth", "pin", "customer", "photo", "upload"];
  const shellBlock = source.match(/const APP_SHELL_URLS = \[([\s\S]*?)\];/)?.[1] ?? "";
  for (const fragment of forbiddenShellEntries) {
    assert.ok(!shellBlock.toLowerCase().includes(fragment), `App shell must not include ${fragment}`);
  }

  const showNotificationBlock = source.match(/showNotification\(copy\.title, \{([\s\S]*?)\}\)\)/)?.[1] ?? "";
  assert.ok(showNotificationBlock.includes("body: copy.body"));
  assert.ok(!showNotificationBlock.includes("payload.title"));
  assert.ok(!showNotificationBlock.includes("payload.body"));

  await verifyServiceWorkerBehavior(source);
}

async function verifyServiceWorkerBehavior(source) {
  const listeners = new Map();
  const fetches = [];
  const cacheReads = [];
  const shownNotifications = [];
  const openedWindows = [];
  const cachedResponses = new Map([
    "https://example.test/app/index.html",
    "https://example.test/app/app.webmanifest",
    "https://example.test/app/icons/icon-192.png",
    "https://example.test/app/icons/icon-512.png",
    "https://example.test/app/icons/icon-maskable-512.png"
  ].map((url) => [url, "cached"]));
  let failNetwork = false;

  const responseFor = (label, contentType = "text/plain") => new Response(label, {
    status: 200,
    headers: { "content-type": contentType }
  });
  const requestUrl = (request) => typeof request === "string" ? request : request.url;

  const cache = {
    async addAll(urls) {
      urls.forEach((url) => cachedResponses.set(requestUrl(url), "cached"));
    },
    async match(request) {
      const url = requestUrl(request);
      cacheReads.push(url);
      const label = cachedResponses.get(url);
      return label ? responseFor(label) : undefined;
    },
    async put(request, response) {
      cachedResponses.set(requestUrl(request), await response.text());
    }
  };

  const clientsApi = {
    async matchAll() { return []; },
    async claim() {},
    async openWindow(url) { openedWindows.push(url); }
  };
  const selfApi = {
    location: new URL("https://example.test/app/sw.js"),
    clients: clientsApi,
    registration: {
      async showNotification(title, options) {
        shownNotifications.push({ title, options });
      }
    },
    addEventListener(name, listener) { listeners.set(name, listener); },
    async skipWaiting() {}
  };

  const context = vm.createContext({
    self: selfApi,
    caches: {
      async open() { return cache; },
      async match(request) { return cache.match(request); },
      async keys() { return []; },
      async delete() { return true; }
    },
    async fetch(request) {
      const url = requestUrl(request);
      fetches.push(url);
      if (failNetwork) throw new Error("offline");
      return responseFor("network", request.mode === "navigate" ? "text/html" : "text/plain");
    },
    URL,
    Response,
    Headers,
    console
  });
  new vm.Script(source, { filename: "WIREFRAME/sw.js" }).runInContext(context);

  async function dispatchFetch(url, options = {}) {
    let responsePromise;
    const event = {
      request: {
        url,
        method: options.method ?? "GET",
        mode: options.mode ?? "cors",
        cache: options.cache ?? "default",
        headers: new Headers(options.headers)
      },
      respondWith(value) { responsePromise = Promise.resolve(value); }
    };
    listeners.get("fetch")(event);
    assert.ok(responsePromise, `Fetch handler did not respond for ${url}`);
    return responsePromise;
  }

  async function expectNetworkOnly(url, options = {}) {
    const cacheCount = cacheReads.length;
    const fetchCount = fetches.length;
    await dispatchFetch(url, options);
    assert.equal(cacheReads.length, cacheCount, `${url} must not read cache`);
    assert.equal(fetches.length, fetchCount + 1, `${url} must use the network`);
  }

  await expectNetworkOnly("https://example.test/app/api/rooms");
  await expectNetworkOnly("https://example.test/app/index.html?pin=1234");
  await expectNetworkOnly("https://example.test/app/index.html", {
    headers: { authorization: "Bearer test-only" }
  });
  await expectNetworkOnly("https://example.test/app/runtime-config.json", { mode: "navigate" });
  await expectNetworkOnly("https://images.example.test/photo.png");

  const iconFetchCount = fetches.length;
  const iconCacheCount = cacheReads.length;
  const iconResponse = await dispatchFetch("https://example.test/app/icons/icon-192.png");
  assert.equal(await iconResponse.text(), "cached");
  assert.equal(fetches.length, iconFetchCount, "Cached app-shell icon must not hit network");
  assert.equal(cacheReads.length, iconCacheCount + 1, "App-shell icon must use cache first");

  const navigationFetchCount = fetches.length;
  await dispatchFetch("https://example.test/app/index.html?view=more", { mode: "navigate" });
  assert.equal(fetches.length, navigationFetchCount + 1, "Navigation must use network first");

  failNetwork = true;
  const offlineNavigation = await dispatchFetch(
    "https://example.test/app/index.html?view=more",
    { mode: "navigate" }
  );
  assert.equal(await offlineNavigation.text(), "network", "Online navigation must refresh the offline app shell");

  failNetwork = false;
  const rootNavigation = await dispatchFetch("https://example.test/app/", { mode: "navigate" });
  assert.equal(await rootNavigation.text(), "network");
  failNetwork = true;
  const offlineRootNavigation = await dispatchFetch("https://example.test/app/", { mode: "navigate" });
  assert.equal(await offlineRootNavigation.text(), "network", "Scope-root navigation must use the offline app shell");

  failNetwork = false;
  const manifestNavigation = await dispatchFetch(
    "https://example.test/app/app.webmanifest",
    { mode: "navigate" }
  );
  assert.equal(await manifestNavigation.text(), "network");
  failNetwork = true;
  await assert.rejects(
    dispatchFetch("https://example.test/app/app.webmanifest", { mode: "navigate" }),
    /offline/,
    "Non-document navigation must not fall back to the cached HTML shell"
  );
  failNetwork = false;

  let pushPromise;
  listeners.get("push")({
    data: {
      json() {
        return {
          kind: "assignment_changed",
          route: "maid_jobs",
          title: "사용자 입력 제목은 표시하면 안 됨"
        };
      }
    },
    waitUntil(value) { pushPromise = Promise.resolve(value); }
  });
  await pushPromise;
  assert.equal(shownNotifications.length, 1);
  assert.equal(shownNotifications[0].title, "확인할 운영 알림이 있습니다");
  assert.ok(!shownNotifications[0].options.body.includes("사용자 입력"));
  assert.equal(
    shownNotifications[0].options.data.url,
    "https://example.test/app/index.html?view=more"
  );

  let clickPromise;
  listeners.get("notificationclick")({
    notification: {
      data: { url: "https://attacker.example/customer/1" },
      close() {}
    },
    waitUntil(value) { clickPromise = Promise.resolve(value); }
  });
  await clickPromise;
  assert.deepEqual(openedWindows, ["https://example.test/app/index.html?view=more"]);
}

await verifyManifest();
await verifyServiceWorker();
console.log("PWA manifest, icons, cache boundaries, update messages, and push safety checks passed.");
