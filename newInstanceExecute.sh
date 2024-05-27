count=0
for file in ./input/*
do
    if [ $count -lt 4 ]
    then
        count=$((count + 1))
    else
        count=0
        sleep 2000
    fi

    i=1
    while [ $i -le 10 ]
    do
        filename=$(basename "$file")
        nohup python3 BeeHiveOptimization_traffic.py $filename &
        i=$((i + 1))
    done
done

count=0
for file in ./input/*
do
    if [ $count -lt 4 ]
    then
        count=$((count + 1))
    else
        count=0
        sleep 2000
    fi

    i=1
    while [ $i -le 10 ]
    do
        filename=$(basename "$file")
        nohup python3 BeeHiveOptimization_usage.py $filename &
        i=$((i + 1))
    done
done
