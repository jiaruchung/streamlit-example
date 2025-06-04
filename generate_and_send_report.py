from fpdf import FPDF
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import os

def generate_persona_feedback(client, ux_text, persona):
    persona_prompt = build_prompt(ux_text, persona)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a UX accessibility evaluation assistant."},
            {"role": "user", "content": persona_prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def generate_pdf_report(ux_text, persona_feedbacks, filename="UX_Report.pdf"):
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

def send_email_with_pdf(recipient_email, filename="UX_Report.pdf"):
    sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
    with open(filename, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()

    message = Mail(
        from_email="your@email.com",
        to_emails=recipient_email,
        subject="Your UX Autorater Full Report",
        html_content="Thanks for purchasing! Your full UX feedback report is attached."
    )
    message.attachment = Attachment(
        FileContent(encoded),
        FileName(filename),
        FileType("application/pdf"),
        Disposition("attachment")
    )

    sg.send(message)

def generate_and_send_report(client, ux_text, email, personas):
    feedbacks = {}
    for persona in personas:
        feedbacks[persona] = generate_persona_feedback(client, ux_text, persona)

    filename = f"UX_Report_{email.replace('@', '_')}.pdf"
    generate_pdf_report(ux_text, feedbacks, filename)
    send_email_with_pdf(email, filename)
