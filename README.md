# 🌤️ Automated Weather ETL Pipeline & Live Dashboard

[![CI Pipeline](https://github.com/Flashters/ph-weather-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Flashters/ph-weather-pipeline/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ph-weather-pipeline.streamlit.app)

An automated end-to-end data engineering pipeline extracting hourly weather forecast and historical data for major Philippine cities (Manila, Cebu, Davao, Baguio, Batangas) via the Open-Meteo API, complete with CI/CD testing and a live web dashboard.

🔗 **Live App:** [ph-weather-pipeline.streamlit.app](https://ph-weather-pipeline.streamlit.app)

---

## 📊 Overview & Key Highlights
- **Automation:** Runs autonomously every 6 hours via GitHub Actions cron workflows to fetch and refresh meteorological metrics.
- **Idempotent Upsert:** Implements strict primary key constraints (`city`, `obs_time`) inside SQLite to prevent duplicate records during overlapping pipeline triggers.
- **Data Quality Gate:** Programmatically rejects missing values and out-of-bounds physiological metrics (-10°C to 55°C, 0-100% humidity).

---

## 🛠️ Tech Stack & Architecture
- **Language:** Python (`pandas`, `requests`)
- **Data Store:** SQLite (`weather.db`)
- **Testing Framework:** `pytest`
- **Orchestration & CI/CD:** GitHub Actions
- **Web Frontend:** Streamlit Community Cloud

---

## 📂 Project Structure & Execution
- **`etl.py`:** End-to-end data pipeline script incorporating REST API extraction, data quality validation checks, and idempotent database loading.
- **`app.py`:** Interactive Streamlit web application providing multi-city trend comparisons, row storage tracking, and temperature/precipitation visualizations.
- **`tests/test_etl.py`:** Unit test suite validating schema enforcement, function reliability, and data integrity.
- **`.github/workflows/ci.yml`:** Automated CI pipeline verifying code syntax and executing `pytest` runs on every push.

---

## 🔍 Implementation Drills & Methodology
This codebase incorporates structured checkpoints to ensure pipeline reliability and data integrity:
1. **API Extraction & Parsing (`etl.py`):** Pulls hourly forecast and historical records from Open-Meteo across targeted Philippine coordinates, flattening JSON payloads into structured tabular arrays.
2. **Data Quality Validation Gate:** Validates raw schema headers, filters out null values, and enforces logical domain bounds for temperature and relative humidity metrics before writing to disk.
3. **Idempotent Storage Layer:** Leverages SQLite `INSERT OR REPLACE` mechanics to guarantee safe, repeatable ingestion runs without creating database row bloat or duplicates.
4. **Continuous Integration Testing (`pytest`):** Runs automated test checks on every version control commit to ensure module imports, path resolutions, and schema requirements remain stable.

---

## 📖 Glossary of Technical Terms
- **ETL (Extract, Transform, Load):** A data pipeline process that gathers data from an external source (Open-Meteo API), cleans and validates it, and loads it into a target data store (`weather.db`).
- **Idempotency:** An operation property where executing the command multiple times yields the exact same database state as running it once, preventing duplicate records.
- **Data Quality Gate:** A programmatic validation checkpoint that stops invalid, corrupt, or out-of-range data from propagating downstream into production tables.
- **CI/CD (Continuous Integration / Continuous Deployment):** An automated software practice (managed here via GitHub Actions) that tests and builds code changes instantly upon pushing to version control.
- **SQLite:** A lightweight, serverless file-based relational database management system used for portable local storage.

---

## 🏗️ Data Engineering Architecture
```text
[Open-Meteo REST API] (5 PH Cities)
         │
         ▼
[Extraction & Normalization] (`etl.py` / Requests + Pandas)
         │
         ▼
[Data Quality Gate] (Schema & Range Validation Checks)
         │
         ▼
[Idempotent Loading] (`weather.db` / SQLite `INSERT OR REPLACE`)
         │
         ▼
[Automated Orchestration] (GitHub Actions Cron / 6 Hrs)
         │
         ▼
[Interactive Dashboard] Streamlit Web App (`app.py`)
