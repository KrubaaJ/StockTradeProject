import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Trade Gap Analysis", layout="wide")
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background: #dee2e6;
    }
    .stButton>button {
        background-color: #008CBA;
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stSlider>div[role='slider'] {
        background-color: #008CBA;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Stock Trade Gap Analysis")

# Sidebar for inputs
st.sidebar.header("Parameters")
stock_symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")

end_date = datetime.now()
start_date = end_date - timedelta(days=180)  # Default to 6 months of data

start_date_input = st.sidebar.date_input("Start Date", value=start_date)
end_date_input = st.sidebar.date_input("End Date", value=end_date)

gap_threshold = st.sidebar.slider("Gap Threshold (%)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
df['gap_percent'] = ((df['Open'] - df['prev_close']) / df['prev_close']) * 100
df['gap_percent'] = df['gap_percent'].astype(float)  # Ensure it's a single numeric column

# Function to analyze gaps
def analyze_gaps(df, threshold):
    df['prev_close'] = df['Close'].shift(1)
    df['gap_percent'] = ((df['Open'] - df['prev_close']) / df['prev_close'] * 100)
    df['has_gap'] = abs(df['gap_percent']) > threshold
    df['gap_type'] = 'none'
    df.loc[df['gap_percent'] > threshold, 'gap_type'] = 'up'
    df.loc[df['gap_percent'] < -threshold, 'gap_type'] = 'down'
    return df

# Analyze button
if st.sidebar.button("Analyze Stock"):
    try:
        with st.spinner(f"Loading data for {stock_symbol}..."):
            data = yf.download(stock_symbol, start=start_date_input, end=end_date_input)

            if data.empty:
                st.error(f"No data found for {stock_symbol}. Please check the symbol and try again.")
            else:
                data = data.reset_index()
                analyzed_data = analyze_gaps(data, gap_threshold)

                # Create visualization
                fig = go.Figure()

                # Candlestick chart
                fig.add_trace(go.Candlestick(
                    x=data['Date'], open=data['Open'], high=data['High'],
                    low=data['Low'], close=data['Close'], name='Price'
                ))

                # Highlight up gaps
                up_gaps = analyzed_data[analyzed_data['gap_type'] == 'up']
                if not up_gaps.empty:
                    fig.add_trace(go.Scatter(
                        x=up_gaps['Date'], y=up_gaps['High'], mode='markers',
                        marker=dict(symbol='triangle-up', size=15, color='green'), name='Up Gap'
                    ))

                # Highlight down gaps
                down_gaps = analyzed_data[analyzed_data['gap_type'] == 'down']
                if not down_gaps.empty:
                    fig.add_trace(go.Scatter(
                        x=down_gaps['Date'], y=down_gaps['Low'], mode='markers',
                        marker=dict(symbol='triangle-down', size=15, color='red'), name='Down Gap'
                    ))

                fig.update_layout(title=f'{stock_symbol} Price Gaps', yaxis_title='Price', xaxis_title='Date', height=600)
                st.plotly_chart(fig, use_container_width=True)

                # Display gap summary
                st.subheader("Gap Analysis Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Gaps", analyzed_data['has_gap'].sum())
                col2.metric("Up Gaps", len(up_gaps))
                col3.metric("Down Gaps", len(down_gaps))

                # Show data
                st.subheader("Data with Gap Analysis")
                display_df = analyzed_data[['Date', 'Open', 'High', 'Low', 'Close', 'gap_percent', 'gap_type', 'has_gap']]
                display_df['Date'] = display_df['Date'].dt.date
                display_df['gap_percent'] = display_df['gap_percent'].round(2).astype(str) + '%'
                st.dataframe(display_df)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
import streamlit as st

st.title("Stock Trade Gap Analysis")

st.write("Hello! Your Streamlit app is working.")

