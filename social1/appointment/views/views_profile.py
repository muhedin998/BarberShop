from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from ..models import Notification
from ..forms import ProfileUpdateForm
from django.contrib import messages


@login_required
def profile_page(request):
    user = request.user
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil je uspešno ažuriran!')
            return redirect('profile_page')
        else:
            messages.error(request, 'Greška pri ažuriranju profila. Molimo pokušajte ponovo.', extra_tags='danger')
    else:
        form = ProfileUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    return render(request, 'appointment/profil-page.html', context)


@login_required
def notifications_page(request):
    """Display notifications page with user's notifications"""
    user = request.user
    
    # Get unread notifications
    unread_notifications = Notification.objects.filter(
        user=user, 
        is_read=False
    ).order_by('-created_at')
    
    # Get read notifications (archived)
    archived_notifications = Notification.objects.filter(
        user=user, 
        is_read=True
    ).order_by('-read_at')
    
    # Count notifications
    unread_count = unread_notifications.count()
    archived_count = archived_notifications.count()
    
    context = {
        'unread_notifications': unread_notifications,
        'archived_notifications': archived_notifications,
        'unread_count': unread_count,
        'archived_count': archived_count,
    }
    
    return render(request, 'appointment/notifications_page.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    return JsonResponse({'success': True, 'message': 'Obaveštenje je označeno kao pročitano'})


@login_required
@require_POST
def mark_notification_unread(request, notification_id):
    """Mark a notification as unread"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if notification.is_read:
        notification.is_read = False
        notification.read_at = None
        notification.save()
    
    return JsonResponse({'success': True, 'message': 'Obaveštenje je označeno kao nepročitano'})


@login_required
@require_POST
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    
    return JsonResponse({'success': True, 'message': 'Obaveštenje je obrisano'})


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    updated_count = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).update(
        is_read=True, 
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True, 
        'message': f'{updated_count} obaveštenja su označena kao pročitana'
    })


@login_required
def fcm_debug_page(request):
    """Debug page for FCM token registration"""
    return render(request, 'appointment/fcm_debug.html')
