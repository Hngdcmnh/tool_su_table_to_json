#!/bin/bash

echo "🚀 Deploying PRD QC Table Transformer to Production..."
echo "===================================================="

# Create necessary directories
mkdir -p uploads logs

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start the service in production mode
echo "🔨 Building and starting production service..."
docker-compose -f docker-compose.prod.yml up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Production deployment successful!"
    echo ""
    echo "📊 Container status:"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    echo "🌐 Application is running at:"
    echo "   http://YOUR_SERVER_IP"
    echo "   http://localhost (if running locally)"
    echo ""
    echo "📋 Production commands:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f    # View logs"
    echo "   docker-compose -f docker-compose.prod.yml stop       # Stop service"
    echo "   docker-compose -f docker-compose.prod.yml restart    # Restart service"
    echo "   docker-compose -f docker-compose.prod.yml down       # Stop and remove"
    echo ""
    echo "⚠️  Important for server deployment:"
    echo "   - Make sure port 80 is open in firewall"
    echo "   - Update YOUR_SERVER_IP with actual server IP"
    echo "   - Consider setting up SSL certificate for HTTPS"
else
    echo "❌ Production deployment failed!"
    exit 1
fi 