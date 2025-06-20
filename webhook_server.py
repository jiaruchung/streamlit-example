import os
import stripe
from openai import OpenAI
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
openai_api_key = os.getenv("OPENAI_API_KEY")
gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
sender_email = os.getenv("SENDER_EMAIL", "jc55248@gmail.com")

client = OpenAI(api_key=openai_api_key)

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class CheckoutRequest(BaseModel):
    persona: str
    ux_input: str

@app.post("/create_checkout_session")
async def create_checkout_session(data: CheckoutRequest):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": "your_price_id_here",  # Replace with your real Stripe price ID
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:8501?success=true",
        cancel_url="http://localhost:8501?cancelled=true",
        metadata={
            "persona": data.persona,
            "ux_input": data.ux_input
        }
    )
    return {"checkout_url": session.url}

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_details"]["email"]
        persona = session["metadata"].get("persona")
        ux_input = session["metadata"].get("ux_input")
        generate_and_send_report(email, persona, ux_input)

    return {"status": "ok"}

def generate_and_send_report(email, persona, ux_input):
    print(f"[→] Generating report for: {email} ({persona})")

    prompt = (
        f"You are a professional UX researcher specializing in {persona}.\n\n"
        "Analyze the following UX copy and generate a structured report "
        "with a brief summary (Clarity, Cognitive Load, Personalization), "
        "followed by actionable suggestions.\n\n"
        f"UX Copy: {ux_input}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ux_feedback = response.choices[0].message.content.strip()
    except Exception as e:
        ux_feedback = f"(Error generating feedback: {e})"

    filename = f"UX_Report_{email.replace('@', '_')}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Your UX Report", ln=True, align="C")
    pdf.ln()
    pdf.multi_cell(0, 10, f"Persona: {persona}")
    pdf.ln()
    pdf.multi_cell(0, 10, f"UX Input:\n{ux_input}")
    pdf.ln()
    pdf.multi_cell(0, 10, f"Feedback:\n{ux_feedback}")
    pdf.output(filename)

    msg = EmailMessage()
    msg["Subject"] = "Your UX Autorater Report"
    msg["From"] = sender_email
    msg["To"] = email
    msg.set_content("Thanks for your payment! Your UX report is attached.")

    with open(filename, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=filename)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, gmail_app_password)
            smtp.send_message(msg)
        print(f"[✓] Email sent to {email}")
    except Exception as e:
        print(f"[✗] Failed to send email: {e}")

    if os.path.exists(filename):
        os.remove(filename)









