import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

# Константы
G = 9.81  # ускорение свободного падения, м/с^2

def run_static_calculations(inputs: Dict) -> Dict:
    """
    Выполняет статические расчеты параметров робота.
    """
    # 1. Напряжение
    voltage_nom = inputs["voltage_s"] * 3.7  # номинал LiPo/LiIon
    
    # 2. Скорость (теоретическая холостая)
    # RPM = KV * V
    motor_rpm_no_load = inputs["motor_kv"] * voltage_nom
    # RPM колеса = RPM мотора / редукцию
    wheel_rpm = motor_rpm_no_load / inputs["gear_ratio"]
    # Скорость = (RPM * pi * D) / 60
    # D в метрах = mm / 1000
    wheel_circ_m = np.pi * (inputs["wheel_dia_mm"] / 1000.0)
    speed_mps = (wheel_rpm * wheel_circ_m) / 60.0
    speed_kmh = speed_mps * 3.6
    
    # 3. Масса брони
    # Объем = площадь * толщина
    # В реальности площадь брони зависит от размеров робота, 
    # здесь упрощенно берем "armor_area_total" как параметр (кв.м), 
    # который масштабируется от "coverage"
    effective_area = inputs["armor_area_total"] * (inputs["armor_coverage"] / 100.0)
    armor_vol_m3 = effective_area * (inputs["armor_thickness"] / 1000.0)
    armor_mass = armor_vol_m3 * inputs["armor_density_kg_m3"]
    
    # 4. Общая масса
    # Сумма: ходовая + электроника + рама + броня + оружие
    # (в base_drive_mass уже включены моторы и колеса упрощенно)
    total_mass = (
        inputs["base_drive_mass"] +
        inputs["base_elec_mass"] +
        inputs["base_frame_mass"] +
        armor_mass +
        inputs["weapon_mass_kg"] # масса ротора/оружия
    )
    
    # 5. Оружие
    weapon_rpm = 0.0
    weapon_energy = 0.0
    weapon_tip_speed = 0.0
    weapon_inertia = 0.0
    
    if inputs["simulate_weapon"]:
        weapon_rpm = (inputs["weapon_motor_kv"] * voltage_nom) / inputs["weapon_reduction"]
        # Момент инерции кольца/диска: I = 0.5 * m * r^2
        r_m = inputs["weapon_radius_mm"] / 1000.0
        weapon_inertia = 0.5 * inputs["weapon_mass_kg"] * (r_m ** 2)
        # Кинетическая энергия: E = 0.5 * I * w^2, где w - рад/с
        w_rad_s = weapon_rpm * 2 * np.pi / 60.0
        weapon_energy = 0.5 * weapon_inertia * (w_rad_s ** 2)
        weapon_tip_speed = w_rad_s * r_m * 3.6 # км/ч

    return {
        "voltage_nom": voltage_nom,
        "speed_kmh": speed_kmh,
        "armor_mass": armor_mass,
        "total_mass": total_mass,
        "weapon_rpm": weapon_rpm,
        "weapon_energy": weapon_energy, # Дж
        "weapon_tip_speed": weapon_tip_speed,
        "weapon_inertia": weapon_inertia
    }


