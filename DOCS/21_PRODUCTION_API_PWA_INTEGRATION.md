# 운영 API·PWA 연결 기록

작성일: 2026-08-31

최종 갱신: 2026-09-20 · 백엔드 `v0.4.0` (120 paths / 130 operations)

## 연결 대상으로 확정한 프로젝트

- 운영 project ref: `aodikrxcczbogjpsjwjt`
- API root: `https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api`
- Supabase project URL: `https://aodikrxcczbogjpsjwjt.supabase.co`
- `matalcofimnhuzslfhdd` 프로젝트는 Auth 응답은 있지만 문서의 Edge Function API가 없으므로 프런트엔드 운영 대상으로 사용하지 않는다.
- 브라우저에는 `sb_publishable_` 공개키 또는 `role=anon`인 legacy JWT만 넣는다. `service_role`, secret key, 사용자 access/refresh token은 런타임 설정에 넣지 않는다.

## 이번 프런트엔드 연결 범위

- `/v1/auth/login`, Supabase refresh token, `/v1/auth/me`를 연결했다.
- 전용 origin의 개인 기기에서는 `로그인 유지`를 켤 수 있고, access token 만료 전에 refresh token으로 세션을 갱신한다.
- 관리자에게 운영 객실 읽기와 계정 생성·역할·상태·잠금·비밀번호 초기화 기능을 연결했다.
- 백엔드 `v0.4.0`의 기간 예약 목록·예약 가능성 preview·단건 고객명 조회·등록·변경·취소·수동 체크아웃·객실 변경 preview/commit과 연박/추가 청소 요청 생성·취소를 연결했다. 고객명은 관리자 단건 모달의 현재 DOM에만 두고 목록·URL·로그·`localStorage`·`sessionStorage`에 남기지 않는다.
- 메이드의 다음 주 가능일 최초/재제출과 마감 후 변경 요청, 관리자의 메이드별 가능일 표와 변경 요청 승인·반려를 연결했다. 모든 mutation은 현재 version을 CAS 값으로 보내고 멱등 키를 사용한다.
- 객실 단건 projection, 객실 유형 카탈로그·기준정보 변경, 촛불 수량, 운영 차단, 객실 이슈, PIN 동기화 상태 기록을 연결했다. v0.4.0의 명시적 PIN reveal과 prepare/confirm/rollback 변경 흐름도 기존 객실 카드의 `보기·수정` UI에 연결하며 원문은 한 객실·최대 30초 메모리에만 둔다.
- 개발자 기본 화면에 runtime·database·scheduler·계정/객실 요약을 연결했다. 설정은 `configured` 여부만 표시하고 값·길이·해시는 표시하지 않는다.
- 관리자는 기존 `오늘·객실·간편 예약·청소·메이드·더보기`, 메이드는 기존 `내 업무·근무 일정·주급·더보기` 정보 구조를 그대로 사용한다.
- 운영 API가 있는 화면은 기존 카드·목록 안에 실제 응답을 표시하고, 아직 endpoint가 없는 화면은 같은 내비게이션과 레이아웃 안에서 `API 연결 대기` 상태를 표시한다.
- 객실 탭과 목록은 정본 순서 `전체 → 스탠다드 → 프리미어 → 파셜 오션뷰 → 패밀리 투룸` 및 기존 객실 카탈로그 순서를 사용한다.
- 관리자 `메이드`는 계정 목록으로 대체하지 않고 기존 `주간 근무표·근무 기록·주급 정산·컴플레인·벌점` 구조를 유지한다. 계정 API의 실제 메이드와 실제 가능일을 주간 표·카드에 표시하고, 주급·컴플레인은 같은 카드·탭·상세 화면에서 운영 원장과 상태 전이를 연결한다. 과거 근무 기록 전용 조회만 아직 `API 연결 대기`다.
- 개발자는 `운영 상태·계정·더보기`를 사용하고, 모든 역할은 서버가 반환한 역할 범위 안에서만 데이터와 작업을 볼 수 있다.
- 운영 API 오류나 런타임 설정 오류를 데모 데이터로 대체하지 않는다.
- 더보기의 `로그인 상태`는 상태 모달만 열고, 별도의 `로그아웃` 버튼만 세션을 종료한다.
- PWA manifest, 아이콘, 서비스 워커, 설치 안내, 브라우저 알림 권한 요청과 Web Push 공개키 조회·구독 등록/회전·폐기를 연결했다.
- 객실 주 상태는 서버의 `primaryDisplayStatus`만 기존 객실 카드 표시 모델로 변환한다. 프런트는 `reservationLifecycle`, `readinessStatus`, `allocationReady`로 대표 상태를 다시 계산하지 않는다. 서버 우선순위는 `배정 불가 → 투숙 중 → 입실 예정 → 예약 있음 → 청소 필요 → 배정 가능`이며, API 필드명을 새 화면에 노출하지 않는다.
- 주급은 마감 주차 조회·항목 pagination·지급 시작·외부 송금 결과·상계·수익 정정/취소·늦은 확정 이월을 연결한다. 컴플레인은 접수·검토·판정/정정·메이드 확인/이의·종결·재청소 배정을 연결하며 벌점은 주급에서 자동 차감하지 않는다.

