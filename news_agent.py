import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime
import subprocess

st.set_page_config(page_title="LLaMA3 News Summary", page_icon="🦙")
st.title("🦙 LLaMA 3 News Agent")

def search_news(topic):
    with DDGS() as ddg:
        results = ddg.text(f"{topic} news {datetime.now().strftime('%Y-%m')}", max_results=3)
        if results:
            return "\n\n".join([
                f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}"
                for r in results
            ])
        return "No news found."

def ask_llama(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3", prompt],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"❌ LLaMA error: {str(e)}"

def process_news(topic):
    with st.status("Processing news with LLaMA 3...", expanded=True) as status:
        status.write("🔍 Searching...")
        raw_news = search_news(topic)

        status.write("🔄 Synthesizing...")
        synth_prompt = f"Synthesize these news articles:\n\n{raw_news}"
        synthesized = ask_llama(synth_prompt)

        status.write("📝 Summarizing...")
        summary_prompt = (
            f"Summarize this in 1 paragraph in news style:\n\n{synthesized}"
        )
        summary = ask_llama(summary_prompt)

        return raw_news, synthesized, summary

# UI
topic = st.text_input("Enter a news topic:", value="Africa economy")
if st.button("Generate News Summary"):
    if topic:
        raw, synthesis, summary = process_news(topic)
        st.subheader("📋 Summary:")
        st.markdown(summary)
        st.subheader("🧠 Synthesis:")
        st.markdown(synthesis)
        st.subheader("📄 Raw Results:")
        st.markdown(raw)
    else:
        st.warning("Enter a topic to begin.")
