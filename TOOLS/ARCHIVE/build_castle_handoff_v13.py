from pathlib import Path
import shutil, json, hashlib, os
from datetime import datetime, timezone, timedelta

SRC = Path('/mnt/data/Castle_The_Art_Codex_Handoff_FINAL_v12')
ROOT = Path('/mnt/data/Castle_The_Art_Codex_Handoff_FINAL_v13')
if ROOT.exists():
    shutil.rmtree(ROOT)
shutil.copytree(SRC, ROOT)

# Clean current deliverables and legacy v12 QA that could be mistaken for the current source of truth.
for p in (ROOT/'CURRENT').glob('*'):
    if p.is_file(): p.unlink()
for sub in ['screenshots_v13','focused_v13','extended_v13']:
    q=ROOT/'QA'/sub
    if q.exists(): shutil.rmtree(q)

# Current executable prototype and source extracts.
shutil.copy2('/mnt/data/castle_the_art_room_manager_wireframe_v13.html', ROOT/'CURRENT'/'castle_the_art_room_manager_wireframe_v13.html')
shutil.copy2('/mnt/data/castle_the_art_room_manager_wireframe_latest.html', ROOT/'CURRENT'/'castle_the_art_room_manager_wireframe_latest.html')
shutil.copy2('/mnt/data/castle_the_art_room_manager_wireframe_v13.html', ROOT/'CURRENT'/'index.html')
shutil.copy2('/mnt/data/castle_v13_script.js', ROOT/'CURRENT'/'castle_v13_script.js')

# Historical sources and reproduction tools.
shutil.copy2('/mnt/data/castle_the_art_room_manager_wireframe_v13.html', ROOT/'HISTORY'/'castle_the_art_room_manager_wireframe_v13.html')
for tool in ['patch_castle_v13.py','patch_v13_maid_candle_permissions.py','qa_castle_v13.py','qa_castle_v13_handoff.py','capture_castle_v13_handoff.py','build_castle_handoff_v13.py']:
    src=Path('/mnt/data')/tool
    if src.exists(): shutil.copy2(src, ROOT/'TOOLS'/tool)

# Current QA reports/scripts/screenshots.
(ROOT/'QA'/'focused_v13').mkdir(parents=True, exist_ok=True)
(ROOT/'QA'/'extended_v13').mkdir(parents=True, exist_ok=True)
(ROOT/'QA'/'screenshots_v13').mkdir(parents=True, exist_ok=True)
shutil.copy2('/mnt/data/castle_the_art_v13_qa_report.json', ROOT/'QA'/'focused_v13'/'castle_the_art_v13_qa_report.json')
shutil.copy2('/mnt/data/qa_castle_v13.py', ROOT/'QA'/'focused_v13'/'qa_castle_v13.py')
shutil.copy2('/mnt/data/castle_the_art_v13_extended_qa_report.json', ROOT/'QA'/'extended_v13'/'castle_the_art_v13_extended_qa_report.json')
shutil.copy2('/mnt/data/qa_castle_v13_handoff.py', ROOT/'QA'/'extended_v13'/'qa_castle_v13_handoff.py')
for d in ['/mnt/data/castle_the_art_v13_handoff_screens','/mnt/data/castle_the_art_v13_screens','/mnt/data/castle_the_art_v13_extended_screens']:
    src=Path(d)
    if src.exists():
        target=ROOT/'QA'/'screenshots_v13'/src.name
        shutil.copytree(src,target,dirs_exist_ok=True)

DOCS = {}
DOCS['00_START_HERE.md'] = r'''# Castle The Art 객실관리 앱 — Codex 이관 시작점 v13

## 현재 기준본

- 실행형 프로토타입: `CURRENT/castle_the_art_room_manager_wireframe_v13.html`
- 동일 최신본: `CURRENT/castle_the_art_room_manager_wireframe_latest.html`
- 브라우저 진입점: `CURRENT/index.html`
- 추출 JavaScript: `CURRENT/castle_v13_script.js`
- 집중 QA: `QA/focused_v13/qa_castle_v13.py` — **37/37 통과**
- 확장 회귀 QA: `QA/extended_v13/qa_castle_v13_handoff.py` — **59/59 통과**
- 핵심 화면: `QA/screenshots_v13/castle_the_art_v13_handoff_screens/`

이 패키지는 Castle The Art 관리자·메이드용 모바일 내부 앱을 실제 개발로 이관하기 위한 기준 자료다. 목표는 단순 청소 앱이 아니라 **객실 운영, 고객 객실 배정, 청소 일감, 인증사진 검수, 촛불 안전 상태, 메이드 주급·벌점, 일자별 이력**을 하나의 도메인으로 연결하는 것이다.

## 절대 우선 규칙

1. 객실 운영 상태, 예약·투숙, 청소·검수, 고객 배정 차단 이슈, 촛불, 청소 담당은 서로 독립된 축으로 저장한다.
2. `운영 중지`는 예약·청소보다 상위 제약이다. 운영 중지 객실에는 활성 예약, 투숙, 청소 작업, 메이드 담당, 일감 공개가 남아 있으면 안 된다.
3. **촛불이 1개라도 기록된 객실은 고객 배정과 입실이 불가능하다.** 관리자가 현장에서 회수하고 수량을 `0개`로 최종 확정해야 차단이 해제된다.
4. 메이드는 이번 작업에서 새로 둔 촛불 수량만 추가할 수 있다. 기존 양수 수량을 줄이거나 0개로 만드는 회수 확정은 관리자만 할 수 있다.
5. 기존 예약이 있는 객실에 운영 중지·차단 특이사항·촛불이 생기면 `예약 충돌`로 표시한다. 예약을 자동 삭제하지 말고, 원인 해결·예약 이동·배정 해제 중 하나를 명시적으로 처리한다.
6. 608호 기준 불변식은 `운영 중지 + 공실 + 예약 없음 + 청소 작업 없음 + 담당 없음 + 일감 공개 닫힘 + 고객 배정 불가`다. 촛불 3개도 별도 차단 사유로 남는다.
7. 중요한 변경은 `입력 → 영향 검토 → 최종 확인 모달 → 서버 최신 상태 재검증 → 트랜잭션 → 감사 로그·알림 outbox` 순서다.
8. 메이드 일감 선택은 서버에서 원자적으로 처리해 한 명만 성공해야 한다.
9. 과거 원본 기록은 덮어쓰지 않는다. 정정 이벤트를 추가한다.
10. 벌점은 주급에서 자동 차감하지 않는다.

## 빠른 실행

```bash
python -m http.server 8000 --directory CURRENT
```

브라우저에서 다음 주소를 연다.

```text
http://localhost:8000/index.html
```

단일 파일이므로 `CURRENT/castle_the_art_room_manager_wireframe_v13.html`을 브라우저로 직접 열어도 된다.

## 기준 시각과 데모 계정

- 기본 체크인: **16:00**
- 기본 체크아웃: **11:00**
- 관리자 데모 ID: `manager01`
- 메이드 데모 ID: `maid01`
- 프로토타입은 실제 인증 없이 역할별 화면으로 이동한다.

## 문서 읽기 순서

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

현재 HTML은 클릭 흐름과 업무 규칙을 시각적으로 합의하기 위한 단일 파일이다. 새로고침하면 상태가 초기화된다. 실사용 인증, DB, 실제 사진 저장, 동시성 제어, 푸시, 도어락, PMS/OTA 연동은 없다. UI의 필드 변경을 그대로 복사하지 말고, 본 문서의 도메인 명령·상태 전이·트랜잭션 규칙으로 재구현한다.
'''

