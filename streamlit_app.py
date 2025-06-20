import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- OpenAI Setup ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Page Setup ---
st.set_page_config(page_title="Persona UX Autorater", layout="wide")

# --- UI ---
st.title("👥 Persona-Based UX Autorater")
st.subheader("Simulate accessibility feedback from diverse users — before you ship.")
st.markdown("Test your UX copy using AI-generated feedback from **neurodiverse and accessibility personas**. Make your products more inclusive and user-friendly.")

# --- Persona Selector ---
persona = st.selectbox("Choose a simulated user persona:", [
    "🧠 ADHD",
    "🧩 Autism",
    "🌍 ESL (English as Second Language)",
    "👁️ Vision-Impaired (Screen Reader)"
])

# --- UX Input Section ---
default_example = "Thanks! We’ve received your request. You’ll get a response shortly."
ux_input = st.text_area("Enter your UX copy:", value=default_example, height=180)

# --- Prompt Builder ---
def build_prompt(ux_text, persona):
    if persona == "🧠 ADHD":
        return f"""You are simulating feedback from a user with ADHD.\nEvaluate this UX copy:\n{ux_text}\n\n1. Does the language feel too fast, dense, or distracting?\n2. Is attention required to interpret? How could it be more direct?\n3. Suggestions to reduce cognitive load."""
    elif persona == "🧩 Autism":
        return f"""You are simulating feedback from a user with autistic traits.\nEvaluate this UX copy:\n{ux_text}\n\n1. Is the tone overly casual or ambiguous?\n2. Are there any confusing phrases or vague timing?\n3. Suggestions for clarity, predictability, and directness."""
    elif persona == "🌍 ESL (English as Second Language)":
        return f"""You are simulating feedback from an ESL user.\nEvaluate this UX copy:\n{ux_text}\n\n1. Are there idioms, jargon, or complex phrasing?\n2. How simple is the vocabulary and grammar?\n3. Suggestions for clearer and easier-to-translate language."""
    elif persona == "👁️ Vision-Impaired (Screen Reader)":
        return f"""You are simulating feedback from a user relying on screen reader software.\nEvaluate this UX copy:\n{ux_text}\n\n1. Are there confusing word orders or redundant terms?\n2. Would this copy read aloud naturally and helpfully?\n3. Suggestions to make it more accessible for auditory processing."""

# --- Feedback Function ---
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

# --- Autorater Evaluation ---
if st.button("Run Autorater"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = get_feedback(ux_input, persona)
            st.markdown("### 📝 Simulated Feedback")
            st.text_area("Persona Feedback", feedback, height=300)
    else:
        st.warning("Please enter UX copy first.")

# --- Call to Action ---
st.divider()
st.markdown("### 🔒 Want a full UX report?")
st.markdown("Get a complete accessibility audit including PDF download, persona comparisons, and expert design suggestions.")
st.markdown(
    '<a class="buy-button" href="https://buy.stripe.com/test_eVq4gy4UI6If01Le8odQQ00">\ud83d\udcb3 Buy Full Evaluation \u2192</a>',
    unsafe_allow_html=True
)



















