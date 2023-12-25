# Traffic-Signaling
# Traffic Signaling with Bee Hive
## Algorithm Description

1. Generate Solutions based on ns - parameter and calculate fintess for each solution
2. Start the execution of the while loop, and repeat until the program has run out of the  
    executionTime.
   1. Sort instances based on the fitness in descending order
   2. For each best solution do:
   3. Apply operators based on the neighborhoodShrinkageFactor and save the better solutions(if          any)
   4. If solution has stagnated more than stgLim, abandon it.
   5. For the other solutions(not the best) replace with new generated solutions
3. Return the best solution
 
