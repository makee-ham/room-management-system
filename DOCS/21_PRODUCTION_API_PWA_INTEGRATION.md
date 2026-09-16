# 운영 API·PWA 연결 기록

작성일: 2026-08-31

최종 갱신: 2026-09-16 · 프런트 운영 통합 기준 `70935dc`와 백엔드 `dev@fb50775` (109 paths / 117 operations) 재대조

## 계약 snapshot과 문서 성격

| 구분 | exact commit | 의미 |
|---|---|---|
| 프런트 `main` | `c0657e2680355e4132424f35498c6dbb1708003c` | GitHub 기본 브랜치의 마지막 통합 지점. 수동 Vercel 배포 산출물과 정확히 같은 source라고 간주하지 않는다. |
| 프런트 운영 통합선 | `70935dc322045586adda0a4fc8a3dbc787fe806f` | 현재 수동 Vercel 산출물과 가장 가까운 운영 API UI 기준. 객실·예약·운영·PIN·청소·검수 상세 화면을 포함하며, 현재 객실 상태 보완 브랜치의 기준 commit이다. |
| 백엔드 `dev` | `fb50775289b14f16b27679af471e282504b5f5f6` | source OpenAPI `0.3.0`, 109 paths / 117 operations. `evaluatedAt`과 `reservationPhase`를 포함한 현재 객실 상태 projection이 source/dev에 통합됐다. production 활성화로 해석하지 않는다. |
| 백엔드 `main` | `a12595edf68644b94215c4792e0d3aadd64772c6` | production 56 migrations·API v16·v7 템플릿 게시 결과를 문서화한 GitHub 정본이다. runtime source identity는 `6604b2215e06b9e9ebf0b3138e3716a000c57ddb`다. |

