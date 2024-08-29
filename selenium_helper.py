import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import psutil

logger = logging.getLogger(__name__)

# Global set to store PIDs of Chrome processes we've started
our_chrome_pids = set()


class CustomChromeDriver(webdriver.Chrome):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = psutil.Process(self.service.process.pid)
        our_chrome_pids.add(self.service.process.pid)
        # Add child processes
        for child in self.process.children(recursive=True):
            our_chrome_pids.add(child.pid)

    def quit(self):
        try:
            super().quit()
        except Exception as e:
            logger.error(f"Error while quitting Chrome: {e}")
        finally:
            self.kill_process_tree()

    def kill_process_tree(self):
        try:
            parent = psutil.Process(self.service.process.pid)
            for child in parent.children(recursive=True):
                if child.pid in our_chrome_pids:
                    child.terminate()
                    our_chrome_pids.remove(child.pid)
            parent.terminate()
            our_chrome_pids.remove(parent.pid)
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            logger.error(f"Error while killing Chrome process tree: {e}")


def get_selenium_driver(headless=True):
    logger.info("Setting up the chrome webdriver")
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('./chromedriver.exe')
    driver = CustomChromeDriver(service=service, options=chrome_options)
    return driver


def cleanup_our_chrome_processes():
    for pid in list(our_chrome_pids):
        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)
            our_chrome_pids.remove(pid)
        except psutil.NoSuchProcess:
            our_chrome_pids.remove(pid)
        except psutil.TimeoutExpired:
            process.kill()
            our_chrome_pids.remove(pid)
    logger.info("Cleaned up remaining Chrome processes started by our script")
