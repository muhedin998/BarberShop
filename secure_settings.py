#!/usr/bin/env python3
"""
Script to help migrate Django settings to use environment variables
and remove hardcoded secrets.
"""

import os
import re

def update_settings_file():
    """Update settings.py to use environment variables"""
    
    settings_path = 'social1/social1/settings.py'
    
    if not os.path.exists(settings_path):
        print(f"Settings file not found: {settings_path}")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Replace hardcoded SECRET_KEY with environment variable
    content = re.sub(
        r"SECRET_KEY\s*=\s*['\"].*?['\"]",
        "SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')",
        content
    )
    
    # Replace hardcoded database credentials with environment variables
    database_pattern = r"'NAME'\s*:\s*['\"](.*?)['\"],\s*'USER'\s*:\s*['\"](.*?)['\"],\s*'PASSWORD'\s*:\s*['\"](.*?)['\"],"
    
    def replace_database(match):
        name, user, password = match.groups()
        return f"'NAME': os.environ.get('DB_NAME', '{name}'),\n        'USER': os.environ.get('DB_USER', '{user}'),\n        'PASSWORD': os.environ.get('DB_PASSWORD', '{password}'),"
    
    content = re.sub(database_pattern, replace_database, content)
    
    # Write updated content back
    with open(settings_path, 'w') as f:
        f.write(content)
    
    print("Settings file updated to use environment variables")
    print("Please set the following environment variables:")
    print("  - DJANGO_SECRET_KEY")
    print("  - DB_NAME") 
    print("  - DB_USER")
    print("  - DB_PASSWORD")
    
    return True

def create_env_file():
    """Create .env file from current settings"""
    
    env_path = '.env'
    if os.path.exists(env_path):
        print(f".env file already exists: {env_path}")
        return False
    
    # Read current settings to extract values
    settings_path = 'social1/social1/settings.py'
    
    if not os.path.exists(settings_path):
        print(f"Settings file not found: {settings_path}")
        return False
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Extract SECRET_KEY
    secret_key_match = re.search(r"SECRET_KEY\s*=\s*['\"](.*?)['\"]", content)
    secret_key = secret_key_match.group(1) if secret_key_match else 'your-super-secret-key-here'
    
    # Extract database credentials
    db_name_match = re.search(r"'NAME'\s*:\s*['\"](.*?)['\"]", content)
    db_user_match = re.search(r"'USER'\s*:\s*['\"](.*?)['\"]", content)
    db_password_match = re.search(r"'PASSWORD'\s*:\s*['\"](.*?)['\"]", content)
    
    db_name = db_name_match.group(1) if db_name_match else 'barbershop'
    db_user = db_user_match.group(1) if db_user_match else 'barberuser'
    db_password = db_password_match.group(1) if db_password_match else 'your-mysql-password'
    
    # Create .env file
    env_content = f"""# Django Settings
DJANGO_SECRET_KEY={secret_key}
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST=localhost
DB_PORT=3306

# Add other environment variables as needed
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"Created {env_path} with current settings")
    print("WARNING: This file contains secrets. Add it to .gitignore!")
    
    return True

def main():
    """Main function"""
    print("Django Settings Security Migration Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python secure_settings.py [command]")
        print("Commands:")
        print("  update-settings - Update settings.py to use env variables")
        print("  create-env      - Create .env file from current settings")
        return
    
    command = sys.argv[1]
    
    if command == 'update-settings':
        update_settings_file()
    elif command == 'create-env':
        create_env_file()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    import sys
    main()