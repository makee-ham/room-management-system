from pathlib import Path
import shutil, json, hashlib, textwrap, subprocess, os

ROOT = Path('/mnt/data/Castle_The_Art_Codex_Handoff_v12')
if ROOT.exists():
    shutil.rmtree(ROOT)
for sub in ['CURRENT','HISTORY','DOCS','FLOWCHARTS','QA/screenshots','TOOLS']:
    (ROOT/sub).mkdir(parents=True, exist_ok=True)

# Copy current release.
current_files = [
    '/mnt/data/castle_the_art_room_manager_wireframe_v12.html',
    '/mnt/data/castle_the_art_room_manager_wireframe_latest.html',
    '/mnt/data/castle_v12_script.js',
]
for f in current_files:
    p=Path(f)
    if p.exists(): shutil.copy2(p, ROOT/'CURRENT'/p.name)

# Copy all historical HTML prototypes and relevant backups.
for p in sorted(Path('/mnt/data').glob('castle_the_art_room_manager_wireframe_v*.html')):
    shutil.copy2(p, ROOT/'HISTORY'/p.name)
for name in ['castle_the_art_room_manager_wireframe_latest.html']:
    p=Path('/mnt/data')/name
    if p.exists(): shutil.copy2(p, ROOT/'HISTORY'/name)

# QA and tooling.
for f in [
    '/mnt/data/qa_castle_v12_final.py',
    '/mnt/data/test_castle_v12.py',
    '/mnt/data/castle_the_art_v12_qa_report.json',
]:
    p=Path(f)
    if p.exists(): shutil.copy2(p, ROOT/'QA'/p.name)
for p in sorted(Path('/mnt/data/castle_the_art_v12_screens').glob('*.png')):
    shutil.copy2(p, ROOT/'QA/screenshots'/p.name)
for f in [
    '/mnt/data/patch_castle_v11.py',
    '/mnt/data/patch_v11_safety.py',
    '/mnt/data/build_castle_handoff_v12.py',
]:
    p=Path(f)
    if p.exists(): shutil.copy2(p, ROOT/'TOOLS'/p.name)

# Markdown docs.
docs = {}

docs['00_START_HERE.md'] = r'''# Castle The Art 객실관리 앱 — Codex 이관 시작점

## 현재 기준본

- **프로토타입:** `CURRENT/castle_the_art_room_manager_wireframe_v12.html`
- **동일 최신본:** `CURRENT/castle_the_art_room_manager_wireframe_latest.html`
- **추출 JavaScript:** `CURRENT/castle_v12_script.js`
- **자동 검수:** `QA/qa_castle_v12_final.py`
- **검수 결과:** `QA/castle_the_art_v12_qa_report.json`

이 패키지는 Castle The Art의 관리자·메이드용 모바일 내부 앱을 실제 개발로 이관하기 위한 자료다. 단순 청소 앱이 아니라 **객실 운영, 고객 객실 배정, 청소 작업, 인증사진 검수, 메이드 주급·벌점, 일자별 이력**을 연결하는 운영 앱을 목표로 한다.

## 가장 먼저 지켜야 할 원칙

1. **객실 운영 상태는 예약·청소보다 상위 제약이다.** `운영 중지` 객실에는 고객 예약, 입실, 청소 작업, 메이드 담당이 남아 있으면 안 된다.
2. **예약·투숙·청소·검수·차단 특이사항은 하나의 상태값으로 합치지 않는다.** 서로 독립된 축으로 저장하고 화면용 상태를 파생 계산한다.
3. **608호 기준 불변식**은 `운영 중지 + 예약 없음 + 작업 없음 + 담당 없음 + 고객 배정 불가`다.
4. 예약이 있는 객실을 운영 중지하거나, 예약 객실에 차단 특이사항이 생기면 **충돌 상태**로 표시하고 예약 이동·해제를 먼저 처리한다.
5. 중요한 변경은 `입력 → 영향 검토 → 최종 확인 → 서버 재검증 → 트랜잭션 저장 → 감사 로그` 순서로 처리한다.
6. 메이드 일감 선택은 서버에서 원자적으로 처리해 한 명만 성공해야 한다.
7. 과거 원본 기록은 수정하지 않는다. 정정은 별도 이벤트로 추가한다.
8. 촛불은 현황 수량일 뿐 고객 배정 차단 조건이 아니다.

## 빠른 실행

HTML 파일을 브라우저에서 직접 열 수 있다.

```bash
xdg-open CURRENT/castle_the_art_room_manager_wireframe_v12.html
```

또는 로컬 서버를 연다.

```bash
python -m http.server 8000 --directory CURRENT
```

브라우저에서 `http://localhost:8000/castle_the_art_room_manager_wireframe_v12.html`을 연다.

## 자동 검수

Linux 환경에서 Chromium과 Playwright가 준비되어 있다면:

```bash
python QA/qa_castle_v12_final.py
```

현재 패키지 생성 시점 기준 **30/30 검수 통과**다.

## Codex 권장 읽기 순서

1. `01_PRODUCT_PURPOSE_AND_SCOPE.md`
2. `03_STATE_MODEL_AND_BUSINESS_RULES.md`
3. `04_WORKFLOWS_AND_FLOWCHARTS.md`
4. `05_CONFIRMATION_AND_SAFETY_MATRIX.md`
5. `06_DATA_MODEL.md`
6. `07_API_AND_TRANSACTION_DESIGN.md`
7. `08_ACCEPTANCE_CRITERIA.md`
8. `09_CRITIQUE_AND_IMPROVEMENTS.md`
9. `10_CODEX_IMPLEMENTATION_GUIDE.md`
10. `CODEX_PROMPT.md`

## 프로토타입의 성격

현재 HTML은 클릭 흐름 검증용 단일 파일이다. 새로고침하면 상태가 초기화되고, 실사용 인증·DB·사진 저장·푸시·동시성 제어는 없다. UI 구조와 업무 규칙의 기준본으로만 사용하고, 실제 앱은 상태 전이와 권한을 서버에서 검증하도록 재구현해야 한다.
'''

docs['01_PRODUCT_PURPOSE_AND_SCOPE.md'] = r'''# 1. 제품 목적과 범위

## 제품 목적

Castle The Art 내부 운영자가 모바일에서 다음 질문에 즉시 답할 수 있게 한다.

- 오늘 고객에게 배정할 수 있는 객실은 어디인가?
- 청소가 필요한 객실은 어디이며 퇴실 청소인지 연박 청소인지?
- 담당 메이드는 지정됐는지, 미지정인지, 누구인지?
- 고객 배정이 불가능하다면 청소·투숙·예약·시설 문제 중 무엇 때문인지?
- 객실 비밀번호와 촛불 수량은 무엇인지?
- 얼리 체크인과 레이트 체크아웃은 몇 시인지?
- 메이드가 어떤 인증사진을 제출했고 검수 결과는 무엇인지?
- 이번 주 메이드별 확정 주급과 지급 여부는 무엇인지?
- 누가 언제 상태를 변경했는지?

## 핵심 사용자

### 관리자

- 전체 객실 운영 상태 관리
- 고객 예약 객실 배정·변경·해제·입실·퇴실
- 객실 운영 중지·재개
- 청소 일감 생성·공개·배정·변경·미배정 회수
- 인증사진 검수·승인·재청소 요청
- 비밀번호·촛불·차단 특이사항·입퇴실 시각 관리
- 메이드 계정·소프트 삭제 관리
- 주급 지급·지급 취소
- 벌점 부여·삭제·복구
- 날짜별 과거 조회·정정 이력 추가

### 메이드

- 공개된 일감의 금액·시간·유형 확인 후 선택
- 본인 담당 객실과 허용 시각 확인
- 담당 객실 비밀번호 확인
- 청소 시작·체크리스트·사진·특이사항·촛불 수량 제출
- 검수 승인 또는 반려 알림 확인
- 재청소 대상 사진과 사유 확인
- 본인 주급과 벌점 확인

## 관리자 첫 화면의 네 운영 목록

1. **고객 배정 가능 객실**  
   청소·검수 완료, 차단 특이사항 없음, 공실, 기존 예약 미배정.
2. **청소 필요 객실**  
   퇴실·연박·재청소 유형과 담당 지정·미지정을 함께 표시.
3. **고객 배정 불가 객실**  
   운영 중지, 투숙 중, 예약 배정 완료, 청소·검수 미완료, 차단 특이사항, 예약 충돌 등 이유 표시.
4. **촛불 있는 객실**  
   촛불 수량을 교차 조회. 다른 상태 판단과 독립적이며 고객 배정 여부에 영향을 주지 않는다.

이 목록들은 완전히 배타적이지 않다. 예를 들어 연박 청소가 필요한 투숙 객실은 `청소 필요`와 `고객 배정 불가`에 동시에 포함된다. 촛불 객실은 다른 목록에도 동시에 포함될 수 있다.

## 1차 실서비스 범위

- 모바일 웹/PWA
- 관리자·메이드 권한별 로그인
- 객실·예약·청소·검수·주급·벌점·이력
- 사진 업로드와 푸시 알림
- 주급 기간 관리
- 감사 로그

## 2차 이후 범위

- OTA/PMS 자동 연동
- 객실 도어락 API 연동
- 자동 문자·카카오 알림
- 층별 동선·마감 기반 자동 배정 추천
- 다지점 운영
- 사진 품질 보조 판별

## 명시적 비범위

현재 프로토타입의 4자리 랜덤 생성은 실제 도어락 비밀번호를 자동 변경하지 않는다. 실제 문을 여는 코드로 사용하려면 도어락 업체의 공식 연동 방식이 필요하다.
'''

