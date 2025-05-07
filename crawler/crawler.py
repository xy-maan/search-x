import time
from db import Database
from scraper import scrape_url, extract_links

# SQL Server connection settings
DB_CONFIG = {
    'server': 'TOSHIBA-L50-C\\MSSQLSERVER19',
    'database': 'SearchX',
}

class Crawler:
    def __init__(self, db, max_pages=2000, delay=0.5):
        self.db = db
        self.max_pages = max_pages  # max per seed
        self.delay = delay
        self.visited = set()

    def crawl_seed(self, seed):
        queue = [seed]
        local_visited = set()
        count = 0
        while queue and count < self.max_pages:
            url = queue.pop(0)
            if url in self.visited or url in local_visited:
                continue
            print(f"Crawling: {url}")
            text, soup = scrape_url(url)
            if text:
                self.db.save_page(url, text)
                count += 1
            self.visited.add(url)
            local_visited.add(url)
            if soup:
                for link in extract_links(soup, url):
                    if link not in self.visited and link not in local_visited and len(queue) < self.max_pages:
                        queue.append(link)
            time.sleep(self.delay)
        print(f"Seed '{seed}' finished. Pages crawled: {count}")

    def crawl(self, seeds):
        for seed in seeds:
            self.crawl_seed(seed)
        print(f"Crawling finished for all seeds.")

if __name__ == '__main__':
    db = Database(DB_CONFIG)
    seeds = [
        'https://www.geeksforgeeks.org/',
        'https://www.w3schools.com/',
    ]
    crawler = Crawler(db, max_pages=20)
    crawler.crawl(seeds)
    db.close()
