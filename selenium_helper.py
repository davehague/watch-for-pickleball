from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_selenium_driver(headless=True):
    print ("Setting up the chrome webdriver")
    chrome_options = Options()

    if(headless):
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver