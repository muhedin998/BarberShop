// Firebase Messaging Service Worker - Django Template
// This file must be accessible at the root of your domain

// Import Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging-compat.js');

// Firebase configuration - loaded from Django settings
const firebaseConfig = {
  apiKey: "{{ firebase_web_config.apiKey }}",
  authDomain: "{{ firebase_web_config.authDomain }}",
  projectId: "{{ firebase_web_config.projectId }}",
  storageBucket: "{{ firebase_web_config.storageBucket }}",
  messagingSenderId: "{{ firebase_web_config.messagingSenderId }}",
  appId: "{{ firebase_web_config.appId }}",
  measurementId: "{{ firebase_web_config.measurementId }}"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firebase Messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('Received background message:', payload);

  const notificationTitle = payload.notification?.title || 'New Notification';
  const notificationOptions = {
    body: payload.notification?.body || 'You have a new message',
    icon: payload.notification?.icon || '/static/images/icon.png',
    badge: '/static/images/icon.png',
    tag: 'appointment-notification',
    requireInteraction: true,
    renotify: true,
    data: payload.data || {}
  };

  // Show notification
  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click events
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);
  
  event.notification.close();
  
  // Handle notification click based on data
  const clickAction = event.notification.data?.click_action || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Check if there's already a window/tab open with the target URL
      for (const client of clientList) {
        if (client.url === clickAction && 'focus' in client) {
          return client.focus();
        }
      }
      
      // If no existing window found, open a new one
      if (clients.openWindow) {
        return clients.openWindow(clickAction);
      }
    })
  );
});

// Handle push events (for older browsers) - REMOVED to prevent duplicates
// Firebase's onBackgroundMessage already handles push notifications

// Service worker activation
self.addEventListener('activate', (event) => {
  console.log('Firebase messaging service worker activated');
  // Send message to main thread for mobile debugging
  event.waitUntil(
    self.clients.claim().then(() => {
      return self.clients.matchAll();
    }).then(clients => {
      clients.forEach(client => {
        client.postMessage({
          type: 'debug',
          message: 'DEBUG: Service worker activated successfully'
        });
      });
    })
  );
});

// Service worker installation
self.addEventListener('install', (event) => {
  console.log('Firebase messaging service worker installed');
  // Send message to main thread for mobile debugging
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage({
        type: 'debug',
        message: 'DEBUG: Service worker installed successfully'
      });
    });
  });
  self.skipWaiting();
});