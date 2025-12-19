import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict


def setup_page():
    st.set_page_config(
        page_title="Digital Twin: 1T Rex",
        page_icon="🦖",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_css():
    st.markdown(
        """
        <style>
        /* --- ИМПОРТ ШРИФТОВ --- */
        @import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@300;400;600;700&family=Raleway:wght@300;400;500;600;700&display=swap');

        /* --- CSS ПЕРЕМЕННЫЕ --- */
        :root {
            --bg-color: #05020a;
            --text-main: #ffffff;
            --text-secondary: #c0bdd0;
            --text-tertiary: #7a7788;
            
            --accent-primary: #d50085; 
            --accent-secondary: #0099ff; 
            --accent-gradient: linear-gradient(270deg, #d50085 0%, #0099ff 100%);
            
            --surface-bg: rgba(20, 15, 35, 0.35);
            --surface-border: rgba(255, 255, 255, 0.08);
            --surface-glow: rgba(0, 153, 255, 0.1);
            
            --font-head: 'Unbounded', sans-serif;
            --font-body: 'Raleway', sans-serif;
        }

        /* --- СБРОС STREAMLIT СТИЛЕЙ --- */
        .stApp {
            background-color: var(--bg-color) !important;
            background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #05020a 70%) !important;
            background-attachment: fixed;
            font-family: var(--font-body) !important;
            color: var(--text-main) !important;
        }

        /* Убираем лишние отступы */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 2rem !important;
        }

        /* --- ТИПОГРАФИКА --- */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-head) !important;
            color: var(--text-main) !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
        }
        
        /* Главный заголовок с градиентом */
        h1 {
            background: var(--accent-gradient) !important;
            background-size: 200% 200% !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            animation: gradient-shift 8s ease infinite;
        }

        @keyframes gradient-shift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        /* Заголовки в сайдбаре */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4 {
            color: var(--text-main) !important;
            font-size: 1rem !important;
            margin-bottom: 0.5rem !important;
        }

        /* Обычный текст */
        p, span, div, label {
            font-family: var(--font-body) !important;
            color: var(--text-secondary) !important;
        }

        /* --- САЙДБАР (GLASSMORPHISM) --- */
        section[data-testid="stSidebar"] {
            background: rgba(5, 2, 10, 0.7) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid var(--surface-border) !important;
        }

        section[data-testid="stSidebar"] > div {
            background-color: transparent !important;
        }

        /* --- МЕТРИКИ (KPI КАРТОЧКИ) --- */
        div[data-testid="stMetric"] {
            background: var(--surface-bg) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border: 1px solid var(--surface-border) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px) !important;
            border-color: var(--accent-secondary) !important;
            box-shadow: 0 8px 30px var(--surface-glow) !important;
        }

        /* Лейблы метрик (КАПИТЕЛЬ) */
        div[data-testid="stMetric"] label {
            font-family: var(--font-body) !important;
            color: var(--text-tertiary) !important;
            font-size: 0.75rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            font-weight: 600 !important;
            margin-bottom: 8px !important;
        }
        
        /* Значения метрик */
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-family: var(--font-head) !important;
            color: var(--text-main) !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Дельта метрик */
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-family: var(--font-head) !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }

        /* --- КНОПКИ --- */
        .stButton button {
            background: transparent !important;
            border: 1.5px solid var(--accent-secondary) !important;
            color: var(--accent-secondary) !important;
            font-family: var(--font-head) !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton button:before {
            content: '' !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 100% !important;
            height: 100% !important;
            background: var(--accent-gradient) !important;
            transition: left 0.3s ease !important;
            z-index: -1 !important;
        }
        
        .stButton button:hover {
            color: #000 !important;
            border-color: transparent !important;
            box-shadow: 0 0 25px rgba(0, 153, 255, 0.6) !important;
        }
        
        .stButton button:hover:before {
            left: 0 !important;
        }
        
        .stButton button:active {
            transform: scale(0.97) !important;
        }

        /* --- ТАБЫ --- */
        .stTabs {
            background: transparent !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 6px !important;
            background-color: transparent !important;
            border-bottom: 1px solid var(--surface-border) !important;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(5px) !important;
            border: 1px solid transparent !important;
            border-radius: 10px 10px 0 0 !important;
            color: var(--text-tertiary) !important;
            font-family: var(--font-body) !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            padding: 10px 18px !important;
            transition: all 0.2s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.05) !important;
            color: var(--text-main) !important;
            border-color: rgba(255, 255, 255, 0.1) !important;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(213, 0, 133, 0.15), rgba(0, 153, 255, 0.15)) !important;
            border: 1px solid rgba(213, 0, 133, 0.4) !important;
            border-bottom-color: transparent !important;
            color: #fff !important;
            font-weight: 600 !important;
            box-shadow: 0 -2px 15px rgba(213, 0, 133, 0.2) !important;
        }

        /* --- ИНПУТЫ И СЕЛЕКТЫ --- */
        .stTextInput input, .stNumberInput input {
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: var(--text-main) !important;
            font-family: var(--font-body) !important;
            padding: 0.6rem 0.8rem !important;
            transition: all 0.2s ease !important;
        }

        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: var(--accent-secondary) !important;
            box-shadow: 0 0 0 1px var(--accent-secondary) !important;
            outline: none !important;
        }

        /* Селекты */
        div[data-baseweb="select"] > div {
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 10px !important;
            color: var(--text-main) !important;
        }

        div[data-baseweb="select"] > div:hover {
            border-color: rgba(255, 255, 255, 0.25) !important;
        }

        /* --- СЛАЙДЕРЫ --- */
        div[data-baseweb="slider"] {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
        }

        /* Трек слайдера */
        div[data-baseweb="slider"] [role="slider"] {
            background: var(--accent-gradient) !important;
            box-shadow: 0 0 15px rgba(213, 0, 133, 0.5) !important;
            width: 18px !important;
            height: 18px !important;
        }

        div[data-baseweb="slider"] [role="slider"]:hover {
            box-shadow: 0 0 25px rgba(213, 0, 133, 0.8) !important;
        }

        /* Линия слайдера */
        div[data-baseweb="slider"] > div > div {
            background: rgba(255, 255, 255, 0.1) !important;
        }

        /* Заполненная часть */
        div[data-baseweb="slider"] > div > div > div {
            background: var(--accent-gradient) !important;
        }

        /* --- ПРОГРЕСС-БАР --- */
        .stProgress > div > div > div {
            background: var(--accent-gradient) !important;
        }

        /* --- EXPANDER (АККОРДЕОН) --- */
        div[data-testid="stExpander"] {
            background: var(--surface-bg) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--surface-border) !important;
            border-radius: 12px !important;
        }

        div[data-testid="stExpander"] summary {
            color: var(--text-main) !important;
            font-weight: 600 !important;
        }

        /* --- DATAFRAME --- */
        div[data-testid="stDataFrame"] {
            background: var(--surface-bg) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--surface-border) !important;
            border-radius: 12px !important;
        }

        /* --- КАСТОМНЫЕ КЛАССЫ --- */
        .sidebar-preview {
            background: linear-gradient(145deg, rgba(30, 20, 60, 0.5), rgba(10, 5, 30, 0.7)) !important;
            backdrop-filter: blur(15px) !important;
            border: 1px solid rgba(0, 153, 255, 0.25) !important;
            border-radius: 14px !important;
            padding: 20px !important;
            margin: 15px 0 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        }
        
        .preview-value {
            font-family: var(--font-head) !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: #00d4ff !important;
            text-shadow: 0 0 12px rgba(0, 212, 255, 0.5) !important;
        }
        
        .preview-label {
            font-family: var(--font-body) !important;
            font-size: 0.7rem !important;
            color: var(--text-tertiary) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            margin-bottom: 6px !important;
        }

        /* --- УБИРАЕМ ЛИШНЕЕ --- */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_preview(static_res: Dict, sim_stats: Dict):
    """Мини-превью результатов в сайдбаре (Live Preview)."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### ⚡ Телеметрия")
    
    preview_html = f"""
    <div class="sidebar-preview">
        <div style="display: flex; justify-content: space-between; margin-bottom: 14px;">
            <div>
                <div class="preview-label">Скорость</div>
                <div class="preview-value">{static_res['speed_kmh']:.1f} <span style="font-size:0.75rem; opacity:0.7;">км/ч</span></div>
            </div>
            <div style="text-align: right;">
                <div class="preview-label">Масса</div>
                <div class="preview-value" style="color: #d50085; text-shadow: 0 0 12px rgba(213,0,133,0.5);">{static_res['total_mass']:.1f} <span style="font-size:0.75rem; opacity:0.7;">кг</span></div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <div class="preview-label">Энергия</div>
                <div class="preview-value" style="color: #ffffff; text-shadow: 0 0 12px rgba(255,255,255,0.3);">{static_res['weapon_energy']/1000:.1f} <span style="font-size:0.75rem; opacity:0.7;">кДж</span></div>
            </div>
            <div style="text-align: right;">
                <div class="preview-label">Пик тока</div>
                <div class="preview-value" style="color: #ff9900; text-shadow: 0 0 12px rgba(255,153,0,0.5);">{sim_stats.get('peak_current', 0):.0f} <span style="font-size:0.75rem; opacity:0.7;">А</span></div>
            </div>
        </div>
    </div>
    """
    st.sidebar.markdown(preview_html, unsafe_allow_html=True)
    
    # Прогресс-бар массы
    mass_percent = (static_res['total_mass'] / 110.0) * 100
    if mass_percent > 100:
        st.sidebar.error(f"⚠️ Перевес: {static_res['total_mass'] - 110:.1f} кг")
    else:
        st.sidebar.progress(mass_percent / 100, text=f"Лимит массы: {mass_percent:.1f}%")


def render_kpi_row(static_res: Dict, sim_stats: Dict, total_mass_limit: float):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Скорость", f"{static_res['speed_kmh']:.1f} км/ч")
    col2.metric("Энергия удара", f"{static_res['weapon_energy']/1000:.1f} кДж")
    delta_mass = total_mass_limit - static_res["total_mass"]
    col3.metric(
        "Масса",
        f"{static_res['total_mass']:.1f} кг",
        f"{delta_mass:+.1f} кг",
        delta_color="normal" if delta_mass >= 0 else "inverse",
    )
    col4.metric("Пиковый ток", f"{sim_stats['peak_current']:.0f} А", sim_stats["wire_awg"])


def _apply_dark_theme(fig, title_text: str):
    """Единая функция для применения темной темы ко всем графикам."""
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(family="Unbounded", size=18, color="#ffffff"),
            x=0.05
        ),
        paper_bgcolor='rgba(0,0,0,0)',           # Прозрачный внешний фон
        plot_bgcolor='rgba(10, 5, 20, 0.35)',    # Полупрозрачный темный фон графика
        font=dict(family="Raleway", color="#c0bdd0", size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            gridwidth=1,
            zerolinecolor='rgba(255,255,255,0.1)',
            color='#c0bdd0'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            gridwidth=1,
            zerolinecolor='rgba(255,255,255,0.1)',
            color='#c0bdd0'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0.3)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(color="#ffffff")
        ),
        hovermode="x unified",
        margin=dict(l=60, r=40, t=80, b=60),
        hoverlabel=dict(
            bgcolor="rgba(10, 5, 20, 0.9)",
            font_size=13,
            font_family="Raleway"
        )
    )
    return fig


