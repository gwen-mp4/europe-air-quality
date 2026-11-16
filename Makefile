SHELL := /bin/bash
ENV   := set -a && source dbt/.env && set +a

.DEFAULT_GOAL := help
.PHONY: help install ingest dbt-debug dbt-build dbt-docs map-sources map-dev map-build refresh

help:  ## Show the available commands
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

install:  ## Install Python and Node dependencies
	uv sync
	cd evidence-legacy && npm install

ingest:  ## Download EEA data into S3 (editable in `src/air_quality_pipeline/bronze/utils/config.py`)
	$(ENV) && uv run python -m src.air_quality_pipeline.bronze.ingestion.get_raw_data

dbt-debug:  ## Check the dbt connection
	$(ENV) && cd dbt && uv run dbt debug --profiles-dir .

dbt-build:  ## Build all dbt models and tests
	$(ENV) && cd dbt && uv run dbt build --profiles-dir .

dbt-docs:  ## Generate and serve the dbt documentation
	cd dbt && uv run dbt docs generate --profiles-dir . && uv run dbt docs serve --profiles-dir .

map-sources:  ## Load the exported Parquet into Evidence
	cd evidence-legacy && npm run sources

map-dev:  ## Start the map locally (http://localhost:3000)
	cd evidence-legacy && npm run dev

map-build:  ## Build the static map site
	cd evidence-legacy && npm run build

refresh: ingest dbt-build map-sources  ## Ingest, transform and reload the map