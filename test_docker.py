#!/usr/bin/env python3
"""
Test Docker deployment
"""

import subprocess
import time
import requests
import sys

def run_command(cmd, description):
    """Run shell command and return success status"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def test_docker_deployment():
    """Test Docker deployment process"""
    print("🐳 Testing Docker Deployment")
    print("=" * 50)
    
    # Test 1: Check Docker
    if not run_command("docker --version", "Check Docker installation"):
        print("💡 Please install Docker first")
        return False
    
    # Test 2: Check Docker Compose
    if not run_command("docker-compose --version", "Check Docker Compose"):
        print("💡 Please install Docker Compose first")
        return False
    
    # Test 3: Build image
    if not run_command("docker build -t prd-transformer:test .", "Build Docker image"):
        return False
    
    # Test 4: Start container
    print("📋 Starting test container...")
    if not run_command("docker run -d -p 8888:5000 --name prd-test prd-transformer:test", "Start test container"):
        return False
    
    # Test 5: Wait for startup
    print("⏳ Waiting for container to start...")
    time.sleep(5)
    
    # Test 6: Check health
    try:
        response = requests.get("http://localhost:8888", timeout=10)
        if response.status_code == 200:
            print("✅ Container is responding")
        else:
            print(f"❌ Container responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to container: {e}")
        return False
    
    # Cleanup
    print("🧹 Cleaning up test container...")
    run_command("docker stop prd-test", "Stop test container")
    run_command("docker rm prd-test", "Remove test container")
    run_command("docker rmi prd-transformer:test", "Remove test image")
    
    return True

def show_deployment_guide():
    """Show deployment instructions"""
    print("\n🚀 DOCKER DEPLOYMENT GUIDE")
    print("=" * 50)
    print("1. Development deployment:")
    print("   ./docker-deploy.sh")
    print("   → Access at http://localhost:5000")
    print("")
    print("2. Production deployment:")
    print("   ./deploy-production.sh")
    print("   → Access at http://YOUR_SERVER_IP")
    print("")
    print("3. Stop containers:")
    print("   ./docker-stop.sh")
    print("")
    print("🌐 Server Access:")
    print("   - Make sure port 80 is open in firewall")
    print("   - Update DNS to point to your server IP")
    print("   - Consider SSL certificate for HTTPS")
    print("")
    print("📊 Monitoring:")
    print("   docker-compose logs -f              # View logs")
    print("   docker-compose ps                   # Check status")
    print("   docker stats                        # Resource usage")

if __name__ == "__main__":
    if test_docker_deployment():
        print("\n✅ Docker deployment test passed!")
        show_deployment_guide()
    else:
        print("\n❌ Docker deployment test failed!")
        print("💡 Check Docker installation and try again")
        sys.exit(1) 