import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

# --- ЦВЕТОВАЯ ПАЛИТРА TACTICAL INDUSTRIAL ---
COLOR_BG = "#0E1117"          # Основной фон (глубокий антрацит)
COLOR_PANEL = "#161B22"       # Фон панелей/карточек
COLOR_BORDER = "#30363D"      # Цвет границ
COLOR_ACCENT = "#FF9F1C"      # Акцентный (Safety Orange) - для действий
COLOR_DATA_1 = "#00D4FF"      # Данные 1 (Cyber Cyan)
COLOR_DATA_2 = "#FF005C"      # Данные 2 (Neon Red)
COLOR_DATA_3 = "#00E096"      # Данные 3 (Matrix Green)
COLOR_TEXT_MAIN = "#E6EDF3"   # Основной текст
COLOR_TEXT_DIM = "#8B949E"    # Второстепенный текст

def setup_page():
    st.set_page_config(
        page_title="1T Rex // Digital Twin",
        page_icon="🦖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def inject_global_css():
    st.markdown(
        f"""
        <style>
        /* ИМПОРТ ШРИФТОВ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@400;500;700&display=swap');

        /* ГЛОБАЛЬНЫЕ СТИЛИ */
        .stApp {{
            background-color: {COLOR_BG};
            font-family: 'Inter', sans-serif;
            color: {COLOR_TEXT_MAIN};
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: {COLOR_TEXT_MAIN};
            text-transform: none; /* Sentence case enforced */
        }}
        
        /* Заголовки секций с декоративной полоской */
        h2 {{
            border-bottom: 1px solid {COLOR_BORDER};
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }}

        /* САЙДБАР */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_PANEL};
            border-right: 1px solid {COLOR_BORDER};
        }}
        
        /* МЕТРИКИ (HUD Style) */
        [data-testid="stMetric"] {{
            background-color: {COLOR_PANEL};
            border: 1px solid {COLOR_BORDER};
            border-left: 4px solid {COLOR_ACCENT}; /* Оранжевый акцент слева */
            border-radius: 4px; /* Чуть скругленные углы, но строгие */
            padding: 12px 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        
        [data-testid="stMetricLabel"] {{
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            color: {COLOR_TEXT_DIM};
            text-transform: none;
        }}
        
        [data-testid="stMetricValue"] {{
            font-family: 'JetBrains Mono', monospace; /* Моноширинный для цифр */
            font-size: 1.8rem;
            font-weight: 700;
            color: {COLOR_TEXT_MAIN};
        }}
        
        [data-testid="stMetricDelta"] {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
        }}

        /* КНОПКИ (Tactical Buttons) */
        .stButton button {{
            background-color: transparent;
            color: {COLOR_ACCENT};
            border: 1px solid {COLOR_ACCENT};
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            text-transform: none;
            transition: all 0.2s ease;
        }}
        
        .stButton button:hover {{
            background-color: {COLOR_ACCENT};
            color: #000000;
            border-color: {COLOR_ACCENT};
            box-shadow: 0 0 10px {COLOR_ACCENT}40; /* Свечение */
        }}
        
        .stButton button:active {{
            transform: translateY(1px);
        }}

        /* Вкладки (Tabs) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 40px;
            border-radius: 4px;
            background-color: transparent;
            color: {COLOR_TEXT_DIM};
            border: 1px solid transparent;
            font-family: 'Inter', sans-serif;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            color: {COLOR_ACCENT};
            background-color: {COLOR_PANEL};
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {COLOR_PANEL};
            color: {COLOR_ACCENT};
            border: 1px solid {COLOR_BORDER};
            border-bottom: 2px solid {COLOR_ACCENT};
        }}

        /* Input fields & Sliders */
        .stSlider [data-baseweb="slider"] {{
            /* Сложно стилизовать глубоко, но основные цвета подтянутся из темы */
        }}
        
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT_MAIN};
            border: 1px solid {COLOR_BORDER};
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* МИНИ-ПРЕВЬЮ В САЙДБАРЕ */
        .sidebar-preview {{
            background-color: rgba(22, 27, 34, 0.8);
            border: 1px solid {COLOR_BORDER};
            border-top: 2px solid {COLOR_DATA_1};
            border-radius: 4px;
            padding: 16px;
            margin: 16px 0;
            backdrop-filter: blur(4px);
        }}
        
        .preview-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.2rem;
            font-weight: 700;
            color: {COLOR_TEXT_MAIN};
            letter-spacing: -0.5px;
        }}
        
        .preview-label {{
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            color: {COLOR_TEXT_DIM};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}
        
        /* Comparison Card */
        .comparison-card {{
            background-color: {COLOR_PANEL};
            border: 1px solid {COLOR_BORDER};
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 12px;
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: {COLOR_PANEL};
            border: 1px solid {COLOR_BORDER};
            border-radius: 4px;
            color: {COLOR_TEXT_MAIN};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# --- УТИЛИТА ДЛЯ ГРАФИКОВ (PLOTLY THEME) ---
def apply_tactical_theme(fig):
    """Применяет тему Tactical Industrial к графикам Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono", color=COLOR_TEXT_DIM),
        title_font=dict(family="Inter", size=18, color=COLOR_TEXT_MAIN),
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor=COLOR_BORDER,
            zeroline=False,
            showline=True,
            linecolor=COLOR_BORDER
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor=COLOR_BORDER,
            zeroline=False,
            showline=True,
            linecolor=COLOR_BORDER
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)"
        )
    )
    return fig

