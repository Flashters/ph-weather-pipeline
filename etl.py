import sqlite3
import time
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DB_PATH = "weather.db"
API_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = [
    {"name": "Manila", "latitude": 14.5995, "longitude": 120.9842},
    {"name": "Cebu", "latitude": 10.3157, "longitude": 123.8854},
    {"name": "Davao", "latitude": 7.1907, "longitude": 125.4553},
    {"name": "Baguio", "latitude": 16.4023, "longitude": 120.5960},
    {"name": "Batangas", "latitude": 13.7565, "longitude": 121.0583},
]


def create_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,  # waits 2s, 4s, 8s between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": "ph-weather-pipeline/1.0 (https://github.com/Flashters/ph-weather-pipeline)"
        }
    )
    return session


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS hourly_weather (
            city TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature_2m REAL,
            relative_humidity_2m REAL,
            precipitation REAL,
            wind_speed_10m REAL,
            ingested_at TEXT NOT NULL,
            PRIMARY KEY (city, timestamp)
        )
        """
    )
    conn.commit()


def validate(payload: dict) -> bool:
    """Validates that the API payload contains expected hourly weather keys."""
    if not isinstance(payload, dict):
        return False
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        return False
    
    required_keys = ["time", "temperature_2m", "relative_humidity_2m", "precipitation"]
    return all(k in hourly for k in required_keys)


def extract_city(session: requests.Session, city: dict) -> dict:
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "Asia/Manila",
        "forecast_days": 2,
    }
    response = session.get(API_URL, params=params, timeout=(10, 45))
    response.raise_for_status()
    payload = response.json()

    if not validate(payload):
        raise ValueError(f"Invalid payload structure returned for {city['name']}")
    return payload


def transform_and_load(conn: sqlite3.Connection, city_name: str, payload: dict) -> int:
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    precips = hourly.get("precipitation", [])
    winds = hourly.get("wind_speed_10m", [])

    ingested_at = datetime.now(timezone.utc).isoformat()
    rows = []

    for i, ts in enumerate(times):
        rows.append(
            (
                city_name,
                ts,
                temps[i] if i < len(temps) else None,
                humidities[i] if i < len(humidities) else None,
                precips[i] if i < len(precips) else None,
                winds[i] if i < len(winds) else None,
                ingested_at,
            )
        )

    conn.executemany(
        """
        INSERT INTO hourly_weather (
            city, timestamp, temperature_2m, relative_humidity_2m,
            precipitation, wind_speed_10m, ingested_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(city, timestamp) DO UPDATE SET
            temperature_2m = excluded.temperature_2m,
            relative_humidity_2m = excluded.relative_humidity_2m,
            precipitation = excluded.precipitation,
            wind_speed_10m = excluded.wind_speed_10m,
            ingested_at = excluded.ingested_at
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def run() -> None:
    session = create_session()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    success_count = 0

    try:
        for city in CITIES:
            name = city["name"]
            try:
                payload = extract_city(session, city)
                upserted = transform_and_load(conn, name, payload)
                print(f"OK {name}: upserted {upserted} hourly records")
                success_count += 1
            except Exception as exc:
                print(f"WARN {name}: {exc}")
            time.sleep(1.5)  # brief pacing between requests

        if success_count == 0:
            raise RuntimeError("All extractions failed")
    finally:
        conn.close()
        session.close()


if __name__ == "__main__":
    run()
