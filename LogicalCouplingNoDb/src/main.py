import argparse
import itertools
import os
from operator import itemgetter

import pandas
import pandas as pd
import pydriller
from git import Repo


def checkout(repo_url, branch, commit_hash):
    path = f".temp/{repo_url.replace('/', '_')}"
    Repo.clone_from(repo_url, path)
    return path


def load_previuos_results(repo_name):
    file = f'../.data/{repo_name}/LogicalCoupling.csv'
    if os.path.exists(file):
        print("Previous results found")
        data = pandas.read_csv(file)
    else:
        print("No previous results found")
        os.makedirs(f'../.data/{repo_name}', exist_ok=True)
        data = pandas.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE'])

    return data


def analyze_actual_commit(path_to_repo, branch, commit_hash):
    result = []
    for commit in pydriller.Repository(path_to_repo, single=commit_hash, only_in_branch=branch).traverse_commits():

        modified_files = commit.modified_files

        for files in modified_files:
            result.append(files.new_path)

    components = [root_calculator(file_path) for file_path in result]
    combinations = list(itertools.combinations(list(set(components)), 2))
    combinations_sorted = sorted(combinations, key=itemgetter(0))
    new_data = pandas.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE'])
    for comb in combinations_sorted:
        new_data = new_data.append({'COMPONENT 1': comb[0], 'COMPONENT 2': comb[1], 'LC_VALUE': 1}, ignore_index=True)
    return new_data

    # for combination in combinations_sorted:
    #
    #
    #     to_find = f"C1:{combination[0]}!C2:{combination[1]}"
    #     cond = self.components_coupling[self.components_coupling['COMPONENTS'] == to_find]
    #     if cond.empty:
    #         self.components_coupling = self.components_coupling.append(
    #             {'COMPONENTS': to_find, 'COUPLING': 1}, ignore_index=True)
    #     else:
    #         self.components_coupling.loc[cond.index, 'COUPLING'] += 1
    #
    # self.loader.save()


def root_calculator(self, file_path: str) -> str:
    path = file_path.lstrip(os.sep)
    root = path[:path.index(os.sep)] if os.sep in path else path
    return root


def update_data(data, new_data):
    # merged_df = pd.merge(data, new_data, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')
    # merged_df['LC_VALUE'] = merged_df['LC_VALUE_x'].fillna(0) + merged_df['LC_VALUE_y'].fillna(0)
    #
    # # Drop unnecessary columns
    # merged_df = merged_df[['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE']]

    merged_df = pd.merge(data, new_data, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')
    merged_df['LC_VALUE'] = merged_df['LC_VALUE_x'].fillna(0) + merged_df['LC_VALUE_y'].fillna(0)

    # Drop unnecessary columns
    merged_df = merged_df[['COMPONENT 1', 'COMPONENT 2', 'LC_VALUE']]
    merged_df['LC_VALUE'] = merged_df['LC_VALUE'].astype(int)

    return merged_df


def alert(data_extracted, previous_data):
    new_rows = []
    # data = pd.DataFrame(columns=['COMPONENT 1', 'COMPONENT 2', 'NEW_LC_VALUE', 'OLD_LC_VALUE'])


    to_alert = previous_data[previous_data[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1).isin(data_extracted[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1))]

    new_coupling = data_extracted[~data_extracted[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1).isin(previous_data[['COMPONENT 1', 'COMPONENT 2']].apply(tuple, axis=1))]
    new_coupling['LC_VALUE'] = 0

    to_alert = pd.merge(to_alert, new_coupling, on=['COMPONENT 1', 'COMPONENT 2'], how='outer')

    to_alert['LC_VALUE'] = to_alert['LC_VALUE_x'].combine_first(to_alert['LC_VALUE_y'])
    to_alert = to_alert.drop(['LC_VALUE_x', 'LC_VALUE_y'], axis=1)

    for index, row in to_alert.iterrows():
        new_rows.append({'COMPONENT 1': row['COMPONENT 1'], 'COMPONENT 2': row['COMPONENT 2'],
                         'NEW_LC_VALUE': row['LC_VALUE'] + 1, 'OLD_LC_VALUE': row['LC_VALUE']})
    return pd.DataFrame(new_rows)


def print_alert(increasing_data):
    for index, row in increasing_data.iterrows():
        if row['OLD_LC_VALUE'] >= 5:
            print(f"The new coupling between the coupled components {row['COMPONENT 1']} and {row['COMPONENT 2']} is increased: {row['NEW_LC_VALUE']}")
        elif row['NEW_LC_VALUE'] >= 5:
            print(f"The components  {row['COMPONENT 1']} and {row['COMPONENT 2']} are coupled: {row['NEW_LC_VALUE']}")
        else:
            print(f" Logical coupling between {row['COMPONENT 1']} and {row['COMPONENT 2']} increased from {row['OLD_LC_VALUE']} to {row['NEW_LC_VALUE']}")

def save(data, repo_name):
    data.to_csv(f'../.data/{repo_name}/LogicalCoupling.csv', index=False)


def initialize():
    if not os.path.exists('../.data'):
        os.mkdir('../.data')
    # if not os.path.exists('../.temp'):
    #     os.mkdir('../.temp')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit_hash")
    parser.add_argument("--branch")
    parser.add_argument("--repo_url")


    args = parser.parse_args()
    print(args.repo_url, args.branch, args.commit_hash)

    initialize()

    commit_hash = args.commit_hash
    branch = args.branch
    repo_url = args.repo_url
    repo_name = repo_url.split('/')[-1].split('.')[0]+"b:"+branch



    path_to_cloned_repo = checkout(repo_url, branch, commit_hash)
    data = load_previuos_results(repo_name)
    new_data = analyze_actual_commit(path_to_cloned_repo, branch, commit_hash)
    save(new_data, repo_name)
