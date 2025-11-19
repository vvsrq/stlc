from stable_baselines3 import DQN
from sumo_rl import SumoEnvironment
import traci


def throughput_only_reward(traffic_signal):
    reward = traci.simulation.getArrivedNumber()

    return float(reward)

# --- ОСНОВНОЙ КОД ---

if __name__ == '__main__':
    # --- 1. СОЗДАНИЕ СРЕДЫ С ОДНИМ ВАЖНЫМ ПАРАМЕТРОМ ---
    env = SumoEnvironment(
        net_file='intersection.net.xml',
        route_file='training_routes.rou.xml',
        single_agent=True,
        use_gui=False,
        num_seconds=10000,

        # ИЗМЕНЕНИЕ ЗДЕСЬ:
        # Вместо строки 'diff-waiting-time' передаем нашу функцию
        reward_fn='diff-waiting-time',

        delta_time=5
    )

    # --- 2. СОЗДАНИЕ МОДЕЛИ АГЕНТА (без изменений) ---
    model = DQN(
        policy='MlpPolicy',
        env=env,
        verbose=1,
        learning_rate=1e-4,
        gamma=0.99,
    )

    # --- 3. ОБУЧЕНИЕ МОДЕЛИ (без изменений) ---
    model.learn(total_timesteps=20000)

    # --- 4. СОХРАНЕНИЕ МОДЕЛИ (без изменений) ---
    model.save("dqn_model")
    print("======================================================")
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО. МОДЕЛЬ СОХРАНЕНА В ФАЙЛ 'dqn_model.zip'")
    print("======================================================")

    env.close()