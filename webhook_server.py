# webhook_server.py
import os
import stripe
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fpdf import FPDF
import sendgrid
from sendgrid.helpers.mail import Mail

app = FastAPI()

# Stripe setup
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# SendGrid setup
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


def generate_report(ux_text):
    # Sample simulated prompt – expand this as needed
    prompt = f"Give a UX report on this copy from a neurodiverse perspective:\n\n{ux_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response['choices'][0]['message']['content']


def create_pdf(content: str, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)


def send_email(to_email: str, pdf_path: str):
    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(
        from_email="noreply@yourdomain.com",
        to_emails=to_email,
        subject="Your UX Report",
        plain_text_content="Thanks for your purchase. Here's your UX report.",
    )
    with open(pdf_path, 'rb') as f:
        data = f.read()
        f.close()
    message.add_attachment(
        data,
        filename="ux_report.pdf",
        type="application/pdf",
        disposition="attachment"
    )
    sg.send(message)


@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle checkout session completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get("customer_details", {}).get("email")
        metadata = session.get("metadata", {})
        ux_copy = metadata.get("ux_copy", "No UX copy provided")

        # 1. Generate feedback
        report_content = generate_report(ux_copy)

        # 2. Create PDF
        pdf_path = "/tmp/ux_report.pdf"
        create_pdf(report_content, pdf_path)

        # 3. Email report
        if customer_email:
            send_email(customer_email, pdf_path)

    return JSONResponse(status_code=200, content={"status": "success"})


# Simulated function (replace this)
def generate_and_send_report(email):
    print(f"📄 Generating report for {email}... (you’ll connect this to your Streamlit app or model)")
