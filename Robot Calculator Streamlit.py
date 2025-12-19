import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Digital Twin: 1T Rex (Comparison Lab)",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STATE MANAGEMENT (SESSION STATE) ---
if 'saved_configs' not in st.session_state:
    st.session_state.saved_configs = []

def save_config(params, results, sim_stats, collision_stats):
    """Сохранение текущей конфигурации в память"""
    config = {
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'name': params['name'],
        'mass': results['total_mass'],
        'speed': results['speed_kmh'],
        'energy': results['weapon_energy'],
        'g_force': collision_stats['g_force_self'],
        'peak_current': sim_stats['peak_current'],
        'params': params # Сохраняем полные входные параметры на будущее
    }
    st.session_state.saved_configs.append(config)

def clear_configs():
    st.session_state.saved_configs = []

# --- ФИЗИЧЕСКИЕ КОНСТАНТЫ ---
MATERIALS = {
    "Алюминиевый сплав (АМг6/Д16Т)": 2.70,
    "Титан (VT6)": 4.43,
    "Сталь (Ст3/Hardox)": 7.85,
    "Полиуретан (Колеса)": 1.20
}
ROBOT_LIMIT_KG = 110.0
G_FORCE = 9.81
AMBIENT_TEMP = 25.0
C_THERMAL_MOTOR = 400.0
COOLING_COEFF_BASE = 0.5

# --- ФИЗИЧЕСКОЕ ЯДРО (PHYSICS ENGINE) ---
def get_damage_equivalent(energy_joules):
    if energy_joules < 100: return "Удар молотком"
    if energy_joules < 500: return "Пуля .22 LR"
    if energy_joules < 1000: return "Пуля 9мм ПМ"
    if energy_joules < 2000: return "Пуля 5.56 NATO"
    if energy_joules < 4000: return "Пуля 7.62 АКМ"
    if energy_joules < 10000: return "Выстрел из СВД"
    if energy_joules < 30000: return "Падение рояля (200кг)"
    return "Снаряд 30мм"

def simulate_collision(robot_mass, weapon_inertia, weapon_rpm, target_mass=110.0, impact_duration_ms=10.0):
    w_rad_s = (weapon_rpm * 2 * np.pi) / 60
    E_kinetic = 0.5 * weapon_inertia * (w_rad_s ** 2)
    L_initial = weapon_inertia * w_rad_s
    dt = impact_duration_ms / 1000.0
    efficiency = 0.7 
    E_transfer = E_kinetic * efficiency
    
    v_target_recoil = np.sqrt(2 * E_transfer / target_mass)
    a_target_ms2 = v_target_recoil / dt
    g_target = a_target_ms2 / G_FORCE
    
    v_self_recoil = (target_mass * v_target_recoil) / robot_mass
    a_self_ms2 = v_self_recoil / dt
    g_self = a_self_ms2 / G_FORCE
    
    return {
        'energy_joules': E_kinetic,
        'impact_force_kn': (target_mass * a_target_ms2) / 1000,
        'g_force_self': g_self,
        'g_force_target': g_target,
        'recoil_speed_kmh': v_self_recoil * 3.6,
        'equivalent': get_damage_equivalent(E_kinetic)
    }

def get_wire_recommendation(current_rms):
    if current_rms < 20: return "16 AWG"
    if current_rms < 40: return "14 AWG"
    if current_rms < 60: return "12 AWG"
    if current_rms < 90: return "10 AWG"
    if current_rms < 150: return "8 AWG"
    return "6 AWG (или шина)"

