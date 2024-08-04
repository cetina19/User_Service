from abc import ABC, abstractmethod

class EmailService(ABC):

    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str):
        pass

class MockEmailService(EmailService):

    def send_email(self, recipient: str, subject: str, body: str):
        print(f"Mock email sent to {recipient} with subject '{subject}' and body '{body}'")