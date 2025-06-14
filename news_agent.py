import streamlit as st
from duckduckgo_search import DDGS
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load Hugging Face Token
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

st.set_page_config(page_title="📰 AI News Agent (HF API)", page_icon="📰")
st.title("📰 News Inshorts - Powered by Hugging Face API")

# Headers for API request
headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# Hugging Face API endpoint
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def summarize_with_hf_api(text):
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        raise Exception(f"Hugging Face API Error: {response.status_code} - {response.text}")

# News search
def search_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=3)
        if results:
            return "\n\n".join([
                f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}"
                for r in results
            ])
        return "No news found."

# Streamlit UI
topic = st.text_input("Enter news topic:", value="climate change")

if st.button("Process News", type="primary"):
    if topic:
        with st.status("Processing news...", expanded=True) as status:
            try:
                status.write("🔍 Searching for news...")
                raw_news = search_news(topic)

                status.write("📝 Summarizing via Hugging Face API...")
                summary = summarize_with_hf_api(raw_news)

                st.header("📝 Summary")
                st.markdown(summary)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a topic.")
