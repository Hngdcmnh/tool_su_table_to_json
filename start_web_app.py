#!/usr/bin/env python3
"""
Starter script for PRD QC Table Transformer Web App
"""

import os
import webbrowser
import time
import socket
from threading import Timer
from app import app

def find_free_port():
    """Find a free port to run the server"""
    for port in [5000, 8000, 8080, 3000, 5001, 8001]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return 5000  # fallback

def open_browser(port):
    """Open browser after server starts"""
    webbrowser.open(f'http://localhost:{port}')

def main():
    port = find_free_port()
    
    print("🌐 PRD QC Table Transformer Web App")
    print("=" * 50)
    print("🚀 Starting Flask server...")
    print(f"📁 Upload interface will open at: http://localhost:{port}")
    print("💾 Files will be processed automatically")
    print("📋 Results can be copied or downloaded")
    if port != 5000:
        print(f"💡 Note: Using port {port} (5000 was busy - probably AirPlay)")
    print("=" * 50)
    
    # Open browser after 1 second delay
    Timer(1.0, lambda: open_browser(port)).start()
    
    # Start Flask app
    app.run(debug=False, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main() 