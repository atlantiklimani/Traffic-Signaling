import GlobalFunctions as gl
from time import time
from random import sample, choices, shuffle
from recordclass import recordclass
from copy import deepcopy
import random
import math
import sys
import os
import string

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


def initialPopulation(streets, intersections, paths, total_duration, bonus_points):
    population = []
    for i in range(10):
        schedules = randomSolution(intersections)
        population.append([gl.grade(schedules, streets, intersections, paths, total_duration, bonus_points), schedules])
    return population

def sortKey(e):
  return e.score

class Patch:
    def __init__(self, score, scout):
        self.score = score
        self.scout = scout
        self.stgLim = 0
        self.employees = 0
        self.stg = True

def changeGreenTimeDuration(schedule, numberOfIntersection, numberOfRoads, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length):
    if(numberOfIntersection <= 0):
        return schedule

    count = 0
    randomRangeBegins = random.randint(0,len(schedule)- numberOfIntersection - 1)
        
    while(count < numberOfIntersection):
        rand = random.randint(randomRangeBegins, randomRangeBegins + numberOfIntersection)
        length = len(schedule[rand].order)
        otherCount = 0
        while(otherCount < length and otherCount < numberOfRoads):
            semaforId = random.randint(0,length - 1)
            initial = schedule[rand].green_times[schedule[rand].order[semaforId]] 
            # while True:
            loop_upper_limit = 20
            for i in range(0, loop_upper_limit):
                schedule[rand].green_times[schedule[rand].order[semaforId]] = random.randint(limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration)
                if (len(schedule[rand].green_times) <= 1):
                    break
                intersectionCycle = 0
                for x in schedule[rand].green_times.values():
                    intersectionCycle += x
                if (intersectionCycle >= limit_on_minimum_cycle_length and intersectionCycle <= limit_on_maximum_cycle_length):
                    break
                print("Phase Green Time Boundaries Not Correct - Change Green Time")

                if(i == loop_upper_limit - 1):
                    schedule[rand].green_times[schedule[rand].order[semaforId]] = initial    
            otherCount += 1
        count+=1

    return schedule

def shuffleOrder(schedules,numberOfIntersection, intersections, name_to_i_street):
    if(numberOfIntersection <= 0):
        return schedules
    
    count = 0

    while(count < numberOfIntersection):
        rand = random.randint(0, len(schedules) - 1)

        schedules[rand] = shuffleSingleOrder(schedules[rand], intersections, name_to_i_street)
 
        count+=1
        
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

        print('Shuffle Single Order.')
        if (not gl.assertOrderPhaseForSchedule(schedule, intersections, name_to_i_street)):
            raise Exception("Order Not Attained")
        
    return schedule

def swapOrder(schedules, numberOfIntersections, intersections, name_to_i_street):
    if(numberOfIntersections <= 0):
        return schedules
    for i in range(0, numberOfIntersections):
        rand = random.randint(0, len(schedules) - 1)
        incomingStreetsLength = len(schedules[rand].order)
        if(incomingStreetsLength == 1):
            continue
        initial_order = [*schedules[rand].order]
        upper_loop_limit = 20
        for i in range(0, upper_loop_limit):
            print("Applying Swap")
            rand1 = random.randint(0, incomingStreetsLength - 1)
            rand2 = random.randint(0, incomingStreetsLength - 1)
            while(rand1 == rand2):
                rand2 = random.randint(0, incomingStreetsLength - 1)
            temp = schedules[rand].order[rand1]
            schedules[rand].order[rand1] = schedules[rand].order[rand2]
            schedules[rand].order[rand2] = temp
            if (gl.assertOrderPhaseForSchedule(schedules[rand], intersections, name_to_i_street)):
                break
            print("Phase Order Not Correct - Swap")
            if (i == upper_loop_limit - 1):
                schedules[rand].order = initial_order
    return schedules

def copyScheduleArray(scheduleArr):
    newScheduleArr = []
    for i in range(0,len(scheduleArr)):
        newScheduleArr.append(
            Schedule(
                i_intersection=scheduleArr[i].i_intersection,
                order=deepcopy(scheduleArr[i].order),
                green_times=deepcopy(scheduleArr[i].green_times))
            )
        
    return newScheduleArr

