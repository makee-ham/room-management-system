# CASTLE THE ART 객실관리 와이어프레임

관리자와 메이드가 사용하는 객실관리 앱의 모바일 퍼스트 클릭형 와이어프레임, 최종 정책 문서, 제작 인계서, QA 기록, 시각 참고자료를 함께 보관하는 저장소입니다. 현재 구현 정본은 [`WIREFRAME/index.html`](WIREFRAME/index.html)이며 `CURRENT/`와 `HISTORY/`는 이전 시안 비교용입니다.

## 맥북에서 바로 시작

```bash
git clone https://github.com/makee-ham/room-management-system.git
cd room-management-system
python3 scripts/serve.py
```

브라우저에서 `http://127.0.0.1:4173/index.html`을 엽니다. 빌드·패키지 설치·외부 CDN은 필요하지 않습니다. Python이 없으면 [`WIREFRAME/index.html`](WIREFRAME/index.html)을 직접 열어도 되지만, 브라우저 뒤로가기와 URL 상태 검증에는 로컬 서버를 권장합니다.

Windows에서는 다음 명령을 사용합니다.

```powershell
python scripts/serve.py
```

## Codex 작업 시작 순서

새 환경의 Codex는 저장소 루트의 [`AGENTS.md`](AGENTS.md)를 자동 작업 규칙으로 사용해야 합니다. 수동으로 시작할 때는 다음 한 줄이면 됩니다.

> `AGENTS.md`와 `DOCS/00_START_HERE.md`를 끝까지 읽고 현재 상태를 확인한 뒤 이어서 작업해 줘.

정책 우선순위는 다음과 같습니다.

1. 현재 작업에서 사용자가 명시적으로 확정한 결정
2. [`DOCS/FINAL_UX_AUDIT.md`](DOCS/FINAL_UX_AUDIT.md) — 최종 UX 감사 원문, 수정 금지
3. [`DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md`](DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md) — 제작 인계서
4. [`WIREFRAME/README.md`](WIREFRAME/README.md)와 [`WIREFRAME/QA.md`](WIREFRAME/QA.md) — 현재 구현·검증 계약
5. `DOCS/01`~`DOCS/13`, `CURRENT/`, `HISTORY/` — 감사 근거와 시각 참고만 사용

## 저장소 구조

- `WIREFRAME/`: 현재 단일 파일 앱, 구현 문서, QA 기록, 대표 스크린샷과 디자인 참고자료
- `DOCS/`: 최종 정책 원문, 제작 인계서, 구현·상태·API 관련 문서
- `CURRENT/`: 기존 v13 시안. 현재 제품 정책의 정본이 아님
- `HISTORY/`: 이전 HTML 스냅샷
- `FLOWCHARTS/`: 기존 업무 흐름도와 원본
- `QA/`: v13 자동화 스크립트와 과거 실행 증거
- `TOOLS/`: 과거 시안 생성·패치 도구
- `scripts/`: 환경 독립 실행·정적 검증 도구

## 검증

의존성 없는 정적 점검은 Node.js 18 이상에서 실행합니다.

```bash
node scripts/check-workspace.mjs
```

화면 QA는 360, 390, 768, 1440px에서 수행하고 결과를 [`WIREFRAME/QA.md`](WIREFRAME/QA.md)에 기록합니다. 대표 증거는 [`WIREFRAME/QA/screenshots/`](WIREFRAME/QA/screenshots/)에 보관합니다.

## 중요한 경계

- 모든 객실 번호·PIN·금액·인명·사진은 결정적 데모 데이터입니다.
- 실제 인증, 서버 저장, 도어락, 사진 업로드, 송금, 푸시는 연결되어 있지 않습니다.
- PIN·고객명·사진 원문을 브라우저 영속 저장소에 저장하지 않습니다.
- `.codex-remote-attachments/`는 작업 중 임시 첨부물이므로 Git에 포함하지 않습니다.
- 외부 Codex 폴더에 있던 최종 UX 감사는 내용과 SHA-256을 유지한 채 `DOCS/FINAL_UX_AUDIT.md`에 포함했습니다.
