import GlobalFunctions as gl
from time import time
from random import sample, choices, shuffle
from recordclass import recordclass
from copy import deepcopy
import random
import math
import sys
import numpy as np
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

def firstOperator(order):
    order = order[1:] + order[:1]
    return order

def fifthOperator(schedules, numberOfIntersections, numberOfRoads, instersections, streets):
    if(numberOfIntersections <= 0):
        return schedules
    
    maxNumOfSchedules = len(schedules)
    for i in range(0,numberOfIntersections):
        intersection = schedules[random.randint(0,maxNumOfSchedules)]
        for j in range (0, numberOfRoads):
            if(j >= len(intersection.order)):
                break
            else:
                streetId = intersection.order[random.randint(0,len(intersection.order) - 1)]
                intersection.green_times[streetId] = choices([2,3,4], weights=[85,10,5])
        ## Street to find the next intersection
        streetId = intersection.order[random.randint(0,len(intersection.order) - 1)]
        nextInterectionId = streets[streetId].end
        # print(streets[streetId], ' -------------- aouiwfhsihfauish')
        intersection = [x for x in schedules if x.i_intersection ==  nextInterectionId][0]

    return schedules

def changeGreenTimeDuration(schedules, numberOfRoads):
    count = 0

    for schedule in schedules:
        length = len(schedule.order)
        otherCount = 0
        while(otherCount < length and otherCount < numberOfRoads):
            semaforId = random.randint(0,length - 1)
            schedule.green_times[schedule.order[semaforId]] = int(choices([1, 2, 3],weights=[10, 70, 20], k=1)[0]) 
            otherCount += 1
        count+=1

    return schedule

def shuffleOrder(schedules):
    for schedule in schedules:
        random.shuffle(schedule.order)

    return schedules

def swapOrder(schedules):
    for schedule in schedules:
        incomingStreetsLength = len(schedule.order)
        if(incomingStreetsLength == 1):
            continue
        rand1 = random.randint(0, incomingStreetsLength - 1)
        rand2 = random.randint(0, incomingStreetsLength - 1)
        while(rand1 == rand2):
            rand2 = random.randint(0, incomingStreetsLength - 1)
        temp = schedule.order[rand1]
        schedule.order[rand1] = schedule.order[rand2]
        schedule.order[rand2] = temp
    
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

def traffic_based_initial_solution(intersections: list[gl.Intersection]) -> list[Schedule]:
    schedules = []

    # Calculate the global threshold first for efficiency
    all_waiting_cars = [len(street.waiting_cars) for intersection in intersections for street in intersection.incomings]
    threshold = sum(all_waiting_cars) / len(all_waiting_cars)

    for intersection in intersections:
        order = []
        green_times = {}

        # Sort streets based on the sum of lengths of driving_cars and waiting_cars
        sorted_streets = sorted(intersection.incomings,
                                key=lambda s: len(s.driving_cars) + len(s.waiting_cars),
                                reverse=True)

        for street in sorted_streets:
            if street.name in intersection.using_streets:
                order.append(street.id)
                # Introduce randomness in green time allocation
                random_factor = random.uniform(1, 2)  # Adjust the range as needed
                green_time = 2 if len(street.waiting_cars) > threshold else 1
                green_times[street.id] = int(green_time * random_factor)

        if order:
            schedules.append(Schedule(intersection.id, order, green_times))
    return schedules

def usage_based_initial_solution(intersections: list[gl.Intersection]) -> list[Schedule]:
    schedules = []
    for intersection in intersections:
        order = []
        green_times = {}

        sorted_streets = sorted(intersection.incomings, key=lambda s: intersection.streets_usage.get(s.name, 0),
                                reverse=True)

        for street in sorted_streets:
            if street.name in intersection.using_streets:
                order.append(street.id)
                usage = intersection.streets_usage.get(street.name, 0)
                green_time = int(math.sqrt(usage)) if usage > 0 else 1
                green_times[street.id] = green_time

        if order:
            schedules.append(Schedule(intersection.id, order, green_times))
    return schedules

def generateSolution(intersections):
    decideGen = random.randint(0,1)

    if(decideGen == 0):
        solution = traffic_based_initial_solution(intersections)
    else:
        solution = usage_based_initial_solution(intersections)

    return solution

def assignEmployeesArray(ns, ne, shrinkage):
    employees = np.zeros(ns)

    for i in range(0,ns):
        employees[i] = shrinkage ** (i / 2)
    
    employees = employees / employees.sum()

    for i in range(0, ns):
        employees[i] = math.floor(employees[i] * ne)
    
    for i in range(0, int(ne - employees.sum())):
        employees[i] += 1

    return employees
def outputToFile(patches, executionTime, countIterations, ns, nEmployees, stgLim, initialShrinkageFactor, shrinkageFactorReducedBy, shrinkageFactor, start):
    global file

    if not os.path.exists(f'output/{file}'):
        os.mkdir(f'output/{file}')
    
    output = open(f'output/{file}/{file}_{patches[0].score}_{"".join(random.choices(string.ascii_lowercase, k= 3))}', 'a')
    output.write(f'Parameters:\nns - {ns}, number of employees - {nEmployees},\nStagnation limit - {stgLim}\nInitial shrinkage factor - {initialShrinkageFactor}, Shrinkage Factor per Iteration Reduced by - {shrinkageFactorReducedBy}, Termianl shrinkage factor - {shrinkageFactor:.3f}'
    f'\nExecution Time - {executionTime}, Number of loop iterations - {countIterations}\n')
    for i in range(0,10):
        output.write(f'Score of patch: ,{patches[i].score}\n')
    output.write(f'Real Execution Time: {time() - start}\n')
    output.write("------------------------- Output File Begins Here -------------------------------------\n")
    output.write(gl.getPrintedSchedule(patches[0].scout, streets=streets))
    output.close()
    return