이 문서는 시점이 붙은 운영 연동 기록이다. 제품 정책 정본이나 생성 client 자체가 아니며, runtime OpenAPI와 exact source commit이 다르면 runtime을 우선하고 차이를 Issue로 기록한다. generated client와 breaking diff CI는 백엔드 [#173](https://github.com/wrongstory/room-management-system-backend/issues/173), 전체 adapter 전환과 권한별 browser E2E는 [#13](https://github.com/wrongstory/room-management-system-backend/issues/13)에서 진행한다.

## 실제 소비와 source 제공 구분

| 영역 | `main` 실제 소비 | `dev` 차기 후보 | 백엔드 source | 상태 |
|---|---|---|---|
| 인증·계정·개발자 상태 | 소비 | 동일 | 제공 | 호환 |
| 가능일·예약·객실 | 소비 | 동일 | 제공 | 호환. CAS·멱등 키·409 재조회 유지 |
| 청소 템플릿·수행·미퇴실 사건 | 운영 API 소비 | 동일 | 제공 | `main` 연동 완료, 운영 계정 hosted smoke 대기 |
| 배정·사진·제출·검수 | 운영 API 소비 | 동일. #179 A안 fixture·정적 계약은 PR #141 후보 | 제공 | 현재 단일 사진 운영 연결 완료, 사진 다중 컬렉션은 #180 대기 |
| 알림·Web Push | PWA shell/권한만 | 앱 내부 알림 소비·Web Push 전달 별도 | source 제공 | 외부 push provider 활성화 별도 |
| 주급·컴플레인 | 데모 | 동일 | 제공 | 연동 대기 |
| PIN·Google Sheets | legacy 상태 기록만 | 신규 API 미소비 | source 제공 | 민감정보 경계 유지, hosted 활성화 별도 |
| 검수 대기열 cursor | 미소비 | 미소비 | 백엔드 PR #176 후보 | 병합 뒤 generated client 갱신 대상 |

`scripts/check-api-integration.mjs`의 63 paths / 68 operations는 health·OpenAPI·Swagger와 운영 진단용 endpoint를 포함한 필수 계약 검사 범위다. 이 수치는 `WIREFRAME/index.html`의 실제 UI 호출 수가 아니다. `/health`, `/openapi.json`, `/docs`, 개발자 감사·활동·진단 일부, 예약 전이 processor, 객실 master-data 명령처럼 배포 검증이나 별도 worker가 사용하는 계약도 포함한다.

## 사진 슬롯 계약 결정과 전환 상태

2026-09-16 사용자 결정과 [백엔드 Decision #179](https://github.com/wrongstory/room-management-system-backend/issues/179)에 따라 A안을 확정했다. 새 v8+ 퇴실 청소 template은 객실 타입별 총 9 / 10 / 12 / 14 슬롯, 필수 8 / 9 / 11 / 13 슬롯을 사용한다. required `tv-on`·`entry-storage`는 유지하고 중복 `entry-number`는 제외하며, 마지막 `extra-proof`만 선택·`maxPhotos: 10`이다. 프런트 데모의 pre-A v7과 백엔드의 `maxPhotos` 없는 pre-A v7 이상 template/진행 중 attempt/제출·검수 snapshot의 10 / 11 / 13 / 15 계약은 재작성하지 않는다.

백엔드 #179 source 후보가 append-only v8 validator·publisher·OpenAPI를 구현하지만 운영 DB 적용과 template 재게시는 아직 아니다. 현재 백엔드는 슬롯당 current 사진 한 장 구조이므로 `extra-proof`의 실제 0~10장 추가·개별 삭제·제출 봉인은 [백엔드 #180](https://github.com/wrongstory/room-management-system-backend/issues/180)에서 완료한다. #180 전에는 이 UI fixture를 운영 API가 완전히 지원한다고 표시하거나 v8 운영 template을 게시하지 않는다.

공통 계약은 다음과 같다.

- 역할과 권한은 access token actor 및 서버의 최신 role/status/capability를 정본으로 사용한다. 401/403에서 다른 계정이나 역할로 자동 재실행하지 않는다.
- 오류는 HTTP status, 안정된 `error.code`, `requestId`로 분기한다. 서버 message와 request body를 화면 문구·로그 정본으로 사용하지 않는다.
- 모든 mutation은 `Idempotency-Key`를 사용한다. 응답 유실 때 같은 actor·path·정규화 body에만 같은 키를 재사용하고 Service Worker는 mutation을 캐시하거나 반복하지 않는다.
- 서버 응답의 `version`, `stateVersion`, assignment revision, execution version, impact fingerprint를 CAS 입력으로 사용한다. 409 뒤 관련 projection을 다시 읽고 사용자에게 재확인받는다.

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
- 백엔드 `v0.3.0` 운영 계약의 예약 목록·단건 고객명 조회·등록·변경·취소·수동 체크아웃과 연박/추가 청소 요청 생성·취소를 연결했다. 고객명은 관리자 단건 모달의 현재 DOM에만 두고 목록·URL·로그·`localStorage`·`sessionStorage`에 남기지 않는다.
- 메이드의 다음 주 가능일 최초/재제출과 마감 후 변경 요청, 관리자의 메이드별 가능일 표와 변경 요청 승인·반려를 연결했다. 모든 mutation은 현재 version을 CAS 값으로 보내고 멱등 키를 사용한다.
- 객실 단건 projection, 촛불 수량, 운영 차단, 객실 이슈, PIN 동기화 상태 기록을 연결했다. v0.3.0의 명시적 PIN reveal과 prepare/confirm/rollback 변경 흐름도 기존 객실 카드의 `보기·수정` UI에 연결하며 원문은 한 객실·최대 30초 메모리에만 둔다.
- 개발자 기본 화면에 runtime·database·scheduler·계정/객실 요약을 연결했다. 설정은 `configured` 여부만 표시하고 값·길이·해시는 표시하지 않는다.
- 관리자는 기존 `오늘·객실·간편 예약·청소·메이드·더보기`, 메이드는 기존 `내 업무·근무 일정·주급·더보기` 정보 구조를 그대로 사용한다.
- 운영 API가 있는 화면은 기존 카드·목록 안에 실제 응답을 표시한다. 수동 Vercel 산출물과 가장 가까운 운영 통합 기준은 `70935dc`이며, 현재 객실 상태 보완 후보는 이 기준에서 분기했다. 아직 endpoint가 없는 화면은 같은 내비게이션과 레이아웃 안에서 `API 연결 대기` 상태를 표시한다.
- 객실 탭과 목록은 최신 와이어프레임 정본 순서 `전체 → 스탠다드 → 프리미어 → 파셜 오션뷰 → 패밀리 투룸` 및 기존 객실 카탈로그 순서를 사용한다.
- 관리자 `메이드`는 계정 목록으로 대체하지 않고 기존 `주간 근무표·근무 기록·주급 정산·컴플레인·벌점` 구조를 유지한다. 계정 API의 실제 메이드와 실제 가능일을 주간 표·카드에 표시하고, 배정·근무 이력·주급·컴플레인 값은 `API 연결 대기`로 둔다.
- 개발자는 `운영 상태·계정·더보기`를 사용하고, 모든 역할은 서버가 반환한 역할 범위 안에서만 데이터와 작업을 볼 수 있다.
- 운영 API 오류나 런타임 설정 오류를 데모 데이터로 대체하지 않는다.
- 더보기의 `로그인 상태`는 상태 모달만 열고, 별도의 `로그아웃` 버튼만 세션을 종료한다.
- PWA manifest, 아이콘, 서비스 워커, 설치 안내, 브라우저 알림 권한 요청을 추가했다.

## 예약 배정 차단 계약

- `GET /v1/rooms`의 모든 객실은 같은 서버 snapshot 시각 `evaluatedAt`을 사용한다. 프런트는 브라우저 시각으로 현재 상태를 다시 추정하지 않고 서버가 계산한 `reservationPhase=none|upcoming|current`를 사용한다.
- 대표 상태는 `current 또는 occupied → 투숙 중`, `cleaningRequired → 청소 필요`, `upcoming → 투숙 예정`, `allocationReady → 배정 가능`, 나머지 `배정 불가` 순서로 정확히 하나를 고른다. 각 독립 상태 축과 `reasonCodes`는 보존한다.
- 미래 예약의 planned checkout target은 일정·청소 계획으로 유지하되 현재 `cleaningRequired`로 표시하지 않는다. 실제 체크아웃 또는 현재 청소 의무가 활성화된 뒤에만 `청소 필요`로 표시한다.
- 오늘 요약과 객실 필터의 다섯 상태 수치는 위 대표 상태 기준으로 서로 겹치지 않게 집계한다.

- 예약 등록 UI는 `GET /v1/rooms`의 `allocationReady`, `allocationBlocked`, `reasonCodes`, `pinSyncStatus`, `dataStatus`, `stateVersion`을 함께 사용한다. `allocationReady === true`인 객실만 등록 버튼과 option을 활성화한다.
- `DATA_UNCONFIRMED`는 `pinSyncStatus`와 `dataStatus`를 함께 확인해 `PIN 동기화 미설정`, `PIN 불일치`, `객실 기준정보 미확인`을 중복 없이 모두 표시한다.
- 모달 진입, 객실 선택 변경, 제출 직전에 객실 목록을 다시 읽으며, 최신 `stateVersion`을 `expectedRoomVersion`으로 보낸다. 선택 객실 누락·배정 불가·버전 불일치면 POST를 보내지 않는다.
- 서버의 `ROOM_ALLOCATION_BLOCKED` 409와 `STALE_VERSION`은 정상적인 경쟁 상태로 처리한다. 객실 목록을 다시 읽고 `error.code`에 해당하는 사용자 안내, 최신 차단 사유, `requestId`만 표시하며 서버 내부 message는 화면 문구로 사용하지 않는다.
- 서비스 워커는 API, Authorization, 민감 URL, cross-origin, 모든 non-GET 요청을 브라우저 네트워크에 직접 맡긴다. 예약 POST는 서비스 워커가 캐시하거나 자동 재시도하지 않는다. navigation 실패는 캐시된 앱 문서가 없더라도 503 HTML fallback을 반환한다.

## 백엔드 source에는 있으나 현재 `main`이 소비하지 않는 범위

현재 OpenAPI v0.3.0에는 주급 정산·지급, 외부 Web Push 구독·전달, 완료 청소의 최근 7일 전용 목록 endpoint가 없다. 이 기능은 데모 화면을 운영 데이터처럼 보여 주지 않고 기존 역할별 화면 안에서 `API 연결 대기` 또는 정확한 빈 상태로 표시한다. 청소 배정·현장 수행·사진·제출·검수·앱 내부 알림과 객실 PIN 조회·변경은 v0.3.0 운영 계약에 연결되어 있다. 다만 A안 `extra-proof` 다중 사진 collection은 #180 완료 전 운영 활성화하지 않는다.

객실 기준정보 변경은 `roomTypeId`가 필요하지만 현재 `v0.3.0` 운영 계약에는 프런트가 안전하게 선택할 객실 유형 ID 카탈로그 endpoint가 없다. 객실 유형 ID를 추측하지 않으며 카탈로그 계약이 추가될 때까지 운영 화면에서 기준정보 mutation을 노출하지 않는다. 운영 차단·객실 이슈 해제도 목록 endpoint가 없으므로 현재 브라우저 세션에서 생성 응답의 `entityId`를 받은 건만 바로 해제할 수 있다.

브라우저 알림 권한을 허용하는 것만으로 앱이 닫힌 동안 알림을 보낼 수는 없다. 다음 백엔드가 추가되어야 한다.

1. VAPID 공개키 조회 endpoint
2. 인증된 기기의 Web Push subscription 등록·갱신·해지 endpoint
3. 계정·기기·endpoint·`p256dh`·`auth`를 보호해 저장하는 테이블과 RLS 또는 서버 전용 접근
4. 업무 이벤트 outbox와 대상자 계산, 재시도·만료 구독 제거를 담당하는 발송 worker
5. 로그아웃·계정 비활성·퇴사 시 구독 해지, `pushsubscriptionchange` 재등록
6. 알림 payload의 허용된 `kind`·`route`만 전송하는 서버 검증

알림 제목·본문에는 고객명, 휴대전화, 객실 PIN, 사진 URL, 토큰, 상세 주급액을 넣지 않는다. 현재 서비스 워커도 서버 자유 입력을 표시하지 않고 사전에 정한 일반 문구만 사용한다.

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