def simulate_full_system(params: Dict, total_mass_kg: float, max_time: float = 8.0) -> pd.DataFrame:
    """
    Симуляция разгона во времени с учетом тока и нагрева.
    """
    dt = 0.05  # шаг времени, с
    t_values = np.arange(0, max_time, dt)
    
    # Состояние
    v = 0.0  # скорость, м/с
    dist = 0.0 # дистанция
    temp_drive = 25.0 # температура моторов, С
    temp_weap = 25.0
    
    # Параметры ходовой
    U = params["voltage_nom"]
    R_bat = params["battery_ir_mohm"] / 1000.0 # Ом
    
    # Ход
    kv_drive = params["motor_kv"]
    kt_drive = 9.55 / kv_drive if kv_drive > 0 else 0 # Kt approx
    R_phase_drive = 0.05 # Упрощенно 50 мОм фазное
    gear_drive = params["gear_ratio"]
    r_wheel = (params["wheel_dia_mm"] / 1000.0) / 2.0
    n_motors_drive = params["drive_motor_count"]
    limit_drive = params["esc_current_limit_drive"]
    mu = params["friction_coeff"]
    
    results = []
    
    for t in t_values:
        # --- Ходовая ---
        # Back EMF = Kw * w_motor
        w_wheel = v / r_wheel # рад/с
        w_motor = w_wheel * gear_drive
        rpm_motor = w_motor * 60 / (2*np.pi)
        
        back_emf = rpm_motor / kv_drive
        
        # Ток двигателя (I = (U - E) / R)
        # Упрощенная модель DC-двигателя
        # Напряжение на моторе падает из-за просадки батареи: U_mot = U_bat - I_total * R_bat
        # Решаем итеративно или берем с прошлого шага (проще)
        
        # Максимально возможный ток при текущей скорости (Back EMF)
        if U > back_emf:
            # I = (U - E) / R_total_circuit
            i_drive_raw = (U - back_emf) / R_phase_drive
        else:
            i_drive_raw = 0.0
            
        # Лимит ESC (на один мотор)
        i_drive_limited = min(i_drive_raw, limit_drive)
        
        # Полный ток ходовой
        i_drive_total = i_drive_limited * n_motors_drive
        
        # Сила тяги: F = (I * Kt * Gear * Efficiency) / r_wheel
        # Efficiency ~ 80%
        torque_motor = i_drive_limited * kt_drive
        torque_wheel = torque_motor * gear_drive * 0.8
        force_propulsion = (torque_wheel * n_motors_drive) / r_wheel
        
        # Сила трения (ограничение тяги сцеплением)
        # F_max = mu * m * g
        force_friction_limit = mu * total_mass_kg * G
        
        # Реальная сила (не больше трения)
        force_real = min(force_propulsion, force_friction_limit)
        
        # Аэродинамика + трение качения (упрощенно)
        force_drag = 0.5 * 1.2 * 0.5 * (v**2) + (0.02 * total_mass_kg * G)
        
        # Ускорение
        accel = (force_real - force_drag) / total_mass_kg
        if accel < 0 and v < 0.1: accel = 0 # Стоим
            
        v += accel * dt
        dist += v * dt
        
        # --- Оружие (упрощенно, раскрутка) ---
        i_weap_total = 0.0
        if params["simulate_weapon"]:
            # Аналогично ходовой, раскрутка инерционной массы
            # Тут просто профиль тока: макс ток пока не раскрутится
            # Предположим раскрутку за 3 сек
            if t < 3.0:
                i_weap_total = params["esc_current_limit_weapon"] * params["weapon_motor_count"]
            else:
                i_weap_total = 10.0 # поддержание
                
        # --- Батарея и Тепло ---
        i_bat_total = i_drive_total + i_weap_total
        
        # Просадка напряжения
        u_sag = i_bat_total * R_bat
        u_actual = U - u_sag
        
        # Нагрев (I^2 * R * dt / HeatCapacity)
        # HeatCapacity мотора ~ 500 Дж/К (грубо для 500г мотора)
        heat_cap = 500.0 
        
        # Тепло ходовой (на 1 мотор)
        power_heat_drive = (i_drive_limited**2) * R_phase_drive
        d_temp_drive = (power_heat_drive * dt) / heat_cap
        # Остывание (Ньютон)
        d_temp_drive -= (temp_drive - 25.0) * 0.05 * dt
        temp_drive += d_temp_drive
        
        # Тепло оружия
        if params["simulate_weapon"]:
            i_weap_single = i_weap_total / params["weapon_motor_count"]
            power_heat_weap = (i_weap_single**2) * R_phase_drive
            temp_weap += ((power_heat_weap * dt) / heat_cap) - ((temp_weap - 25.0) * 0.05 * dt)
        
        results.append({
            "t": t,
            "v_kmh": v * 3.6,
            "dist": dist,
            "I_bat": i_bat_total,
            "U_bat": u_actual,
            "T_drive": temp_drive,
            "T_weapon": temp_weap
        })
        
    return pd.DataFrame(results)


def aggregate_sim_stats(df: pd.DataFrame) -> Dict:
    """
    Считает итоговые метрики по симуляции.
    """
    peak_current = df["I_bat"].max()
    min_voltage = df["U_bat"].min()
    temp_drive_max = df["T_drive"].max()
    temp_weap_max = df["T_weapon"].max()
    
    # Подбор сечения провода по току (табличное)
    # < 50A -> 12AWG, < 80A -> 10AWG, < 150A -> 8AWG, else 6AWG
    if peak_current < 50: awg = "12 AWG"
    elif peak_current < 80: awg = "10 AWG"
    elif peak_current < 150: awg = "8 AWG"
    else: awg = "6 AWG (или шина)"
    
    return {
        "peak_current": peak_current,
        "min_voltage": min_voltage,
        "temp_drive_max": temp_drive_max,
        "temp_weap_max": temp_weap_max,
        "wire_awg": awg
    }


def analyze_collision(
    robot_mass: float, 
    weapon_inertia: float, 
    weapon_rpm: float, 
    target_mass: float = 110.0
) -> Dict:
    """
    Расчет параметров удара (абсолютно неупругое столкновение для оценки пиков).
    """
    # Энергия ротора
    w = weapon_rpm * 2 * np.pi / 60
    energy = 0.5 * weapon_inertia * (w**2)
    
    # Импульс удара (оценка)
    # Предположим передачу 30% энергии в кинетическую энергию разлета роботов
    # и длительность удара 0.05 с
    impact_duration = 0.02 # 20 мс
    
    # Переданная энергия
    transferred_energy = energy * 0.3
    
    # Сила удара (F * d = E -> F = E/d ?) нет, F*t = mv
    # Оценим через импульс. J = sqrt(2 * m_reduced * E_transferred)
    # m_reduced = (m1*m2)/(m1+m2)
    m_red = (robot_mass * target_mass) / (robot_mass + target_mass)
    impulse = np.sqrt(2 * m_red * transferred_energy)
    
    avg_force = impulse / impact_duration # Ньютон
    
    # Перегрузка (G)
    accel_self = avg_force / robot_mass
    g_force_self = accel_self / G
    
    accel_target = avg_force / target_mass
    g_force_target = accel_target / G
    
    # Скорость отскока
    v_recoil = impulse / robot_mass
    
    # Эквивалент (автомобиль 1.5т на скорости X)
    # E_car = 0.5 * 1500 * v^2 = energy
    # v = sqrt(2*E / 1500)
    v_car_mps = np.sqrt(2 * energy / 1500.0)
    v_car_kmh = v_car_mps * 3.6
    
    return {
        "energy_joules": energy,
        "impact_force_kn": avg_force / 1000.0,
        "g_force_self": g_force_self,
        "g_force_target": g_force_target,
        "recoil_speed_kmh": v_recoil * 3.6,
        "equivalent": f"Авто (1.5т) на {v_car_kmh:.1f} км/ч"
    }


