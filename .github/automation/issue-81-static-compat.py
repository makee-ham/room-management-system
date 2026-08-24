from pathlib import Path
import re

path=Path('scripts/check-workspace.mjs')
text=path.read_text(encoding='utf-8')
pattern=r'''for \(const contract of \[\n  "key:'blocked',tone:'red',status:'배정 불가'",.*?throw new Error\(`Room card priority must remain blocked > cleaning > occupied > available: \$\{roomPresentationOrder\.join\(', '\)\}`\);\n\}\n'''
replacement='''for (const contract of [
  'function roomStateFacets(no)',
  "occupancyLabel=occupied?'투숙 중':next?'공실 · 입실 예정':'공실'",
  'cleaningNeeded=roomNeedsCleaningNow(no)',
  'checkoutInspectionPending=checkoutInspectionPending(no)',
  'available=!occupied&&!cleaningNeeded&&!checkoutInspectionPending&&!blocked',
  'roomFacetBadgeMarkup(no)',
  'roomFacetSubMarkup(no)',
  'cardReservationStatus(no)',
  "{id:'reservation-demo-142'",
  'label:`연박 ${day}/${total}일차`',
]) {
  if (!html.includes(contract)) throw new Error(`Independent room-state contract missing: ${contract}`);
}
const roomPresentationSource = html.slice(html.indexOf('function roomStateFacets(no)'), html.indexOf('function renderPinRow', html.indexOf('function roomStateFacets(no)')));
for (const contract of ['occupied','cleaningNeeded','checkoutInspectionPending','blocked','available','conflict']) {
  if (!roomPresentationSource.includes(contract)) throw new Error(`Room-state facet source missing: ${contract}`);
}
'''
text,count=re.subn(pattern,replacement,text,count=1,flags=re.S)
if count!=1:
    raise SystemExit(f'legacy four-state static block mismatch: {count}')
text=text.replace("if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);","if(state.roomFilter==='extra-guests')return roomHasExtraGuests(room.no);")
text=text.replace("if(state.roomFilter==='candle')return r.occupancy!=='occupied'&&(state.candles[r.no]||0)>0;","if(state.roomFilter==='candle')return !facets.occupied&&(state.candles[room.no]||0)>0;")
path.write_text(text,encoding='utf-8')
