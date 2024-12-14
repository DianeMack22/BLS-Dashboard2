# -*- coding: utf-8 -*-
"""bls_jobs_dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vJe0PbAtoFnONc6A8VJnQKT9Cd0woAIz
"""

import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime

# Clear Streamlit's cache
st.cache_data.clear()
st.cache_resource.clear()

# Function to calculate percentage changes
def calculate_percentage_change(df, comparison_type):
    if comparison_type == "MoM":
        df["change"] = df["value"].pct_change() * 100
        title = "Month Over Month % Change"
    elif comparison_type == "YoY":
        df["change"] = df["value"].pct_change(periods=12) * 100
        title = "Year Over Year % Change"
    return df, title

# Function to fetch and parse data from BLS
def fetch_data():
    url = "https://data.bls.gov/dataViewer/view/timeseries/LNS11000000"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table", {"id": "seriesDataTable1"})

    if table:
        rows = table.find_all("tr")
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 0:
                year = cols[0].text.strip()
                period = cols[1].text.strip()
                try:
                    value = float(cols[3].text.strip().replace(",", "").split("\r")[0])
                    month_code = period[1:]
                    concatenated_date = f"{month_code}-{year}"
                    data.append({
                        "date": concatenated_date,
                        "value": value
                    })
                except (ValueError, IndexError):
                    continue

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"], format="%m-%Y", errors="coerce")
        df = df.dropna(subset=["date"])  # Drop rows where date parsing failed
        return df
    else:
        return pd.DataFrame()

# Function to determine if today is the 15th day of the month
def is_15th_or_first_run():
    today = datetime.now().day
    return today == 15 or "df" not in st.session_state

# Streamlit app
st.title("BLS Employment Data Dashboard")

# Automatically fetch data on the 15th or during the first app run
if is_15th_or_first_run():
    with st.spinner("Fetching data..."):
        df = fetch_data()
        if not df.empty:
            st.session_state.df = df
            st.success("Data fetched successfully!")
        else:
            st.error("Failed to fetch data. Ensure the URL or table structure is correct.")

# Check if data exists in session state
if "df" in st.session_state and not st.session_state.df.empty:
    df = st.session_state.df

    # Display the dataframe
    st.subheader("BLS Employment Data")
    st.dataframe(df)

    # Select data type for visualization
    data_type = st.selectbox(
        "Select Data Type:",
        ["Actual Employment", "Percentage Change (Month over Month)", "Percentage Change (Year over Year)"]
    )

    if data_type == "Actual Employment":
        fig = px.line(
            df,
            x="date",
            y="value",
            title="Civilian Labor Force",
            labels={"date": "Date", "value": "Employment Level"},
            template="plotly_dark"
        )
    else:
        comparison_type = "MoM" if "Month" in data_type else "YoY"
        df, title = calculate_percentage_change(df, comparison_type)
        fig = px.line(
            df,
            x="date",
            y="change",
            title=title,
            labels={"date": "Date", "change": "% Change"},
            template="plotly_dark"
        )

    st.plotly_chart(fig)
else:
    st.info("Data will be fetched and displayed automatically.")