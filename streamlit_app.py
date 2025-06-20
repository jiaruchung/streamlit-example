import streamlit as st
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Persona UX Autorater", layout="wide")

st.title("👥 Persona-Based UX Autorater")
st.subheader("Simulate accessibility feedback from diverse users — before you ship.")

persona = st.selectbox("Choose a simulated user persona:", [
    "🧠 ADHD",
    "🧩 Autism",
    "🌍 ESL (English as Second Language)",
    "👁️ Vision-Impaired (Screen Reader)"
])

default_example = "Thanks! We’ve received your request. You’ll get a response shortly."
ux_input = st.text_area("Enter your UX copy:", value=default_example, height=180)

def build_prompt(ux_text, persona):
    return f"""You are simulating feedback from a user with traits of {persona}.
Evaluate this UX copy:
{ux_text}

1. Is the language appropriate for this persona?
2. Are there confusing parts or accessibility issues?
3. Suggestions to improve clarity and usability."""

def get_feedback(ux_text, persona):
    prompt = build_prompt(ux_text, persona)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a UX accessibility evaluation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

if st.button("Run Autorater"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = get_feedback(ux_input, persona)
            st.markdown("### 📝 Simulated Feedback")
            st.text_area("Persona Feedback", feedback, height=300)
    else:
        st.warning("Please enter UX copy first.")

st.divider()
st.markdown("### 🔒 Want a full UX report?")
st.markdown("Get a complete accessibility audit including PDF download via email.")

if st.button("💳 Buy Full Evaluation →"):
    if ux_input.strip():
        with st.spinner("Creating checkout session..."):
            res = requests.post("https://streamlit-example-1-dwdp.onrender.com/create_checkout_session", json={
                "persona": persona,
                "ux_input": ux_input
            })
            if res.ok:
                checkout_url = res.json()["checkout_url"]
                st.success("Redirecting to Stripe...")
                st.markdown(f"[👉 Click here to pay]({checkout_url})", unsafe_allow_html=True)
            else:
                st.error("Failed to create checkout session.")
    else:
        st.warning("Please enter your UX copy before purchasing.")


















