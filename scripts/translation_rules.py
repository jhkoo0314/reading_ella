"""Rule-based Korean seed translation for Reading ELLA packs."""

from __future__ import annotations

import re
from typing import Any

try:
    from backend.app.core.config import get_settings as get_backend_settings
    from backend.app.services.gemini_client import generate_json_response
    from backend.app.services.model_router import select_translation_model
except Exception:  # pragma: no cover - script fallback
    get_backend_settings = None
    generate_json_response = None
    select_translation_model = None


PROMPT_EXACT_MAP = {
    "What is this passage mostly about?": "이 글은 주로 무엇에 대한 글인가요?",
    "What is the passage mostly about?": "이 글은 주로 무엇에 대한 글인가요?",
    "What is the passage mainly about?": "이 글은 주로 무엇에 대한 글인가요?",
    "What does difference mean in the fifth sentence?": "다섯 번째 문장에서 difference는 무슨 뜻인가요?",
    "What does compare mean in the fifth sentence?": "다섯 번째 문장에서 compare는 무슨 뜻인가요?",
    "What does notice mean in the fifth sentence?": "다섯 번째 문장에서 notice는 무슨 뜻인가요?",
    "What does match mean in the third sentence?": "세 번째 문장에서 match는 무슨 뜻인가요?",
    "What does changes mean in the last sentence?": "마지막 문장에서 changes는 무슨 뜻인가요?",
    "What problem did students mention about the first plan?": "학생들은 처음 계획의 어떤 문제를 말했나요?",
    "What problem did students mention about the first map?": "학생들은 처음 지도의 어떤 문제를 말했나요?",
    "Why did the new design work better for younger students?": "왜 새 디자인이 더 어린 학생들에게 더 잘 맞았나요?",
    "Why did clearer signs work better for younger students?": "왜 더 분명한 표지판이 더 어린 학생들에게 더 잘 맞았나요?",
    "What will the team most likely do next?": "팀은 다음에 무엇을 할 가능성이 가장 큰가요?",
    "What will the library most likely do next?": "도서관은 다음에 무엇을 할 가능성이 가장 큰가요?",
    "What did the group check or write down?": "그 모둠은 무엇을 확인하거나 적어 두었나요?",
    "What did the club write in a notebook?": "그 동아리는 공책에 무엇을 적었나요?",
    "What does the student move on the board?": "그 학생은 게시판에서 무엇을 움직이나요?",
}

