import math
import os
import random
import string
import sys
from copy import deepcopy
from random import choices
from time import time

import numpy as np
from recordclass import recordclass

import GlobalFunctions as gl

Schedule = recordclass('Schedule', [
    'i_intersection',
    'order',
    'green_times'
])

def randomSolution(intersections):
    schedules = []
    for intersection in intersections:
        order = []
        green_times = {}
        for i in range(len(intersection.incomings)):
            green_time = choices([1, 2], weights=[90, 10], k=1)
            street = intersection.incomings[i]
            if street.name in intersection.using_streets:
                order.append(street.id)
                green_times[street.id] = int(green_time[0])
        if len(order) > 0:
            schedule = Schedule(i_intersection=intersection.id,
                                order=order,
                                green_times=green_times)
            schedules.append(schedule)
    return schedules


def sortKey(e):
    return e.score


class Patch:
    def __init__(self, score, scout, cars, avg):
        self.score = score
        self.scout = scout
        self.cars = cars
        self.avg = avg
        self.stgLim = 0
        self.employees = 0
        self.stg = True


def changeGreenTimeDuration(schedule, numberOfIntersection, numberOfRoads, limit_on_minimum_green_phase_duration,
                            limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                            limit_on_maximum_cycle_length, i_id_to_intersection,
                            increase_green_time):
    constant = 15
    if (numberOfIntersection <= 0):
        return schedule

    count = 0
    if len(schedule) - numberOfIntersection - 1>=0:
        randomRangeBegins = random.randint(0, len(schedule) - numberOfIntersection - 1)
    else:
        randomRangeBegins=0
    while (count < numberOfIntersection):
        rand = random.randint(randomRangeBegins, randomRangeBegins + numberOfIntersection-1)
        length = len(schedule[rand].order)
        otherCount = 0
        while (otherCount < length and otherCount < numberOfRoads):
            semaforId = random.randint(0, length - 1)
            initial = schedule[rand].green_times[schedule[rand].order[semaforId]]
            # while True:
            loop_upper_limit = 100
            for i in range(0, loop_upper_limit):
                current_green_time = schedule[rand].green_times[schedule[rand].order[semaforId]]
                probabilty_for_increase = 0.8 if increase_green_time else 0.2
                sign = 1 if random.random() < probabilty_for_increase else -1
                new_green_time = current_green_time + sign* random.randint(1, constant)
                # print("new_green_time: "+str(new_green_time))
                if (new_green_time < limit_on_minimum_green_phase_duration):
                    new_green_time = limit_on_minimum_green_phase_duration
                elif (new_green_time > limit_on_maximum_green_phase_duration):
                    new_green_time = limit_on_maximum_green_phase_duration
                schedule[rand].green_times[schedule[rand].order[semaforId]] = new_green_time
                # schedule[rand].green_times[schedule[rand].order[semaforId]] = random.randint(limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration)
                if (len(schedule[rand].green_times) <= 1):
                    break
                intersectionCycle = i_id_to_intersection[schedule[rand].i_intersection]['pedestrian_phase_interval']
                intersectionCycle += i_id_to_intersection[schedule[rand].i_intersection]['all_red_phase_interval']
                for x in schedule[rand].green_times.values():
                    intersectionCycle += x
                if (
                        intersectionCycle >= limit_on_minimum_cycle_length and intersectionCycle <= limit_on_maximum_cycle_length):
                    break
                # print("Phase Green Time Boundaries Not Correct - Change Green Time")

                if (i == loop_upper_limit - 1):
                    schedule[rand].green_times[schedule[rand].order[semaforId]] = initial
            otherCount += 1
        count += 1

    return schedule


def shuffleOrder(schedules, numberOfIntersection, intersections, name_to_i_street):
    if (numberOfIntersection <= 0):
        return schedules

    count = 0

    while (count < numberOfIntersection):
        rand = random.randint(0, len(schedules) - 1)

        schedules[rand] = shuffleSingleOrder(schedules[rand], intersections, name_to_i_street)

        count += 1

    return schedules


