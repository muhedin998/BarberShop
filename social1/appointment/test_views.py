from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Notification
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def create_test_notification(request):
    """
    Create a test notification for the current admin user
    """
    try:
        data = json.loads(request.body)
        title = data.get('title', 'Test Notification')
        message = data.get('message', 'This is a test notification')
        
        # Create notification for the current user
        notification = Notification.objects.create(
            user=request.user,
            title=title,
            message=message
        )
        
        logger.info(f'Test notification created for admin user {request.user.username}')
        
        return JsonResponse({
            'success': True,
            'message': 'Test notification created successfully',
            'notification_id': notification.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Error creating test notification: {str(e)}')
        return JsonResponse({'error': 'Internal server error'}, status=500)