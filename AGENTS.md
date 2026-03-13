# Reading ELLA AGENTS

## 1. 이 프로젝트가 무엇인지

- 제품 이름: `Reading ELLA`
- 대상: `초1`
- 레벨: `GT / S / MGT`
- 학습 단위: `지문 1개 + 객관식 6문항`
- 백엔드: `FastAPI`
- 프론트엔드: `Next.js / React / TypeScript`
- 저장:
  - 문제 원본: `packs/*.json`
  - 번역 오버레이: `translations/**/*.json`
  - 학생 기록: `backend/data/*.db`

쉽게 말하면:

- `frontend`는 학생이 보는 화면
- `backend`는 문제 불러오기, 채점, 저장 담당
- `scripts`는 문제 생성/검사 도구

## 2. 지금 기준의 실제 상태

- 안티그래비티 디자인 반영 완료
- 기능 뼈대와 API 연결 완료
- 통합 테스트는 통과했음
- `배포 전 점검 Step 18`까지 완료됨

중요:

- `packs/g1_*_0001.json ~ g1_*_0100.json` 은 현재 `실문항 300세트`로 다시 생성되어 있음
- `python scripts/validate_packs.py packs --strict-warnings` 기준으로 `303개 파일 전체 OK` 상태다
- 학생 랜덤 로드 API도 현재 `GT / S / MGT`에서 실제 실문항을 반환한다

현재 샘플 실문항 3개도 함께 유지한다.

- `packs/g1_gt_9001.json`
- `packs/g1_s_9001.json`
- `packs/g1_mgt_9001.json`

현재 생성기 구조:

- `scripts/content/common.py`
  - 공통 조립 함수
- `scripts/content/gt_generator.py`
  - GT 전용 생성 로직
- `scripts/content/s_generator.py`
  - S 전용 생성 로직
- `scripts/content/mgt_generator.py`
  - MGT 전용 생성 로직
- `scripts/content/data/*.json`
  - 실제 주제, 보기 후보, 문장 재료 데이터

현재 번역 구조:

- `scripts/generate_local_translations.py`
  - `packs/*.json`을 읽어서 `translations/ko/*.json` 로컬 번역 초안을 일괄 생성한다
- `scripts/validate_translations.py`
  - 번역 JSON이 원본 pack과 구조상 맞는지 검사한다
- `scripts/translation_rules.py`
  - 규칙 기반 한국어 초안을 만든다

## 3. 템플릿 pack 관련 매우 중요한 규칙

이 프로젝트에서 가장 헷갈리기 쉬운 부분이다.

- `scripts/create_pack.py`
  - 레벨 규칙에 맞는 `pack 틀`을 만든다
  - 즉, 완성 문제를 쓰는 도구가 아니라 `빈 문제 구조`를 만든다
- `scripts/generate_pack_bank.py`
  - `GT / S / MGT` 실문항 300세트를 일괄 생성한다
  - 기본 모드는 `real`이고, 필요하면 `--mode template`로 템플릿도 만들 수 있다

새 문제를 더 늘릴 때의 원칙:

- 문장 틀 자체를 바꾸고 싶으면 `scripts/content/*_generator.py`를 본다
- 주제, 보기 후보, 문장 재료만 늘리고 싶으면 `scripts/content/data/*.json`을 먼저 수정한다
- 계획 row 수를 늘리고 싶으면 `python scripts/create_pack_bank_plan.py --packs-per-level 120 --force` 같은 식으로 새 계획표를 만든다
- 즉, 앞으로는 가능하면 `코드`보다 `JSON 데이터`를 늘리는 쪽을 우선한다

현재 보호 장치:

- `scripts/validate_packs.py`
  - `TODO`, `Choice A` 같은 템플릿 문구가 남아 있으면 이제 `ERROR`로 처리한다
- `backend/app/services/pack_loader.py`
  - 학생용 랜덤 문제 로드는 `validator 오류가 없는 pack`만 뽑는다
  - 그래서 TODO 템플릿은 학생 화면에서 자동 제외된다

즉:

- 템플릿 pack은 폴더에 있어도 됨
- 하지만 학생용 문제로 섞여 나오면 안 됨

## 4. 역할 분담

### 코덱스 CLI

