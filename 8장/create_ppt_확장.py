"""8장 의사결정나무 - 확장 강의 PPT 생성 스크립트"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# --- Color Palette ---
DARK_BG = RGBColor(0x1B, 0x1B, 0x2F)
ACCENT_BLUE = RGBColor(0x00, 0x96, 0xFF)
ACCENT_CYAN = RGBColor(0x00, 0xD2, 0xFF)
ACCENT_GREEN = RGBColor(0x00, 0xE6, 0x96)
ACCENT_ORANGE = RGBColor(0xFF, 0x8C, 0x00)
ACCENT_RED = RGBColor(0xFF, 0x45, 0x45)
ACCENT_PURPLE = RGBColor(0xA0, 0x6C, 0xFF)
ACCENT_YELLOW = RGBColor(0xFF, 0xD7, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xBB, 0xBB, 0xCC)
DARK_GRAY = RGBColor(0x88, 0x88, 0x99)
CARD_BG = RGBColor(0x25, 0x25, 0x3D)
SECTION_BG = RGBColor(0x10, 0x10, 0x28)
CODE_BG = RGBColor(0x1E, 0x1E, 0x30)

# ============================================================
# Helper Functions
# ============================================================
def add_bg(slide, color=DARK_BG):
    bg = slide.background; fill = bg.fill; fill.solid(); fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, fill_color, border_color=None, radius=None):
    if radius:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.adjustments[0] = 0.05
    else:
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid(); shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color; shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, left, top, width, height, text, font_size=18, color=WHITE,
             bold=False, align=PP_ALIGN.LEFT, font_name='맑은 고딕'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text; p.font.size = Pt(font_size)
    p.font.color.rgb = color; p.font.bold = bold; p.font.name = font_name; p.alignment = align
    return txBox

def add_bullet_list(slide, left, top, width, height, items, font_size=16,
                    color=WHITE, spacing=Pt(6), bold_first=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame; tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item; p.font.size = Pt(font_size); p.font.color.rgb = color
        p.font.name = '맑은 고딕'; p.space_after = spacing; p.level = 0
        if bold_first and i == 0:
            p.font.bold = True
    return txBox

def add_accent_line(slide, left, top, width, color=ACCENT_BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    shape.fill.solid(); shape.fill.fore_color.rgb = color; shape.line.fill.background()
    return shape

def add_card(slide, left, top, width, height, title, body_items,
             title_color=ACCENT_CYAN, border=None):
    bc = border if border else CARD_BG
    add_shape(slide, left, top, width, height, CARD_BG, bc, radius=True)
    add_text(slide, left + Inches(0.2), top + Inches(0.1), width - Inches(0.4), Inches(0.4),
             title, font_size=15, color=title_color, bold=True)
    add_bullet_list(slide, left + Inches(0.2), top + Inches(0.5), width - Inches(0.4),
                    height - Inches(0.6), body_items, font_size=13, color=LIGHT_GRAY, spacing=Pt(4))

def slide_header(slide, section_num, title, subtitle=""):
    add_accent_line(slide, Inches(0.6), Inches(0.5), Inches(1.2), ACCENT_BLUE)
    add_text(slide, Inches(0.6), Inches(0.55), Inches(2), Inches(0.4),
             f"SECTION {section_num}" if section_num else "", font_size=12,
             color=ACCENT_BLUE, bold=True)
    add_text(slide, Inches(0.6), Inches(0.9), Inches(11), Inches(0.6),
             title, font_size=32, color=WHITE, bold=True)
    if subtitle:
        add_text(slide, Inches(0.6), Inches(1.5), Inches(11), Inches(0.4),
                 subtitle, font_size=16, color=DARK_GRAY)

def add_code_block(slide, left, top, width, height, code_lines, font_size=11):
    add_shape(slide, left, top, width, height, CODE_BG, ACCENT_BLUE, radius=True)
    txBox = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15),
                                      width - Inches(0.4), height - Inches(0.3))
    tf = txBox.text_frame; tf.word_wrap = True
    for i, line in enumerate(code_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(font_size)
        p.font.color.rgb = ACCENT_GREEN; p.font.name = 'Consolas'; p.space_after = Pt(2)

def add_table_slide(slide, headers, rows, left, top, col_widths,
                    header_color=ACCENT_BLUE, row_height=0.45, font_size=13, header_font_size=14):
    cx = left
    for j, (h, w) in enumerate(zip(headers, col_widths)):
        add_shape(slide, cx, top, Inches(w), Inches(0.45), header_color)
        add_text(slide, cx, top, Inches(w), Inches(0.45),
                 h, font_size=header_font_size, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        cx += Inches(w)
    for i, row in enumerate(rows):
        y = top + Inches(0.45) + Inches(row_height) * i
        bg = CARD_BG if i % 2 == 0 else RGBColor(0x2D, 0x2D, 0x45)
        cx = left
        for j, (cell, w) in enumerate(zip(row, col_widths)):
            add_shape(slide, cx, y, Inches(w), Inches(row_height), bg)
            fc = ACCENT_CYAN if j == 0 else LIGHT_GRAY
            add_text(slide, cx + Inches(0.05), y, Inches(w - 0.1), Inches(row_height),
                     cell, font_size=font_size, color=fc, bold=(j == 0), align=PP_ALIGN.CENTER)
            cx += Inches(w)

def section_divider(title, subtitle, section_num, accent=ACCENT_BLUE):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, SECTION_BG)
    add_shape(s, Inches(0), Inches(0), prs.slide_width, Pt(4), accent)
    add_shape(s, Inches(0), Inches(7.2), prs.slide_width, Pt(4), accent)
    add_text(s, Inches(0), Inches(2.0), prs.slide_width, Inches(0.5),
             f"SECTION {section_num}", font_size=20, color=accent, bold=True, align=PP_ALIGN.CENTER)
    add_accent_line(s, Inches(5.5), Inches(2.7), Inches(2.3), accent)
    add_text(s, Inches(0), Inches(3.0), prs.slide_width, Inches(1.0),
             title, font_size=44, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, Inches(0), Inches(4.2), prs.slide_width, Inches(0.5),
             subtitle, font_size=18, color=DARK_GRAY, align=PP_ALIGN.CENTER)
    return s

# ============================================================
# Slide 1: Title
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s, SECTION_BG)
add_shape(s, Inches(0), Inches(0), prs.slide_width, Pt(4), ACCENT_BLUE)
add_shape(s, Inches(0), Inches(7.2), prs.slide_width, Pt(4), ACCENT_BLUE)
add_text(s, Inches(0), Inches(1.2), prs.slide_width, Inches(0.5),
         "CHAPTER 8", font_size=22, color=ACCENT_BLUE, bold=True, align=PP_ALIGN.CENTER)
add_accent_line(s, Inches(5.5), Inches(1.9), Inches(2.3), ACCENT_BLUE)
add_text(s, Inches(0), Inches(2.2), prs.slide_width, Inches(1.2),
         "의사결정나무 (Decision Tree)", font_size=48, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
add_text(s, Inches(0), Inches(3.8), prs.slide_width, Inches(0.5),
         "직관 | 정보이론 | 분할 기준 | ID3/CART/C4.5 | 가지치기 | 앙상블 동기 | 실습",
         font_size=18, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
add_text(s, Inches(0), Inches(5.5), prs.slide_width, Inches(0.4),
         "기계학습 (Machine Learning)", font_size=16, color=DARK_GRAY, align=PP_ALIGN.CENTER)

# ============================================================
# Slide 2: Table of Contents
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "", "목차 (Table of Contents)")
sections_left = [
    "8.1  직관 - 인간의 의사결정 모방",
    "8.2  정보이론 기초",
    "8.3  분할 기준",
    "8.4  알고리즘 역사 (ID3/CART/C4.5)",
    "8.5  가지치기 (Pruning)",
    "8.6  과적합과 불안정성",
    "8.7  변수 선택 편향",
]
sections_right = [
    "8.8  보충 (결측치, 회귀, 시각화)",
    "8.9  논문 리뷰 (TDIDT 프레임워크)",
    "8.10 실습: 의사결정나무 스크래치",
    "8.11 실습: CART 가지치기",
    "8.12 실습: 트리 앙상블 기초",
    "8.13 응용사례",
    "8.14 핵심 요약 + 복습 질문",
]
add_bullet_list(s, Inches(0.8), Inches(2.0), Inches(5.5), Inches(5.0),
                sections_left, font_size=18, color=LIGHT_GRAY, spacing=Pt(12))
add_bullet_list(s, Inches(6.8), Inches(2.0), Inches(5.5), Inches(5.0),
                sections_right, font_size=18, color=LIGHT_GRAY, spacing=Pt(12))

# ============================================================
# Slide 3: Learning Objectives
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "", "학습 목표")
objectives = [
    "1. 의사결정나무의 수학적 원리(엔트로피, 지니 불순도)를 깊이 이해한다",
    "2. ID3, CART, C4.5의 발전 과정과 각 알고리즘의 핵심 기여를 파악한다",
    "3. 비용-복잡도 가지치기(CCP)와 1-SE Rule의 원리를 이해하고 적용한다",
    "4. 과적합/불안정성 문제를 인식하고 앙상블 기법의 동기를 이해한다",
    "5. 스크래치 구현과 가지치기 실습을 통해 실무 적용 능력을 갖춘다",
]
add_bullet_list(s, Inches(0.8), Inches(2.2), Inches(11), Inches(4.5),
                objectives, font_size=20, color=LIGHT_GRAY, spacing=Pt(16))

# ============================================================
# SECTION 1: 8.1 직관 - 인간의 의사결정 모방
# ============================================================
section_divider("직관 - 인간의 의사결정 모방", "Decision Tree Intuition", "8.1", ACCENT_BLUE)

# Slide 5: 스무고개 비유
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.1", "스무고개 비유", "의사결정나무는 인간의 순차적 질문-응답 과정을 모델링한다")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.5),
         "스무고개 게임의 원리",
         ["'그것은 동물인가?' -> 예/아니오",
          "'날 수 있는가?' -> 예/아니오",
          "'크기가 고양이보다 큰가?' -> 예/아니오",
          "=> 반복적 질문으로 정답에 도달"],
         title_color=ACCENT_CYAN, border=ACCENT_BLUE)
add_card(s, Inches(6.6), Inches(2.2), Inches(6.0), Inches(2.5),
         "연봉 예측 예시",
         ["질문 1: '교육 수준이 13년 이상인가?'",
          "  -> 예 -> '주당 근무시간 >= 40?' -> 예 -> [>50K]",
          "  -> 아니오 -> '나이 >= 30?' -> ...",
          "데이터 특성 기반 조건으로 분할하며 예측 수행"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_shape(s, Inches(0.6), Inches(5.2), Inches(12), Inches(1.5), CARD_BG, ACCENT_ORANGE, radius=True)
add_text(s, Inches(0.9), Inches(5.3), Inches(11.4), Inches(1.3),
         "핵심 포인트: 의사결정나무는 '인간이 이해할 수 있는 형태의 규칙'을 자동으로 학습하는 알고리즘이다. "
         "이 해석가능성이 여전히 의사결정나무가 실무에서 널리 사용되는 이유이다.",
         font_size=16, color=ACCENT_ORANGE, bold=True)

# Slide 6: 트리의 구조
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.1", "트리의 구조", "루트 노드, 내부 노드, 리프 노드의 계층적 구성")
add_code_block(s, Inches(0.6), Inches(2.2), Inches(6.0), Inches(2.5), [
    "            [교육 수준 <= 12.5]         <- 루트 노드 (Root)",
    "            /                \\",
    "     [나이 <= 35.5]      [주당 근무 > 45]  <- 내부 노드 (Internal)",
    "      /        \\           /         \\",
    "  [<=50K]   [<=50K]    [>50K]     [<=50K]  <- 리프 노드 (Leaf)",
], font_size=13)
add_table_slide(s,
    ["용어", "영문", "설명"],
    [["루트 노드", "Root Node", "트리의 최상단, 첫 번째 분할 지점"],
     ["내부 노드", "Internal Node", "추가적인 분할 조건을 가진 중간 노드"],
     ["리프 노드", "Leaf Node", "최종 예측값을 가진 최하단 노드"],
     ["분기 (Split)", "Split", "조건에 따라 데이터를 하위 노드로 나누는 과정"],
     ["깊이 (Depth)", "Depth", "루트에서 특정 노드까지의 간선 수"],
     ["가지치기", "Pruning", "과적합 방지를 위해 가지를 제거하는 기법"]],
    Inches(7.0), Inches(2.2), [1.6, 1.8, 3.5], row_height=0.42, font_size=12)

# Slide 7: 해석가능성
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.1", "해석가능성 (Interpretability)", "블랙박스 모델과 달리 '왜 이런 예측을 했는가?'를 직관적으로 이해")
add_card(s, Inches(0.6), Inches(2.2), Inches(3.6), Inches(3.0),
         "금융 (Finance)",
         ["'대출이 거절된 이유'를",
          "고객에게 설명해야 하는",
          "규제 요건 충족",
          "",
          "예: '연소득 < 3000만원 AND",
          "    신용등급 < 600' -> 거절"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(4.5), Inches(2.2), Inches(3.6), Inches(3.0),
         "의료 (Medical)",
         ["'왜 이 진단을 내렸는가'를",
          "의사가 이해할 수 있어야",
          "하는 윤리적 요구",
          "",
          "예: 'tumor_size > 3cm AND",
          "    age > 60' -> 악성 의심"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(8.4), Inches(2.2), Inches(4.2), Inches(3.0),
         "법률 / 규제 (Legal)",
         ["EU GDPR: '설명 가능한 AI'",
          "(Explainable AI) 요구",
          "",
          "의사결정나무는 규칙 형태로",
          "의사결정 과정을 투명하게 제시",
          "=> 규제 준수에 가장 유리한 모델"],
         title_color=ACCENT_PURPLE, border=ACCENT_PURPLE)
add_text(s, Inches(0.6), Inches(5.8), Inches(12), Inches(0.8),
         "=> 의사결정나무의 최대 장점: '인간이 이해할 수 있는 형태의 규칙'을 자동으로 학습",
         font_size=18, color=ACCENT_YELLOW, bold=True)

# ============================================================
# SECTION 2: 8.2 정보이론 기초
# ============================================================
section_divider("정보이론 기초", "Shannon Entropy & Information Gain", "8.2", ACCENT_CYAN)

# Slide 9: 섀넌 엔트로피 정의
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.2", "섀넌 엔트로피 (Shannon Entropy)", "Claude Shannon (1948) - 데이터의 불확실성을 정량화")
add_shape(s, Inches(0.6), Inches(2.2), Inches(6.0), Inches(1.8), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(5.4), Inches(0.4),
         "엔트로피 정의", font_size=16, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.8), Inches(5.4), Inches(0.8),
         "H(X) = - SUM[ p_i * log2(p_i) ],  i = 1, ..., C\n"
         "0 * log2(0) = 0 으로 정의 (극한값)",
         font_size=18, color=WHITE, bold=True, font_name='Consolas')
add_card(s, Inches(7.0), Inches(2.2), Inches(5.5), Inches(1.8),
         "직관적 의미",
         ["데이터를 설명하는 데 필요한 '평균 비트 수'",
          "불확실성이 높을수록 -> 더 많은 비트 필요",
          "완전 순수(한 클래스) -> H = 0 (불확실성 없음)",
          "최대 불순(균등 분포) -> H = log2(C) (최대 불확실성)"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
# 이진 분류 엔트로피 표
add_table_slide(s,
    ["상태", "p1", "p2", "H", "의미"],
    [["완전 순수", "1.0", "0.0", "0", "불확실성 없음"],
     ["약간 불순", "0.9", "0.1", "0.469", "낮은 불확실성"],
     ["중간 불순", "0.7", "0.3", "0.881", "중간 불확실성"],
     ["최대 불순", "0.5", "0.5", "1.000", "최대 불확실성 (동전)"]],
    Inches(0.6), Inches(4.5), [1.8, 1.2, 1.2, 1.2, 3.0], row_height=0.42, font_size=13)

# Slide 10: 엔트로피 계산 예시
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.2", "엔트로피 계산 예시", "구체적 수치로 엔트로피 계산 과정 이해하기")
add_shape(s, Inches(0.6), Inches(2.2), Inches(12), Inches(1.8), CARD_BG, ACCENT_BLUE, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(11.4), Inches(0.3),
         "예시: 노드에 클래스 A 7개, 클래스 B 3개", font_size=16, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(11.4), Inches(1.1),
         "H = -( 0.7 * log2(0.7) + 0.3 * log2(0.3) )\n"
         "  = -( 0.7 * (-0.5146) + 0.3 * (-1.7370) )\n"
         "  = -( -0.3602 + (-0.5211) ) = 0.8813",
         font_size=17, color=WHITE, font_name='Consolas')
add_code_block(s, Inches(0.6), Inches(4.4), Inches(12), Inches(2.8), [
    "import numpy as np",
    "",
    "def entropy(labels):",
    '    """엔트로피를 계산하는 함수"""',
    "    if len(labels) == 0: return 0.0",
    "    classes, counts = np.unique(labels, return_counts=True)",
    "    probabilities = counts / len(labels)",
    "    ent = -np.sum(probabilities * np.log2(probabilities + 1e-10))",
    "    return ent",
    "",
    "# 순수 노드: 0.0000 | 혼합 노드 7:3: 0.8813 | 최대 불순 5:5: 1.0000",
], font_size=12)

# Slide 11: 정보이득 정의
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.2", "정보이득 (Information Gain)", "분할 전후의 엔트로피 감소량 = 좋은 질문의 척도")
add_shape(s, Inches(0.6), Inches(2.2), Inches(6.0), Inches(2.0), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(5.4), Inches(0.4),
         "정보이득 공식", font_size=16, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.8), Inches(5.4), Inches(1.2),
         "IG(S, A) = H(S) - SUM[ |S_v|/|S| * H(S_v) ]\n\n"
         "S: 부모 노드의 데이터\n"
         "A: 분할 속성\n"
         "S_v: 속성 A의 값이 v인 부분집합",
         font_size=15, color=WHITE, font_name='Consolas')
add_card(s, Inches(7.0), Inches(2.2), Inches(5.5), Inches(2.0),
         "핵심 원리",
         ["의사결정나무는 정보이득이 '가장 큰' 분할을 선택",
          "정보이득이 크다 = 분할 후 자식 노드가 더 순수해짐",
          "좋은 질문 = 불확실성을 크게 줄이는 질문",
          "탐욕적(greedy) 방식으로 매 단계 최적 분할 선택"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 12: 정보이득 계산 예시
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.2", "정보이득 계산 예시", "구체적 수치를 통한 단계별 계산")
add_shape(s, Inches(0.6), Inches(2.2), Inches(12), Inches(4.5), CARD_BG, ACCENT_BLUE, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(11.4), Inches(0.4),
         "단계별 계산", font_size=16, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.8), Inches(11.4), Inches(4.0),
         "1. 부모 노드: 클래스 A 7개, 클래스 B 3개 (총 10개)\n"
         "   -> H(parent) = 0.8813\n\n"
         "2. 왼쪽 자식: 클래스 A 6개, 클래스 B 1개 (총 7개)\n"
         "   -> H(left) = -( 6/7*log2(6/7) + 1/7*log2(1/7) ) = 0.5917\n\n"
         "3. 오른쪽 자식: 클래스 A 1개, 클래스 B 2개 (총 3개)\n"
         "   -> H(right) = -( 1/3*log2(1/3) + 2/3*log2(2/3) ) = 0.9183\n\n"
         "4. 정보이득 계산:\n"
         "   IG = 0.8813 - ( 7/10 * 0.5917 + 3/10 * 0.9183 )\n"
         "      = 0.8813 - ( 0.4142 + 0.2755 ) = 0.8813 - 0.6897 = 0.1916",
         font_size=15, color=WHITE, font_name='Consolas')

# ============================================================
# SECTION 3: 8.3 분할 기준
# ============================================================
section_divider("분할 기준", "Splitting Criteria: Entropy, Gini, Variance", "8.3", ACCENT_GREEN)

# Slide 14: 엔트로피 (분할 기준)
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.3", "분할 기준 1: 엔트로피 (Entropy)", "ID3, C4.5 알고리즘의 기본 분할 기준")
add_shape(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(1.5), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(5.0), Inches(0.3),
         "수식", font_size=14, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(5.0), Inches(0.8),
         "Entropy(t) = - SUM[ p_i * log2(p_i) ]\n"
         "범위: [0, log2(C)],  이진분류: [0, 1]",
         font_size=17, color=WHITE, font_name='Consolas')
add_code_block(s, Inches(0.6), Inches(4.0), Inches(5.5), Inches(3.2), [
    "def entropy(labels):",
    '    """엔트로피를 계산하는 함수"""',
    "    if len(labels) == 0: return 0.0",
    "    classes, counts = np.unique(labels,",
    "                                return_counts=True)",
    "    probs = counts / len(labels)",
    "    ent = -np.sum(probs * np.log2(probs + 1e-10))",
    "    return ent",
    "",
    "# 순수 노드 [0,0,0,0,0]: 0.0000",
    "# 혼합 7:3  [0,..,0,1,1,1]: 0.8813",
    "# 최대 5:5  [0,..,0,1,..,1]: 1.0000",
], font_size=11)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(5.0),
         "엔트로피의 특성",
         ["정보이론(Information Theory)에 기반한 수학적으로 엄밀한 기준",
          "p = 0.5에서 최대값 1.0 (최대 불확실성)",
          "p = 0 또는 p = 1에서 최소값 0 (완전 순수)",
          "log2 연산 필요 -> 지니보다 계산 비용이 약간 높음",
          "",
          "Shannon (1948)의 정보이론:",
          "  '데이터를 설명하는 데 필요한 평균 비트 수'",
          "  -> 불확실성이 높을수록 더 많은 비트 필요"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 15: 지니 불순도
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.3", "분할 기준 2: 지니 불순도 (Gini Impurity)", "CART 알고리즘과 scikit-learn의 기본 기준")
add_shape(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(1.5), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(5.0), Inches(0.3),
         "수식", font_size=14, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(5.0), Inches(0.8),
         "Gini(t) = 1 - SUM[ p_i^2 ]\n"
         "이진 분류 범위: [0, 0.5]",
         font_size=17, color=WHITE, font_name='Consolas')
add_shape(s, Inches(0.6), Inches(4.0), Inches(5.5), Inches(1.8), CARD_BG, ACCENT_ORANGE, radius=True)
add_text(s, Inches(0.9), Inches(4.1), Inches(5.0), Inches(0.3),
         "계산 예시 (A: 7개, B: 3개)", font_size=14, color=ACCENT_ORANGE, bold=True)
add_text(s, Inches(0.9), Inches(4.5), Inches(5.0), Inches(1.0),
         "Gini = 1 - (0.7^2 + 0.3^2)\n"
         "     = 1 - (0.49 + 0.09) = 0.42",
         font_size=16, color=WHITE, font_name='Consolas')
add_code_block(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.5), [
    "def gini_impurity(labels):",
    '    """지니 불순도를 계산하는 함수"""',
    "    if len(labels) == 0: return 0.0",
    "    classes, counts = np.unique(labels,",
    "                                return_counts=True)",
    "    probs = counts / len(labels)",
    "    gini = 1 - np.sum(probs ** 2)",
    "    return gini",
], font_size=12)
add_card(s, Inches(6.5), Inches(5.0), Inches(6.0), Inches(2.0),
         "지니의 직관적 의미",
         ["한 노드에서 임의로 두 샘플을 뽑았을 때",
          "서로 다른 클래스일 확률",
          "로그 연산 불필요 -> 계산 효율적",
          "scikit-learn의 기본값 (criterion='gini')"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)

# Slide 16: 분산 감소 (회귀 트리)
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.3", "분할 기준 3: 분산 감소 (Variance Reduction)", "회귀 트리에서의 분할 기준 - MSE 감소")
add_shape(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.0), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(5.0), Inches(0.3),
         "MSE (Mean Squared Error) 기준", font_size=14, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(5.0), Inches(1.3),
         "MSE(t) = (1/N) * SUM[ (y_i - y_bar)^2 ]\n\n"
         "delta_MSE = MSE(parent)\n"
         "  - ( N_L/N * MSE(L) + N_R/N * MSE(R) )",
         font_size=16, color=WHITE, font_name='Consolas')
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.0),
         "회귀 트리의 예측",
         ["각 리프 노드의 예측값 = 해당 노드 샘플들의 평균값 y_bar",
          "= 구간별 상수 모델 (piecewise constant model)",
          "분할 기준: MSE 감소량이 가장 큰 분할 선택",
          "범위: [0, inf) - 연속값 예측에 사용"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_text(s, Inches(0.6), Inches(4.8), Inches(12), Inches(0.4),
         "CART (회귀 모드): DecisionTreeRegressor(criterion='squared_error')",
         font_size=16, color=ACCENT_ORANGE, bold=True)

# Slide 17: 세 기준 비교
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.3", "세 분할 기준의 비교", "Entropy vs Gini vs Variance Reduction")
add_table_slide(s,
    ["기준", "사용 알고리즘", "범위 (이진)", "계산 복잡도", "특징"],
    [["엔트로피", "ID3, C4.5", "[0, 1]", "O(C) + log", "정보이론 기반, 수학적 엄밀"],
     ["지니 불순도", "CART, sklearn", "[0, 0.5]", "O(C)", "로그 연산 불필요, 효율적"],
     ["분산 감소", "CART (회귀)", "[0, inf)", "O(N)", "연속값 예측에 사용"]],
    Inches(0.6), Inches(2.2), [2.0, 2.2, 1.8, 2.0, 3.5], row_height=0.55, font_size=14)
add_shape(s, Inches(0.6), Inches(4.5), Inches(12), Inches(2.5), CARD_BG, ACCENT_BLUE, radius=True)
add_text(s, Inches(0.9), Inches(4.6), Inches(11.4), Inches(0.3),
         "실질적 비교 결과", font_size=16, color=ACCENT_CYAN, bold=True)
add_bullet_list(s, Inches(0.9), Inches(5.0), Inches(11.4), Inches(1.8), [
    "엔트로피와 지니 모두 p=0.5에서 최대, p=0 또는 p=1에서 0",
    "두 기준의 분할 결과는 실질적으로 거의 유사 (약 2%의 경우에만 차이)",
    "지니가 계산이 더 빠르므로 scikit-learn에서 기본값으로 사용",
    "불순도 비교 그래프: Gini, Entropy, Classification Error 곡선이 유사한 형태",
], font_size=15, color=LIGHT_GRAY, spacing=Pt(8))

# ============================================================
# SECTION 4: 8.4 알고리즘 역사
# ============================================================
section_divider("알고리즘 역사", "ID3 -> CART -> C4.5: Evolution of Decision Trees", "8.4", ACCENT_ORANGE)

# Slide 19: ID3
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.4", "ID3 (Iterative Dichotomiser 3)", "J. Ross Quinlan, 1986 - Machine Learning 학술지")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.5),
         "핵심 특징",
         ["정보이득(Information Gain) 기반 속성 선택",
          "다중 분기(multi-way split) 허용",
          "  - 범주형 속성의 모든 값에 대해 분기",
          "하향식 재귀 분할(TDIDT) 방법론 정립",
          "범주형 속성만 처리 가능 (연속형 미지원)"],
         title_color=ACCENT_CYAN, border=ACCENT_BLUE)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.5),
         "한계점",
         ["카디널리티(고유 값 수)가 높은 속성을 부당하게 선호",
          "  -> 고유 값이 N개인 속성: 2^(N-1)-1개 분할 후보",
          "  -> 우연히 높은 정보이득을 얻을 확률이 높음",
          "가지치기(pruning) 전략 미흡",
          "결측값 처리 불가"],
         title_color=ACCENT_RED, border=ACCENT_RED)
add_shape(s, Inches(0.6), Inches(5.0), Inches(12), Inches(2.2), CARD_BG, ACCENT_ORANGE, radius=True)
add_text(s, Inches(0.9), Inches(5.1), Inches(11.4), Inches(0.3),
         "ID3 알고리즘 의사코드", font_size=14, color=ACCENT_ORANGE, bold=True)
add_text(s, Inches(0.9), Inches(5.5), Inches(11.4), Inches(1.5),
         "ID3(S, Attributes):\n"
         "  if S의 모든 샘플이 같은 클래스 c: return Leaf(c)\n"
         "  if Attributes 비어있음: return Leaf(최빈 클래스)\n"
         "  A* = argmax IG(S, A)   // 정보이득 최대 속성\n"
         "  for each v in Values(A*): 재귀 호출 ID3(S_v, Attrs - {A*})",
         font_size=13, color=LIGHT_GRAY, font_name='Consolas')

# Slide 20: CART
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.4", "CART (Classification and Regression Trees)", "Breiman, Friedman, Stone, Olshen - 1984")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(4.8),
         "핵심 특징",
         ["이진 분할(binary split) 전용:",
          "  - 항상 데이터를 정확히 두 부분집합으로 분할",
          "지니 불순도(Gini Impurity) 사용 (분류)",
          "MSE 사용 (회귀)",
          "비용-복잡도 가지치기(CCP):",
          "  - 체계적 사후 가지치기 방법론",
          "  - R_a(T) = R(T) + a * |T_leaf|",
          "대리 분할(Surrogate Split):",
          "  - 결측값 처리의 체계적 방법",
          "분류와 회귀를 동일 프레임워크에서 처리"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(4.8),
         "CART vs ID3 비교",
         ["[분할 방식] ID3: 다중 분기 / CART: 이진 분할만",
          "[분할 기준] ID3: 정보이득 / CART: 지니 불순도",
          "[회귀 지원] ID3: 불가 / CART: 가능 (MSE)",
          "[가지치기] ID3: 미흡 / CART: CCP (체계적)",
          "[결측값] ID3: 미지원 / CART: 대리 분할",
          "",
          "scikit-learn의 DecisionTreeClassifier와",
          "DecisionTreeRegressor는 CART 알고리즘을 구현",
          "",
          "통계학적 관점에서 의사결정나무를 엄밀하게 정립한",
          "역사적으로 중요한 연구"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 21: C4.5
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.4", "C4.5 - Quinlan, 1993", "IEEE ICDM '데이터 마이닝 10대 알고리즘' 투표 1위 (2006)")
add_card(s, Inches(0.6), Inches(2.2), Inches(12), Inches(1.8),
         "핵심 개선: 정보이득비율 (Gain Ratio) 도입",
         ["GainRatio(S, A) = IG(S, A) / SplitInfo(S, A)",
          "SplitInfo(S, A) = -SUM[ |S_v|/|S| * log2(|S_v|/|S|) ]",
          "=> 카디널리티 편향 해결: 고유 값이 많은 속성의 SplitInfo가 크므로 GainRatio가 작아짐"],
         title_color=ACCENT_CYAN, border=ACCENT_BLUE)
add_card(s, Inches(0.6), Inches(4.3), Inches(3.8), Inches(2.8),
         "연속형 속성 처리",
         ["이진 분할점(threshold) 탐색",
          "속성값을 정렬 후 인접 값의",
          "중간점을 후보로 검토",
          "=> ID3의 범주형 제한 극복"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(4.7), Inches(4.3), Inches(3.8), Inches(2.8),
         "오류 기반 가지치기 (EBP)",
         ["별도의 검증 데이터 없이",
          "비관적 오류 추정으로 가지치기",
          "각 리프의 오류를 비관적으로",
          "추정하여 가지치기 여부 결정"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)
add_card(s, Inches(8.8), Inches(4.3), Inches(3.8), Inches(2.8),
         "추가 기능",
         ["결측값의 확률적 처리:",
          "  결측 인스턴스를 확률적으로 분배",
          "트리-규칙 변환:",
          "  루트-리프 경로를 if-then 규칙으로"],
         title_color=ACCENT_PURPLE, border=ACCENT_PURPLE)

# Slide 22: 발전 타임라인
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.4", "의사결정나무 발전 타임라인", "1964년부터 현재까지의 알고리즘 진화")
add_table_slide(s,
    ["연도", "알고리즘/사건", "주요 기여", "저자"],
    [["1964", "AID", "최초의 자동 상호작용 탐지", "Morgan & Sonquist"],
     ["1980", "CHAID", "카이제곱 검정 기반 분할", "Kass"],
     ["1984", "CART", "지니 불순도, CCP, 대리 분할", "Breiman et al."],
     ["1986", "ID3", "정보이득, TDIDT 프레임워크", "Quinlan"],
     ["1993", "C4.5", "이득비율, EBP, 연속형 처리", "Quinlan"],
     ["2005", "TDIDT 서베이", "분할/가지치기 체계적 분류", "Rokach & Maimon"],
     ["2009", "GUIDE", "편향 없는 변수 선택", "Loh"]],
    Inches(0.6), Inches(2.2), [1.2, 2.5, 4.5, 3.0], row_height=0.5, font_size=13)

# ============================================================
# SECTION 5: 8.5 가지치기
# ============================================================
section_divider("가지치기 (Pruning)", "Pre-Pruning & Post-Pruning: Controlling Tree Complexity", "8.5", ACCENT_RED)

# Slide 24: 왜 가지치기가 필요한가
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.5", "왜 가지치기가 필요한가?", "가지치기 없이 완전히 성장 -> 노이즈까지 학습 -> 과적합")
add_shape(s, Inches(0.6), Inches(2.2), Inches(12), Inches(1.5), CARD_BG, ACCENT_RED, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(11.4), Inches(0.3),
         "과적합 예시", font_size=15, color=ACCENT_RED, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(11.4), Inches(0.8),
         "가지치기 없음:  Train=97.8%  Test=81.6%  -> 격차 16.2% (과적합!)\n"
         "max_depth=5:   Train=85.4%  Test=85.0%  -> 격차  0.4% (양호)",
         font_size=16, color=WHITE, font_name='Consolas')
add_card(s, Inches(0.6), Inches(4.0), Inches(5.5), Inches(3.0),
         "과적합의 원인",
         ["트리를 완전히 성장시키면 훈련 데이터의",
          "노이즈(noise)까지 학습",
          "리프 노드에 소수의 샘플만 남아",
          "통계적으로 신뢰할 수 없는 예측",
          "=> 새로운 데이터에 대한 일반화 성능 저하"],
         title_color=ACCENT_RED, border=ACCENT_RED)
add_card(s, Inches(6.5), Inches(4.0), Inches(6.0), Inches(3.0),
         "가지치기의 목적",
         ["불필요하게 복잡한 가지를 제거",
          "편향(bias)은 약간 증가하지만",
          "분산(variance)을 크게 감소시킴",
          "=> Bias-Variance Tradeoff의 최적점 탐색",
          "=> 일반화 성능(test accuracy) 향상"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 25: 사전 가지치기
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.5", "사전 가지치기 (Pre-Pruning)", "트리 성장 과정에서 조건을 두어 조기 중단")
add_table_slide(s,
    ["파라미터", "설명", "기본값", "효과"],
    [["max_depth", "트리의 최대 깊이", "None", "값이 작을수록 단순한 트리"],
     ["min_samples_split", "분할 최소 샘플 수", "2", "값이 클수록 분할 억제"],
     ["min_samples_leaf", "리프 최소 샘플 수", "1", "값이 클수록 작은 리프 제거"],
     ["max_features", "고려 최대 특성 수", "None", "랜덤성 부여"]],
    Inches(0.6), Inches(2.2), [2.5, 3.5, 1.5, 4.0], row_height=0.5, font_size=14)
add_card(s, Inches(0.6), Inches(4.8), Inches(5.5), Inches(2.2),
         "장점",
         ["구현이 간단하고 계산 비용이 적다",
          "scikit-learn에서 파라미터 하나로 제어",
          "대규모 데이터에서도 빠르게 적용 가능"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(6.5), Inches(4.8), Inches(6.0), Inches(2.2),
         "단점",
         ["최적의 중단 시점을 사전에 알기 어렵다",
          "조기에 중단하면 이후의 유용한 분할을 놓칠 수 있음",
          "  (예: 현재 분할은 효과 없지만 다음 분할이 유효한 경우)",
          "=> 사후 가지치기가 더 체계적인 대안"],
         title_color=ACCENT_RED, border=ACCENT_RED)

# Slide 26: CCP 개요
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.5", "비용-복잡도 가지치기 (CCP) - 개요", "CART에서 제안한 가장 널리 사용되는 사후 가지치기")
add_shape(s, Inches(0.6), Inches(2.2), Inches(12), Inches(2.0), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(11.4), Inches(0.4),
         "비용-복잡도 함수 (Cost-Complexity Function)", font_size=16, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.8), Inches(11.4), Inches(1.2),
         "R_alpha(T) = R(T) + alpha * |T_leaf|\n\n"
         "R(T)      : 트리 T의 오분류 비율 (또는 총 불순도)\n"
         "|T_leaf|  : 트리 T의 리프 노드 수\n"
         "alpha     : 복잡도 파라미터 (alpha >= 0)",
         font_size=16, color=WHITE, font_name='Consolas')
add_card(s, Inches(0.6), Inches(4.5), Inches(5.5), Inches(2.7),
         "alpha의 역할",
         ["alpha = 0: 완전한 트리 (가지치기 없음)",
          "alpha 증가: 리프 노드 수에 대한 페널티 증가",
          "  -> 더 공격적으로 가지치기",
          "alpha -> inf: 루트 노드만 남은 최단순 트리",
          "",
          "목표: 최적의 alpha를 교차검증으로 선택"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)
add_card(s, Inches(6.5), Inches(4.5), Inches(6.0), Inches(2.7),
         "직관적 이해",
         ["R(T): 트리의 '정확도' (오류를 줄이고 싶음)",
          "|T_leaf|: 트리의 '복잡도' (단순하게 만들고 싶음)",
          "alpha: 정확도와 복잡도 사이의 균형 조절",
          "",
          "= 정규화(Regularization)의 원리와 동일!",
          "  (LASSO의 lambda와 같은 역할)"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 27: CCP 알고리즘 절차
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.5", "CCP 알고리즘 절차", "완전 트리에서 출발하여 점진적으로 가지치기")
add_shape(s, Inches(0.6), Inches(2.2), Inches(12), Inches(5.0), CARD_BG, ACCENT_BLUE, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(11.4), Inches(4.8),
         "1. 완전히 성장한 트리 T_max에서 시작\n\n"
         "2. 각 내부 노드 t에 대해, 하위 트리 T_t를 단일 리프로 대체했을 때의\n"
         "   유효 alpha 계산:\n"
         "   alpha_eff(t) = [ R(t) - R(T_t) ] / [ |T_t_leaf| - 1 ]\n\n"
         "   R(t): 노드 t를 리프로 만들었을 때의 오분류 비율\n"
         "   R(T_t): 노드 t의 하위 트리 전체의 오분류 비율\n"
         "   |T_t_leaf|: 하위 트리의 리프 수\n\n"
         "3. 가장 작은 alpha_eff를 가진 노드의 하위 트리를 가지치기\n"
         "   (= 가지치기해도 오류 증가가 가장 적은 노드)\n\n"
         "4. 2-3단계를 반복:\n"
         "   T_max ⊃ T_1 ⊃ T_2 ⊃ ... ⊃ T_root\n\n"
         "5. 교차검증(cross-validation)으로 최적의 alpha 선택",
         font_size=15, color=WHITE, font_name='Consolas')

# Slide 28: 1-SE Rule
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.5", "1-SE Rule (One Standard Error Rule)", "오컴의 면도날 원칙: 비슷한 성능이면 가장 단순한 모델")
add_shape(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.0), CARD_BG, ACCENT_CYAN, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(5.0), Inches(0.3),
         "1-SE Rule 공식", font_size=14, color=ACCENT_CYAN, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(5.0), Inches(1.3),
         "alpha_1SE = max{ alpha |\n"
         "  CV(alpha) >= CV(alpha*) - SE(alpha*) }\n\n"
         "alpha*: CV 점수 최대인 alpha\n"
         "SE: 표준오차 (standard error)",
         font_size=15, color=WHITE, font_name='Consolas')
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.0),
         "원칙",
         ["CV 정확도가 (최적 정확도 - 1*표준오차) 이상인",
          "범위에서 가장 큰 alpha(가장 단순한 트리) 선택",
          "",
          "= '비슷한 성능 범위 내에서 가장 단순한 모델'"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_code_block(s, Inches(0.6), Inches(4.5), Inches(12), Inches(2.7), [
    "from sklearn.tree import DecisionTreeClassifier",
    "",
    "# CCP 경로 계산",
    "full_tree = DecisionTreeClassifier(random_state=42)",
    "full_tree.fit(X_train, y_train)",
    "path = full_tree.cost_complexity_pruning_path(X_train, y_train)",
    "ccp_alphas = path.ccp_alphas",
    "",
    "# 1-SE Rule 적용",
    "one_se_threshold = best_cv_mean - best_cv_std",
    "one_se_candidates = alphas[cv_means >= one_se_threshold]",
    "alpha_1se = one_se_candidates[-1]  # 가장 큰 alpha = 가장 단순한 트리",
], font_size=12)

# ============================================================
# SECTION 6: 8.6 과적합과 불안정성
# ============================================================
section_divider("과적합과 불안정성", "Overfitting & High Variance Problem", "8.6", ACCENT_PURPLE)

# Slide 30: 과적합
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.6", "과적합 (Overfitting)", "훈련 데이터에 지나치게 맞추어 일반화 성능이 저하되는 현상")
add_shape(s, Inches(0.6), Inches(2.2), Inches(12), Inches(2.0), CARD_BG, ACCENT_RED, radius=True)
add_text(s, Inches(0.9), Inches(2.3), Inches(11.4), Inches(0.3),
         "깊이별 성능 변화", font_size=15, color=ACCENT_RED, bold=True)
add_text(s, Inches(0.9), Inches(2.7), Inches(11.4), Inches(1.3),
         "max_depth=1:    Train=91.2%  Test=90.4%  격차=0.8%  (과소적합)\n"
         "max_depth=3:    Train=96.2%  Test=93.4%  격차=2.8%  (양호)\n"
         "max_depth=5:    Train=98.8%  Test=93.4%  격차=5.4%  (경계)\n"
         "max_depth=None: Train=100%   Test=91.2%  격차=8.8%  (과적합!)",
         font_size=15, color=WHITE, font_name='Consolas')
add_card(s, Inches(0.6), Inches(4.5), Inches(12), Inches(2.7),
         "과적합 해결 전략",
         ["1. 사전 가지치기: max_depth, min_samples_split, min_samples_leaf 등",
          "2. 사후 가지치기: CCP(비용-복잡도 가지치기) + 교차검증",
          "3. 앙상블 기법: 배깅, 랜덤 포레스트, 그래디언트 부스팅",
          "4. 데이터 관점: 더 많은 훈련 데이터 수집, 노이즈 제거",
          "",
          "=> 가지치기 없이 트리를 완전히 성장시키면 과적합 가능성이 매우 높다"],
         title_color=ACCENT_CYAN, border=ACCENT_BLUE)

# Slide 31: 높은 분산 문제
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.6", "높은 분산 문제 (High Variance)", "의사결정나무의 가장 심각한 단점: 불안정성")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(3.0),
         "원인 분석",
         ["1. 탐욕적(greedy) 알고리즘:",
          "   루트 노드 분할이 달라지면 전체 트리 변경",
          "2. 계층적(hierarchical) 구조:",
          "   상위 노드의 변화가 모든 하위 노드에 영향",
          "3. 데이터 민감성:",
          "   소수의 샘플 변화가 분할 결정을 바꿈"],
         title_color=ACCENT_RED, border=ACCENT_RED)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(3.0),
         "실험적 확인",
         ["같은 데이터에서 부트스트랩 샘플만 달라도",
          "트리 구조가 크게 변한다:",
          "  트리 1: petal_width 루트",
          "  트리 2: petal_length 루트",
          "  트리 3: sepal_length 루트",
          "",
          "=> 특성 중요도도 트리마다 크게 변동"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)
add_shape(s, Inches(0.6), Inches(5.5), Inches(12), Inches(1.7), CARD_BG, ACCENT_GREEN, radius=True)
add_text(s, Inches(0.9), Inches(5.6), Inches(11.4), Inches(0.3),
         "Bias-Variance Tradeoff", font_size=15, color=ACCENT_GREEN, bold=True)
add_text(s, Inches(0.9), Inches(6.0), Inches(11.4), Inches(1.0),
         "단일 트리: 낮은 편향(bias) + 높은 분산(variance)\n"
         "=> 앙상블: 분산을 줄이면서 편향을 유지하여 전체 오차를 감소시킴",
         font_size=16, color=WHITE)

# Slide 32: 앙상블 동기
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.6", "앙상블 동기", "높은 분산 문제를 해결하기 위한 접근법")
add_card(s, Inches(0.6), Inches(2.2), Inches(3.6), Inches(3.5),
         "배깅 (Bagging)",
         ["Bootstrap Aggregating",
          "부트스트랩 샘플에서",
          "여러 트리를 독립적으로 학습",
          "다수결 투표로 최종 예측",
          "",
          "분산 감소: Var/n 효과"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(4.5), Inches(2.2), Inches(3.8), Inches(3.5),
         "랜덤 포레스트 (RF)",
         ["배깅 + 특성 랜덤 선택",
          "각 분할 시 sqrt(d) 특성만 고려",
          "트리 간 상관관계 감소",
          "=> 더 효과적인 분산 감소",
          "",
          "Breiman (2001)"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(8.6), Inches(2.2), Inches(4.0), Inches(3.5),
         "그래디언트 부스팅 (GB)",
         ["잔차를 순차적으로 학습하는",
          "약한 트리(shallow tree)들의 결합",
          "각 트리는 이전 트리의 오류를 수정",
          "XGBoost, LightGBM, CatBoost",
          "",
          "Friedman (2001)"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)
add_text(s, Inches(0.6), Inches(6.2), Inches(12), Inches(0.5),
         "=> 9장에서 앙상블 기법을 본격적으로 학습합니다",
         font_size=18, color=ACCENT_YELLOW, bold=True)

# ============================================================
# SECTION 7: 8.7 변수 선택 편향
# ============================================================
section_divider("변수 선택 편향", "Variable Selection Bias in Decision Trees", "8.7", ACCENT_YELLOW)

# Slide 34: Loh(2011) 편향 분석
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.7", "변수 선택 편향 (Variable Selection Bias)", "Loh (2011) - WIREs Data Mining and Knowledge Discovery")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.5),
         "편향의 정의",
         ["예측력이 동일한 두 변수가 있을 때,",
          "알고리즘이 특정 유형의 변수를",
          "부당하게 선호하는 현상",
          "",
          "=> 모델의 공정성과 신뢰성에 영향"],
         title_color=ACCENT_RED, border=ACCENT_RED)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.5),
         "편향의 원인",
         ["1. 카디널리티 편향:",
          "   고유 값이 많은 속성 -> 더 많은 분할 후보",
          "   -> 우연히 높은 정보이득 확률 증가",
          "   예: '주민번호' -> 2^(N-1)-1개 분할 후보",
          "2. 결측값 편향:",
          "   결측값 비율이 높은 속성이 선호될 수 있음"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)

# Slide 35: 해결책
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.7", "편향 해결책", "이득비율, 통계적 검정, 순열 중요도")
add_table_slide(s,
    ["방법", "설명", "예시 알고리즘"],
    [["이득비율 (Gain Ratio)", "정보이득을 SplitInfo로 나누어 정규화", "C4.5"],
     ["통계적 검정", "변수 선택에 카이제곱 검정 등 사용", "CHAID, GUIDE"],
     ["변수 선택/분할점 분리", "두 단계를 독립적으로 수행", "GUIDE (Loh, 2009)"],
     ["순열 중요도", "변수를 무작위 섞어 성능 감소 측정", "랜덤 포레스트"]],
    Inches(0.6), Inches(2.2), [3.0, 5.0, 3.0], row_height=0.5, font_size=14)
add_shape(s, Inches(0.6), Inches(4.8), Inches(12), Inches(2.3), CARD_BG, ACCENT_ORANGE, radius=True)
add_text(s, Inches(0.9), Inches(4.9), Inches(11.4), Inches(0.3),
         "실무적 시사점", font_size=15, color=ACCENT_ORANGE, bold=True)
add_bullet_list(s, Inches(0.9), Inches(5.3), Inches(11.4), Inches(1.5), [
    "scikit-learn의 feature_importances_는 지니 불순도 감소 기반 -> 카디널리티 편향 존재",
    "편향 없는 중요도 평가: permutation_importance()를 함께 사용 권장",
    "고카디널리티 범주형 변수 (예: 우편번호, ID) 사용 시 주의 필요",
    "GUIDE 알고리즘: 변수 선택과 분할점 결정을 분리하여 편향 제거",
], font_size=14, color=LIGHT_GRAY, spacing=Pt(6))

# ============================================================
# SECTION 8: 8.8 보충
# ============================================================
section_divider("보충", "Surrogate Splits, Regression Tree, Visualization", "8.8", ACCENT_CYAN)

# Slide 37: 대리 분할
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.8", "결측치 처리: 대리 분할 (Surrogate Splits)", "CART에서 제안한 결측값 처리의 체계적 방법")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(3.5),
         "원리",
         ["1. 노드에서 최적 분할 속성 A*와 임계값 theta* 결정",
          "2. 다른 모든 속성 A_j에 대해,",
          "   A*의 분할과 가장 높은 일치율을 보이는 분할을 탐색",
          "3. A*가 결측인 샘플은 첫 번째 대리 분할로 처리",
          "4. 그것도 결측이면 두 번째 대리 분할 사용",
          "",
          "핵심: 최적 분할과 가장 유사한 결과를 내는",
          "다른 속성을 대리(surrogate)로 사용"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(3.5),
         "실무 참고사항",
         ["scikit-learn: 대리 분할 미지원",
          "  -> 사전에 결측치를 처리해야 함",
          "  -> SimpleImputer, KNNImputer 등 사용",
          "",
          "XGBoost: 결측값 직접 처리 가능",
          "  -> 결측 샘플을 좌/우 분기에 각각 보내어",
          "     더 나은 쪽을 자동 선택",
          "LightGBM: 마찬가지로 결측값 직접 처리",
          "",
          "=> 실무에서는 XGBoost/LightGBM이",
          "   결측값 처리에 더 편리"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 38: 회귀 나무
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.8", "회귀 나무 (Regression Tree)", "연속값 예측: 리프 노드의 예측값 = 해당 노드 샘플들의 평균")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.0),
         "구간별 상수 모델 (Piecewise Constant)",
         ["각 리프 노드의 예측값 = 해당 노드 샘플의 평균값",
          "입력 공간을 직사각형(axis-aligned) 영역으로 분할",
          "각 영역에서 상수값(평균)으로 예측",
          "MSE 감소를 분할 기준으로 사용"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_code_block(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.0), [
    "from sklearn.tree import DecisionTreeRegressor",
    "",
    "reg_tree = DecisionTreeRegressor(",
    "    max_depth=3, random_state=42)",
    "reg_tree.fit(X_train, y_train)",
    "# 각 리프: 해당 구간의 평균값을 예측",
], font_size=12)
add_card(s, Inches(0.6), Inches(4.5), Inches(12), Inches(2.5),
         "모델 트리 (Model Tree) - 확장",
         ["각 리프에서 상수 대신 선형 회귀 모델을 적합",
          "=> 표현력 향상: 각 영역에서 선형 함수로 예측",
          "Quinlan의 M5 알고리즘이 대표적",
          "",
          "일반 회귀 트리: y = c (상수)  vs  모델 트리: y = w0 + w1*x1 + w2*x2 + ...",
          "=> 연속적인 예측 함수를 더 잘 근사"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# Slide 39: 시각화
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.8", "트리 시각화 (Visualization)", "scikit-learn의 두 가지 트리 시각화 방법")
add_code_block(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.5), [
    "# 방법 1: 그래픽 시각화",
    "from sklearn.tree import plot_tree",
    "",
    "plt.figure(figsize=(25, 12))",
    "plot_tree(model,",
    "    feature_names=feature_names,",
    "    class_names=class_names,",
    "    filled=True,    # 색상으로 클래스 표시",
    "    rounded=True,   # 둥근 모서리",
    "    fontsize=10)",
    "plt.show()",
], font_size=12)
add_code_block(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.5), [
    "# 방법 2: 텍스트 규칙 출력",
    "from sklearn.tree import export_text",
    "",
    "rules = export_text(model,",
    "    feature_names=list(feature_names))",
    "print(rules)",
    "",
    "# |--- petal width <= 0.80",
    "# |   |--- class: setosa",
    "# |--- petal width >  0.80",
    "# |   |--- petal length <= 4.95 ...",
], font_size=12)
add_card(s, Inches(0.6), Inches(5.0), Inches(12), Inches(2.0),
         "규칙 추출 (Rule Extraction) - C4.5",
         ["트리의 각 루트-리프 경로를 if-then 규칙으로 변환",
          "예: IF worst_radius <= 16.80 AND worst_concave_points <= 0.14 THEN benign [신뢰도: 97.2%]",
          "각 규칙을 독립적으로 가지치기 -> 더 간결한 분류기",
          "decision_path()로 개별 샘플의 결정 경로 추적 가능"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)

# ============================================================
# SECTION 9: 8.9 논문 리뷰
# ============================================================
section_divider("논문 리뷰", "Rokach & Maimon (2005) - TDIDT Framework", "8.9", ACCENT_PURPLE)

# Slide 41: TDIDT 프레임워크
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.9", "TDIDT 프레임워크", "Rokach & Maimon (2005) - IEEE Trans. SMC, Vol.35, No.4")
add_card(s, Inches(0.6), Inches(2.2), Inches(12), Inches(1.5),
         "논문의 핵심: 트리 유도를 독립적 설계 결정(Design Choice)으로 분해",
         ["하향식 의사결정나무 유도(Top-Down Induction of Decision Trees) 알고리즘에 대한 포괄적 분류 체계",
          "각 설계 결정은 독립적으로 선택 가능하며, 조합에 따라 다양한 알고리즘 구성 가능"],
         title_color=ACCENT_PURPLE, border=ACCENT_PURPLE)
add_table_slide(s,
    ["설계 결정", "선택지", "대표 알고리즘"],
    [["분할 기준", "정보이득, 이득비율, 지니, 카이제곱, 분산감소", "ID3, C4.5, CART, CHAID"],
     ["정지 기준", "max_depth, min_samples, 순수도 임계값", "모든 알고리즘"],
     ["가지치기", "사전(pre), CCP, EBP, MEP, MDL", "CART, C4.5"],
     ["결측값 처리", "대리 분할, 확률적 분배, 삭제", "CART, C4.5"],
     ["분할 유형", "축 정렬, 경사(oblique), 다변량", "CART, OC1, CART-LC"]],
    Inches(0.6), Inches(4.0), [2.5, 5.5, 3.5], row_height=0.42, font_size=12)

# Slide 42: 논문의 주요 기여
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.9", "논문의 주요 기여", "불순도 vs 거리 기반 분할, 가지치기 비교, 다변량 분할")
add_card(s, Inches(0.6), Inches(2.2), Inches(3.6), Inches(4.5),
         "불순도 vs 거리 기반",
         ["불순도 함수:",
          "  엔트로피, 지니 불순도",
          "  -> 노드의 순수도를 측정",
          "",
          "거리 기반 기준:",
          "  카이제곱, 콜모고로프-스미르노프",
          "  -> 분할 전후의 분포 차이 측정",
          "",
          "이론적 차이를 명확히 분석"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(4.5), Inches(2.2), Inches(3.8), Inches(4.5),
         "가지치기 비교",
         ["CCP (CART):",
          "  교차검증 기반 -> 안정적",
          "  but 계산 비용이 높음",
          "",
          "EBP (C4.5):",
          "  효율적이나 비관적 추정의",
          "  정확도에 의존",
          "",
          "둘 다 사후 가지치기 방식"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(8.6), Inches(2.2), Inches(4.0), Inches(4.5),
         "다변량 분할",
         ["축 정렬 분할 (axis-aligned):",
          "  x_i <= theta (한 변수만 사용)",
          "",
          "경사 분할 (oblique):",
          "  a1*x1 + a2*x2 + ... <= theta",
          "  -> 표현력이 높지만",
          "  -> 해석가능성이 저하됨",
          "",
          "=> 표현력 vs 해석가능성",
          "   트레이드오프"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)

# ============================================================
# SECTION 10: 8.10 실습 - 의사결정나무 스크래치
# ============================================================
section_divider("실습: 의사결정나무 스크래치", "01_decision_tree_scratch.py", "8.10", ACCENT_GREEN)

# Slide 44: 실습 개요
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.10", "실습 1: 의사결정나무 스크래치 구현", "라이브러리 없이 처음부터 구현하여 내부 동작 원리 이해")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(5.0),
         "구현 내용",
         ["1. 불순도 측정 함수 구현",
          "   - gini_impurity(labels)",
          "   - entropy(labels)",
          "   - information_gain(parent, left, right)",
          "",
          "2. DecisionNode 클래스",
          "   - feature_index, threshold",
          "   - left, right, value",
          "",
          "3. DecisionTreeFromScratch 클래스",
          "   - fit(): 재귀적 트리 구축",
          "   - predict(): 트리 탐색 예측",
          "   - print_tree(): 텍스트 출력",
          "",
          "4. sklearn DecisionTreeClassifier와 비교"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(5.0),
         "핵심 학습 포인트",
         ["데이터셋: Iris (sklearn 내장, 150개, 4특성, 3클래스)",
          "",
          "CART 알고리즘 기반 구현:",
          "  - 이진 분할(binary split) 사용",
          "  - 지니 불순도 또는 엔트로피 기준 지원",
          "",
          "정지 조건(Stopping Criteria):",
          "  - 모든 샘플이 같은 클래스 (순수 노드)",
          "  - 최대 깊이에 도달",
          "  - 최소 분할 샘플 수 미달",
          "",
          "특성 중요도 계산:",
          "  - 가중 불순도 감소량 누적",
          "  - 정규화하여 합이 1이 되도록"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)

# Slide 45: 불순도 함수 구현
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.10", "불순도 함수 구현", "gini_impurity, entropy, information_gain")
add_code_block(s, Inches(0.6), Inches(2.2), Inches(5.8), Inches(4.8), [
    "def gini_impurity(labels):",
    '    """Gini(t) = 1 - SUM(p_i^2)"""',
    "    if len(labels) == 0: return 0.0",
    "    counter = Counter(labels)",
    "    total = len(labels)",
    "    probs = [c/total for c in counter.values()]",
    "    return 1.0 - sum(p**2 for p in probs)",
    "",
    "def entropy(labels):",
    '    """H(t) = -SUM(p_i * log2(p_i))"""',
    "    if len(labels) == 0: return 0.0",
    "    counter = Counter(labels)",
    "    total = len(labels)",
    "    ent = 0.0",
    "    for count in counter.values():",
    "        p = count / total",
    "        if p > 0:",
    "            ent -= p * np.log2(p)",
    "    return ent",
], font_size=11)
add_code_block(s, Inches(6.8), Inches(2.2), Inches(5.8), Inches(4.8), [
    "def information_gain(parent, left, right,",
    "                     criterion='gini'):",
    '    """IG = parent - weighted child impurity"""',
    "    fn = gini_impurity if criterion=='gini'",
    "         else entropy",
    "    parent_imp = fn(parent)",
    "    n = len(parent)",
    "    n_l, n_r = len(left), len(right)",
    "    if n_l == 0 or n_r == 0: return 0.0",
    "    child_imp = (",
    "        (n_l/n) * fn(left) +",
    "        (n_r/n) * fn(right)",
    "    )",
    "    return parent_imp - child_imp",
    "",
    "# 검증 예시:",
    "# 순수 노드:     Gini=0.0000",
    "# 혼합 노드 7:3: Gini=0.4200",
    "# 최대 불순 5:5: Gini=0.5000",
], font_size=11)

# Slide 46: 재귀적 트리 구축
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.10", "재귀적 트리 구축 (_build_tree)", "핵심 알고리즘: 최적 분할 탐색 + 재귀 호출")
add_code_block(s, Inches(0.6), Inches(2.2), Inches(12), Inches(5.0), [
    "def _build_tree(self, X, y, depth):",
    "    n_samples, n_classes = len(y), len(set(y))",
    "    current_impurity = impurity_fn(y)",
    "",
    "    # === 정지 조건 확인 ===",
    "    if n_classes == 1 or (max_depth and depth >= max_depth) or n_samples < min_samples_split:",
    "        return DecisionNode(value=Counter(y).most_common(1)[0][0])  # 리프 노드",
    "",
    "    # === 최적 분할 탐색 (전수 탐색) ===",
    "    best_gain = -1",
    "    for feature_idx in range(n_features):           # 모든 특성에 대해",
    "        thresholds = np.unique(X[:, feature_idx])   # 모든 고유값을 후보로",
    "        for threshold in thresholds:                 # 각 임계값에 대해",
    "            left_mask = X[:, feature_idx] <= threshold",
    "            if sum(left_mask) < min_samples_leaf or sum(~left_mask) < min_samples_leaf:",
    "                continue",
    "            gain = information_gain(y, y[left_mask], y[~left_mask], criterion)",
    "            if gain > best_gain:  best_gain, best_feature, best_threshold = gain, feature_idx, threshold",
    "",
    "    # === 재귀적으로 자식 노드 구축 ===",
    "    left_child  = self._build_tree(X[best_left], y[best_left], depth + 1)",
    "    right_child = self._build_tree(X[best_right], y[best_right], depth + 1)",
    "    return DecisionNode(feature_index=best_feature, threshold=best_threshold,",
    "                        left=left_child, right=right_child, info_gain=best_gain)",
], font_size=11)

# Slide 47: 예측과 비교
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.10", "예측 및 sklearn과의 비교 결과", "Scratch 구현 vs sklearn DecisionTreeClassifier")
add_code_block(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.0), [
    "def predict(self, X):",
    "    return np.array([self._predict_single(x, self.root) for x in X])",
    "",
    "def _predict_single(self, x, node):",
    "    if node.value is not None: return node.value",
    "    if x[node.feature_index] <= node.threshold:",
    "        return self._predict_single(x, node.left)",
    "    else:",
    "        return self._predict_single(x, node.right)",
], font_size=12)
add_table_slide(s,
    ["모델", "Train Acc", "Test Acc"],
    [["Scratch (Gini)", "~1.0000", "~0.9556"],
     ["sklearn (Gini)", "~1.0000", "~0.9556"],
     ["Scratch (Entropy)", "-", "~0.9556"],
     ["sklearn (Entropy)", "-", "~0.9556"]],
    Inches(6.5), Inches(2.2), [2.5, 1.8, 1.8], row_height=0.45, font_size=14)
add_card(s, Inches(0.6), Inches(4.8), Inches(12), Inches(2.3),
         "비교 결과",
         ["Scratch 구현과 sklearn의 성능이 거의 동일 -> 알고리즘 구현의 정확성 검증",
          "특성 중요도도 유사한 패턴: petal_width, petal_length가 가장 중요",
          "sklearn은 C/Cython으로 최적화되어 대규모 데이터에서 훨씬 빠름",
          "학습 목적으로는 Scratch 구현이 내부 동작 이해에 매우 효과적"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)

# ============================================================
# SECTION 11: 8.11 실습 - CART 가지치기
# ============================================================
section_divider("실습: CART 가지치기", "02_cart_pruning.py", "8.11", ACCENT_ORANGE)

# Slide 49: 가지치기 실습 개요
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.11", "실습 2: CART 가지치기", "비용-복잡도 가지치기(CCP)의 원리를 실습하고 최적 alpha 선택")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(5.0),
         "실습 내용",
         ["데이터셋: Breast Cancer (sklearn, 569개, 30특성, 2클래스)",
          "",
          "1. 완전 트리 성장 (Full Tree Growth)",
          "   - 가지치기 없이 완전히 성장",
          "   - 과적합 확인: Train ~100% vs Test ~93%",
          "",
          "2. CCP 경로(cost_complexity_pruning_path) 계산",
          "   - 가능한 alpha 값들과 총 불순도 추출",
          "",
          "3. alpha별 트리 학습 및 성능 변화 관찰",
          "   - Train/Test 정확도, 리프 수, 깊이 변화",
          "",
          "4. 5-폴드 교차검증으로 최적 alpha 선택",
          "5. 1-SE Rule 적용",
          "6. 가지치기 전후 트리 시각화 비교"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(5.0),
         "핵심 코드",
         ["# CCP 경로 계산",
          "full_tree = DecisionTreeClassifier(random_state=42)",
          "full_tree.fit(X_train, y_train)",
          "path = full_tree.cost_complexity_pruning_path(",
          "    X_train, y_train)",
          "ccp_alphas = path.ccp_alphas",
          "impurities = path.impurities",
          "",
          "# 각 alpha에 대해 트리 학습",
          "for alpha in ccp_alphas:",
          "    tree = DecisionTreeClassifier(",
          "        ccp_alpha=alpha, random_state=42)",
          "    tree.fit(X_train, y_train)",
          "",
          "# 교차검증으로 최적 alpha 선택",
          "scores = cross_val_score(tree, X_train,",
          "    y_train, cv=5, scoring='accuracy')"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)

# Slide 50: CCP 결과 분석
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.11", "CCP 결과 분석", "alpha 증가에 따른 트리 복잡도와 성능 변화")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.0),
         "alpha에 따른 변화",
         ["alpha 증가 -> 리프 노드 수 감소 (트리 단순화)",
          "alpha 증가 -> 트리 깊이 감소",
          "Train 정확도: alpha 증가시 꾸준히 감소",
          "Test 정확도: 처음에 증가 후 감소 (U자형 역전)"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.0),
         "교차검증 + 1-SE Rule",
         ["최적 alpha: CV 정확도가 최대인 지점",
          "1-SE alpha: 최적 - 1SE 이상에서 가장 큰 alpha",
          "=> 1-SE Rule이 더 단순한 트리를 선택",
          "=> Occam's Razor 원칙 적용"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_table_slide(s,
    ["모델", "깊이", "리프 수", "Train", "Test", "격차"],
    [["완전 트리 (alpha=0)", "~7", "~17", "1.0000", "~0.9298", "~0.07"],
     ["최적 alpha", "~4", "~8", "~0.97", "~0.9532", "~0.02"],
     ["1-SE alpha", "~3", "~5", "~0.96", "~0.9474", "~0.01"]],
    Inches(0.6), Inches(4.8), [3.0, 1.0, 1.2, 1.5, 1.5, 1.5], row_height=0.5, font_size=14)
add_text(s, Inches(0.6), Inches(6.5), Inches(12), Inches(0.5),
         "=> 가지치기를 통해 과적합을 효과적으로 제어하면서 테스트 성능이 향상됨",
         font_size=16, color=ACCENT_YELLOW, bold=True)

# ============================================================
# SECTION 12: 8.12 실습 - 트리 앙상블 기초
# ============================================================
section_divider("실습: 트리 앙상블 기초", "03_tree_ensemble_basics.py", "8.12", ACCENT_BLUE)

# Slide 52: 앙상블 실습 개요
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.12", "실습 3: 트리 앙상블 기초", "단일 트리의 불안정성 확인과 다수결 투표의 분산 감소 효과")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(5.0),
         "실습 내용",
         ["1. 부트스트랩 샘플에서 10개 독립 트리 학습",
          "   - 같은 데이터, 다른 부트스트랩 샘플",
          "   - 트리 구조의 불안정성 확인",
          "",
          "2. 예측 분산 분석",
          "   - 각 샘플별 10개 트리의 예측 일치도",
          "   - 완전 일치 vs 낮은 일치 비율",
          "",
          "3. 다수결 투표 앙상블",
          "   - 10개 트리의 다수결 vs 개별 트리 성능 비교",
          "",
          "4. 특성 중요도의 불안정성 분석",
          "   - 각 트리마다 중요도가 크게 변동",
          "",
          "5. 앙상블 크기에 따른 성능 안정화",
          "   - 1개 -> 100개 트리로 성능 수렴 관찰"],
         title_color=ACCENT_BLUE, border=ACCENT_BLUE)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(5.0),
         "핵심 코드: 부트스트랩 + 다수결",
         ["# 부트스트랩 샘플에서 트리 학습",
          "for i in range(n_trees):",
          "    bootstrap_idx = np.random.choice(",
          "        n_samples, size=n_samples, replace=True)",
          "    X_boot = X_train[bootstrap_idx]",
          "    y_boot = y_train[bootstrap_idx]",
          "    tree = DecisionTreeClassifier()",
          "    tree.fit(X_boot, y_boot)",
          "",
          "# 다수결 투표",
          "for j in range(len(y_test)):",
          "    votes = [tree.predict(X_test[j:j+1])[0]",
          "             for tree in trees]",
          "    majority_vote = Counter(votes)",
          "                   .most_common(1)[0][0]",
          "",
          "# 고유 샘플 비율 ~63.2% (부트스트랩 이론)"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)

# Slide 53: 앙상블 결과
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.12", "앙상블 실험 결과", "다수결 투표가 개별 트리보다 안정적이고 정확하다")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.5),
         "성능 비교",
         ["개별 트리 Test Accuracy: 평균 ~0.93, 표준편차 ~0.03",
          "10개 트리 다수결 앙상블: ~0.96",
          "=> 앙상블이 평균 대비 +3% 개선",
          "",
          "앙상블 크기 증가 효과:",
          "  1개 -> 10개 -> 50개 -> 100개: 점차 수렴"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.5),
         "핵심 발견",
         ["1. 같은 데이터에서 부트스트랩 샘플만 달라도",
          "   트리 구조가 크게 변한다 (High Variance)",
          "2. 특성 중요도도 트리마다 크게 변동",
          "3. 여러 트리 결합 -> 오류 상쇄 -> 분산 감소",
          "4. 이것이 랜덤 포레스트의 n_estimators 의미"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)
add_card(s, Inches(0.6), Inches(5.0), Inches(12), Inches(2.0),
         "2D 결정 경계 비교",
         ["make_moons 데이터에서 5개 부트스트랩 트리 vs 20개 앙상블 비교",
          "개별 트리: 결정 경계가 불안정하고 복잡하며 과적합 경향",
          "앙상블: 결정 경계가 부드럽고 안정적이며 일반화 성능 우수",
          "=> 배깅(Bagging)의 핵심 원리를 시각적으로 확인"],
         title_color=ACCENT_CYAN, border=ACCENT_BLUE)

# ============================================================
# SECTION 13: 8.13 응용사례
# ============================================================
section_divider("응용사례", "Medical Diagnosis, Customer Segmentation, Manufacturing", "8.13", ACCENT_GREEN)

# Slide 55: 의료 진단
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.13", "응용 1: 의료 진단 트리", "해석 가능한 진단 규칙 추출")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(2.5),
         "적용 이유",
         ["의사에게 해석 가능한 규칙 제공",
          "  'worst perimeter > 114.45이면 악성 가능성 높음'",
          "의료 가이드라인 생성: 진단 프로토콜 수립",
          "트리아지(Triage) 시스템: 환자 긴급도 자동 분류",
          "FDA 등 규제 기관의 승인에 유리한 설명가능성"],
         title_color=ACCENT_GREEN, border=ACCENT_GREEN)
add_code_block(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(2.5), [
    "from sklearn.tree import export_text",
    "",
    "diag_model = DecisionTreeClassifier(",
    "    max_depth=3, random_state=42)",
    "diag_model.fit(X, y)",
    "rules = export_text(diag_model,",
    "    feature_names=list(feature_names))",
    "# 개별 환자 진단 경로 추적:",
    "node_indicator = diag_model.decision_path(X[:1])",
], font_size=12)
add_shape(s, Inches(0.6), Inches(5.0), Inches(12), Inches(2.0), CARD_BG, ACCENT_RED, radius=True)
add_text(s, Inches(0.9), Inches(5.1), Inches(11.4), Inches(0.3),
         "주의사항", font_size=15, color=ACCENT_RED, bold=True)
add_text(s, Inches(0.9), Inches(5.5), Inches(11.4), Inches(1.2),
         "의료 AI에서 단일 의사결정나무는 보조 도구로만 사용. 최종 진단은 반드시 의료 전문가가 내려야 한다.\n"
         "정확도가 요구되는 경우 앙상블 모델을 사용하되, 해석가능성을 위해 SHAP 등의 설명 기법 병행.",
         font_size=14, color=LIGHT_GRAY)

# Slide 56: 고객 세그멘테이션 & 제조 불량
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.13", "응용 2-3: 고객 세그멘테이션 & 제조 불량 분석")
add_card(s, Inches(0.6), Inches(2.2), Inches(5.5), Inches(4.8),
         "고객 세그멘테이션",
         ["시나리오: 이커머스 고객 VIP/일반/이탈 분류",
          "",
          "[최근 구매일 <= 30일]",
          "  예 -> [월 구매금액 >= 50만원]",
          "     예 -> [VIP 고객]",
          "     아니오 -> [일반 고객]",
          "  아니오 -> [최근 구매일 <= 90일]",
          "     예 -> [이탈 위험]",
          "     아니오 -> [이탈 고객]",
          "",
          "장점:",
          "  추출된 규칙을 마케팅 전략에 직접 활용",
          "  비전문가(마케터)도 즉시 이해 가능"],
         title_color=ACCENT_CYAN, border=ACCENT_CYAN)
add_card(s, Inches(6.5), Inches(2.2), Inches(6.0), Inches(4.8),
         "제조 불량 분석 (Root Cause Analysis)",
         ["시나리오: 반도체 공정 불량률 증가 원인 파악",
          "",
          "[온도 > 185도]",
          "  예 -> [습도 > 65%]",
          "     예 -> [불량률: 23.4%]  <- 핵심 원인!",
          "     아니오 -> [불량률: 5.2%]",
          "  아니오 -> [불량률: 1.8%]",
          "",
          "장점:",
          "  특성 중요도로 불량 원인 변수 식별",
          "  분할 규칙에서 불량 조건 명확히 파악",
          "  공정 엔지니어에게 직관적 개선 방향 제시",
          "  실시간 모니터링 시스템에 규칙 탑재 가능"],
         title_color=ACCENT_ORANGE, border=ACCENT_ORANGE)

# ============================================================
# SECTION 14: 8.14 핵심 요약
# ============================================================
section_divider("핵심 요약 + 복습 질문", "Key Summary & Review Questions", "8.14", ACCENT_YELLOW)

# Slide 58: 핵심 요약 표 (1)
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.14", "핵심 요약 (1/2)", "주요 개념과 수식 정리")
add_table_slide(s,
    ["주제", "핵심 내용"],
    [["트리 구조", "루트 -> 내부 노드 -> 리프의 계층적 구조"],
     ["엔트로피", "H = -SUM(p_i * log2(p_i)), 범위: [0,1] (이진)"],
     ["지니 불순도", "Gini = 1 - SUM(p_i^2), 범위: [0,0.5] (이진)"],
     ["정보이득", "분할 전후 불순도 감소량, 가장 큰 분할 선택"],
     ["알고리즘 역사", "ID3(1986) -> CART(1984) -> C4.5(1993)"],
     ["사전 가지치기", "max_depth, min_samples_split, min_samples_leaf"],
     ["사후 가지치기", "CCP: R_a(T) = R(T) + a*|T_leaf|, CV로 최적 a 선택"]],
    Inches(0.6), Inches(2.2), [2.5, 9.0], row_height=0.52, font_size=14)

# Slide 59: 핵심 요약 표 (2)
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.14", "핵심 요약 (2/2)", "추가 개념과 장단점")
add_table_slide(s,
    ["주제", "핵심 내용"],
    [["1-SE Rule", "최적 성능 - 1SE 이상에서 가장 단순한 모델 선택"],
     ["과적합/불안정성", "높은 분산(high variance), 앙상블로 해결"],
     ["변수 선택 편향", "고카디널리티 선호, 이득비율/통계적 검정으로 완화"],
     ["대리 분할", "결측값 처리: 최적 분할과 유사한 대체 속성 사용"],
     ["회귀 트리", "MSE 감소 기준, 리프 예측값 = 평균"],
     ["장점", "해석가능성, 전처리 불필요, 비선형 포착, 빠른 예측"],
     ["단점", "과적합, 불안정성, 축 정렬 분할, 탐욕적 최적화"]],
    Inches(0.6), Inches(2.2), [2.5, 9.0], row_height=0.52, font_size=14)

# Slide 60: 복습 질문 (1/2)
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.14", "복습 질문 (1/2)")
add_bullet_list(s, Inches(0.6), Inches(2.0), Inches(12), Inches(5.0), [
    "Q1. [개념] 엔트로피와 지니 불순도의 수학적 정의를 쓰고, 이진 분류에서 각각의 최대값을 구하시오.",
    "",
    "Q2. [계산] 노드에 클래스 A 8개, 클래스 B 2개가 있을 때, (a) 지니 불순도, (b) 엔트로피를 계산하시오.",
    "",
    "Q3. [비교] ID3, CART, C4.5 알고리즘의 분할 기준, 분할 방식, 가지치기 전략을 각각 비교하시오.",
    "",
    "Q4. [수학] 비용-복잡도 함수에서 alpha의 역할을 설명하고, alpha=0과 alpha->inf에서 각각 어떤 트리가 선택되는지 설명하시오.",
    "",
    "Q5. [실무] 1-SE Rule이란 무엇이며, 왜 단순히 CV 점수가 최대인 모델 대신 이 규칙을 적용하는가?",
], font_size=16, color=LIGHT_GRAY, spacing=Pt(4))

# Slide 61: 복습 질문 (2/2)
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "8.14", "복습 질문 (2/2)")
add_bullet_list(s, Inches(0.6), Inches(2.0), Inches(12), Inches(5.0), [
    "Q6. [이론] 의사결정나무가 높은 분산을 가지는 이유를 설명하고, 이를 해결하기 위한 앙상블 기법의 기본 아이디어를 서술하시오.",
    "",
    "Q7. [편향] Loh(2011)가 지적한 변수 선택 편향이란 무엇이며, C4.5의 이득비율은 이 문제를 어떻게 완화하는가?",
    "",
    "Q8. [결측] CART의 대리 분할의 원리를 설명하시오. scikit-learn에서 결측치를 가진 데이터로 의사결정나무를 학습하려면?",
    "",
    "Q9. [구현] 의사결정나무 스크래치 구현에서, 최적 분할 탐색의 시간 복잡도를 분석하시오. (특성 수 d, 샘플 수 n, 깊이 h)",
    "",
    "Q10. [응용] 금융 분야(대출 심사)에서 의사결정나무가 신경망보다 선호되는 이유를 '해석가능성'과 '규제 요건' 관점에서 설명하시오.",
], font_size=16, color=LIGHT_GRAY, spacing=Pt(4))

# ============================================================
# 참고 논문
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s)
slide_header(s, "", "참고 논문", "핵심 논문 5편")
add_table_slide(s,
    ["#", "논문", "핵심 기여", "연도"],
    [["1", "Quinlan - Induction of Decision Trees", "ID3, 정보 이득 기반 속성 선택", "1986"],
     ["2", "Breiman et al. - CART", "지니 불순도, CCP, 대리 분할", "1984"],
     ["3", "Quinlan - C4.5: Programs for ML", "이득비율, EBP, 결측치 처리", "1993"],
     ["4", "Rokach & Maimon - TDIDT Survey", "TDIDT 프레임워크, 체계적 분류", "2005"],
     ["5", "Loh - Classification and Regression Trees", "변수 선택 편향 분석, GUIDE", "2011"]],
    Inches(0.6), Inches(2.2), [0.8, 4.5, 4.2, 1.2], row_height=0.55, font_size=13)

# ============================================================
# Thank You Slide
# ============================================================
s = prs.slides.add_slide(prs.slide_layouts[6]); add_bg(s, SECTION_BG)
add_shape(s, Inches(0), Inches(0), prs.slide_width, Pt(4), ACCENT_BLUE)
add_shape(s, Inches(0), Inches(7.2), prs.slide_width, Pt(4), ACCENT_BLUE)
add_text(s, Inches(0), Inches(2.5), prs.slide_width, Inches(1.0),
         "Thank You", font_size=52, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
add_accent_line(s, Inches(5.5), Inches(3.7), Inches(2.3), ACCENT_BLUE)
add_text(s, Inches(0), Inches(4.2), prs.slide_width, Inches(0.5),
         "8장 의사결정나무 (Decision Tree)", font_size=22, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
add_text(s, Inches(0), Inches(5.0), prs.slide_width, Inches(0.5),
         "다음 장: 9장 앙상블 학습 (Ensemble Learning)", font_size=18, color=DARK_GRAY, align=PP_ALIGN.CENTER)

# ============================================================
# Save
# ============================================================
out = os.path.join(os.path.dirname(__file__), "8장_의사결정나무_강의PPT_확장.pptx")
prs.save(out)
print(f"Created: {out}")
print(f"Total slides: {len(prs.slides)}")
