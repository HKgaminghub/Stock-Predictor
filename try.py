import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import datetime

# Load ticker list from CSV
ticker_df = pd.read_csv("crypto_tickers_inr.csv")
tickers = ticker_df.iloc[:, 0].dropna().unique().tolist()

# Function to fetch data
def fetch_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    if not df.empty:
        df['Std Dev'] = df['Close'].rolling(window=10).std()
    return df

# Function to apply logo background
def apply_logo_background(ticker):
    symbol = ticker.split("-")[0].lower()
    logo_url = f"https://cryptoicons.org/api/icon/{symbol}/500"
    css = f"""
    <style>
    .stApp {{
        background-image: url('{logo_url}');
        background-repeat: no-repeat;
        background-position: center;
        background-size: 35%;
        opacity: 1.0;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📊 Crypto Visualizer with Logo Watermark")

ticker = st.selectbox("Select Crypto Ticker", tickers)
metric = st.selectbox("Select Metric", ["Close", "Open", "Volume", "Std Dev"])
start_date = st.date_input("Start Date", datetime.date(2022, 1, 1))
end_date = st.date_input("End Date", datetime.date.today())

if ticker:
    apply_logo_background(ticker)
    df = fetch_data(ticker, start_date, end_date)

    if not df.empty and metric in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[metric], mode='lines', name=metric))
        fig.update_layout(title=f"{ticker} - {metric}", xaxis_title="Date", yaxis_title=metric)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Data not available or metric not found.")
