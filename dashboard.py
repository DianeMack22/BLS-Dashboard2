# -*- coding: utf-8 -*-
"""dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dc3OFUKJxSS2PH5XpiNxgE5XVTRIJydH
"""

# dashboard.py
import streamlit as st
import pandas as pd


# Load the prepared data
DATA_FILE = "prepared_data.csv"

def load_data():
    return pd.read_csv(DATA_FILE, parse_dates=["date"])

# Create the dashboard
def main():
    st.title("US Labor Statistics Dashboard")
    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filter Options")
    selected_series = st.sidebar.multiselect(
        "Select Metrics", df.columns[1:], default=df.columns[1:]
    )

    # Filter data
    filtered_df = df[["date"] + selected_series]

    # Plot the data
    st.line_chart(filtered_df.set_index("date"))

    # Display raw data option
    if st.checkbox("Show raw data"):
        st.write(filtered_df)

if __name__ == "__main__":
    main()