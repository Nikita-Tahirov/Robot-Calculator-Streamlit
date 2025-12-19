import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- 1. CONFIGURATION & ASSETS ---
st.set_page_config(
    page_title="1T Rex: Digital Twin",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DESIGN SYSTEM: LIQUID GLASS (CSS INJECTION) ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* IMPORT FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600&family=Unbounded:wght@300;400;600;700&display=swap');

        /* === THEME VARIABLES === */
        :root {
            --bg-color: #05020a;
            --accent-primary: #d50085;
            --accent-secondary: #0099ff;
            --text-main: #ffffff;
            --text-muted: #a0a0b0;
            --glass-bg: rgba(20, 15, 30, 0.4);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            --font-head: 'Unbounded', sans-serif;
            --font-body: 'Raleway', sans-serif;
        }

        /* === GLOBAL RESET & BACKGROUND === */
        .stApp {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(213, 0, 133, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0, 153, 255, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, #1a0b2e 0%, #05020a 100%);
            background-attachment: fixed;
            font-family: var(--font-body);
            color: var(--text-main);
        }
        
        /* TYPOGRAPHY */
        h1, h2, h3, .stMetricLabel {
            font-family: var(--font-head) !important;
            font-weight: 600;
            letter-spacing: -0.02em;
        }
        
        h1 {
            background: linear-gradient(90deg, #fff, #c0c0c0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
        }

        /* === SIDEBAR (GLASS PANEL) === */
        [data-testid="stSidebar"] {
            background-color: transparent !important;
            border-right: 1px solid var(--glass-border);
            backdrop-filter: blur(20px);
            box-shadow: 10px 0 30px rgba(0,0,0,0.5);
        }
        
        [data-testid="stSidebar"] h1 {
            font-size: 1.5rem !important;
            background: linear-gradient(270deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* === WIDGETS (INPUTS, SLIDERS) === */
        .stTextInput > div > div, .stNumberInput > div > div, .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            color: var(--text-main) !important;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div:hover, .stNumberInput > div > div:hover {
            border-color: var(--accent-secondary) !important;
            box-shadow: 0 0 10px rgba(0, 153, 255, 0.2);
        }

        /* Sliders */
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background-color: var(--accent-primary) !important;
            box-shadow: 0 0 15px var(--accent-primary);
        }
        .stSlider [data-baseweb="slider"] div > div {
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        }

        /* === CARDS & CONTAINERS (METRICS) === */
        [data-testid="stMetric"] {
            background: var(--glass-bg);
            padding: 20px;
            border-radius: 20px;
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(10px);
            box-shadow: var(--glass-shadow);
            transition: transform 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.2);
        }

        [data-testid="stMetricValue"] {
            font-family: 'Unbounded', sans-serif !important;
            font-size: 2rem !important;
            background: linear-gradient(90deg, var(--accent-secondary), #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* === TABS === */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: rgba(255,255,255,0.05);
            border-radius: 12px;
            border: 1px solid transparent;
            color: var(--text-muted);
            font-family: var(--font-head);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: rgba(0, 153, 255, 0.15);
            border-color: var(--accent-secondary);
            color: #fff;
            box-shadow: 0 0 20px rgba(0, 153, 255, 0.2);
        }

        /* === TABLES === */
        [data-testid="stDataFrame"] {
            background: transparent !important;
        }
        
        /* === BUTTONS === */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-primary), #a00060) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-family: var(--font-head) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            box-shadow: 0 0 25px var(--accent-primary);
            transform: scale(1.02);
        }

        /* Hiding standard streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
    </style>
    """, unsafe_allow_html=True)

# Function to apply theme to Plotly charts
def apply_glass_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Raleway", color="#ffffff"),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="#1a0b2e",
            font_size=14,
            font_family="Unbounded"
        )
    )
    return fig

# --- 3. LOGIC & CALCULATIONS (PRESERVED) ---

inject_custom_css() # APPLY DESIGN SYSTEM

# --- STATE MANAGEMENT ---
if 'saved_configs' not in st.session_state:
    st.session_state.saved_configs = []

def save_config(params, results, sim_stats, collision_stats):
    config = {
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'name': params['name'],
        'mass': results['total_mass'],
        'speed': results['speed_kmh'],
        'energy': results['weapon_energy'],
        'g_force': collision_stats['g_force_self'],
        'peak_current': sim_stats['peak_current'],
        'params': params
    }
    st.session_state.saved_configs.append(config)

def clear_configs():
    st.session_state.saved_configs = []

# --- CONSTANTS ---
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

# --- PHYSICS ENGINE ---
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
            I_weap = 0
        
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
    comparison_md = ""
    if st.session_state.saved_configs:
        comparison_md = "\n## 4. Сравнительный анализ\n| Версия | Масса (кг) | V (км/ч) | E (кДж) | G-Force |\n|---|---|---|---|---|\n"
        for cfg in st.session_state.saved_configs:
            comparison_md += f"| {cfg['name']} | {cfg['mass']:.1f} | {cfg['speed']:.1f} | {cfg['energy']/1000:.1f} | {cfg['g_force']:.1f} |\n"
        comparison_md += f"| **CURRENT** | **{results['total_mass']:.1f}** | **{results['speed_kmh']:.1f}** | **{collision_stats['energy_joules']/1000:.1f}** | **{collision_stats['g_force_self']:.1f}** |\n"

    report = f"""
# ТЕХНИЧЕСКИЙ ПАСПОРТ: {params['name']}
**Дата:** {date_str}

## 1. Impact Analysis
* **Energy:** {collision_stats['energy_joules']/1000:.1f} kJ
* **G-Force:** {collision_stats['g_force_self']:.1f} G

## 2. Power & Thermal
* **Max Current:** {sim_stats['peak_current']:.0f} A
* **Motor Temp:** {sim_stats['temp_weap_max']:.1f} °C

## 3. General Stats
* **Speed:** {results['speed_kmh']:.1f} km/h
* **Total Mass:** {results['total_mass']:.2f} kg

{comparison_md}
---
*Generated by 1T Rex Digital Twin*
"""
    return report

# --- UI: SIDEBAR CONTROLS ---
st.sidebar.markdown("<h1>⚙️ SYSTEM CONFIG</h1>", unsafe_allow_html=True)

st.sidebar.caption("1. ENERGY & BASE")
robot_name = st.sidebar.text_input("Project Name", value="1T Rex (Base)")
voltage_s = st.sidebar.slider("Battery (S)", 6, 14, 12)
battery_ir_mohm = st.sidebar.number_input("IR (mOhm)", value=25.0)
voltage_nom = voltage_s * 3.7

st.sidebar.caption("2. DRIVE TRAIN")
drive_motor_count = st.sidebar.selectbox("Motors (Drive)", [2, 4], index=1)
motor_kv = st.sidebar.number_input("Drive KV", value=190)
gear_ratio = st.sidebar.number_input("Gear Ratio", value=12.5)
wheel_dia_mm = st.sidebar.number_input("Wheel (mm)", value=200)
esc_current_limit = st.sidebar.slider("ESC Limit (Drive)", 20, 150, 60)
friction_coeff = st.sidebar.slider("Friction (µ)", 0.3, 1.0, 0.7)

st.sidebar.caption("3. WEAPON SYSTEM")
simulate_weapon = st.sidebar.checkbox("Simulate Weapon", value=True)
weapon_motor_count = st.sidebar.selectbox("Motors (Weapon)", [1, 2], index=1)
weapon_motor_kv = st.sidebar.number_input("Weapon KV", value=150)
weapon_reduction = st.sidebar.number_input("Reduction", value=1.5)
weapon_mass_kg = st.sidebar.number_input("Rotor Mass (kg)", value=28.0)
weapon_radius_mm = st.sidebar.number_input("Radius (mm)", value=180)
esc_current_limit_weapon = st.sidebar.slider("ESC Limit (Weapon)", 50, 300, 120)

st.sidebar.caption("4. ARMOR & WEIGHT")
armor_thickness = st.sidebar.slider("Armor (mm)", 2, 10, 5)
armor_coverage = st.sidebar.slider("Coverage %", 10, 100, 35)

# --- BACKEND CALCULATION ---
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
    'wire_awg': get_wire_recommendation(np.sqrt(np.mean(df_sim['I_bat']**2)))
}
results_dict = {
    'speed_kmh': speed_kmh_static, 'weapon_energy': energy_static, 'total_mass': total_mass, 'weapon_rpm': weapon_rpm_static
}
params_dict = {'name': robot_name, 'voltage_s': voltage_s, 'voltage_v': voltage_nom}

# --- VISUALIZATION LAYOUT ---
st.markdown(f"<h1>🚧 {robot_name.upper()} <span style='font-size:0.5em; opacity:0.5'>// DESIGN LAB</span></h1>", unsafe_allow_html=True)

# Actions
c1, c2 = st.columns([1, 5])
if c1.button("SAVE CONFIG"):
    save_config(params_dict, results_dict, sim_stats, collision_results)
    st.toast("Configuration saved to memory buffer.", icon="💾")
if c2.button("CLEAR MEMORY"):
    clear_configs()
    st.rerun()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["COMPARISON", "IMPACT", "DASHBOARD", "TELEMETRY", "PASSPORT"])

with tab1:
    st.markdown("<h3>⚔️ CONFIGURATION ANALYSIS</h3>", unsafe_allow_html=True)
    if not st.session_state.saved_configs:
        st.info("Awaiting configuration snapshots for comparison...")
    else:
        data_compare = []
        for cfg in st.session_state.saved_configs:
            data_compare.append({
                "ID": cfg['name'], "MASS": cfg['mass'], "SPD": cfg['speed'], "NRG": cfg['energy']/1000, "G": cfg['g_force']
            })
        data_compare.append({
            "ID": "ACTIVE", "MASS": results_dict['total_mass'], "SPD": results_dict['speed_kmh'], 
            "NRG": collision_results['energy_joules']/1000, "G": collision_results['g_force_self']
        })
        
        df_cmp = pd.DataFrame(data_compare)
        st.dataframe(df_cmp.style.highlight_max(axis=0, color='#0044ff', subset=['SPD', 'NRG']), use_container_width=True)
        
        # Radar Chart
        categories = ['Agility (Speed)', 'Lethality (Energy)', 'Durability (Mass)', 'Stability (G)']
        fig_radar = go.Figure()
        for i, row in df_cmp.iterrows():
            vals = [row['SPD']*2, row['NRG'], 150-row['MASS'], 100-row['G']] # Norm
            fig_radar.add_trace(go.Scatterpolar(r=vals, theta=categories, fill='toself', name=row['ID']))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, color="white")),
            showlegend=True,
            font=dict(color="white")
        )
        st.plotly_chart(apply_glass_theme(fig_radar), use_container_width=True)

with tab2:
    c_i1, c_i2 = st.columns(2)
    with c_i1:
        st.metric("IMPACT ENERGY", f"{collision_results['energy_joules']/1000:.1f} kJ", "Kinetic Output")
        st.markdown(f"<div style='background:rgba(255,0,0,0.1); padding:15px; border-radius:10px; border:1px solid red'>⚠️ EQUIVALENT: {collision_results['equivalent']}</div>", unsafe_allow_html=True)
    with c_i2:
        st.metric("SELF G-FORCE", f"{collision_results['g_force_self']:.1f} G", "Recoil Shock")
        st.metric("IMPACT FORCE", f"{collision_results['impact_force_kn']:.1f} kN", "Instant Load")

with tab3:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOP SPEED", f"{speed_kmh_static:.1f} km/h")
    c2.metric("TOTAL MASS", f"{total_mass:.1f} kg")
    c3.metric("PEAK CURRENT", f"{sim_stats['peak_current']:.0f} A")
    c4.metric("VOLTAGE SAG", f"{(voltage_nom-sim_stats['min_voltage']):.1f} V")

with tab4:
    st.markdown("<h3>📈 REAL-TIME TELEMETRY</h3>", unsafe_allow_html=True)
    
    # 1. Elec
    fig_elec = go.Figure()
    fig_elec.add_trace(go.Scatter(x=df_sim['t'], y=df_sim['I_bat'], name='Current (A)', line=dict(color='#d50085', width=3)))
    fig_elec.add_trace(go.Scatter(x=df_sim['t'], y=df_sim['U_sag'], name='Voltage (V)', yaxis='y2', line=dict(color='#0099ff', dash='dot')))
    fig_elec.update_layout(yaxis2=dict(overlaying='y', side='right'), title="Battery Load Profile")
    st.plotly_chart(apply_glass_theme(fig_elec), use_container_width=True)
    
    # 2. Mech
    fig_mech = go.Figure()
    fig_mech.add_trace(go.Scatter(x=df_sim['t'], y=df_sim['v'], name='Velocity (km/h)', line=dict(color='#00ff99', width=3)))
    if simulate_weapon:
        fig_mech.add_trace(go.Scatter(x=df_sim['t'], y=df_sim['weap_rpm'], name='Weapon RPM', yaxis='y2', line=dict(color='#ff9900')))
    fig_mech.update_layout(yaxis2=dict(overlaying='y', side='right'), title="Mechanical Output")
    st.plotly_chart(apply_glass_theme(fig_mech), use_container_width=True)

with tab5:
    report_md = generate_report(params_dict, results_dict, sim_stats, collision_results)
    st.markdown(report_md)
    st.download_button("DOWNLOAD PASSPORT", report_md, "passport_neon.md")
