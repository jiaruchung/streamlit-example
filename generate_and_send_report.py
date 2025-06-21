import os
from openai import OpenAI
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
sender_email = os.getenv("SENDER_EMAIL", "jc55248@gmail.com")  # default fallback

print("[DEBUG] OPENAI_API_KEY loaded:", bool(openai_api_key))
print("[DEBUG] GMAIL_APP_PASSWORD loaded:", bool(gmail_app_password))
print("[DEBUG] STRIPE_SECRET_KEY loaded:", bool(os.getenv("STRIPE_SECRET_KEY")))
print("[DEBUG] STRIPE_WEBHOOK_SECRET loaded:", bool(os.getenv("STRIPE_WEBHOOK_SECRET")))
print("[DEBUG] SENDER_EMAIL loaded:", sender_email)

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

def safe_pdf(text):
    """Removes characters not supported by latin-1 for FPDF."""
    return text.encode("latin-1", errors="ignore").decode("latin-1")

def generate_and_send_report(email, persona, ux_input):
    print(f"📄 Generating report for {email}...")

    # --- 1. Generate UX Feedback via OpenAI ---
    prompt = (
        f"You are a professional UX researcher specializing in {persona}.\n\n"
        "Analyze the following user interaction data or feedback and generate a structured UX report.\n"
        "Provide a brief summary (Clarity, Cognitive Load, Personalization), followed by specific actionable suggestions.\n"
        "Keep the language professional, but accessible.\n\n"
        f"User input: '{ux_input}'"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        ux_feedback = response.choices[0].message.content.strip()
        print("[✓] Feedback generated from OpenAI")
    except Exception as e:
        print(f"[✗] Failed to generate feedback from OpenAI: {e}")
        ux_feedback = "Could not generate feedback due to an error."

    # --- 2. Generate PDF Report ---
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
        print(f"[✓] PDF report saved as: {filename}")
    except Exception as e:
        print(f"[✗] Failed to create PDF: {e}")
        return

    # --- 3. Email the Report ---
    if not gmail_app_password:
        print("[✗] Missing Gmail app password, cannot send email.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Your UX Autorater Report"
    msg["From"] = sender_email
    msg["To"] = email
    msg.set_content("Thanks for your purchase! Your UX feedback report is attached.")

    try:
        with open(filename, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=filename)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, gmail_app_password)
            smtp.send_message(msg)
        print(f"[✓] Email sent to {email}")
    except Exception as e:
        print(f"[✗] Failed to send email: {e}")

    # --- 4. Clean up ---
    if os.path.exists(filename):
        os.remove(filename)
        print(f"[✓] Temp file deleted: {filename}")







