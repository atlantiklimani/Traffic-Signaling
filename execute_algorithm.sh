#!/bin/bash

# runs script
# chmod +x execute_algorithm.sh
# ./execute_algorithm.sh

instance_names=(
    "I70_S210_C200.txt"
    "I80_S240_C300.txt"
    "I80_S480_C600.txt"
    "I90_S360_C400.txt"
    "I99_S399_C400.txt"
    "I100_S400_C600.txt"
    "I100_S500_C500.txt"
    "I100_S600_C153.txt"
    "I110_S330_C450.txt"
    "I120_S480_C500.txt"
    "I120_S720_C400.txt"
    "I150_S45150_C100.txt"
    "I155_S57155_C300.txt"
    "I180_S1080_C800.txt"
    "I200_S1000_C400.txt"
    "I200_S1000_C550.txt"
    "I200_S4200_C400.txt"
    "I200_S17200_C1000.txt"
    "I220_S660_C430.txt"
    "I220_S1100_C558.txt"
    "I241_S43241_C158.txt"
    "I300_S900_C500.txt"
    "I300_S1500_C469.txt"
    "I400_S2400_C944.txt"
    "I444_S1776_C666.txt"
    "I500_S998_C1000.txt"
    "I500_S2000_C315.txt"
    "I600_S3000_C332.txt"
    "I1662_S10000_C1000.txt"
    "I2000_S6000_C376.txt"
    "I2000_S12000_C57.txt"
    "I2500_S10000_C306.txt"
    "I2999_S17994_C103.txt"
    "I3000_S12000_C407.txt"
    "I3000_S15000_C316.txt"
    "I3000_S18000_C227.txt"
    "I3333_S13332_C428.txt"
    "I4000_S12000_C161.txt"
    "I4000_S12000_C387.txt"
    "I4000_S12000_C397.txt"
    "I4000_S20000_C309.txt"
    "I4000_S24000_C401.txt"
    "I7073_S9102_C1000.txt"
    "I8000_S95928_C1000.txt"
    "I9000_S36000_C1500.txt"
    "I10000_S30000_C1200.txt"
    "I10000_S35030_C1000.txt"
    "I12000_S36000_C2000.txt"
)

MAX_THREADS=60

function run_in_parallel {
    while (( $(jobs | wc -l) >= MAX_THREADS )); do
        sleep 0.5
    done
    "$@" &
}

for instance in "${instance_names[@]}"; do
    for version in {1..10}; do
        run_in_parallel python3 BeeHiveOptimization.py --instance_name "$instance" --version "$version"
    done
done

wait

echo "All jobs have been completed."