DOCS['01_PRODUCT_PURPOSE_AND_SCOPE.md'] = r'''# 1. 제품 목적과 범위

## 제품 목적

Castle The Art 운영자가 모바일에서 다음 질문에 즉시 답할 수 있게 한다.

- 오늘 고객에게 배정할 수 있는 객실은 어디인가?
- 배정할 수 없다면 청소·검수, 촛불, 운영 중지, 투숙·예약, 차단 특이사항 중 무엇 때문인가?
- 퇴실 청소·연박 청소·재청소가 필요한 객실은 어디이며 담당자가 지정됐는가?
- 객실 비밀번호, 얼리 체크인·레이트 체크아웃 실제 시각, 촛불 개수는 무엇인가?
- 어떤 메이드가 무엇을 제출했고 사진 검수 결과는 무엇인가?
- 이번 주 메이드별 확정 주급과 지급 여부는 무엇인가?
- 누가 언제 상태를 바꿨으며 되돌리거나 정정한 이유는 무엇인가?

## 관리자 첫 화면의 네 운영 목록

1. **고객 배정 가능 객실**  
   정상 운영, 공실, 예약 미배정, 청소·검수 승인, 차단 특이사항 없음, **촛불 0개**를 모두 충족한다.
2. **청소 필요 객실**  
   퇴실 청소·연박 청소·재청소를 유형별로 보여주고 담당 지정·미지정을 함께 표시한다.
3. **고객 배정 불가 객실**  
   운영 중지, 청소·검수 미완료, 촛불 회수 필요, 고객 입실 중, 기존 예약 배정, 차단 특이사항, 예약 충돌 등 구체 사유를 보여준다.
4. **촛불 있는 객실**  
   수량과 위치를 교차 조회한다. 이 목록은 `고객 배정 불가`와 중복되며, 전량 회수 전 고객 배정·입실이 잠긴다.

목록은 배타적이지 않다. 예를 들어 촛불이 있는 예약 객실은 `촛불 있음`, `고객 배정 불가`, `예약 충돌`에 모두 나타날 수 있다. 중복은 오류가 아니라 운영상 필요한 교차 시야다.

## 핵심 사용자

### 관리자

- 날짜별 전체 객실 운영 현황
- 고객 객실 배정·이동·해제·입실·퇴실
- 운영 중지·재개 및 충돌 해결
- 청소 일감 생성·오픈·클로즈·직접 배정·담당 변경·미배정 회수
- 객실 비밀번호·입퇴실 시각·차단 특이사항·촛불 관리
- 인증사진 검수·승인·반려·재청소 요청
- 메이드 계정 추가·수정·비활성·퇴사 처리·복구
- 주급 지급·미지급 복구
- 벌점 부여·삭제·복구
- 일자별 조회와 과거 정정 이벤트

### 메이드

- 공개 일감의 금액·유형·시각·마감 확인 후 선택
- 선택 전 취소 제한 확인, 선택 후 관리자에게 변경 요청
- 담당 객실 비밀번호와 특이사항 확인
- 체크리스트·인증사진·작업 메모 제출
- 이번 청소에서 **새로 둔 촛불 수량 추가 기록**
- 검수 승인·반려·재청소 알림 확인
- 본인 주급·벌점 조회

## 1차 실서비스 범위

- 모바일 웹/PWA
- 관리자·메이드 인증과 세부 권한
- 객실·예약·투숙·청소·검수·촛불·주급·벌점·이력
- 사진 업로드와 재시도
- 푸시 알림 및 읽음 상태
- 감사 로그와 중요한 변경의 사유·전후 값
- CSV 예약 가져오기

## 2차 이후

- PMS/OTA 양방향 연동
- 객실 도어락 공식 API 연동
- 카카오·문자 알림
- 이동 동선·마감 기반 배정 추천
- 사진 흐림·누락 보조 판별
- 다지점 운영과 통합 리포트

## 명시적 비범위

프로토타입의 4자리 랜덤 생성은 실제 도어락을 자동 변경하지 않는다. 실제 개폐 코드로 쓰려면 도어락 공급사의 지원 방식, 만료, 동기화 실패, 비상 코드 정책을 별도로 설계해야 한다.
'''

DOCS['02_USER_ROLES_AND_SCREEN_MAP.md'] = r'''# 2. 사용자 역할과 화면 구조

## 관리자 하단 메뉴

### 객실

- 날짜 선택 월 달력과 오늘 이동
- 고객 배정 가능·청소 필요·고객 배정 불가·촛불 있음 요약
- 예약 충돌 경고
- 객실 유형·상태·담당·번호 검색
- 배정 불가 이유별 그룹
- 객실 상세
  - 운영 상태
  - 고객 객실 배정·이동·해제·입실·퇴실
  - 청소 담당 배정·변경·미배정 회수
  - 비밀번호 수정·4자리 랜덤 생성
  - 기본 16:00/11:00 및 얼리·레이트 실제 시각
  - 입실 차단 특이사항
  - 촛불 수량·위치·관리자 회수 확정
  - 일자별 변경 이력

### 청소 배정

- 배정 가능 / 담당 확정 / 배정 불가
- 퇴실 / 연박 / 재청소
- 담당 지정 / 미지정
- 메이드 선택 오픈·클로즈
- 관리자 직접 배정
- 다른 메이드로 변경
- 미배정으로 회수 후 오픈 또는 클로즈
- 작업 중 변경 시 중단 작업 이력

### 검수

- 검수 대기·재청소 목록
- 항목별 인증사진 썸네일과 원본 확대
- 사진별 확인
- 전 사진 확인 후 승인
- 선택 사진·사유 기준 반려
- 메이드 알림
- 검수 승인과 객실 가용성 분리: 촛불·차단 이슈·운영 중지는 그대로 유지
- 필요 시 별도 벌점 절차

### 주급

- 주차 선택
- 예상·확정·지급 금액
- 지급 완료 토글
- 미지급 복구 시 사유·확인
- 변경 이력과 엑셀 내보내기 위치

### 더보기

- 메이드 계정 관리와 소프트 삭제
- 벌점·컴플레인
- 객실 유형·청소비·체크리스트 설정 위치
- 역할 전환·로그아웃

## 메이드 하단 메뉴

### 일감 찾기

- 관리자가 공개한 미배정 일감만 표시
- 객실·유형·금액·청소 가능 시각·마감·얼리/레이트·현재 촛불
- 선택 전 최종 확인
- 확정 후 직접 취소 불가, 관리자에게 변경 요청

### 내 업무

- 지금 가능 / 입실 대기 / 청소 중 / 재청소
- 본인 담당만 표시
- 담당·허용 시각 조건에서 비밀번호 표시
- 시작 확인 모달
- 체크리스트·사진·특이사항
- 기존 촛불은 감소 불가, 이번 작업의 추가 수량만 기록

### 완료

- 검수 대기
- 승인 완료
- 반려·재청소와 상세 사유

### 주급 / 내 정보

- 이번 주 예상·확정·지급 완료
- 작업별 금액
- 본인 벌점·컴플레인과 미확인 알림

## 권한 원칙

- 메이드는 담당하지 않은 객실의 비밀번호를 볼 수 없다.
- 메이드는 기존 촛불 수량을 줄이거나 회수 완료 처리할 수 없다.
- 메이드는 다른 직원의 주급·벌점·작업을 볼 수 없다.
- 관리자는 운영, 검수, 정산, 계정, 민감정보 열람 권한을 세분화한다.
- 과거 비밀번호·사진 원본 조회는 별도 감사 로그를 남긴다.
'''

DOCS['03_STATE_MODEL_AND_BUSINESS_RULES.md'] = r'''# 3. 상태 모델과 핵심 업무 규칙

## 하나의 상태값으로 합치지 말 것

| 독립 축 | 예시 |
|---|---|
| 운영 상태 | `active`, `out_of_service` |
| 예약 상태 | 미배정, 객실 배정, 이동, 해제, 체크인, 체크아웃 |
| 투숙 상태 | 공실, 오늘 입실, 투숙 중, 오늘 퇴실, 장기투숙 |
| 청소 작업 | 없음, 입실 대기, 청소 가능, 청소 중, 업로드, 검수 대기, 재청소, 승인, 제외 |
| 청소 담당 | 미배정, 담당 확정, 변경, 중단 |
| 고객 배정 차단 이슈 | 없음, 해결 전 차단 |
| 촛불 | 현재 수량·위치·마지막 확인자 |
| 접근 코드 | 현재 코드·유효 기간·조회 로그 |

색상이나 `room.status = red` 같은 표시값은 저장하지 않는다. 고객 배정 가능, 예약 충돌, 청소 담당 가능, 색상은 원본 축에서 파생한다.

## 고객 객실 배정 파생 규칙

```text
hard_block = out_of_service OR blocking_issue_open OR candle_count > 0

if reservation_assigned AND hard_block:
    return RESERVATION_CONFLICT
if out_of_service:
    return UNAVAILABLE
if occupied_or_long_stay:
    return UNAVAILABLE
if reservation_assigned:
    return ASSIGNED
if blocking_issue_open:
    return UNAVAILABLE
if candle_count > 0:
    return UNAVAILABLE
if cleaning_status != APPROVED_READY:
    return UNAVAILABLE
return AVAILABLE
```

### 고객 배정 가능 조건

모두 참이어야 한다.

- 정상 운영
- 공실
- 활성 예약 객실 배정 없음
- 청소·인증사진 검수 승인 완료
- 미해결 고객 배정 차단 특이사항 없음
- **촛불 0개**

### 예약 충돌

예약이 이미 붙은 뒤 다음 중 하나가 생기면 충돌이다.

- 운영 중지
- 고객 배정 차단 특이사항
- 촛불 1개 이상

예약을 조용히 삭제하거나 `오늘 입실`만 유지하지 않는다. 관리자에게 원인 해결, 다른 가용 객실 이동, 예약 배정 해제를 제시한다.

## 고객 입실 처리 조건

- 정상 운영
- 활성 예약 객실 배정 존재
- 현재 투숙 중이 아님
- 청소·검수 승인 완료
- 차단 특이사항 없음
- **촛불 0개**

예약이 있어도 조건 하나라도 어긋나면 입실 버튼을 잠그고 이유를 표시한다.

## 운영 중지 불변식

```text
reservation_assignment = none
occupancy = vacant
cleaning_suppressed = true
active_cleaning_task = none
active_cleaning_assignment = none
claim_open = false
assignment_enabled = false
guest_allocation = unavailable
```

예약·투숙이 있으면 운영 중지 확정을 거절하고 먼저 이동·해제·퇴실을 요구한다.

### 608호 기준

```text
운영: out_of_service
투숙: 공실
예약: 없음
청소: 작업 없음·청소 제외
담당: 없음
메이드 선택: 닫힘
촛불: 3개
고객 배정: 불가
```

정상 운영 재개 시 `운영 재개 점검 청소`를 미배정·선택 클로즈로 생성한다. 청소·검수 승인과 촛불 전량 회수, 차단 이슈 해결까지 모두 끝나야 가용 여부를 다시 계산한다.

## 촛불 생명주기

1. 메이드 또는 관리자가 냄새 제거를 위해 촛불을 둔다.
2. 메이드는 청소 작업에서 **이번 작업의 추가 개수**를 기록한다.
3. 기존 수량이 양수라면 메이드 화면의 감소 버튼은 기존 수량 아래로 내려가지 않는다.
4. 촛불 수량이 1개 이상이 되는 즉시 고객 배정과 입실을 차단한다.
5. 관리자가 현장에서 실제 수량과 위치를 확인한다.
6. 관리자가 회수 사유·전후 수량을 검토하고 최종 확인 모달에서 확정한다.
7. `0개`가 되면 촛불 차단만 해제하고, 운영·청소·예약·이슈 조건을 다시 계산한다.
8. 검수 승인은 촛불을 자동으로 0개로 만들지 않는다.

메이드 제출과 관리자 회수가 동시에 일어날 수 있으므로 실제 서버에서는 객실 촛불 버전 또는 객실 버전을 비교해 오래된 제출이 회수 완료를 되살리지 못하게 한다.

## 청소 담당 배정

- 실제 청소 작업이 있고 배정 가능한 단계에서만 담당 지정 가능.
- 메이드가 선택하면 다른 메이드에게 즉시 닫히지만 관리자에게는 변경 가능.
- 관리자는 다른 메이드 또는 `미배정`으로 돌릴 수 있다.
- 청소 중 변경 시 기존 사진·체크·시작 시각은 중단 작업 이력으로 보존한다.
- 새 담당자는 이전 제출물을 자기 작업으로 이어받지 않는다.
- 검수 대기·승인 작업은 일반 담당 변경 금지. 반려 후 재청소 담당을 별도로 지정한다.

## 일감 선택 원자성

```text
assignee_id IS NULL
claim_open = true
assignment_enabled = true
room.operation_status = active
task.status is claimable
maid.status = active
```

최초 요청만 성공하고 나머지는 409 응답을 받는다.

## 검수와 고객 가용성

```text
메이드 제출 → 사진 업로드 완료 → 검수 대기
승인 → 청소 품질 승인 + 주급 확정
가용성 → 승인 이후에도 운영·촛불·차단 이슈·예약·투숙을 다시 계산
반려 → 재청소 필요 + 메이드 미확인 알림 + 제출 버전 보존
```

## 시간·이력·정산

- 기본 체크인 16:00, 체크아웃 11:00.
- 얼리·레이트는 실제 시각을 저장하고 변경 이력을 남긴다.
- 과거 날짜 원본은 읽기 전용이며 정정 이벤트만 추가한다.
- 청소비는 작업 생성 시 스냅샷으로 저장한다.
- 검수 승인 시 주급 확정 항목을 한 번만 생성한다.
- 주급 지급 상태는 되돌릴 수 있으나 사유와 감사 로그가 필수다.
- 벌점은 소프트 삭제·복구하며 임금과 자동 연동하지 않는다.
'''

