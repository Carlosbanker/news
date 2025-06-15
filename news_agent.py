import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Setup Streamlit UI
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")

st.title("🗞️ News Lookup")
st.markdown("A multi-source AI-powered news summarizer with filtering and pagination.")

# Search input and source filters
topic = st.text_input("Enter a news topic:", "")
available_sources = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]
selected_sources = st.multiselect("Filter by source:", available_sources, default=available_sources)

if st.button("🔎 Look Up News") and topic:
    with st.spinner("Fetching news..."):
        all_news = []
        rate_limits = {}

        # GNews Featured Section
        featured = []
        try:
            gnews_url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&token={GNEWS_KEY}"
            gnews_data = requests.get(gnews_url).json()
            if 'articles' in gnews_data:
                featured = gnews_data['articles']
        except Exception as e:
            rate_limits['GNews'] = f"⚠️ GNews failed: {e}"

        # DuckDuckGo Search
        if "DuckDuckGo" in selected_sources:
            try:
                with DDGS() as ddgs:
                    ddg_results = [r for r in ddgs.text(topic, max_results=50)]
                    for r in ddg_results:
                        all_news.append({
                            "title": r.get("title"),
                            "link": r.get("href"),
                            "body": r.get("body"),
                            "source": "DuckDuckGo",
                            "published": datetime.now(),
                        })
            except Exception as e:
                rate_limits['DuckDuckGo'] = f"⚠️ DuckDuckGo failed: {e}"

        # RSS Feeds
        feeds = {
            "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
            "Reuters": "http://feeds.reuters.com/reuters/topNews",
            "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        }

        for name, url in feeds.items():
            if name in selected_sources:
                try:
                    d = feedparser.parse(url)
                    for entry in d.entries[:50]:
                        all_news.append({
                            "title": entry.title,
                            "link": entry.link,
                            "body": entry.summary,
                            "source": name,
                            "published": datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now(),
                        })
                except Exception as e:
                    rate_limits[name] = f"⚠️ {name} failed: {e}"

        # Sort by newest first
        all_news = sorted(all_news, key=lambda x: x.get("published", datetime.min), reverse=True)

        # Display Results and Featured
        col1, col2 = st.columns([3, 1])

        with col2:
            st.markdown("### 🟨 Featured (GNews)")
            for item in featured:
                st.image(item.get("image", "https://via.placeholder.com/150"), use_container_width=True)
                st.markdown(f"[{item.get('title')}]({item.get('url')})")
                st.caption(item.get("source", {}).get("name", ""))

        with col1:
            st.markdown("## 📰 Results")
            page_size = 10
            total_pages = len(all_news) // page_size + (1 if len(all_news) % page_size > 0 else 0)
            page = st.number_input("Page", 1, total_pages, 1, 1)
            start = (page - 1) * page_size
            end = start + page_size
            for item in all_news[start:end]:
                st.markdown(f"**{item['title']}** [{item['source']}]({item['link']})")
                st.image("https://via.placeholder.com/150", width=400)
                st.caption(item['body'])

        # Settings Panel
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            st.markdown("Toggle News Sources and View Options")
            for src in available_sources:
                st.checkbox(f"Enable {src}", value=(src in selected_sources), key=f"chk_{src}")
            theme = st.radio("Theme", ["Light", "Dark"], index=1)
            st.markdown("---")
            st.markdown("### 🚨 Rate Limit / Errors")
            for key, msg in rate_limits.items():
                st.warning(msg)
