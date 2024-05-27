import argparse
import json
import os
import pandas as pd


def load_json(json_path: str) -> dict:
    """Load JSON data from a file."""
    with open(json_path, 'r') as file:
        return json.load(file)


def intersection_name_to_streets_index(bee_hive_data: dict) -> dict:
    """Extract streets and their green times from bee hive data."""
    intersection_name_to_streets = {}
    for intersection in bee_hive_data['intersections']:
        streets = {}
        for phase in intersection['phases']:
            streets_representative = list(phase['streets'][0].keys())[0]
            green_time = list(phase['streets'][0].values())[0]
            streets[streets_representative] = green_time
        intersection_name = intersection['intersection_name']
        intersection_name_to_streets[intersection_name] = streets
    return intersection_name_to_streets


def compare_intersections(manual_data, bee_hive_data):
    """Create a comparison table from manual and bee hive data."""
    manual_streets = intersection_name_to_streets_index(manual_data)
    bee_hive_streets = intersection_name_to_streets_index(bee_hive_data)

    rows = []
    for intersection, streets in manual_streets.items():
        for i, (manual_street, manual_time) in enumerate(streets.items()):
            bee_hive_street = list(bee_hive_streets.get(intersection, {}).keys())[i] if i < len(
                bee_hive_streets.get(intersection, {})) else "N/A"
            rows.append({
                'Intersection Name': intersection,
                'Nr Phase': i + 1,
                'Manual Street Name': manual_street,
                'Bee Hive Street Name': bee_hive_street
            })

    return pd.DataFrame(rows)


def main(bee_hive_output_path: str, manual_output_path: str):
    if not os.path.exists(bee_hive_output_path) or not os.path.exists(manual_output_path):
        raise FileNotFoundError(f'Output not found: {bee_hive_output_path} or {manual_output_path}')

    bee_hive_data = load_json(bee_hive_output_path)
    manual_data = load_json(manual_output_path)

    comparison_table = compare_intersections(manual_data, bee_hive_data)
    print(comparison_table)
    comparison_table.to_csv('intersection_comparison.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--bee_hive_output_path', type=str, required=True)
    parser.add_argument('-m', '--manual_output_path', type=str, required=True)
    args = parser.parse_args()
    main(args.bee_hive_output_path, args.manual_output_path)
