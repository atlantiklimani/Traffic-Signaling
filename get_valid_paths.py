import argparse
import glob
import os.path

import pandas as pd


def read_txt_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        return data


def process_file_contents(file_contents: str) -> list[list[str]]:
    blocks = file_contents.strip().split('\n\n')
    result = [block.split() for block in blocks]
    return result


def get_valid_paths(processed_contents: list[list[str]], paths: list[str]) -> list[list[str]]:
    valid_paths = []

    for street_block in processed_contents:
        if " ".join(street_block) in paths:
            valid_paths.append(street_block)

    return valid_paths


def save_paths_in_csv(valid_paths: list[list[str]], output_path: str) -> None:
    joined_paths = [' '.join(sublist) for sublist in valid_paths]
    df = pd.DataFrame(joined_paths, columns=['Path'])
    df.to_csv(output_path, index=False)


def main(possible_paths_path: str, raw_files_dir: str) -> None:
    if not os.path.exists(possible_paths_path):
        raise FileNotFoundError(f'The possible paths file was not found: {possible_paths_path}')
    if not os.path.exists(raw_files_dir):
        raise FileNotFoundError(f'The folder was not found: {raw_files_dir}')

    possible_paths_df = pd.read_csv(possible_paths_path)
    paths = possible_paths_df['Path'].tolist()

    all_valid_paths = []
    for file_path in glob.glob(os.path.join(raw_files_dir, '*.txt')):
        file_contents = read_txt_file(file_path)
        processed_contents = process_file_contents(file_contents)

        valid_paths = get_valid_paths(processed_contents, paths)
        all_valid_paths.extend(valid_paths)

    output_path = 'possible_paths_dir/possible_paths_taxi.csv'
    save_paths_in_csv(all_valid_paths, output_path)

    print(f"Saved valid paths to {output_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--possible_paths_file_path', type=str, required=True)
    parser.add_argument('-f', '--raw_files_dir', type=str, required=True)

    args = parser.parse_args()
    main(args.possible_paths_file_path, args.raw_files_dir)
