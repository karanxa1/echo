# ECHO Quick Start Guide

Get ECHO running in minutes with this step-by-step guide.

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### Steps

1. **Clone and configure**:
```bash
git clone <your-repo-url>
cd echo
cp env.example .env
```

2. **Add your OpenAI API key**:
Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

3. **Start the application**:
```bash
docker-compose up -d
```

4. **Visit the application**:
Open http://localhost:3000 in your browser

That's it! 🎉

## 🛠️ Manual Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL
- OpenAI API key

### Backend Setup

1. **Navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your settings
```

5. **Setup database**:
```bash
createdb echo_db
```

6. **Start backend**:
```bash
python app.py
```

### Frontend Setup

1. **Navigate to frontend**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start frontend**:
```bash
npm run dev
```

4. **Visit**: http://localhost:3000

## 🔑 Essential Configuration

### Required Environment Variables

**Backend (.env)**:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/echo_db
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_super_secret_key_here
```

### First Steps After Setup

1. **Create an account** at http://localhost:3000/register
2. **Upload your first memory** - try a text note or voice memo
3. **Chat with your past self** using the memories you've uploaded
4. **Create a replica** of a loved one and start a conversation

## 📁 Project Structure

```
echo/
├── backend/          # FastAPI backend
│   ├── api/         # API endpoints
│   ├── models/      # Database models
│   ├── services/    # Business logic
│   └── app.py       # Main application
├── frontend/        # React frontend
│   └── src/
│       ├── pages/   # Next.js pages
│       ├── context/ # React context
│       └── services/# API services
└── docker-compose.yml
```

## 🆘 Troubleshooting

### Common Issues

**Backend won't start**:
- Check if PostgreSQL is running
- Verify your database credentials in `.env`
- Ensure OpenAI API key is valid

**Frontend can't connect**:
- Make sure backend is running on port 8000
- Check CORS settings in backend

**Database connection failed**:
- Create the database: `createdb echo_db`
- Check PostgreSQL is running: `pg_isready`

### Getting Help

1. Check the console/terminal for error messages
2. Verify all environment variables are set
3. Ensure all services are running (database, backend, frontend)

## 🎯 Next Steps

- **Upload memories**: Start with text memories, then try voice and images
- **Create replicas**: Add information about loved ones to create AI replicas
- **Explore conversations**: Try different types of conversations and questions
- **Review the full README.md** for advanced features and configuration

---

**Need help?** Check the main [README.md](README.md) for detailed documentation. 