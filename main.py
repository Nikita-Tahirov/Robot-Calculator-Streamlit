import datetime
import streamlit as st

# Импорты модулей
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

@st.cache_data(ttl=60)
def cached_static_calc(
    voltage_s, motor_kv, gear_ratio, wheel_dia_mm,
    weapon_mass_kg, weapon_radius_mm, armor_thickness, armor_coverage,
    _other_params_hash
):
    inputs = st.session_state.get("full_inputs", {})
    if not inputs: return None
    return run_static_calculations(inputs)

def build_sidebar():
    st.sidebar.markdown("### ПАРАМЕТРЫ СИСТЕМЫ")
    
    with st.sidebar.expander("1. Энергетика и шасси", expanded=True):
        name = st.text_input("Имя проекта", value="1T Rex")
        voltage_s = st.slider("Батарея (S)", 6, 14, 12)
        battery_ir_mohm = st.number_input("Вн. сопр. батареи (мОм)", value=25.0)
        
        drive_motor_count = st.selectbox("Моторы хода (шт)", [2, 4], index=1)
        motor_kv = st.number_input("KV моторов хода", value=190)
        gear_ratio = st.number_input("Редукция", value=12.5, step=0.1)
        wheel_dia_mm = st.number_input("Диаметр колеса (мм)", value=200, step=5)
        
    with st.sidebar.expander("2. Оружие и защита", expanded=False):
        simulate_weapon = st.checkbox("Активное оружие", value=True)
        weapon_motor_count = st.selectbox("Моторы оружия (шт)", [1, 2], index=1)
        weapon_motor_kv = st.number_input("KV моторов оружия", value=150)
        weapon_reduction = st.number_input("Редукция оружия", value=1.5, step=0.1)
        weapon_mass_kg = st.number_input("Масса ротора (кг)", value=28.0, step=0.5)
        weapon_radius_mm = st.number_input("Радиус удара (мм)", value=180, step=5)
        
        armor_thickness = st.slider("Толщина брони (мм)", 2, 10, 5)
        armor_coverage = st.slider("Площадь бронирования (%)", 10, 100, 35, step=5)

    # Технические настройки симуляции (скрыты в expander)
    with st.sidebar.expander("⚙️ Расширенные настройки", expanded=False):
        esc_current_limit_drive = st.slider("Лимит тока ESC (ход)", 20, 150, 60)
        friction_coeff = st.slider("Коэф. трения", 0.3, 1.0, 0.7, step=0.05)
        esc_current_limit_weapon = st.slider("Лимит тока ESC (оружие)", 50, 300, 120)

    # Constants
    base_drive_mass, base_elec_mass, base_frame_mass = 18.0, 12.0, 25.0
    armor_density_kg_m3, armor_area_total = 2700.0, 3.0

    inputs = {
        "name": name, "voltage_s": voltage_s, "battery_ir_mohm": battery_ir_mohm,
        "drive_motor_count": drive_motor_count, "motor_kv": motor_kv, "gear_ratio": gear_ratio,
        "wheel_dia_mm": wheel_dia_mm, "esc_current_limit_drive": esc_current_limit_drive,
        "friction_coeff": friction_coeff, "simulate_weapon": simulate_weapon,
        "weapon_motor_count": weapon_motor_count, "weapon_motor_kv": weapon_motor_kv,
        "weapon_reduction": weapon_reduction, "weapon_mass_kg": weapon_mass_kg,
        "weapon_radius_mm": weapon_radius_mm, "esc_current_limit_weapon": esc_current_limit_weapon,
        "armor_thickness": armor_thickness, "armor_coverage": armor_coverage,
        "base_drive_mass": base_drive_mass, "base_elec_mass": base_elec_mass,
        "base_frame_mass": base_frame_mass, "armor_density_kg_m3": armor_density_kg_m3,
        "armor_area_total": armor_area_total,
    }
    st.session_state["full_inputs"] = inputs
    return inputs, base_drive_mass, base_elec_mass, base_frame_mass

