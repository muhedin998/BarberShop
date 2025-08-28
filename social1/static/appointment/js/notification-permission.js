// Notification Permission Handler

class NotificationPermissionHandler {
  constructor() {
    this.permissionGranted = false;
    this.permissionRequested = false;
    this.init();
  }

  async init() {
    console.log('NotificationPermissionHandler init called');
    
    // Check if FCM Manager detected an unsupported browser
    if (window.fcmManager && !window.fcmManager.isInitialized && !window.fcmManager.isSupported) {
      console.log('Browser does not support push notifications, skipping permission UI setup');
      return;
    }
    
    // Check current permission status
    this.checkPermissionStatus();
    
    // Wait for FCM to be ready before showing UI (especially important for mobile)
    if (window.fcmManager && !window.fcmManager.isInitialized) {
      console.log('Waiting for FCM initialization before showing UI...');
      try {
        await new Promise((resolve) => {
          const checkFCM = () => {
            if (window.fcmManager.isInitialized) {
              resolve();
            } else {
              setTimeout(checkFCM, 100);
            }
          };
          checkFCM();
          
          // Timeout after 5 seconds to not block UI indefinitely
          setTimeout(resolve, 5000);
        });
      } catch (error) {
        console.error('Error waiting for FCM:', error);
      }
    }
    
    // Only proceed if FCM was successfully initialized or permission is already granted
    if (!window.fcmManager || (!window.fcmManager.isInitialized && !this.permissionGranted)) {
      console.log('FCM not available, skipping notification setup');
      return;
    }
    
    // If permission is already granted, generate token immediately
    if (this.permissionGranted) {
      this.generateTokenForGrantedPermission();
    } else {
      // Setup permission request UI only if permission not granted and FCM is available
      this.setupPermissionUI();
    }
    
    // Auto-request permission for logged in users (optional)
    this.autoRequestPermission();
    
    // Show initialization message for debugging
    this.showToast('Sistem obaveštenja je inicijalizovan', 'info', 3000);
  }

  checkPermissionStatus() {
    if ('Notification' in window) {
      this.permissionGranted = Notification.permission === 'granted';
      console.log('Notification API available. Permission:', Notification.permission);
    } else {
      console.warn('Ovaj pretraživač ne podržava obaveštenja');
    }
  }

  setupPermissionUI() {
    // Create notification permission banner
    this.createPermissionBanner();
    
    // Setup permission button handlers
    this.setupButtonHandlers();
  }

