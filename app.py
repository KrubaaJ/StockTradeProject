import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="📈 Stock Trade Gap Analysis", layout="wide")

# --- CUSTOM CSS FOR BETTER UI ---
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
        padding: 20px;
        border-right: 3px solid #dcdcdc;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
    }
    .stSlider>div[role='slider'] {
        background-color: #008CBA;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# --- TITLE ---
st.title("📊 Stock Trade Gap Analysis")

# --- SIDEBAR INPUTS ---
st.sidebar.header("🔹 Select Parameters")
stock_symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

start_date_input = st.sidebar.date_input("Start Date", value=start_date)
end_date_input = st.sidebar.date_input("End Date", value=end_date)
gap_threshold = st.sidebar.slider("Gap Threshold (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)

# --- FUNCTION TO ANALYZE GAPS ---
def analyze_gaps(data, threshold):
    """Identify trade gaps and categorize them as 'Up Gap' or 'Down Gap'."""
    if data is not None and not data.empty:
        df = data.copy()
        df['prev_close'] = df['Close'].shift(1)  # Shift to get previous close price
        df['prev_close'].fillna(df['Open'], inplace=True)  # Fill first row

        # Calculate gap percentage
        df['gap_percent'] = ((df['Open'] - df['prev_close']) / df['prev_close']) * 100

        # Identify gaps
        df['has_gap'] = abs(df['gap_percent']) > threshold
        df['gap_type'] = 'None'
        df.loc[df['gap_percent'] > threshold, 'gap_type'] = '⬆️ Up Gap'
        df.loc[df['gap_percent'] < -threshold, 'gap_type'] = '⬇️ Down Gap'

        return df
    return pd.DataFrame()  # Return empty DataFrame if no data available

# --- PROCESS USER REQUEST ---
if st.sidebar.button("🔍 Analyze Stock"):
    with st.spinner(f"Fetching data for {stock_symbol}..."):
        data = yf.download(stock_symbol, start=start_date_input, end=end_date_input)

        if data.empty:
            st.error(f"No data found for {stock_symbol}. Please check the symbol and try again.")
        else:
            data = data.reset_index()
            analyzed_data = analyze_gaps(data, gap_threshold)

            # --- CREATE PLOT ---
            fig = go.Figure()

            # Candlestick chart
            fig.add_trace(go.Candlestick(
                x=data['Date'], open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'], name='Stock Price'
            ))

            # Highlight gaps
            up_gaps = analyzed_data[analyzed_data['gap_type'] == '⬆️ Up Gap']
            down_gaps = analyzed_data[analyzed_data['gap_type'] == '⬇️ Down Gap']

            fig.add_trace(go.Scatter(
                x=up_gaps['Date'], y=up_gaps['High'], mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='green'), name='Up Gap'
            ))

            fig.add_trace(go.Scatter(
                x=down_gaps['Date'], y=down_gaps['Low'], mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='red'), name='Down Gap'
            ))

            fig.update_layout(title=f"{stock_symbol} Price Gaps", height=600)
            st.plotly_chart(fig, use_container_width=True)

            # --- DOWNLOAD ANALYSIS CSV ---
            csv = analyzed_data.to_csv(index=False)
            st.download_button("📥 Download Analysis CSV", csv, f"{stock_symbol}_gap_analysis.csv", "text/csv")

            # --- DISPLAY DATA ---
            st.subheader("📋 Gap Analysis Data")
            st.dataframe(analyzed_data)

