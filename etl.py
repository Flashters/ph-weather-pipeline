"""Project 3 - Automated weather ETL: extract (Open-Meteo) -> validate -> load (SQLite)."""
import sqlite3
from datetime import datetime, timezone
import pandas as pd
import requests

CITIES = {
    "Manila": (14.5995, 120.9842), "Cebu": (10.3157, 123.8854),
    "Davao": (7.1907, 125.4553), "Baguio": (16.4023, 120.5960),
    "Batangas": (13.7565, 121.0583),
}
URL = "https://api.open-meteo.com/v1/forecast"
DB = "weather.db"

def extract(city, lat, lon):
    params = {"latitude": lat, "longitude": lon, "timezone": "Asia/Manila",
              "hourly": "temperature_2m,relative_humidity_2m,precipitation",
              "past_days": 1, "forecast_days": 1}
    r = requests.get(URL, params=params, timeout=20)
    r.raise_for_status()                      # fail loudly -> GitHub Action turns red
    h = r.json()["hourly"]
    df = pd.DataFrame({"obs_time": h["time"], "temp_c": h["temperature_2m"],
                       "humidity": h["relative_humidity_2m"],
                       "rain_mm": h["precipitation"]})
    df["city"] = city
    return df

def validate(df):
    """Data-quality gate: bad rows are dropped and counted, not silently loaded."""
    before = len(df)
    df = df.dropna(subset=["temp_c", "humidity"])
    df = df[df["temp_c"].between(-10, 55) & df["humidity"].between(0, 100)
            & (df["rain_mm"].fillna(0) >= 0)]
    print(f"validate: kept {len(df)}/{before} rows")
    if df.empty:
        raise ValueError("No valid rows - aborting load")
    return df

def load(df, db=DB):
    df = df.assign(loaded_at=datetime.now(timezone.utc).isoformat())
    with sqlite3.connect(db) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS weather_hourly (
            city TEXT, obs_time TEXT, temp_c REAL, humidity REAL, rain_mm REAL,
            loaded_at TEXT, PRIMARY KEY (city, obs_time))""")   # PK = no duplicates
        con.executemany(
            "INSERT OR REPLACE INTO weather_hourly VALUES (?,?,?,?,?,?)",
            df[["city", "obs_time", "temp_c", "humidity", "rain_mm", "loaded_at"]]
            .itertuples(index=False, name=None))
    print(f"load: upserted {len(df)} rows")

def run():
    frames = []
    for city, (lat, lon) in CITIES.items():
        try:
            frames.append(extract(city, lat, lon))
        except requests.RequestException as e:      # one city failing != total failure
            print(f"WARN {city}: {e}")
    if not frames:
        raise RuntimeError("All extractions failed")
    load(validate(pd.concat(frames, ignore_index=True)))

if __name__ == "__main__":
    run()