DOCS['04_WORKFLOWS_AND_FLOWCHARTS.md'] = r'''# 4. 주요 업무 흐름과 플로우차트

렌더링된 PNG·SVG와 Graphviz 원본은 `FLOWCHARTS/`에 있다.

## 4.1 객실 운영·고객 배정

```mermaid
flowchart TD
  A[날짜 선택] --> B[객실 운영 현황]
  B --> C{운영 중지?}
  C -- 예 --> D[배정·입실·청소 차단]
  C -- 아니오 --> E{예약 있음 + 하드 차단?}
  E -- 예 --> F[예약 충돌]
  F --> G[원인 해결 / 다른 객실 이동 / 배정 해제]
  E -- 아니오 --> H{투숙 중?}
  H -- 예 --> I[신규 배정 불가]
  H -- 아니오 --> J{예약 배정됨?}
  J -- 예 --> K{입실 조건 충족?}
  K -- 아니오 --> L[입실 잠금·사유 표시]
  K -- 예 --> M[입실 확인 모달]
  J -- 아니오 --> N{청소 승인 + 이슈 없음 + 촛불 0개?}
  N -- 예 --> O[고객 배정 가능]
  N -- 아니오 --> P[배정 불가 사유 표시]
```

## 4.2 608호 운영 중지·재개

```mermaid
flowchart TD
  A[운영 중지 요청] --> B{예약·투숙 있음?}
  B -- 예 --> C[확정 차단]
  C --> D[예약 이동·해제 또는 퇴실]
  D --> A
  B -- 아니오 --> E[사유·영향 확인]
  E --> F[최종 확인]
  F --> G[예약 없음·작업 없음·담당 없음·공개 닫힘]
  G --> H[운영 중지]
  H --> I[운영 재개 요청]
  I --> J[점검 청소 생성]
  J --> K[청소·검수]
  K --> L{촛불 0개·이슈 없음?}
  L -- 아니오 --> M[계속 배정 불가]
  L -- 예 --> N[가용성 재계산]
```

## 4.3 청소 일감·담당

```mermaid
flowchart TD
  A[청소 작업 생성] --> B{배정 가능?}
  B -- 아니오 --> C[불가 사유]
  B -- 예 --> D{관리자 직접 배정?}
  D -- 예 --> E[메이드 선택·사유·확인]
  D -- 아니오 --> F[메이드 선택 오픈]
  F --> G[메이드가 금액·시간 확인]
  G --> H[선택 후 직접 취소 불가 확인]
  H --> I[원자적 claim]
  I -- 성공 --> J[담당 확정·자동 클로즈]
  I -- 실패 --> K[이미 선택됨]
  J --> L{관리자 변경?}
  L -- 교체 --> M[변경 사유·중단 이력]
  L -- 미배정 --> N[회수 후 오픈/클로즈]
```

## 4.4 청소·사진·검수

```mermaid
flowchart TD
  A[담당 객실] --> B[청소 시작 확인]
  B --> C[체크리스트·사진·메모]
  C --> D[메이드 촛불 추가 수량 기록]
  D --> E[완료 제출 확인]
  E --> F[검수 대기]
  F --> G[관리자 사진별 확인]
  G --> H{승인/반려}
  H -- 승인 --> I[청소 승인·주급 확정]
  I --> J{촛불 0개·이슈 없음·정상 운영?}
  J -- 예 --> K[입실 준비 가능]
  J -- 아니오 --> L[별도 차단 유지]
  H -- 반려 --> M[사진·사유·최종 확인]
  M --> N[재청소·메이드 알림]
```

## 4.5 촛불 배치·회수

```mermaid
flowchart TD
  A[현재 촛불 0개 이상] --> B{메이드 청소 중?}
  B -- 예 --> C[기존 수량 이하 감소 금지]
  C --> D[이번 작업 추가 개수 기록]
  B -- 아니오 --> E[관리자 수량·위치 입력]
  D --> F[최종 수량 1개 이상]
  E --> F
  F --> G[고객 배정·입실 즉시 차단]
  G --> H[관리자 현장 회수]
  H --> I[전후 수량·사유 확인]
  I --> J{0개로 확정?}
  J -- 아니오 --> G
  J -- 예 --> K[촛불 차단 해제]
  K --> L[다른 가용 조건 재계산]
```

## 4.6 주급·벌점

```mermaid
flowchart TD
  A[검수 승인] --> B[주급 확정 항목]
  B --> C[주차 합산]
  C --> D[지급 완료 확인]
  D --> E{기록 오류?}
  E -- 예 --> F[사유 입력·미지급 복구]
  E -- 아니오 --> G[지급 유지]
  H[품질 문제 확인] --> I[벌점 사유·근거]
  I --> J[최종 확인]
  J --> K[메이드 알림]
  K --> L{삭제/복구?}
  L --> M[사유와 소프트 상태 변경]
```

## 4.7 일자별 이력·정정

```mermaid
flowchart TD
  A[월 달력에서 날짜 선택] --> B[일자별 읽기 모델 조회]
  B --> C{오늘?}
  C -- 예 --> D[실시간 명령 가능]
  C -- 아니오 --> E[읽기 전용]
  E --> F{오기입 발견?}
  F -- 예 --> G[정정 내용·사유]
  G --> H[최종 확인]
  H --> I[원본 유지·정정 이벤트 추가]
```
'''

