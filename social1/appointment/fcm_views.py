from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from .models import FCMToken
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def register_fcm_token(request):
    """
    Register or update FCM token for the current user
    """
    try:
        logger.info(f'FCM token registration request from user {request.user.username}')
        logger.info(f'Request body: {request.body.decode("utf-8")[:200]}...')
        
        data = json.loads(request.body)
        token = data.get('token')
        device_id = data.get('device_id', 'web-browser')
        
        logger.info(f'Token length: {len(token) if token else 0}, Device ID: {device_id}')
        
        if not token:
            logger.error('No FCM token provided in request')
            return JsonResponse({'error': 'FCM token is required'}, status=400)
        
        # First, deactivate any existing tokens for this user/device combination
        existing_tokens = FCMToken.objects.filter(
            user=request.user,
            device_id=device_id,
            is_active=True
        ).exclude(token=token)
        
        deactivated_count = existing_tokens.update(is_active=False)
        if deactivated_count > 0:
            logger.info(f'Deactivated {deactivated_count} old FCM tokens for user {request.user.username}')
        
        # Create or update the FCM token
        fcm_token, created = FCMToken.objects.update_or_create(
            user=request.user,
            device_id=device_id,
            defaults={
                'token': token,
                'is_active': True
            }
        )
        
        action = 'created' if created else 'updated'
        logger.info(f'FCM token {action} for user {request.user.username} - Token ID: {fcm_token.id}')
        
        return JsonResponse({
            'success': True,
            'message': f'FCM token {action} successfully',
            'token_id': fcm_token.id
        })
        
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON data in FCM token registration: {str(e)}')
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Error registering FCM token: {str(e)}', exc_info=True)
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def unregister_fcm_token(request):
    """
    Unregister FCM token for the current user
    """
    try:
        data = json.loads(request.body)
        device_id = data.get('device_id', 'web-browser')
        
        # Deactivate the FCM token
        updated = FCMToken.objects.filter(
            user=request.user,
            device_id=device_id
        ).update(is_active=False)
        
        if updated:
            logger.info(f'FCM token deactivated for user {request.user.username}')
            return JsonResponse({
                'success': True,
                'message': 'FCM token unregistered successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No active FCM token found'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Error unregistering FCM token: {str(e)}')
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
@login_required
def fcm_token_status(request):
    """
    Get FCM token status for the current user
    """
    try:
        tokens = FCMToken.objects.filter(user=request.user, is_active=True)
        token_data = [
            {
                'id': token.id,
                'device_id': token.device_id,
                'created_at': token.created_at.isoformat(),
                'updated_at': token.updated_at.isoformat()
            }
            for token in tokens
        ]
        
        return JsonResponse({
            'success': True,
            'tokens': token_data,
            'count': len(token_data)
        })
        
    except Exception as e:
        logger.error(f'Error getting FCM token status: {str(e)}')
        return JsonResponse({'error': 'Internal server error'}, status=500)