import os
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


load_dotenv()
URL = os.getenv('URL')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
EVENTS_FILE = 'events.json'
PICKLEBALL_LOCATION = os.getenv('PICKLEBALL_LOCATION')


# Setup Selenium WebDriver
def setup_driver():
    print ("Setting up the chrome webdriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# Fetch and parse the webpage content using Selenium
def fetch_events():
    driver = setup_driver()
    print ("Fetching the webpage content")
    driver.get(URL)

    # Wait for the page to load and JavaScript to execute
    print ("Waiting for the page to load")
    time.sleep(10)  # Adjust the sleep time as needed

    print ("Extracting the event details")
    events = driver.find_elements(By.CLASS_NAME, 'activity-card-info')
    new_events = []

    for event in events:
        try:
            # Extract event title
            event_title_element = event.find_element(By.CSS_SELECTOR, '.activity-card-info__name > h3')
            event_title = event_title_element.text.strip() if event_title_element else 'No Title'

            # Extract event date
            event_date_element = event.find_element(By.CSS_SELECTOR, '.activity-card-info__dateRange > span')
            event_date = event_date_element.text.strip() if event_date_element else 'No Date'

            # Extract event time
            try:
                event_time_element = event.find_element(By.CSS_SELECTOR, '.activity-card-info__timeRange > span')
                event_time = event_time_element.text.strip() if event_time_element else 'No Time'
            except:
                event_time = 'No Time'  # Fallback if time element is not found

            # Append the event details
            print(f"Found an event: {event_title} on {event_date} at {event_time}")
            new_events.append({'title': event_title, 'date': event_date, 'time': event_time})

        except Exception as e:
            print(f"Error extracting event details: {e}")

    driver.quit()
    return new_events


# Compare new events with previously stored events
def check_for_new_events():
    new_events = fetch_events()

    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as file:
            stored_events = json.load(file)
    else:
        stored_events = []

    stored_event_details = {(event['title'], event['date'], event['time']) for event in stored_events}
    new_unique_events = [event for event in new_events if
                         (event['title'], event['date'], event['time']) not in stored_event_details]

    if new_unique_events:
        send_email(new_unique_events)
        with open(EVENTS_FILE, 'w') as file:
            json.dump(stored_events + new_unique_events, file)
    else:
        print ("No new events found, skipping email notification")


# Send an email notification
def send_email(events):
    print("Found new events, sending an email notification")
    subject = "New Pickleball Events Posted at " + PICKLEBALL_LOCATION
    body = "\n".join([f"{event['title']} on {event['date']} at {event['time']}" for event in events])

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


if __name__ == '__main__':
    check_for_new_events()