docs['02_USER_ROLES_AND_SCREEN_MAP.md'] = r'''# 2. 사용자 역할과 화면 구조

## 관리자 하단 메뉴

### 객실

- 날짜 선택 캘린더
- 고객 배정 가능·청소 필요·고객 배정 불가·촛불 있음 요약
- 예약 충돌 경고
- 객실 유형·상태·담당·객실 번호 검색
- 객실 상세
  - 운영 상태
  - 고객 객실 배정
  - 청소 담당 배정
  - 비밀번호
  - 촛불 수량
  - 입실 차단 특이사항
  - 얼리·레이트 시간
  - 일자별 변경 이력

### 청소 배정

- 배정 가능 / 담당 확정 / 배정 불가
- 퇴실 청소 / 연박 청소 / 재청소
- 담당 지정 / 미지정
- 선택 오픈·클로즈
- 관리자 직접 배정
- 담당 변경
- 담당 미배정 회수
- 중단 작업 이력

### 검수

- 검수 대기 목록
- 항목별 인증사진 썸네일·확대
- 사진별 확인
- 전 사진 확인 후 승인
- 선택 사진 기준 반려·재청소
- 메이드 알림
- 필요 시 별도 벌점 등록

### 주급

- 주차 선택
- 메이드별 예상·확정·지급 금액
- 지급 완료 토글
- 미지급 복구와 사유
- 변경 로그
- 엑셀 내보내기 위치

### 더보기

- 메이드 관리
- 벌점·컴플레인 관리
- 객실·요금·체크리스트 설정 위치
- 역할 전환과 로그아웃

## 메이드 하단 메뉴

### 일감 찾기

- 관리자에게 오픈된 미배정 일감만 표시
- 객실·유형·금액·가능 시각·마감·예상 시간·얼리/레이트·촛불 수량
- 선택 전 최종 확인
- 선택 후 직접 취소 불가 안내

### 내 업무

- 지금 가능 / 입실 대기 / 청소 중 / 재청소
- 담당 객실만 표시
- 비밀번호는 담당·허용 시각 조건에서만 표시
- 작업 상세·시작·체크리스트·사진·특이사항·촛불 수량

### 완료

- 검수 대기
- 승인 완료
- 반려·재청소

### 주급

- 이번 주 예상·확정·지급 완료 금액
- 작업별 상세
- 지난 주 내역

### 내 정보

- 계정 정보
- 벌점·컴플레인
- 미확인 벌점 알림
- 로그아웃

## 권한 원칙

- 메이드는 담당하지 않은 객실의 비밀번호를 볼 수 없다.
- 메이드는 다른 메이드의 주급·벌점·작업을 볼 수 없다.
- 관리자도 역할을 세분화하는 것이 좋다: 운영, 검수, 정산, 최고관리자.
- 과거 비밀번호와 민감 정보 조회는 최고관리자 권한과 별도 조회 로그가 필요하다.
'''

docs['03_STATE_MODEL_AND_BUSINESS_RULES.md'] = r'''# 3. 상태 모델과 핵심 업무 규칙

## 하나의 `room_status`로 만들지 말 것

객실은 다음 독립 축을 동시에 가진다.

| 축 | 예시 값 |
|---|---|
| 운영 상태 | `active`, `out_of_service` |
| 예약 상태 | 미배정, 객실 배정 완료, 취소, 체크인, 체크아웃 |
| 투숙 상태 | 공실, 오늘 입실, 투숙 중, 오늘 퇴실, 장기투숙 |
| 청소 상태 | 작업 없음, 입실 대기, 청소 가능, 청소 중, 검수 대기, 재청소 필요, 입실 준비 완료, 청소 제외 |
| 청소 담당 | 미배정, 담당 확정, 변경·중단 |
| 차단 특이사항 | 없음, 고객 배정 차단 이슈 있음 |
| 촛불 | 0개 이상 현황 |
| 접근 코드 | 현재 코드와 유효 기간 |

화면의 `고객 배정 가능`, `예약 충돌`, `청소 담당 가능`은 위 원본 필드에서 파생한다.

## 고객 객실 배정 파생 규칙

의사코드:

```text
if reservation_assigned and (out_of_service or blocking_issue):
    return RESERVATION_CONFLICT
if out_of_service:
    return UNAVAILABLE
if occupied_or_long_stay:
    return UNAVAILABLE
if reservation_assigned:
    return ASSIGNED
if blocking_issue:
    return UNAVAILABLE
if cleaning_status != READY:
    return UNAVAILABLE
return AVAILABLE
```

### 고객 배정 가능 조건

모두 참이어야 한다.

- 정상 운영
- 공실
- 예약 미배정
- 청소·검수 승인 완료
- 고객 배정 차단 특이사항 없음

촛불 수량은 조건에 포함하지 않는다.

## 입실 처리 조건

예약이 객실에 배정됐더라도 다음이 모두 충족되어야 입실 처리가 가능하다.

- 정상 운영
- 예약 배정 존재
- 아직 투숙 중이 아님
- 청소 상태 `입실 준비 완료`
- 차단 특이사항 없음

## 운영 중지 불변식

`out_of_service`가 확정된 객실은 반드시 다음을 만족해야 한다.

```text
reservation_assigned = false
occupancy = vacant/out_of_service
cleaning_suppressed = true
cleaning_task = none
cleaning_assignee = null
claim_open = false
assignment_enabled = false
guest_allocation = unavailable
```

예약이나 투숙이 있으면 운영 중지 확정을 거절하고 예약 이동·배정 해제·퇴실 처리를 먼저 요구한다.

## 608호 기준 시나리오

현재 608호는 냄새 원인 확인을 위해 운영 중지다.

```text
운영 상태: 운영 중지
고객 예약: 없음
투숙: 없음
청소 작업: 없음
청소 담당: 없음
메이드 선택 공개: 닫힘
고객 배정: 불가
촛불: 3개 현황만 기록
```

정상 운영 재개 시 즉시 고객 배정 가능으로 만들지 않는다. `운영 재개 점검 청소`를 미배정·선택 클로즈로 생성하고, 청소·검수 승인을 거쳐야 고객 배정 가능 여부를 다시 계산한다.

## 청소 담당 배정 규칙

- 작업이 존재하고 배정 가능한 단계에서만 담당 지정 가능.
- 메이드가 선택하면 다른 메이드에게 즉시 닫히지만 관리자는 변경·미배정 회수 가능.
- 청소 중 변경 시 기존 사진·체크·시작 시각은 중단 작업 이력으로 보존.
- 새 담당자는 이전 제출물을 자기 작업처럼 이어받지 않는다.
- 검수 대기 또는 승인 완료 작업은 일반 담당 변경 금지. 반려 후 재청소 담당을 별도로 지정한다.

## 일감 선택 원자성

두 메이드가 동시에 선택할 수 있으므로 서버에서 다음 조건을 한 트랜잭션으로 보장한다.

```text
assignee_id IS NULL
claim_open = true
assignment_enabled = true
operational_status = active
cleaning_task.status is claimable
```

조건을 만족한 최초 요청만 성공하고 나머지는 `이미 다른 메이드가 선택함` 응답을 받는다.

## 검수와 가용 상태

메이드의 청소 완료는 곧바로 고객 배정 가능을 의미하지 않는다.

```text
청소 완료 → 사진 업로드 완료 → 검수 대기
검수 승인 + 차단 이슈 없음 + 정상 운영 → 입실 준비 완료
검수 반려 → 재청소 필요 → 메이드 알림 → 재제출
```

## 주급과 벌점

- 청소비는 작업 생성 시 금액 스냅샷으로 저장한다.
- 검수 승인 시 확정 주급 항목이 된다.
- 지급 완료는 실제 송금 후 기록하며 미지급 복구 가능.
- 벌점은 주급에서 자동 차감하지 않는다.
- 벌점 삭제는 물리 삭제가 아니라 `void/deleted` 상태이며 이력은 남는다.

## 과거 기록

과거 날짜의 원본 상태는 읽기 전용이다. 오기입은 원본을 덮어쓰지 않고 정정 이벤트를 추가한다.
'''

