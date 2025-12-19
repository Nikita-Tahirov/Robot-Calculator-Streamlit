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
        .stMetric {
            background-color: #1e2836;
            border: 1px solid #3a4552;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .stMetric label {
            color: #a8b2c1 !important;
            font-size: 0.9rem;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .stMetric [data-testid="stMetricDelta"] {
            color: #6dd4a8 !important;
        }
        
        h1, h2, h3, h4 {
            color: #fafafa;
        }
        
        /* Мини-превью в сайдбаре */
        .sidebar-preview {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d1b3d 100%);
            border: 2px solid #4a5f7f;
            border-radius: 12px;
            padding: 16px;
            margin: 12px 0;
        }
        
        .preview-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #00d4ff;
        }
        
        .preview-label {
            font-size: 0.75rem;
            color: #a8b2c1;
            text-transform: uppercase;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_preview(static_res: Dict, sim_stats: Dict):
    """Мини-превью результатов прямо в сайдбаре (Live Preview)."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Live Preview")
    
    # Используем HTML для красивого оформления
    preview_html = f"""
    <div class="sidebar-preview">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <div>
                <div class="preview-label">Скорость</div>
                <div class="preview-value">{static_res['speed_kmh']:.1f} км/ч</div>
            </div>
            <div>
                <div class="preview-label">Масса</div>
                <div class="preview-value">{static_res['total_mass']:.1f} кг</div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <div class="preview-label">Энергия</div>
                <div class="preview-value">{static_res['weapon_energy']/1000:.1f} кДж</div>
            </div>
            <div>
                <div class="preview-label">Ток пик</div>
                <div class="preview-value">{sim_stats.get('peak_current', 0):.0f} А</div>
            </div>
        </div>
    </div>
    """
    st.sidebar.markdown(preview_html, unsafe_allow_html=True)
    
    # Индикатор массы (прогресс-бар)
    mass_percent = (static_res['total_mass'] / 110.0) * 100
    if mass_percent > 100:
        st.sidebar.error(f"⚠️ Перевес: {static_res['total_mass'] - 110:.1f} кг")
    else:
        st.sidebar.progress(mass_percent / 100, text=f"Использовано: {mass_percent:.1f}%")


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


def render_weight_pie(static_res: Dict, base_drive: float,
                      base_elec: float, base_frame: float):
    mass_dict = {
        "Броня": static_res["armor_mass"],
        "Оружие (ротор)": static_res["weapon_inertia"] * 10,
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
        hole=0.4,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_drive_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["v_kmh"],
            name="Скорость (км/ч)",
            line=dict(color="cyan", width=3),
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["I_bat"],
            name="Ток АКБ (А)",
            line=dict(color="magenta", dash="dot"),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Разгон и нагрузка на батарею",
        xaxis_title="Время (с)",
        yaxis=dict(title="Скорость (км/ч)"),
        yaxis2=dict(
            title="Ток (А)", overlaying="y", side="right"
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_thermal_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_drive"],
            name="Двигатели хода",
            line=dict(color="orange", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_weapon"],
            name="Двигатели оружия",
            line=dict(color="red", width=3),
        )
    )
    fig.add_hline(y=100, line_dash="dash", line_color="red",
                  annotation_text="Критическая зона")
    fig.update_layout(
        title="Тепловой режим моторов",
        xaxis_title="Время (с)",
        yaxis_title="Температура (°C)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_parameter_scan_plots(df_scan: pd.DataFrame, param_name: str, param_unit: str):
    """Визуализация результатов параметрического сканирования."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scan["param_value"],
        y=df_scan["speed_kmh"],
        name="Скорость",
        line=dict(color="cyan", width=3),
        mode="lines+markers"
    ))
    
    fig.update_layout(
        title=f"Зависимость скорости от {param_name}",
        xaxis_title=f"{param_name} ({param_unit})",
        yaxis_title="Скорость (км/ч)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_scan["param_value"],
            y=df_scan["total_mass"],
            line=dict(color="orange", width=2),
            mode="lines+markers"
        ))
        fig2.update_layout(
            title="Масса",
            xaxis_title=f"{param_name}",
            yaxis_title="кг"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=df_scan["param_value"],
            y=df_scan["peak_current"],
            line=dict(color="red", width=2),
            mode="lines+markers"
        ))
        fig3.update_layout(
            title="Пиковый ток",
            xaxis_title=f"{param_name}",
            yaxis_title="А"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col3:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=df_scan["param_value"],
            y=df_scan["time_to_20"],
            line=dict(color="green", width=2),
            mode="lines+markers"
        ))
        fig4.update_layout(
            title="Время 0-20 км/ч",
            xaxis_title=f"{param_name}",
            yaxis_title="сек"
        )
        st.plotly_chart(fig4, use_container_width=True)


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
    """Визуализация прогресса оптимизации."""
    if not history:
        return
    
    df_hist = pd.DataFrame(history)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=df_hist["score"],
        mode="lines+markers",
        name="Objective Score",
        line=dict(color="cyan", width=2)
    ))
    
    fig.update_layout(
        title="Сходимость оптимизации",
        xaxis_title="Итерация",
        yaxis_title="Целевая функция (меньше = лучше)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
