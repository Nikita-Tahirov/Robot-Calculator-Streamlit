# styles.py
import streamlit as st

def apply_design_system():
    """
    Применяет глобальные стили Liquid Glass / Deep Dark Violet.
    """
    st.markdown("""
        <style>
        /* === ИМПОРТ ШРИФТОВ === */
        @import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@400;600;700&family=Raleway:wght@300;400;600&display=swap');

        :root {
            /* Палитра Deep Space */
            --bg-dark: #05020a;
            --brand-violet: #280046;
            --accent-furore: #DCDCF0;
            --neon-blue: #3be4ff;
            --neon-pink: #ff2eaa;
            
            /* Стекло */
            --glass-bg: linear-gradient(145deg, rgba(20, 15, 35, 0.75), rgba(10, 5, 20, 0.85));
            --glass-border: 1px solid rgba(220, 220, 240, 0.15);
            --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            
            /* Текст */
            --text-main: #ECECF5;
            --text-muted: #9CA3AF;
        }

        /* Глобальный сброс и фон */
        .stApp {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 50% 0%, #2a1045 0%, transparent 60%),
                radial-gradient(circle at 90% 90%, #101530 0%, transparent 50%);
            background-attachment: fixed;
            font-family: 'Raleway', sans-serif;
            color: var(--text-main);
        }

        /* === ТИПОГРАФИКА === */
        h1, h2, h3 {
            font-family: 'Unbounded', sans-serif !important;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: var(--text-main) !important;
        }
        
        h1 {
            background: linear-gradient(90deg, var(--accent-furore), var(--neon-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(59, 228, 255, 0.3);
        }

        /* === КАРТОЧКИ === */
        .lg-card {
            background: var(--glass-bg);
            border: var(--glass-border);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: var(--glass-shadow);
            backdrop-filter: blur(12px);
            transition: transform 0.3s ease;
        }
        
        .lg-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(59, 228, 255, 0.15);
            border-color: rgba(59, 228, 255, 0.3);
        }

        /* === САЙДБАР === */
        section[data-testid="stSidebar"] {
            background-color: rgba(5, 2, 10, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* === ВИДЖЕТЫ INPUT === */
        .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: var(--accent-furore) !important;
            border-radius: 10px !important;
        }
        
        /* Слайдеры */
        div[data-baseweb="slider"] div {
            background: linear-gradient(90deg, var(--brand-violet), var(--neon-blue));
        }

        /* === КНОПКИ === */
        .stButton button {
            background: linear-gradient(135deg, var(--brand-violet), #4c1d95) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: white !important;
            font-family: 'Unbounded', sans-serif !important;
            font-weight: 600 !important;
            border-radius: 50px !important;
            box-shadow: 0 0 15px rgba(76, 29, 149, 0.5);
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
            box-shadow: 0 0 25px rgba(59, 228, 255, 0.6);
            transform: scale(1.02);
            border-color: var(--neon-blue) !important;
        }

        /* === МЕТРИКИ === */
        div[data-testid="stMetricValue"] {
            font-family: 'Unbounded', sans-serif;
            color: var(--neon-blue) !important;
            text-shadow: 0 0 10px rgba(59, 228, 255, 0.4);
        }
        div[data-testid="stMetricLabel"] {
            color: var(--text-muted) !important;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)

def card_start():
    st.markdown('<div class="lg-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)
