#!/usr/bin/env python3
import sqlite3
import mysql.connector
from mysql.connector import Error

def import_termin():
    # SQLite connection
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()
    
    # MySQL connection
    try:
        mysql_conn = mysql.connector.connect(
            host='localhost',
            database='barbershop',
            user='barberuser',
            password='barberpass123'
        )
        mysql_cursor = mysql_conn.cursor()
        
        # Disable foreign key checks
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        print("Importing appointment_termin...")
        
        # Get data from SQLite
        sqlite_cursor.execute("SELECT * FROM appointment_termin")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print("  No data in appointment_termin")
            return
            
        # Get column names
        sqlite_cursor.execute("PRAGMA table_info(appointment_termin)")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        insert_sql = f"INSERT INTO appointment_termin ({columns_str}) VALUES ({placeholders})"
        
        # Insert data into MySQL
        success_count = 0
        error_count = 0
        
        for row in rows:
            try:
                mysql_cursor.execute(insert_sql, row)
                success_count += 1
            except Error as e:
                print(f"  Error inserting: {e}")
                error_count += 1
                continue
        
        mysql_conn.commit()
        print(f"  Successfully imported: {success_count} rows")
        print(f"  Failed imports: {error_count} rows")
        
        # Re-enable foreign key checks
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        
    except Error as e:
        print(f"MySQL connection error: {e}")
    finally:
        if mysql_conn.is_connected():
            mysql_cursor.close()
            mysql_conn.close()
        sqlite_cursor.close()
        sqlite_conn.close()

if __name__ == "__main__":
    import_termin()