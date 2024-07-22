import os
import json
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from emailing import send_email

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
def get_active_community_events(driver, url):
    print ("Fetching the webpage content")
    driver.get(url)

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

    return new_events


def get_stored_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as file:
            stored_events = json.load(file)
    else:
        stored_events = []

    stored_event_details = {(event['title'], event['date'], event['time']) for event in stored_events}
    return stored_events, stored_event_details


def get_unique_new_events(scraped_events, stored_event_details):
    new_unique_events = [event for event in scraped_events if
                         (event['title'], event['date'], event['time']) not in stored_event_details]

    return new_unique_events


if __name__ == '__main__':
    load_dotenv()
    URL = os.getenv('URL')
    EVENTS_FILE = 'events.json'

    driver = setup_driver()
    new_events = get_active_community_events(driver, URL)
    stored_events, stored_event_details = get_stored_events()
    unique_new_events = get_unique_new_events(new_events, stored_event_details)

    if unique_new_events:
        send_email(unique_new_events)
        with open(EVENTS_FILE, 'w') as file:
            json.dump(stored_events + unique_new_events, file, indent=4)
    else:
        print("No new events found, skipping email notification")
    driver.quit()
