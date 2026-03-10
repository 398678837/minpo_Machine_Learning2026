# -*- coding: utf-8 -*-
"""
Markdown → PDF 변환 스크립트
reportlab + matplotlib(LaTeX 수식 렌더링)을 사용하여 한글 지원 PDF 생성
"""

import os
import re
import sys
import hashlib
import tempfile
import shutil
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.mathtext

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white, grey, lightgrey
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# ============================================================
# 한글 폰트 등록
# ============================================================
FONT_PATH_REGULAR = r"C:\Windows\Fonts\malgun.ttf"
FONT_PATH_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"

if os.path.exists(FONT_PATH_REGULAR):
    pdfmetrics.registerFont(TTFont('MalgunGothic', FONT_PATH_REGULAR))
if os.path.exists(FONT_PATH_BOLD):
    pdfmetrics.registerFont(TTFont('MalgunGothicBold', FONT_PATH_BOLD))

FONT_NAME = 'MalgunGothic'
FONT_NAME_BOLD = 'MalgunGothicBold' if os.path.exists(FONT_PATH_BOLD) else FONT_NAME
MONO_FONT = 'Courier'

# ============================================================
# LaTeX 수식 렌더링 (matplotlib mathtext)
# ============================================================
FORMULA_TEMP_DIR = None
FORMULA_CACHE = {}


def init_formula_renderer():
    """수식 렌더링용 임시 디렉토리 생성"""
    global FORMULA_TEMP_DIR
    FORMULA_TEMP_DIR = tempfile.mkdtemp(prefix='latex_formulas_')
    return FORMULA_TEMP_DIR


def cleanup_formula_renderer():
    """임시 디렉토리 정리"""
    global FORMULA_TEMP_DIR, FORMULA_CACHE
    if FORMULA_TEMP_DIR and os.path.exists(FORMULA_TEMP_DIR):
        shutil.rmtree(FORMULA_TEMP_DIR, ignore_errors=True)
    FORMULA_TEMP_DIR = None
    FORMULA_CACHE = {}


def preprocess_latex(expr):
    """matplotlib mathtext 호환을 위한 LaTeX 전처리"""
    # \text{} → \mathrm{} (mathtext는 \text 미지원)
    expr = expr.replace('\\text{', '\\mathrm{')
    return expr


def render_latex(expr, fontsize=14, dpi=200, is_block=False):
    """
    LaTeX 수식을 PNG 이미지로 렌더링한다.

    Returns
    -------
    (path, width_pt, height_pt) : tuple
        렌더링된 이미지 경로와 크기 (포인트 단위)
    """
    global FORMULA_CACHE

    cache_key = f"{expr}_{fontsize}_{dpi}_{is_block}"
    if cache_key in FORMULA_CACHE:
        return FORMULA_CACHE[cache_key]

    processed = preprocess_latex(expr)

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_facecolor('white')

    actual_fs = fontsize + 4 if is_block else fontsize

    fig.text(
        0, 0,
        f'${processed}$',
        fontsize=actual_fs,
        fontfamily='serif',
        math_fontfamily='cm',  # Computer Modern (클래식 LaTeX 서체)
        verticalalignment='baseline',
    )

    hash_name = hashlib.md5(cache_key.encode()).hexdigest()[:12]
    path = os.path.join(FORMULA_TEMP_DIR, f'formula_{hash_name}.png')

    fig.savefig(
        path, dpi=dpi, bbox_inches='tight',
        pad_inches=0.04, facecolor='white', edgecolor='none'
    )
    plt.close(fig)

    # 이미지 크기를 포인트로 변환 (1 inch = 72 points)
    reader = ImageReader(path)
    px_w, px_h = reader.getSize()
    pt_w = px_w * 72.0 / dpi
    pt_h = px_h * 72.0 / dpi

    result = (path, pt_w, pt_h)
    FORMULA_CACHE[cache_key] = result
    return result


