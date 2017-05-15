import json
import os
import subprocess

import git
import pandas
import shutil

from git import Repo
from shared_constants import data_dir, repo_candidates_filename

temp_repo_dir = "temp-repo"
code_metrics_file = "code-metrics.csv"
code_metrics_folder = "code-metrics"


def read_json(filename):
    print("reading result from {}/{}".format(data_dir, filename))
    with open("{}/{}.json".format(data_dir, filename), "r") as file:
        data = json.load(file)

    return data


def main():
    # for all repos

    candidate_repos = read_json(repo_candidates_filename)

    # create the folder where to store the code metrics
    if not os.path.exists("{}/{}".format(data_dir, code_metrics_folder)):
        os.makedirs("{}/{}".format(data_dir, code_metrics_folder))

    metrics = None
    for i in range(0, len(candidate_repos)):
        # for i in range(0, 10):

        # create the folder where to store the repos temporarily
        if not os.path.exists(temp_repo_dir):
            os.makedirs(temp_repo_dir)

        candidate_repo = candidate_repos[i]

        # download repo
        git_url = candidate_repo["html_url"]
        repo_name = candidate_repo["name"]

        print("============================================")
        print("cloning repository {}".format(repo_name))
        try:
            Repo.clone_from(git_url, temp_repo_dir)
        except git.exc.GitCommandError:
            print("error cloning repository")
            continue

        # calculate code metrics on last snapshot
        print("calculating code metrics")
        repo_id = candidate_repo["id"]
        output_file = "{}/{}/{}-{}".format(data_dir, code_metrics_folder, repo_id, code_metrics_file)

        if not compute_metrics(output_file):
            continue

        temp_frame = prepare_metrics_data(candidate_repo, output_file, repo_id, repo_name)

        if metrics is None:
            metrics = temp_frame
        else:
            metrics = pandas.concat([metrics, temp_frame], ignore_index=True)

        print("save data to csv")
        metrics.to_csv("{}/final-{}".format(data_dir, code_metrics_file))

        shutil.rmtree(temp_repo_dir)


def compute_metrics(output_file):
    # e.g "Exception in thread "main" java.lang.NullPointerException..."
    # java -jar ck/ck-0.2.1-SNAPSHOT-jar-with-dependencies.jar temp-repo/ data/36057260-code-metrics.csv
    # subprocess.run("java -jar ck/ck-0.2.1-SNAPSHOT-jar-with-dependencies.jar {} {}"
    #                .format(temp_repo_dir, output_file), shell=True)

    try:
        subprocess.run(
            " ".join(
                ["java", "-jar", "ck/ck-0.2.1-SNAPSHOT-jar-with-dependencies.jar", temp_repo_dir, output_file]
            ),
            shell=True, check=True,
            timeout=60 * 10
        )

    except subprocess.CalledProcessError:
        print("exception analysing the repository - skipping")
        shutil.rmtree(temp_repo_dir)
        return False

    except subprocess.TimeoutExpired:
        print("timeout analysing the repository - skipping")
        shutil.rmtree(temp_repo_dir)
        return False

    return True


def prepare_metrics_data(candidate_repo, output_file, repo_id, repo_name):
    # analyse  code quality vs stars and num contributors
    print("preparing data")
    metrics_raw = pandas.read_csv(output_file)
    metrics_raw.pop("file")
    metrics_raw.pop("class")
    metrics_raw.pop("type")
    # for each metric compute  mean, median, Q1, and Q3
    mean = metrics_raw.mean().rename(lambda x: "average_{}".format(x))
    median = metrics_raw.median().rename(lambda x: "median_{}".format(x))
    q1 = metrics_raw.quantile(q=0.25).rename(lambda x: "Q1_{}".format(x))
    q3 = metrics_raw.quantile(q=0.75).rename(lambda x: "Q3_{}".format(x))
    temp_frame = pandas.DataFrame(pandas.concat([mean, median, q1, q3])).T
    temp_frame['id'] = repo_id
    temp_frame['name'] = repo_name
    temp_frame['stars'] = candidate_repo["stargazers_count"]
    temp_frame['contributors_total'] = candidate_repo["num_contributors"]
    return temp_frame


if __name__ == '__main__':
    main()
