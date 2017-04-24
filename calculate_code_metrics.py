import json
import os

from shared_constants import data_dir, repo_candidates_filename

temp_repo_dir = "temp-repo"


def read_json(filename):
    print("reading result from {}/{}".format(data_dir, filename))
    with open("{}/{}.json".format(data_dir, filename), "r") as file:
        data = json.load(file)

    return data


def main():

    # create the folder where to store the repos temporarily
    if not os.path.exists(temp_repo_dir):
        os.makedirs(temp_repo_dir)

    candidate_repos = read_json(repo_candidates_filename)

    # STEP 2
    # download repos
    # calculate code metrics on last snapshot
    # analyse  code quality vs stars and num contributors


if __name__ == '__main__':
    main()