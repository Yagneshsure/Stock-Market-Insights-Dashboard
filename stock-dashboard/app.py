# import streamlit as st
# import yfinance as yf
# import plotly.graph_objs as go
# import pandas as pd
# import requests
# import os
# import datetime
# from dotenv import load_dotenv
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# from newspaper import Article

# # Load environment variables
# load_dotenv()
# NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

# # --- Page Setup ---
# st.set_page_config(page_title="📈 Stock Insights", layout="wide")
# st.markdown(
#     """
#     <div style='background-color:#0E1117;padding:15px;border-radius:10px;margin-bottom:20px'>
#     <h1 style='color:white;text-align:center;'>📊 Stock Market Insights Dashboard</h1>
#     </div>
#     """, unsafe_allow_html=True
# )

# # --- Sidebar ---
# st.sidebar.title("🔎 Controls")
# market = st.sidebar.selectbox("Select Market Type", ("Stocks", "Cryptocurrency"))
# default_ticker = {"Stocks": "AAPL", "Cryptocurrency": "BTC-USD"}[market]
# ticker = st.sidebar.text_input(f"Enter {market} Ticker Symbol", default_ticker)
# start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
# end_date = st.sidebar.date_input("End Date", value=datetime.date.today())
# interval = st.sidebar.selectbox("Select Interval", options=["1h", "1d", "1wk", "1mo"], index=1)

# # --- Main Content ---
# if ticker:
#     stock = yf.Ticker(ticker)
#     try:
#         hist = stock.history(start=start_date, end=end_date, interval=interval)
#         info = stock.info
#     except Exception as e:
#         st.error(f"⚠️ Could not fetch data: {e}")
#         st.stop()

#     if hist.empty:
#         st.warning("⚠️ No historical data available for selected range/interval.")
#         st.stop()

#     # Tabs
#     if market == "Stocks":
#         tab1, tab2, tab3 = st.tabs(["📈 Overview", "📉 Financials", "📰 News & Sentiment"])
#     else:
#         tab1, tab3 = st.tabs(["📈 Overview", "📰 News & Sentiment"])

#     # --- Tab 1: Overview ---
#     with tab1:
#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader("🏢 Company Info")
#             st.write({
#                 "Name": info.get("longName", "N/A"),
#                 "Sector": info.get("sector", "N/A"),
#                 "Industry": info.get("industry", "N/A"),
#                 "Website": info.get("website", "N/A"),
#             })
#         with col2:
#             st.subheader("💲 Current Price")
#             current_price = info.get("currentPrice", "N/A")
#             st.metric(label=f"{ticker}", value=f"${current_price}")

#         with st.expander("📊 Historical Price Chart"):
#             st.markdown(f"**Interval:** {interval.upper()} | **Range:** {start_date} to {end_date}")
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close Price"))
#             fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_dark")
#             st.plotly_chart(fig, use_container_width=True)

#         with st.expander("🔢 Moving Averages"):
#             hist['MA20'] = hist['Close'].rolling(window=20).mean()
#             hist['MA50'] = hist['Close'].rolling(window=50).mean()
#             ma_fig = go.Figure()
#             ma_fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Close'))
#             ma_fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], name='20-Day MA'))
#             ma_fig.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], name='50-Day MA'))
#             ma_fig.update_layout(title="Moving Averages", template="plotly_dark")
#             st.plotly_chart(ma_fig, use_container_width=True)

#     # --- Tab 2: Financials ---
#     if market == "Stocks":
#         with tab2:
#             earnings = stock.earnings
#             quarterly_earnings = stock.quarterly_earnings
#             financials = stock.financials

#             if earnings is not None and not earnings.empty:
#                 with st.expander("📈 Annual Net Income"):
#                     st.line_chart(earnings['Net Income'])

#             if quarterly_earnings is not None and not quarterly_earnings.empty:
#                 with st.expander("📊 Quarterly Revenue vs Earnings"):
#                     st.bar_chart(quarterly_earnings[['Revenue', 'Earnings']])

