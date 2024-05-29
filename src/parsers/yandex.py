import random
import time
from typing import Any, Sequence

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


class Parser:
    def __init__(
        self,
        driver: webdriver.Chrome,
    ) -> None:
        self._driver = driver

    def __call__(self, links: list[str]):
        result_list = []

        for link in links:
            self._driver.get(link)
            try:
                item = self._driver.find_element(By.CLASS_NAME, "sidebar-container")
                result_list.append(self._get_info(item))

            except NoSuchElementException:
                print()

        return result_list

    def _get_info(self, item: WebElement):
        item_info: dict[str, Sequence[Any]] = {}
        item_info["title"] = item.find_element(By.TAG_NAME, "h1").text
        item_info["type"] = (
            item.find_element(By.CLASS_NAME, "breadcrumbs-view")
            .find_elements(By.TAG_NAME, "a")[-1]
            .text
        )

        address_block, contacts_block, schedule_block = item.find_elements(
            By.CLASS_NAME, "business-contacts-view__block"
        )

        item_info["address"] = address_block.find_element(
            By.CLASS_NAME, "business-contacts-view__address-link"
        ).text

        item_info["contacts"] = [
            el.find_element(By.TAG_NAME, "span").text
            for el in contacts_block.find_elements(By.CLASS_NAME, "card-phones-view")
        ]
        item_info["site"] = contacts_block.find_element(
            By.CLASS_NAME, "business-urls-view__link"
        ).get_attribute("href")

        schedule_block = schedule_block.find_element(
            By.CLASS_NAME, "card-dropdown-view"
        )
        schedule_block.click()
        ac = ActionChains(self._driver).scroll_to_element(schedule_block)
        ac.perform()
        schedule_list = schedule_block.find_element(
            By.CLASS_NAME, "card-dropdown-view__content"
        ).find_elements(By.CLASS_NAME, "card-feature-view__content")
        schedule_items = []
        for item in schedule_list:
            try:
                schedule_element = WebDriverWait(
                    self._driver,
                    10,
                ).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "business-working-intervals-view__item")
                    )
                )
                ac.scroll_to_element(item).perform()
                week_day = schedule_element.find_element(
                    By.CLASS_NAME, "business-working-intervals-view__day"
                ).text
                schedule = schedule_element.find_element(
                    By.CLASS_NAME, "business-working-intervals-view__interval"
                ).text
            except NoSuchElementException:
                continue
            schedule_items.append(f"{week_day} - {schedule}")

        item_info["schedule"] = "\n".join(schedule_items)

        lat, long = (
            self._driver.find_element(
                By.CLASS_NAME, "search-placemark-view"
            ).get_attribute("data-coordinates")
        ).split(",")
        item_info["lat"] = lat
        item_info["long"] = long

        return item_info