# --- КОМПОНЕНТЫ UI ---

def render_sidebar_preview(static_res: Dict, sim_stats: Dict):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Телеметрия (Live)")
    
    preview_html = f"""
    <div class="sidebar-preview">
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div class="preview-label">СКОРОСТЬ</div>
                <div class="preview-value" style="color: {COLOR_DATA_1};">{static_res['speed_kmh']:.1f} <span style="font-size:0.8em; color:{COLOR_TEXT_DIM}">км/ч</span></div>
            </div>
            <div style="text-align: right;">
                <div class="preview-label">МАССА</div>
                <div class="preview-value">{static_res['total_mass']:.1f} <span style="font-size:0.8em; color:{COLOR_TEXT_DIM}">кг</span></div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <div class="preview-label">ЭНЕРГИЯ</div>
                <div class="preview-value" style="color: {COLOR_ACCENT};">{static_res['weapon_energy']/1000:.1f} <span style="font-size:0.8em; color:{COLOR_TEXT_DIM}">кДж</span></div>
            </div>
            <div style="text-align: right;">
                <div class="preview-label">ТОК (ПИК)</div>
                <div class="preview-value">{sim_stats.get('peak_current', 0):.0f} <span style="font-size:0.8em; color:{COLOR_TEXT_DIM}">А</span></div>
            </div>
        </div>
    </div>
    """
    st.sidebar.markdown(preview_html, unsafe_allow_html=True)
    
    # Индикатор массы (кастомный прогресс бар через HTML, так как стандартный нельзя перекрасить)
    mass_pct = min((static_res['total_mass'] / 110.0) * 100, 100)
    bar_color = COLOR_DATA_3 if mass_pct <= 90 else (COLOR_ACCENT if mass_pct <= 100 else COLOR_DATA_2)
    
    st.sidebar.markdown(
        f"""
        <div style="margin-top: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: {COLOR_TEXT_DIM}; margin-bottom: 4px;">
                <span>НАГРУЗКА ШАССИ</span>
                <span>{mass_pct:.1f}%</span>
            </div>
            <div style="width: 100%; background-color: {COLOR_BORDER}; height: 4px; border-radius: 2px;">
                <div style="width: {mass_pct}%; background-color: {bar_color}; height: 4px; border-radius: 2px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if static_res['total_mass'] > 110:
        st.sidebar.markdown(f"<div style='color:{COLOR_DATA_2}; font-size: 0.8rem; margin-top: 4px;'>⚠️ ПЕРЕГРУЗКА: +{static_res['total_mass'] - 110:.1f} КГ</div>", unsafe_allow_html=True)


def render_kpi_row(static_res: Dict, sim_stats: Dict, total_mass_limit: float):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Скорость (теор.)", f"{static_res['speed_kmh']:.1f} км/ч")
    col2.metric("Энергия удара", f"{static_res['weapon_energy']/1000:.1f} кДж")
    delta_mass = total_mass_limit - static_res["total_mass"]
    col3.metric(
        "Масса",
        f"{static_res['total_mass']:.1f} кг",
        f"{delta_mass:+.1f} кг",
        delta_color="normal" if delta_mass >= 0 else "inverse",
    )
    col4.metric("Пиковый ток", f"{sim_stats['peak_current']:.0f} А", sim_stats["wire_awg"])


def render_weight_pie(static_res: Dict, base_drive: float, base_elec: float, base_frame: float):
    mass_dict = {
        "Броня": static_res["armor_mass"],
        "Оружие": static_res["weapon_inertia"] * 10, # Scaling for visibility assumption
        "Ходовая": base_drive,
        "Электроника": base_elec,
        "Рама": base_frame,
    }
    df = pd.DataFrame({"Компонент": mass_dict.keys(), "Масса": mass_dict.values()})
    
    fig = px.pie(
        df, values="Масса", names="Компонент",
        title="Распределение массы (Weight Budget)",
        hole=0.5,
        color_discrete_sequence=[COLOR_DATA_1, COLOR_DATA_3, COLOR_ACCENT, "#8e44ad", "#e74c3c"]
    )
    fig.update_traces(textinfo='percent+label', textfont_size=13)
    st.plotly_chart(apply_tactical_theme(fig), use_container_width=True)


def render_drive_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sim["t"], y=df_sim["v_kmh"], name="Скорость",
        line=dict(color=COLOR_DATA_1, width=3), yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=df_sim["t"], y=df_sim["I_bat"], name="Ток",
        line=dict(color=COLOR_DATA_2, dash="dot", width=2), yaxis="y2"
    ))
    fig.update_layout(
        title="Динамика разгона",
        xaxis_title="Время (с)",
        yaxis=dict(title="Скорость (км/ч)", titlefont=dict(color=COLOR_DATA_1)),
        yaxis2=dict(title="Ток (А)", overlaying="y", side="right", titlefont=dict(color=COLOR_DATA_2)),
        hovermode="x unified"
    )
    st.plotly_chart(apply_tactical_theme(fig), use_container_width=True)


def render_thermal_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sim["t"], y=df_sim["T_drive"], name="Двигатели хода",
        line=dict(color=COLOR_DATA_3, width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df_sim["t"], y=df_sim["T_weapon"], name="Двигатели оружия",
        line=dict(color=COLOR_ACCENT, width=3)
    ))
    fig.add_hline(y=100, line_dash="dash", line_color=COLOR_DATA_2, annotation_text="ПРЕДЕЛ (100°C)")
    fig.update_layout(
        title="Тепловой профиль",
        xaxis_title="Время (с)",
        yaxis_title="Температура (°C)",
    )
    st.plotly_chart(apply_tactical_theme(fig), use_container_width=True)


def render_parameter_scan_plots(df_scan: pd.DataFrame, param_name: str, param_unit: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scan["param_value"], y=df_scan["speed_kmh"],
        name="Скорость", line=dict(color=COLOR_DATA_1, width=3),
        mode="lines+markers"
    ))
    fig.update_layout(
        title=f"Анализ чувствительности: {param_name}",
        xaxis_title=f"{param_name} ({param_unit})",
        yaxis_title="Скорость (км/ч)",
        hovermode="x unified"
    )
    st.plotly_chart(apply_tactical_theme(fig), use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    def small_plot(y_col, title, color):
        f = go.Figure()
        f.add_trace(go.Scatter(
            x=df_scan["param_value"], y=df_scan[y_col],
            line=dict(color=color, width=2), mode="lines"
        ))
        f.update_layout(title=title, margin=dict(l=20,r=20,t=40,b=20), height=200)
        return apply_tactical_theme(f)
    
    with col1: st.plotly_chart(small_plot("total_mass", "Масса (кг)", COLOR_ACCENT), use_container_width=True)
    with col2: st.plotly_chart(small_plot("peak_current", "Ток (А)", COLOR_DATA_2), use_container_width=True)
    with col3: st.plotly_chart(small_plot("time_to_20", "Разгон (с)", COLOR_DATA_3), use_container_width=True)


def render_comparison_view(config_a: Dict, config_b: Dict, comparison: Dict):
    col_a, col_b = st.columns(2)
    
    def render_card(conf, is_diff=False, comp_data=None):
        border_col = COLOR_DATA_3 if is_diff else COLOR_DATA_1
        st.markdown(f"""
        <div style="border: 1px solid {border_col}; border-radius: 4px; padding: 16px; background-color: {COLOR_PANEL}; height: 100%;">
            <h3 style="color: {border_col}; margin-top: 0;">{conf['name']}</h3>
        """, unsafe_allow_html=True)
        
        metrics = [
            ("Скорость", "speed_kmh", "км/ч"),
            ("Масса", "total_mass", "кг"),
            ("Энергия", "weapon_energy_kj", "кДж"),
            ("Ток", "peak_current", "А"),
            ("Перегрузка", "g_force_self", "G")
        ]
        
        for label, key, unit in metrics:
            val = conf[key]
            delta_html = ""
            if is_diff and comp_data:
                d = comp_data[key]['delta']
                d_pct = comp_data[key]['delta_pct']
                color = COLOR_DATA_3 if d >= 0 else COLOR_DATA_2 # Упрощено
                if key in ['total_mass', 'peak_current', 'g_force_self']: # Меньше = лучше
                    color = COLOR_DATA_3 if d <= 0 else COLOR_DATA_2
                
                sign = "+" if d > 0 else ""
                delta_html = f"<span style='color:{color}; font-size: 0.8em; margin-left: 8px;'>{sign}{d:.1f} ({sign}{d_pct:.1f}%)</span>"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid {COLOR_BORDER}; padding-bottom: 4px;">
                <span style="color: {COLOR_TEXT_DIM}; font-size: 0.9em;">{label}</span>
                <span style="font-family: 'JetBrains Mono'; font-weight: 600;">{val:.1f} {delta_html}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col_a: render_card(config_a)
    with col_b: render_card(config_b, is_diff=True, comp_data=comparison)


def render_optimization_progress(history: list):
    if not history: return
    df_hist = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=df_hist["score"], mode="lines+markers", name="Функция потерь",
        line=dict(color=COLOR_ACCENT, width=2)
    ))
    fig.update_layout(
        title="Сходимость алгоритма",
        xaxis_title="Итерация", yaxis_title="Штрафная функция"
    )
    st.plotly_chart(apply_tactical_theme(fig), use_container_width=True)
