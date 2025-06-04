import streamlit as st
import os
import time
from openai import OpenAI

# --- Setup ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.set_page_config(page_title="UX Autorater", layout="centered")

# --- Dark Theme & Button Styling ---
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
    background-color: #ffffff !important;
    color: black !important;
    border-radius: 8px;
    font-weight: bold;
}
a {
    color: #00bfff !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- Hero Illustration ---
st.image("https://undraw.co/api/illustrations/8f110aa0-e9d6-4990-9cf7-850c6c91f0e1", use_column_width=True)

# --- Title and Introduction ---
st.title("👥 Persona-Based UX Autorater")
st.markdown("Test your UX copy with AI-generated feedback from neurodiverse and accessibility personas.")

# --- Instructions & UX Copy Input ---
st.markdown("### 🎯 Try It Free")
st.markdown("_Enter product text like tooltips, confirmations, alerts, etc._")

example = "Thanks! We’ve received your request. You’ll get a response shortly."
ux_input = st.text_area("Enter your UX copy:", value=example, height=180)

# --- Personas to Compare ---
selected_personas = st.multiselect(
    "Select personas to simulate feedback from:",
    ["🧠 ADHD", "🧩 Autism", "🌍 ESL", "👁️ Vision-Impaired"],
    default=["🧠 ADHD", "🌍 ESL"]
)

# --- Build Prompt ---
def build_prompt(ux_text, persona):
    prompts = {
        "🧠 ADHD": f"""You are simulating feedback from a user with ADHD.
UX Copy:
{ux_text}
Respond with cognitive load, attention challenge, and improvement suggestions.""",

        "🧩 Autism": f"""You are simulating feedback from a user with autistic traits.
UX Copy:
{ux_text}
Comment on tone, clarity, predictability, and sensory comfort.""",

        "🌍 ESL": f"""You are simulating feedback from an ESL user.
UX Copy:
{ux_text}
Respond with feedback on language simplicity, grammar clarity, and translation friendliness.""",

        "👁️ Vision-Impaired": f"""You are simulating feedback from a screen reader user.
UX Copy:
{ux_text}
Comment on audio clarity, accessibility of structure, and improvement tips."""
    }
    return prompts[persona]

# --- Animated Typewriter Effect ---
def typewriter(text):
    for char in text:
        st.markdown(f"<span style='font-size:16px'>{char}</span>", unsafe_allow_html=True)
        time.sleep(0.01)

# --- Get Feedback from OpenAI ---
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

# --- Autorater Run ---
if st.button("✨ Run Autorater"):
    if ux_input.strip() and selected_personas:
        st.markdown("### 📝 Simulated Feedback")
        cols = st.columns(len(selected_personas))
        for idx, persona in enumerate(selected_personas):
            with cols[idx]:
                st.markdown(f"**{persona}**")
                with st.spinner(f"Analyzing {persona}..."):
                    feedback = get_feedback(ux_input, persona)
                    st.text_area("Feedback", feedback, height=250, key=persona)
    else:
        st.warning("Please enter UX copy and select at least one persona.")

# --- Call to Action ---
st.divider()
st.markdown("### 🔒 Want a full UX report?")
st.markdown("Get a downloadable PDF, expert suggestions, and persona comparison.")
st.markdown(
    "[💳 Buy Full Evaluation →](https://buy.stripe.com/test_8x26oJc9VdbLgM7eMN6EU00)",
    unsafe_allow_html=True
)










