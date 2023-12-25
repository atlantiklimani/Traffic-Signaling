# Traffic-Signaling
## Traffic Signaling with Bee Hive
### Algorithm Description

1. Generate Solutions based on ns - parameter and calculate fintess for each solution
2. Start the execution of the while loop, and repeat until the program has run out of the  
    executionTime.
   1. Sort instances based on the fitness in descending order
   2. For each best solution do:
       1. Apply operators based on the neighborhoodShrinkageFactor and save the better solutions(if any)
       2. If solution has stagnated more than stgLim, abandon it.
   3. For the other solutions(not the best) replace with new generated solutions
3. Return the best solution

|Instance|Upper Bound|	Sagi Shporer Greedy Approach - SSGA|ABC (score)|ABC Best vs. SSGA (%)|	ABC Avg vs. SSGA (%)|(SSGA+ABC Best) vs. SSGA score)|(SSGA+ABC Best) vs. SSGA (%)|														
