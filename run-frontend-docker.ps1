# PowerShell script to run frontend in Docker
Write-Host "Building and running ECHO frontend in Docker..." -ForegroundColor Green

# Stop and remove existing container if it exists
docker stop echo-frontend-dev 2>$null
docker rm echo-frontend-dev 2>$null

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -f frontend/Dockerfile.dev -t echo-frontend:dev frontend/

# Run the container
Write-Host "Starting container..." -ForegroundColor Yellow
docker run -d `
  --name echo-frontend-dev `
  -p 3000:3000 `
  -v "${PWD}/frontend:/app" `
  -v /app/node_modules `
  -v /app/.next `
  -e WATCHPACK_POLLING=true `
  echo-frontend:dev

Write-Host "Frontend is now running at http://localhost:3000" -ForegroundColor Green
Write-Host "To view logs: docker logs -f echo-frontend-dev" -ForegroundColor Cyan
Write-Host "To stop: docker stop echo-frontend-dev" -ForegroundColor Cyan 