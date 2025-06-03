import streamlit as st
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI()  # Uses OPENAI_API_KEY from environment variables

def simulate_neurodiverse_feedback(ux_copy: str) -> str:
    system_prompt = (
        "You are simulating a neurodivergent user (specifically autistic and ADHD traits) "
        "evaluating a piece of UX copy. Focus on cognitive load, clarity, tone, "
        "and any sensory or attention challenges it may present. Be honest and concrete."
    )

    user_prompt = (
        f"UX Copy to Evaluate:\n{ux_copy}\n\n"
        "Please provide:\n"
        "1. Clarity Rating (1–5): How easy is this to understand?\n"
        "2. Cognitive Load Rating (1–5): How mentally taxing is this?\n"
        "3. Sensory/Distraction Issues: Any sensory overload or disruptive structure?\n"
        "4. Suggestions to improve accessibility and usability."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content

# Streamlit App
st.set_page_config(page_title="Neurodiverse UX Autorater", layout="centered")
st.title("🧠 Neurodiverse UX Autorater")
st.markdown("Simulate feedback from an autistic/ADHD user on your UX copy.")

ux_input = st.text_area("Enter UX copy to evaluate:", height=200)

if st.button("Rate UX Copy"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = simulate_neurodiverse_feedback(ux_input)
            st.markdown("### 📝 Simulated Persona Feedback")
            st.text_area("Feedback", feedback, height=300)
    else:
        st.warning("Please enter UX copy first.")


