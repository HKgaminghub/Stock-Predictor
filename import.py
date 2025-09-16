import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Load ticker data from CSV
tickers_df = pd.read_csv("C:/Users/hardb/AppData/Local/Microsoft/Windows/INetCache/IE/FHMFEBM2/Tickers[1].csv")
tickers = tickers_df.iloc[:, 0].dropna().unique().tolist()

# Streamlit setup
st.set_page_config(page_title="Stock Analyzer", layout="wide")

# Fetch stock data
def fetch_stock_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    if not data.empty:
        data['Standard Deviation'] = data['Close'].rolling(window=20).std()
        data.to_csv(f"data_{ticker}.csv")
    return data

# Plot graph
def plot_graph(data, metric, title, background_image=None):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x=data.index, y=data[metric].values.flatten(), ax=ax)
    ax.set_title(title)
    st.pyplot(fig)

# EMA strategy
def ema_strategy(data):
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['Signal'] = data['Close'].values > data['EMA20'].values  # avoid misalignment
    return data

# Currency logo
def load_logo(currency):
    logos = {
        'USD': 'https://upload.wikimedia.org/wikipedia/commons/a/a4/USD_symbol.svg',
        'INR': 'https://upload.wikimedia.org/wikipedia/commons/4/4e/Indian_Rupee_symbol.svg',
        'EUR': 'https://upload.wikimedia.org/wikipedia/commons/b/b7/Euro_symbol_black.svg',
    }
    return logos.get(currency, None)

# Get currency
def get_currency(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('currency', 'USD')
    except:
        return 'USD'

# Sidebar
window = st.sidebar.radio("Select Window", [
    "1. Single Stock Chart",
    "2. Compare Two Stocks",
    "3. EMA Buy Signal",
    "4. Live Data"
])

start_date = st.sidebar.date_input("Start Date", datetime(2022, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.today())

# Window 1: Single Stock Chart
if window.startswith("1"):
    st.header("📈 Single Stock Analysis")
    col1, col2 = st.columns(2)
    with col1:
        stock = st.selectbox("Choose a Stock", tickers)
    with col2:
        metric = st.selectbox("Metric", ["Close", "Open", "Volume", "Standard Deviation"])

    if stock:
        df = fetch_stock_data(stock, start_date, end_date)
        if not df.empty:
            currency = get_currency(stock)
            logo_url = load_logo(currency)
            if logo_url:
                st.markdown(f"<img src='{logo_url}' width='80' style='position:absolute;top:10px;right:10px;opacity:0.1;'>", unsafe_allow_html=True)
            st.subheader(f"{stock} - {metric}")
            plot_graph(df, metric, f"{stock} - {metric}")
        else:
            st.error("No data found for selected stock.")

# Window 2: Compare Two Stocks
elif window.startswith("2"):
    st.header("📊 Compare Two Stocks")
    col1, col2, col3 = st.columns(3)
    with col1:
        stock1 = st.selectbox("Stock 1", tickers, key="cmp1")
    with col2:
        stock2 = st.selectbox("Stock 2", tickers, key="cmp2")
    with col3:
        metric = st.selectbox("Metric", ["Close", "Open", "Volume", "Standard Deviation"], key="cmpmetric")

    if stock1 != stock2:
        df1 = fetch_stock_data(stock1, start_date, end_date)[[metric]].rename(columns={metric: stock1})
        df2 = fetch_stock_data(stock2, start_date, end_date)[[metric]].rename(columns={metric: stock2})

        combined_df = pd.concat([df1, df2], axis=1).dropna().copy()
        combined_df.reset_index(inplace=True)
        melted = combined_df.melt(id_vars='Date', var_name='Stock', value_name='Value')

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=melted, x='Date', y='Value', hue='Stock', ax=ax)
        ax.set_title(f"{metric} Comparison")
        st.pyplot(fig)
    else:
        st.warning("Choose different stocks to compare.")

# Window 3: EMA Buy Signal
elif window.startswith("3"):
    st.header("📉 EMA Buy Signal Recommendation")
    stock = st.selectbox("Choose a Stock", tickers, key="ema_stock")
    if stock:
        df = fetch_stock_data(stock, start_date, end_date)
        if not df.empty:
            df = ema_strategy(df)
            currency = get_currency(stock)
            logo_url = load_logo(currency)
            if logo_url:
                st.markdown(f"<img src='{logo_url}' width='80' style='position:absolute;top:10px;right:10px;opacity:0.1;'>", unsafe_allow_html=True)
            st.subheader(f"{stock} - Close Price and EMA")
            plot_graph(df, "Close", f"{stock} - EMA Buy Signal")
            st.line_chart(df[['Close', 'EMA20']])
            if df['Signal'].iloc[-1]:
                st.success("✅ BUY Signal: Price is above EMA.")
            else:
                st.error("❌ DO NOT BUY: Price is below EMA.")
        else:
            st.error("No data found.")

# Window 4: Live Data
elif window.startswith("4"):
    st.header("🟢 Live Stock Data")
    stock = st.selectbox("Choose a Stock", tickers, key="live")
    if stock:
        try:
            live_data = yf.Ticker(stock).history(period="1d", interval="1m")
            if live_data.empty:
                live_data = yf.Ticker(stock).history(period="5d", interval="1h")
                st.warning("⚠️ Showing fallback data (1h interval, 5 days). Market might be closed or 1m data unavailable.")
            st.subheader(f"Live Data for {stock}")
            st.line_chart(live_data['Close'])
        except Exception as e:
            st.error(f"❌ Could not fetch live data. Reason: {e}")
