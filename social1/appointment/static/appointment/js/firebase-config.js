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
      
      // Enhanced browser detection for unsupported browsers
      const browserInfo = this.detectBrowser();
      
      // Check if browser is known to be unsupported
      if (browserInfo.isUnsupported) {
        this.showUnsupportedBrowserMessage(browserInfo);
        return false;
      }
      
      // Check if Firebase Messaging is supported
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        this.showUnsupportedBrowserMessage(browserInfo);
        return false;
      }
      
      
      // Browser detection for debugging and mobile-specific handling
      const userAgent = navigator.userAgent.toLowerCase();
      const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
      

      // Check for HTTPS requirement (critical for mobile browsers)
      if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
        return false;
      }

      // Register service worker FIRST, before Firebase
      await this.registerServiceWorker();

      // Import Firebase modules with error handling for mobile
      let initializeApp, getMessaging, getToken, onMessage, isSupported;
      try {
        const firebaseApp = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js');
        const firebaseMessaging = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging.js');
        
        initializeApp = firebaseApp.initializeApp;
        getMessaging = firebaseMessaging.getMessaging;
        getToken = firebaseMessaging.getToken;
        onMessage = firebaseMessaging.onMessage;
        isSupported = firebaseMessaging.isSupported;
      } catch (importError) {
        return false;
      }

      // Check if messaging is supported
      this.isSupported = await isSupported();
      
      if (!this.isSupported) {
        return false;
      }

      // Initialize Firebase
      const app = initializeApp(firebaseConfig);
      this.messaging = getMessaging(app);

      this.isInitialized = true;
      return true;

    } catch (error) {
      
      // More specific error logging for mobile debugging
      
      return false;
    }
  }

  async registerServiceWorker() {
    try {
      const swUrl = `${window.location.origin}/firebase-messaging-sw.js`;
      
      // Check if service worker is already registered
      const existingRegistration = await navigator.serviceWorker.getRegistration('/');
      if (existingRegistration) {
        
        // Wait for it to be active
        if (existingRegistration.active) {
          return existingRegistration;
        } else {
          await this.waitForServiceWorkerActive(existingRegistration);
          return existingRegistration;
        }
      }
      
      
      // For mobile browsers, add additional options
      const registrationOptions = {
        scope: '/',
        // Help mobile browsers with service worker lifecycle
        updateViaCache: 'none'
      };
      
      const registration = await navigator.serviceWorker.register(swUrl, registrationOptions);
      
      // Wait for the service worker to be active
      await this.waitForServiceWorkerActive(registration);
      
      return registration;
    } catch (error) {
      
      // More specific error handling for mobile browsers
      
      throw error;
    }
  }

  async waitForServiceWorkerActive(registration) {
    return new Promise((resolve, reject) => {
      let resolved = false;
      
      const resolveOnce = () => {
        if (!resolved) {
          resolved = true;
          resolve();
        }
      };
      
      if (registration.active) {
        resolveOnce();
        return;
      }
      
      const serviceWorker = registration.installing || registration.waiting;
      if (serviceWorker) {
        serviceWorker.addEventListener('statechange', function() {
          if (this.state === 'activated') {
            resolveOnce();
          } else if (this.state === 'redundant') {
            resolveOnce(); // Still resolve, but it might not work
          }
        });
        
        // Also check periodically in case the event doesn't fire
        const checkInterval = setInterval(() => {
          if (registration.active) {
            clearInterval(checkInterval);
            resolveOnce();
          }
        }, 500);
        
        // Timeout after 10 seconds
        setTimeout(() => {
          clearInterval(checkInterval);
          resolveOnce();
        }, 10000);
        
      } else {
        // Still wait a bit in case it becomes active
        setTimeout(() => {
          if (registration.active) {
            resolveOnce();
          } else {
            resolveOnce();
          }
        }, 2000);
      }
    });
  }

  async requestPermission() {
    try {

      if (!this.isInitialized) {
        return null;
      }

      // Check if permission is already granted
      if (Notification.permission === 'granted') {
        return await this.generateToken();
      }

      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        return await this.generateToken();
      } else {
        return null;
      }
    } catch (error) {
      return null;
    }
  }

  async generateToken() {
    try {
      
      if (!this.messaging) {
        throw new Error('FCM not initialized');
      }

      // Check service worker status before generating token
      const registrations = await navigator.serviceWorker.getRegistrations();
      
      if (registrations.length === 0) {
        throw new Error('No service worker registrations found');
      }
      
      const activeRegistration = registrations.find(reg => reg.active);
      
      if (!activeRegistration) {
        await this.registerServiceWorker();
      }

      const { getToken } = await import('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging.js');
      
      // Get the service worker registration
      const swRegistration = await navigator.serviceWorker.getRegistration('/');
      
      if (!swRegistration || !swRegistration.active) {
        throw new Error('Service worker not properly registered or active');
      }

      // For mobile browsers, always try with VAPID key first for better compatibility
      let token;
      try {
        token = await getToken(this.messaging, {
          vapidKey: 'BKAhiDB3rapdGVKIyzRrNb2EJlIkvDcV4ujdy_lz7dWN5wD_9uI6spViYbpwC_ckZ1md0Nn-Ara2E2wSdaCNNw4',
          serviceWorkerRegistration: swRegistration
        });
      } catch (vapidError) {
        
        // Fallback: try without VAPID key
        try {
          token = await getToken(this.messaging, {
            serviceWorkerRegistration: swRegistration
          });
        } catch (fallbackError) {
          throw fallbackError;
        }
      }

      if (token) {
        this.currentToken = token;
        await this.registerTokenWithBackend(token);
        return token;
      } else {
        return null;
      }
    } catch (error) {
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
        return data;
      } else {
        return null;
      }
    } catch (error) {
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
        this.currentToken = null;
        return data;
      } else {
        return null;
      }
    } catch (error) {
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
        // Show notification when app is in foreground
        this.showForegroundNotification(payload);
      });

    } catch (error) {
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

  detectBrowser() {
    const userAgent = navigator.userAgent.toLowerCase();
    const vendor = navigator.vendor?.toLowerCase() || '';
    
    // Known unsupported browsers
    const unsupportedBrowsers = {
      'duckduckgo': {
        name: 'DuckDuckGo Browser',
        reason: 'DuckDuckGo pretraživač blokira API-je za praćenje uključujući push obaveštenja zbog zaštite privatnosti.',
        recommendations: ['Chrome', 'Firefox', 'Samsung Internet']
      },
      'arc': {
        name: 'Arc Browser',
        reason: 'Arc pretraživač ima ograničenu podršku za push obaveštenja na mobilnim uređajima.',
        recommendations: ['Chrome', 'Firefox', 'Safari']
      },
      'focus': {
        name: 'Firefox Focus',
        reason: 'Firefox Focus je dizajniran za privatnost i blokira push obaveštenja.',
        recommendations: ['Firefox', 'Chrome']
      },
      'brave': {
        name: 'Brave Browser',
        reason: 'Brave pretraživač može blokirati push obaveštenja po defaultu zbog privatnosti.',
        recommendations: ['Chrome', 'Firefox']
      }
    };

    // Check for specific browsers
    let browserInfo = {
      name: 'Unknown Browser',
      isUnsupported: false,
      reason: '',
      recommendations: ['Chrome', 'Firefox'],
      isMobile: /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)
    };

    // Detect specific browsers
    if (userAgent.includes('duckduckgo') || userAgent.includes('ddg')) {
      browserInfo = { ...browserInfo, ...unsupportedBrowsers.duckduckgo, isUnsupported: true };
    } else if (userAgent.includes('arc')) {
      browserInfo = { ...browserInfo, ...unsupportedBrowsers.arc, isUnsupported: true };
    } else if (userAgent.includes('focus')) {
      browserInfo = { ...browserInfo, ...unsupportedBrowsers.focus, isUnsupported: true };
    } else if (userAgent.includes('brave')) {
      browserInfo = { ...browserInfo, ...unsupportedBrowsers.brave, isUnsupported: true };
    } else if (userAgent.includes('safari') && userAgent.includes('mobile') && !userAgent.includes('chrome')) {
      // Safari mobile has limited support
      browserInfo.name = 'Safari Mobile';
      browserInfo.isUnsupported = true;
      browserInfo.reason = 'Safari mobilni zahteva dodavanje veb sajta na vaš početni ekran za push obaveštenja.';
      browserInfo.recommendations = ['Chrome', 'Firefox'];
    } else if (userAgent.includes('chrome')) {
      browserInfo.name = 'Chrome';
    } else if (userAgent.includes('firefox')) {
      browserInfo.name = 'Firefox';
    } else if (userAgent.includes('edge')) {
      browserInfo.name = 'Edge';
    } else if (userAgent.includes('opera')) {
      browserInfo.name = 'Opera';
    }

    return browserInfo;
  }

  showUnsupportedBrowserMessage(browserInfo) {
    // Remove any existing unsupported browser messages
    const existingMessage = document.getElementById('unsupported-browser-message');
    if (existingMessage) {
      existingMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.id = 'unsupported-browser-message';
    messageDiv.className = 'unsupported-browser-banner';
    
    messageDiv.innerHTML = `
      <div class="unsupported-browser-content">
        <div class="unsupported-browser-icon">ℹ️</div>
        <div class="unsupported-browser-text">
          <strong>Push obaveštenja nisu dostupna</strong>
          <p>${browserInfo.reason}</p>
          <p><strong>Preporučeni pretraživači:</strong> ${browserInfo.recommendations.join(', ')}</p>
          <div class="unsupported-browser-actions">
            <button id="learn-more-browser" class="btn btn-outline btn-sm">Saznaj više</button>
            <button id="dismiss-browser-message" class="btn btn-secondary btn-sm">Ukloni</button>
          </div>
        </div>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .unsupported-browser-banner {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #ffc107 0%, #ff8f00 100%);
        color: #333;
        padding: 12px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        transform: translateY(-100%);
        transition: transform 0.3s ease;
      }
      
      .unsupported-browser-banner.show {
        transform: translateY(0);
      }
      
      .unsupported-browser-content {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        max-width: 1200px;
        margin: 0 auto;
      }
      
      .unsupported-browser-icon {
        font-size: 24px;
        flex-shrink: 0;
      }
      
      .unsupported-browser-text {
        flex: 1;
      }
      
      .unsupported-browser-text p {
        margin: 4px 0;
        font-size: 14px;
      }
      
      .unsupported-browser-actions {
        margin-top: 8px;
        display: flex;
        gap: 8px;
      }
      
      .unsupported-browser-banner .btn {
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
        border: none;
      }
      
      .unsupported-browser-banner .btn-outline {
        background: transparent;
        border: 1px solid #333;
        color: #333;
      }
      
      .unsupported-browser-banner .btn-secondary {
        background: rgba(0,0,0,0.1);
        color: #333;
      }
      
      @media (max-width: 768px) {
        .unsupported-browser-content {
          flex-direction: column;
          text-align: center;
        }
        
        .unsupported-browser-actions {
          justify-content: center;
        }
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(messageDiv);

    // Setup event handlers
    setTimeout(() => {
      const learnMoreBtn = document.getElementById('learn-more-browser');
      const dismissBtn = document.getElementById('dismiss-browser-message');
      
      if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', () => {
          this.showBrowserCompatibilityInfo(browserInfo);
        });
      }
      
      if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
          localStorage.setItem('browser_message_dismissed', 'true');
          messageDiv.classList.remove('show');
          setTimeout(() => messageDiv.remove(), 300);
        });
      }
      
      // Check if user previously dismissed
      const dismissed = localStorage.getItem('browser_message_dismissed');
      if (!dismissed) {
        messageDiv.classList.add('show');
      }
    }, 100);
  }

  showBrowserCompatibilityInfo(browserInfo) {
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div class="browser-info-modal-overlay">
        <div class="browser-info-modal">
          <h3>Informacije o kompatibilnosti pretraživača</h3>
          <div class="browser-info-content">
            <p><strong>Trenutni pretraživač:</strong> ${browserInfo.name}</p>
            <p><strong>Problem:</strong> ${browserInfo.reason}</p>
            
            <h4>Preporučeni pretraživači za Push obaveštenja:</h4>
            <ul>
              <li><strong>Chrome/Chromium:</strong> Puna podrška na svim platformama</li>
              <li><strong>Firefox:</strong> Puna podrška na desktop i mobilnim uređajima</li>
              <li><strong>Edge:</strong> Puna podrška na Windows i mobilnim uređajima</li>
              <li><strong>Samsung Internet:</strong> Puna podrška na Android uređajima</li>
            </ul>
            
            <h4>Alternativni načini da ostanete u toku:</h4>
            <ul>
              <li>📧 Omogućite email obaveštenja u podešavanjima naloga</li>
              <li>🔄 Ručno osvežite stranicu da proverite ažuriranja</li>
              <li>📱 Koristite našu mobilnu aplikaciju ako je dostupna</li>
              <li>🌐 Dodajte ovu stranicu u bookmark i redovno proveravajte</li>
            </ul>
          </div>
          <button id="close-browser-modal" class="btn btn-primary">Razumem</button>
        </div>
      </div>
    `;
    
    // Add modal styles
    const modalStyle = document.createElement('style');
    modalStyle.textContent = `
      .browser-info-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
      }
      
      .browser-info-modal {
        background: white;
        border-radius: 8px;
        padding: 24px;
        max-width: 500px;
        width: 100%;
        max-height: 80vh;
        overflow-y: auto;
      }
      
      .browser-info-modal h3 {
        margin-top: 0;
        color: #333;
      }
      
      .browser-info-modal h4 {
        margin-top: 20px;
        margin-bottom: 8px;
        color: #555;
      }
      
      .browser-info-content {
        margin-bottom: 20px;
      }
      
      .browser-info-modal ul {
        margin: 8px 0;
        padding-left: 20px;
      }
      
      .browser-info-modal li {
        margin: 4px 0;
      }
      
      .browser-info-modal .btn {
        background: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
      }
    `;
    
    document.head.appendChild(modalStyle);
    document.body.appendChild(modal);
    
    // Close modal handler
    document.getElementById('close-browser-modal').addEventListener('click', () => {
      modal.remove();
      modalStyle.remove();
    });
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
      if (e.target === modal.querySelector('.browser-info-modal-overlay')) {
        modal.remove();
        modalStyle.remove();
      }
    });
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
    window.dispatchEvent(new CustomEvent('fcmReady', {
      detail: { fcmManager: window.fcmManager }
    }));
  }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FCMManager;
}