## 예약 기간 가능성 계약

- 미래 예약 가능 여부는 `POST /v1/reservations/bookability/preview`의 객실별 `intervalBookable`만 사용한다. `checkInReady`와 `allocationReady`는 현재 청소·PIN 준비 상태이며 미래 기간 option이나 달력 행을 잠그지 않는다.
- 29일 예약 달력은 `GET /v1/reservations?from=&to=&cursor=`의 strict RFC 3339 범위와 opaque cursor를 사용한다. 기존 예약 한 건은 `[checkInAt, checkOutAt)`만 차지하며 겹치지 않는 이후 날짜는 다시 선택할 수 있다.
- 모달 진입, 날짜·예약 유형 변경, 제출 직전에 같은 기간을 다시 preview한다. `intervalBookable === true`인 후보의 `roomStateVersion`만 `expectedRoomVersion`으로 보내며 preview 결과를 성공 보장으로 취급하지 않는다.
- `checkInReady === false`이면 현재 입실 준비가 미완료라고 안내하되 `intervalBookable === true`인 미래 예약은 계속 선택할 수 있다. PIN 불일치·미설정도 미래 기간 자체를 차단하지 않는다.
- 서버의 `ROOM_ALLOCATION_BLOCKED` 409와 `STALE_VERSION`은 정상적인 경쟁 상태로 처리한다. 객실 목록을 다시 읽고 `error.code`에 해당하는 사용자 안내, 최신 차단 사유, `requestId`만 표시하며 서버 내부 message는 화면 문구로 사용하지 않는다.
- 서비스 워커는 API, Authorization, 민감 URL, cross-origin, 모든 non-GET 요청을 브라우저 네트워크에 직접 맡긴다. 예약 POST는 서비스 워커가 캐시하거나 자동 재시도하지 않는다. navigation 실패는 캐시된 앱 문서가 없더라도 503 HTML fallback을 반환한다.

## 계약이 아직 부족한 범위

OpenAPI v0.4.0에서 기간 예약 목록, bookability, 객실 이동, 객실 유형 카탈로그, 청소·근무 이력 조회가 제공된다. 이 릴리즈는 객실 현황·예약 달력·예약 생성/수정·객실 이동·객실 기준정보 흐름을 연결했다. 운영 차단·객실 이슈 해제는 목록 endpoint가 없으므로 현재 브라우저 세션에서 생성 응답의 `entityId`를 받은 건만 바로 해제할 수 있다.

`GET /v1/payroll/entries?kind=adjustments`의 `PayrollAdjustmentEntry`에는 후속 정정·취소 CAS에 필요한 `bookVersion`이 없다. 확정 수익 정정/취소와 늦은 확정 이월은 계약대로 `expectedVersion: 0`으로 연결했지만, 기존 adjustment의 재정정·취소 버튼은 버전을 추측하지 않고 `정정 버전 API 미제공`으로 둔다. `bookVersion`이 entries projection에 추가되면 같은 상세 행에 바로 연결한다.

Web Push 프런트는 `/v1/push-subscriptions/config`, 등록/회전, 폐기 endpoint까지 연결했다. 브라우저 저장소에는 endpoint·`p256dh`·`auth`·binding proof를 남기지 않고 안전한 logical subscription의 `id/version/status`만 둔다. 로그아웃 때 서버 폐기와 브라우저 unsubscribe를 먼저 시도하고 `pushsubscriptionchange`에서는 새 세션 결합 proof를 받아 회전한다. 실제 외부 전달은 백엔드 provider/worker 설정 상태에 따르며, 미설정·503은 성공처럼 표시하지 않는다.

알림 제목·본문에는 고객명, 휴대전화, 객실 PIN, 사진 URL, 토큰, 상세 주급액을 넣지 않는다. 서비스 워커도 서버 자유 입력을 표시하지 않고 사전에 정한 일반 문구만 사용한다.

## 배포 환경

로컬에서는 저장소 루트의 `.env.local`을 `scripts/serve.py`가 읽는다. 이 파일은 Git에 포함하지 않는다.

