# styles.py
from __future__ import annotations

import textwrap
import streamlit as st


def get_liquid_glass_css() -> str:
    """
    Глобальный CSS для темы Liquid Glass / Deep Dark Violet.
    Включает:
    - фон Deep Space с радиальными градиентами,
    - стеклянные карточки,
    - неоновые акценты,
    - фирменные цвета (brand violet #280046, Furore #DCDCF0).
    """
    css = textwrap.dedent(
        """
        <style>
        :root {
            /* === ПАЛИТРА Deep Dark Violet / Liquid Glass === */
            --bg-dark: #05020a;
            --bg-gradient: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #05020a 80%);
            --bg-spot-1: radial-gradient(circle at 0% 0%, rgba(88, 28, 135, 0.35), transparent 60%);
            --bg-spot-2: radial-gradient(circle at 100% 100%, rgba(56, 189, 248, 0.25), transparent 60%);

            /* Брендовые цвета */
            --brand-violet: #280046;
            --accent-furore: #DCDCF0;

            /* Акцентные неоновые цвета */
            --accent-pink: #ff2eaa;
            --accent-cyan: #3be4ff;
            --accent-yellow: #ffe45e;

            /* Текст */
            --text-main: #f5f5ff;
            --text-muted: #9ca3c7;
            --text-soft: #A0A0C5;
            --text-danger: #ff7b7b;
            --text-success: #7ee8a1;

            /* Стекло / карточки */
            --glass-bg: linear-gradient(
                145deg,
                rgba(15, 23, 42, 0.82),
                rgba(17, 24, 39, 0.78)
            );
            --glass-border: rgba(148, 163, 184, 0.28);
            --glass-highlight: rgba(255, 255, 255, 0.08);
            --glass-shadow: 0 18px 45px rgba(8, 8, 35, 0.9);

            /* Кнопки */
            --btn-bg: linear-gradient(135deg, #280046, #4c1d95);
            --btn-bg-hover: linear-gradient(135deg, #4c1d95, #7c3aed);
            --btn-border: rgba(244, 244, 255, 0.3);

            /* Поля ввода */
            --input-bg: rgba(15, 23, 42, 0.75);
            --input-border: rgba(148, 163, 184, 0.45);
            --input-border-focus: rgba(59, 130, 246, 0.95);

            /* Радиусы, тени, анимации */
            --radius-lg: 18px;
            --radius-md: 12px;
            --radius-pill: 999px;

            --shadow-soft: 0 12px 30px rgba(0, 0, 0, 0.55);
            --shadow-inner: inset 0 0 0 1px rgba(255, 255, 255, 0.06);

            --transition-fast: 150ms ease-out;
            --transition-base: 220ms ease;

            /* Сетка */
            --container-max-width: 1200px;
            --gutter: 1.5rem;

            /* Типографика */
            --font-title: "Unbounded", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            --font-body: "Raleway", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* === БАЗА ПРИЛОЖЕНИЯ === */

        html, body, .stApp {
            background: var(--bg-dark);
            background-image:
                var(--bg-gradient),
                var(--bg-spot-1),
                var(--bg-spot-2);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: var(--font-body);
        }

        .stApp {
            position: relative;
            min-height: 100vh;
        }

        /* Дополнительный "noise"/glow слой можно добавить при необходимости
           через ::before/::after, но Streamlit ограничивает прямой доступ к body.
        */

        /* === ГЛАВНЫЙ КОНТЕЙНЕР === */

        .main > div {
            max-width: var(--container-max-width);
            margin: 0 auto;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        /* === САЙДБАР (перемещаем в стекло) === */

        section[data-testid="stSidebar"] > div {
            background: radial-gradient(circle at 0 0, rgba(88, 28, 135, 0.55), rgba(15, 23, 42, 0.96));
            border-right: 1px solid rgba(148, 163, 184, 0.35);
            box-shadow: 0 0 35px rgba(15, 23, 42, 0.9);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            padding-top: 1.5rem;
        }

        section[data-testid="stSidebar"] * {
            color: var(--text-main);
        }

        /* === ЗАГОЛОВОК / БРЕНДИНГ === */

        .app-header-brand {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 1.75rem;
        }

        .app-logo {
            width: 40px;
            height: 40px;
            border-radius: 14px;
            background: radial-gradient(circle at 30% 0%, #DCDCF0 0%, #280046 45%, #05020a 90%);
            box-shadow:
                0 0 28px rgba(220, 220, 240, 0.55),
                0 0 60px rgba(104, 40, 224, 0.6);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-weight: 700;
            font-family: var(--font-title);
            font-size: 1rem;
            letter-spacing: 0.08em;
        }

        .app-title-block {
            display: flex;
            flex-direction: column;
        }

        .app-title {
            font-family: var(--font-title);
            font-size: 1.6rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--accent-furore);
            text-shadow:
                0 0 24px rgba(255, 255, 255, 0.5),
                0 0 40px rgba(59, 228, 255, 0.7);
        }

        .app-subtitle {
            font-size: 0.86rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: var(--text-muted);
        }

        /* === КАРТОЧКИ (основные панели / секции) === */

        .lg-card {
            background: var(--glass-bg);
            border-radius: var(--radius-lg);
            padding: 1.4rem 1.5rem;
            border: 1px solid var(--glass-border);
            box-shadow: var(--glass-shadow);
            position: relative;
            overflow: hidden;
        }

        .lg-card::before {
            content: "";
            position: absolute;
            inset: -40%;
            background: radial-gradient(circle at 0 0, rgba(220, 220, 240, 0.16), transparent 60%);
            opacity: 0;
            transition: opacity var(--transition-base);
            pointer-events: none;
        }

        .lg-card:hover::before {
            opacity: 1;
        }

        .lg-card-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 0.9rem;
            gap: 0.75rem;
        }

        .lg-card-title {
            font-family: var(--font-title);
            font-size: 1.05rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--accent-furore);
        }

        .lg-card-badge {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(220, 220, 240, 0.5);
            background: rgba(15, 23, 42, 0.75);
            color: var(--text-soft);
        }

        /* === КНОПКИ === */

        button[kind="primary"],
        .stButton > button {
            border-radius: var(--radius-pill);
            border: 1px solid var(--btn-border);
            background-image: var(--btn-bg);
            color: #f9fafb;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 0.55rem 1.35rem;
            box-shadow:
                0 0 22px rgba(59, 228, 255, 0.55),
                0 10px 24px rgba(15, 23, 42, 0.85);
            transition: transform var(--transition-fast), box-shadow var(--transition-base), filter var(--transition-base);
        }

        .stButton > button:hover {
            background-image: var(--btn-bg-hover);
            transform: translateY(-1px);
            box-shadow:
                0 0 36px rgba(255, 46, 170, 0.7),
                0 16px 32px rgba(15, 23, 42, 0.95);
            filter: saturate(1.15);
        }

        .stButton > button:active {
            transform: translateY(1px) scale(0.99);
            box-shadow:
                0 0 14px rgba(59, 228, 255, 0.65),
                0 8px 18px rgba(15, 23, 42, 0.95);
        }

        /* Вторичные и текстовые кнопки */
        .stDownloadButton > button,
        .stButton > button[kind="secondary"] {
            border-radius: var(--radius-pill);
            background: radial-gradient(circle at 0 0, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.96));
            border: 1px solid rgba(148, 163, 184, 0.45);
            color: var(--text-soft);
            text-transform: uppercase;
            font-weight: 500;
            letter-spacing: 0.12em;
            padding: 0.4rem 1.2rem;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.7);
        }

        .stDownloadButton > button:hover,
        .stButton > button[kind="secondary"]:hover {
            border-color: rgba(220, 220, 240, 0.8);
            color: var(--accent-furore);
            box-shadow:
                0 0 25px rgba(59, 228, 255, 0.4),
                0 14px 30px rgba(15, 23, 42, 0.95);
        }

        /* === ПОЛЯ ВВОДА, SELECT, SLIDERS === */

        input[type="text"],
        input[type="number"],
        textarea,
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stSelectbox > div > div,
        .stTextArea textarea {
            background: var(--input-bg);
            border-radius: var(--radius-md);
            border: 1px solid var(--input-border);
            color: var(--text-main);
            box-shadow: var(--shadow-inner);
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput input:focus,
        .stSelectbox > div > div:focus-within,
        .stTextArea textarea:focus {
            border-color: var(--input-border-focus);
            box-shadow:
                0 0 0 1px rgba(59, 130, 246, 0.6),
                0 0 24px rgba(56, 189, 248, 0.5);
        }

        /* Labels */
        label, .stRadio label, .stCheckbox label {
            color: var(--text-soft);
            font-size: 0.86rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }

        /* Sliders */
        .stSlider > div > div > div > div {
            background: rgba(31, 41, 55, 0.8);
        }

        .stSlider [role="slider"] {
            background: radial-gradient(circle at 30% 0, #DCDCF0, #3be4ff);
            box-shadow:
                0 0 18px rgba(59, 228, 255, 0.85),
                0 0 34px rgba(162, 28, 175, 0.85);
        }

        .stSlider > div > div > div > div[data-baseweb="slider"] > div > div {
            background: linear-gradient(90deg, var(--accent-pink), var(--accent-cyan), var(--accent-yellow));
        }

        /* === МЕТРИКИ, КОЛОНКИ, ТАБЛИЦЫ === */

        .stMetric {
            background: var(--glass-bg);
            border-radius: var(--radius-md);
            padding: 0.9rem 1rem;
            border: 1px solid var(--glass-border);
            box-shadow: var(--shadow-soft);
        }

        .stMetric label {
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.7rem;
        }

        .stMetric [data-testid="stMetricValue"] {
            color: var(--accent-furore);
            font-family: var(--font-title);
            font-size: 1.25rem;
            text-shadow: 0 0 20px rgba(59, 228, 255, 0.7);
        }

        .stDataFrame,
        .stTable {
            border-radius: var(--radius-md);
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.5);
            box-shadow: var(--shadow-soft);
        }

        /* === FOOTER / STATUS BAR === */

        .app-footer {
            margin-top: 1.8rem;
            padding: 0.9rem 1.1rem;
            border-radius: var(--radius-lg);
            background: radial-gradient(circle at 0 0, rgba(88, 28, 135, 0.55), rgba(15, 23, 42, 0.98));
            border: 1px solid rgba(148, 163, 184, 0.45);
            box-shadow:
                0 -14px 32px rgba(15, 23, 42, 0.9),
                0 0 40px rgba(59, 228, 255, 0.25);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.78rem;
            color: var(--text-soft);
        }

        .app-footer span.status {
            text-transform: uppercase;
            letter-spacing: 0.14em;
        }

        .app-footer span.status-ok {
            color: var(--text-success);
        }

        .app-footer span.status-warning {
            color: var(--accent-yellow);
        }

        /* === ADAPTIVE === */

        @media (max-width: 900px) {
            .main > div {
                padding: 1.25rem;
            }

            .app-header-brand {
                flex-direction: row;
                align-items: center;
            }

            .lg-card {
                padding: 1.1rem 1.1rem;
            }

            .app-title {
                font-size: 1.25rem;
            }
        }

        @media (max-width: 640px) {
            .app-title {
                font-size: 1.05rem;
            }

            .app-subtitle {
                font-size: 0.72rem;
            }

            .lg-card {
                padding: 1rem;
            }
        }
        </style>
        """
    )
    return css


def apply_design_system() -> None:
    """
    Применяет дизайн‑систему Liquid Glass / Deep Dark Violet к приложению Streamlit.
    Вызывать как можно раньше в main.py.
    """
    st.markdown(get_liquid_glass_css(), unsafe_allow_html=True)
