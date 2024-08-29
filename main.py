import logging
from dotenv import load_dotenv

from emailing import send_email, send_error_email
from platforms.active_communities import get_active_community_events
from platforms.court_reserve import get_court_reserve_events
from platforms.vermont_systems_webtrac import get_webtrac_events
from persistent_data import PersistentData
from selenium_helper import cleanup_our_chrome_processes


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_unique_new_events(scraped_events, stored_event_details):
    stored_event_tuples = {(event[0], event[1], event[2], event[3]) for event in stored_event_details}
    new_unique_events = [event for event in scraped_events if
                         (event['title'], event['date'], event['time'], event['facilityId']) not in stored_event_tuples]
    return new_unique_events


def check_for_unique_events(new_events, db, facility_id):
    for event in new_events:
        event['facilityId'] = facility_id

    stored_events, stored_event_details = db.get_stored_events()
    return get_unique_new_events(new_events, stored_event_details)


def main():
    load_dotenv()
    logging.info("Starting Pickleball Event Scraper")
    db = None
    try:
        with PersistentData() as db:
            facilities = db.get_facilities()
            for facility in facilities:
                platform = facility['platform']
                logging.info(f"Fetching events from {facility['name']} ({platform})")

                new_events = []
                try:
                    if platform == 'active_communities':
                        new_events = get_active_community_events(facility['url'])
                    elif platform == 'vermont_systems_webtrac':
                        new_events = get_webtrac_events(facility['url'])
                    elif platform == 'court_reserve':
                        new_events = get_court_reserve_events(facility['url'], facility['username'], facility['password'])
                    else:
                        logging.warning(f"Unknown platform: {platform}")
                        continue

                    unique_new_events = check_for_unique_events(new_events, db, facility['id'])

                    if unique_new_events:
                        logging.info(f"Found {len(unique_new_events)} new events for {facility['name']}")
                        send_email(unique_new_events, facility['name'], facility['url'])
                        db.insert_events(unique_new_events)
                    else:
                        logging.info(f"No new events found for {facility['name']}")

                except Exception as e:
                    logging.error(f"Error processing {facility['name']}: {str(e)}")
                    send_error_email(f"Error processing {facility['name']}: {str(e)}")

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        send_error_email(f"Unexpected error in main script: {str(e)}")
    finally:
        cleanup_our_chrome_processes()


if __name__ == '__main__':
    main()
