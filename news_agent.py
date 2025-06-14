import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

# Load environment variables from .env
load_dotenv()

# Setup OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

st.set_page_config(page_title="AI News Processor", page_icon="📰")
st.title("📰 News Inshorts Agent")

# ----------- Wrapper Function --------------

def ask_openai(prompt, role_description, model="gpt-3.5-turbo", temperature=0.5):
    messages = [
        {"role": "system", "content": role_description},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1000
    )
    return response.choices[0].message.content

# ----------- News Search --------------

def search_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=3)
        if results:
            return "\n\n".join([
                f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}"
                for r in results
            ])
        return "No news found."

# ----------- News Processing Flow -------------

def process_news(topic):
    with st.status("Processing news...", expanded=True) as status:
        # Step 1: Search
        status.write("🔍 Searching for news...")
        raw_news = search_news(topic)

        # Step 2: Synthesize
        status.write("🔄 Synthesizing articles...")
        synth_prompt = f"Synthesize the following news articles:\n\n{raw_news}"
        synth_role = (
            "You are a news synthesis expert. Summarize the key points from multiple news sources "
            "into 2–3 clear, objective paragraphs."
        )
        synthesized = ask_openai(synth_prompt, synth_role)

        # Step 3: Summarize
        status.write("📝 Creating a summary...")
        summary_prompt = f"Summarize this news synthesis:\n\n{synthesized}"
        summary_role = (
            "You are a professional news summarizer using AP/Reuters style. Write one short paragraph "
            "explaining what happened, why it matters, and what’s next. Be concise, clear, and factual."
        )
        summary = ask_openai(summary_prompt, summary_role)

        return raw_news, synthesized, summary

# ----------- UI -------------

topic = st.text_input("Enter news topic:", value="Artificial Intelligence")

if st.button("Process News", type="primary"):
    if topic:
        try:
            raw, synth, summary = process_news(topic)
            st.header(f"📝 News Summary: {topic}")
            st.markdown(summary)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a topic.")
