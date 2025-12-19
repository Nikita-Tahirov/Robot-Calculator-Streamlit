"""
Модуль сравнения конфигураций (Side-by-Side).
"""
import streamlit as st
from typing import Dict, Optional


def init_comparison_state():
    """Инициализация session state для сравнения."""
    if "saved_configs" not in st.session_state:
        st.session_state.saved_configs = []


def save_configuration(
    name: str,
    inputs: Dict,
    static_res: Dict,
    sim_stats: Dict,
    collision: Dict
) -> None:
    """Сохранение конфигурации в session state."""
    config = {
        "name": name,
        "timestamp": st.session_state.get("timestamp", "N/A"),
        # Входные параметры
        "inputs": inputs.copy(),
        # Результаты
        "speed_kmh": static_res["speed_kmh"],
        "total_mass": static_res["total_mass"],
        "weapon_energy_kj": static_res["weapon_energy"] / 1000,
        "peak_current": sim_stats["peak_current"],
        "min_voltage": sim_stats["min_voltage"],
        "temp_max_drive": sim_stats["temp_drive_max"],
        "temp_max_weapon": sim_stats["temp_weap_max"],
        "g_force_self": collision["g_force_self"],
        "time_to_20": sim_stats.get("time_to_20", "N/A"),
    }
    
    st.session_state.saved_configs.append(config)


def get_saved_configs():
    """Получить список сохраненных конфигураций."""
    return st.session_state.get("saved_configs", [])


def clear_saved_configs():
    """Очистить все сохраненные конфигурации."""
    st.session_state.saved_configs = []


def get_comparison_data(config_a: Dict, config_b: Dict) -> Dict:
    """
    Рассчитать разницу между двумя конфигурациями.
    Возвращает дельты (абсолютные и процентные).
    """
    metrics = [
        "speed_kmh", "total_mass", "weapon_energy_kj",
        "peak_current", "g_force_self"
    ]
    
    comparison = {}
    for metric in metrics:
        val_a = config_a.get(metric, 0)
        val_b = config_b.get(metric, 0)
        delta = val_b - val_a
        delta_pct = (delta / val_a * 100) if val_a != 0 else 0
        
        comparison[metric] = {
            "a": val_a,
            "b": val_b,
            "delta": delta,
            "delta_pct": delta_pct
        }
    
    return comparison
