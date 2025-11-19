import pandas as pd
import xml.etree.ElementTree as ET
import glob
import os


def print_metrics():
    print("=" * 40)
    print("       РЕЗУЛЬТАТЫ СИМУЛЯЦИИ")
    print("=" * 40)

    # --- 1. Читаем данные из CSV (созданного sumo-rl) ---
    # Находим последний файл CSV
    list_of_files = glob.glob('outputs/final_result*.csv')
    if list_of_files:
        latest_csv = max(list_of_files, key=os.path.getctime)
        df = pd.read_csv(latest_csv)

        # Считаем среднюю длину очереди (system_mean_stopped_vehicles)
        # Это среднее количество стоящих машин в любой момент времени
        avg_queue = df['system_mean_stopped_vehicles'].mean()
        print(f"1. Средняя длина очереди:   {avg_queue:.2f} машин (одновременно)")
    else:
        print("1. Средняя длина очереди:   Нет данных (CSV не найден)")

    # --- 2. Читаем данные из XML (созданного самим SUMO) ---
    stats_file = "outputs/sumo_stats.xml"

    if os.path.exists(stats_file):
        tree = ET.parse(stats_file)
        root = tree.getroot()

        # Ищем тег <vehicles> внутри <vehicleTripStatistics>
        # В разных версиях SUMO структура может чуть отличаться, ищем атрибуты
        # Обычно это <vehicleTripStatistics>
        veh_stats = root.find("vehicleTripStatistics")

        if veh_stats is not None:
            # Пропускная способность (сколько машин закончило маршрут)
            finished = int(veh_stats.get("count", 0))
            print(f"2. Пропускная способность:  {finished} машин (за час)")

            # Среднее время ожидания (duration - routeLength / speed... но проще взять waitingTime)
            wait_time = float(veh_stats.get("waitingTime", 0))
            print(f"3. Среднее время ожидания:  {wait_time:.2f} сек")

        else:
            print("2. Пропускная способность:  Ошибка чтения XML")
            print("3. Среднее время ожидания:  Ошибка чтения XML")

        # Экология
        # Обычно находится в теге <vehicleTripStatistics> или корне,
        # но чаще всего глобальные выбросы в самом низу в теге с итогами, но проще взять сумму из tripinfo если этого нет.
        # В statistic-output есть общие выбросы

        # Попробуем найти тег <vehicleTripStatistics> атрибут 'CO2_abs' (в миллиграммах)
        if veh_stats is not None:
            co2_mg = float(veh_stats.get("CO2_abs", 0))
            co2_kg = co2_mg / 1_000_000  # переводим в кг
            print(f"4. Общие выбросы CO2:       {co2_kg:.2f} кг")
        else:
            print("4. Общие выбросы CO2:       Нет данных")

        # Общее время симуляции
        # Берется из конфига или duration
        # В statistic-output есть 'duration'
        perf_stats = root.find("performance")
        if perf_stats is not None:
            duration = float(perf_stats.get("duration", 0)) / 1000  # оно в мс
            # Или просто возьмем реальное время моделирования из clock
            real_time = float(perf_stats.get("realTime", 0))
            print(f"5. Общее время симуляции:   {real_time:.2f} сек (реального времени)")
            print(f"   (Виртуальное время):     3600 сек")
        else:
            print("5. Общее время симуляции:   3600 сек")

    else:
        print("\n[!] Файл 'outputs/sumo_stats.xml' не найден.")
        print("Убедитесь, что вы добавили <output> в .sumocfg и запустили run_simulation.py")

    print("=" * 40)


if __name__ == "__main__":
    print_metrics()