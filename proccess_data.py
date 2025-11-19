import pandas as pd
import generate_routes

try:
    queue_df = pd.read_csv('baseline_queue.csv', delimiter=';')

    if 'lane_queueing_length' in queue_df.columns:
        avg_queue_length = queue_df['lane_queueing_length'].mean()
    else:
        avg_queue_length = "Столбец 'lane_queueing_length' не найден"

    tripinfo_df = pd.read_csv('baseline_tripinfo.csv', delimiter=';')

    if 'tripinfo_id' in tripinfo_df.columns:
        trip_count = len(tripinfo_df['tripinfo_id'])
    else:
        trip_count = "Столбец 'tripinfo_id' не найден"

    if 'tripinfo_waitingTime' in tripinfo_df.columns:
        avg_waiting_time = tripinfo_df['tripinfo_waitingTime'].mean()
    else:
        avg_waiting_time = "Столбец 'tripinfo_waitingTime' не найден"

    if 'tripinfo_arrival' in tripinfo_df.columns:
        max_arrival_time = tripinfo_df['tripinfo_arrival'].max()
    else:
        max_arrival_time = "Столбец 'tripinfo_arrival' не найден"

    emissions_df = pd.read_csv('baseline_emissions.csv', delimiter=';')

    if 'vehicle_CO2' in emissions_df.columns:
        total_co2_emissions = emissions_df['vehicle_CO2'].sum() / 1000000
    else:
        total_co2_emissions = "Столбец 'vehicle_CO2' не найден"

    with open('results.txt', 'w', encoding='utf-8') as f:
        f.write(f"Результаты анализа данных:{generate_routes.num_vehicles} Машин\n")
        f.write("="*30 + "\n")
        f.write(f"Средняя длина очереди: {avg_queue_length}\n")
        f.write(f"Общее количество поездок: {trip_count}\n")
        f.write(f"Среднее время ожидания: {avg_waiting_time}\n")
        f.write(f"Суммарные выбросы CO2: {total_co2_emissions}\n")
        f.write(f"Максимальное время прибытия: {max_arrival_time}\n")


    print("Обработка завершена. Результаты сохранены в файл 'results.txt'.")

except FileNotFoundError as e:
    print(f"Ошибка: Файл не найден - {e.filename}. Убедитесь, что все CSV-файлы находятся в той же папке, что и скрипт.")
except Exception as e:
    print(f"Произошла ошибка: {e}")