docs['04_WORKFLOWS_AND_FLOWCHARTS.md'] = r'''# 4. 주요 업무 흐름과 플로우차트

렌더링된 SVG·PNG는 `FLOWCHARTS/`에 있다. Mermaid 원문도 함께 제공한다.

## 4.1 전체 객실 운영과 고객 배정

```mermaid
flowchart TD
    A[날짜 선택] --> B[객실 운영 현황 조회]
    B --> C{운영 중지?}
    C -- 예 --> D[고객 배정 불가·청소 제외·담당 불가]
    C -- 아니오 --> E{예약+차단 상태 충돌?}
    E -- 예 --> F[예약 충돌 경고]
    F --> G[다른 객실 이동 또는 배정 해제]
    E -- 아니오 --> H{투숙 중?}
    H -- 예 --> I[신규 배정 불가]
    H -- 아니오 --> J{예약 배정됨?}
    J -- 예 --> K[예약 배정 완료]
    K --> L{청소·검수 완료?}
    L -- 아니오 --> M[입실 처리 잠금]
    L -- 예 --> N[입실 처리 가능]
    J -- 아니오 --> O{차단 특이사항 없음 + 입실 준비 완료?}
    O -- 예 --> P[고객 배정 가능]
    O -- 아니오 --> Q[고객 배정 불가 사유 표시]
```

## 4.2 운영 중지와 608호

```mermaid
flowchart TD
    A[관리자 운영 중지 요청] --> B{예약 또는 투숙 있음?}
    B -- 예 --> C[확정 차단]
    C --> D[예약 이동·배정 해제·퇴실 처리]
    D --> A
    B -- 아니오 --> E[사유 입력]
    E --> F[최종 확인 모달]
    F --> G[운영 중지 트랜잭션]
    G --> H[예약 없음]
    G --> I[청소 작업 없음]
    G --> J[담당 없음·선택 닫힘]
    G --> K[고객 배정 불가]
    K --> L[정상 운영 재개 요청]
    L --> M[사유·최종 확인]
    M --> N[운영 재개 점검 청소 생성]
    N --> O[청소·검수 승인]
    O --> P[고객 배정 가능 여부 재계산]
```

## 4.3 청소 일감 공개·선택·담당 변경

```mermaid
flowchart TD
    A[청소 작업 생성] --> B{배정 가능?}
    B -- 아니오 --> C[배정 불가 사유 표시]
    B -- 예 --> D{관리자 직접 배정?}
    D -- 예 --> E[담당 선택·사유·확인]
    D -- 아니오 --> F[메이드 선택 오픈]
    F --> G[메이드가 금액·시간 확인]
    G --> H[선택 확인 모달]
    H --> I[원자적 claim]
    I -->|성공| J[담당 확정·다른 메이드 목록에서 제거]
    I -->|실패| K[이미 선택됨 안내]
    J --> L{관리자 변경?}
    L -- 다른 메이드 --> M[변경 사유·확인·이력]
    L -- 미배정 회수 --> N[미배정·오픈 또는 클로즈]
```

## 4.4 청소·인증사진·검수

```mermaid
flowchart TD
    A[메이드 담당 객실] --> B[청소 시작 확인]
    B --> C[체크리스트·항목별 사진·특이사항]
    C --> D[청소 후 촛불 수량 기록]
    D --> E[완료·검수 요청 확인]
    E --> F[검수 대기]
    F --> G[관리자 사진별 확인]
    G --> H{결과}
    H -- 승인 --> I[승인 확인 모달]
    I --> J[입실 준비 완료·주급 확정]
    H -- 반려 --> K[사진·사유 입력]
    K --> L[반려 최종 확인]
    L --> M[재청소 필요·메이드 빨간 알림]
    M --> C
    H -- 별도 필요 --> N[벌점 부여 절차]
```

## 4.5 주급과 벌점

```mermaid
flowchart TD
    A[검수 승인 작업] --> B[주급 확정 항목]
    B --> C[주차별 합산]
    C --> D{실제 송금 완료?}
    D -- 예 --> E[지급 완료 확인·로그]
    E --> F{기록 실수?}
    F -- 예 --> G[사유 입력 후 미지급 복구]
    D -- 아니오 --> H[미지급 유지]

    I[품질 문제 확인] --> J[벌점 사유·근거 입력]
    J --> K[부여 최종 확인]
    K --> L[유효 벌점·메이드 알림]
    L --> M{삭제 필요?}
    M -- 예 --> N[삭제 사유·소프트 삭제]
    N --> O{복구 필요?}
    O -- 예 --> P[복구 사유·유효 상태 복원]
```

## 4.6 일자별 이력

```mermaid
flowchart TD
    A[달력에서 날짜 선택] --> B[해당 날짜 객실 스냅샷 조회]
    B --> C{오늘인가?}
    C -- 예 --> D[실시간 상태 변경 가능]
    C -- 아니오 --> E[읽기 전용]
    E --> F{오기입 발견?}
    F -- 예 --> G[정정 내용·사유 입력]
    G --> H[최종 확인]
    H --> I[원본 유지·정정 이벤트 추가]
    F -- 아니오 --> J[조회 종료]
```
'''

docs['05_CONFIRMATION_AND_SAFETY_MATRIX.md'] = r'''# 5. 확인 모달과 안전장치 매트릭스

화면 모달은 실수 방지를 돕지만 최종 안전장치는 아니다. 실제 앱은 확인 후에도 서버에서 최신 상태와 권한을 다시 검증해야 한다.

| 변경 | v12 UI | 추가 입력 | 서버 필수 검증 |
|---|---|---|---|
| 객실 운영 중지·재개 | 2단계 확인 | 사유 | 예약·투숙·담당 충돌, 버전 |
| 고객 객실 배정 | 미리보기+확정 | 예약 식별, 시각 | 객실 가용성, 중복 배정 |
| 예약 이동 | 후보 선택+확정 | 대상 객실 | 출발 예약 존재, 대상 가용 |
| 예약 배정 해제 | 확인 | 선택적 사유 권장 | 체크인 전인지, 권한 |
| 고객 입실·퇴실 | 확인 | 운영상 사유 권장 | 입실 가능 조건, 현재 투숙 |
| 객실 비밀번호 변경 | 전·후 확인 | 4자리 | 권한, 암호화, 조회 로그 |
| 얼리·레이트 변경 | 전·후 확인 | 정확한 시각 | 기본 시각 대비 유효성, 충돌 |
| 차단 특이사항 등록·해결 | 확인 | 구체 사유 | 예약 충돌, 해결 권한 |
| 청소 담당 직접 배정·변경 | 확인 | 변경 사유 | 작업 상태, 대상 메이드 활성 |
| 담당 미배정 회수 | 확인 | 사유, 오픈/클로즈 | 기존 제출물 보존 |
| 단일·일괄 일감 오픈/클로즈 | 확인 | 없음 | 여전히 미배정·공개 가능인지 |
| 메이드 일감 선택 | 확인 | 없음 | 원자적 claim, 중복 방지 |
| 청소 시작 | 확인 | 없음 | 담당자·허용 시각·운영 상태 |
| 청소 완료·검수 요청 | 확인 | 체크·사진·특이사항 | 필수 사진 업로드 완료 |
| 검수 승인 | 전 사진 확인+확정 | 없음 | 최신 제출 버전, 차단 이슈 |
| 검수 반려 | 사유 입력+최종 확인 | 사진, 사유 | 작업 버전, 담당자 알림 |
| 주급 지급 완료·취소 | 확인 | 취소 사유 필수 | 정산 잠금, 중복 지급 방지 |
| 벌점 부여 | 근거 입력+확정 | 사유·증빙 | 권한, 정책 점수 범위 |
| 벌점 삭제·복구 | 확인 | 사유 | 소프트 삭제, 감사 로그 |
| 메이드 추가·수정 | 미리보기+확정 | 계정 정보 | 로그인 ID 유일성 |
| 활성·비활성·퇴사·복구 | 확인 | 퇴사 사유 | 진행 작업 회수, 이력 보존 |
| 과거 기록 정정 | 미리보기+확정 | 내용·사유 | 원본 불변, 정정 이벤트 |

## 의도적으로 즉시 반영되는 저위험 조작

- 필터·검색·날짜 탐색
- 사진 썸네일 선택·확대
- 체크리스트 체크
- 촛불 수량 `+/-` 임시 입력

실서비스에서는 촛불 수량도 최종 작업 제출 시점에 한 번 확정·기록한다.

## 모달 문구 원칙

- 무엇이 바뀌는가
- 현재 값과 변경 후 값
- 영향받는 예약·객실·메이드·정산
- 되돌리는 방법
- 사유가 필요한지
- 최종 확정 버튼은 구체적 동사로 표시

`확인`, `저장`처럼 모호한 버튼보다 `운영 중지 확정`, `예약 이동 확정`, `미지급으로 복구`처럼 결과가 드러나는 문구를 사용한다.
'''

