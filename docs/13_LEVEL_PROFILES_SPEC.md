# Rebuild v1 Level Profiles Spec

## 1. 문서 목적

이 문서는 `level_profiles.py`에 들어갈 상수 구조를 고정하는 문서다.

쉽게 말하면:
나중에 Python 코드로 그대로 옮길 기준표다.

## 2. 이 문서가 필요한 이유

`12_CONTENT_DIFFICULTY_MATRIX.md`에서
레벨별 난이도 기준은 이미 정했다.

하지만 구현 단계에서는
"이걸 코드에 어떤 키 이름으로 넣을지"가 또 흔들릴 수 있다.

그래서 이 문서는 아래를 고정한다.

- 상수 파일 이름
- 최상위 딕셔너리 이름
- 레벨 키 이름
- 내부 필드 이름
- 필수 값 구조

## 3. 파일 이름 고정

Python 상수 파일 이름은 아래로 고정한다.

```text
scripts/level_profiles.py
```

## 4. 최상위 상수 이름 고정

최상위 상수 이름은 아래로 고정한다.

```python
LEVEL_PROFILES
```

다른 이름으로 퍼지지 않게 이 이름을 기준으로 통일한다.

## 5. 최상위 구조

최상위 구조는 아래처럼 간다.

```python
LEVEL_PROFILES = {
    "GT": {...},
    "S": {...},
    "MGT": {...},
}
```

중요:

- v1에서는 `MAG`를 넣지 않는다
- v1에서는 `GTi`, `R`도 넣지 않는다

## 6. 각 레벨의 필수 필드

각 레벨 객체는 아래 필드를 반드시 가져야 한다.

```python
{
    "grade": "G1",
    "level": "GT",
    "label": "GT",
    "word_count_min": 60,
    "word_count_max": 110,
    "sentence_count_min": 5,
    "sentence_count_max": 8,
    "skills": [...],
    "inference_allowed": False,
    "translation_priority": "high",
    "tts_priority": "high",
    "explanation_depth": "simple",
}
```

## 7. 필드별 의미

### `grade`

- 문자열
- v1에서는 항상 `G1`

### `level`

- 문자열
- `GT`, `S`, `MGT` 중 하나

### `label`

- 화면 표시용 짧은 이름
- 일단 `level`과 같은 값 사용 가능

### `word_count_min`

- 지문 최소 단어 수

### `word_count_max`

- 지문 최대 단어 수

### `sentence_count_min`

- 지문 최소 문장 수

### `sentence_count_max`

- 지문 최대 문장 수

### `skills`

- 길이 6의 문자열 배열
- 6문항 스킬 분포를 순서대로 담음

### `inference_allowed`

- 추론 문항을 허용하는지 여부
- `GT`는 `False`
- `S`, `MGT`는 `True`

### `translation_priority`

- `high`, `medium`, `low` 중 하나
- UI와 운영 판단에 같이 참고 가능

### `tts_priority`

- `high`, `medium`, `low` 중 하나

### `explanation_depth`

- `simple`, `standard`, `detailed` 중 하나
- 오답 해설 기본 깊이 기준

## 8. 권장 추가 필드

아래는 v1에서 있으면 좋은 필드다.

```python
{
    "preferred_connectors": [...],
    "passage_rules": [...],
    "choice_rules": [...],
    "validator": {...},
}
```

## 9. 추가 필드 의미

### `preferred_connectors`

- 해당 레벨에서 지문에 자연스럽게 허용할 연결어 목록

### `passage_rules`

- 사람과 스크립트가 같이 참고할 간단한 규칙 목록

예:

- `single_event_or_single_info`
- `present_tense_preferred`

### `choice_rules`

- 보기 설계 규칙 목록

예:

- `short_choices`
- `avoid_overly_tricky_distractors`

### `validator`

- 검증기에 넘길 레벨별 검사 기준

## 10. validator 하위 구조 고정

`validator`는 아래 구조를 권장한다.

```python
{
    "enforce_skill_distribution": True,
    "warn_if_word_count_outside_range": True,
    "warn_if_sentence_count_outside_range": True,
}
```

## 11. 최종 권장 구조 예시

