import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# Конфигурация страницы
st.set_page_config(
    page_title="Калькулятор Боевого Робота",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили и CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-unit {
        font-size: 14px;
        opacity: 0.9;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #667eea;
        margin-top: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #667eea;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        color: #856404;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        color: #004085;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок приложения
st.markdown("# 🤖 Калькулятор Параметров Боевого Робота")
st.markdown("Расчет основных характеристик боевого робота на основе параметров мотора и конструкции")

# ========== БОКОВАЯ ПАНЕЛЬ ==========
st.sidebar.markdown("## ⚙️ Параметры Конфигурации")

# Стандартные значения (110 кг, 12S, 25 км/ч)
default_voltage = 44.4  # 12S LiPo = 12 × 3.7V = 44.4V
default_speed = 25  # км/ч
default_mass_total = 110  # кг

# Входные параметры
st.sidebar.markdown("### Электропитание")
voltage_s = st.sidebar.number_input(
    "Напряжение (S)",
    min_value=1,
    max_value=30,
    value=12,
    help="Количество ячеек LiPo (каждая ячейка 3.7V)"
)
voltage = voltage_s * 3.7  # Преобразование S в вольты

st.sidebar.markdown("### Параметры Мотора")
kv_motor = st.sidebar.number_input(
    "KV мотора (RPM/V)",
    min_value=10,
    max_value=5000,
    value=50,
    help="Обороты мотора на один вольт без нагрузки"
)

transmission_ratio = st.sidebar.number_input(
    "Передаточное число редуктора",
    min_value=1,
    max_value=100,
    value=20,
    help="Отношение входных оборотов к выходным"
)

st.sidebar.markdown("### Конструкция")
wheel_diameter = st.sidebar.slider(
    "Диаметр колеса (см)",
    min_value=5,
    max_value=50,
    value=20,
    help="Диаметр колеса в сантиметрах"
)

armor_mass = st.sidebar.number_input(
    "Масса брони (кг)",
    min_value=0.0,
    max_value=100.0,
    value=50.0,
    step=1.0
)

weapon_mass = st.sidebar.number_input(
    "Масса оружия (кг)",
    min_value=0.0,
    max_value=100.0,
    value=30.0,
    step=1.0
)

# Рассчитанная общая масса
mass_total = armor_mass + weapon_mass

st.sidebar.markdown(f"**Общая масса:** {mass_total:.1f} кг")

# Эффективность мотора
motor_efficiency = st.sidebar.slider(
    "КПД мотора (%)",
    min_value=50,
    max_value=95,
    value=85,
    help="Коэффициент полезного действия мотора"
) / 100

# Батарея
st.sidebar.markdown("### Батарея")
battery_capacity = st.sidebar.number_input(
    "Емкость батареи (mAh)",
    min_value=100,
    max_value=100000,
    value=10000,
    help="Емкость аккумулятора в миллиампер-часах"
)

battery_cells = st.sidebar.number_input(
    "Количество параллельных батарей",
    min_value=1,
    max_value=10,
    value=2,
    help="Количество параллельно соединенных батарей"
)

# ========== РАСЧЕТЫ ==========

# Основные расчеты
wheel_radius_m = (wheel_diameter / 100) / 2  # Радиус в метрах
wheel_circumference = np.pi * wheel_diameter / 100  # Длина окружности в метрах

# Максимальная частота вращения вала мотора (в об/мин)
max_rpm_motor = kv_motor * voltage

# Частота вращения колеса (об/мин)
rpm_wheel = max_rpm_motor / transmission_ratio

# Линейная скорость (м/с)
linear_speed_ms = (rpm_wheel / 60) * wheel_circumference

# Скорость в км/ч
speed_kmh = linear_speed_ms * 3.6

# Крутящий момент на валу мотора (приблизительно)
# T = P / ω, но для начального расчета используем KV и характеристики LiPo
estimated_torque_nm = (voltage / 1000) * 0.5  # Приблизительный момент

# Крутящий момент на выходе редуктора
torque_output = estimated_torque_nm * transmission_ratio * motor_efficiency

# Максимальный ток (приблизительный расчет)
# Для LiPo батареи, примерно 20C discharge rating
c_rating = 20
max_current = (battery_capacity / 1000) * battery_cells * (c_rating / 60)  # в амперах

# Кинетическая энергия оружия (только движущаяся часть)
# E_k = (m * v^2) / 2, где m - масса оружия, v - скорость
kinetic_energy_weapon = (weapon_mass * (linear_speed_ms ** 2)) / 2

# Общий ток при максимальной нагрузке
# P = U * I, I = P / U
# Мощность примерно P = voltage * max_current * efficiency
motor_power = voltage * max_current * motor_efficiency
total_current_operating = motor_power / voltage if voltage > 0 else 0

# Время работы (часов)
total_capacity_mah = battery_capacity * battery_cells
time_operation_hours = total_capacity_mah / (total_current_operating * 1000) if total_current_operating > 0 else 0

# ========== ОСНОВНАЯ ПЛОЩАДЬ ==========

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="metric-unit">Скорость робота</div>
        <div class="metric-value">{speed_kmh:.1f}</div>
        <div class="metric-unit">км/ч</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
        <div class="metric-unit">Кинетическая энергия оружия</div>
        <div class="metric-value">{kinetic_energy_weapon:.1f}</div>
        <div class="metric-unit">Дж</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <div class="metric-unit">Общий ток</div>
        <div class="metric-value">{total_current_operating:.1f}</div>
        <div class="metric-unit">А</div>
    </div>
    """, unsafe_allow_html=True)

# ========== ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ==========

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Графики", "⚙️ Расчеты", "📈 Анализ", "ℹ️ Справка"])

with tab1:
    st.markdown("### Интерактивные Графики")
    
    # График 1: Зависимость скорости от диаметра колеса
    wheel_diameters = np.linspace(5, 50, 100)
    speeds_for_diameters = []
    
    for wd in wheel_diameters:
        r = (wd / 100) / 2
        circ = np.pi * wd / 100
        rpm_w = max_rpm_motor / transmission_ratio
        v_ms = (rpm_w / 60) * circ
        v_kmh = v_ms * 3.6
        speeds_for_diameters.append(v_kmh)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=wheel_diameters,
            y=speeds_for_diameters,
            mode='lines+markers',
            name='Скорость',
            line=dict(color='#667eea', width=3),
            marker=dict(size=6)
        ))
        fig1.add_vline(x=wheel_diameter, line_dash="dash", line_color="red", 
                       annotation_text=f"Текущий: {wheel_diameter}см",
                       annotation_position="top right")
        fig1.update_layout(
            title="Скорость робота vs Диаметр колеса",
            xaxis_title="Диаметр колеса (см)",
            yaxis_title="Скорость (км/ч)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # График 2: Энергия оружия от скорости
        speeds_range = np.linspace(0, speed_kmh * 1.5, 50)
        speeds_range_ms = speeds_range / 3.6
        energies = (weapon_mass * (speeds_range_ms ** 2)) / 2
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=speeds_range,
            y=energies,
            mode='lines',
            name='Кинетическая энергия',
            line=dict(color='#f5576c', width=3),
            fill='tozeroy'
        ))
        fig2.add_vline(x=speed_kmh, line_dash="dash", line_color="red",
                       annotation_text=f"Текущая: {speed_kmh:.1f}км/ч",
                       annotation_position="top right")
        fig2.update_layout(
            title="Кинетическая энергия оружия",
            xaxis_title="Скорость (км/ч)",
            yaxis_title="Энергия (Дж)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown("### Подробные Расчеты")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Параметры Мотора**")
        params_motor = {
            "Напряжение батареи": f"{voltage:.1f} В",
            "KV мотора": f"{kv_motor} об/мин/В",
            "Макс. обороты вала": f"{max_rpm_motor:.0f} об/мин",
            "Передаточное число": f"{transmission_ratio}:1",
            "Обороты на выходе": f"{rpm_wheel:.0f} об/мин",
            "КПД мотора": f"{motor_efficiency*100:.0f}%"
        }
        df_motor = pd.DataFrame(list(params_motor.items()), columns=["Параметр", "Значение"])
        st.table(df_motor)
    
    with col2:
        st.markdown("**Параметры Передвижения**")
        params_movement = {
            "Диаметр колеса": f"{wheel_diameter} см",
            "Радиус колеса": f"{wheel_radius_m*100:.1f} см",
            "Длина окружности": f"{wheel_circumference:.3f} м",
            "Скорость (м/с)": f"{linear_speed_ms:.2f} м/с",
            "Скорость (км/ч)": f"{speed_kmh:.2f} км/ч",
            "Крутящий момент": f"{torque_output:.2f} Н·м"
        }
        df_movement = pd.DataFrame(list(params_movement.items()), columns=["Параметр", "Значение"])
        st.table(df_movement)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("**Параметры Питания**")
        params_power = {
            "Емкость батареи": f"{battery_capacity} mAh",
            "Параллельных батарей": f"{battery_cells}",
            "Общая емкость": f"{total_capacity_mah} mAh",
            "Max ток (20C)": f"{max_current:.1f} А",
            "Рабочий ток": f"{total_current_operating:.2f} А",
            "Мощность мотора": f"{motor_power:.1f} Вт"
        }
        df_power = pd.DataFrame(list(params_power.items()), columns=["Параметр", "Значение"])
        st.table(df_power)
    
    with col4:
        st.markdown("**Параметры Конструкции**")
        params_construction = {
            "Масса брони": f"{armor_mass:.1f} кг",
            "Масса оружия": f"{weapon_mass:.1f} кг",
            "Общая масса": f"{mass_total:.1f} кг",
            "Кинет. энергия": f"{kinetic_energy_weapon:.2f} Дж",
            "Время работы": f"{time_operation_hours:.2f} часов",
            "Удельная мощность": f"{motor_power/mass_total:.2f} Вт/кг"
        }
        df_construction = pd.DataFrame(list(params_construction.items()), columns=["Параметр", "Значение"])
        st.table(df_construction)

with tab3:
    st.markdown("### Анализ и Рекомендации")
    
    # Анализ производительности
    st.markdown("#### 🎯 Анализ Производительности")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        efficiency_score = min(100, (speed_kmh / 30) * 100)
        st.metric("Скорость (оценка)", f"{efficiency_score:.0f}%", 
                 f"{speed_kmh:.1f} км/ч")
    
    with col2:
        power_density = motor_power / mass_total
        st.metric("Удельная мощность", f"{power_density:.1f} Вт/кг",
                 f"Мощность: {motor_power:.0f}Вт")
    
    with col3:
        energy_score = min(100, (kinetic_energy_weapon / 500) * 100)
        st.metric("Энергия оружия (оценка)", f"{energy_score:.0f}%",
                 f"{kinetic_energy_weapon:.1f} Дж")
    
    # Рекомендации
    col1, col2 = st.columns(2)
    
    with col1:
        if speed_kmh < 15:
            st.markdown("""
            <div class="warning-box">
            <strong>⚠️ Низкая скорость</strong><br>
            Рассмотрите увеличение KV мотора или уменьшение передаточного числа для большей скорости.
            </div>
            """, unsafe_allow_html=True)
        elif speed_kmh > 40:
            st.markdown("""
            <div class="warning-box">
            <strong>⚠️ Высокая скорость</strong><br>
            Убедитесь в достаточной охлаждении мотора и прочности конструкции при высоких оборотах.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
            <strong>✓ Оптимальная скорость</strong><br>
            Скорость находится в хорошем диапазоне для боевого робота.
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if time_operation_hours < 0.5:
            st.markdown("""
            <div class="warning-box">
            <strong>⚠️ Короткое время работы</strong><br>
            Рассмотрите увеличение емкости батареи или параллельных ячеек.
            </div>
            """, unsafe_allow_html=True)
        elif time_operation_hours > 2:
            st.markdown("""
            <div class="info-box">
            <strong>✓ Хорошее время работы</strong><br>
            Батарея обеспечит достаточное время боя.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
            <strong>✓ Нормальное время работы</strong><br>
            Батарея обеспечит приемлемое время боя.
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("### 📖 Справка по Формулам")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Скорость робота (v):**
        v = (RPM × Длина_окружности_колеса) / 60
        RPM = KV × Напряжение / Передаточное_число
        
        **Кинетическая энергия оружия (E_k):**
        E_k = (m × v²) / 2
        где m - масса оружия, v - скорость
        
        **Крутящий момент (τ):**
        τ = (V / 1000) × 0.5 × Передаточное_число × КПД
        """)
    
    with col2:
        st.markdown("""
        **Максимальный ток:**
        I_max = (Емкость_батареи / 1000) × Батареи_параллельно × C_rating
        C_rating - максимальный ток разряда (обычно 20-50C)
        
        **Время работы (t):**
        t = Общая_емкость / Рабочий_ток (в часах)
        
        **Удельная мощность:**
        P_удельная = Мощность_мотора / Общая_масса (Вт/кг)
        """)
    
    st.markdown("---")
    st.markdown("### Технические заметки")
    st.markdown("""
    - **KV мотора**: Количество оборотов на вольт напряжения (без нагрузки)
    - **Передаточное число**: Отношение входящих оборотов к выходящим (редукция)
    - **LiPo батареи**: Каждая ячейка имеет номинальное напряжение 3.7V
    - **C-rating**: Максимальный ток разряда батареи (обычно 20-50C)
    - **КПД**: Коэффициент полезного действия мотора (обычно 80-90%)
    """)

# ========== ПОДВАЛ ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <small>Калькулятор параметров боевого робота | v1.0</small><br>
    <small>Все расчеты приблизительны. Для точных значений проводите экспериментальные испытания.</small>
</div>
""", unsafe_allow_html=True)

