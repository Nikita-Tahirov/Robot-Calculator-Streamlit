import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict
from theme_config import *


def setup_page():
    """Настройка страницы с принудительной светлой темой."""
    st.set_page_config(
        page_title="Цифровой двойник: 1T Rex",
        page_icon="🦖",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_css():
    """Глобальные стили с форсированием светлой темы (перекрывает системную темную тему)."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* === ФОРСИРУЕМ СВЕТЛУЮ ТЕМУ === */
        /* Перекрываем системные настройки браузера */
        :root {{
            color-scheme: light !important;
        }}
        
        * {{
            font-family: {FONT_FAMILY};
            color-scheme: light !important;
        }}
        
        /* Все фоны принудительно белые/светлые */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background-color: {SURFACE_BG} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        .main {{
            background-color: {SURFACE_BG} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        .main .block-container {{
            background-color: {SURFACE_BG} !important;
        }}
        
        /* Сайдбар */
        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG} !important;
            border-right: 1px solid {OUTLINE} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        section[data-testid="stSidebar"] > div {{
            background-color: {SIDEBAR_BG} !important;
            padding-top: 2rem;
        }}
        
        section[data-testid="stSidebar"] * {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* === ТИПОГРАФИКА === */
        h1, h2, h3, h4, h5, h6 {{
            color: {TEXT_PRIMARY} !important;
            font-weight: 600;
            letter-spacing: -0.02em;
        }}
        
        p, label, span, div {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* === МЕТРИКИ === */
        [data-testid="stMetric"] {{
            background: {SURFACE_VARIANT} !important;
            border: 1px solid {OUTLINE} !important;
            border-radius: {RADIUS_MEDIUM};
            padding: 1.25rem;
            box-shadow: {SHADOW_1};
        }}
        
        [data-testid="stMetric"] label {{
            color: {TEXT_SECONDARY} !important;
            font-size: 0.875rem;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {PRIMARY} !important;
            font-size: 2rem;
            font-weight: 700;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            color: {SUCCESS} !important;
        }}
        
        /* === КНОПКИ === */
        .stButton > button {{
            background: {PRIMARY} !important;
            color: white !important;
            border: none !important;
            border-radius: {RADIUS_PILL};
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            box-shadow: {SHADOW_1};
        }}
        
        .stButton > button:hover {{
            background: {PRIMARY_DARK} !important;
            transform: translateY(-1px);
        }}
        
        /* === ТАБЫ === */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {SURFACE_BG} !important;
            border-bottom: 2px solid {OUTLINE} !important;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent !important;
            color: {TEXT_SECONDARY} !important;
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {PRIMARY} !important;
            border-bottom: 3px solid {PRIMARY} !important;
            font-weight: 600;
        }}
        
        /* === ИНПУТЫ === */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {{
            background: {SURFACE_BG} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {OUTLINE} !important;
            border-radius: {RADIUS_SMALL};
        }}
        
        .stSelectbox {{
            background-color: {SURFACE_BG} !important;
        }}
        
        .stSelectbox [data-baseweb="select"] {{
            background-color: {SURFACE_BG} !important;
        }}
        
        /* Dropdown меню */
        [data-baseweb="popover"] {{
            background-color: {SURFACE_BG} !important;
        }}
        
        [role="listbox"] {{
            background-color: {SURFACE_BG} !important;
        }}
        
        [role="option"] {{
            background-color: {SURFACE_BG} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        [role="option"]:hover {{
            background-color: {SURFACE_VARIANT} !important;
        }}
        
        /* === СЛАЙДЕРЫ === */
        .stSlider {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        .stSlider [data-testid="stTickBar"] > div {{
            background: {OUTLINE} !important;
        }}
        
        .stSlider [data-baseweb="slider"] {{
            background: transparent !important;
        }}
        
        /* === CHECKBOX === */
        .stCheckbox {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        .stCheckbox label {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* === ПРОГРЕСС БАР === */
        .stProgress > div > div > div {{
            background-color: {OUTLINE} !important;
        }}
        
        .stProgress > div > div > div > div {{
            background-color: {PRIMARY} !important;
        }}
        
        /* === MARKDOWN === */
        .stMarkdown {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* === DATAFRAME === */
        [data-testid="stDataFrame"] {{
            background-color: {SURFACE_BG} !important;
        }}
        
        .dataframe {{
            background-color: {SURFACE_BG} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        .dataframe th {{
            background-color: {SURFACE_VARIANT} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        .dataframe td {{
            background-color: {SURFACE_BG} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* === EXPANDER === */
        .streamlit-expanderHeader {{
            background-color: {SURFACE_VARIANT} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {OUTLINE} !important;
        }}
        
        .streamlit-expanderContent {{
            background-color: {SURFACE_BG} !important;
            border: 1px solid {OUTLINE} !important;
        }}
        
        /* === ALERTS === */
        [data-baseweb="notification"] {{
            background-color: {SURFACE_VARIANT} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* === LIVE PREVIEW === */
        .sidebar-preview {{
            background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%) !important;
            border-radius: {RADIUS_LARGE};
            padding: 1.25rem;
            margin: 1rem 0;
            box-shadow: {SHADOW_2};
        }}
        
        .preview-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.8) !important;
            text-transform: uppercase;
        }}
        
        .preview-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white !important;
        }}
        
        /* === SPINNER === */
        .stSpinner > div {{
            border-top-color: {PRIMARY} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_preview(static_res: Dict, sim_stats: Dict):
    """Мини-превью результатов в сайдбаре."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Быстрый просмотр")
    
    preview_html = f"""
    <div class="sidebar-preview">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div>
                <div class="preview-label">Скорость</div>
                <div class="preview-value">{static_res['speed_kmh']:.1f} км/ч</div>
            </div>
            <div>
                <div class="preview-label">Масса</div>
                <div class="preview-value">{static_res['total_mass']:.1f} кг</div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <div class="preview-label">Энергия</div>
                <div class="preview-value">{static_res['weapon_energy']/1000:.1f} кДж</div>
            </div>
            <div>
                <div class="preview-label">Ток</div>
                <div class="preview-value">{sim_stats.get('peak_current', 0):.0f} А</div>
            </div>
        </div>
    </div>
    """
    st.sidebar.markdown(preview_html, unsafe_allow_html=True)
    
    mass_percent = (static_res['total_mass'] / 110.0) * 100
    st.sidebar.markdown(f"**Использование массы:** {mass_percent:.1f}%")
    st.sidebar.progress(min(mass_percent / 100, 1.0))


