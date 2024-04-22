from collections import deque
from recordclass import recordclass
import json 

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
    'needs_updates',
    'pedestrian_phase_interval',
    'all_red_phase_interval',
    'constraints'
])
Schedule = recordclass('Schedule', [
    'i_intersection',
    'order',
    'green_times'
])

def readSolution(solution_file_path, streets):
    
    with open(solution_file_path) as f:
        lines = deque(f.readlines())
    
    num_intersections = int(lines.popleft())
    
    schedules = []
    for i in range(0,num_intersections):
        i_intersection = int(lines.popleft())
        num_streets = int(lines.popleft())
        order = []
        green_times = {}
        for j in range(0, num_streets):
            street_name, green_time_str = lines.popleft().split()
            green_time = int(green_time_str)
            
            street_id = None
            for street in streets:
                if street.name == street_name:
                    street_id = street.id
                    break

            order.append(street_id)
            green_times[street_id] = green_time

        schedules.append(Schedule(i_intersection=i_intersection,
                                order=order,
                                green_times=green_times))
    
    return schedules

def readInput(input_file_path):
    # filename = "Instances/" + input_file_path
    filename = "input/" + input_file_path

    f = open(filename, 'r')

    json_file = json.load(fp=f)

    total_duration = json_file['simulation']['duration']
    num_intersections = json_file['simulation']['intersections']
    num_streets = json_file['simulation']['streets']
    num_cars = json_file['simulation']['cars']
    bonus_points = json_file['simulation']['bonus']
    duration_to_pass_through_an_intersection = json_file['simulation']['duration_to_pass_through_an_intersection']
    yellow_phase = json_file['simulation']['yellow_phase']
    limit_on_minimum_cycle_length = json_file['simulation']['limit_on_minimum_cycle_length']
    limit_on_maximum_cycle_length = json_file['simulation']['limit_on_maximum_cycle_length']
    limit_on_minimum_green_phase_duration = json_file['simulation']['limit_on_minimum_green_phase_duration']
    limit_on_maximum_green_phase_duration = json_file['simulation']['limit_on_maximum_green_phase_duration']
    intersections = tuple(Intersection(id=inter['name'],
                                       incomings=deque(),
                                       outgoings=deque(),
                                       green_street=None,
                                       num_waiting_cars=None,
                                       green_street_per_t_mod=[],
                                       schedule_duration=None,
                                       using_streets=deque(),
                                       streets_usage=dict(),
                                       needs_updates=False,
                                       pedestrian_phase_interval=inter['pedestrian_phase_interval'],
                                       all_red_phase_interval=inter['all_red_phase_interval'],                                            
                                       constraints={})
                        for inter in json_file['intersections'])
                        #   for i in range(num_intersections))
                        
    # Parse the streets
    streets = []
    name_to_street = {}
    # for i_street in range(num_streets):
    for i_street in range(0, len(json_file['streets'])): 
        s = json_file['streets'][i_street]       
        start = s['start']
        end = s['end']
        name = s['name']
        duration = s['time']

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
        path_length = json_file['cars'][i_car]['path_length']
        path = json_file['cars'][i_car]['path']

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
    
    for constraint in json_file['constraints']:
        intersection = intersections[constraint['intersection_name']]
        if (constraint['type'] == 'simultaneously_signal'):
            if ('simultaneously_signal' in intersection.constraints):
                intersection.constraints['simultaneously_signal'].append(constraint['streets'])
            else:
                intersection.constraints['simultaneously_signal'] = [constraint['streets']]
        elif (constraint['type'] == 'signal_phase_order'):
            intersection.constraints['signal_phase_order'] = constraint['streets']
            # if ('signal_phase_order' in intersection.constraints):
            #     intersection.constraints['signal_phase_order'].append(constraint['streets'])
            # else:
            #     intersection.constraints['signal_phase_order'] = [constraint['streets']]

    for inter in intersections:
        #delete duplicates in using_streets array
        intersections[inter.id].using_streets = list(dict.fromkeys(intersections[inter.id].using_streets))
    return total_duration, bonus_points, intersections, \
           streets, name_to_street, paths, duration_to_pass_through_an_intersection, \
        yellow_phase,limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, \
        limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration

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


def grade(schedules, streets, intersections, paths, total_duration, bonus_points, yellow_phase):
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
                intersection.green_street = None
                if(t_mod + yellow_phase < len(intersection.green_street_per_t_mod)):
                    if(intersection.green_street_per_t_mod[t_mod + yellow_phase].id == intersection.green_street_per_t_mod[t_mod].id):
                        intersection.green_street = intersection.green_street_per_t_mod[t_mod]

            if(intersection.green_street is None):
                green_streets = []
            else:
                green_street = intersection.green_street
                green_streets = [green_street]
                if ('simultaneously_signal' in intersection.constraints):
                    for group_street in intersection.constraints['simultaneously_signal']:
                        for i_street_in_group in range(0, len(group_street)):
                            if green_street == group_street[i_street_in_group]:
                                green_street = group_street[i_street_in_group:]
                        # if green_street == group_street[0]:
                        #     green_streets = [*group_street]

            for street in green_streets:  
                waiting_cars = street.waiting_cars
                if len(waiting_cars) > 0:
                    # Drive across the intersection
                    waiting_car = waiting_cars.popleft()
                    street.departure_times[waiting_car] = t
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

def assertOrder(actual, constraint, name_to_i_street):
    indices = [actual.index(name_to_i_street[c].id) if name_to_i_street[c].id in actual else -1 for c in constraint]
    # indices = [x for x in indices if x != -1]
    print('Schedule Order: ', actual, '. Schedule Constraints: ', constraint)

    for i in range(0,len(indices)):
        if indices[i] != -1:
            indices = indices[i:]

    for i in range(len(indices) - 1, 0):
        if indices[i] != -1:
            indices = indices[:i]        

    if indices == sorted(indices):
        return True
    else:
        return False

def assertOrderPhaseForSolution(schedules, intersections, name_to_i_street):
    for schedule in schedules:
        if 'signal_phase_order' in intersections[schedule.i_intersection].constraints: 
            if (assertOrder(
                schedule.order, 
                intersections[schedule.i_intersection].constraints['signal_phase_order'],
                name_to_i_street) == False
            ):
                return False
    return True

def assertOrderPhaseForSchedule(schedule, intersections, name_to_i_street):
    if 'signal_phase_order' in intersections[schedule.i_intersection].constraints:
        if (assertOrder(
            schedule.order, 
            intersections[schedule.i_intersection].constraints['signal_phase_order'],
            name_to_i_street) == False
        ):
            return False
    return True

def printSchedule(schedules, streets):
    print(len(schedules))
    for schedule in schedules:
        print(schedule.i_intersection)
        print(len(schedule.order))
        for i in range(len(schedule.order)):
            print(streets[schedule.order[i]].name, schedule.green_times[schedule.order[i]])

def getPrintedSchedule(schedules, streets):
    result = f'{len(schedules)}\n'
    # print(len(schedules))
    for schedule in schedules:
        # print(schedule.i_intersection)
        # print(len(schedule.order))
        result += f'{schedule.i_intersection}\n'
        result += f'{len(schedule.order)}\n'
        for i in range(len(schedule.order)):
            # print(streets[schedule.order[i]].name, schedule.green_times[schedule.order[i]])
            result += f'{streets[schedule.order[i]].name} {schedule.green_times[schedule.order[i]]}\n'
    
    return result
