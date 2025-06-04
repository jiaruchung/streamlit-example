import streamlit as st
import os
from openai import OpenAI

# --- SETUP ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Persona UX Autorater", layout="centered")

# --- DARK THEME STYLING ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #0f0f0f, #1a1a1a);
    color: #f0f0f0;
}
h1, h2, h3, h4, p, label {
    color: #f8f8f8 !important;
}
textarea, input, .stTextInput>div>div>input {
    background-color: #1e1e1e !important;
    color: #e0e0e0 !important;
}
button[kind="primary"] {
    background-color: #ff4b4b !important;
    color: white !important;
    border-radius: 8px;
    font-weight: bold;
}
a {
    color: #00bfff !important;
    font-weight: bold;
}
.css-18ni7ap.e8zbici2 {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("👥 Persona-Based UX Autorater")
st.subheader("Simulate accessibility feedback from diverse users before you ship.")
st.markdown("Test your UX copy with simulated feedback from **neurodiverse and accessibility personas** using AI.")

# --- PERSONA SELECTOR ---
persona = st.selectbox("Choose a simulated user persona:", [
    "🧠 ADHD",
    "🧩 Autism",
    "🌍 ESL (English as Second Language)",
    "👁️ Vision-Impaired (Screen Reader)"
])

# --- UX INPUT ---
st.markdown("### 🎯 Try It Free")
ux_input = st.text_area(
    "Enter your UX copy below:",
    placeholder="Example: 'Thanks! We’ve received your request. You’ll get a response shortly.'",
    height=180
)

# --- PROMPT FACTORY ---
def build_prompt(ux_text, persona):
    prompts = {
        "🧠 ADHD": f"""You are simulating feedback from a user with ADHD.
Evaluate this UX copy:
{ux_text}

1. Does the language feel too fast, dense, or distracting?
2. Is attention required to interpret? How could it be more direct?
3. Suggestions to reduce cognitive load.""",

        "🧩 Autism": f"""You are simulating feedback from a user with autistic traits.
Evaluate this UX copy:
{ux_text}

1. Is the tone overly casual or ambiguous?
2. Are there any confusing phrases or vague timing?
3. Suggestions for clarity, predictability, and directness.""",

        "🌍 ESL (English as Second Language)": f"""You are simulating feedback from an ESL user.
Evaluate this UX copy:
{ux_text}

1. Are there idioms, jargon, or complex phrasing?
2. How simple is the vocabulary and grammar?
3. Suggestions for clearer and easier-to-translate language.""",

        "👁️ Vision-Impaired (Screen Reader)": f"""You are simulating feedback from a user relying on screen reader software.
Evaluate this UX copy:
{ux_text}

1. Are there confusing word orders or redundant terms?
2. Would this copy read aloud naturally and helpfully?
3. Suggestions to make it more accessible for auditory processing."""
    }
    return prompts[persona]

# --- EVALUATION ---
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

# --- RUN BUTTON ---
if st.button("Run Autorater"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = get_feedback(ux_input, persona)
            st.markdown("### 📝 Simulated Feedback")
            st.text_area("Persona Feedback", feedback, height=300)
    else:
        st.warning("Please enter your UX copy above.")

st.divider()

# --- CTA TO PAID OPTION ---
st.markdown("### 🔒 Want a full UX report?")
st.markdown("Get a full accessibility audit with **PDF download**, persona comparisons, and design recommendations.")
st.markdown("[💳 Buy Full Evaluation →](https://buy.stripe.com/test_xxx)", unsafe_allow_html=True)






