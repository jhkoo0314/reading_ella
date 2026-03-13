# Rebuild v1 Content Difficulty Matrix

## 1. 문서 목적

이 문서는 초1 Reading 콘텐츠를
`GT / S / MGT` 기준으로 얼마나 다르게 만들지 고정하는 문서다.

쉽게 말하면:
레벨별 제작 규칙표다.

## 2. 이 문서의 역할

`11_LEVEL_GUIDE.md`가
"각 레벨이 대충 어떤 느낌인가"를 정하는 문서라면,

이 문서는
"실제로 문제를 만들 때 어느 수치와 규칙을 따를 것인가"를 정하는 문서다.

즉, 이 문서는 감각 설명보다 더 실무적인 기준표다.

## 3. 가장 중요한 원칙

- 대상 학년은 `초1` 고정
- 사용 레벨은 `GT / S / MGT`
- `MAG`는 v1에서 제외
- `pack.json` 형식은 바꾸지 않는다
- 레벨 차이는 `pack 내용`과 `Python 생성 규칙`으로 만든다

즉:

- 데이터 계약은 유지
- 레벨별 차이는 스크립트와 작성 규칙으로 관리

## 4. 고정 레벨 순서

이 문서는 아래 순서를 전제로 한다.

```text
GT -> S -> MGT
```

이건 서비스 내부 운영 기준이다.

## 5. 레벨별 핵심 매트릭스

| 항목 | GT | S | MGT |
|---|---|---|---|
| 대상 느낌 | 기본 상급 | 심화 안정 | 상위 도전 |
| 권장 단어 수 | 60~110 | 90~140 | 120~180 |
| 권장 문장 수 | 5~8 | 6~9 | 7~10 |
| 문장 길이 | 짧고 직접적 | 짧지만 연결 가능 | 더 길고 정보 밀도 높음 |
| 문장 구조 | 단문 중심 | 단문 + 쉬운 연결 | 이유, 비교, 지시어 포함 가능 |
| 주제 | 생활, 학교, 가족, 동물 | 생활 + 간단한 설명 | 설명, 비교, 순서, 원인-결과 |
| 정답 근거 | 비교적 바로 보임 | 두 정보 연결 필요 가능 | 두 단서 이상 연결 필요 |
| 오답 난도 | 너무 교묘하지 않음 | 비슷한 보기 1~2개 가능 | 부분적으로 맞는 오답 가능 |
| 추론 비중 | 낮음 | 중간 | 높음 |
| 번역 필요도 | 높음 | 중간 | 선택 보조 |
| TTS 필요도 | 높음 | 중간 | 중간 |
| 오답 해설 깊이 | 아주 쉬운 한국어 | 짧은 이유 설명 | 근거 + 오답 제거 이유 설명 |

## 6. 지문 규칙 매트릭스

## 6.1 GT 지문 규칙

- 한 가지 사건 또는 한 가지 정보 중심
- 현재시제 중심
- 등장인물과 행동이 분명해야 함
- 연결어는 많지 않게
- 문장 하나에서 핵심 정보가 바로 보이게

권장 연결어:

- `and`
- `but`
- `then`

## 6.2 S 지문 규칙

- 두 정보가 자연스럽게 이어질 수 있음
- 이유나 순서가 간단히 들어갈 수 있음
- 연결어를 조금 더 자연스럽게 사용 가능

권장 연결어:

- `and`
- `but`
- `because`
- `then`

## 6.3 MGT 지문 규칙

- 비교, 원인-결과, 순서 구조 가능
- 지시어 해석이 일부 필요할 수 있음
- 같은 문단 안에 두 단서가 흩어질 수 있음

권장 연결어:

- `because`
- `so`
- `after`
- `before`
- `however`

## 7. 문항 구성 매트릭스

문항 수는 항상 6개다.

### GT

- `main_idea`: 1
- `detail`: 3
- `vocab_in_context`: 2

### S

- `main_idea`: 1
- `detail`: 2
- `vocab_in_context`: 2
- `inference`: 1

### MGT

- `main_idea`: 1
- `detail`: 2
- `vocab_in_context`: 1
- `inference`: 2

## 8. 보기 설계 매트릭스

## 8.1 GT 보기 규칙

- 보기 길이는 짧게
- 오답은 너무 길게 쓰지 않음
- 정답은 지문 근거와 가까운 표현 허용
- 오답은 아예 엉뚱한 것보다 "조금 틀린 것" 정도로 시작

## 8.2 S 보기 규칙

- 보기 1~2개는 비슷해 보이게 구성 가능
- 정답은 두 단서를 함께 봐야 확실해지게 가능
- 오답은 한 부분만 맞는 형태 가능

## 8.3 MGT 보기 규칙

- 오답도 부분적으로 맞아 보이게 가능
- 정답은 전체 의미와 가장 잘 맞는 보기여야 함
- 보기 문장 길이를 GT/S보다 조금 더 늘릴 수 있음

## 9. 오답 해설 매트릭스

