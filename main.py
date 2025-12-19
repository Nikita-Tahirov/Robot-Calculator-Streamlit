import datetime
import streamlit as st

# ... (Импорты остаются те же)
from physics import (
    run_static_calculations,
    simulate_full_system,
    analyze_collision,
    aggregate_sim_stats,
    generate_report,
    run_monte_carlo_simulation, # Новый импорт
)
from styles import (
    setup_page,
    inject_global_css,
    render_kpi_row,
    render_weight_pie,
    render_drive_plot,
    render_thermal_plot,
    render_parameter_scan_plots,
    render_comparison_view,
    render_sidebar_preview,
    render_optimization_progress,
    render_monte_carlo_plot, # Новый импорт
)
from analysis import (
    SCANNABLE_PARAMS,
    run_parameter_scan,
    get_optimal_range,
)
from comparison import (
    init_comparison_state,
    save_configuration,
    get_saved_configs,
    clear_saved_configs,
    get_comparison_data,
)
from optimizer import (
    RobotOptimizer,
    get_default_bounds,
    parse_optimized_params,
)
from manual import show_manual
# Импорт базы данных компонентов
from library_data import MOTORS_DB, BATTERIES_DB

ROBOT_LIMIT_KG = 110.0

@st.cache_data(ttl=60)
def cached_static_calc(
    voltage_s, motor_kv, gear_ratio, wheel_dia_mm,
    weapon_mass_kg, weapon_radius_mm, armor_thickness, armor_coverage,
    _other_params_hash
):
    inputs = st.session_state.get("full_inputs", {})
    if not inputs:
        return None
    return run_static_calculations(inputs)


