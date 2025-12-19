"""
Модуль автоматической оптимизации параметров робота.
Использует scipy.optimize для поиска оптимальных конфигураций.
"""
import numpy as np
from scipy.optimize import differential_evolution, OptimizeResult
from typing import Dict, List, Tuple, Callable
from physics import run_static_calculations, simulate_full_system, aggregate_sim_stats, analyze_collision


class RobotOptimizer:
    """Оптимизатор параметров боевого робота."""
    
    def __init__(self, base_inputs: Dict):
        self.base_inputs = base_inputs.copy()
        self.optimization_history = []
        
    def objective_function(self, params: np.ndarray, goals: Dict, constraints: Dict) -> float:
        """
        Целевая функция для минимизации.
        Чем меньше значение, тем лучше конфигурация.
        """
        # Распаковка параметров
        gear_ratio, wheel_dia, motor_kv, weapon_mass, armor_thick = params
        
        # Обновление входных данных
        inputs = self.base_inputs.copy()
        inputs["gear_ratio"] = gear_ratio
        inputs["wheel_dia_mm"] = wheel_dia
        inputs["motor_kv"] = motor_kv
        inputs["weapon_mass_kg"] = weapon_mass
        inputs["armor_thickness"] = armor_thick
        
        try:
            # Расчет статики
            static_res = run_static_calculations(inputs)
            
            # Проверка жестких ограничений
            if static_res["total_mass"] > constraints["max_mass"]:
                return 1e6  # Штраф за перевес
            
            # Быстрая симуляция для оценки динамики
            sim_params = {
                "voltage_nom": static_res["voltage_nom"],
                "battery_ir_mohm": inputs["battery_ir_mohm"],
                "drive_motor_count": inputs["drive_motor_count"],
                "motor_kv": motor_kv,
                "gear_ratio": gear_ratio,
                "wheel_dia_mm": wheel_dia,
                "friction_coeff": inputs["friction_coeff"],
                "esc_current_limit_drive": inputs["esc_current_limit_drive"],
                "simulate_weapon": False,  # отключаем для скорости
                "weapon_motor_count": inputs["weapon_motor_count"],
                "weapon_motor_kv": inputs["weapon_motor_kv"],
                "weapon_reduction": inputs["weapon_reduction"],
                "weapon_inertia": static_res["weapon_inertia"],
                "esc_current_limit_weapon": inputs["esc_current_limit_weapon"],
            }
            
            df_sim = simulate_full_system(sim_params, static_res["total_mass"], max_time=4.0)
            sim_stats = aggregate_sim_stats(df_sim)
            
            collision = analyze_collision(
                static_res["total_mass"],
                static_res["weapon_inertia"],
                static_res["weapon_rpm"]
            )
            
            # Проверка мягких ограничений
            if sim_stats["peak_current"] > constraints["max_current"]:
                return 1e5  # Штраф за превышение тока
            
            # Расчет целевой функции (инвертированная полезность)
            score = 0.0
            
            # Максимизируем скорость (инвертируем для минимизации)
            if goals.get("maximize_speed", False):
                score -= static_res["speed_kmh"] * goals.get("speed_weight", 1.0)
            
            # Максимизируем энергию удара
            if goals.get("maximize_energy", False):
                score -= (static_res["weapon_energy"] / 1000) * goals.get("energy_weight", 1.0)
            
            # Минимизируем массу
            if goals.get("minimize_mass", False):
                score += static_res["total_mass"] * goals.get("mass_weight", 1.0)
            
            # Минимизируем ток
            if goals.get("minimize_current", False):
                score += sim_stats["peak_current"] * goals.get("current_weight", 0.1)
            
            # Минимизируем перегрузку
            if goals.get("minimize_gforce", False):
                score += collision["g_force_self"] * goals.get("gforce_weight", 1.0)
            
            # Сохранение истории
            self.optimization_history.append({
                "params": params.copy(),
                "score": score,
                "speed": static_res["speed_kmh"],
                "mass": static_res["total_mass"],
                "energy": static_res["weapon_energy"] / 1000,
                "current": sim_stats["peak_current"],
                "gforce": collision["g_force_self"]
            })
            
            return score
            
        except Exception as e:
            return 1e7  # Штраф за ошибку расчета
    
    def optimize(
        self,
        goals: Dict,
        constraints: Dict,
        bounds: List[Tuple[float, float]],
        max_iterations: int = 50
    ) -> OptimizeResult:
        """
        Запуск оптимизации.
        
        Args:
            goals: Цели оптимизации (maximize_speed, maximize_energy и т.д.)
            constraints: Ограничения (max_mass, max_current)
            bounds: Границы параметров [(min, max), ...]
            max_iterations: Максимальное количество итераций
        
        Returns:
            OptimizeResult: Результат оптимизации
        """
        self.optimization_history = []
        
        result = differential_evolution(
            func=lambda x: self.objective_function(x, goals, constraints),
            bounds=bounds,
            maxiter=max_iterations,
            popsize=10,
            tol=0.01,
            atol=0.001,
            seed=42,
            workers=1,
            updating='deferred',
            disp=False
        )
        
        return result
    
    def get_history(self) -> List[Dict]:
        """Получить историю оптимизации."""
        return self.optimization_history


def get_default_bounds() -> List[Tuple[float, float]]:
    """Дефолтные границы параметров для оптимизации."""
    return [
        (8.0, 20.0),    # gear_ratio
        (150, 300),     # wheel_dia_mm
        (100, 300),     # motor_kv
        (15.0, 40.0),   # weapon_mass_kg
        (2, 12)         # armor_thickness
    ]


def parse_optimized_params(result: OptimizeResult) -> Dict:
    """Парсинг результатов оптимизации."""
    params = result.x
    return {
        "gear_ratio": params[0],
        "wheel_dia_mm": int(params[1]),
        "motor_kv": int(params[2]),
        "weapon_mass_kg": params[3],
        "armor_thickness": int(params[4])
    }