EXACT_CHOICE_MAP = {
    "Buying new school supplies": "새 학용품 사기",
    "Painting a class poster": "반 포스터 그리기",
    "Cleaning a noisy hallway": "시끄러운 복도 청소하기",
    "Planning a lunch picnic": "점심 소풍 계획하기",
    "Buying decorations for a party": "파티 장식 사기",
    "Painting a classroom wall": "교실 벽 칠하기",
    "Packing clothes for a trip": "여행 옷 싸기",
    "Choosing a movie for the weekend": "주말 영화를 고르기",
    "Painting a room with brighter colors": "방을 더 밝은 색으로 칠하기",
    "Buying more books for a library sale": "도서관 판매용 책 더 사기",
    "Writing long reports about class rules": "학급 규칙에 대한 긴 보고서 쓰기",
    "Moving students to a different school": "학생들을 다른 학교로 옮기기",
    "by the door": "문 옆에",
    "near the window": "창문 근처에",
    "next to the sink": "싱크대 옆에",
    "under the clock": "시계 아래에",
    "beside the rug": "러그 옆에",
    "on the kitchen wall": "부엌 벽에",
    "In the morning": "아침에",
    "After lunch": "점심 후에",
    "Before bed": "잠자기 전에",
    "On Saturday morning": "토요일 아침에",
    "During snack time": "간식 시간에",
    "In the evening": "저녁에",
    "After school": "방과 후에",
    "In the afternoon": "오후에",
    "During homeroom": "조회 시간에",
    "During the first break": "첫 쉬는 시간에",
    "After recess": "쉬는 시간 후에",
    "Name tags": "이름표",
    "Animal cards": "동물 카드",
    "Picture cards": "그림 카드",
    "Short notes": "짧은 메모",
    "Food labels": "음식 라벨",
    "Leaf cards": "잎 카드",
    "Photo cards": "사진 카드",
    "Weather cards": "날씨 카드",
    "Choice cards": "선택 카드",
    "Basket cards": "바구니 카드",
    "Care cards": "돌봄 카드",
    "Fruit cards": "과일 카드",
    "Return cards": "반납 카드",
    "Garden notes": "정원 메모",
    "Toy labels": "장난감 라벨",
    "Helper cards": "도우미 카드",
    "Color labels": "색 라벨",
    "Label cards": "라벨 카드",
    "Look at two things together": "두 가지를 함께 살펴보다",
    "Start a noisy game": "시끄러운 게임을 시작하다",
    "Hide something quickly": "무언가를 빨리 숨기다",
    "Finish all the work": "모든 일을 끝내다",
    "See something important": "중요한 것을 알아차리다",
    "Make a loud sound": "큰 소리를 내다",
    "Carry a heavy box": "무거운 상자를 나르다",
    "Draw a new picture": "새 그림을 그리다",
    "The test results": "시험 결과",
    "The results": "결과",
    "The totals": "합계",
    "Each finished chore": "끝낸 집안일 하나하나",
    "The minutes": "걸린 시간",
    "How quickly each student started": "각 학생이 얼마나 빨리 시작했는지",
    "The finished bracelets": "완성된 팔찌",
    "Each donation": "기부 물품 하나하나",
    "Each leaf change": "잎의 변화 하나하나",
    "A list of class rules": "학급 규칙 목록",
    "A place to store tools": "도구를 두는 곳",
    "A loud sound in a room": "방 안의 큰 소리",
    "A color on the wall": "벽의 색깔",
    "A person who visits a club": "동아리에 오는 사람",
    "A kind of snack": "간식 한 종류",
    "A paint brush": "붓",
    "A long paper list": "긴 종이 목록",
    "A toy basket": "장난감 바구니",
    "A wall poster": "벽 포스터",
    "A room that is easy to clean": "청소하기 쉬운 방",
    "A rule about lunch time": "점심 시간 규칙",
    "A person who leads the school": "학교를 이끄는 사람",
    "The labels were too small to read quickly": "라벨이 너무 작아서 빨리 읽기 어려웠다",
    "The first plan had too many steps": "처음 계획에는 단계가 너무 많았다",
    "Students could not tell what to do next": "학생들은 다음에 무엇을 해야 할지 알기 어려웠다",
    "The design looked nice but felt confusing": "디자인은 예뻤지만 헷갈렸다",
    "Important directions were hard to spot": "중요한 안내를 알아보기 어려웠다",
    "Larger arrows": "더 큰 화살표",
    "Short signs": "짧은 표지판",
    "Color blocks": "색 블록",
    "Simple symbols": "간단한 기호",
    "Practice cards": "연습 카드",
    "It made the room much larger": "방을 훨씬 더 크게 만들었다",
    "It reduced the number of students": "학생 수를 줄였다",
    "It removed every sign from the area": "그 구역의 표지판을 모두 없앴다",
    "Ask students to memorize everything": "학생들에게 모든 것을 외우라고 하기",
    "Remove every sign from the room": "방의 표지판을 모두 없애기",
    "The teacher told the student to stop working": "선생님이 그 학생에게 일을 멈추라고 했다",
    "The group wanted to decorate the room more": "모둠은 방을 더 꾸미고 싶어 했다",
    "The first tool was missing from the class": "첫 번째 도구가 교실에 없었다",
    "The way two things are not the same": "두 가지가 서로 다른 방식",
    "A cover that keeps papers together": "종이를 함께 모아 두는 덮개",
    "Look at something again to remember it": "기억하려고 다시 살펴보다",
    "A home job that someone needs to do": "집에서 해야 하는 일",
    "A set of steps done in the usual order": "보통 순서대로 하는 단계 묶음",
    "Move the body to loosen it": "몸을 풀기 위해 움직이다",
    "The stops on the chart": "차트에 있는 정차 지점들",
    "The way from one place to another": "한 곳에서 다른 곳으로 가는 길",
    "A design that follows the same order": "같은 순서를 따르는 무늬",
    "Something given to help others": "다른 사람을 돕기 위해 내놓은 것",
    "A place with less direct sunlight": "직접 햇빛이 덜 드는 곳",
    "The stem numbers": "줄기 번호",
    "The plant's main stalk": "식물의 주된 줄기",
    "One short action word": "짧은 행동 말 하나",
    "Sample tools": "예시 도구",
    "The same shapes": "같은 모양들",
    "Helper signs": "도움 표지판",
    "Quick maps": "빠른 확인 지도",
    "Short reminder cards": "짧은 안내 카드",
    "One extra sign": "추가 표지판 하나",
    "Quick-check boards": "빠른 확인 게시판",
    "Make sure something is correct": "무언가가 맞는지 확인하다",
    "Too full and hard to read": "너무 빽빽해서 읽기 어렵다",
    "Shown again and again in the same way": "같은 방식으로 여러 번 보이다",
    "People who help without being paid": "돈을 받지 않고 돕는 사람들",
    "Pretty parts that are not the main guide": "핵심 안내는 아니지만 보기 좋게 꾸민 부분",
    "A small picture that stands for something": "어떤 것을 나타내는 작은 그림",
}

