#!/bin/bash

# Safer approach: Create a new clean repository without sensitive history

echo "=== Migrating to Clean Repository ==="
echo "This creates a new repository without sensitive commit history"
echo ""

CURRENT_DIR=$(pwd)
CLEAN_DIR="${CURRENT_DIR}_clean"

# Check if clean directory already exists
if [ -d "$CLEAN_DIR" ]; then
    echo "Error: Clean directory already exists: $CLEAN_DIR"
    exit 1
fi

echo "Creating clean repository in: $CLEAN_DIR"
mkdir "$CLEAN_DIR"
cd "$CLEAN_DIR" || exit 1

# Initialize new git repository
git init
echo "# BarberShop - Clean Repository" > README.md
git add README.md
git commit -m "Initial commit - clean repository"

echo ""
echo "Copying files from original repository (excluding sensitive files)..."

# Copy files excluding sensitive patterns
rsync -av --progress "$CURRENT_DIR/" "$CLEAN_DIR/" \
    --exclude='.git' \
    --exclude='.env' \
    --exclude='*.sqlite' \
    --exclude='*.db' \
    --exclude='*.backup' \
    --exclude='*.key' \
    --exclude='*.pem' \
    --exclude='*.crt' \
    --exclude='secrets.json' \
    --exclude='firebase-credentials.json' \
    --exclude='env/' \
    --exclude='venv/' \
    --exclude='.venv' \
    --exclude='__pycache__/' \
    --exclude='*.pyc'

echo ""
echo "Updating settings.py to use environment variables..."

# Update settings.py to remove hardcoded secrets
if [ -f "social1/social1/settings.py" ]; then
    # Create backup
    cp "social1/social1/settings.py" "social1/social1/settings.py.backup"
    
    # Replace hardcoded secrets with environment variables
    sed -i "s/SECRET_KEY =.*/SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')/" "social1/social1/settings.py"
    sed -i "s/'PASSWORD':.*/'PASSWORD': os.environ.get('DB_PASSWORD'),/" "social1/social1/settings.py"
    sed -i "s/EMAIL_HOST_PASSWORD =.*/EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')/" "social1/social1/settings.py"
    
    echo "Updated settings.py to use environment variables"
fi

echo ""
echo "Creating .gitignore for clean repository..."
cp "$CURRENT_DIR/.gitignore" .

# Add additional gitignore patterns
cat >> .gitignore << 'EOF'

# Additional sensitive files
*.env.local
*.env.production
.env.*
secret_key.txt

# Local development files
local_settings.py
override_settings.py
EOF

echo ""
echo "Creating environment template..."
cat > .env.example << 'EOF'
# Django Settings
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=barbershop
DB_USER=barberuser
DB_PASSWORD=your-mysql-password-here
DB_HOST=localhost
DB_PORT=3306

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-app-password
EOF

echo ""
echo "Adding files to new repository..."
git add .
git commit -m "Add application code with environment-based configuration"

echo ""
echo "=== Migration Complete ==="
echo "New clean repository created at: $CLEAN_DIR"
echo ""
echo "Next steps:"
echo "1. Review the new repository: cd $CLEAN_DIR"
echo "2. Create .env file with your actual secrets: cp .env.example .env"
 echo "3. Update .env with your actual database and email credentials"
echo "4. Set up your database and run migrations"
echo "5. Update your deployment to use the new repository"
echo ""
echo "WARNING: .env file contains secrets - DO NOT commit it to git!"
echo "Add it to .gitignore if it doesn't exist already."