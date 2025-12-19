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
        
        /* Типографика */
        h1, h2, h3, h4, h5, h6 {{
            color: {TEXT_PRIMARY};
            font-weight: 600;
            letter-spacing: -0.02em;
        }}
        
        h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }}
        h3 {{ font-size: 1.25rem; margin-top: 1.5rem; }}
        
        p, label, span {{ color: {TEXT_PRIMARY}; }}
        
        /* Метрики */
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
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {PRIMARY};
            font-size: 2rem;
            font-weight: 700;
        }}
        
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        [data-testid="stMetricDelta"][data-delta-color="normal"] {{ color: {SUCCESS}; }}
        [data-testid="stMetricDelta"][data-delta-color="inverse"] {{ color: {ERROR}; }}
        
        /* Кнопки */
        .stButton > button {{
            background: {PRIMARY};
            color: white;
            border: none;
            border-radius: {RADIUS_PILL};
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            box-shadow: {SHADOW_1};
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: {PRIMARY_DARK};
            box-shadow: {SHADOW_2};
            transform: translateY(-1px);
        }}
        
        /* Табы */
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
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {PRIMARY};
            border-bottom: 3px solid {PRIMARY};
            font-weight: 600;
        }}
        
        /* Инпуты */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div {{
            border: 1px solid {OUTLINE};
            border-radius: {RADIUS_SMALL};
            background: {SURFACE_BG};
            color: {TEXT_PRIMARY};
        }}
        
        /* Live Preview */
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
            margin-bottom: 0.25rem;
        }}
        
        .preview-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            line-height: 1.2;
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
    if mass_percent > 100:
        st.sidebar.error(f"⚠️ Перевес: {static_res['total_mass'] - 110:.1f} кг")
    else:
        st.sidebar.progress(min(mass_percent / 100, 1.0))


def render_kpi_row(static_res: Dict, sim_stats: Dict, total_mass_limit: float):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Скорость (теор.)", f"{static_res['speed_kmh']:.1f} км/ч")
    with col2: st.metric("Энергия удара", f"{static_res['weapon_energy']/1000:.1f} кДж")
    with col3:
        delta_mass = total_mass_limit - static_res["total_mass"]
        st.metric("Масса", f"{static_res['total_mass']:.1f} кг", f"{delta_mass:+.1f} кг",
                  delta_color="normal" if delta_mass >= 0 else "inverse")
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
    """Вспомогательная функция для применения темы к графикам."""
    fig.update_layout(
        paper_bgcolor=SURFACE_BG,
        plot_bgcolor=SURFACE_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_PRIMARY, size=13),
        title=dict(text=title, font=dict(size=16, color=TEXT_PRIMARY)),
        xaxis=dict(
            title=xlabel,
            gridcolor=OUTLINE,
            zerolinecolor=OUTLINE_VARIANT,
            linecolor=OUTLINE_VARIANT
        ),
        yaxis=dict(
            title=ylabel,
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
            title="Ток (А)", titlefont=dict(color=WARNING),
            overlaying="y", side="right"
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
    
    # Маленькие графики
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
        st.metric("Энергия", f"{config_a['weapon_energy_kj']:.1f} кДж")
    with col_b:
        st.markdown(f"### 🟢 {config_b['name']}")
        st.metric("Скорость", f"{config_b['speed_kmh']:.1f} км/ч",
                  f"{comparison['speed_kmh']['delta']:+.1f}")
        st.metric("Масса", f"{config_b['total_mass']:.1f} кг",
                  f"{comparison['total_mass']['delta']:+.1f}")
        st.metric("Энергия", f"{config_b['weapon_energy_kj']:.1f} кДж",
                  f"{comparison['weapon_energy_kj']['delta']:+.1f}")


def render_optimization_progress(history: list):
    if not history: return
    df = pd.DataFrame(history)
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df["score"], mode="lines+markers", line=dict(color=PRIMARY, width=2)))
    _apply_theme(fig, "Сходимость", "Итерация", "Целевая функция")
    st.plotly_chart(fig, use_container_width=True)
