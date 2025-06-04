import streamlit as st
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # or use st.secrets["OPENAI_API_KEY"]

def simulate_neurodiverse_feedback(ux_copy: str) -> str:
    system_prompt = (
        "You are simulating a neurodivergent user (specifically autistic and ADHD traits) "
        "evaluating a piece of UX copy. Focus on cognitive load, clarity, tone, "
        "and any sensory or attention challenges it may present. Be honest and concrete."
    )

    user_prompt = f"""
    UX Copy to Evaluate:
    {ux_copy}

    Please provide:
    1. Clarity Rating (1–5): How easy is this to understand?
    2. Cognitive Load Rating (1–5): How mentally taxing is this?
    3. Sensory/Distraction Issues: Any sensory overload or disruptive structure?
    4. Suggestions to improve accessibility and usability.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    return response['choices'][0]['message']['content']


# Streamlit App
st.set_page_config(page_title="Neurodiverse UX Autorater", layout="centered")

# ✅ Title & Intro
st.title("🧠 Neurodiverse UX Autorater")
st.subheader("Design better. For everyone.")
st.markdown("Simulate how neurodivergent users — especially those with **autism and ADHD** — experience your UX writing.")

# ✅ Pricing Blurb
st.markdown("### 💡 Pricing")
st.markdown("Get a free preview below. For a full evaluation and PDF report, it’s just **$9.99 per copy**.")

st.divider()

# ✅ Sample UX Input
st.markdown("### 🎯 Try it Free")
ux_input = st.text_area(
    "Enter UX copy to evaluate:",
    placeholder="Example: 'Thanks! We’ve received your request. You’ll get a response shortly.'",
    height=180
)

# ✅ Evaluation Output
if st.button("Evaluate Free Sample"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = simulate_neurodiverse_feedback(ux_input)
            st.markdown("### 📝 Simulated Persona Feedback")
            st.text_area("Feedback", feedback, height=300)
    else:
        st.warning("⚠️ Please enter your UX copy above.")

st.divider()

# ✅ CTA to Paid Service
st.markdown("### 🔒 Want a full neurodiverse UX report?")
st.markdown("[Buy full UX evaluation →](https://buy.stripe.com/test_xxx)", unsafe_allow_html=True)



