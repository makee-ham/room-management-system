import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const url = process.env.QA_URL || 'http://127.0.0.1:4173/index.html';
const allowedKinds = new Set(['퇴실 청소', '연박 청소', '추가 청소', '재청소']);
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
const page = await context.newPage();
const runtimeErrors = [];

page.on('pageerror', error => runtimeErrors.push(`pageerror: ${error.message}`));
page.on('console', message => {
  if (message.type() === 'error') runtimeErrors.push(`console: ${message.text()}`);
});

async function waitForTestApi() {
  await page.waitForFunction(() => Boolean(window.__CASTLE_TEST__), null, { timeout: 30_000 });
}

async function resetScenarioWithCandidate(occupancy) {
  const result = await page.evaluate(targetOccupancy => {
    const api = window.__CASTLE_TEST__;
    for (let scenario = 0; scenario < 24; scenario += 1) {
      api.resetScenario(scenario);
      const candidate = api.manualCleaningCandidates().find(item => item.occupancy === targetOccupancy);
      if (candidate) {
        api.setRoomFilter('all');
        return { scenario, candidate };
      }
    }
    return null;
  }, occupancy);
  assert.ok(result, `${occupancy} 상태에서 청소 요청 가능한 객실을 찾지 못했습니다.`);
  return result;
}

async function durableFingerprint() {
  return page.evaluate(() => window.__CASTLE_TEST__.fingerprint());
}

async function openRequestModal(room) {
  const selector = `.room-card-v2[data-room="${room}"] [data-room-cleaning-control="${room}"]`;
  const button = page.locator(selector);
  await button.waitFor({ state: 'visible' });
  assert.equal((await button.textContent()).trim(), '청소 요청', `${room}호 요청 전 버튼 문구`);
  assert.equal(await button.isDisabled(), false, `${room}호 청소 요청 버튼이 활성 상태여야 합니다.`);
  const before = await durableFingerprint();
  await button.click();
  const confirm = page.locator('[data-action="confirm-room-cleaning-on"]');
  await confirm.waitFor({ state: 'visible' });
  assert.equal((await confirm.textContent()).trim(), '청소 대기열에 넣기', '요청 모달 확인 문구');
  const afterOpen = await durableFingerprint();
  assert.equal(afterOpen, before, '요청 모달을 여는 동안 내구 원장이 바뀌면 안 됩니다.');
  return { before, confirm };
}

async function cancelRequestViaUi(room) {
  await page.evaluate(() => window.__CASTLE_TEST__.setRoomFilter('all'));
  const selector = `.room-card-v2[data-room="${room}"] [data-room-cleaning-control="${room}"]`;
  const button = page.locator(selector);
  await button.waitFor({ state: 'visible' });
  assert.equal((await button.textContent()).trim(), '청소 취소', `${room}호 요청 후 버튼 문구`);
  const before = await durableFingerprint();
  await button.click();
  const confirm = page.locator('[data-action="confirm-room-cleaning-off"]');
  await confirm.waitFor({ state: 'visible' });
  assert.equal((await confirm.textContent()).trim(), '청소 취소', '취소 모달 확인 문구');
  const afterOpen = await durableFingerprint();
  assert.equal(afterOpen, before, '취소 모달을 여는 동안 내구 원장이 바뀌면 안 됩니다.');
  await confirm.click();
  await page.waitForFunction(roomNo => !window.__CASTLE_TEST__.manualCleaningState(roomNo).request, room);
  const state = await page.evaluate(roomNo => window.__CASTLE_TEST__.manualCleaningState(roomNo), room);
  assert.equal(state.request, null, `${room}호 활성 요청이 취소돼야 합니다.`);
  assert.equal(state.manualTargetCount, 0, `${room}호 활성 대기열 항목이 남으면 안 됩니다.`);
  assert.equal(state.control.label, '청소 요청', `${room}호는 취소 후 다시 청소 요청이 가능해야 합니다.`);
}

