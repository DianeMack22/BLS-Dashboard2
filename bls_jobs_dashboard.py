# -*- coding: utf-8 -*-
"""BLS_jobs_dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17pKc-AK8KgEya3TF7YRz64rKFCCtwrD4
"""

!pip install streamlit
!pip install plotly

import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler as bs # This line should now work
from datetime import datetime
import holidays

# Function to fetch and parse the data from BLS table and convert it to a dataframe.
def fetch_bls_table_data():
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
                value = float(cols[3].text.strip().replace(",", "").split("\r")[0])

                try:
                    month_code = period[1:]
                    concatenated_date = f"{month_code}-{year}"
                    data.append({
                        "date": concatenated_date,
                        "value": float(value)
                    })
                except ValueError:
                    print(f"Skipping row with invalid date format: {period} {year}")
                    continue

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"], format="%m-%Y")
        return df
    else:
        print("Table not found.")
        return pd.DataFrame()

# Calculate percentage change for MoM and YoY
def calculate_percentage_change(df, comparison_type):
    if comparison_type == "MoM":
        df["change"] = df["value"].pct_change() * 100
        title = "Month Over Month % Change"
    elif comparison_type == "YoY":
        df["change"] = df["value"].pct_change(periods=12) * 100
        title = "Year Over Year % Change"

    return df, title

# Function to check if today is the first business day of the month
def is_first_business_day():
    today = datetime.now().date()
    us_holidays = holidays.US()  # You can customize this for other countries
    first_day = today.replace(day=1)

    # If the first day is a weekend or holiday, find the next business day
    while first_day.weekday() > 4 or first_day in us_holidays:  # 0-4 are weekdays
        first_day += pd.Timedelta(days=1)

    return today == first_day

# Function to fetch and update data if it is the first business day
def fetch_and_update_data():
    if is_first_business_day():
        df = fetch_bls_table_data()
        if not df.empty:
            df["actual"] = df["value"]
        st.session_state.df = df  # Store in session state
        print("Data updated successfully.")
    else:
        print("Not the first business day. No update performed.")

# Main Streamlit app
#st.title("BLS Employment Data")

# Initialize session state if not already initialized
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Start APScheduler in the background to fetch data on the first business day of each month
if 'scheduler' not in st.session_state:
    scheduler = bs()
    scheduler.add_job(fetch_and_update_data, 'cron', day='1-7', hour=9, minute=0)  # Check daily at 9 AM
    scheduler.start()
    st.session_state.scheduler = scheduler  # Store the scheduler in session state

# Check if the data is loaded
if not st.session_state.df.empty:
    df = st.session_state.df

    data_type = st.selectbox(
        "Select Data Slice:",
        ["Actual Employment", "Percentage Change (Month over Month)", "Percentage Change (Year over Year)"]
    )

    if data_type == "Actual Employment":
        fig = px.line(df, x="date", y="actual", title="Civilian Labor Force",
                      labels={"date": "Date", "actual": "Actual Employment"},
                      template="plotly_dark")
    else:
        comparison_type = "MoM" if "Month" in data_type else "YoY"
        df, title = calculate_percentage_change(df, comparison_type)
        fig = px.line(df, x="date", y="change", title="BLS Employment Data",
                      labels={"date": "Date", "change": "% Change"},
                      template="plotly_dark")
    st.plotly_chart(fig)
    fig.show()
else:
    st.error("Data not found for graph. This is not your day. :'(")

#https://jobsdashboard-frwck3weu5t672hvqcemvc.streamlit.app/