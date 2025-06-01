import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.memory import Memory
from models.user import User
from config import settings
import json

class MemoryService:
    def __init__(self):
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

    def process_text_memory(self, content: str, user_id: int, db: Session, **metadata) -> Memory:
        """Process and store a text-based memory."""
        
        # Create memory record
        memory = Memory(
            user_id=user_id,
            content=content,
            content_type="text",
            source=metadata.get("source", "manual"),
            timestamp=metadata.get("timestamp", datetime.utcnow()),
            title=metadata.get("title", content[:50] + "..." if len(content) > 50 else content),
            processed=True
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        return memory

    def process_voice_memory(self, file_path: str, user_id: int, db: Session, **metadata) -> Memory:
        """Process and store an audio memory (simplified - no transcription)."""
        
        # Create memory record
        memory = Memory(
            user_id=user_id,
            content=f"Audio file: {metadata.get('filename', 'unknown')}",
            content_type="voice",
            file_path=file_path,
            original_filename=metadata.get("filename"),
            source=metadata.get("source", "upload"),
            timestamp=metadata.get("timestamp", datetime.utcnow()),
            title=metadata.get("title", f"Voice memo"),
            processed=True
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        return memory

    def process_image_memory(self, file_path: str, user_id: int, db: Session, **metadata) -> Memory:
        """Process and store an image memory (simplified - no OCR)."""
        
        # Create content with metadata
        content = f"Image: {metadata.get('title', 'Untitled image')}\n"
        if metadata.get("description"):
            content += f"Description: {metadata['description']}"
        
        # Create memory record
        memory = Memory(
            user_id=user_id,
            content=content,
            content_type="image",
            file_path=file_path,
            original_filename=metadata.get("filename"),
            source=metadata.get("source", "upload"),
            timestamp=metadata.get("timestamp", datetime.utcnow()),
            title=metadata.get("title", "Image memory"),
            processed=True
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        return memory

    def search_memories(self, query: str, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for memories using simple text matching."""
        # This is a simplified version - in production, use semantic search
        return []

    def get_context_for_conversation(self, query: str, user_id: int, replica_id: Optional[int] = None, limit: int = 5) -> str:
        """Get relevant memory context for conversation (simplified)."""
        return "No memories found for context."

    def analyze_emotions(self, content: str) -> Dict[str, float]:
        """Analyze emotions in content (simplified)."""
        return {"positive": 0.5, "negative": 0.3, "neutral": 0.2}

    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from content (simplified)."""
        return {"people": [], "places": [], "organizations": [], "dates": []}

# Global instance
memory_service = MemoryService() 