def render_kpi_row(static_res: Dict, sim_stats: Dict, total_mass_limit: float):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Скорость (теор.)", f"{static_res['speed_kmh']:.1f} км/ч")
    with col2: st.metric("Энергия удара", f"{static_res['weapon_energy']/1000:.1f} кДж")
    with col3:
        delta_mass = total_mass_limit - static_res["total_mass"]
        st.metric("Масса", f"{static_res['total_mass']:.1f} кг", f"{delta_mass:+.1f} кг")
    with col4: st.metric("Пиковый ток", f"{sim_stats['peak_current']:.0f} А", sim_stats["wire_awg"])


def render_weight_pie(static_res: Dict, base_drive: float, base_elec: float, base_frame: float):
    mass_dict = {
        "Броня": static_res["armor_mass"],
        "Оружие": static_res["weapon_inertia"] * 10,
        "Ходовая": base_drive,
        "Электроника": base_elec,
        "Рама": base_frame,
    }
    df = pd.DataFrame({"Компонент": mass_dict.keys(), "Масса": mass_dict.values()})
    
    fig = px.pie(
        df, values="Масса", names="Компонент", title="Весовой бюджет", hole=0.45,
        color_discrete_sequence=[PRIMARY, SECONDARY, PRIMARY_LIGHT, SECONDARY_LIGHT, "#B0BEC5"]
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color=SURFACE_BG, width=2)))
    fig.update_layout(
        paper_bgcolor=SURFACE_BG, plot_bgcolor=SURFACE_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
        showlegend=True, legend=dict(orientation="h", y=-0.1)
    )
    st.plotly_chart(fig, use_container_width=True)


