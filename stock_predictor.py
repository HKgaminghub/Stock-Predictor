import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime
import requests
import time

# Map Yahoo tickers to CoinGecko IDs
COIN_GECKO_MAP = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "BNB-USD": "binancecoin",
    "SOL-USD": "solana",
    "ADA-USD": "cardano",
}

@st.cache_data
def fetch_logo(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["image"]["large"]
    return None

@st.cache_data
def fetch_data(ticker, start, end):
    df = yf.Ticker(ticker).history(start=start, end=end, interval="1d")
    df["STD"] = df["Close"].rolling(window=5).std()
    df.to_csv(f"{ticker}.csv")
    return df

# Load tickers
tickers_df = pd.read_csv("ticker.csv")
tickers = tickers_df["Ticker"].tolist()

# App layout
st.set_page_config(layout="wide")
tabs = st.tabs(["📈 Single Crypto Analysis", "📊 Compare Cryptos", "📉 EMA Strategy", "💹 Live Prices"])

# ---------------------------- Window 1 ----------------------------
with tabs[0]:
    st.header("📈 Single Crypto Analysis")
    col1, col2 = st.columns(2)
    with col1:
        selected = st.selectbox("Choose Crypto", tickers)
    with col2:
        metric = st.selectbox("Metric", ["Open", "Close", "Volume", "STD"])

    start = st.date_input("Start Date", datetime.date(2022, 1, 1))
    end = st.date_input("End Date", datetime.date.today())

    if st.button("Fetch Data"):
        df = fetch_data(selected, start, end)
        if df.empty or len(df) < 5:
            st.warning("Not enough data to plot. Please choose a wider or more recent range.")
        else:
            logo_url = fetch_logo(COIN_GECKO_MAP.get(selected))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[metric], mode="lines", name=metric))
            if logo_url:
                fig.add_layout_image(
                    dict(
                        source=logo_url,
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        sizex=0.6, sizey=0.6,
                        xanchor="center", yanchor="middle",
                        opacity=0.15,
                        layer="below"
                    )
                )
            fig.update_layout(title=f"{selected} - {metric}", xaxis_title="Date", yaxis_title=metric)
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------- Window 2 ----------------------------
with tabs[1]:
    st.header("📊 Compare Two Cryptos")
    c1, c2, c3 = st.columns(3)
    with c1:
        s1 = st.selectbox("Crypto 1", tickers, key="comp1")
    with c2:
        s2 = st.selectbox("Crypto 2", tickers, key="comp2")
    with c3:
        metric2 = st.selectbox("Metric", ["Open", "Close", "Volume", "STD"], key="metric2")

    if st.button("Compare"):
        df1 = fetch_data(s1, start, end)
        df2 = fetch_data(s2, start, end)
        if df1.empty or df2.empty:
            st.warning("No data for one or both selected cryptos.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df1.index, y=df1[metric2], name=s1))
            fig.add_trace(go.Scatter(x=df2.index, y=df2[metric2], name=s2))
            fig.update_layout(title=f"Comparison: {s1} vs {s2} ({metric2})", xaxis_title="Date", yaxis_title=metric2)
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------- Window 3 ----------------------------
with tabs[2]:
    st.header("📉 Buy/Sell Signal using EMA Strategy")
    stock = st.selectbox("Choose Crypto", tickers, key="ema_stock")
    start2 = st.date_input("Start Date for EMA", datetime.date(2022, 1, 1), key="start_ema")
    end2 = st.date_input("End Date for EMA", datetime.date.today(), key="end_ema")

    if st.button("Analyze"):
        df = fetch_data(stock, start2, end2)
        if df.empty or len(df) < 30:
            st.warning("Not enough data for EMA analysis.")
        else:
            df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
            df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()

            signal = "BUY" if df["EMA12"].iloc[-1] > df["EMA26"].iloc[-1] else "SELL"
            st.subheader(f"Recommendation: **{signal}**")

            logo_url = fetch_logo(COIN_GECKO_MAP.get(stock))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA12"], name="EMA12"))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA26"], name="EMA26"))
            if logo_url:
                fig.add_layout_image(
                    dict(
                        source=logo_url,
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        sizex=0.6, sizey=0.6,
                        xanchor="center", yanchor="middle",
                        opacity=0.15,
                        layer="below"
                    )
                )
            fig.update_layout(title=f"{stock} - EMA Strategy", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------- Window 4 ----------------------------
with tabs[3]:
    st.header("💹 Live Crypto Price Streaming (Full Day)")
    live_coin = st.selectbox("Choose Crypto to Stream", tickers, key="live_coin")
    placeholder = st.empty()

    if st.button("Start Live Stream"):
        today = datetime.datetime.now().date()
        start_time = datetime.datetime.combine(today, datetime.time(0, 0))

        for _ in range(300):  # stream for 300 seconds
            try:
                now = datetime.datetime.now()

                df = yf.download(
                    tickers=live_coin,
                    start=start_time,
                    end=now,
                    interval="1m",
                    progress=False
                )

                if df.empty:
                    st.warning("No live data yet. Please try again later.")
                    break

                # Fix the DataFrame
                df = df.reset_index()
                times = df["Datetime"].tolist()
                prices = df["Close"].astype(float).tolist()

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=times, y=prices, mode="lines", name="Price"))
                fig.update_layout(
                    title=f"{live_coin} Full-Day Live Chart",
                    xaxis_title="Time",
                    yaxis_title="Price",
                    xaxis=dict(showspikes=True),
                )
                placeholder.plotly_chart(fig, use_container_width=True)
                time.sleep(1)

            except Exception as e:
                st.error(f"Error: {e}")
                break