#             if financials is not None and not financials.empty:
#                 with st.expander("📜 Income Statement Table"):
#                     st.dataframe(financials)
#                     st.download_button("Download as CSV", financials.to_csv().encode('utf-8'), file_name=f"{ticker}_financials.csv")

#                 with st.expander("🔢 Financial Metrics Visualized"):
#                     metrics = ['EBITDA', 'EBIT', 'Reconciled Cost Of Revenue']
#                     display_df = financials.loc[metrics].transpose()
#                     st.line_chart(display_df)

#             if (earnings is None or earnings.empty) and (financials is None or financials.empty) and (quarterly_earnings is None or quarterly_earnings.empty):
#                 st.warning("⚠️ Financial data not available. Try another ticker like AAPL or MSFT.")

#     # --- Tab 3: News ---
#     with tab3:
#         st.subheader("📰 Latest News with Sentiment")
#         if NEWS_API_KEY:
#             news_url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
#             response = requests.get(news_url)
#             if response.status_code == 200:
#                 articles = response.json().get("articles", [])
#                 analyzer = SentimentIntensityAnalyzer()
#                 for article in articles:
#                     url = article["url"]
#                     try:
#                         a = Article(url)
#                         a.download()
#                         a.parse()
#                         full_text = a.text
#                     except:
#                         full_text = article.get("description") or "No summary available."
#                     sentiment = analyzer.polarity_scores(full_text)
#                     score = sentiment['compound']
#                     if score >= 0.05:
#                         sentiment_label = "😊 Positive"
#                         color = "green"
#                     elif score <= -0.05:
#                         sentiment_label = "😠 Negative"
#                         color = "red"
#                     else:
#                         sentiment_label = "😐 Neutral"
#                         color = "gray"
#                     st.markdown(f"### {article['title']}")
#                     st.write(full_text[:400] + "...")
#                     st.markdown(f"<span style='color:{color};font-weight:bold'>Sentiment: {sentiment_label} (Score: {score:.2f})</span>", unsafe_allow_html=True)
#                     st.markdown(f"[Read more →]({url})")
#                     st.markdown("---")
#             else:
#                 st.error("❌ Failed to fetch news. Check your API key or quota.")
#         else:
#             st.warning("⚠️ NEWSAPI_KEY not found in your .env file.")




#######################################################################################


import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import requests
import os
import datetime
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newspaper import Article

# Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

# --- Page Setup ---
st.set_page_config(page_title=" Stock Insights", layout="wide")

