"""
База данных компонентов для Digital Twin.
Характеристики реальных моторов и аккумуляторов.
"""

MOTORS_DB = {
    "Custom (Свой)": {
        "kv": 190,
        "mass_kg": 1.2,
        "desc": "Ручной ввод параметров"
    },
    "TP Power 5670": {
        "kv": 220,
        "mass_kg": 1.05,
        "desc": "Популярный inrunner, 6kW пик"
    },
    "Leopard 58110": {
        "kv": 160,
        "mass_kg": 1.45,
        "desc": "Тяговитый, тяжелый мотор"
    },
    "Hobbywing 5687": {
        "kv": 1100,
        "mass_kg": 0.95,
        "desc": "Высокооборотистый (требует высокой редукции)"
    },
    "Turnigy SK3 6374": {
        "kv": 192,
        "mass_kg": 0.85,
        "desc": "Outrunner, дешевый, но греется"
    }
}

BATTERIES_DB = {
    "Custom (Своя сборка)": {
        "cell_ir": 2.0,  # мОм на ячейку (условно)
        "capacity_ah": 5.0,
        "desc": "Ручной ввод сопротивления сборки"
    },
    "Molicel P42A (21700)": {
        "cell_ir": 1.8,  # AC IR 1kHz ~9mOhm, DC IR под нагрузкой ниже
        "capacity_ah": 4.2,
        "desc": "High power 45A, industry standard"
    },
    "Samsung 40T (21700)": {
        "cell_ir": 2.5,
        "capacity_ah": 4.0,
        "desc": "Хороший баланс, 35A"
    },
    "GNB LiPo HV (High C)": {
        "cell_ir": 0.8,  # Очень низкое сопротивление
        "capacity_ah": 6.0,
        "desc": "Высокая токоотдача, низкий цикл жизни"
    }
}
