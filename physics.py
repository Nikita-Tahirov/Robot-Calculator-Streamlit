# physics.py
import numpy as np
import pandas as pd

class RobotPhysics:
    def __init__(self, mass, voltage, motor_kv, gear_ratio, wheel_diam_mm, resistance_mohm):
        self.mass = mass  # кг
        self.voltage = voltage  # В
        self.kv = motor_kv  # об/В
        self.gear = gear_ratio  # X:1
        self.wheel_radius = (wheel_diam_mm / 1000) / 2  # метры
        self.battery_r = resistance_mohm / 1000  # Ом
        
        # Константы
        self.g = 9.81
        self.motor_r_internal = 0.05  # Ом (усредненно для мощных BLDC)
        self.kt = 9.55 / self.kv  # Коэффициент момента
    
    def calculate_static_specs(self):
        """Базовые статические характеристики"""
        max_rpm_motor = self.voltage * self.kv
        max_rpm_wheel = max_rpm_motor / self.gear
        max_speed_ms = max_rpm_wheel * (2 * np.pi * self.wheel_radius) / 60
        max_speed_kmh = max_speed_ms * 3.6
        
        stall_current = self.voltage / self.motor_r_internal
        stall_torque_motor = stall_current * self.kt
        stall_torque_wheel = stall_torque_motor * self.gear
        max_force = stall_torque_wheel / self.wheel_radius
        
        return {
            "speed_kmh": max_speed_kmh,
            "force_n": max_force,
            "push_ratio": max_force / (self.mass * self.g)  # Коэффициент тяги к весу
        }

    def run_time_domain_simulation(self, duration=3.0, dt=0.05):
        """Симуляция разгона во времени (Time-Domain)"""
        t_values = np.arange(0, duration, dt)
        
        v = 0  # скорость, м/с
        x = 0  # дистанция, м
        results = []
        
        for t in t_values:
            # 1. Back EMF (Противо-ЭДС)
            rpm_wheel = (v * 60) / (2 * np.pi * self.wheel_radius)
            rpm_motor = rpm_wheel * self.gear
            back_emf = rpm_motor / self.kv
            
            # 2. Ток с учетом просадки напряжения батареи
            # U_eff = U_batt - I * R_batt
            # I = (U_batt - BackEMF) / (R_motor + R_batt)
            current = max(0, (self.voltage - back_emf) / (self.motor_r_internal + self.battery_r))
            
            # 3. Момент и сила
            torque_motor = current * self.kt
            torque_wheel = torque_motor * self.gear * 0.9  # 0.9 КПД трансмиссии
            force = torque_wheel / self.wheel_radius
            
            # 4. Аэродинамика и трение
            drag = 0.5 * 1.22 * 0.4 * (0.3 * 0.3) * v**2  # Примерная аэродинамика
            friction = self.mass * self.g * 0.02 # Трение качения
            
            net_force = force - drag - friction
            accel = net_force / self.mass
            
            # 5. Интеграция
            v += accel * dt
            x += v * dt
            
            results.append({
                "time": t,
                "speed_kmh": v * 3.6,
                "current": current,
                "accel": accel,
                "distance": x
            })
            
        return pd.DataFrame(results)

    def impact_analysis(self, impact_speed_kmh, deformation_mm):
        """Расчет перегрузок при ударе (G-force)"""
        v_ms = impact_speed_kmh / 3.6
        s_m = deformation_mm / 1000
        
        # a = v^2 / 2s
        if s_m <= 0: return 0, 0
        
        accel_ms2 = (v_ms**2) / (2 * s_m)
        g_force = accel_ms2 / 9.81
        impact_energy = 0.5 * self.mass * v_ms**2
        
        return {
            "g_force": g_force,
            "energy_joules": impact_energy,
            "impact_speed_ms": v_ms
        }
