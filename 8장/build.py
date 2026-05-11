# -*- coding: utf-8 -*-
"""8장 의사결정나무 — 교재 PPT 빌더 (한국어 + 중국어 간체)"""
import sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_textbook_ppt import (
    new_prs, blank_slide, slide_header, add_text, add_bullets,
    add_card, add_code_block, add_table, add_accent_line, add_shape,
    set_notes,
    DARK_BG, SECTION_BG, CARD_BG, CARD_BG2, CODE_BG,
    ACCENT_BLUE, ACCENT_CYAN, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_RED,
    ACCENT_PURPLE, ACCENT_YELLOW, WHITE, LIGHT_GRAY, DARK_GRAY,
    Inches, Pt, PP_ALIGN
)
from slides_content import SLIDES
from slides_content_2 import SLIDES_2
from slides_content_3 import SLIDES_3

ALL_SLIDES = SLIDES + SLIDES_2 + SLIDES_3

# 한국어 / 중국어 폰트
FONT_KO = '맑은 고딕'
FONT_CN = 'Microsoft YaHei'  # Windows 표준 중국어 폰트


# ============================================================
# 슬라이드 종류별 렌더링
# ============================================================
def render_title(slide, c, font):
    add_shape(slide, Inches(0.5), Inches(0.5), Inches(12.3), Inches(6.5),
              SECTION_BG, ACCENT_BLUE, radius=True)
    add_accent_line(slide, Inches(1.0), Inches(1.2), Inches(2.5), ACCENT_CYAN)
    add_text(slide, Inches(1.0), Inches(1.3), Inches(11), Inches(0.4),
             c['subject'], font_size=14, color=ACCENT_CYAN, bold=True, font_name=font)
    add_text(slide, Inches(1.0), Inches(1.7), Inches(11), Inches(0.5),
             c['chapter'], font_size=18, color=LIGHT_GRAY, font_name=font)
    add_text(slide, Inches(1.0), Inches(2.4), Inches(11), Inches(1.5),
             c['title'], font_size=72, color=WHITE, bold=True, font_name=font)
    add_text(slide, Inches(1.0), Inches(3.7), Inches(11), Inches(0.6),
             c['subtitle'], font_size=28, color=ACCENT_CYAN, font_name=font)
    add_accent_line(slide, Inches(1.0), Inches(4.5), Inches(4), ACCENT_BLUE)
    add_text(slide, Inches(1.0), Inches(4.7), Inches(11), Inches(0.5),
             c['tagline'], font_size=18, color=LIGHT_GRAY, font_name=font)
    add_text(slide, Inches(1.0), Inches(6.4), Inches(11), Inches(0.4),
             c['meta'], font_size=12, color=DARK_GRAY, font_name=font)


def render_toc(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    items = c['items']
    # 2 columns x 7 rows
    col_w = Inches(5.9)
    row_h = Inches(0.6)
    for i, (num, label) in enumerate(items):
        col = i // 7
        row = i % 7
        x = Inches(0.6) + col * Inches(6.2)
        y = Inches(2.1) + row * row_h
        add_shape(slide, x, y + Inches(0.05), Inches(0.7), Inches(0.5),
                  ACCENT_BLUE, radius=True)
        add_text(slide, x, y + Inches(0.05), Inches(0.7), Inches(0.5),
                 num, font_size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER, font_name=font)
        add_text(slide, x + Inches(0.85), y + Inches(0.1), col_w - Inches(1.0), Inches(0.5),
                 label, font_size=15, color=LIGHT_GRAY, font_name=font)


def render_section_cover(slide, c, font):
    # left big number
    add_text(slide, Inches(0.5), Inches(1.5), Inches(5), Inches(4.5),
             c['num'], font_size=320, color=CARD_BG, bold=True, font_name=font)
    add_accent_line(slide, Inches(5.5), Inches(2.3), Inches(1.0), ACCENT_BLUE)
    add_text(slide, Inches(5.5), Inches(2.4), Inches(7.5), Inches(0.5),
             c['section'], font_size=14, color=ACCENT_CYAN, bold=True, font_name=font)
    add_text(slide, Inches(5.5), Inches(2.95), Inches(7.5), Inches(1.5),
             c['title'], font_size=44, color=WHITE, bold=True, font_name=font)
    add_text(slide, Inches(5.5), Inches(4.5), Inches(7.5), Inches(0.6),
             c['subtitle'], font_size=18, color=LIGHT_GRAY, font_name=font)


def render_two_card(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    # left card
    lx, w, y, h = Inches(0.6), Inches(6.0), Inches(2.2), Inches(4.9)
    add_shape(slide, lx, y, w, h, CARD_BG, ACCENT_BLUE, radius=True)
    add_text(slide, lx + Inches(0.3), y + Inches(0.2), w - Inches(0.6), Inches(0.5),
             c['left_title'], font_size=18, color=ACCENT_CYAN, bold=True, font_name=font)
    add_bullets(slide, lx + Inches(0.3), y + Inches(0.85), w - Inches(0.6), h - Inches(1.0),
                c['left_items'], font_size=14, color=LIGHT_GRAY, spacing=Pt(8), font_name=font)
    # right card
    rx = Inches(6.8)
    add_shape(slide, rx, y, w, h, CARD_BG, ACCENT_GREEN, radius=True)
    add_text(slide, rx + Inches(0.3), y + Inches(0.2), w - Inches(0.6), Inches(0.5),
             c['right_title'], font_size=18, color=ACCENT_GREEN, bold=True, font_name=font)
    add_bullets(slide, rx + Inches(0.3), y + Inches(0.85), w - Inches(0.6), h - Inches(1.0),
                c['right_items'], font_size=14, color=LIGHT_GRAY, spacing=Pt(8), font_name=font)


def render_three_card(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    cards = c['cards']
    colors = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE]
    cx, w, y, h = Inches(0.6), Inches(4.0), Inches(2.2), Inches(4.0)
    for i, ((title, body), col) in enumerate(zip(cards, colors)):
        x = cx + i * Inches(4.15)
        add_shape(slide, x, y, w, h, CARD_BG, col, radius=True)
        add_text(slide, x + Inches(0.25), y + Inches(0.2), w - Inches(0.5), Inches(0.5),
                 title, font_size=15, color=col, bold=True, font_name=font)
        # body as paragraph (preserve newlines)
        tx = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.85),
                                      w - Inches(0.5), h - Inches(1.0))
        tf = tx.text_frame; tf.word_wrap = True
        lines = body.split('\n')
        for j, line in enumerate(lines):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = line; p.font.size = Pt(11)
            p.font.color.rgb = LIGHT_GRAY; p.font.name = font
            p.space_after = Pt(2)
    # punch line
    if c.get('punch'):
        add_shape(slide, Inches(0.6), Inches(6.4), Inches(12.2), Inches(0.7),
                  SECTION_BG, ACCENT_YELLOW, radius=True)
        add_text(slide, Inches(0.8), Inches(6.5), Inches(11.8), Inches(0.5),
                 '🔑 ' + c['punch'], font_size=14, color=ACCENT_YELLOW, bold=True, font_name=font)


