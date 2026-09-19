"""
Script to generate the official executive 16:9 presentation (.pptx)
for CosmoHackathon 2026 defense: 'Топливный космоконтур 2035'.
Ultra-high contrast, WCAG AAA compliant, executive aerospace layout,
embedded QR code, verified mathematical KPIs, and crisp visual hierarchy.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Ensure QR code exists
import qrcode

QR_PATH = "qr_code.png"
URL = "https://zahar713713-dot.github.io/Cosmo-Hackaton-2026/"
qr = qrcode.QRCode(box_size=10, border=2)
qr.add_data(URL)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save(QR_PATH)

# Dimensions: 16:9 widescreen
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Executive Aerospace Palette (Light Theme, high contrast, clean & authoritative)
BG_CANVAS = RGBColor(248, 250, 252)         # Slate 50
CARD_BG = RGBColor(255, 255, 255)           # Pure White
CARD_BORDER = RGBColor(226, 232, 240)       # Slate 200
CARD_BORDER_ACCENT = RGBColor(186, 230, 253) # Light Sky border

TEXT_PRIMARY = RGBColor(15, 23, 42)         # Slate 900 (Deep Navy Charcoal)
TEXT_SECONDARY = RGBColor(51, 65, 85)       # Slate 700
TEXT_MUTED = RGBColor(100, 116, 139)        # Slate 500

ACCENT_BLUE = RGBColor(2, 132, 199)         # Sky 600
ACCENT_GREEN = RGBColor(16, 149, 93)        # Emerald 600 (Savings, SLA 100%)
ACCENT_GREEN_BG = RGBColor(236, 253, 245)   # Soft Emerald Tint
ACCENT_AMBER = RGBColor(180, 83, 9)         # Amber 700
ACCENT_AMBER_BG = RGBColor(254, 243, 199)   # Soft Amber Tint
ACCENT_PURPLE = RGBColor(126, 34, 206)      # Purple 700 (ISRU)
ACCENT_PURPLE_BG = RGBColor(250, 245, 255)  # Soft Purple Tint

TABLE_HEADER_BG = RGBColor(30, 41, 59)      # Slate 800
TABLE_HEADER_TEXT = RGBColor(255, 255, 255)
TABLE_ROW_ALT = RGBColor(248, 250, 252)


def build_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    def add_base_slide(tag: str, title: str, timing: str):
        slide = prs.slides.add_slide(blank_layout)

        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_CANVAS
        bg.line.fill.background()

        # Header Box
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.2), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_tag = tf.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_BLUE

        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_PRIMARY

        # Timing Badge (Top Right)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.0), Inches(0.45), Inches(1.5), Inches(0.42))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(241, 245, 249)
        badge.line.color.rgb = RGBColor(203, 213, 225)
        badge.line.width = Pt(1)
        tf_b = badge.text_frame
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.text = f"⏱ {timing}"
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = TEXT_SECONDARY

        return slide

    def add_card(slide, x, y, w, h, border_color=CARD_BORDER, bg_color=CARD_BG, top_strip_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5 if top_strip_color else 1)

        if top_strip_color:
            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, Inches(0.08))
            bar.fill.solid()
            bar.fill.fore_color.rgb = top_strip_color
            bar.line.fill.background()

        return shape

    # =========================================================================
    # SLIDE 1: Title Slide + Live Demo QR Code (0:00 - 0:45)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_CANVAS
    bg1.line.fill.background()

    # Left Column: Hero Details
    left_card = add_card(s1, Inches(0.8), Inches(0.7), Inches(7.8), Inches(6.1), border_color=RGBColor(203, 213, 225), top_strip_color=ACCENT_BLUE)
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(7.0), Inches(5.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "КОСМОХАКАТОН 2026 // САНКТ-ПЕТЕРБУРГ"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    p = tf1.add_paragraph()
    p.text = "ТОПЛИВНЫЙ КОСМОКОНТУР (2035)"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "Оптимизация материального баланса, стоимости жизненного цикла (LCC) и устойчивости снабжения цислунарного Орбитального топливного узла (ОТУ) на 2035–2040 гг."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_SECONDARY
    p.space_after = Pt(20)

    # 3 Pill Badges
    p = tf1.add_paragraph()
    p.text = "★ ЧИСТАЯ ЭКОНОМИЯ: 11.81% (–1 096.8 МЛН У.Е. NPV / –1 384.5 МЛН LCC)\n" \
             "★ КРИТИЧЕСКИЙ SLA: 100.0% // ПИЛОТИРУЕМЫЕ МИССИИ ЗАЩИЩЕНЫ НА 100%\n" \
             "★ ГОТОВНОСТЬ TRL-4/5: 792/792 МАТЕМАТИЧЕСКИХ ИНВАРИАНТА ВЕРИФИЦИРОВАНО"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(24)

    p = tf1.add_paragraph()
    p.text = "Команда: Whatrushki | Федеральный проект «Кадры для космоса»"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # Right Column: QR Code Card
    right_card = add_card(s1, Inches(8.8), Inches(0.7), Inches(3.7), Inches(6.1), border_color=RGBColor(186, 230, 253), bg_color=CARD_BG, top_strip_color=ACCENT_GREEN)
    tb_qr = s1.shapes.add_textbox(Inches(9.0), Inches(0.95), Inches(3.3), Inches(1.1))
    tf_qr = tb_qr.text_frame
    tf_qr.word_wrap = True

    p = tf_qr.paragraphs[0]
    p.text = "ИНТЕРАКТИВНЫЙ ЦИФРОВОЙ КОНТУР"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.alignment = PP_ALIGN.CENTER

    p = tf_qr.add_paragraph()
    p.text = "Отсканируйте камерой смартфона для живого тестирования прямо сейчас:"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_SECONDARY
    p.alignment = PP_ALIGN.CENTER

    # Add QR Code image
    if os.path.exists(QR_PATH):
        s1.shapes.add_picture(QR_PATH, Inches(9.45), Inches(2.2), Inches(2.4), Inches(2.4))

    tb_url = s1.shapes.add_textbox(Inches(9.0), Inches(4.75), Inches(3.3), Inches(1.8))
    tf_u = tb_url.text_frame
    tf_u.word_wrap = True

    p = tf_u.paragraphs[0]
    p.text = "zahar713713-dot.github.io/Cosmo-Hackaton-2026"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.alignment = PP_ALIGN.CENTER

    p = tf_u.add_paragraph()
    p.text = "✓ 100% Zero-Backend (клиентский расчет)\n✓ Адаптировано под мобильные устройства\n✓ Ползунки, стресс-тест и экспорт Excel"
    p.font.size = Pt(9.5)
    p.font.color.rgb = TEXT_MUTED
    p.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: Challenge & Supply Architecture (0:45 - 1:45)
    # =========================================================================
    s2 = add_base_slide(
        "СТРУКТУРА СИСТЕМЫ И ОГРАНИЧЕНИЯ ТЗ",
        "ФИЗИЧЕСКИЙ УЗЕЛ ОТУ И 5 КАНАЛОВ СНАБЖЕНИЯ 2035–2040 ГГ.",
        "0:45 – 1:45"
    )

    # 3 Architecture Cards
    # Card 1: Orbital Depot
    c1 = add_card(s2, Inches(0.8), Inches(1.65), Inches(3.7), Inches(5.1), top_strip_color=ACCENT_BLUE)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(3.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ОРБИТАЛЬНЫЙ ТОПЛИВНЫЙ УЗЕЛ (ОТУ)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(8)

    items = [
        ("Вместимость баков", "70 тонн (база) → 120 тонн (после ZBO)"),
        ("Страховой буфер", "45 суток непрерывного спроса R_45d = ceil(D·45/365)"),
        ("Потери throughput", "4.5% (базовые) → 1.2% (ZBO-модернизация)"),
        ("Тариф на хранение", "0.72 млн у.е./т·год на средний остаток топлива"),
        ("Ключевой вызов", "Спрос растет со 100 т (2035) до 390 т (2040) — в 3.9 раза! Без ZBO баки переполняются, а потери превышают лимит."),
    ]
    for label, desc in items:
        p = tf.add_paragraph()
        p.text = f"• {label}: "
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_PRIMARY
        # add desc
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # Card 2: 5 Delivery Channels
    c2 = add_card(s2, Inches(4.8), Inches(1.65), Inches(4.5), Inches(5.1), top_strip_color=ACCENT_AMBER)
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(1.85), Inches(4.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "5 ТРАНСПОРТНЫХ КАНАЛОВ ПОСТАВКИ"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(8)

    channels = [
        ("Канал A (Earth-Core)", "190 т/год | Тариф 6.2 + 0.45 бронь | TOP 70% (85%) | Lead time 12 мес. Фундамент земного плеча."),
        ("Канал B (Earth-Flex)", "110 т/год | Тариф 8.9 + 0.15 бронь | TOP 0% | Lead time 4 мес. Оперативная балансировка."),
        ("Канал C (Earth-New)", "130 т/год | 90М опцион + 270М ввод | Тариф 7.1 + 0.30 | TOP 50% | Lead time 18-24 мес."),
        ("Канал D (Lunar-ISRU)", "120 т/год | CAPEX 1 250М (2037) | Тариф 3.0, нулевая бронь! | Старт с 2038 г. Лунный суверенитет."),
        ("Канал E (Emergency)", "80 т/год | Тариф 13.8 + 0.35 | Lead time 6 нед. Жесткий лимит ТЗ: не более 2 лет подряд."),
    ]
    for ch, d in channels:
        p = tf.add_paragraph()
        p.text = f"• {ch}: "
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_PRIMARY
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # Card 3: Requirements & Stakeholders
    c3 = add_card(s2, Inches(9.6), Inches(1.65), Inches(2.9), Inches(5.1), top_strip_color=ACCENT_GREEN)
    tb = s2.shapes.add_textbox(Inches(9.8), Inches(1.85), Inches(2.5), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "НОРМАТИВЫ И ДИРЕКТИВНЫЙ SLA"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)

    crit = [
        ("Критический спрос", "SLA ≥ 99.0%\nПилотируемая лунная база и безопасность космонавтов."),
        ("Совокупный спрос", "SLA ≥ 97.0%\nГрузовые рейсы, геостационарные спутники, буксиры."),
        ("Лимит CAPEX 2037", "≤ 1 800.0 млн у.е.\nПервый этап финансирования."),
        ("Полный лимит CAPEX", "≤ 2 800.0 млн у.е.\nСовокупная программа 2040."),
        ("Потолок потерь", "≤ 2.0% при стрессе (ТЗ)"),
    ]
    for c_lbl, c_val in crit:
        p = tf.add_paragraph()
        p.text = f"★ {c_lbl}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        p = tf.add_paragraph()
        p.text = c_val
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 3: Mathematical Model & Net Savings (1:45 - 3:00)
    # =========================================================================
    s3 = add_base_slide(
        "МАТЕМАТИЧЕСКАЯ ОПТИМИЗАЦИЯ NASA MILP",
        "ЭКОНОМИЯ 11.81% (–1 096.8 МЛН У.Е. NPV) ПРОТИВ РЕГЛАМЕНТА",
        "1:45 – 3:00"
    )

    # 3 Big Stat KPI Blocks
    kpi1 = add_card(s3, Inches(0.8), Inches(1.65), Inches(3.7), Inches(1.3), border_color=RGBColor(167, 243, 208), bg_color=ACCENT_GREEN_BG)
    tb = s3.shapes.add_textbox(Inches(0.95), Inches(1.75), Inches(3.4), Inches(1.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ЧИСТАЯ ЭКОНОМИЯ NPV (r=8%)"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "–11.81% (–1 096.76 млн)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p = tf.add_paragraph()
    p.text = "8 188.52 млн у.е. против 9 285.28 млн регламента"
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_SECONDARY

    kpi2 = add_card(s3, Inches(4.8), Inches(1.65), Inches(3.7), Inches(1.3), border_color=RGBColor(186, 230, 253), bg_color=RGBColor(240, 249, 255))
    tb = s3.shapes.add_textbox(Inches(4.95), Inches(1.75), Inches(3.4), Inches(1.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ЭКОНОМИЯ ЗАТРАТ ЖИЗНЕННОГО ЦИКЛА (LCC)"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "–1 384.48 млн у.е."
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p = tf.add_paragraph()
    p.text = "10 206.17 млн у.е. против 11 590.65 млн регламента"
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_SECONDARY

    kpi3 = add_card(s3, Inches(8.8), Inches(1.65), Inches(3.7), Inches(1.3), border_color=RGBColor(254, 215, 170), bg_color=ACCENT_AMBER_BG)
    tb = s3.shapes.add_textbox(Inches(8.95), Inches(1.75), Inches(3.4), Inches(1.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ШТРАФЫ TAKE-OR-PAY"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf.add_paragraph()
    p.text = "0.00 млн у.е. (100% УСТРАНЕНЫ)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p = tf.add_paragraph()
    p.text = "Синхронизация брони и отбора топлива"
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_SECONDARY

    # Comparative Table
    tbl_card = add_card(s3, Inches(0.8), Inches(3.15), Inches(11.7), Inches(3.6))
    
    rows, cols = 7, 5
    table_shape = s3.shapes.add_table(rows, cols, Inches(0.9), Inches(3.25), Inches(11.5), Inches(3.3))
    table = table_shape.table
    table.columns[0].width = Inches(3.3)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.2)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(2.0)

    headers = ["Показатель эффективности", "Регламент ТЗ", "NASA MILP (Наш выбор)", "Дельта (Экономия)", "Эффект / Статус"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(10)
        p.font.color.rgb = TABLE_HEADER_TEXT

    table_data = [
        ("Приведенная стоимость затрат (NPV, r=8%)", "9 285.28 млн у.е.", "8 188.52 млн у.е.", "–1 096.76 млн", "Экономия 11.81%"),
        ("Совокупные затраты жизненного цикла (LCC)", "11 590.65 млн у.е.", "10 206.17 млн у.е.", "–1 384.48 млн", "Экономия 11.94%"),
        ("Затраты на закупку и бронирование КРТ", "9 735.65 млн у.е.", "8 411.17 млн у.е.", "–1 324.48 млн", "Оптимизация каналов"),
        ("Штрафы за недобор Take-or-Pay", "342.10 млн у.е.", "0.00 млн у.е.", "–342.10 млн", "Ликвидированы 100%"),
        ("Затраты на хранение топлива на ОТУ", "425.00 млн у.е.", "365.00 млн у.е.", "–60.00 млн", "Минимизация затоваривания"),
        ("Средний уровень сервиса (SLA Total / Critical)", "97.4% / 100.0%", "97.8% / 100.0%", "+0.4% / 0.0%", "Нормативы перевыполнены"),
    ]

    for row_idx, data_row in enumerate(table_data, start=1):
        for col_idx, val in enumerate(data_row):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_ROW_ALT if row_idx % 2 == 0 else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_PRIMARY
            elif col_idx == 2 or col_idx == 3:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            else:
                p.font.color.rgb = TEXT_SECONDARY

    # =========================================================================
    # SLIDE 4: Investment Portfolio & Lunar Sovereignty (3:00 - 4:15)
    # =========================================================================
    s4 = add_base_slide(
        "КАПИТАЛЬНЫЕ ЗАТРАТЫ (CAPEX) И СТРАТЕГИЯ",
        "СТРАТЕГИЧЕСКИЙ ИНВЕСТ-ПОРТФЕЛЬ И ЛУННЫЙ СУВЕРЕНИТЕТ",
        "3:00 – 4:15"
    )

    # 3 Strategic Investment Columns
    # 1. ZBO
    add_card(s4, Inches(0.8), Inches(1.65), Inches(3.7), Inches(4.3), border_color=RGBColor(167, 243, 208), top_strip_color=ACCENT_GREEN)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(3.3), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "1. ZBO-МОДЕРНИЗАЦИЯ (ВВОД В 2036 Г.)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(6)

    zbo_points = [
        ("Инвестиции CAPEX", "180.0 млн у.е. (в 2036 г.)"),
        ("Операционные OPEX", "+12.0 млн у.е./год"),
        ("Снижение потерь", "С 4.5% до 1.2% (экономия ~35 т КРТ/год)"),
        ("Расширение баков", "С 70 т до 120 т (гарантия буфера 45 дней)"),
        ("Срок окупаемости", "2.3 года! Полная окупаемость уже в 2038 г."),
        ("Значение для ТЗ", "Единственный способ пройти стресс-тест ТЗ (потери ≤2.0%)."),
    ]
    for l, v in zbo_points:
        p = tf.add_paragraph()
        p.text = f"• {l}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = v
        r.font.bold = False
        r.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(3)

    # 2. Lunar-ISRU
    add_card(s4, Inches(4.8), Inches(1.65), Inches(3.7), Inches(4.3), border_color=RGBColor(233, 213, 255), top_strip_color=ACCENT_PURPLE)
    tb = s4.shapes.add_textbox(Inches(5.0), Inches(1.85), Inches(3.3), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "2. ДОБЫЧА LUNAR-ISRU (ВВОД В 2038 Г.)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(6)

    isru_points = [
        ("Инвестиции CAPEX", "1 250.0 млн у.е. (транш 2037 г.)"),
        ("Операционные OPEX", "+70.0 млн у.е./год"),
        ("Себестоимость КРТ", "3.0 млн у.е./т (в 2.5–4.5 раза дешевле Земли!)"),
        ("Тариф бронирования", "0.0 млн у.е. (собственная инфраструктура)"),
        ("Доля лунного топлива", "28.4% к 2040 г. (120 т/год из 390 т)"),
        ("Стратегический эффект", "Переход к ресурсному суверенитету и резкое падение зависимости от земных РН."),
    ]
    for l, v in isru_points:
        p = tf.add_paragraph()
        p.text = f"• {l}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = v
        r.font.bold = False
        r.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(3)

    # 3. Earth-New
    add_card(s4, Inches(8.8), Inches(1.65), Inches(3.7), Inches(4.3), border_color=RGBColor(254, 215, 170), top_strip_color=ACCENT_AMBER)
    tb = s4.shapes.add_textbox(Inches(9.0), Inches(1.85), Inches(3.3), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "3. ОПЦИОН EARTH-NEW (КАНАЛ C)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(6)

    c_points = [
        ("Стоимость опциона", "90.0 млн у.е. (2035 г.)"),
        ("Стоимость исполнения", "270.0 млн у.е. (Суммарно 360.0 млн)"),
        ("Решение оптимизатора", "НЕ активировать в базовом сценарии"),
        ("Обоснование отказа", "Lunar-ISRU дешевле (3.0 vs 7.1 млн/т). Активация Канала C избыточна и увеличивает LCC на +260 млн."),
        ("Роль в программе", "Резервный инструмент хеджирования (real option) при задержке развертывания Lunar-ISRU."),
    ]
    for l, v in c_points:
        p = tf.add_paragraph()
        p.text = f"• {l}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = v
        r.font.bold = False
        r.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(3)

    # Bottom Full-width Compliance Strip
    strip = add_card(s4, Inches(0.8), Inches(6.1), Inches(11.7), Inches(0.75), border_color=RGBColor(186, 230, 253), bg_color=CARD_BG)
    tb = s4.shapes.add_textbox(Inches(1.0), Inches(6.15), Inches(11.3), Inches(0.65))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "БЮДЖЕТНАЯ ДИСЦИПЛИНА И СОБЛЮДЕНИЕ ПОТОЛКОВ ТЗ:"
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = ACCENT_BLUE

    p = tf.add_paragraph()
    p.text = "✔ CAPEX до конца 2037 г.: 1 430.0 млн у.е. (Лимит ТЗ 1 800.0 млн | Запас надежности +370.0 млн)    " \
             "✔ Совокупный CAPEX 2040 г.: 1 430.0 млн у.е. (Лимит ТЗ 2 800.0 млн | Запас +1 370.0 млн)"
    p.font.bold = True
    p.font.size = Pt(9.5)
    p.font.color.rgb = ACCENT_GREEN

    # =========================================================================
    # SLIDE 5: Stress-Testing & Resilience (4:15 - 5:30)
    # =========================================================================
    s5 = add_base_slide(
        "СТРЕСС-ТЕСТИРОВАНИЕ И УПРАВЛЕНИЕ РИСКАМИ",
        "ПРОВЕРКА ОТКАЗОУСТОЙЧИВОСТИ: КРИТИЧЕСКИЙ SLA 100.00%",
        "4:15 – 5:30"
    )

    # Left Card: Stress Definition
    add_card(s5, Inches(0.8), Inches(1.65), Inches(3.6), Inches(5.1), top_strip_color=ACCENT_AMBER)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(3.2), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ПАРАМЕТРЫ ОБЯЗАТЕЛЬНОГО СТРЕСС-ТЕСТА"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(8)

    st_items = [
        ("Срыв земных поставок", "–15% во все годы стресс-сценария"),
        ("Инфляция тарифов", "+25% на все переменные тарифы"),
        ("Срыв отдачи ISRU", "2038: 55% мощности (66 т)\n2039: 75% мощности (90 т)"),
        ("Рост директивного спроса", "+15% во все годы планирования"),
        ("Условия прохождения ТЗ", "1) Покрытие критического спроса\n2) Потери испарения ≤ 2.0%\n3) Лимит Emergency ≤ 2 лет подряд"),
    ]
    for l, v in st_items:
        p = tf.add_paragraph()
        p.text = f"• {l}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = v
        r.font.bold = False
        r.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # Right Top: Results Cards
    res_kpi1 = add_card(s5, Inches(4.7), Inches(1.65), Inches(3.7), Inches(1.4), border_color=RGBColor(167, 243, 208), bg_color=ACCENT_GREEN_BG)
    tb = s5.shapes.add_textbox(Inches(4.85), Inches(1.75), Inches(3.4), Inches(1.2))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "КРИТИЧЕСКИЙ SLA В СТРЕССЕ"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p = tf.add_paragraph()
    p.text = "100.00% (БЕЗ ДЕФИЦИТА)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p = tf.add_paragraph()
    p.text = "Пилотируемые миссии защищены абсолютно"
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_SECONDARY

    res_kpi2 = add_card(s5, Inches(8.7), Inches(1.65), Inches(3.8), Inches(1.4), border_color=RGBColor(186, 230, 253), bg_color=RGBColor(240, 249, 255))
    tb = s5.shapes.add_textbox(Inches(8.85), Inches(1.75), Inches(3.5), Inches(1.2))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "ПОТЕРИ THROUGHPUT ПРИ СТРЕССЕ"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p = tf.add_paragraph()
    p.text = "1.20% (НОРМАТИВ ТЗ ≤ 2.0%)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p = tf.add_paragraph()
    p.text = "Строгое соответствие критерию 14 кейса"
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_SECONDARY

    # Right Bottom: Risk Hedging Matrix (4 Quadrants)
    risk_card = add_card(s5, Inches(4.7), Inches(3.2), Inches(7.8), Inches(3.55), top_strip_color=ACCENT_BLUE)
    tb = s5.shapes.add_textbox(Inches(4.9), Inches(3.35), Inches(7.4), Inches(3.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "МАТРИЦА ХЕДЖИРОВАНИЯ И ИЗОЛЯЦИИ РИСКОВ"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(6)

    risks = [
        ("Технический срыв канала Earth-Core (–15%)", "Хедж: Увеличенный склад 120 т ZBO + оперативная балансировка через гибкий Канал B (Earth-Flex) с lead time 4 мес."),
        ("Задержка ввода лунного завода Lunar-ISRU", "Хедж: Сохранение опциона Канала C (Earth-New), позволяющего развернуть 130 т/год мощности за 18–24 мес."),
        ("Риск переполнения баков и затоваривания", "Хедж: Математическая синхронизация бронирования и отбора (NASA MILP), устраняющая штрафы Take-or-Pay."),
        ("Геополитический шок и закрытие земных каналов", "Хедж: Достижение 28.4% автономности на лунном водороде и кислороде к 2040 г., масштабируемое до 50%+ к 2045 г."),
    ]
    for r_lbl, r_h in risks:
        p = tf.add_paragraph()
        p.text = f"★ {r_lbl}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        p = tf.add_paragraph()
        p.text = r_h
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(3)

    # =========================================================================
    # SLIDE 6: Digital Contour & Live Demo (5:30 - 6:30)
    # =========================================================================
    s6 = add_base_slide(
        "ЦИФРОВОЙ КОНТУР И ГОТОВНОСТЬ К ВНЕДРЕНИЮ",
        "ДЕЙСТВУЮЩИЙ ПРОТОТИП УРОВНЯ TRL-4/5: СТЕК И ДЕМОНСТРАЦИЯ",
        "5:30 – 6:30"
    )

    # 3 Summary Pillars
    # 1. Tech Stack
    add_card(s6, Inches(0.8), Inches(1.65), Inches(3.7), Inches(5.1), top_strip_color=ACCENT_BLUE)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(3.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ПРОМЫШЛЕННЫЙ ТЕХНОЛОГИЧЕСКИЙ СТЕК"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(8)

    tech = [
        ("Математическое ядро", "Python 3.12, SciPy/HiGHS MILP, Pydantic v2. Микросекундный расчет матбаланса."),
        ("Надежность вычислений", "792/792 инварианта верифицировано unit-тестами. 0 нарушений закона сохранения массы."),
        ("Интерфейс оператора", "React 19, TypeScript, Tailwind v4, Recharts Composed/Dual-Axis."),
        ("Zero-Backend Fallback", "Автономное исполнение в браузере без серверов. 100% готовность к работе онлайн."),
        ("Мобильная оптимизация", "Touch-слайдеры, адаптивная сетка под смартфоны и планшеты."),
    ]
    for l, v in tech:
        p = tf.add_paragraph()
        p.text = f"• {l}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = v
        r.font.bold = False
        r.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # 2. Operator Features
    add_card(s6, Inches(4.8), Inches(1.65), Inches(3.7), Inches(5.1), top_strip_color=ACCENT_GREEN)
    tb = s6.shapes.add_textbox(Inches(5.0), Inches(1.85), Inches(3.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ИНСТРУМЕНТЫ ПРИНЯТИЯ РЕШЕНИЙ"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)

    feat = [
        ("Мульти-ядерная оптимизация", "Переключение NASA MILP, Минэнерго РФ и Minimax Robust на лету."),
        ("Интерактивное планирование", "Слайдеры отбора и бронирования с визуализацией порогов Take-or-Pay."),
        ("Стресс-тестирование в 1 клик", "Мгновенное моделирование отказов и сопоставление финансовых и объемных шкал."),
        ("Экспорт отчетов в Excel", "Генерация отчетов в формате XLSX со всеми годами и статьями затрат."),
        ("Масштабирование (Критерий 20)", "Расширение горизонта до 2045 г. + подключение произвольного «Канала F»."),
    ]
    for l, v in feat:
        p = tf.add_paragraph()
        p.text = f"✔ {l}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_PRIMARY
        r = p.add_run()
        r.text = v
        r.font.bold = False
        r.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # 3. Live Demo & Repositories
    add_card(s6, Inches(8.8), Inches(1.65), Inches(3.7), Inches(5.1), border_color=RGBColor(186, 230, 253), top_strip_color=ACCENT_AMBER)
    tb = s6.shapes.add_textbox(Inches(9.0), Inches(1.85), Inches(3.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "ЖИВОЙ ДОСТУП И ССЫЛКИ"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(6)

    # Add QR code image
    if os.path.exists(QR_PATH):
        s6.shapes.add_picture(QR_PATH, Inches(9.55), Inches(2.45), Inches(2.2), Inches(2.2))

    tb_qr_desc = s6.shapes.add_textbox(Inches(9.0), Inches(4.8), Inches(3.3), Inches(1.8))
    tf_qd = tb_qr_desc.text_frame
    tf_qd.word_wrap = True

    p = tf_qd.paragraphs[0]
    p.text = "zahar713713-dot.github.io/Cosmo-Hackaton-2026"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.alignment = PP_ALIGN.CENTER

    p = tf_qd.add_paragraph()
    p.text = "Репозиторий проекта:\ngithub.com/whatrushki/fuel-contur"
    p.font.size = Pt(9)
    p.font.color.rgb = TEXT_SECONDARY
    p.alignment = PP_ALIGN.CENTER
    p.space_after = Pt(4)

    p = tf_qd.add_paragraph()
    p.text = "Спасибо за внимание! Готовы ответить на вопросы комиссии."
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.alignment = PP_ALIGN.CENTER

    output_path = "Топливный_космоконтур_2035_Презентация.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")


if __name__ == "__main__":
    build_presentation()
