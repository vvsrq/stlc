import os
import sys
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment


def run_visual():
    # Имя файла для сохранения статистики этого запуска
    output_name = "outputs/final_result"

    # 1. Создаем среду с теми же параметрами, что и при обучении
    # Но включаем use_gui=True, чтобы видеть результат глазами
    env = SumoEnvironment(
        net_file="../sim_configs/my_avenue.net.xml",
        route_file="../sim_configs/avenue_traffic.rou.xml",
        out_csv_name=output_name,  # Сюда запишется статистика (CSV)
        use_gui=True,  # Включаем графику SUMO
        num_seconds=3600,
        min_green=5,
        max_green=50,
        delta_time=5,
        reward_fn="diff-waiting-time",
        single_agent=True  # <--- ОБЯЗАТЕЛЬНО!
    )

    # 2. Загружаем обученную модель
    # Убедись, что файл ppo_avenue_model.zip существует в папке
    try:
        model = PPO.load("ppo_avenue_model")
        print("Модель успешно загружена.")
    except FileNotFoundError:
        print("Ошибка: Файл модели 'ppo_avenue_model.zip' не найден. Сначала запустите train_avenue.py")
        return

    # 3. Запуск цикла симуляции
    obs, info = env.reset()
    done = False
    total_reward = 0

    print("Запуск симуляции...")
    while not done:
        # Модель предсказывает действие. deterministic=True убирает случайность (использует лучшее решение)
        action, _states = model.predict(obs, deterministic=True)

        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward

    print(f"Симуляция завершена. Общая награда: {total_reward}")
    print(f"Результаты сохранены в папку 'outputs/' с префиксом '{output_name}'")

    env.close()


if __name__ == "__main__":
    run_visual()