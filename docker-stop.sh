#!/bin/bash

echo "🛑 Stopping PRD QC Table Transformer..."
echo "======================================"

# Stop and remove containers
docker-compose down

if [ $? -eq 0 ]; then
    echo "✅ All containers stopped successfully!"
    echo ""
    echo "📊 Current status:"
    docker-compose ps
    echo ""
    echo "🚀 To start again:"
    echo "   ./docker-deploy.sh"
else
    echo "❌ Failed to stop containers!"
    exit 1
fi 