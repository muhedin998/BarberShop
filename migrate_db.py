#!/usr/bin/env python3
"""
Database Migration Script for BarberShop
This script handles migrating between SQLite and MySQL databases.
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social1.settings')
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'social1'))
    django.setup()

def export_sqlite_to_mysql():
    """Export data from SQLite to MySQL"""
    print("Exporting data from SQLite to MySQL...")
    
    # Create backup of SQLite data
    execute_from_command_line(['manage.py', 'dumpdata', '--natural-foreign', '--natural-primary', 
                             '-e', 'contenttypes', '-e', 'auth.Permission', 
                             '--indent', '2', '-o', 'sqlite_backup.json'])
    
    print("Data exported to sqlite_backup.json")

def import_mysql_from_backup():
    """Import data from backup to MySQL"""
    print("Importing data to MySQL from backup...")
    
    # Load data into MySQL
    execute_from_command_line(['manage.py', 'loaddata', 'sqlite_backup.json'])
    
    print("Data imported successfully to MySQL")

def migrate_to_mysql():
    """Full migration from SQLite to MySQL"""
    print("Starting migration from SQLite to MySQL...")
    
    # Step 1: Export data from SQLite
    export_sqlite_to_mysql()
    
    # Step 2: Switch to MySQL in settings (assumes settings are already configured)
    print("Please ensure MySQL settings are configured in settings.py")
    
    # Step 3: Import data to MySQL
    import_mysql_from_backup()
    
    print("Migration completed successfully!")

def create_mysql_backup():
    """Create backup of MySQL database"""
    print("Creating MySQL backup...")
    
    execute_from_command_line(['manage.py', 'dumpdata', '--natural-foreign', '--natural-primary', 
                             '-e', 'contenttypes', '-e', 'auth.Permission', 
                             '--indent', '2', '-o', 'mysql_backup.json'])
    
    print("MySQL backup created: mysql_backup.json")

def main():
    """Main function"""
    setup_django()
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_db.py [command]")
        print("Commands:")
        print("  export-sqlite    - Export SQLite data to backup")
        print("  import-mysql     - Import backup to MySQL") 
        print("  migrate          - Full migration from SQLite to MySQL")
        print("  backup-mysql     - Create MySQL backup")
        return
    
    command = sys.argv[1]
    
    if command == 'export-sqlite':
        export_sqlite_to_mysql()
    elif command == 'import-mysql':
        import_mysql_from_backup()
    elif command == 'migrate':
        migrate_to_mysql()
    elif command == 'backup-mysql':
        create_mysql_backup()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()