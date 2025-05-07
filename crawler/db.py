import pyodbc

class Database:
    def __init__(self, config):
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"Trusted_Connection=yes;"
        )
        self.conn = pyodbc.connect(self.conn_str)
        self.ensure_table()
        self.ensure_inverted_index_tables()

    def ensure_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Pages' AND xtype='U')
            CREATE TABLE Pages (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                Url NVARCHAR(2048) UNIQUE,
                Content NVARCHAR(MAX)
            )
        ''')
        self.conn.commit()

    def ensure_inverted_index_tables(self):
        cursor = self.conn.cursor()
        # InvertedIndex table with tf
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InvertedIndex' AND xtype='U')
            CREATE TABLE InvertedIndex (
                word NVARCHAR(255) NOT NULL,
                page_id INT NOT NULL,
                tf INT NOT NULL,
                PRIMARY KEY (word, page_id),
                FOREIGN KEY (page_id) REFERENCES Pages(Id)
            )
        ''')
        # Words table with df
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Words' AND xtype='U')
            CREATE TABLE Words (
                word NVARCHAR(255) PRIMARY KEY,
                df INT NOT NULL
            )
        ''')
        # PageRank table
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PageRank' AND xtype='U')
            CREATE TABLE PageRank (
                page_id INT PRIMARY KEY,
                score FLOAT NOT NULL,
                FOREIGN KEY (page_id) REFERENCES Pages(Id)
            )
        ''')
        self.conn.commit()

    def save_page(self, url, content):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO Pages (Url, Content) VALUES (?, ?)', (url, content))
            self.conn.commit()
        except Exception as e:
            if 'UNIQUE' not in str(e):
                print(f"DB error for {url}: {e}")

    def close(self):
        self.conn.close()
