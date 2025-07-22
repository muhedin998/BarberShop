import firebase_admin
from firebase_admin import credentials, messaging
import os
from django.conf import settings
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    if not firebase_admin._apps:
        # Try to use environment variables first, fallback to config file
        if hasattr(settings, 'FIREBASE_CONFIG') and settings.FIREBASE_CONFIG.get('private_key'):
            cred = credentials.Certificate(settings.FIREBASE_CONFIG)
        else:
            # Fallback to config file for development
            cred_path = os.path.join(settings.BASE_DIR, 'firebase-config.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                raise Exception("Firebase configuration not found. Please set environment variables or provide firebase-config.json")
        firebase_admin.initialize_app(cred)

def get_site_url():
    """
    Get the current site URL for notifications
    """
    try:
        # Try to get from settings first (for ngrok/development)
        if hasattr(settings, 'SITE_URL'):
            return settings.SITE_URL
        
        # Try to get current site
        current_site = Site.objects.get_current()
        protocol = 'https' if settings.DEBUG else 'https'  # Always HTTPS for push notifications
        return f'{protocol}://{current_site.domain}'
    except Exception:
        # Fallback
        return 'https://frizerskisalonhasko.com'

def send_push_notification(fcm_token, title, body, data=None):
    """
    Send a push notification to a specific FCM token
    
    Args:
        fcm_token (str): FCM token of the device
        title (str): Notification title
        body (str): Notification body
        data (dict): Optional data payload
    
    Returns:
        str: Message ID if successful, None if failed
    """
    try:
        initialize_firebase()
        
        # Get current site URL
        site_url = get_site_url()
        icon_url = f'{site_url}/static/images/icon.png'
        
        # Create the notification
        notification = messaging.Notification(
            title=title,
            body=body
        )
        
        # Create the message
        message = messaging.Message(
            notification=notification,
            data=data or {},
            token=fcm_token,
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                    icon=icon_url,
                    badge=icon_url,
                    require_interaction=True,
                    renotify=True,
                    tag='appointment-notification'
                ),
                fcm_options=messaging.WebpushFCMOptions(
                    link=site_url
                )
            )
        )
        
        # Send the message
        response = messaging.send(message)
        logger.info(f'Successfully sent message: {response}')
        return response
        
    except Exception as e:
        logger.error(f'Error sending push notification: {str(e)}')
        return None

def send_push_notification_to_user(user, title, body, data=None):
    """
    Send push notification to all devices of a user
    
    Args:
        user: User object
        title (str): Notification title
        body (str): Notification body
        data (dict): Optional data payload
    
    Returns:
        list: List of successful message IDs
    """
    try:
        # Get all FCM tokens for the user
        from .models import FCMToken
        user_tokens = FCMToken.objects.filter(user=user, is_active=True)
        
        logger.info(f'Found {user_tokens.count()} active FCM tokens for user {user.username}')
        
        if not user_tokens.exists():
            logger.warning(f'No active FCM tokens found for user {user.username}')
            return []
        
        successful_sends = []
        
        for token_obj in user_tokens:
            logger.info(f'Attempting to send push notification to token {token_obj.id} for user {user.username}')
            result = send_push_notification(token_obj.token, title, body, data)
            if result:
                successful_sends.append(result)
                logger.info(f'Successfully sent notification to token {token_obj.id}')
            else:
                logger.warning(f'Failed to send notification to token {token_obj.id}, marking as inactive')
                # Mark token as inactive if sending failed
                token_obj.is_active = False
                token_obj.save()
        
        logger.info(f'Push notification summary for user {user.username}: {len(successful_sends)} successful, {user_tokens.count() - len(successful_sends)} failed')
        return successful_sends
        
    except Exception as e:
        logger.error(f'Error sending push notification to user {user.username}: {str(e)}', exc_info=True)
        return []

def send_bulk_push_notifications(tokens, title, body, data=None):
    """
    Send push notifications to multiple tokens
    
    Args:
        tokens (list): List of FCM tokens
        title (str): Notification title  
        body (str): Notification body
        data (dict): Optional data payload
    
    Returns:
        dict: Results with successful and failed sends
    """
    try:
        initialize_firebase()
        
        # Create messages for all tokens
        messages = []
        for token in tokens:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token,
                webpush=messaging.WebpushConfig(
                    notification=messaging.WebpushNotification(
                        title=title,
                        body=body,
                        icon='https://frizerskisalonhasko.com/static/images/icon.png',
                        badge='https://frizerskisalonhasko.com/static/images/icon.png',
                        require_interaction=True,
                        renotify=True,
                        tag='appointment-notification'
                    ),
                    fcm_options=messaging.WebpushFCMOptions(
                        link='https://frizerskisalonhasko.com/'
                    )
                )
            )
            messages.append(message)
        
        # Send all messages
        response = messaging.send_all(messages)
        
        logger.info(f'Successfully sent {response.success_count} messages')
        if response.failure_count > 0:
            logger.warning(f'Failed to send {response.failure_count} messages')
            
        return {
            'success_count': response.success_count,
            'failure_count': response.failure_count,
            'responses': response.responses
        }
        
    except Exception as e:
        logger.error(f'Error sending bulk push notifications: {str(e)}')
        return {
            'success_count': 0,
            'failure_count': len(tokens),
            'error': str(e)
        }