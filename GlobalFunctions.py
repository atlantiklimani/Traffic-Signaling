from collections import deque
from recordclass import recordclass

Street = recordclass('Street', [
    'id',
    'start',
    'end',
    'name',
    'duration',
    'driving_cars',
    'waiting_cars',
    'arrival_times',
    'departure_times'
])

Intersection = recordclass('Intersection', [
    'id',
    'incomings',
    'outgoings',
    'green_street',
    'num_waiting_cars',
    'schedule_duration',
    'using_streets',
    'streets_usage',
    'green_street_per_t_mod',
    'needs_updates'
])
Schedule = recordclass('Schedule', [
    'i_intersection',
    'order',
    'green_times'
])


def readInput(input_file_path):
    filename = "Instances/" + input_file_path

    with open(filename) as f:
        lines = deque(f.readlines())

    # Parse the first line
    total_duration, num_intersections, num_streets, \
    num_cars, bonus_points = map(int, lines.popleft().split())

    intersections = tuple(Intersection(id=i,
                                       incomings=deque(),
                                       outgoings=deque(),
                                       green_street=None,
                                       num_waiting_cars=None,
                                       green_street_per_t_mod=[],
                                       schedule_duration=None,
                                       using_streets=deque(),
                                       streets_usage=dict(),
                                       needs_updates=False)
                          for i in range(num_intersections))

    # Parse the streets
    streets = []
    name_to_street = {}
    for i_street in range(num_streets):
        line = lines.popleft().split()
        start, end = map(int, line[:2])
        name = line[2]
        duration = int(line[3])
        street = Street(id=i_street,
                        start=intersections[start],
                        end=intersections[end],
                        name=name,
                        duration=duration,
                        driving_cars={},
                        waiting_cars=deque(),
                        arrival_times={},
                        departure_times={})
        name_to_street[name] = street
        intersections[start].outgoings.append(street)
        intersections[end].incomings.append(street)
        streets.append(street)

    # Parse the paths
    paths = []
    for i_car in range(num_cars):
        line = lines.popleft().split()
        path_length = int(line[0])
        path = line[1:]
        assert len(path) == path_length
        for name in path:
            id_inter = name_to_street[name].end.id
            intersections[id_inter].using_streets.append(name)
            if name in intersections[id_inter].streets_usage:
                intersections[id_inter].streets_usage[name] += 1
            else:
                intersections[id_inter].streets_usage[name] = 1

        path = deque(name_to_street[name] for name in path)
        paths.append(path)
    for inter in intersections:
        #delete duplicates in using_streets array
        intersections[inter.id].using_streets = list(dict.fromkeys(intersections[inter.id].using_streets))
    return total_duration, bonus_points, intersections, \
           streets, name_to_street, paths

def reinit(streets, intersections):
    # Reinitialize mutable data structures
    for street in streets:
        street.driving_cars.clear()
        street.waiting_cars.clear()
        street.arrival_times.clear()
        street.departure_times.clear()

    for intersection in intersections:
        intersection.green_street = None
        intersection.num_waiting_cars = 0
        intersection.green_street_per_t_mod.clear()
        intersection.schedule_duration = None
        intersection.needs_updates = False


def grade(schedules, streets, intersections, paths, total_duration, bonus_points):
    reinit(streets, intersections) # we reset intersections and streets before performing a simulation

    #save path copies to reset them after performing the simulation
    paths_copy = [path.copy() for path in paths]

    # Iterate through the schedules and initialize the intersections.
    intersection_ids_with_schedules = set()
    for schedule in schedules:
        intersection = intersections[schedule.i_intersection]
        intersection_ids_with_schedules.add(intersection.id)
        first_street = streets[schedule.order[0]]
        intersection.green_street = first_street
        intersection.needs_updates = len(schedule.order) > 1
        schedule_duration = 0
        green_street_per_t_mod = intersection.green_street_per_t_mod
        for street_id in schedule.order:
            green_time = schedule.green_times[street_id]
            for _ in range(green_time):
                green_street_per_t_mod.append(streets[street_id])
            schedule_duration += green_time
        intersection.schedule_duration = schedule_duration

    # intersection_ids_with_waiting_cars is restricted to intersections
    # with schedules
    intersection_ids_with_waiting_cars = set()
    for i_car, path in enumerate(paths):
        street = path.popleft()
        street.waiting_cars.append(i_car)
        if street.end.id in intersection_ids_with_schedules:
            intersection_ids_with_waiting_cars.add(street.end.id)
        street.end.num_waiting_cars += 1

    street_ids_with_driving_cars = set()
    score = 0

    # Main simulation loop
    for t in range(total_duration):

        # Drive across intersections
        # Store the ids of intersections that don't have waiting cars after this.
        intersection_ids_to_remove = set()
        for i_intersection in intersection_ids_with_waiting_cars:
            intersection = intersections[i_intersection]

            if intersection.needs_updates:
                # Update the green street
                t_mod = t % intersection.schedule_duration
                intersection.green_street = intersection.green_street_per_t_mod[t_mod]

            green_street = intersection.green_street
            waiting_cars = green_street.waiting_cars
            if len(waiting_cars) > 0:
                # Drive across the intersection
                waiting_car = waiting_cars.popleft()
                green_street.departure_times[waiting_car] = t
                next_street = paths[waiting_car].popleft()
                next_street.driving_cars[waiting_car] = next_street.duration
                street_ids_with_driving_cars.add(next_street.id)

                intersection.num_waiting_cars -= 1
                if intersection.num_waiting_cars == 0:
                    intersection_ids_to_remove.add(i_intersection)

        intersection_ids_with_waiting_cars.difference_update(intersection_ids_to_remove)

        # Drive across roads
        # Store the ids of streets that don't have driving cars after this.
        street_ids_to_remove = set()
        for i_street in street_ids_with_driving_cars:
            street = streets[i_street]
            driving_cars = street.driving_cars
            for car in list(driving_cars):
                # Update the "time to live" of this car, i.e. the remaining
                # driving seconds.
                ttl = driving_cars[car]
                ttl -= 1
                if ttl < 0:
                    raise ValueError
                elif ttl == 0:
                    # Reached the end of the street
                    del driving_cars[car]
                    if len(paths[car]) == 0:
                        # car finished its path
                        score += bonus_points
                        score += total_duration - t - 1
                    else:
                        street.waiting_cars.append(car)
                        street.end.num_waiting_cars += 1
                        street.arrival_times[car] = t + 1
                        intersection_id = street.end.id
                        if intersection_id in intersection_ids_with_schedules:
                            intersection_ids_with_waiting_cars.add(intersection_id)
                else:
                    # The car is still driving on the street
                    driving_cars[car] = ttl
            if len(driving_cars) == 0:
                street_ids_to_remove.add(i_street)
        street_ids_with_driving_cars.difference_update(street_ids_to_remove)

    # The end of simulation, we reset the paths
    for i_path in range(len(paths)):
        paths[i_path] = paths_copy[i_path]
    return score

def printSchedule(schedules, streets):
    print(len(schedules))
    for schedule in schedules:
        print(schedule.i_intersection)
        print(len(schedule.order))
        for i in range(len(schedule.order)):
            print(streets[schedule.order[i]].name, schedule.green_times[schedule.order[i]])
