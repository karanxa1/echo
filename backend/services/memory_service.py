import os
import uuid
import chromadb
import openai
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.memory import Memory
from models.user import User
from config import settings
import json
import whisper
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer

class MemoryService:
    def __init__(self):
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_directory)
        
        # Initialize OpenAI
        openai.api_key = settings.openai_api_key
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Whisper for audio transcription
        self.whisper_model = whisper.load_model("base")
        
        # Ensure upload directory exists
        os.makedirs(settings.upload_directory, exist_ok=True)

    def get_or_create_collection(self, user_id: int, collection_name: str = None) -> chromadb.Collection:
        """Get or create a ChromaDB collection for a user's memories."""
        if not collection_name:
            collection_name = f"user_{user_id}_memories"
        
        try:
            collection = self.chroma_client.get_collection(collection_name)
        except:
            collection = self.chroma_client.create_collection(collection_name)
        
        return collection

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
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        # Generate embedding and store in ChromaDB
        self._create_embedding(memory, content, user_id)
        
        # Mark as processed
        memory.processed = True
        db.commit()
        
        return memory

    def process_voice_memory(self, file_path: str, user_id: int, db: Session, **metadata) -> Memory:
        """Process and store an audio memory."""
        
        # Transcribe audio using Whisper
        result = self.whisper_model.transcribe(file_path)
        transcribed_text = result["text"]
        
        # Create memory record
        memory = Memory(
            user_id=user_id,
            content=transcribed_text,
            content_type="voice",
            file_path=file_path,
            original_filename=metadata.get("filename"),
            source=metadata.get("source", "upload"),
            timestamp=metadata.get("timestamp", datetime.utcnow()),
            title=metadata.get("title", f"Voice memo: {transcribed_text[:30]}..."),
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        # Generate embedding and store in ChromaDB
        self._create_embedding(memory, transcribed_text, user_id)
        
        # Mark as processed
        memory.processed = True
        db.commit()
        
        return memory

    def process_image_memory(self, file_path: str, user_id: int, db: Session, **metadata) -> Memory:
        """Process and store an image memory."""
        
        # Extract text from image using OCR
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)
        except Exception as e:
            extracted_text = f"Image content could not be extracted: {str(e)}"
        
        # Create content combining extracted text and metadata
        content = f"Image: {metadata.get('title', 'Untitled image')}\n"
        if extracted_text.strip():
            content += f"Text in image: {extracted_text.strip()}\n"
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
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        
        # Generate embedding and store in ChromaDB
        self._create_embedding(memory, content, user_id)
        
        # Mark as processed
        memory.processed = True
        db.commit()
        
        return memory

    def _create_embedding(self, memory: Memory, content: str, user_id: int):
        """Create and store vector embedding for memory content."""
        
        # Generate embedding
        embedding = self.embedding_model.encode([content])[0].tolist()
        
        # Get user's memory collection
        collection = self.get_or_create_collection(user_id)
        
        # Create unique ID for this memory
        embedding_id = f"memory_{memory.id}_{uuid.uuid4().hex[:8]}"
        
        # Store in ChromaDB
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "memory_id": memory.id,
                "user_id": user_id,
                "content_type": memory.content_type,
                "timestamp": memory.timestamp.isoformat() if memory.timestamp else None,
                "source": memory.source,
                "title": memory.title,
            }],
            ids=[embedding_id]
        )
        
        # Update memory with embedding ID
        memory.embedding_id = embedding_id

    def search_memories(self, query: str, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant memories using semantic similarity."""
        
        # Get user's memory collection
        collection = self.get_or_create_collection(user_id)
        
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search for similar memories
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        memories = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                
                memories.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance,  # Convert distance to similarity
                    "memory_id": metadata.get("memory_id")
                })
        
        return memories

    def get_context_for_conversation(self, query: str, user_id: int, replica_id: Optional[int] = None, limit: int = 5) -> str:
        """Get relevant memory context for a conversation."""
        
        # Search for relevant memories
        memories = self.search_memories(query, user_id, limit)
        
        # Format context
        context_parts = []
        for memory in memories:
            if memory["similarity_score"] > 0.7:  # Only include highly relevant memories
                timestamp = memory["metadata"].get("timestamp", "Unknown time")
                content = memory["content"]
                source = memory["metadata"].get("source", "Unknown source")
                
                context_parts.append(f"[{timestamp}] ({source}): {content}")
        
        if context_parts:
            return "Relevant memories:\n" + "\n\n".join(context_parts)
        else:
            return "No directly relevant memories found."

    def analyze_emotions(self, content: str) -> Dict[str, float]:
        """Analyze emotions in memory content using OpenAI."""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an emotion analysis expert. Analyze the emotional content of the given text and return a JSON object with emotion scores between 0 and 1 for: joy, sadness, anger, fear, surprise, disgust, trust, anticipation."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse the response
            emotion_text = response.choices[0].message.content
            return json.loads(emotion_text)
            
        except Exception as e:
            print(f"Error analyzing emotions: {e}")
            return {}

    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract people, locations, and topics from memory content."""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract people, locations, and topics from the text. Return a JSON object with three arrays: 'people' (names of people mentioned), 'locations' (places mentioned), and 'topics' (main themes or subjects discussed)."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            # Parse the response
            entities_text = response.choices[0].message.content
            return json.loads(entities_text)
            
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {"people": [], "locations": [], "topics": []}

memory_service = MemoryService() 