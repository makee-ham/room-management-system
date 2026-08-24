from pathlib import Path

path = Path('scripts/check-workspace.mjs')
text = path.read_text(encoding='utf-8')
old = '''for (const contract of [
  "key:'blocked',tone:'red',status:'배정 불가'",
  "key:'cleaning',tone:'amber',status:'청소 필요'",
  "key:'occupied',tone:'neutral',status:'투숙 중'",
  "key:'available',tone:'green',status:'배정 가능'",
  'roomCleaningStageLabel(job)',
  'cardReservationStatus(no)',
  "{id:'reservation-demo-142'",
  'label:`연박 ${day}/${total}일차`',
]) {
  if (!html.includes(contract)) throw new Error(`Four-state room card contract missing: ${contract}`);
}
const roomPresentationSource = html.slice(html.indexOf('function roomPresentation(no)'), html.indexOf('function renderPinRow', html.indexOf('function roomPresentation(no)')));
const roomPresentationOrder = ["if(blockers.length)return", "if(cleaning)return", "if(room.occupancy==='occupied')return", "key:'available'"]
  .map((marker) => roomPresentationSource.indexOf(marker));
if (roomPresentationOrder.some((index) => index < 0) || roomPresentationOrder.some((index, position) => position && index <= roomPresentationOrder[position - 1])) {
  throw new Error(`Room card priority must remain blocked > cleaning > occupied > available: ${roomPresentationOrder.join(', ')}`);
}
'''
new = '''for (const contract of [
  'function roomStateFacets(no)',
  "if(state.roomFilter==='occupied')return facets.occupied;",
  "if(state.roomFilter==='cleaning')return facets.cleaningNeeded;",
  "if(state.roomFilter==='checkout-inspection')return facets.checkoutInspectionPending;",
  'data-cleaning-needed="${facets.cleaningNeeded}"',
  '상태는 서로 겹칠 수 있습니다',
  'roomCleaningStageLabel(job)',
  'cardReservationStatus(no)',
  "{id:'reservation-demo-142'",
  'label:`연박 ${day}/${total}일차`',
]) {
  if (!html.includes(contract)) throw new Error(`Independent room-state contract missing: ${contract}`);
}
'''
if text.count(old) != 1:
    raise SystemExit(f'legacy four-state checker block mismatch: {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
