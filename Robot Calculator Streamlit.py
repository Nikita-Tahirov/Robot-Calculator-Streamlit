import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(
    page_title="Конфигуратор платформы 1T Rex",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- КОНСТАНТЫ И СПРАВОЧНИКИ ---
MATERIALS = {
    "Алюминиевый сплав (АМг6/Д16Т)": 2.70,
    "Титан (VT6)": 4.43,
    "Сталь (Ст3/Hardox)": 7.85,
    "Полиуретан (Колеса)": 1.20
}

ROBOT_LIMIT_KG = 110.0

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def calculate_plate_weight(material_name, area_m2, thickness_mm):
    """Расчет массы пластины/брони"""
    density_g_cm3 = MATERIALS[material_name]
    density_kg_m3 = density_g_cm3 * 1000
    volume_m3 = area_m2 * (thickness_mm / 1000)
    return volume_m3 * density_kg_m3

def generate_report(params, results):
    """Генерация Markdown отчета для ВКР"""
    date_str = datetime.now().strftime("%d.%m.%Y")
    report = f"""
# ТЕХНИЧЕСКИЙ ПАСПОРТ РОБОТИЗИРОВАННОЙ ПЛАТФОРМЫ
**Проект:** {params['name']}
**Направление:** 15.04.06 Мехатроника и робототехника
**Дата расчета:** {date_str}

## 1. Общие сведения
| Параметр | Значение |
|----------|----------|
| **Габариты (ДхШхВ)** | {params['dims']} мм |
| **Расчетная масса** | {results['total_mass']:.2f} кг |
| **Класс** | Heavyweight ({ROBOT_LIMIT_KG} кг) |
| **Макс. скорость** | {results['speed_kmh']:.1f} км/ч |
| **Энергосистема** | LiPo {params['voltage_s']}S ({params['voltage_v']:.1f} В) |

## 2. Силовая установка и трансмиссия
* **Привод хода:** {params['drive_count']} электродвигателя(ей) через редукторы.
* **Привод орудия:** {params['weapon_motor_count']} электродвигателя(ей), ременная передача.
* **Колеса:** Полиуретан, Ø{params['wheel_dia_mm']} мм (собственное изготовление).

## 3. Боевая часть
* **Тип:** {params['weapon_type']}
* **Эффективная масса ротора:** {params['weapon_mass']} кг
* **Кинетическая энергия:** {results['weapon_energy']:.0f} Дж ({results['weapon_energy']/1000:.1f} кДж)
* **Скорость вращения:** {results['weapon_rpm']:.0f} об/мин

## 4. Конструкция и материалы
* **Бронирование:** {params['armor_material']}, толщина {params['armor_thickness']} мм.
* **Рама:** Сборная (болтовые соединения + сварка).
* **Особенности:** Возможность движения в перевернутом виде, раздельные контуры питания.

---
*Расчет выполнен в программном модуле "Digital Twin 1T Rex"*
"""
    return report

# --- ИНТЕРФЕЙС: БОКОВАЯ ПАНЕЛЬ (INPUTS) ---
st.sidebar.title("🦖 1T Rex: Config")
st.sidebar.markdown("**Параметры цифрового двойника**")

# Секция 1: База
st.sidebar.header("1. Энергетика и База")
robot_name = st.sidebar.text_input("Название", value="1T Rex")
dims_str = st.sidebar.text_input("Габариты (ДхШхВ)", value="940 x 830 x 435")
voltage_s = st.sidebar.slider("Аккумулятор (S LiPo)", 6, 14, 12, help="Номинал 44.4В для 12S")

# Секция 2: Движение (4 мотора)
st.sidebar.header("2. Ходовая часть (4WD)")
drive_motor_count = st.sidebar.selectbox("Кол-во моторов хода", [2, 4, 6], index=1)
# Подбираем KV и редукцию так, чтобы при 12S выходило ~25 км/ч на 200мм колесах
# 25 км/ч = 6.94 м/с. Колесо D=0.2м -> L=0.628м. RPM колеса = 663.
# Мотор KV190 на 44.4В = 8436 RPM. Редукция нужна ~12.7:1
motor_kv = st.sidebar.number_input("KV моторов хода", value=190, step=10)
gear_ratio = st.sidebar.number_input("Редукция хода (X:1)", value=12.5, step=0.1)
wheel_dia_mm = st.sidebar.number_input("Диаметр колеса (мм)", value=200, step=5)
wheel_friction_coeff = 0.7 # Для полиуретана

# Секция 3: Оружие (2 мотора)
st.sidebar.header("3. Вертикальный спиннер")
weapon_motor_count = st.sidebar.selectbox("Кол-во моторов оружия", [1, 2], index=1)
weapon_type = "Вертикальный спиннер (Диск/Биток)"
weapon_motor_kv = st.sidebar.number_input("KV моторов оружия", value=150, step=10) # Мощные низы
weapon_reduction = st.sidebar.number_input("Редукция (Ремень) X:1", value=1.5, step=0.1)
weapon_mass_kg = st.sidebar.number_input("Масса ротора (кг)", value=28.0, step=0.5)
weapon_radius_mm = st.sidebar.number_input("Радиус удара (мм)", value=180, step=10)

# Секция 4: Весовая сводка
st.sidebar.header("4. Вес и Материалы")
armor_material = st.sidebar.selectbox("Материал брони", list(MATERIALS.keys()), index=0) # Алюминий
armor_thickness = st.sidebar.slider("Толщина внеш. панелей (мм)", 2, 12, 5)
# Площадь обшивки. У робота 940х830 огромная площадь. Допустим, обшито 40% поверхности
total_surface_area = 3.0 # Грубая оценка м2 полной коробки
armor_coverage_percent = st.sidebar.slider("Процент бронирования площади (%)", 10, 100, 35)
active_armor_area = total_surface_area * (armor_coverage_percent / 100)

# Фиксированные веса (примерные)
# 4 мотора (по 1.5 кг) + 2 мотора оружия (по 2 кг) + редукторы + колеса
drive_train_mass = st.sidebar.number_input("Масса ходовой (Моторы+Колеса) кг", value=18.0) 
electronics_mass = st.sidebar.number_input("Электроника (АКБ+ESC+Провода)", value=12.0)
frame_internal_mass = st.sidebar.number_input("Внутр. рама и крепеж (кг)", value=25.0)

# --- РАСЧЕТНАЯ МОДЕЛЬ (BACKEND) ---

voltage_nom = voltage_s * 3.7

# 1. Расчет скорости
wheel_circumference_m = (wheel_dia_mm / 1000) * np.pi
motor_rpm_loaded = (voltage_nom * motor_kv) * 0.85 # 85% эффективность под нагрузкой
wheel_rpm = motor_rpm_loaded / gear_ratio
speed_ms = (wheel_rpm * wheel_circumference_m) / 60
speed_kmh = speed_ms * 3.6

# 2. Расчет оружия
# Момент инерции для диска/битка (коэфф 0.6 усредненный для сложной формы)
inertia = 0.6 * weapon_mass_kg * ((weapon_radius_mm/1000) ** 2)
weapon_rpm = (voltage_nom * weapon_motor_kv) / weapon_reduction
weapon_rad_s = (weapon_rpm * 2 * np.pi) / 60
kinetic_energy = 0.5 * inertia * (weapon_rad_s ** 2)

# 3. Расчет массы
calculated_armor_mass = calculate_plate_weight(armor_material, active_armor_area, armor_thickness)
total_mass = drive_train_mass + electronics_mass + frame_internal_mass + weapon_mass_kg + calculated_armor_mass

# Словарь для отчета
results_dict = {
    'total_mass': total_mass,
    'speed_kmh': speed_kmh,
    'weapon_energy': kinetic_energy,
    'weapon_rpm': weapon_rpm,
    'armor_mass': calculated_armor_mass
}
params_dict = {
    'name': robot_name,
    'dims': dims_str,
    'voltage_s': voltage_s,
    'voltage_v': voltage_nom,
    'drive_count': drive_motor_count,
    'wheel_dia_mm': wheel_dia_mm,
    'weapon_type': weapon_type,
    'weapon_motor_count': weapon_motor_count,
    'weapon_mass': weapon_mass_kg,
    'armor_material': armor_material,
    'armor_thickness': armor_thickness
}

# --- ВИЗУАЛИЗАЦИЯ (UI) ---

st.title(f"🛠️ Проектирование платформы: {robot_name}")
st.caption(f"Направление: 15.04.06 Мехатроника и робототехника | Спонсор: 1Т")

# Вкладки
tab1, tab2, tab3 = st.tabs(["📊 Сводка характеристик", "⚖️ Весовой бюджет", "📑 Паспорт ВКР"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Скорость (Расчетная)", f"{speed_kmh:.1f} км/ч", f"Цель: ~25 км/ч")
        st.caption(f"При редукции {gear_ratio}:1 и {voltage_s}S")
    with col2:
        st.metric("Кинетическая энергия", f"{kinetic_energy/1000:.1f} кДж", f"{weapon_rpm:.0f} RPM")
        st.caption("Вертикальный спиннер")
    with col3:
        delta = ROBOT_LIMIT_KG - total_mass
        st.metric("Итоговая масса", f"{total_mass:.1f} кг", f"{delta:+.1f} кг (Запас)", 
                  delta_color="normal" if delta >= 0 else "inverse")
    
    st.divider()
    
    # Визуализация "Спидометр vs Оружие"
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Ходовая часть:** {drive_motor_count} мотора(ов) • Полиуретан Ø{wheel_dia_mm}мм")
    with c2:
        st.error(f"**Оружие:** {weapon_motor_count} мотора(ов) • Ротор {weapon_mass_kg}кг • Ремень")

with tab2:
    st.subheader("Распределение массы по подсистемам")
    
    mass_data = {
        "Броня (Al сплав)": calculated_armor_mass,
        "Орудие (Ротор + Привод)": weapon_mass_kg + (weapon_motor_count * 2.0), # + вес моторов оружия
        "Ходовая (Моторы + Колеса)": drive_train_mass,
        "Рама и Крепеж": frame_internal_mass,
        "Электроника и АКБ": electronics_mass
    }
    
    # Корректировка тотала для графика (чтобы сумма сходилась с total_mass, если мы добавили вес моторов оружия вручную выше)
    # Для простоты в пайчарте используем чистые введенные категории
    
    fig = px.pie(
        values=list(mass_data.values()), 
        names=list(mass_data.keys()),
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Prism, # Палитра поярче
    )
    fig.update_layout(title_text="Структура веса (кг)", annotations=[dict(text=f'{total_mass:.0f} кг', x=0.5, y=0.5, font_size=20, showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)
    
    if total_mass > ROBOT_LIMIT_KG:
        st.warning(f"⚠️ **Превышение лимита!** Необходимо снизить вес на {total_mass - ROBOT_LIMIT_KG:.2f} кг.")
        st.markdown("- Попробуйте уменьшить толщину брони\n- Уменьшите % покрытия броней\n- Облегчите раму")

with tab3:
    st.header("📄 Предпросмотр Паспорта")
    st.info("Ниже представлен визуализированный отчет. Он отрендерен согласно стандартам разметки Markdown.")
    
    report_md = generate_report(params_dict, results_dict)
    
    # Визуализация отчета в красивой рамке
    with st.container(border=True):
        st.markdown(report_md)
    
    st.divider()
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        # Кнопка для скачивания файла
        st.download_button(
            label="📥 Скачать Паспорт (.md)",
            data=report_md,
            file_name=f"Passport_1T_Rex_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            help="Файл можно открыть в любом текстовом редакторе или импортировать в Word"
        )
    
    with col_dl2:
        # Возможность быстро скопировать сырой код, если нужно
        with st.expander("Показать исходный код (для копирования)"):
            st.code(report_md, language="markdown")
