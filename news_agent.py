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

# Theme toggle
theme = st.sidebar.radio("Theme", ["Light", "Dark"], index=0)

# Apply Daily Maverick Inspired Styling
if theme == "Dark":
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            background-color: #121212;
            color: #e0e0e0;
        }

        .stApp {
            background-color: #121212;
        }

        .st-emotion-cache-1v0mbdj, .st-emotion-cache-13k62yr {
            background-color: #1e1e1e;
            color: #fff;
            border: 1px solid #333;
        }

        .stButton > button {
            background-color: #bb86fc;
            color: black;
        }

        .news-card {
            background-color: #222;
            color: #eee;
            border-left: 4px solid #bb86fc;
        }

        .featured-right {
            background-color: #1e1e1e;
            color: #fff;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            font-family: 'Merriweather', 'Georgia', serif;
            color: #111;
            background-color: #f8f9fa;
        }

        h1, h2, h3, h4 {
            color: #111;
            font-weight: 700;
        }

        .stApp {
            background-color: #ffffff;
        }

        .st-emotion-cache-1v0mbdj, .st-emotion-cache-13k62yr {
            background: #fff;
            border: 1px solid #ddd;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            border-radius: 8px;
        }

        .stImage > img {
            border-radius: 4px;
            box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
        }

        .stButton > button {
            background-color: #c62828;
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            border-radius: 5px;
            transition: background 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #8e0000;
        }

        .news-card {
            background: white;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            border-left: 5px solid #d32f2f;
            box-shadow: 0 3px 10px rgba(0,0,0,0.04);
            transition: transform 0.2s ease;
        }

        .news-card:hover {
            transform: scale(1.01);
        }

        .news-card h4 {
            margin-top: 0;
        }

        .featured-right {
            padding: 1rem;
            background: #fafafa;
            border-left: 4px solid gold;
            margin-left: 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
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
