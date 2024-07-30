from selenium.webdriver.common.by import By
import time

from selenium_helper import get_selenium_driver


def get_active_community_events(url):
    try:
        driver = get_selenium_driver()
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
    except Exception as e:
        print(f"Error fetching webpage content: {e}")
    finally:
        driver.quit()