# ============================================================
# 스타일 정의
# ============================================================
def create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='KorTitle',
        fontName=FONT_NAME_BOLD,
        fontSize=20,
        leading=28,
        alignment=TA_LEFT,
        spaceAfter=12,
        textColor=HexColor('#1a1a2e'),
    ))
    styles.add(ParagraphStyle(
        name='KorH2',
        fontName=FONT_NAME_BOLD,
        fontSize=16,
        leading=22,
        alignment=TA_LEFT,
        spaceBefore=18,
        spaceAfter=8,
        textColor=HexColor('#16213e'),
    ))
    styles.add(ParagraphStyle(
        name='KorH3',
        fontName=FONT_NAME_BOLD,
        fontSize=13,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=6,
        textColor=HexColor('#0f3460'),
    ))
    styles.add(ParagraphStyle(
        name='KorH4',
        fontName=FONT_NAME_BOLD,
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=10,
        spaceAfter=4,
        textColor=HexColor('#333333'),
    ))
    styles.add(ParagraphStyle(
        name='KorBody',
        fontName=FONT_NAME,
        fontSize=10,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        textColor=black,
    ))
    styles.add(ParagraphStyle(
        name='KorBullet',
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        leftIndent=18,
        spaceAfter=3,
        bulletIndent=6,
        textColor=black,
    ))
    styles.add(ParagraphStyle(
        name='KorBullet2',
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        leftIndent=36,
        spaceAfter=3,
        bulletIndent=24,
        textColor=HexColor('#333333'),
    ))
    styles.add(ParagraphStyle(
        name='KorCode',
        fontName=MONO_FONT,
        fontSize=8.5,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=2,
        leftIndent=10,
        textColor=HexColor('#1a1a1a'),
        backColor=HexColor('#f5f5f5'),
    ))
    styles.add(ParagraphStyle(
        name='KorBlockquote',
        fontName=FONT_NAME,
        fontSize=10,
        leading=16,
        alignment=TA_LEFT,
        leftIndent=20,
        spaceAfter=6,
        textColor=HexColor('#555555'),
        borderColor=HexColor('#4285F4'),
        borderWidth=2,
        borderPadding=8,
    ))
    styles.add(ParagraphStyle(
        name='KorTableCell',
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=12,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name='KorTableHeader',
        fontName=FONT_NAME_BOLD,
        fontSize=8.5,
        leading=12,
        alignment=TA_CENTER,
        textColor=white,
    ))
    styles.add(ParagraphStyle(
        name='KorCaption',
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        spaceAfter=10,
        textColor=HexColor('#666666'),
    ))

    return styles


# ============================================================
# 마크다운 인라인 포맷 변환 (LaTeX 수식 포함)
# ============================================================
def convert_inline(text):
    """마크다운 인라인 포맷을 reportlab XML 태그로 변환 (수식 렌더링 포함)"""

    # --- 1단계: 수식을 먼저 추출하고 플레이스홀더로 대체 ---
    # (HTML 이스케이프 전에 수식을 추출해야 LaTeX 명령어가 깨지지 않음)
    formulas = {}
    formula_counter = [0]

    def _extract_inline_math(match):
        expr = match.group(1)
        placeholder = f"__FORMULA_{formula_counter[0]}__"
        formulas[placeholder] = ('inline', expr)
        formula_counter[0] += 1
        return placeholder

    def _extract_block_math(match):
        expr = match.group(1)
        placeholder = f"__FORMULA_{formula_counter[0]}__"
        formulas[placeholder] = ('block_inline', expr)
        formula_counter[0] += 1
        return placeholder

    # 코드 인라인 보호: `...` 안의 $를 먼저 보호
    code_spans = {}
    code_counter = [0]

    def _protect_code(match):
        placeholder = f"__CODE_{code_counter[0]}__"
        code_spans[placeholder] = match.group(0)
        code_counter[0] += 1
        return placeholder

    text = re.sub(r'`[^`]+`', _protect_code, text)

    # $$...$$ (인라인 블록 수식) 먼저 추출
    text = re.sub(r'\$\$(.+?)\$\$', _extract_block_math, text)
    # $...$ (인라인 수식) 추출
    text = re.sub(r'\$(.+?)\$', _extract_inline_math, text)

    # 코드 복원
    for placeholder, original in code_spans.items():
        text = text.replace(placeholder, original)

    # --- 2단계: HTML 특수문자 이스케이프 ---
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;').replace('>', '&gt;')

    # --- 3단계: 마크다운 인라인 포맷 변환 ---
    # 코드 인라인: `code` → <font>
    text = re.sub(r'`([^`]+)`',
                  r'<font face="Courier" size="9" color="#c7254e">\1</font>', text)

    # 볼드+이탤릭: ***text***
    text = re.sub(r'\*\*\*(.+?)\*\*\*',
                  rf'<font face="{FONT_NAME_BOLD}"><i>\1</i></font>', text)

    # 볼드: **text**
    text = re.sub(r'\*\*(.+?)\*\*',
                  rf'<font face="{FONT_NAME_BOLD}">\1</font>', text)

    # 이탤릭: *text*
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)

    # --- 4단계: 수식 플레이스홀더를 렌더링된 이미지로 대체 ---
    for placeholder, (math_type, expr) in formulas.items():
        try:
            if math_type == 'block_inline':
                path, w, h = render_latex(expr, fontsize=13, dpi=200)
            else:
                path, w, h = render_latex(expr, fontsize=11, dpi=200)

            # valign: 텍스트 베이스라인에 맞추기 위한 수직 오프셋
            valign = -(h * 0.30)
            # Windows 경로의 백슬래시를 슬래시로 변환 (XML 안전)
            safe_path = path.replace('\\', '/')
            img_tag = (
                f'<img src="{safe_path}" '
                f'width="{w:.1f}" height="{h:.1f}" '
                f'valign="{valign:.1f}"/>'
            )
            text = text.replace(placeholder, img_tag)
        except Exception as e:
            # 렌더링 실패 시 원본 수식을 이탤릭으로 표시
            escaped_expr = expr.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text = text.replace(placeholder, f'<i>{escaped_expr}</i>')

    return text


