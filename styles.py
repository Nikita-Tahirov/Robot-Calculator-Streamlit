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
        .main { background-color: #0c0f13; }
        .stMetric { background-color: #151922; border-radius: 8px; padding: 6px; }
        h1, h2, h3, h4 { color: #fafafa; }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
        "Оружие (ротор)": static_res["weapon_inertia"],  # условно
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
