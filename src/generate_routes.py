import random

def generate_routefile(seed):
    random.seed(seed)

    global num_vehicles
    num_vehicles = 500
    num_pedestrians = 600
    sim_duration = 3600

    trips = []

    car_routes = [
        ('N_in', 'S_out'), ('S_in', 'N_out'),
        ('W_in', 'E_out'), ('E_in', 'W_out')
    ]
    for i in range(num_vehicles):
        from_edge, to_edge = random.choice(car_routes)
        depart_time = random.uniform(0, sim_duration - 100)
        trips.append((depart_time,
                      f'    <trip id="veh_{i}" type="car" from="{from_edge}" to="{to_edge}" depart="{depart_time:.2f}" />'))

    ped_routes = [('N_in', 'S_out'), ('W_in', 'E_out'), ('S_in', 'N_out'), ('E_in', 'W_out')]
    for i in range(num_pedestrians):
        from_edge, to_edge = random.choice(ped_routes)
        depart_time = random.uniform(0, sim_duration - 100)
        trips.append((depart_time,
                      f'    <person id="ped_{i}" depart="{depart_time:.2f}"><walk from="{from_edge}" to="{to_edge}"/></person>'))

    trips.sort()
    with open("../sim_configs/evaluation_routes.rou.xml", "w") as routes:
        print("""<routes>
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" maxSpeed="35"/>
    """, file=routes)

        for _, trip_line in trips:
            print(trip_line, file=routes)

        print("</routes>", file=routes)


if __name__ == "__main__":
    generate_routefile(seed=42)
    print("Файл 'evaluation_routes.rou.xml' с машинами и пешеходами успешно создан.")