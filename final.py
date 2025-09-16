import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import streamlit as st

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="💹 Advanced Crypto Dashboard", layout="wide")

st.title("💹 Advanced Crypto Dashboard")
st.write("Analyze cryptocurrencies with EMA, Volume, Volatility, and Price Comparison.")

# Sidebar: Crypto selection
crypto_options = {
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD",
    "Binance Coin (BNB)": "BNB-USD",
    "Solana (SOL)": "SOL-USD",
    "Dogecoin (DOGE)": "DOGE-USD"
}

crypto_name = st.sidebar.selectbox("Select Main Cryptocurrency", list(crypto_options.keys()))
crypto_symbol = crypto_options[crypto_name]

interval = st.sidebar.selectbox("Select Interval", ["5m", "15m", "30m", "1h", "1d"], index=2)
period = st.sidebar.selectbox("Select Period", ["1d", "5d", "1mo", "3mo", "6mo"], index=1)

# Comparison selection (exclude main crypto)
compare_options = {k: v for k, v in crypto_options.items() if k != crypto_name}
compare_cryptos = st.sidebar.multiselect("Compare with Other Cryptos", list(compare_options.keys()))

normalize = st.sidebar.checkbox("Normalize Comparison (Start = 100)", value=True)

# ---------------- Fetch Data ----------------
@st.cache_data(ttl=60)
def load_data(symbol, period, interval):
    return yf.download(symbol, period=period, interval=interval)

df = load_data(crypto_symbol, period, interval)

# ---------------- Tabs ----------------
tab1, tab2 = st.tabs(["📊 Main Analysis", "📈 Comparison"])

with tab1:
    if df.empty:
        st.error("❌ No data found. Try another crypto or interval.")
    else:
        # EMA + Volatility
        df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
        df["Returns"] = df["Close"].pct_change()
        df["Volatility"] = df["Returns"].rolling(window=20).std() * (len(df) ** 0.5)

        # Chart with EMA + Volume
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Candlestick"))
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA12"], line=dict(color="orange", width=1.5), name="EMA 12"))
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA26"], line=dict(color="blue", width=1.5), name="EMA 26"))
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                             marker=dict(color="purple"), opacity=0.3, yaxis="y2"))

        fig.update_layout(
            title=f"{crypto_name} ({crypto_symbol}) Chart with EMA & Volume",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=600,
            yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Prediction
        if df["EMA12"].iloc[-1] > df["EMA26"].iloc[-1]:
            st.success(f"📈 BUY Signal for {crypto_name}: Uptrend expected (EMA12 > EMA26)")
        else:
            st.error(f"📉 SELL Signal for {crypto_name}: Downtrend expected (EMA12 < EMA26)")

        # Volatility
        st.subheader("📊 Volatility")
        vol_fig = go.Figure()
        vol_fig.add_trace(go.Scatter(x=df.index, y=df["Volatility"], line=dict(color="red"), name="Volatility"))
        vol_fig.update_layout(template="plotly_dark", height=300, title="Volatility (20-period Rolling StdDev)")
        st.plotly_chart(vol_fig, use_container_width=True)

        with st.expander("🔍 Show Data Table"):
            st.dataframe(df.tail(50))

with tab2:
    if compare_cryptos:
        st.subheader("📈 Crypto Price & Volume Comparison")

        # Dictionary to hold aligned data
        compare_data = pd.DataFrame(index=df.index)
        compare_data[crypto_name] = df["Close"]
        volume_data = pd.DataFrame(index=df.index)
        volume_data[crypto_name] = df["Volume"]

        # Add other cryptos
        for c in compare_cryptos:
            comp_df = load_data(compare_options[c], period, interval)
            if not comp_df.empty:
                comp_df = comp_df.reindex(df.index, method="ffill")  # align timestamps
                compare_data[c] = comp_df["Close"]
                volume_data[c] = comp_df["Volume"]

        # Normalize if needed
        if normalize:
            compare_data = compare_data / compare_data.iloc[0] * 100

        # Subplots: Prices + Volume
        comp_fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 row_heights=[0.7, 0.3],
                                 vertical_spacing=0.1,
                                 subplot_titles=("Price Comparison", "Volume Comparison"))

        # Price Lines
        for col in compare_data.columns:
            comp_fig.add_trace(go.Scatter(x=compare_data.index, y=compare_data[col],
                                          mode="lines", name=col), row=1, col=1)

        # Volume Bars (stacked per crypto)
        for col in volume_data.columns:
            comp_fig.add_trace(go.Bar(x=volume_data.index, y=volume_data[col],
                                      name=f"{col} Volume", opacity=0.5), row=2, col=1)

        comp_fig.update_layout(template="plotly_dark", height=700, title="Crypto Price & Volume Comparison")
        st.plotly_chart(comp_fig, use_container_width=True)
    else:
        st.info("ℹ️ Select other cryptos from the sidebar for comparison.")
