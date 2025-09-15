from .models import Notification, Banner

def notification_count(request):
    """
    Context processor to add unread notification count to all templates
    """
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {'unread_notification_count': unread_count}
    return {'unread_notification_count': 0}

def active_banners(request):
    """
    Context processor to add active banners to all templates
    """
    banners = Banner.get_active_banners()
    return {'active_banners': banners}