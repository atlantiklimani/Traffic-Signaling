"""See and save comparison plots between the green times.

Examples usage:
    python comparison_between_street_times.py \
        --bee_hive_output_path output\\instance_pr.json\\instance_pr.json_270390_fyb.json \
        --manual_output_path output\\instance_pr.json\\instance_pr.json_270744_aas.json

Default:
    show_plots: include when you want to see the plots before saving them.
    Default: False

Aliases:
    -b, --bee_hive_output_path
    -m, --manual_output_path
    -s, --show_plots
"""
import argparse
import json
import os.path

import matplotlib.pyplot as plt
import pandas as pd


def load_json(json_path: str) -> dict:
    with open(json_path, 'r') as file:
        return json.load(file)


def intersection_name_to_streets_index(bee_hive_data: dict) -> dict:
    intersection_name_to_streets_bee_hive = {}

    for intersection in bee_hive_data['intersections']:
        streets = {}

        for phase in intersection['phases']:
            streets_representative = list(phase['streets'][0].keys())[0]
            green_time = list(phase['streets'][0].values())[0]

            streets[streets_representative] = green_time

        intersection_name = intersection['intersection_name']
        intersection_name_to_streets_bee_hive[intersection_name] = streets

    return intersection_name_to_streets_bee_hive


def add_results_to_intersections(intersection_name_to_street_green_times: dict,
                                 intersection_name_to_streets_bee_hive: dict
                                 ) -> None:
    for intersection_name, streets in intersection_name_to_streets_bee_hive.items():
        if intersection_name not in intersection_name_to_street_green_times:
            intersection_name_to_street_green_times[intersection_name] = {}

        for street in streets:
            if street not in intersection_name_to_street_green_times[intersection_name]:
                intersection_name_to_street_green_times[intersection_name][street] = [streets[street]]
            else:
                intersection_name_to_street_green_times[intersection_name][street].append(streets[street])


def main(bee_hive_output_path: str, manual_output_path: str, show_plots: bool) -> None:
    if not os.path.exists(bee_hive_output_path):
        raise FileNotFoundError('Bee Hive output not found. '
                                'You give this path:', bee_hive_output_path)
    if not os.path.exists(manual_output_path):
        raise FileNotFoundError('Manual output not found. '
                                'You give this path:', manual_output_path)

    bee_hive_data = load_json(bee_hive_output_path)
    manual_data = load_json(manual_output_path)

    intersection_name_to_streets_bee_hive = intersection_name_to_streets_index(bee_hive_data)
    intersection_name_to_streets_manual = intersection_name_to_streets_index(manual_data)

    intersection_name_to_street_green_times = {}
    add_results_to_intersections(intersection_name_to_street_green_times, intersection_name_to_streets_bee_hive)
    add_results_to_intersections(intersection_name_to_street_green_times, intersection_name_to_streets_manual)

    for intersection_name, street_results in intersection_name_to_street_green_times.items():
        df = pd.DataFrame.from_dict(street_results,
                                    orient='index',
                                    columns=['Bee Hive Value', 'Real Value'])
        ax = df.plot(kind='barh',
                     title=intersection_name,
                     color=['green', 'red'],
                     figsize=(10, len(street_results) * 1.2))
        ax.set_xlabel('Green Time Values')
        ax.set_ylabel('Streets')
        plt.tight_layout()
        os.makedirs('figures', exist_ok=True)
        plt.savefig(f'figures/{intersection_name}.png')

        if show_plots:
            plt.show()

    print('Saved the plots for each intersection.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bee_hive_output_path', type=str, required=True)
    parser.add_argument('-m', '--manual_output_path', type=str, required=True)

    parser.add_argument('-s', '--show_plots', action='store_true')

    args = parser.parse_args()
    main(args.bee_hive_output_path, args.manual_output_path, args.show_plots)
