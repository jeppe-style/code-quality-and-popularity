import seaborn as sns
from scipy import stats

from ccas.constants import data_dir

sns.set(color_codes=True)


def get_success_data(repo_candidates):
    success = []
    for commit in repo_candidates:
        success.append((commit['id'], commit['stargazers_count'], commit['num_contributors']))

    return success


def plot_success_data(repo_candidates):
    success = get_success_data(repo_candidates)
    plot = sns.distplot(success[1], kde=False, fit=stats.gamma)
    plot.figure.savefig("{}/stars_distribution.png".format(data_dir))
