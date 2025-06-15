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
HF_TOKEN = os.getenv("HF_TOKEN")
GNEWS_KEY = os.getenv("GNEWS_KEY")

# Setup Streamlit UI
st.set_page_config(page_title="📰 News Lookup", page_icon="🗞️", layout="wide")

# Apply Daily Maverick Inspired Styling
st.markdown("""
    <style>
    html, body {
        background-color: #f5f5f5;
        color: #222;
        font-family: 'Georgia', serif;
        line-height: 1.6;
        font-size: 16px;
    }
    .st-emotion-cache-1v0mbdj, .st-emotion-cache-13k62yr {
        background: white;
        border: 1px solid #ddd;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #111;
    }
    .stImage > img {
        border-radius: 5px;
    }
    .stButton > button {
        background-color: #d32f2f;
        color: white;
        border: none;
        padding: 0.5em 1em;
        border-radius: 4px;
    }
    .stButton > button:hover {
        background-color: #b71c1c;
    }
    .news-card {
        background: white;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #d32f2f;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .news-card h4 {
        margin-top: 0;
    }
    [data-testid="column"] div:has(> .element-container:nth-child(1)) {
        position: sticky;
        top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗞️ News Lookup")
st.markdown("A multi-source AI-powered news summarizer with filtering and pagination.")

# Continue with the rest of your code unchanged
