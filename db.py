import sqlite3
import os

def get_db_connection():
    return sqlite3.connect('berkay_bot.db')

def init_database():
    """Veritabanını ve tabloları oluşturur"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Messages tablosunu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tests tablosunu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("Veritabanı ve tablolar başarıyla oluşturuldu!")
        
    except Exception as e:
        print(f"Veritabanı oluşturma hatası: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_database()