def render_weight_pie(static_res: Dict, base_drive: float,
                      base_elec: float, base_frame: float):
    mass_dict = {
        "Броня": static_res["armor_mass"],
        "Оружие": static_res["weapon_inertia"] * 10,
        "Ходовая": base_drive,
        "Электроника": base_elec,
        "Рама": base_frame,
    }
    df = pd.DataFrame(
        {"Компонент": mass_dict.keys(), "Масса": mass_dict.values()}
    )
    
    # Киберпанк-палитра
    colors = ['#5200cc', '#d50085', '#0099ff', '#00d4ff', '#8a00d4']
    
    fig = px.pie(
        df,
        values="Масса",
        names="Компонент",
        hole=0.55,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='outside',
        textinfo='label+percent',
        marker=dict(line=dict(color='rgba(0,0,0,0.5)', width=2))
    )
    
    fig.update_layout(
        title=dict(text="Весовой бюджет", font=dict(family="Unbounded", size=18, color="#ffffff")),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Raleway", color="#c0bdd0", size=12),
        showlegend=True,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Центральная цифра
    fig.add_annotation(
        text=f"{static_res['total_mass']:.1f}<br><span style='font-size:14px'>кг</span>",
        x=0.5, y=0.5,
        font=dict(size=24, color="white", family="Unbounded"),
        showarrow=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_drive_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    
    # Скорость (циан, толстая линия)
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["v_kmh"],
            name="Скорость",
            line=dict(color="#00d4ff", width=3.5),
            yaxis="y1",
        )
    )
    
    # Ток (маджента, пунктир)
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["I_bat"],
            name="Ток АКБ",
            line=dict(color="#d50085", width=2.5, dash="dot"),
            yaxis="y2",
        )
    )
    
    fig = _apply_dark_theme(fig, "Разгон и нагрузка на батарею")
    
    fig.update_layout(
        yaxis=dict(title="Скорость (км/ч)", title_font=dict(color="#00d4ff")),
        yaxis2=dict(
            title="Ток (А)",
            overlaying="y",
            side="right",
            title_font=dict(color="#d50085")
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_thermal_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_drive"],
            name="Двигатели хода",
            line=dict(color="#ff9900", width=3),
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_weapon"],
            name="Двигатели оружия",
            line=dict(color="#ff3333", width=3),
        )
    )
    
    # Критическая зона
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="rgba(255, 51, 51, 0.6)",
        line_width=2,
        annotation_text="Критическая зона",
        annotation_position="right",
        annotation_font=dict(color="#ff3333", size=11)
    )
    
    fig = _apply_dark_theme(fig, "Тепловой режим моторов")
    fig.update_layout(yaxis_title="Температура (°C)")
    
    st.plotly_chart(fig, use_container_width=True)


