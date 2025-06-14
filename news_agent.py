import streamlit as st
from duckduckgo_search import DDGS
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load Hugging Face Token
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# App and model config
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="🗞️ News Look Up", page_icon="🔎", layout="wide")

# ---------- Styling ----------
st.markdown("""
    <style>
        .main-title {
            font-size: 3em;
            font-weight: bold;
            color: #222;
        }
        .subtitle {
            font-size: 1.1em;
            color: #666;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🗞️ News Look Up</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Real-time news search & detailed AI summarization</div>", unsafe_allow_html=True)
st.divider()

# ---------- Summarizer ----------
def summarize_with_hf_api(text):
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": 500,
            "min_length": 200,
            "do_sample": False,
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        raise Exception(f"Hugging Face API Error {response.status_code}: {response.text}")

# ---------- News Search ----------
def search_news(topic):
    with DDGS() as ddg:
        return ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=10)

# ---------- User Input ----------
topic = st.text_input("🔍 Enter a news topic", value="climate change", placeholder="e.g. AI, elections, sports...")

if st.button("🚀 Process News", type="primary"):
    if topic.strip() == "":
        st.warning("Please enter a topic.")
    else:
        with st.status("Fetching and summarizing articles...", expanded=True) as status:
            try:
                news_results = search_news(topic)
                if not news_results:
                    st.warning("No news found.")
                else:
                    st.subheader("📰 Top Articles")
                    for i, article in enumerate(news_results):
                        title = article['title']
                        url = article['href']
                        body = article['body']

                        st.markdown(f"### {i+1}. [{title}]({url})")
                        st.caption(body)

                        try:
                            status.write(f"Summarizing article {i+1}...")
                            summary = summarize_with_hf_api(body)
                        except Exception as e:
                            summary = f"Error generating summary: {str(e)}"

                        expander_label = "📖 Click to read AI-generated summary"
                        st.expander(expander_label).markdown(summary)

                        st.markdown("---")

                    status.update(label="✅ Done summarizing!", state="complete")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
