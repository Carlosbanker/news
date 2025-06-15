# Expanded version of News Lookup with multi-source aggregation
import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")  # Optional, can leave blank to skip

# --- Page Config ---
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️")
st.title("🗞️ News Lookup")
st.markdown("""
A free, multi-source AI-powered news summarizer. Get concise overviews from different reputable sources.
""")

# --- HuggingFace API Headers ---
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# --- RSS Feeds ---
RSS_FEEDS = [
    ("BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("Reuters", "http://feeds.reuters.com/reuters/topNews"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
]

# --- Summarization Function ---
def summarize(text):
    payload = {"inputs": text}
    res = requests.post(HF_API_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()[0]['summary_text']
    else:
        return f"❌ Error: {res.status_code}"

# --- DuckDuckGo News Search ---
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

# --- RSS Feed Parser ---
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

# --- NewsAPI Aggregator ---
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

    res = requests.get(url, params=params)
    if res.status_code == 200:
        articles = res.json().get("articles", [])
        return [
            {
                "source": "NewsAPI",
                "title": a["title"],
                "url": a["url"],
                "content": a.get("description") or a.get("content", "No description available.")
            } for a in articles if a.get("description") or a.get("content")
        ]
    else:
        st.error(f"NewsAPI Error: {res.status_code} - {res.text}")
        return []

# --- Search Input ---
topic = st.text_input("Enter a news topic:", value="climate change")

# --- Result Pagination State ---
if "result_index" not in st.session_state:
    st.session_state.result_index = 0

# --- Lookup Button ---
if st.button("🔎 Look Up News"):
    if topic:
        with st.status("Looking up multiple sources...", expanded=True):
            news = get_duckduckgo_news(topic)
            news += get_rss_news()
            news += get_newsapi_news(topic)

        # Store full result set in session
        st.session_state.news_results = news
        st.session_state.result_index = 0
    else:
        st.warning("Please enter a topic to search.")

# --- Display Results ---
if "news_results" in st.session_state and st.session_state.news_results:
    total = len(st.session_state.news_results)
    idx = st.session_state.result_index
    end_idx = min(idx + 10, total)

    st.markdown("---")
    st.subheader(f"Showing articles {idx + 1} to {end_idx} of {total}")

    for i in range(idx, end_idx):
        article = st.session_state.news_results[i]
        with st.expander(f"{i+1}. {article['title']} [{article['source']}]"):
            st.markdown(f"**URL:** [{article['url']}]({article['url']})")
            st.markdown(f"**Original:** {article['content'][:500]}...")
            st.markdown("**Summary:**")
            st.markdown(summarize(article['content']))

    if end_idx < total:
        if st.button("🔽 Show 10 More"):
            st.session_state.result_index += 10
