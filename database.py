import sqlite3

def create_database(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_title TEXT,
            episode_date TEXT,
            episode_wav_filename TEXT,
            transcript TEXT,
            doc_link TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diarization_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            speaker_id INTEGER NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            duration REAL NOT NULL,
            FOREIGN KEY (episode_id) REFERENCES transcripts(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcription_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            speaker_id INTEGER NOT NULL,
            FOREIGN KEY (episode_id) REFERENCES transcripts(id)
        )
    """)

    conn.commit()
    return conn
