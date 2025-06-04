import streamlit as st
import openai
import os

# Set API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup
st.set_page_config(page_title="Persona UX Autorater", layout="centered")

st.title("👥 Persona-Based UX Autorater")
st.subheader("Simulate accessibility feedback from diverse users before you ship.")
st.markdown("Test your UX copy with simulated feedback from neurodiverse and accessibility-focused personas using AI.")

# Persona tabs
persona = st.selectbox("Choose a simulated user persona:", [
    "🧠 ADHD",
    "🧩 Autism",
    "🌍 ESL (English as Second Language)",
    "👁️ Vision-Impaired (Screen Reader)"
])

st.markdown("### 🎯 Try it Free")

ux_input = st.text_area(
    "Enter your UX copy here:",
    placeholder="Example: 'Thanks! We’ve received your request. You’ll get a response shortly.'",
    height=180
)

# Prompt templates per persona
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
1. Are there any confusing word orders or redundant terms?
2. Would this copy read aloud naturally and helpfully?
3. Suggestions to make it more accessible for auditory processing."""
    }
    return prompts[persona]

# Evaluation logic
def get_feedback(ux_text, persona):
    prompt = build_prompt(ux_text, persona)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a UX accessibility evaluation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response['choices'][0]['message']['content']

# Evaluation
if st.button("Run Autorater"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = get_feedback(ux_input, persona)
            st.markdown("### 📝 Simulated Feedback")
            st.text_area("Persona Feedback", feedback, height=300)
    else:
        st.warning("Please enter some UX copy above.")

st.divider()

# CTA Section
st.markdown("### 🔒 Get Full Reports")
st.markdown("Ready to improve your product with feedback from multiple personas? Get a full audit, accessibility summary, and download-ready PDF.")
st.markdown("[Buy full UX evaluation →](https://buy.stripe.com/test_xxx)", unsafe_allow_html=True)




