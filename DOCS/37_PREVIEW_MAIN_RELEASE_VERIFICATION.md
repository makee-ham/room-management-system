# Preview 검증과 main 릴리스

사용자가 2026-10-22 요청한 프런트 이슈 처리·Preview 검증·main 병합의 실제 증거를 기록한다. 새 제품 정책을 결정하는 문서는 아니다.

## 수정 PR과 배포 신원

- PR #222: 사진 재시도·계획일·PIN Excel 분리. dev 병합 `10c46b9`.
- PR [#223](https://github.com/makee-ham/room-management-system/pull/223): 종료 예약/중복 예약/과거 청소/로컬 사진 검사·중복 함수 제거·API 계약 CI. 최종 head `9f39cd1b56904e251c72b9364b9be4e4c63c71c4`, 원격 [API contract run](https://github.com/makee-ham/room-management-system/actions/runs/39714729891) PASS 후 squash 병합.
- Preview 소스: dev `86698747d5032f6936155b3ecd9dfb06ee3623ab`.
- Preview deployment: `dpl_CZ7fAfMkzGvW59CCdtsUT2cdJD44`, `https://room-management-system-prod-h9vyowk3h.vercel.app`.
- 고정 Preview 별칭: [room-management-system-prod-preview.vercel.app](https://room-management-system-prod-preview.vercel.app/).
- `build-info.json`: sourceCommit 위 dev commit, indexSha256 `44ade2c6848804d7d61634cf0a5b91465594f3541ac26d81e40fbf3a1a2fb4c0`, serviceWorkerVersion `2026-10-22-2`, deploymentChannel `preview`.
- 운영 Vercel production 승격은 수행하지 않았다. main GitHub Pages의 push 배포는 해당 workflow의 결과로 별도 확인한다.

## 실제 확인

| 대상 | 결과·방법 |
| --- | --- |
| 배포/보호 | Ready 및 고정 별칭 연결 완료. 익명 GET 302로 기존 보호 유지. 인증된 Vercel CLI GET으로 HTML/SW/manifest/privacy/3개 icon/build-info/runtime를 읽음 |
| 소스 일치 | 배포 HTML·SW·manifest/privacy/icons가 승인된 dev 소스와 byte-for-byte 동일. build-info SHA와 sourceCommit 대조 |
| 실제 설정 | live / preview / session. optionalCleaningWorkflow, photoUploadSnapshot, assignmentPlanningDate, roomPinExport true. roomPinTransfer false |
| 공개 API | Preview 별칭 origin으로 CORS preflight, publishable key, health, OpenAPI 154 paths/166 operations PASS. 업무 인증·mutation은 실행하지 않음 |
| 실제 Chrome | 보호된 별칭의 운영 로그인 렌더·신규 과거 이력 guard/사진 preflight 코드 DOM 확인, 빈 로그인 폼의 아이디 포커스, 개인정보처리방침 링크 및 복귀, 가로 넘침 없음 |
| 콘솔 | 앱 warning/error 없음. 새 개별 배포 주소의 Vercel 로그인 과정에서 Google One Tap FedCM 경고 1건은 Vercel 외부 코드로 확인. 앱 경고로 합산하지 않음 |
| 배포 파일 렌더 | 인증 GET으로 가져온 동일 파일을 로컬 정적 서버에 제공하고 demo runtime만 가로챔. 관리자 today/rooms/quickReservation/cleaning/maids/more, 메이드 my/schedule/pay/more의 목적지·의미 있는 화면 PASS |
| 반응형 | 위 배포 파일을 360/390/768/1440px Playwright Chromium 151에서 검증. blank/오류 overlay/가로 넘침/page error/app console warning/error 없음 |
| 변경 흐름 | 같은 index SHA의 예약·과거 이력·사진 재시도/경계값·권한·Back/Forward/포커스 검사는 PR #223 QA에 기록. 운영 업무 쓰기 대신 합성 fixture 사용 |

Browser plugin not available로 로컬/파일 렌더는 기존 Playwright를 사용했고, 실제 배포 UI는 연결된 Chrome에서 별도로 확인했다. 실제 메이드 계정 로그인·휴대폰 카메라/PWA·HEIC codec·실사진 UAT·운영 p50/p95는 미검증이다. 사용자에게 위임된 실사진 UAT와 Drive 인증/물리 PIN 복구 차단은 관련 이슈에 남긴다.

## 사진 조회량 추가 회귀

합성 배정 1/10/20개 각각에서 사진 1장 업로드를 snapshot OFF/ON으로 확인했다. 전체 배정·다른 attempt/submissions 재조회 0회, 초기 상세 GET 1회를 포함한 대상 photo-slots GET은 OFF에서 2회/ON에서 1회로 배정 수와 무관했다. 서버 실지연이나 운영 p50/p95 수치는 아니다. 같은 fixture를 `scripts/check-photo-performance.mjs`에 유지한다.

## 증거와 병합 범위

- 배포 파일 demo 화면: `WIREFRAME/QA/screenshots/preview-oct22-admin-390.png`, `preview-oct22-calendar-1440.png`. 실제 운영 계정 화면으로 오해하지 않는다.
- 수정 흐름: `reservation-readonly-oct22-*`, `reservation-conflict-oct22-*`, `maid-past-readonly-oct22-*` PNG 및 `WIREFRAME/QA.md`.
- main 대비 병합 tree는 소스 dev tree와 동일하며 충돌 없음(6 main-only/26 dev-only 시점). 릴리스 브랜치에는 이 검증 문서·QA/증거와 사진 조회량 회귀만 추가한다. 최종 main PR의 원격 CI와 병합 결과를 실제 PR에서 확인한다.
- #168/#170/#188/#189/#202/#142는 구현·검증 완료. #84/#89는 9월 28일 일반 사진 정책과 9월 29일 템플릿 UI 제거로 대체되었다. #194/#140/#206/#207/#219/#220은 실기기/계정·외부 인증·백엔드 확인 범위를 완료로 꾸미지 않고 열어 둔다.