def simulate_full_system(params, total_mass_kg, dt=0.05, max_time=10.0):
    U_nom = params['voltage_v']
    bat_ir = params['battery_ir_mohm'] / 1000.0 
    drive_n, drive_kv = params['drive_count'], params['motor_kv']
    drive_R, drive_mass = 0.05, 1.0
    wheel_r = (params['wheel_dia_mm'] / 1000) / 2
    gear_ratio, mu = params['gear_ratio'], params['friction_coeff']
    esc_lim_drive = params['esc_current_limit']

    weap_n, weap_kv = params['weapon_motor_count'], params['weapon_motor_kv']
    weap_R, weap_mass = 0.08, 1.5
    weap_reduction, weap_inertia = params['weapon_reduction'], params['weapon_inertia']
    esc_lim_weap = params['esc_current_limit_weapon']
    is_weapon_active = params['simulate_weapon']

    drive_kt = 9.55 / drive_kv if drive_kv > 0 else 0
    weap_kt = 9.55 / weap_kv if weap_kv > 0 else 0

    times = np.arange(0, max_time, dt)
    history = {'t': [], 'v': [], 'I_bat': [], 'U_sag': [], 'T_drive': [], 'T_weap': [], 'weap_rpm': []}
    
    v, w_weap = 0, 0
    temp_drive, temp_weap = AMBIENT_TEMP, AMBIENT_TEMP
    
    for t in times:
        wheel_rpm = (v / (2 * np.pi * wheel_r)) * 60
        motor_rpm_drive = wheel_rpm * gear_ratio
        bemf_drive = motor_rpm_drive / drive_kv
        
        U_current = history['U_sag'][-1] if len(history['U_sag']) > 0 else U_nom

        I_drive = min((U_current - bemf_drive) / drive_R, esc_lim_drive) if U_current > bemf_drive else 0
        
        if is_weapon_active:
            rotor_rpm = (w_weap * 60) / (2 * np.pi)
            motor_rpm_weap = rotor_rpm * weap_reduction
            bemf_weap = motor_rpm_weap / weap_kv
            I_weap_raw = (U_current - bemf_weap) / weap_R if U_current > bemf_weap else 0
            I_weap = min(I_weap_raw, esc_lim_weap)
        else:
            I_weap, motor_rpm_weap = 0, 0
        
        I_total = (I_drive * drive_n) + (I_weap * weap_n)
        U_sag = U_nom - (I_total * bat_ir)
        
        torque_drive = I_drive * drive_kt * 0.9
        F_tract = (torque_drive * gear_ratio / wheel_r) * drive_n
        F_fric = total_mass_kg * G_FORCE * mu
        F_net = min(F_tract, F_fric) - (0.5 * 0.5 * v**2)
        v += (F_net / total_mass_kg) * dt
        
        if is_weapon_active:
            torque_weap = I_weap * weap_kt * weap_n * 0.85
            alpha = (torque_weap * weap_reduction - 0.00001 * w_weap**2) / weap_inertia
            w_weap += alpha * dt
        
        P_heat_d = (I_drive ** 2) * drive_R
        P_cool_d = (temp_drive - AMBIENT_TEMP) * (COOLING_COEFF_BASE + 0.1 * v)
        temp_drive += (P_heat_d - P_cool_d) / (drive_mass * C_THERMAL_MOTOR) * dt
        
        if is_weapon_active:
            P_heat_w = (I_weap ** 2) * weap_R
            P_cool_w = (temp_weap - AMBIENT_TEMP) * (COOLING_COEFF_BASE + 0.05 * w_weap)
            temp_weap += (P_heat_w - P_cool_w) / (weap_mass * C_THERMAL_MOTOR) * dt

        history['t'].append(t)
        history['v'].append(v * 3.6)
        history['I_bat'].append(I_total)
        history['U_sag'].append(U_sag)
        history['T_drive'].append(temp_drive)
        history['T_weap'].append(temp_weap)
        history['weap_rpm'].append(w_weap * 60 / (2*np.pi))

    return pd.DataFrame(history)

def calculate_plate_weight(material_name, area_m2, thickness_mm):
    density_g_cm3 = MATERIALS[material_name]
    return area_m2 * (thickness_mm / 1000) * density_g_cm3 * 1000

def generate_report(params, results, sim_stats, collision_stats):
    date_str = datetime.now().strftime("%d.%m.%Y")
    
    # Генерация Markdown таблицы сравнения (если есть сохранения)
    comparison_md = ""
    if st.session_state.saved_configs:
        comparison_md = "\n## 4. Сравнительный анализ конфигураций\n| Конфигурация | Масса (кг) | Скорость (км/ч) | Энергия (кДж) | Перегрузка (G) |\n|---|---|---|---|---|\n"
        for cfg in st.session_state.saved_configs:
            comparison_md += f"| {cfg['name']} | {cfg['mass']:.1f} | {cfg['speed']:.1f} | {cfg['energy']/1000:.1f} | {cfg['g_force']:.1f} |\n"
        # Добавляем текущую
        comparison_md += f"| **ТЕКУЩАЯ** | **{results['total_mass']:.1f}** | **{results['speed_kmh']:.1f}** | **{collision_stats['energy_joules']/1000:.1f}** | **{collision_stats['g_force_self']:.1f}** |\n"

    report = f"""
# ТЕХНИЧЕСКИЙ ПАСПОРТ
**Проект:** {params['name']}
**Дата:** {date_str}

## 1. Боевая эффективность
* **Энергия удара:** {collision_stats['energy_joules']/1000:.1f} кДж
* **Сила удара:** {collision_stats['impact_force_kn']:.1f} кН
* **Ожидаемая перегрузка (Self):** {collision_stats['g_force_self']:.1f} G

## 2. Энергетика
* **Пиковый ток:** {sim_stats['peak_current']:.0f} А
* **Температура моторов (Weapon):** {sim_stats['temp_weap_max']:.1f} °C

## 3. Общие характеристики
* **Макс. скорость:** {results['speed_kmh']:.1f} км/ч
* **Полная масса:** {results['total_mass']:.2f} кг

{comparison_md}

---
*Digital Twin Physics Engine v4.0*
"""
    return report

