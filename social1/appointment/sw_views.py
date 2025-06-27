from django.http import HttpResponse, Http404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings

@never_cache
@csrf_exempt
def firebase_messaging_sw(request):
    """
    Serve the Firebase messaging service worker from the root path
    """
    try:
        sw_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR, 'firebase-messaging-sw.js')
        
        # If STATIC_ROOT doesn't exist or file not found, try static directory
        if not os.path.exists(sw_path):
            sw_path = os.path.join(settings.BASE_DIR, 'static', 'firebase-messaging-sw.js')
        
        if not os.path.exists(sw_path):
            raise Http404("Service worker not found")
            
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        response = HttpResponse(content, content_type='application/javascript')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
        
    except FileNotFoundError:
        raise Http404("Service worker not found")