PHRASE_REPLACEMENTS = {
    "rainy day": "비 오는 날",
    "holder keeps school papers safe": "보관 도구가 학교 종이를 안전하게 지키는지",
    "which holder keeps school papers safe": "어떤 보관 도구가 학교 종이를 안전하게 지키는지",
    "a better way to carry take-home papers": "가정 학습지를 더 잘 가져가는 방법",
    "a bag that protects homework on rainy days": "비 오는 날 숙제를 지켜 주는 가방",
    "a better way to remember new words": "새 단어를 더 잘 기억하는 방법",
    "which study tool helps word review": "어떤 공부 도구가 단어 복습을 돕는지",
    "an easier way to practice vocabulary": "어휘를 더 쉽게 연습하는 방법",
    "follow stations": "스테이션을 따라갈",
    "follow a community path": "지역 사회 길을 따라갈",
    "follow the morning plan": "아침 계획을 따라갈",
    "a hallway guide for first graders": "1학년용 복도 안내",
    "a school path": "학교 길",
    "school signs": "학교 표지판",
    "event signs": "행사 표지판",
    "community booths": "지역 사회 부스",
    "a community path": "지역 사회 길",
    "protect her papers better": "그녀의 종이를 더 잘 지켜 줄",
    "keep her work drier": "그녀의 학습지를 더 마르게 지켜 줄",
    "stop the pages from bending": "종이가 구겨지는 것을 막아 줄",
    "shorter practice would help her remember more": "더 짧게 연습하면 더 많이 기억하게 도와줄",
    "the cards would make review easier to repeat": "카드가 복습을 더 쉽게 반복하게 해 줄",
    "the slips would help her check words one by one": "쪽지가 단어를 하나씩 확인하게 도와줄",
    "school papers": "학교 종이",
    "homework": "숙제",
    "word review": "단어 복습",
    "vocabulary": "어휘",
    "the new signs gave students clearer directions at each step": "새 표지판이 학생들에게 각 단계마다 더 분명한 안내를 주었다",
    "the redesign reduced extra words and made the route easier to follow": "새 설계가 불필요한 말을 줄이고 길을 더 쉽게 따라가게 했다",
    "students could understand the next move more quickly": "학생들이 다음 움직임을 더 빨리 이해할 수 있었다",
    "use the same clearer style in more places": "더 많은 곳에 같은 더 분명한 방식을 쓰기",
    "use the same clearer style in more school areas": "더 많은 학교 공간에 같은 더 분명한 방식을 쓰기",
    "redesign another hallway with the new system": "새 체계로 다른 복도를 다시 설계하기",
    "expand the new sign system to other grade-one spaces": "새 표지판 체계를 다른 1학년 공간으로 넓히기",
    "job wheel": "역할 바퀴판",
    "schedule board": "일정 게시판",
    "plan chart": "계획 차트",
    "helper chart": "도우미 차트",
    "reading basket board": "읽기 바구니 게시판",
    "center choice board": "센터 선택 게시판",
    "family photo calendar": "가족 사진 달력",
    "chore strip": "집안일 스트립",
    "dinner helper board": "저녁 도우미 게시판",
    "door basket": "문 옆 바구니",
    "routine strip": "루틴 스트립",
    "toy shelf chart": "장난감 선반 차트",
    "weather board": "날씨 게시판",
    "rainy day chart": "비 오는 날 차트",
    "animal corner board": "동물 코너 게시판",
    "pet care chart": "반려동물 돌봄 차트",
    "garden watch board": "정원 관찰 게시판",
    "garden helper chart": "정원 도우미 차트",
    "fruit table board": "과일 테이블 게시판",
    "snack chart": "간식 차트",
    "play choice board": "놀이 선택 게시판",
    "toy turn chart": "장난감 차례 차트",
    "return card board": "반납 카드 게시판",
    "mail table": "우편 테이블",
    "feeding turn board": "먹이 주기 차례판",
    "tree season board": "나무 계절 게시판",
    "leaf color chart": "잎 색깔 차트",
    "sky watch chart": "하늘 관찰 차트",
    "zip bag": "지퍼백",
    "sealed pouch": "밀봉 파우치",
    "snap bag": "스냅 가방",
    "thin plastic folder": "얇은 플라스틱 파일",
    "loose paper folder": "헐거운 종이 파일",
    "open paper file": "열린 종이 파일",
    "small word cards": "작은 단어 카드",
    "tiny review cards": "작은 복습 카드",
    "short word slips": "짧은 단어 쪽지",
    "small chore cards": "작은 집안일 카드",
    "job cards on a ring": "고리에 끼운 일 카드",
    "color chore slips": "색깔 집안일 쪽지",
    "picture routine cards": "그림 루틴 카드",
    "a step board with photos": "사진 단계 보드",
    "small routine pictures": "작은 루틴 그림",
    "three simple stretches": "간단한 스트레칭 세 가지",
    "a short stretch routine": "짧은 스트레칭 순서",
    "easy arm and leg stretches": "쉬운 팔과 다리 스트레칭",
    "small stop cards": "작은 정류장 카드",
    "a simple route strip": "간단한 경로 스트립",
    "short turn cards": "짧은 방향 카드",
    "a color pattern card": "색 패턴 카드",
    "small step pictures": "작은 단계 그림",
    "a short bead pattern strip": "짧은 구슬 패턴 스트립",
    "small labeled boxes": "작은 이름표 상자",
    "color donation bins": "색깔 기부 상자",
    "short shelf labels": "짧은 선반 라벨",
    "the light shade bed": "연한 그늘 화단",
    "a cooler shady patch": "더 서늘한 그늘 자리",
    "the soft shade area": "부드러운 그늘 구역",
    "a bright open patch": "밝고 트인 자리",
    "a sunny window spot": "햇빛 드는 창가 자리",
    "the bright window ledge": "밝은 창턱",
    "the hot sunny bed": "뜨거운 햇빛 화단",
    "the lightest place in the room": "방에서 가장 밝은 자리",
    "the warmest corner": "가장 따뜻한 구석",
    "a full map with every room": "모든 방이 다 들어간 큰 지도",
    "one detailed hallway map": "자세한 복도 지도 하나",
    "one long route on a big map": "큰 지도에 길게 적은 경로 하나",
    "one big notebook": "큰 공책 하나",
    "a long word list": "긴 단어 목록",
    "one large study page": "큰 공부 페이지 하나",
    "one long note on the fridge": "냉장고에 붙인 긴 메모 하나",
    "a plain paper list": "평범한 종이 목록",
    "one big family note": "큰 가족 메모 하나",
    "a parent saying all the steps": "부모가 모든 단계를 말해 주기",
    "one long spoken reminder": "길게 말해 주는 알림 하나",
    "a simple oral list": "간단한 말 목록",
    "doing only one quick move": "빠른 동작 하나만 하기",
    "taking a short rest at the desk": "책상에서 잠깐 쉬기",
    "staying in the chair quietly": "의자에 조용히 앉아 있기",
    "one large mixed box": "큰 섞인 상자 하나",
    "one open table pile": "테이블 위에 열린 더미 하나",
    "a single big basket": "큰 바구니 하나",
    "one page of written steps": "글로 적힌 단계 한 페이지",
    "morning stations": "아침 스테이션",
    "activity booths": "활동 부스",
    "event path": "행사 길",
    "experiment steps": "실험 단계",
    "plant tests": "식물 실험",
    "science directions": "과학 안내",
    "simple tech tools": "간단한 기술 도구",
    "simple repair tools": "간단한 수리 도구",
    "travel stops": "이동 지점",
    "group roles": "모둠 역할",
    "team steps": "팀 단계",
    "puzzle steps": "퍼즐 단계",
    "start and stop steps": "시작과 멈춤 단계",
    "tablet station steps": "태블릿 활동 단계",
    "a story timeline": "이야기 연대표",
    "a transfer path": "환승 경로",
    "bus tour route": "버스 견학 경로",
    "recycling more correctly": "재활용을 더 정확하게 하는 것",
    "take-home papers": "가정 학습지",
    "new words": "새 단어",
    "more easily": "더 쉽게",
    "more clearly": "더 분명하게",
    "with less confusion": "덜 헷갈리도록",
    "without extra help": "추가 도움 없이",
    "without teacher reminders": "교사의 추가 알림 없이",
    "one small change": "작은 변화 하나",
    "the day's job": "그날의 일",
    "younger students": "더 어린 학생들",
    "younger visitors": "더 어린 방문객들",
    "younger children": "더 어린 아이들",
    "first graders": "1학년 학생들",
    "grade-one": "1학년",
    "morning": "아침",
    "afternoon": "오후",
    "evening": "저녁",
    "reading time": "읽기 시간",
    "music class": "음악 시간",
    "story time": "이야기 시간",
    "cleanup time": "정리 시간",
    "dinner": "저녁 식사",
    "bath time": "목욕 시간",
    "homework time": "숙제 시간",
    "playtime": "놀이 시간",
    "lunch": "점심",
    "math": "수학",
    "reading": "읽기",
    "weather": "날씨",
    "animal": "동물",
    "fruit": "과일",
    "garden": "정원",
    "sky": "하늘",
    "leaf": "잎",
    "shelf": "선반",
    "door": "문",
    "window": "창문",
    "clock": "시계",
    "fridge": "냉장고",
    "table": "테이블",
    "board": "게시판",
    "chart": "차트",
    "calendar": "달력",
    "notes": "메모",
    "cards": "카드",
    "card": "카드",
    "labels": "라벨",
    "label": "라벨",
    "map": "지도",
    "project": "프로젝트",
    "test": "테스트",
    "trial": "실험",
    "check": "확인",
    "update": "개선",
    "redesign": "다시 설계",
    "sign": "표지판",
    "signs": "표지판",
    "route": "경로",
    "corner": "코너",
    "station": "스테이션",
    "stations": "스테이션",
    "hallway": "복도",
    "folder": "파일",
    "library": "도서관",
    "museum": "박물관",
    "gallery": "전시실",
    "science": "과학",
    "history": "역사",
    "art": "미술",
    "community": "지역 사회",
}

