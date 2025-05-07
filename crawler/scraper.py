import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def scrape_url(url):
    try:
        resp = requests.get(url, timeout=10)
        content_type = resp.headers.get('Content-Type', '')
        if resp.status_code == 200 and re.search(r'text/html|application/xhtml\+xml', content_type):
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Remove media/embedded content and non-text tags
            for tag in soup(['img', 'video', 'audio', 'embed', 'object', 'iframe',
                            'source', 'track', 'canvas', 'script', 'style']):
                tag.decompose()
            # Extract clean text
            text = soup.get_text(separator=' ', strip=True)
            return text, soup
        else:
            print(f"Non-HTML or bad status for {url}: {resp.status_code}, {content_type}")
    except Exception as e:
        print(f"Scrape error for {url}: {e}")
    return '', None

def extract_links(soup, base_url):
    links = set()
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        # Clean URL fragments and normalize
        abs_url = urljoin(base_url, href.split('#')[0])
        if abs_url.startswith('http'):
            links.add(abs_url)
    return links