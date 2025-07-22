# Push Notifications Production Setup Guide

## Issues Resolved

### ✅ 1. Ngrok Duplicate Notifications - FIXED
- **Problem**: Users receiving 2-4 duplicate notifications
- **Cause**: Multiple active FCM tokens per user
- **Solution**: Ran `python manage.py cleanup_fcm_tokens` - now each user has exactly 1 active token
- **Status**: SOLVED ✅

### ❌ 2. Production Notifications Not Working - NEEDS CONFIGURATION

## Configuration Options

### Option 1: Production (Environment Variables)
For production deployment, set these environment variables:

```bash
# Firebase Service Account Configuration
export FIREBASE_TYPE="service_account"
export FIREBASE_PROJECT_ID="push-notify-4ffd3"
export FIREBASE_PRIVATE_KEY_ID="your_private_key_id_here"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key content here\n-----END PRIVATE KEY-----"
export FIREBASE_CLIENT_EMAIL="firebase-adminsdk-xxxxx@push-notify-4ffd3.iam.gserviceaccount.com"
export FIREBASE_CLIENT_ID="your_client_id_here"
export FIREBASE_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
export FIREBASE_TOKEN_URI="https://oauth2.googleapis.com/token"
export FIREBASE_AUTH_PROVIDER_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
export FIREBASE_CLIENT_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40push-notify-4ffd3.iam.gserviceaccount.com"
export FIREBASE_UNIVERSE_DOMAIN="googleapis.com"
```

### Option 2: Development (Configuration File)
For development and testing, place the Firebase service account JSON file as:
```
project_root/firebase-config.json
```

**File Structure:**
```
social1/
├── firebase-config.json          ← Place Firebase service account JSON here
├── manage.py
├── appointment/
│   ├── static/appointment/js/
│   │   └── firebase-config.js    ← Client-side Firebase config (already exists)
└── social1/
    └── settings.py
```

### 3. Firebase Service Account Configuration

#### ✅ Development - Already Working
Your development environment already has the working `firebase-config.json` file in the project root.

#### ⚠️ Production - Needs Environment Variables
For production security, extract the values from your existing `firebase-config.json` and set them as environment variables (from Option 1 above). This keeps sensitive credentials out of your codebase in production.

### 4. Optional: Development/Testing Environment Variables
For development and testing environments, you can set:
```bash
# For ngrok development
export SITE_URL="https://your-ngrok-subdomain.ngrok-free.app"

# For evoluci4n.online testing
export SITE_URL="https://evoluci4n.online"
```

## Troubleshooting

### Check Configuration
Use this script to verify your setup:
```bash
python3 check_config.py
```

### Check FCM Tokens
```bash
python3 manage.py shell -c "
from appointment.models import FCMToken
from django.contrib.auth import get_user_model
User = get_user_model()

for user in User.objects.filter(fcmtoken__is_active=True).distinct():
    tokens = FCMToken.objects.filter(user=user, is_active=True)
    print(f'User: {user.username} - Active tokens: {tokens.count()}')
"
```

### Manual Token Cleanup
If you see duplicate tokens:
```bash
python3 manage.py cleanup_fcm_tokens
```

### Test Notifications
```bash
python3 manage.py shell -c "
from appointment.models import Notification
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='your_username')
notification = Notification.objects.create(
    user=user,
    title='Test Notification',
    message='Testing production push notifications'
)
print(f'Notification created: {notification.id}, Push sent: {notification.push_sent}')
"
```

### Check Logs
Monitor Django logs for push notification errors:
```bash
tail -f push_notifications.log
```

## Domain Configuration

### ✅ Configured Domains
The system now supports multiple domains automatically:
- **Production**: `frizerskisalonhasko.com` ✅
- **Testing**: `evoluci4n.online` ✅ (added to Django sites)
- **Development**: `localhost:8000` ✅
- **Ngrok**: Dynamic subdomains ✅ (via SITE_URL environment variable)

### 🔧 How Multi-Domain Support Works
- Firebase service worker uses `self.location.origin` for dynamic domain handling ✅
- JavaScript config uses `window.location.origin` for service worker registration ✅
- Backend `get_site_url()` function supports SITE_URL override or Django sites framework ✅
- No hardcoded domains in client-side code ✅

## Current Status

### ✅ Working Components
- FCM token registration and management ✅
- Firebase SDK initialization ✅
- Notification model with automatic push sending ✅
- Token cleanup system ✅
- Duplicate notification issue resolved ✅
- Site URL configuration fixed ✅
- Multi-domain support configured ✅

### ⚠️ Requires Configuration
- Firebase environment variables in production ❌
- Verify users have registered FCM tokens in production ❌

## Production Deployment Checklist

1. **Set Firebase environment variables** (see above)
2. **Verify Firebase service account has FCM permissions**
3. **Test notification creation manually**
4. **Verify users can register for notifications**
5. **Monitor logs for errors**
6. **Run periodic token cleanup if needed**

## Files Modified

### Fixed Production URL Issue
- `appointment/push_notifications.py` - Fixed `get_site_url()` to handle None values
- Added proper fallback to production domain

### Debugging Code Removed
- Created `fcm_debug_cleanup.patch` with all debugging code
- Removed all test/debug views, templates, and scripts
- Cleaned production JavaScript files

## Notes

- Development uses `firebase-config.json` file ✅
- Production should use environment variables ❌
- Push notifications require HTTPS (handled automatically) ✅
- All debugging code archived in patch file ✅