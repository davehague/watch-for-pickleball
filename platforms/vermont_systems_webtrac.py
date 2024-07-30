from selenium.webdriver.common.by import By
import time

from selenium_helper import get_selenium_driver


def get_webtrac_events(url):
    driver = get_selenium_driver()
    print("Fetching the webpage content")
    driver.get(url)
    driver.set_window_size(1920, 1080)

    # Wait for the page to load and JavaScript to execute
    print("Waiting for the page to load")
    time.sleep(5)  # Adjust the sleep time as needed

    print("Extracting the event details")
    new_events = []
    try:
        containers = driver.find_elements(By.CLASS_NAME, 'tablecollapsecontainer')
        for container in containers:
            container.click()
            time.sleep(1)

            header = container.find_element(By.TAG_NAME, 'h2').find_element(By.TAG_NAME, 'span').text

            rows = container.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) == 0:
                    continue

                description_cell = row.find_element(By.XPATH, './/td[@data-title="Description"]')
                description = description_cell.find_element(By.TAG_NAME, 'a').text

                dates_cell = row.find_element(By.XPATH, './/td[@data-title="Dates"]')
                start_date = dates_cell.find_element(By.TAG_NAME, 'span').text

                times_cell = row.find_element(By.XPATH, './/td[@data-title="Times"]')
                start_time = times_cell.find_element(By.TAG_NAME, 'span').text

                event_title = f"{header} - {description}"
                print(f"Found an event: {event_title} on {start_date} at {start_time}")
                new_events.append({'title': event_title, 'date': start_date, 'time': start_time})

    except Exception as e:
        print(f"Error extracting event details: {e}")
    finally:
        driver.quit()

    return new_events