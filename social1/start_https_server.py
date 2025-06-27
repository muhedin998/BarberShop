#!/usr/bin/env python3
"""
Simple HTTPS server for testing FCM on local network
"""
import os
import sys
import subprocess

def main():
    # Check if certificates exist
    if not os.path.exists('social1/cert.pem') or not os.path.exists('social1/key.pem'):
        print("SSL certificates not found!")
        print("Run this first:")
        print("openssl req -x509 -newkey rsa:4096 -keyout social1/key.pem -out social1/cert.pem -days 365 -nodes -subj '/CN=192.168.0.34'")
        return False
    
    # Stop any existing Django server
    try:
        subprocess.run(['pkill', '-f', 'python3 manage.py runserver'], check=False)
        print("Stopped existing Django server")
    except:
        pass
    
    # Start HTTPS server
    print("Starting Django HTTPS server on https://192.168.0.34:8443")
    print("Note: You'll need to accept the self-signed certificate warning in your browser")
    print("Press Ctrl+C to stop")
    
    try:
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '--cert-file', 'social1/cert.pem',
            '--key-file', 'social1/key.pem',
            '192.168.0.34:8443'
        ]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: Use Django's built-in runserver with manual SSL
        print("You can manually start the HTTPS server by running:")
        print("python3 manage.py runserver_plus --cert-file social1/cert.pem --key-file social1/key.pem 192.168.0.34:8443")

if __name__ == "__main__":
    main()