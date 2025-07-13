// Firebase Configuration and FCM Setup

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyC6FWY3qwRD8s0NfwI7LEAAA3ByHTHtIRE",
  authDomain: "push-notify-4ffd3.firebaseapp.com",
  projectId: "push-notify-4ffd3",
  storageBucket: "push-notify-4ffd3.firebasestorage.app",
  messagingSenderId: "470008617640",
  appId: "1:470008617640:web:3e7fff66b4865f5276809d",
  measurementId: "G-YWVQ328VDH"
};

// Firebase and FCM management class
class FCMManager {
  constructor() {
    this.messaging = null;
    this.currentToken = null;
    this.isSupported = false;
    this.isInitialized = false;
  }

  async init() {
    try {
      console.log('Starting FCM Manager initialization...');
      
      // Check if Firebase Messaging is supported
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push messaging is not supported in this browser');
        return false;
      }

      console.log('Browser supports push messaging');

      // Import Firebase modules
      console.log('Importing Firebase modules...');
      const { initializeApp } = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js');
      const { getMessaging, getToken, onMessage, isSupported } = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging.js');

      console.log('Firebase modules imported successfully');

      // Check if messaging is supported
      this.isSupported = await isSupported();
      console.log('Firebase messaging supported:', this.isSupported);
      
      if (!this.isSupported) {
        console.warn('Firebase Messaging is not supported in this browser');
        return false;
      }

      // Initialize Firebase
      console.log('Initializing Firebase app...');
      const app = initializeApp(firebaseConfig);
      this.messaging = getMessaging(app);
      console.log('Firebase messaging initialized');

      // Register service worker
      console.log('Registering service worker...');
      await this.registerServiceWorker();

      this.isInitialized = true;
      console.log('FCM Manager initialized successfully');
      return true;

    } catch (error) {
      console.error('Error initializing FCM Manager:', error);
      console.error('Error details:', error.message, error.stack);
      return false;
    }
  }

  async registerServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
        scope: '/'
      });
      console.log('Service Worker registered successfully:', registration);
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      throw error;
    }
  }

  async requestPermission() {
    try {
      console.log('Requesting notification permission...');
      console.log('Current FCM Manager state:', {
        isInitialized: this.isInitialized,
        isSupported: this.isSupported,
        messaging: !!this.messaging
      });

      if (!this.isInitialized) {
        console.error('FCM Manager not initialized');
        return null;
      }

      const permission = await Notification.requestPermission();
      console.log('Notification permission result:', permission);
      
      if (permission === 'granted') {
        console.log('Notification permission granted, generating token...');
        return await this.generateToken();
      } else {
        console.log('Notification permission denied or dismissed');
        return null;
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      console.error('Error details:', error.message, error.stack);
      return null;
    }
  }

  async generateToken() {
    try {
      if (!this.messaging) {
        throw new Error('FCM not initialized');
      }

      const { getToken } = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging.js');
      
      // Try to get token without VAPID key first (Firebase will use project default)
      let token;
      try {
        token = await getToken(this.messaging);
      } catch (vapidError) {
        console.log('Trying with VAPID key...', vapidError.message);
        // If that fails, try with a VAPID key
        token = await getToken(this.messaging, {
          vapidKey: 'BKAhiDB3rapdGVKIyzRrNb2EJlIkvDcV4ujdy_lz7dWN5wD_9uI6spViYbpwC_ckZ1md0Nn-Ara2E2wSdaCNNw4'
        });
      }

      if (token) {
        console.log('FCM token generated:', token);
        this.currentToken = token;
        
        // Register token with backend
        await this.registerTokenWithBackend(token);
        return token;
      } else {
        console.log('No registration token available. Make sure messaging is enabled in Firebase console.');
        return null;
      }
    } catch (error) {
      console.error('Error generating FCM token:', error);
      if (error.message.includes('messaging/unsupported-browser')) {
        console.error('This browser does not support Firebase messaging');
      } else if (error.message.includes('messaging/permission-blocked')) {
        console.error('Notification permission was denied');
      }
      return null;
    }
  }

  async registerTokenWithBackend(token) {
    try {
      const response = await fetch('/fcm/register-token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          token: token,
          device_id: this.getDeviceId()
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Token registered successfully:', data);
        return data;
      } else {
        console.error('Failed to register token:', response.statusText);
        return null;
      }
    } catch (error) {
      console.error('Error registering token with backend:', error);
      return null;
    }
  }

  async unregisterToken() {
    try {
      const response = await fetch('/fcm/unregister-token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          device_id: this.getDeviceId()
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Token unregistered successfully:', data);
        this.currentToken = null;
        return data;
      } else {
        console.error('Failed to unregister token:', response.statusText);
        return null;
      }
    } catch (error) {
      console.error('Error unregistering token:', error);
      return null;
    }
  }

  async setupForegroundMessaging() {
    try {
      if (!this.messaging) {
        throw new Error('FCM not initialized');
      }

      const { onMessage } = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging.js');

      onMessage(this.messaging, (payload) => {
        console.log('Message received in foreground:', payload);
        
        // Show notification when app is in foreground
        this.showForegroundNotification(payload);
      });

      console.log('Foreground messaging setup complete');
    } catch (error) {
      console.error('Error setting up foreground messaging:', error);
    }
  }

  showForegroundNotification(payload) {
    const title = payload.notification?.title || 'New Notification';
    const options = {
      body: payload.notification?.body || 'You have a new message',
      icon: payload.notification?.icon || '/static/images/icon.png',
      badge: '/static/images/icon.png',
      tag: 'appointment-notification',
      requireInteraction: true,
      renotify: true,
      data: payload.data || {}
    };

    if (Notification.permission === 'granted') {
      const notification = new Notification(title, options);
      
      notification.onclick = () => {
        window.focus();
        notification.close();
        
        // Navigate to notifications page if needed
        if (payload.data?.notification_id) {
          window.location.href = '/notifications-page/';
        }
      };
    }
  }

  getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return value;
      }
    }
    
    // Fallback: try to get from meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    return csrfMeta ? csrfMeta.getAttribute('content') : '';
  }

  getDeviceId() {
    // Generate or retrieve a unique device ID for this browser
    let deviceId = localStorage.getItem('fcm_device_id');
    if (!deviceId) {
      deviceId = 'web-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('fcm_device_id', deviceId);
    }
    return deviceId;
  }

  async getTokenStatus() {
    try {
      const response = await fetch('/fcm/token-status/', {
        method: 'GET',
        headers: {
          'X-CSRFToken': this.getCSRFToken()
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        console.error('Failed to get token status:', response.statusText);
        return null;
      }
    } catch (error) {
      console.error('Error getting token status:', error);
      return null;
    }
  }
}

// Global FCM Manager instance
window.fcmManager = new FCMManager();

// Initialize FCM when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
  const initialized = await window.fcmManager.init();
  if (initialized) {
    await window.fcmManager.setupForegroundMessaging();
    console.log('FCM setup complete');
  }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FCMManager;
}