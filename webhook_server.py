import os
import stripe
from openai import OpenAI
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
openai_api_key = os.getenv("OPENAI_API_KEY")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "jc55248@gmail.com")

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "✅ FastAPI server is running!"}

@app.post("/webhook")
async def stripe_webhook(request: Request):
    print("🚨 Webhook triggered")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        print(f"✅ Stripe event type: {event['type']}")
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event["type"] == "checkout.session.completed":
        print("🎯 Handling checkout.session.completed")
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        if not customer_email:
            print("❌ No customer email found")
            return {"status": "no email found"}
        
        print(f"📧 Email: {customer_email}")
        generate_and_send_report(customer_email)
    else:
        print(f"ℹ️ Unhandled event type: {event['type']}")

    return {"status": "ok"}

def generate_and_send_report(email):
    print(f"📄 Generating report for {email}")

    # 1. OpenAI Feedback
    prompt = (
        "You are a professional UX researcher. Analyze the following user interaction data or feedback "
        "and generate a structured UX report.\n\n"
        "Provide a brief summary (Clarity, Cognitive Load, Personalization), followed by specific actionable suggestions.\n"
        "Keep the language professional, but accessible.\n\n"
        "Example data: 'User attempted to complete checkout but dropped off on payment screen due to unclear instructions and overloaded UI elements.'"
    )

    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ux_feedback = response.choices[0].message.content.strip()
        print("🧠 OpenAI feedback generated")
    except Exception as e:
        print(f"❌ OpenAI request failed: {e}")
        ux_feedback = "Could not generate feedback due to an error."

    # 2. Generate PDF
    filename = f"UX_Report_{email.replace('@', '_')}.pdf"
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Your UX Report", ln=True, align="C")
        pdf.ln()
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, ux_feedback)
        pdf.output(filename)
        print(f"[✓] PDF report saved: {filename}")
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")
        return

    # 3. Email it
    if not GMAIL_APP_PASSWORD:
        print("❌ GMAIL_APP_PASSWORD not set. Cannot send email.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Your UX Autorater Full Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = email
    msg.set_content("Thanks for your purchase! Your UX feedback report is attached.")

    try:
        with open(filename, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="UX_Report.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)

        print(f"📬 Report emailed to {email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

    # 4. Cleanup
    if os.path.exists(filename):
        os.remove(filename)
        print(f"🧹 Temp file deleted: {filename}")








