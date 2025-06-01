import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Credentials (you can store them as environment variables or keep them hardcoded as shown here)
SENDER_EMAIL = "ayush04coder@gmail.com"
SENDER_PASSWORD = "ibsr ongz bjnc gpiy"  # App-specific password
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL Port for Gmail
RECIPIENT_EMAIL = "2023csb1108@iitrpr.ac.in"

def send_email(to_email, subject, body):
    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the server and send the email
    try:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)  # SSL connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage:
if __name__ == '__main__':
    send_email(RECIPIENT_EMAIL, "Test Subject", "This is a test email body.")
