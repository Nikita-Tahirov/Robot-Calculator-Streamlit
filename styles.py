import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict
from theme_config import *


def setup_page():
    """Настройка страницы с светлой темой."""
    st.set_page_config(
        page_title="Цифровой двойник: 1T Rex",
        page_icon="🦖",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_css():
    """Глобальные стили Material Design 3 (светлая тема)."""
    st.markdown(
        f"""
        <style>
        /* === ОБЩИЕ СТИЛИ === */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: {FONT_FAMILY};
        }}
        
        .main {{
            background-color: {SURFACE_BG};
        }}
        
        /* Сайдбар */
        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: 1px solid {OUTLINE};
        }}
        
        section[data-testid="stSidebar"] > div {{
            padding-top: 2rem;
        }}
        
        /* === ТИПОГРАФИКА === */
        h1, h2, h3, h4, h5, h6 {{
            color: {TEXT_PRIMARY};
            font-weight: 600;
            letter-spacing: -0.02em;
        }}
        
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        h2 {{
            font-size: 1.5rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        
        h3 {{
            font-size: 1.25rem;
            margin-top: 1.5rem;
        }}
        
        p, label, span {{
            color: {TEXT_PRIMARY};
        }}
        
        /* === МЕТРИКИ (КАРТОЧКИ) === */
        [data-testid="stMetric"] {{
            background: {SURFACE_VARIANT};
            border: 1px solid {OUTLINE};
            border-radius: {RADIUS_MEDIUM};
            padding: 1.25rem;
            box-shadow: {SHADOW_1};
            transition: all 0.2s ease;
        }}
        
        [data-testid="stMetric"]:hover {{
            box-shadow: {SHADOW_2};
            transform: translateY(-2px);
        }}
        
        [data-testid="stMetric"] label {{
            color: {TEXT_SECONDARY};
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: none;
            letter-spacing: 0;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {PRIMARY};
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        /* Цвета дельт */
        [data-testid="stMetricDelta"][data-delta-color="normal"] {{
            color: {SUCCESS};
        }}
        
        [data-testid="stMetricDelta"][data-delta-color="inverse"] {{
            color: {ERROR};
        }}
        
        /* === КНОПКИ === */
        .stButton > button {{
            background: {PRIMARY};
            color: white;
            border: none;
            border-radius: {RADIUS_PILL};
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            font-size: 0.9375rem;
            box-shadow: {SHADOW_1};
            transition: all 0.2s ease;
            text-transform: none;
        }}
        
        .stButton > button:hover {{
            background: {PRIMARY_DARK};
            box-shadow: {SHADOW_2};
            transform: translateY(-1px);
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* Вторичные кнопки (через custom class) */
        .stButton.secondary > button {{
            background: transparent;
            color: {PRIMARY};
            border: 2px solid {PRIMARY};
            box-shadow: none;
        }}
        
        .stButton.secondary > button:hover {{
            background: rgba(0, 97, 164, 0.08);
        }}
        
        /* === ТАБЫ === */
        .stTabs {{
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            border-bottom: 2px solid {OUTLINE};
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border: none;
            color: {TEXT_SECONDARY};
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            border-radius: {RADIUS_SMALL} {RADIUS_SMALL} 0 0;
            transition: all 0.2s ease;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(0, 97, 164, 0.04);
            color: {PRIMARY};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: transparent;
            color: {PRIMARY};
            border-bottom: 3px solid {PRIMARY};
            font-weight: 600;
        }}
        
        /* === ИНПУТЫ === */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {{
            border: 1px solid {OUTLINE};
            border-radius: {RADIUS_SMALL};
            background: {SURFACE_BG};
            color: {TEXT_PRIMARY};
            padding: 0.625rem 0.875rem;
            transition: all 0.2s ease;
        }}
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {{
            border-color: {PRIMARY};
            box-shadow: 0 0 0 3px rgba(0, 97, 164, 0.1);
            outline: none;
        }}
        
        /* === СЛАЙДЕРЫ === */
        .stSlider > div > div > div > div {{
            background: {OUTLINE};
        }}
        
        .stSlider > div > div > div > div > div {{
            background: {PRIMARY};
        }}
        
        .stSlider > div > div > div > div > div > div {{
            background: white;
            border: 3px solid {PRIMARY};
            box-shadow: {SHADOW_1};
        }}
        
        /* === CHECKBOX === */
        .stCheckbox {{
            color: {TEXT_PRIMARY};
        }}
        
        .stCheckbox > label > div {{
            background: {SURFACE_BG};
            border: 2px solid {OUTLINE};
            border-radius: 4px;
        }}
        
        .stCheckbox > label > div[data-checked="true"] {{
            background: {PRIMARY};
            border-color: {PRIMARY};
        }}
        
        /* === ПРОГРЕСС БАР === */
        .stProgress > div > div > div > div {{
            background: {PRIMARY};
            border-radius: {RADIUS_PILL};
        }}
        
        /* === АЛЕРТЫ === */
        .stAlert {{
            border-radius: {RADIUS_MEDIUM};
            border-left: 4px solid;
            padding: 1rem;
        }}
        
        [data-baseweb="notification"][kind="info"] {{
            background: rgba(0, 97, 164, 0.08);
            border-left-color: {PRIMARY};
        }}
        
        [data-baseweb="notification"][kind="success"] {{
            background: rgba(46, 125, 50, 0.08);
            border-left-color: {SUCCESS};
        }}
        
        [data-baseweb="notification"][kind="warning"] {{
            background: rgba(245, 124, 0, 0.08);
            border-left-color: {WARNING};
        }}
        
        [data-baseweb="notification"][kind="error"] {{
            background: rgba(186, 26, 26, 0.08);
            border-left-color: {ERROR};
        }}
        
        /* === КОНТЕЙНЕРЫ С РАМКОЙ === */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {{
            background: {SURFACE_VARIANT};
            border: 1px solid {OUTLINE};
            border-radius: {RADIUS_MEDIUM};
            padding: 1.5rem;
        }}
        
        /* === LIVE PREVIEW (САЙДБАР) === */
        .sidebar-preview {{
            background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
            border-radius: {RADIUS_LARGE};
            padding: 1.25rem;
            margin: 1rem 0;
            box-shadow: {SHADOW_2};
        }}
        
        .preview-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.8);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }}
        
        .preview-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            line-height: 1.2;
        }}
        
        /* === СПИННЕР === */
        .stSpinner > div {{
            border-top-color: {PRIMARY};
        }}
        
        /* === РАЗДЕЛИТЕЛИ === */
        hr {{
            border: none;
            border-top: 1px solid {OUTLINE};
            margin: 2rem 0;
        }}
        
        /* === EXPANDER === */
        .streamlit-expanderHeader {{
            background: {SURFACE_VARIANT};
            border: 1px solid {OUTLINE};
            border-radius: {RADIUS_SMALL};
            color: {TEXT_PRIMARY};
            font-weight: 500;
        }}
        
        .streamlit-expanderHeader:hover {{
            background: rgba(0, 97, 164, 0.04);
        }}
        
        /* === DATAFRAME === */
        .dataframe {{
            border: 1px solid {OUTLINE};
            border-radius: {RADIUS_SMALL};
        }}
        
        .dataframe thead th {{
            background: {SURFACE_VARIANT};
            color: {TEXT_PRIMARY};
            font-weight: 600;
            border-bottom: 2px solid {OUTLINE};
        }}
        
        .dataframe tbody tr:hover {{
            background: rgba(0, 97, 164, 0.04);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_preview(static_res: Dict, sim_stats: Dict):
    """Мини-превью результатов в сайдбаре (Material Design)."""
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
    
    # Прогресс-бар массы
    mass_percent = (static_res['total_mass'] / 110.0) * 100
    st.sidebar.markdown(f"**Использование массы:** {mass_percent:.1f}%")
    if mass_percent > 100:
        st.sidebar.error(f"⚠️ Перевес: {static_res['total_mass'] - 110:.1f} кг")
    else:
        st.sidebar.progress(min(mass_percent / 100, 1.0))


def render_kpi_row(static_res: Dict, sim_stats: Dict, total_mass_limit: float):
    """Строка ключевых метрик."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Скорость (теор.)", f"{static_res['speed_kmh']:.1f} км/ч")
    
    with col2:
        st.metric("Энергия удара", f"{static_res['weapon_energy']/1000:.1f} кДж")
    
    with col3:
        delta_mass = total_mass_limit - static_res["total_mass"]
        st.metric(
            "Масса",
            f"{static_res['total_mass']:.1f} кг",
            f"{delta_mass:+.1f} кг",
            delta_color="normal" if delta_mass >= 0 else "inverse",
        )
    
    with col4:
        st.metric("Пиковый ток", f"{sim_stats['peak_current']:.0f} А", sim_stats["wire_awg"])


def render_weight_pie(static_res: Dict, base_drive: float,
                      base_elec: float, base_frame: float):
    """Круговая диаграмма распределения массы."""
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
    
    fig = px.pie(
        df,
        values="Масса",
        names="Компонент",
        title="Весовой бюджет",
        hole=0.45,
        color_discrete_sequence=[PRIMARY, SECONDARY, PRIMARY_LIGHT, SECONDARY_LIGHT, "#B0BEC5"]
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=13,
        marker=dict(line=dict(color=SURFACE_BG, width=2))
    )
    
    fig.update_layout(
        paper_bgcolor=SURFACE_BG,
        plot_bgcolor=SURFACE_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY),
        title_font_size=16,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def get_plotly_theme():
    """Общая тема для всех графиков Plotly."""
    return dict(
        paper_bgcolor=SURFACE_BG,
        plot_bgcolor=SURFACE_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=13),
        xaxis=dict(
            gridcolor=OUTLINE,
            zerolinecolor=OUTLINE_VARIANT,
            linecolor=OUTLINE_VARIANT
        ),
        yaxis=dict(
            gridcolor=OUTLINE,
            zerolinecolor=OUTLINE_VARIANT,
            linecolor=OUTLINE_VARIANT
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=SURFACE_VARIANT,
            font_size=13,
            font_family=FONT_FAMILY
        )
    )


