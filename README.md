# ECHO – Your Life, Remembered Forever

*Talk to your past self. Talk to your loved ones who are gone. Never lose a moment again.*

## 🔥 Overview

ECHO is an AI-powered personal memory and legacy system that allows users to capture, organize, and interact with their own life memories and create conversational AI replicas of loved ones (living or deceased). It offers a secure, emotional, and intelligent interface to preserve human experiences forever.

## 🌟 Key Features

- **AI Memory Capture**: Ingest data from messages, journals, photos, and voice notes
- **AI Replica Creation**: Create conversational AI replicas of loved ones
- **Conversational Interface**: Talk to your past self or deceased family members
- **Privacy-First**: Local-first architecture with full encryption
- **Multi-Modal**: Text, voice, and image support

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- OpenAI API key (or local LLM setup)

### Installation

1. **Clone and setup backend**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Setup database**:
```bash
# Create PostgreSQL database
createdb echo_db

# Run migrations
python manage.py migrate
```

3. **Setup frontend**:
```bash
cd frontend
npm install
```

4. **Environment setup**:
```bash
# Copy environment template
cp .env.example .env

# Add your API keys and database credentials
```

### Running the Application

1. **Start backend**:
```bash
cd backend
python app.py
```

2. **Start frontend**:
```bash
cd frontend
npm run dev
```

3. **Visit**: http://localhost:3000

## 📂 Project Structure

```
echo/
├── backend/              # FastAPI backend
│   ├── app.py           # Main application
│   ├── models/          # Database models
│   ├── api/             # API endpoints
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   └── utils/       # Utilities
└── docs/               # Documentation
```

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL, ChromaDB
- **AI**: OpenAI GPT-4, Whisper
- **Speech**: Web Speech API, ElevenLabs
- **Deployment**: Docker, local-first

## 📖 Usage

### 1. Memory Ingestion
- Upload text files, voice recordings, or images
- Data is automatically processed and indexed
- Semantic search enables intelligent querying

### 2. Creating Replicas
- Upload conversations and media from/about loved ones
- AI learns their personality and communication style
- Chat interface allows natural conversations

### 3. Conversational Modes
- **Past Self**: Query your own memories and experiences
- **Loved Ones**: Talk to AI replicas of family/friends
- **Memory Exploration**: Re-live specific moments or time periods

## 🔒 Privacy & Security

- Local-first architecture
- End-to-end encryption for all data
- Optional cloud backup with user control
- Open-source and auditable

## 🗺️ Roadmap

- [x] Phase 1: Data ingestion and storage
- [x] Phase 2: Memory chatbot
- [ ] Phase 3: Personality cloning
- [ ] Phase 4: Voice and avatar interaction
- [ ] Phase 5: Advanced features (emotion analysis, memory graphs)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Ethical Considerations

ECHO is designed with deep respect for human emotions and memories. Please use responsibly:
- Obtain consent before creating replicas of others
- Be mindful of emotional impact
- Remember that AI replicas are not real people
- Respect privacy and data ownership

---

*ECHO - Because every moment matters, and every voice deserves to be heard forever.* 