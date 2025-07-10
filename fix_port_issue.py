#!/usr/bin/env python3
"""
Fix port 5000 issue on macOS
Provides solutions for AirPlay Receiver blocking port 5000
"""

import os
import socket
import subprocess
import sys

def check_port(port):
    """Check if port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def find_process_on_port(port):
    """Find what process is using the port"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        return result.stdout
    except:
        return "Could not check process"

def main():
    print("🔧 PRD QC Table Transformer - Port Issue Fixer")
    print("=" * 60)
    
    # Check port 5000
    if check_port(5000):
        print("❌ Port 5000 is currently in use")
        print("\n📋 Process using port 5000:")
        process_info = find_process_on_port(5000)
        print(process_info)
        
        print("\n💡 SOLUTIONS:")
        print("=" * 40)
        
        print("1. 🔧 Use our app with auto port detection (RECOMMENDED):")
        print("   python3 start_web_app.py")
        print("   → App will automatically use port 8000, 8080, 3000, etc.")
        
        print("\n2. 🍎 Turn off AirPlay Receiver (macOS):")
        print("   System Preferences > Sharing > AirPlay Receiver (uncheck)")
        print("   OR")
        print("   System Settings > General > AirDrop & Handoff > AirPlay Receiver (off)")
        
        print("\n3. 🚫 Kill the process manually:")
        print("   sudo lsof -ti:5000 | xargs kill -9")
        print("   (Use with caution - may affect other services)")
        
    else:
        print("✅ Port 5000 is available!")
        print("You can run the app normally:")
        print("   python3 start_web_app.py")
    
    # Check alternative ports
    print(f"\n📊 Port availability check:")
    print("-" * 30)
    for port in [5000, 8000, 8080, 3000, 5001, 8001, 9000]:
        status = "🔴 BUSY" if check_port(port) else "✅ FREE"
        print(f"Port {port}: {status}")
    
    print(f"\n🚀 QUICK START:")
    print("-" * 20)
    print("Just run: python3 start_web_app.py")
    print("The app will automatically find a free port!")

if __name__ == "__main__":
    main() 