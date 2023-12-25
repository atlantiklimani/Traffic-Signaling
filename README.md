# Traffic-Signaling
# Traffic Signaling with Bee Hive
## Algorithm Description

1. Generate Solutions based on ns - parameter and calculate fintess for each solution
2. Start the execution of the while loop, and repeat until the program has run out of the  
    executionTime.
   - Sort instances based on the fitness in descending order
   - For each best solution do:
   - Apply operators based on the neighborhoodShrinkageFactor and save the better solutions(if          any)
   - If solution has stagnated more than stgLim, abandon it.
   - For the other solutions(not the best) replace with new generated solutions
3. Return the best solution
 