WORD_REPLACEMENTS = {
    "the": "",
    "a": "",
    "an": "",
    "our": "우리",
    "group": "모둠",
    "team": "팀",
    "club": "동아리",
    "class": "반",
    "school": "학교",
    "student": "학생",
    "students": "학생들",
    "child": "아이",
    "children": "아이들",
    "family": "가족",
    "teacher": "선생님",
    "helpers": "도우미들",
    "helper": "도우미",
    "guide": "안내",
    "guides": "안내들",
    "role": "역할",
    "roles": "역할들",
    "menu": "메뉴",
    "report": "보고",
    "reports": "보고들",
    "time": "시간",
    "times": "시간들",
    "order": "순서",
    "orders": "순서들",
    "step": "단계",
    "steps": "단계들",
    "system": "체계",
    "style": "방식",
    "format": "형식",
    "path": "길",
    "paths": "길들",
    "place": "장소",
    "places": "장소들",
    "direction": "방향",
    "directions": "안내",
    "clue": "단서",
    "clues": "단서들",
    "light": "빛",
    "plants": "식물들",
    "plant": "식물",
    "pictures": "그림들",
    "picture": "그림",
    "event": "행사",
    "events": "행사들",
    "eco": "친환경",
    "tech": "기술",
    "travel": "이동",
    "transfer": "환승",
    "box": "상자",
    "boxes": "상자들",
    "cup": "컵",
    "cups": "컵들",
    "jobs": "일들",
    "job": "일",
    "list": "목록",
    "lists": "목록들",
    "game": "게임",
    "games": "게임들",
    "bead": "구슬",
    "slips": "쪽지들",
    "slip": "쪽지",
    "turn": "차례",
    "name": "이름",
    "picture": "그림",
    "important": "중요한",
    "real": "실제",
    "wrong": "잘못된",
    "young": "어린",
    "study": "공부",
    "sitting": "앉아 있기",
    "understand": "이해하다",
    "remember": "기억하다",
    "find": "찾다",
    "made": "만들었다",
    "make": "만들다",
    "help": "도움",
    "helps": "도와준다",
    "use": "사용",
    "uses": "사용한다",
    "showed": "보여 주었다",
    "show": "보여 주다",
    "see": "보다",
    "set": "놓다",
    "add": "더하다",
    "adds": "더한다",
    "reduced": "줄였다",
    "hard": "어려운",
    "faster": "더 빠르게",
    "much": "많이",
    "each": "각",
    "every": "모든",
    "with": "",
    "for": "",
    "to": "",
    "of": "",
    "in": "",
    "on": "",
    "at": "",
    "and": "그리고",
    "that": "그것",
    "it": "그것",
    "his": "그의",
    "her": "그녀의",
    "not": "않는",
    "could": "할 수",
    "would": "",
    "better": "더 잘",
    "clearer": "더 분명한",
    "clear": "분명한",
    "small": "작은",
    "short": "짧은",
    "large": "큰",
    "larger": "더 큰",
    "simple": "간단한",
    "same": "같은",
    "new": "새로운",
    "next": "다음",
    "first": "첫",
    "last": "마지막",
    "right": "맞는",
    "left": "왼쪽",
    "quickly": "빠르게",
    "slowly": "천천히",
    "again": "다시",
    "because": "왜냐하면",
    "after": "후에",
    "before": "전에",
    "during": "동안",
    "one": "하나",
    "two": "두 가지",
    "many": "많은",
    "more": "더",
    "less": "덜",
    "easy": "쉬운",
    "easier": "더 쉬운",
}