- 폴더 구조
- Python 스크립트
- FastAPI
- SQLite
- Next.js 페이지 구조
- 상태 관리
- API 연결
- 테스트 가능한 최소 UI

### 안티그래비티

- 프론트 최종 디자인
- 비주얼 방향
- 색상/타이포/간격
- 카드/버튼/패널 최종 스타일
- 반응형 완성도
- 인터랙션 감도

원칙:

- 코덱스는 기능과 구조를 우선 완성
- 안티그래비티는 시각 완성도를 담당
- 기능 로직을 다시 뒤엎기보다, 이미 있는 구조를 살려 디자인을 입히는 방향을 유지

## 5. 실행할 때 꼭 알아야 할 것

이 프로젝트는 프론트와 백엔드를 같이 켜야 제대로 동작한다.

### 자주 쓰는 명령

```powershell
pnpm dev
pnpm dev:backend
pnpm dev:all
pnpm packs:generate
pnpm packs:validate
pnpm translations:generate
pnpm translations:validate
pnpm check:final
```

뜻:

- `pnpm dev`: 프론트 실행
- `pnpm dev:backend`: 백엔드 실행
- `pnpm dev:all`: 둘 다 실행
- `pnpm packs:generate`: 실문항 300세트 일괄 생성
- `pnpm packs:validate`: 현재 pack 전체 검사
- `pnpm translations:generate`: 없는 로컬 번역 초안 일괄 생성
- `pnpm translations:validate`: 번역 오버레이 구조 검사
- `pnpm check:final`: 프론트 빌드 + pack 검사 + 백엔드 통합 점검

문제 불러오기 실패가 나오면 먼저 확인할 것:

1. `pnpm dev:backend` 가 켜져 있는지
2. `frontend/.env.local` 의 API 주소가 맞는지
3. 브라우저를 강력 새로고침 했는지

## 6. 환경 파일

### 프론트

- 파일: `frontend/.env.local`
- 대표 값:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### 백엔드

- 파일: `backend/.env`
- 예시 파일: `backend/.env.example`

현재 모델 전략:

- 기본 번역, 짧은 해설: `gemini-3.1-flash-lite-preview`
- 자세한 해설: `gemini-2.5-flash`

외부 API 원칙:

- 기본 `OFF`
- 학생이 직접 켠 경우만 사용
- provider를 비우면 외부 호출 안 함
- `mock`으로는 테스트 가능

중요:

- 현재 코드는 `실제 Gemini API Key를 넣어 바로 쓰는 상태`까지는 아직 정리되지 않았다
- provider/model 라우팅 구조는 있지만, 실제 상용 키 연결 여부는 별도 확인이 필요하다

## 7. 문서 우선순위

작업 전에 아래 문서를 먼저 본다.

1. `docs/01_README.md`
2. `docs/TODO.md`
3. 필요 시 나머지 `docs/*.md`

특히 `docs/TODO.md`는 현재 진행 상태를 적는 기준표다.

## 8. 수정할 때 지켜야 할 것

- 완료된 작업은 `docs/TODO.md`에 바로 체크 반영
- 실제 상태가 달라졌으면 문서도 같이 수정
- `create_pack.py` 템플릿과 `generate_pack_bank.py` 실문항 생성을 구분해서 설명할 것
- 학생용으로 노출되는 문제는 `validator error 없음`이 기본 조건
- `packs`를 건드릴 때는 `실문항 300세트`와 `샘플 9001`을 함께 고려할 것
- 문제 생성 관련 설명을 할 때는
  - `생성 체계`
  - `개별 템플릿`
  - `학생용 배포 가능 문제`
  이 3개를 섞어 말하지 말 것

## 9. 현재 신뢰 가능한 검증 기준

아래가 통과되면 기본 점검은 된 것으로 본다.

```powershell
pnpm lint
pnpm build
pnpm packs:validate
pnpm check:final
```

다만 주의:

- 지금은 `packs:generate`가 실제 실문항 300개를 다시 만든다
- 그래도 콘텐츠 품질과 문장 다듬기는 운영 검수 대상으로 계속 본다

## 10. 지금 시점의 한 줄 정리

현재 Reading ELLA는 `기능이 돌아가는 학습 앱`이며,
`GT / S / MGT 실문항 300세트 + validator 통과` 상태다.
