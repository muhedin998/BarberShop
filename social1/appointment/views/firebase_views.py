from django.http import HttpResponse
from django.template import loader
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

@never_cache
@csrf_exempt
def firebase_config_js(request):
    """
    Serve the Firebase config JavaScript file with dynamic configuration
    """
    template = loader.get_template('appointment/js/firebase-config.js')
    context = {
        'firebase_web_config': settings.FIREBASE_WEB_CONFIG,
        'firebase_vapid_key': settings.FIREBASE_VAPID_KEY
    }
    
    content = template.render(context, request)
    
    response = HttpResponse(content, content_type='application/javascript')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@never_cache
@csrf_exempt
def firebase_messaging_sw_js(request):
    """
    Serve the Firebase messaging service worker with dynamic configuration
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