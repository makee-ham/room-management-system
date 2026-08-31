# 운영 API·PWA 연결 기록

작성일: 2026-08-31

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
- 관리자는 기존 `오늘·객실·간편 예약·청소·메이드·더보기`, 메이드는 기존 `내 업무·근무 일정·주급·더보기` 정보 구조를 그대로 사용한다.
- 운영 객실·계정 API가 있는 화면은 기존 카드·목록 안에 실제 응답을 표시하고, 아직 endpoint가 없는 화면은 같은 내비게이션과 레이아웃 안에서 `API 연결 대기` 상태를 표시한다.
- 객실 탭과 목록은 정본 순서 `전체 → 스탠다드 → 프리미어 → 파셜 오션뷰 프리미어 → 파셜 오션뷰 패밀리 투룸` 및 기존 객실 카탈로그 순서를 사용한다.
- 관리자 `메이드`는 계정 목록으로 대체하지 않고 기존 `주간 근무표·근무 기록·주급 정산·컴플레인·벌점` 구조를 유지한다. 계정 API의 실제 메이드만 기존 메이드 카드에 표시하고, 근무 endpoint가 없는 값은 `API 연결 대기`로 둔다.
- 개발자는 계정 관리 중심 화면을 사용하고, 모든 역할은 서버가 반환한 역할 범위 안에서만 데이터와 작업을 볼 수 있다.
- 운영 API 오류나 런타임 설정 오류를 데모 데이터로 대체하지 않는다.
- 더보기의 `로그인 상태`는 상태 모달만 열고, 별도의 `로그아웃` 버튼만 세션을 종료한다.
- PWA manifest, 아이콘, 서비스 워커, 설치 안내, 브라우저 알림 권한 요청을 추가했다.

## 아직 운영 API가 없는 범위

현재 OpenAPI 0.2.0에는 예약, 청소 배정·수행·검수, 사진 업로드, 주급, 객실 PIN 조회·변경, 알림함, Web Push 구독 endpoint가 없다. 이 기능은 데모 화면을 운영 데이터처럼 보여 주지 않고 기존 역할별 화면 안에서 준비 중으로 명확히 표시한다.

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

Pages workflow는 정적 작업공간 검사, PWA 검사, 실제 운영 health·OpenAPI·CORS 검사를 모두 통과한 뒤에만 배포한다.

2026-08-31 기준 repository variable `RMS_API_BASE_URL`, `SUPABASE_URL`과 secret `SUPABASE_PUBLISHABLE_KEY`는 등록했다. 공개키 값은 추적 파일이나 문서에 기록하지 않는다. `RMS_APP_ORIGIN`은 전용 도메인이 정해진 뒤 등록한다.

`makee-ham.github.io`는 저장소 경로가 달라도 browser storage와 service worker 권한의 origin을 공유한다. 다른 Pages 앱이 운영 token에 접근할 가능성을 없애기 위해 workflow는 이 공유 origin을 운영 로그인 배포 대상으로 거부한다. 브라우저를 닫아도 로그인을 안전하게 유지하려면 이 앱만 사용하는 custom domain 또는 전용 origin이 필요하며, 도메인을 연결할 때 `RMS_APP_ORIGIN`, CORS allowlist와 Pages 설정을 함께 바꾼다.

## 배포 전 백엔드 필수 설정

- 앱 전용 custom domain의 정확한 origin만 운영 Edge Function CORS allowlist에 추가한다.
- `http://127.0.0.1:4173`과 `http://localhost:4173`은 로컬 확인용으로 유지한다.
- CORS에는 정확한 origin만 넣고 `*`와 credentials 조합은 사용하지 않는다.
- 배포 뒤 전용 origin에서 `/v1/auth/login` OPTIONS 요청이 204, 요청 origin echo, credentials 허용, 필수 header 허용인지 다시 확인한다.

2026-08-31 확인 시 공유 Pages origin `https://makee-ham.github.io`의 preflight는 `403 ORIGIN_NOT_ALLOWED`다. 이 origin은 계속 허용하지 않는다. 전용 origin이 정해지고 해당 origin의 preflight가 통과하기 전에는 Pages workflow와 운영 배포를 완료하지 않는다.

## 운영 시작에 필요한 계정 정보

- 백엔드 계정 관리 API로 생성한 관리자 또는 개발자 `loginId`
- 생성 직후 한 번만 표시되는 임시 비밀번호
- 메이드별 운영 계정이 필요하면 승인된 표시 이름과 휴대전화 번호

기존 Google·Supabase 계정 비밀번호나 개인 이메일 비밀번호를 전달할 필요는 없다. 최초 로그인에서 `mustChangePassword`가 켜져 있으면 앱이 다른 화면보다 개인 비밀번호 변경을 먼저 요구한다.
