import numpy as np
import pandas as pd

# Физические константы
G_FORCE = 9.81
AMBIENT_TEMP = 25.0
C_THERMAL_MOTOR = 400.0       # Дж/(кг*К) условная теплоемкость мотора
COOLING_COEFF_BASE = 0.5      # базовый коэффициент теплоотдачи


def get_wire_recommendation(current_rms: float) -> str:
    """Рекомендуемое сечение кабеля по RMS-току."""
    if current_rms < 20:
        return "16 AWG"
    if current_rms < 40:
        return "14 AWG"
    if current_rms < 60:
        return "12 AWG"
    if current_rms < 90:
        return "10 AWG"
    if current_rms < 150:
        return "8 AWG"
    return "6 AWG (или шина)"


def get_damage_equivalent(energy_joules: float) -> str:
    """Человеко-понятное описание энергии удара."""
    if energy_joules < 100:
        return "Удар молотком"
    if energy_joules < 500:
        return "Пуля .22 LR"
    if energy_joules < 1000:
        return "Пуля 9мм ПМ (~600 Дж)"
    if energy_joules < 2000:
        return "Пуля 5.56 NATO"
    if energy_joules < 4000:
        return "Пуля 7.62 АКМ (~2000 Дж)"
    if energy_joules < 10000:
        return "Выстрел из СВД"
    if energy_joules < 30000:
        return "Падение рояля (200 кг) с высоты"
    return "Уровень снаряда 30мм"


# ---------- Статические расчеты ----------

def run_static_calculations(inputs: dict) -> dict:
    """Статические характеристики: скорость, масса, инерция оружия."""
    voltage_nom = inputs["voltage_s"] * 3.7
    motor_kv = inputs["motor_kv"]
    gear_ratio = inputs["gear_ratio"]
    wheel_dia_mm = inputs["wheel_dia_mm"]
    weapon_mass_kg = inputs["weapon_mass_kg"]
    weapon_radius_mm = inputs["weapon_radius_mm"]
    armor_thickness = inputs["armor_thickness"]
    armor_coverage = inputs["armor_coverage"]
    base_drive_mass = inputs["base_drive_mass"]
    base_elec_mass = inputs["base_elec_mass"]
    base_frame_mass = inputs["base_frame_mass"]
    armor_density_kg_m3 = inputs["armor_density_kg_m3"]
    armor_area_total = inputs["armor_area_total"]

    # Скорость
    wheel_circumference = (wheel_dia_mm / 1000) * np.pi
    speed_kmh = ((voltage_nom * motor_kv / gear_ratio) *
                 wheel_circumference / 60) * 3.6

    # Момент инерции ротора (усреднённый коэффициент 0.6)
    weapon_inertia = 0.6 * weapon_mass_kg * (weapon_radius_mm / 1000) ** 2

    # Обороты оружия (теоретические)
    weapon_motor_kv = inputs["weapon_motor_kv"]
    weapon_reduction = inputs["weapon_reduction"]
    weapon_rpm = (voltage_nom * weapon_motor_kv) / weapon_reduction
    weapon_omega = weapon_rpm * 2 * np.pi / 60
    weapon_energy = 0.5 * weapon_inertia * weapon_omega ** 2

    # Масса брони
    active_area = armor_area_total * (armor_coverage / 100)
    armor_mass = active_area * (armor_thickness / 1000) * armor_density_kg_m3

    total_mass = (base_drive_mass + base_elec_mass + base_frame_mass +
                  weapon_mass_kg + armor_mass)

    return {
        "voltage_nom": voltage_nom,
        "speed_kmh": speed_kmh,
        "weapon_inertia": weapon_inertia,
        "weapon_rpm": weapon_rpm,
        "weapon_energy": weapon_energy,
        "armor_mass": armor_mass,
        "total_mass": total_mass,
    }


# ---------- Динамика + электрика + термодинамика ----------

