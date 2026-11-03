# 🌤️ Automated Weather ETL Pipeline & Live Dashboard

[![CI Pipeline](https://github.com/Flashters/ph-weather-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/Flashters/ph-weather-pipeline/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ph-weather-pipeline.streamlit.app)

## 📊 Overview & Key Highlights
Automated end-to-end data engineering pipeline extracting hourly weather forecast and historical data for major Philippine cities (Manila, Cebu, Davao, Baguio, Batangas) via Open-Meteo API.

- **Automation:** Runs autonomously every 6 hours via GitHub Actions workflows.
- **Idempotent Upsert:** Implements primary key constraints (`city`, `obs_time`) to prevent duplicate historical records.
- **Data Quality Gate:** Rejects missing values and invalid physiological metrics (-10°C to 55°C, 0-100% humidity).

🔗 **Live App:** [ph-weather-pipeline.streamlit.app](https://ph-weather-pipeline.streamlit.app)

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
