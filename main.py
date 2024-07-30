from dotenv import load_dotenv

from emailing import send_email, send_error_email
from platforms.active_communities import get_active_community_events
from platforms.court_reserve import get_court_reserve_events
from platforms.vermont_systems_webtrac import get_webtrac_events
from persistent_data import PersistentData


def get_unique_new_events(scraped_events, stored_event_details):
    stored_event_tuples = {(event[0], event[1], event[2], event[3]) for event in stored_event_details}
    new_unique_events = [event for event in scraped_events if
                         (event['title'], event['date'], event['time'], event['facilityId']) not in stored_event_tuples]

    return new_unique_events


def check_for_unique_events(new_events, db):
    for event in new_events:
        event['facilityId'] = facility['id']

    stored_events, stored_event_details = db.get_stored_events()
    return get_unique_new_events(new_events, stored_event_details)


if __name__ == '__main__':
    load_dotenv()
    try:
        db = PersistentData()
        facilities = db.get_facilities()
        for facility in facilities:
            platform = facility['platform']

            new_events = []
            if platform == 'active_communities':
                print(f"Fetching events from {facility['name']}")
                new_events = get_active_community_events(facility['url'])
            if platform == 'vermont_systems_webtrac':
                print (f"Fetching events from {facility['name']}")
                new_events = get_webtrac_events(facility['url'])
            if platform == 'court_reserve':
                print(f"Fetching events from {facility['name']}")
                new_events = get_court_reserve_events(facility['url'], facility['username'], facility['password'])

            unique_new_events = check_for_unique_events(new_events, db)

            if unique_new_events:
                send_email(unique_new_events, facility['name'], facility['url'])
                db.insert_events(unique_new_events)
            else:
                print("No new events found, skipping email notification")

    except Exception as e:
        send_error_email(e)
    finally:
        db.close()