  createPermissionBanner() {
    // Only show banner if permission is not granted and not already requested
    if (this.permissionGranted || this.hasUserDismissedBanner()) {
      return;
    }

    const banner = document.createElement('div');
    banner.id = 'notification-permission-banner';
    banner.className = 'notification-banner';
    banner.innerHTML = `
      <div class="notification-banner-content">
        <div class="notification-banner-text">
          <strong>Ostanite u toku!</strong>
          <p>Omogućite obaveštenja da biste primali važne informacije o vašim terminima.</p>
        </div>
        <div class="notification-banner-actions">
          <button id="enable-notifications-btn" class="btn btn-primary btn-sm">
            Omogući obaveštenja
          </button>
          <button id="dismiss-notification-banner" class="btn btn-secondary btn-sm">
            Ne sada
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

    // Setup button handlers AFTER the banner is in the DOM
    this.setupButtonHandlers();

    // Show banner with animation
    setTimeout(() => {
      banner.classList.add('show');
    }, 100);
  }

  setupButtonHandlers() {
    // Enable notifications button
    const enableBtn = document.getElementById('enable-notifications-btn');
    console.log('Enable button found:', !!enableBtn);
    
    if (enableBtn) {
      console.log('Setting up enable button handlers');
      
      // Remove any existing event listeners to prevent duplicates
      enableBtn.replaceWith(enableBtn.cloneNode(true));
      const newEnableBtn = document.getElementById('enable-notifications-btn');
      
      // Single handler for mobile compatibility - avoid multiple event listeners
      const handlePermissionRequest = (e) => {
        console.log('Enable button clicked/touched, event type:', e.type);
        
        // Prevent any potential conflicts with other handlers
        e.preventDefault();
        e.stopPropagation();
        
        // Ensure we're in a user gesture context for mobile browsers
        this.requestPermissionWithUserGesture(e);
      };
      
      // Use only click event for maximum compatibility
      // Mobile devices will trigger click after touchend automatically
      newEnableBtn.addEventListener('click', handlePermissionRequest, { once: true });
      
      // Add touch event for mobile - use once to prevent multiple registrations
      newEnableBtn.addEventListener('touchend', handlePermissionRequest, { once: true, passive: false });
      
    } else {
      console.error('Enable button not found in DOM');
      this.showToast('Dugme nije pronađeno - molimo osvežite stranicu', 'error', 5000);
    }

    // Dismiss banner button
    const dismissBtn = document.getElementById('dismiss-notification-banner');
    console.log('Dismiss button found:', !!dismissBtn);
    if (dismissBtn) {
      const handleDismiss = (e) => {
        console.log('Dismiss button clicked/touched');
        e.preventDefault();
        e.stopPropagation();
        this.dismissBanner();
      };
      
      dismissBtn.addEventListener('click', handleDismiss);
      dismissBtn.addEventListener('touchend', handleDismiss);
      
      dismissBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
      });
    }
  }

  // Method specifically for mobile compatibility
  async requestPermissionWithUserGesture(event) {
    try {
      console.log('requestPermissionWithUserGesture called with event:', event.type);
      
      // Disable the button immediately to prevent double-clicks
      const button = event.target.closest('button');
      if (button) {
        button.disabled = true;
        button.textContent = 'Zahtevam dozvolu...';
      }
      
      // For mobile browsers, ensure FCM is ready before requesting permission
      if (window.fcmManager && !window.fcmManager.isInitialized) {
        console.log('FCM not initialized, waiting for initialization...');
        await new Promise(resolve => {
          const checkInitialized = () => {
            if (window.fcmManager.isInitialized) {
              resolve();
            } else {
              setTimeout(checkInitialized, 100);
            }
          };
          checkInitialized();
          
          // Timeout after 3 seconds
          setTimeout(resolve, 3000);
        });
      }
      
      // Call the main permission request method immediately
      // Don't show toast before - keep user gesture context clean
      const result = await this.requestPermission();
      
      // Re-enable button if permission failed
      if (!result && button) {
        button.disabled = false;
        button.textContent = 'Omogući obaveštenja';
      }
      
      return result;
    } catch (error) {
      console.error('Error in requestPermissionWithUserGesture:', error);
      
      // Re-enable button on error
      const button = event.target.closest('button');
      if (button) {
        button.disabled = false;
        button.textContent = 'Omogući obaveštenja';
      }
      
      // Show error toast after button is restored
      this.showToast(`Greška: ${error.message}`, 'error', 5000);
      return false;
    }
  }

  async requestPermission() {
    try {
      console.log('requestPermission called');
      
      // Check current permission status
      const currentPermission = Notification.permission;
      console.log('Current permission status:', currentPermission);

      if (currentPermission === 'denied') {
        this.showPermissionBlockedMessage();
        return false;
      }

      // For mobile browsers, request permission directly
      console.log('Requesting browser notification permission directly');
      
      let permission;
      try {
        permission = await Notification.requestPermission();
        console.log('Notification.requestPermission() returned:', permission);
      } catch (error) {
        console.error('Error requesting permission:', error);
        this.showErrorMessage('Neuspešan zahtev za dozvolu obaveštenja. Molimo pokušajte ponovo.');
        return false;
      }
      
      console.log('Browser permission result:', permission);
      
      if (permission !== 'granted') {
        if (permission === 'denied') {
          this.showPermissionBlockedMessage();
        } else {
          this.showErrorMessage('Dozvola za obaveštenja nije data. Molimo pokušajte ponovo.');
        }
        return false;
      }

      // Success - permission granted
      console.log('Permission granted successfully');
      this.permissionGranted = true;
      this.permissionRequested = true;
      
      // Hide banner
      this.hideBanner();
      
      // Show success message
      this.showSuccessMessage();
      
      // Try to get FCM token if available, but don't fail if not
      if (window.fcmManager && window.fcmManager.isInitialized) {
        try {
          console.log('Attempting to generate FCM token');
          const token = await window.fcmManager.generateToken();
          console.log('FCM token result:', !!token);
        } catch (tokenError) {
          console.error('Error generating FCM token:', tokenError);
          // Don't show error - browser permission was still successful
        }
      }
      
      return true;
    } catch (error) {
      console.error('Error in requestPermission:', error);
      this.showErrorMessage('Došlo je do greške prilikom omogućavanja obaveštenja.');
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
    this.showToast('Obaveštenja su uspešno omogućena! Sada ćete primati važna ažuriranja.', 'success');
  }

  showErrorMessage(customMessage = null) {
    const message = customMessage || 'Neuspešno omogućavanje obaveštenja. Molimo pokušajte ponovo ili proverite podešavanja vašeg pretraživača.';
    this.showToast(message, 'error');
  }

  showPermissionBlockedMessage() {
    const instructions = this.getBrowserInstructions();
    this.showToast(
      `Obaveštenja su blokirana za ovaj sajt. ${instructions}`,
      'error',
      10000 // Show for 10 seconds
    );
  }

  getBrowserInstructions() {
    const userAgent = navigator.userAgent.toLowerCase();
    
    if (userAgent.includes('chrome')) {
      return 'Kliknite na ikonu brave u adresnoj liniji → Obaveštenja → Dozvoli, zatim osvežite stranicu.';
    } else if (userAgent.includes('firefox')) {
      return 'Kliknite na ikonu štita u adresnoj liniji → Isključite blokiranje obaveštenja, zatim osvežite stranicu.';
    } else if (userAgent.includes('safari')) {
      return 'Idite na Safari → Podešavanja → Veb sajtovi → Obaveštenja → Dozvolite za ovaj sajt, zatim osvežite stranicu.';
    } else if (userAgent.includes('edge')) {
      return 'Kliknite na ikonu brave u adresnoj liniji → Obaveštenja → Dozvoli, zatim osvežite stranicu.';
    }
    
    return 'Molimo proverite podešavanja vašeg pretraživača da biste dozvolili obaveštenja za ovaj sajt, zatim osvežite stranicu.';
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
      // Check if we already have a token
      if (window.fcmManager && window.fcmManager.currentToken) {
        return true;
      }
      
      if (!window.fcmManager) {
        return false;
      }

      if (!window.fcmManager.isInitialized) {
        // Wait a bit for FCM Manager to initialize
        await new Promise(resolve => {
          const checkInitialized = () => {
            if (window.fcmManager.isInitialized) {
              resolve();
            } else {
              setTimeout(checkInitialized, 500);
            }
          };
          checkInitialized();
          
          // Timeout after 10 seconds
          setTimeout(resolve, 10000);
        });
      }

      if (!window.fcmManager.isInitialized) {
        return false;
      }

      const token = await window.fcmManager.generateToken();
      
      if (token) {
        // Show a subtle success message (not as prominent as the banner success)
        this.showToast('Push obaveštenja su spremna! Primaćete važna ažuriranja.', 'success', 3000);
        return true;
      } else {
        return false;
      }
      
    } catch (error) {
      return false;
    }
  }
}

// Add a manual check for updates button for browsers without push notification support
function addManualUpdateButton() {
  // Only add if not already present
  if (document.getElementById('manual-update-btn')) {
    return;
  }

  const updateBtn = document.createElement('button');
  updateBtn.id = 'manual-update-btn';
  updateBtn.textContent = '🔄 Check for Updates';
  updateBtn.title = 'Manually check for new notifications and updates';
  updateBtn.style.position = 'fixed';
  updateBtn.style.bottom = '20px';
  updateBtn.style.right = '20px';
  updateBtn.style.zIndex = '1000';
  updateBtn.style.background = '#28a745';
  updateBtn.style.color = 'white';
  updateBtn.style.border = 'none';
  updateBtn.style.padding = '12px 16px';
  updateBtn.style.borderRadius = '50px';
  updateBtn.style.fontSize = '14px';
  updateBtn.style.cursor = 'pointer';
  updateBtn.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  updateBtn.style.transition = 'all 0.3s ease';
  
  // Add hover effect
  updateBtn.addEventListener('mouseenter', () => {
    updateBtn.style.transform = 'scale(1.05)';
    updateBtn.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
  });
  
  updateBtn.addEventListener('mouseleave', () => {
    updateBtn.style.transform = 'scale(1)';
    updateBtn.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  });
  
  updateBtn.addEventListener('click', () => {
    updateBtn.textContent = '🔄 Checking...';
    updateBtn.disabled = true;
    
    // Simulate checking for updates
    setTimeout(() => {
      location.reload();
    }, 1000);
  });
  
  document.body.appendChild(updateBtn);
  
  // Auto-hide after 10 seconds, but show again if user interacts with page
  setTimeout(() => {
    updateBtn.style.opacity = '0.6';
  }, 10000);
  
  // Show on scroll or click
  let activityTimer;
  const showOnActivity = () => {
    updateBtn.style.opacity = '1';
    clearTimeout(activityTimer);
    activityTimer = setTimeout(() => {
      updateBtn.style.opacity = '0.6';
    }, 5000);
  };
  
  document.addEventListener('scroll', showOnActivity);
  document.addEventListener('click', showOnActivity);
}

// Initialize notification permission handler when DOM is ready AND FCM is ready
async function initializeNotificationHandler() {
  
  // Check authentication status
  const bodyHasAuthClass = document.body.classList.contains('authenticated');
  const metaTag = document.querySelector('meta[name="user-authenticated"]');
  const metaIsAuth = metaTag && metaTag.content === 'true';
  const isAuthenticated = bodyHasAuthClass || metaIsAuth;
  
  
  // Always initialize for testing - remove authentication requirement
  
  // Wait a moment for FCM manager to complete initialization
  setTimeout(async () => {
    // Check if FCM manager failed to initialize (unsupported browser)
    if (window.fcmManager && !window.fcmManager.isInitialized) {
      console.log('FCM Manager failed to initialize, adding manual update button for unsupported browser');
      addManualUpdateButton();
      return;
    }
    
    // Initialize notification handler immediately without waiting for FCM
    try {
      window.notificationPermissionHandler = new NotificationPermissionHandler();
    } catch (error) {
      // Browser/notification error occurred
    }
  }, 1000); // Give FCM time to initialize
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeNotificationHandler);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = NotificationPermissionHandler;
}