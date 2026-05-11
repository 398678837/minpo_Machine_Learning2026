"""
8장 의사결정나무 강의 PPT 생성 스크립트
python-pptx를 사용하여 강의용 슬라이드를 자동 생성한다.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

DARK_BG = RGBColor(0x1B, 0x1B, 0x2F)
ACCENT_BLUE = RGBColor(0x00, 0x96, 0xFF)
ACCENT_CYAN = RGBColor(0x00, 0xD2, 0xFF)
ACCENT_GREEN = RGBColor(0x00, 0xE6, 0x96)
ACCENT_ORANGE = RGBColor(0xFF, 0x8C, 0x00)
ACCENT_RED = RGBColor(0xFF, 0x45, 0x45)
ACCENT_PURPLE = RGBColor(0xA0, 0x6C, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xBB, 0xBB, 0xCC)
DARK_GRAY = RGBColor(0x88, 0x88, 0x99)
CARD_BG = RGBColor(0x25, 0x25, 0x3D)
SECTION_BG = RGBColor(0x10, 0x10, 0x28)


def add_bg(slide, color=DARK_BG):
    bg = slide.background; fill = bg.fill; fill.solid(); fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color, border_color=None, radius=None):
    if radius:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.adjustments[0] = 0.05
    else:
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, left, top, width, height, text, font_size=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT, font_name='맑은 고딕'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = align
    return txBox


def add_bullet_list(slide, left, top, width, height, items, font_size=16, color=WHITE, spacing=Pt(6)):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = '맑은 고딕'
        p.space_after = spacing
        p.level = 0
    return txBox


def add_accent_line(slide, left, top, width, color=ACCENT_BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_card(slide, left, top, width, height, title, body_items, title_color=ACCENT_CYAN, border=None):
    bc = border if border else CARD_BG
    card = add_shape(slide, left, top, width, height, CARD_BG, bc, radius=True)
    add_text(slide, left + Inches(0.2), top + Inches(0.1), width - Inches(0.4), Inches(0.4),
             title, font_size=15, color=title_color, bold=True)
    add_bullet_list(slide, left + Inches(0.2), top + Inches(0.5), width - Inches(0.4), height - Inches(0.6),
                    body_items, font_size=13, color=LIGHT_GRAY, spacing=Pt(4))


def slide_header(slide, section_num, title, subtitle=""):
    add_accent_line(slide, Inches(0.6), Inches(0.5), Inches(1.2), ACCENT_BLUE)
    add_text(slide, Inches(0.6), Inches(0.55), Inches(2), Inches(0.4),
             f"SECTION {section_num}", font_size=12, color=ACCENT_BLUE, bold=True)
    add_text(slide, Inches(0.6), Inches(0.9), Inches(11), Inches(0.6),
             title, font_size=32, color=WHITE, bold=True)
    if subtitle:
        add_text(slide, Inches(0.6), Inches(1.5), Inches(11), Inches(0.4),
                 subtitle, font_size=16, color=DARK_GRAY)


# ============================================================
# 슬라이드 1: 표지
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SECTION_BG)

# 상단 장식 라인
add_shape(slide, Inches(0), Inches(0), prs.slide_width, Pt(4), ACCENT_BLUE)

# 중앙 콘텐츠
add_text(slide, Inches(0.6), Inches(1.2), Inches(12), Inches(0.5),
         "CHAPTER 8", font_size=20, color=ACCENT_BLUE, bold=True, align=PP_ALIGN.CENTER)
add_accent_line(slide, Inches(5.5), Inches(1.8), Inches(2.3), ACCENT_BLUE)

add_text(slide, Inches(0.6), Inches(2.2), Inches(12), Inches(1.0),
         "의사결정 나무", font_size=48, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, Inches(0.6), Inches(3.2), Inches(12), Inches(0.6),
         "Decision Trees", font_size=28, color=ACCENT_CYAN, bold=False, align=PP_ALIGN.CENTER)

add_text(slide, Inches(0.6), Inches(4.4), Inches(12), Inches(0.5),
         "정보이론 | 분할 기준 | 알고리즘 역사 | 가지치기 | 앙상블 동기",
         font_size=16, color=DARK_GRAY, align=PP_ALIGN.CENTER)

# 하단 정보
add_shape(slide, Inches(3), Inches(5.5), Inches(7.3), Inches(1.2), CARD_BG, ACCENT_BLUE, radius=True)
add_text(slide, Inches(3.3), Inches(5.7), Inches(6.7), Inches(0.35),
         "기계학습 (Machine Learning)", font_size=16, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, Inches(3.3), Inches(6.1), Inches(6.7), Inches(0.35),
         "의사결정나무의 수학적 원리와 ID3/C4.5/CART의 발전 과정을 이해한다",
         font_size=12, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


# ============================================================
# 슬라이드 2: 목차
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "", "목차", "Chapter 8 Overview")

toc_left = [
    ("01", "직관 - 인간의 의사결정 모방", ACCENT_BLUE),
    ("02", "정보이론 기초", ACCENT_CYAN),
    ("03", "분할 기준", ACCENT_GREEN),
    ("04", "알고리즘 역사", ACCENT_ORANGE),
    ("05", "가지치기", ACCENT_PURPLE),
]
toc_right = [
    ("06", "과적합과 불안정성", ACCENT_RED),
    ("07", "변수 선택 편향 / 보충", ACCENT_BLUE),
    ("08", "논문 리뷰", ACCENT_CYAN),
    ("09", "실습 안내", ACCENT_GREEN),
    ("10", "핵심 요약 + 복습 질문", ACCENT_ORANGE),
]

for i, (num, title, clr) in enumerate(toc_left):
    y = Inches(2.2) + Inches(0.85) * i
    add_shape(slide, Inches(0.8), y, Inches(5.5), Inches(0.7), CARD_BG, clr, radius=True)
    add_text(slide, Inches(1.0), y + Inches(0.12), Inches(0.6), Inches(0.45),
             num, font_size=18, color=clr, bold=True)
    add_text(slide, Inches(1.7), y + Inches(0.12), Inches(4.4), Inches(0.45),
             title, font_size=16, color=WHITE)

for i, (num, title, clr) in enumerate(toc_right):
    y = Inches(2.2) + Inches(0.85) * i
    add_shape(slide, Inches(7.0), y, Inches(5.5), Inches(0.7), CARD_BG, clr, radius=True)
    add_text(slide, Inches(7.2), y + Inches(0.12), Inches(0.6), Inches(0.45),
             num, font_size=18, color=clr, bold=True)
    add_text(slide, Inches(7.9), y + Inches(0.12), Inches(4.4), Inches(0.45),
             title, font_size=16, color=WHITE)


# ============================================================
# 슬라이드 3: 8.1 직관 - 스무고개 비유
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.1", "직관 - 인간의 의사결정 모방", "스무고개 비유와 트리 구조")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.5),
         "스무고개 비유", [
             "의사결정나무 = 순차적 질문-응답 과정의 수학적 모델링",
             '"그것은 동물인가?" -> "날 수 있는가?" -> ...',
             "예/아니오 질문을 반복하여 정답에 도달",
             "데이터의 특성(feature) 기반 조건 분할",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.8), Inches(2.5),
         "트리 시각 예시 (연봉 예측)", [
             'Q1: "교육 수준이 13년 이상인가?"',
             '  -> 예 -> Q2: "주당 근무시간 >= 40?" -> [>50K]',
             '  -> 아니오 -> Q3: "나이 >= 30?" -> [<=50K]',
             "조건에 따라 데이터를 분할해 나가며 예측 수행",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(5.0), Inches(12.0), Inches(2.0),
         "핵심 포인트: 해석가능성 (Interpretability)", [
             "의사결정나무의 최강 장점 = 해석가능성. 블랙박스 모델과 달리 '왜 이런 예측을 했는가?'를 직관적으로 이해 가능",
             "금융: 대출 거절 이유 설명 / 의료: 진단 근거 제공 / 법률: EU GDPR 설명 가능한 AI 요건 충족",
             '"인간이 이해할 수 있는 형태의 규칙"을 자동으로 학습하는 알고리즘 -> 여전히 실무에서 널리 사용',
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 4: 8.1 트리 구조 용어
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.1", "트리의 구조와 핵심 용어", "Root Node, Internal Node, Leaf Node")

# 트리 구조 다이어그램 (카드 형태)
add_card(slide, Inches(0.6), Inches(2.2), Inches(6.0), Inches(4.8),
         "트리 구조 다이어그램", [
             "           [교육 수준 <= 12.5]           <- 루트 노드",
             "           /                    \\",
             "   [나이 <= 35.5]        [주당 근무 > 45]   <- 내부 노드",
             "    /          \\            /            \\",
             "[<=50K]   [<=50K]     [>50K]       [<=50K]  <- 리프 노드",
         ], ACCENT_CYAN, ACCENT_CYAN)

# 용어 정리 카드
terms = [
    ("루트 노드 (Root Node)", "최상단 노드, 전체 데이터에 첫 번째 분할", ACCENT_BLUE),
    ("내부 노드 (Internal Node)", "루트와 리프 사이, 추가 분할 조건 보유", ACCENT_CYAN),
    ("리프 노드 (Leaf Node)", "최하단 노드, 최종 예측값 보유", ACCENT_GREEN),
    ("분기 (Split)", "특정 조건에 따라 하위 노드로 분할", ACCENT_ORANGE),
    ("깊이 (Depth)", "루트에서 특정 노드까지의 간선 수", ACCENT_PURPLE),
    ("가지치기 (Pruning)", "과적합 방지를 위해 일부 가지 제거", ACCENT_RED),
]

for i, (term, desc, clr) in enumerate(terms):
    y = Inches(2.2) + Inches(0.75) * i
    add_shape(slide, Inches(7.0), y, Inches(5.7), Inches(0.65), CARD_BG, clr, radius=True)
    add_text(slide, Inches(7.2), y + Inches(0.05), Inches(2.6), Inches(0.3),
             term, font_size=13, color=clr, bold=True)
    add_text(slide, Inches(7.2), y + Inches(0.33), Inches(5.2), Inches(0.28),
             desc, font_size=12, color=LIGHT_GRAY)


# ============================================================
# 슬라이드 5: 8.2 섀넌 엔트로피
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.2", "정보이론 기초 - 섀넌 엔트로피", "Shannon Entropy (1948)")

add_card(slide, Inches(0.6), Inches(2.2), Inches(6.0), Inches(2.2),
         "엔트로피 정의", [
             "H(X) = -SUM( pi * log2(pi) )",
             "",
             "데이터의 불확실성(uncertainty) / 무질서도(disorder)를 정량화",
             '"데이터를 설명하는 데 필요한 평균 비트 수"',
             "0 * log2(0) = 0 으로 정의 (극한값)",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.2),
         "이진 분류에서의 엔트로피", [
             "완전 순수:  p1=1.0, p2=0.0 -> H = 0       (불확실성 없음)",
             "약간 불순:  p1=0.9, p2=0.1 -> H = 0.469   (낮은 불확실성)",
             "중간 불순:  p1=0.7, p2=0.3 -> H = 0.881   (중간 불확실성)",
             "최대 불순:  p1=0.5, p2=0.5 -> H = 1.000   (최대 = 동전 던지기)",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(4.7), Inches(12.1), Inches(2.5),
         "계산 예시: 클래스 A=7개, B=3개 (총 10개)", [
             "H = -(0.7 * log2(0.7) + 0.3 * log2(0.3))",
             "  = -(0.7 * (-0.5146) + 0.3 * (-1.7370))",
             "  = -((-0.3602) + (-0.5211)) = 0.8813",
             "",
             "불확실성이 높을수록 더 많은 비트가 필요하다",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 6: 8.2 정보이득
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.2", "정보이득 (Information Gain)", "분할 전후의 엔트로피 감소량")

add_card(slide, Inches(0.6), Inches(2.2), Inches(6.0), Inches(2.0),
         "정보이득 공식", [
             "IG(S, A) = H(S) - SUM( |Sv|/|S| * H(Sv) )",
             "",
             "S = 부모 노드 데이터, A = 분할 속성",
             "Sv = 속성 A의 값이 v인 부분집합",
             "의사결정나무는 정보이득이 가장 큰 분할을 선택!",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.0),
         "직관적 의미", [
             "정보이득이 크다 = 분할 후 자식 노드가 더 순수(pure)",
             "좋은 질문 = 불확실성을 크게 줄이는 질문",
             "최적 분할 = 정보이득 최대화",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(4.5), Inches(12.1), Inches(2.7),
         "계산 예시", [
             "부모: A=7, B=3 (총 10) -> H = 0.8813",
             "왼쪽 자식: A=6, B=1 (총 7) -> H_L = 0.5917",
             "오른쪽 자식: A=1, B=2 (총 3) -> H_R = 0.9183",
             "",
             "IG = 0.8813 - (7/10 * 0.5917 + 3/10 * 0.9183)",
             "   = 0.8813 - 0.6897 = 0.1916",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 7: 8.3 분할 기준 - 지니 불순도
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.3", "분할 기준 - 지니 불순도", "Gini Impurity (CART / scikit-learn 기본)")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.3),
         "지니 불순도 정의", [
             "Gini(t) = 1 - SUM( pi^2 )",
             "",
             "한 노드에서 임의로 두 샘플을 뽑았을 때",
             "서로 다른 클래스일 확률",
             "이진 분류 범위: 0 (완전 순수) ~ 0.5 (최대 불순)",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.3),
         "계산 예시 (A=7, B=3)", [
             "p(A) = 7/10 = 0.7",
             "p(B) = 3/10 = 0.3",
             "Gini = 1 - (0.7^2 + 0.3^2)",
             "     = 1 - (0.49 + 0.09) = 0.42",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(4.8), Inches(12.1), Inches(2.3),
         "Gini vs Entropy vs Classification Error 비교", [
             "세 기준 모두 p=0.5에서 최대, p=0 또는 p=1에서 0",
             "Gini: 로그 연산 불필요, 계산 효율적 -> scikit-learn 기본값",
             "Entropy: 정보이론 기반, 수학적으로 엄밀 -> ID3, C4.5",
             "Classification Error: 분할 기준으로 사용 시 비효율적 (참고용)",
             "실질적으로 Gini와 Entropy의 분할 결과는 거의 유사함",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 8: 8.3 분산 감소 (회귀 트리) + 기준 비교 표
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.3", "회귀 트리의 분할 기준 + 세 기준 비교", "Variance Reduction (MSE) & Summary")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.2),
         "회귀 트리: MSE (Mean Squared Error)", [
             "MSE(t) = (1/N) * SUM( (yi - y_bar)^2 )",
             "",
             "분할 기준 = MSE 감소량:",
             "dMSE = MSE(부모) - (N_L/N * MSE(L) + N_R/N * MSE(R))",
             "리프 노드의 예측값 = 해당 노드 샘플들의 평균값",
         ], ACCENT_CYAN, ACCENT_CYAN)

# 비교 표 카드
add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.2),
         "세 기준 비교 요약", [
             "엔트로피   | ID3, C4.5 | [0, 1]    | 정보이론 기반",
             "지니 불순도 | CART, sklearn | [0, 0.5] | 계산 효율적",
             "분산 감소   | CART(회귀) | [0, inf)  | 연속값 예측",
             "",
             "sklearn: DecisionTreeClassifier (분류)",
             "sklearn: DecisionTreeRegressor  (회귀)",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(4.7), Inches(12.1), Inches(2.5),
         "Python 코드 예시", [
             "def gini_impurity(labels):",
             "    classes, counts = np.unique(labels, return_counts=True)",
             "    probabilities = counts / len(labels)",
             "    return 1 - np.sum(probabilities ** 2)",
             "",
             "def entropy(labels):",
             "    probabilities = counts / len(labels)",
             "    return -np.sum(probabilities * np.log2(probabilities + 1e-10))",
         ], ACCENT_PURPLE, ACCENT_PURPLE)


# ============================================================
# 슬라이드 9: 8.4 알고리즘 역사 (1) - ID3
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.4", "알고리즘 역사 (1) - ID3", "Iterative Dichotomiser 3 (Quinlan, 1986)")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(3.0),
         "ID3 핵심 특징", [
             "정보이득(Information Gain) 기반 속성 선택",
             "다중 분기(multi-way split) 허용",
             "하향식 재귀 분할(Top-Down Recursive Partitioning)",
             "범주형 속성만 처리 가능 (연속형 미지원)",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(3.0),
         "ID3 한계점", [
             "카디널리티가 높은 속성을 부당하게 선호 (편향)",
             "  -> 고유 값이 많을수록 높은 IG 얻을 확률 증가",
             "가지치기(pruning) 전략 미흡",
             "결측값 처리 불가",
             "",
             "이 한계를 극복한 것이 C4.5와 CART!",
         ], ACCENT_RED, ACCENT_RED)

add_card(slide, Inches(0.6), Inches(5.5), Inches(12.1), Inches(1.6),
         "ID3 알고리즘 의사코드", [
             "ID3(S, Attributes): A* = argmax_A IG(S, A)   # 정보이득 최대 속성",
             "    for each v in Values(A*):  S_v 부분집합 -> 재귀 호출 ID3(S_v, Attributes - {A*})",
             "    정지 조건: 모든 샘플 같은 클래스 or Attributes 비어있음 -> 리프 노드 생성",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 10: 8.4 알고리즘 역사 (2) - CART
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.4", "알고리즘 역사 (2) - CART", "Classification and Regression Trees (Breiman et al., 1984)")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.7),
         "CART 핵심 특징", [
             "이진 분할(binary split) 전용: 항상 2개 부분집합으로 분할",
             "분류: 지니 불순도 / 회귀: MSE",
             "비용-복잡도 가지치기(CCP): 체계적 사후 가지치기",
             "대리 분할(Surrogate Split): 결측값 처리의 체계적 방법",
             "분류와 회귀를 동일 프레임워크에서 처리",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.7),
         "CART vs ID3 비교", [
             "분할 방식:  ID3 = 다중 분기  |  CART = 이진 분할만",
             "분할 기준:  ID3 = 정보이득    |  CART = 지니 불순도",
             "회귀 지원:  ID3 = 불가        |  CART = 가능 (MSE)",
             "가지치기:   ID3 = 미흡        |  CART = CCP (체계적)",
             "결측값:     ID3 = 미지원      |  CART = 대리 분할",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_shape(slide, Inches(0.6), Inches(5.3), Inches(12.1), Inches(1.5), CARD_BG, ACCENT_ORANGE, radius=True)
add_text(slide, Inches(0.8), Inches(5.5), Inches(11.7), Inches(0.5),
         "scikit-learn의 DecisionTreeClassifier와 DecisionTreeRegressor는 CART 알고리즘을 구현한 것이다.",
         font_size=16, color=ACCENT_ORANGE, bold=True)
add_text(slide, Inches(0.8), Inches(6.0), Inches(11.7), Inches(0.5),
         "Leo Breiman은 이후 Random Forest(2001)의 창시자이기도 하다.",
         font_size=14, color=LIGHT_GRAY)


# ============================================================
# 슬라이드 11: 8.4 알고리즘 역사 (3) - C4.5 + 타임라인
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.4", "알고리즘 역사 (3) - C4.5 + 발전 타임라인", "Quinlan, 1993 / IEEE ICDM 데이터 마이닝 10대 알고리즘 1위")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(3.5),
         "C4.5 주요 개선점 (ID3 대비)", [
             "1. 정보이득비율(Gain Ratio) 도입 -> 카디널리티 편향 해결",
             "   GainRatio = IG(S,A) / SplitInfo(S,A)",
             "2. 연속형 속성의 체계적 처리 (이진 분할점 탐색)",
             "3. 오류 기반 가지치기(EBP): 검증 데이터 없이 가지치기",
             "4. 결측값의 확률적 처리: 분수적 분배",
             "5. 트리-규칙 변환: 루트-리프 경로 -> if-then 규칙",
         ], ACCENT_CYAN, ACCENT_CYAN)

# 타임라인
timeline = [
    ("1964", "AID", "최초의 자동 상호작용 탐지"),
    ("1984", "CART", "지니 불순도, CCP, 대리 분할"),
    ("1986", "ID3", "정보이득, TDIDT 프레임워크"),
    ("1993", "C4.5", "이득비율, EBP, 연속형 처리"),
    ("2009", "GUIDE", "편향 없는 변수 선택 (Loh)"),
]

for i, (year, algo, desc) in enumerate(timeline):
    y = Inches(2.3) + Inches(0.7) * i
    clr = ACCENT_ORANGE if algo in ["CART", "C4.5"] else ACCENT_BLUE
    add_shape(slide, Inches(6.8), y, Inches(5.9), Inches(0.6), CARD_BG, clr, radius=True)
    add_text(slide, Inches(7.0), y + Inches(0.1), Inches(0.8), Inches(0.4),
             year, font_size=14, color=clr, bold=True)
    add_text(slide, Inches(7.9), y + Inches(0.1), Inches(1.0), Inches(0.4),
             algo, font_size=14, color=WHITE, bold=True)
    add_text(slide, Inches(9.0), y + Inches(0.1), Inches(3.5), Inches(0.4),
             desc, font_size=12, color=LIGHT_GRAY)

# SplitInfo 수식 카드
add_card(slide, Inches(0.6), Inches(6.0), Inches(12.1), Inches(1.0),
         "SplitInfo(S,A) = -SUM( |Sv|/|S| * log2(|Sv|/|S|) )", [
             "SplitInfo가 클수록 (분기가 많을수록) GainRatio가 줄어듬 -> 과다 분기 억제 효과",
         ], ACCENT_PURPLE, ACCENT_PURPLE)


# ============================================================
# 슬라이드 12: 8.5 가지치기 (1) - 사전 가지치기
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.5", "가지치기 (1) - 사전 가지치기", "Pre-Pruning: 트리 성장 조기 중단")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.2),
         "왜 가지치기가 필요한가?", [
             "가지치기 없음:  Train=97.8%  Test=81.6%  (격차 16.2% = 과적합!)",
             "max_depth=5:   Train=85.4%  Test=85.0%  (격차 0.4% = 양호)",
             "",
             "완전 성장 트리 = 훈련 데이터의 노이즈까지 학습",
         ], ACCENT_RED, ACCENT_RED)

# 파라미터 테이블
params = [
    ("max_depth", "트리의 최대 깊이", "None", "작을수록 단순한 트리"),
    ("min_samples_split", "분할 최소 샘플 수", "2", "클수록 분할 억제"),
    ("min_samples_leaf", "리프 최소 샘플 수", "1", "클수록 작은 리프 제거"),
    ("max_features", "분할 시 최대 특성 수", "None", "랜덤성 부여"),
]

add_shape(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(3.5), CARD_BG, ACCENT_GREEN, radius=True)
add_text(slide, Inches(7.0), Inches(2.3), Inches(5.5), Inches(0.4),
         "주요 하이퍼파라미터", font_size=15, color=ACCENT_GREEN, bold=True)

for i, (name, desc, default, effect) in enumerate(params):
    y = Inches(2.8) + Inches(0.65) * i
    add_text(slide, Inches(7.0), y, Inches(2.2), Inches(0.3),
             name, font_size=12, color=ACCENT_CYAN, bold=True)
    add_text(slide, Inches(9.3), y, Inches(3.2), Inches(0.3),
             f"{desc} (기본={default})", font_size=11, color=LIGHT_GRAY)
    add_text(slide, Inches(9.3), y + Inches(0.25), Inches(3.2), Inches(0.3),
             f"효과: {effect}", font_size=11, color=DARK_GRAY)

add_card(slide, Inches(0.6), Inches(4.7), Inches(12.1), Inches(2.5),
         "max_depth에 따른 트리 변화", [
             "max_depth=1 (Decision Stump): 매우 단순 -> 과소적합(Underfitting) 가능",
             "max_depth=3: 적절한 복잡도, 대부분의 패턴 포착",
             "max_depth=None (제한 없음): 매우 깊은 트리 -> 과적합(Overfitting) 가능",
             "",
             "장점: 구현 간단, 계산 비용 적음 / 단점: 최적 중단 시점을 사전에 알기 어려움",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 13: 8.5 가지치기 (2) - 비용-복잡도 가지치기 (CCP)
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.5", "가지치기 (2) - 비용-복잡도 가지치기 (CCP)", "Cost-Complexity Pruning (CART)")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.5),
         "비용-복잡도 함수", [
             "R_alpha(T) = R(T) + alpha * |T_leaf|",
             "",
             "R(T): 트리 T의 오분류 비율 (총 불순도)",
             "|T_leaf|: 리프 노드 수",
             "alpha: 복잡도 파라미터 (alpha >= 0)",
             "alpha가 클수록 -> 더 공격적으로 가지치기",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.5),
         "CCP 알고리즘 절차", [
             "1. 완전히 성장한 T_max에서 시작",
             "2. 각 내부 노드의 유효 alpha 계산:",
             "   alpha_eff(t) = (R(t) - R(T_t)) / (|T_t,leaf| - 1)",
             "3. 가장 작은 alpha_eff의 하위 트리를 가지치기",
             "4. 반복: T_max > T1 > T2 > ... > T_root",
             "5. 교차검증으로 최적 alpha 선택",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(5.0), Inches(12.1), Inches(2.2),
         "1-SE Rule (One Standard Error Rule)", [
             "단순히 CV 점수 최대인 alpha 대신, 더 보수적인 선택",
             "alpha_1SE = max{ alpha | CV(alpha) >= CV(alpha*) - SE(alpha*) }",
             '"비슷한 성능 범위 내에서 가장 단순한 모델" = 오컴의 면도날(Occam\'s Razor)',
             "sklearn: full_tree.cost_complexity_pruning_path(X_train, y_train) 으로 alpha 경로 계산",
         ], ACCENT_PURPLE, ACCENT_PURPLE)


# ============================================================
# 슬라이드 14: 8.6 과적합과 불안정성
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.6", "과적합과 불안정성", "Overfitting & High Variance Problem")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.3),
         "과적합 (Overfitting)", [
             "모델이 훈련 데이터에 지나치게 맞춰진 상태",
             "",
             "max_depth=1:    Train=91.2%  Test=90.4% (과소적합)",
             "max_depth=3:    Train=96.2%  Test=93.4% (양호)",
             "max_depth=None: Train=100%   Test=91.2% (과적합!)",
         ], ACCENT_RED, ACCENT_RED)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.3),
         "높은 분산 문제 (High Variance)", [
             "의사결정나무의 가장 심각한 단점 = 불안정성",
             "데이터가 약간만 변해도 트리 구조가 크게 달라짐",
             "",
             "원인 1: 탐욕적(greedy) 알고리즘 -> 연쇄 변경",
             "원인 2: 계층적 구조 -> 상위 변화 = 하위 전파",
             "원인 3: 소수 샘플 변화가 분할 결정을 바꿀 수 있음",
         ], ACCENT_ORANGE, ACCENT_ORANGE)

add_card(slide, Inches(0.6), Inches(4.8), Inches(12.1), Inches(2.4),
         "앙상블 동기: Bias-Variance Tradeoff", [
             "단일 트리: 낮은 편향(bias) + 높은 분산(variance)",
             "앙상블: 분산을 줄이면서 편향을 유지 -> 전체 오차 감소",
             "",
             "배깅(Bagging): 부트스트랩 샘플에서 여러 트리 학습, 다수결 투표",
             "랜덤 포레스트(Random Forest): 배깅 + 특성 랜덤 선택 -> 트리 간 상관관계 감소",
             "그래디언트 부스팅(Gradient Boosting): 잔차를 순차적으로 학습하는 약한 트리들의 결합",
         ], ACCENT_GREEN, ACCENT_GREEN)


# ============================================================
# 슬라이드 15: 8.7 변수 선택 편향 + 보충
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.7", "변수 선택 편향 + 보충", "Variable Selection Bias & Supplementary Topics")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.3),
         "Loh(2011)의 편향 분석", [
             "편향 = 예측력이 동일한 두 변수 중 특정 유형을 부당하게 선호",
             "",
             "카디널리티 편향: 고유 값이 많은 속성 -> 분할 후보가 많아",
             "  우연히 높은 IG를 얻을 확률이 높음",
             '예: "주민번호"(고유 값 N개) -> 2^(N-1)-1개 분할 후보',
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.3),
         "해결책", [
             "이득비율(Gain Ratio): IG를 SplitInfo로 나눔 -> C4.5",
             "통계적 검정: 카이제곱 검정 사용 -> CHAID, GUIDE",
             "변수 선택과 분할점 분리: 2단계 독립 수행 -> GUIDE (Loh)",
             "순열 중요도: 변수 무작위 섞어 성능 감소 측정",
             "",
             "sklearn: permutation_importance() 사용 권장",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(4.8), Inches(5.8), Inches(2.4),
         "대리 분할 (Surrogate Splits)", [
             "CART의 결측값 처리 방법",
             "최적 분할 속성이 결측 -> 유사한 결과를 내는",
             "  다른 속성을 대리(surrogate)로 사용",
             "",
             "sklearn은 미지원 -> 사전 결측치 처리 필요",
             "XGBoost/LightGBM은 결측값 직접 처리 가능",
         ], ACCENT_ORANGE, ACCENT_ORANGE)

add_card(slide, Inches(6.8), Inches(4.8), Inches(5.9), Inches(2.4),
         "규칙 추출 (Rule Extraction)", [
             "트리의 루트-리프 경로 -> if-then 규칙 변환",
             "",
             "규칙 1: IF worst_radius <= 16.80",
             "        AND worst_concave_points <= 0.14",
             "        THEN 양성 [신뢰도: 97.2%]",
             "C4.5에서 제안, 각 규칙 독립 가지치기 가능",
         ], ACCENT_PURPLE, ACCENT_PURPLE)


# ============================================================
# 슬라이드 16: 의사결정나무의 장단점
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.6-7", "의사결정나무의 장단점 종합", "Pros and Cons Summary")

pros = [
    ("높은 해석력", "트리 시각화로 예측 근거를 직관적으로 이해 가능"),
    ("전처리 불필요", "스케일링 불필요, 값의 순서(크기 비교)만 사용"),
    ("범주형/수치형 혼합 처리", "두 유형의 데이터를 동시에 처리"),
    ("비선형 관계 포착", "선형 모델과 달리 비선형 패턴 자동 포착"),
    ("빠른 예측 속도", "O(log n) 시간 복잡도"),
]

cons = [
    ("과적합 경향", "제한 없이 성장시키면 노이즈까지 학습"),
    ("불안정성 (High Variance)", "데이터 약간 변해도 트리 구조 크게 변화"),
    ("편향된 분할", "카디널리티 높은 특성에 편향"),
    ("축 정렬 분할만 가능", "대각선 결정 경계 비효율적"),
    ("최적 트리 보장 불가", "탐욕적 알고리즘 -> 지역 최적"),
]

for i, (title, desc) in enumerate(pros):
    y = Inches(2.2) + Inches(0.7) * i
    add_shape(slide, Inches(0.6), y, Inches(5.8), Inches(0.6), CARD_BG, ACCENT_GREEN, radius=True)
    add_text(slide, Inches(0.8), y + Inches(0.05), Inches(2.0), Inches(0.25),
             title, font_size=13, color=ACCENT_GREEN, bold=True)
    add_text(slide, Inches(0.8), y + Inches(0.3), Inches(5.4), Inches(0.25),
             desc, font_size=11, color=LIGHT_GRAY)

for i, (title, desc) in enumerate(cons):
    y = Inches(2.2) + Inches(0.7) * i
    add_shape(slide, Inches(6.8), y, Inches(5.9), Inches(0.6), CARD_BG, ACCENT_RED, radius=True)
    add_text(slide, Inches(7.0), y + Inches(0.05), Inches(2.2), Inches(0.25),
             title, font_size=13, color=ACCENT_RED, bold=True)
    add_text(slide, Inches(7.0), y + Inches(0.3), Inches(5.5), Inches(0.25),
             desc, font_size=11, color=LIGHT_GRAY)

add_shape(slide, Inches(0.6), Inches(5.8), Inches(12.1), Inches(1.2), CARD_BG, ACCENT_ORANGE, radius=True)
add_text(slide, Inches(0.8), Inches(5.9), Inches(11.7), Inches(0.5),
         "불안정성의 해결: 앙상블(Ensemble) 기법", font_size=16, color=ACCENT_ORANGE, bold=True)
add_text(slide, Inches(0.8), Inches(6.35), Inches(11.7), Inches(0.5),
         "랜덤 포레스트(Random Forest)와 그래디언트 부스팅(Gradient Boosting)이 여러 트리를 결합하여 분산을 줄인다.",
         font_size=13, color=LIGHT_GRAY)


# ============================================================
# 슬라이드 17: 전처리 - 범주형 데이터 + 결측치
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.8", "전처리: 범주형 데이터 & 결측치 처리", "Preprocessing for scikit-learn")

add_card(slide, Inches(0.6), Inches(2.2), Inches(3.8), Inches(2.5),
         "map() 변환", [
             "의미가 명확한 이진 변수:",
             "",
             "df['income'].map({",
             "  '<=50K': 0,",
             "  '>50K': 1",
             "})",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(4.6), Inches(2.2), Inches(3.8), Inches(2.5),
         "get_dummies() 원-핫", [
             "3개+ 범주를 가진 변수:",
             "",
             "pd.get_dummies(df,",
             "  drop_first=True)",
             "",
             "drop_first: 다중공선성 방지",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(8.6), Inches(2.2), Inches(4.1), Inches(2.5),
         "Mean Encoding", [
             "고카디널리티 변수 처리:",
             "각 범주 -> 타겟 변수 평균으로 대체",
             "",
             "US -> 0.244 (>50K 비율)",
             "India -> 0.411",
             "주의: 데이터 누수 방지 필수!",
         ], ACCENT_ORANGE, ACCENT_ORANGE)

add_card(slide, Inches(0.6), Inches(5.0), Inches(5.8), Inches(2.2),
         "결측치 처리 방법", [
             "최빈값(Mode) 대체: workclass -> 'Private'",
             "Unknown 대체: occupation -> 'Unknown'",
             "특수값 대체: 인코딩값을 -99로 대체",
             "",
             "sklearn은 결측치를 직접 처리 못함 -> 사전 처리 필수",
         ], ACCENT_PURPLE, ACCENT_PURPLE)

add_card(slide, Inches(6.8), Inches(5.0), Inches(5.9), Inches(2.2),
         "scikit-learn 제약 사항", [
             "sklearn의 DecisionTree는 수치형 입력만 허용",
             "이론적으로 트리는 범주형 직접 처리 가능하지만",
             "sklearn 구현에서는 인코딩이 필수",
             "",
             "트리의 장점: 스케일링(정규화/표준화) 불필요",
             "값의 순서(크기 비교)만 사용하므로 스케일 무관",
         ], ACCENT_CYAN, ACCENT_CYAN)


# ============================================================
# 슬라이드 18: 8.9 논문 리뷰
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.9", "논문 리뷰", "Rokach & Maimon (2005) - TDIDT Framework")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.0),
         "논문 개요", [
             '"Top-Down Induction of Decision Trees Classifiers - A Survey"',
             "IEEE Trans. Systems, Man, and Cybernetics, Vol. 35, No. 4",
             "",
             "TDIDT 알고리즘의 포괄적 분류 체계 제시",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.0),
         "핵심 프레임워크: 5가지 설계 결정", [
             "분할 기준: IG, GainRatio, Gini, Chi-square, 분산 감소",
             "정지 기준: max_depth, min_samples, 순수도 임계값",
             "가지치기: 사전(pre), CCP, EBP, MEP, MDL",
             "결측값 처리: 대리 분할, 확률적 분배, 삭제",
             "분할 유형: 축 정렬, 경사(oblique), 다변량",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(4.5), Inches(12.1), Inches(2.8),
         "주요 기여 3가지", [
             "1. 불순도 기반 vs 거리 기반 분할의 구분",
             "   - 불순도 함수(엔트로피, 지니) vs 거리 기반(카이제곱, KS 검정)의 이론적 차이 분석",
             "2. 가지치기 방법론 비교",
             "   - CCP(CART): 교차검증 기반, 안정적이나 계산 비용 높음",
             "   - EBP(C4.5): 효율적이나 비관적 추정의 정확도에 의존",
             "3. 다변량 분할: a1*x1 + a2*x2 + ... <= theta (경사 분할)",
             "   - 축 정렬 분할보다 표현력 높지만 해석가능성 저하 트레이드오프",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 19: 참고 논문 목록
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.9", "참고 논문 목록", "Key References in Decision Tree Research")

papers = [
    ("1", "Quinlan (1986)", "ID3 알고리즘 제안, 정보이득 기반 속성 선택 공식화",
     "Machine Learning, 1(1), 81-106", ACCENT_BLUE),
    ("2", "Breiman et al. (1984)", "CART, 지니 불순도, 비용-복잡도 가지치기(CCP)",
     "Classification and Regression Trees, Wadsworth", ACCENT_CYAN),
    ("3", "Quinlan (1993)", "이득비율(Gain Ratio), 오류 기반 가지치기(EBP)",
     "C4.5: Programs for Machine Learning, Morgan Kaufmann", ACCENT_GREEN),
    ("4", "Rokach & Maimon (2005)", "TDIDT 프레임워크, 분할/가지치기 체계적 분류",
     "IEEE Trans. SMC-C, 35(4), 476-487", ACCENT_ORANGE),
    ("5", "Loh (2011)", "변수 선택 편향 분석, GUIDE 알고리즘",
     "WIREs DMKD, 1(1), 14-23", ACCENT_PURPLE),
]

for i, (num, author, contrib, journal, clr) in enumerate(papers):
    y = Inches(2.2) + Inches(1.0) * i
    add_shape(slide, Inches(0.6), y, Inches(12.1), Inches(0.85), CARD_BG, clr, radius=True)
    add_text(slide, Inches(0.8), y + Inches(0.05), Inches(0.5), Inches(0.35),
             f"[{num}]", font_size=16, color=clr, bold=True)
    add_text(slide, Inches(1.4), y + Inches(0.05), Inches(3.0), Inches(0.35),
             author, font_size=14, color=WHITE, bold=True)
    add_text(slide, Inches(4.5), y + Inches(0.05), Inches(7.8), Inches(0.35),
             contrib, font_size=13, color=LIGHT_GRAY)
    add_text(slide, Inches(4.5), y + Inches(0.4), Inches(7.8), Inches(0.35),
             journal, font_size=11, color=DARK_GRAY)


# ============================================================
# 슬라이드 20: 실습 안내 (1) - 스크래치 구현
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.10", "실습: 의사결정나무 스크래치 구현", "01_decision_tree_scratch.py")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.5),
         "실습 목표", [
             "의사결정나무를 라이브러리 없이 처음부터 구현",
             "내부 동작 원리를 완전히 이해",
             "",
             "데이터셋: Iris (sklearn 내장)",
             "sklearn DecisionTreeClassifier와 비교",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.5),
         "구현 핵심 내용", [
             "1. 지니 불순도(Gini Impurity) 계산",
             "2. 엔트로피(Entropy) 계산",
             "3. 정보 이득(Information Gain) 계산",
             "4. 재귀적 트리 분할(Recursive Splitting)",
             "5. 예측(Prediction) 및 특성 중요도",
             "6. sklearn과 성능/구조 비교",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(5.0), Inches(12.1), Inches(2.2),
         "핵심 클래스 구조", [
             "class DecisionTreeFromScratch:  # CART 기반",
             "    def __init__(self, max_depth, min_samples_split, criterion):  # 'gini' or 'entropy'",
             "    def fit(self, X, y):         # 재귀적 트리 구축 -> self.root",
             "    def _build_tree(self, X, y, depth):  # 최적 분할 탐색 (모든 특성 x 모든 임계값)",
             "    def predict(self, X):        # 트리 탐색으로 예측",
             "    def print_tree(self, node):  # 텍스트 시각화",
         ], ACCENT_PURPLE, ACCENT_PURPLE)


# ============================================================
# 슬라이드 21: 실습 안내 (2) - CART 가지치기
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.11", "실습: CART 가지치기", "02_cart_pruning.py")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.5),
         "실습 목표", [
             "비용-복잡도 가지치기(CCP)의 원리를 실습",
             "교차검증과 1-SE Rule로 최적 alpha 선택",
             "",
             "데이터셋: Breast Cancer (sklearn 내장)",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.5),
         "실습 핵심 단계", [
             "1. 완전 트리 성장 (Full Tree Growth)",
             "2. CCP Path 계산: cost_complexity_pruning_path()",
             "3. alpha별 트리 학습 + Train/Test 성능 비교",
             "4. 5-폴드 교차검증으로 최적 alpha 선택",
             "5. 1-SE Rule 적용",
             "6. 가지치기 전후 트리 시각화 비교",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(5.0), Inches(12.1), Inches(2.2),
         "기대 결과", [
             "완전 트리: 깊이 ~ 7+, 리프 ~ 20+, Train 높음 but Test 과적합",
             "최적 alpha: 교차검증 최고 CV 정확도의 alpha -> 적절한 가지치기",
             "1-SE alpha: 비슷한 성능 범위에서 가장 단순한 트리",
             "결론: CCP는 과적합을 효과적으로 제어하며, 1-SE Rule은 오컴의 면도날을 실현",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 22: 실습 안내 (3) - 트리 앙상블 기초
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.12", "실습: 트리 앙상블 기초", "03_tree_ensemble_basics.py")

add_card(slide, Inches(0.6), Inches(2.2), Inches(5.8), Inches(2.5),
         "실습 목표", [
             "단일 트리의 불안정성을 실험적으로 확인",
             "다수결 투표(앙상블)가 분산을 감소시키는 원리 이해",
             "",
             "데이터셋: Iris, make_moons (sklearn)",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(6.8), Inches(2.2), Inches(5.9), Inches(2.5),
         "핵심 실험 내용", [
             "1. 부트스트랩 샘플에서 10개 독립 트리 학습",
             "   -> 구조적 불안정성 확인 (특성 중요도 변동)",
             "2. 10개 트리의 예측 분산 비교",
             "3. 다수결 투표 앙상블 vs 개별 트리 성능 비교",
             "4. 앙상블 크기(1~100) 증가 -> 성능 안정화",
             "5. 2D 결정 경계 시각화 비교",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(0.6), Inches(5.0), Inches(12.1), Inches(2.2),
         "기대 핵심 발견", [
             "1. 같은 데이터에서 부트스트랩만 다르게 해도 트리 구조/중요도가 크게 변동 (High Variance)",
             "2. 다수결 투표 앙상블이 개별 트리 평균보다 높은 정확도 달성",
             "3. 트리 수가 증가하면 성능이 안정적으로 수렴 -> 이것이 Random Forest의 n_estimators!",
             "-> 배깅(Bagging) + 특성 랜덤 선택 = 랜덤 포레스트 (다음 장에서 학습)",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 23: 응용 사례
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.13", "응용 사례", "Medical Diagnosis / Customer Segmentation / Manufacturing")

add_card(slide, Inches(0.6), Inches(2.2), Inches(3.8), Inches(4.8),
         "의료 진단 트리", [
             "진단 규칙(Diagnostic Rules) 추출",
             "",
             "해석 가능한 규칙 제공:",
             '"worst perimeter > 114.45이면',
             ' 악성 가능성 높음"',
             "",
             "의료 가이드라인 생성",
             "트리아지(Triage) 자동 분류",
             "FDA 승인에 유리한 설명가능성",
         ], ACCENT_CYAN, ACCENT_CYAN)

add_card(slide, Inches(4.6), Inches(2.2), Inches(3.9), Inches(4.8),
         "고객 세그멘테이션", [
             "VIP / 일반 / 이탈 위험 분류",
             "",
             "[최근 구매일 <= 30일]",
             "  -> [월 구매 >= 50만원]",
             "    -> VIP 고객",
             "    -> 일반 고객",
             "  -> [최근 구매 <= 90일]",
             "    -> 이탈 위험",
             "    -> 이탈 고객",
         ], ACCENT_GREEN, ACCENT_GREEN)

add_card(slide, Inches(8.7), Inches(2.2), Inches(4.0), Inches(4.8),
         "제조 불량 분석", [
             "불량 원인 분석 (Root Cause)",
             "",
             "[온도 > 185도]",
             "  -> [습도 > 65%]",
             "    -> 불량률: 23.4%",
             "    -> 불량률: 5.2%",
             "  -> 불량률: 1.8%",
             "",
             "특성 중요도로 핵심 공정 변수 식별",
             "실시간 모니터링 규칙 탑재 가능",
         ], ACCENT_ORANGE, ACCENT_ORANGE)


# ============================================================
# 슬라이드 24: 핵심 요약 (1/2)
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.14", "핵심 요약 (1/2)", "Key Summary - Part 1")

summary_items = [
    ("트리 구조", "루트 노드 -> 내부 노드 -> 리프 노드의 계층적 구조", ACCENT_BLUE),
    ("엔트로피", "H = -SUM(pi * log2(pi)), 범위 [0, 1] (이진 분류)", ACCENT_CYAN),
    ("지니 불순도", "Gini = 1 - SUM(pi^2), 범위 [0, 0.5] (이진 분류)", ACCENT_GREEN),
    ("정보이득", "분할 전후 불순도 감소량, 가장 큰 분할 선택", ACCENT_ORANGE),
    ("알고리즘 역사", "ID3(1986)->CART(1984)->C4.5(1993), 각각의 핵심 기여", ACCENT_PURPLE),
    ("사전 가지치기", "max_depth, min_samples_split, min_samples_leaf 등으로 제한", ACCENT_RED),
    ("사후 가지치기", "CCP: R_alpha(T) = R(T) + alpha*|T_leaf|, CV로 최적 alpha", ACCENT_BLUE),
]

for i, (topic, content, clr) in enumerate(summary_items):
    y = Inches(2.1) + Inches(0.72) * i
    add_shape(slide, Inches(0.6), y, Inches(12.1), Inches(0.62), CARD_BG, clr, radius=True)
    add_text(slide, Inches(0.8), y + Inches(0.12), Inches(2.2), Inches(0.38),
             topic, font_size=14, color=clr, bold=True)
    add_text(slide, Inches(3.1), y + Inches(0.12), Inches(9.3), Inches(0.38),
             content, font_size=13, color=LIGHT_GRAY)


# ============================================================
# 슬라이드 25: 핵심 요약 (2/2)
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.14", "핵심 요약 (2/2)", "Key Summary - Part 2")

summary_items2 = [
    ("1-SE Rule", "최적 성능 - 1SE 이상인 범위에서 가장 단순한 모델 선택", ACCENT_CYAN),
    ("과적합/불안정성", "높은 분산(high variance), 앙상블로 해결", ACCENT_RED),
    ("변수 선택 편향", "고카디널리티 속성 선호, 이득비율/통계검정으로 완화", ACCENT_ORANGE),
    ("대리 분할", "결측값 처리: 최적 분할과 유사한 대체 속성 사용", ACCENT_PURPLE),
    ("회귀 트리", "MSE 감소 기준, 리프 예측값 = 평균", ACCENT_GREEN),
    ("장점", "해석가능성, 전처리 불필요, 비선형 포착, 빠른 예측", ACCENT_BLUE),
    ("단점", "과적합, 불안정성, 축 정렬 분할만, 탐욕적 최적화", ACCENT_RED),
]

for i, (topic, content, clr) in enumerate(summary_items2):
    y = Inches(2.1) + Inches(0.72) * i
    add_shape(slide, Inches(0.6), y, Inches(12.1), Inches(0.62), CARD_BG, clr, radius=True)
    add_text(slide, Inches(0.8), y + Inches(0.12), Inches(2.2), Inches(0.38),
             topic, font_size=14, color=clr, bold=True)
    add_text(slide, Inches(3.1), y + Inches(0.12), Inches(9.3), Inches(0.38),
             content, font_size=13, color=LIGHT_GRAY)


# ============================================================
# 슬라이드 26: 핵심 수식 모음
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.14", "핵심 수식 모음", "Essential Formulas")

formulas = [
    ("섀넌 엔트로피", "H(X) = -SUM( pi * log2(pi) )", "데이터의 불확실성 측정"),
    ("지니 불순도", "Gini(t) = 1 - SUM( pi^2 )", "두 샘플이 다른 클래스일 확률"),
    ("정보이득", "IG(S,A) = H(S) - SUM( |Sv|/|S| * H(Sv) )", "분할 전후 엔트로피 감소량"),
    ("이득비율", "GainRatio(S,A) = IG(S,A) / SplitInfo(S,A)", "카디널리티 편향 보정 (C4.5)"),
    ("MSE (회귀)", "MSE(t) = (1/N) * SUM( (yi - y_bar)^2 )", "회귀 트리의 분할 기준"),
    ("비용-복잡도", "R_alpha(T) = R(T) + alpha * |T_leaf|", "사후 가지치기 (CCP)"),
    ("유효 alpha", "alpha_eff(t) = (R(t)-R(Tt)) / (|Tt,leaf|-1)", "CCP 가지치기 순서 결정"),
    ("1-SE Rule", "alpha_1SE = max{a | CV(a) >= CV(a*)-SE(a*)}", "단순한 모델 선택 원칙"),
]

for i, (name, formula, desc) in enumerate(formulas):
    y = Inches(2.1) + Inches(0.62) * i
    clr = [ACCENT_BLUE, ACCENT_CYAN, ACCENT_GREEN, ACCENT_ORANGE,
           ACCENT_PURPLE, ACCENT_RED, ACCENT_BLUE, ACCENT_CYAN][i]
    add_shape(slide, Inches(0.6), y, Inches(12.1), Inches(0.55), CARD_BG, clr, radius=True)
    add_text(slide, Inches(0.8), y + Inches(0.1), Inches(1.8), Inches(0.35),
             name, font_size=12, color=clr, bold=True)
    add_text(slide, Inches(2.7), y + Inches(0.1), Inches(5.5), Inches(0.35),
             formula, font_size=13, color=WHITE, bold=False, font_name='Consolas')
    add_text(slide, Inches(8.3), y + Inches(0.1), Inches(4.2), Inches(0.35),
             desc, font_size=11, color=DARK_GRAY)


# ============================================================
# 슬라이드 27: 복습 질문
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
slide_header(slide, "8.14", "복습 질문", "Review Questions (10)")

questions_left = [
    ("Q1", "[개념] 엔트로피와 지니 불순도의 수학적 정의를 쓰고,\n이진 분류에서 각각의 최대값을 구하시오."),
    ("Q2", "[계산] 노드에 클래스 A 8개, B 2개가 있을 때,\n(a) 지니 불순도, (b) 엔트로피를 계산하시오."),
    ("Q3", "[비교] ID3, CART, C4.5의 분할 기준, 분할 방식,\n가지치기 전략을 각각 비교하시오."),
    ("Q4", "[수학] 비용-복잡도 함수에서 alpha의 역할과\nalpha=0, alpha->inf 일 때의 트리를 설명하시오."),
    ("Q5", "[실무] 1-SE Rule이란 무엇이며 왜 적용하는가?"),
]

questions_right = [
    ("Q6", "[이론] 의사결정나무의 높은 분산 원인과\n앙상블 기법의 기본 아이디어를 서술하시오."),
    ("Q7", "[편향] 변수 선택 편향이란? C4.5의 이득비율은\n이 문제를 어떻게 완화하는가?"),
    ("Q8", "[결측] CART 대리 분할의 원리를 설명하시오.\nsklearn에서 결측치 처리 방법은?"),
    ("Q9", "[구현] 스크래치 구현의 최적 분할 탐색\n시간 복잡도를 분석하시오. (d, n, h)"),
    ("Q10", "[응용] 금융(대출 심사)에서 의사결정나무가 신경망보다\n선호되는 이유를 설명하시오."),
]

for i, (qnum, text) in enumerate(questions_left):
    y = Inches(2.1) + Inches(1.0) * i
    clr = [ACCENT_BLUE, ACCENT_CYAN, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_PURPLE][i]
    add_shape(slide, Inches(0.6), y, Inches(5.8), Inches(0.85), CARD_BG, clr, radius=True)
    add_text(slide, Inches(0.8), y + Inches(0.08), Inches(0.5), Inches(0.3),
             qnum, font_size=14, color=clr, bold=True)
    add_text(slide, Inches(1.4), y + Inches(0.08), Inches(4.8), Inches(0.7),
             text, font_size=11, color=LIGHT_GRAY)

for i, (qnum, text) in enumerate(questions_right):
    y = Inches(2.1) + Inches(1.0) * i
    clr = [ACCENT_RED, ACCENT_BLUE, ACCENT_CYAN, ACCENT_GREEN, ACCENT_ORANGE][i]
    add_shape(slide, Inches(6.8), y, Inches(5.9), Inches(0.85), CARD_BG, clr, radius=True)
    add_text(slide, Inches(7.0), y + Inches(0.08), Inches(0.5), Inches(0.3),
             qnum, font_size=14, color=clr, bold=True)
    add_text(slide, Inches(7.6), y + Inches(0.08), Inches(4.9), Inches(0.7),
             text, font_size=11, color=LIGHT_GRAY)


# ============================================================
# 슬라이드 28: Thank You
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, SECTION_BG)

add_shape(slide, Inches(0), Inches(0), prs.slide_width, Pt(4), ACCENT_BLUE)

add_text(slide, Inches(0.6), Inches(1.8), Inches(12), Inches(0.8),
         "Thank You", font_size=52, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

add_accent_line(slide, Inches(5.5), Inches(2.8), Inches(2.3), ACCENT_CYAN)

add_text(slide, Inches(0.6), Inches(3.2), Inches(12), Inches(0.5),
         "8장: 의사결정 나무 (Decision Trees)", font_size=22, color=ACCENT_CYAN, align=PP_ALIGN.CENTER)

add_text(slide, Inches(0.6), Inches(3.9), Inches(12), Inches(0.4),
         "정보이론, 분할 기준, 알고리즘 역사, 가지치기, 앙상블 동기",
         font_size=14, color=DARK_GRAY, align=PP_ALIGN.CENTER)

# 다음 장 안내
add_shape(slide, Inches(3.5), Inches(5.0), Inches(6.3), Inches(1.4), CARD_BG, ACCENT_GREEN, radius=True)
add_text(slide, Inches(3.7), Inches(5.15), Inches(5.9), Inches(0.45),
         "다음 장 예고", font_size=14, color=ACCENT_GREEN, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, Inches(3.7), Inches(5.55), Inches(5.9), Inches(0.45),
         "9장 - 랜덤 포레스트 (Random Forest)", font_size=20, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
add_text(slide, Inches(3.7), Inches(6.0), Inches(5.9), Inches(0.35),
         "배깅 + 특성 랜덤 선택으로 트리의 분산 문제를 해결한다",
         font_size=12, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)


# ============================================================
# 저장
# ============================================================
output_path = r"D:\26년1학기\기계학습\8장\8장_의사결정나무_강의PPT.pptx"
prs.save(output_path)
print(f"PPT 파일이 성공적으로 생성되었습니다: {output_path}")
print(f"총 슬라이드 수: {len(prs.slides)}")