def render_drive_plot(df_sim: pd.DataFrame):
    """График разгона и нагрузки."""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["v_kmh"],
            name="Скорость (км/ч)",
            line=dict(color=PRIMARY, width=3),
            yaxis="y1",
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["I_bat"],
            name="Ток АКБ (А)",
            line=dict(color=WARNING, width=2, dash="dot"),
            yaxis="y2",
        )
    )
    
    fig.update_layout(
        **get_plotly_theme(),
        title="Разгон и нагрузка на батарею",
        xaxis_title="Время (с)",
        yaxis=dict(title="Скорость (км/ч)", titlefont=dict(color=PRIMARY)),
        yaxis2=dict(
            title="Ток (А)",
            titlefont=dict(color=WARNING),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_thermal_plot(df_sim: pd.DataFrame):
    """График тепловых режимов."""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_drive"],
            name="Двигатели хода",
            line=dict(color=WARNING, width=3),
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_weapon"],
            name="Двигатели оружия",
            line=dict(color=ERROR, width=3),
        )
    )
    
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color=ERROR,
        annotation_text="Критическая зона",
        annotation_position="right"
    )
    
    fig.update_layout(
        **get_plotly_theme(),
        title="Тепловой режим моторов",
        xaxis_title="Время (с)",
        yaxis_title="Температура (°C)",
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_parameter_scan_plots(df_scan: pd.DataFrame, param_name: str, param_unit: str):
    """Графики параметрического сканирования."""
    
    # Главный график
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scan["param_value"],
        y=df_scan["speed_kmh"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=8, color=PRIMARY_LIGHT, line=dict(color=PRIMARY, width=2))
    ))
    
    fig.update_layout(
        **get_plotly_theme(),
        title=f"Зависимость скорости от {param_name.lower()}",
        xaxis_title=f"{param_name} ({param_unit})",
        yaxis_title="Скорость (км/ч)"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Три дополнительных графика
    col1, col2, col3 = st.columns(3)
    
    metrics = [
        ("total_mass", "Масса", "кг", SECONDARY, col1),
        ("peak_current", "Пиковый ток", "А", WARNING, col2),
        ("time_to_20", "Время 0-20 км/ч", "сек", SUCCESS, col3)
    ]
    
    for metric_key, title, unit, color, column in metrics:
        with column:
            fig_small = go.Figure()
            fig_small.add_trace(go.Scatter(
                x=df_scan["param_value"],
                y=df_scan[metric_key],
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
            fig_small.update_layout(
                **get_plotly_theme(),
                title=title,
                xaxis_title="",
                yaxis_title=unit,
                height=300,
                margin=dict(l=40, r=20, t=40, b=40)
            )
            st.plotly_chart(fig_small, use_container_width=True)


def render_comparison_view(config_a: Dict, config_b: Dict, comparison: Dict):
    """Side-by-side сравнение конфигураций."""
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
            f"{comparison['speed_kmh']['delta']:+.1f} ({comparison['speed_kmh']['delta_pct']:+.1f}%)"
        )
        st.metric(
            "Масса",
            f"{config_b['total_mass']:.1f} кг",
            f"{comparison['total_mass']['delta']:+.1f} ({comparison['total_mass']['delta_pct']:+.1f}%)"
        )
        st.metric(
            "Энергия удара",
            f"{config_b['weapon_energy_kj']:.1f} кДж",
            f"{comparison['weapon_energy_kj']['delta']:+.1f} ({comparison['weapon_energy_kj']['delta_pct']:+.1f}%)"
        )
        st.metric(
            "Пиковый ток",
            f"{config_b['peak_current']:.0f} А",
            f"{comparison['peak_current']['delta']:+.0f} ({comparison['peak_current']['delta_pct']:+.1f}%)"
        )
        st.metric(
            "Перегрузка",
            f"{config_b['g_force_self']:.1f} G",
            f"{comparison['g_force_self']['delta']:+.1f} ({comparison['g_force_self']['delta_pct']:+.1f}%)"
        )


def render_optimization_progress(history: list):
    """График прогресса оптимизации."""
    if not history:
        return
    
    df_hist = pd.DataFrame(history)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=df_hist["score"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=2),
        marker=dict(size=6, color=PRIMARY_LIGHT, line=dict(color=PRIMARY, width=1))
    ))
    
    fig.update_layout(
        **get_plotly_theme(),
        title="Сходимость оптимизации",
        xaxis_title="Итерация",
        yaxis_title="Целевая функция (меньше = лучше)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
