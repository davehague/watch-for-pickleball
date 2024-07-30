from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')


def send_email(events, facility_name, url):
    print("Found new events, sending an email notification")
    subject = "New Pickleball Events Posted at " + facility_name
    body = f"The following new events have been discovered at {facility_name}:\n\n"
    body += "\n".join([f"{event['title']} on {event['date']} at {event['time']}" for event in events])
    body += f"\n\nView the events at {url}"

    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL, RECIPIENT_EMAIL, text)
    print ("Email sent successfully")
    server.quit()