| 항목 | GT | S | MGT |
|---|---|---|---|
| 길이 | 1~2문장 | 2~3문장 | 3~4문장 |
| 말투 | 아주 쉬운 한국어 | 쉬운 이유 설명 | 근거 중심 설명 |
| 중심 방식 | 답이 글에 어디 있는지 | 왜 이 답인지 | 왜 정답이고 왜 오답인지 |
| 권장 모델 | `gemini-3.1-flash-lite-preview` | `gemini-3.1-flash-lite-preview` | `gemini-2.5-flash` |

## 10. Python 스크립트 생성 규칙

결론부터 말하면:

**네, 레벨별로 Python 스크립트가 만들어낼 수 있도록 구성해야 한다.**

그 이유는 아래와 같다.

- 사람이 만들 때 기준이 흔들리지 않게 하기 위해
- GT/S/MGT가 말로만 다르고 실제 pack은 섞여버리는 문제를 막기 위해
- 검증 스크립트가 자동으로 레벨 규칙 위반을 잡기 위해

## 10.1 추천 구조

Python 쪽에는 최소한 아래 구조가 필요하다.

```text
scripts/
  level_profiles.py
  create_pack.py
  validate_packs.py
  create_translation_template.py
```

## 10.2 level_profiles.py 역할

이 파일은 레벨별 규칙 상수 모음이다.

예상 책임:

- 레벨별 단어 수 범위
- 레벨별 문항 분포
- 레벨별 설명 난도
- 레벨별 연결어 허용 범위
- 레벨별 오답 설계 규칙

예시 개념:

```python
LEVEL_PROFILES = {
    "GT": {
        "word_count_min": 60,
        "word_count_max": 110,
        "skills": ["main_idea", "detail", "detail", "detail", "vocab_in_context", "vocab_in_context"],
    },
    "S": {
        "word_count_min": 90,
        "word_count_max": 140,
        "skills": ["main_idea", "detail", "detail", "vocab_in_context", "vocab_in_context", "inference"],
    },
    "MGT": {
        "word_count_min": 120,
        "word_count_max": 180,
        "skills": ["main_idea", "detail", "detail", "vocab_in_context", "inference", "inference"],
    },
}
```

## 10.3 create_pack.py 역할

이 스크립트는 레벨을 입력받아
그 레벨에 맞는 pack 템플릿을 만든다.

권장 입력:

```bash
python scripts/create_pack.py --grade G1 --level GT --number 0001 --topic "Weather"
```

권장 동작:

- `pack_id` 자동 생성
- `level` 자동 입력
- 레벨별 질문 분포 자동 생성
- 레벨별 word count 목표값 안내 문구 생성
- 질문 6개 뼈대 자동 생성
- 작성자가 채워 넣을 placeholder 생성

## 10.4 create_pack.py가 만들어야 하는 것

이 스크립트는 최소한 아래를 자동으로 넣어줘야 한다.

- `meta.pack_id`
- `meta.level`
- `meta.topic`
- `meta.created_at`
- `meta.version`
- 질문 6개 틀
- 질문별 `skill`
- 선택지 4개 자리

중요:

- `pack schema`는 바꾸지 않는다
- 레벨별 추가 메모가 필요하면 JSON 밖에서 관리한다

## 10.5 validate_packs.py 역할

이 스크립트는 형식 검사만 하는 게 아니라
레벨 규칙도 함께 검사해야 한다.

즉, 아래를 같이 본다.

- 6문항인지
- 선택지 4개인지
- `answer_index` 범위가 맞는지
- `level` 값이 `GT/S/MGT` 중 하나인지
- word count가 레벨 범위 안인지
- skill 분포가 레벨 규칙과 맞는지

## 10.6 validator 경고와 에러 구분

### 에러로 막아야 하는 것

- `level`이 없음
- `level` 값이 잘못됨
- 문항 수가 6개가 아님
- skill 분포가 레벨 규칙과 다름

### 경고로 먼저 볼 수 있는 것

- word count가 권장 범위를 조금 벗어남
- 보기 문장이 너무 길어 보임
- GT인데 inference 느낌의 문항이 너무 어려워 보임

## 11. 스크립트 운영 방식 권장

### 생성

운영자가 `create_pack.py`로 레벨별 초안을 만든다.

### 작성

운영자가 영어 지문과 질문을 채운다.

### 검증

`validate_packs.py`가 레벨 규칙까지 검사한다.

### 번역

필요하면 `create_translation_template.py`로 번역 틀을 만든다.

## 12. 구현자가 꼭 기억할 점

- 레벨 차이는 사람 머릿속에만 두면 안 된다
- Python 스크립트가 레벨 규칙을 알고 있어야 한다
- validator가 레벨 위반을 잡아야 한다
- 그래야 GT/S/MGT 품질이 섞이지 않는다

## 13. 서비스 적용 결론

이 프로젝트는 아래처럼 고정한다.

```text
레벨 선택 UI: GT / S / MGT
pack 생성 방식: level-aware Python scripts
pack 검증 방식: level-aware validator
schema 유지: 기존 pack.json 계약 유지
```

## 14. 관련 문서

- `04_DATA_CONTRACT.md`
- `05_BUILD_PLAN.md`
- `07_CONTENT_MODEL.md`
- `11_LEVEL_GUIDE.md`
