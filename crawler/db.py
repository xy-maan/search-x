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
