// Notification Permission Handler

class NotificationPermissionHandler {
  constructor() {
    this.permissionGranted = false;
    this.permissionRequested = false;
    this.init();
  }

  init() {
    console.log('NotificationPermissionHandler.init() called');
    
    // Check current permission status
    this.checkPermissionStatus();
    
    // If permission is already granted, generate token immediately
    if (this.permissionGranted) {
      console.log('Notification permission already granted, generating FCM token automatically...');
      this.generateTokenForGrantedPermission();
    } else {
      console.log('Notification permission not granted, setting up UI...');
      // Setup permission request UI only if permission not granted
      this.setupPermissionUI();
    }
    
    // Auto-request permission for logged in users (optional)
    this.autoRequestPermission();
    
    console.log('NotificationPermissionHandler initialization complete');
  }

  checkPermissionStatus() {
    if ('Notification' in window) {
      this.permissionGranted = Notification.permission === 'granted';
      console.log('Current notification permission:', Notification.permission);
    } else {
      console.warn('This browser does not support notifications');
    }
  }

  setupPermissionUI() {
    // Create notification permission banner
    this.createPermissionBanner();
    
    // Setup permission button handlers
    this.setupButtonHandlers();
  }

  createPermissionBanner() {
    console.log('createPermissionBanner() called');
    console.log('  - Permission granted:', this.permissionGranted);
    console.log('  - User dismissed banner:', this.hasUserDismissedBanner());
    
    // Only show banner if permission is not granted and not already requested
    if (this.permissionGranted || this.hasUserDismissedBanner()) {
      console.log('Banner creation skipped - permission granted or user dismissed');
      return;
    }
    
    console.log('Creating notification permission banner...');

    const banner = document.createElement('div');
    banner.id = 'notification-permission-banner';
    banner.className = 'notification-banner';
    banner.innerHTML = `
      <div class="notification-banner-content">
        <div class="notification-banner-text">
          <strong>Stay Updated!</strong>
          <p>Enable notifications to receive important updates about your appointments.</p>
        </div>
        <div class="notification-banner-actions">
          <button id="enable-notifications-btn" class="btn btn-primary btn-sm">
            Enable Notifications
          </button>
          <button id="dismiss-notification-banner" class="btn btn-secondary btn-sm">
            Not Now
          </button>
        </div>
      </div>
    `;

    // Add CSS styles
    const style = document.createElement('style');
    style.textContent = `
      .notification-banner {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        transform: translateY(-100%);
        transition: transform 0.3s ease;
      }
      
      .notification-banner.show {
        transform: translateY(0);
      }
      
      .notification-banner-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
      }
      
      .notification-banner-text p {
        margin: 4px 0 0 0;
        font-size: 14px;
        opacity: 0.9;
      }
      
      .notification-banner-actions {
        display: flex;
        gap: 10px;
        align-items: center;
      }
      
      .notification-banner .btn {
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s ease;
      }
      
      .notification-banner .btn-primary {
        background: rgba(255,255,255,0.2);
        color: white;
      }
      
      .notification-banner .btn-primary:hover {
        background: rgba(255,255,255,0.3);
      }
      
      .notification-banner .btn-secondary {
        background: transparent;
        color: rgba(255,255,255,0.8);
        border: 1px solid rgba(255,255,255,0.3);
      }
      
      .notification-banner .btn-secondary:hover {
        background: rgba(255,255,255,0.1);
        color: white;
      }
      
      @media (max-width: 768px) {
        .notification-banner-content {
          flex-direction: column;
          gap: 12px;
          text-align: center;
        }
        
        .notification-banner-actions {
          width: 100%;
          justify-content: center;
        }
      }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(banner);

    // Show banner with animation
    setTimeout(() => {
      banner.classList.add('show');
    }, 100);
  }

  setupButtonHandlers() {
    console.log('Setting up banner button handlers...');
    
    // Enable notifications button
    const enableBtn = document.getElementById('enable-notifications-btn');
    if (enableBtn) {
      console.log('Enable notifications button found, adding click handler');
      enableBtn.addEventListener('click', () => {
        console.log('Enable notifications button clicked');
        this.requestPermission();
      });
    } else {
      console.log('Enable notifications button not found');
    }

    // Dismiss banner button
    const dismissBtn = document.getElementById('dismiss-notification-banner');
    if (dismissBtn) {
      console.log('Dismiss banner button found, adding click handler');
      dismissBtn.addEventListener('click', () => {
        console.log('Dismiss banner button clicked');
        this.dismissBanner();
      });
    } else {
      console.log('Dismiss banner button not found');
    }
  }

  async requestPermission() {
    try {
      console.log('NotificationPermissionHandler.requestPermission() called');
      
      if (!window.fcmManager) {
        console.error('FCM Manager not available');
        this.showErrorMessage('Notification system not available. Please refresh the page and try again.');
        return false;
      }

      console.log('FCM Manager status:', {
        isInitialized: window.fcmManager.isInitialized,
        isSupported: window.fcmManager.isSupported,
        currentToken: !!window.fcmManager.currentToken
      });

      if (!window.fcmManager.isInitialized) {
        console.error('FCM Manager not initialized');
        this.showErrorMessage('Notification system not ready. Please wait a moment and try again.');
        return false;
      }

      // Check current permission status
      const currentPermission = Notification.permission;
      console.log('Current notification permission:', currentPermission);

      if (currentPermission === 'denied') {
        this.showPermissionBlockedMessage();
        return false;
      }

      console.log('Calling fcmManager.requestPermission()...');
      // Request notification permission and get FCM token
      const token = await window.fcmManager.requestPermission();
      console.log('fcmManager.requestPermission() returned:', !!token);
      
      if (token) {
        this.permissionGranted = true;
        this.permissionRequested = true;
        
        // Hide banner
        this.hideBanner();
        
        // Show success message
        this.showSuccessMessage();
        
        console.log('Notification permission granted and FCM token registered successfully');
        return true;
      } else {
        // Check if permission was denied
        const newPermission = Notification.permission;
        console.log('Permission after request:', newPermission);
        
        if (newPermission === 'denied') {
          this.showPermissionBlockedMessage();
        } else if (newPermission === 'granted') {
          console.error('Permission granted but token generation failed');
          this.showErrorMessage('Notifications enabled but token registration failed. Please try again.');
        } else {
          this.showErrorMessage('Failed to enable notifications. Please try again.');
        }
        return false;
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      console.error('Error stack:', error.stack);
      this.showErrorMessage('An error occurred while enabling notifications.');
      return false;
    }
  }

  dismissBanner() {
    // Mark as dismissed in localStorage
    localStorage.setItem('notification_banner_dismissed', 'true');
    localStorage.setItem('notification_banner_dismissed_date', new Date().toISOString());
    
    this.hideBanner();
  }

  hideBanner() {
    const banner = document.getElementById('notification-permission-banner');
    if (banner) {
      banner.classList.remove('show');
      setTimeout(() => {
        banner.remove();
      }, 300);
    }
  }

  hasUserDismissedBanner() {
    const dismissed = localStorage.getItem('notification_banner_dismissed');
    const dismissedDate = localStorage.getItem('notification_banner_dismissed_date');
    
    if (!dismissed || !dismissedDate) {
      return false;
    }
    
    // Show banner again after 7 days
    const dismissedTime = new Date(dismissedDate);
    const now = new Date();
    const daysSinceDismissed = (now - dismissedTime) / (1000 * 60 * 60 * 24);
    
    return daysSinceDismissed < 7;
  }

  showSuccessMessage() {
    this.showToast('Notifications enabled successfully! You\'ll now receive important updates.', 'success');
  }

  showErrorMessage(customMessage = null) {
    const message = customMessage || 'Failed to enable notifications. Please try again or check your browser settings.';
    this.showToast(message, 'error');
  }

  showPermissionBlockedMessage() {
    const instructions = this.getBrowserInstructions();
    this.showToast(
      `Notifications are blocked for this site. ${instructions}`,
      'error',
      10000 // Show for 10 seconds
    );
  }

  getBrowserInstructions() {
    const userAgent = navigator.userAgent.toLowerCase();
    
    if (userAgent.includes('chrome')) {
      return 'Click the lock icon in the address bar → Notifications → Allow, then refresh the page.';
    } else if (userAgent.includes('firefox')) {
      return 'Click the shield icon in the address bar → Turn off blocking for Notifications, then refresh the page.';
    } else if (userAgent.includes('safari')) {
      return 'Go to Safari → Preferences → Websites → Notifications → Allow for this site, then refresh the page.';
    } else if (userAgent.includes('edge')) {
      return 'Click the lock icon in the address bar → Notifications → Allow, then refresh the page.';
    }
    
    return 'Please check your browser settings to allow notifications for this site, then refresh the page.';
  }

  showToast(message, type = 'info', duration = 5000) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;

    // Add toast styles if not already added
    if (!document.getElementById('toast-styles')) {
      const style = document.createElement('style');
      style.id = 'toast-styles';
      style.textContent = `
        .toast {
          position: fixed;
          top: 80px;
          right: 20px;
          max-width: 450px;
          padding: 16px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          z-index: 1001;
          animation: slideInRight 0.3s ease;
          word-wrap: break-word;
        }
        
        .toast-success {
          background: #d4edda;
          border: 1px solid #c3e6cb;
          color: #155724;
        }
        
        .toast-error {
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          color: #721c24;
        }
        
        .toast-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
        }
        