try {
  await page.goto(url, { waitUntil: 'networkidle', timeout: 45_000 });
  await waitForTestApi();

  // 전체 객실 카드에 동일한 청소 제어가 정확히 하나씩 있는지 확인합니다.
  await page.evaluate(() => {
    window.__CASTLE_TEST__.resetScenario(0);
    window.__CASTLE_TEST__.setRoomFilter('all');
  });
  await page.waitForSelector('.room-card-v2');
  const cardCoverage = await page.evaluate(() => {
    const cards = [...document.querySelectorAll('.room-card-v2')];
    return {
      cards: cards.length,
      controls: cards.reduce((total, card) => total + card.querySelectorAll('[data-room-cleaning-control]').length, 0),
      invalid: cards
        .filter(card => card.querySelectorAll('[data-room-cleaning-control]').length !== 1)
        .map(card => card.getAttribute('data-room')),
    };
  });
  assert.equal(cardCoverage.cards, 121, '전체 객실 카드 수');
  assert.equal(cardCoverage.controls, 121, '전체 객실 카드 청소 버튼 수');
  assert.deepEqual(cardCoverage.invalid, [], '카드별 청소 버튼은 정확히 하나여야 합니다.');

  const controlContract = await page.evaluate(() => window.__CASTLE_TEST__.roomCleaningControls());
  assert.equal(controlContract.length, 121, '전체 객실 청소 제어 계약 수');
  assert.ok(controlContract.some(item => item.label === '청소 요청'), '청소 요청 가능한 객실이 있어야 합니다.');
  assert.ok(controlContract.some(item => item.label === '청소 진행 보기'), '진행 중 청소를 확인하는 객실이 있어야 합니다.');
  for (const item of controlContract.filter(entry => entry.label === '청소 진행 보기')) {
    assert.ok(allowedKinds.has(item.kind), `${item.room}호 진행 작업 종류가 유효해야 합니다: ${item.kind}`);
  }

  // 투숙 중 객실: 요청 모달 -> 연박 청소 대기열 -> 투숙 중 하위 상태 -> 두 필터 -> 취소.
  const occupiedCase = await resetScenarioWithCandidate('occupied');
  const occupiedRoom = occupiedCase.candidate.room;
  const occupiedModal = await openRequestModal(occupiedRoom);
  await occupiedModal.confirm.click();
  await page.waitForFunction(roomNo => Boolean(window.__CASTLE_TEST__.manualCleaningState(roomNo).request), occupiedRoom);
  const occupiedState = await page.evaluate(roomNo => window.__CASTLE_TEST__.manualCleaningState(roomNo), occupiedRoom);
  assert.equal(occupiedState.request.kind, '연박 청소', '투숙 중 수동 요청은 연박 청소여야 합니다.');
  assert.equal(occupiedState.request.status, 'active', '연박 청소 요청 상태');
  assert.equal(occupiedState.manualTargetCount, 1, '연박 청소 대기열 항목은 한 건이어야 합니다.');
  assert.equal(occupiedState.presentation.status, '투숙 중', '청소 요청 뒤에도 주 상태는 투숙 중이어야 합니다.');
  assert.equal(occupiedState.presentation.cleaning, true, '투숙 중 객실의 청소 필요 하위 상태');
  assert.equal(occupiedState.presentation.cleaningKind, '연박 청소', '투숙 중 하위 청소 종류');
  assert.equal(occupiedState.control.label, '청소 취소', '배정 전 활성 요청은 청소 취소를 표시해야 합니다.');

  const occupiedCardText = await page.locator(`.room-card-v2[data-room="${occupiedRoom}"]`).innerText();
  assert.match(occupiedCardText, /투숙 중/, '객실 카드의 투숙 중 표시');
  assert.match(occupiedCardText, /청소 필요 · 연박 청소/, '객실 카드의 연박 청소 하위 상태');
  const occupiedFilter = await page.evaluate(() => window.__CASTLE_TEST__.setRoomFilter('occupied'));
  const cleaningFilter = await page.evaluate(() => window.__CASTLE_TEST__.setRoomFilter('cleaning'));
  assert.ok(occupiedFilter.includes(occupiedRoom), '연박 청소 객실은 투숙 중 필터에 포함돼야 합니다.');
  assert.ok(cleaningFilter.includes(occupiedRoom), '연박 청소 객실은 청소 필요 필터에도 포함돼야 합니다.');
  await cancelRequestViaUi(occupiedRoom);

  // 공실 객실: 같은 UI를 사용하되 추가 청소로 생성합니다.
  const vacantCase = await resetScenarioWithCandidate('vacant');
  const vacantRoom = vacantCase.candidate.room;
  const vacantModal = await openRequestModal(vacantRoom);
  await vacantModal.confirm.click();
  await page.waitForFunction(roomNo => Boolean(window.__CASTLE_TEST__.manualCleaningState(roomNo).request), vacantRoom);
  const vacantState = await page.evaluate(roomNo => window.__CASTLE_TEST__.manualCleaningState(roomNo), vacantRoom);
  assert.equal(vacantState.request.kind, '추가 청소', '공실 수동 요청은 추가 청소여야 합니다.');
  assert.equal(vacantState.manualTargetCount, 1, '추가 청소 대기열 항목은 한 건이어야 합니다.');
  assert.equal(vacantState.control.label, '청소 취소', '공실 요청도 배정 전에는 청소 취소를 표시해야 합니다.');
  await cancelRequestViaUi(vacantRoom);

  // 모든 객실 상세(정보 보류·충돌 포함)에 청소 패널이 하나씩 있는지 전수 확인합니다.
  const detailCoverage = await page.evaluate(() => {
    const api = window.__CASTLE_TEST__;
    api.resetScenario(0);
    const before = api.fingerprint();
    const rooms = api.roomCleaningControls().map(item => item.room);
    const invalid = [];
    for (const room of rooms) {
      api.showRoom(room);
      const count = document.querySelectorAll(`[data-room-cleaning-panel="${CSS.escape(room)}"]`).length;
      if (count !== 1) invalid.push({ room, count });
    }
    return { rooms: rooms.length, invalid, before, after: api.fingerprint() };
  });
  assert.equal(detailCoverage.rooms, 121, '객실 상세 전수 검사 수');
  assert.deepEqual(detailCoverage.invalid, [], '모든 객실 상세에 청소 패널이 정확히 하나 있어야 합니다.');
  assert.equal(detailCoverage.after, detailCoverage.before, '객실 상세를 전수 열람해도 내구 원장이 바뀌면 안 됩니다.');

  // 반복 렌더링 및 중복 레코드 검사를 실행합니다.
  const durability = await page.evaluate(() => {
    const repeated = window.__CASTLE_TEST__.repeatRender(10);
    const unique = window.__CASTLE_TEST__.assertUnique();
    return { repeated, unique };
  });
  assert.equal(durability.repeated.equal, true, '반복 렌더링 후 내구 원장 불변');

  // 사용자 화면에 스위치 구현 용어가 남지 않았는지 확인합니다.
  const pageSource = await page.content();
  for (const forbidden of ['ON으로 변경', 'OFF로 변경', '청소 필요 ON', '청소 필요 OFF']) {
    assert.equal(pageSource.includes(forbidden), false, `금지된 사용자 문구: ${forbidden}`);
  }

  // 목록과 상세의 대표 화면을 390/768/1440px에서 검사합니다.
  const viewportResults = [];
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1100 });
    await page.evaluate(() => {
      window.__CASTLE_TEST__.resetScenario(0);
      window.__CASTLE_TEST__.setRoomFilter('all');
    });
    const listOverflow = await page.evaluate(() => ({
      document: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      body: document.body.scrollWidth - document.body.clientWidth,
    }));
    assert.ok(listOverflow.document <= 1 && listOverflow.body <= 1, `${width}px 객실 목록 가로 넘침: ${JSON.stringify(listOverflow)}`);

    const sampleRoom = await page.evaluate(() => window.__CASTLE_TEST__.roomCleaningControls()[0].room);
    await page.evaluate(roomNo => window.__CASTLE_TEST__.showRoom(roomNo), sampleRoom);
    const detailOverflow = await page.evaluate(() => ({
      document: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      body: document.body.scrollWidth - document.body.clientWidth,
    }));
    assert.ok(detailOverflow.document <= 1 && detailOverflow.body <= 1, `${width}px 객실 상세 가로 넘침: ${JSON.stringify(detailOverflow)}`);
    viewportResults.push({ width, listOverflow, detailOverflow });
  }

  assert.deepEqual(runtimeErrors, [], `브라우저 런타임 오류:\n${runtimeErrors.join('\n')}`);

  console.log(JSON.stringify({
    result: 'PASS',
    cardCoverage,
    occupiedCase: { scenario: occupiedCase.scenario, room: occupiedRoom, kind: '연박 청소' },
    vacantCase: { scenario: vacantCase.scenario, room: vacantRoom, kind: '추가 청소' },
    detailCoverage: { rooms: detailCoverage.rooms, invalid: detailCoverage.invalid },
    progressControls: controlContract.filter(item => item.label === '청소 진행 보기').length,
    durabilityEqual: durability.repeated.equal,
    viewportResults,
    runtimeErrors,
  }, null, 2));
} finally {
  await browser.close();
}
