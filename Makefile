
SHELL := /bin/bash
.SHELLFLAGS := -e -c
.ONESHELL:

# Load environment variables from dbt/.env
ENV := set -a; source dbt/.env; set +a

# Removed AD AL AT BA BE BG CH CY CZ DE DK EE ES FI FR GB GR HR HU IE IS IT LT LU LV ME MK MT NL because already done
COUNTRIES ?= NO PL PT RO RS SE SI SK
YEARS     ?= 2020 2021 2022 2023 2024 2025

.DEFAULT_GOAL := help

.PHONY: help install ingest \
        dbt-debug dbt-build dbt-batches dbt-rest dbt-test dbt-docs \
        map-sources map-dev map-build transform refresh

help:  ## Show the available commands
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

install:  ## Install Python and Node dependencies
	uv sync
	cd evidence-legacy
	npm install

ingest:  ## Download EEA data into S3 (editable in `src/air_quality_pipeline/bronze/utils/config.py`)
	$(ENV)
	uv run python -m src.air_quality_pipeline.bronze.ingestion.get_raw_data

dbt-debug:  ## Check the dbt connection
	$(ENV)
	cd dbt
	uv run dbt debug --profiles-dir .

dbt-build:  ## Build all dbt models and tests (Not recommended on small local machine)
	$(ENV)
	cd dbt
	uv run dbt build --profiles-dir .

dbt-batches:  ## Build the heavy hourly models one country/year slice at a time
	$(ENV)
	cd dbt
	for c in $(COUNTRIES); do
		for y in $(YEARS); do
			echo "Building country=$$c year=$$y"
			uv run dbt run --select tag:heavy --vars "{country: '$$c', year: $$y}" --profiles-dir .
		done
	done

dbt-rest:  ## Build everything else (dimensions, facts, marts)
	$(ENV)
	cd dbt
	uv run dbt run --exclude tag:heavy --profiles-dir .

dbt-test:  ## Run all dbt tests once
	$(ENV)
	cd dbt
	uv run dbt test --profiles-dir .

dbt-docs:  ## Generate and serve the dbt documentation
	cd dbt
	uv run dbt docs generate --profiles-dir .
	uv run dbt docs serve --profiles-dir .

map-sources:  ## Load the exported Parquet into Evidence
	cd evidence-legacy
	npm run sources

map-dev:  ## Start the map locally (http://localhost:3000)
	cd evidence-legacy
	npm run dev

map-build:  ## Build the static map site
	cd evidence-legacy
	npm run build

transform: dbt-batches dbt-rest dbt-test  ## Full transformation

refresh: ingest transform map-sources  ## Ingest, transform and reload the map
