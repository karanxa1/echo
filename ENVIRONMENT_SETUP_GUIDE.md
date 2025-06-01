# 🔧 Environment Setup Guide

Complete guide for setting up environment variables for both **Backend** and **Frontend** of your ECHO application.

## 📁 File Structure

```
echo/
├── backend/
│   ├── config.env.example        # Backend environment template
│   └── config.env                # Your actual backend config (create this)
├── frontend/
│   ├── env.example               # Frontend environment template  
│   └── .env.local                # Your actual frontend config (create this)
└── README.md
```

## 🚀 Quick Setup (5 minutes)

### **Step 1: Backend Configuration**
```bash
# Navigate to backend directory
cd backend

# Copy the example file
cp config.env.example config.env

# Edit the file with your settings
nano config.env  # or use your preferred editor
```

### **Step 2: Frontend Configuration**
```bash
# Navigate to frontend directory
cd frontend

# Copy the example file
cp env.example .env.local

# Edit the file with your settings
nano .env.local  # or use your preferred editor
```

### **Step 3: Restart Services**
```bash
# Restart both containers to apply changes
docker restart echo_backend_dev echo_frontend_dev
```

## 🔧 Backend Environment (`backend/config.env`)

### **🌟 Minimal Required Setup**
```env
# Security (REQUIRED)
SECRET_KEY=your_super_secret_jwt_key_change_this_in_production

# AI Service (Choose at least one)
GEMINI_API_KEY=your_gemini_api_key_here
# OR
GROQ_API_KEY=your_groq_api_key_here

# Database (Default for Docker)
DATABASE_URL=postgresql://echo_user:echo_password@localhost:5432/echo_db
```

### **🎯 Recommended Free Setup**
```env
# Security
SECRET_KEY=your_super_secret_jwt_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Free AI Services (Best combination)
GEMINI_API_KEY=your_gemini_api_key_here        # 1M tokens/month free
GROQ_API_KEY=your_groq_api_key_here            # 14.4K tokens/minute free

# Database
DATABASE_URL=postgresql://echo_user:echo_password@localhost:5432/echo_db

# App Settings
DEBUG=True
FRONTEND_URL=http://localhost:3000
```

### **🔐 Production Setup**
```env
# Security (Use strong values)
SECRET_KEY=your_super_secure_production_secret_key_32_chars_minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Services
GEMINI_API_KEY=your_production_gemini_key
GROQ_API_KEY=your_production_groq_key
OPENAI_API_KEY=your_openai_key_if_needed

# Database (Use production PostgreSQL)
DATABASE_URL=postgresql://prod_user:secure_password@your-db-host:5432/echo_prod

# App Settings
DEBUG=False
FRONTEND_URL=https://your-domain.com
API_HOST=0.0.0.0
API_PORT=8000
```

## 🌐 Frontend Environment (`frontend/.env.local`)

### **🌟 Minimal Required Setup**
```env
# API Connection (REQUIRED)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **🎯 Recommended Development Setup**
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Development Settings
NODE_ENV=development
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_SHOW_ERRORS=true

# AI Provider Preferences
NEXT_PUBLIC_DEFAULT_AI_PROVIDER=gemini
NEXT_PUBLIC_ENABLE_GEMINI=true
NEXT_PUBLIC_ENABLE_GROQ=true

# UI Settings
NEXT_PUBLIC_DEFAULT_THEME=dark
NEXT_PUBLIC_ENABLE_ANIMATIONS=true
```

### **🔐 Production Setup**
```env
# API Configuration
NEXT_PUBLIC_API_URL=https://api.your-domain.com

# Production Settings
NODE_ENV=production
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_SHOW_ERRORS=false

# Security
NEXT_PUBLIC_API_RATE_LIMIT=60

# Analytics (Optional)
NEXT_PUBLIC_GA_TRACKING_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn
```

## 🆓 Getting Free AI API Keys

### **1. Google Gemini (Recommended)**
```
🌟 Best free option - High quality responses
📊 Free tier: 1 million tokens/month, 15 requests/minute
🔗 Get key: https://makersuite.google.com/app/apikey

Steps:
1. Go to Google AI Studio
2. Sign in with Google account  
3. Click "Create API Key"
4. Copy the key to GEMINI_API_KEY
```

