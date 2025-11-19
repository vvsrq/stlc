import random


def generate_routefile(seed, output_filename="avenue_traffic_generated.rou.xml"):
    """
    Генерирует файл маршрутов .rou.xml со случайными поездками (trips)
    для сложной дорожной сети "my_avenue.net.xml".
    """
    random.seed(seed)

    # --- НАСТРОЙКИ СИМУЛЯЦИИ (Можете изменять эти значения) ---
    num_vehicles = 1200  # Общее количество машин (сделайте больше, чтобы создать пробку)
    num_pedestrians = 250  # Общее количество пешеходов
    sim_duration = 3600  # Длительность симуляции в секундах (1 час)

    # --- ОПРЕДЕЛЕНИЕ МАРШРУТОВ ДЛЯ ВАШЕЙ НОВОЙ СЕТИ ---
    # Мы определяем крайние точки въезда и выезда, а также съезды/заезды на перекрестках.
    # SUMO сам найдет кратчайший путь между этими точками.

    # 1. Основные сквозные маршруты (главный трафик)
    main_routes = [
        ('E4', 'E22'),  # С запада на восток (сквозной)
        ('E23', 'E5')  # С востока на запад (сквозной)
    ]

    # 2. Локальные маршруты (создают "шум" и усложняют задачу)
    local_routes = [
        ('E2', '-E3'),  # Пересечение J1 с севера на юг
        ('-E3', 'E2'),  # Пересечение J1 с юга на север
        ('E11', 'E5'),  # Въезд с севера на J11 и поворот налево на запад
        ('E4', 'E25'),  # Движение с запада и съезд на юг на J19
        ('E24', 'E20'),  # Въезд с севера на J19 и поворот направо на запад
        ('E2', 'E22')  # Въезд с севера на J1 и поворот направо на восток
    ]

    # Объединяем все возможные маршруты для машин
    # Мы даем основным маршрутам больший "вес", чтобы они встречались чаще
    all_car_routes = main_routes * 5 + local_routes

    # Маршруты для пешеходов (используем те же крайние точки для простоты)
    ped_routes = [
        ('E2', '-E3'), ('-E3', 'E2'),
        ('E4', 'E5'), ('E23', 'E22')
    ]

    # --- ГЕНЕРАЦИЯ ПОЕЗДОК (TRIPS) ---
    trips = []

    # Генерируем машины
    for i in range(num_vehicles):
        # Выбираем случайный маршрут (откуда и куда)
        from_edge, to_edge = random.choice(all_car_routes)
        # Выбираем случайное время старта
        depart_time = random.uniform(0, sim_duration - 100)
        # Добавляем поездку в список
        trips.append((depart_time,
                      f'    <trip id="veh_{i}" type="car" from="{from_edge}" to="{to_edge}" depart="{depart_time:.2f}" />'))

    # Генерируем пешеходов
    for i in range(num_pedestrians):
        from_edge, to_edge = random.choice(ped_routes)
        depart_time = random.uniform(0, sim_duration - 100)
        trips.append((depart_time,
                      f'    <person id="ped_{i}" depart="{depart_time:.2f}"><walk from="{from_edge}" to="{to_edge}"/></person>'))

    # Сортируем все поездки по времени старта (важно для SUMO)
    trips.sort()

    # --- ЗАПИСЬ ФАЙЛА ---
    with open(output_filename, "w") as routes:
        print("""<routes>
    <!-- Тип транспортного средства -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" maxSpeed="16.67" />
    """, file=routes)

        # Записываем отсортированные поездки в файл
        for _, trip_line in trips:
            print(trip_line, file=routes)

        print("</routes>", file=routes)


if __name__ == "__main__":
    # Вызываем функцию с фиксированным seed для воспроизводимости результатов
    generate_routefile(seed=42)
    print("Файл 'avenue_traffic_generated.rou.xml' успешно создан.")