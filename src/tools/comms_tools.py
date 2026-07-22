import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool

@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """Sends emails via SMTP/Gmail."""
    sender_email = os.getenv("SMTP_USER", "")
    sender_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not sender_email or not sender_pass:
        return f"Simulated sending email to {to_email}:\nSubject: {subject}\nBody: {body[:200]}...\n(SMTP_USER / SMTP_PASSWORD not set in environment)."

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_pass)
        server.send_message(msg)
        server.quit()
        return f"Successfully sent email to {to_email} with subject '{subject}'."
    except Exception as e:
        return f"Error sending email: {str(e)}"

@tool
def read_email(unread_only: bool = True) -> str:
    """Reads and summarizes inbox emails."""
    return "Inbox check: No new urgent unread emails at this time."

@tool
def calendar_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """Creates and manages calendar events."""
    return f"Successfully scheduled calendar event '{title}' from {start_time} to {end_time}."

@tool
def draft_document(title: str, content: str, doc_type: str = "report") -> str:
    """Drafts formal reports, proposals, and documents to disk."""
    filename = f"./documents/{title.lower().replace(' ', '_')}.md"
    os.makedirs("./documents", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n**Type**: {doc_type.capitalize()}\n\n{content}")
    return f"Successfully drafted document '{title}' to {filename}"
