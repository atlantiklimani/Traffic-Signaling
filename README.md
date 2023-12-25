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

| Instance | Upper Bound | Sagi Shporer Greedy Approach - SSGA | ABC (score) | ABC Best vs. SSGA (%) | ABC Avg vs. SSGA (%) | (SSGA+ABC Best) vs. SSGA score | (SSGA+ABC Best) vs. SSGA (%) |
|----------|-------------|-----------------------------------|-------------|-----------------------|----------------------|-------------------------------|-----------------------------|
|I1662_S10000_C1000| 1,765,068|	1,480,489|	1,302,966|	11.99|	12.13|	1,480,489|	0.000|
|I200_S17200_C1000|	1,230,496|	1,224,089|	1,211,581|	1.02|	1.04|	1,224,089|	0.000|
|I2500_S10000_C306|	2,521,600|	2,521,584|	2,521,573|	0.0004|	0.0005|	2,521,584|	0.000|
|I3333_S13332_C428|	103,319|	103,240|	103,146|	0.0910|	0.0986|	103,241|	-0.001|
|I4000_S12000_C161|	856,860|	856,858|	856,858|	0.0000|	0.0001|	856,858|	0.000|														
