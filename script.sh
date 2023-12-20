for ((i=1; i<=10; i++))
do
    nohup python3 BeeHiveOptimization.py > "./results/I8000_S95928_C1000/I8000_S95928_C1000_run_$i" &
done
