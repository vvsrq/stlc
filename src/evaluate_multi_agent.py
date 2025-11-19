# Файл: evaluate_multi_agent.py

import os
from stable_baselines3 import DQN
from sumo_rl import SumoEnvironment
import traci
import numpy as np

def get_incoming_lanes():
    """
    Динамически получает список всех входящих полос для всех светофоров в сети.
    """
    incoming_lanes = set()
    for tls_id in traci.trafficlight.getIDList():
        controlled_lanes = traci.trafficlight.getControlledLanes(tls_id)
        incoming_lanes.update(controlled_lanes)
    return list(incoming_lanes)


if __name__ == '__main__':

    net_file = '../sim_configs/my_avenue.net.xml'
    route_file = 'avenue_traffic_generated.rou.xml'
    model_path = "dqn_model.zip"

    env = SumoEnvironment(
        net_file=net_file,
        route_file=route_file,
        single_agent=False,
        use_gui=True,
        # Этот аргумент работает в новых версиях sumo-rl
        pad_observation=True,
        num_seconds=15000,
        sumo_warnings=False,
        delta_time=5,
    )

    try:
        model = DQN.load(model_path)
    except FileNotFoundError:
        print(f"Ошибка: Файл модели '{model_path}' не найден. Убедитесь, что он находится в той же папке.")
        exit()

    print("--- ЗАПУСК ОЦЕНКИ (СБОР ВСЕХ МЕТРИК) ---")

    # Сбрасываем среду (используя новый API Gymnasium)
    obs, info = env.reset()

    incoming_lanes = get_incoming_lanes()
    print(f"Обнаружено {len(incoming_lanes)} контролируемых полос для сбора метрик.")

    # Инициализация переменных для метрик
    done = {'__all__': False}
    total_waiting_time = 0.0
    total_co2_emissions_mg = 0.0
    queue_lengths = []
    arrived_vehicles = 0
    last_active_time = 0

    # Главный цикл симуляции
    while not done['__all__']:
        actions = {}
        for agent_id, agent_obs in obs.items():
            action, _states = model.predict(agent_obs, deterministic=True)
            actions[agent_id] = int(action)

        # Шаг симуляции (используя новый API Gymnasium)
        obs, reward, terminated, truncated, info = env.step(actions)

        if terminated['__all__'] or truncated['__all__']:
            done['__all__'] = True

        # Сбор метрик на каждом шаге
        if traci.simulation.getMinExpectedNumber() > 0:
            last_active_time = traci.simulation.getTime()

        vehicle_ids = traci.vehicle.getIDList()
        current_total_queue = 0

        for lane_id in incoming_lanes:
            current_total_queue += traci.lane.getLastStepHaltingNumber(lane_id)
        queue_lengths.append(current_total_queue)

        for v_id in vehicle_ids:
            total_waiting_time += traci.vehicle.getWaitingTime(v_id)
            total_co2_emissions_mg += traci.vehicle.getCO2Emission(v_id)

        arrived_vehicles += traci.simulation.getArrivedNumber()

    print("--- СИМУЛЯЦИЯ ЗАВЕРШЕНА ---")

    # Вычисление итоговых метрик
    avg_queue_length = np.mean(queue_lengths) if queue_lengths else 0
    avg_wait_time_per_vehicle = total_waiting_time / arrived_vehicles if arrived_vehicles > 0 else 0
    simulation_hours = last_active_time / 3600
    throughput_per_hour = arrived_vehicles / simulation_hours if simulation_hours > 0 else 0
    total_co2_kg = total_co2_emissions_mg / 1_000_000

    print("\n--- ИТОГОВЫЕ РЕЗУЛЬТАТЫ (RL-АГЕНТ) ---")
    print(f"Общее время симуляции: {last_active_time:.2f} сек ({simulation_hours:.2f} часов)")
    print(f"Всего прибыло автомобилей: {arrived_vehicles}")
    print(f"Пропускная способность: {throughput_per_hour:.2f} авто/час")
    print(f"Средняя длина очереди (по всем перекресткам): {avg_queue_length:.2f} авто")
    print(f"Среднее время ожидания на одно авто: {avg_wait_time_per_vehicle:.2f} сек")
    print(f"Общие выбросы CO2: {total_co2_kg:.2f} кг")

    env.close()