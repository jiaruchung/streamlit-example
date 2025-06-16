import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from openai import OpenAI

# --- Load environment variables ---
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SENDER_EMAIL = "jc55248@gmail.com"  # 🔒 use your Gmail address

# --- OpenAI client ---
client = OpenAI(api_key=OPENAI_API_KEY)

# --- FastAPI setup ---
app = FastAPI()


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
        generate_and_send_report(customer_email)

    return {"status": "ok"}


def generate_persona_feedback(client, ux_text, persona):
    prompt = f"You are a UX evaluation assistant for the persona: {persona}.\n\nEvaluate the following UX text:\n\n{ux_text}\n\nGive a detailed evaluation of its accessibility, clarity, tone, and design suggestions from the perspective of {persona}."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a UX accessibility evaluation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return "OpenAI feedback generation failed."


def generate_and_send_report(email):
    print(f"📄 Generating report for {email}...")

    ux_text = "Example UX copy the user submitted for review."  # Replace with real input
    personas = ["Visually Impaired User", "Senior User", "Mobile-Only User"]

    # --- Generate feedback per persona ---
    feedbacks = {}
    for persona in personas:
        feedbacks[persona] = generate_persona_feedback(client, ux_text, persona)

    # --- Create PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="UX Autorater Full Report", ln=True, align="C")
    pdf.ln()
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, f"Evaluated UX Copy:\n{ux_text}")
    pdf.ln()

    for persona, feedback in feedbacks.items():
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, f"\n{persona}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, feedback)
        pdf.ln()

    pdf.output("report.pdf")
    print("[✓] PDF report created")

    # --- Send via Gmail ---
    if not GMAIL_APP_PASSWORD:
        print("❌ GMAIL_APP_PASSWORD not set")
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





