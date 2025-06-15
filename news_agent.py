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
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Streamlit setup
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")
st.title("🗞️ News Lookup")
st.markdown("A multi-source AI-powered news summarizer with filtering and pagination.")

# Input section
topic = st.text_input("Enter a news topic:")
available_sources = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]
selected_sources = st.multiselect("Filter by source:", available_sources, default=available_sources)

# Extract image from HTML summary
def extract_image(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag["src"]
    except:
        pass
    return "https://via.placeholder.com/400x200"

if st.button("🔍 Search") and topic:
    st.info("Fetching news...")
    all_news = []
    featured_news = []
    errors = {}

    # --- GNews Featured ---
    try:
        gnews_url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&token={GNEWS_KEY}"
        gnews_data = requests.get(gnews_url).json()
        for item in gnews_data.get("articles", []):
            featured_news.append({
                "title": item["title"],
                "url": item["url"],
                "image": item.get("image", "https://via.placeholder.com/400x200"),
                "source": item["source"]["name"],
                "published": item["publishedAt"]
            })
    except Exception as e:
        errors["GNews"] = str(e)

    # --- DuckDuckGo ---
    if "DuckDuckGo" in selected_sources:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(topic, max_results=30):
                    all_news.append({
                        "title": r.get("title"),
                        "link": r.get("href"),
                        "body": r.get("body", "No description available."),
                        "source": "DuckDuckGo",
                        "published": datetime.now()
                    })
        except Exception as e:
            errors["DuckDuckGo"] = str(e)

    # --- RSS Feeds ---
    feeds = {
        "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    }

    for name, url in feeds.items():
        if name in selected_sources:
            try:
                d = feedparser.parse(url)
                for entry in d.entries[:30]:
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "body": entry.get("summary", ""),
                        "source": name,
                        "published": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else datetime.now()
                    })
            except Exception as e:
                errors[name] = str(e)

    # Sort articles
    all_news = sorted(all_news, key=lambda x: x.get("published", datetime.min), reverse=True)

    # --- Display Featured News ---
    st.subheader("🌟 Featured News")
    for f in featured_news:
        st.markdown(f"**[{f['title']}]({f['url']})**")
        st.image(f["image"], use_container_width=True)
        st.caption(f"{f['source']} | {f['published'][:10]}")
        st.markdown("---")

    # --- Paginated Main Results ---
    st.subheader("📰 All Results")
    if not all_news:
        st.warning("No news found.")
    else:
        page_size = 10
        total_pages = (len(all_news) - 1) // page_size + 1
        page = st.number_input("Page", 1, total_pages, 1)
        start = (page - 1) * page_size
        end = start + page_size

        for article in all_news[start:end]:
            img = extract_image(article["body"]) if article["source"] != "DuckDuckGo" else "https://via.placeholder.com/400x200"
            pub_str = article["published"].strftime("%Y-%m-%d %H:%M") if isinstance(article["published"], datetime) else str(article["published"])
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.caption(f"{article['source']} | {pub_str}")
            st.image(img, use_container_width=True)
            st.write(article["body"])
            st.markdown("---")

    # --- Error Section ---
    if errors:
        st.subheader("⚠️ Errors")
        for name, msg in errors.items():
            st.warning(f"{name}: {msg}")