DOCS['05_CONFIRMATION_AND_SAFETY_MATRIX.md'] = r'''# 5. 확인 모달과 안전장치 매트릭스

확인 모달은 사용자 실수를 줄이는 UX일 뿐 최종 보안 장치가 아니다. 확정 요청을 받은 서버는 권한, 최신 버전, 상태 전이 가능 여부를 다시 검사한다.

| 중요 변경 | UI 안전장치 | 필수 입력·표시 | 서버 검증 |
|---|---|---|---|
| 운영 중지·재개 | 영향 검토→최종 확인 | 사유, 예약·청소 영향 | 예약·투숙·작업·버전 |
| 고객 객실 배정 | 후보·전후 확인 | 예약 ID, 시각 | 가용성·촛불 0·중복 배정 |
| 예약 이동·해제 | 후보 선택→최종 확인 | 대상 객실·사유 | 출발 예약·대상 가용 |
| 입실·퇴실 | 최종 확인 | 객실·예약·시각 | 운영·청소·이슈·촛불 |
| 촛불 배치·수량 변경 | 전후 수량·영향 확인 | 위치, 사유 | 권한·버전·0 이상 |
| 촛불 전량 회수 | 별도 녹색 확정 | 전후 수량, 현장 확인 사유 | 관리자 권한·최신 수량 |
| 비밀번호 변경 | 전후 확인 | 4자리 | 암호화·권한·조회 로그 |
| 얼리·레이트 변경 | 전후 시각 확인 | 정확한 시각 | 예약 시간 유효성 |
| 차단 특이사항 등록·해결 | 영향 확인 | 구체 사유 | 예약 충돌·해결 권한 |
| 청소 담당 배정·변경 | 전후 담당 확인 | 변경 사유 | 작업 단계·활성 메이드 |
| 담당 미배정 회수 | 결과 확인 | 사유, 공개 상태 | 기존 작업 보존 |
| 일감 오픈·클로즈 | 단일·일괄 확인 | 대상 수 | 미배정·공개 가능 여부 |
| 메이드 일감 선택 | 취소 제한 확인 | 금액·시간·유형 | 원자적 claim |
| 청소 시작 | 시작 확인 | 가능 시각 | 담당자·운영 상태 |
| 청소 완료 제출 | 제출 취소 제한 확인 | 체크·사진·촛불 추가분 | 필수 업로드·촛불 하한 |
| 검수 승인 | 전 사진 확인→확정 | 주급·촛불·이슈 영향 | 제출 버전·중복 승인 |
| 검수 반려 | 사진·사유→최종 확인 | 재청소 지시 | 작업 버전·알림 outbox |
| 주급 지급·취소 | 양방향 확인 | 취소 사유 필수 | 정산 잠금·중복 처리 |
| 벌점 부여 | 근거 입력→확정 | 사유·증빙·점수 | 권한·정책 범위 |
| 벌점 삭제·복구 | 양방향 확인 | 사유 | 소프트 상태·로그 |
| 메이드 계정·퇴사·복구 | 미리보기→확정 | 계정·퇴사 사유 | ID 유일·진행 작업 회수 |
| 과거 정정 | 전후 내용 확인 | 정정 내용·사유 | 원본 불변·추가 이벤트 |

## 되돌리기 원칙

- 메이드가 선택한 일감은 메이드가 직접 취소하지 못하지만 관리자는 다른 담당 또는 미배정으로 되돌릴 수 있다.
- 지급 완료는 사유를 입력해 미지급으로 되돌릴 수 있다.
- 벌점은 삭제·복구가 가능하지만 원본 이력은 남는다.
- 메이드 퇴사는 소프트 삭제하고 비활성 상태로 복구한다.
- 과거 원본은 되돌리는 UPDATE가 아니라 정정 이벤트를 추가한다.

## 즉시 반영 가능한 저위험 조작

- 검색·필터·날짜 탐색
- 사진 썸네일 선택·확대
- 청소 중 임시 체크리스트
- 메이드가 새로 둔 촛불의 **임시 추가 수량** 조정

기존 촛불 수량 감소와 최종 회수는 저위험 조작이 아니며 관리자 확인 명령이다.

## 모달 문구 원칙

- 대상과 현재 값
- 변경 후 값
- 예약·입실·청소·주급에 미치는 영향
- 직접 되돌릴 수 있는지와 방법
- 사유
- 구체적 확정 동사: `전량 회수 확정`, `미배정으로 확정`, `미지급으로 복구`

모달이 열린 동안 토스트가 핵심 내용을 가리지 않도록 배치한다. 버튼 연타·네트워크 재시도는 idempotency key로 중복 실행을 막는다.
'''

DOCS['06_DATA_MODEL.md'] = r'''# 6. 권장 데이터 모델

관계형 DB와 이벤트·읽기 모델 조합을 권장한다. 표시 이름이나 색상 대신 불변 ID와 원본 상태를 저장한다.

## 사용자·권한

### `users`

- `id` UUID PK
- `login_id` unique
- `display_name`
- `role` (`admin`, `maid`)
- `employment_status` (`active`, `inactive`, `retired`)
- `login_enabled`
- `created_at`, `updated_at`, `retired_at`

### `admin_permissions`

- 객실 운영, 고객 배정, 검수, 촛불 회수, 정산, 벌점, 계정, 비밀번호 이력 권한

### `maid_profiles`

- 전화번호, 입사일, 메모
- 과거 작업과 연결되는 불변 `user_id`

## 객실·운영

### `rooms`

- `id`, `room_number`, `room_type_id`
- `operation_status`
- `operation_reason`
- `current_candle_count` 캐시 컬럼
- `version` optimistic lock

### `room_operation_events`

- 전후 상태, 사유, actor, 시각

### `room_issues`

- 카테고리, 설명, 심각도
- `blocks_guest_assignment`
- 상태, 등록·해결자와 시각

### `room_candle_events`

- `id`, `room_id`
- `action` (`maid_added`, `admin_set`, `admin_adjusted`, `admin_recovered`)
- `count_before`, `count_after`
- `added_count`
- `location_note`
- `reason`
- `source` (`cleaning_task`, `admin_room_check`)
- `cleaning_task_id` nullable
- `actor_id`
- `physically_verified` boolean
- `created_at`
- `room_version_before`, `room_version_after`

제약:

- `count_after >= 0`
- 메이드 명령은 `count_after >= count_before`
- 양수에서 감소 또는 0으로의 전이는 촛불 회수 권한이 있는 관리자만 가능
- `current_candle_count > 0`이면 고객 배정·입실 읽기 모델은 차단

### `room_access_codes`, `access_code_view_logs`

- 암호화 코드, 유효 기간, 생성·폐기자
- 조회자, 작업 ID, 시각

## 예약·투숙

### `reservations`

- 외부 채널·예약 ID
- 기본 체크인 16:00, 체크아웃 11:00
- 실제 체크인·체크아웃
- 얼리·레이트 시각
- 상태

### `reservation_room_assignments`

- 예약, 객실, 상태
- 배정·이동·해제·체크인·체크아웃 이력
- 한 예약에 활성 객실 배정 최대 1개

## 청소·검수

### `cleaning_tasks`

- 객실, 서비스 일자, 유형
- 상태
- 가능·마감 시각
- 가격 스냅샷
- 공개·배정 가능 여부
- `version`

### `cleaning_task_assignments`

- 작업, 메이드, 출처(`admin`, `maid_claim`)
- 활성·종료·중단
- 전후 담당과 사유
- 작업당 활성 담당 최대 1명

### `cleaning_submissions`

- 제출 버전
- 체크리스트 스냅샷
- 메모
- `candle_count_before`
- `maid_added_candle_count`
- `candle_count_after`
- 제출자·시각

서버는 `candle_count_after >= candle_count_before`를 검증한다. 관리자가 청소 도중 회수해 객실 버전이 바뀌었으면 제출을 재검토하게 한다.

### `cleaning_photos`

- 카테고리, 원본·썸네일 URL
- 촬영·업로드 시각
- 업로드 상태
- 제출 버전

### `inspections`, `inspection_photo_reviews`

- 승인·반려
- 검사자, 사유, 사진별 결과
- 검수 승인은 촛불 상태를 바꾸지 않는다.

## 주급·벌점

- `weekly_pay_periods`
- `weekly_pay_items`
- `weekly_payment_events` (`marked_paid`, `reverted_unpaid`)
- `penalties` (`active`, `void`)와 부여·삭제·복구 사유

## 이력·알림·읽기 모델

### `audit_events`

- aggregate, event type
- before/after JSON
- actor, reason
- request ID, idempotency key, 시각

### `room_daily_snapshots` 또는 `room_operation_read_models`

특정 날짜의 객실 운영판을 빠르게 조회하는 재생성 가능한 읽기 모델이다. 원본 진실은 예약·작업·이벤트 테이블이다.

### `notifications`, `notification_outbox`

- 수신자, 유형, payload, 읽음, 푸시 상태, 재시도

## 핵심 DB 제약

- 운영 중지 객실에 활성 예약 배정·활성 청소 작업 금지
- 촛불 양수 객실에 신규 예약 객실 배정·체크인 명령 금지
- 한 작업에 활성 담당 최대 1명
- 한 예약에 활성 객실 배정 최대 1개
- 검수 승인·주급 항목은 동일 제출 버전에 한 번만
- 메이드 퇴사는 물리 삭제 금지
- 과거 정정은 원본 UPDATE 금지
'''