def shuffleSingleOrder(schedule, intersections, name_to_i_street):
    random.shuffle(schedule.order)
    if 'signal_phase_order' in intersections[schedule.i_intersection].constraints:
        if (not gl.assertOrderPhaseForSchedule(schedule, intersections, name_to_i_street)):
            # max_val = len(intersections[schedule.i_intersection].incomings) - len(intersections[schedule.i_intersection].constraints['signal_phase_order'])
            # rand_index = random.randint(0, max_val)
            rand_index = 0
            for street in intersections[schedule.i_intersection].constraints['signal_phase_order']:
                street_id = name_to_i_street.get(street).id
                index = schedule.order.index(street_id)
                temp_val = schedule.order[rand_index]
                schedule.order[rand_index] = schedule.order[index]
                schedule.order[index] = temp_val
                rand_index += 1

        # print('Shuffle Single Order.')
        if (not gl.assertOrderPhaseForSchedule(schedule, intersections, name_to_i_street)):
            raise Exception("Order Not Attained")

    return schedule


def swapOrder(schedules, numberOfIntersections, intersections, name_to_i_street):
    if (numberOfIntersections <= 0):
        return schedules
    for i in range(0, numberOfIntersections):
        rand = random.randint(0, len(schedules) - 1)
        incomingStreetsLength = len(schedules[rand].order)
        if (incomingStreetsLength == 1):
            continue
        initial_order = [*schedules[rand].order]
        upper_loop_limit = 100
        for i in range(0, upper_loop_limit):
            # print("Applying Swap")
            rand1 = random.randint(0, incomingStreetsLength - 1)
            rand2 = random.randint(0, incomingStreetsLength - 1)
            while (rand1 == rand2):
                rand2 = random.randint(0, incomingStreetsLength - 1)
            temp = schedules[rand].order[rand1]
            schedules[rand].order[rand1] = schedules[rand].order[rand2]
            schedules[rand].order[rand2] = temp
            if (gl.assertOrderPhaseForSchedule(schedules[rand], intersections, name_to_i_street)):
                break
            if (i == upper_loop_limit - 1):
                schedules[rand].order = initial_order
        # print("Phase Order Not Correct - Swap - Initial Order Returned")

    return schedules


def copyScheduleArray(scheduleArr):
    newScheduleArr = []
    for i in range(0, len(scheduleArr)):
        newScheduleArr.append(
            Schedule(
                i_intersection=scheduleArr[i].i_intersection,
                order=deepcopy(scheduleArr[i].order),
                green_times=deepcopy(scheduleArr[i].green_times))
        )

    return newScheduleArr


def scale_list(original_map: dict, n_min, n_max, sum_min, sum_max):
    if (len(original_map.values()) == 0):
        return original_map

    current_min = min(original_map.values())
    current_max = max(original_map.values())

    scaling_factor = (n_max - n_min)

    if (current_min != current_max):
        scaling_factor = (n_max - n_min) / (current_max - current_min)

    for key in original_map:
        original_map[key] = int(n_min + (original_map[key] - current_min) * scaling_factor)

    scaled_sum = sum(original_map.values())

    if scaled_sum < sum_min:
        scaling_factor = 1.1
    elif scaled_sum > sum_max:
        scaling_factor = 0.9

    while scaled_sum < sum_min or scaled_sum > sum_max:
        current_min = min(original_map.values())
        if scaled_sum < sum_min:
            scaling_factor *= 1.1
        elif scaled_sum > sum_max:
            scaling_factor *= 0.9

        for key in original_map:
            original_map[key] = int(n_min + (original_map[key] - n_min) * scaling_factor)
            if scaled_sum < sum_min and original_map[key] == n_min:
                original_map[key] += 1
        scaled_sum = sum(original_map.values())

    return original_map


def transform_array(arr, limit_cycle):
    # First, scale the numbers so they are between 15 and 70
    arr_scaled = 15 + arr * 55

    # Then, adjust the sum to be between 60 and 120
    sum_arr = np.sum(arr_scaled)
    if sum_arr < 60:
        arr_scaled = arr_scaled * (60 / sum_arr)
    elif sum_arr > limit_cycle:
        arr_scaled = arr_scaled * (limit_cycle / sum_arr)
        # print("arr scaled", arr_scaled)

    # Convert the array to integers
    arr_scaled = np.round(arr_scaled).astype(int)

    return arr_scaled


