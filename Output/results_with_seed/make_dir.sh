for file in ../Traffic\ Instances/instances_to_test/*;
do 
	filename=$(basename "$file")
	mkdir $filename
done

