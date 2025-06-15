import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Setup Streamlit UI
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️")
st.title("🗞️ News Lookup")
st.markdown("A free, multi-source AI-powered news summarizer. Get concise overviews from different reputable sources.")

# HuggingFace Summarizer
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def summarize(text):
    payload = {"inputs": text}
    res = requests.post(HF_API_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()[0]['summary_text']
    return f"❌ Error: {res.status_code}"

# DuckDuckGo News
def get_duckduckgo_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news", max_results=5)
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
        for entry in feed.entries[:2]:  # limit per feed
            entries.append({
                "source": name,
                "title": entry.title,
                "url": entry.link,
                "content": getattr(entry, "summary", "")
            })
    return entries

# GNews (Featured Section)
def get_gnews_news(topic):
    if not GNEWS_KEY:
        return []

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": topic,
        "lang": "en",
        "max": 5,
        "token": GNEWS_KEY
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        articles = res.json().get("articles", [])
        return [
            {
                "source": a["source"]["name"],
                "title": a["title"],
                "url": a["url"],
                "content": a.get("description") or a.get("content", "No description available.")
            } for a in articles if a.get("title") and a.get("url")
        ]
    except Exception as e:
        st.warning(f"⚠️ GNews failed: {e}")
        return []

# Topic Input
topic = st.text_input("Enter a news topic:", value="climate change")

# Session states
if "news_index" not in st.session_state:
    st.session_state.news_index = 0
if "general_news" not in st.session_state:
    st.session_state.general_news = []
if "featured_news" not in st.session_state:
    st.session_state.featured_news = []

# Search Button
if st.button("🔎 Look Up News"):
    if topic.strip():
        with st.status("Gathering and summarizing news...", expanded=True):
            st.session_state.news_index = 0
            st.session_state.general_news = get_duckduckgo_news(topic) + get_rss_news()
            st.session_state.featured_news = get_gnews_news(topic)
    else:
        st.warning("Please enter a topic to search.")

# Display Featured Section (GNews)
if st.session_state.featured_news:
    st.subheader("🟨 Featured (GNews)")
    for i, article in enumerate(st.session_state.featured_news):
        with st.expander(f"{i+1}. {article['title']} [{article['source']}]"):
            st.markdown(f"**URL:** [{article['url']}]({article['url']})")
            st.markdown(f"**Original:** {article['content'][:500]}...")
            st.markdown("**Summary:**")
            st.markdown(summarize(article['content']))

# Display General News with Pagination
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