def adjust_array(arr):
    change = random.randint(3, 8)
    # Make sure the array has at least two elements
    if len(arr) < 2:
        return arr

    # Choose two random indices in the array
    indices = np.random.choice(len(arr), 2, replace=False)

    # Increase one number and decrease the other
    arr[indices[0]] += change
    arr[indices[1]] -= change

    # Check if the numbers are within the desired range
    if arr[indices[0]] < 15 or arr[indices[0]] > 70 or arr[indices[1]] < 15 or arr[indices[1]] > 70:
        arr[indices[0]] -= change  # undo the change
        arr[indices[1]] += change  # undo the change

    return arr


def traffic_based_initial_solution(intersections: list[gl.Intersection], limit_on_minimum_green_phase_duration: int,
                                   limit_on_maximum_green_phase_duration: int, limit_on_minimum_cycle_length: int,
                                   limit_on_maximum_cycle_length: int, name_to_i_street) -> list[Schedule]:
    schedules = []

    # Calculate the global threshold first for efficiency
    all_waiting_cars = [len(street.waiting_cars) for intersection in intersections for street in intersection.incomings]
    threshold = sum(all_waiting_cars) / len(all_waiting_cars)

    for intersection in intersections:
        order = []
        green_times = {}

        # Sort streets based on the sum of lengths of driving_cars and waiting_cars
        if 'simultaneously_signal' in intersection.constraints:
            street_group_traffic = {}
            streets = []
            street_mps = [group[0] for group in intersection.constraints['simultaneously_signal']]

            for street in street_mps:
                street_group_traffic[street] = 0
                streets.append(name_to_i_street.get(street))
            for street in intersection.incomings:
                for group in intersection.constraints['simultaneously_signal']:
                    if street in group:
                        street_obj = name_to_i_street.get(street)
                        street_group_traffic[group[0]] += len(street_obj.driving_cars) + len(street_obj.waiting_cars)
            sorted_streets = sorted(streets, key=lambda s: street_group_traffic.get(s.name, 0), reverse=True)

            for street in sorted_streets:
                order.append(street.id)

            street_usage = {
                street: usage
                for street, usage in street_group_traffic.items()
            }

            total_usage = sum(list(street_usage.values()))

            propotions = []
            for _usage in list(street_usage.values()):
                if total_usage == 0:
                    propotions.append(1 / len(list(street_usage.values())))
                else:
                    propotions.append(_usage / total_usage)

            green_times = transform_array(np.array(propotions),
                                          limit_on_maximum_cycle_length - intersection.pedestrian_phase_interval - intersection.all_red_phase_interval)

            green_times = adjust_array(green_times)

            green_time_dict = dict()
            for _order, _green_time in zip(order, green_times):
                green_time_dict[_order] = int(_green_time)

            # print('Green Times: ',green_time_dict)
            # print("Order: ", order)
            # if sum(green_time_dict.values()) > 120:
            #     print("Times: ", green_times, " SUM: ", sum(green_times))

        if order:
            # schedules.append(Schedule(intersection.id, order, green_times,intersection.pedestrian_phase,intersection.all_red_phase))
            schedules.append(Schedule(intersection.id, order, green_time_dict))
    return schedules