def generate_report(params: Dict, static: Dict, sim: Dict, col: Dict) -> str:
    """
    Генерация Markdown отчета.
    """
    return f"""
# Паспорт проекта: {params['name']}
Дата расчета: {params['date_str']}

## 1. Основные характеристики
* **Напряжение системы:** {params['voltage_s']}S ({params['voltage_nom']:.1f} В)
* **Общая масса:** {static['total_mass']:.2f} кг
* **Максимальная скорость:** {static['speed_kmh']:.1f} км/ч
* **Энергия оружия:** {static['weapon_energy']/1000:.1f} кДж

## 2. Электрика и Привод
* **Пиковый ток батареи:** {sim['peak_current']:.1f} А
* **Просадка напряжения:** до {sim['min_voltage']:.1f} В
* **Рекомендуемая проводка:** {sim['wire_awg']}
* **Нагрев моторов (пик):** {sim['temp_drive_max']:.1f} °C

## 3. Боевая эффективность
* **Сила удара:** {col['impact_force_kn']:.1f} кН
* **Перегрузка при ударе:** {col['g_force_self']:.1f} G
* **Скорость отскока:** {col['recoil_speed_kmh']:.1f} км/ч

---
*Сгенерировано в Digital Twin 1T Rex*
"""

def run_monte_carlo_simulation(
    base_inputs: Dict,
    static_res: Dict,
    variation_pct: float = 0.10,  # 10% разброс (3 сигма)
    iterations: int = 100
) -> pd.DataFrame:
    """
    Вероятностное моделирование (Monte Carlo).
    Варьирует ключевые параметры: KV, трение, напряжение, сопротивление.
    """
    results = []
    
    # Генераторы случайных чисел (нормальное распределение)
    # variation_pct считается как "3 сигма" (99.7% значений попадают в этот диапазон)
    sigma_scale = variation_pct / 3.0
    
    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
    
    for i in range(iterations):
        # Варьируем параметры
        # 1. KV моторов (производственный разброс)
        kv_factor = rng.normal(1.0, sigma_scale)
        sim_kv = base_inputs["motor_kv"] * kv_factor
        
        # 2. Трение (сильно зависит от покрытия)
        friction_factor = rng.normal(1.0, sigma_scale * 1.5) # Трение варьируется сильнее
        sim_friction = max(0.1, min(1.5, base_inputs["friction_coeff"] * friction_factor))
        
        # 3. Сопротивление батареи (температура, заряд)
        ir_factor = rng.normal(1.0, sigma_scale)
        sim_ir = base_inputs["battery_ir_mohm"] * ir_factor
        
        # Собираем параметры для симуляции
        sim_params = {
            "voltage_nom": static_res["voltage_nom"], # Напряжение считаем номинальным, но IR "гуляет"
            "battery_ir_mohm": sim_ir,
            "drive_motor_count": base_inputs["drive_motor_count"],
            "motor_kv": sim_kv,
            "gear_ratio": base_inputs["gear_ratio"],
            "wheel_dia_mm": base_inputs["wheel_dia_mm"],
            "friction_coeff": sim_friction,
            "esc_current_limit_drive": base_inputs["esc_current_limit_drive"],
            "simulate_weapon": False, # Для ускорения отключаем оружие в Монте-Карло
            "weapon_motor_count": 0,
            "weapon_motor_kv": 0,
            "weapon_reduction": 1,
            "weapon_inertia": 0,
            "esc_current_limit_weapon": 0,
        }
        
        # Запускаем короткую симуляцию (до 4 сек достаточно для разгона)
        df_sim = simulate_full_system(sim_params, static_res["total_mass"], max_time=4.0)
        
        # Агрегируем результаты
        peak_current = df_sim["I_bat"].max()
        max_speed = df_sim["v_kmh"].max()
        
        # Время до 20 км/ч
        try:
            time_to_20 = df_sim[df_sim["v_kmh"] >= 20.0].iloc[0]["t"]
        except IndexError:
            time_to_20 = 4.0 # Не достиг
            
        results.append({
            "iteration": i,
            "kv_used": sim_kv,
            "friction_used": sim_friction,
            "peak_current": peak_current,
            "max_speed": max_speed,
            "time_to_20": time_to_20
        })
        
    return pd.DataFrame(results)