def render_parameter_scan_plots(df_scan: pd.DataFrame, param_name: str, param_unit: str):
    """Визуализация результатов параметрического сканирования."""
    
    # Главный график
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scan["param_value"],
        y=df_scan["speed_kmh"],
        name="Скорость",
        line=dict(color="#00d4ff", width=3.5),
        mode="lines+markers",
        marker=dict(
            size=9,
            color="#05020a",
            line=dict(width=2, color="#00d4ff")
        )
    ))
    
    fig = _apply_dark_theme(fig, f"Зависимость скорости от {param_name}")
    fig.update_layout(
        xaxis_title=f"{param_name} ({param_unit})",
        yaxis_title="Скорость (км/ч)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Мини-графики
    col1, col2, col3 = st.columns(3)
    
    def _create_mini_plot(x, y, title, color):
        f = go.Figure()
        f.add_trace(go.Scatter(
            x=x, y=y,
            line=dict(color=color, width=2.5),
            mode="lines",
            fill='tozeroy',
            fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}'
        ))
        f.update_layout(
            title=dict(text=title, font=dict(size=13, color="white", family="Unbounded")),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,5,20,0.3)',
            font=dict(family="Raleway", color="#999", size=10),
            margin=dict(l=40, r=10, t=50, b=30),
            height=220,
            xaxis=dict(showgrid=False, color="#777"),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', color="#777")
        )
        return f

    with col1:
        st.plotly_chart(_create_mini_plot(df_scan["param_value"], df_scan["total_mass"], "Масса (кг)", "#ff9900"), use_container_width=True)
    with col2:
        st.plotly_chart(_create_mini_plot(df_scan["param_value"], df_scan["peak_current"], "Пиковый ток (А)", "#ff3333"), use_container_width=True)
    with col3:
        st.plotly_chart(_create_mini_plot(df_scan["param_value"], df_scan["time_to_20"], "Разгон 0-20 км/ч (с)", "#00ff99"), use_container_width=True)


