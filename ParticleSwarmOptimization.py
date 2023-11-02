import GlobalFunctions as gl
from time import time
from random import sample, choices, shuffle
from recordclass import recordclass
from copy import deepcopy

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


# this function will modify position of particle, i.e. modify actual schedule ( details in documentation )
def updateParticlePosition(ac_schedule, pBest, gBest, c1, c2):
    new_schedule = deepcopy(ac_schedule)
    gBestCopy = deepcopy(gBest)
    pBestCopy = deepcopy(pBest)

    gBest_inters = sample(gBestCopy, c2)
    pBest_inters = sample(pBestCopy, c1)
    pBest_inters_id = [schedule.i_intersection for schedule in pBest_inters]
    gBest_inters_id = [schedule.i_intersection for schedule in gBest_inters]
    gBest_inters_id = list(set(gBest_inters_id) - set(pBest_inters_id))
    gBest_to_omit = []
    for inter_gBest in gBest_inters:
        if inter_gBest.i_intersection not in gBest_inters_id:
            gBest_to_omit.append(inter_gBest)
    to_delete = []
    for intersection in new_schedule:
        if intersection.i_intersection in gBest_inters_id or intersection.i_intersection in pBest_inters_id:
            to_delete.append(intersection)
            continue
        # we have 85% that we will shuffle order of streets in intersection schedule and 15% that we will shuffle green time for each street
        choice = choices([0, 1], weights=[85, 15], k=1)
        if choice[0] == 0:  # shuffle order of streets
            shuffle(intersection.order)
        else:
            values = list(intersection.green_times.values())  # shuffle green time
            shuffle(values)
            new_greens = dict(zip(intersection.green_times, values))
            intersection.green_times = new_greens
    for to_del in to_delete:
        new_schedule.remove(to_del)
    for intersection in gBest_inters:
        if intersection not in gBest_to_omit:
            new_schedule.append(intersection)
    for intersection in pBest_inters:
        new_schedule.append(intersection)
    return new_schedule


# Main Particle Swarm Optimization function.
def PSO(streets, intersections, paths, total_duration, bonus_points, terminated_time):
    particles = initialPopulation(streets, intersections, paths, total_duration, bonus_points)
    pBest_schedules = [i[1] for i in particles]  # list which holds best schedule for i-th particle
    actual_perticle_position = deepcopy(pBest_schedules)
    pBests = [i[0] for i in particles]  # list which holds best scores for i-th particle
    velocity_gBest = [1 for i in range(10)]
    velocity_pBest = [1 for i in range(10)]
    gbest = max(pBests)
    gbest_schedule = pBest_schedules[pBests.index(gbest)]
    while (time() - terminated_time < 260):
        for i in range(len(pBest_schedules)):
            # 1. update position
            # 2. get score of new position
            # 3. if necessery update pBest or even gBest
            new_particle_position = updateParticlePosition(actual_perticle_position[i], pBest_schedules[i],
                                                           gbest_schedule, velocity_pBest[i], velocity_gBest[i])
            actual_perticle_position[i] = deepcopy(new_particle_position)
            score = gl.grade(new_particle_position, streets, intersections, paths, total_duration, bonus_points)
            if velocity_pBest[i] < len(intersections):
                velocity_pBest[i] += 1
            if velocity_gBest[i] < len(intersections):
                velocity_gBest[i] += 1
            if score > pBests[i]:
                pBests[i] = score
                pBest_schedules[i] = deepcopy(actual_perticle_position[i])
                velocity_pBest[i] = 0
                if score > gbest:
                    gbest = score
                    gbest_schedule = deepcopy(actual_perticle_position[i])
                    velocity_gBest[i] = 1  # we reset velocity_gBest for this particle since it found new best solution
    return gbest_schedule, gbest


file = input("Enter name of the input file, e.g. \"a.txt\": ")
start = time()
total_duration, bonus_points, intersections, streets, name_to_i_street, paths = gl.readInput(file)
schedule, score = PSO(streets, intersections, paths, total_duration, bonus_points, start)
time_spend = time() - start
gl.printSchedule(schedule, streets)
print("Score: ", score)
print("Time: ", time_spend)
