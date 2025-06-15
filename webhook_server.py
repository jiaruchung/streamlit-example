import os
import stripe
import openai
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# Load environment variables from .env file
load_dotenv()

# Stripe + OpenAI + Gmail credentials
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")
SENDER_EMAIL = "jc55248@gmail.com"  # ✅ Your Gmail
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

app = FastAPI()

# 🔍 AI function to generate feedback
def generate_ux_feedback(ux_text):
    system_prompt = "You are a senior UX researcher generating an evaluation report based on user-facing copy."
    user_prompt = f"""Evaluate the following UX copy:

\"{ux_text}\"

Provide:
- A clarity score (out of 5) and explanation
- A cognitive load score (out of 5) and explanation
- Readability analysis (e.g., grade level)
- Suggestions for improvement (bullet list)
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )

    return response['choices'][0]['message']['content']

# 🖨 PDF and email generation
def generate_and_send_report(email, ux_text="Thank you for signing up. You will receive an email shortly."):
    print(f"📄 Generating report for {email}...")

    # 1. AI-generated content
    ai_feedback = generate_ux_feedback(ux_text)

    # 2. PDF creation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "UX Autorater – Full Report", align="C")
    pdf.ln()

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "Evaluated UX Copy:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, ux_text)
    pdf.ln()

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "AI-Generated Feedback:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, ai_feedback)
    pdf.output("report.pdf")
    print("[✓] PDF report created")

    # 3. Email via Gmail
    if not GMAIL_APP_PASSWORD:
        print("❌ GMAIL_APP_PASSWORD not set. Cannot send email.")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Your UX Autorater Full Report'
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg.set_content("Thanks for your purchase! Your full UX feedback report is attached.")

    with open("report.pdf", 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename='UX_Report.pdf')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        print(f"📬 Report sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# 🌐 Stripe webhook endpoint
@app.post("/webhook")
async def stripe_webhook(request: Request):
    print("🚨 Stripe webhook called")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        print(f"✅ Payment received from: {customer_email}")

        # You can dynamically replace this text if collected from user
        ux_text = "Thank you for signing up. You will receive an email shortly."

        generate_and_send_report(customer_email, ux_text)

    return {"status": "ok"}




