#!/usr/bin/env node
// Exercise the live room candle handlers without sending an operational API request.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const html = readFileSync('WIREFRAME/index.html', 'utf8');
const start = html.indexOf('async function runLiveRoomOperation(');
const end = html.indexOf('async function resolveLiveRoomOperation(', start);
assert(start >= 0 && end > start, 'live candle handlers are present');

const room = { id: 'room-352', roomNumber: '352', candleCount: 0, stateVersion: 2 };
const state = { remote: { rooms: { status: 'ready' }, roomOperations: new Map() } };
const elements = {
  'live-room-candle-count': { value: '' },
  'live-room-candle-verified': { checked: false },
};
const requests = [];
const messages = [];
const forms = [];
const sandbox = {
  state,
  document: { activeElement: { id: 'minus-button' }, getElementById: id => elements[id] },
  liveRoomById: id => id === room.id ? room : null,
  openLiveRoomOperationForm: (...args) => forms.push(args),
  mutationApiRequest: async (path, options) => {
    requests.push({ path, ...options });
    room.candleCount = options.body.count;
    room.stateVersion += 1;
    return { data: {} };
  },
  render() {},
  toast: message => messages.push(message),
  loadLiveRooms: async () => { state.remote.rooms.status = 'ready'; },
  liveAccountMutationButtonDisabled() {},
  closeModal() {},
};
const { changeLiveCandleCount, runLiveRoomOperation } = runInNewContext(
  `${html.slice(start, end)}; ({ changeLiveCandleCount, runLiveRoomOperation })`,
  sandbox,
);

await changeLiveCandleCount(room.id, 1);
assert.equal(requests.length, 1, 'first increment writes once');
assert.equal(requests[0].body.count, 1);
assert.equal(requests[0].body.physicallyVerified, false);
assert.equal(room.stateVersion, 3);

await changeLiveCandleCount(room.id, -1);
assert.equal(forms.length, 1, 'decrement opens the existing verification form');
assert.equal(elements['live-room-candle-count'].value, '0');
assert.equal(requests.length, 1, 'decrement does not silently write');

await runLiveRoomOperation('candle', room.id);
assert.equal(requests.length, 1, 'unverified decrement never reaches the API');
assert(messages.some(message => message.includes('현장에서 회수')));

elements['live-room-candle-verified'].checked = true;
await runLiveRoomOperation('candle', room.id);
assert.equal(requests.length, 2, 'verified decrement writes once');
assert.equal(requests[1].body.count, 0);
assert.equal(requests[1].body.physicallyVerified, true);
assert.equal(requests[1].body.expectedRoomVersion, 3);
assert.equal(room.candleCount, 0);

await changeLiveCandleCount(room.id, 1);
assert.equal(requests.length, 3, 'the next increment is still available');
assert.equal(requests[2].body.expectedRoomVersion, 4);
console.log('Candle increment, verified decrement, and next operation: passed');