def simulate_full_system(params: dict,
                         total_mass_kg: float,
                         dt: float = 0.05,
                         max_time: float = 8.0) -> pd.DataFrame:
    """
    Совмещённая симуляция: динамика хода, раскрутка оружия, ток, просадка, нагрев.
    """
    U_nom = params["voltage_nom"]
    bat_ir = params["battery_ir_mohm"] / 1000.0

    # Drive
    drive_n = params["drive_motor_count"]
    drive_kv = params["motor_kv"]
    drive_R = 0.05
    drive_mass = 1.0
    wheel_r = (params["wheel_dia_mm"] / 1000) / 2
    gear_ratio = params["gear_ratio"]
    mu = params["friction_coeff"]
    esc_lim_drive = params["esc_current_limit_drive"]

    # Weapon
    weap_on = params["simulate_weapon"]
    weap_n = params["weapon_motor_count"]
    weap_kv = params["weapon_motor_kv"]
    weap_R = 0.08
    weap_mass = 1.5
    weap_red = params["weapon_reduction"]
    weap_inertia = params["weapon_inertia"]
    esc_lim_weap = params["esc_current_limit_weapon"]

    drive_kt = 9.55 / drive_kv if drive_kv > 0 else 0
    weap_kt = 9.55 / weap_kv if weap_kv > 0 else 0

    times = np.arange(0, max_time, dt)
    hist = {
        "t": [], "v_kmh": [], "I_bat": [], "U_sag": [],
        "T_drive": [], "T_weapon": [], "weapon_rpm": []
    }

    v = 0.0
    w_weap = 0.0
    temp_drive = AMBIENT_TEMP
    temp_weap = AMBIENT_TEMP

    for t in times:
        wheel_rpm = (v / (2 * np.pi * wheel_r)) * 60
        motor_rpm_drive = wheel_rpm * gear_ratio
        bemf_drive = motor_rpm_drive / drive_kv

        U_current = hist["U_sag"][-1] if hist["U_sag"] else U_nom

        if U_current > bemf_drive:
            I_drive = (U_current - bemf_drive) / drive_R
            I_drive = min(I_drive, esc_lim_drive)
        else:
            I_drive = 0.0

        # Weapon current
        if weap_on:
            rotor_rpm = (w_weap * 60) / (2 * np.pi)
            motor_rpm_weap = rotor_rpm * weap_red
            bemf_weap = motor_rpm_weap / weap_kv
            if U_current > bemf_weap:
                I_weap = (U_current - bemf_weap) / weap_R
                I_weap = min(I_weap, esc_lim_weap)
            else:
                I_weap = 0.0
        else:
            I_weap = 0.0

        I_total = I_drive * drive_n + I_weap * weap_n
        U_sag = U_nom - I_total * bat_ir

        # Drive mechanics
        torque_drive = I_drive * drive_kt * 0.9
        F_tract = (torque_drive * gear_ratio / wheel_r) * drive_n
        F_fric = total_mass_kg * G_FORCE * mu
        F_net = min(F_tract, F_fric) - 0.5 * 0.5 * v ** 2
        a = F_net / total_mass_kg
        v += a * dt

        # Weapon mechanics
        if weap_on:
            torque_weap = I_weap * weap_kt * weap_n * 0.85
            trq_drag = 1e-5 * w_weap ** 2
            alpha = (torque_weap * weap_red - trq_drag) / weap_inertia
            w_weap += alpha * dt

        # Thermal drive
        P_heat_d = (I_drive ** 2) * drive_R
        P_cool_d = (temp_drive - AMBIENT_TEMP) * (COOLING_COEFF_BASE + 0.1 * max(v, 0))
        temp_drive += (P_heat_d - P_cool_d) / (drive_mass * C_THERMAL_MOTOR) * dt

        # Thermal weapon
        if weap_on:
            P_heat_w = (I_weap ** 2) * weap_R
            P_cool_w = (temp_weap - AMBIENT_TEMP) * (COOLING_COEFF_BASE + 0.05 * w_weap)
            temp_weap += (P_heat_w - P_cool_w) / (weap_mass * C_THERMAL_MOTOR) * dt

        hist["t"].append(t)
        hist["v_kmh"].append(v * 3.6)
        hist["I_bat"].append(I_total)
        hist["U_sag"].append(U_sag)
        hist["T_drive"].append(temp_drive)
        hist["T_weapon"].append(temp_weap)
        hist["weapon_rpm"].append(w_weap * 60 / (2 * np.pi))

    return pd.DataFrame(hist)


