### https://www.srbija-nekretnine.org/en

from playwright.sync_api import sync_playwright, expect
from tqdm import tqdm
import pandas as pd


class ScrapinghSrbijaNekretnine:
    def __init__(self, url, city, save_to_file: str):
        self.url = url
        self.city = city
        self.save_to_file = save_to_file

    def __connect(self):
        self.page.goto(self.url)
        self.page.wait_for_timeout(1000)
        self.page.get_by_role("button", name="AGREE", exact=True).click()

    def __get_data_from_page(self):
        # container = self.page.locator('#results-container').all_inner_texts()
        container = self.page.locator("#results-container >> .resultRow >> .property >> .property__info")

        results = []
        for c in container.all():
            # Exception handling is needed. There are cards without a price.
            title = c.locator(".property__title").inner_text()
            link = c.locator(".property__title >> a").get_attribute("href").strip()
            price = c.locator(".property__meta >> .property__price").inner_text()
            currency = c.locator(".property__meta >> .property__price__symbol").inner_text()
            params = c.locator(".property__meta >> .property__meta__data").all_inner_texts()
            owner = c.locator(".property__bottom2 >> a").first.get_attribute("href")

            data = {
                "title": title,
                "link": link,
                "price": price,
                "currency": currency,
                "params": params,
                "owner": owner
            }
            results.append(data)

        return results

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            self.page = context.new_page()
            self.__connect()
            self.page.wait_for_timeout(1000)

            for i in tqdm(range(473, 666 + 1)):
                self.page.goto(f"{self.url}?page={i}")
                data = self.__get_data_from_page()
                df = pd.DataFrame.from_dict(data)
                df.to_csv(f"{self.save_to_file}.csv", header=None, mode="a", index_label=False)
                self.page.wait_for_timeout(2000)


if __name__ == '__main__':
    url = 'https://www.srbija-nekretnine.org/en/apartments/for-sale/belgrade'
    ScrapinghSrbijaNekretnine(url=url, city=None, save_to_file='belgrade_ads').run()