def main():
    setup_page()
    inject_global_css()
    init_comparison_state()

    inputs, base_drive_mass, base_elec_mass, base_frame_mass = build_sidebar()

    # Calculation Block
    other_params = f"{inputs['battery_ir_mohm']}_{inputs['drive_motor_count']}"
    static_res = cached_static_calc(
        inputs["voltage_s"], inputs["motor_kv"], inputs["gear_ratio"],
        inputs["wheel_dia_mm"], inputs["weapon_mass_kg"], inputs["weapon_radius_mm"],
        inputs["armor_thickness"], inputs["armor_coverage"], other_params
    )
    if static_res is None: static_res = run_static_calculations(inputs)

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
    collision = analyze_collision(static_res["total_mass"], static_res["weapon_inertia"], static_res["weapon_rpm"])

    render_sidebar_preview(static_res, sim_stats)

    # Header
    st.title(f"1T REX // ЦИФРОВОЙ ДВОЙНИК")
    st.markdown(f"**Проект:** {inputs['name']} | **Статус:** Активен")

    # Action Bar
    col_save, col_clear = st.columns([3, 1])
    with col_save:
        if st.button("Сохранить конфигурацию"):
            save_configuration(inputs["name"], inputs, static_res, sim_stats, collision)
            st.success(f"Конфигурация сохранена в буфер")
    with col_clear:
        if st.button("Сброс"):
            clear_saved_configs()
            st.rerun()

    # Tabs
    tabs = st.tabs([
        "Сводка", "Динамика", "Терморежим", "Удар",
        "Параметры", "Сравнение", "Оптимизация", "Паспорт"
    ])

    with tabs[0]:
        st.header("Оперативная сводка")
        render_kpi_row(static_res, sim_stats, ROBOT_LIMIT_KG)
        st.markdown("<br>", unsafe_allow_html=True)
        render_weight_pie(static_res, base_drive_mass, base_elec_mass, base_frame_mass)

    with tabs[1]:
        st.header("Динамические характеристики")
        render_drive_plot(df_sim)

    with tabs[2]:
        st.header("Тепловой баланс")
        render_thermal_plot(df_sim)

    with tabs[3]:
        st.header("Моделирование столкновения")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Энергия", f"{collision['energy_joules']/1000:.1f} кДж")
            st.metric("Сила удара", f"{collision['impact_force_kn']:.1f} кН")
            st.metric("Эквивалент", collision["equivalent"])
        with col2:
            st.metric("G-Force (Свой)", f"{collision['g_force_self']:.1f} G")
            st.metric("G-Force (Цель)", f"{collision['g_force_target']:.1f} G")
            st.metric("Скорость отскока", f"{collision['recoil_speed_kmh']:.1f} км/ч")

    with tabs[4]:
        st.header("Анализ чувствительности")
        col_param, col_range = st.columns([2, 2])
        with col_param:
            selected_param = st.selectbox("Целевой параметр", list(SCANNABLE_PARAMS.keys()), format_func=lambda x: SCANNABLE_PARAMS[x]["name"])
        param_info = SCANNABLE_PARAMS[selected_param]
        with col_range:
            num_points = st.slider("Точность (точек)", 10, 30, 15)
        
        if st.button("Запустить сканирование"):
            with st.spinner("Выполняется расчет вариаций..."):
                df_scan = run_parameter_scan(inputs, selected_param, param_info["range"], num_points)
                st.session_state["scan_result"] = df_scan
                st.session_state["scan_param"] = selected_param
        
        if "scan_result" in st.session_state:
            df_scan = st.session_state["scan_result"]
            param_info = SCANNABLE_PARAMS[st.session_state["scan_param"]]
            render_parameter_scan_plots(df_scan, param_info["name"], param_info["unit"])
            optimal = get_optimal_range(df_scan, st.session_state["scan_param"])
            st.info(f"Рекомендуемый диапазон: {optimal['optimal_value']:.2f} {param_info['unit']}")

    with tabs[5]:
        st.header("Сравнительный анализ")
        saved = get_saved_configs()
        if not saved:
            st.warning("Нет сохраненных конфигураций. Сохраните текущую версию через верхнее меню.")
        else:
            col_a, col_b = st.columns(2)
            with col_a: name_a = st.selectbox("Вариант А", [c["name"] for c in saved], key="c_a")
            with col_b: use_live = st.checkbox("Сравнить с текущим (Live)", True)
            
            conf_a = next(c for c in saved if c["name"] == name_a)
            conf_b = {
                "name": "Live Version", "speed_kmh": static_res["speed_kmh"],
                "total_mass": static_res["total_mass"], "weapon_energy_kj": static_res["weapon_energy"]/1000,
                "peak_current": sim_stats["peak_current"], "g_force_self": collision["g_force_self"]
            } if use_live else next(c for c in saved if c["name"] == st.selectbox("Вариант Б", [c["name"] for c in saved if c["name"] != name_a]))
            
            render_comparison_view(conf_a, conf_b, get_comparison_data(conf_a, conf_b))

    with tabs[6]:
        st.header("Автоматическая оптимизация")
        col1, col2 = st.columns(2)
        with col1:
            maximize_speed = st.checkbox("Макс. скорость", True)
            maximize_energy = st.checkbox("Макс. энергию", True)
        with col2:
            st.markdown(f"**Ограничения:** Масса < {ROBOT_LIMIT_KG} кг")
            iter_count = st.slider("Итерации", 20, 100, 30)
        
        if st.button("Найти оптимальное решение"):
            optimizer = RobotOptimizer(inputs)
            goals = {"maximize_speed": maximize_speed, "maximize_energy": maximize_energy}
            constraints = {"max_mass": ROBOT_LIMIT_KG, "max_current": 500}
            with st.spinner("Работает генетический алгоритм..."):
                res = optimizer.optimize(goals, constraints, get_default_bounds(), iter_count)
                st.session_state["opt_res"] = parse_optimized_params(res)
                st.session_state["opt_hist"] = optimizer.get_history()
        
        if "opt_res" in st.session_state:
            p = st.session_state["opt_res"]
            st.success("Найдено решение:")
            st.code(f"Редукция: {p['gear_ratio']:.2f} | Колесо: {p['wheel_dia_mm']}мм | Броня: {p['armor_thickness']}мм")
            if st.button("Применить параметры"):
                for k, v in p.items(): st.session_state[k] = v
                st.rerun()
            render_optimization_progress(st.session_state["opt_hist"])

    with tabs[7]:
        st.header("Экспорт документации")
        report = generate_report({"name": inputs["name"], "voltage_s": inputs["voltage_s"], "date_str": datetime.datetime.now().strftime("%d.%m.%Y")}, static_res, sim_stats, collision)
        st.download_button("Скачать паспорт (.md)", report, "passport.md")

if __name__ == "__main__":
    main()