DOCS['07_API_AND_TRANSACTION_DESIGN.md'] = r'''# 7. API와 트랜잭션 설계

## 조회 API 예시

```text
GET /api/room-operations?date=2026-08-14&view=guest-unavailable
GET /api/rooms/{roomId}?date=2026-08-14
GET /api/rooms?candleState=present
GET /api/cleaning-tasks/market?date=2026-08-14
GET /api/maids/me/tasks?date=2026-08-14
GET /api/inspections?status=pending
GET /api/weekly-pay?week=2026-W33
GET /api/audit-events?roomId=608&date=2026-08-14
```

## 명령 API 예시

```text
POST /api/rooms/{id}/commands/stop-operation
POST /api/rooms/{id}/commands/resume-operation
POST /api/rooms/{id}/commands/set-candles
POST /api/rooms/{id}/commands/confirm-candle-recovery
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

중요 명령 공통 필드:

```json
{
  "expectedVersion": 42,
  "reason": "관리자 입력 사유",
  "idempotencyKey": "uuid",
  "clientConfirmedAt": "2026-08-14T18:00:00+09:00"
}
```

## 고객 배정·입실 트랜잭션

1. 객실·예약 행 잠금 또는 expectedVersion 검증.
2. 운영 정상, 공실, 촛불 0, 차단 이슈 없음, 청소 승인 확인.
3. 활성 객실 배정 중복 확인.
4. 조건 불충족 시 409와 구체 코드 반환.
5. 배정·입실 이벤트와 감사 로그·알림 outbox를 같은 트랜잭션에 저장.

권장 오류 코드:

- `ROOM_OUT_OF_SERVICE`
- `ROOM_HAS_CANDLES`
- `ROOM_BLOCKING_ISSUE_OPEN`
- `ROOM_CLEANING_NOT_APPROVED`
- `ROOM_ALREADY_OCCUPIED`
- `RESERVATION_ROOM_CONFLICT`

## 촛불 수량 변경 트랜잭션

### 메이드 작업 제출

1. 청소 작업과 객실을 잠근다.
2. 현재 객실 촛불 수량을 `floor`로 읽는다.
3. `submitted_count >= floor`인지 검사한다.
4. 추가 수량과 작업 제출을 저장한다.
5. 수량이 양수면 고객 배정·입실 읽기 모델을 차단한다.
6. 감사 이벤트·관리자 알림을 저장한다.

메이드가 변조 요청으로 수량을 낮추면 422 `MAID_CANNOT_REDUCE_EXISTING_CANDLES`.

### 관리자 회수 확정

1. 객실 잠금·버전 확인.
2. 관리자 `can_manage_candles` 권한 확인.
3. 현재 수량, 변경 후 수량, 위치, 현장 확인 사유를 저장.
4. 감소 또는 0 전이는 `physically_verified=true` 필수.
5. 0이 되면 촛불 차단만 해제하고 전체 가용 조건을 재계산.
6. 기존 예약이 있다면 입실 잠금 해제 가능 여부를 다시 계산.

## 메이드 일감 claim

```sql
UPDATE cleaning_tasks
SET status = 'assigned', assignee_id = :maid_id, claim_open = false, version = version + 1
WHERE id = :task_id
  AND assignee_id IS NULL
  AND claim_open = true
  AND assignment_enabled = true
  AND status IN ('waiting','claimable')
  AND version = :expected_version
RETURNING *;
```

0행이면 이미 선택됐거나 상태가 바뀐 것이다.

## 운영 중지

- 예약·투숙이 있으면 409.
- 활성 담당이 있으면 중단 이력.
- 청소 작업 취소·제외.
- 공개 닫힘·배정 불가.
- 감사 이벤트와 outbox.

## 검수 승인

- 최신 제출 버전과 모든 필수 사진 업로드 확인.
- 승인과 주급 항목을 한 번만 생성.
- 객실 청소 상태는 준비 완료로 바꾸되 촛불·이슈·운영 상태는 변경하지 않는다.
- 전체 고객 가용성을 다시 계산한다.

## 사진·알림·보안

- 사전 서명 URL, 업로드 완료 검증, 썸네일, 오프라인 큐.
- 상태 변경과 알림 outbox를 같은 DB 트랜잭션에 저장.
- 접근 코드 평문 로그 금지, 조회 로그 필수.
- 메이드 API는 본인 담당만 반환.
- 사진 URL은 짧은 만료의 서명 URL.
- 모든 명령은 RBAC와 idempotency를 서버에서 검증.
'''

DOCS['08_ACCEPTANCE_CRITERIA.md'] = r'''# 8. 수용 기준

## 객실 운영·고객 배정

1. 608호 운영 중지 시 예약·투숙·청소 작업·담당·일감 공개가 없어야 한다.
2. 활성 예약·투숙이 있는 객실은 운영 중지 확정 전에 이동·해제·퇴실을 요구해야 한다.
3. 운영 재개 시 `운영 재개 점검 청소`를 미배정·클로즈로 만들고 즉시 판매 가능으로 만들지 않는다.
4. 고객 배정 가능은 정상 운영·공실·예약 미배정·청소 승인·이슈 없음·촛불 0을 모두 충족해야 한다.
5. 예약이 배정됐어도 입실 조건이 하나라도 미충족이면 입실 버튼이 잠겨야 한다.
6. 배정 불가 화면에는 구체 사유가 텍스트로 보여야 한다.
7. 촛불 객실은 촛불 전용 목록과 배정 불가 목록에 중복 표시될 수 있어야 한다.

## 촛불

8. 촛불 수량이 1개 이상이면 신규 고객 배정과 체크인이 모두 거절되어야 한다.
9. 기존 예약이 있는 객실에 촛불이 생기면 예약 충돌로 표시되어야 한다.
10. 관리자가 수량·위치·사유를 검토하고 최종 확정해야 촛불 상태가 변경되어야 한다.
11. 관리자 전량 회수로 0개가 되면 촛불 차단만 해제하고 다른 조건을 재계산해야 한다.
12. 검수 승인은 촛불 수량을 자동으로 0개로 만들면 안 된다.
13. 메이드는 기존 양수 수량 아래로 촛불 수량을 낮출 수 없어야 한다.
14. 메이드 제출 payload를 조작해도 서버가 기존 수량보다 낮은 값은 거절해야 한다.
15. 메이드가 추가한 수량과 기존 수량이 감사 이벤트에 분리되어야 한다.
16. 관리자 회수와 메이드 제출이 충돌하면 버전 검증으로 오래된 요청을 거절해야 한다.

## 청소 배정·메이드

17. 메이드는 선택 전 금액·유형·시각·직접 취소 불가 안내를 확인해야 한다.
18. 동시에 두 메이드가 선택하면 한 명만 성공해야 한다.
19. 관리자는 담당자를 다른 메이드 또는 미배정으로 바꿀 수 있어야 한다.
20. 미배정 회수 시 메이드 선택 오픈·클로즈를 정할 수 있어야 한다.
21. 청소 중 담당 변경 시 기존 체크·사진·시각이 중단 이력으로 남아야 한다.
22. 운영 중지·작업 없음·검수 완료 객실은 새 담당 배정 대상에 노출되면 안 된다.
23. 레이트 체크아웃 전에는 비밀번호·청소 시작이 잠기고 정확한 가능 시각이 보여야 한다.

## 검수·사진

24. 필수 사진 업로드가 끝나지 않으면 검수 요청할 수 없다.
25. 관리자가 모든 사진을 확인하기 전 승인할 수 없다.
26. 반려 시 사진·사유·상세 지시가 메이드에게 전달되어야 한다.
27. 메이드 화면에 미확인 반려 알림과 재청소 카드가 보여야 한다.
28. 검수 반려만으로 벌점이 자동 생성되면 안 된다.
29. 검수 승인 후에도 촛불·이슈·운영 중지 조건이 있으면 고객 배정 불가여야 한다.

## 주급·벌점·계정

30. 검수 승인 금액은 해당 주의 확정 주급에 한 번만 반영되어야 한다.
31. 지급 완료를 미지급으로 되돌릴 때 사유가 필수여야 한다.
32. 벌점 부여에는 사유·근거·점수가 필수여야 한다.
33. 벌점 삭제 후 활성 점수에서는 빠지지만 이력은 남아야 한다.
34. 삭제한 벌점 복구 시 사유와 메이드 알림이 남아야 한다.
35. 벌점은 주급에서 자동 차감되지 않아야 한다.
36. 퇴사 처리된 메이드는 로그인·신규 선택이 불가능해야 한다.
37. 퇴사 후에도 과거 작업·사진·주급·벌점이 조회되어야 한다.

## 시간·이력·품질

38. 기본 체크인 16:00, 체크아웃 11:00이 적용되어야 한다.
39. 얼리·레이트 실제 시각이 모든 관련 화면과 이력에 표시되어야 한다.
40. 달력으로 날짜를 선택하고 해당 날짜의 객실 상태를 조회할 수 있어야 한다.
41. 과거 원본은 수정할 수 없고 정정 이벤트만 추가할 수 있어야 한다.
42. 중요한 변경은 actor, time, reason, before, after를 남겨야 한다.
43. 360px·390px·430px에서 가로 스크롤이 없어야 한다.
44. 색상만으로 상태를 전달하지 않아야 한다.
45. 버튼 연타·재시도에도 명령이 중복 실행되지 않아야 한다.
46. 권한 없는 직접 API 호출은 서버에서 거절되어야 한다.
47. 오프라인 사진은 유실 없이 재전송되어야 한다.
'''

