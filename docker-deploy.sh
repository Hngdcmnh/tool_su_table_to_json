#!/bin/bash

echo "🚀 Deploying PRD QC Table Transformer..."
echo "========================================"

# Stop any running containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the service
echo "🔨 Building and starting service..."
docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 Container status:"
    docker-compose ps
    echo ""
    echo "🌐 Application is running at:"
    echo "   http://localhost:5000"
    echo "   http://YOUR_SERVER_IP:5000"
    echo ""
    echo "📋 Useful commands:"
    echo "   docker-compose logs -f          # View logs"
    echo "   docker-compose stop             # Stop service"
    echo "   docker-compose restart          # Restart service"
    echo "   docker-compose down             # Stop and remove containers"
else
    echo "❌ Deployment failed!"
    exit 1
fi 