def traffic_based_initial_solution(intersections: list[gl.Intersection],limit_on_minimum_green_phase_duration:int,limit_on_maximum_green_phase_duration:int,limit_on_minimum_cycle_length:int,limit_on_maximum_cycle_length:int, name_to_i_street) -> list[Schedule]:
    schedules = []

    # Calculate the global threshold first for efficiency
    all_waiting_cars = [len(street.waiting_cars) for intersection in intersections for street in intersection.incomings]
    threshold = sum(all_waiting_cars) / len(all_waiting_cars)

    for intersection in intersections:
        order = []
        green_times = {}
        total_green_time =0
        # Sort streets based on the sum of lengths of driving_cars and waiting_cars
        
        if 'signal_phase_order' in intersection.constraints:
            street_group_traffic = {}
            streets = []
            street_mps = [group[0] for group in intersection.constraints['simultaneously_signal']]

            # for street in intersection.constraints['signal_phase_order']:
            for street in street_mps:
                street_group_traffic[street] = 0
                streets.append(name_to_i_street.get(street))
            for street in intersection.incomings:
                for group in intersection.constraints['simultaneously_signal']:
                    if street in group:
                        street_obj = name_to_i_street.get(street)
                        street_group_traffic[group[0]] += len(street_obj.driving_cars) + len(street_obj.waiting_cars)
            sorted_streets = sorted(streets, key=lambda s:street_group_traffic.get(s.name, 0), reverse=True) 
        else:
            sorted_streets = sorted(intersection.incomings,
                                key=lambda s: len(s.driving_cars) + len(s.waiting_cars),
                                reverse=True)
        
        for street in sorted_streets:
            # if street.name in intersection.using_streets:
            order.append(street.id)
            # Introduce randomness in green time allocation
            random_factor = random.uniform(limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration)  # Adjust the range as needed
            green_time = 2 if len(street.waiting_cars) > threshold else 1
            green_times[street.id] = int(green_time * random_factor)
            total_green_time += green_times[street.id]

        # Apply minimum and maximum constraints on total green time for the intersection
        total_green_time = max(min(total_green_time, limit_on_minimum_cycle_length), limit_on_maximum_cycle_length)
        
        # Normalize green times to fit within the min and max constraints
        if total_green_time > 0:
            for street_id in green_times:
                green_times[street_id] = int(green_times[street_id] * (total_green_time / sum(green_times.values())))
        
        # Enforce minimum and maximum for individual street green times
        for street_id in green_times:
            green_times[street_id] = max(min(green_times[street_id], limit_on_maximum_green_phase_duration), limit_on_minimum_green_phase_duration)
        if order:
            # schedules.append(Schedule(intersection.id, order, green_times,intersection.pedestrian_phase,intersection.all_red_phase))
            schedules.append(Schedule(intersection.id, order, green_times))
    return schedules

def usage_based_initial_solution(intersections: list[gl.Intersection],limit_on_minimum_green_phase_duration:int,limit_on_maximum_green_phase_duration:int,limit_on_minimum_cycle_length:int,limit_on_maximum_cycle_length:int, name_to_i_street) -> list[Schedule]:
    schedules = []
    for intersection in intersections:
        order = []
        green_times = {}
        total_green_time =0

        if 'signal_phase_order' in intersection.constraints:
            street_group_usage = {}
            streets = []
            street_mps = [group[0] for group in intersection.constraints['simultaneously_signal']]

            # for street in intersection.constraints['signal_phase_order']:
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
            sorted_streets = sorted(intersection.incomings, key=lambda s: intersection.streets_usage.get(s.name, 0),
                                reverse=True)

        for street in sorted_streets:
            # if street.name in intersection.using_streets:
            order.append(street.id)
            usage = intersection.streets_usage.get(street.name, 0)
            #green_time = int(math.sqrt(usage)) if usage > 0 else 1
            green_time = min(max(limit_on_minimum_green_phase_duration, int(math.sqrt(usage))), limit_on_maximum_green_phase_duration)
            green_times[street.id] = green_time
            total_green_time += green_times[street.id]
         # Apply minimum and maximum constraints on total green time for the intersection
        total_green_time = max(min(total_green_time, limit_on_minimum_cycle_length), limit_on_maximum_cycle_length)
        
        # Normalize green times to fit within the min and max constraints
        if total_green_time > 0:
            for street_id in green_times:
                green_times[street_id] = int(green_times[street_id] * (total_green_time / sum(green_times.values())))
        
        # Enforce minimum and maximum for individual street green times
        for street_id in green_times:
            green_times[street_id] = max(min(green_times[street_id], limit_on_maximum_green_phase_duration), limit_on_minimum_green_phase_duration)
        
        if order:
            # schedules.append(Schedule(intersection.id, order, green_times,intersection.pedestrian_phase,intersection.all_red_phase))
            schedules.append(Schedule(intersection.id, order, green_times))
    return schedules


def generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration):
    # while True:
    decideGen = random.randint(0,1)
    if(decideGen == 0):
        solution = traffic_based_initial_solution(intersections, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, name_to_i_street)
    else:
        solution = usage_based_initial_solution(intersections, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, name_to_i_street)

    for i in range(0,len(solution)):
        schedule = solution[i]
        while(not gl.assertOrderPhaseForSchedule(schedule, intersections, name_to_i_street)):
            solution[i] = shuffleSingleOrder(schedule, intersections, name_to_i_street)
            print("Phase Order Not Correct - Generate Solution")

        # break
    return solution
        
            
def outputToFile(patches, executionTime, countIterations, ns, nb, ne, nrb, nre, stgLim, initialShrinkageFactor, shrinkageFactorReducedBy, shrinkageFactor, start):
    global file

    if not os.path.exists(f'output/{file}'):
        os.mkdir(f'output/{file}')
    
    code = "".join(random.choices(string.ascii_lowercase, k= 3))
    output = open(f'output/{file}/{file}_{patches[0].score}_{code}', 'a')
    output.write(f'Parameters:\nns - {ns}, nb - {nb}, ne - {ne}, nrb - {nrb}, nre - {nre},\nStagnation limit - {stgLim}\nInitial shrinkage factor - {initialShrinkageFactor}, Shrinkage Factor per Iteration Reduced by - {shrinkageFactorReducedBy}, Termianl shrinkage factor - {shrinkageFactor:.3f}'
    f'\nExecution Time - {executionTime}, Number of loop iterations - {countIterations}\n')
    for i in range(0,10):
        output.write(f'Score of patch: ,{patches[i].score}\n')
    output.write(f'Real Execution Time: {time() - start}\n')
    output.write("------------------------- Output File Begins Here -------------------------------------\n")
    output.write(gl.getPrintedSchedule(patches[0].scout, streets=streets))
    output.close()

    gl.print_json_solution(patches=patches, schedules=patches[0].scout, streets=streets, intersections=intersections, file= file, code=code )

    return

