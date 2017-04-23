import json
import os

from github import Github
import ccas.github_repos as github_repos
from ccas.analysis import plot_success_data

from ccas.constants import data_dir, repo_candidates_filename

# TODO
"""
The main entry point. Invoke as ''.
"""


def read_json(filename):
    print("reading result from {}/{}".format(data_dir, filename))
    with open("{}/{}.json".format(data_dir, filename), "r") as file:
        data = json.load(file)

    return data


def main():
    # STEP 1
    # fetch list of projects from github.com (repo url, number of stars, number of contributors)

    with open('../config', 'r') as f:
        user = f.readline().strip()
        password = f.readline().strip()

    # create the folder where to store the results
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    github_client = Github(login_or_token=user, password=password)
    github_repos.save_repo_data_from_git(github_client)

    repo_candidates = read_json(repo_candidates_filename)

    # calculate the distribution of stars and plot
    plot_success_data(repo_candidates)


    # STEP 2
    # download repos
    # calculate code metrics on last snapshot
    # analyse  code quality vs stars and num contributors


if __name__ == '__main__':
    main()
