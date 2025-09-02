#!/usr/bin/env python3
import sqlite3
import mysql.connector
from mysql.connector import Error
import os

def import_data():
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
        
        # List of tables to import (excluding auth and django tables)
        tables = [
            'appointment_korisnik',
            'appointment_termin', 
            'appointment_notification',
            'appointment_duznik',
            'appointment_review',
            'appointment_usluge',
            'appointment_frizer'
        ]
        
        for table in tables:
            print(f"Importing {table}...")
            
            # Get data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  No data in {table}")
                continue
                
            # Get column names
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in sqlite_cursor.fetchall()]
            
            # Prepare insert statement
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            insert_sql = f"INSERT IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"
            
            # Insert data into MySQL
            for row in rows:
                try:
                    mysql_cursor.execute(insert_sql, row)
                except Error as e:
                    print(f"  Error inserting into {table}: {e}")
                    continue
            
            print(f"  Imported {len(rows)} rows")
            
        mysql_conn.commit()
        print("Data import completed!")
        
    except Error as e:
        print(f"MySQL connection error: {e}")
    finally:
        if mysql_conn.is_connected():
            mysql_cursor.close()
            mysql_conn.close()
        sqlite_cursor.close()
        sqlite_conn.close()

if __name__ == "__main__":
    import_data()