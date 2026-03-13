# Reading ELLA

초1용 영어 리딩 학습 앱입니다.

쉽게 말하면:

- 학생은 웹에서 문제를 풉니다.
- 백엔드는 문제를 불러오고 채점하고 기록을 저장합니다.
- 운영자는 문제와 번역을 JSON 파일로 관리합니다.

## 현재 상태

- 프론트엔드: `Next.js`
- 백엔드: `FastAPI`
- 기록 저장: `SQLite`
- 문제 원본: `packs/*.json`
- 번역 오버레이: `translations/ko/*.json`
- 레벨: `GT / S / MGT`
- 문제 수: 레벨별 `100세트`씩, 총 `300세트`
- 샘플 세트: `9001` 3개 추가 유지

현재 검증 상태:

- pack 파일 `303개` 검사 통과
- 번역 파일 `303개` 존재
- 번역 검사는 `warning 1개`, `error 0개`
- 최종 점검 스크립트 통과

주의:

- `translations/ko/g1_gt_9001.json`은 기존 수동 번역 파일이라 아직 일부 문항만 채워져 있습니다.
- 새로 만든 번역들은 `자동 초안`입니다. 앱에서는 바로 쓸 수 있지만, 표현은 나중에 더 자연스럽게 다듬을 수 있습니다.

## 바로 실행

이 프로젝트는 프론트와 백엔드를 같이 켜야 제대로 동작합니다.

프론트:

```powershell
cd C:\reading_ella
pnpm dev
```

백엔드:

```powershell
cd C:\reading_ella
pnpm dev:backend
```

한 번에 같이 켜기:

```powershell
cd C:\reading_ella
pnpm dev:all
```

지금 기본 백엔드는 `0.0.0.0:8000`으로 열리도록 맞춰져 있어서,
같은 와이파이에 있는 태블릿도 내 PC IP로 붙을 수 있습니다.

예를 들어 내 PC IP가 `192.168.219.200`이면:

- 백엔드 주소: `http://192.168.219.200:8000/api/v1`
- 태블릿 브라우저나 Vercel 프론트는 이 주소를 API 주소로 사용

주의:

- PC와 태블릿은 같은 네트워크에 있어야 합니다.
- 윈도우 방화벽이 `8000` 포트를 막으면 태블릿에서 안 열릴 수 있습니다.
- Vercel 프론트를 쓸 때는 백엔드 `CORS`에 Vercel 주소를 넣어야 합니다.

## 자주 쓰는 명령

```powershell
pnpm dev
pnpm dev:backend
pnpm build
pnpm lint
pnpm packs:generate
pnpm packs:validate
pnpm translations:generate
pnpm translations:validate
pnpm check:final
```

뜻은 이렇습니다.

- `pnpm dev`: 학생 화면 실행
- `pnpm dev:backend`: 백엔드 실행
- `pnpm build`: 프론트 빌드 확인
- `pnpm lint`: 프론트 코드 검사
- `pnpm packs:generate`: 실문항 다시 생성
- `pnpm packs:validate`: 문제 JSON 검사
- `pnpm translations:generate`: 없는 한국어 번역 초안 생성
- `pnpm translations:validate`: 번역 JSON 구조 검사
- `pnpm check:final`: 프론트 빌드 + 문제 검사 + 번역 검사 + 백엔드 흐름까지 한 번에 점검

## 폴더 설명

- `frontend`: 학생이 보는 웹 화면
- `backend`: 문제 로드, 채점, 저장 API
- `packs`: 영어 원본 문제
- `translations/ko`: 한국어 번역 오버레이
- `scripts`: 문제 생성, 검증, 번역 생성 도구
- `docs`: 설계 문서

## 번역 방식

현재 번역은 2가지가 섞여 있습니다.

- 수동 번역: 사람이 직접 만든 번역
- 자동 초안 번역: 규칙 기반으로 미리 만든 번역

자동 초안 생성기는 아래 파일입니다.

- [generate_local_translations.py](/C:/reading_ella/scripts/generate_local_translations.py)
- [translation_rules.py](/C:/reading_ella/scripts/translation_rules.py)
- [validate_translations.py](/C:/reading_ella/scripts/validate_translations.py)

즉, 운영 방식은 보통 이렇게 보면 됩니다.

1. 영어 문제를 만든다.
2. 자동 번역 초안을 만든다.
3. 필요한 세트만 사람이 빠르게 다듬는다.

## 환경 파일

프론트:

- `frontend/.env.local`
- 대표값: `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1`
- 태블릿/같은 와이파이 예시: `NEXT_PUBLIC_API_BASE_URL=http://내PC_IP:8000/api/v1`

백엔드:

- `backend/.env`
- 예시 파일: `backend/.env.example`
- Gemini 키도 여기에 넣습니다.
- 예: `GEMINI_API_KEY=...`
- Vercel 프론트를 쓸 때는 예:
  `READING_ELLA_CORS_ORIGINS=https://내버셀주소.vercel.app`

현재 보조 모델 기준:

- 기본 번역, 짧은 해설: `gemini-3.1-flash-lite-preview`
- 자세한 해설: `gemini-2.5-flash`

외부 API는 기본 `OFF`입니다.

## 문서

실제 작업 기준 문서는 아래 순서로 보면 됩니다.

1. [README.md](/C:/reading_ella/README.md)
2. [01_README.md](/C:/reading_ella/docs/01_README.md)
3. [TODO.md](/C:/reading_ella/docs/TODO.md)
4. [AGENTS.md](/C:/reading_ella/AGENTS.md)

`docs/01_README.md`는 설계 기준 문서이고,
지금 이 `README.md`는 현재 프로젝트 상태를 바로 보는 안내서입니다.
# reading_ella
