# Dependencies

The following tools are required to execute the code:

* `python2.7`
* `python-virtualenv`
* `make`

### Ubuntu
```
$ sudo apt-get install python-dev python-virtualenv build-essential
```

# Setup

* Prepare the virtual environment by running `make env`:
```
$ make env
New python executable in venv/bin/python2.7
Also creating executable in venv/bin/python
...
Successfully installed ...
```

# Execution

* You can list all of the available `make` targets (with descriptions) by running `make`:
```
$ make
###########################################################
# Cohorts Analysis Actions
###########################################################

clean                                    Removes the temporary files and the virtual environment
cohorts-1w-est                           Run cohorts analysis - display all cohorts w/ 7-day buckets (EST timezone)
cohorts-1w-est-8                         Run cohorts analysis - display 8 cohorts w/ 7-day buckets (EST timezone)
cohorts-1w-pst                           Run cohorts analysis - display all cohorts w/ 7-day buckets (PST timezone)
cohorts-1w-pst-8                         Run cohorts analysis - display 8 cohorts w/ 7-day buckets (PST timezone)
cohorts-1w-utc                           Run cohorts analysis - all ALL cohorts w/ 7-day buckets (UTC timezone)
cohorts-1w-utc-8                         Run cohorts analysis - display 8 cohorts w/ 7-day buckets (UTC timezone)
env                                      create virtualenv for DEV/TEST environment
env-prod                                 create virtualenv for PROD environment
lint                                     Runs the linter over the codebase
test                                     Runs the cohort analysis tests

    (use 'make <target> -n' to show the commands)
```

* The `make` targets can be expanded into the full command using the `-n` flag:
```
$ make cohorts-1w-utc -n
. venv/bin/activate; python cohorts/cohort.py \
		data/orders.csv \
		data/customers.csv \
		--timezone UTC \
		--days-per-bucket 7
```

* The main program can also be run with the `-h` flag to see the available options:
```
$ ./venv/bin/python cohorts/cohort.py -h
usage: cohort.py [-h] [-s LIMIT] [-tz TIMEZONE] [-d DAYS] [-v]
                 orders_file customers_file

positional arguments:
  orders_file           the orders CSV file
  customers_file        the customers CSV file

optional arguments:
  -h, --help            show this help message and exit
  -s LIMIT, --limit LIMIT
                        num cohorts to display
  -tz TIMEZONE, --timezone TIMEZONE
                        the timezone associated with the cohort groups
  -d DAYS, --days-per-bucket DAYS
                        number of days per bucket
  -v, --verbosity       display debugging information
```

# Examples

* Here is an example:
```
$ make cohorts-1w-4
+-----------+----------------+--------------------+------------------+------------------+------------------+
| Cohort    | Customers      | 0-6 days           | 7-13 days        | 14-20 days       | 21-27 days       |
+-----------+----------------+--------------------+------------------+------------------+------------------+
| 7/1-7/7   | 1102 customers | 15% orderers (163) |                  |                  |                  |
|           |                | 15% 1st time (163) |                  |                  |                  |
...
+-----------+----------------+--------------------+------------------+------------------+------------------+
```

# Tests

* To run the tests, run `make test`:
```
$ make test
Successful
.....
----------------------------------------------------------------------
Ran 5 tests in 0.005s

OK
```
