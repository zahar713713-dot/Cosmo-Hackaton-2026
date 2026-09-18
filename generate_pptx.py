"""
Generates high-impact 16:9 PowerPoint (.pptx) presentation for CosmoHackathon 2026 defense.
Theme: Cyber-brutalist space logistics (#050507, #ccff00, #ffffff).
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette
BG_COLOR = RGBColor(5, 5, 7)          # #050507
CARD_BG = RGBColor(15, 15, 20)        # #0f0f14
CARD_BORDER = RGBColor(35, 35, 42)    # #23232a
ACCENT_LIME = RGBColor(204, 255, 0)   # #ccff00
WHITE = RGBColor(255, 255, 255)       # #ffffff
GRAY_MUTED = RGBColor(161, 161, 170)  # #a1a1aa
GRAY_DARK = RGBColor(24, 24, 28)      # #18181c


def create_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]  # Blank slide

    def add_base_slide(tag: str, title: str, timing: str):
        slide = prs.slides.add_slide(blank_layout)

        # Background fill
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()

        # Header Box
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(10.0), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Tag
        p_tag = tf.paragraphs[0]
        p_tag.text = tag
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_LIME

        # Title
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        # Timing Badge (Top Right)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.0), Inches(0.55), Inches(1.5), Inches(0.4))
        badge.fill.solid()
        badge.fill.fore_color.rgb = GRAY_DARK
        badge.line.color.rgb = CARD_BORDER
        tf_b = badge.text_frame
        tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.text = timing
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = GRAY_MUTED

        return slide

    def add_card(slide, x, y, w, h, border_color=CARD_BORDER, bg_color=CARD_BG):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
        return shape

    # ==================== SLIDE 1 ====================
    s1 = add_base_slide(
        "<СЛАЙД 01 // КОНЦЕПЦИЯ СИСТЕМЫ>",
        "ТОПЛИВНЫЙ КОСМОКОНТУР 2035 // СИТУАЦИОННЫЙ ЦЕНТР ОТУ",
        "0:00 — 0:35"
    )
    # Left Card: Challenge
    add_card(s1, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), ACCENT_LIME)
    tb = s1.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "🎯 СТРАТЕГИЧЕСКИЙ ВЫЗОВ ЛУННОЙ ПРОГРАММЫ"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    p = tf.add_paragraph()
    p.text = (
        "\nРазвертывание и гарантированное снабжение цислунарного орбитального топливного узла (ОТУ) "
        "в 2035–2040 гг. для обеспечения пилотируемой станции, многоразовых посадочных модулей "
        "и межорбитальных буксиров."
    )
    p.font.size = Pt(13)
    p.font.color.rgb = WHITE

    p = tf.add_paragraph()
    p.text = "\n⚠️ КРИТИЧЕСКИЕ БАРЬЕРЫ КЕЙСА:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    for item in [
        "Колоссальная стоимость земной доставки: 6.2–8.9 млн у.е./т при плече до 12 мес.",
        "Директивный потолок бюджета: CAPEX <= 1 800 млн у.е. до конца 2037 г.",
        "Безусловная безопасность: критический SLA >= 99.0% и неснижаемый 45-дневный буфер.",
    ]:
        p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(11)
        p.font.color.rgb = GRAY_MUTED

    # Right Card: Tech Stack
    add_card(s1, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tb2 = s1.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "🏛️ ОТЕЧЕСТВЕННЫЙ ТЕХНОЛОГИЧЕСКИЙ СТЕК"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    for title, desc in [
        ("Python 3.12 + Pydantic v2", "Строго типизированное детерминированное математическое ядро. Запрещены эвристики и неявные допущения."),
        ("FastAPI + OpenAPI Docs", "Высокопроизводительный REST API слой со строгой валидацией запросов и русской локализацией ошибок."),
        ("React 19 + TypeScript + Vite", "Рабочее место оператора с реактивным откликом (< 20 мс) и симметричным кибер-бруталистским дизайном."),
        ("38 Автоматических тестов pytest", "100% воспроизводимость: контрольный пример 2035 года проверен до 4 знаков после запятой."),
    ]:
        p = tf2.add_paragraph()
        p.text = f"\n{title}"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = WHITE

        p_desc = tf2.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = GRAY_MUTED

    # ==================== SLIDE 2 ====================
    s2 = add_base_slide(
        "<СЛАЙД 02 // МАТЕМАТИЧЕСКОЕ ЯДРО>",
        "ФИЗИЧЕСКИЙ МАТЕРИАЛЬНЫЙ БАЛАНС И ВЕРИФИКАЦИЯ",
        "0:35 — 1:10"
    )
    # Left Card: Equations
    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tb = s2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "⚖️ ФОРМУЛА ФИЗИЧЕСКОГО БАЛАНСА"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    p = tf.add_paragraph()
    p.text = "\nEnd_Stock = Start_Stock + Gross - Losses - Served"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = WHITE

    for title, desc in [
        ("Потери throughput (4.5% / 1.2%):", "Начисляются строго 1 раз на валовый приход топлива. Повторные потери на остаток исключены."),
        ("Исключение отрицательных остатков:", "Физический остаток строго >= 0. При дефиците объем недопоставки изолируется в отдельную метрику."),
        ("Приоритет критического спроса:", "Пилотируемый сектор обеспечивается первым: Served_Crit = min(Served, Demand_Crit)."),
        ("Защита Take-or-Pay от двойного счета:", "Billable_Vol = max(Order, 0.70 * Reserved). Штраф начисляется только при недоборе лимита."),
    ]:
        p = tf.add_paragraph()
        p.text = f"\n• {title} {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = GRAY_MUTED

    # Right Card: Benchmark Table
    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), ACCENT_LIME)
    tb2 = s2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "🔬 ВЕРИФИКАЦИЯ КОНТРОЛЬНОГО ПРИМЕРА 2035 Г."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    rows = [
        ("Начальный запас (45 дней)", "12.3288 т", "12.3288 т", "0.0000"),
        ("Заказ Earth-Core", "95.0000 т", "95.0000 т", "0.0000"),
        ("Потери валовые (4.5%)", "4.2750 т", "4.2750 т", "0.0000"),
        ("Полезный приход", "90.7250 т", "90.7250 т", "0.0000"),
        ("Отпуск на спрос (в т.ч. крит 80)", "100.0000 т", "100.0000 т", "0.0000"),
        ("Конечный остаток на 31.12", "3.0538 т", "3.0538 т", "0.0000 ✅"),
    ]

    p = tf2.add_paragraph()
    p.text = "\nПараметр проверки          ТЗ        Ядро      Дельта"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE

    for param, tz_val, core_val, delta in rows:
        p = tf2.add_paragraph()
        p.text = f"{param:<24} {tz_val:<10} {core_val:<10} {delta}"
        p.font.size = Pt(10)
        p.font.color.rgb = ACCENT_LIME if delta == "0.0000 ✅" else GRAY_MUTED

    p = tf2.add_paragraph()
    p.text = "\n✓ Автоматический тест test_balance.py подтверждает сходимость с точностью до 4 знаков."
    p.font.size = Pt(11)
    p.font.color.rgb = WHITE

    # ==================== SLIDE 3 ====================
    s3 = add_base_slide(
        "<СЛАЙД 03 // ИНВЕСТИЦИОННАЯ СТРАТЕГИЯ>",
        "ИНВЕСТИЦИОННЫЕ ВОРОТА (GATE-ПОДХОД КЕЙСА)",
        "1:10 — 1:45"
    )
    # 3 Gateway Cards
    col_w = Inches(3.64)
    gap = Inches(0.35)

    # Gate 1
    add_card(s3, Inches(0.8), Inches(1.8), col_w, Inches(4.8), ACCENT_LIME)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), col_w - Inches(0.4), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ШЛЮЗ 01: ZBO-МОДЕРНИЗАЦИЯ"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME
    p = tf.add_paragraph()
    p.text = "\nCAPEX: 180 МЛН У.Е."
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p = tf.add_paragraph()
    p.text = (
        "\n• Год ввода: 2036 г.\n"
        "• OPEX: +12 млн у.е./год\n"
        "• Снижение потерь: 4.5% -> 1.2%\n"
        "• Расширение баков: 70 -> 120 т\n\n"
        "Критическое решение: без ZBO невозможно пройти обязательный стресс-тест ТЗ (потери выше нормы <= 2.0%)."
    )
    p.font.size = Pt(11)
    p.font.color.rgb = GRAY_MUTED

    # Gate 2
    add_card(s3, Inches(0.8) + col_w + gap, Inches(1.8), col_w, Inches(4.8), ACCENT_LIME)
    tb = s3.shapes.add_textbox(Inches(1.0) + col_w + gap, Inches(2.0), col_w - Inches(0.4), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ШЛЮЗ 02: LUNAR-ISRU (ЛУНА)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME
    p = tf.add_paragraph()
    p.text = "\nCAPEX: 1 250 МЛН У.Е."
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p = tf.add_paragraph()
    p.text = (
        "\n• Транши: 250 (35) + 500 (36) + 500 (37)\n"
        "• Ввод в строй: строго с 2038 г.\n"
        "• Мощность: до 120 т/год\n"
        "• Себестоимость: 3.0 млн/т (0 бронь)\n\n"
        "CAPEX до 2037 г.: 1 430 млн у.е. при лимите 1 800 млн (запас +370 млн у.е.). Окупается к 2040 г."
    )
    p.font.size = Pt(11)
    p.font.color.rgb = GRAY_MUTED

    # Gate 3
    add_card(s3, Inches(0.8) + (col_w + gap) * 2, Inches(1.8), col_w, Inches(4.8))
    tb = s3.shapes.add_textbox(Inches(1.0) + (col_w + gap) * 2, Inches(2.0), col_w - Inches(0.4), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ШЛЮЗ 03: ОПЦИОН EARTH-NEW"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p = tf.add_paragraph()
    p.text = "\nCAPEX: 360 МЛН У.Е."
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p = tf.add_paragraph()
    p.text = (
        "\n• Опцион: 90 млн у.е. (2035 г.)\n"
        "• Ввод: 270 млн у.е. (2036 г.)\n"
        "• Мощность: 130 т/год (тариф 7.1)\n\n"
        "Решение: Оставить в резерве. Служит страховкой на случай задержки лунной базы более чем на 2 года."
    )
    p.font.size = Pt(11)
    p.font.color.rgb = GRAY_MUTED

    # ==================== SLIDE 4 ====================
    s4 = add_base_slide(
        "<СЛАЙД 04 // ЖИВОЕ ДЕМО>",
        "РАБОЧЕЕ МЕСТО ОПЕРАТОРА ОТУ (ДЕМОНСТРАЦИЯ)",
        "1:45 — 2:45"
    )
    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tb = s4.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "🖥️ ЕДИНЫЙ ЭКРАН СИТУАЦИОННОГО ЦЕНТРА"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    for title, desc in [
        ("Интегральные KPI:", "Статус узла, затраты LCC, NPV (r=8%), обслуженный спрос, физический дефицит, потери оборота."),
        ("Панель 10 ограничений:", "Живые алерты SLA >= 99%, лимитов CAPEX 1800/2800 млн, буфера 45 дней, емкости баков 120 т."),
        ("Слайдеры отбора и брони:", "Управление 5 каналами с индикатором порога Take-or-Pay."),
        ("4 Графика Recharts:", "Материальный баланс, траектория бака, структура LCC и дельта стресс-теста."),
    ]:
        p = tf.add_paragraph()
        p.text = f"\n• {title} {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = GRAY_MUTED

    # Action prompt
    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8), ACCENT_LIME)
    tb2 = s4.shapes.add_textbox(Inches(7.1), Inches(2.8), Inches(5.1), Inches(3.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "⚡ ПЕРЕХОД К ЖИВОМУ ДЕМОНСТРАЦИОННОМУ СТЕНДУ"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    p = tf2.add_paragraph()
    p.text = (
        "\nДемонстрация в браузере (http://localhost:3000):\n\n"
        "1. Запуск Обязательного стресс-теста ТЗ\n"
        "2. Тестирование отказа без ZBO и снятие нарушения\n"
        "3. Интерактивный отклик Take-or-Pay при снижении отбора\n"
        "4. Скачивание многостраничного отчета Excel в 1 клик"
    )
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(13)
    p.font.color.rgb = WHITE

    # ==================== SLIDE 5 ====================
    s5 = add_base_slide(
        "<СЛАЙД 05 // ИННОВАЦИЯ И ВАУ-ЭФФЕКТ>",
        "МУЛЬТИ-ЯДЕРНАЯ ОПТИМИЗАЦИЯ // NASA SPACE LOGISTICS",
        "2:45 — 3:20"
    )
    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), ACCENT_LIME)
    tb = s5.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🚀 NASA SPACE LOGISTICS (MILP) ★ ЦЕЛЕВОЕ ЯДРО"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    p = tf.add_paragraph()
    p.text = "\nЭКОНОМИЯ: -11.81% NPV LCC"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    p = tf.add_paragraph()
    p.text = (
        "\nСнижение бюджета программы на 1 096.8 млн у.е. при сохранении 100% надежности!\n\n"
        "• Методология: MIT / NASA Glenn (AIAA Space Logistics Framework).\n"
        "• Целочисленное линейное программирование (MILP).\n"
        "• Обнуление Take-or-Pay: объем заказа строго равен бронированию.\n"
        "• Максимизация лунного топлива: забор 120 т/год по 3.0 млн у.е./т.\n"
        "• Минимизация расходов на хранение (0.72 млн/т·год)."
    )
    p.font.size = Pt(11)
    p.font.color.rgb = WHITE

    # Right Card: Table
    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tb2 = s5.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "📊 СРАВНЕНИЕ МАТЕМАТИЧЕСКИХ АЛГОРИТМОВ"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    comp_rows = [
        ("Критический SLA", "100.0%", "100.0%", "100.0%"),
        ("Общий SLA", "98.8%", "99.8%", "99.5%"),
        ("Недисконтированный LCC", "11 483 млн", "10 112 млн", "11 950 млн"),
        ("NPV LCC (r=8%)", "9 284.7 млн", "8 187.9 млн", "9 540 млн"),
        ("Экономия бюджета", "База (0%)", "-11.81% (1.09 млрд) ★", "+2.7% запас"),
    ]

    p = tf2.add_paragraph()
    p.text = "\nМетрика                  Регламент ТЗ   NASA MILP      Minimax"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE

    for m, reg, milp, minmax in comp_rows:
        p = tf2.add_paragraph()
        p.text = f"{m:<24} {reg:<14} {milp:<14} {minmax}"
        p.font.size = Pt(10)
        p.font.color.rgb = ACCENT_LIME if "★" in milp else GRAY_MUTED

    p = tf2.add_paragraph()
    p.text = "\nВывод: Алгоритм NASA MILP признан целевым ядром для минимизации затрат программы."
    p.font.size = Pt(11)
    p.font.color.rgb = WHITE

    # ==================== SLIDE 6 ====================
    s6 = add_base_slide(
        "<СЛАЙД 06 // СТРЕСС-ТЕСТЫ И РИСКИ>",
        "СТРЕСС-ТЕСТИРОВАНИЕ И МАТРИЦА РИСКОВ",
        "3:20 — 3:45"
    )
    add_card(s6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), ACCENT_LIME)
    tb = s6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "⚡ ОБЯЗАТЕЛЬНЫЙ СТРЕСС-ТЕСТ ТЗ"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    for title, desc in [
        ("Шоки спроса и цен:", "Спрос +15% (2038–2040), тарифы Earth-Core и Flex +25% (2038–2039), ISRU срезан до 55%/75%."),
        ("Потери оборота:", "Фактические потери 1.2% (благодаря ZBO строго выдержан норматив <= 2.0%)."),
        ("Критический SLA:", "100.0% — дефицит пилотируемых миссий равен строго 0.0 тонн."),
        ("Совокупный SLA:", "97.4% — директивный норматив >= 97.0% соблюден."),
        ("Бонус: Геополитика (+5):", "Модуль парирования санкций и скачка тарифов Земли до +50%."),
    ]:
        p = tf.add_paragraph()
        p.text = f"\n• {title} {desc}"
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE

    # Right Card: Tornado
    add_card(s6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tb2 = s6.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "🌪️ TORNADO-АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    risk_items = [
        ("Задержка ввода ISRU на 2 года", "+850 млн у.е. LCC", "Шлюз 03 (Опцион Earth-New)"),
        ("Штрафы Take-or-Pay", "до 120 млн/год", "NASA MILP: Order = Reserved"),
        ("Рост цен земных пусков +25%", "+435 млн у.е. LCC", "Максимизация лунного топлива"),
        ("Пиковый рост спроса свыше +20%", "Риск дефицита", "Буфер 120 т + Emergency 80 т"),
    ]

    p = tf2.add_paragraph()
    p.text = "\nФактор риска               Ущерб               Мера защиты"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE

    for factor, dmg, prot in risk_items:
        p = tf2.add_paragraph()
        p.text = f"{factor:<26} {dmg:<18} {prot}"
        p.font.size = Pt(10)
        p.font.color.rgb = GRAY_MUTED

    p = tf2.add_paragraph()
    p.text = "\nВывод: Все критические риски имеют встроенные в систему инженерные контрмеры."
    p.font.size = Pt(11)
    p.font.color.rgb = WHITE

    # ==================== SLIDE 7 ====================
    s7 = add_base_slide(
        "<СЛАЙД 07 // ИТОГИ И РЕШЕНИЯ>",
        "ИТОГИ ПРОГРАММЫ И ПРОЕКТ РЕШЕНИЙ",
        "3:45 — 4:00"
    )
    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8), ACCENT_LIME)
    tb = s7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "🏆 РЕЗУЛЬТАТЫ ВЫПОЛНЕНИЯ КЕЙСА"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    for item in [
        "Все 20 критериев ТЗ выполнены на 100% + реализован бонус за геополитику.",
        "Сходимость контрольного примера 2035 г. с точностью до 4 знаков (10^-4 т).",
        "Доказанная экономия 1 096.8 млн у.е. NPV LCC при алгоритме NASA MILP.",
        "Соблюдение директивы CAPEX с запасом 370 млн у.е. до 2037 года.",
        "Масштабируемость до 2045 года и динамический ввод Канала F без изменения ядра.",
        "Экспорт официальной отчетности в 1 клик (XLSX на 7 листов с единицами измерения).",
    ]:
        p = tf.add_paragraph()
        p.text = f"\n✓ {item}"
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE

    # Right Card: Recommendations
    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    tb2 = s7.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.4))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "📝 ПРОЕКТ РЕШЕНИЙ ЭКСПЕРТНОГО СОВЕТА"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    decisions = [
        "1. Принять целевой план на базе алгоритма NASA MILP как базовую стратегию снабжения ОТУ.",
        "2. Утвердить финансирование ZBO-модернизации (180 млн у.е.) в 2036 г. для удержания потерь <= 2.0%.",
        "3. Санкционировать трехлетний график траншей Lunar-ISRU (250 + 500 + 500 млн у.е. в 2035–2037 гг.).",
        "4. Внедрить разработанный комплекс в качестве штатного рабочего места ситуационного центра.",
    ]

    for dec in decisions:
        p = tf2.add_paragraph()
        p.text = f"\n{dec}"
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE

    p = tf2.add_paragraph()
    p.text = "\n\nСПАСИБО ЗА ВНИМАНИЕ! ГОТОВЫ К ОТВЕТАМ НА ВОПРОСЫ (Q&A)"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_LIME

    # Save presentation
    output_path = "Топливный_космоконтур_2035_Презентация.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")


if __name__ == "__main__":
    create_deck()
