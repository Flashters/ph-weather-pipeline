"""Streamlit dashboard for the weather ETL. Run: streamlit run app.py"""
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PH Weather Pipeline", layout="wide")
st.title("Philippine weather pipeline")

with sqlite3.connect("weather.db") as con:
    df = pd.read_sql_query("SELECT * FROM weather_hourly", con, parse_dates=["obs_time"])

cities = st.multiselect("Cities", sorted(df["city"].unique()),
                        default=sorted(df["city"].unique()))
view = df[df["city"].isin(cities)]

c1, c2, c3 = st.columns(3)
c1.metric("Rows stored", f"{len(view):,}")
c2.metric("Avg temp (C)", f"{view['temp_c'].mean():.1f}")
c3.metric("Total rain (mm)", f"{view['rain_mm'].sum():.1f}")

st.line_chart(view.pivot(index="obs_time", columns="city", values="temp_c"))
st.dataframe(view.sort_values("obs_time", ascending=False).head(100))