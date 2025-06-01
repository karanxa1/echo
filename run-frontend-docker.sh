#!/bin/bash

echo "🚀 Building and running ECHO frontend in Docker..."

# Stop and remove existing container if it exists
docker stop echo-frontend-dev 2>/dev/null || true
docker rm echo-frontend-dev 2>/dev/null || true

# Build the Docker image
echo "📦 Building Docker image..."
docker build -f frontend/Dockerfile.dev -t echo-frontend:dev frontend/

# Run the container
echo "🔥 Starting container..."
docker run -d \
  --name echo-frontend-dev \
  -p 3000:3000 \
  -v "$(pwd)/frontend:/app" \
  -v /app/node_modules \
  -v /app/.next \
  -e WATCHPACK_POLLING=true \
  echo-frontend:dev

echo "✅ Frontend is now running at http://localhost:3000"
echo "📋 To view logs: docker logs -f echo-frontend-dev"
echo "🛑 To stop: docker stop echo-frontend-dev" 