        .toast-message {
          flex: 1;
          font-size: 14px;
          line-height: 1.4;
        }
        
        .toast-close {
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          padding: 0;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        
        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Auto-remove toast after specified duration
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, duration);
  }

  autoRequestPermission() {
    // Auto-request permission for returning users (optional)
    // This is disabled by default to avoid being too aggressive
    
    // Uncomment the following lines if you want to auto-request permission
    // for logged-in users who haven't been asked before
    
    /*
    const hasAutoRequested = localStorage.getItem('notification_auto_requested');
    if (!hasAutoRequested && !this.permissionGranted && !this.hasUserDismissedBanner()) {
      // Wait a bit before auto-requesting
      setTimeout(() => {
        this.requestPermission();
        localStorage.setItem('notification_auto_requested', 'true');
      }, 3000);
    }
    */
  }

  async generateTokenForGrantedPermission() {
    try {
      console.log('generateTokenForGrantedPermission() called');
      
      // Check if we already have a token
      if (window.fcmManager && window.fcmManager.currentToken) {
        console.log('FCM token already exists, skipping generation');
        return true;
      }
      
      if (!window.fcmManager) {
        console.error('FCM Manager not available for automatic token generation');
        return false;
      }

      if (!window.fcmManager.isInitialized) {
        console.log('FCM Manager not initialized yet, waiting...');
        // Wait a bit for FCM Manager to initialize
        await new Promise(resolve => {
          const checkInitialized = () => {
            if (window.fcmManager.isInitialized) {
              console.log('FCM Manager is now initialized');
              resolve();
            } else {
              setTimeout(checkInitialized, 500);
            }
          };
          checkInitialized();
          
          // Timeout after 10 seconds
          setTimeout(() => {
            console.warn('FCM Manager initialization timeout');
            resolve();
          }, 10000);
        });
      }

      if (!window.fcmManager.isInitialized) {
        console.error('FCM Manager failed to initialize for automatic token generation');
        return false;
      }

      console.log('Generating FCM token automatically...');
      const token = await window.fcmManager.generateToken();
      
      if (token) {
        console.log('FCM token generated automatically:', token.substring(0, 50) + '...');
        
        // Show a subtle success message (not as prominent as the banner success)
        this.showToast('Push notifications are ready! You\'ll receive important updates.', 'success', 3000);
        
        return true;
      } else {
        console.error('Failed to generate FCM token automatically');
        return false;
      }
      
    } catch (error) {
      console.error('Error in automatic FCM token generation:', error);
      return false;
    }
  }
}

