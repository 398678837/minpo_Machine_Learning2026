# -*- coding: utf-8 -*-
"""8장 의사결정나무 - 교재용 강의 PPT (한국어/중국어 동시 생성)"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

OUT_DIR = r"F:\minpodata\기계학습\기계학습\8장"

# ===== Color Palette =====
DARK_BG       = RGBColor(0x1B, 0x1B, 0x2F)
SECTION_BG    = RGBColor(0x10, 0x10, 0x28)
CARD_BG       = RGBColor(0x25, 0x25, 0x3D)
CARD_BG2      = RGBColor(0x2D, 0x2D, 0x45)
CODE_BG       = RGBColor(0x1E, 0x1E, 0x30)
ACCENT_BLUE   = RGBColor(0x00, 0x96, 0xFF)
ACCENT_CYAN   = RGBColor(0x00, 0xD2, 0xFF)
ACCENT_GREEN  = RGBColor(0x00, 0xE6, 0x96)
ACCENT_ORANGE = RGBColor(0xFF, 0x8C, 0x00)
ACCENT_RED    = RGBColor(0xFF, 0x45, 0x45)
ACCENT_PURPLE = RGBColor(0xA0, 0x6C, 0xFF)
ACCENT_YELLOW = RGBColor(0xFF, 0xD7, 0x00)
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY    = RGBColor(0xBB, 0xBB, 0xCC)
DARK_GRAY     = RGBColor(0x88, 0x88, 0x99)


# ===== Helpers =====
def add_bg(slide, color=DARK_BG):
    bg = slide.background; fill = bg.fill; fill.solid(); fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color, border_color=None, radius=False):
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
    tx = slide.shapes.add_textbox(left, top, width, height)
    tf = tx.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(font_size)
    p.font.color.rgb = color; p.font.bold = bold
    p.font.name = font_name; p.alignment = align
    return tx


def add_bullets(slide, left, top, width, height, items, font_size=15,
                color=LIGHT_GRAY, spacing=Pt(6), font_name='맑은 고딕'):
    tx = slide.shapes.add_textbox(left, top, width, height)
    tf = tx.text_frame; tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item; p.font.size = Pt(font_size)
        p.font.color.rgb = color; p.font.name = font_name
        p.space_after = spacing
    return tx


def add_accent_line(slide, left, top, width, color=ACCENT_BLUE):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background()
    return s


def slide_header(slide, section_label, title, subtitle=""):
    add_accent_line(slide, Inches(0.6), Inches(0.5), Inches(1.2), ACCENT_BLUE)
    if section_label:
        add_text(slide, Inches(0.6), Inches(0.55), Inches(3), Inches(0.4),
                 section_label, font_size=12, color=ACCENT_BLUE, bold=True)
    add_text(slide, Inches(0.6), Inches(0.9), Inches(12.2), Inches(0.7),
             title, font_size=30, color=WHITE, bold=True)
    if subtitle:
        add_text(slide, Inches(0.6), Inches(1.55), Inches(12.2), Inches(0.4),
                 subtitle, font_size=15, color=DARK_GRAY)


def add_card(slide, left, top, width, height, title, body_items,
             title_color=ACCENT_CYAN, font_name='맑은 고딕'):
    add_shape(slide, left, top, width, height, CARD_BG, CARD_BG, radius=True)
    add_text(slide, left + Inches(0.2), top + Inches(0.12), width - Inches(0.4), Inches(0.4),
             title, font_size=15, color=title_color, bold=True, font_name=font_name)
    add_bullets(slide, left + Inches(0.2), top + Inches(0.55), width - Inches(0.4),
                height - Inches(0.65), body_items, font_size=12, color=LIGHT_GRAY,
                spacing=Pt(4), font_name=font_name)


def add_code_block(slide, left, top, width, height, code_lines, font_size=11):
    add_shape(slide, left, top, width, height, CODE_BG, ACCENT_BLUE, radius=True)
    tx = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15),
                                  width - Inches(0.4), height - Inches(0.3))
    tf = tx.text_frame; tf.word_wrap = True
    for i, line in enumerate(code_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(font_size)
        p.font.color.rgb = ACCENT_GREEN; p.font.name = 'Consolas'
        p.space_after = Pt(2)


def add_table(slide, headers, rows, left, top, col_widths,
              header_color=ACCENT_BLUE, row_height=0.42, font_size=12,
              header_font_size=13, font_name='맑은 고딕'):
    cx = left
    for h, w in zip(headers, col_widths):
        add_shape(slide, cx, top, Inches(w), Inches(0.45), header_color)
        add_text(slide, cx, top, Inches(w), Inches(0.45),
                 h, font_size=header_font_size, color=WHITE, bold=True,
                 align=PP_ALIGN.CENTER, font_name=font_name)
        cx += Inches(w)
    for i, row in enumerate(rows):
        y = top + Inches(0.45) + Inches(row_height) * i
        bg = CARD_BG if i % 2 == 0 else CARD_BG2
        cx = left
        for j, (cell, w) in enumerate(zip(row, col_widths)):
            add_shape(slide, cx, y, Inches(w), Inches(row_height), bg)
            fc = ACCENT_CYAN if j == 0 else LIGHT_GRAY
            add_text(slide, cx + Inches(0.05), y, Inches(w - 0.1), Inches(row_height),
                     cell, font_size=font_size, color=fc, bold=(j == 0),
                     align=PP_ALIGN.CENTER, font_name=font_name)
            cx += Inches(w)


def set_notes(slide, text):
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.text = text


def new_prs():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def blank_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(s, DARK_BG)
    return s


# Sentinel to mark slide content
__all__ = [
    'OUT_DIR', 'new_prs', 'blank_slide', 'slide_header', 'add_text', 'add_bullets',
    'add_card', 'add_code_block', 'add_table', 'add_accent_line', 'add_shape',
    'set_notes', 'DARK_BG', 'SECTION_BG', 'CARD_BG', 'CARD_BG2', 'CODE_BG',
    'ACCENT_BLUE', 'ACCENT_CYAN', 'ACCENT_GREEN', 'ACCENT_ORANGE', 'ACCENT_RED',
    'ACCENT_PURPLE', 'ACCENT_YELLOW', 'WHITE', 'LIGHT_GRAY', 'DARK_GRAY',
    'Inches', 'Pt', 'PP_ALIGN'
]
