// Test Notification Button for Admin Testing

function createTestNotificationButton() {
  // Only show for superusers (you can customize this condition)
  const isAdmin = document.querySelector('meta[name="user-is-admin"]')?.content === 'true';
  
  if (!isAdmin) {
    return;
  }

  const button = document.createElement('button');
  button.id = 'test-push-notification';
  button.className = 'btn btn-info btn-sm';
  button.style.cssText = `
    position: fixed;
    bottom: 80px;
    right: 20px;
    z-index: 1000;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    background: #17a2b8;
    color: white;
    cursor: pointer;
    font-size: 12px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  `;
  button.innerHTML = '🔔 Test Push';
  button.title = 'Test push notification (Admin only)';

  button.addEventListener('click', async () => {
    try {
      // Test if FCM is working
      if (!window.fcmManager || !window.fcmManager.currentToken) {
        alert('FCM not initialized or no token available. Please enable notifications first.');
        return;
      }

      // Create a test notification via the backend
      const response = await fetch('/admin/create-test-notification/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
          title: 'Test Notification',
          message: 'This is a test push notification from your appointment system!'
        })
      });

      if (response.ok) {
        const data = await response.json();
        showToast('Test notification sent successfully!', 'success');
      } else {
        showToast('Failed to send test notification', 'error');
      }
    } catch (error) {
      console.error('Error sending test notification:', error);
      showToast('Error sending test notification', 'error');
    }
  });

  document.body.appendChild(button);
}

function getCSRFToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  return csrfMeta ? csrfMeta.getAttribute('content') : '';
}

function showToast(message, type = 'info') {
  // Use the existing toast function if available, otherwise create a simple alert
  if (window.notificationPermissionHandler && typeof window.notificationPermissionHandler.showToast === 'function') {
    window.notificationPermissionHandler.showToast(message, type);
  } else {
    alert(message);
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Add a small delay to ensure other scripts are loaded
  setTimeout(createTestNotificationButton, 1000);
});