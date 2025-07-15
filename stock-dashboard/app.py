# import streamlit as st
# import yfinance as yf
# import plotly.graph_objs as go
# import requests
# import os
# from dotenv import load_dotenv
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# # Load environment variables
# load_dotenv()
# NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

# # Streamlit page configuration
# st.set_page_config(page_title="📈 Stock Market Insights", layout="wide")
# st.title("📈 Stock Market Insights Dashboard")

# # User input
# ticker = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, TSLA, MSFT)", "AAPL").upper()

# if ticker:
#     try:
#         stock = yf.Ticker(ticker)
#         info = stock.info

#         # Company Info
#         st.subheader(f"🏢 Company Info: {ticker}")
#         st.write({
#             "Name": info.get("longName", "N/A"),
#             "Sector": info.get("sector", "N/A"),
#             "Industry": info.get("industry", "N/A"),
#             "Website": info.get("website", "N/A")
#         })

#         # Current Price
#         st.subheader("📊 Current Price")
#         current_price = info.get("currentPrice", "N/A")
#         st.write(f"**{ticker}**: ${current_price}")

#         # Historical Chart
#         st.subheader("📉 Historical Price Chart (Past 6 Months)")
#         hist = stock.history(period="6mo")
#         if not hist.empty:
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close Price"))
#             fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price (USD)")
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.warning("⚠️ No historical data available.")

#         # Latest News
#         st.subheader("📰 Latest News")

#         if NEWS_API_KEY:
#             url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
#             response = requests.get(url)

#             if response.status_code == 200:
#                 articles = response.json().get("articles", [])
#                 if articles:
#                     analyzer = SentimentIntensityAnalyzer()
#                     for article in articles:
#                         title = article.get("title", "No title")
#                         description = article.get("description", "")
#                         url = article.get("url", "#")

#                         content = f"{title}. {description}"
#                         sentiment_score = analyzer.polarity_scores(content)['compound']
#                         if sentiment_score >= 0.05:
#                             sentiment = "😊 Positive"
#                         elif sentiment_score <= -0.05:
#                             sentiment = "😟 Negative"
#                         else:
#                             sentiment = "😐 Neutral"

#                         st.markdown(f"**{title}**")
#                         st.write(description)
#                         st.write(f"🧠 Sentiment: `{sentiment}` (Score: {sentiment_score:.2f})")
#                         st.markdown(f"[Read more]({url})")
#                         st.markdown("---")
#                 else:
#                     st.write("No news articles found.")
#             else:
#                 st.error("❌ Failed to fetch news. Check your API key or NewsAPI usage limits.")
#         else:
#             st.warning("⚠️ NEWSAPI_KEY not found in `.env`. Please set it before running.")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")


# app.py




import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser
import urllib.parse

st.set_page_config(page_title="📈 Stock Market Insights Dashboard", layout="wide")

# Helper: Sentiment analysis
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)["compound"]
    if score > 0.05:
        return "😊 Positive", score
    elif score < -0.05:
        return "😟 Negative", score
    else:
        return "😐 Neutral", score

# Helper: Get company info
def get_company_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "Name": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Website": info.get("website", "N/A"),
    }

# Helper: Historical chart
def plot_historical_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name=ticker))
    fig.update_layout(title=f"{ticker} - Past 6 Months", xaxis_title="Date", yaxis_title="Price (₹)")
    return fig

# Helper: Fetch news using Google RSS
def fetch_google_news(ticker):
    query = urllib.parse.quote(f"{ticker} stock India")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        source = entry.source.title if 'source' in entry else "Google News"
        sentiment, score = analyze_sentiment(title)
        articles.append({"title": title, "link": link, "source": source, "sentiment": sentiment, "score": score})
    return articles

# App UI
st.title("📈 Stock Market Insights Dashboard")
ticker = st.text_input("Enter Stock Ticker Symbol (e.g., RELIANCE.NS, INFY.NS, TCS.NS)", "INFY.NS").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)

        # Company Info
        info = get_company_info(ticker)
        st.subheader(f"🏢 Company Info: {ticker}")
        st.json(info)

        # Current Price
        current_price = stock.history(period="1d")["Close"].iloc[-1]
        st.subheader("📊 Current Price")
        st.write(f"{ticker}: ₹{round(current_price, 2)}")

        # Historical Chart
        st.subheader("📉 Historical Price Chart (Past 6 Months)")
        chart = plot_historical_chart(ticker)
        st.plotly_chart(chart, use_container_width=True)

        # News + Sentiment
        st.subheader("📰 Latest News")
        articles = fetch_google_news(ticker)
        for article in articles:
            st.markdown(f"**{article['title']}**  \n"
                        f"🧠 Sentiment: {article['sentiment']} (Score: {article['score']:.2f})  \n"
                        f"[Read more]({article['link']})  \n"
                        f"<font color='#6f6f6f'>{article['source']}</font>",
                        unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

