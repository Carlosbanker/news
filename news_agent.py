import streamlit as st
from duckduckgo_search import DDGS
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI News Processor", page_icon="📰")
st.title("📰 News Inshorts Agent")

# -------------------- OpenAI Wrappers ----------------------

def ask_openai(prompt, role_description, temperature=0.5, model="gpt-4"):
    messages = [
        {"role": "system", "content": role_description},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=1000,
    )
    return response.choices[0].message.content

# -------------------- DuckDuckGo Search ----------------------

def search_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=3)
        if results:
            return "\n\n".join([
                f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}"
                for r in results
            ])
        return "No news found."

# -------------------- Main Pipeline ----------------------

def process_news(topic):
    with st.status("Processing news...", expanded=True) as status:
        # Search
        status.write("🔍 Searching for news...")
        raw_news = search_news(topic)

        # Synthesize
        status.write("🔄 Synthesizing information...")
        synth_prompt = f"Synthesize these news articles:\n\n{raw_news}"
        synth_role = (
            "You are a news synthesis expert. Your job is to combine multiple articles into a clear, "
            "objective 2–3 paragraph synthesis. Be concise and focus on main themes."
        )
        synthesized_news = ask_openai(synth_prompt, synth_role)

        # Summarize
        status.write("📝 Creating summary...")
        summary_prompt = f"Summarize this synthesis:\n\n{synthesized_news}"
        summary_role = (
            "You are a professional news summarizer in AP/Reuters style. Give a clear 1-paragraph summary "
            "covering the what, who, why it matters, and what’s next. Be factual and brief."
        )
        final_summary = ask_openai(summary_prompt, summary_role)

        return raw_news, synthesized_news, final_summary

# -------------------- Streamlit UI ----------------------

topic = st.text_input("Enter news topic:", value="artificial intelligence")
if st.button("Process News", type="primary"):
    if topic:
        try:
            raw_news, synthesized_news, final_summary = process_news(topic)
            st.header(f"📝 News Summary: {topic}")
            st.markdown(final_summary)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please enter a topic.")
