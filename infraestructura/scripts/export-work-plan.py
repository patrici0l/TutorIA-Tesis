"""Exporta el plan consolidado a PDF con tablas y saltos de página explícitos."""

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
NAVY = colors.HexColor('#123451')
BLUE = colors.HexColor('#005aa8')
MUTED = colors.HexColor('#506577')
GOLD = colors.HexColor('#efb32a')
WIDTH, HEIGHT = landscape(A4)


def register_fonts():
    # Usa fuentes locales; el PDF no depende de conexiones ni recursos remotos.
    for directory in [Path('C:/Windows/Fonts'), Path('/usr/share/fonts/truetype/dejavu')]:
        regular = directory / ('arial.ttf' if directory.name == 'Fonts' else 'DejaVuSans.ttf')
        bold = directory / ('arialbd.ttf' if directory.name == 'Fonts' else 'DejaVuSans-Bold.ttf')
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont('Plan', str(regular)))
            pdfmetrics.registerFont(TTFont('PlanBold', str(bold)))
            return 'Plan', 'PlanBold'
    return 'Helvetica', 'Helvetica-Bold'


def export(source: Path, destination: Path):
    regular, bold = register_fonts()
    body = ParagraphStyle('Body', fontName=regular, fontSize=10.1, leading=14,
                          textColor=NAVY, spaceAfter=9)
    title = ParagraphStyle('Title', parent=body, fontName=bold, fontSize=26,
                           leading=31, spaceAfter=14)
    heading = ParagraphStyle('Heading', parent=body, fontName=bold, fontSize=17,
                             leading=22, spaceAfter=13)
    cell = ParagraphStyle('Cell', parent=body, fontSize=9.1, leading=12.1,
                          spaceAfter=0, splitLongWords=True, alignment=TA_LEFT)
    small_cell = ParagraphStyle('Reference', parent=cell, fontSize=8.5, leading=11.2)
    header = ParagraphStyle('Header', parent=cell, fontName=bold, textColor=colors.white)
    pages = source.read_text(encoding='utf-8').split('<!-- page -->')
    available = WIDTH - 64
    story = []

    def paragraph(text, style=body):
        return Paragraph(escape(text).replace('&lt;br&gt;', '<br/>'), style)

    def add_table(rows, page_index):
        if page_index in (1, 2, 3, 4):
            widths = [96, 99, 185, 195, available - 575]
        elif page_index == 5:
            widths = [115, 122, 320, available - 557]
        elif page_index == 6:
            widths = [46, 113, 231, 183, available - 573]
        elif page_index == 7:
            widths = [105, 155, 255, available - 515]
        elif page_index >= 8:
            widths = [34, 386, available - 420]
        else:
            widths = [190, 190, available - 380]
        style = small_cell if page_index >= 8 else cell
        data = [[paragraph(v, header if i == 0 else style) for v in row]
                for i, row in enumerate(rows)]
        table = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor('#f0f5fa'), colors.white]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5 if page_index >= 8 else 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5 if page_index >= 8 else 7),
            ('LINEBELOW', (0, 0), (-1, 0), 2, GOLD),
            ('LINEBELOW', (0, 1), (-1, -1), .35, colors.HexColor('#d6e1eb')),
        ]))
        story.extend([table, Spacer(1, 12)])

    for page_index, section in enumerate(pages):
        if page_index:
            story.append(PageBreak())
        lines = section.strip().splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith('|'):
                rows = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    row = [v.strip() for v in lines[i].strip().strip('|').split('|')]
                    if not all(re.fullmatch(r':?-+:?', v) for v in row):
                        rows.append(row)
                    i += 1
                add_table(rows, page_index)
                continue
            if line.startswith('# '):
                story.append(paragraph(line[2:], title))
            elif line.startswith('## '):
                story.append(KeepTogether([paragraph(line[3:], heading), Spacer(1, 1)]))
            else:
                story.append(paragraph(line))
            i += 1

    def frame(canvas, doc):
        canvas.setFillColor(BLUE)
        canvas.rect(32, HEIGHT - 27, 28, 3, stroke=0, fill=1)
        canvas.setFillColor(MUTED)
        canvas.setFont(regular, 8)
        canvas.drawString(68, HEIGHT - 27, 'TUTORIA-LUCERO  /  PLAN Y EVIDENCIA DE AVANCE')
        canvas.setStrokeColor(colors.HexColor('#d6e1eb'))
        canvas.line(32, 27, WIDTH - 32, 27)
        canvas.setFont(regular, 7.7)
        canvas.drawString(32, 15, 'Corte: 25/10/2026  |  America/Guayaquil  |  TutorIA-Lucero')
        canvas.drawRightString(WIDTH - 32, 15, f'{doc.page} / {len(pages)}')

    destination.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(destination), pagesize=(WIDTH, HEIGHT),
                            rightMargin=32, leftMargin=32, topMargin=48, bottomMargin=40,
                            title='TutorIA-Lucero - Plan de trabajo y estado verificable',
                            author='TutorIA-Lucero', pageCompression=1)
    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    print(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'documentacion/PLAN_ACTUAL.md')
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'output/pdf/plan_trabajo_tutoria_2026-10-25.pdf')
    args = parser.parse_args()
    export(args.source, args.output)
