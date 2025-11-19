import os
import sys
import time
import xml.etree.ElementTree as ET
import pandas as pd
import traci
from sumolib import checkBinary
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment

# --- НАСТРОЙКИ ---
SCENARIOS = [
    {"name": "Light", "route": "traffic_500.rou.xml"},
    {"name": "Medium", "route": "traffic_1500.rou.xml"},
    {"name": "Heavy", "route": "traffic_3000.rou.xml"},
    {"name": "Uneven_Win", "route": "traffic_uneven.rou.xml"}
]

MODEL_PATH = "ppo_avenue_model"
NET_FILE = "my_avenue.net.xml"
TELEPORT_TIME = "300"  # 5 минут терпения

# Создаем папку
if not os.path.exists("outputs_csv"): os.makedirs("outputs_csv")


def parse_tripinfo(xml_file):
    metrics = {"throughput": 0, "co2_kg": 0.0, "fuel_liters": 0.0, "avg_wait": 0.0, "avg_speed": 0.0}
    if not os.path.exists(xml_file): return metrics
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        trips = root.findall("tripinfo")
        count = len(trips)
        if count == 0: return metrics

        total_wait = 0.0
        total_co2 = 0.0
        total_fuel = 0.0
        total_len = 0.0
        total_dur = 0.0

        for trip in trips:
            total_wait += float(trip.get("waitingTime", 0))

            # Парсинг CO2/Fuel с проверкой разных названий атрибутов
            co2 = trip.get("CO2_abs") or trip.get("CO2")
            if not co2:
                e = trip.find("emissions")
                if e is not None: co2 = e.get("CO2_abs")
            if co2: total_co2 += float(co2)

            fuel = trip.get("fuel_abs") or trip.get("fuel")
            if not fuel:
                e = trip.find("emissions")
                if e is not None: fuel = e.get("fuel_abs")
            if fuel: total_fuel += float(fuel)

            total_len += float(trip.get("routeLength", 0))
            total_dur += float(trip.get("duration", 0))

        metrics["throughput"] = count
        metrics["co2_kg"] = total_co2 / 1_000_000
        metrics["fuel_liters"] = total_fuel / 750_000  # ~0.75 kg/l density
        metrics["avg_wait"] = total_wait / count
        if total_dur > 0: metrics["avg_speed"] = (total_len / total_dur) * 3.6
    except Exception:
        pass
    return metrics


def run_rl_agent(scenario):
    print(f"   [AI] Запуск модели ({scenario['name']})...")
    base_name = f"{scenario['name']}_RL"
    trip_out = os.path.abspath(f"outputs_csv/{base_name}_tripinfo.xml")
    csv_out = os.path.abspath(f"outputs_csv/{base_name}_log")
    if os.path.exists(trip_out): os.remove(trip_out)

    try:
        model = PPO.load(MODEL_PATH)
    except:
        return None

    env = SumoEnvironment(
        net_file=NET_FILE, route_file=scenario['route'], out_csv_name=csv_out,
        use_gui=False, num_seconds=20000,
        min_green=5, max_green=120, delta_time=5, reward_fn="pressure", fixed_ts=True, single_agent=True,
        additional_sumo_cmd=f"--tripinfo-output {trip_out} --device.emissions.probability 1.0"
    )

    obs, _ = env.reset()
    done = False
    total_queue = 0
    teleport_count = 0
    steps = 0
    sim_end_time = 0.0

    try:
        while not done:
            teleport_count += env.sumo.simulation.getStartingTeleportNumber()
            curr_q = 0
            for edge in env.sumo.edge.getIDList():
                curr_q += env.sumo.edge.getLastStepHaltingNumber(edge)
            total_queue += curr_q
            steps += 1

            action, _ = model.predict(obs, deterministic=True)
            obs, _, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            if env.sumo.simulation.getMinExpectedNumber() <= 0:
                sim_end_time = env.sumo.simulation.getTime()
                done = True
    finally:
        env.close()

    metrics = parse_tripinfo(trip_out)
    metrics["avg_queue"] = total_queue / steps if steps > 0 else 0
    metrics["teleports"] = teleport_count
    metrics["total_time"] = sim_end_time
    return metrics


