import streamlit as st
from duckduckgo_search import DDGS
import requests
import feedparser
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GNEWS_KEY = os.getenv("GNEWS_KEY")

st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")
st.title("🗞️ News Lookup")
st.markdown("A multi-source AI-powered news summarizer with filtering and pagination.")

# Input
topic = st.text_input("Enter a news topic:")
available_sources = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]
selected_sources = st.multiselect("Filter by source:", available_sources, default=available_sources)

# Only trigger when search pressed
if st.button("🔎 Look Up News") and topic:
    with st.spinner("Fetching news..."):
        all_news = []
        rate_limits = {}

        # Fetch from GNews
        featured = []
        try:
            gnews_url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&token={GNEWS_KEY}"
            gnews_data = requests.get(gnews_url).json()
            if gnews_data.get("articles"):
                for item in gnews_data["articles"]:
                    featured.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "image": item.get("image") or "https://via.placeholder.com/150",
                        "source": item.get("source", {}).get("name", "GNews"),
                        "published": item.get("publishedAt", datetime.now().isoformat())
                    })
        except Exception as e:
            rate_limits['GNews'] = f"⚠️ GNews error: {e}"

        # DuckDuckGo Search
        if "DuckDuckGo" in selected_sources:
            try:
                with DDGS() as ddgs:
                    ddg_results = ddgs.text(topic, max_results=30)
                    for r in ddg_results:
                        all_news.append({
                            "title": r.get("title"),
                            "link": r.get("href"),
                            "body": r.get("body") or "No description available.",
                            "source": "DuckDuckGo",
                            "published": datetime.now(),
                        })
            except Exception as e:
                rate_limits['DuckDuckGo'] = f"⚠️ DuckDuckGo error: {e}"

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
                    for entry in d.entries[:20]:
                        all_news.append({
                            "title": entry.get("title"),
                            "link": entry.get("link"),
                            "body": entry.get("summary", "No summary available."),
                            "source": name,
                            "published": datetime(*entry.published_parsed[:6]) if entry.get('published_parsed') else datetime.now(),
                        })
                except Exception as e:
                    rate_limits[name] = f"⚠️ {name} RSS error: {e}"

        # Sort news by date
        all_news = sorted(all_news, key=lambda x: x.get("published", datetime.min), reverse=True)

        # Display UI
        col1, col2 = st.columns([3, 1])

        with col2:
            st.markdown("### 🟨 Featured (GNews)")
            for item in featured:
                st.image(item["image"], use_container_width=True)
                st.markdown(f"[{item['title']}]({item['url']})")
                st.caption(item["source"])

        with col1:
            st.markdown("## 📰 Results")
            page_size = 10
            total_pages = max(1, (len(all_news) - 1) // page_size + 1)
            page = st.number_input("Page", 1, total_pages, 1)
            start = (page - 1) * page_size
            end = start + page_size

            for item in all_news[start:end]:
                st.markdown(f"### [{item['title']}]({item['link']})")
                st.caption(f"*Source: {item['source']} | Date: {item['published'].strftime('%Y-%m-%d %H:%M')}*")
                st.image("https://via.placeholder.com/400x200", width=400)
                st.write(item["body"])

        # Sidebar Settings
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            for src in available_sources:
                st.checkbox(f"Enable {src}", value=(src in selected_sources), key=f"chk_{src}")
            theme = st.radio("Theme", ["Light", "Dark"], index=0)
            st.markdown("---")
            st.markdown("### 🚨 Rate Limit / Errors")
            for k, v in rate_limits.items():
                st.warning(v)
