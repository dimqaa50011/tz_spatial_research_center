import csv

from selenium import webdriver
from selenium_stealth import stealth

from src.parsers.yandex import LinksCollector, Parser


def save(data: list[dict[str, str]]):
    fieldnames = data[0].keys()
    with open("result.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writerow({k: k for k in fieldnames})
        writer.writerows(data)


def main():
    opt = webdriver.ChromeOptions()
    opt.add_argument("--disable-blink-features=AutomationControlled")
    opt.add_argument("--start-maximized")
    opt.add_experimental_option("excludeSwitches", ["enable-automation"])
    opt.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=opt)
    link_collector = LinksCollector(driver)
    parser = Parser(driver)
    try:
        links = link_collector("тверь пятерочка")
        result = parser(links)
        save(result)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
