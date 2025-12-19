# main.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import physics  # Наш модуль
import styles   # Наш модуль

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(
    page_title="1T Rex | Digital Twin",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ПРИМЕНЕНИЕ СТИЛЯ ---
styles.apply_design_system()

# --- САЙДБАР (Ввод данных) ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/robot.png", width=64) # Можно заменить на лого
    st.title("КОНФИГУРАТОР")
    
    st.markdown("### ⚡ Энергосистема")
    voltage_s = st.selectbox("Батарея (S)", [4, 6, 8, 12], index=3)
    voltage = voltage_s * 3.7
    batt_res = st.slider("Сопротивление батареи (мОм)", 10, 200, 40)
    
    st.markdown("### ⚙️ Привод")
    kv = st.number_input("KV мотора", value=180, step=10)
    gear = st.number_input("Редукция (X:1)", value=12.0, step=0.5)
    wheel = st.number_input("Диаметр колеса (мм)", value=120, step=10)
    
    st.markdown("### ⚖️ Масса")
    mass = st.number_input("Полная масса (кг)", value=13.6, step=0.1)

# --- ИНИЦИАЛИЗАЦИЯ ФИЗИКИ ---
bot = physics.RobotPhysics(mass, voltage, kv, gear, wheel, batt_res)
specs = bot.calculate_static_specs()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
# Шапка
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style='margin-bottom: 0;'>1T REX <span style='font-size: 0.5em; opacity: 0.7;'>DIGITAL TWIN</span></h1>
            <p style='color: var(--text-muted);'>Инженерная симуляция боевой платформы</p>
        </div>
        <div style='text-align: right;'>
             <span style='background: #280046; padding: 5px 15px; border-radius: 15px; font-size: 0.8em; border: 1px solid #3be4ff;'>v2.4.0 STABLE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Метрики (Top Level)
col1, col2, col3, col4 = st.columns(4)
col1.metric("МАКС. СКОРОСТЬ", f"{specs['speed_kmh']:.1f} км/ч")
col2.metric("СИЛА ТЯГИ", f"{specs['force_n']:.0f} Н")
col3.metric("КОЭФФ. ТЯГИ", f"{specs['push_ratio']:.2f} G")
col4.metric("ПИТАНИЕ", f"{voltage:.1f} В")

# --- ВКЛАДКИ АНАЛИЗА ---
tab1, tab2, tab3 = st.tabs(["🚀 ДИНАМИКА РАЗГОНА", "💥 УДАР И G-FORCE", "📋 ПАСПОРТ"])

# TAB 1: СИМУЛЯЦИЯ
with tab1:
    styles.card_start()
    st.markdown("### Time-Domain Simulation (0-3 сек)")
    
    df_sim = bot.run_time_domain_simulation()
    
    # График Plotly
    fig = go.Figure()
    
    # Линия скорости
    fig.add_trace(go.Scatter(
        x=df_sim['time'], y=df_sim['speed_kmh'],
        name='Скорость (км/ч)',
        line=dict(color='#3be4ff', width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 228, 255, 0.1)'
    ))
    
    # Линия тока (на второй оси)
    fig.add_trace(go.Scatter(
        x=df_sim['time'], y=df_sim['current'],
        name='Ток (А)',
        line=dict(color='#ff2eaa', width=2, dash='dot'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(title="Скорость (км/ч)", gridcolor='rgba(255,255,255,0.1)'),
        yaxis2=dict(title="Ток (А)", overlaying='y', side='right', showgrid=False),
        xaxis=dict(title="Время (сек)", gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(orientation="h", y=1.1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Выводы симуляции
    t_to_20 = df_sim[df_sim['speed_kmh'] >= 20]['time'].min()
    if pd.isna(t_to_20): t_to_20 = "> 3.0"
    
    c1, c2 = st.columns(2)
    c1.info(f"⏱️ Разгон 0-20 км/ч: **{t_to_20} сек**")
    c2.warning(f"🔋 Пиковый ток старта: **{df_sim['current'].max():.1f} А**")
    
    styles.card_end()

# TAB 2: УДАР
with tab2:
    col_impact_l, col_impact_r = st.columns([1, 2])
    
    with col_impact_l:
        styles.card_start()
        st.markdown("### 📐 Условия удара")
        imp_speed = st.slider("Скорость удара (км/ч)", 5, 50, 25)
        deform = st.slider("Деформация защиты (мм)", 1, 100, 15, help="Насколько сомнется демпфер при ударе")
        
        impact_data = bot.impact_analysis(imp_speed, deform)
        styles.card_end()
        
    with col_impact_r:
        styles.card_start()
        g = impact_data['g_force']
        
        # Цветовая кодировка опасности
        color = "#7ee8a1" # Green
        status = "БЕЗОПАСНО"
        if g > 20: 
            color = "#ffe45e"
            status = "ВНИМАНИЕ"
        if g > 50: 
            color = "#ff7b7b"
            status = "КРИТИЧЕСКИ"
            
        st.markdown(f"""
            <div style='text-align: center;'>
                <h3 style='color: {color}; font-size: 3em; margin: 0;'>{g:.1f} G</h3>
                <p style='letter-spacing: 0.2em; color: {color}; opacity: 0.8;'>ПЕРЕГРУЗКА ЭЛЕКТРОНИКИ ({status})</p>
                <hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0;'>
                <p>Энергия удара: <b>{impact_data['energy_joules']:.1f} Дж</b></p>
            </div>
        """, unsafe_allow_html=True)
        styles.card_end()

# TAB 3: ПАСПОРТ
with tab3:
    st.markdown("### 📄 Технический паспорт")
    code = f"""
    МОДЕЛЬ: 1T REX CONFIGURATION
    ----------------------------
    Масса: {mass} кг
    Напряжение: {voltage:.1f} В ({voltage_s}S)
    Мотор: KV {kv}
    Макс. скорость: {specs['speed_kmh']:.1f} км/ч
    Тяговооруженность: {specs['push_ratio']:.2f}
    """
    st.code(code, language="yaml")
    st.download_button("Скачать конфигурацию", code, "robot_config.txt")

# Футер
st.markdown("<br><br><div style='text-align:center; color:#555; font-size:0.8em;'>POWERED BY STREAMLIT & PHYSICS ENGINE</div>", unsafe_allow_html=True)