DOCS['09_CRITIQUE_AND_IMPROVEMENTS.md'] = r'''# 9. 현재 시안의 비판점과 개선 우선순위

## 강점

- 청소 앱이 아니라 객실 운영 앱으로 정보 구조를 정리했다.
- 고객 객실 배정과 청소 담당 배정을 분리했다.
- 운영 중지, 예약 충돌, 촛불 하드 차단을 명시했다.
- 메이드 선택 후 관리자 변경·미배정 회수 경로가 있다.
- 사진 검수, 주급, 벌점, 소프트 삭제, 날짜 이력이 연결돼 있다.
- 중요한 변경에 전후 영향·최종 확인·되돌리기 경로가 있다.
- 모바일과 주요 상호작용을 자동 검증했다.

## 구조적 한계

1. **단일 HTML 모놀리스** — UI·샘플 데이터·도메인 규칙이 한 파일에 있다.
2. **메모리 상태** — 새로고침·다중 기기·동시성이 없다.
3. **샘플 이름 연결** — 실제 구현은 UUID foreign key가 필요하다.
4. **예약·투숙 표현 혼재** — 별도 상태 머신과 이벤트가 필요하다.
5. **날짜별 배열 복제** — 읽기 모델로는 가능하지만 진실 원본으로 쓰면 안 된다.
6. **실제 사진·알림·보안 미구현** — 샘플 그래픽과 토스트뿐이다.
7. **도어락 미연동** — 랜덤 숫자 생성과 실제 잠금 코드 변경은 다르다.
8. **주급·벌점 운영 규정 미확정** — 마감, 지급일, 부분 작업비, 점수 기준이 필요하다.
9. **관리자 권한 한 종류** — 운영·검수·정산·계정·민감정보를 분리해야 한다.
10. **오프라인·오류 복구 부족** — 현장 네트워크를 고려한 큐가 필요하다.

## 촛불 로직의 특별한 위험

촛불 수량은 앱 값만 바꿔서는 안전이 보장되지 않는 **물리적 현장 사실**이다.

- 관리자가 실제 회수하지 않고 0개를 눌렀을 가능성
- 위치 정보 누락
- 청소 도중 관리자 회수와 메이드 제출의 경쟁 조건
- 촛불을 둔 뒤 앱 기록을 잊은 경우
- 회수했지만 앱 갱신을 잊은 경우

개선 권장:

- 회수 권한을 제한하고 사유·현장 확인 체크를 필수화
- 선택적으로 회수 확인 사진을 관리자에게만 요구
- 오래 남은 촛불 경고와 알림
- 객실 문 앞 QR/NFC로 현장 객실을 다시 확인한 뒤 회수 확정
- 메이드 제출과 관리자 회수에 객실 버전 사용
- 일일 마감 시 `촛불 > 0 + 오늘/내일 입실 예약` 고위험 목록 자동 생성

## 데모 데이터의 예약 충돌

v13 기본 데이터에는 1502·1004·108호처럼 촛불 또는 차단 이슈가 있는데 예약이 붙은 샘플이 있다. 이는 정상 운영 데이터를 뜻하는 것이 아니라 **충돌 감지와 해결 UI를 보여주기 위한 의도적 시나리오**다. 실제 초기 데이터 마이그레이션에서는 이러한 모순을 탐지해 관리자 해결 큐에 올려야 한다.

## P0 — 실사용 전 필수

- PostgreSQL 스키마와 DB 제약
- 인증·세부 RBAC
- 서버 상태 전이와 optimistic lock
- 원자적 일감 claim
- 고객 배정·입실과 촛불 하드 차단 트랜잭션
- 운영 중지·예약 이동·검수·주급 idempotency
- 감사 로그·알림 outbox
- 사진 저장·썸네일·오프라인 재시도
- 접근 코드 암호화·조회 로그
- 실제 객실·청소비·주급·벌점 정책 확정

## P1 — 운영 안정화

- CSV 예약 가져오기와 중복·충돌 검사
- PMS/OTA 어댑터
- 촛불 장기 방치·입실 임박 경고
- 주급 잠금·엑셀·지급 배치
- 객실 이슈 담당·기한·완료 사진
- 관리자 역할 세분화
- API·DB·E2E 테스트

## P2 — 최적화

- 동선·마감 기반 청소 추천
- 예상 청소시간 학습
- 사진 흐림·누락 보조 감지
- 반복 이슈·검수 반려·촛불 사용 통계
- 다지점 지원

## 아직 결정할 운영 질문

- 정확한 주급 마감일과 지급일
- 담당 변경 전 기존 메이드의 부분 작업비
- 객실 유형별 청소비·추가 수당
- 전 객실 검수인지 표본 검수인지
- 벌점 점수표·초기화·이의 처리
- 촛불 회수 확인 사진을 의무화할지
- 촛불 위치를 자유 메모로 둘지 구조화할지
- 관리자 중 누가 회수 권한을 가질지
- 예약 원본 시스템과 동기화 책임
'''

DOCS['10_CODEX_IMPLEMENTATION_GUIDE.md'] = r'''# 10. Codex 구현 가이드

## 권장 구조

- Frontend: React + TypeScript + Vite, 모바일 PWA
- Server state: TanStack Query
- Forms: React Hook Form + schema validation
- Backend: TypeScript 서버 프레임워크
- DB: PostgreSQL
- 사진: S3 호환 object storage
- Push: Web Push/FCM 계열
- Tests: unit + DB integration + API + Playwright E2E

## 프런트엔드 모듈

```text
src/
  app/ auth/
  rooms/
    operations/ guest-allocation/ reservation-conflicts/
    issues/ candles/ access-codes/ schedules/
  cleaning/
    market/ assignments/ task-detail/ photos/ inspections/
  workforce/
    maids/ weekly-pay/ penalties/
  history/ notifications/ shared/
```

## 도메인 서비스

```text
RoomOperationService
RoomAvailabilityPolicy
ReservationAssignmentService
RoomCandleService
CleaningTaskService
CleaningAssignmentService
InspectionService
WeeklyPayService
PenaltyService
AuditService
NotificationService
```

React 컴포넌트에서 여러 필드를 직접 바꾸지 말고 도메인 명령을 호출한다.

## 구현 단계

### 0. 규칙·데이터 확정

- 상태 enum과 상태 전이 표
- 객실·청소비·체크리스트
- 촛불 회수 권한·증빙 정책
- 주급·벌점 운영 규정

### 1. 인증·읽기 전용 객실 운영판

- DB·마이그레이션
- RBAC
- 일자별 읽기 모델
- 네 운영 목록·필터
- 608 불변식과 촛불 하드 차단 테스트

### 2. 객실 운영·예약·촛불

- 운영 중지·재개
- 예약 배정·이동·해제·입실·퇴실
- 차단 특이사항
- 얼리·레이트
- 촛불 배치·관리자 회수·예약 충돌
- 접근 코드

### 3. 청소 배정

- 작업 생성
- 오픈·클로즈
- 원자적 claim
- 관리자 배정·변경·미배정
- 중단 이력

### 4. 메이드 현장 PWA

- 담당 작업과 비밀번호 권한
- 체크리스트·오프라인 사진 큐
- 촛불 추가 수량만 기록, 기존 수량 하한 검증
- 완료 제출

### 5. 검수·알림

- 사진별 검수
- 승인·반려
- 재청소 알림
- 승인 후 전체 가용성 재계산

### 6. 주급·벌점·계정

- 주차별 정산·지급·취소
- 벌점 소프트 삭제·복구
- 메이드 소프트 삭제

### 7. 외부 연동

- CSV
- PMS/OTA
- 도어락

## 첫 구현 순서

1. 문서의 상태 규칙을 TypeScript 순수 함수로 옮긴다.
2. `08_ACCEPTANCE_CRITERIA.md`를 테스트로 먼저 만든다.
3. PostgreSQL 제약과 트랜잭션 테스트를 작성한다.
4. 608, 촛불 배치·회수, 예약 충돌, 일감 claim, 검수 승인부터 구현한다.
5. 프로토타입의 390px UI를 기준으로 화면을 재구성한다.
6. 360/390/430px와 키보드·스크린리더를 검수한다.

## 금지할 구현

- 색상이나 단일 `room_status`를 진실 원본으로 저장
- UI에서만 버튼을 숨기고 API는 허용
- 촛불 양수 객실을 서버에서 배정·입실 허용
- 메이드가 기존 촛불 수량을 낮추는 요청 허용
- 검수 승인 시 촛불을 자동 회수 처리
- 운영 중지 객실에 예약·청소를 만들고 화면에서만 숨김
- 표시 이름을 foreign key로 사용
- 과거 이력을 UPDATE로 덮어쓰기
- 벌점 자동 임금 차감
- 업로드 완료 전 검수 요청
'''

DOCS['11_USAGE_GUIDE.md'] = r'''# 11. 현재 HTML 사용법

## 실행

```bash
python -m http.server 8000 --directory CURRENT
```

`http://localhost:8000/index.html`을 연다. PC에서는 왼쪽에 빠른 탐색, 오른쪽에 모바일 프레임이 보인다. 모바일에서는 화면 전체를 앱처럼 사용한다.

## 관리자 확인 순서

1. `객실`에서 날짜와 네 운영 목록을 확인한다.
2. `배정 불가`를 누르면 운영 중지, 청소·검수, 투숙, 촛불, 이슈, 예약 이유별 그룹이 나온다.
3. 608호를 열어 `운영 중지·예약 없음·청소 없음·담당 없음·촛불 3개`를 확인한다.
4. 운영 재개를 시도해 점검 청소 생성 확인 모달을 본다.
5. 촛불 0개인 412호에서 `촛불 기록`으로 1개를 입력하면 최종 확인 뒤 배정 불가가 된다.
6. 같은 화면에서 관리자가 0개·회수 사유를 입력하면 촛불 차단이 해제된다.
7. 1502호에서 고객 배정 화면을 열면 예약+촛불 충돌과 회수·이동·해제 경로가 보인다.
8. `청소 배정`에서 담당 변경 또는 미배정 회수를 확인한다.
9. `검수`에서 사진 확인·승인·반려를 확인한다. 승인해도 촛불은 별도 차단으로 남는다.
10. `주급`에서 지급 완료를 미지급으로 되돌린다.
11. `더보기`에서 메이드 소프트 삭제와 벌점 부여·삭제·복구를 확인한다.

## 메이드 확인 순서

1. 역할을 메이드로 전환한다.
2. `일감 찾기`에서 금액·시간을 확인하고 선택한다.
3. 직접 취소할 수 없다는 최종 확인을 본다.
4. `내 업무`에서 청소를 시작한다.
5. 체크리스트·사진·메모를 입력한다.
6. 촛불이 이미 1개 기록된 객실에서는 감소 버튼이 잠겨 있다. 새로 둔 수량만 추가한다.
7. 완료 제출 모달에서 기존 수량, 이번 작업 추가분, 총 수량과 배정 차단 영향을 확인한다.
8. 반려된 객실의 빨간 알림·사진·사유를 확인한다.
9. 본인 주급과 벌점을 확인한다.

## 날짜 이력

- 날짜 영역을 누르면 월 달력이 열린다.
- 과거 날짜는 읽기 전용이다.
- 오기입은 `기록 정정`에서 내용·사유·최종 확인을 거쳐 별도 이벤트로 남긴다.

## 프로토타입 제한

- 새로고침 시 상태 초기화
- 사진은 샘플 그래픽
- 푸시는 토스트로 표현
- DB·동시성·실제 송금·도어락·OTA 미연동
- 데모 예약 충돌은 안전 흐름을 보여주기 위한 의도적 데이터
'''

