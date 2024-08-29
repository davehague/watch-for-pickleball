import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from retrying import retry

from selenium_helper import get_selenium_driver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_webtrac_events(url):
    try:
        with get_selenium_driver() as driver:
            logging.info("Fetching the webpage content")
            driver.get(url)
            driver.set_window_size(1920, 1080)

            wait = WebDriverWait(driver, 10)

            logging.info("Waiting for the page to load")
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tablecollapsecontainer')))

            logging.info("Extracting the event details")
            new_events = []

            containers = driver.find_elements(By.CLASS_NAME, 'tablecollapsecontainer')
            for container in containers:
                container.click()
                wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'tr')))

                header = container.find_element(By.TAG_NAME, 'h2').find_element(By.TAG_NAME, 'span').text

                rows = container.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) == 0:
                        continue

                    try:
                        description_cell = row.find_element(By.XPATH, './/td[@data-title="Description"]')
                        description = description_cell.find_element(By.TAG_NAME, 'a').text

                        dates_cell = row.find_element(By.XPATH, './/td[@data-title="Dates"]')
                        start_date = dates_cell.find_element(By.TAG_NAME, 'span').text

                        times_cell = row.find_element(By.XPATH, './/td[@data-title="Times"]')
                        start_time = times_cell.find_element(By.TAG_NAME, 'span').text

                        event_title = f"{header} - {description}"
                        logging.info(f"Found an event: {event_title} on {start_date} at {start_time}")
                        new_events.append({'title': event_title, 'date': start_date, 'time': start_time})
                    except NoSuchElementException as e:
                        logging.warning(f"Skipping a row due to missing element: {e}")
                        continue

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