def usage_based_initial_solution(intersections: list[gl.Intersection], limit_on_minimum_green_phase_duration: int,
                                 limit_on_maximum_green_phase_duration: int, limit_on_minimum_cycle_length: int,
                                 limit_on_maximum_cycle_length: int, name_to_i_street) -> list[Schedule]:
    schedules = []
    for intersection in intersections:
        order = []
        green_times = {}
        total_green_time = 0

        if 'simultaneously_signal' in intersection.constraints:
            street_group_usage = {}
            streets = []
            street_mps = [group[0] for group in intersection.constraints['simultaneously_signal']]

            ## for street in intersection.constraints['signal_phase_order']:
            for street in street_mps:
                street_group_usage[street] = 0
                streets.append(name_to_i_street.get(street))
            for street in intersection.incomings:
                for group in intersection.constraints['simultaneously_signal']:
                    if street in group:
                        street_group_usage[group[0]] += intersection.streets_usage.get(street.name, 0)
            intersection.streets_usage = street_group_usage
            sorted_streets = sorted(streets, key=lambda s: intersection.streets_usage.get(s.name, 0), reverse=True)
        else:
            sorted_streets = []
        #     sorted_streets = sorted(intersection.incomings, key=lambda s: intersection.streets_usage.get(s.name, 0),
        #                         reverse=True)

        for street in sorted_streets:
            # if street.name in intersection.using_streets:
            order.append(street.id)
            usage = intersection.streets_usage.get(street.name, 0)
            # green_time = int(math.sqrt(usage)) if usage > 0 else 1
            green_time = min(max(limit_on_minimum_green_phase_duration, int(math.sqrt(usage))),
                             limit_on_maximum_green_phase_duration)
            green_times[street.id] = green_time
            total_green_time += green_times[street.id]
        # Apply minimum and maximum constraints on total green time for the intersection
        total_green_time = total_green_time - intersection.pedestrian_phase_interval - intersection.all_red_phase_interval

        total_green_time = max(min(total_green_time, limit_on_minimum_cycle_length), limit_on_maximum_cycle_length)

        # Normalize green times to fit within the min and max constraints
        green_time_sum = sum(green_times.values())
        if total_green_time > 0:
            for street_id in green_times:
                green_times[street_id] = int(green_times[street_id] * (total_green_time / sum(green_times.values())))

        # Enforce minimum and maximum for individual street green times
        for street_id in green_times:
            green_times[street_id] = max(min(green_times[street_id], limit_on_maximum_green_phase_duration),
                                         limit_on_minimum_green_phase_duration)

        if order:
            # schedules.append(Schedule(intersection.id, order, green_times,intersection.pedestrian_phase,intersection.all_red_phase))
            schedules.append(Schedule(intersection.id, order, green_times))
    return schedules


def generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration,
                     limit_on_maximum_green_phase_duration):
    # while True:
    decideGen = random.randint(0, 1)
    # decideGen = 0
    if (decideGen == 0):
        solution = traffic_based_initial_solution(intersections, limit_on_minimum_green_phase_duration,
                                                  limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                                                  limit_on_maximum_cycle_length, name_to_i_street)
    else:
        solution = usage_based_initial_solution(intersections, limit_on_minimum_green_phase_duration,
                                                limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                                                limit_on_maximum_cycle_length, name_to_i_street)

    for i in range(0, len(solution)):
        schedule = solution[i]
        while (not gl.assertOrderPhaseForSchedule(schedule, intersections, name_to_i_street)):
            solution[i] = shuffleSingleOrder(schedule, intersections, name_to_i_street)
            print("Phase Order Not Correct - Generate Solution")

        # break
    return solution


def outputToFile(patches, executionTime, countIterations, ns, nb, ne, nrb, nre, stgLim, initialShrinkageFactor,
                 shrinkageFactorReducedBy, shrinkageFactor, start,completed_cars,avg_cars,score):
    global file

    if not os.path.exists(f'output/{file}'):
        os.mkdir(f'output/{file}')

    code = "".join(random.choices(string.ascii_lowercase, k=3))
    output = open(f'output/{file}/{file}_{patches[0].score}_{code}', 'a')
    output.write(
        f'Parameters:\nns - {ns}, nb - {nb}, ne - {ne}, nrb - {nrb}, nre - {nre},\nStagnation limit - {stgLim}\nInitial shrinkage factor - {initialShrinkageFactor}, Shrinkage Factor per Iteration Reduced by - {shrinkageFactorReducedBy}, Termianl shrinkage factor - {shrinkageFactor:.3f}'
        f'\nExecution Time - {executionTime}, Number of loop iterations - {countIterations}\n')
    for i in range(0, 10):
        output.write(f'Score of patch: ,{patches[i].score}\n')
    output.write(f'Real Execution Time: {time() - start}\n')
    output.write("------------------------- Output File Begins Here -------------------------------------\n")
    output.write(gl.getPrintedSchedule(patches[0].scout, streets=streets))
    output.close()

    gl.print_json_solution(patches=patches, schedules=patches[0].scout, streets=streets, intersections=intersections,
                           file=file, code=code,completed_cars=completed_cars,avg_cars=avg_cars,score=score)

    return