def run_standard(scenario):
    sc_name = scenario['name']
    print(f"   [Standard] Запуск ({sc_name})...")

    base_name = f"{sc_name}_STD"
    trip_out = os.path.abspath(f"outputs_csv/{base_name}_tripinfo.xml")
    if os.path.exists(trip_out): os.remove(trip_out)

    sumoBinary = checkBinary('sumo')
    cmd = [
        sumoBinary, "-n", NET_FILE, "-r", scenario['route'],
        "--tripinfo-output", trip_out, "--no-step-log", "true",
        "--time-to-teleport", TELEPORT_TIME, "--ignore-route-errors", "true",
        "--device.emissions.probability", "1.0"
    ]

    total_queue = 0
    teleport_count = 0
    steps = 0
    sim_end_time = 0.0

    try:
        traci.start(cmd)
        tls_id = "clusterJ19_J20"
        traci.trafficlight.setProgram(tls_id, "0")  # Сброс логики

        # --- НАСТРОЙКА РУЧНОГО ТАЙМЕРА ---
        # Если сценарий Uneven - ставим "плохой" таймер (15/45), симулируя ошибку настройки
        # Если сценарий обычный - ставим "честный" таймер (35/35)
        is_uneven = "Uneven" in sc_name
        cycle_len = 70 if is_uneven else 80

        green_main = 15 if is_uneven else 35
        # 5 сек желтый
        green_side_start = green_main + 5
        green_side_end = green_side_start + (45 if is_uneven else 35)

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            # Ручное управление
            t = steps % cycle_len
            if t < green_main:
                traci.trafficlight.setPhase(tls_id, 0)
            elif t < green_side_start:
                traci.trafficlight.setPhase(tls_id, 1)
            elif t < green_side_end:
                traci.trafficlight.setPhase(tls_id, 2)
            else:
                traci.trafficlight.setPhase(tls_id, 3)

            teleport_count += traci.simulation.getStartingTeleportNumber()
            curr_q = 0
            for edge in traci.edge.getIDList(): curr_q += traci.edge.getLastStepHaltingNumber(edge)
            total_queue += curr_q

            steps += 1
            sim_end_time = traci.simulation.getTime()
            if steps > 30000: break
        traci.close()
    except Exception:
        try:
            traci.close()
        except:
            pass

    metrics = parse_tripinfo(trip_out)
    metrics["avg_queue"] = total_queue / steps if steps > 0 else 0
    metrics["teleports"] = teleport_count
    metrics["total_time"] = sim_end_time
    return metrics


def main():
    results = []
    print("=" * 140)
    print(f"{'GRAND FINAL REPORT':^140}")
    print("=" * 140)

    for sc in SCENARIOS:
        print(f"\n>>> СЦЕНАРИЙ: {sc['name']}")
        m_rl = run_rl_agent(sc)
        if not m_rl: continue
        m_std = run_standard(sc)

        def diff(v1, v2, invert=False):
            if v2 == 0: return "0%"
            d = ((v2 - v1) / v2) * 100
            if invert: d = -d
            sign = "+" if d > 0 else ""
            return f"{sign}{d:.1f}%"

        results.append({"Сценарий": sc['name'], "Тип": "AI (RL)",
                        "Время (с)": m_rl['total_time'], "Телепорты": m_rl['teleports'],
                        "Очередь": round(m_rl['avg_queue'], 1), "Ожидание": round(m_rl['avg_wait'], 1),
                        "Скорость": round(m_rl['avg_speed'], 1), "Топливо": round(m_rl['fuel_liters'], 1),
                        "CO2": round(m_rl['co2_kg'], 1)})

        results.append({"Сценарий": sc['name'], "Тип": "Standard",
                        "Время (с)": m_std['total_time'], "Телепорты": m_std['teleports'],
                        "Очередь": round(m_std['avg_queue'], 1), "Ожидание": round(m_std['avg_wait'], 1),
                        "Скорость": round(m_std['avg_speed'], 1), "Топливо": round(m_std['fuel_liters'], 1),
                        "CO2": round(m_std['co2_kg'], 1)})

        results.append({"Сценарий": "", "Тип": "ВЫГОДА",
                        "Время (с)": diff(m_rl['total_time'], m_std['total_time']),
                        "Телепорты": diff(m_rl['teleports'], m_std['teleports']),
                        "Очередь": diff(m_rl['avg_queue'], m_std['avg_queue']),
                        "Ожидание": diff(m_rl['avg_wait'], m_std['avg_wait']),
                        "Скорость": diff(m_rl['avg_speed'], m_std['avg_speed'], invert=True),
                        "Топливо": diff(m_rl['fuel_liters'], m_std['fuel_liters']),
                        "CO2": diff(m_rl['co2_kg'], m_std['co2_kg'])})

    print("\n" + "=" * 140)
    df = pd.DataFrame(results)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.colheader_justify', 'center')
    print(df.to_string(index=False))
    print("=" * 140)


if __name__ == "__main__":
    main()