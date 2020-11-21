from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC


def wait_frame_switch(webdriver, by: By, frame: str, timeout: int = 30):
    try:
        Wait(webdriver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((by, frame))
        )
    except TimeoutException as e:
        raise e

def element_exists_by_xpath(webdriver, xpath: str, timeout: int = 10) -> bool:
    try:
        Wait(webdriver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except TimeoutException:
        return False
    return True