# --- Styling ---
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00FFAA;
    }
    .stMetric {background-color: #1E1E1E; padding: 10px; border-radius: 10px;}
    .css-1v0mbdj p {font-size: 1rem; color: #FAFAFA;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown(
    """
    <div style='background: linear-gradient(to right, #00c6ff, #0072ff); padding: 2rem; border-radius: 12px;'>
    <h1 style='color:white;text-align:center;'> Stock Market Insights Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
st.sidebar.title("🔎 Controls")

market = st.sidebar.selectbox("Select Market Type", ("Stocks", "Cryptocurrency"))

default_ticker = {
    "Stocks": "AAPL",
    "Cryptocurrency": "BTC-USD"
}[market]

ticker = st.sidebar.text_input(f"Enter {market} Ticker Symbol", default_ticker)
start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.date.today())

interval = st.sidebar.selectbox(
    "Select Interval",
    options=["1h", "1d", "1wk", "1mo"],
    index=1,
    help="1h for hourly, 1d for daily, etc."
)

# --- Main Content ---
if ticker:
    stock = yf.Ticker(ticker)

    try:
        hist = stock.history(start=start_date, end=end_date, interval=interval)
        info = stock.info
    except Exception as e:
        st.error(f"⚠️ Could not fetch data: {e}")
        st.stop()

    if hist.empty:
        st.warning("⚠️ No historical data available for selected range/interval. Try another one.")
        st.stop()

    if market == "Stocks":
        tab1, tab2, tab3 = st.tabs(["📈 Overview", "📉 Financials", "📰 News & Sentiment"])
    else:
        tab1, tab3 = st.tabs(["📈 Overview", "📰 News & Sentiment"])

    # --- Tab 1: Overview ---
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏢 Company Info")
            st.markdown(f"""
            <div style='background-color:#1E1E1E; padding:10px; border-radius:10px;'>
                <p><strong>Name:</strong> {info.get("longName", "N/A")}</p>
                <p><strong>Sector:</strong> {info.get("sector", "N/A")}</p>
                <p><strong>Industry:</strong> {info.get("industry", "N/A")}</p>
                <p><strong>Website:</strong> <a href='{info.get("website", "")}' target='_blank'>{info.get("website", "N/A")}</a></p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.subheader("Current Price")
            current_price = info.get("currentPrice", "N/A")
            st.metric(label=f"{ticker}", value=f"{current_price}")

        with st.expander("📊 Historical Price Chart"):
            st.markdown(f"**Interval:** {interval.upper()} | **Range:** {start_date} to {end_date}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close Price", line=dict(color='#00FFAA')))
            fig.update_layout(
                title=f"{ticker} Price Chart",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                template="plotly_dark",
                plot_bgcolor='#1E1E1E',
                paper_bgcolor='#0E1117'
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔢 Moving Averages"):
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            ma_fig = go.Figure()
            ma_fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Close'))
            ma_fig.add_trace(go.Scatter(x=hist.index, y=hist['MA20'], name='20-Day MA'))
            ma_fig.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], name='50-Day MA'))
            ma_fig.update_layout(title="Moving Averages", template="plotly_dark")
            st.plotly_chart(ma_fig, use_container_width=True)

    # --- Tab 2: Financials ---
    if market == "Stocks":
        with tab2:
            earnings = stock.earnings
            quarterly_earnings = stock.quarterly_earnings
            financials = stock.financials

            if earnings is not None and not earnings.empty:
                with st.expander("📈 Annual Net Income"):
                    st.line_chart(earnings['Net Income'])

            if quarterly_earnings is not None and not quarterly_earnings.empty:
                with st.expander("📊 Quarterly Revenue vs Earnings"):
                    st.bar_chart(quarterly_earnings[['Revenue', 'Earnings']])

            if financials is not None and not financials.empty:
                with st.expander("🧾 Income Statement"):
                    st.dataframe(financials.style.highlight_max(axis=0))

                with st.expander("📉 Key Financial Metrics"):
                    metrics = ['EBITDA', 'EBIT', 'Reconciled Cost Of Revenue']
                    display_df = financials.loc[metrics].transpose()
                    st.line_chart(display_df)

            if (
                (earnings is None or earnings.empty) and
                (financials is None or financials.empty) and
                (quarterly_earnings is None or quarterly_earnings.empty)
            ):
                st.warning("⚠️ Financial data not available. Try another ticker like AAPL or MSFT.")

    # --- Tab 3: News ---
    with tab3:
        st.subheader("📰 Latest News with Sentiment")

        if NEWS_API_KEY:
            news_url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
            response = requests.get(news_url)

            if response.status_code == 200:
                articles = response.json().get("articles", [])
                analyzer = SentimentIntensityAnalyzer()

                for article in articles:
                    url = article["url"]
                    try:
                        a = Article(url)
                        a.download()
                        a.parse()
                        full_text = a.text
                    except:
                        full_text = article.get("description") or "No summary available."

                    sentiment = analyzer.polarity_scores(full_text)
                    score = sentiment['compound']
                    if score >= 0.05:
                        sentiment_label = "😊 Positive"
                        color = "green"
                    elif score <= -0.05:
                        sentiment_label = "😠 Negative"
                        color = "red"
                    else:
                        sentiment_label = "😐 Neutral"
                        color = "gray"

                    st.markdown(f"### {article['title']}")
                    st.write(full_text[:400] + "...")
                    st.markdown(
                        f"<span style='color:{color};font-weight:bold'>Sentiment: {sentiment_label} (Score: {score:.2f})</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(f"[Read more →]({url})")
                    st.markdown("---")
            else:
                st.error("❌ Failed to fetch news. Check your API key or quota.")
        else:
            st.warning("⚠️ NEWSAPI_KEY not found in your .env file.")


##################################################################################################################
