#!/bin/bash

# MySQL Database Setup Script for BarberShop Application
# This script creates the database and user for the Django application

echo "Setting up MySQL database for BarberShop..."

# Database configuration
DB_NAME="barbershop"
DB_USER="barberuser"
DB_PASSWORD="barberpass123"

# Create database
sudo mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Create user
sudo mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"

# Grant privileges
sudo mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"

# Flush privileges
sudo mysql -e "FLUSH PRIVILEGES;"

echo "MySQL setup completed successfully!"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "You can now run the Django migrations with:"
echo "python manage.py migrate"