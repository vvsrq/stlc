import os
import sys
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment

if "SUMO_HOME" not in os.environ:
    print("Пожалуйста, установите переменную окружения SUMO_HOME")
    sys.exit(1)


def train():
    # ВАЖНО: Обучаем ТОЛЬКО на Uneven (Неравномерном) сценарии.
    # Это самый сложный случай. Если агент научится здесь, он
    # автоматически справится и с симметричным трафиком (Heavy),
    # так как там разница давлений будет около нуля, и он будет делить время поровну.
    route_file = "traffic_uneven.rou.xml"

    env = SumoEnvironment(
        net_file="my_avenue.net.xml",
        route_file=route_file,
        out_csv_name="outputs/my_avenue_uneven",
        use_gui=False,
        num_seconds=3600,

        # Даем ему свободу переключаться быстро, если дорога пустая
        min_green=5,
        max_green=60,
        delta_time=5,

        # Лучшая метрика для пробок
        reward_fn="diff-waiting-time",

        # Упрощаем задачу: только выбор фазы
        fixed_ts=True,
        single_agent=True
    )

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=0.0003,
        batch_size=512,
        gamma=0.99,
        policy_kwargs=dict(net_arch=[256, 256]),
        device="cpu"
    )

    print(f"Начинаем СПЕЦ-ОБУЧЕНИЕ на сценарии {route_file}...")

    # 70,000 шагов хватит
    model.learn(total_timesteps=70000)

    print("Обучение завершено.")
    model.save("ppo_avenue_model")
    env.close()


if __name__ == "__main__":
    train()