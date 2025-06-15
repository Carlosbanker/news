# Expanded version of News Lookup with multi-source aggregation
import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  # Optional, can leave blank to skip

st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️")
st.title("🗞️ News Lookup")
st.markdown("""
A free, multi-source AI-powered news summarizer. Get concise overviews from different reputable sources.
""")

# Headers for HF API
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# RSS Feeds
RSS_FEEDS = [
    ("BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "http://feeds.reuters.com/reuters/topNews"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
]

# ---- Summarization ----
def summarize(text):
    payload = {"inputs": text}
    res = requests.post(HF_API_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()[0]['summary_text']
    else:
        return f"❌ Error: {res.status_code}"

# ---- Source 1: DuckDuckGo ----
def get_duckduckgo_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=5)
        return [
            {
                "source": "DuckDuckGo",
                "title": r["title"],
                "url": r["href"],
                "content": r["body"]
            } for r in results
        ] if results else []

# ---- Source 2: RSS Feeds ----
def get_rss_news():
    entries = []
    for name, url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:2]:  # Limit to 2 per feed
            entries.append({
                "source": name,
                "title": entry.title,
                "url": entry.link,
                "content": entry.summary if hasattr(entry, "summary") else ""
            })
    return entries

# ---- Source 3: NewsAPI (optional) ----
def get_newsapi_news(topic):
    if not NEWSAPI_KEY:
        return []
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWSAPI_KEY}&pageSize=3"
    res = requests.get(url)
    if res.status_code == 200:
        articles = res.json().get("articles", [])
        return [
            {
                "source": "NewsAPI",
                "title": a["title"],
                "url": a["url"],
                "content": a["description"]
            } for a in articles if a["description"]
        ]
    return []

# ---- UI ----
topic = st.text_input("Enter a news topic:", value="climate change")
if st.button("🔎 Look Up News"):
    if topic:
        with st.status("Looking up multiple sources...", expanded=True):
            news = get_duckduckgo_news(topic)
            news += get_rss_news()
            news += get_newsapi_news(topic)

        if not news:
            st.warning("No news found across all sources.")
        else:
            st.markdown("---")
            for i, article in enumerate(news[:10]):
                with st.expander(f"{i+1}. {article['title']} [{article['source']}]"):
                    st.markdown(f"**URL:** [{article['url']}]({article['url']})")
                    st.markdown(f"**Original:** {article['content'][:500]}...")
                    st.markdown("**Summary:**")
                    st.markdown(summarize(article['content']))
    else:
        st.warning("Please enter a topic to search.")