def build_sidebar():
    st.sidebar.title("🦖 1T Rex – Конфигуратор")

    # 1. Энергосистема с выбором АКБ
    st.sidebar.header("1. Энергосистема")
    name = st.sidebar.text_input("Название проекта", value="1T Rex")
    voltage_s = st.sidebar.slider("Аккумулятор (S)", 6, 14, 12)
    
    # --- Выбор Батареи ---
    battery_options = list(BATTERIES_DB.keys())
    selected_battery = st.sidebar.selectbox("Тип ячеек АКБ", battery_options, index=0)
    
    # Логика подстановки значений АКБ
    batt_data = BATTERIES_DB[selected_battery]
    if selected_battery != "Custom (Своя сборка)":
        # Примерный расчет сопротивления сборки: (IR ячейки / кол-во параллель) * кол-во послед
        # Допустим, у нас 12S4P конфиг для хэвивейта (стандарт)
        cells_p = 4 
        calc_ir = (batt_data["cell_ir"] / cells_p) * voltage_s * 1.5 # 1.5 - коэф на провода/сварку
        ir_value = float(calc_ir)
        ir_disabled = True
        st.sidebar.caption(f"ℹ️ {batt_data['desc']} (Расчет для 12S{cells_p}P)")
    else:
        ir_value = 25.0
        ir_disabled = False
    
    battery_ir_mohm = st.sidebar.number_input(
        "Внутреннее сопротивление сборки (мОм)", 
        value=ir_value, 
        disabled=ir_disabled
    )

    # 2. Ходовая с выбором мотора
    st.sidebar.header("2. Ходовая часть")
    drive_motor_count = st.sidebar.selectbox("Кол-во моторов хода", [2, 4], index=1)
    
    # --- Выбор Мотора ---
    motor_options = list(MOTORS_DB.keys())
    selected_motor = st.sidebar.selectbox("Модель мотора", motor_options, index=0)
    
    motor_data = MOTORS_DB[selected_motor]
    if selected_motor != "Custom (Свой)":
        kv_value = int(motor_data["kv"])
        kv_disabled = True
        # Масса мотора тоже могла бы подставляться, но у нас в базе пока только KV для инпутов
        # (в идеале нужно обновлять и массу компонентов, но пока ограничимся KV)
        st.sidebar.caption(f"ℹ️ {motor_data['desc']}")
    else:
        kv_value = 190
        kv_disabled = False
        
    motor_kv = st.sidebar.number_input("KV моторов хода", value=kv_value, disabled=kv_disabled)
    
    gear_ratio = st.sidebar.number_input("Редукция хода", value=12.5, step=0.1)
    wheel_dia_mm = st.sidebar.number_input("Диаметр колеса (мм)", value=200, step=5)
    esc_current_limit_drive = st.sidebar.slider(
        "Лимит тока ESC (ход), А", 20, 150, 60
    )
    friction_coeff = st.sidebar.slider("Коэф. трения (покрытие/колеса)", 0.3, 1.0, 0.7, step=0.05)

    # 3. Оружие
    st.sidebar.header("3. Оружие")
    simulate_weapon = st.sidebar.checkbox("Симулировать работу оружия", value=True)
    weapon_motor_count = st.sidebar.selectbox("Кол-во моторов оружия", [1, 2], index=1)
    weapon_motor_kv = st.sidebar.number_input("KV моторов оружия", value=150)
    weapon_reduction = st.sidebar.number_input("Редукция оружия", value=1.5, step=0.1)
    weapon_mass_kg = st.sidebar.number_input("Масса ротора (кг)", value=28.0, step=0.5)
    weapon_radius_mm = st.sidebar.number_input("Радиус удара (мм)", value=180, step=5)
    esc_current_limit_weapon = st.sidebar.slider(
        "Лимит тока ESC (оружие), А", 50, 300, 120
    )

    # 4. Вес и броня
    st.sidebar.header("4. Броня и масса")
    armor_thickness = st.sidebar.slider("Толщина брони (мм)", 2, 10, 5)
    armor_coverage = st.sidebar.slider("Покрытие броней (%)", 10, 100, 35, step=5)

    # Базовые массы (можно доработать, чтобы брались из базы моторов)
    base_drive_mass = 18.0 
    # Если выбран реальный мотор, можно скорректировать массу (упрощенно)
    if selected_motor != "Custom (Свой)":
        # 4 мотора * масса одного + колеса и редукторы
        base_drive_mass = (drive_motor_count * motor_data["mass_kg"]) + 10.0 
    
    base_elec_mass = 12.0
    base_frame_mass = 25.0
    armor_density_kg_m3 = 2700.0
    armor_area_total = 3.0

    inputs = {
        "name": name,
        "voltage_s": voltage_s,
        "battery_ir_mohm": battery_ir_mohm,
        "drive_motor_count": drive_motor_count,
        "motor_kv": motor_kv,
        "gear_ratio": gear_ratio,
        "wheel_dia_mm": wheel_dia_mm,
        "esc_current_limit_drive": esc_current_limit_drive,
        "friction_coeff": friction_coeff,
        "simulate_weapon": simulate_weapon,
        "weapon_motor_count": weapon_motor_count,
        "weapon_motor_kv": weapon_motor_kv,
        "weapon_reduction": weapon_reduction,
        "weapon_mass_kg": weapon_mass_kg,
        "weapon_radius_mm": weapon_radius_mm,
        "esc_current_limit_weapon": esc_current_limit_weapon,
        "armor_thickness": armor_thickness,
        "armor_coverage": armor_coverage,
        "base_drive_mass": base_drive_mass,
        "base_elec_mass": base_elec_mass,
        "base_frame_mass": base_frame_mass,
        "armor_density_kg_m3": armor_density_kg_m3,
        "armor_area_total": armor_area_total,
    }
    
    st.session_state["full_inputs"] = inputs

    return inputs, base_drive_mass, base_elec_mass, base_frame_mass


