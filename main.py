import os
import json

from dotenv import load_dotenv

from emailing import send_email
from platforms.active_communities import get_active_community_events
from selenium_helper import get_selenium_driver


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

    driver = get_selenium_driver()
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
