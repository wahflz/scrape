import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from . import APP_BIN

class Browser:
    def __init__(self, headless: bool = True):
        self.browser = None
        self.headless = headless

    def __enter__(self):
        self.browser = webdriver.Firefox(
            service=Service(APP_BIN),
            options=self.configure_firefox_options()
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.browser:
            self.browser.quit()
    
    def get(self, url):
        self.browser.get(url)
    
    def close(self):
        self.browser.quit()

    def find_element(self, by: By, value: str, *, strict: bool = True) -> WebElement|None:
        try:
            return self.browser.find_element(by, value)
        except NoSuchElementException:
            if strict:
                raise
    
    def find_element_by_xpath(self, value: str) -> WebElement|None:
         return self.find_element(By.XPATH, value, strict=False)

    def find_element_by_css(self, value: str) -> WebElement|None:
         return self.find_element(By.CSS_SELECTOR, value, strict=False)

    def find_elements_by_class(self, value: str) -> list:
        return self.browser.find_elements(By.CLASS_NAME, value)

    def wait_for_element(self, by, value: str, timeout: int = 10, *, strict: bool = True) -> WebElement|None:
        element = None

        try:
            element = WebDriverWait(self.browser, timeout).\
                until(lambda x: x.find_element(by, value)) 
        except TimeoutException:
            if strict:
                raise

        return element

    def wait_for_element_by_xpath(self, value: str, timeout: int = 10, *, strict: bool = True) -> WebElement|None:
        return self.wait_for_element(By.XPATH, value, timeout, strict=strict)

    def wait_for_element_by_css(self, value: str, timeout: int = 10, *, strict: bool = True) -> WebElement|None:
        return self.wait_for_element(By.CSS_SELECTOR, value, timeout, strict=strict)

    def wait_until_stale(self, element: WebElement, timeout: int = 10, *, strict: bool = True):
        try:
            WebDriverWait(self.browser, timeout).until(lambda x: EC.staleness_of(element)) # poop
        except TimeoutException:
            if strict:
                raise

    # def wait_until_hidden(self, element: WebElement, timeout: int = 10, *, strict: bool = True):
    #     try:
    #         WebDriverWait(self.browser, timeout, (No)).until_not(lambda x: element.is_displayed()) 
    #     except TimeoutException:
    #         if strict:
    #             raise

    def insert_text(self, element, text, min_delay=0.05, max_delay=0.2):
        for char in text:
            element.send_keys(char)
            self.jitter(min_delay, max_delay)

    def clear_form(self, by: By, value: str):
        try:
            submit = self.wait_for_element(by, value)
            self.wait_until_stale(submit)
            self.jitter()
            self.move_pointer_to_element(submit)
        except TimeoutError:
            return
        
        # wait until gone...

    def clear_form_by_xpath(self, value: str):
        self.clear_form(By.XPATH, value)

    def clear_form_by_css(self, value: str):
        self.clear_form(By.CSS_SELECTOR, value)

    def move_pointer_to_element(self, element: WebElement, duration: int = 250):
        action = ActionChains(self.browser, duration)
        action.move_to_element(element).perform()
        action.click().perform()

    def configure_firefox_options(self):
        options = webdriver.FirefoxOptions()
        options.set_preference('permissions.default.geo', 1) # enable location for all, easiest way
        if self.headless:
                options.add_argument('--headless')

        return options

    @staticmethod
    def find_child_by_xpath(element: WebElement, value: str) -> WebElement:
        return element.find_element(By.XPATH, value)

    @staticmethod
    def jitter(min_delay=0.1, max_delay=1.0):
        time.sleep(random.uniform(min_delay, max_delay))
