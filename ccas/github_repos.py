import json
import time
from github import Github
from datetime import datetime, timezone

from ccas.constants import repo_time_format, data_dir, repo_candidates_filename

"""
Provides a list of projects from github.com (repo url, number of stars, number of contributors)
# Criteria for selecting project
- 1 year of history
- at least 50 files
- Java projects (metrics calculation)
- 100 commits
- at least 10 contributors
- at least 1 commit in the last month
"""

created = "<2016-04-22"
language = "Java"

min_contributors = 10
min_commits_last_month = 1
min_commits = 100
min_files = 50

last_month_date = datetime(2017, 3, 22)

repos_count = 1000


def save_json(data, filename):
    filename = "{}.json".format(filename)
    print("saving result to {}/{}".format(data_dir, filename))
    with open("{}/{}".format(data_dir, filename), "w") as file:
        file.write(json.dumps(data, indent=4))


def save_repo_data_from_git(github_client: Github):
    # TODO - ASK now it sorts per most updated
    # https://developer.github.com/v3/search/#search-repositories

    repo_candidates = []
    num_repos = 0
    for repo in github_client.search_repositories(query='', created=created, language=language, sort='updated'):

        requests_remaining = github_client.rate_limiting[0]
        print("requests remaining {}".format(requests_remaining))
        if requests_remaining < 50:
            sleep_interval = github_client.rate_limiting_resettime - datetime.now().replace(tzinfo=timezone.utc).timestamp()
            print("sleeping for {} seconds".format(sleep_interval))
            time.sleep(sleep_interval)

        print("{} {} {}".format(repo.full_name, repo.language, repo.created_at))

        try:

            # contributors
            print("checking contributors")
            if not len(repo.get_contributors().get_page(0)) > min_contributors:
                print("not enough contributors")
                continue

            contributors = 0
            for _ in repo.get_contributors():
                contributors += 1

            # commits last month
            print("checking commits last month")
            if not len(repo.get_commits(since=last_month_date).get_page(0)) > min_commits_last_month:
                print("not enough commits last month")
                continue

            # total commits
            print("checking total commits")
            commits_retrieved = 0
            page = 0
            while commits_retrieved <= min_commits:
                commits = len(repo.get_commits().get_page(page))

                if commits < 30:
                    break

                commits_retrieved += commits
                page += 1

            if commits_retrieved < min_commits:
                print("not enough commits")
                continue

            # total files
            print("checking total files")
            if retrieve_files(repo, "/", 0) < min_files:
                print("not enough files")
                continue

        except ConnectionResetError:
            continue

        repo_candidates.append({
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name,
            "html_url": repo.html_url,
            "url": repo.url,
            "created_at": repo.created_at.strftime(repo_time_format),
            "updated_at": repo.updated_at.strftime(repo_time_format),
            "pushed_at": repo.pushed_at.strftime(repo_time_format),
            "stargazers_count": repo.stargazers_count,
            "watchers_count": repo.watchers_count,
            "language": repo.language,
            "default_branch": repo.default_branch,
            "num_contributors": contributors
        })

        num_repos += 1
        print("found {} candidate repos".format(num_repos))
        save_json(repo_candidates, repo_candidates_filename)
        if num_repos >= repos_count:
            break


def retrieve_files(repo, path, files_retrieved):
    print("files retrieved: {}".format(files_retrieved))
    for file in repo.get_contents(path=path):

        files_retrieved += 1

        if files_retrieved > min_files:
            return files_retrieved

        if file.type == "dir":
            files_retrieved = retrieve_files(repo, file.path, files_retrieved)

    return files_retrieved
