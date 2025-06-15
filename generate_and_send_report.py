from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os

def generate_persona_feedback(client, ux_text, persona):
    print(f"[→] Generating feedback for persona: {persona}")
    persona_prompt = build_prompt(ux_text, persona)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a UX accessibility evaluation assistant."},
            {"role": "user", "content": persona_prompt}
        ],
        temperature=0.4
    )
    feedback = response.choices[0].message.content.strip()
    print(f"[✓] Feedback for {persona} generated")
    return feedback

def generate_pdf_report(ux_text, persona_feedbacks, filename="UX_Report.pdf"):
    print(f"[→] Generating PDF report: {filename}")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "UX Autorater – Full Report", align="C")
    pdf.ln()

    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, f"Evaluated UX Copy:\n{ux_text}")
    pdf.ln()

    for persona, feedback in persona_feedbacks.items():
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, f"\n{persona}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, feedback)
        pdf.ln()

    pdf.output(filename)
    print(f"[✓] PDF saved: {filename} (exists? {os.path.exists(filename)})")

def send_email_with_pdf(recipient_email, filename="UX_Report.pdf"):
    print(f"[→] Preparing to send email to: {recipient_email}")
    sender_email = "your_email@gmail.com"  # Replace with your Gmail
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not app_password:
        print("[✗] ERROR: Missing Gmail app password from environment variable.")
        return

    if not os.path.exists(filename):
        print(f"[✗] ERROR: Attachment not found: {filename}")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Your UX Autorater Full Report'
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content("Thanks for your purchase! Your full UX feedback report is attached.")

    with open(filename, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=filename)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print(f"[✓] Email sent to: {recipient_email}")
    except Exception as e:
        print(f"[✗] ERROR sending email: {e}")

def generate_and_send_report(client, ux_text, email, personas):
    print(f"[→] Starting report generation for: {email}")
    try:
        feedbacks = {}
        for persona in personas:
            feedbacks[persona] = generate_persona_feedback(client, ux_text, persona)

        filename = f"UX_Report_{email.replace('@', '_')}.pdf"
        generate_pdf_report(ux_text, feedbacks, filename)

        print(f"[→] Calling send_email_with_pdf()")
        send_email_with_pdf(email, filename)

        # Optional cleanup
        if os.path.exists(filename):
            os.remove(filename)
            print(f"[✓] Temp file deleted: {filename}")
    except Exception as e:
        print(f"[✗] ERROR in generate_and_send_report: {e}")



