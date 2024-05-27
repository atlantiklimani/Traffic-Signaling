for file in ./input/*
do
    i=1
    while [ $i -le 2 ]
    do
        filename=$(basename "$file")
        nohup python3 BeeHiveOptimization_traffic.py $filename &
        i=$((i + 1))
    done
done

sleep 14500

for file in ./input/*
do
    i=1
    while [ $i -le 2 ]
    do
        filename=$(basename "$file")
        nohup python3 BeeHiveOptimization_usage.py $filename &
        i=$((i + 1))
    done
done
