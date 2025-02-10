import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

class EmailService:
    def __init__(self, smtp_server, port, email_address, email_password):
        self.smtp_server = smtp_server
        self.port = port
        self.email_address = email_address
        self.email_password = email_password

    def send_email(self, recipient_email, subject, body, attachment_path=None):
        try:
            # Create the email
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Add the email body
            msg.attach(MIMEText(body, 'plain'))

            # Attach the QR code if provided
            if attachment_path:
                with open(attachment_path, 'rb') as file:
                    img = MIMEImage(file.read())
                    img.add_header('Content-Disposition', f'attachment; filename="{attachment_path}"')
                    msg.attach(img)

            # Send the email
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)

            print(f"Email sent to {recipient_email} successfully.")
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {e}")