// Initialize notification permission handler when DOM is ready AND FCM is ready
function initializeNotificationHandler() {
  console.log('=== initializeNotificationHandler() called ===');
  
  // Check authentication status with better debugging
  const bodyHasAuthClass = document.body.classList.contains('authenticated');
  const metaTag = document.querySelector('meta[name="user-authenticated"]');
  const metaIsAuth = metaTag && metaTag.content === 'true';
  const isAuthenticated = bodyHasAuthClass || metaIsAuth;
  
  console.log('NotificationPermissionHandler - Authentication check:');
  console.log('  - Body has authenticated class:', bodyHasAuthClass);
  console.log('  - Meta tag exists:', !!metaTag);
  console.log('  - Meta tag content:', metaTag ? metaTag.content : 'none');
  console.log('  - Final authentication status:', isAuthenticated);
  
  if (isAuthenticated) {
    console.log('User is authenticated, checking FCM Manager status...');
    console.log('  - FCM Manager exists:', !!window.fcmManager);
    console.log('  - FCM Manager initialized:', window.fcmManager ? window.fcmManager.isInitialized : 'N/A');
    
    // Wait for FCM to be ready before initializing notification handler
    if (window.fcmManager && window.fcmManager.isInitialized) {
      console.log('FCM Manager already ready, initializing NotificationPermissionHandler NOW');
      try {
        window.notificationPermissionHandler = new NotificationPermissionHandler();
        console.log('NotificationPermissionHandler created successfully');
      } catch (error) {
        console.error('Error creating NotificationPermissionHandler:', error);
      }
    } else {
      console.log('FCM Manager not ready, waiting for fcmReady event...');
      window.addEventListener('fcmReady', () => {
        console.log('FCM ready event received, initializing NotificationPermissionHandler NOW');
        try {
          window.notificationPermissionHandler = new NotificationPermissionHandler();
          console.log('NotificationPermissionHandler created successfully after fcmReady');
        } catch (error) {
          console.error('Error creating NotificationPermissionHandler after fcmReady:', error);
        }
      });
      
      // Fallback timeout in case FCM fails to initialize
      setTimeout(() => {
        if (!window.notificationPermissionHandler) {
          console.warn('FCM initialization timeout, checking if we can initialize anyway...');
          console.log('  - FCM Manager exists:', !!window.fcmManager);
          console.log('  - FCM Manager initialized:', window.fcmManager ? window.fcmManager.isInitialized : 'N/A');
          
          if (window.fcmManager) {
            console.warn('Trying to initialize NotificationPermissionHandler anyway...');
            try {
              window.notificationPermissionHandler = new NotificationPermissionHandler();
              console.log('NotificationPermissionHandler created via timeout fallback');
            } catch (error) {
              console.error('Error creating NotificationPermissionHandler via fallback:', error);
            }
          } else {
            console.error('FCM Manager still not available after timeout');
          }
        } else {
          console.log('NotificationPermissionHandler already exists, timeout fallback not needed');
        }
      }, 5000);
    }
  } else {
    console.log('User is not authenticated, skipping notification permission handler');
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeNotificationHandler);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = NotificationPermissionHandler;
}