# ============================================================
# 마크다운 테이블 파싱
# ============================================================
def parse_table(lines, styles):
    """마크다운 테이블 라인들을 reportlab Table 객체로 변환"""
    rows = []
    for line in lines:
        line = line.strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|'):
            line = line[:-1]

        cells = [c.strip() for c in line.split('|')]

        # 구분선 (---) 스킵
        if all(re.match(r'^[-:]+$', c) for c in cells):
            continue

        rows.append(cells)

    if not rows:
        return None

    # 첫 행은 헤더
    header = rows[0]
    data_rows = rows[1:]

    page_width = A4[0] - 50*mm
    n_cols = len(header)
    col_width = page_width / n_cols

    # 테이블 데이터 구성
    table_data = []

    # 헤더 행
    header_cells = []
    for cell in header:
        header_cells.append(Paragraph(convert_inline(cell), styles['KorTableHeader']))
    table_data.append(header_cells)

    # 데이터 행
    for row in data_rows:
        row_cells = []
        for i, cell in enumerate(row):
            if i < n_cols:
                row_cells.append(Paragraph(convert_inline(cell), styles['KorTableCell']))
        # 열 수 맞추기
        while len(row_cells) < n_cols:
            row_cells.append(Paragraph('', styles['KorTableCell']))
        table_data.append(row_cells)

    col_widths = [col_width] * n_cols

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4285F4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    return table


# ============================================================
# 블록 수식 렌더링 ($$...$$ 독립 블록)
# ============================================================
def render_block_formula(expr):
    """
    블록 수식을 중앙 정렬된 Image flowable로 렌더링한다.
    연한 배경 + 패딩이 있는 테이블로 감싸 깔끔하게 표시.
    """
    try:
        path, w, h = render_latex(expr, fontsize=16, dpi=250, is_block=True)

        # 페이지 폭에 맞추기
        max_w = A4[0] - 60*mm
        if w > max_w:
            scale = max_w / w
            w *= scale
            h *= scale

        img = Image(path, width=w, height=h)

        # 수식을 연한 배경의 테이블로 감싸기
        formula_table = Table([[img]], colWidths=[A4[0] - 50*mm])
        formula_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FAFBFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#D0D8E8')),
        ]))

        return formula_table
    except Exception as e:
        # 실패 시 텍스트로 폴백
        escaped = expr.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        styles = create_styles()
        return Paragraph(f'<i>[Formula] {escaped}</i>', styles['KorBody'])