def render_comparison_view(config_a: Dict, config_b: Dict, comparison: Dict):
    """Side-by-side сравнение двух конфигураций."""
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(f"### 🔵 {config_a['name']}")
        st.metric("Скорость", f"{config_a['speed_kmh']:.1f} км/ч")
        st.metric("Масса", f"{config_a['total_mass']:.1f} кг")
        st.metric("Энергия удара", f"{config_a['weapon_energy_kj']:.1f} кДж")
        st.metric("Пиковый ток", f"{config_a['peak_current']:.0f} А")
        st.metric("Перегрузка", f"{config_a['g_force_self']:.1f} G")
    
    with col_b:
        st.markdown(f"### 🟢 {config_b['name']}")
        st.metric(
            "Скорость",
            f"{config_b['speed_kmh']:.1f} км/ч",
            f"{comparison['speed_kmh']['delta']:+.1f}"
        )
        st.metric(
            "Масса",
            f"{config_b['total_mass']:.1f} кг",
            f"{comparison['total_mass']['delta']:+.1f}"
        )
        st.metric(
            "Энергия удара",
            f"{config_b['weapon_energy_kj']:.1f} кДж",
            f"{comparison['weapon_energy_kj']['delta']:+.1f}"
        )
        st.metric(
            "Пиковый ток",
            f"{config_b['peak_current']:.0f} А",
            f"{comparison['peak_current']['delta']:+.0f}"
        )
        st.metric(
            "Перегрузка",
            f"{config_b['g_force_self']:.1f} G",
            f"{comparison['g_force_self']['delta']:+.1f}"
        )


def render_optimization_progress(history: list):
    """Визуализация прогресса оптимизации."""
    if not history:
        return
    
    df_hist = pd.DataFrame(history)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=df_hist["score"],
        mode="lines+markers",
        name="Целевая функция",
        line=dict(color="#00ff99", width=3),
        marker=dict(
            size=7,
            color="#05020a",
            line=dict(width=2, color="#00ff99")
        )
    ))
    
    fig = _apply_dark_theme(fig, "Сходимость оптимизации")
    fig.update_layout(
        xaxis_title="Итерация",
        yaxis_title="Целевая функция (меньше = лучше)"
    )
    st.plotly_chart(fig, use_container_width=True)
