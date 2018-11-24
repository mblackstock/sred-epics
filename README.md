# SRED Time Reporting Tool

Tool to generate useful reports from Harvest data for SRED reporting using [numpy](http://www.numpy.org/) and [pandas](https://pandas.pydata.org/).

To work with the tool you need to use the [pipenv python packaging and environment stool](https://pipenv.readthedocs.io/en/latest/) to install the dependencies.

Once the repo is cloned, cd to the directory and run.

```
pipenv install
```

This should install all of the required dependencies.

To run it in the shell:

```
pipenv shell
python weekly_report.py raw-data/harvest_time_report_from2018-10-01to2018-12-31.csv
```
This will generate csv files in the `reports` directory