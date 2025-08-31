# MySQL Database Setup for BarberShop

This document explains how to set up MySQL database for the BarberShop Django application.

## Prerequisites

- MySQL Server installed and running
- sudo access to create database and users

## Quick Setup

Run the automated setup script:

```bash
./setup_mysql.sh
```

## Manual Setup Commands

If you prefer to run the commands manually:

```bash
# Create database
sudo mysql -e "CREATE DATABASE IF NOT EXISTS barbershop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Create user
sudo mysql -e "CREATE USER IF NOT EXISTS 'barberuser'@'localhost' IDENTIFIED BY 'barberpass123';"

# Grant privileges
sudo mysql -e "GRANT ALL PRIVILEGES ON barbershop.* TO 'barberuser'@'localhost';"

# Flush privileges
sudo mysql -e "FLUSH PRIVILEGES;"
```

## Django Configuration

The application is already configured to use MySQL with these settings in `social1/social1/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'barbershop',
        'USER': 'barberuser',
        'PASSWORD': 'barberpass123',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

## Python Dependencies

The following Python packages are required for MySQL connectivity:

- `pymysql==1.1.2` (already added to requirements.txt)

Install dependencies:
```bash
pip install -r social1/requirements.txt
```

## Migration Steps

After setting up the database, run Django migrations:

```bash
cd social1
python manage.py migrate
```

## Database Backup and Restore

### Backup MySQL database:
```bash
mysqldump -u barberuser -p barbershop > backup.sql
```

### Restore MySQL database:
```bash
mysql -u barberuser -p barbershop < backup.sql
```

## Troubleshooting

### Common Issues:

1. **MySQL connection refused**: Ensure MySQL server is running
   ```bash
   sudo systemctl status mysql
   sudo systemctl start mysql
   ```

2. **Access denied for user**: Check user privileges and password

3. **Database doesn't exist**: Run the setup script again

4. **Character encoding issues**: Ensure database uses utf8mb4 charset

## Security Notes

- Change the default password in production
- Consider using environment variables for database credentials
- Restrict database user privileges to only necessary operations