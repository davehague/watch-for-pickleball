from selenium.webdriver.common.by import By
import time

from selenium_helper import get_selenium_driver


def get_court_reserve_events(url, username, password):
    try:
        driver = get_selenium_driver()
        print("Fetching the webpage content")
        driver.get(url)
        time.sleep(1)
        # driver.set_window_size(1920, 1080)

        username_input = driver.find_element(By.ID, 'UserNameOrEmail')
        username_input.send_keys(username)
        password_input = driver.find_element(By.ID, 'Password')
        password_input.send_keys(password)

        login_button = driver.find_element(By.TAG_NAME, 'button')
        login_button.click()
        time.sleep(1)
        driver.get(url)

        # Wait for the page to load and JavaScript to execute
        print("Waiting for the page to load")
        time.sleep(5)

        print("Extracting the event details")
        new_events = []

        containers = driver.find_elements(By.CLASS_NAME, 'fn-event-item')
        for container in containers:
            title = container.find_element(By.TAG_NAME, 'h4').text
            date_and_time_span = container.find_element(By.CLASS_NAME, 'title-part')
            date_and_time = date_and_time_span.find_element(By.TAG_NAME, 'a').text

            split_values = date_and_time.split(',')
            split_values = [value.strip() for value in split_values]

            # Time is the last one
            times = split_values.pop()
            date = ', '.join(split_values)

            print(f"Found an event: {title} on {date} at {times}")
            new_events.append({'title': title, 'date': date, 'time': times})

    except Exception as e:
        print(f"Error extracting event details: {e}")
        raise e
    finally:
        driver.quit()

    return new_events