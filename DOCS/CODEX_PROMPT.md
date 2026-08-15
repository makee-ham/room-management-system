# Codex에 전달할 시작 프롬프트

아래 문장을 새 Codex 작업의 첫 요청으로 사용합니다.

> 저장소 루트의 `AGENTS.md`와 `DOCS/00_START_HERE.md`를 끝까지 읽어 정책 우선순위와 현재 구현 상태를 고정해 주세요. 이어서 `DOCS/FINAL_UX_AUDIT.md`, `DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md`, `WIREFRAME/README.md`, `WIREFRAME/QA.md`를 모두 읽고 `WIREFRAME/index.html`을 현재 정본으로 작업하세요. 외부 절대경로에 의존하지 말고, `CURRENT/`와 `HISTORY/`는 시각 참고로만 사용하세요. 화면 변경은 모바일 퍼스트로 구현한 뒤 360/390/768/1440px, 키보드·모달·뒤로가기·접근성·가로 넘침·콘솔 오류를 검증하고 QA 기록과 대표 스크린샷을 갱신하세요. 최종 UX 감사 원문은 수정하지 마세요.

작업 성격에 따라 다음 스킬을 사용합니다.

- 새 화면·대규모 재설계: `build-web-apps:frontend-app-builder`
- 렌더링·반응형·상호작용 회귀: `build-web-apps:frontend-testing-debugging`

실제 운영 데이터가 아닌 객실 번호·단가·예상시간·템플릿은 제작 인계서의 명시적 데모 fixture로 진행합니다. 실제 서버·도어락·사진 업로드·송금·푸시·동시성은 구현한 것처럼 주장하지 않습니다.
