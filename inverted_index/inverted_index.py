import re
from collections import defaultdict
from crawler.db import Database
from bs4 import BeautifulSoup  # Add this import

# Use a more advanced stop word list (from NLTK)
STOP_WORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
])

def simple_stem(word):
    # Very basic stemming: remove common suffixes
    for suffix in ['ing', 'ed', 'ly', 'es', 's', 'ment']:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word

def tokenize(text):
    words = re.findall(r'\w+', text.lower())
    # Remove stop words and apply stemming
    return [simple_stem(w) for w in words if w not in STOP_WORDS]

def extract_visible_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Remove script, style, head, meta, and [hidden] elements
    for tag in soup(['script', 'style', 'head', 'meta', '[hidden]']):
        tag.decompose()
    # Remove elements hidden by CSS (display:none, visibility:hidden)
    for tag in soup.find_all(style=True):
        style = tag['style'].lower()
        if 'display:none' in style or 'visibility:hidden' in style:
            tag.decompose()
    # Only join visible strings
    return ' '.join(soup.stripped_strings)

def build_inverted_index(db):
    cursor = db.conn.cursor()
    cursor.execute('SELECT Id, Content FROM Pages')
    inverted_index = defaultdict(lambda: defaultdict(int))  # word -> page_id -> tf
    df_counter = defaultdict(set)  # word -> set(page_id)
    for page_id, content in cursor.fetchall():
        visible_text = extract_visible_text(content)
        words = tokenize(visible_text)
        for word in words:
            inverted_index[word][page_id] += 1
            df_counter[word].add(page_id)
    # Compute df for each word
    word_df = {word: len(page_ids) for word, page_ids in df_counter.items()}
    return inverted_index, word_df

def store_inverted_index(db, index, word_df):
    cursor = db.conn.cursor()
    cursor.execute('DELETE FROM InvertedIndex')
    cursor.execute('DELETE FROM Words')
    db.conn.commit()
    for word, page_dict in index.items():
        for page_id, tf in page_dict.items():
            cursor.execute('INSERT INTO InvertedIndex (word, page_id, tf) VALUES (?, ?, ?)', (word, page_id, tf))
    for word, df in word_df.items():
        cursor.execute('INSERT INTO Words (word, df) VALUES (?, ?)', (word, df))
    db.conn.commit()

if __name__ == '__main__':
    from crawler.db import Database
    DB_CONFIG = {
        'server': 'TOSHIBA-L50-C\\MSSQLSERVER19',
        'database': 'SearchX',
    }
    db = Database(DB_CONFIG)
    print('Building inverted index...')
    index, word_df = build_inverted_index(db)
    print(f'Index built for {len(index)} words. Storing in DB...')
    store_inverted_index(db, index, word_df)
    print('Inverted index stored in SQL Server.')
    db.close()
