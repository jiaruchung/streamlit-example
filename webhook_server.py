import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

app = FastAPI()

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 🎉 Payment completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        print(f"✅ Payment received from: {customer_email}")

        # 🚀 TODO: Trigger report generation & email delivery here
        generate_and_send_report(customer_email)

    return {"status": "ok"}

# Simulated function (replace this)
def generate_and_send_report(email):
    print(f"📄 Generating report for {email}... (you’ll connect this to your Streamlit app or model)")
