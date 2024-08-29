import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from retrying import retry


from selenium_helper import get_selenium_driver

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_court_reserve_events(url, username, password):
    driver = None
    try:
        with get_selenium_driver() as driver:
            logging.info("Fetching the webpage content")
            driver.get(url)

            wait = WebDriverWait(driver, 10)

            username_input = wait.until(EC.presence_of_element_located((By.ID, 'UserNameOrEmail')))
            username_input.send_keys(username)
            password_input = driver.find_element(By.ID, 'Password')
            password_input.send_keys(password)

            login_button = driver.find_element(By.TAG_NAME, 'button')
            login_button.click()

            driver.get(url)

            logging.info("Extracting the event details")
            new_events = []

            containers = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'fn-event-item')))
            for container in containers:
                title = container.find_element(By.TAG_NAME, 'h4').text
                date_and_time_span = container.find_element(By.CLASS_NAME, 'title-part')
                date_and_time = date_and_time_span.find_element(By.TAG_NAME, 'a').text

                split_values = date_and_time.split(',')
                split_values = [value.strip() for value in split_values]

                times = split_values.pop()
                date = ', '.join(split_values)

                logging.info(f"Found an event: {title} on {date} at {times}")
                new_events.append({'title': title, 'date': date, 'time': times})

    except TimeoutException:
        logging.error("Timeout waiting for page elements to load")
        raise
    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    return new_events
