import psycopg2
from psycopg2.extras import execute_values

def load_data_to_postgres(analyzed_records):
    """
    Connects to the database and inserts rows
    """
    print(f"Starting data Load: {len(analyzed_records)} records...")
    
    # database configuration
    db_credentials = {
        "host": "localhost",
        "dbname": "damian",
        "user": "postgres",
        "port": 5432,
        "connect_timeout": 5  
    }
    
    try:
        conn = psycopg2.connect(**db_credentials)
        cursor = conn.cursor()
    except Exception as e:
        print(f"[ERROR] connection failed: {e}")
        raise e

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_sentiment_analysis (
            id SERIAL PRIMARY KEY,
            date DATE,
            headline TEXT,
            gold_close_price NUMERIC(10, 2),
            gold_volume BIGINT,
            sentiment_score NUMERIC(4, 3),
            sentiment_label VARCHAR(10),
            inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, headline)
        )
    """)
    
    insert_query = """
        INSERT INTO gold_sentiment_analysis 
        (date, headline, gold_close_price, gold_volume, sentiment_score, sentiment_label)
        VALUES %s
        ON CONFLICT (date, headline) DO NOTHING
    """
    
    data_tuples = [
        (
            row['date'],
            row['headline'],
            row['gold_close_price'],
            row['gold_volume'],
            row['sentiment_score'],
            row['sentiment_label']
        )
        for row in analyzed_records
    ]
    
    try:
        execute_values(cursor, insert_query, data_tuples)
        conn.commit()
        print("database updated successfully.")
    except Exception as e:
        conn.rollback()
        print(f"insert transaction failed: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()