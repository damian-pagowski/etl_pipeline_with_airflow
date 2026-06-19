import psycopg2
import sys

def verify_database_connection():
    """
    Attempts to connect to the Postgre to verify credentials   
    """    
    db_credentials = {
        "host": "localhost",
        "dbname": "damian",
        "user": "postgres",
        "port": 5432,
        "connect_timeout": 5  
    }
    
    conn = None
    try:
        conn = psycopg2.connect(**db_credentials)
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("\n[SUCCESS] Connected to DB successfully!")
        print(f"Database Server Version: {db_version[0]}\n")
        
        cursor.close()
        return True

    except psycopg2.OperationalError as e:
        print("\n[ERROR] Connection test failed.")
        print(f"\nError Log:\n{e}\n")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}\n")
        return False
        
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    connection_alive = verify_database_connection()
    
    if not connection_alive:
        print("Failure.")
