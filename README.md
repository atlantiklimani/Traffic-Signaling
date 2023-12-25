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

| Id | Instance | Upper Bound | Sagi Shporer Greedy Approach - SSGA | ABC (score) | ABC Best vs. SSGA (%) | ABC Avg vs. SSGA (%) | (SSGA+ABC Best) vs. SSGA score | (SSGA+ABC Best) vs. SSGA (%) |
|----|----------|-------------|-----------------------------------|-------------|-----------------------|----------------------|-------------------------------|-----------------------------|
|1|I1662_S10000_C1000| 1,765,068|	1,480,489| 1,302,966| 11.99| 12.13|	1,480,489|	0.000|
|2|I200_S17200_C1000|	1,230,496| 1,224,089| 1,211,581| 1.02| 1.04| 1,224,089|	0.000|
|3|I2500_S10000_C306|	2,521,600| 2,521,584| 2,521,573| 0.0004| 0.0005| 2,521,584|	0.000|
|4|I3333_S13332_C428|	103,319| 103,240| 103,146|	0.0910|	0.0986|	103,241| -0.001|
|5|I4000_S12000_C161|	856,860| 856,858| 856,858|	0.0000|	0.0001|	856,858| 0.000|
|6|I444_S1776_C666| 407,542| 330,207|	309,833| 6.1701| 6.6939| 330,823| -0.187|
|7|I500_S998_C1000| 921,303| 762,253|	733,360| 3.7905| 4.1536| 762,253| 0.000|	
|8|I7073_S9102_C1000| 4,576,202| 4,570,281| 4,566,911| 0.0737| 0.0750| 4,570,281|	0.000|
|9|I10000_S35030_C1000| 1,328,389| 1,314,708|	1,300,348| 1.0923| 1.1063| 1,314,708|	0.000|
|10|I8000_S95928_C1000| 3,986,591|	2,610,027| 1,596,701| 38.8243| 38.9953| 2,610,027|0.000|

