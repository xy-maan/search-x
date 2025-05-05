import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    try:
        resp = requests.get(url, timeout=10)
        # Only process if the content type is text/html
        content_type = resp.headers.get('Content-Type', '')
        if resp.status_code == 200 and 'text/html' in content_type:
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = ' '.join(soup.stripped_strings)
            return text, soup
    except Exception as e:
        print(f"Scrape error for {url}: {e}")
    return '', None

def extract_links(soup, base_url):
    from urllib.parse import urljoin
    links = set()
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        abs_url = urljoin(base_url, href)
        if abs_url.startswith('http') and '#' not in abs_url:
            links.add(abs_url)
    return links
