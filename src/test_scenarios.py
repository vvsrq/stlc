import os
import sys
import glob
import xml.etree.ElementTree as ET
import pandas as pd
from stable_baselines3 import PPO
from sumo_rl import SumoEnvironment

# Список сценариев
SCENARIOS = [
    {"name": "Легкий (500)", "route": "traffic_500.rou.xml"},
    {"name": "Средний (1500)", "route": "traffic_1500.rou.xml"},
    {"name": "Тяжелый (3000)", "route": "traffic_3000.rou.xml"}
]


def parse_sumo_stats(stats_file):
    """Функция для чтения XML статистики SUMO"""
    metrics = {
        "throughput": 0,
        "co2_kg": 0.0,
        "avg_wait": 0.0,
        "duration": 0.0
    }

    if not os.path.exists(stats_file):
        return metrics

    try:
        tree = ET.parse(stats_file)
        root = tree.getroot()

        # 1. Данные по поездкам (Пропускная способность, CO2, Ожидание)
        veh_stats = root.find("vehicleTripStatistics")
        if veh_stats is not None:
            # Пропускная способность (сколько машин доехало до финиша)
            metrics["throughput"] = int(veh_stats.get("count", 0))

            # CO2 (в мг -> переводим в кг)
            metrics["co2_kg"] = float(veh_stats.get("CO2_abs", 0)) / 1_000_000

            # Среднее время ожидания (waitingTime - это суммарное, делим на кол-во)
            # Либо берем duration, если waitingTime нет
            total_wait = float(veh_stats.get("waitingTime", 0))
            count = metrics["throughput"]
            if count > 0:
                metrics["avg_wait"] = total_wait / count
            else:
                metrics["avg_wait"] = 0

        # 2. Время выполнения
        perf_stats = root.find("performance")
        if perf_stats is not None:
            # Реальное время выполнения симуляции компьютером
            metrics["duration"] = float(perf_stats.get("realTime", 0))

    except Exception as e:
        print(f"Ошибка чтения XML {stats_file}: {e}")

    return metrics


def test_all():
    results = []

    print("Загрузка обученной модели...")
    try:
        model = PPO.load("ppo_avenue_model")
    except FileNotFoundError:
        print("Ошибка: Модель 'ppo_avenue_model.zip' не найдена.")
        return

    for scenario in SCENARIOS:
        print(f"\n--- Тестирование: {scenario['name']} ---")

        # Генерируем уникальные имена файлов для вывода
        base_name = scenario['route'].replace('.rou.xml', '')
        csv_output = f"outputs/test_{base_name}"
        xml_stats_output = f"outputs/stats_{base_name}.xml"

        # Удаляем старый XML если был
        if os.path.exists(xml_stats_output):
            os.remove(xml_stats_output)

        # Создаем среду
        # Важно: передаем additional_sumo_cmd, чтобы SUMO сохранил статистику в XML
        env = SumoEnvironment(
            net_file="../sim_configs/my_avenue.net.xml",
            route_file=scenario['route'],
            out_csv_name=csv_output,
            use_gui=True,  # Ставим False для скорости
            num_seconds=3600,
            min_green=5,
            max_green=60,
            delta_time=5,
            reward_fn="diff-waiting-time",
            single_agent=True,
            additional_sumo_cmd=f"--statistic-output {xml_stats_output}"
        )

        obs, info = env.reset()
        done = False

        # Запуск симуляции
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

        env.close()

        # --- СБОР ДАННЫХ ---

        # 1. Читаем CSV от sumo-rl (Очереди)
        avg_queue = 0
        search_path = f"{csv_output}_conn*.csv"
        files = glob.glob(search_path)
        if files:
            latest_file = max(files, key=os.path.getctime)
            df = pd.read_csv(latest_file)
            # Средняя длина очереди за всю симуляцию
            avg_queue = df['system_mean_stopped_vehicles'].mean()

        # 2. Читаем XML от SUMO (CO2, Пропускная способность, Время)
        xml_metrics = parse_sumo_stats(xml_stats_output)

        # Добавляем в отчет
        results.append({
            "Сценарий": scenario['name'],
            "Ср. очередь (машин)": round(avg_queue, 2),
            "Пропускная спос. (авто/час)": xml_metrics["throughput"],
            "Ср. ожидание (сек)": round(xml_metrics["avg_wait"], 2),
            "Выбросы CO2 (кг)": round(xml_metrics["co2_kg"], 2),
            "Время расчета (сек)": round(xml_metrics["duration"], 2)
        })

    # --- ВЫВОД ТАБЛИЦЫ ---
    print("\n" + "=" * 100)
    print(f"{'ИТОГОВЫЕ РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТА':^100}")
    print("=" * 100)

    df_res = pd.DataFrame(results)

    # Красивый вывод
    # Устанавливаем ширину колонок, чтобы все влезло
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'center')

    print(df_res.to_string(index=False))
    print("=" * 100)


if __name__ == "__main__":
    test_all()