# ---------- Столкновения ----------

def analyze_collision(robot_mass: float,
                      weapon_inertia: float,
                      weapon_rpm: float,
                      target_mass: float = 110.0,
                      impact_duration_ms: float = 10.0) -> dict:
    """Анализ удара спиннером по цели такой же массы."""
    w = weapon_rpm * 2 * np.pi / 60
    E_kin = 0.5 * weapon_inertia * w ** 2

    dt = impact_duration_ms / 1000.0
    efficiency = 0.7
    E_transfer = E_kin * efficiency

    v_target = np.sqrt(2 * E_transfer / target_mass)
    a_target = v_target / dt
    g_target = a_target / G_FORCE

    v_self = (target_mass * v_target) / robot_mass
    a_self = v_self / dt
    g_self = a_self / G_FORCE

    impact_force_kn = target_mass * a_target / 1000.0

    return {
        "energy_joules": E_kin,
        "impact_force_kn": impact_force_kn,
        "g_force_self": g_self,
        "g_force_target": g_target,
        "recoil_speed_kmh": v_self * 3.6,
        "equivalent": get_damage_equivalent(E_kin),
    }


# ---------- Агрегация статистики и отчёт ----------

def aggregate_sim_stats(df: pd.DataFrame) -> dict:
    """Сводная статистика по результатам симуляции."""
    peak_current = df["I_bat"].max()
    min_voltage = df["U_sag"].min()
    temp_drive_max = df["T_drive"].max()
    temp_weap_max = df["T_weapon"].max()
    rms_current = float(np.sqrt(np.mean(df["I_bat"] ** 2)))
    wire_awg = get_wire_recommendation(rms_current)

    try:
        time_to_20 = df[df["v_kmh"] >= 20.0].iloc[0]["t"]
        time_to_20_str = f"{time_to_20:.2f}"
    except IndexError:
        time_to_20_str = "> симуляции"

    return {
        "peak_current": peak_current,
        "min_voltage": min_voltage,
        "temp_drive_max": temp_drive_max,
        "temp_weap_max": temp_weap_max,
        "wire_awg": wire_awg,
        "time_to_20": time_to_20_str,
    }


def generate_report(params: dict,
                    static_res: dict,
                    sim_stats: dict,
                    collision: dict) -> str:
    """Markdown‑паспорт для вкладки и скачивания."""
    date_str = params["date_str"]
    return f"""
# ТЕХНИЧЕСКИЙ ПАСПОРТ БОЕВОГО РОБОТА

**Проект:** {params['name']}  
**Дата расчета:** {date_str}

## 1. Общие характеристики
- Масса: **{static_res['total_mass']:.2f} кг**
- Макс. скорость: **{static_res['speed_kmh']:.1f} км/ч**
- Питание: **{params['voltage_s']}S LiPo ({static_res['voltage_nom']:.1f} В ном.)**

## 2. Динамика и энергетика
- Время разгона 0–20 км/ч: **{sim_stats['time_to_20']} с**
- Пиковый ток: **{sim_stats['peak_current']:.0f} А**
- Минимальное напряжение под нагрузкой: **{sim_stats['min_voltage']:.1f} В**
- Рекомендуемый силовой кабель: **{sim_stats['wire_awg']}**

## 3. Оружие (вертикальный спиннер)
- Энергия удара: **{collision['energy_joules']/1000:.1f} кДж**
- Эквивалент: *{collision['equivalent']}*
- Перегрузка своего шасси при ударе: **{collision['g_force_self']:.1f} G**
- Скорость отдачи робота: **{collision['recoil_speed_kmh']:.1f} км/ч**

## 4. Тепловой режим
- Макс. температура моторов хода: **{sim_stats['temp_drive_max']:.1f} °C**
- Макс. температура моторов оружия: **{sim_stats['temp_weap_max']:.1f} °C**

---
*Сгенерировано модулем цифрового двойника 1T Rex.*
"""