docs['06_DATA_MODEL.md'] = r'''# 6. 권장 데이터 모델

아래는 관계형 DB 기준 권장안이다. 실제 구현 시 마이그레이션과 제약조건을 코드로 관리한다.

## 사용자와 권한

### `users`

- `id` UUID PK
- `login_id` unique
- `display_name`
- `role` (`admin`, `maid`)
- `status` (`active`, `inactive`, `retired`)
- `login_enabled`
- `created_at`, `updated_at`, `retired_at`

### `admin_permissions`

- `user_id`
- `can_manage_rooms`
- `can_inspect`
- `can_manage_pay`
- `can_manage_users`
- `can_view_password_history`

### `maid_profiles`

- `user_id`
- `phone`
- `joined_at`
- `note`

## 객실과 운영

### `rooms`

- `id` UUID PK
- `room_number` unique
- `room_type_id`
- `operation_status` (`active`, `out_of_service`)
- `operation_reason`
- `version` optimistic lock

### `room_operation_events`

- `room_id`
- `from_status`, `to_status`
- `reason`
- `actor_id`
- `created_at`

### `room_access_codes`

- `room_id`
- `encrypted_code`
- `valid_from`, `valid_to`
- `created_by`
- `revoked_at`

### `access_code_view_logs`

- `room_access_code_id`
- `viewer_id`
- `cleaning_task_id`
- `viewed_at`

### `room_issues`

- `room_id`
- `category`
- `description`
- `severity`
- `blocks_guest_assignment` boolean
- `status` (`open`, `resolved`, `void`)
- `created_by`, `resolved_by`
- `created_at`, `resolved_at`

### `room_candle_events`

- `room_id`
- `count_after`
- `location_note`
- `source` (`admin`, `cleaning_task`)
- `actor_id`
- `created_at`

현재 수량은 마지막 이벤트 또는 별도 캐시 컬럼에서 조회한다.

## 예약과 고객 객실 배정

### `reservations`

- `id`
- `external_channel`
- `external_reservation_id`
- `checkin_at`, `checkout_at`
- `standard_checkin_at`, `standard_checkout_at`
- `early_checkin_at`, `late_checkout_at`
- `status`

### `reservation_room_assignments`

- `reservation_id`
- `room_id`
- `status` (`active`, `released`, `transferred`, `checked_in`, `checked_out`)
- `assigned_by`
- `assigned_at`, `ended_at`
- `reason`

한 예약에 활성 객실 배정은 하나만 허용한다.

## 청소

### `cleaning_tasks`

- `id`
- `room_id`
- `service_date`
- `task_type` (`checkout`, `stayover`, `reclean`, `reopen_inspection`)
- `status` (`waiting`, `claimable`, `assigned`, `in_progress`, `uploading`, `inspection`, `reclean`, `approved`, `cancelled`, `excluded`)
- `available_at`, `due_at`
- `price_snapshot`
- `assignment_enabled`
- `claim_open`
- `version`

### `cleaning_task_assignments`

- `cleaning_task_id`
- `maid_id`
- `source` (`admin`, `maid_claim`)
- `status` (`active`, `ended`, `interrupted`)
- `assigned_at`, `ended_at`
- `reason`

작업당 활성 담당은 한 명만 허용한다.

### `cleaning_check_results`

- `cleaning_task_id`
- `checklist_item_id`
- `checked`
- `checked_at`

### `cleaning_photos`

- `cleaning_task_id`
- `category`
- `original_url`, `thumbnail_url`
- `captured_at`, `uploaded_at`
- `upload_status`
- `submission_version`
- `uploaded_by`

### `inspections`

- `cleaning_task_id`
- `submission_version`
- `status` (`pending`, `approved`, `rejected`)
- `inspector_id`
- `reason`
- `created_at`, `decided_at`

### `inspection_photo_reviews`

- `inspection_id`
- `cleaning_photo_id`
- `reviewed_at`
- `result`

## 정산과 벌점

### `weekly_pay_periods`

- `id`
- `starts_at`, `ends_at`
- `status` (`open`, `locked`, `paid`)

### `weekly_pay_items`

- `period_id`
- `maid_id`
- `cleaning_task_id`
- `base_amount`
- `adjustment_amount`
- `final_amount`
- `status`

### `weekly_payment_events`

- `period_id`
- `maid_id`
- `action` (`marked_paid`, `reverted_unpaid`)
- `amount`
- `reason`
- `actor_id`
- `created_at`

### `penalties`

- `maid_id`
- `cleaning_task_id` nullable
- `category`
- `points`
- `reason`
- `evidence`
- `status` (`active`, `void`)
- `created_by`, `voided_by`, `restored_by`
- timestamps and reasons

## 이력과 알림

### `audit_events`

- `aggregate_type`, `aggregate_id`
- `event_type`
- `before_json`, `after_json`
- `reason`
- `actor_id`
- `request_id`, `idempotency_key`
- `created_at`

### `room_daily_snapshots`

빠른 일자별 조회를 위한 읽기 모델이다. 원본 진실은 이벤트·예약·작업 테이블이며, 스냅샷은 재생성 가능해야 한다.

### `notifications`

- `recipient_id`
- `type`
- `payload_json`
- `read_at`
- `push_status`

## 핵심 제약조건

- 운영 중지 객실에는 활성 예약 객실 배정·활성 청소 작업을 생성하지 않는다.
- 한 청소 작업에 활성 담당은 최대 한 명.
- 한 예약에 활성 객실 배정은 최대 한 개.
- 검수 승인 없이 청소 작업을 `approved`로 변경할 수 없다.
- 지급 완료 상태 변경은 감사 이벤트와 같은 트랜잭션에 저장한다.
- 메이드 퇴사는 물리 삭제하지 않는다.
'''

