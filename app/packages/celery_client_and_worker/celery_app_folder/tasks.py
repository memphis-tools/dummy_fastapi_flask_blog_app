"""The celery worker's tasks"""

import os
import base64
import smtplib
import textwrap
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from celery_app import celery_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from python_http_client.exceptions import HTTPError
import requests.exceptions

from books_into_pdf import generate_a_pdf_to_consume
try:
    from utils import get_secret
except ModuleNotFoundError:
    from app.packages.utils import get_secret


@celery_app.task(name="generate_pdf_and_send_email_task")
def generate_pdf_and_send_email_task(recipient):
    """The task ran by celery worker"""
    try:
        pdf_file_path = generate_a_pdf_to_consume()
        send_email(recipient, pdf_file_path)
        os.remove(pdf_file_path)
        return {
            "status": "success",
            "message": f"Email sent successfully to {recipient}",
        }
    except FileNotFoundError:
        return {"status": "failure", "message": "Books file not found"}


def send_email(recipient, pdf_file_path):
    """A send email function triggered by the celery worker's task"""

    with open(pdf_file_path, "rb") as fd:
        pdf_data = fd.read()
        encoded_file = base64.b64encode(pdf_data).decode()

    if os.getenv("SCOPE") == "production":
        pdf_file_name = os.getenv("PDF_FILE_NAME")
        # Create an Attachment object
        attached_file = Attachment(
            FileContent(encoded_file),
            FileName(pdf_file_name),
            FileType('application/pdf'),
            Disposition('attachment')
        )
        message = Mail(
            from_email="no-reply@dummy-ops.dev",
            to_emails=recipient,
            subject="Dummy-ops books",
            html_content=textwrap.dedent("""
                Find attached a list of the books published on dummy-ops.dev.
                Thank you for your interest.
            """)
        )

        # Add the attachment to the Mail object
        message.attachment = attached_file
        # Send the email
        SENDGRID_API_KEY = get_secret("/run/secrets/SENDGRID_API_KEY")
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except HTTPError as e:
            return {"status": "failure", "message": f"SendGrid HTTP error: {e}"}
        except requests.exceptions.RequestException as e:
            return {"status": "failure", "message": f"Request failed: {e}"}
        except Exception as e:
            # Fallback for unexpected errors
            return {"status": "failure", "message": f"Unexpected error: {e}"}
    elif os.getenv("SCOPE") == "development":
        # We use smtplib and MailTrap
        mailtrap_user_name = os.getenv("MAILTRAP_USER_NAME")
        mailtrap_user_password = os.getenv("MAILTRAP_USER_PASSWORD")
        # Email configuration
        sender = "no-reply@dummy-ops.dev"
        receiver = "to@example.com"
        subject = "Dummy-ops books"
        body = textwrap.dedent("""
            Find attached a list of the books published on dummy-ops.dev.
            Thank you for your interest.
        """)

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        # Attach the body
        msg.attach(MIMEText(body, 'plain'))

        filename = f"{pdf_file_path}"
        attachment = open(filename, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {filename.split('/')[-1]}")
        msg.attach(part)

        # Send the email
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login(mailtrap_user_name, mailtrap_user_password)
            server.set_debuglevel(1)
            result = server.sendmail(sender, receiver, msg.as_string())

            print("Sendmail result:", result)
