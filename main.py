import os
from dotenv import load_dotenv

from emailing import send_email
from platforms.active_communities import get_active_community_events
from selenium_helper import get_selenium_driver
from persistent_data import PersistentData


def get_unique_new_events(scraped_events, stored_event_details):
    new_unique_events = [event for event in scraped_events if
                         (event['title'], event['date'], event['time']) not in stored_event_details]

    return new_unique_events


if __name__ == '__main__':
    load_dotenv()
    db = PersistentData()

    facilities = db.get_facilities()
    for facility in facilities:
        platform = facility['platform']

        if platform == 'active_communities':
            facility_id = facility['id']
            url = facility['url']
            driver = get_selenium_driver()
            new_events = get_active_community_events(driver, url)

            for event in new_events:
                event['facilityId'] = facility_id

            stored_events, stored_event_details = db.get_stored_events()
            unique_new_events = get_unique_new_events(new_events, stored_event_details)

            if unique_new_events:
                send_email(unique_new_events)
                db.insert_events(unique_new_events)
            else:
                print("No new events found, skipping email notification")

            driver.quit()
            db.close()