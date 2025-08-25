from django.core.management.base import BaseCommand
from django.conf import settings
import os
import firebase_admin
from firebase_admin import credentials

class Command(BaseCommand):
    help = 'Test Firebase configuration'

    def handle(self, *args, **options):
        self.stdout.write("🔥 Testing Firebase Configuration...\n")
        
        # Check environment variables
        firebase_vars = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY_ID', 
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'FIREBASE_CLIENT_ID',
        ]
        
        self.stdout.write("📋 Environment Variables:")
        missing_vars = []
        for var in firebase_vars:
            value = os.environ.get(var)
            if value:
                if var == 'FIREBASE_PRIVATE_KEY':
                    self.stdout.write(f"  ✅ {var}: [PRIVATE KEY SET - {len(value)} chars]")
                else:
                    self.stdout.write(f"  ✅ {var}: {value}")
            else:
                self.stdout.write(f"  ❌ {var}: NOT SET")
                missing_vars.append(var)
        
        if missing_vars:
            self.stdout.write(f"\n❌ Missing variables: {', '.join(missing_vars)}")
            return
        
        # Check Django settings
        self.stdout.write(f"\n🔧 Django FIREBASE_CONFIG:")
        config = settings.FIREBASE_CONFIG
        for key, value in config.items():
            if key == 'private_key':
                self.stdout.write(f"  {key}: [PRIVATE KEY - {len(value) if value else 0} chars]")
            else:
                self.stdout.write(f"  {key}: {value}")
        
        # Test Firebase initialization
        self.stdout.write(f"\n🚀 Testing Firebase Initialization:")
        try:
            # Clear any existing apps first
            for app in firebase_admin._apps.copy():
                firebase_admin.delete_app(app)
            
            # Try to initialize
            if config.get('private_key'):
                cred = credentials.Certificate(config)
                app = firebase_admin.initialize_app(cred)
                self.stdout.write("  ✅ Firebase Admin SDK initialized successfully!")
                self.stdout.write(f"  📱 Project ID: {app.project_id}")
                
                # Test a simple operation
                from firebase_admin import messaging
                self.stdout.write("  ✅ Firebase Messaging module loaded successfully!")
                
                # Clean up
                firebase_admin.delete_app(app)
                
            else:
                self.stdout.write("  ❌ No private_key found in configuration")
                
        except Exception as e:
            self.stdout.write(f"  ❌ Firebase initialization failed: {str(e)}")
        
        self.stdout.write(f"\n🏁 Test completed!")