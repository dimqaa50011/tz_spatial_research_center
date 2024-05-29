import csv

from selenium import webdriver

from src.parsers.yandex import YandexMapsCollector, Parser


def save(data: list[dict[str, str]]):
    fieldnames = data[0].keys()
    with open("result.csv", "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writerow({k: k for k in fieldnames})
        writer.writerows(data)

def main():
    driver = webdriver.Chrome()
    ymp = YandexMapsCollector(driver)
    parser = Parser(driver)
    try:
        links = ymp("тверь пятерочка")
        result = parser(links)
        save(result)
    finally:
        driver.quit()
    
if __name__ == "__main__":
    main()