```python
LEVEL_PROFILES = {
    "GT": {
        "grade": "G1",
        "level": "GT",
        "label": "GT",
        "word_count_min": 60,
        "word_count_max": 110,
        "sentence_count_min": 5,
        "sentence_count_max": 8,
        "skills": [
            "main_idea",
            "detail",
            "detail",
            "detail",
            "vocab_in_context",
            "vocab_in_context",
        ],
        "inference_allowed": False,
        "translation_priority": "high",
        "tts_priority": "high",
        "explanation_depth": "simple",
        "preferred_connectors": ["and", "but", "then"],
        "passage_rules": [
            "single_event_or_single_info",
            "present_tense_preferred",
            "clear_actor_and_action",
        ],
        "choice_rules": [
            "short_choices",
            "direct_evidence_preferred",
            "avoid_overly_tricky_distractors",
        ],
        "validator": {
            "enforce_skill_distribution": True,
            "warn_if_word_count_outside_range": True,
            "warn_if_sentence_count_outside_range": True,
        },
    },
    "S": {
        "grade": "G1",
        "level": "S",
        "label": "S",
        "word_count_min": 90,
        "word_count_max": 140,
        "sentence_count_min": 6,
        "sentence_count_max": 9,
        "skills": [
            "main_idea",
            "detail",
            "detail",
            "vocab_in_context",
            "vocab_in_context",
            "inference",
        ],
        "inference_allowed": True,
        "translation_priority": "medium",
        "tts_priority": "medium",
        "explanation_depth": "standard",
        "preferred_connectors": ["and", "but", "because", "then"],
        "passage_rules": [
            "two_connected_info_units_allowed",
            "simple_reason_or_sequence_allowed",
        ],
        "choice_rules": [
            "allow_one_or_two_similar_distractors",
            "two_clues_may_be_needed",
        ],
        "validator": {
            "enforce_skill_distribution": True,
            "warn_if_word_count_outside_range": True,
            "warn_if_sentence_count_outside_range": True,
        },
    },
    "MGT": {
        "grade": "G1",
        "level": "MGT",
        "label": "MGT",
        "word_count_min": 120,
        "word_count_max": 180,
        "sentence_count_min": 7,
        "sentence_count_max": 10,
        "skills": [
            "main_idea",
            "detail",
            "detail",
            "vocab_in_context",
            "inference",
            "inference",
        ],
        "inference_allowed": True,
        "translation_priority": "low",
        "tts_priority": "medium",
        "explanation_depth": "detailed",
        "preferred_connectors": ["because", "so", "after", "before", "however"],
        "passage_rules": [
            "comparison_allowed",
            "cause_effect_allowed",
            "reference_tracking_allowed",
        ],
        "choice_rules": [
            "allow_partially_correct_distractors",
            "best_overall_meaning_choice",
        ],
        "validator": {
            "enforce_skill_distribution": True,
            "warn_if_word_count_outside_range": True,
            "warn_if_sentence_count_outside_range": True,
        },
    },
}
```

## 12. create_pack.py가 이 상수를 쓰는 방식

`create_pack.py`는 아래처럼 사용하면 된다.

1. 입력받은 `level`로 `LEVEL_PROFILES[level]` 조회
2. `skills` 배열 길이가 6인지 확인
3. `pack_id` 생성
4. 6문항 템플릿 생성
5. 각 문항에 `skills[i]` 값 채우기

## 13. validate_packs.py가 이 상수를 쓰는 방식

`validate_packs.py`는 아래처럼 사용하면 된다.

1. pack의 `level` 읽기
2. 해당 `LEVEL_PROFILES[level]` 찾기
3. `skills` 분포 비교
4. word count 범위 검사
5. sentence count 범위 검사

## 14. 구현 시 금지할 것

- 레벨별 규칙을 여러 파일에 중복 하드코딩
- `create_pack.py`와 `validate_packs.py`가 서로 다른 기준 사용
- 레벨 이름을 소문자/대문자 섞어서 사용
- `MAG`를 몰래 같은 구조에 넣어두기

## 15. v1 고정 결론

v1에서 `level_profiles.py`는 아래를 만족해야 한다.

- 파일명: `scripts/level_profiles.py`
- 상수명: `LEVEL_PROFILES`
- 레벨 키: `GT`, `S`, `MGT`
- grade 값: `G1`
- skill 배열 길이: 항상 6

## 16. 관련 문서

- `04_DATA_CONTRACT.md`
- `05_BUILD_PLAN.md`
- `11_LEVEL_GUIDE.md`
- `12_CONTENT_DIFFICULTY_MATRIX.md`
