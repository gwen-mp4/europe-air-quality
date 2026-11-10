# European Air Quality ELT Pipeline

A batch ELT pipeline that ingests, validates, cleans and models European air quality measurements published by the European Environment Agency (EEA). The project focuses on data quality, reproducibility and clear modeling decisions rather than on heavy infrastructure.

> **Status: work in progress.** The core pipeline (ingestion → bronze → silver → gold) works end to end on the current scope. See [Status](#-status) and [Roadmap](#-roadmap).

## 📖 Overview

- **Scope:** hourly measurements of selected pollutants, January 2020 to December 2025, from the EEA verified dataset (E1a). The scope is extended country by country and pollutant by pollutant.
- **Scale:** more than 70 million hourly rows in staging for France alone (5 pollutants, 2020–2025).
- **Approach:** raw files are kept untouched in S3 (bronze); all cleaning decisions live in versioned SQL models (silver and gold) so they are visible, testable and reversible.
- **Stack:** Python, AWS S3, Parquet, DuckDB, dbt, managed with `uv`.

## 📌 Status

| Area | State |
| --- | --- |
| Ingestion of EEA Parquet archives into S3 | ✅ Done |
| Sampling point metadata (EEA data flow D) | ✅ Done |
| dbt staging, intermediate and marts models | ✅ Done (growing) |
| dbt data tests | ✅ Basic coverage |
| Station dimension with coordinates | ✅ Done |
| Interactive station map | 🚧 Next |
| More countries and pollutants | 🚧 In progress |
| CI, orchestration, recent unverified data | 📝 Planned |

## 🏗️ Architecture

```mermaid
flowchart LR
    A[EEA Download Service<br/>E1a verified data] --> B[Python ingestion]
    M[EEA metadata<br/>data flow D] --> B
    B --> C[(AWS S3<br/>bronze: archives, parquet, metadata)]
    C --> D[dbt + DuckDB<br/>staging]
    D --> E[dbt + DuckDB<br/>intermediate / silver]
    E --> F[dbt + DuckDB<br/>marts / gold]
    F --> G[Analytics and map<br/>planned]
```

| Layer | Where | What happens |
| --- | --- | --- |
| **Bronze** | S3 (`raw/eea/`) | Files exactly as delivered by the EEA (ZIP archives and extracted Parquet), plus metadata. Never modified. |
| **Staging** | dbt (DuckDB) | One model per source. Renaming, typing, nothing else. |
| **Silver** (intermediate) | dbt (DuckDB) | Decisions: validity filtering, sentinel handling, quality flags, deduplication. |
| **Gold** (marts) | dbt (DuckDB) | Analysis-ready tables: dimensions and facts. |

## ⚙️ How it works

### 1. Source data

The EEA Air Quality Download Service delivers ZIP archives of Parquet files for a requested country, pollutant and period. Two datasets exist:

- **E1a:** verified data, reported by countries after validation. This is what the project uses.
- **E2a:** recent, not yet verified data. Not implemented yet.

Each measurement carries a `Validity` flag (is the value usable?) and a `Verification` status (has it been checked?). Sampling point coordinates are not in the measurement files: they come from the EEA metadata (data flow D, reported yearly by countries).

### 2. Ingestion (bronze)

Implemented in `src/air_quality_pipeline/bronze/ingestion/`.

1. For one `(country, pollutant, period)`, a request is sent to the EEA download API.
2. The response is checked to be a valid ZIP archive.
3. The archive is uploaded as-is to S3 (`archives/`).
4. The Parquet files inside are extracted and uploaded to S3 (`parquet/`) under Hive-style partitions.

**Why this design**

- Object keys are built from the request parameters, so rerunning the same request overwrites the same objects instead of creating duplicates.
- Keeping the original ZIP files allows auditing and replaying the extraction without downloading again.
- Partitions such as `country=FR/pollutant_name=PM25/year=2020/month=01` are understood by DuckDB, which then only reads the files it needs.

### 3. S3 layout

```text
s3://aws-s3-air-quality-bucket/
└── raw/
    └── eea/
        ├── archives/        # original ZIP files, by country / pollutant / year
        ├── metadata/        # sampling point metadata (EEA data flow D, CSV)
        └── parquet/         # extracted Parquet files, Hive-style partitions
            └── country=FR/
                └── pollutant_name=PM25/
                    └── year=2020/
                        └── month=01/
                            └── ...parquet
```

### 4. Staging

One model per source, only changing the *form* of the data:

- snake_case column names and explicit type casts;
- partition columns (`country`, `pollutant_name`, `year`, `month`) read from the S3 path;
- no filtering, so invalid rows can still be counted and analyzed.

DuckDB reads the Parquet files directly from S3 through the `httpfs` extension and a temporary S3 secret created from environment variables, so no credentials are written in the repository.

### 5. Intermediate (silver)

This is where decisions are made.

| Rule | Why |
| --- | --- |
| Normalize sampling point IDs by removing the country prefix (`FR/SPO-...` → `SPO-...`) | Measurement files and metadata do not use the same ID format; this is the join key. |
| Keep validity codes `1`, `2`, `3`; drop `-99` and `-1` | `1` valid; `2` valid but below detection limit (value given); `3` valid but below detection limit (value replaced by half the limit). `-99` invalid because of maintenance/calibration; `-1` invalid for other reasons. |
| Turn the sentinel value `-999` into `NULL` | `-999` means "no measurement"; leaving it would corrupt every average. |
| Flag instead of delete: `is_below_detection_limit`, `is_imputed`, `is_negative` | Small negative values are normal instrument noise; the decision to exclude them belongs to downstream models. |
| Deduplicate on `(sampling point, pollutant, period start, period end)`, keeping the best verification status and the most recent result | A measurement must appear once. |

### 6. Marts (gold)

- **`dim_eea__sampling_point`:** one row per sampling point, built from the latest declaration in the EEA metadata (coordinates, station type, area type).
- **Analytical marts:** an initial mart linking countries to their number of monitoring stations. More marts are added as the scope grows.

Data tests (`not_null`, `unique`, `relationships`, and more) are declared in the YAML files next to the models and run with `dbt build`.

## ✅ Data quality

- With the current metadata, every sampling point present in the measurements has coordinates (checked in `dim_stations`).
- Quality decisions are kept visible: flags rather than silent deletion, tests rather than assumptions.
- An earlier metadata snapshot (from 2020) was replaced by the EEA data flow D metadata after a per-year match check showed the older file was missing recent sampling points.

## 🧠 Design decisions

| Decision | Reason |
| --- | --- |
| **DuckDB instead of Spark / Databricks** | The data fits on a single machine. DuckDB reads Parquet from S3 directly and handles tens of millions of rows. A cluster would add cost and complexity without a benefit at this scale. |
| **S3 + Parquet** | Cheap, standard, separates storage from compute, and keeps raw data immutable. |
| **dbt for transformations** | Dependency-aware SQL models, tests, documentation and lineage. |
| **Flags instead of deleting rows** | Filtering is a decision; making it in a later model keeps the earlier data inspectable. |
| **Metadata as a source, not a dbt seed** | It is large and changes over time; seeds are meant for small static files. |
| **`uv` for Python dependencies** | Fast, reproducible environments from `pyproject.toml` and a lockfile. |

## 📦 Project structure

```text
air-quality-pipeline/
├── README.md
├── pyproject.toml
├── uv.lock
├── src/
│   └── air_quality_pipeline/
│       └── bronze/                     # Ingestion and bronze layer
│           ├── ingestion/
│           │   ├── get_date.py         # Date helpers for ingestion windows
│           │   └── get_raw_data.py     # Download, validation, extraction and S3 upload
│           └── utils/
│               ├── config.py           # Pipeline and storage configuration
│               └── logging.py          # Logging setup for ingestion runs
│
└── dbt/                                # Silver and gold layers
    ├── dbt_project.yml                 # dbt project configuration
    ├── profiles.yml                    # dbt connection profile (gitignored)
    ├── dev.duckdb                      # Local DuckDB database (gitignored)
    ├── .env.example                    # Environment variables template (no secrets)
    └── models/
        ├── staging/
        │   ├── E1a/                    # Staging models for E1a data
        │   └── E2a/                    # Placeholder for E2a (not implemented)
        ├── intermediate/
        │   └── E1a/                    # Validity rules, flags, deduplication
        └── marts/
            ├── E1a/                    # Dimensions and facts for E1a data
            └── E2a/                    # Placeholder for E2a (not implemented)
```

## 🚀 Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (it installs and manages the Python version and dependencies)
- An AWS account with an S3 bucket and credentials allowed to list, read and write it
- No EEA account or API key is needed

### Installation

```bash
git clone https://github.com/gwen-mp4/europe-air-quality.git
cd air-quality-pipeline

# Create the virtual environment and install dependencies from pyproject.toml / uv.lock
uv sync
```

### Configuration

```bash
cp dbt/.env.example dbt/.env
# Fill in your AWS region, bucket name and credentials
```

dbt does **not** read `.env` files by itself. You have to write down the variables in `profiles.yml` (located in `~/.dbt/profiles.yml` by default on Linux) using Jinja templates:  
```bash
secrets:
- type: s3
    region: "{{ env_var('S3_REGION') }}"
    key_id: "{{ env_var('S3_ACCESS_KEY_ID') }}"
    secret: "{{ env_var('S3_SECRET_ACCESS_KEY') }}"
```

### Run the ingestion

```bash
uv run python -m src.air_quality_pipeline.bronze.ingestion.get_raw_data
```

### Run the transformations

```bash
cd dbt

# Check the connection and the profile
uv run dbt debug --profiles-dir .

# Build everything (models + tests)
uv run dbt build --profiles-dir .
```

On the first run, build step by step to read errors more easily:

```bash
uv run dbt build --select stg_e1a__air_quality --profiles-dir .
uv run dbt build --select +int_e1a__valid --profiles-dir .
```

`+model` selects a model and everything it depends on; `model+` selects it and everything downstream.

## 🛠️ Useful commands

```bash
# List what is stored in S3 and its total size (needs AWS CLI installed and logged via 'aws login')
aws s3 ls s3://{your_bucket_name}/raw/eea/ --recursive --human-readable --summarize

# Generate and open the dbt documentation (includes the lineage graph)
uv run dbt docs generate --profiles-dir .
uv run dbt docs serve --profiles-dir .

# Inspect the local DuckDB database (read-only, avoids lock conflicts, by default, database name is dev.duckdb)
uv run python -c "import duckdb; duckdb.connect('dev.duckdb', read_only=True).sql('show all tables').show()"
```

## 🩺 Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| `dbt debug` cannot find the profile | Run it from the `dbt/` folder with `--profiles-dir .`, and check that the profile name in `profiles.yml` matches `profile:` in `dbt_project.yml`. |
| `Env var required but not provided` | The variables from `.env` were not exported. See [Configuration](#configuration). |
| S3 errors (`403`, `Access Denied`, region errors) | Check the credentials, that the secret region matches the bucket region (eu-west-3), and that the IAM user can list, read and write the bucket. |
| `Could not set lock on file` / `database is locked` | Another process (DuckDB CLI, notebook, IDE extension) has `dev.duckdb` open. Close it or open the database read-only. |
| Out-of-memory errors or the editor freezes on large models | Set `memory_limit`, `temp_directory` and `threads` in the DuckDB settings of the dbt profile, materialize upstream models as tables, and avoid `select *` before window functions. |
| Sampling points do not match the metadata | Check the ID normalization (country prefix) and compare match rates per country before writing any new rule. |
| EEA download returns an error or a non-ZIP response | Temporary service issue or wrong parameters. The request is safe to rerun. |
| First `dbt build` is slow | DuckDB reads Parquet from S3 for the first time. Later models read local tables. |

## ⚠️ Known limitations

- Only verified (E1a) data is processed; recent unverified data is not.
- Timestamps follow the time zone of each reporting network, which matters when aggregating by day.
- Country-level averages (when added) are simple averages across stations, so urban, traffic and rural stations are not weighted differently.
- Coordinates come from yearly declarations by countries; a few recent sampling points may be missing in a given metadata version.
- Single-machine processing: very large extensions to all countries require batching.

## 🗺️ Roadmap

1. Interactive map of stations colored by concentration (static site built with Evidence).
2. Extend to more countries and pollutants (configuration-driven).
3. CI with GitHub Actions: lint, tests and `dbt build` on a small sample.
4. Additional data quality reporting from dbt tests.
5. *(Optional)* Recent unverified data (E2a) with scheduled collection, and orchestration.

## 🤝 Credits

- **Data:** European Environment Agency (EEA). Please refer to the EEA copyright and re-use policy.
- **Tools:** AWS S3, DuckDB, dbt, Python and uv.
