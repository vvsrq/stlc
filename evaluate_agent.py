from stable_baselines3 import DQN
from sumo_rl import SumoEnvironment
import traci
import numpy as np

if __name__ == '__main__':

    env = SumoEnvironment(
        net_file='intersection.net.xml',
        route_file='evaluation_routes.rou.xml',
        single_agent=True,
        use_gui=True,
        num_seconds=5000,
        sumo_warnings=False,
        delta_time=5,
    )

    model = DQN.load("dqn_model")

    print("--- ЗАПУСК ОЦЕНКИ (СБОР ВСЕХ МЕТРИК) ---")
    obs, info = env.reset()
    done = False
    total_waiting_time = 0.0

    total_co2_emissions_mg = 0.0
    unique_vehicles_stopped = set()
    queue_lengths = []
    arrived_vehicles = 0

    incoming_lanes = [
        "N_in_0", "N_in_1", "S_in_0", "S_in_1",
        "E_in_0", "E_in_1", "W_in_0", "W_in_1"
    ]

    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)

        active_vehicles = traci.simulation.getMinExpectedNumber()

        if active_vehicles > 0:
            last_active_time = traci.simulation.getTime()

        done = terminated or truncated

        vehicle_ids = traci.vehicle.getIDList()
        current_total_queue = 0

        arrived_vehicles += traci.simulation.getArrivedNumber()

        for lane_id in incoming_lanes:
            current_total_queue += traci.lane.getLastStepHaltingNumber(lane_id)
        queue_lengths.append(current_total_queue)

        for v_id in vehicle_ids:
            total_waiting_time += traci.vehicle.getWaitingTime(v_id)
            total_co2_emissions_mg += traci.vehicle.getCO2Emission(v_id)  # мг/с

            if traci.vehicle.getSpeed(v_id) < 0.1:
                unique_vehicles_stopped.add(v_id)

    print("--- СИМУЛЯЦИЯ ЗАВЕРШЕНА ---")

    end_time_sim = traci.simulation.getTime()


    num_stopped = len(unique_vehicles_stopped)
    avg_wait_time = total_waiting_time / num_stopped if num_stopped > 0 else 0
    avg_queue_length = np.mean(queue_lengths) if queue_lengths else 0
    throughput = arrived_vehicles

    total_co2_kg = total_co2_emissions_mg / 1000000

    print("\n--- ИТОГОВЫЕ РЕЗУЛЬТАТЫ (RL-АГЕНТ) ---")
    print(f"Средняя длина очереди: {avg_queue_length:.2f} авто")
    print(f"Пропускная способность: {throughput} авто/час")
    print(f"Среднее время ожидания: {avg_wait_time:.2f} сек")
    print(f"Общие выбросы CO2: {total_co2_kg:.2f} кг")
    print(f"Общее время симуляции: {last_active_time:.2f} сек")

    env.close()