#!/bin/bash

echo "🐳 Building PRD QC Table Transformer Docker Image..."
echo "=================================================="

# Build the Docker image
docker build -t prd-transformer:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "📊 Image info:"
    docker images prd-transformer:latest
    echo ""
    echo "🚀 To run the container:"
    echo "   docker-compose up -d"
    echo "   OR"
    echo "   docker run -p 5000:5000 prd-transformer:latest"
else
    echo "❌ Docker build failed!"
    exit 1
fi 