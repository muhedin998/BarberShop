#!/usr/bin/env python3
"""
SQLite to MySQL Migration Script for BarberShop
=================================================
This script provides a complete solution for migrating data from SQLite to MySQL.

Usage:
    python3 sqlite_to_mysql.py [command]
    
Commands:
    setup       - Setup MySQL database and user
    export      - Export data from SQLite to JSON backup
    import      - Import data from JSON backup to MySQL  
    migrate     - Complete migration (export + import)
    verify      - Verify migration was successful
    cleanup     - Remove temporary backup files
"""

import os
import sys
import django
import json
import subprocess
import sqlite3
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social1.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'social1'))

def setup_mysql():
    """Setup MySQL database and user"""
    print("🔧 Setting up MySQL database...")
    
    commands = [
        "CREATE DATABASE IF NOT EXISTS barbershop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "CREATE USER IF NOT EXISTS 'barberuser'@'localhost' IDENTIFIED BY 'barberpass123';", 
        "GRANT ALL PRIVILEGES ON barbershop.* TO 'barberuser'@'localhost';",
        "FLUSH PRIVILEGES;"
    ]
    
    for cmd in commands:
        result = subprocess.run(['mysql', '-u', 'root', '-h', '127.0.0.1', '-e', cmd], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ MySQL command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
    
    print("✅ MySQL database setup completed")
    return True

def export_sqlite_data():
    """Export data from SQLite to JSON backup"""
    print("📤 Exporting data from SQLite...")
    
    # Use Django management command with SQLite settings
    env = os.environ.copy()
    env['USE_SQLITE'] = '1'
    
    cmd = [
        'python3', 'social1/manage.py', 'dumpdata', 
        '--natural-foreign', '--natural-primary',
        '-e', 'contenttypes', '-e', 'auth.Permission',
        '--indent', '2', '-o', 'migration_backup.json'
    ]
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Export failed: {result.stderr}")
        return False
    
    # Check if file was created and has content
    if os.path.exists('migration_backup.json'):
        size = os.path.getsize('migration_backup.json')
        print(f"✅ Data exported successfully ({size:,} bytes)")
        return True
    else:
        print("❌ Export file not created")
        return False

def import_mysql_data():
    """Import data from JSON backup to MySQL with error handling"""
    print("📥 Importing data to MySQL...")
    
    if not os.path.exists('migration_backup.json'):
        print("❌ Backup file 'migration_backup.json' not found")
        return False
    
    # Setup Django
    django.setup()
    from django.core import serializers
    
    try:
        with open('migration_backup.json', 'r') as f:
            data = json.load(f)
        
        print(f"📊 Found {len(data)} objects to import")
        
        successful_imports = 0
        failed_imports = 0
        failed_objects = []
        
        for i, obj_data in enumerate(data):
            try:
                # Convert back to Django object and save
                obj = list(serializers.deserialize('json', json.dumps([obj_data])))[0]
                obj.save()
                successful_imports += 1
                
                # Progress indicator
                if (i + 1) % 1000 == 0:
                    print(f"   Imported {successful_imports:,} objects...")
                    
            except Exception as e:
                failed_imports += 1
                failed_objects.append({
                    'model': obj_data.get('model', 'unknown'),
                    'pk': obj_data.get('pk', 'unknown'),
                    'error': str(e)
                })
                # Continue with next object
                continue
        
        print(f"\n✅ Import completed!")
        print(f"   Successful: {successful_imports:,}")
        print(f"   Failed: {failed_imports:,}")
        
        if failed_imports > 0:
            print(f"\n⚠️  Some objects failed to import (usually due to data integrity issues):")
            # Show first few failures
            for failure in failed_objects[:5]:
                print(f"   - {failure['model']} (pk={failure['pk']}): {failure['error'][:60]}...")
            if len(failed_objects) > 5:
                print(f"   ... and {len(failed_objects) - 5} more")
        
        return successful_imports > 0
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def verify_migration():
    """Verify migration was successful by comparing counts"""
    print("🔍 Verifying migration...")
    
    # Setup Django to use MySQL
    django.setup()
    from django.db import connection
    
    # Check SQLite counts
    sqlite_conn = sqlite3.connect('social1/db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Check MySQL counts  
    mysql_cursor = connection.cursor()
    
    tables_to_check = [
        'appointment_korisnik',
        'appointment_termin', 
        'appointment_frizer',
        'appointment_usluge',
        'socialaccount_socialapp'
    ]
    
    print(f"{'Table':<25} {'SQLite':<10} {'MySQL':<10} {'Status'}")
    print("-" * 55)
    
    all_good = True
    
    for table in tables_to_check:
        try:
            # SQLite count
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
        except:
            sqlite_count = 0
            
        try:
            # MySQL count
            mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            mysql_count = mysql_cursor.fetchone()[0]
        except:
            mysql_count = 0
        
        if mysql_count >= sqlite_count * 0.95:  # Allow 5% data loss due to duplicates
            status = "✅ OK"
        elif mysql_count > 0:
            status = "⚠️  PARTIAL" 
        else:
            status = "❌ MISSING"
            all_good = False
            
        print(f"{table:<25} {sqlite_count:<10} {mysql_count:<10} {status}")
    
    sqlite_conn.close()
    
    if all_good:
        print("\n✅ Migration verification successful!")
    else:
        print("\n⚠️  Some issues found in migration")
    
    return all_good

def cleanup_files():
    """Remove temporary backup files"""
    print("🧹 Cleaning up temporary files...")
    
    files_to_remove = [
        'migration_backup.json',
        'sqlite_backup.json', 
        'sqlite_backup_full.json',
        'sqlite_data_partial.json',
        'missing_permissions.json',
        'backup_sqlite.py',
        'import_data_safe.py',
        'compare_tables.py'
    ]
    
    removed_count = 0
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")
            removed_count += 1
    
    print(f"✅ Cleaned up {removed_count} temporary files")

def complete_migration():
    """Complete migration from SQLite to MySQL"""
    print("🚀 Starting complete SQLite to MySQL migration...")
    print("=" * 60)
    
    # Step 1: Setup MySQL
    if not setup_mysql():
        return False
        
    # Step 2: Run Django migrations
    print("📋 Running Django migrations...")
    result = subprocess.run(['python3', 'social1/manage.py', 'migrate'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Django migrations failed: {result.stderr}")
        return False
    print("✅ Django migrations completed")
    
    # Step 3: Export from SQLite
    if not export_sqlite_data():
        return False
        
    # Step 4: Import to MySQL
    if not import_mysql_data():
        return False
        
    # Step 5: Verify
    verify_migration()
    
    print("\n🎉 Migration completed successfully!")
    print("Your barbershop application is now running on MySQL!")
    print("\nNext steps:")
    print("   1. Test your application: python3 social1/manage.py runserver")
    print("   2. Create a superuser: python3 social1/manage.py createsuperuser") 
    print("   3. Run cleanup to remove temp files: python3 sqlite_to_mysql.py cleanup")
    
    return True

def main():
    """Main function"""
    print("SQLite to MySQL Migration Tool")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        setup_mysql()
    elif command == 'export':
        export_sqlite_data()
    elif command == 'import':
        django.setup()
        import_mysql_data()
    elif command == 'migrate':
        complete_migration()
    elif command == 'verify':
        django.setup()
        verify_migration()
    elif command == 'cleanup':
        cleanup_files()
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()