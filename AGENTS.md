# CASTLE THE ART 작업 지침

이 파일은 운영체제와 Codex 세션이 바뀌어도 같은 정책과 작업 순서를 유지하기 위한 저장소 로컬 지침이다.

## 작업 전 필독 순서

1. `DOCS/16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md`를 끝까지 읽는다. 청소 근무 가능일·담당 결정 방식의 최신 정본이다.
2. `DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md`를 끝까지 읽는다. 객실 기준정보·점유·카드 주 상태·수동 체크아웃의 최신 정본이다.
3. `DOCS/FINAL_UX_AUDIT.md`를 끝까지 읽는다. 이 파일은 그 밖의 최종 제품 정책 정본이며 사용자의 명시적 요청 없이는 수정하지 않는다.
4. `DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md`를 끝까지 읽는다.
5. `WIREFRAME/README.md`와 `WIREFRAME/QA.md`를 읽어 현재 구현·검증 상태를 확인한다.
6. `DOCS/WIREFRAME_TASK_PROMPT.md`의 실행 계약을 확인한다.

충돌 시 `현재 사용자의 명시적 결정 → 16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY(청소 배정 범위) → 17_ROOM_CATALOG_LONG_STAY_DECISIONS(객실 기준정보·점유·카드 주 상태 범위) → FINAL_UX_AUDIT → 14_CLICKABLE_WIREFRAME_HANDOFF → WIREFRAME README/QA → 이전 문서·시안` 순서로 따른다. `CURRENT/`, `HISTORY/`, `DOCS/01`~`DOCS/13`은 감사 근거와 시각 참고일 뿐 현재 제품 정책의 정본이 아니다.

## 구현 범위

- 현재 앱 진입점은 `WIREFRAME/index.html`이다.
- 외부 CDN, 번들러, 백엔드 없이 동작하는 자체 포함 HTML/CSS/JavaScript를 유지한다.
- 모바일 퍼스트로 설계하고 데스크톱은 동일 정보구조를 확장한다.
- 관리자와 메이드 양쪽 권한·상태·내비게이션을 함께 유지한다.
- 실제 운영값이 확정되지 않은 객실 매핑·단가·예상시간·템플릿은 인계서의 `데모` fixture를 사용하며 질문 때문에 작업을 멈추지 않는다.
- 실제 서버·도어락·송금·푸시·동시성을 구현한 것처럼 표현하지 않는다.

## 프런트엔드 작업 규칙

- 새 화면이나 큰 재설계에는 `build-web-apps:frontend-app-builder` 스킬을 사용한다.
- 렌더링·상호작용·반응형 회귀 수정에는 `build-web-apps:frontend-testing-debugging` 스킬을 사용한다.
- 화면 변경 뒤 360/390/768/1440px, 가로 넘침, 키보드, 포커스, 모달, 뒤로가기, 접근성 이름, 콘솔 warning/error를 검증한다.
- 대표 UI 변경은 `WIREFRAME/QA/screenshots/`에 PNG로 남기고 `WIREFRAME/QA.md`에 실제 확인 범위와 한계를 기록한다.
- 색만으로 상태를 전달하지 않고 상태명·이유·아이콘을 함께 제공한다. 모바일 주 컨트롤은 최소 44×44px를 유지한다.
- 실제로 확인하지 않은 항목을 통과로 기록하지 않는다.

## 보안·데이터 계약

- 객실 PIN 원문은 명시적 조회 후 한 객실만 최대 30초 메모리에 둔다.
- PIN·고객명·사진 원문을 URL, 로그, 알림, `localStorage`, `sessionStorage`, 브라우저 history state에 남기지 않는다.
- 메이드는 본인 업무·주급·평가만 볼 수 있고 관리자 전용 상세와 액션은 URL 직접 진입에서도 차단한다.
- 모든 금액·객실·인명·사진 fixture는 실제 데이터가 아닌 데모임을 화면과 문서에서 명시한다.

## 환경 독립성

- 문서와 코드에는 드라이브 문자나 사용자 홈으로 시작하는 개인 컴퓨터 절대경로를 새로 넣지 않는다.
- 파일 링크와 명령은 저장소 루트 기준 상대경로를 사용한다.
- 실행은 macOS/Linux에서 `python3 scripts/serve.py`, Windows에서 `python scripts/serve.py`를 사용한다.
- 정적 검증은 `node scripts/check-workspace.mjs`로 실행한다. 앱 자체 실행에는 Node가 필요하지 않다.

## Git 규칙

- 임시 첨부물 `.codex-remote-attachments/`, 로컬 캐시, 비밀값, OS 생성 파일은 커밋하지 않는다.
- 커밋과 PR 제목은 짧은 한국어 명령형 `<타입>: <설명>` 형식을 사용한다.
- UI PR에는 변경 이유, 검증 결과, 대표 스크린샷 경로를 포함한다.
- 사용자 변경을 덮어쓰거나 최종 감사 원문을 재작성하지 않는다.
- 완료한 작업은 관련 검증을 통과한 뒤 작업 범위 파일만 명시적으로 스테이징하고, `codex/` 작업 브랜치에 한글 커밋으로 기록해 원격에 푸시한다.
- `main`·`dev`에는 직접 푸시하지 않고 작업 브랜치에서 PR을 생성해 병합한다. PR 기준 브랜치는 `현재 사용자의 명시적 지정 → 원격 dev가 있으면 dev → 원격 main → 저장소 기본 브랜치` 순서로 선택한다.
- PR은 변경 이유·사용자 영향·검증 결과·UI 변경 시 대표 스크린샷 경로를 포함해 병합 가능한 상태로 만들고, 충돌과 필수 검사 실패가 없으면 기본적으로 squash merge까지 완료한다.
- 필수 리뷰·보호 규칙·외부 검사 때문에 즉시 병합할 수 없으면 우회하지 않는다. 가능한 경우 auto-merge를 설정하고, 불가능하면 정확한 차단 사유와 필요한 후속 조치를 보고한다.