def BeeHive(streets, intersections, paths, total_duration, bonus_points, terminated_time, yellow_phase,
            name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration,
            limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light,
            i_id_to_intersection, use_seed=True, solution_file_path=None):
    patches = []
    ns = 20  # number of scout bees
    nb = 10  # number of best sites
    ne = 5  # number of elite sites
    nrb = 10  # number of recruited bees for best sites
    nre = 15  # number of recruited bees for elite sites
    stgLim = 10  # stagnation limit for patches
    shrinkageFactor = 0.8  # how fast does the neighborhood shrink. 1 is max. This higher the factor the less is the neighborhood shrinking
    shrinkageFactorReducedBy = 0.99  # by how much is the shrinkage factor reduceb by for iteration
    executionTime =  180  # 8 * 60 * 60
    ## Only for visualisation purposes
    initialShrinkageFactor = shrinkageFactor
    countIterations = 0
    ## Extra parameters
    increase_green_time=True
    increase_green_time_alternate_frequency=10


    for i in range(0, ns):
        if (use_seed == 'True' and i < 5):
            sol = gl.readSolution(solution_file_path=solution_file_path, streets=streets)
            if i != 0:
                sol = shuffleOrder(sol, math.floor(len(intersections) * 0.2) + 1, intersections, name_to_i_street)
        else:
            sol = generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration,
                                   limit_on_maximum_green_phase_duration)

        grade, completed_cars, avg_cars = gl.grade(sol, streets, intersections, paths, total_duration, bonus_points,
                                                   yellow_phase, duration_to_pass_through_a_traffic_light)
        patches.append(Patch(grade, sol, cars=completed_cars, avg=avg_cars))
    while (time() - terminated_time < executionTime):
        patches.sort(reverse=True, key=sortKey)
        patches = patches[0: ns]

        # outputToFile(patches, executionTime, countIterations, ns, nb, ne, nrb, nre, stgLim, initialShrinkageFactor,
        #             shrinkageFactorReducedBy, shrinkageFactor, start)

        # return patches[0].scout, patches[0].score, patches[0].cars, patches[0].avg

        for i in range(0, nb):
            employees = 0
            if (i < ne):
                employees = nre
                patches[i].employees = nre
            else:
                employees = nrb
                patches[i].employees = nrb

            patches[i].stg = True

            for e in range(0, employees):
                tempSchedule = copyScheduleArray(patches[i].scout)
                decideOperator = random.randint(0, 30)
                if (decideOperator < 5):
                    tempSchedule = shuffleOrder(tempSchedule, math.floor(len(intersections) * shrinkageFactor) + 1,
                                                intersections, name_to_i_street)
                elif (decideOperator >= 5 and decideOperator < 15):
                    tempSchedule = swapOrder(tempSchedule, math.floor(len(tempSchedule) * shrinkageFactor) + 1,
                                             intersections, name_to_i_street)
                else:
                    tempSchedule = changeGreenTimeDuration(tempSchedule,
                                                           math.floor(len(tempSchedule) * shrinkageFactor) + 1,
                                                           2**32-1, limit_on_minimum_green_phase_duration,
                                                           limit_on_maximum_green_phase_duration,
                                                           limit_on_minimum_cycle_length, limit_on_maximum_cycle_length,
                                                           i_id_to_intersection,
                                                           increase_green_time)

                tempScore, completed_cars1, avg_cars1 = gl.grade(tempSchedule, streets, intersections, paths,
                                                                 total_duration, bonus_points, yellow_phase,
                                                                 duration_to_pass_through_a_traffic_light)

                if (tempScore > patches[i].score):
                    patches[i].stg = False
                    # patches[i].scout = tempSchedule
                    # patches[i].score = tempScore
                    # break
                    patches.append(Patch(score=tempScore, scout=tempSchedule, cars=completed_cars1, avg=avg_cars1))

            if (patches[i].stg):
                patches[i].stgLim += 1
            else:
                patches[i].stgLim = 0

            if (patches[i].stgLim > stgLim and i != 0):
                solution = generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration,
                                            limit_on_maximum_green_phase_duration)
                grade, completed_cars2, avg_cars2 = gl.grade(solution, streets, intersections, paths, total_duration,
                                                             bonus_points, yellow_phase,
                                                             duration_to_pass_through_a_traffic_light)
                patches[i] = Patch(score=grade, scout=solution, cars=completed_cars2, avg=avg_cars2)

        for i in range(nb, ns):
            solution = generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration,
                                        limit_on_maximum_green_phase_duration)
            grade, completed_cars4, avg_cars4 = gl.grade(solution, streets, intersections, paths, total_duration,
                                                         bonus_points, yellow_phase,
                                                         duration_to_pass_through_a_traffic_light)
            # gl.grade_for_simulation(solution, streets, intersections, paths, total_duration,
            #                                              bonus_points, yellow_phase,
            #                                              duration_to_pass_through_a_traffic_light,grade)
            patches.append(Patch(score=grade, scout=solution, cars=completed_cars4, avg=avg_cars4))

        if (shrinkageFactor > 0.001):
            shrinkageFactor *= shrinkageFactorReducedBy

        countIterations += 1
        print(countIterations)
        if countIterations%increase_green_time_alternate_frequency==0:
            increase_green_time=not increase_green_time

        # patches.sort(reverse=True, key=sortKey)
        # patches = patches[0: ns]

    patches.sort(reverse=True, key=sortKey)
    gl.grade_for_simulation(patches[0].scout, streets, intersections, paths, total_duration,
                                                         bonus_points, yellow_phase,
                                                         duration_to_pass_through_a_traffic_light,grade)
    outputToFile(patches, executionTime, countIterations, ns, nb, ne, nrb, nre, stgLim, initialShrinkageFactor,
                 shrinkageFactorReducedBy, shrinkageFactor, start,patches[0].cars, patches[0].avg,patches[0].score)

    return patches[0].scout, patches[0].score, patches[0].cars, patches[0].avg


