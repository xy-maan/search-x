from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import traceback

def scrape_url(url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    try:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'head', 'meta', 'noscript']):
            tag.decompose()
        hidden_tags = []
        for tag in soup.find_all(style=True):
            style_attr = tag.get('style')
            if style_attr and isinstance(style_attr, str):
                style = style_attr.lower()
                if 'display:none' in style or 'visibility:hidden' in style:
                    hidden_tags.append(tag)
        for tag in hidden_tags:
            tag.decompose()
        for tag in soup(['img', 'video', 'audio', 'embed', 'object', 'iframe', 'source', 'track', 'canvas']):
            tag.decompose()
        text = ' '.join(soup.stripped_strings)
        return text, soup
    except Exception as e:
        print(f'Selenium scrape error for {url}: {e}')
        traceback.print_exc()
    finally:
        driver.quit()
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
