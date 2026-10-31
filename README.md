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
├── README.md                                                       # Project overview, architecture, workflow, roadmap, and credits.
├── pyproject.toml                                                  # Python project configuration and dependency management.
├── src/
│   └── air_quality_pipeline/
│       ├── bronze/
│       │   ├── config.py                                           # Config settings for ingestion and storage access.
│       │   └── get_raw_data.py                                     # Main data ingestion script for downloading and extracting source files.
│       ├── silver/                                                 # Silver layer package for cleaned and quality-checked data logic.
│       └── gold/                                                   # Gold layer package for curated final analytical models.
├── dbt/
│   ├── dbt_project.yml                                             # dbt project configuration.
│   ├── profiles.yml                                                # dbt connection profile configuration. (.gitignore)
│   ├── dev.duckdb                                                  # Local DuckDB database used in development. (.gitignore)
│   ├── analyses/                                                   # Ad hoc SQL analysis files.
│   ├── macros/                                                     # Reusable dbt macros.
│   ├── models/
│   │   ├── staging/
│   │   │   └── eea/
│   │   │       ├── _stg_eea__models.yml                            # Metadata and tests for staging models.
│   │   │       └── stg_eea__air_quality.sql                        # Staging model for the EEA dataset.
│   │   ├── intermediate/
│   │   │   └── eea/
│   │   │       ├── _int_eea__models.yml                            # Metadata and tests for intermediate models.
│   │   │       ├── int_air_quality__valid.sql                      # Validity-filtered intermediate dataset.
│   │   │       └── int_air_quality__deduplicated.sql               # Deduplicated intermediate dataset.
│   │   └── marts/
│   │       └── eea/
│   │           ├── _marts_eea__models.yml                          # Metadata and tests for mart models.
│   │           ├── dim_countries.sql                               # Country dimension table.
│   │           ├── fct_daily_pollutant_by_country.sql              # Daily pollutant fact table by country.
│   │           ├── fct_monthly_pollutant_by_country.sql            # Monthly pollutant fact table by country.
│   │           ├── fct_yearly_exceedance.sql                       # Yearly exceedance fact table.
│   │           └── fct_yearly_pollutant_by_country.sql             # Yearly pollutant fact table by country.
│   ├── seeds/
│   │   ├── _seeds.yml                                              # Seed metadata and schema definitions.
│   │   └── countries.csv                                           # Country-code reference data.
│   ├── snapshots/                                                  # Historical snapshot definitions.
│   ├── target/                                                     # Compiled dbt artifacts and execution output.
│   └── tests/                                                      # dbt tests and custom data validation rules.
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
