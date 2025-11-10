#!/usr/bin/env python3
"""
Fixed SQLite to MySQL Migration Script
Handles duplicate usernames by lowercasing and foreign key issues
"""

import os
import sys
import json
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social1.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'social1'))
django.setup()

from django.core import serializers
from django.db import transaction
from appointment.models import Korisnik, Termin

def import_with_fixes():
    """Import data with duplicate handling"""
    print("📥 Importing data with duplicate fixes...")
    
    with open('migration_backup.json', 'r') as f:
        data = json.load(f)
    
    print(f"📊 Found {len(data)} objects to import")
    
    # Separate by model type
    users = [obj for obj in data if obj['model'] == 'appointment.korisnik']
    appointments = [obj for obj in data if obj['model'] == 'appointment.termin']
    others = [obj for obj in data if obj['model'] not in ['appointment.korisnik', 'appointment.termin']]
    
    print(f"   Users: {len(users)}")
    print(f"   Appointments: {len(appointments)}")
    print(f"   Others: {len(others)}")
    
    # Track username mapping for duplicates
    username_map = {}  # old_pk -> new_pk
    seen_usernames = {}  # lowercase_username -> pk
    
    # Import users first, handling duplicates
    print("\n📝 Importing users...")
    success_count = 0
    skip_count = 0
    
    for obj_data in users:
        pk = obj_data['pk']
        username = obj_data['fields']['username']
        username_lower = username.lower()
        
        # Check if we've seen this username (case-insensitive)
        if username_lower in seen_usernames:
            # Duplicate found - map old pk to existing pk
            username_map[pk] = seen_usernames[username_lower]
            skip_count += 1
            continue
        
        try:
            obj = list(serializers.deserialize('json', json.dumps([obj_data])))[0]
            obj.save()
            username_map[pk] = pk
            seen_usernames[username_lower] = pk
            success_count += 1
            
            if success_count % 100 == 0:
                print(f"   Imported {success_count} users...")
        except Exception as e:
            print(f"   ⚠️  Failed to import user {username} (pk={pk}): {str(e)[:60]}")
            skip_count += 1
    
    print(f"✅ Users: {success_count} imported, {skip_count} skipped (duplicates)")
    
    # Import other models
    print("\n📝 Importing other models...")
    success_count = 0
    for obj_data in others:
        try:
            obj = list(serializers.deserialize('json', json.dumps([obj_data])))[0]
            obj.save()
            success_count += 1
        except Exception as e:
            pass  # Skip failures
    print(f"✅ Others: {success_count} imported")
    
    # Import appointments with FK mapping
    print("\n📝 Importing appointments...")
    success_count = 0
    skip_count = 0
    
    for obj_data in appointments:
        # Fix foreign key references
        korisnik_pk = obj_data['fields'].get('korisnik')
        if korisnik_pk and korisnik_pk in username_map:
            obj_data['fields']['korisnik'] = username_map[korisnik_pk]
        
        try:
            obj = list(serializers.deserialize('json', json.dumps([obj_data])))[0]
            obj.save()
            success_count += 1
            
            if success_count % 1000 == 0:
                print(f"   Imported {success_count} appointments...")
        except Exception as e:
            skip_count += 1
            if skip_count <= 5:
                print(f"   ⚠️  Failed: {str(e)[:80]}")
    
    print(f"✅ Appointments: {success_count} imported, {skip_count} failed")
    
    print("\n🎉 Migration completed!")
    return success_count > 0

if __name__ == '__main__':
    import_with_fixes()
