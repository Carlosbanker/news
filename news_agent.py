import streamlit as st
from duckduckgo_search import DDGS
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Streamlit page setup
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")
st.title("🗞️ News Lookup")
st.markdown("Get live news from multiple sources, including featured headlines.")

# --- Input ---
topic = st.text_input("Enter a news topic:")
available_sources = ["DuckDuckGo", "BBC", "Reuters", "Al Jazeera"]
selected_sources = st.multiselect("Select sources", available_sources, default=available_sources)

# Placeholder fallback image
PLACEHOLDER = "https://via.placeholder.com/400x200"

# Extract image from HTML content
def extract_image(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag["src"]
    except:
        pass
    return PLACEHOLDER

if st.button("🔍 Search") and topic:
    st.info("Fetching articles...")

    all_news = []
    featured = []
    errors = {}

    # --- GNEWS FEATURED ---
    try:
        gnews_url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=5&token={GNEWS_KEY}"
        response = requests.get(gnews_url)
        gnews_data = response.json()

        for article in gnews_data.get("articles", []):
            featured.append({
                "title": article["title"],
                "url": article["url"],
                "image": article.get("image", PLACEHOLDER),
                "source": article["source"]["name"],
                "published": article["publishedAt"]
            })
    except Exception as e:
        errors["GNews"] = str(e)

    # --- DuckDuckGo Search ---
    if "DuckDuckGo" in selected_sources:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(topic, max_results=30):
                    all_news.append({
                        "title": r.get("title"),
                        "link": r.get("href"),
                        "body": r.get("body", "No summary."),
                        "image": PLACEHOLDER,
                        "source": "DuckDuckGo",
                        "published": datetime.now()
                    })
        except Exception as e:
            errors["DuckDuckGo"] = str(e)

    # --- RSS FEEDS ---
    feeds = {
        "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
        "Reuters": "http://feeds.reuters.com/reuters/topNews",
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    }

    for name, url in feeds.items():
        if name in selected_sources:
            try:
                parsed = feedparser.parse(url)
                for entry in parsed.entries[:20]:
                    all_news.append({
                        "title": entry.title,
                        "link": entry.link,
                        "body": entry.get("summary", ""),
                        "image": extract_image(entry.get("summary", "")),
                        "source": name,
                        "published": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else datetime.now()
                    })
            except Exception as e:
                errors[name] = str(e)

    # --- SORT BY DATE ---
    all_news = sorted(all_news, key=lambda x: x.get("published", datetime.min), reverse=True)

    # --- FEATURED SECTION ---
    if featured:
        st.subheader("🌟 Featured News (GNews)")
        for f in featured:
            st.image(f["image"], use_container_width=True)
            st.markdown(f"**[{f['title']}]({f['url']})**")
            st.caption(f"{f['source']} | {f['published'][:10]}")
            st.markdown("---")

    # --- PAGINATION ---
    st.subheader("📰 News Results")
    if not all_news:
        st.warning("No news found.")
    else:
        page_size = 10
        total_pages = (len(all_news) - 1) // page_size + 1
        page = st.number_input("Page", 1, total_pages, 1)

        start = (page - 1) * page_size
        end = start + page_size

        for article in all_news[start:end]:
            st.markdown(f"### [{article['title']}]({article['link']})")
            st.caption(f"{article['source']} | {article['published'].strftime('%Y-%m-%d %H:%M')}")
            st.image(article["image"], use_container_width=True)
            st.write(article["body"])
            st.markdown("---")

    # --- ERROR REPORT ---
    if errors:
        st.subheader("⚠️ Errors")
        for src, msg in errors.items():
            st.warning(f"{src}: {msg}")
