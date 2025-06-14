import streamlit as st
from duckduckgo_search import DDGS
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load API token
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Hugging Face setup
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# App config
st.set_page_config(page_title="🗞️ News Look Up", page_icon="🔎", layout="wide")

# Header
st.markdown("""
    <style>
        .main-title {
            font-size: 3em;
            font-weight: 700;
            color: #333333;
        }
        .subtitle {
            font-size: 1.2em;
            color: #777777;
            margin-bottom: 1em;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🗞️ News Look Up</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Real-time news search & AI-powered intelligent summarization</div>", unsafe_allow_html=True)

# Search bar
topic = st.text_input("🔍 Enter a topic to look up news", value="AI regulation", placeholder="e.g. Bitcoin, War in Gaza, Climate Change...")

# Hugging Face summarizer
def summarize_with_hf_api(text):
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 400,
            "min_length": 150,
            "do_sample": False,
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        raise Exception(f"Hugging Face API Error {response.status_code}: {response.text}")

# DuckDuckGo search
def search_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=10)
        return results if results else []

# Process
if st.button("🚀 Process News", type="primary"):
    if topic.strip() == "":
        st.warning("Please enter a topic.")
    else:
        with st.status("🔎 Fetching and processing news...", expanded=True) as status:
            try:
                news_results = search_news(topic)
                if not news_results:
                    st.warning("No news articles found.")
                else:
                    full_text = ""
                    st.subheader("📰 Sources")
                    for i, article in enumerate(news_results):
                        with st.container():
                            st.markdown(f"**{i+1}. [{article['title']}]({article['href']})**")
                            st.caption(article['body'])
                            full_text += article['body'] + "\n\n"

                    status.write("✍️ Summarizing with Hugging Face...")
                    summary = summarize_with_hf_api(full_text)

                    st.divider()
                    st.subheader("🧠 AI Summary")
                    st.markdown(f"```{summary}```")
                    st.success("✅ Done!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
