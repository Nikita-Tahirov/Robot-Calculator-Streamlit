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
            # Ищем первое вхождение скорости >= 20
            reached = df_sim[df_sim["v_kmh"] >= 20.0]
            if not reached.empty:
                time_to_20 = reached.iloc[0]["t"]
            else:
                time_to_20 = 5.0 # Макс время симуляции
        except Exception:
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
    if df.empty:
        return {"optimal_value": 0, "best_idx": 0, "scores": df}

    df_norm = df.copy()
    
    # Вспомогательная функция для безопасной нормализации (0..1)
    def normalize(series, maximize=True):
        min_val = series.min()
        max_val = series.max()
        diff = max_val - min_val
        
        # Защита от деления на ноль (если все значения одинаковые)
        if diff == 0:
            return pd.Series([0.5] * len(series), index=series.index)
            
        if maximize:
            return (series - min_val) / diff
        else:
            return 1.0 - (series - min_val) / diff

    # Нормализуем метрики
    df_norm["speed_score"] = normalize(df["speed_kmh"], maximize=True)
    df_norm["energy_score"] = normalize(df["weapon_energy_kj"], maximize=True)
    df_norm["mass_score"] = normalize(df["total_mass"], maximize=False)
    df_norm["current_score"] = normalize(df["peak_current"], maximize=False)
    df_norm["time_score"] = normalize(df["time_to_20"], maximize=False)
    
    # Считаем общий балл с весами
    # fillna(0) защищает от NaN если что-то пошло не так
    df_norm["total_score"] = (
        df_norm["speed_score"].fillna(0) * 0.3 +
        df_norm["energy_score"].fillna(0) * 0.2 +
        df_norm["mass_score"].fillna(0) * 0.2 +
        df_norm["current_score"].fillna(0) * 0.15 +
        df_norm["time_score"].fillna(0) * 0.15
    )
    
    # Находим индекс лучшего значения
    best_idx = df_norm["total_score"].idxmax()
    
    # Защита: если idxmax вернул NaN (крайне редко)
    if pd.isna(best_idx):
        best_idx = df.index[0]
        
    optimal_value = df.loc[best_idx, "param_value"]
    
    return {
        "optimal_value": optimal_value,
        "best_idx": best_idx,
        "scores": df_norm
    }
