import streamlit as st
import os
import openai  # ✅ Correct SDK for compatibility

# --- OpenAI Setup ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Page Setup ---
st.set_page_config(page_title="Persona UX Autorater", layout="wide")

# --- Custom Theme Styling ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    color: #f0f0f0;
    padding-top: 0 !important;
}
h1, h2, h3, h4, h5, h6, p, label {
    color: #ffffff !important;
}
textarea, input, .stTextInput>div>div>input {
    background-color: #222 !important;
    color: #e0e0e0 !important;
    border-radius: 10px;
    border: 1px solid #444;
}
div.stButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.7em 1.5em;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #87CEEB !important;
    color: #000000 !important;
}
a.buy-button {
    display: inline-block;
    background: #F08080;
    color: white !important;
    padding: 0.8em 1.6em;
    font-weight: bold;
    border-radius: 10px;
    text-decoration:


