docs['07_API_AND_TRANSACTION_DESIGN.md'] = r'''# 7. API와 트랜잭션 설계

## 조회 API 예시

```text
GET /api/room-operations?date=2026-08-14&type=standard&view=cleaning-needed
GET /api/rooms/{roomId}?date=2026-08-14
GET /api/cleaning-tasks/market?date=2026-08-14
GET /api/maids/me/tasks?date=2026-08-14
GET /api/inspections?status=pending
GET /api/weekly-pay?week=2026-W33
GET /api/audit-events?roomId=608&date=2026-08-14
```

## 명령 API 예시

직접 필드 PATCH보다 업무 명령 형태를 권장한다.

```text
POST /api/rooms/{id}/commands/stop-operation
POST /api/rooms/{id}/commands/resume-operation
POST /api/reservations/{id}/commands/assign-room
POST /api/reservations/{id}/commands/transfer-room
POST /api/reservations/{id}/commands/release-room
POST /api/reservations/{id}/commands/check-in
POST /api/reservations/{id}/commands/check-out
POST /api/cleaning-tasks/{id}/commands/open-claim
POST /api/cleaning-tasks/{id}/commands/claim
POST /api/cleaning-tasks/{id}/commands/assign
POST /api/cleaning-tasks/{id}/commands/unassign
POST /api/cleaning-tasks/{id}/commands/start
POST /api/cleaning-tasks/{id}/commands/submit
POST /api/inspections/{id}/commands/approve
POST /api/inspections/{id}/commands/reject
POST /api/weekly-pay/{periodId}/maids/{maidId}/commands/mark-paid
POST /api/weekly-pay/{periodId}/maids/{maidId}/commands/revert-unpaid
POST /api/penalties/{id}/commands/void
POST /api/penalties/{id}/commands/restore
```

모든 중요 명령에는 다음을 포함한다.

```json
{
  "expectedVersion": 12,
  "reason": "관리자 입력 사유",
  "idempotencyKey": "uuid",
  "clientConfirmedAt": "2026-08-14T18:00:00+09:00"
}
```

## 일감 claim 트랜잭션

```sql
UPDATE cleaning_tasks
SET status = 'assigned', version = version + 1
WHERE id = :task_id
  AND status IN ('claimable', 'waiting')
  AND claim_open = true
  AND assignment_enabled = true
  AND assignee_id IS NULL
  AND version = :expected_version
RETURNING *;
```

성공한 경우에만 같은 트랜잭션에서 담당 이력과 감사 이벤트를 작성한다. 0행이면 이미 다른 사람이 선택했거나 상태가 바뀐 것이다.

## 운영 중지 트랜잭션

1. 객실 행 잠금.
2. 활성 예약·투숙 확인.
3. 존재하면 409 `ROOM_HAS_ACTIVE_RESERVATION_OR_GUEST`.
4. 활성 청소 담당이 있으면 중단 작업 이력 작성.
5. 청소 작업 취소·제외.
6. 운영 중지 상태 저장.
7. 감사 이벤트와 알림 outbox 저장.
8. 커밋 후 푸시 발송.

## 예약 이동 트랜잭션

- 출발 예약 배정이 여전히 활성인지 확인.
- 대상 객실을 잠그고 고객 배정 가능 조건을 다시 계산.
- 출발 배정 종료, 대상 배정 생성.
- 양 객실 감사 이벤트 저장.
- 실패 시 전부 롤백.

## 사진 업로드

1. 앱이 업로드 슬롯 요청.
2. 서버가 사전 서명 URL과 사진 레코드 생성.
3. 클라이언트가 원본 업로드.
4. 업로드 완료 콜백/검증.
5. 썸네일 생성.
6. 모든 필수 사진이 `uploaded`인 경우만 작업 제출 허용.
7. 오프라인에서는 로컬 큐에 보관하고 재시도.

## 알림 outbox

검수 반려, 담당 변경, 주급 처리, 벌점 부여는 DB 트랜잭션과 같은 순간에 outbox 레코드를 만든다. 푸시 발송 실패가 업무 상태 저장을 되돌리지는 않으며 재시도한다.

## 보안

- 접근 코드는 평문 로그에 남기지 않는다.
- 코드 조회 이벤트는 별도 저장.
- 사진 URL은 짧은 만료의 서명 URL 사용.
- 메이드 API는 본인 담당 작업만 반환.
- 정산·벌점·퇴사 처리는 관리자 세부 권한 필요.
'''

docs['08_ACCEPTANCE_CRITERIA.md'] = r'''# 8. 수용 기준

## 객실 운영

1. **608 운영 중지**  
   Given 608호가 운영 중지일 때, Then 예약·투숙·청소 작업·담당이 없고 고객 배정과 메이드 선택이 모두 불가능해야 한다.
2. **예약 객실 운영 중지 차단**  
   Given 활성 예약이 있는 객실에서, When 운영 중지를 확정하려 하면, Then 저장하지 않고 예약 이동·배정 해제를 요구해야 한다.
3. **운영 재개**  
   When 운영 중지 객실을 재개하면, Then `운영 재개 점검 청소`를 담당 미지정·선택 클로즈로 생성하고 고객 배정은 계속 막아야 한다.
4. **입실 잠금**  
   Given 예약이 배정됐지만 청소·검수 미완료라면, Then 입실 버튼은 비활성화되어야 한다.
5. **촛불 독립성**  
   Given 촛불이 1개 이상이어도, When 다른 모든 조건이 충족되면, Then 고객 배정 가능이어야 한다.

## 청소 배정

6. 메이드가 일감을 선택하기 전 금액·유형·시각과 직접 취소 불가 안내를 확인해야 한다.
7. 동시에 두 메이드가 선택하면 한 명만 성공해야 한다.
8. 관리자는 담당자를 다른 메이드 또는 미배정으로 바꿀 수 있어야 한다.
9. 청소 중 담당 변경 시 기존 사진·체크·시각이 중단 이력에 남아야 한다.
10. 운영 중지·작업 없음·검수 완료 객실은 담당 배정 대상에 노출되면 안 된다.

## 검수

11. 필수 사진 업로드가 완료되지 않으면 검수 요청할 수 없다.
12. 관리자가 모든 사진을 확인하기 전 승인할 수 없다.
13. 반려 시 선택 사진·사유·상세 지시가 메이드에게 전달되어야 한다.
14. 메이드 화면에 미확인 반려 알림점과 재청소 카드가 보여야 한다.
15. 검수 반려만으로 벌점이 자동 생성되면 안 된다.

## 정산과 벌점

16. 검수 승인 시 작업 금액이 해당 주의 확정 주급에 한 번만 반영되어야 한다.
17. 지급 완료를 미지급으로 되돌릴 때 사유가 필수여야 한다.
18. 벌점 부여에는 사유와 근거가 필수여야 한다.
19. 벌점 삭제 후 활성 점수에서 제외되지만 기록은 남아야 한다.
20. 벌점 복구 시 복구 사유와 알림 이력이 남아야 한다.

## 계정과 이력

21. 퇴사 처리된 메이드는 로그인과 신규 일감 선택이 불가능해야 한다.
22. 퇴사 후에도 과거 작업·사진·검수·주급·벌점이 조회되어야 한다.
23. 과거 날짜 원본은 수정할 수 없어야 한다.
24. 과거 정정은 원본을 덮어쓰지 않고 별도 이벤트로 남아야 한다.
25. 모든 중요 변경에는 actor, time, reason, before, after가 기록되어야 한다.

## 모바일·품질

26. 360px, 390px, 430px에서 가로 스크롤이 없어야 한다.
27. 색상만으로 상태를 전달하지 않고 텍스트를 병기해야 한다.
28. 버튼 중복 탭과 네트워크 재시도에도 명령이 중복 실행되지 않아야 한다.
29. 오프라인 사진은 유실 없이 재전송되어야 한다.
30. 권한 없는 사용자의 API 직접 호출은 서버에서 거절되어야 한다.
'''

