# 🌤️ Automated Weather ETL Pipeline & Live Dashboard

![CI Status](https://github.com/Flashters/ph-weather-pipeline/actions/workflows/ci.yml/badge.svg)

## 📊 Overview & Key Highlights
Automated end-to-end data engineering pipeline extracting hourly weather forecast and historical data for major Philippine cities (Manila, Cebu, Davao, Baguio, Batangas) via Open-Meteo API.

* **Automation:** Runs autonomously every 6 hours via GitHub Actions workflows.
* **Idempotent Upsert:** Implements primary key constraints (`city`, `obs_time`) to prevent duplicate historical records.
* **Data Quality Gate:** Rejects missing values and invalid physiological metrics (-10°C to 55°C, 0-100% humidity).

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