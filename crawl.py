from WebScraper.Sitemap import Sitemap
from WebScraper.TQueue import TaskQueue
from WebScraper.ChromeBrowser import ChromeBrowser
from WebScraper.Scraper import Scraper
import json


def main():
    browser = None
    try:
        with open("testlink.json", encoding="utf-8") as f:
           json_sitemap = json.load(f)
        sitemap = Sitemap(json_sitemap.get("_id"), json_sitemap.get("startUrl"), json_sitemap.get("selectors"))
        queue = TaskQueue()
        browser = ChromeBrowser(list(), {})
        scraper = Scraper(queue, sitemap, browser)
        data = scraper.run()
        print(data)
        browser.quit()
    except Exception as e:
        if browser:
            browser.quit()
        raise

if __name__ == '__main__':
    main()

