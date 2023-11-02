import GlobalFunctions as gl
from time import time
from recordclass import recordclass

Schedule = recordclass('Schedule', [
    'i_intersection',
    'order',
    'green_times'
])




def generateGreedy(intersections):
    schedules = []
    for intersection in intersections:
        order = []
        green_times = {}
        most_busy_streets = [k for k, v in intersection.streets_usage.items() if v == max(intersection.streets_usage.values())]
        for i in range(len(intersection.incomings)):
            street = intersection.incomings[i]
            order.append(street.id)
            if street.name in most_busy_streets and len(most_busy_streets) == 1:
                green_times[street.id] = 2
            else:
                green_times[street.id] = 1
        schedule = Schedule(i_intersection=intersection.id,
                            order=order,
                            green_times=green_times)
        schedules.append(schedule)
    return schedules


file = input("Enter name of the input file, e.g. \"a.txt\": ")
start = time()
total_duration, bonus_points, intersections, streets, name_to_i_street, paths = gl.readInput(file)
schedule = generateGreedy(intersections)
score = gl.grade(schedule, streets, intersections, paths, total_duration, bonus_points)
time_spend = time() - start
gl.printSchedule(schedule, streets)
print("Score: ", score)
print("Time: ", time_spend)





