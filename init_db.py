import mysql.connector
from mysql.connector import Error
import sys
import time

def wait_for_mysql(max_attempts=5, delay_seconds=2):
    for attempt in range(max_attempts):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root'
            )
            if connection.is_connected():
                connection.close()
                return True
        except Error:
            if attempt < max_attempts - 1:
                print(f"Attempting to connect to MySQL... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(delay_seconds)
            continue
    return False

def init_database():
    connection = None
    try:
        # Check if MySQL is running
        if not wait_for_mysql():
            print("Error: Could not connect to MySQL server. Please ensure:")
            print("1. MySQL server is installed")
            print("2. MySQL service is running")
            print("3. Credentials (root/root) are correct")
            sys.exit(1)

        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS lost_and_found")
            print("Database 'lost_and_found' created successfully")
            
            # Switch to the created database
            cursor.execute("USE lost_and_found")
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    init_database()