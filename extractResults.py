import os
import json
import csv
import pandas as pd

result = {}

solution_generated_by = 'usage'

path = f'./output/{solution_generated_by}'

folders = os.listdir(path=path)

for folder in folders:
    solution_group_path = f'{path}/{folder}'
    files = os.listdir(path=solution_group_path)
    json_files = []
    for file in files:
        if ".json" in file:
            json_files.append(file)

    score_field_name = f'{folder} Score'
    avg_cars_field_name = f'{folder} Average Number of Waiting Cars'
    completed_path_field_name = f'{folder} Completed Path Number of Cars'

    result[score_field_name] = []
    result[avg_cars_field_name] = []
    result[completed_path_field_name] = []
    
    for file in json_files:
        json_file = open(file=f'{solution_group_path}/{file}', mode='r')
        json_object = json.load(fp=json_file)
        result[score_field_name].append(json_object['score'])
        result[avg_cars_field_name].append(json_object['average_waiting_cars'])
        result[completed_path_field_name].append(json_object['cars_completed'])
    

df = pd.DataFrame.from_dict(data=result)
# df.transpose()
df.to_excel(f'results_{solution_generated_by}.xlsx')
