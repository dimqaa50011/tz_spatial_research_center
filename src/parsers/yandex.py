import random
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


class YandexMapsCollector:
    def __init__(self, driver: webdriver.Chrome | webdriver.Firefox) -> None:
        self._driver = driver
        self._last_element = None

    def _random_delay(self):
        return random.randint(1, 2)

    def __call__(self, search_text: str):
        self._driver.get("https://yandex.ru/maps")
        el = self._driver.find_element(By.XPATH, "//form//input")
        time.sleep(self._random_delay())
        el.send_keys(search_text, Keys.ENTER)
        time.sleep(self._random_delay())
        return self._get_full_links()

    def _get_full_links(self):
        _list_items = []
        while True:
            ul = self._driver.find_element(By.TAG_NAME, "ul")
            _list_items += self._parse_links(ul.find_elements(By.TAG_NAME, "li"))
            blocks = ul.find_elements(By.TAG_NAME, "div")
            ActionChains(self._driver).scroll_to_element(blocks[-1]).perform()
            el = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li:last-child"))
            )

            if el == self._last_element:
                break
            time.sleep(self._random_delay())

        return _list_items

    def _parse_links(self, elements: list[WebElement]):
        res: list[str | None] = []
        for element in elements:
            try:
                element.find_element(By.CLASS_NAME, "_closed")
            except NoSuchElementException:

                res.append(element.find_element(By.TAG_NAME, "a").get_attribute("href"))
            finally:
                self._last_element = element

        return res
