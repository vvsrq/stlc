import os
import sys
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment

# --- НАСТРОЙКИ ---
# Выбираем сценарий, где ИИ должен всех порвать
ROUTE_FILE = "../sim_configs/traffic_uneven.rou.xml"
MODEL_PATH = "ppo_avenue_model"


def visualize_ai():
    print(f"--- ЗАПУСК ВИЗУАЛИЗАЦИИ ИИ ({ROUTE_FILE}) ---")

    # 1. Создаем среду с ГРАФИКОЙ (use_gui=True)
    env = SumoEnvironment(
        net_file="../sim_configs/my_avenue.net.xml",
        route_file=ROUTE_FILE,
        out_csv_name="outputs/visual_ai",
        use_gui=True,  # <--- ГЛАВНОЕ: Открывает окно
        num_seconds=3600,
        min_green=5,  # Важно: должно совпадать с обучением!
        max_green=90,
        delta_time=5,
        reward_fn="pressure",  # Или diff-waiting-time (не важно для просмотра)
        fixed_ts=True,  # Важно: должно совпадать с обучением!
        single_agent=True
    )

    # 2. Загружаем мозг
    try:
        model = PPO.load(MODEL_PATH)
    except FileNotFoundError:
        print("Ошибка: Нет файла модели!")
        return

    obs, _ = env.reset()
    done = False

    print("Окно открыто. Нажми 'Play' (зеленый треугольник) в SUMO.")

    while not done:
        # ИИ принимает решение
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

    env.close()


if __name__ == "__main__":
    visualize_ai()