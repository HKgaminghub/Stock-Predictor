import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Test BTC-USD Data")

start = st.date_input("Start", pd.to_datetime("2022-01-01"))
end = st.date_input("End", pd.to_datetime("2024-01-01"))

if st.button("Fetch"):
    df = yf.download("BTC-USD", start=start, end=end, interval="1d", progress=False)
    st.write("Rows fetched:", df.shape[0])
    st.dataframe(df.tail())
