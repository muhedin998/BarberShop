# Barber Shop Django Application with Push Notifications

A Django-based barber shop management system with Firebase push notifications support.

## Features

- **User Management**: Registration, authentication, profile management
- **Appointment Booking**: Schedule and manage appointments
- **Gallery**: Photo gallery of haircuts and services
- **Push Notifications**: Firebase-powered browser notifications
- **Admin Panel**: Comprehensive admin interface
- **Responsive Design**: Mobile-friendly interface

## Quick Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (recommended for production)
- Firebase project with service account

### Installation

1. **Clone and setup virtual environment:**
```bash
git clone <your-repo>
cd social1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Database setup:**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

3. **Firebase setup:**
   - Copy your Firebase service account JSON to `firebase-config.json`
   - Or set environment variables (see Environment Variables section)

4. **Run development server:**
```bash
python manage.py runserver
```

## Production Deployment

For production deployment on your testing server (evoluci4n.online), use the provided setup script:

```bash
chmod +x setup-push-notifications.sh
sudo ./setup-push-notifications.sh
```

This script will:
- Install Firebase dependencies
- Update nginx configuration with push notification support
- Configure gunicorn with environment variables
- Set up Firebase credentials
- Update Django settings
- Restart all services

## Environment Variables

Create a `.env` file with:

```bash
# Django Settings
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True  # Set to False in production
SITE_URL=https://your-domain.com

# Firebase Configuration
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=your-client-cert-url
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
```

## Project Structure

```
social1/
├── appointment/          # Main application
│   ├── models.py        # Database models
│   ├── views/           # View controllers
│   ├── push_notifications.py  # Firebase push notifications
│   ├── management/      # Django management commands
│   └── templates/       # HTML templates
├── galerija/            # Gallery application
├── static/              # Static files (CSS, JS, images)
├── media/               # User uploaded files
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── firebase-config.json # Firebase service account (gitignored)
└── setup-push-notifications.sh  # Production setup script
```

## Key Files

- **`setup-push-notifications.sh`**: Production deployment script
- **`requirements.txt`**: Python dependencies including Firebase admin
- **`production_requirements.txt`**: Production-specific dependencies
- **`appointment/push_notifications.py`**: Firebase integration
- **`appointment/models.py`**: Database models including Notification model
- **`static/firebase-messaging-sw.js`**: Service worker for push notifications

## Firebase Push Notifications

### Setup
1. Create a Firebase project
2. Generate a service account key
3. Enable Cloud Messaging API
4. Add your domain to authorized domains

### Usage
- Users can subscribe to notifications from the frontend
- Notifications are automatically sent when created via admin or code
- Service worker handles background notifications
- Supports rich notifications with actions and images

### Management Commands
```bash
# Clean up inactive FCM tokens
python manage.py cleanup_fcm_tokens

# Check FCM token status
python manage.py fcm_status
```

## Development

### Running Tests
```bash
python manage.py test
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic
```

## Production Considerations

- Set `DEBUG=False` in production
- Use PostgreSQL instead of SQLite
- Configure proper logging
- Set up SSL certificates
- Use environment variables for sensitive data ✅
- Configure firewall and security headers ✅
- Set up monitoring and backups

## Support

For issues or questions, check the application logs:
- **Django logs**: `python manage.py check`
- **Push notification logs**: `tail -f push_notifications.log`
- **Server logs**: `sudo journalctl -u gunicorn -f`