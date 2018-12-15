# SRED Epic Reporting Tool

Tool to generate useful reports from Harvest data for SRED reporting using [numpy](http://www.numpy.org/) and [pandas](https://pandas.pydata.org/).

Currently generates several csv files:

* Person week total hours including time off - `total-hours.csv`
* Person week work hours  - `work-hours.csv`
* Person week SRED hours - `sred-hours.csv`
* Person week epic lists - `epics.csv`
* Person week missing epics - `missing-epics.csv`

The `epics.csv` file shows the list of Notes for a given week.  No cleanup is done on the Notes themselves.
The `missing-epics.csv` list indicates weeks where there was SRED hours logged, but there was no Note for that week.

To work with the tool you need to use the [pipenv python packaging and environment stool](https://pipenv.readthedocs.io/en/latest/) to install the dependencies.

Once the repo is cloned, cd to the directory and run.

```
pipenv install
```

This should install all of the required dependencies.

To run it in the shell:

```
pipenv shell
python weekly_report.py data/harvest_time_report_from2018-10-01to2018-12-31.csv reports-2018-11-25
```
This will generate csv files in the `reports-2018-11-25` directory