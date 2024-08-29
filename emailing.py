import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def send_email_with_smtp(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        logging.info("Email sent successfully")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise


def send_error_email(error_message):
    logging.error(f"An error occurred: {error_message}")
    subject = "Error in the Pickleball Event Scraper"
    body = f"An error occurred while running the scraper:\n\n{error_message}"

    try:
        send_email_with_smtp(subject, body)
        logging.info("Error notification email sent")
    except Exception as e:
        logging.error(f"Failed to send error notification email: {str(e)}")


def send_email(events, facility_name, url):
    logging.info(f"Sending email notification for new events at {facility_name}")
    subject = f"New Pickleball Events Posted at {facility_name}"
    body = f"The following new events have been discovered at {facility_name}:\n\n"
    body += "\n".join([f"{event['title']} on {event['date']} at {event['time']}" for event in events])
    body += f"\n\nView the events at {url}"

    try:
        send_email_with_smtp(subject, body)
        logging.info(f"New events notification email sent for {facility_name}")
    except Exception as e:
        logging.error(f"Failed to send new events notification email for {facility_name}: {str(e)}")
        raise
