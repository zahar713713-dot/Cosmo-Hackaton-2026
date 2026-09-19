"""
Generates high-contrast, executive-ready 16:9 PowerPoint (.pptx) presentation for CosmoHackathon 2026 defense.
Theme: Modern Aerospace Executive (Light Slate, Pure White Cards, Deep Navy Text, Vivid Aerospace Blue & Emerald accents).
Ultra-high contrast, WCAG AAA compliant, fully readable on any screen/projector.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Modern High-Contrast Executive Color Palette
BG_CANVAS = RGBColor(248, 250, 252)       # Slate 50 (clean soft background)
CARD_BG = RGBColor(255, 255, 255)         # Pure White for cards
CARD_BORDER = RGBColor(226, 232, 240)     # Slate 200 (subtle crisp border)
CARD_BORDER_ACCENT = RGBColor(186, 230, 253) # Light Sky border

TEXT_PRIMARY = RGBColor(15, 23, 42)       # Slate 900 (Deep Charcoal / Navy, max contrast)
TEXT_SECONDARY = RGBColor(51, 65, 85)     # Slate 700 (High contrast body text)
TEXT_MUTED = RGBColor(100, 116, 139)      # Slate 500 (Footnotes, secondary captions)

ACCENT_BLUE = RGBColor(2, 132, 199)       # Sky 600 (Aerospace Blue)
ACCENT_BLUE_DARK = RGBColor(3, 105, 161)  # Sky 700
ACCENT_GREEN = RGBColor(16, 149, 93)      # Emerald Green (Savings, success, SLA 100%)
ACCENT_GREEN_BG = RGBColor(236, 253, 245) # Soft Emerald Tint
ACCENT_AMBER = RGBColor(180, 83, 9)       # Amber 700 (Risks, constraints)
ACCENT_AMBER_BG = RGBColor(254, 243, 199) # Soft Amber Tint

TABLE_HEADER_BG = RGBColor(30, 41, 59)    # Slate 800 (Dark professional table header)
TABLE_HEADER_TEXT = RGBColor(255, 255, 255)
TABLE_ROW_ALT = RGBColor(248, 250, 252)   # Slate 50 for alternating rows


def create_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    def add_base_slide(tag: str, title: str, timing: str):
        slide = prs.slides.add_slide(blank_layout)

        # Background canvas fill
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_CANVAS
        bg.line.fill.background()

        # Header Box
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.2), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Category / Tag
        p_tag = tf.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_BLUE

        # Title
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_PRIMARY

        # Timing Badge (Top Right)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.1), Inches(0.45), Inches(1.4), Inches(0.42))
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

    def add_card(slide, x, y, w, h, border_color=CARD_BORDER, bg_color=CARD_BG, top_bar_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5 if top_bar_color else 1)

        # Optional colored decorative top strip
        if top_bar_color:
            bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, Inches(0.08))
            bar.fill.solid()
            bar.fill.fore_color.rgb = top_bar_color
            bar.line.fill.background()

        return shape

    def add_metric_card(slide, x, y, w, h, value: str, label: str, val_color=ACCENT_GREEN, subtext=""):
        card = add_card(slide, x, y, w, h, border_color=CARD_BORDER, bg_color=CARD_BG, top_bar_color=val_color)
        tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.18), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = value
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = val_color

        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY

        if subtext:
            p3 = tf.add_paragraph()
            p3.text = subtext
            p3.font.size = Pt(9)
            p3.font.color.rgb = TEXT_MUTED
        return card

    # ==================== SLIDE 1: КОНЦЕПЦИЯ И АРХИТЕКТУРА ====================
    s1 = add_base_slide(
        "Слайд 1 // Стратегия и Архитектура",
        "Топливный космоконтур 2035: Ситуационный центр ОТУ",
        "0:00 — 0:35"
    )

    # Left Card: Mission Challenge
    add_card(s1, Inches(0.8), Inches(1.65), Inches(5.6), Inches(5.3), top_bar_color=ACCENT_BLUE)
    tb1 = s1.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.9))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = 0

    p = tf1.paragraphs[0]
    p.text = "🎯 Стратегическая цель программы"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE_DARK

    p = tf1.add_paragraph()
    p.text = (
        "Гарантированное и экономически эффективное снабжение цислунарного "
        "Орбитального Топливного Узла (ОТУ) в 2035–2040 гг. для обеспечения лунной "
        "инфраструктуры, межорбитальных буксиров и пилотируемых экспедиций."
    )
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_SECONDARY
    p.space_after = Pt(12)

    p = tf1.add_paragraph()
    p.text = "⚠️ Ключевые барьеры и директивы ТЗ:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    constraints = [
        ("Высокая стоимость доставки Земли:", "6.2–8.9 млн у.е./т при плече планирования до 12 месяцев."),
        ("Директивный потолок CAPEX:", "Строго <= 1 800 млн у.е. до конца 2037 г. и <= 2 800 млн суммарно."),
        ("Риск штрафов Take-or-Pay:", "Оплата 70% от забронированного объема при любом недоборе."),
        ("Безусловная безопасность:", "Критический SLA >= 99.0% и неснижаемый 45-дневный запас топлива."),
    ]
    for title, desc in constraints:
        p = tf1.add_paragraph()
        p.text = f"• {title} {desc}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # Right Card: Technology Stack
    add_card(s1, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), top_bar_color=ACCENT_GREEN)
    tb2 = s1.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0

    p = tf2.paragraphs[0]
    p.text = "🏛️ Инженерный стек и надежность решения"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    tech_items = [
        ("Python 3.12 + Pydantic v2", "Строго типизированное математическое ядро. Детерминированный расчет без эвристик и скрытых допущений."),
        ("FastAPI + REST API", "Высокоскоростной API-слой с автоматической валидацией параметров и русской локализацией ошибок."),
        ("React 19 + TypeScript + Vite", "Интерактивное рабочее место оператора с реактивным откликом (< 200 мс) и наглядными графиками Recharts."),
        ("38 Автоматических тестов pytest", "100% покрытие физического баланса: контрольный пример ТЗ проверен с точностью 10^-4 т."),
        ("Мульти-ядерная архитектура", "Поддержка 3 алгоритмов (Регламент, NASA MILP, Minimax) с возможностью мгновенного переключения."),
    ]
    for title, desc in tech_items:
        p = tf2.add_paragraph()
        p.text = f"{title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(6)

        p_desc = tf2.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = TEXT_SECONDARY
        p_desc.space_after = Pt(2)

    # ==================== SLIDE 2: ФИЗИЧЕСКИЙ БАЛАНС И ВЕРИФИКАЦИЯ ====================
    s2 = add_base_slide(
        "Слайд 2 // Физика Узла и Верификация",
        "Материальный баланс и сходимость контрольного примера 2035 года",
        "0:35 — 1:10"
    )

    # Left Card: Equations
    add_card(s2, Inches(0.8), Inches(1.65), Inches(5.6), Inches(5.3), top_bar_color=ACCENT_BLUE)
    tb = s2.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "⚖️ Формула сохранения физического баланса"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE_DARK

    # Formula Box
    p = tf.add_paragraph()
    p.text = "End_Stock = Start_Stock + Gross_In - Losses - Served"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p.space_before = Pt(4)
    p.space_after = Pt(10)

    rules = [
        ("Потери Throughput (4.5% / 1.2%):", "Начисляются строго 1 раз на валовый приход топлива. Повторные потери на остаток в баке исключены."),
        ("Физическая неотрицательность остатков:", "Остаток строго >= 0. При нехватке топлива дефицит изолируется в метрику Unmet Demand (недопоставка)."),
        ("Приоритет критического спроса:", "Пилотируемые экипажи обеспечиваются первыми: Served_Crit = min(Served, Demand_Crit)."),
        ("Защита Take-or-Pay:", "Оплачиваемый объем = max(Order, 0.70 * Reserved). Штраф за недобор начисляется прозрачно."),
    ]
    for title, desc in rules:
        p = tf.add_paragraph()
        p.text = f"• {title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = f"   {desc}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_SECONDARY
        p2.space_after = Pt(4)

    # Right Card: Real Table Verification
    add_card(s2, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), top_bar_color=ACCENT_GREEN)
    tb_t = s2.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(0.6))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p = tf_t.paragraphs[0]
    p.text = "🔬 Сходимость контрольного примера 2035 г."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    # Add Table
    table_shape = s2.shapes.add_table(7, 4, Inches(7.0), Inches(2.45), Inches(5.3), Inches(3.4))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(1.0)
    table.columns[2].width = Inches(1.0)
    table.columns[3].width = Inches(1.1)

    table_data = [
        ("Параметр проверки", "ТЗ Регламент", "Наше ядро", "Дельта"),
        ("Начальный запас (45 дн.)", "12.3288 т", "12.3288 т", "0.0000 т"),
        ("Заказ Earth-Core", "95.0000 т", "95.0000 т", "0.0000 т"),
        ("Потери валовые (4.5%)", "4.2750 т", "4.2750 т", "0.0000 т"),
        ("Полезный приход", "90.7250 т", "90.7250 т", "0.0000 т"),
        ("Отпуск на спрос (в т.ч. крит 80)", "100.0000 т", "100.0000 т", "0.0000 т"),
        ("Конечный остаток на 31.12", "3.0538 т", "3.0538 т", "0.0000 т ✅"),
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
            
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = TABLE_HEADER_BG
                p.font.size = Pt(9.5)
                p.font.bold = True
                p.font.color.rgb = TABLE_HEADER_TEXT
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = ACCENT_GREEN_BG if r_idx == 6 else (TABLE_ROW_ALT if r_idx % 2 == 1 else CARD_BG)
                p.font.size = Pt(9.5)
                p.font.color.rgb = ACCENT_GREEN if (c_idx == 3 and r_idx == 6) else TEXT_PRIMARY
                if c_idx == 3 or r_idx == 6:
                    p.font.bold = True

    # Note under table
    tb_note = s2.shapes.add_textbox(Inches(7.1), Inches(6.1), Inches(5.1), Inches(0.7))
    tf_n = tb_note.text_frame
    tf_n.word_wrap = True
    p = tf_n.paragraphs[0]
    p.text = "✅ 100% совпадение с эталоном ТЗ подтверждено автоматическим тестом test_balance.py (погрешность < 10^-4 т)."
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    # ==================== SLIDE 3: ИНВЕСТИЦИОННЫЕ ШЛЮЗЫ ====================
    s3 = add_base_slide(
        "Слайд 3 // Управление CAPEX и Проектами",
        "Инвестиционная стратегия: Трехшлюзовая модель (Gate-подход)",
        "1:10 — 1:45"
    )

    col_w = Inches(3.64)
    gap = Inches(0.4)

    # Gate 1: ZBO
    x1 = Inches(0.8)
    add_card(s3, x1, Inches(1.65), col_w, Inches(5.3), top_bar_color=ACCENT_BLUE)
    tb = s3.shapes.add_textbox(x1 + Inches(0.2), Inches(1.85), col_w - Inches(0.4), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "ШЛЮЗ 01: МОДЕРНИЗАЦИЯ ZBO"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE_DARK

    p = tf.add_paragraph()
    p.text = "CAPEX: 180 млн у.е."
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "Статус: Обязательно к реализации"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)

    items_zbo = [
        "Год ввода: 2036 г. (транш 180 млн).",
        "OPEX обслуживания: +12 млн у.е./год.",
        "Эффект 1: Снижение потерь с 4.5% до 1.2%.",
        "Эффект 2: Расширение емкости баков с 70 до 120 тонн.",
        "Обоснование: Без ZBO невозможно пройти обязательный стресс-тест ТЗ (норма потерь <= 2.0%).",
    ]
    for it in items_zbo:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # Gate 2: ISRU
    x2 = Inches(0.8) + col_w + gap
    add_card(s3, x2, Inches(1.65), col_w, Inches(5.3), top_bar_color=ACCENT_GREEN)
    tb = s3.shapes.add_textbox(x2 + Inches(0.2), Inches(1.85), col_w - Inches(0.4), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "ШЛЮЗ 02: LUNAR-ISRU (ЛУНА)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p = tf.add_paragraph()
    p.text = "CAPEX: 1 250 млн у.е."
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "Статус: Главный драйвер окупаемости"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)

    items_isru = [
        "Транши: 250 (35 г.) + 500 (36 г.) + 500 (37 г.).",
        "Ввод в строй: 2038 год.",
        "Мощность: до 120 т/год по тарифу 3.0 млн у.е./т.",
        "0 млн у.е. бронирования (нет Take-or-Pay).",
        "CAPEX до 2037 г.: 1 430 млн у.е. (запас +370 млн у.е. до лимита 1 800 млн).",
        "Полная окупаемость инвестиций к 2040 году.",
    ]
    for it in items_isru:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # Gate 3: Earth-New
    x3 = Inches(0.8) + (col_w + gap) * 2
    add_card(s3, x3, Inches(1.65), col_w, Inches(5.3), top_bar_color=ACCENT_AMBER)
    tb = s3.shapes.add_textbox(x3 + Inches(0.2), Inches(1.85), col_w - Inches(0.4), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "ШЛЮЗ 03: ОПЦИОН EARTH-NEW"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    p = tf.add_paragraph()
    p.text = "CAPEX: 360 млн у.е."
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    p.space_after = Pt(8)

    p = tf.add_paragraph()
    p.text = "Статус: Резервный опцион (Заморожен)"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(8)

    items_new = [
        "Опцион выкупа: 90 млн у.е. (2035 г.).",
        "Финальный ввод: 270 млн у.е. (2036 г.).",
        "Мощность: 130 т/год по тарифу 7.1 млн у.е./т.",
        "Обоснование решения: В базовом плане НЕ активируется ввиду достатка лунного ISRU.",
        "Служит страховкой на случай задержки лунной базы свыше 2 лет.",
    ]
    for it in items_new:
        p = tf.add_paragraph()
        p.text = f"• {it}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(4)

    # ==================== SLIDE 4: СРАВНЕНИЕ АЛГОРИТМОВ ====================
    s4 = add_base_slide(
        "Слайд 4 // Мульти-ядерная Оптимизация",
        "Сравнительный анализ алгоритмов: Экономия 1.096 млрд у.е.",
        "1:45 — 2:30"
    )

    # Top Metric Chips
    m_w = Inches(3.7)
    add_metric_card(s4, Inches(0.8), Inches(1.65), m_w, Inches(1.15), "-1 096.8 млн", "Экономия бюджета NPV LCC (-11.81%)", ACCENT_GREEN, "Целевое ядро NASA MILP")
    add_metric_card(s4, Inches(0.8) + m_w + Inches(0.3), Inches(1.65), m_w, Inches(1.15), "0.0 млн у.е.", "Штрафы Take-or-Pay ликвидированы", ACCENT_GREEN, "Заказ строго равен бронированию")
    add_metric_card(s4, Inches(0.8) + (m_w + Inches(0.3)) * 2, Inches(1.65), m_w, Inches(1.15), "100.0%", "Критический SLA пилотируемых миссий", ACCENT_BLUE, "Общий SLA системы 99.8%")

    # Comparison Table
    table_shape = s4.shapes.add_table(8, 4, Inches(0.8), Inches(3.05), Inches(11.73), Inches(3.6))
    table = table_shape.table
    table.columns[0].width = Inches(3.33)
    table.columns[1].width = Inches(2.8)
    table.columns[2].width = Inches(2.8)
    table.columns[3].width = Inches(2.8)

    comp_headers = ["Показатель эффективности", "ТЗ Регламент (Baseline)", "NASA MILP (Целевое) ★", "Minimax Robust (Вальд)"]
    comp_rows = [
        ("Критический SLA (пилотируемый)", "100.0%", "100.0%", "100.0%"),
        ("Совокупный SLA программы", "98.8%", "99.8%", "99.5%"),
        ("Недисконтированный LCC (2035–2040)", "11 483.0 млн у.е.", "10 112.4 млн у.е.", "11 950.0 млн у.е."),
        ("Дисконтированный LCC (NPV r=8%)", "9 284.7 млн у.е.", "8 187.9 млн у.е.", "9 540.0 млн у.е."),
        ("Экономия бюджета (NPV дельта)", "0.0 млн (База)", "-1 096.8 млн у.е. (-11.81%) ★", "+255.3 млн (+2.7% запас)"),
        ("Штрафы за недобор Take-or-Pay", "147.2 млн у.е.", "0.0 млн у.е. (100% защита)", "0.0 млн у.е."),
        ("Логика формирования заказов", "Фиксированные квоты ТЗ", "MILP оптимизация потоков", "Худший сценарий (буфер 60 дн)"),
    ]

    for c_idx, h_text in enumerate(comp_headers):
        cell = table.cell(0, c_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TABLE_HEADER_TEXT

    for r_idx, row in enumerate(comp_rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            if c_idx == 2:
                cell.fill.fore_color.rgb = ACCENT_GREEN_BG
            else:
                cell.fill.fore_color.rgb = TABLE_ROW_ALT if r_idx % 2 == 1 else CARD_BG

            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
            p.font.size = Pt(9.5)
            if c_idx == 2:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            else:
                p.font.color.rgb = TEXT_PRIMARY

    # Bottom summary note
    tb_bot = s4.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.73), Inches(0.4))
    tf_b = tb_bot.text_frame
    p = tf_b.paragraphs[0]
    p.text = "💡 Вывод: Ядро NASA MILP превосходит базовый регламент по всем параметрам, высвобождая более 1.09 млрд у.е. при нулевом риске."
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY

    # ==================== SLIDE 5: ИНТЕРФЕЙС И ЖИВОЕ ДЕМО ====================
    s5 = add_base_slide(
        "Слайд 5 // Операционный Контур",
        "Интерфейс ситуационного центра и план демонстрации",
        "2:30 — 3:05"
    )

    # Left Card: UI Modules
    add_card(s5, Inches(0.8), Inches(1.65), Inches(5.6), Inches(5.3), top_bar_color=ACCENT_BLUE)
    tb = s5.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "🖥️ Функционал веб-приложения оператора"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE_DARK

    ui_modules = [
        ("Селектор алгоритмов:", "Переключение между Регламентом, NASA MILP и Минимаксом с динамическим пересчетом за ~200 мс."),
        ("Светофор 10 ограничений ТЗ:", "Мгновенные алерты SLA >= 99%, лимитов CAPEX 1800/2800 млн, емкости баков 120 т и 45-дневного буфера."),
        ("Слайдеры отбора и бронирования:", "Интерактивное управление 5 каналами с динамическим контролем порога Take-or-Pay 70%."),
        ("4 Интерактивных графика Recharts:", "Траектория остатка в баке, структура LCC, материальный баланс и дельта стресс-теста."),
        ("Экспорт аудиторского отчета:", "Скачивание полной книги XLSX на 7 листов с формулами и единицами измерения в 1 клик."),
    ]
    for title, desc in ui_modules:
        p = tf.add_paragraph()
        p.text = f"• {title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(5)

        p2 = tf.add_paragraph()
        p2.text = f"   {desc}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_SECONDARY
        p2.space_after = Pt(2)

    # Right Card: Live Demo Steps
    add_card(s5, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), top_bar_color=ACCENT_GREEN)
    tb2 = s5.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0

    p = tf2.paragraphs[0]
    p.text = "⚡ План показа живой системы на стенде"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    demo_steps = [
        ("Шаг 1: Базовый режим NASA MILP", "Демонстрация нулевых штрафов Take-or-Pay, NPV 8.188 млрд у.е. и зеленого статуса всех 10 лимитов."),
        ("Шаг 2: Сравнение с ТЗ Регламентом", "Включение ядра 'ТЗ Регламент': визуализация падения эффективности на 1.096 млрд у.е. из-за неоптимального отбора."),
        ("Шаг 3: Активация стресс-теста ТЗ", "Нажатие кнопки 'Обязательный стресс-тест': рост спроса +15%, срез ISRU, подтверждение потерь 1.2% (норма <= 2.0%)."),
        ("Шаг 4: Тест отказа ZBO", "Отключение ZBO: демонстрация мгновенного срабатывания красного алерта нарушения емкости и потерь."),
        ("Шаг 5: Экспорт в Excel", "Генерация официальной отчетности для руководства за 1 секунду."),
    ]
    for title, desc in demo_steps:
        p = tf2.add_paragraph()
        p.text = f"{title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(6)

        p2 = tf2.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_SECONDARY
        p2.space_after = Pt(2)

    # ==================== SLIDE 6: СТРЕСС-ТЕСТИРОВАНИЕ И РИСКИ ====================
    s6 = add_base_slide(
        "Слайд 6 // Надежность и Риск-менеджмент",
        "Стресс-тестирование и матрица парирования рисков",
        "3:05 — 3:45"
    )

    # Top: Mandatory Stress-Test Results
    add_card(s6, Inches(0.8), Inches(1.65), Inches(11.73), Inches(2.2), top_bar_color=ACCENT_AMBER)
    tb_st = s6.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(1.9))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True
    tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0

    p = tf_st.paragraphs[0]
    p.text = "⚡ Результаты Обязательного стресс-теста ТЗ (2038–2040 гг.)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    p = tf_st.add_paragraph()
    p.text = (
        "Параметры шока: Спрос +15% (38–40 гг.), тарифы Земли +25% (38–39 гг.), срез лунного ISRU до 55% и 75%.\n"
        "• Потери Throughput: 1.2% — строго выдержан норматив ТЗ (<= 2.0%) благодаря модернизации ZBO.\n"
        "• Критический SLA: 100.0% — дефицит пилотируемых миссий равен строго 0.0 тонн на всем горизонте.\n"
        "• Совокупный SLA: 97.4% — директивный норматив ТЗ (>= 97.0%) полностью соблюден.\n"
        "• Бонусный геополитический контур: модуль выдерживает санкционный скачок земных тарифов до +50%."
    )
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_SECONDARY
    p.space_before = Pt(4)

    # Bottom: Real Table Risk Matrix
    add_card(s6, Inches(0.8), Inches(4.05), Inches(11.73), Inches(2.9), top_bar_color=ACCENT_BLUE)
    table_shape = s6.shapes.add_table(5, 3, Inches(1.0), Inches(4.25), Inches(11.33), Inches(2.5))
    table = table_shape.table
    table.columns[0].width = Inches(3.6)
    table.columns[1].width = Inches(2.7)
    table.columns[2].width = Inches(5.03)

    r_headers = ["Фактор неопределенности", "Потенциальный ущерб", "Инженерная мера парирования в системе"]
    r_data = [
        ("Задержка ввода ISRU на 2 года", "+850 млн у.е. LCC", "Шлюз 03: Активация резервного опциона Earth-New (130 т/год)."),
        ("Штрафы Take-or-Pay за недобор", "до 120 млн у.е./год", "Алгоритм NASA MILP: Объем заказа строго равен бронированию (0 штрафов)."),
        ("Рост цен пусков Земли на +25%", "+435 млн у.е. LCC", "Приоритетный отбор лунного топлива (до 120 т/год по себестоимости 3.0)."),
        ("Аномальный пик спроса (> +20%)", "Риск дефицита топлива", "Экспресс-доставка Earth-Flex + неснижаемый Emergency-резерв 80 т."),
    ]

    for c_idx, h_text in enumerate(r_headers):
        cell = table.cell(0, c_idx)
        cell.text = h_text
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER if c_idx == 1 else PP_ALIGN.LEFT
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TABLE_HEADER_TEXT

    for r_idx, row in enumerate(r_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_ROW_ALT if r_idx % 2 == 1 else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c_idx == 1 else PP_ALIGN.LEFT
            p.font.size = Pt(9.5)
            p.font.color.rgb = ACCENT_AMBER if c_idx == 1 else TEXT_PRIMARY
            if c_idx == 1:
                p.font.bold = True

    # ==================== SLIDE 7: ЗАКЛЮЧЕНИЕ И РЕШЕНИЯ ====================
    s7 = add_base_slide(
        "Слайд 7 // Итоги и Решения",
        "Результаты выполнения кейса и проект решений",
        "3:45 — 4:00"
    )

    # Left Card: Achievements
    add_card(s7, Inches(0.8), Inches(1.65), Inches(5.6), Inches(5.3), top_bar_color=ACCENT_GREEN)
    tb = s7.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(5.0), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "🏆 Ключевые результаты команды"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    achievements = [
        ("100% выполнение ТЗ:", "Все 20 критериев кейса выполнены полностью + реализован бонус за геополитику."),
        ("Абсолютная точность физики:", "Сходимость контрольного примера 2035 г. с точностью до 10^-4 т подтверждена тестами."),
        ("Экономия 1 096.8 млн у.е.:", "Доказанное снижение NPV LCC на 11.81% при ядре NASA MILP без потери надежности."),
        ("Соблюдение лимитов CAPEX:", "Запас +370 млн у.е. до 2037 года и +1 190 млн у.е. на всем горизонте до 2040 г."),
        ("Инженерная готовность:", "Полноценный интерактивный веб-комплекс, 38 тестов pytest, экспорт XLSX в 1 клик."),
    ]
    for title, desc in achievements:
        p = tf.add_paragraph()
        p.text = f"✓ {title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(6)

        p2 = tf.add_paragraph()
        p2.text = f"   {desc}"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_SECONDARY
        p2.space_after = Pt(2)

    # Right Card: Council Decisions & Final Call
    add_card(s7, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.3), top_bar_color=ACCENT_BLUE)
    tb2 = s7.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.1), Inches(4.9))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0

    p = tf2.paragraphs[0]
    p.text = "📝 Проект решений для утверждения"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE_DARK

    decisions = [
        "1. Утвердить алгоритм NASA MILP в качестве штатного оптимизатора логистических потоков ОТУ.",
        "2. Санкционировать финансирование ZBO-модернизации (180 млн у.е.) в 2036 г. для удержания потерь <= 2.0%.",
        "3. Утвердить инвестиционный график Lunar-ISRU (250 + 500 + 500 млн у.е. в 2035–2037 гг.).",
        "4. Рекомендовать разработанный программный комплекс к опытно-промышленной эксплуатации в ЦУП.",
    ]
    for dec in decisions:
        p = tf2.add_paragraph()
        p.text = dec
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(6)
        p.space_after = Pt(4)

    # Q&A Banner
    p = tf2.add_paragraph()
    p.text = "\nСПАСИБО ЗА ВНИМАНИЕ!\nГОТОВЫ К СЕССИИ ВОПРОСОВ И ОТВЕТОВ (Q&A)"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE_DARK
    p.space_before = Pt(14)

    # Save to both standard names
    prs.save("Топливный_космоконтур_2035_Презентация.pptx")
    prs.save("Presentation_Space_Logistics_2035.pptx")
    print("Executive high-contrast presentation generated successfully!")


if __name__ == "__main__":
    create_deck()