### **2. Groq (Fastest)**
```
⚡ Ultra-fast responses - Best for high volume
📊 Free tier: 14,400 tokens/minute
🔗 Get key: https://console.groq.com/keys

Steps:
1. Go to Groq Console
2. Sign up for free account
3. Navigate to "API Keys"
4. Create new API key
5. Copy the key to GROQ_API_KEY
```

### **3. Hugging Face (Experimental)**
```
🧪 Access to many open-source models
📊 Free tier: 1,000 requests/month per model
🔗 Get key: https://huggingface.co/settings/tokens

Steps:
1. Go to Hugging Face
2. Create account and go to Settings
3. Create new token
4. Copy the token to HUGGINGFACE_API_KEY
```

## 🔒 Security Best Practices

### **🔑 JWT Secret Key Generation**
```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# 7ksyDNH4wL9pqK2mNzV8xJ3fG1eR6tY9uC4bS0aQ5hE
```

### **🛡️ Environment File Security**
```bash
# Never commit .env files to git
echo "config.env" >> backend/.gitignore
echo ".env.local" >> frontend/.gitignore

# Set proper file permissions (Linux/Mac)
chmod 600 backend/config.env
chmod 600 frontend/.env.local
```

## 🧪 Testing Your Setup

### **1. Test Backend Configuration**
```bash
# Check if backend loads environment
docker logs echo_backend_dev

# Test API health
curl http://localhost:8000/health

# Test AI providers (need auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/chat/free-ai/test
```

### **2. Test Frontend Configuration**
```bash
# Check if frontend starts
docker logs echo_frontend_dev

# Visit the application
curl http://localhost:3000
```

## 🔧 Troubleshooting

### **Backend Issues**

**❌ "SECRET_KEY not set"**
```bash
# Add to backend/config.env:
SECRET_KEY=your_secret_key_here
```

**❌ "Database connection failed"**
```bash
# Check database is running:
docker ps | grep postgres

# Verify DATABASE_URL in config.env
DATABASE_URL=postgresql://echo_user:echo_password@localhost:5432/echo_db
```

**❌ "AI provider not available"**
```bash
# Add at least one AI API key to config.env:
GEMINI_API_KEY=your_key_here
# OR
GROQ_API_KEY=your_key_here
```

### **Frontend Issues**

**❌ "API connection failed"**
```bash
# Check NEXT_PUBLIC_API_URL in frontend/.env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000

# Verify backend is running:
curl http://localhost:8000/health
```

**❌ "Environment variables not loading"**
```bash
# Ensure file is named correctly:
mv frontend/env.local frontend/.env.local

# Restart frontend:
docker restart echo_frontend_dev
```

## 📊 Environment Validation

### **Backend Validation Script**
```bash
# Run this in backend directory
python3 -c "
from config import settings
print(f'✅ SECRET_KEY: {len(settings.SECRET_KEY)} chars')
print(f'✅ Database: {settings.DATABASE_URL[:20]}...')
print(f'✅ Gemini: {'✓' if settings.GEMINI_API_KEY else '✗'}')
print(f'✅ Groq: {'✓' if settings.GROQ_API_KEY else '✗'}')
"
```

### **Frontend Validation**
```bash
# Check environment in browser console:
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
console.log('Debug mode:', process.env.NEXT_PUBLIC_DEBUG)
```

## 🎉 Complete Setup Checklist

### **Backend ✅**
- [ ] `backend/config.env` created from template
- [ ] `SECRET_KEY` set to secure random string
- [ ] At least one AI API key configured (Gemini/Groq recommended)
- [ ] `DATABASE_URL` set correctly
- [ ] Backend container restarted
- [ ] Health endpoint responds: `curl http://localhost:8000/health`

### **Frontend ✅**
- [ ] `frontend/.env.local` created from template  
- [ ] `NEXT_PUBLIC_API_URL` points to backend
- [ ] Frontend container restarted
- [ ] Application loads: `curl http://localhost:3000`

### **Integration ✅**
- [ ] Can register new user
- [ ] Can login successfully
- [ ] AI chat responses working
- [ ] Fallback system activated (if one provider fails)

## 🚀 Ready to Go!

Once you've completed this setup, your ECHO application will have:

✅ **Secure authentication** with JWT tokens  
✅ **Multiple AI providers** with automatic fallback  
✅ **Database persistence** for conversations and memories  
✅ **Production-ready configuration** options  

Your intelligent memory companion is now fully configured! 🌟 