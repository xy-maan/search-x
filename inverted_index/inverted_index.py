import re
from collections import defaultdict
from crawler.db import Database

def tokenize(text):
    return re.findall(r'\w+', text.lower())

def build_inverted_index(db):
    cursor = db.conn.cursor()
    cursor.execute('SELECT Url, Content FROM Pages')
    inverted_index = defaultdict(set)
    for url, content in cursor.fetchall():
        words = set(tokenize(content))
        for word in words:
            inverted_index[word].add(url)
    return inverted_index

def store_inverted_index(db, index):
    cursor = db.conn.cursor()
    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvertedIndex' AND xtype='U')
        CREATE TABLE InvertedIndex (
            Word NVARCHAR(256),
            Url NVARCHAR(2048)
        )
    ''')
    db.conn.commit()
    cursor.execute('DELETE FROM InvertedIndex')
    db.conn.commit()
    for word, urls in index.items():
        for url in urls:
            cursor.execute('INSERT INTO InvertedIndex (Word, Url) VALUES (?, ?)', (word, url))
    db.conn.commit()

if __name__ == '__main__':
    from crawler.db import Database
    DB_CONFIG = {
        'server': 'TOSHIBA-L50-C\\MSSQLSERVER19',
        'database': 'SearchX',
    }
    db = Database(DB_CONFIG)
    print('Building inverted index...')
    index = build_inverted_index(db)
    print(f'Index built for {len(index)} words. Storing in DB...')
    store_inverted_index(db, index)
    print('Inverted index stored in SQL Server.')
    db.close()
