import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from retrying import retry

from selenium_helper import get_selenium_driver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_active_community_events(url):
    try:
        with get_selenium_driver() as driver:
            logging.info("Fetching the webpage content")
            driver.get(url)

            wait = WebDriverWait(driver, 10)

            logging.info("Waiting for the page to load")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'activity-card-info')))

            logging.info("Extracting the event details")
            events = driver.find_elements(By.CLASS_NAME, 'activity-card-info')
            new_events = []

            for event in events:
                try:
                    # Extract event title
                    event_title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.activity-card-info__name > h3')))
                    event_title = event_title_element.text.strip() if event_title_element else 'No Title'

                    # Extract event date
                    event_date_element = event.find_element(By.CSS_SELECTOR, '.activity-card-info__dateRange > span')
                    event_date = event_date_element.text.strip() if event_date_element else 'No Date'

                    # Extract event time
                    try:
                        event_time_element = event.find_element(By.CSS_SELECTOR, '.activity-card-info__timeRange > span')
                        event_time = event_time_element.text.strip() if event_time_element else 'No Time'
                    except NoSuchElementException:
                        event_time = 'No Time'  # Fallback if time element is not found

                    # Append the event details
                    logging.info(f"Found an event: {event_title} on {event_date} at {event_time}")
                    new_events.append({'title': event_title, 'date': event_date, 'time': event_time})

                except Exception as e:
                    logging.error(f"Error extracting event details: {e}")
                    continue  # Continue with the next event instead of raising an exception

        return new_events
    except TimeoutException:
        logging.error("Timeout waiting for page elements to load")
        raise
    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
