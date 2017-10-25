PROJECT_NAME=Cohorts Analysis
PYTHON_ENV?=venv
DATA_DIR=data
PACKAGE_NAME=cohorts
IN_ENV=. $(PYTHON_ENV)/bin/activate


.PHONY: help
help:
	@echo "###########################################################"
	@echo "# $(PROJECT_NAME) Actions"
	@echo "###########################################################"
	@echo ""
	@grep -E -h '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}' | sort
	@echo ""
	@echo "    (use 'make <target> -n' to show the commands)"
	@echo ""


.PHONY: clean
clean:  ## Removes the temporary files and the virtual environment
	@find . \
		-name *.pyc \
		-exec rm -f {} \
		\;
	@rm -rf $(PYTHON_ENV)


.PHONY: env
env:  ## create virtualenv for DEV/TEST environment
	@virtualenv --no-site-packages --prompt='($(PROJECT_NAME)) ' $(PYTHON_ENV)
	@$(IN_ENV); pip install --upgrade pip distribute setuptools markerlib
	@$(IN_ENV); pip install --upgrade pyOpenSSL ndg-httpsclient pyasn1
	@$(IN_ENV); pip install -r requirements-dev.txt


.PHONY: env-prod
env-prod:  ## create virtualenv for PROD environment
	@virtualenv --no-site-packages --prompt='($(PROJECT_NAME)) ' $(PYTHON_ENV)
	@$(IN_ENV); pip install --upgrade pip distribute setuptools markerlib
	@$(IN_ENV); pip install --upgrade pyOpenSSL ndg-httpsclient pyasn1
	@$(IN_ENV); pip install -r requirements.txt


.PHONY: lint
lint:  ## Runs the linter over the codebase
	@$(IN_ENV); flake8 $(PACKAGE_NAME) --config=setup.cfg && echo 'Lint Success'


.PHONY: test
test: lint  ## Runs the cohort analysis tests
	@$(IN_ENV); nose2 -c conf/nose2.cfg


.PHONY: cohorts-1w-utc
cohorts-1w-utc:  ## Run cohorts analysis - all ALL cohorts w/ 7-day buckets (UTC timezone)
	@$(IN_ENV); python $(PACKAGE_NAME)/cohort.py \
		$(DATA_DIR)/orders.csv \
		$(DATA_DIR)/customers.csv \
		--timezone UTC \
		--days-per-bucket 7


.PHONY: cohorts-1w-utc-8
cohorts-1w-utc-8:  ## Run cohorts analysis - display 8 cohorts w/ 7-day buckets (UTC timezone)
	@$(IN_ENV); python $(PACKAGE_NAME)/cohort.py \
		$(DATA_DIR)/orders.csv \
		$(DATA_DIR)/customers.csv \
		--timezone UTC \
		--days-per-bucket 7 \
		--limit 8


.PHONY: cohorts-1w-pst
cohorts-1w-pst:  ## Run cohorts analysis - display all cohorts w/ 7-day buckets (PST timezone)
	@$(IN_ENV); python $(PACKAGE_NAME)/cohort.py \
		$(DATA_DIR)/orders.csv \
		$(DATA_DIR)/customers.csv \
		--timezone America/Los_Angeles \
		--days-per-bucket 7


.PHONY: cohorts-1w-pst-8
cohorts-1w-pst-8:  ## Run cohorts analysis - display 8 cohorts w/ 7-day buckets (PST timezone)
	@$(IN_ENV); python $(PACKAGE_NAME)/cohort.py \
		$(DATA_DIR)/orders.csv \
		$(DATA_DIR)/customers.csv \
		--timezone America/Los_Angeles \
		--days-per-bucket 7 \
		--limit 8


.PHONY: cohorts-1w-est
cohorts-1w-est:  ## Run cohorts analysis - display all cohorts w/ 7-day buckets (EST timezone)
	@$(IN_ENV); python $(PACKAGE_NAME)/cohort.py \
		$(DATA_DIR)/orders.csv \
		$(DATA_DIR)/customers.csv \
		--timezone America/New_York \
		--days-per-bucket 7


.PHONY: cohorts-1w-est-8
cohorts-1w-est-8:  ## Run cohorts analysis - display 8 cohorts w/ 7-day buckets (EST timezone)
	@$(IN_ENV); python $(PACKAGE_NAME)/cohort.py \
		$(DATA_DIR)/orders.csv \
		$(DATA_DIR)/customers.csv \
		--timezone America/New_York \
		--days-per-bucket 7 \
		--limit 8
