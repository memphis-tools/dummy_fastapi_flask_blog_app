"""The celery worker's tasks"""

import os
import base64
from celery_app import celery_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from books_into_pdf import generate_a_pdf_to_consume


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
        html_content="""
            Find attached the books published on dummy-ops.dev<br>
            <strong>Thank you for your interest.</strong>
        """
    )

    # Add the attachment to the Mail object
    message.attachment = attached_file
    # Send the email
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    try:
        sg = SendGridAPIClient(os.environ.get(''))
        response = sg.send(message)
    except Exception as e:
        return {"status": "failure", "message": "Mail sending failed"}
