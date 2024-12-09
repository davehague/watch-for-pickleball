import logging
from dotenv import load_dotenv

from emailing import send_email, send_error_email
from platforms.active_communities import get_active_community_events
from platforms.court_reserve import get_court_reserve_events
from platforms.vermont_systems_webtrac import get_webtrac_events
from persistent_data import PersistentData
from selenium_helper import cleanup_our_chrome_processes
from datetime import datetime


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


def check_schedule(schedule: str) -> bool:
    # Schedule string follows the following formats:
    # Example: "Mon AM, Wed AM, Fri PM, Sun AM, Sun PM" (runs Monday morning, Wednesday morning, Friday evening, and both slots on Sunday).

    if not schedule:
        return True

    # Normalize the schedule string
    normalized_schedule = schedule.strip().lower()
    schedule_items = [item.strip() for item in normalized_schedule.split(",")]

    # Get the current day and time
    now = datetime.now()
    current_day = now.strftime("%a").lower()  # Short weekday name (e.g., mon, tue)
    current_hour = now.hour
    is_am_slot = current_hour < 12

    for item in schedule_items:
        if not item:
            continue  # Skip empty items
        parts = item.split()
        day = parts[0] if len(parts) > 0 else ""
        slots = parts[1:] if len(parts) > 1 else []

        if day == current_day:
            if (is_am_slot and "am" in slots) or (not is_am_slot and "pm" in slots):
                return True

    return False


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

                should_check_for_events = check_schedule(facility['schedule'])
                if not should_check_for_events:
                    print(f"Skipping {facility['name']} because it has a schedule and is not scheduled to run at this time")
                    continue

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
