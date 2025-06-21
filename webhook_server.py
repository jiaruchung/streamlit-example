import os
import stripe
from openai import OpenAI
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from fastapi.responses import RedirectResponse

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
    return RedirectResponse(url="https://jiaruchung-streamlit-example.streamlit.app/")

@app.get("/success")
async def success_page():
    return {"message": "✅ Payment successful! Your UX report will be emailed within a few minutes."}

@app.get("/cancel")
async def cancel_page():
    return {"message": "⚠️ Payment was canceled. Feel free to try again later."}

@app.post("/create_checkout_session")
async def create_checkout_session(req: Request):
    data = await req.json()
    email = data.get("email")
    persona = data.get("persona")
    ux_input = data.get("ux_input")

    if not all([email, persona, ux_input]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": 700,  # $7.00
                    "product_data": {
                        "name": "UX Autorater Report",
                        "description": f"Persona: {persona}"
                    }
                },
                "quantity": 1
            }],
            success_url="https://httpbin.org/get",
            cancel_url="https://httpbin.org/status/400",
            metadata={"persona": persona, "ux_input": ux_input},
            customer_email=email
        )
        return {"checkout_url": session.url}
    except Exception as e:
        print(f"❌ Stripe session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Stripe session creation failed")

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
        generate_and_send_report(customer_email, persona, ux_input)

    return {"status": "ok"}

def safe_pdf(text):
    return text.encode("latin-1", errors="ignore").decode("latin-1")

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
        pdf.cell(200, 10, txt=safe_pdf("Your UX Report"), ln=True, align="C")
        pdf.ln()
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, safe_pdf(f"Persona: {persona}"))
        pdf.ln()
        pdf.multi_cell(0, 10, safe_pdf(f"User Input:\n{ux_input}"))
        pdf.ln()
        pdf.multi_cell(0, 10, safe_pdf(f"AI-Generated Feedback:\n{ux_feedback}"))
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














