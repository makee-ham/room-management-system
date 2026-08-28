import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const origin = 'http://127.0.0.1:4173/index.html';
const browser = await chromium.launch({ headless: true });
const runtimeErrors = [];

function normalize(text) {
  return String(text || '').replace(/\s+/g, ' ').trim();
}

async function openPage(width, height, hash) {
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  page.on('pageerror', error => runtimeErrors.push(`${width}px pageerror: ${error.stack || error.message}`));
  page.on('console', message => {
    if (message.type() === 'error') runtimeErrors.push(`${width}px console: ${message.text()}`);
  });
  await page.goto(`${origin}${hash}`, { waitUntil: 'networkidle' });
  await page.locator('#main-content').waitFor();
  return { context, page };
}

async function assertHealthy(page, width, label) {
  const mainText = normalize(await page.locator('#main-content').innerText());
  assert.ok(mainText.length > 80, `${label}: ${width}px main content must not be blank`);
  assert.doesNotMatch(mainText, /Application error|Internal Server Error|Unhandled Runtime Error|ReferenceError/);
  const overflowReport = await page.evaluate(() => {
    const viewportWidth = window.innerWidth;
    const overflow = document.documentElement.scrollWidth - viewportWidth;
    const elements = [...document.querySelectorAll('body *')]
      .map(element => {
        const rect = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        return {
          tag: element.tagName.toLowerCase(),
          id: element.id || '',
          className: typeof element.className === 'string' ? element.className : '',
          left: Math.round(rect.left * 10) / 10,
          right: Math.round(rect.right * 10) / 10,
          width: Math.round(rect.width * 10) / 10,
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          overflowX: style.overflowX,
          position: style.position,
        };
      })
      .filter(item => item.right > viewportWidth + 1 || item.left < -1)
      .sort((left, right) => Math.max(right.right - viewportWidth, -right.left) - Math.max(left.right - viewportWidth, -left.left))
      .slice(0, 20);
    return { overflow, viewportWidth, scrollWidth: document.documentElement.scrollWidth, elements };
  });
  assert.ok(
    overflowReport.overflow <= 1,
    `${label}: ${width}px document horizontal overflow: ${overflowReport.overflow}\n${JSON.stringify(overflowReport, null, 2)}`,
  );
}

async function quickReservationQa(width, height) {
  const { context, page } = await openPage(
    width,
    height,
    '#scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=',
  );
  const label = 'quick reservation';
  await assertHealthy(page, width, label);

  const headerRoot = width <= 720 ? '#quick-grid-mobile-header' : '#quick-grid-scroller';
  const headers = page.locator(`${headerRoot} .quick-grid-header .quick-day-header`);
  await headers.first().waitFor({ state: 'visible' });
  assert.equal(await headers.count(), 29, `${width}px quick reservation must render 29 dates`);
  assert.equal(await headers.first().getAttribute('data-quick-date'), '2026-08-08');
  assert.equal(await headers.last().getAttribute('data-quick-date'), '2026-09-05');

  const todayDates = await headers.evaluateAll(elements => elements
    .filter(element => element.classList.contains('today'))
    .map(element => element.getAttribute('data-quick-date')));
  assert.deepEqual(todayDates, ['2026-08-15'], `${width}px mock today must be 2026-08-15`);

  const resetButton = page.locator('[data-action="quick-month-today"]');
  await resetButton.waitFor();
  assert.equal(normalize(await resetButton.innerText()), '기준일');
  assert.match(normalize(await page.locator('.quick-month-label').innerText()), /8월 15일 기준 29일/);
  assert.match(normalize(await page.locator('.quick-booking-hero-copy').innerText()), /8월 15일/);

  await page.locator('[data-action="quick-month-shift"][data-offset="7"]').click();
  await page.waitForFunction(
    ({ root }) => document.querySelector(`${root} .quick-day-header`)?.getAttribute('data-quick-date') === '2026-08-15',
    { root: headerRoot },
  );
  assert.equal(await headers.first().getAttribute('data-quick-date'), '2026-08-15');

  await resetButton.click();
  await page.waitForFunction(
    ({ root }) => document.querySelector(`${root} .quick-day-header`)?.getAttribute('data-quick-date') === '2026-08-08',
    { root: headerRoot },
  );
  assert.equal(await headers.first().getAttribute('data-quick-date'), '2026-08-08');
  assert.deepEqual(
    await headers.evaluateAll(elements => elements
      .filter(element => element.classList.contains('today'))
      .map(element => element.getAttribute('data-quick-date'))),
    ['2026-08-15'],
  );

  await page.screenshot({ path: `/tmp/admin-quick-booking-demo-date-${width}.png`, fullPage: false });
  await assertHealthy(page, width, label);
  await context.close();
}

