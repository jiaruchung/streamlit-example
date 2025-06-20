import os
import stripe
from openai import OpenAI
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
openai_api_key = os.getenv("OPENAI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "jc55248@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Debug checks
print("[DEBUG] OPENAI_API_KEY loaded:", bool(openai_api_key))
print("[DEBUG] GMAIL_APP_PASSWORD loaded:", bool(GMAIL_APP_PASSWORD))
print("[DEBUG] STRIPE_SECRET_KEY loaded:", bool(stripe.api_key))
print("[DEBUG] STRIPE_WEBHOOK_SECRET loaded:", bool(endpoint_secret))
print("[DEBUG] SENDER_EMAIL loaded:", SENDER_EMAIL)

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "✅ FastAPI server is running!"}

@app.post("/create_checkout_session")
async def create_checkout_session(request: Request):
    body = await request.json()
    email = body.get("email")
    ux_input = body.get("ux_input", "")
    persona = body.get("persona", "General User")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "UX Autorater Full Report",
                        "description": f"Evaluation for persona: {persona}"
                    },
                    "unit_amount": 500,  # $5.00 USD
                },
                "quantity": 1,
            }],
            mode="payment",
            customer_email=email,
            metadata={
                "persona": persona,
                "ux_input": ux_input,
            },
            success_url="https://streamlit-example-1thq.onrender.com?success=true",
            cancel_url="https://streamlit-example-1thq.onrender.com?canceled=true",
        )

        return JSONResponse({"checkout_url": session.url})
    except Exception as e:
        print(f"[ERROR] Failed to create Stripe session: {e}")
        raise HTTPException(status_code=500, detail="Could not create Stripe session")

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        metadata = session.get("metadata", {})
        persona = metadata.get("persona", "general user")
        ux_input = metadata.get("ux_input", "No input provided")
        print(f"✅ Payment received from: {customer_email}")
        print(f"[Metadata] persona={persona}, ux_input={ux_input[:40]}...")
        generate_and_send_report(customer_email, persona, ux_input)

    return {"status": "ok"}

def generate_and_send_report(email, persona, ux_input):
    print(f"📄 Generating report for {email}...")

    # 1. Generate feedback via OpenAI
    try:
        client = OpenAI(api_key=openai_api_key)
        prompt = (
            f"You are a professional UX researcher specializing in {persona}.\n\n"
            "Analyze the following user interaction data or feedback and generate a structured UX report.\n"
            "Provide a brief summary (Clarity, Cognitive Load, Personalization), followed by specific actionable suggestions.\n"
            "Keep the language professional, but accessible.\n\n"
            f"User input: '{ux_input}'"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ux_feedback = response.choices[0].message.content.strip()
        print("[✓] Feedback generated from OpenAI")
    except Exception as e:
        print(f"❌ OpenAI request failed: {e}")
        ux_feedback = "Could not generate feedback due to an error."

    # 2. Generate PDF report
    filename = f"UX_Report_{email.replace('@', '_')}.pdf"
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Your UX Report", ln=True, align="C")
        pdf.ln()
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, f"Persona: {persona}")
        pdf.ln()
        pdf.multi_cell(0, 10, f"User Input:\n{ux_input}")
        pdf.ln()
        pdf.multi_cell(0, 10, f"AI-Generated Feedback:\n{ux_feedback}")
        pdf.output(filename)
        print(f"[✓] PDF saved as {filename}")
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")
        return

    # 3. Email the report
    if not GMAIL_APP_PASSWORD:
        print("❌ GMAIL_APP_PASSWORD not set. Cannot send email.")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = "Your UX Autorater Full Report"
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg.set_content("Thanks for your purchase! Your UX feedback report is attached.")

        with open(filename, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="UX_Report.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        print(f"📬 Report emailed to {email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

    # 4. Clean up
    if os.path.exists(filename):
        os.remove(filename)
        print(f"[✓] Temp file deleted: {filename}")












