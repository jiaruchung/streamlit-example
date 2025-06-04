import streamlit as st
import os
from openai import OpenAI

# --- OpenAI Setup ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Page Setup ---
st.set_page_config(page_title="Persona UX Autorater", layout="centered")

# --- Custom Dark Theme Styling + ✅ Button Fix ---
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
div.stButton > button {
    background-color: #1e1e1e !important;  /* white background */
    color: #e0e0e0 !important;             /* black text */
    font-weight: bold !important;
    border-radius: 8px !important;
    border: 1px solid #ccc !important;
    padding: 0.6em 1.4em !important;
}
div.stButton > button:hover {
    background-color: #f0f0f0 !important;
    color: #1e1e1e !important;
    border-color: #aaa !important;
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

# --- Title & Intro ---
st.title("👥 Persona-Based UX Autorater")
st.subheader("Simulate accessibility feedback from diverse users before you ship.")
st.markdown("Test your UX copy with AI-generated feedback from **neurodiverse and accessibility personas**.")

# --- Persona Overview ---
st.markdown("""
### 💡 Supported Personas

| 👤 Persona | Description |
|------------|-------------|
| 🧠 **ADHD** | Easily distracted, overwhelmed by cluttered or vague text |
| 🧩 **Autism** | Prefers clear, literal, structured, and emotionally neutral content |
| 🌍 **ESL** | May struggle with idioms, slang, or overly complex grammar |
| 👁️ **Low Vision** | Uses screen readers or magnifiers; prefers linear and concise layout |
""")

# --- Persona Selector ---
persona = st.selectbox("Choose a simulated user persona:", [
    "🧠 ADHD",
    "🧩 Autism",
    "🌍 ESL (English as Second Language)",
    "👁️ Vision-Impaired (Screen Reader)"
])

# --- UX Input Section ---
st.markdown("### 🎯 Try It Free")
st.markdown("_Paste a message or microcopy that users will read in your product — for example, a confirmation message, tooltip, button label, or system alert._")

default_example = "Thanks! We’ve received your request. You’ll get a response shortly."

ux_input = st.text_area("Enter your UX copy:", value=default_example, height=180)

# --- Prompt Builder ---
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
    "[💳 Buy Full Evaluation →](https://buy.stripe.com/test_8x26oJc9VdbLgM7eMN6EU00)",
    unsafe_allow_html=True
)














