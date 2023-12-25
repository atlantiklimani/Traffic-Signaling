for file in ./Input/*
do
	for ((i=1;i<=10;i++));
	do
		nohup python3 BeeHiveOptimization $file > ./Output/results_without_seed/$i & 
	done
	sleep 900
done

