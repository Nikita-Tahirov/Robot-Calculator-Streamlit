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
        /* --- ШРИФТЫ --- */
        @import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@300;400;600;700&family=Raleway:wght@300;400;500;600&display=swap');

        :root {
            /* Цветовая палитра */
            --bg-color: #05020a;
            --text-main: #ffffff;
            --text-secondary: #c0bdd0;
            
            --accent-primary: #d50085; 
            --accent-secondary: #0099ff; 
            --accent-gradient: linear-gradient(270deg, var(--accent-primary), var(--accent-secondary));
            
            /* Эффекты стекла */
            --surface-bg: rgba(20, 15, 35, 0.4);
            --surface-border: 1px solid rgba(255, 255, 255, 0.1);
            --surface-blur: blur(12px);
            --surface-radius: 16px;
            
            --font-head: 'Unbounded', sans-serif;
            --font-body: 'Raleway', sans-serif;
        }

        /* --- ГЛОБАЛЬНЫЙ ФОН --- */
        .stApp {
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #05020a 60%);
            background-attachment: fixed;
            font-family: var(--font-body);
            color: var(--text-main);
        }

        /* --- ЗАГОЛОВКИ --- */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-head) !important;
            color: var(--text-main) !important;
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        h1 {
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(213, 0, 133, 0.3);
        }

        /* --- КАРТОЧКИ И КОНТЕЙНЕРЫ (СТЕКЛО) --- */
        .stMetric, .sidebar-preview, div[data-testid="stExpander"], div.stDataFrame {
            background: var(--surface-bg) !important;
            backdrop-filter: var(--surface-blur);
            -webkit-backdrop-filter: var(--surface-blur);
            border: var(--surface-border);
            border-radius: var(--surface-radius);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        
        /* Эффект ховера для метрик */
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 30px rgba(0, 153, 255, 0.15);
        }

        /* --- МЕТРИКИ --- */
        .stMetric label {
            font-family: var(--font-body);
            color: var(--text-secondary) !important;
            font-size: 0.85rem !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 500;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-family: var(--font-head);
            color: var(--text-main) !important;
            font-size: 2rem !important;
            font-weight: 700;
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
        }
        
        .stMetric [data-testid="stMetricDelta"] {
            font-family: var(--font-head);
            font-size: 0.9rem;
        }

        /* --- САЙДБАР --- */
        section[data-testid="stSidebar"] {
            background-color: rgba(5, 2, 10, 0.85);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Мини-превью в сайдбаре (кастомный класс) */
        .sidebar-preview {
            background: linear-gradient(145deg, rgba(30, 20, 60, 0.6), rgba(10, 5, 20, 0.8)) !important;
            padding: 20px !important;
            margin: 15px 0 !important;
            border: 1px solid rgba(0, 153, 255, 0.2) !important;
        }
        
        .preview-value {
            font-family: var(--font-head);
            font-size: 1.4rem;
            font-weight: 700;
            color: #00d4ff;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.4);
        }
        
        .preview-label {
            font-family: var(--font-body);
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 4px;
        }

        /* --- КНОПКИ --- */
        .stButton button {
            background: transparent;
            border: 1px solid var(--accent-secondary);
            color: var(--accent-secondary);
            font-family: var(--font-head);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }
        
        .stButton button:hover {
            background: var(--accent-secondary);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 153, 255, 0.5);
            border-color: var(--accent-secondary);
        }
        
        /* Основная кнопка (Primary) - делаем её градиентной */
        div.stButton button:active {
             transform: scale(0.98);
        }

        /* --- ТАБЫ --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255,255,255,0.03);
            border-radius: 8px;
            border: 1px solid transparent;
            color: var(--text-secondary);
            font-family: var(--font-body);
            padding: 8px 16px;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255,255,255,0.08);
            color: var(--text-main);
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(213, 0, 133, 0.15) !important;
            border: 1px solid var(--accent-primary) !important;
            color: #fff !important;
            font-weight: 600;
        }
        
        /* --- СЛАЙДЕРЫ И ИНПУТЫ --- */
        div[data-baseweb="slider"] div[role="slider"] {
            background-color: var(--accent-secondary) !important;
            box-shadow: 0 0 10px var(--accent-secondary);
        }
        
        div[data-baseweb="select"] > div {
            background-color: rgba(255,255,255,0.05);
            border-color: rgba(255,255,255,0.1);
            color: white;
        }
        
        .stTextInput input, .stNumberInput input {
            background-color: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            color: white;
            border-radius: 8px;
        }

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
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <div class="preview-label">Скорость</div>
                <div class="preview-value">{static_res['speed_kmh']:.1f} <span style="font-size:0.8rem">км/ч</span></div>
            </div>
            <div style="text-align: right;">
                <div class="preview-label">Масса</div>
                <div class="preview-value" style="color: #d50085;">{static_res['total_mass']:.1f} <span style="font-size:0.8rem">кг</span></div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <div>
                <div class="preview-label">Энергия</div>
                <div class="preview-value" style="color: #ffffff;">{static_res['weapon_energy']/1000:.1f} <span style="font-size:0.8rem">кДж</span></div>
            </div>
            <div style="text-align: right;">
                <div class="preview-label">Ток пик</div>
                <div class="preview-value" style="color: #ffffff;">{sim_stats.get('peak_current', 0):.0f} <span style="font-size:0.8rem">А</span></div>
            </div>
        </div>
    </div>
    """
    st.sidebar.markdown(preview_html, unsafe_allow_html=True)
    
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


def _update_fig_layout_dark(fig, title_text):
    """Вспомогательная функция для стилизации графиков под Cyberpunk."""
    fig.update_layout(
        title=dict(text=title_text, font=dict(family="Unbounded", size=18, color="white")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Raleway", color="#c0bdd0"),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)', 
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)', 
            zerolinecolor='rgba(255,255,255,0.1)'
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig


def render_weight_pie(static_res: Dict, base_drive: float,
                      base_elec: float, base_frame: float):
    mass_dict = {
        "Броня": static_res["armor_mass"],
        "Оружие (ротор)": static_res["weapon_inertia"] * 10, # масштаб
        "Ходовая": base_drive,
        "Электроника": base_elec,
        "Рама": base_frame,
    }
    df = pd.DataFrame(
        {"Компонент": mass_dict.keys(), "Масса": mass_dict.values()}
    )
    
    # Кибер-цвета для пайчарта
    colors = ['#2d1b4e', '#d50085', '#0099ff', '#00d4ff', '#5200cc']
    
    fig = px.pie(
        df,
        values="Масса",
        names="Компонент",
        hole=0.5,
        color_discrete_sequence=colors
    )
    
    fig.update_layout(
        title=dict(text="Весовой бюджет", font=dict(family="Unbounded", size=18, color="white")),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Raleway", color="#c0bdd0"),
        showlegend=True
    )
    # Добавляем текст в центр бублика
    fig.add_annotation(text=f"{static_res['total_mass']:.1f} кг", x=0.5, y=0.5, font_size=20, showarrow=False, font_color="white", font_family="Unbounded")
    
    st.plotly_chart(fig, use_container_width=True)


def render_drive_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    # Неоновое свечение через тень реализуется сложно в plotly, используем яркие цвета
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["v_kmh"],
            name="Скорость",
            line=dict(color="#00d4ff", width=3), # Cyan
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["I_bat"],
            name="Ток АКБ",
            line=dict(color="#d50085", width=2, dash="dot"), # Magenta
            yaxis="y2",
        )
    )
    
    fig = _update_fig_layout_dark(fig, "Разгон и нагрузка на батарею")
    fig.update_layout(
        yaxis=dict(title="Скорость (км/ч)", title_font=dict(color="#00d4ff")),
        yaxis2=dict(title="Ток (А)", overlaying="y", side="right", title_font=dict(color="#d50085"))
    )
    st.plotly_chart(fig, use_container_width=True)


def render_thermal_plot(df_sim: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_drive"],
            name="Двигатели хода",
            line=dict(color="#ff9900", width=3), # Orange
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sim["t"],
            y=df_sim["T_weapon"],
            name="Двигатели оружия",
            line=dict(color="#ff3333", width=3), # Red
        )
    )
    fig.add_hline(y=100, line_dash="dash", line_color="red",
                  annotation_text="Критическая зона")
    
    fig = _update_fig_layout_dark(fig, "Тепловой режим моторов")
    fig.update_layout(yaxis_title="Температура (°C)")
    
    st.plotly_chart(fig, use_container_width=True)


def render_parameter_scan_plots(df_scan: pd.DataFrame, param_name: str, param_unit: str):
    """Визуализация результатов параметрического сканирования."""
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_scan["param_value"],
        y=df_scan["speed_kmh"],
        name="Скорость",
        line=dict(color="#00d4ff", width=3),
        mode="lines+markers",
        marker=dict(size=8, color="#000", line=dict(width=2, color="#00d4ff"))
    ))
    
    fig = _update_fig_layout_dark(fig, f"Зависимость скорости от {param_name}")
    fig.update_layout(xaxis_title=f"{param_name} ({param_unit})", yaxis_title="Скорость (км/ч)")
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    def _mini_plot(x, y, title, color):
        f = go.Figure()
        f.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=2), mode="lines"))
        f.update_layout(
            title=dict(text=title, font=dict(size=14, color="white")),
            paper_bgcolor='rgba(255,255,255,0.03)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Raleway", color="#aaa", size=10),
            margin=dict(l=10, r=10, t=40, b=10),
            height=200
        )
        return f

    with col1:
        st.plotly_chart(_mini_plot(df_scan["param_value"], df_scan["total_mass"], "Масса (кг)", "#ff9900"), use_container_width=True)
    with col2:
        st.plotly_chart(_mini_plot(df_scan["param_value"], df_scan["peak_current"], "Пиковый ток (А)", "#ff3333"), use_container_width=True)
    with col3:
        st.plotly_chart(_mini_plot(df_scan["param_value"], df_scan["time_to_20"], "Разгон 0-20 (сек)", "#00ff99"), use_container_width=True)


def render_comparison_view(config_a: Dict, config_b: Dict, comparison: Dict):
    """Side-by-side сравнение двух конфигураций."""
    
    col_a, col_b = st.columns(2)
    
    def _render_card(config, title, color_accent):
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.03); 
                border: 1px solid {color_accent}; 
                border-radius: 12px; 
                padding: 20px; 
                margin-bottom: 20px;">
                <h3 style="margin-top:0; color:{color_accent}">{title}</h3>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.metric("Скорость", f"{config['speed_kmh']:.1f} км/ч")
        st.metric("Масса", f"{config['total_mass']:.1f} кг")
        st.metric("Энергия удара", f"{config['weapon_energy_kj']:.1f} кДж")
        st.metric("Пиковый ток", f"{config['peak_current']:.0f} А")
        st.metric("Перегрузка", f"{config['g_force_self']:.1f} G")

    with col_a:
        st.markdown(f"<h3 style='color:#0099ff'>🔵 {config_a['name']}</h3>", unsafe_allow_html=True)
        st.metric("Скорость", f"{config_a['speed_kmh']:.1f} км/ч")
        st.metric("Масса", f"{config_a['total_mass']:.1f} кг")
        
    with col_b:
        st.markdown(f"<h3 style='color:#00d4ff'>🟢 {config_b['name']}</h3>", unsafe_allow_html=True)
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
        line=dict(color="#00ff99", width=2),
        marker=dict(color="#000", line=dict(width=1, color="#00ff99"))
    ))
    
    fig = _update_fig_layout_dark(fig, "Сходимость оптимизации")
    fig.update_layout(yaxis_title="Целевая функция (меньше = лучше)")
    st.plotly_chart(fig, use_container_width=True)
