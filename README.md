# code-quality-and-popularity
by Jesper Findahl

Written in Python version 3.x.

## Prerequisites
Requires:
- [PyGithub](http://pygithub.readthedocs.io/en/latest/introduction.html#very-short-tutorial), e.g. `pip3 install PyGithub`
- [GitPython](http://gitpython.readthedocs.io/en/stable/), e.g. `pip3 install gitpython`
- [pandas](http://pandas.pydata.org/pandas-docs/stable/index.html), e.g. `pip3 install pandas`

## GitHub configuration
A file named `config` placed in the same directory as the script is required to connect to github.
- first line: username
- second line: password

## Run
Requires Python 3.x. So run as `python3 ...`.

## Folders
The tool will create 1 folder `data`.

## Usage
1. Use `get_repo_candidates.py` to fetch the basic data for the repositories via GitHub search API. The result is stored in the file `data\repo_candidates.json`
2. Use `static_code_metrics.py` to clone the candidate repos and compute the CK metrics. The repos will be stored locally temporarily, one by one. The results per project is stored in `data\code-metrics\` with the ID of the repo in the filename. The aggregated metrics are stored in the file `data\final-code-metrics.csv`.
 3. Use the R scripts in `analysis.Rmd` to replicate the results in the project report.

