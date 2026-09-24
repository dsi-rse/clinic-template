
# general
mkfile_path := $(abspath $(firstword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
current_abs_path := $(subst Makefile,,$(mkfile_path))

# pipeline constants
# PROJECT_NAME
project_name := "{{ cookiecutter.project_slug }}"
project_dir := "$(current_abs_path)"

# environment variables
include .env
{% if cookiecutter.data_dir != 'none' %}
# Check required environment variables
ifeq ($(DATA_DIR),)
	$(error DATA_DIR must be set in .env file)
endif
{% endif %}

{% if cookiecutter.docker == "yes" %}# Build Docker image
.PHONY: build-only run-interactive run-notebook

# Build Docker image
build-only:
	docker compose build

run-interactive: build-only
	docker compose run -it --rm $(project_name) /bin/bash

run-notebooks: build-only
	docker compose run --rm -p 8888:8888 -t $(project_name) \
	jupyter lab --port=8888 --ip='*' --NotebookApp.token='' --NotebookApp.password='' \
	--no-browser --allow-root

{% endif %}
{% if cookiecutter.examples in ['dashboard', 'data-science-and-dashboard'] %}
# Dashboard targets
.PHONY: dashboard-data dashboard-install dashboard-dev dashboard-build

{% if cookiecutter.docker == "yes" %}
dashboard-data:
	docker compose run --rm dashboard-data

dashboard-install:
	docker compose run --rm dashboard npm install

dashboard-dev: dashboard-install
	docker compose run --rm -p 5173:5173 dashboard npm run dev -- --host

dashboard-build: dashboard-install
	docker compose run --rm dashboard npm run build

{% else %}
# pull_data.py is stdlib-only, so it runs with any host python3
dashboard-data:
	python3 dashboard/scripts/pull_data.py

dashboard-install:
	cd dashboard && npm install

dashboard-dev: dashboard-install
	cd dashboard && npm run dev -- --host

dashboard-build: dashboard-install
	cd dashboard && npm run build

{% endif %}
{% endif %}
{% if cookiecutter.cluster == "yes" %}
open-ssh-login-node:
	code --remote ssh-remote+fe.ds ~/{{ cookiecutter.project_slug }}
{% endif %}