def main():
    setup_page()
    inject_global_css()
    init_comparison_state()

    if "first_visit" not in st.session_state:
        st.session_state.first_visit = True

    inputs, base_drive_mass, base_elec_mass, base_frame_mass = build_sidebar()

    # --------- Расчеты ---------
    other_params = f"{inputs['battery_ir_mohm']}_{inputs['drive_motor_count']}"
    static_res = cached_static_calc(
        inputs["voltage_s"], inputs["motor_kv"], inputs["gear_ratio"],
        inputs["wheel_dia_mm"], inputs["weapon_mass_kg"], inputs["weapon_radius_mm"],
        inputs["armor_thickness"], inputs["armor_coverage"],
        other_params
    )
    
    if static_res is None:
        static_res = run_static_calculations(inputs)

    sim_params = {
        "voltage_nom": static_res["voltage_nom"],
        "battery_ir_mohm": inputs["battery_ir_mohm"],
        "drive_motor_count": inputs["drive_motor_count"],
        "motor_kv": inputs["motor_kv"],
        "gear_ratio": inputs["gear_ratio"],
        "wheel_dia_mm": inputs["wheel_dia_mm"],
        "friction_coeff": inputs["friction_coeff"],
        "esc_current_limit_drive": inputs["esc_current_limit_drive"],
        "simulate_weapon": inputs["simulate_weapon"],
        "weapon_motor_count": inputs["weapon_motor_count"],
        "weapon_motor_kv": inputs["weapon_motor_kv"],
        "weapon_reduction": inputs["weapon_reduction"],
        "weapon_inertia": static_res["weapon_inertia"],
        "esc_current_limit_weapon": inputs["esc_current_limit_weapon"],
    }

    df_sim = simulate_full_system(sim_params, static_res["total_mass"], max_time=8.0)
    sim_stats = aggregate_sim_stats(df_sim)
    
    collision = analyze_collision(
        static_res["total_mass"],
        static_res["weapon_inertia"],
        static_res["weapon_rpm"],
        target_mass=110.0,
    )

    render_sidebar_preview(static_res, sim_stats)
    st.sidebar.markdown("---")
    if st.sidebar.button("📘 Руководство", type="secondary"):
        show_manual()

    params_for_report = {
        "name": inputs["name"],
        "voltage_s": inputs["voltage_s"],
        "voltage_nom": static_res["voltage_nom"],
        "date_str": datetime.datetime.now().strftime("%d.%m.%Y"),
    }

    report_md = generate_report(params_for_report, static_res, sim_stats, collision)

    # --------- UI ---------
    st.title(f"Digital Twin: {inputs['name']}")

    col_save, col_clear = st.columns([3, 1])
    with col_save:
        if st.button("💾 Сохранить конфигурацию"):
            save_configuration(inputs["name"], inputs, static_res, sim_stats, collision)
            st.success(f"Конфигурация '{inputs['name']}' сохранена")
    with col_clear:
        if st.button("🗑️ Очистить"):
            clear_saved_configs()
            st.rerun()

    tabs = st.tabs([
        "📊 Сводка",
        "⏱ Динамика",
        "🔥 Тепло",
        "💥 Столкновение",
        "🎲 Вероятность", # Новая вкладка
        "🔬 Анализ",
        "⚖️ Сравнение",
        "🤖 Оптимизатор",
        "📑 Паспорт"
    ])

    with tabs[0]:
        render_kpi_row(static_res, sim_stats, ROBOT_LIMIT_KG)
        st.markdown("---")
        render_weight_pie(static_res, base_drive_mass, base_elec_mass, base_frame_mass)

    with tabs[1]:
        st.subheader("Разгон и нагрузка на батарею")
        render_drive_plot(df_sim)

    with tabs[2]:
        st.subheader("Тепловой режим моторов")
        render_thermal_plot(df_sim)

    with tabs[3]:
        st.subheader("Столкновение")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Энергия", f"{collision['energy_joules']/1000:.1f} кДж")
            st.metric("Сила", f"{collision['impact_force_kn']:.1f} кН")
        with col2:
            st.metric("G-force (свой)", f"{collision['g_force_self']:.1f} G")
            st.metric("G-force (цель)", f"{collision['g_force_target']:.1f} G")

    # НОВАЯ ВКЛАДКА: Вероятность (Монте-Карло)
    with tabs[4]:
        st.header("🎲 Анализ неопределенности (Monte Carlo)")
        st.markdown("""
        Реальные параметры робота всегда отличаются от идеальных. Трение меняется, 
        моторы имеют разброс KV, батареи разряжаются по-разному.
        Этот модуль запускает **100 симуляций** с небольшими случайными отклонениями, 
        чтобы показать реальный диапазон характеристик.
        """)
        
        mc_col1, mc_col2 = st.columns(2)
        with mc_col1:
            mc_variation = st.slider("Разброс параметров (±%)", 5, 20, 10, 5)
        with mc_col2:
            mc_iters = st.slider("Количество симуляций", 50, 500, 100, 50)
            
        if st.button("🎲 Запустить Монте-Карло"):
            with st.spinner(f"Выполняем {mc_iters} симуляций..."):
                df_mc = run_monte_carlo_simulation(
                    inputs, 
                    static_res, 
                    variation_pct=mc_variation/100.0, 
                    iterations=mc_iters
                )
                
                st.subheader("Результаты анализа")
                
                # График 1: Ток
                mean_curr, std_curr = render_monte_carlo_plot(
                    df_mc, "peak_current", "Распределение пикового тока", "А"
                )
                st.info(f"Средний ток: **{mean_curr:.1f} А**. С вероятностью 95% он будет в диапазоне **{mean_curr-2*std_curr:.0f} ... {mean_curr+2*std_curr:.0f} А**.")
                
                st.markdown("---")
                
                # График 2: Скорость
                mean_spd, std_spd = render_monte_carlo_plot(
                    df_mc, "max_speed", "Распределение максимальной скорости", "км/ч"
                )
                st.info(f"Средняя скорость: **{mean_spd:.1f} км/ч**. Доверительный интервал: **{mean_spd-2*std_spd:.1f} ... {mean_spd+2*std_spd:.1f} км/ч**.")

    with tabs[5]:
        st.header("🔬 Параметрическое сканирование")
        col_param, col_range = st.columns([2, 2])
        with col_param:
            selected_param = st.selectbox("Параметр", list(SCANNABLE_PARAMS.keys()), format_func=lambda x: SCANNABLE_PARAMS[x]["name"])
        param_info = SCANNABLE_PARAMS[selected_param]
        with col_range:
            st.write(f"Диапазон: {param_info['range'][0]} – {param_info['range'][1]} {param_info['unit']}")
            num_points = st.slider("Точки", 10, 30, 15)
        
        if st.button("▶️ Запустить сканирование"):
            with st.spinner("Анализ..."):
                df_scan = run_parameter_scan(inputs, selected_param, param_info["range"], num_points)
                st.session_state["scan_result"] = df_scan
                st.session_state["scan_param"] = selected_param
        
        if "scan_result" in st.session_state:
            df_scan = st.session_state["scan_result"]
            scan_param = st.session_state["scan_param"]
            param_info = SCANNABLE_PARAMS[scan_param]
            render_parameter_scan_plots(df_scan, param_info["name"], param_info["unit"])
            optimal = get_optimal_range(df_scan, scan_param)
            st.success(f"Рекомендуемое: {optimal['optimal_value']:.2f} {param_info['unit']}")

    with tabs[6]:
        st.header("⚖️ Сравнение")
        saved_configs = get_saved_configs()
        if len(saved_configs) < 1:
            st.info("Сохраните конфигурацию для сравнения.")
        else:
            col_sel_a, col_sel_b = st.columns(2)
            with col_sel_a: config_a_name = st.selectbox("Конфиг A", [c["name"] for c in saved_configs], key="cfg_a")
            with col_sel_b: use_live = st.checkbox("Текущий (LIVE)", True)
            
            config_a = next((c for c in saved_configs if c["name"] == config_a_name), None)
            if use_live:
                config_b = {
                    "name": "⚡ LIVE", 
                    "speed_kmh": static_res["speed_kmh"], 
                    "total_mass": static_res["total_mass"],
                    "weapon_energy_kj": static_res["weapon_energy"]/1000,
                    "peak_current": sim_stats["peak_current"],
                    "g_force_self": collision["g_force_self"]
                }
            else:
                config_b_name = st.selectbox("Конфиг B", [c["name"] for c in saved_configs if c["name"] != config_a_name], key="cfg_b")
                config_b = next((c for c in saved_configs if c["name"] == config_b_name), None)
            
            if config_a and config_b:
                comparison = get_comparison_data(config_a, config_b)
                render_comparison_view(config_a, config_b, comparison)

    with tabs[7]:
        st.header("🤖 Оптимизатор")
        col_g, col_c = st.columns(2)
        with col_g:
            max_spd = st.checkbox("Макс. скорость", True)
            max_en = st.checkbox("Макс. энергия", True)
        with col_c:
            lim_mass = st.number_input("Макс. масса", 110.0)
            lim_curr = st.number_input("Макс. ток", 500.0)
        
        if st.button("🚀 Запустить"):
            with st.spinner("Оптимизация..."):
                optimizer = RobotOptimizer(inputs)
                goals = {"maximize_speed": max_spd, "maximize_energy": max_en, "speed_weight": 1.0, "energy_weight": 1.0}
                res = optimizer.optimize(goals, {"max_mass": lim_mass, "max_current": lim_curr}, get_default_bounds())
                opt_params = parse_optimized_params(res)
                st.success("Готово!")
                st.write(opt_params)
                if st.button("Применить"):
                    for k, v in opt_params.items(): st.session_state[k] = v
                    st.rerun()

    with tabs[8]:
        st.subheader("Паспорт")
        st.download_button("Скачать .md", report_md, "robot.md")
        st.markdown(report_md)

    if st.session_state.first_visit:
        show_manual()
        st.session_state.first_visit = False

if __name__ == "__main__":
    main()
