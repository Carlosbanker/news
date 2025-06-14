import streamlit as st
from duckduckgo_search import DDGS
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
HF_API_KEY = os.getenv("HF_TOKEN")

st.set_page_config(page_title="🗞️ AI News Processor", page_icon="📰")
st.title("📰 Multi-Format News Generator (Powered by Hugging Face)")

# -------------------- Hugging Face Inference ----------------------

def ask_huggingface(prompt, system_prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"<s>[INST] <<SYS>>{system_prompt}<</SYS>> {prompt} [/INST]",
        "parameters": {"temperature": 0.7, "max_new_tokens": 1024}
    }

    response = requests.post(
        "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return response.json()[0]["generated_text"].split("[/INST]")[-1].strip()
    else:
        raise Exception(f"API error {response.status_code}: {response.text}")

# -------------------- DuckDuckGo Search ----------------------

def search_news(topic, max_results=10):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=max_results)
        if results:
            return [
                f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}" for r in results
            ]
        return []

# -------------------- News Workflow ----------------------

def process_news(topic, count):
    with st.status("Processing news...", expanded=True) as status:
        status.write("🔍 Gathering news...")
        articles = search_news(topic, count)
        full_text = "\n\n".join(articles)

        if not full_text:
            raise Exception("No news found.")

        # 🔄 Synthesis
        status.write("🔄 Synthesizing...")
        synthesis = ask_huggingface(
            full_text,
            "You are a professional journalist. Combine the articles into a cohesive, factual synthesis. Avoid bias. Write in 3-5 paragraphs."
        )

        # 🧠 Headlines
        status.write("🗞️ Generating headlines...")
        headlines = ask_huggingface(
            full_text,
            "You are a headline writer. Generate a list of up to 10 punchy, accurate headlines from these articles."
        )

        # 📰 Final Summary
        status.write("✍️ Creating AP/Reuters-style summary...")
        summary = ask_huggingface(
            synthesis,
            "You are an AP/Reuters-style journalist. Summarize the key development in one clear paragraph: What happened? Why it matters? What's next?"
        )

        return articles, synthesis, headlines, summary

# -------------------- Streamlit UI ----------------------

st.markdown("Enter a topic to fetch and summarize up to 10 news articles.")

col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Enter topic:", value="artificial intelligence")
with col2:
    count = st.slider("Articles", min_value=1, max_value=10, value=5)

if st.button("Generate News Report", type="primary"):
    if topic:
        try:
            raw_articles, synthesis, headlines, summary = process_news(topic, count)

            st.subheader("📝 Final Summary")
            st.markdown(summary)

            st.subheader("🧠 Synthesized News")
            st.markdown(synthesis)

            st.subheader("🗞️ Top Headlines")
            st.markdown(headlines)

            st.subheader("📰 Full Articles")
            for i, article in enumerate(raw_articles, start=1):
                st.markdown(f"**Article {i}:**\n{article}\n")

        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a topic.")
