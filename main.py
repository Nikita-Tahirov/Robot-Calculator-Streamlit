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
)

ROBOT_LIMIT_KG = 110.0


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
    gear_ratio = st.sidebar.number_input("Редукция хода", value=12.5)
    wheel_dia_mm = st.sidebar.number_input("Диаметр колеса (мм)", value=200)
    esc_current_limit_drive = st.sidebar.slider(
        "Лимит тока ESC (ход), А", 20, 150, 60
    )
    friction_coeff = st.sidebar.slider("Коэф. трения (покрытие/колеса)", 0.3, 1.0, 0.7)

    # 3. Оружие
    st.sidebar.header("3. Оружие")
    simulate_weapon = st.sidebar.checkbox("Симулировать работу оружия", value=True)
    weapon_motor_count = st.sidebar.selectbox("Кол-во моторов оружия", [1, 2], index=1)
    weapon_motor_kv = st.sidebar.number_input("KV моторов оружия", value=150)
    weapon_reduction = st.sidebar.number_input("Редукция оружия", value=1.5)
    weapon_mass_kg = st.sidebar.number_input("Масса ротора (кг)", value=28.0)
    weapon_radius_mm = st.sidebar.number_input("Радиус удара (мм)", value=180)
    esc_current_limit_weapon = st.sidebar.slider(
        "Лимит тока ESC (оружие), А", 50, 300, 120
    )

    # 4. Вес и броня
    st.sidebar.header("4. Броня и масса")
    armor_thickness = st.sidebar.slider("Толщина брони (мм)", 2, 10, 5)
    armor_coverage = st.sidebar.slider("Покрытие броней (%)", 10, 100, 35)

    # Базовые массы (можно вынести в отдельные настройки)
    base_drive_mass = 18.0
    base_elec_mass = 12.0
    base_frame_mass = 25.0
    armor_density_kg_m3 = 2700.0  # алюминий
    armor_area_total = 3.0        # м²

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

    return inputs, base_drive_mass, base_elec_mass, base_frame_mass


def main():
    setup_page()
    inject_global_css()

    inputs, base_drive_mass, base_elec_mass, base_frame_mass = build_sidebar()

    # --------- Расчеты ---------
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

    df_sim = simulate_full_system(sim_params, static_res["total_mass"])
    sim_stats = aggregate_sim_stats(df_sim)
    collision = analyze_collision(
        static_res["total_mass"],
        static_res["weapon_inertia"],
        static_res["weapon_rpm"],
        target_mass=110.0,
    )

    params_for_report = {
        "name": inputs["name"],
        "voltage_s": inputs["voltage_s"],
        "voltage_nom": static_res["voltage_nom"],
        "date_str": datetime.datetime.now().strftime("%d.%m.%Y"),
    }

    report_md = generate_report(params_for_report, static_res, sim_stats, collision)

    # --------- UI ---------
    st.title(f"Digital Twin: {inputs['name']}")

    tab_summary, tab_dynamics, tab_thermal, tab_collision, tab_passport = st.tabs(
        ["📊 Сводка", "⏱ Динамика", "🔥 Тепло", "💥 Столкновение", "📑 Паспорт"]
    )

    with tab_summary:
        render_kpi_row(static_res, sim_stats, ROBOT_LIMIT_KG)
        st.markdown("---")
        render_weight_pie(static_res, base_drive_mass, base_elec_mass, base_frame_mass)

    with tab_dynamics:
        st.subheader("Разгон и нагрузка на батарею")
        render_drive_plot(df_sim)

    with tab_thermal:
        st.subheader("Тепловой режим моторов")
        render_thermal_plot(df_sim)

    with tab_collision:
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

    with tab_passport:
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