def _apply_theme(fig, title, xlabel, ylabel):
    """Применение светлой темы к графику."""
    fig.update_layout(
        paper_bgcolor=SURFACE_BG,
        plot_bgcolor=SURFACE_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=13),
        title=dict(text=title, font=dict(size=16, color=TEXT_PRIMARY)),
        xaxis=dict(
            title=dict(text=xlabel),
            gridcolor=OUTLINE,
            zerolinecolor=OUTLINE_VARIANT,
            linecolor=OUTLINE_VARIANT
        ),
        yaxis=dict(
            title=dict(text=ylabel),
            gridcolor=OUTLINE,
            zerolinecolor=OUTLINE_VARIANT,
            linecolor=OUTLINE_VARIANT
        ),
        hovermode="x unified",
        margin=dict(l=40, r=20, t=40, b=40)
    )


def render_drive_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sim["t"], y=df_sim["v_kmh"], name="Скорость",
        line=dict(color=PRIMARY, width=3), yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=df_sim["t"], y=df_sim["I_bat"], name="Ток",
        line=dict(color=WARNING, width=2, dash="dot"), yaxis="y2"
    ))
    
    _apply_theme(fig, "Разгон и нагрузка", "Время (с)", "Скорость (км/ч)")
    fig.update_layout(
        yaxis2=dict(
            title=dict(text="Ток (А)", font=dict(color=WARNING)),
            overlaying="y", side="right",
            gridcolor=OUTLINE, zerolinecolor=OUTLINE_VARIANT
        ),
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_thermal_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sim["t"], y=df_sim["T_drive"], name="Ход", line=dict(color=WARNING, width=3)))
    fig.add_trace(go.Scatter(x=df_sim["t"], y=df_sim["T_weapon"], name="Оружие", line=dict(color=ERROR, width=3)))
    fig.add_hline(y=100, line_dash="dash", line_color=ERROR, annotation_text="Критическая зона")
    
    _apply_theme(fig, "Тепловой режим", "Время (с)", "Температура (°C)")
    fig.update_layout(legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)"))
    st.plotly_chart(fig, use_container_width=True)


def render_parameter_scan_plots(df_scan: pd.DataFrame, param_name: str, param_unit: str):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scan["param_value"], y=df_scan["speed_kmh"],
        mode="lines+markers", line=dict(color=PRIMARY, width=3)
    ))
    _apply_theme(fig, f"Скорость от {param_name}", f"{param_name} ({param_unit})", "Скорость (км/ч)")
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    for col, key, title, color in [
        (col1, "total_mass", "Масса (кг)", SECONDARY),
        (col2, "peak_current", "Ток (А)", WARNING),
        (col3, "time_to_20", "Разгон (с)", SUCCESS)
    ]:
        with col:
            f = go.Figure()
            f.add_trace(go.Scatter(
                x=df_scan["param_value"], y=df_scan[key],
                mode="lines+markers", line=dict(color=color, width=2)
            ))
            _apply_theme(f, title, "", "")
            f.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(f, use_container_width=True)


def render_comparison_view(config_a: Dict, config_b: Dict, comparison: Dict):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### 🔵 {config_a['name']}")
        st.metric("Скорость", f"{config_a['speed_kmh']:.1f} км/ч")
        st.metric("Масса", f"{config_a['total_mass']:.1f} кг")
    with col_b:
        st.markdown(f"### 🟢 {config_b['name']}")
        st.metric("Скорость", f"{config_b['speed_kmh']:.1f} км/ч", f"{comparison['speed_kmh']['delta']:+.1f}")
        st.metric("Масса", f"{config_b['total_mass']:.1f} кг", f"{comparison['total_mass']['delta']:+.1f}")


def render_optimization_progress(history: list):
    if not history: return
    df = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df["score"], mode="lines+markers", line=dict(color=PRIMARY, width=2)))
    _apply_theme(fig, "Сходимость", "Итерация", "Целевая функция")
    st.plotly_chart(fig, use_container_width=True)
