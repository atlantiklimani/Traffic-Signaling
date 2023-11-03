from copy import deepcopy

arr = [1,2,3,4]

arr = arr[1:] + arr[:1]

arr2 = deepcopy(arr)
print(id(arr),' ',arr)
print(id(arr2),' ',arr2)


class Patch:
    def __init__(self, score, schedule):
        self.score = score
        self.schedule = schedule
        self.stgLim = 0
        self.employees = 0
firstPatch = Patch(101, [1,2,3])

print(firstPatch.score)