# --- UI: SIDEBAR ---
st.sidebar.title("🦖 1T Rex: Lab")

st.sidebar.header("1. Энергетика")
robot_name = st.sidebar.text_input("Имя конфига", value="1T Rex (Base)")
voltage_s = st.sidebar.slider("Аккумулятор (S)", 6, 14, 12)
battery_ir_mohm = st.sidebar.number_input("Вн. сопр. (мОм)", value=25.0)
voltage_nom = voltage_s * 3.7

st.sidebar.header("2. Ходовая")
drive_motor_count = st.sidebar.selectbox("Кол-во моторов хода", [2, 4], index=1)
motor_kv = st.sidebar.number_input("KV моторов хода", value=190)
gear_ratio = st.sidebar.number_input("Редукция хода", value=12.5)
wheel_dia_mm = st.sidebar.number_input("Диаметр колеса (мм)", value=200)
esc_current_limit = st.sidebar.slider("Лимит тока ESC (ход)", 20, 150, 60)
friction_coeff = st.sidebar.slider("Коэф. трения", 0.3, 1.0, 0.7)

st.sidebar.header("3. Оружие")
simulate_weapon = st.sidebar.checkbox("Включить симуляцию", value=True)
weapon_motor_count = st.sidebar.selectbox("Кол-во моторов орудия", [1, 2], index=1)
weapon_motor_kv = st.sidebar.number_input("KV моторов оружия", value=150)
weapon_reduction = st.sidebar.number_input("Редукция оружия", value=1.5)
weapon_mass_kg = st.sidebar.number_input("Масса ротора (кг)", value=28.0)
weapon_radius_mm = st.sidebar.number_input("Радиус удара (мм)", value=180)
esc_current_limit_weapon = st.sidebar.slider("Лимит тока ESC (орудие)", 50, 300, 120)

st.sidebar.header("4. Вес")
armor_thickness = st.sidebar.slider("Толщина брони (мм)", 2, 10, 5)
armor_coverage = st.sidebar.slider("Покрытие броней %", 10, 100, 35)

# --- CALCULATIONS ---
wheel_circumference = (wheel_dia_mm/1000) * np.pi
speed_kmh_static = ((voltage_nom * motor_kv / gear_ratio) * wheel_circumference / 60) * 3.6
inertia_weapon = 0.6 * weapon_mass_kg * ((weapon_radius_mm/1000)**2)
weapon_rpm_static = (voltage_nom * weapon_motor_kv) / weapon_reduction
energy_static = 0.5 * inertia_weapon * ((weapon_rpm_static * 2 * np.pi / 60)**2)

area_total = 3.0 
armor_mass = calculate_plate_weight("Алюминиевый сплав (АМг6/Д16Т)", area_total * (armor_coverage/100), armor_thickness)
total_mass = 18.0 + 12.0 + 25.0 + weapon_mass_kg + armor_mass 

sim_params = {
    'voltage_v': voltage_nom, 'battery_ir_mohm': battery_ir_mohm,
    'drive_count': drive_motor_count, 'motor_kv': motor_kv, 'gear_ratio': gear_ratio,
    'wheel_dia_mm': wheel_dia_mm, 'friction_coeff': friction_coeff, 'esc_current_limit': esc_current_limit,
    'weapon_motor_count': weapon_motor_count, 'weapon_motor_kv': weapon_motor_kv,
    'weapon_reduction': weapon_reduction, 'weapon_inertia': inertia_weapon, 'esc_current_limit_weapon': esc_current_limit_weapon,
    'simulate_weapon': simulate_weapon
}

df_sim = simulate_full_system(sim_params, total_mass, max_time=8.0)
collision_results = simulate_collision(total_mass, inertia_weapon, weapon_rpm_static, target_mass=110.0)

