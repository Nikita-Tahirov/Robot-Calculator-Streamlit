"""
Модуль параметрического сканирования (Sensitivity Analysis).
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from physics import run_static_calculations, simulate_full_system, aggregate_sim_stats


SCANNABLE_PARAMS = {
    "gear_ratio": {
        "name": "Редукция хода",
        "default": 12.5,
        "range": (8.0, 20.0),
        "step": 0.5,
        "unit": ":1"
    },
    "wheel_dia_mm": {
        "name": "Диаметр колеса",
        "default": 200,
        "range": (150, 300),
        "step": 10,
        "unit": "мм"
    },
    "motor_kv": {
        "name": "KV моторов хода",
        "default": 190,
        "range": (100, 300),
        "step": 10,
        "unit": "об/В"
    },
    "weapon_mass_kg": {
        "name": "Масса ротора",
        "default": 28.0,
        "range": (15.0, 40.0),
        "step": 1.0,
        "unit": "кг"
    },
    "armor_thickness": {
        "name": "Толщина брони",
        "default": 5,
        "range": (2, 12),
        "step": 1,
        "unit": "мм"
    },
    "voltage_s": {
        "name": "Напряжение (S)",
        "default": 12,
        "range": (8, 14),
        "step": 1,
        "unit": "S"
    }
}


def run_parameter_scan(
    base_inputs: Dict,
    param_name: str,
    param_range: Tuple[float, float],
    num_points: int = 20
) -> pd.DataFrame:
    """
    Сканирование одного параметра по диапазону.
    Возвращает DataFrame с результатами.
    """
    min_val, max_val = param_range
    param_values = np.linspace(min_val, max_val, num_points)
    
    results = []
    
    for val in param_values:
        # Создаем копию входных данных
        inputs = base_inputs.copy()
        inputs[param_name] = val
        
        # Пересчитываем статику
        static_res = run_static_calculations(inputs)
        
        # Быстрая симуляция (меньше точек для скорости)
        sim_params = {
            "voltage_nom": static_res["voltage_nom"],
            "battery_ir_mohm": inputs["battery_ir_mohm"],
            "drive_motor_count": inputs["drive_motor_count"],
            "motor_kv": inputs["motor_kv"],
            "gear_ratio": inputs["gear_ratio"],
            "wheel_dia_mm": inputs["wheel_dia_mm"],
            "friction_coeff": inputs["friction_coeff"],
            "esc_current_limit_drive": inputs["esc_current_limit_drive"],
            "simulate_weapon": False,  # отключаем оружие для скорости
            "weapon_motor_count": inputs["weapon_motor_count"],
            "weapon_motor_kv": inputs["weapon_motor_kv"],
            "weapon_reduction": inputs["weapon_reduction"],
            "weapon_inertia": static_res["weapon_inertia"],
            "esc_current_limit_weapon": inputs["esc_current_limit_weapon"],
        }
        
        df_sim = simulate_full_system(sim_params, static_res["total_mass"], max_time=5.0)
        sim_stats = aggregate_sim_stats(df_sim)
        
        # Время разгона
        try:
            time_to_20 = df_sim[df_sim["v_kmh"] >= 20.0].iloc[0]["t"]
        except IndexError:
            time_to_20 = 5.0
        
        results.append({
            "param_value": val,
            "speed_kmh": static_res["speed_kmh"],
            "total_mass": static_res["total_mass"],
            "weapon_energy_kj": static_res["weapon_energy"] / 1000,
            "peak_current": sim_stats["peak_current"],
            "time_to_20": time_to_20,
            "temp_max": sim_stats["temp_drive_max"]
        })
    
    return pd.DataFrame(results)


def get_optimal_range(df: pd.DataFrame, param_name: str) -> Dict:
    """
    Анализ оптимального диапазона на основе результатов сканирования.
    """
    # Находим "золотую середину" по нескольким критериям
    # Нормализуем все метрики к [0, 1]
    
    df_norm = df.copy()
    
    # Больше = лучше
    df_norm["speed_score"] = (df["speed_kmh"] - df["speed_kmh"].min()) / (df["speed_kmh"].max() - df["speed_kmh"].min())
    df_norm["energy_score"] = (df["weapon_energy_kj"] - df["weapon_energy_kj"].min()) / (df["weapon_energy_kj"].max() - df["weapon_energy_kj"].min())
    
    # Меньше = лучше (инвертируем)
    df_norm["mass_score"] = 1 - (df["total_mass"] - df["total_mass"].min()) / (df["total_mass"].max() - df["total_mass"].min())
    df_norm["current_score"] = 1 - (df["peak_current"] - df["peak_current"].min()) / (df["peak_current"].max() - df["peak_current"].min())
    df_norm["time_score"] = 1 - (df["time_to_20"] - df["time_to_20"].min()) / (df["time_to_20"].max() - df["time_to_20"].min())
    
    # Общий балл (можно варьировать веса)
    df_norm["total_score"] = (
        df_norm["speed_score"] * 0.3 +
        df_norm["energy_score"] * 0.2 +
        df_norm["mass_score"] * 0.2 +
        df_norm["current_score"] * 0.15 +
        df_norm["time_score"] * 0.15
    )
    
    best_idx = df_norm["total_score"].idxmax()
    optimal_value = df.loc[best_idx, "param_value"]
    
    return {
        "optimal_value": optimal_value,
        "best_idx": best_idx,
        "scores": df_norm
    }
