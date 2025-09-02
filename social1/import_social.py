#!/usr/bin/env python3
import sqlite3
import mysql.connector
from mysql.connector import Error

def import_social():
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
        
        print("Importing socialaccount_socialapp...")
        
        # Get social app data from SQLite
        sqlite_cursor.execute("SELECT * FROM socialaccount_socialapp")
        social_apps = sqlite_cursor.fetchall()
        
        if social_apps:
            # Insert social apps
            insert_sql = """INSERT INTO socialaccount_socialapp 
                           (id, provider, name, client_id, secret, key, settings) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            
            for app in social_apps:
                try:
                    mysql_cursor.execute(insert_sql, app)
                    print(f"  Imported social app: {app[1]}")
                except Error as e:
                    print(f"  Error inserting social app {app[1]}: {e}")
        
        print("Importing socialaccount_socialapp_sites...")
        
        # Get social app sites data from SQLite
        sqlite_cursor.execute("SELECT * FROM socialaccount_socialapp_sites")
        app_sites = sqlite_cursor.fetchall()
        
        if app_sites:
            # Insert social app sites
            insert_sql = "INSERT INTO socialaccount_socialapp_sites (id, socialapp_id, site_id) VALUES (%s, %s, %s)"
            
            for site in app_sites:
                try:
                    mysql_cursor.execute(insert_sql, site)
                    print(f"  Imported social app site mapping: {site}")
                except Error as e:
                    print(f"  Error inserting social app site mapping: {e}")
        
        mysql_conn.commit()
        print("Social app data import completed!")
        
    except Error as e:
        print(f"MySQL connection error: {e}")
    finally:
        if mysql_conn.is_connected():
            mysql_cursor.close()
            mysql_conn.close()
        sqlite_cursor.close()
        sqlite_conn.close()

if __name__ == "__main__":
    import_social()