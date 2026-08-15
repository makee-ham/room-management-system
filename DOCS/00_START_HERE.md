# CASTLE THE ART 객실관리 앱 — Codex 시작점

이 저장소는 관리자·메이드용 객실관리 앱의 최종 정책 문서, 모바일 퍼스트 클릭형 와이어프레임, QA 기록과 이전 감사 근거를 함께 보관합니다.

## 현재 정본

- 실행형 와이어프레임: [`../WIREFRAME/index.html`](../WIREFRAME/index.html)
- 구현 안내: [`../WIREFRAME/README.md`](../WIREFRAME/README.md)
- QA 기록: [`../WIREFRAME/QA.md`](../WIREFRAME/QA.md)
- 저장소 작업 규칙: [`../AGENTS.md`](../AGENTS.md)

`CURRENT/`와 `HISTORY/`는 이전 v13 시안과 변경 근거입니다. 현재 제품 정책이나 구현 정본으로 사용하지 않습니다.

## 필독 순서와 정책 우선순위

1. 현재 작업에서 사용자가 명시적으로 확정한 결정
2. [`FINAL_UX_AUDIT.md`](FINAL_UX_AUDIT.md) — 최종 UX 감사 원문, 수정 금지
3. [`14_CLICKABLE_WIREFRAME_HANDOFF.md`](14_CLICKABLE_WIREFRAME_HANDOFF.md) — 제작 인계서
4. [`../WIREFRAME/README.md`](../WIREFRAME/README.md)와 [`../WIREFRAME/QA.md`](../WIREFRAME/QA.md)
5. `01`~`13` 문서, `CURRENT/`, `HISTORY/` — 감사 근거와 시각 참고

과거 문서와 현재 정본이 충돌하면 위 순서대로 판단합니다. 특히 608호 전용 규칙, 사진별 승인, 촛불 자동 해제, 예약 충돌이라는 단일 상태, 임의 실제 데이터는 현재 정책으로 되살리지 않습니다.

## 빠른 실행

macOS/Linux:

```bash
python3 scripts/serve.py
```

Windows:

```powershell
python scripts/serve.py
```

브라우저에서 `http://127.0.0.1:4173/index.html`을 엽니다. 정적 검증은 `node scripts/check-workspace.mjs`로 실행합니다.

## 프로토타입 경계

현재 HTML은 화면 배치, 상태 전이, 권한과 업무 흐름을 합의하기 위한 결정적 데모입니다. 실제 인증, DB, 사진 저장, 서버 동시성, 푸시, 도어락, 송금은 없습니다. 객실 번호·단가·PIN·인명·사진은 모두 데모이며 PIN·고객명·사진 원문을 브라우저 영속 저장소에 남기지 않습니다.
