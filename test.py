import sqlitecloud

# Open the connection to SQLite Cloud
conn = sqlitecloud.connect("sqlitecloud://ciyajymohz.g5.sqlite.cloud:8860/FlaskApp?apikey=EAWIMb4h1ab3RO3bgMc14uq7ZQcQhwgqPzzbP6bKyHU")

conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
''')
conn.commit()
