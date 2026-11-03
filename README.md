# Europe Air Quality Pipeline

## 📖 Overview
This project implements an ELT pipeline for European air quality data, covering historical records from January 2020 to December 2025. The objective is to ingest, validate, transform, and model air quality measurements in a structured and analysis-ready format for reporting and downstream analytics.

The pipeline follows a medallion-style architecture, with bronze, silver, and gold layers progressively improving data quality and analytical readiness. The project is still a work in progress, and the current scope focuses on verified EEA data sources rather than completely unverified raw sources. The raw files are not entirely "raw" in the strictest sense because they come from the European Environment Agency (EEA), which provides validated and trusted measurements.

The repository is designed to support both ingestion and analytical transformation, with a path toward stronger orchestration, data quality checks, lineage tracking, and governance as the project evolves.

### 🔎 Technologies Used
- **Data Lake / Object Storage**: [AWS S3](https://aws.amazon.com/s3/)
- **Data Transformation & Modeling**: [dbt](https://www.getdbt.com/)
- **Analytical Engine**: [DuckDB](https://duckdb.org/)
- **Ingestion & Automation**: [Python](https://www.python.org/)

## 🏗️ Architecture
The project follows a medallion ELT architecture:

```mermaid
flowchart LR
    A[Source Data - EEA] --> B[Python Ingestion]
    B --> C[AWS S3 - Bronze]
    C --> D[dbt - Staging]
    D --> E[dbt - Intermediate / Silver]
    E --> F[dbt - Marts / Gold]
    F --> G[Analytics and Reporting]
```

This is a simple and scalable architecture that separates ingestion, transformation, and final analytical models while keeping the system easy to evolve.

### Workflow
1. A Python ingestion script downloads the EEA air quality source data and extracts it into Parquet format.
2. The generated Parquet files are stored in AWS S3, acting as the bronze layer and landing zone for the pipeline.
3. dbt reads the stored data and builds staging models to standardize schema, column names, and data types.
4. The staging data is then passed through intermediate models, where validity rules, deduplication logic, and basic cleaning operations are applied.
5. The cleaned and enriched intermediate data is transformed into mart models for downstream reporting and analysis with dbt.
6. DuckDB executes the SQL transformation logic efficiently, ensuring fast and flexible analytical processing.

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| --- | --- | --- |
| **Data Lake / Storage** | [AWS S3](https://aws.amazon.com/s3/) | Stores the ingested Parquet datasets and acts as the bronze storage layer. |
| **Data Transformation** | [dbt](https://www.getdbt.com/) | Builds staging, intermediate, and mart models and handles SQL-based cleaning and enrichment. |
| **Analytical Engine** | [DuckDB](https://duckdb.org/) | Runs analytical SQL efficiently for dbt transformations and local querying. |
| **Ingestion Layer** | [Python](https://www.python.org/) | Downloads source data and prepares it for storage in the pipeline. |

## 📦 Project Structure
```text
air-quality-pipeline/
├── README.md                                                          # Project overview, architecture, workflow, roadmap, and credits.
├── pyproject.toml                                                     # Python project configuration and dependency management.
├── src/
│   └── air_quality_pipeline/
│       └── bronze/
│           ├── ingestion/
│           │   ├── get_date.py                                        # Date helpers used by ingestion logic.
│           │   ├── get_raw_data.py                                    # Main data ingestion script for downloading and extracting source files.
│           │   └── logs/
│           └── utils/
│               ├── config.py                                          # Config settings for ingestion and storage access.
│               └── logging.py                                         # Logging helpers for pipeline execution.
├── dbt/
│   ├── dbt_project.yml                                                # dbt project configuration.
│   ├── profiles.yml                                                   # dbt connection profile configuration.
│   ├── dev.duckdb                                                     # Local DuckDB database used in development.
│   ├── analyses/                                                      # Ad hoc SQL analysis files.
│   ├── logs/                                                          # dbt execution logs.
│   ├── macros/                                                        # Reusable dbt macros.
│   ├── models/
│   │   ├── intermediate/
│   │   │   ├── E1a/
│   │   │   │   ├── _int_e1a__models.yml                               # Metadata and tests for intermediate E1a models.
│   │   │   │   ├── int_e1a__deduplicated.sql                          # Deduplicated E1a intermediate dataset.
│   │   │   │   └── int_e1a__valid.sql                                 # Validity-filtered E1a intermediate dataset.
│   │   │   └── E2a/
│   │   │       └── int_e2a__daily.sql                                 # Daily E2a intermediate dataset.
│   │   ├── marts/
│   │   │   ├── E1a/
│   │   │   │   ├── _marts_e1a__models.yml                             # Metadata and tests for E1a mart models.
│   │   │   │   ├── dim_e1a__countries.sql                             # E1a country dimension table.
│   │   │   │   ├── dim_e1a__stations.sql                              # E1a station dimension table.
│   │   │   │   ├── fct_e1a__monthly_country_pollutant.sql             # E1a monthly country-pollutant fact table.
│   │   │   │   ├── fct_e1a_yearly_country_exceedance.sql              # E1a yearly exceedance fact table.
│   │   │   │   └── fct_e1a_yearly_country_pollutant.sql               # E1a yearly country-pollutant fact table.
│   │   │   └── E2a/
│   │   │       ├── dim_e2a_countries.sql                              # E2a country dimension table.
│   │   │       ├── dim_e2a_stations.sql                               # E2a station dimension table.
│   │   │       └── fct_e2a_daily_country_pollutant.sql                # E2a daily country-pollutant fact table.
│   │   └── staging/
│   │       ├── E1a/
│   │       │   ├── _stg_e1a__models.yml                               # Metadata and tests for E1a staging models.
│   │       │   ├── _stg_e1a__sources.yml                              # Source definitions for E1a staging models.
│   │       │   └── stg_e1a__air_quality.sql                           # E1a staging model for EEA air-quality data.
│   │       └── E2a/
│   ├── seeds/
│   │   ├── _seeds.yml                                                 # Seed metadata and schema definitions.
│   │   └── countries.csv                                              # Country-code reference data.
│   ├── snapshots/                                                     # Historical snapshot definitions.
│   ├── target/                                                        # Compiled dbt artifacts and execution output.
│   ├── dbt_packages/                                                  # Installed dbt dependencies.
│   └── tests/                                                         # dbt tests and custom data validation rules.
└──
```

## 🔧 Setup
This section is intentionally left out for now while the project continues to evolve.

## 🚀 Future
- [ ] Add non-verified raw data from the most recent period and clean it before modeling.
- [ ] Add data quality checks using dbt and tools such as Soda.
- [ ] Add Apache Airflow for orchestrating ingestion and transformation workflows.
- [ ] Add data validation with Pydantic.
- [ ] Add data lineage tracking across the pipeline.
- [ ] Add ACID support with Delta Lake.
- [ ] Add monitoring and dashboards with Prometheus and Grafana.
- [ ] Containerize the full project for simpler deployment and reproducibility.

## 🤝 Credit
- AWS S3: used as the storage and landing layer for the pipeline data lake.
- dbt: used for staging, intermediate, and mart transformations, as well as testing and modeling.
- DuckDB: used as the analytical engine for fast SQL processing in the ELT workflow.
- Python: used for data ingestion and extraction logic.
- EEA (European Environment Agency): provides the verified air quality datasets used in this project.