docs['09_CRITIQUE_AND_IMPROVEMENTS.md'] = r'''# 9. 현재 시안의 비판점과 개선 우선순위

## 현재 시안의 강점

- 청소 중심이 아니라 객실 운영 중심으로 정보 구조를 재정렬했다.
- 고객 배정과 청소 담당 배정을 분리했다.
- 운영 중지와 예약 충돌을 명시적으로 다룬다.
- 메이드 선택 후 관리자 변경·미배정 회수가 가능하다.
- 검수 사진, 주급, 벌점, 소프트 삭제, 날짜 이력을 한 흐름으로 연결했다.
- 주요 변경에 확인 모달과 되돌리기 경로가 있다.
- 모바일 360·390·430px에서 핵심 화면을 점검했다.

## 현재 시안의 구조적 한계

1. **단일 HTML 모놀리스**  
   UI, 상태, 비즈니스 규칙, 샘플 데이터가 한 파일에 있다. 실제 개발에서는 기능 모듈과 도메인 서비스를 분리해야 한다.
2. **메모리 상태**  
   새로고침하면 초기화된다. 다중 기기·동시 사용·감사 로그가 없다.
3. **이름 기반 담당 연결**  
   일부 샘플 로직은 `김하나` 같은 표시 이름으로 연결한다. 실제 DB는 불변 UUID를 써야 한다.
4. **예약과 투숙 상태 혼재**  
   `reservationAssigned`와 `stayStatus`가 함께 있어 모순 가능성이 있다. 예약 상태 머신과 투숙 이벤트를 분리해야 한다.
5. **스냅샷 복제**  
   날짜별 전체 객실 배열 복제는 프로토타입에는 편하지만 운영 DB의 진실 원본으로 부적절하다.
6. **동시성 부재**  
   일감 선택·예약 이동·검수 승인·주급 처리에서 경쟁 조건을 막을 서버 트랜잭션이 없다.
7. **사진이 샘플 그래픽**  
   원본·썸네일·업로드 재시도·EXIF·저장 기간·개인정보 정책이 없다.
8. **비밀번호 보안 미구현**  
   암호화·마스킹·권한·조회 로그·유효 기간·도어락 반영이 없다.
9. **알림 미구현**  
   토스트만 있으며 푸시·읽음·재시도·중요도 설정이 없다.
10. **주급·벌점 정책 미확정**  
    주급 마감·지급일, 부분 작업비, 정산 조정, 벌점 기준·초기화·이의 절차가 필요하다.
11. **접근성·오프라인·오류 복구 부족**  
    네트워크가 불안한 현장 환경을 고려한 큐와 동기화 UX가 필요하다.
12. **관리자 권한이 한 종류**  
    운영·검수·정산·계정·비밀번호 열람 권한을 나눠야 한다.

## P0 — 실사용 전에 반드시

- PostgreSQL 기반 도메인 모델과 마이그레이션
- 관리자·메이드 인증과 세부 RBAC
- 서버 측 상태 전이 검증
- 원자적 일감 claim과 optimistic locking
- 예약 이동·운영 중지·검수·정산 트랜잭션
- 감사 로그와 idempotency key
- 사진 원본 저장·썸네일·업로드 재시도
- 푸시 알림과 outbox
- 접근 코드 암호화·조회 로그
- 실제 객실·메이드·청소비·주급 규칙 확정

## P1 — 운영 안정화

- PWA 오프라인 큐
- 예약 CSV 가져오기와 중복 검증
- PMS/OTA 연동 어댑터
- 주급 잠금·엑셀·지급 배치
- 객실 이슈 처리 담당·기한·완료 사진
- 알림 우선순위와 미확인 대시보드
- 관리자 역할 세분화
- E2E·API·DB 제약 테스트

## P2 — 최적화

- 메이드 이동 동선과 마감 기반 추천
- 청소 예상 시간 학습
- 사진 누락·흐림 보조 감지
- 운영 리포트와 객실별 반복 이슈 통계
- 다지점 지원

## 아직 운영 결정이 필요한 질문

- 주급 산정 주차와 지급 요일은 정확히 언제인가?
- 담당 변경 전 기존 메이드의 부분 작업비를 지급하는가?
- 객실 유형별 기본 청소비와 추가 수당은?
- 검수는 전 객실인지 표본 검수인지?
- 벌점 사유별 점수, 누적 초기화, 이의 처리 기준은?
- 촛불 위치까지 저장할지 수량만 저장할지?
- 운영 중지 재개 후 점검 청소의 검수자는 누구인가?
- 고객 예약 정보를 어느 시스템에서 가져오는가?
'''

docs['10_CODEX_IMPLEMENTATION_GUIDE.md'] = r'''# 10. Codex 구현 가이드

## 권장 기술 구조

- **Frontend:** React + TypeScript + Vite, 모바일 PWA
- **UI 상태:** TanStack Query + 작은 로컬 UI store
- **Forms:** React Hook Form + schema validation
- **Backend:** TypeScript API 또는 서버 프레임워크
- **DB:** PostgreSQL
- **사진:** S3 호환 object storage
- **Push:** Web Push/FCM 계열
- **Tests:** unit + API integration + Playwright E2E

특정 공급자는 바꿀 수 있지만, 트랜잭션·RLS/RBAC·object storage·push가 필요하다.

## 프런트엔드 모듈 제안

```text
src/
  app/
  auth/
  rooms/
    room-operations/
    guest-allocation/
    room-issues/
    access-codes/
  cleaning/
    task-market/
    task-detail/
    assignment/
    photos/
    inspection/
  workforce/
    maids/
    weekly-pay/
    penalties/
  history/
  notifications/
  shared/
```

## 도메인 서비스 제안

```text
RoomOperationService
ReservationAssignmentService
CleaningTaskService
InspectionService
WeeklyPayService
PenaltyService
AuditService
NotificationService
```

컴포넌트에서 여러 필드를 직접 바꾸지 말고 도메인 명령을 호출한다.

## 구현 단계

### 0단계: 규칙 고정

- 운영 상태·예약·투숙·청소 상태 enum 확정
- 주급·벌점 운영 정책 확정
- 실제 객실 유형·가격·체크리스트 수집

### 1단계: 읽기 전용 관리자 객실판

- DB 스키마
- 로그인/RBAC
- 일자별 객실 운영 읽기 모델
- 네 운영 목록과 필터
- 608 불변식 테스트

### 2단계: 객실 운영과 고객 배정

- 운영 중지·재개
- 예약 배정·이동·해제·입실·퇴실
- 차단 특이사항
- 얼리·레이트
- 접근 코드
- 모든 명령 감사 로그

### 3단계: 청소 배정

- 작업 생성
- 공개·클로즈
- 원자적 메이드 선택
- 관리자 직접 배정·변경·미배정
- 작업 중단 이력

### 4단계: 메이드 현장 앱

- 담당 작업·비밀번호 권한
- 체크리스트
- 오프라인 사진 큐
- 촛불 수량
- 완료 제출

### 5단계: 검수·알림

- 사진 검수
- 승인·반려
- 메이드 재청소 알림
- 객실 준비 완료 파생 계산

### 6단계: 주급·벌점·계정

- 주차별 정산
- 지급·취소 로그
- 벌점 정책
- 메이드 소프트 삭제

### 7단계: 외부 연동

- CSV
- PMS/OTA
- 도어락

## Codex가 처음 수행할 작업

1. `CURRENT` HTML에서 화면·문구·상호작용 인벤토리를 추출한다.
2. `03_STATE_MODEL_AND_BUSINESS_RULES.md`를 TypeScript 타입과 순수 파생 함수로 옮긴다.
3. `08_ACCEPTANCE_CRITERIA.md`를 테스트 파일로 먼저 만든다.
4. 608호·예약 충돌·일감 claim·검수 승인 시나리오부터 구현한다.
5. 프로토타입과 모바일 390px 렌더를 비교한다.

## 금지할 구현 방식

- `room.status = "red"` 같은 색상 중심 상태 저장
- UI에서만 버튼을 숨기고 서버는 허용하는 방식
- 메이드 이름 문자열을 foreign key로 사용
- 기존 이력을 UPDATE로 덮어쓰기
- 벌점 발생 시 자동 임금 차감
- 운영 중지 객실에 청소·예약을 생성한 뒤 화면에서만 숨기기
- 사진 업로드 완료 전에 검수 요청 상태로 변경
'''

docs['11_USAGE_GUIDE.md'] = r'''# 11. 현재 HTML 사용법

## PC에서 보기

브라우저로 HTML을 열면 왼쪽에 프로토타입 빠른 탐색, 오른쪽에 모바일 앱 프레임이 보인다. 빠른 화면 전환 버튼으로 관리자·메이드 주요 상태를 확인할 수 있다.

## 모바일에서 보기

휴대폰 브라우저로 파일 또는 로컬 서버 주소를 열면 휴대폰 프레임 없이 화면 전체를 앱처럼 사용한다. 기준 폭은 390px이며 360px·430px도 검수했다.

## 관리자 핵심 확인 순서

1. 관리자로 로그인.
2. `객실`에서 날짜와 네 운영 목록 확인.
3. 608호를 열어 운영 중지·예약 없음·작업 없음 확인.
4. `운영 상태 변경`에서 재개를 선택하고 최종 확인 모달 확인.
5. 예약 충돌 객실 108호에서 예약 이동·배정 해제 흐름 확인.
6. 1502호에서 고객 배정 화면을 열어 청소 미완료 시 입실 잠금 확인.
7. `청소 배정`에서 단일 일감 오픈·클로즈와 담당 변경·미배정 확인.
8. `검수`에서 사진 확인·승인·반려 확인.
9. `주급`에서 지급 완료를 미지급으로 되돌리는 흐름 확인.
10. `더보기`에서 메이드·벌점 관리 확인.

## 메이드 핵심 확인 순서

1. 메이드로 로그인 또는 역할 전환.
2. `일감 찾기`에서 가격·시간 확인 후 `이 객실 맡기`.
3. 선택 확인 모달에서 직접 취소 불가 안내 확인.
4. `내 업무`에서 작업을 열고 청소 시작 확인.
5. 체크리스트·사진·촛불 수량을 입력하고 검수 요청.
6. 반려된 작업의 빨간 알림·사진·사유 확인.
7. `주급`, `내 정보 → 벌점` 확인.

## 날짜 이력

- 날짜 버튼을 누르면 월 달력이 열린다.
- 과거 날짜는 읽기 전용이다.
- 오기입은 `기록 정정`에서 내용과 사유를 입력한 뒤 최종 확인한다.

## 프로토타입 제한

- 입력 상태는 새로고침 시 사라진다.
- 샘플 사진은 실제 업로드 파일이 아니다.
- 푸시·문자·카카오 알림은 토스트로만 표현한다.
- 엑셀 내보내기·도어락·OTA 연동은 위치만 있다.
'''