async function workforceQa(width, height) {
  const { context, page } = await openPage(
    width,
    height,
    '#scenario=0&role=admin&view=maids&date=2026-08-15&filter=all&type=all&q=',
  );
  const label = 'all-maid workforce';
  await assertHealthy(page, width, label);

  const rows = page.locator('.availability-matrix tbody tr');
  await rows.first().waitFor();
  assert.equal(await rows.count(), 9, `${width}px workforce matrix must show all nine maids`);
  assert.equal(await page.locator('[data-maid-card]').count(), 9, `${width}px maid cards must show all nine maids`);
  assert.match(normalize(await page.locator('#main-content').innerText()), /9\s*\/\s*9\s*제출/);

  for (let index = 0; index < 9; index += 1) {
    const row = rows.nth(index);
    const maidName = normalize(await row.locator('th').innerText());
    const monday = normalize(await row.locator('td').first().innerText());
    assert.match(monday, /✓/, `${maidName} must be available on Monday 2026-08-17`);
  }

  const expectedNames = ['김민지1', '김민지2', '이서연', '박소영', '최은지', '정다현', '오세라', '한지민', '윤가영'];
  const matrixNames = await rows.locator('th').allInnerTexts();
  assert.deepEqual(matrixNames.map(normalize), expectedNames);

  await page.screenshot({ path: `/tmp/admin-all-maid-workforce-${width}.png`, fullPage: false });
  await assertHealthy(page, width, label);
  await context.close();
}

async function randomAssignmentQa(width, height) {
  const { context, page } = await openPage(
    width,
    height,
    '#scenario=2&role=admin&view=cleaning&date=2026-08-16&cleaningDay=tomorrow&filter=all&type=all&q=',
  );
  const label = 'nine-maid random assignment';
  await assertHealthy(page, width, label);

  const randomCard = page.locator('.assignment-random');
  await randomCard.waitFor();
  assert.match(normalize(await randomCard.innerText()), /근무 가능 9명/);

  const firstAssignee = page.locator('select[data-control="assignment-maid"]').first();
  await firstAssignee.waitFor();
  const availableMaidValues = await firstAssignee.locator('option').evaluateAll(options => options
    .map(option => option.value)
    .filter(value => /^m\d+$/.test(value)));
  assert.deepEqual(availableMaidValues, ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']);

  const randomButton = page.locator('[data-action="random-assignments"]').first();
  await randomButton.waitFor();
  assert.ok(await randomButton.isEnabled(), `${width}px random assignment must be enabled`);
  await randomButton.click();
  await page.locator('[data-action="undo-random-assignment"]').waitFor();

  const lanes = page.locator('.maid-order-lane');
  await page.waitForFunction(() => document.querySelectorAll('.maid-order-lane').length === 9);
  assert.equal(await lanes.count(), 9, `${width}px random draft must show nine maid lanes`);
  const laneNames = (await lanes.locator('h4').allInnerTexts()).map(text => normalize(text).replace(/ 배정 객실·청소 순서$/, ''));
  assert.deepEqual(laneNames, ['김민지1', '김민지2', '이서연', '박소영', '최은지', '정다현', '오세라', '한지민', '윤가영']);

  const draftAssignments = await page.locator('select[data-control="assignment-maid"] option:checked').evaluateAll(options => options.filter(option => /^m\d+$/.test(option.value)).length);
  assert.ok(draftAssignments > 0, `${width}px random assignment must assign at least one room`);
  assert.match(normalize(await randomCard.innerText()), /초안 배정 \d+객실/);

  await page.screenshot({ path: `/tmp/admin-nine-maid-random-assignment-${width}.png`, fullPage: false });
  await assertHealthy(page, width, label);
  await context.close();
}

try {
  await quickReservationQa(1440, 1000);
  await quickReservationQa(390, 844);
  await workforceQa(1440, 1000);
  await workforceQa(390, 844);
  await randomAssignmentQa(1440, 1000);
  await randomAssignmentQa(390, 844);
} finally {
  await browser.close();
}

assert.deepEqual(runtimeErrors, [], runtimeErrors.join('\n'));
console.log('Demo-date quick reservation and all-maid random assignment rendered QA: passed');
