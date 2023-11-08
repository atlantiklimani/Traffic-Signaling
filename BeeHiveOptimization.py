import GlobalFunctions as gl
from time import time
from random import sample, choices, shuffle
from recordclass import recordclass
from copy import deepcopy
import random
import math

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

# resp = [x["age"] for x in filonlist]

def justTry(streets, intersections, paths, total_duration, bonus_points):
    # particles = initialPopulation(streets, intersections, paths, total_duration, bonus_points)
    # print(particles,'Tryin something')
    sol = randomSolution(intersections)
    # print(sol, "Try Somethingg")
    print("Score of Random Solution: ",gl.grade(sol,streets, intersections, paths, total_duration, bonus_points))
    print("First Element: ",len(sol[1].order))

def sortKey(e):
  return e.score

class Patch:
    def __init__(self, score, scheduleArray):
        self.score = score
        self.scheduleArray = scheduleArray
        self.stgLim = 0
        self.employees = 0
        self.stg = True

def firstOperator(order):
    order = order[1:] + order[:1]
    return order

def thirdOperator(schedule,numberOfIntersection):
    if(numberOfIntersection <= 0):
        return schedule
    
    count = 0
    randomRangeBegins = random.randint(0,len(schedule)- numberOfIntersection - 1)

    while(count < numberOfIntersection):
        rand = random.randint(randomRangeBegins, randomRangeBegins + numberOfIntersection)
        random.shuffle(schedule[rand].order)
        count+=1
        
    return schedule

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

def BeeHive(streets, intersections, paths, total_duration, bonus_points, terminated_time):
    patches = []
    ns = 1 #number of scout bees
    nb = 1 #number of best sites
    ne = 1 #number of elite sites
    nrb = 10 #number of recruited bees for best sites
    nre = 100 #number of recruited bees for elite sites
    stgLim = 10 #stagnation limit for patches
    shrinkageFactor = 0.01 # how fast does the neighbourhood shrink. 1 is max. This higher the factor the less is the neighbourhood shrinking
    print("number of intersections = ",len(intersections))
    for i in range(0,ns):
        sol = randomSolution(intersections)
        grade = gl.grade(sol,streets, intersections, paths, total_duration, bonus_points)
        patches.append(Patch(grade, sol))


    while (time() - terminated_time < 60):
        patches.sort(reverse=True, key=sortKey)
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
                rand = random.randint(0,len(patches[i].scheduleArray) - 1)
                tempSchedule = copyScheduleArray(patches[i].scheduleArray)
                # tempSchedule[rand].order = firstOperator(tempSchedule[rand].order)
                tempSchedule = thirdOperator(tempSchedule, math.floor(len(intersections) * shrinkageFactor))
                tempScore = gl.grade(tempSchedule,streets, intersections, paths, total_duration, bonus_points)

                if(tempScore > patches[i].score):
                    patches[i].stg = False
                    patches[i].scheduleArray = tempSchedule
                    patches[i].score = tempScore
            
            if(patches[i].stg):
                patches[i].stgLim += 1

            if(patches[i].stgLim > stgLim and i != 0):
                patches[i].scheduleArray = randomSolution(intersections)
                patches[i].score = gl.grade(patches[i].scheduleArray,streets, intersections, paths, total_duration, bonus_points)
                patches[i].stgLim = 0

        for i in range(nb, ns):
            patches[i].scheduleArray = randomSolution(intersections)
            patches[i].score = gl.grade(patches[i].scheduleArray,streets, intersections, paths, total_duration, bonus_points)
            patches[i].stgLim = 0
    
        shrinkageFactor *= 0.8
        print('shrinkage factor: ',shrinkageFactor)
    
    ### For visualising purposes
    patches.sort(reverse=True, key=sortKey)
    # for patch in patches:
    #     print(patch.score, " Score of patch")
    
    print("Validate Score of Best Patch: ",gl.grade(patches[0].scheduleArray,streets, intersections, paths, total_duration, bonus_points))

file = input("Enter name of the input file, e.g. \"a.txt\": ")
start = time()
total_duration, bonus_points, intersections, streets, name_to_i_street, paths = gl.readInput(file)
BeeHive(streets, intersections, paths, total_duration, bonus_points,start)

