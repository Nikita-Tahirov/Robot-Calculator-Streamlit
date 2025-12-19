import datetime
import streamlit as st

from physics import (
    run_static_calculations,
    simulate_full_system,
    analyze_collision,
    aggregate_sim_stats,
    generate_report,
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

ROBOT_LIMIT_KG = 110.0


# Кэширование для ускорения Live Preview (только статические расчеты)
@st.cache_data(ttl=60)
def cached_static_calc(
    voltage_s, motor_kv, gear_ratio, wheel_dia_mm,
    weapon_mass_kg, weapon_radius_mm, armor_thickness, armor_coverage,
    _other_params_hash  # Остальные параметры в виде хэша
):
    """Кэшированная версия статических расчетов для Live Preview."""
    # Восстанавливаем полный inputs из кэша
    inputs = st.session_state.get("full_inputs", {})
    if not inputs:
        return None
    return run_static_calculations(inputs)


def build_sidebar():
    st.sidebar.title("🦖 1T Rex – Конфигуратор")

    # 1. Энергосистема
    st.sidebar.header("1. Энергосистема")
    name = st.sidebar.text_input("Название проекта", value="1T Rex")
    voltage_s = st.sidebar.slider("Аккумулятор (S)", 6, 14, 12)
    battery_ir_mohm = st.sidebar.number_input(
        "Внутреннее сопротивление сборки (мОм)", value=25.0
    )

    # 2. Ходовая
    st.sidebar.header("2. Ходовая часть")
    drive_motor_count = st.sidebar.selectbox("Кол-во моторов хода", [2, 4], index=1)
    motor_kv = st.sidebar.number_input("KV моторов хода", value=190)
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

    # Базовые массы
    base_drive_mass = 18.0
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
    
    # Сохраняем в session_state для кэша
    st.session_state["full_inputs"] = inputs

    return inputs, base_drive_mass, base_elec_mass, base_frame_mass


def main():
    setup_page()
    inject_global_css()
    init_comparison_state()

    inputs, base_drive_mass, base_elec_mass, base_frame_mass = build_sidebar()

    # --------- Расчеты (с кэшированием для Live Preview) ---------
    
    # Быстрые статические расчеты (кэшируются)
    other_params = f"{inputs['battery_ir_mohm']}_{inputs['drive_motor_count']}"
    static_res = cached_static_calc(
        inputs["voltage_s"], inputs["motor_kv"], inputs["gear_ratio"],
        inputs["wheel_dia_mm"], inputs["weapon_mass_kg"], inputs["weapon_radius_mm"],
        inputs["armor_thickness"], inputs["armor_coverage"],
        other_params
    )
    
    # Если кэш не сработал, считаем заново
    if static_res is None:
        static_res = run_static_calculations(inputs)

    # Для Live Preview делаем упрощенную симуляцию (без оружия, короче)
    if "live_preview_mode" not in st.session_state:
        st.session_state["live_preview_mode"] = True
    
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

    # Полная симуляция (для детальных табов)
    df_sim = simulate_full_system(sim_params, static_res["total_mass"], max_time=8.0)
    sim_stats = aggregate_sim_stats(df_sim)
    
    collision = analyze_collision(
        static_res["total_mass"],
        static_res["weapon_inertia"],
        static_res["weapon_rpm"],
        target_mass=110.0,
    )

    # Live Preview в сайдбаре
    render_sidebar_preview(static_res, sim_stats)

    params_for_report = {
        "name": inputs["name"],
        "voltage_s": inputs["voltage_s"],
        "voltage_nom": static_res["voltage_nom"],
        "date_str": datetime.datetime.now().strftime("%d.%m.%Y"),
    }

    report_md = generate_report(params_for_report, static_res, sim_stats, collision)

    # --------- UI ---------
    st.title(f"Digital Twin: {inputs['name']}")

    # Кнопка сохранения конфигурации
    col_save, col_clear = st.columns([3, 1])
    with col_save:
        if st.button("💾 Сохранить конфигурацию"):
            save_configuration(inputs["name"], inputs, static_res, sim_stats, collision)
            st.success(f"✅ Конфигурация '{inputs['name']}' сохранена")
    with col_clear:
        if st.button("🗑️ Очистить"):
            clear_saved_configs()
            st.rerun()

    # Табы (добавлена вкладка Оптимизатор)
    tabs = st.tabs([
        "📊 Сводка",
        "⏱ Динамика",
        "🔥 Тепло",
        "💥 Столкновение",
        "🔬 Анализ параметров",
        "⚖️ Сравнение",
        "🤖 Авто-оптимизатор",
        "📑 Паспорт"
    ])

    with tabs[0]:  # Сводка
        render_kpi_row(static_res, sim_stats, ROBOT_LIMIT_KG)
        st.markdown("---")
        render_weight_pie(static_res, base_drive_mass, base_elec_mass, base_frame_mass)

    with tabs[1]:  # Динамика
        st.subheader("Разгон и нагрузка на батарею")
        render_drive_plot(df_sim)

    with tabs[2]:  # Тепло
        st.subheader("Тепловой режим моторов")
        render_thermal_plot(df_sim)

    with tabs[3]:  # Столкновение
        st.subheader("Модель столкновения спиннера с целью 110 кг")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Энергия удара", f"{collision['energy_joules']/1000:.1f} кДж")
            st.metric("Сила удара", f"{collision['impact_force_kn']:.1f} кН")
            st.metric("Эквивалент", collision["equivalent"])
        with col2:
            st.metric("Перегрузка для нас", f"{collision['g_force_self']:.1f} G")
            st.metric("Перегрузка цели", f"{collision['g_force_target']:.1f} G")
            st.metric("Скорость отдачи", f"{collision['recoil_speed_kmh']:.1f} км/ч")

    with tabs[4]:  # Анализ параметров
        st.header("🔬 Параметрическое сканирование")
        st.markdown("Анализ влияния одного параметра на все характеристики робота.")
        
        col_param, col_range = st.columns([2, 2])
        
        with col_param:
            selected_param = st.selectbox(
                "Выберите параметр для анализа",
                options=list(SCANNABLE_PARAMS.keys()),
                format_func=lambda x: SCANNABLE_PARAMS[x]["name"]
            )
        
        param_info = SCANNABLE_PARAMS[selected_param]
        
        with col_range:
            st.write(f"**Диапазон:** {param_info['range'][0]} – {param_info['range'][1]} {param_info['unit']}")
            num_points = st.slider("Количество точек", 10, 30, 15)
        
        if st.button("▶️ Запустить сканирование"):
            with st.spinner("Симуляция в процессе..."):
                df_scan = run_parameter_scan(
                    inputs,
                    selected_param,
                    param_info["range"],
                    num_points
                )
                st.session_state["scan_result"] = df_scan
                st.session_state["scan_param"] = selected_param
        
        if "scan_result" in st.session_state:
            df_scan = st.session_state["scan_result"]
            scan_param = st.session_state["scan_param"]
            param_info = SCANNABLE_PARAMS[scan_param]
            
            render_parameter_scan_plots(df_scan, param_info["name"], param_info["unit"])
            
            optimal = get_optimal_range(df_scan, scan_param)
            st.success(f"🎯 Рекомендуемое значение: **{optimal['optimal_value']:.2f} {param_info['unit']}**")
            
            with st.expander("📊 Таблица результатов"):
                st.dataframe(df_scan.style.highlight_max(axis=0, subset=["speed_kmh", "weapon_energy_kj"])
                                         .highlight_min(axis=0, subset=["total_mass", "peak_current", "time_to_20"]))

    with tabs[5]:  # Сравнение
        st.header("⚖️ Side-by-Side сравнение")
        
        saved_configs = get_saved_configs()
        
        if len(saved_configs) < 1:
            st.info("ℹ️ Нет сохраненных конфигураций. Сохраните хотя бы одну для сравнения.")
        else:
            st.markdown(f"**Сохранено конфигураций:** {len(saved_configs)}")
            
            col_sel_a, col_sel_b = st.columns(2)
            
            with col_sel_a:
                config_a_name = st.selectbox(
                    "Конфигурация A",
                    options=[c["name"] for c in saved_configs],
                    key="config_a"
                )
            
            with col_sel_b:
                use_live = st.checkbox("Использовать текущую (LIVE)", value=True)
            
            config_a = next((c for c in saved_configs if c["name"] == config_a_name), None)
            
            if use_live:
                config_b = {
                    "name": "⚡ CURRENT (LIVE)",
                    "speed_kmh": static_res["speed_kmh"],
                    "total_mass": static_res["total_mass"],
                    "weapon_energy_kj": static_res["weapon_energy"] / 1000,
                    "peak_current": sim_stats["peak_current"],
                    "g_force_self": collision["g_force_self"],
                }
            else:
                config_b_name = st.selectbox(
                    "Конфигурация B",
                    options=[c["name"] for c in saved_configs if c["name"] != config_a_name],
                    key="config_b"
                )
                config_b = next((c for c in saved_configs if c["name"] == config_b_name), None)
            
            if config_a and config_b:
                comparison = get_comparison_data(config_a, config_b)
                render_comparison_view(config_a, config_b, comparison)

    with tabs[6]:  # Авто-оптимизатор (НОВЫЙ!)
        st.header("🤖 Автоматическая оптимизация")
        st.markdown("Поиск оптимальных параметров на основе ваших целей и ограничений.")
        
        col_goals, col_constraints = st.columns(2)
        
        with col_goals:
            st.subheader("Цели оптимизации")
            maximize_speed = st.checkbox("Максимизировать скорость", value=True)
            maximize_energy = st.checkbox("Максимизировать энергию удара", value=True)
            minimize_mass = st.checkbox("Минимизировать массу", value=False)
            minimize_current = st.checkbox("Минимизировать ток", value=False)
            minimize_gforce = st.checkbox("Минимизировать перегрузку", value=False)
            
            st.markdown("**Веса целей** (важность)")
            speed_weight = st.slider("Вес: Скорость", 0.1, 2.0, 1.0, 0.1)
            energy_weight = st.slider("Вес: Энергия", 0.1, 2.0, 1.0, 0.1)
        
        with col_constraints:
            st.subheader("Ограничения")
            max_mass = st.number_input("Макс. масса (кг)", value=110.0, step=1.0)
            max_current = st.number_input("Макс. ток (А)", value=500.0, step=10.0)
            
            st.markdown("**Параметры оптимизации**")
            max_iterations = st.slider("Макс. итераций", 20, 100, 50, 10)
        
        if st.button("🚀 Запустить оптимизацию"):
            goals = {
                "maximize_speed": maximize_speed,
                "maximize_energy": maximize_energy,
                "minimize_mass": minimize_mass,
                "minimize_current": minimize_current,
                "minimize_gforce": minimize_gforce,
                "speed_weight": speed_weight,
                "energy_weight": energy_weight,
                "mass_weight": 0.5,
                "current_weight": 0.1,
                "gforce_weight": 0.5,
            }
            
            constraints_dict = {
                "max_mass": max_mass,
                "max_current": max_current,
            }
            
            bounds = get_default_bounds()
            
            optimizer = RobotOptimizer(inputs)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("Оптимизация в процессе..."):
                result = optimizer.optimize(goals, constraints_dict, bounds, max_iterations)
                progress_bar.progress(100)
                status_text.success("✅ Оптимизация завершена!")
            
            # Результаты
            optimized_params = parse_optimized_params(result)
            
            st.subheader("📊 Результаты оптимизации")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown("**Оптимальные параметры:**")
                st.write(f"- Редукция: **{optimized_params['gear_ratio']:.2f}:1**")
                st.write(f"- Диаметр колеса: **{optimized_params['wheel_dia_mm']} мм**")
                st.write(f"- KV мотора: **{optimized_params['motor_kv']}**")
                st.write(f"- Масса ротора: **{optimized_params['weapon_mass_kg']:.1f} кг**")
                st.write(f"- Толщина брони: **{optimized_params['armor_thickness']} мм**")
            
            with col_res2:
                st.markdown("**Применить оптимизацию:**")
                if st.button("✨ Применить найденные параметры"):
                    # Обновляем session_state для применения параметров
                    for key, value in optimized_params.items():
                        if key in st.session_state:
                            st.session_state[key] = value
                    st.success("Параметры применены! Перезагрузите страницу.")
                    st.rerun()
            
            # График сходимости
            history = optimizer.get_history()
            render_optimization_progress(history)
            
            # Сохранение оптимальной конфигурации
            if st.button("💾 Сохранить оптимальную конфигурацию"):
                # Пересчитываем с оптимальными параметрами
                opt_inputs = inputs.copy()
                opt_inputs.update(optimized_params)
                opt_static = run_static_calculations(opt_inputs)
                
                opt_sim_params = sim_params.copy()
                opt_sim_params.update({
                    "motor_kv": optimized_params["motor_kv"],
                    "gear_ratio": optimized_params["gear_ratio"],
                    "wheel_dia_mm": optimized_params["wheel_dia_mm"],
                })
                
                opt_df_sim = simulate_full_system(opt_sim_params, opt_static["total_mass"], max_time=4.0)
                opt_sim_stats = aggregate_sim_stats(opt_df_sim)
                opt_collision = analyze_collision(
                    opt_static["total_mass"],
                    opt_static["weapon_inertia"],
                    opt_static["weapon_rpm"]
                )
                
                save_configuration(
                    f"{inputs['name']} (Optimized)",
                    opt_inputs,
                    opt_static,
                    opt_sim_stats,
                    opt_collision
                )
                st.success("Оптимальная конфигурация сохранена!")

    with tabs[7]:  # Паспорт
        st.subheader("Паспорт робота (Markdown)")
        with st.container(border=True):
            st.markdown(report_md)
        st.download_button(
            "📥 Скачать паспорт (.md)",
            data=report_md,
            file_name="robot_passport.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
