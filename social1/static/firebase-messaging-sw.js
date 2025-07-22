// Firebase Messaging Service Worker

console.log('Firebase Messaging Service Worker loading...');

// Import Firebase scripts
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging-compat.js');

console.log('Firebase scripts imported');

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

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
console.log('Firebase initialized in service worker');

// Force service worker activation
self.addEventListener('install', function(event) {
  console.log('Firebase service worker installing');
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  console.log('Firebase service worker activated');
  // Take control of all pages immediately
  event.waitUntil(self.clients.claim());
});

// Retrieve Firebase Messaging object
const messaging = firebase.messaging();
console.log('Firebase messaging object created');

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  
  const notificationTitle = payload.notification.title || 'New Notification';
  const iconUrl = payload.notification.icon || `${self.location.origin}/static/images/icon.png`;
  const notificationOptions = {
    body: payload.notification.body || 'You have a new message',
    icon: iconUrl,
    badge: `${self.location.origin}/static/images/icon.png`,
    tag: payload.notification.tag || 'appointment-notification',
    requireInteraction: true,
    renotify: true,
    actions: [
      {
        action: 'view',
        title: 'View',
        icon: `${self.location.origin}/static/images/icon.png`
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ],
    data: payload.data || {}
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  console.log('[firebase-messaging-sw.js] Notification click received.');

  event.notification.close();

  if (event.action === 'view' || !event.action) {
    // Open the app when notification is clicked
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
        // Check if there's already a window/tab open with the target URL
        for (const client of clientList) {
          if (client.url === self.location.origin + '/' && 'focus' in client) {
            return client.focus();
          }
        }
        
        // If no window/tab is open, open a new one
        if (clients.openWindow) {
          const data = event.notification.data;
          let url = '/';
          
          // Navigate to specific page based on notification data
          if (data && data.notification_id) {
            url = '/notifications-page/';
          }
          
          return clients.openWindow(self.location.origin + url);
        }
      })
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    console.log('Notification dismissed');
  }
});

// Handle push event (alternative to onBackgroundMessage)
self.addEventListener('push', (event) => {
  if (event.data) {
    console.log('[firebase-messaging-sw.js] Push event received:', event.data.text());
    
    try {
      const payload = event.data.json();
      
      if (payload.notification) {
        const notificationTitle = payload.notification.title || 'New Notification';
        const iconUrl = payload.notification.icon || `${self.location.origin}/static/images/icon.png`;
        const notificationOptions = {
          body: payload.notification.body || 'You have a new message',
          icon: iconUrl,
          badge: `${self.location.origin}/static/images/icon.png`,
          tag: 'appointment-notification',
          requireInteraction: true,
          renotify: true,
          data: payload.data || {}
        };

        event.waitUntil(
          self.registration.showNotification(notificationTitle, notificationOptions)
        );
      }
    } catch (error) {
      console.error('[firebase-messaging-sw.js] Error parsing push data:', error);
    }
  }
});