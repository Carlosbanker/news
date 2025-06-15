import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load keys
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Set Streamlit config
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️")
st.title("🗞️ News Lookup")
st.markdown("A free, multi-source AI-powered news summarizer. Get concise overviews from different reputable sources.")

# HuggingFace summarizer
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def summarize(text):
    payload = {"inputs": text}
    res = requests.post(HF_API_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()[0]['summary_text']
    return f"❌ Error: {res.status_code}"

# DuckDuckGo Search
def get_duckduckgo_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news article", max_results=5)
        return [
            {
                "source": "DuckDuckGo",
                "title": r["title"],
                "url": r["href"],
                "content": r["body"]
            } for r in results
        ] if results else []

# RSS Feeds
RSS_FEEDS = [
    ("BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "http://feeds.reuters.com/reuters/topNews"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
]

def get_rss_news():
    entries = []
    for name, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:
            entries.append({
                "source": name,
                "title": entry.title,
                "url": entry.link,
                "content": getattr(entry, "summary", "")
            })
    return entries

# NewsAPI (Featured section)
def get_newsapi_news(topic):
    if not NEWSAPI_KEY:
        return []

    url = "https://newsapi.org/v2/everything"
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    params = {
        "q": topic,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 5,
        "from": from_date,
        "apiKey": NEWSAPI_KEY
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [
            {
                "source": "NewsAPI",
                "title": a["title"],
                "url": a["url"],
                "content": a.get("description") or a.get("content", "No description available.")
            } for a in articles if a.get("description") or a.get("content")
        ]
    except Exception as e:
        st.warning(f"⚠️ NewsAPI failed: {e}")
        return []

# Input box
topic = st.text_input("Enter a news topic:", value="climate change")

# Session state
if "news_index" not in st.session_state:
    st.session_state.news_index = 0
if "general_news" not in st.session_state:
    st.session_state.general_news = []
if "newsapi_news" not in st.session_state:
    st.session_state.newsapi_news = []

# Button to search
if st.button("🔎 Look Up News"):
    if topic.strip():
        with st.status("Fetching news from all sources...", expanded=True):
            # Clear old state
            st.session_state.news_index = 0
            st.session_state.general_news = get_duckduckgo_news(topic) + get_rss_news()
            st.session_state.newsapi_news = get_newsapi_news(topic)
    else:
        st.warning("Please enter a topic to search.")

# Render Featured NewsAPI Section
if st.session_state.newsapi_news:
    st.subheader("🟨 Featured (NewsAPI)")
    for i, article in enumerate(st.session_state.newsapi_news):
        with st.expander(f"{i+1}. {article['title']} [{article['source']}]"):
            st.markdown(f"**URL:** [{article['url']}]({article['url']})")
            st.markdown(f"**Original:** {article['content'][:500]}...")
            st.markdown("**Summary:**")
            st.markdown(summarize(article['content']))

# Render General News Section with Pagination
if st.session_state.general_news:
    st.markdown("---")
    st.subheader("🌍 General News")
    total = len(st.session_state.general_news)
    idx = st.session_state.news_index
    end_idx = min(idx + 10, total)

    for i in range(idx, end_idx):
        article = st.session_state.general_news[i]
        with st.expander(f"{i+1}. {article['title']} [{article['source']}]"):
            st.markdown(f"**URL:** [{article['url']}]({article['url']})")
            st.markdown(f"**Original:** {article['content'][:500]}...")
            st.markdown("**Summary:**")
            st.markdown(summarize(article['content']))

    if end_idx < total:
        if st.button("🔽 Show 10 More"):
            st.session_state.news_index += 10