docs['12_CHANGELOG.md'] = r'''# 12. 프로토타입 변경 이력

| 버전 | 주요 변화 |
|---|---|
| v2 | 관리자·메이드 역할별 모바일 기본 구조, 객실·청소·비밀번호 초기 흐름 |
| v3 | 전체 객실표, 메이드 일감 선택, 메이드 계정 관리, 주급 정산, 촛불 수량 의미 수정 |
| v4 | 인증사진 상세 검수, 사진 확대·재청소 요청, 메이드 소프트 삭제·복구 |
| v5 | 관리자 담당 변경·미배정 회수, 배정 가능·담당 확정·배정 불가 분리, 중단 이력 |
| v6–v7 | 고객 객실 배정과 청소 담당 배정의 개념 분리, 객실 유형·상태 필터 보강 |
| v8 | 관리자 네 운영 목록, 촛불 독립 현황, 얼리·레이트 정확한 시각, 달력·일자별 이력 |
| v9 | 메이드 선택 확인, 고객 객실 배정·해제, 주급 지급 취소 등 안전장치 확장 |
| v10 | 벌점 부여·삭제·복구, 메이드 알림, 주급과 벌점 분리 |
| v11 | 객실 운영 중지 상위 상태, 예약 충돌 해결, 608호 모순 제거, 운영 재개 점검 청소 |
| v12 | 입실 처리 서버 규칙에 가까운 잠금, 단일 공개 변경·청소 시작·검수 반려·메이드 저장·퇴사 복구·과거 정정 등 확인 모달 전반 보강 |

`HISTORY/`에는 각 HTML 원본을 보관했다. 중간 버전은 구조 탐색 자료이며 실제 구현 기준은 v12와 본 문서다.
'''

docs['13_QA_REPORT.md'] = r'''# 13. QA 보고서

## 자동 검수 결과

- 대상: `castle_the_art_room_manager_wireframe_v12.html`
- 결과: **30/30 통과**
- 콘솔 오류: 없음
- 모바일 가로 넘침: 360px, 390px, 430px 모두 없음

## 검수한 핵심 항목

- 608 운영 중지 불변식
- 608 예약·청소 없음 표시
- 운영 재개 최종 확인과 점검 청소 생성
- 예약 보유 객실 운영 중지 차단
- 예약 이동 최종 확인
- 청소 미완료 예약 객실 입실 잠금
- 얼리·레이트 변경 확인
- 차단 특이사항과 예약 충돌 경고
- 단일 일감 오픈·클로즈 확인
- 메이드 일감 선택 확인
- 메이드 청소 시작 확인
- 검수 반려·승인 확인
- 주급 지급 취소 확인
- 메이드 계정 추가·퇴사 복구 확인
- 과거 이력 정정 확인
- 벌점 부여 확인
- 달력 날짜 선택

상세 결과는 `QA/castle_the_art_v12_qa_report.json`을 본다.

## 시각 검수

`QA/screenshots/`에는 390×844 모바일 기준 주요 화면이 있다. 프로토타입은 별도 이미지 콘셉트가 아니라 이전 HTML 디자인 시스템을 계속 확장한 것이므로, 최종 비교 기준은 v12 렌더와 v10–v11의 승인된 화면 흐름이다.
'''

docs['CODEX_PROMPT.md'] = r'''# Codex에 전달할 시작 프롬프트

아래 폴더는 Castle The Art 객실관리 내부 앱의 클릭형 프로토타입과 기능·상태·데이터·테스트 명세다.

먼저 `00_START_HERE.md`부터 읽고, `03_STATE_MODEL_AND_BUSINESS_RULES.md`, `05_CONFIRMATION_AND_SAFETY_MATRIX.md`, `08_ACCEPTANCE_CRITERIA.md`를 구현 규칙의 우선 기준으로 삼아라. `CURRENT/castle_the_art_room_manager_wireframe_v12.html`은 모바일 UI와 문구·상호작용의 시각 기준이다.

목표는 단일 HTML을 그대로 배포하는 것이 아니라 React + TypeScript 기반 모바일 PWA와 서버·PostgreSQL 구조로 재구현하는 것이다.

반드시 지킬 것:

1. 객실 운영 상태, 예약·투숙, 청소, 검수, 차단 특이사항을 독립 축으로 모델링한다.
2. 608호 `운영 중지 + 예약 없음 + 작업 없음 + 담당 없음 + 고객 배정 불가`를 자동 테스트한다.
3. 예약 객실 운영 중지, 청소 미완료 입실, 중복 메이드 claim을 서버에서 차단한다.
4. 중요 명령은 사유·최종 확인·expectedVersion·idempotency key·감사 로그를 사용한다.
5. 메이드 선택은 DB 트랜잭션으로 한 명만 성공시킨다.
6. 과거 이력은 덮어쓰지 않고 정정 이벤트로 추가한다.
7. 사진 업로드는 오프라인 재시도와 제출 버전을 지원한다.
8. 벌점과 주급은 자동 연결하지 않는다.
9. 모든 화면을 360/390/430px에서 테스트한다.

첫 산출물:

- 앱·도메인·DB 아키텍처 문서
- TypeScript 상태 타입과 파생 함수
- PostgreSQL 마이그레이션 초안
- `08_ACCEPTANCE_CRITERIA.md`의 P0 테스트
- 관리자 객실 운영판과 608호/예약 충돌 흐름

기존 프로토타입에서 규칙이 모호하면 임의로 단순화하지 말고 `09_CRITIQUE_AND_IMPROVEMENTS.md`의 미결정 항목으로 기록한 뒤 질문하라.
'''

for name, content in docs.items():
    (ROOT/'DOCS'/name).write_text(textwrap.dedent(content).strip()+"\n", encoding='utf-8')

# Root README redirects to start doc.
(ROOT/'README.md').write_text("# Castle The Art Codex Handoff v12\n\nStart with [`DOCS/00_START_HERE.md`](DOCS/00_START_HERE.md).\n", encoding='utf-8')