# file = input("Enter name of the input file, e.g. \"a.txt\": ")
file="instance_fk_straight_c100.json"
# file = sys.argv[1]

start = time()
total_duration, bonus_points, intersections, streets, name_to_i_street, paths, \
    duration_to_pass_through_a_traffic_light, yellow_phase, limit_on_minimum_cycle_length, \
    limit_on_maximum_cycle_length, limit_on_minimum_green_phase_duration, \
    limit_on_maximum_green_phase_duration, i_id_to_intersection = gl.readInput(file)

# manualSolution = gl.readSolutionFromJson('./output/manual_output/pr_manual_output.json', name_to_i_street, intersections)
# score,completed_cars3,avg_cars3 = gl.grade(manualSolution, streets, intersections, paths, total_duration, bonus_points, yellow_phase, duration_to_pass_through_a_traffic_light)
# print("Real Score: ",score,", completed cars: ",completed_cars3,", avg cars=",avg_cars3)
if len(sys.argv) == 3:
    use_seed = sys.argv[2]
    solution_file_path = './seeds/' + sys.argv[1] + '.txt.out'
    schedule, score, cars, avg = BeeHive(streets, intersections, paths, total_duration, bonus_points, start,
                                         yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration,
                                         limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                                         limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light,
                                         i_id_to_intersection, use_seed, solution_file_path)
else:
    schedule, score, cars, avg = BeeHive(streets, intersections, paths, total_duration, bonus_points, start,
                                         yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration,
                                         limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length,
                                         limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light,
                                         i_id_to_intersection)
    gl.printSchedule(schedule, streets)
    # gl.print_json_solution(schedule, streets, intersections)

print("Score: ", score, ", completed cars: ", cars, ", avg cars=", avg)

# print(gl.grade(gl.readSolution('./seeds/I500_S998_C1000.txt.out',streets),streets, intersections, paths, total_duration, bonus_points))
# print(gl.grade(gl.readSolution('./I200_S17200_C1000_1207889',streets),streets, intersections, paths, total_duration, bonus_points))

# gl.printSchedule(schedule, streets)
