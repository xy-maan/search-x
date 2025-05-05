import time
from db import Database
from scraper import scrape_url, extract_links

# SQL Server connection settings
DB_CONFIG = {
    'server': 'TOSHIBA-L50-C\\MSSQLSERVER19',
    'database': 'SearchX',
}

class Crawler:
    def __init__(self, db, max_pages=100000, delay=0.5):
        self.db = db
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
        self.queue = []

    def add_seeds(self, seeds):
        for url in seeds:
            if url not in self.visited:
                self.queue.append(url)

    def crawl(self):
        count = 0
        while self.queue and count < self.max_pages:
            url = self.queue.pop(0)
            if url in self.visited:
                continue
            print(f"Crawling: {url}")
            text, soup = scrape_url(url)
            if text:
                self.db.save_page(url, text)
                count += 1
            self.visited.add(url)
            if soup:
                for link in extract_links(soup, url):
                    if link not in self.visited and len(self.queue) < self.max_pages:
                        self.queue.append(link)
            time.sleep(self.delay)
        print(f"Crawling finished. Total pages crawled: {count}")

if __name__ == '__main__':
    db = Database(DB_CONFIG)
    seeds = [
        'https://www.geeksforgeeks.org/',
    ]
    crawler = Crawler(db, max_pages=1000)
    crawler.add_seeds(seeds)
    crawler.crawl()
    db.close()
