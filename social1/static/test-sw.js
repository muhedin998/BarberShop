// Simple test service worker
console.log('Test service worker loaded');

self.addEventListener('install', function(event) {
  console.log('Test service worker installing');
  self.skipWaiting(); // Force activation
});

self.addEventListener('activate', function(event) {
  console.log('Test service worker activated');
  event.waitUntil(self.clients.claim()); // Take control immediately
});

self.addEventListener('push', function(event) {
  console.log('Test service worker received push event');
});

console.log('Test service worker script executed');