# ============================================================
# 마크다운 파서 & PDF 생성
# ============================================================
def md_to_pdf(md_path, pdf_path):
    """마크다운 파일을 PDF로 변환"""
    styles = create_styles()

    # 마크다운 파일 읽기
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    md_dir = os.path.dirname(os.path.abspath(md_path))
    elements = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        stripped = line.strip()

        # 빈 줄
        if not stripped:
            i += 1
            continue

        # === 블록 수식 ($$로 시작하는 독립 블록) ===
        if stripped == '$$':
            # 여러 줄 블록 수식: $$ ... $$
            formula_lines = []
            i += 1
            while i < len(lines):
                fline = lines[i].rstrip('\n').strip()
                if fline == '$$':
                    i += 1
                    break
                formula_lines.append(fline)
                i += 1
            formula_expr = ' '.join(formula_lines)
            if formula_expr:
                elements.append(Spacer(1, 8))
                elements.append(render_block_formula(formula_expr))
                elements.append(Spacer(1, 8))
            continue

        if stripped.startswith('$$') and stripped.endswith('$$') and len(stripped) > 4:
            # 한 줄 블록 수식: $$...$$
            formula_expr = stripped[2:-2].strip()
            if formula_expr:
                elements.append(Spacer(1, 8))
                elements.append(render_block_formula(formula_expr))
                elements.append(Spacer(1, 8))
            i += 1
            continue

        # 코드 블록
        if stripped.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines):
                code_line = lines[i].rstrip('\n')
                if code_line.strip().startswith('```'):
                    i += 1
                    break
                # 탭을 공백으로
                code_line = code_line.replace('\t', '    ')
                # HTML 특수문자 이스케이프
                code_line = code_line.replace('&', '&amp;')
                code_line = code_line.replace('<', '&lt;').replace('>', '&gt;')
                # 공백 보존
                code_line = code_line.replace(' ', '&nbsp;')
                code_lines.append(code_line)
                i += 1

            if code_lines:
                code_text = '<br/>'.join(code_lines)
                elements.append(Spacer(1, 4))
                # 코드 블록을 배경색이 있는 테이블로 감싸기
                code_para = Paragraph(
                    f'<font face="Courier" size="8.5">{code_text}</font>',
                    styles['KorCode']
                )
                code_table = Table([[code_para]], colWidths=[A4[0] - 50*mm])
                code_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F5F5F5')),
                    ('BORDER', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                elements.append(code_table)
                elements.append(Spacer(1, 4))
            continue

        # 테이블 (| 로 시작하는 연속 줄)
        if stripped.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1

            table = parse_table(table_lines, styles)
            if table:
                elements.append(Spacer(1, 4))
                elements.append(table)
                elements.append(Spacer(1, 4))
            continue

        # 제목 (H1 ~ H4)
        if stripped.startswith('#'):
            match = re.match(r'^(#{1,4})\s+(.+)$', stripped)
            if match:
                level = len(match.group(1))
                title_text = convert_inline(match.group(2))
                if level == 1:
                    elements.append(Spacer(1, 6))
                    elements.append(Paragraph(title_text, styles['KorTitle']))
                    # 타이틀 아래 구분선
                    elements.append(HRFlowable(
                        width="100%", thickness=2,
                        color=HexColor('#4285F4'), spaceBefore=2, spaceAfter=10
                    ))
                elif level == 2:
                    elements.append(Paragraph(title_text, styles['KorH2']))
                    elements.append(HRFlowable(
                        width="100%", thickness=1,
                        color=HexColor('#CCCCCC'), spaceBefore=1, spaceAfter=6
                    ))
                elif level == 3:
                    elements.append(Paragraph(title_text, styles['KorH3']))
                elif level == 4:
                    elements.append(Paragraph(title_text, styles['KorH4']))
                i += 1
                continue

        # 수평선
        if stripped in ('---', '***', '___'):
            elements.append(HRFlowable(
                width="100%", thickness=1,
                color=HexColor('#CCCCCC'), spaceBefore=6, spaceAfter=6
            ))
            i += 1
            continue

        # 이미지
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', stripped)
        if img_match:
            alt_text = img_match.group(1)
            img_file = img_match.group(2)
            img_path = os.path.join(md_dir, img_file)

            if os.path.exists(img_path):
                try:
                    img_reader = ImageReader(img_path)
                    iw, ih = img_reader.getSize()

                    # 페이지 폭에 맞추기 (최대 폭)
                    max_width = A4[0] - 50*mm
                    max_height = A4[1] * 0.45  # 페이지 높이의 45%

                    ratio = min(max_width / iw, max_height / ih)
                    display_w = iw * ratio
                    display_h = ih * ratio

                    elements.append(Spacer(1, 6))
                    img_obj = Image(img_path, width=display_w, height=display_h)
                    elements.append(img_obj)

                    if alt_text:
                        elements.append(Paragraph(
                            convert_inline(alt_text), styles['KorCaption']
                        ))
                    elements.append(Spacer(1, 6))
                except Exception as e:
                    elements.append(Paragraph(
                        f'[Image Error: {img_file} - {e}]', styles['KorBody']
                    ))
            else:
                elements.append(Paragraph(
                    f'[Image Not Found: {img_file}]', styles['KorBody']
                ))
            i += 1
            continue

        # 인용문 (>)
        if stripped.startswith('>'):
            quote_text = stripped.lstrip('>').strip()
            quote_text = convert_inline(quote_text)
            # 인용문을 왼쪽 파란 테두리가 있는 테이블로 표현
            quote_para = Paragraph(quote_text, styles['KorBlockquote'])
            quote_table = Table([[quote_para]], colWidths=[A4[0] - 60*mm])
            quote_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F0F4FF')),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LINEBEFOREBORDER', (0, 0), (0, -1)),
                ('LINEBEFORE', (0, 0), (0, -1), 3, HexColor('#4285F4')),
            ]))
            elements.append(Spacer(1, 4))
            elements.append(quote_table)
            elements.append(Spacer(1, 4))
            i += 1
            continue

        # 번호 목록
        num_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if num_match:
            num = num_match.group(1)
            text = convert_inline(num_match.group(2))
            elements.append(Paragraph(
                f'<font face="{FONT_NAME_BOLD}">{num}.</font> {text}',
                styles['KorBullet']
            ))
            i += 1
            continue

        # 글머리표 (- 또는 *)
        bullet_match = re.match(r'^(\s*)([-*])\s+(.+)$', stripped)
        if bullet_match:
            indent = len(bullet_match.group(1))
            text = convert_inline(bullet_match.group(3))
            if indent >= 2:
                elements.append(Paragraph(
                    f'&nbsp;&nbsp;- {text}', styles['KorBullet2']
                ))
            else:
                elements.append(Paragraph(
                    f'\u2022 {text}', styles['KorBullet']
                ))
            i += 1
            continue

        # 일반 텍스트 (연속된 줄을 하나의 단락으로)
        para_lines = []
        while i < len(lines):
            cur = lines[i].rstrip('\n').strip()
            if not cur:
                i += 1
                break
            if cur.startswith('#') or cur.startswith('|') or cur.startswith('```'):
                break
            if cur == '$$' or (cur.startswith('$$') and cur.endswith('$$')):
                break
            if cur.startswith('!['):
                break
            if cur in ('---', '***', '___'):
                break
            if cur.startswith('>'):
                break
            if re.match(r'^\d+\.\s+', cur):
                break
            if re.match(r'^[-*]\s+', cur):
                break
            para_lines.append(cur)
            i += 1

        if para_lines:
            text = ' '.join(para_lines)
            text = convert_inline(text)
            elements.append(Paragraph(text, styles['KorBody']))

    # PDF 생성
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=25*mm,
        rightMargin=25*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
        title=os.path.basename(md_path).replace('.md', ''),
    )

    # 페이지 번호 추가 콜백
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"- {page_num} -"
        canvas.saveState()
        canvas.setFont(FONT_NAME, 8)
        canvas.setFillColor(grey)
        canvas.drawCentredString(A4[0] / 2, 12*mm, text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return pdf_path


# ============================================================
# 메인 실행
# ============================================================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    md_files = [
        '01_bias_variance_tradeoff.md',
        '02_no_free_lunch_demo.md',
        '03_cross_validation_demo.md',
    ]

    # 수식 렌더러 초기화
    init_formula_renderer()
    print(f"[Init] Formula temp dir: {FORMULA_TEMP_DIR}")

    try:
        for md_file in md_files:
            md_path = os.path.join(base_dir, md_file)
            pdf_file = md_file.replace('.md', '.pdf')
            pdf_path = os.path.join(base_dir, pdf_file)

            if not os.path.exists(md_path):
                print(f"[SKIP] {md_file} not found")
                continue

            print(f"[Converting] {md_file} -> {pdf_file} ...")
            try:
                md_to_pdf(md_path, pdf_path)
                file_size = os.path.getsize(pdf_path)
                print(f"[Done] {pdf_file} ({file_size:,} bytes)")
            except Exception as e:
                print(f"[Error] {md_file}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n[Stats] Rendered {len(FORMULA_CACHE)} unique formulas")
    finally:
        # 임시 파일 정리
        cleanup_formula_renderer()
        print("[Cleanup] Temp files removed")

    print("\nAll conversions complete.")