ORDINAL_MAP = {
    "first": "첫 번째",
    "second": "두 번째",
    "third": "세 번째",
    "fourth": "네 번째",
    "fifth": "다섯 번째",
    "sixth": "여섯 번째",
    "seventh": "일곱 번째",
    "last": "마지막",
}

NAME_TOPIC_OVERRIDES = {
    "Mina": "Mina는",
    "Joon": "Joon은",
    "Yuna": "Yuna는",
    "Sora": "Sora는",
    "Theo": "Theo는",
    "Lina": "Lina는",
    "Hana": "Hana는",
    "Noah": "Noah는",
    "Sia": "Sia는",
    "Evan": "Evan은",
}


def _cleanup(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    return text


def _strip_article(text: str) -> str:
    return re.sub(r"^(?:a|an|the)\s+", "", text.strip(), flags=re.IGNORECASE)


def _replace_phrases(text: str) -> str:
    updated = text
    for source, target in sorted(PHRASE_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        updated = re.sub(rf"\b{re.escape(source)}\b", target, updated, flags=re.IGNORECASE)
    return updated


def _translate_position(text: str) -> str:
    raw = text.strip()
    if raw in EXACT_CHOICE_MAP:
        return EXACT_CHOICE_MAP[raw]

    patterns = [
        (r"^by the (.+)$", "{} 옆에"),
        (r"^near the (.+)$", "{} 근처에"),
        (r"^next to the (.+)$", "{} 옆에"),
        (r"^under the (.+)$", "{} 아래에"),
        (r"^beside the (.+)$", "{} 옆에"),
        (r"^on the (.+)$", "{}에"),
        (r"^in the (.+)$", "{}에"),
        (r"^during (.+)$", "{}에"),
        (r"^after (.+)$", "{} 후에"),
        (r"^before (.+)$", "{} 전에"),
        (r"^on (.+)$", "{}에"),
    ]
    for pattern, template in patterns:
        match = re.match(pattern, raw, flags=re.IGNORECASE)
        if match:
            inner = translate_simple_phrase(match.group(1))
            return template.format(inner)
    return translate_simple_phrase(raw)


def translate_simple_phrase(text: str) -> str:
    raw = text.strip().strip('"').rstrip(".")
    if not raw:
        return ""

    if raw in EXACT_CHOICE_MAP:
        return EXACT_CHOICE_MAP[raw]

    possessive_match = re.match(r"^([A-Za-z]+)'s (.+)$", raw)
    if possessive_match:
        return f"{possessive_match.group(1)}의 {translate_simple_phrase(possessive_match.group(2))}"

    stripped = _strip_article(raw)
    replaced = _replace_phrases(stripped)
    parts = re.split(r"(\W+)", replaced)
    translated_parts: list[str] = []
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"\W+", part):
            translated_parts.append(part)
            continue
        lowered = part.lower()
        translated_parts.append(WORD_REPLACEMENTS.get(lowered, part))
    return _cleanup("".join(translated_parts))


def translate_title(title: str) -> str:
    return translate_simple_phrase(title)


def _has_batchim(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    last = stripped[-1]
    if not ("가" <= last <= "힣"):
        return False
    return (ord(last) - ord("가")) % 28 != 0


def _with_particle(text: str, consonant_particle: str, vowel_particle: str) -> str:
    if consonant_particle == "은" and vowel_particle == "는" and text in NAME_TOPIC_OVERRIDES:
        return NAME_TOPIC_OVERRIDES[text]
    particle = consonant_particle if _has_batchim(text) else vowel_particle
    return f"{text}{particle}"


def translate_prompt(prompt: str) -> str:
    raw = prompt.strip()
    if raw in PROMPT_EXACT_MAP:
        return PROMPT_EXACT_MAP[raw]

    patterns = [
        (r"^Where is the (.+)\?$", "{} 어디에 있나요?"),
        (r"^When does ([A-Za-z ]+) use the (.+)\?$", "{} 언제 {}를 사용하나요?"),
        (r"^When does ([A-Za-z ]+) look outside\?$", "{} 언제 밖을 보나요?"),
        (r"^What does the (.+) have\?$", "{}에는 무엇이 있나요?"),
        (r"^Which kind of holder did ([A-Za-z]+) use\?$", "{} 어떤 보관 도구를 사용했나요?"),
        (r"^What did ([A-Za-z]+) use to (.+)\?$", "{} {}할 때 무엇을 사용했나요?"),
        (r"^Where did ([A-Za-z]+) put (.+)\?$", "{} {}를 어디에 두었나요?"),
        (r"^Why did ([A-Za-z]+) switch to (.+)\?$", "왜 {} {}로 바꾸었나요?"),
        (r"^Why did ([A-Za-z]+) move (.+)\?$", "왜 {} {}를 옮겼나요?"),
        (r"^What did the (team|group|helpers|club|library) (.+)\?$", "그 {}은 무엇을 {}했나요?"),
        (r"^What does ([A-Za-z' -]+) mean in the (first|second|third|fourth|fifth|sixth|seventh|last) sentence\?$", "{} 문장에서 {}는 무슨 뜻인가요?"),
        (r"^What does ([A-Za-z' -]+) mean in the passage\?$", "이 글에서 {}는 무슨 뜻인가요?"),
    ]

    for pattern, template in patterns:
        match = re.match(pattern, raw)
        if not match:
            continue
        groups = match.groups()
        if pattern.startswith("^Where is"):
            return template.format(_with_particle(translate_simple_phrase(groups[0]), "은", "는"))
        if pattern.startswith("^When does ([A-Za-z ]+) use"):
            return template.format(_with_particle(groups[0].strip(), "은", "는"), translate_simple_phrase(groups[1]))
        if pattern.startswith("^When does ([A-Za-z ]+) look outside"):
            return template.format(_with_particle(groups[0].strip(), "은", "는"))
        if pattern.startswith("^What does the"):
            return template.format(translate_simple_phrase(groups[0]))
        if pattern.startswith("^Which kind of holder"):
            return template.format(_with_particle(groups[0], "은", "는"))
        if pattern.startswith("^What did ([A-Za-z]+) use to"):
            return template.format(_with_particle(groups[0], "은", "는"), translate_simple_phrase(groups[1]))
        if pattern.startswith("^Where did"):
            return template.format(_with_particle(groups[0], "은", "는"), translate_simple_phrase(groups[1]))
        if pattern.startswith("^Why did ([A-Za-z]+) switch to"):
            return template.format(_with_particle(groups[0], "은", "는"), _with_particle(translate_simple_phrase(groups[1]), "으로", "로"))
        if pattern.startswith("^Why did ([A-Za-z]+) move"):
            return template.format(_with_particle(groups[0], "은", "는"), translate_simple_phrase(groups[1]))
        if pattern.startswith("^What did the"):
            return template.format(groups[0], translate_simple_phrase(groups[1]))
        if pattern.startswith("^What does ([A-Za-z' -]+) mean in the (first|second|third|fourth|fifth|sixth|seventh|last) sentence"):
            return template.format(ORDINAL_MAP[groups[1].lower()], groups[0])
        if pattern.startswith("^What does ([A-Za-z' -]+) mean in the passage"):
            return template.format(groups[0])

    return f"{translate_simple_phrase(raw.rstrip('?'))}에 대한 질문입니다."


def _translate_main_idea_choice(choice: str) -> str:
    match = re.match(r"^Learning which (.+)$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(1))} 알아보기"

    match = re.match(r"^Learning a better way to (.+)$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(1))} 더 좋은 방법 알아보기"

    match = re.match(r"^Testing a better way to (.+)$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(1))} 더 좋은 방법 시험하기"

    match = re.match(r"^Testing which (.+)$", choice)
    if match:
        return f"어떤 {translate_simple_phrase(match.group(1))}인지 시험하기"

    match = re.match(r"^Finding a bag that (.+)$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(1))} 가방 찾기"

    match = re.match(r"^Finding an easier way to (.+)$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(1))} 더 쉬운 방법 찾기"

    match = re.match(r"^Improving (.+) so (.+) can (.+)$", choice)
    if match:
        return (
            f"{translate_simple_phrase(match.group(2))}이 {translate_simple_phrase(match.group(3))} 수 있도록 "
            f"{translate_simple_phrase(match.group(1))} 개선하기"
        )

    match = re.match(r"^Redesigning (.+) for (.+)$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(2))}을 위한 {translate_simple_phrase(match.group(1))} 다시 설계하기"

    match = re.match(r"^Making (.+) easier for (.+) to use$", choice)
    if match:
        return f"{translate_simple_phrase(match.group(2))}이 사용하기 쉬운 {translate_simple_phrase(match.group(1))} 만들기"

    patterns = [
        (r"^Using the (.+)$", "{} 사용하기"),
        (r"^Learning (.+)$", "{} 알아보기"),
        (r"^Testing (.+)$", "{} 시험하기"),
        (r"^Finding (.+)$", "{} 찾기"),
        (r"^Improving (.+)$", "{} 개선하기"),
        (r"^Redesigning (.+)$", "{} 다시 설계하기"),
        (r"^Making (.+)$", "{} 더 쉽게 만들기"),
    ]
    for pattern, template in patterns:
        match = re.match(pattern, choice)
        if match:
            return template.format(translate_simple_phrase(match.group(1)))
    return translate_simple_phrase(choice)


def translate_choice(choice: str, *, prompt: str = "", skill: str = "", level: str = "") -> str:
    raw = choice.strip()
    if raw in EXACT_CHOICE_MAP:
        return EXACT_CHOICE_MAP[raw]

    if skill == "main_idea":
        return _translate_main_idea_choice(raw)

    if prompt.startswith("Where is ") or prompt.startswith("Where did "):
        return _translate_position(raw)

    if prompt.startswith("When does "):
        return _translate_position(raw)

    if prompt.startswith("What does ") and " mean " in prompt:
        return translate_simple_phrase(raw)

    if prompt.startswith("Which kind of holder") or prompt.startswith("What did "):
        return translate_simple_phrase(raw)

    if prompt.startswith("Why did ") and raw.startswith(("She thought ", "He thought ")):
        match = re.match(r"^(She|He) thought (.+)$", raw)
        if match:
            pronoun = "그녀는" if match.group(1) == "She" else "그는"
            thought_text = re.sub(r"^it would\s+", "", match.group(2), flags=re.IGNORECASE)
            return f"{pronoun} {translate_simple_phrase(thought_text)} 것이라고 생각했다"

    return translate_simple_phrase(raw)


def _translated_questions(pack: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    level = str(pack["meta"]["level"])
    for question in pack["questions"]:
        translated_choices = [
            translate_choice(
                str(choice),
                prompt=str(question["prompt"]),
                skill=str(question["skill"]),
                level=level,
            )
            for choice in question["choices"]
        ]
        results.append(
            {
                "id": str(question["id"]),
                "prompt_translated": translate_prompt(str(question["prompt"])),
                "choices_translated": translated_choices,
            }
        )
    return results


def _correct_choice(question: dict[str, Any]) -> str:
    answer_index = int(question.get("answer_index", 0))
    choices = question.get("choices_translated") or []
    if 0 <= answer_index < len(choices):
        return str(choices[answer_index])
    return ""


def _translate_passage_with_live_model(text: str, *, lang: str = "ko") -> str | None:
    if get_backend_settings is None or generate_json_response is None or select_translation_model is None:
        return None

    settings = get_backend_settings()
    if not settings.gemini_api_key:
        return None

    translated = generate_json_response(
        model=select_translation_model(scope="passage"),
        system_instruction=(
            "You translate short English reading passages for Korean elementary learners. "
            "Keep every sentence faithful to the original passage. "
            "Use simple, natural Korean. Do not summarize or add new information. "
            "Return JSON only."
        ),
        user_prompt=(
            f"Translate the following passage into {lang}.\n"
            'Return exactly this JSON shape: {"translated_text":"..."}\n'
            "Keep the full meaning of each sentence. Do not summarize.\n"
            f"PASSAGE: {text}"
        ),
        temperature=0.1,
    )

    if not isinstance(translated, dict):
        return None

    translated_text = str(translated.get("translated_text") or "").strip()
    return translated_text or None


def _translate_passage_fallback(text: str) -> str:
    # Live translation is preferred. This fallback keeps the original sentences
    # instead of replacing them with a summary template.
    return text


def translate_passage_text(pack: dict[str, Any], *, lang: str = "ko") -> str:
    passage = pack.get("passage")
    if not isinstance(passage, dict):
        return ""

    text = str(passage.get("text") or "").strip()
    if not text:
        return ""

    try:
        translated_text = _translate_passage_with_live_model(text, lang=lang)
    except Exception:  # pragma: no cover - network/provider fallback
        translated_text = None

    if translated_text:
        return translated_text
    return _translate_passage_fallback(text)


def build_seed_translation(pack: dict[str, Any], *, lang: str = "ko", source: str = "rule_based_seed") -> dict[str, Any]:
    meta = pack["meta"]
    translated_questions = _translated_questions(pack)
    return {
        "meta": {
            "pack_id": str(meta["pack_id"]),
            "lang": lang,
            "version": str(meta.get("version") or "0.1"),
            "source": source,
        },
        "passage": {
            "title_translated": translate_title(str(pack["passage"]["title"])),
            "text_translated": translate_passage_text(pack, lang=lang),
        },
        "questions": translated_questions,
    }
