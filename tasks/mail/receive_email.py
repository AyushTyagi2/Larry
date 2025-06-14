import imaplib
import email
from email.header import decode_header
import os

# Credentials (you can store them as environment variables or hardcode them here)
SENDER_EMAIL = "ayush04coder@gmail.com"
SENDER_PASSWORD = "ibsr ongz bjnc gpiy"  # App-specific password
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993  # Port for Gmail IMAP over SSL

def clean(text):
    # Clean up the email subject or sender text to be more readable
    return "".join(c if c.isalnum() else "_" for c in text)

def receive_emails():
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Select the mailbox you want to check (INBOX in this case)
        mail.select("inbox")

        # Search for all emails (you can adjust the search criteria)
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        # Loop through the emails
        for email_id in email_ids[:5]:  # Limit to the first 5 emails for example
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            # Parse the email content
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")

                    # Print subject and sender's email
                    print(f"Subject: {subject}")
                    print(f"From: {from_}")

                    # Check if the email message is multipart
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            # Get the email body
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode()
                                print(f"Body: {body}")
                    else:
                        # If the email is not multipart
                        body = msg.get_payload(decode=True).decode()
                        print(f"Body: {body}")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
if __name__ == '__main__':
    receive_emails()