sim_stats = {
    'peak_current': df_sim['I_bat'].max(), 'min_voltage': df_sim['U_sag'].min(), 
    'temp_drive_max': df_sim['T_drive'].max(), 'temp_weap_max': df_sim['T_weap'].max(),
    'sim_time': 8.0, 'wire_awg': get_wire_recommendation(np.sqrt(np.mean(df_sim['I_bat']**2)))
}
results_dict = {
    'speed_kmh': speed_kmh_static, 'weapon_energy': energy_static, 'total_mass': total_mass, 'weapon_rpm': weapon_rpm_static
}
params_dict = {'name': robot_name, 'voltage_s': voltage_s, 'voltage_v': voltage_nom}

# --- VISUALIZATION ---
st.title(f"🛠️ {robot_name}: Comparison Lab")

# Actions Bar
col_act1, col_act2 = st.columns([1, 4])
with col_act1:
    if st.button("💾 Сохранить конфиг"):
        save_config(params_dict, results_dict, sim_stats, collision_results)
        st.success(f"Сохранено: {robot_name}")
with col_act2:
    if st.button("🗑️ Очистить историю"):
        clear_configs()
        st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚖️ Сравнение", "💥 Столкновение", "📊 Сводка", "📈 Динамика", "📑 Паспорт"])

with tab1:
    st.header("Сравнительный анализ (A/B Testing)")
    
    if len(st.session_state.saved_configs) == 0:
        st.info("Нет сохраненных конфигураций. Настройте параметры слева и нажмите 'Сохранить конфиг', чтобы добавить вариант для сравнения.")
    else:
        # Создаем DataFrame для сравнения
        data_compare = []
        # Добавляем сохраненные
        for cfg in st.session_state.saved_configs:
            data_compare.append({
                "Версия": cfg['name'],
                "Масса (кг)": cfg['mass'],
                "Скорость (км/ч)": cfg['speed'],
                "Энергия (кДж)": cfg['energy'] / 1000,
                "Перегрузка (G)": cfg['g_force'],
                "Ток пик (А)": cfg['peak_current']
            })
        # Добавляем текущий (Live)
        data_compare.append({
            "Версия": "⚡ CURRENT (LIVE)",
            "Масса (кг)": results_dict['total_mass'],
            "Скорость (км/ч)": results_dict['speed_kmh'],
            "Энергия (кДж)": collision_results['energy_joules'] / 1000,
            "Перегрузка (G)": collision_results['g_force_self'],
            "Ток пик (А)": sim_stats['peak_current']
        })
        
        df_cmp = pd.DataFrame(data_compare)
        
        # Подсветка лучшего/худшего
        st.dataframe(df_cmp.style.highlight_max(axis=0, color='lightgreen', subset=['Скорость (км/ч)', 'Энергия (кДж)'])
                                 .highlight_min(axis=0, color='lightgreen', subset=['Масса (кг)', 'Перегрузка (G)', 'Ток пик (А)'])
                                 .format("{:.1f}", subset=df_cmp.columns[1:]),
                     use_container_width=True)
        
        # Визуализация (Radar Chart)
        # Нормализация данных для радара
        categories = ['Масса', 'Скорость', 'Энергия', 'Устойчивость (1/G)']
        
        fig_radar = go.Figure()
        
        for i, row in df_cmp.iterrows():
            # Инвертируем массу и G (меньше = лучше)
            vals = [
                100 - (row['Масса (кг)']/1.5), 
                row['Скорость (км/ч)']*3, 
                row['Энергия (кДж)'], 
                100 - row['Перегрузка (G)']
            ]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=categories, fill='toself', name=row['Версия']
            ))
            
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, title="Сравнение характеристик")
        st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    st.metric("Энергия удара", f"{collision_results['energy_joules']/1000:.1f} кДж")
    st.metric("Перегрузка Self", f"{collision_results['g_force_self']:.1f} G")
    
with tab3:
    st.metric("Масса", f"{total_mass:.1f} кг")
    st.metric("Скорость", f"{speed_kmh_static:.1f} км/ч")

with tab4:
    fig_mech = go.Figure()
    fig_mech.add_trace(go.Scatter(x=df_sim['t'], y=df_sim['v'], name='Скорость'))
    st.plotly_chart(fig_mech)

with tab5:
    report_md = generate_report(params_dict, results_dict, sim_stats, collision_results)
    st.markdown(report_md)
    st.download_button("📥 Скачать", report_md, "passport_final.md")
