# 🐳 Docker Setup for ECHO Frontend

## Prerequisites

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Make sure Docker Desktop is running (check system tray)

2. **Verify Docker Installation**
   ```bash
   docker version
   docker-compose version
   ```

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Start Docker Desktop** and ensure it's running

2. **Run the development environment:**
   ```bash
   # For development with hot reload
   docker-compose -f docker-compose.dev.yml up --build frontend
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000 (if running full stack)

### Option 2: Using PowerShell Script

```powershell
# Run the PowerShell script
.\run-frontend-docker.ps1
```

### Option 3: Using Bash Script

```bash
# Make script executable and run
chmod +x run-frontend-docker.sh
./run-frontend-docker.sh
```

### Option 4: Manual Docker Commands

```bash
# Build the image
docker build -f frontend/Dockerfile.dev -t echo-frontend:dev frontend/

# Run the container
docker run -d \
  --name echo-frontend-dev \
  -p 3000:3000 \
  -v "$(pwd)/frontend:/app" \
  -v /app/node_modules \
  -v /app/.next \
  -e WATCHPACK_POLLING=true \
  echo-frontend:dev
```

## 🎥 Background Video Features

The Docker setup includes:
- ✅ Seamless background video looping
- ✅ Responsive videos (desktop: 1440x1080, mobile: 420x1118)
- ✅ No black screen between loops
- ✅ Tailwind CSS with proper PostCSS configuration
- ✅ Hot reload for development

## 🔧 Docker Commands

```bash
# View logs
docker logs -f echo-frontend-dev

# Stop container
docker stop echo-frontend-dev

# Remove container
docker rm echo-frontend-dev

# Rebuild image
docker build -f frontend/Dockerfile.dev -t echo-frontend:dev frontend/ --no-cache

# Full stack (all services)
docker-compose -f docker-compose.dev.yml up --build
```

## 🐛 Troubleshooting

### Docker Desktop Not Running
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.47/version"
```
**Solution:** Start Docker Desktop from Windows Start Menu

### Port Already in Use
```
Error: Port 3000 is already in use
```
**Solution:** 
```bash
# Stop existing container
docker stop echo-frontend-dev
# Or use different port
docker run -p 3001:3000 ...
```

### CSS Not Loading
The Docker setup includes the proper PostCSS configuration, but if you still see issues:
1. Clear browser cache (Ctrl+Shift+R)
2. Rebuild container: `docker-compose -f docker-compose.dev.yml up --build frontend`

## 🌐 Accessing the Application

Once running, visit: **http://localhost:3000**

You should see:
- 🎬 Background video playing seamlessly
- 🎨 Proper Tailwind CSS styling
- 📱 Responsive design
- ⚡ Hot reload on file changes

## 📁 File Structure

```
/
├── docker-compose.yml          # Production setup
├── docker-compose.dev.yml      # Development setup
├── run-frontend-docker.ps1     # PowerShell script
├── run-frontend-docker.sh      # Bash script
└── frontend/
    ├── Dockerfile              # Production Dockerfile
    ├── Dockerfile.dev          # Development Dockerfile
    ├── postcss.config.js       # PostCSS config (for Tailwind)
    └── src/
        ├── components/
        │   └── BackgroundVideo.tsx
        └── pages/
            └── _app.tsx
``` 