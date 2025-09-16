# This file is deprecated - Firebase service worker is now served by firebase_views.py
# Keeping this file for backward compatibility

from django.http import HttpResponse
from django.template import loader
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@never_cache
@csrf_exempt
def firebase_messaging_sw(request):
    """
    Serve the Firebase messaging service worker from the root path
    Now uses Django template for dynamic configuration
    """
    template = loader.get_template('appointment/js/firebase-messaging-sw.js')
    context = {
        'firebase_web_config': settings.FIREBASE_WEB_CONFIG
    }
    
    content = template.render(context, request)
    
    response = HttpResponse(content, content_type='application/javascript')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response