GitHub Pages 배포는 다음 repository variable·secret을 사용해 `_site/runtime-config.json`을 빌드 산출물에만 만든다.

- Variable `RMS_API_BASE_URL`
- Variable `SUPABASE_URL`
- Variable `RMS_APP_ORIGIN` · 이 앱만 사용하는 HTTPS origin
- Secret `SUPABASE_PUBLISHABLE_KEY`
- 전용 origin의 개인 기기 세션 정책 `RMS_SESSION_PERSISTENCE=local`

Pages workflow는 `RMS_APP_ORIGIN`이 설정된 전용 origin에서는 정적 작업공간·PWA·실제 운영 health·OpenAPI·CORS 검사를 모두 통과한 운영 산출물만 배포한다. 전용 origin이 아직 없으면 공유 Pages origin에는 운영 공개키나 세션을 넣지 않은 `{ "mode": "demo" }` 확인본만 배포한다.

2026-08-31 기준 repository variable `RMS_API_BASE_URL`, `SUPABASE_URL`과 secret `SUPABASE_PUBLISHABLE_KEY`는 등록했다. 공개키 값은 추적 파일이나 문서에 기록하지 않는다. Pages용 `RMS_APP_ORIGIN`은 전용 도메인이 정해진 뒤 등록한다.

같은 날 전용 Vercel project `room-management-system-prod`에 운영 산출물을 배포했다. 고정 origin은 `https://room-management-system-prod.vercel.app`이며 런타임 설정은 운영 API·Supabase project와 `local` 세션 정책을 사용한다. 현재 배포는 로컬에서 만든 정적 산출물을 올린 것이므로 Git 저장소 자동 배포 연결은 별도 작업이다.

2026-09-20에 OpenAPI v0.4.0 객실 상태·기간 예약 정합 산출물을 같은 project에 다시 배포했다. 배포된 `index.html` SHA-256은 로컬 정본과 동일했고, 전용 origin의 CORS·health·OpenAPI 0.4.0 120 paths / 130 operations 및 브라우저 안전 runtime config를 읽기 전용으로 재확인했다. 운영 업무 데이터에는 로그인하거나 mutation하지 않았고, 배포 정적 화면은 runtime config만 demo로 가로챈 hosted 브라우저 smoke로 관리자·메이드 전체 1차 내비게이션을 검수했다.

`makee-ham.github.io`는 저장소 경로가 달라도 browser storage와 service worker 권한의 origin을 공유한다. 다른 Pages 앱이 운영 token에 접근할 가능성을 없애기 위해 workflow는 이 공유 origin을 운영 로그인 배포 대상으로 거부하고 데모 확인본만 게시한다. 브라우저를 닫아도 로그인을 안전하게 유지하려면 이 앱만 사용하는 custom domain 또는 전용 origin이 필요하며, 도메인을 연결할 때 `RMS_APP_ORIGIN`, CORS allowlist와 Pages 설정을 함께 바꾼다.

## 배포 전 백엔드 필수 설정

- 앱 전용 custom domain의 정확한 origin만 운영 Edge Function CORS allowlist에 추가한다.
- `http://127.0.0.1:4173`과 `http://localhost:4173`은 로컬 확인용으로 유지한다.
- CORS에는 정확한 origin만 넣고 `*`와 credentials 조합은 사용하지 않는다.
- 배포 뒤 전용 origin에서 `/v1/auth/login` OPTIONS 요청이 204, 요청 origin echo, credentials 허용, 필수 header 허용인지 다시 확인한다.

2026-08-31 확인 시 공유 Pages origin `https://makee-ham.github.io`의 preflight는 `403 ORIGIN_NOT_ALLOWED`다. 이 origin은 계속 허용하지 않는다. 운영 Edge Function의 `CORS_ORIGINS`에는 기존 로컬 origin 두 개와 `https://room-management-system-prod.vercel.app`만 등록했으며, Vercel origin의 preflight 204와 운영 health·OpenAPI 계약을 실제 요청으로 확인했다. 별도의 전용 origin을 연결하기 전까지 GitHub Pages는 데모 확인본만 제공한다.

## 운영 시작에 필요한 계정 정보

- 백엔드 계정 관리 API로 생성한 관리자 또는 개발자 `loginId`
- 생성 직후 한 번만 표시되는 임시 비밀번호
- 메이드별 운영 계정이 필요하면 승인된 표시 이름과 휴대전화 번호

기존 Google·Supabase 계정 비밀번호나 개인 이메일 비밀번호를 전달할 필요는 없다. 최초 로그인에서 `mustChangePassword`가 켜져 있으면 앱이 다른 화면보다 개인 비밀번호 변경을 먼저 요구한다.
