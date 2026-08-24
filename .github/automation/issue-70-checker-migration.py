from pathlib import Path

path = Path('scripts/check-workspace.mjs')
text = path.read_text(encoding='utf-8')
replacements = [
    (
        '예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리해 주세요.',
        '예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.',
    ),
    (
        '투숙 중 · 예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리해 주세요.',
        '투숙 중 · 예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.',
    ),
    (
        '체크인이 시작된 예약은 취소하지 않고 객실 상세의 지금 체크아웃으로 처리해야 합니다.',
        '체크인이 시작된 예약은 취소하지 않고 예약 관리에서 실제 체크아웃 시각을 수정해야 합니다.',
    ),
]
changed = 0
for old, new in replacements:
    count = text.count(old)
    if count:
        text = text.replace(old, new)
        changed += count
if changed < 1:
    raise SystemExit('automatic occupancy checker copy: no obsolete contract was found')
path.write_text(text, encoding='utf-8')
