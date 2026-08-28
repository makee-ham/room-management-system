from pathlib import Path

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8').rstrip()
if '## 간편 예약 범위·링크 호환 표기 (2026-08-29)' not in readme:
    readme += """

## 간편 예약 범위·링크 호환 표기 (2026-08-29)

- 29일 범위의 상대 표기는 기준일 `-7일 ~ +21일`이다.
- 직접 범위를 공유하는 링크 형식은 `bookingAnchor=YYYY-MM-DD`를 유지한다.
"""
readme_path.write_text(readme + '\n', encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8').rstrip()
if '## 2026-08-29 · 간편 예약 29일 경계 회귀' not in qa:
    qa += """

## 2026-08-29 · 간편 예약 29일 경계 회귀

- 기본 날짜 열이 `2026-08-08~2026-09-05`로 이어지는지 확인한다.
- 월 경계를 넘는 `8/31~9/3 연박` 예약을 한 건으로 선택·표시할 수 있는지 확인한다.
"""
qa_path.write_text(qa + '\n', encoding='utf-8')