def BeeHive(streets, intersections, paths, total_duration, bonus_points, terminated_time, yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light, use_seed = False, solution_file_path = None):
    patches = []
    ns = 20 #number of scout bees
    nb = 5 #number of best sites
    ne = 2 #number of elite sites
    nrb = 5 #number of recruited bees for best sites
    nre = 20 #number of recruited bees for elite sites
    stgLim = 4 #stagnation limit for patches
    shrinkageFactor = 0.001 # how fast does the neighborhood shrink. 1 is max. This higher the factor the less is the neighborhood shrinking
    shrinkageFactorReducedBy = 0.99 # by how much is the shrinkage factor reduceb by for iteration
    executionTime = 1 #8 * 60 * 60
    ## Only for visualisation purposes
    initialShrinkageFactor = shrinkageFactor 
    countIterations = 0
    ##
    for i in range(0,ns):
        if(use_seed == 'True' and i < 5):
            sol = gl.readSolution(solution_file_path=solution_file_path, streets=streets)
            if i != 0:
                sol = shuffleOrder(sol, math.floor(len(intersections) * 0.2) + 1,  intersections, name_to_i_street)
        else :    
            sol = generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration)         
        
        grade = gl.grade(sol,streets, intersections, paths, total_duration, bonus_points, yellow_phase, duration_to_pass_through_a_traffic_light)
        patches.append(Patch(grade, sol))
    while (time() - terminated_time < executionTime):
        patches.sort(reverse=True, key=sortKey)
        patches = patches[0: ns]

        for i in range(0,nb):
            employees = 0
            if(i < ne):
                employees = nre
                patches[i].employees = nre
            else :
                employees = nrb
                patches[i].employees = nrb

            patches[i].stg = True

            for e in range(0,employees):
                tempSchedule = copyScheduleArray(patches[i].scout)
                decideOperator = random.randint(0,30) 
                if(decideOperator < 10):
                    tempSchedule = shuffleOrder(tempSchedule, math.floor(len(intersections) * shrinkageFactor) + 1, intersections, name_to_i_street)
                elif(decideOperator >= 10 and decideOperator < 20):
                    tempSchedule = swapOrder(tempSchedule, math.floor(len(intersections) * shrinkageFactor) + 1, intersections, name_to_i_street)
                else:
                    tempSchedule = changeGreenTimeDuration(tempSchedule, math.floor(len(intersections) * shrinkageFactor * 0.001) + 1, 1, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length)
                    
                tempScore = gl.grade(tempSchedule,streets, intersections, paths, total_duration, bonus_points, yellow_phase, duration_to_pass_through_a_traffic_light)

                if(tempScore > patches[i].score):
                    patches[i].stg = False
                    # patches[i].scout = tempSchedule
                    # patches[i].score = tempScore
                    # break
                    patches.append(Patch(score=tempScore, scout=tempSchedule))

            
            if(patches[i].stg):
                patches[i].stgLim += 1
            else:
                patches[i].stgLim = 0
                 
            if(patches[i].stgLim > stgLim and i != 0):
                solution = generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration)      
                grade = gl.grade(solution, streets, intersections, paths, total_duration, bonus_points, yellow_phase, duration_to_pass_through_a_traffic_light)
                patches[i] = Patch(score=grade, scout= solution)

        for i in range(nb, ns):
            solution = generateSolution(intersections, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration)      
            grade = gl.grade(solution, streets, intersections, paths, total_duration, bonus_points, yellow_phase, duration_to_pass_through_a_traffic_light)
            patches.append(Patch(score=grade, scout= solution))
    
        if(shrinkageFactor > 0.001):
            shrinkageFactor *= shrinkageFactorReducedBy
        
        countIterations += 1

        # patches.sort(reverse=True, key=sortKey)
        # patches = patches[0: ns]

    patches.sort(reverse=True, key=sortKey)

    outputToFile(patches, executionTime, countIterations, ns, nb, ne, nrb, nre, stgLim, initialShrinkageFactor, shrinkageFactorReducedBy, shrinkageFactor, start)

    return patches[0].scout, patches[0].score

# file = input("Enter name of the input file, e.g. \"a.txt\": ")
file = sys.argv[1]

start = time()
total_duration, bonus_points, intersections, streets, name_to_i_street, paths, \
    duration_to_pass_through_a_traffic_light, yellow_phase, limit_on_minimum_cycle_length, \
    limit_on_maximum_cycle_length, limit_on_minimum_green_phase_duration, \
    limit_on_maximum_green_phase_duration, = gl.readInput(file)

# manualSolution = gl.readSolutionFromJson('./output/manual_output/pr_manual_output.json', name_to_i_street, intersections)
# score = gl.grade(manualSolution, streets, intersections, paths, total_duration, bonus_points, yellow_phase, duration_to_pass_through_a_traffic_light)
# print("Real Score: ",score)
if len(sys.argv) == 3:
    use_seed = sys.argv[2]
    solution_file_path = './seeds/' + sys.argv[1] + '.txt.out'
    schedule, score = BeeHive(streets, intersections, paths, total_duration, bonus_points,start, yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light, use_seed, solution_file_path)
else :
    schedule, score = BeeHive(streets, intersections, paths, total_duration, bonus_points,start, yellow_phase, name_to_i_street, limit_on_minimum_green_phase_duration, limit_on_maximum_green_phase_duration, limit_on_minimum_cycle_length, limit_on_maximum_cycle_length, duration_to_pass_through_a_traffic_light)
    gl.printSchedule(schedule, streets)
    # gl.print_json_solution(schedule, streets, intersections)

print("Score: ",score)

# print(gl.grade(gl.readSolution('./seeds/I500_S998_C1000.txt.out',streets),streets, intersections, paths, total_duration, bonus_points))
# print(gl.grade(gl.readSolution('./I200_S17200_C1000_1207889',streets),streets, intersections, paths, total_duration, bonus_points))

# gl.printSchedule(schedule, streets)