# Flowchart DOT files.
common = '''digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.35", ranksep="0.5", fontname="Noto Sans CJK KR"];
  node [shape=box, style="rounded,filled", fillcolor="#F7F8FA", color="#B8C0C8", fontname="Noto Sans CJK KR", fontsize=11, margin="0.14,0.09"];
  edge [color="#63707A", fontname="Noto Sans CJK KR", fontsize=9, arrowsize=0.7];
'''
flow_dots = {
'01_room_operation_guest_allocation': common + r'''
  start [label="날짜별 객실 운영 현황", fillcolor="#EAF2F8"];
  op [label="운영 중지?", shape=diamond, fillcolor="#FFF2F2"];
  stopped [label="고객 배정 불가\n청소 제외·담당 불가", fillcolor="#FDECEC", color="#D9474F"];
  conflict [label="예약 + 운영중지/차단 이슈?", shape=diamond];
  conflict_state [label="예약 충돌\n입실 잠금", fillcolor="#FDECEC", color="#D9474F"];
  resolve [label="예약 이동 또는 배정 해제"];
  occupied [label="투숙 중?", shape=diamond];
  occupied_block [label="신규 배정 불가"];
  assigned [label="예약 배정됨?", shape=diamond];
  assigned_state [label="예약 배정 완료"];
  ready_check [label="청소·검수 완료?", shape=diamond];
  checkin [label="입실 처리 가능", fillcolor="#E8F6EF", color="#2C8B68"];
  locked [label="입실 처리 잠금", fillcolor="#FFF4E3", color="#C57A13"];
  available_check [label="차단 이슈 없음 + 입실 준비 완료?", shape=diamond];
  available [label="고객 배정 가능", fillcolor="#E8F6EF", color="#2C8B68"];
  unavailable [label="고객 배정 불가 사유 표시", fillcolor="#FFF4E3", color="#C57A13"];
  start -> op;
  op -> stopped [label="예"];
  op -> conflict [label="아니오"];
  conflict -> conflict_state [label="예"];
  conflict_state -> resolve;
  resolve -> conflict;
  conflict -> occupied [label="아니오"];
  occupied -> occupied_block [label="예"];
  occupied -> assigned [label="아니오"];
  assigned -> assigned_state [label="예"];
  assigned_state -> ready_check;
  ready_check -> checkin [label="예"];
  ready_check -> locked [label="아니오"];
  assigned -> available_check [label="아니오"];
  available_check -> available [label="예"];
  available_check -> unavailable [label="아니오"];
}''',
'02_608_operation_stop_resume': common + r'''
  request [label="운영 중지 요청"];
  has [label="예약 또는 투숙 있음?", shape=diamond];
  block [label="운영 중지 확정 차단", fillcolor="#FDECEC", color="#D9474F"];
  resolve [label="예약 이동·배정 해제·퇴실"];
  reason [label="운영 중지 사유 입력"];
  confirm [label="최종 확인 모달"];
  tx [label="운영 중지 트랜잭션", fillcolor="#EAF2F8"];
  inv [label="예약 없음\n작업 없음\n담당 없음\n고객 배정 불가", fillcolor="#FDECEC", color="#D9474F"];
  resume [label="정상 운영 재개 요청"];
  resume_confirm [label="사유 + 최종 확인"];
  clean [label="운영 재개 점검 청소 생성\n미배정·선택 클로즈", fillcolor="#FFF4E3", color="#C57A13"];
  inspect [label="청소·검수 승인"];
  recalc [label="고객 배정 가능 여부 재계산", fillcolor="#E8F6EF", color="#2C8B68"];
  request -> has;
  has -> block [label="예"];
  block -> resolve;
  resolve -> request;
  has -> reason [label="아니오"];
  reason -> confirm -> tx -> inv;
  inv -> resume -> resume_confirm -> clean -> inspect -> recalc;
}''',
'03_cleaning_assignment_claim': common + r'''
  task [label="청소 작업 생성"];
  eligible [label="담당 배정 가능?", shape=diamond];
  no [label="배정 불가 사유 표시", fillcolor="#FDECEC", color="#D9474F"];
  method [label="배정 방식", shape=diamond];
  direct [label="관리자 직접 배정\n메이드·사유·확인"];
  open [label="메이드 선택 오픈"];
  see [label="메이드가 금액·시간 확인"];
  confirm [label="선택 확인 모달\n직접 취소 불가 안내"];
  claim [label="원자적 claim 트랜잭션", fillcolor="#EAF2F8"];
  success [label="담당 확정\n다른 메이드 목록 제거", fillcolor="#E8F6EF", color="#2C8B68"];
  fail [label="이미 선택됨 안내", fillcolor="#FDECEC", color="#D9474F"];
  admin [label="관리자 변경 필요?", shape=diamond];
  change [label="다른 메이드로 변경\n사유·이력"];
  unassign [label="미배정 회수\n선택 오픈/클로즈"];
  task -> eligible;
  eligible -> no [label="아니오"];
  eligible -> method [label="예"];
  method -> direct [label="직접"];
  method -> open [label="자유 선택"];
  open -> see -> confirm -> claim;
  claim -> success [label="성공"];
  claim -> fail [label="경쟁 실패"];
  direct -> success;
  success -> admin;
  admin -> change [label="담당 변경"];
  admin -> unassign [label="미배정"];
}''',
'04_cleaning_inspection': common + r'''
  assigned [label="담당 객실"];
  start [label="청소 시작 확인"];
  work [label="체크리스트·사진·특이사항"];
  candle [label="청소 후 촛불 수량 기록"];
  submit [label="완료·검수 요청 확인"];
  pending [label="검수 대기", fillcolor="#FFF4E3", color="#C57A13"];
  review [label="관리자 사진별 확인"];
  decision [label="검수 결과", shape=diamond];
  approve [label="승인 최종 확인"];
  ready [label="입실 준비 완료\n주급 확정", fillcolor="#E8F6EF", color="#2C8B68"];
  reject [label="선택 사진·사유 입력"];
  reject_confirm [label="반려 최종 확인"];
  reclean [label="재청소 필요\n메이드 알림", fillcolor="#FDECEC", color="#D9474F"];
  penalty [label="필요 시 별도 벌점 절차", fillcolor="#F7F0FA", color="#8B5AA5"];
  assigned -> start -> work -> candle -> submit -> pending -> review -> decision;
  decision -> approve [label="승인"];
  approve -> ready;
  decision -> reject [label="반려"];
  reject -> reject_confirm -> reclean -> work;
  decision -> penalty [label="별도 판단"];
}''',
'05_weekly_pay_penalty': common + r'''
  approved [label="검수 승인 작업"];
  item [label="주급 확정 항목"];
  sum [label="주차별 합산"];
  paid [label="실제 송금 완료?", shape=diamond];
  mark [label="지급 완료 확인·로그", fillcolor="#E8F6EF", color="#2C8B68"];
  mistake [label="기록 실수?", shape=diamond];
  revert [label="사유 입력 후 미지급 복구", fillcolor="#FFF4E3", color="#C57A13"];
  wait [label="미지급 유지"];
  issue [label="품질 문제 확인"];
  evidence [label="벌점 사유·근거 입력"];
  pconfirm [label="벌점 부여 최종 확인"];
  active [label="유효 벌점·메이드 알림", fillcolor="#FDECEC", color="#D9474F"];
  voidq [label="삭제 필요?", shape=diamond];
  void [label="사유·소프트 삭제"];
  restoreq [label="복구 필요?", shape=diamond];
  restore [label="복구 사유·유효 상태 복원"];
  approved -> item -> sum -> paid;
  paid -> mark [label="예"];
  paid -> wait [label="아니오"];
  mark -> mistake;
  mistake -> revert [label="예"];
  issue -> evidence -> pconfirm -> active -> voidq;
  voidq -> void [label="예"];
  void -> restoreq;
  restoreq -> restore [label="예"];
}''',
'06_date_history_correction': common + r'''
  calendar [label="달력에서 날짜 선택"];
  snapshot [label="해당 날짜 객실 읽기 모델 조회"];
  today [label="오늘인가?", shape=diamond];
  live [label="실시간 상태 변경 가능", fillcolor="#E8F6EF", color="#2C8B68"];
  readonly [label="과거 원본 읽기 전용", fillcolor="#EAF2F8"];
  wrong [label="오기입 발견?", shape=diamond];
  input [label="정정 내용·사유 입력"];
  confirm [label="정정 최종 확인"];
  append [label="원본 유지\n정정 이벤트 추가", fillcolor="#FFF4E3", color="#C57A13"];
  calendar -> snapshot -> today;
  today -> live [label="예"];
  today -> readonly [label="아니오"];
  readonly -> wrong;
  wrong -> input [label="예"];
  input -> confirm -> append;
}'''
}

for stem, dot in flow_dots.items():
    dot_path = ROOT/'FLOWCHARTS'/f'{stem}.dot'
    dot_path.write_text(dot, encoding='utf-8')
    subprocess.run(['dot','-Tsvg',str(dot_path),'-o',str(ROOT/'FLOWCHARTS'/f'{stem}.svg')], check=True)
    subprocess.run(['dot','-Tpng',str(dot_path),'-o',str(ROOT/'FLOWCHARTS'/f'{stem}.png')], check=True)

# Flowchart index HTML.
flow_items='\n'.join([f'<section><h2>{stem.replace("_"," ")}</h2><img src="{stem}.svg" alt="{stem}"></section>' for stem in flow_dots])
(ROOT/'FLOWCHARTS'/'index.html').write_text(f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Castle The Art Flowcharts</title><style>body{{font-family:"Noto Sans CJK KR",sans-serif;margin:0;background:#f4f6f8;color:#17212a}}main{{max-width:1100px;margin:auto;padding:32px}}section{{background:white;border:1px solid #d9dfe4;border-radius:18px;padding:20px;margin:0 0 24px;box-shadow:0 8px 22px rgba(20,30,40,.05)}}h1{{font-size:28px}}h2{{font-size:18px}}img{{width:100%;height:auto}}</style></head><body><main><h1>Castle The Art 업무 플로우차트</h1>{flow_items}</main></body></html>''', encoding='utf-8')

# Manifest with hashes.
manifest=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file():
        data=p.read_bytes()
        manifest.append({'path':str(p.relative_to(ROOT)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(ROOT/'manifest.json').write_text(json.dumps({'package':'Castle The Art Codex Handoff','version':'v12','generated_at':'2026-08-14','files':manifest}, ensure_ascii=False, indent=2), encoding='utf-8')

print(ROOT)
print('files', sum(1 for _ in ROOT.rglob('*') if _.is_file()))
