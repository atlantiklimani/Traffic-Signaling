import argparse
import json
import os

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
                                 intersection_name_to_streets: dict) -> None:
    for intersection_name, streets in intersection_name_to_streets.items():
        if intersection_name not in intersection_name_to_street_green_times:
            intersection_name_to_street_green_times[intersection_name] = {}
        for street in streets:
            if street not in intersection_name_to_street_green_times[intersection_name]:
                intersection_name_to_street_green_times[intersection_name][street] = [streets[street]]
            else:
                intersection_name_to_street_green_times[intersection_name][street].append(streets[street])


def main(bee_hive_output_path: str, manual_output_path: str, show_plots: bool) -> None:
    if not os.path.exists(bee_hive_output_path) or not os.path.exists(manual_output_path):
        raise FileNotFoundError(f'Output not found: {bee_hive_output_path} or {manual_output_path}')

    bee_hive_data = load_json(bee_hive_output_path)
    manual_data = load_json(manual_output_path)

    intersection_name_to_streets_bee_hive = intersection_name_to_streets_index(bee_hive_data)
    intersection_name_to_streets_manual = intersection_name_to_streets_index(manual_data)

    for intersection_name, streets in intersection_name_to_streets_bee_hive.items():
        print(intersection_name)
        print(streets)
        print()

    # intersection_name_to_street_green_times = {}
    # add_results_to_intersections(intersection_name_to_street_green_times, intersection_name_to_streets_bee_hive)
    # add_results_to_intersections(intersection_name_to_street_green_times, intersection_name_to_streets_manual)
    #
    # Handle each set of four intersections
    # all_intersections = list(intersection_name_to_street_green_times.items())
    # num_intersections = len(all_intersections)
    # num_groups = (num_intersections + 3) // 4  # Calculate how many groups of up to four we need
    #
    # for group_index in range(num_groups):
    #     fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 12))  # Set for 2x2 grid
    #     axes = axes.flatten()
    #
    #     start_index = group_index * 4
    #     end_index = min(start_index + 4, num_intersections)
    #     current_group = all_intersections[start_index:end_index]
    #
    #     for ax, (intersection_name, street_results) in zip(axes, current_group):
    #         df = pd.DataFrame.from_dict(street_results, orient='index', columns=['Bee Hive Value', 'Manual Value'])
    #         df.plot(kind='bar', ax=ax, color=['green', 'red'], title=intersection_name)
    #         ax.set_ylabel('Green Time Values')
    #         ax.set_xlabel('Streets')
    #         ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    #
    #         for i, (value1, value2) in enumerate(zip(df['Bee Hive Value'], df['Manual Value'])):
    #             ax.text(i - 0.1, value1 + 0.2, f'{value1:.0f}', va='bottom', ha='center', color='black')
    #             ax.text(i + 0.1, value2 + 0.2, f'{value2:.0f}', va='bottom', ha='center', color='black')
    #
    #     plt.tight_layout()
    #     plt.savefig(f'figures/all_intersections_group_{group_index + 1}.png')
    #     if show_plots:
    #         plt.show()
    #
    # print('Saved the plots for each intersection.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bee_hive_output_path', type=str, required=True)
    parser.add_argument('-m', '--manual_output_path', type=str, required=True)
    parser.add_argument('-s', '--show_plots', action='store_true')
    args = parser.parse_args()
    main(args.bee_hive_output_path, args.manual_output_path, args.show_plots)
