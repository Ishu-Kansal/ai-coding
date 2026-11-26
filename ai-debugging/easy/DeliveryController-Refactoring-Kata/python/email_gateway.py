import smtplib
from email.mime.text import MIMEText


# File responsibility: adapts application email requests to an SMTP server.
# This file contains the infrastructure boundary for formatting and transmitting
# transactional delivery messages; it does not decide who should receive them.

class EmailGateway:
    def __init__(self, connection_server="localhost", from_address="noreply@example.com"):
        self.connection_server = connection_server
        self.from_address = from_address

    def send(self, address, subject, message):
        # Business logic: wraps a subject, sender, recipient, and plain-text body
        # in an email MIME message, sends it through the configured SMTP service, and
        # closes the SMTP connection. It has no recipient-selection or retry logic.
        msg = MIMEText(message)

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = subject
        msg['From'] = self.from_address
        msg['To'] = address

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP(self.connection_server)
        s.sendmail(self.from_address, [address], msg.as_string())
        s.quit()
