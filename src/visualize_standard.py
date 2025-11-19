import os
import sys
import traci
from sumolib import checkBinary

# --- НАСТРОЙКИ ---
ROUTE_FILE = "../sim_configs/traffic_uneven.rou.xml"


def visualize_standard():
    print(f"--- ЗАПУСК ВИЗУАЛИЗАЦИИ СТАНДАРТА ({ROUTE_FILE}) ---")

    # Находим SUMO с графикой
    sumoBinary = checkBinary('sumo-gui')

    cmd = [
        sumoBinary,
        "-n", "my_avenue.net.xml",
        "-r", ROUTE_FILE,
        "--start",  # Автоматически нажать старт (опционально)
        "--delay", "100",
        "--time-to-teleport", "60",  # Чтобы не зависло в мертвой пробке
        "--no-step-log", "true"
    ]

    traci.start(cmd)

    print("Симуляция запущена. Наблюдай за пробками.")

    step = 0
    while step < 3600:
        traci.simulationStep()
        step += 1

        # Если окно SUMO закроют руками, скрипт остановится
        if traci.isLoaded():
            pass
        else:
            break

    traci.close()


if __name__ == "__main__":
    visualize_standard()