def render_tree_structure(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    # tree code block (top)
    add_shape(slide, Inches(0.6), Inches(2.2), Inches(12.2), Inches(2.0),
              CODE_BG, ACCENT_CYAN, radius=True)
    tx = slide.shapes.add_textbox(Inches(0.8), Inches(2.35), Inches(12.0), Inches(1.8))
    tf = tx.text_frame; tf.word_wrap = True
    for i, line in enumerate(c['tree_lines']):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(13)
        p.font.color.rgb = ACCENT_CYAN; p.font.name = 'Consolas'
        p.space_after = Pt(2)
    # terms table (bottom)
    headers = ['용어 / Term', '영문', '설명']
    if font == FONT_CN:
        headers = ['术语 / Term', '英文', '说明']
    rows = [[t[0], t[1], t[2]] for t in c['terms']]
    add_table(slide, headers, rows, Inches(0.6), Inches(4.4),
              [2.5, 2.7, 7.0], font_size=11, header_font_size=12,
              row_height=0.4, font_name=font)


def render_formula(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    # formula box
    add_shape(slide, Inches(0.6), Inches(2.1), Inches(12.2), Inches(1.2),
              CODE_BG, ACCENT_YELLOW, radius=True)
    add_text(slide, Inches(0.6), Inches(2.3), Inches(12.2), Inches(0.7),
             c['formula'], font_size=24, color=ACCENT_YELLOW, bold=True,
             align=PP_ALIGN.CENTER, font_name='Consolas')
    add_text(slide, Inches(0.6), Inches(2.85), Inches(12.2), Inches(0.4),
             c['note'], font_size=11, color=LIGHT_GRAY,
             align=PP_ALIGN.CENTER, font_name=font)
    # meaning card
    add_shape(slide, Inches(0.6), Inches(3.45), Inches(6.0), Inches(3.6),
              CARD_BG, ACCENT_GREEN, radius=True)
    add_text(slide, Inches(0.8), Inches(3.55), Inches(5.7), Inches(0.5),
             c['meaning_title'], font_size=15, color=ACCENT_GREEN, bold=True, font_name=font)
    tx = slide.shapes.add_textbox(Inches(0.8), Inches(4.05), Inches(5.7), Inches(2.9))
    tf = tx.text_frame; tf.word_wrap = True
    for i, line in enumerate(c['meaning'].split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(12)
        p.font.color.rgb = LIGHT_GRAY; p.font.name = font
        p.space_after = Pt(3)
    # table on right — 우측 영역 폭 제한 (left=6.8, right_margin=0.13 → max 6.4")
    col_widths = c.get('col_widths', [2.0, 1.2, 1.2, 1.2, 1.0])
    MAX_W = 6.4
    total = sum(col_widths)
    if total > MAX_W:
        scale = MAX_W / total
        col_widths = [w * scale for w in col_widths]
    n_rows = len(c['table_rows'])
    # 세로: top=3.5, 헤더 0.45 + 행*row_height ≤ 7.3 → row_height 자동 조정
    avail_h = 7.3 - 3.5 - 0.45
    row_h = min(0.5, avail_h / max(n_rows, 1))
    fs = 11 if row_h >= 0.42 else 9
    add_table(slide, c['table_header'], c['table_rows'],
              Inches(6.8), Inches(3.5), col_widths,
              font_size=fs, header_font_size=12, row_height=row_h, font_name=font)


def render_table(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    col_widths = c.get('col_widths', [2.0] * len(c['headers']))
    # 가로 자동 스케일: 슬라이드 폭 13.33", left=0.6, 우측 여백 0.53 → max 12.2"
    MAX_W = 12.2
    total = sum(col_widths)
    if total > MAX_W:
        scale = MAX_W / total
        col_widths = [w * scale for w in col_widths]
    # 세로 자동 스케일: top=2.2, 하단 여백 0.3 → 최대 5.0" (헤더 0.45 + N행)
    n_rows = len(c['rows'])
    avail_h = 7.2 - 2.2 - 0.45  # = 4.55"
    row_h = min(0.55, avail_h / max(n_rows, 1))
    fs = 12
    if row_h < 0.45: fs = 11
    if row_h < 0.38: fs = 10
    if row_h < 0.32: fs = 9
    add_table(slide, c['headers'], c['rows'],
              Inches(0.6), Inches(2.2), col_widths,
              font_size=fs, header_font_size=13, row_height=row_h, font_name=font)


def render_code(slide, c, font):
    slide_header(slide, '', c['header'], c['subtitle'])
    add_code_block(slide, Inches(0.6), Inches(2.1), Inches(12.2), Inches(5.1),
                   c['code'], font_size=11)


def render_closing(slide, c, font):
    add_shape(slide, Inches(0.5), Inches(0.5), Inches(12.3), Inches(6.5),
              SECTION_BG, ACCENT_BLUE, radius=True)
    add_text(slide, Inches(1.0), Inches(1.5), Inches(11.3), Inches(1.2),
             c['main'], font_size=54, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER, font_name=font)
    add_text(slide, Inches(1.0), Inches(2.7), Inches(11.3), Inches(0.6),
             c['sub'], font_size=22, color=ACCENT_CYAN,
             align=PP_ALIGN.CENTER, font_name=font)
    add_accent_line(slide, Inches(5.5), Inches(3.6), Inches(2.3), ACCENT_BLUE)
    add_shape(slide, Inches(1.5), Inches(4.0), Inches(10.3), Inches(1.5),
              CARD_BG, ACCENT_GREEN, radius=True)
    tx = slide.shapes.add_textbox(Inches(1.7), Inches(4.15), Inches(9.9), Inches(1.2))
    tf = tx.text_frame; tf.word_wrap = True
    for i, line in enumerate(c['message'].split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(15)
        p.font.color.rgb = LIGHT_GRAY; p.font.name = font
        p.alignment = PP_ALIGN.CENTER; p.space_after = Pt(4)
    add_text(slide, Inches(1.0), Inches(6.0), Inches(11.3), Inches(0.5),
             '▶ ' + c['next'], font_size=16, color=ACCENT_YELLOW, bold=True,
             align=PP_ALIGN.CENTER, font_name=font)


RENDERERS = {
    'title': render_title,
    'toc': render_toc,
    'section_cover': render_section_cover,
    'two_card': render_two_card,
    'three_card': render_three_card,
    'tree_structure': render_tree_structure,
    'formula': render_formula,
    'table': render_table,
    'code': render_code,
    'closing': render_closing,
}


def build(lang, out_path):
    font = FONT_KO if lang == 'ko' else FONT_CN
    prs = new_prs()
    for spec in ALL_SLIDES:
        kind = spec['kind']
        content = spec[lang]
        slide = blank_slide(prs)
        renderer = RENDERERS.get(kind)
        if renderer is None:
            print(f"⚠ Unknown kind: {kind}")
            continue
        renderer(slide, content, font)
        if 'notes' in content:
            set_notes(slide, content['notes'])
    # 잠금 회피: 임시 파일에 쓰고 교체. 잠겨 있으면 .new.pptx로 저장
    tmp_path = out_path + '.tmp'
    prs.save(tmp_path)
    try:
        os.replace(tmp_path, out_path)
        final = out_path
    except PermissionError:
        final = out_path.replace('.pptx', '_new.pptx')
        os.replace(tmp_path, final)
        print(f"⚠ 원본 잠김 → 대신 저장: {final}")
    print(f"✓ Saved: {final}  ({len(ALL_SLIDES)} slides)")


if __name__ == '__main__':
    out_dir = r"F:\minpodata\기계학습\기계학습\8장"
    build('ko', os.path.join(out_dir, '8장_교재.pptx'))
    build('cn', os.path.join(out_dir, '8장_교재_cn.pptx'))