DOCS['12_CHANGELOG.md'] = r'''# 12. 프로토타입 변경 이력

| 버전 | 주요 변화 |
|---|---|
| v2 | 관리자·메이드 역할별 모바일 기본 구조, 객실·청소·비밀번호 초기 흐름 |
| v3 | 전체 객실표, 메이드 일감 선택, 메이드 관리, 주급, 촛불 수량 |
| v4 | 인증사진 상세 검수, 확대·재청소, 메이드 소프트 삭제 |
| v5 | 담당 변경·미배정 회수, 배정 가능·확정·불가, 중단 이력 |
| v6–v7 | 고객 객실 배정과 청소 담당 배정 분리, 유형·상태 필터 |
| v8 | 네 운영 목록, 얼리·레이트 시각, 달력·일자별 이력 |
| v9 | 메이드 선택 확인, 고객 배정·해제, 주급 지급 취소 안전장치 |
| v10 | 벌점 부여·삭제·복구, 메이드 알림, 주급과 벌점 분리 |
| v11 | 운영 중지 상위 상태, 예약 충돌 해결, 608 모순 제거, 재개 점검 청소 |
| v12 | 입실·운영·배정·검수·계정·과거 정정의 확인 모달 전반 보강 |
| **v13** | **촛불 1개 이상 고객 배정·입실 하드 차단, 예약+촛불 충돌, 관리자 전량 회수 확인, 메이드 기존 수량 감소 금지, 배정 불가 촛불 그룹 중복 표시, 촛불·검수 분리, 608 촛불 조건 강화** |

`HISTORY/`에는 과거 단일 HTML을 보관한다. 구현 기준은 v13과 본 문서다.
'''

DOCS['13_QA_REPORT.md'] = r'''# 13. QA 보고서

## 결과

- 대상: `CURRENT/castle_the_art_room_manager_wireframe_v13.html`
- 집중 촛불·안전 QA: **37/37 통과**
- 확장 회귀 QA: **59/59 통과**
- JavaScript 문법 검사: 통과
- 콘솔 오류: 없음
- 모바일 가로 넘침: 360px, 390px, 430px 모두 없음

## 집중 검수 항목

- 촛불 양수 객실 전체 배정 불가
- 예약+촛불 충돌과 입실 잠금
- 관리자 촛불 배치·회수의 사유·최종 확인
- 전량 회수 후 다른 조건 재계산
- 메이드 기존 촛불 감소 버튼 잠금
- 조작된 메이드 제출도 기존 수량 하한 보존
- 검수 승인 후에도 촛불 차단 유지
- 배정 불가 목록의 촛불 회수 그룹
- 608 운영 중지 불변식
- 메이드 선택·주급 취소·벌점·달력 안전 흐름

## 확장 회귀 항목

- 운영 중지·재개와 예약 충돌
- 고객 입실 확인
- 단일 일감 공개 변경
- 원자적 선택을 전제로 한 선택 확인
- 담당 교체·미배정 회수
- 검수 반려와 메이드 알림
- 청소 시작
- 주급 미지급 복구
- 퇴사 계정 복구
- 중요 확인 액션 존재
- 반응형·콘솔 오류

## 파일

- `QA/focused_v13/castle_the_art_v13_qa_report.json`
- `QA/extended_v13/castle_the_art_v13_extended_qa_report.json`
- `QA/screenshots_v13/`

## 아직 자동 검수할 수 없는 영역

- 실제 서버 트랜잭션·DB 제약
- 두 기기 동시 claim·촛불 갱신 충돌
- 실제 사진 업로드·오프라인 복구
- 푸시 전달과 재시도
- 실제 도어락·PMS/OTA·송금
- 장시간 실사용성·접근성 사용자 테스트
'''

DOCS['CODEX_PROMPT.md'] = r'''# Codex에 전달할 시작 프롬프트

이 폴더는 Castle The Art 객실관리 내부 앱 v13의 클릭형 프로토타입, 상태·데이터·API·테스트 명세, 플로우차트다.

먼저 `DOCS/00_START_HERE.md`를 읽고, 다음 파일을 구현 규칙의 우선 기준으로 삼아라.

1. `DOCS/03_STATE_MODEL_AND_BUSINESS_RULES.md`
2. `DOCS/05_CONFIRMATION_AND_SAFETY_MATRIX.md`
3. `DOCS/06_DATA_MODEL.md`
4. `DOCS/07_API_AND_TRANSACTION_DESIGN.md`
5. `DOCS/08_ACCEPTANCE_CRITERIA.md`

`CURRENT/castle_the_art_room_manager_wireframe_v13.html`은 모바일 UI·문구·상호작용의 시각 기준이다. 단일 HTML을 그대로 배포하지 말고 React + TypeScript 모바일 PWA, 서버 API, PostgreSQL로 재구현하라.

반드시 지킬 것:

- 운영, 예약·투숙, 청소·검수, 청소 담당, 차단 특이사항, 촛불을 독립 축으로 모델링한다.
- 촛불 수량이 1개 이상이면 서버에서 고객 배정과 체크인을 거절한다.
- 기존 예약+촛불은 예약 충돌이며, 원인 해결·이동·해제 흐름을 제공한다.
- 메이드는 기존 촛불 수량을 줄일 수 없고 이번 작업 추가분만 기록한다.
- 관리자만 현장 회수 사유와 최종 확인으로 수량을 낮추거나 0개로 확정한다.
- 검수 승인은 촛불을 자동 해제하지 않는다.
- 608호 `운영 중지 + 공실 + 예약 없음 + 작업 없음 + 담당 없음 + 공개 닫힘 + 고객 배정 불가`를 DB·API·E2E로 테스트한다.
- 메이드 일감 선택은 원자적 트랜잭션으로 한 명만 성공시킨다.
- 중요한 명령은 expectedVersion, idempotency key, 사유, 감사 로그, 알림 outbox를 사용한다.
- 과거 원본은 덮어쓰지 않고 정정 이벤트로 추가한다.
- 벌점과 주급을 자동 연결하지 않는다.
- 360/390/430px과 접근성을 테스트한다.

첫 산출물:

1. 도메인·DB·API 아키텍처 문서
2. TypeScript 타입·상태 전이·가용성 파생 함수
3. PostgreSQL 마이그레이션과 핵심 제약
4. `08_ACCEPTANCE_CRITERIA.md` P0 테스트
5. 관리자 객실 운영판
6. 608호, 촛불 배치·회수, 예약 충돌, 일감 claim, 검수 승인 흐름

규칙이 모호하면 임의로 단순화하지 말고 `DOCS/09_CRITIQUE_AND_IMPROVEMENTS.md`의 미결정 항목에 추가하고 질문하라.
'''

for name, content in DOCS.items():
    (ROOT/'DOCS'/name).write_text(content.strip()+"\n", encoding='utf-8')

# Top-level README and consolidated handoff overview.
(ROOT/'README.md').write_text('''# Castle The Art Codex Handoff v13\n\nStart with [`DOCS/00_START_HERE.md`](DOCS/00_START_HERE.md).\n\nCurrent prototype: [`CURRENT/index.html`](CURRENT/index.html)\n\nThe v13 source of truth makes any positive candle count a hard guest-assignment/check-in block until an administrator confirms physical recovery to zero.\n''', encoding='utf-8')

master = '''# Castle The Art 객실관리 앱 — Codex 이관 요약 v13

## 한 문장 목적

Castle The Art의 객실 가용성, 고객 배정, 청소 작업, 사진 검수, 촛불 안전 상태, 메이드 주급·벌점, 일자별 이력을 모바일에서 일관되게 관리한다.

## 현재 실행 파일

- `CURRENT/index.html`
- `CURRENT/castle_the_art_room_manager_wireframe_v13.html`

## 가장 중요한 규칙

- 촛불 1개 이상: 고객 배정·입실 불가.
- 관리자 실제 회수 후 0개 최종 확정: 촛불 차단만 해제, 다른 조건 재계산.
- 메이드: 기존 촛불 감소 불가, 이번 작업 추가분만 기록.
- 608: 운영 중지, 예약·투숙·청소·담당 없음.
- 예약+운영 중지/차단 이슈/촛불: 예약 충돌.
- 검수 승인과 객실 가용성은 별도.
- 모든 중요한 변경은 사유·전후 영향·최종 확인·감사 로그.

## QA

- 집중 37/37
- 확장 회귀 59/59
- 360/390/430px 가로 넘침 없음

세부 내용은 `DOCS/`와 `FLOWCHARTS/`를 본다.
'''
(ROOT/'CASTLE_THE_ART_HANDOFF_SUMMARY_v13.md').write_text(master, encoding='utf-8')

# Flowchart source files.
FLOW = ROOT/'FLOWCHARTS'
for p in FLOW.glob('*'):
    if p.is_file(): p.unlink()

