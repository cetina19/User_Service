# smtp_email_service.py
from aiosmtplib import send
from email.mime.text import MIMEText
from .email import EmailService

class SMTPEmailService(EmailService):

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    async def send_email(self, recipient: str, subject: str, body: str):
        message = MIMEText(body)
        message["From"] = self.username
        message["To"] = recipient
        message["Subject"] = subject

        await send(
            message,
            hostname=self.smtp_server,
            port=self.smtp_port,
            username=self.username,
            password=self.password,
            start_tls=True
        )

def get_email_service():
    return SMTPEmailService(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="alper8540@gmail.com",
        password="hhpf rcmo psdd tmry"
    )