import streamlit as st
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(page_title="Persona UX Autorater", layout="wide")

# Custom styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
    color: #f0f0f0;
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
    text-decoration: none;
    transition: background 0.3s;
}
a.buy-button:hover {
    background: #e06c6c;
}
.persona-img {
    border-radius: 50%;
    height: 100px;
    margin-right: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("👥 Persona-Based UX Autorater")
st.subheader("Simulate accessibility feedback from diverse users — before you ship.")
st.markdown("Test your UX copy using AI-generated feedback from **neurodiverse and accessibility personas**. Make your products more inclusive and user-friendly.")

# Personas table
st.markdown("### 💡 Supported Personas")
st.markdown("""
<table>
<tr>
  <td><img src="https://img.icons8.com/color/100/adhd.png" class="persona-img"></td>
  <td>🧠 <b>ADHD</b><br>Easily distracted, overwhelmed by cluttered or vague text</td>
</tr>
<tr>
  <td><img src="https://img.icons8.com/color/100/autism.png" class="persona-img"></td>
  <td>🧩 <b>Autism</b><br>Prefers clear, literal, structured, and emotionally neutral content</td>
</tr>
<tr>
  <td><img src="https://img.icons8.com/color/100/language.png" class="persona-img"></td>
  <td>🌍 <b>ESL</b><br>May struggle with idioms, slang, or overly complex grammar</td>
</tr>
<tr>
  <td><img src="https://img.icons8.com/color/100/visible.png" class="persona-img"></td>
  <td>👁️ <b>Low Vision</b><br>Uses screen readers or magnifiers; prefers linear and concise layout</td>
</tr>
</table>
""", unsafe_allow_html=True)

# Persona select
persona = st.selectbox("Choose a simulated user persona:", [
    "🧠 ADHD",
    "🧩 Autism",
    "🌍 ESL (English as Second Language)",
    "👁️ Vision-Impaired (Screen Reader)"
])

# UX Input
st.markdown("### 🎯 Try It Free")
default_example = "Thanks! We’ve received your request. You’ll get a response shortly."
ux_input = st.text_area("Enter your UX copy:", value=default_example, height=180)

# Prompt builder
def build_prompt(ux_text, persona):
    if persona == "🧠 ADHD":
        return f"""You are simulating feedback from a user with ADHD.
Evaluate this UX copy:
{ux_text}

1. Does the language feel too fast, dense, or distracting?
2. Is attention required to interpret? How could it be more direct?
3. Suggestions to reduce cognitive load."""
    
    elif persona == "🧩 Autism":
        return f"""You are simulating feedback from a user with autistic traits.
Evaluate this UX copy:
{ux_text}

1. Is the tone overly casual or ambiguous?
2. Are there any confusing phrases or vague timing?
3. Suggestions for clarity, predictability, and directness."""
    
    elif persona == "🌍 ESL (English as Second Language)":
        return f"""You are simulating feedback from an ESL user.
Evaluate this UX copy:
{ux_text}

1. Are there idioms, jargon, or complex phrasing?
2. How simple is the vocabulary and grammar?
3. Suggestions for clearer and easier-to-translate language."""
    
    elif persona == "👁️ Vision-Impaired (Screen Reader)":
        return f"""You are simulating feedback from a user relying on screen reader software.
Evaluate this UX copy:
{ux_text}

1. Are there confusing word orders or redundant terms?
2. Would this copy read aloud naturally and helpfully?
3. Suggestions to make it more accessible for auditory processing."""

# Feedback logic
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

# Autorater button
if st.button("Run Autorater"):
    if ux_input.strip():
        with st.spinner("Simulating feedback..."):
            feedback = get_feedback(ux_input, persona)
            st.markdown("### 📝 Simulated Feedback")
            st.text_area("Persona Feedback", feedback, height=300)
    else:
        st.warning("Please enter UX copy first.")

# Stripe CTA for full report
st.divider()
st.markdown("### 🔒 Want a full UX report?")
st.markdown("Get a complete accessibility audit including PDF download, persona comparisons, and expert design suggestions.")

user_email = st.text_input("Your email address (for report delivery):", "")

st.markdown(
    '<p><b>After payment, a detailed report will be sent to your email within 1–3 minutes.</b></p>',
    unsafe_allow_html=True
)

if st.button("💳 Buy Full Evaluation"):
    if not user_email or not ux_input.strip():
        st.warning("Please enter your email and UX input before purchasing.")
    else:
        with st.spinner("Creating Stripe Checkout..."):
            try:
                res = requests.post("https://streamlit-example-1thq.onrender.com/create_checkout_session", json={
                    "email": user_email,
                    "persona": persona,
                    "ux_input": ux_input
                })
            
                # DEBUG log
                st.code(f"Status code: {res.status_code}\nResponse text:\n{res.text}")
            
                try:
                    data = res.json()
                    checkout_url = data.get("checkout_url")
                except ValueError:
                st.error("Server response was not valid JSON.")
                checkout_url = None

                if checkout_url:
                    st.success("Redirecting to Stripe...")
                    st.markdown(f'<a href="{checkout_url}" target="_blank" class="buy-button">Proceed to Payment</a>', unsafe_allow_html=True)
                else:
                    st.error("Failed to create checkout session.")
            except Exception as e:
                st.error(f"Error: {e}")





















