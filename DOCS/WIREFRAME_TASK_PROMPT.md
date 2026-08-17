# 클릭형 와이어프레임 작업 프롬프트

CASTLE THE ART 관리자·메이드용 객실관리 앱의 클릭 가능한 반응형 HTML 와이어프레임을 이어서 완성해 주세요.

## 작업 전 필독

아래 문서를 끝까지 읽고 충돌 시 위 문서를 우선합니다.

1. `AGENTS.md`
2. `DOCS/16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md`
3. `DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md`
4. `DOCS/FINAL_UX_AUDIT.md`
5. `DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md`
6. `WIREFRAME/README.md`
7. `WIREFRAME/QA.md`

`CURRENT/index.html`, `HISTORY/`, `DOCS/01`~`DOCS/13`은 감사 근거와 시각 참고만 가능합니다. 기존 상태명·업무 규칙을 현재 제품 정책으로 되살리지 마세요.

## 실행 계약

1. `build-web-apps:frontend-app-builder` 스킬을 읽고 새 화면·재설계에 사용합니다.
2. `WIREFRAME/index.html`을 단일 진입점으로 관리자·메이드 양쪽의 클릭형 와이어프레임을 구현합니다.
3. `build-web-apps:frontend-testing-debugging` 스킬을 읽고 360/390/768/1440px, 키보드, 모달, 뒤로가기, 주요 클릭 흐름, 콘솔 오류, 접근성, 가로 넘침을 검증하고 수정합니다.
4. 구현과 검증에 맞춰 `WIREFRAME/README.md`, `WIREFRAME/QA.md`, `WIREFRAME/QA/screenshots/`를 갱신합니다.
5. 새로 만들거나 수정하는 모든 월간 캘린더는 `일 · 월 · 화 · 수 · 목 · 금 · 토` 열 순서를 고정하고, 일요일·대한민국 공휴일은 빨간색, 토요일은 파란색으로 표시합니다. 공휴일이 토요일과 겹치면 공휴일 색을 우선하며, 색 외의 `휴` 표식과 공휴일 접근성 이름도 제공합니다. 월요일–일요일 운영 주차 계산은 바꾸지 않고 일요일 시작 달력에서 두 행에 걸쳐 강조할 수 있습니다.

실제 객실 번호·객실 타입 매핑·단가·예상시간·체크리스트는 아직 확정 전이므로 질문으로 멈추지 말고 제작 인계서의 `데모` 데이터로 진행합니다. 실제 서버·도어락·송금·푸시·동시성은 구현한 것처럼 주장하지 않고 클릭 가능한 결정적 시뮬레이션으로 표시합니다. PIN·고객 개인정보·사진 원본은 URL, 로그, 알림, 브라우저 영속 저장소에 넣지 않습니다.

내비게이션과 버튼을 단순 전시하지 말고 대표 시나리오에서 카드·상태·배지·타임라인·가능 행동이 실제로 변하게 합니다. 청소 근무·담당 정책은 `DOCS/16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md`, 객실 기준정보·점유·카드 주 상태·수동 체크아웃은 `DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md`를 먼저 확인하고, 그 밖의 정책은 `DOCS/FINAL_UX_AUDIT.md`에서 확인합니다. 실제 운영 데이터가 아니면 합리적인 데모값으로 진행합니다. 최종 UX 감사 원문은 수정하지 않습니다.

완료 뒤에는 변경 파일, 대표 상호작용, 실제 테스트 결과, 남은 데모 한계를 간결하게 보고합니다.