# Select intersections based on the number of waiting cars. This number is the total of waiting cars on all streets
def selectSchedules(schedules, numOfSchedules):
    if(numOfSchedules <= 0):
        return random.sample(schedules, k=1)
    
    if(numOfSchedules * 2 > len(schedules)):
        expandedIntersections = len(schedules)
    else: 
        expandedIntersections = numOfSchedules * 2

    schedules = random.sample(schedules, k=expandedIntersections)
    
    def sortKey(s):
        return intersections[s.i_intersection].num_waiting_cars
        
    schedules.sort(reverse=True, key=sortKey)

    schedules = schedules[:numOfSchedules]

    return schedules

    
def BeeHive(streets, intersections, paths, total_duration, bonus_points, terminated_time, use_seed = False, solution_file_path = None):
    patches = []
    ns = 30 #number of scout bees
    nEmployees = 150
    stgLim = 4 #stagnation limit for patches
    shrinkageFactor = 0.5 # how fast does the neighborhood shrink. 1 is max. This higher the factor the less is the neighborhood shrinking
    shrinkageFactorReducedBy = 0.97 # by how much is the shrinkage factor reduceb by for iteration
    executionTime = 30 * 60
    ## Only for visualisation purposes
    initialShrinkageFactor = shrinkageFactor 
    countIterations = 0
    ##

    for i in range(0,ns):
        if(use_seed == 'True' and i < 5):
            sol = gl.readSolution(solution_file_path=solution_file_path, streets=streets)
            if i != 0:
                selectedSchedules = selectSchedules(sol,  math.floor(len(sol) * 0.2))
                shuffleOrder(selectedSchedules)
        else :    
            sol = generateSolution(intersections)         
        
        grade = gl.grade(sol,streets, intersections, paths, total_duration, bonus_points)
        patches.append(Patch(grade, sol))
    
    while (time() - terminated_time < executionTime):
        
        patches.sort(reverse=True, key=sortKey)
        patches = patches[0: ns]
        assignEmployees = assignEmployeesArray(ns, nEmployees, shrinkage=shrinkageFactor)
        indexOfFirstSiteWithoutEmployees = ns
        for i in range(0,ns):
            employees = assignEmployees[i]

            if(employees == 0):
                indexOfFirstSiteWithoutEmployees = i
                break

            patches[i].stg = True

            for e in range(0,int(employees)):
                tempSchedule = copyScheduleArray(patches[i].scout)
                decideOperator = random.randint(0,20) 
                if(decideOperator < 3):
                    selectedSchedules = selectSchedules(tempSchedule,  math.floor(len(tempSchedule) * shrinkageFactor) + 1)
                    shuffleOrder(selectedSchedules)
                elif(decideOperator >= 3 and decideOperator < 20):
                    selectedSchedules = selectSchedules(tempSchedule,  math.floor(len(tempSchedule) * shrinkageFactor) + 1)
                    swapOrder(selectedSchedules)
                else:
                    selectedSchedules = selectSchedules(tempSchedule,  math.floor(len(tempSchedule) * shrinkageFactor * 0.001) + 1)
                    changeGreenTimeDuration(selectedSchedules, 1)

                    
                tempScore = gl.grade(tempSchedule,streets, intersections, paths, total_duration, bonus_points)

                if(tempScore > patches[i].score):
                    patches[i].stg = False
                    patches.append(Patch(score=tempScore, scout=tempSchedule))

            
            if(patches[i].stg):
                patches[i].stgLim += 1
            else:
                patches[i].stgLim = 0
                 
            if(patches[i].stgLim > stgLim and i != 0):
                solution = generateSolution(intersections)      
                grade = gl.grade(solution, streets, intersections, paths, total_duration, bonus_points)
                patches[i] = Patch(score=grade, scout= solution)

        for i in range(indexOfFirstSiteWithoutEmployees, ns):
            solution = generateSolution(intersections)      
            grade = gl.grade(solution, streets, intersections, paths, total_duration, bonus_points)
            patches.append(Patch(score=grade, scout= solution))
    
        if(shrinkageFactor > 0.001):
            shrinkageFactor *= shrinkageFactorReducedBy
        
        countIterations += 1

        # patches.sort(reverse=True, key=sortKey)
        # patches = patches[0: ns]

    patches.sort(reverse=True, key=sortKey)

    outputToFile(patches, executionTime, countIterations, ns, nEmployees, stgLim, initialShrinkageFactor, shrinkageFactorReducedBy, shrinkageFactor, start)

    return patches[0].scout, patches[0].score

# file = input("Enter name of the input file, e.g. \"a.txt\": ")
file = sys.argv[1]

start = time()
total_duration, bonus_points, intersections, streets, name_to_i_street, paths = gl.readInput(file)
if len(sys.argv) == 3:
    use_seed = sys.argv[2]
    solution_file_path = './seeds/' + sys.argv[1] + '.txt.out'
    schedule, score = BeeHive(streets, intersections, paths, total_duration, bonus_points,start, use_seed, solution_file_path)
else :
    schedule, score = BeeHive(streets, intersections, paths, total_duration, bonus_points,start)

# print(gl.grade(gl.readSolution('./seeds/I500_S998_C1000.txt.out',streets),streets, intersections, paths, total_duration, bonus_points))
# print(gl.grade(gl.readSolution('./I200_S17200_C1000_1207889',streets),streets, intersections, paths, total_duration, bonus_points))

# gl.printSchedule(schedule, streets)