dot_common = '''digraph G {
  graph [rankdir=TB, bgcolor="white", pad="0.25", nodesep="0.32", ranksep="0.42", fontname="NanumSquare"];
  node [shape=box, style="rounded,filled", fontname="NanumSquare", fontsize=11, color="#CBD3D9", fillcolor="#F8FAFB", fontcolor="#17212A", margin="0.15,0.10"];
  edge [fontname="NanumSquare", fontsize=9, color="#697680", fontcolor="#4D5962", arrowsize=0.7];
'''
flows = {
'01_room_operation_guest_allocation': dot_common + r'''
  A [label="날짜 선택\n객실 운영 현황", fillcolor="#EAF3F8"];
  B [label="운영 중지?", shape=diamond, fillcolor="#FFF4E8"];
  C [label="예약 있음 + 하드 차단?", shape=diamond, fillcolor="#FFF4E8"];
  D [label="투숙 중?", shape=diamond, fillcolor="#FFF4E8"];
  E [label="예약 배정됨?", shape=diamond, fillcolor="#FFF4E8"];
  F [label="청소 승인 + 이슈 없음 + 촛불 0개?", shape=diamond, fillcolor="#FFF4E8"];
  X [label="고객 배정·입실·청소 차단", fillcolor="#FDEBEC", color="#D7464B"];
  Y [label="예약 충돌\n원인 해결·이동·해제", fillcolor="#FDEBEC", color="#D7464B"];
  O [label="신규 고객 배정 불가", fillcolor="#F3F4F5"];
  L [label="입실 조건 검사\n미충족 시 잠금", fillcolor="#FFF8E7"];
  V [label="고객 배정 가능", fillcolor="#E8F5EF", color="#24835F"];
  U [label="배정 불가 사유 표시", fillcolor="#FDEBEC", color="#D7464B"];
  A->B; B->X [label="예"]; B->C [label="아니오"];
  C->Y [label="예"]; C->D [label="아니오"];
  D->O [label="예"]; D->E [label="아니오"];
  E->L [label="예"]; E->F [label="아니오"];
  F->V [label="예"]; F->U [label="아니오"];
}''',
'02_608_operation_stop_resume': dot_common + r'''
  A [label="운영 중지 요청"];
  B [label="예약·투숙 있음?", shape=diamond, fillcolor="#FFF4E8"];
  C [label="확정 차단\n예약 이동·해제·퇴실 먼저", fillcolor="#FDEBEC", color="#D7464B"];
  D [label="사유·영향 확인"];
  E [label="최종 확인 모달"];
  F [label="608 불변식\n공실·예약 없음·작업 없음\n담당 없음·공개 닫힘", fillcolor="#FDEBEC"];
  G [label="운영 재개 요청"];
  H [label="운영 재개 점검 청소\n미배정·클로즈", fillcolor="#FFF8E7"];
  I [label="청소·검수 승인"];
  J [label="촛불 0개 + 이슈 없음?", shape=diamond, fillcolor="#FFF4E8"];
  K [label="계속 고객 배정 불가", fillcolor="#FDEBEC"];
  L [label="가용성 재계산", fillcolor="#E8F5EF"];
  A->B; B->C [label="예"]; C->A; B->D [label="아니오"]; D->E->F->G->H->I->J; J->K [label="아니오"]; J->L [label="예"];
}''',
'03_cleaning_assignment_claim': dot_common + r'''
  A [label="청소 작업 생성"];
  B [label="배정 가능?", shape=diamond, fillcolor="#FFF4E8"];
  C [label="배정 불가 사유"];
  D [label="관리자 직접 배정?", shape=diamond, fillcolor="#FFF4E8"];
  E [label="담당·사유·최종 확인"];
  F [label="메이드 선택 오픈"];
  G [label="금액·시간·유형 확인"];
  H [label="선택 후 직접 취소 불가 확인"];
  I [label="원자적 claim", fillcolor="#EAF3F8"];
  J [label="담당 확정·자동 클로즈", fillcolor="#E8F5EF"];
  K [label="이미 다른 메이드가 선택", fillcolor="#FDEBEC"];
  L [label="관리자 교체 또는 미배정 회수", fillcolor="#FFF8E7"];
  A->B; B->C [label="아니오"]; B->D [label="예"]; D->E [label="예"]; D->F [label="아니오"]; F->G->H->I; I->J [label="성공"]; I->K [label="실패"]; J->L;
}''',
'04_cleaning_inspection': dot_common + r'''
  A [label="청소 시작 확인"];
  B [label="체크리스트·사진·메모"];
  C [label="메이드 촛불 추가 수량 기록"];
  D [label="완료 제출 확인"];
  E [label="검수 대기"];
  F [label="사진별 확인"];
  G [label="승인/반려?", shape=diamond, fillcolor="#FFF4E8"];
  H [label="청소 승인·주급 확정", fillcolor="#E8F5EF"];
  I [label="운영·이슈·촛불 재검사", shape=diamond, fillcolor="#FFF4E8"];
  J [label="입실 준비 가능", fillcolor="#E8F5EF"];
  K [label="별도 차단 유지", fillcolor="#FDEBEC"];
  L [label="사진·사유·최종 확인"];
  M [label="재청소·메이드 알림", fillcolor="#FDEBEC"];
  A->B->C->D->E->F->G; G->H [label="승인"]; H->I; I->J [label="모두 충족"]; I->K [label="차단 남음"]; G->L [label="반려"]; L->M->B;
}''',
'05_candle_place_recover': dot_common + r'''
  A [label="현재 촛불 수량"];
  B [label="메이드 작업?", shape=diamond, fillcolor="#FFF4E8"];
  C [label="기존 수량을 하한으로 잠금\n새로 둔 개수만 추가"];
  D [label="관리자 수량·위치·사유 입력"];
  E [label="최종 수량 > 0?", shape=diamond, fillcolor="#FFF4E8"];
  F [label="고객 배정·입실 하드 차단", fillcolor="#FDEBEC", color="#D7464B"];
  G [label="관리자 현장 회수"];
  H [label="전후 수량·사유·최종 확인"];
  I [label="0개 확정?", shape=diamond, fillcolor="#FFF4E8"];
  J [label="차단 유지", fillcolor="#FDEBEC"];
  K [label="촛불 차단 해제\n다른 조건 재계산", fillcolor="#E8F5EF", color="#24835F"];
  A->B; B->C [label="예"]; B->D [label="아니오"]; C->E; D->E; E->F [label="예"]; E->K [label="아니오(0개)"]; F->G->H->I; I->J [label="아니오"]; J->G; I->K [label="예"];
}''',
'06_weekly_pay_penalty': dot_common + r'''
  A [label="검수 승인"];
  B [label="주급 확정 항목"];
  C [label="주차 합산"];
  D [label="지급 완료 확인"];
  E [label="기록 오류?", shape=diamond, fillcolor="#FFF4E8"];
  F [label="사유 입력·미지급 복구", fillcolor="#FFF8E7"];
  G [label="지급 유지", fillcolor="#E8F5EF"];
  H [label="품질 문제"];
  I [label="벌점 사유·근거·점수"];
  J [label="최종 확인·메이드 알림"];
  K [label="삭제·복구?", shape=diamond, fillcolor="#FFF4E8"];
  L [label="사유와 소프트 상태 변경"];
  A->B->C->D->E; E->F [label="예"]; E->G [label="아니오"]; H->I->J->K->L;
}''',
'07_date_history_correction': dot_common + r'''
  A [label="월 달력 날짜 선택"];
  B [label="해당 날짜 객실 읽기 모델"];
  C [label="오늘?", shape=diamond, fillcolor="#FFF4E8"];
  D [label="실시간 명령 가능", fillcolor="#E8F5EF"];
  E [label="과거 읽기 전용", fillcolor="#F3F4F5"];
  F [label="오기입?", shape=diamond, fillcolor="#FFF4E8"];
  G [label="정정 내용·사유"];
  H [label="최종 확인"];
  I [label="원본 유지·정정 이벤트 추가", fillcolor="#EAF3F8"];
  A->B->C; C->D [label="예"]; C->E [label="아니오"]; E->F; F->G [label="예"]; G->H->I;
}'''
}
for name, content in flows.items():
    (FLOW/f'{name}.dot').write_text(content+'\n', encoding='utf-8')

index_parts=['''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Castle The Art v13 Flowcharts</title><style>body{font-family:system-ui,sans-serif;margin:0;background:#f4f6f7;color:#17212a}main{max-width:1100px;margin:auto;padding:28px}article{background:white;border:1px solid #dce2e6;border-radius:18px;padding:18px;margin:18px 0}img{max-width:100%;height:auto}h1{letter-spacing:-.04em}</style></head><body><main><h1>Castle The Art v13 플로우차트</h1>''']
for name in flows:
    title=name.split('_',1)[1].replace('_',' ')
    index_parts.append(f'<article><h2>{title}</h2><a href="{name}.svg"><img src="{name}.svg" alt="{title}"></a></article>')
index_parts.append('</main></body></html>')
(FLOW/'index.html').write_text(''.join(index_parts),encoding='utf-8')

# Package metadata (hashes are generated after flowchart rendering and overview copy).
manifest={
  'package':'Castle The Art Codex Handoff',
  'version':'v13',
  'generated_at_kst':datetime.now(timezone(timedelta(hours=9))).isoformat(),
  'source_of_truth':'CURRENT/castle_the_art_room_manager_wireframe_v13.html',
  'focused_qa':'37/37',
  'extended_qa':'59/59',
  'business_rule':'Any candle count > 0 blocks guest assignment and check-in until an administrator confirms physical recovery to 0.'
}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(ROOT)
