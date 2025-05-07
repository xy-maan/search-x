import pyodbc
from collections import defaultdict

DB_CONFIG = {
    'server': 'TOSHIBA-L50-C\\MSSQLSERVER19',
    'database': 'SearchX',
}

# Connect to the database
def get_db_conn():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

def fetch_pages_and_links(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT Id, Url, Content FROM Pages')
    id_url = {}
    url_id = {}
    links = defaultdict(set)
    for row in cursor.fetchall():
        page_id, url, content = row
        id_url[page_id] = url
        url_id[url] = page_id
    # Build link graph
    cursor.execute('SELECT Id, Url, Content FROM Pages')
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    for row in cursor.fetchall():
        page_id, url, content = row
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            abs_url = urljoin(url, href)
            if abs_url in url_id:
                links[page_id].add(url_id[abs_url])
    return id_url, links

def compute_pagerank(links, num_pages, d=0.85, max_iter=30, tol=1e-6):
    pr = {pid: 1.0 / num_pages for pid in links}
    for _ in range(max_iter):
        new_pr = {}
        for pid in links:
            rank_sum = 0.0
            for other, outlinks in links.items():
                if pid in outlinks and len(outlinks) > 0:
                    rank_sum += pr[other] / len(outlinks)
            new_pr[pid] = (1 - d) / num_pages + d * rank_sum
        # Check convergence
        if all(abs(new_pr[pid] - pr[pid]) < tol for pid in pr):
            break
        pr = new_pr
    return pr

def store_pagerank(conn, pagerank):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM PageRank')
    for pid, score in pagerank.items():
        cursor.execute('INSERT INTO PageRank (page_id, score) VALUES (?, ?)', (pid, float(score)))
    conn.commit()

def main():
    conn = get_db_conn()
    id_url, links = fetch_pages_and_links(conn)
    if not links:
        print('No links found.')
        return
    num_pages = len(id_url)
    pagerank = compute_pagerank(links, num_pages)
    store_pagerank(conn, pagerank)
    print('PageRank scores computed and stored.')
    conn.close()

if __name__ == '__main__':
    main()
